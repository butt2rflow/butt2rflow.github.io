"""Should the dashboard's COR90D / SKEW thresholds move from fixed levels to a
1-year percentile? (2026-10-26)

The COR/SKEW group (worst of COR term spread, COR90D, SKEW) discounts the Kelly
equity weight (standard profile: caution x0.90, danger x0.75). COR90D uses
50/60 and SKEW 150/158, set 2026-05 from the post-2020 distribution. Since
2024-10 COR90D's median is ~38, so 50/60 rarely fires. Same question the VVIX
rule faced on 2026-10-18 (fixed 105 -> 1y percentile >= 90%), tested the same
way, with the playbook's change rules:
  - yearly firing rates (regime dependence)
  - P(10-session max drawdown <= -2%) with episodes and block-bootstrap CI,
    <=2019 vs 2020-, holdout 2024-10-
  - within VIX bands (is it more than a VIX proxy?)
  - Holm-adjusted p vs all days

Candidate: trailing 252-session percentile >= 75% caution, >= 95% danger
(mirrors the p75/p95 intent of the fixed levels).

Run: PYTHONUTF8=1 python scripts/study_corskew.py   (needs brief_log/backfill.csv)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_dashboard as ud  # noqa: E402
from review_briefs import _boot_ci, _episodes, diff_pvalues, holm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HOLDOUT = "2024-10-01"


def pct_1y(s: pd.Series) -> pd.Series:
    """Trailing 252-session percentile, inclusive (same as morning_brief._pct_1y)."""
    return s.rolling(252, min_periods=252).apply(lambda w: (w <= w[-1]).mean(), raw=True)


def bucket(v: pd.Series, lo, hi, reverse=False) -> pd.Series:
    if reverse:
        out = np.where(v < hi, "danger", np.where(v < lo, "caution", "ok"))
    else:
        out = np.where(v >= hi, "danger", np.where(v >= lo, "caution", "ok"))
    return pd.Series(out, index=v.index).where(v.notna())


def worst(*cols: pd.Series) -> pd.Series:
    order = {"ok": 0, "caution": 1, "danger": 2}
    inv = {v: k for k, v in order.items()}
    df = pd.concat([c.map(order) for c in cols], axis=1)
    return df.max(axis=1, skipna=False).map(inv)


def load() -> pd.DataFrame:
    bf = pd.read_csv(ROOT / "brief_log" / "backfill.csv", parse_dates=["date"]).set_index("date")
    bf = bf[["vix", "h10_maxdd", "h20_rv"]].copy()
    tenor = {k: ud._fetch_cboe_index(k) for k in ("COR1M", "COR1Y")}
    skew_full = ud._fetch_cboe_index("SKEW")
    cor90_full = ud._fetch_cboe_index("COR90D")
    x = pd.DataFrame({"cor90d": cor90_full, "skew": skew_full,
                      "spread": tenor["COR1Y"] - tenor["COR1M"]}).sort_index()
    x["cor90d_pct"] = pct_1y(x.cor90d)
    x["skew_pct"] = pct_1y(x["skew"])
    d = bf.join(x, how="inner").dropna(subset=["h10_maxdd", "cor90d", "skew", "cor90d_pct", "skew_pct"])
    d["pos"] = np.arange(len(d))
    d["hit"] = (d.h10_maxdd <= -2).astype(float)
    spread_st = bucket(d.spread, 0, -5, reverse=True)
    d["fix_cor"] = bucket(d.cor90d, 50, 60)
    d["fix_skew"] = bucket(d["skew"], 150, 158)
    d["pct_cor"] = bucket(d.cor90d_pct, 0.75, 0.95)
    d["pct_skew"] = bucket(d.skew_pct, 0.75, 0.95)
    d["fix_group"] = worst(spread_st, d.fix_cor, d.fix_skew)
    d["pct_group"] = worst(spread_st, d.pct_cor, d.pct_skew)
    d["spread_state"] = spread_st
    return d


def firing(d: pd.DataFrame, col: str) -> dict:
    cau = d[col].isin(["caution", "danger"])
    dan = d[col].eq("danger")
    yr_c = cau.groupby(d.index.year).mean()
    yr_d = dan.groupby(d.index.year).mean()
    return {"caution+": f"{cau.mean():.0%}", "danger": f"{dan.mean():.0%}",
            "caution+ by year": f"{yr_c.min():.0%}–{yr_c.max():.0%}",
            "danger by year": f"{yr_d.min():.0%}–{yr_d.max():.0%}",
            "last 2y caution+/danger": f"{cau[d.index >= HOLDOUT].mean():.0%}/{dan[d.index >= HOLDOUT].mean():.0%}"}


def outcome(d: pd.DataFrame, mask: pd.Series) -> dict:
    g = d[mask]
    if len(g) < 5:
        return {"n": len(g), "episodes": _episodes(mask[mask].astype(bool), g.pos) if len(g) else 0}
    lo, hi = _boot_ci(g.hit, g.pos)
    sub = lambda m: d[mask & m].hit.mean() if (mask & m).any() else np.nan  # noqa: E731
    return {"n": len(g), "episodes": _episodes(pd.Series(True, index=g.index), g.pos),
            "P(dd10<=-2%)": f"{g.hit.mean():.0%} [{lo:.0%}–{hi:.0%}]",
            "<=2019": f"{sub(d.index < '2020'):.0%}", "2020-": f"{sub(d.index >= '2020'):.0%}",
            "holdout": f"{sub(d.index >= HOLDOUT):.0%}",
            "RV20/VIX med": f"{(g.h20_rv / g.vix).median():.2f}"}


def band_table(d: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = {}
    for lo, hi in [(0, 16), (16, 20), (20, 25), (25, 35), (35, 200)]:
        x = d[(d.vix >= lo) & (d.vix < hi)]
        row = {"n": len(x), "band all": f"{x.hit.mean():.0%}"}
        for c in cols:
            m = x[c].isin(["caution", "danger"])
            row[f"{c} caution+ (n)"] = int(m.sum())
            row[f"{c} caution+"] = f"{x[m].hit.mean():.0%}" if m.sum() >= 20 else "—"
        rows[f"VIX {lo}–{hi if hi < 200 else '+'}"] = row
    return pd.DataFrame(rows).T


def main() -> None:
    d = load()
    print(f"sample {d.index[0].date()} .. {d.index[-1].date()}, {len(d)} sessions; "
          f"all-day P(dd10<=-2%) {d.hit.mean():.0%}\n")
    cols = ["fix_cor", "pct_cor", "fix_skew", "pct_skew", "fix_group", "pct_group"]
    print("## Firing rates"); print(pd.DataFrame({c: firing(d, c) for c in cols}).T.to_markdown(), "\n")
    rows, masks = {}, {}
    for c in cols:
        for lvl, sel in (("caution+", ["caution", "danger"]), ("danger", ["danger"])):
            m = d[c].isin(sel)
            rows[f"{c} {lvl}"] = outcome(d, m)
            masks[f"{c} {lvl}"] = m
    rows["all days"] = outcome(d, pd.Series(True, index=d.index))
    ph = holm(diff_pvalues(d.rename(columns={}), masks))
    out = pd.DataFrame(rows).T
    out["vs all p(Holm)"] = [f"{ph[k]:.2f}" if k in ph else "" for k in out.index]
    print("## Outcomes (10-session max drawdown <= -2%)"); print(out.to_markdown(), "\n")
    print("## Within VIX bands"); print(band_table(d, cols).to_markdown())


if __name__ == "__main__":
    main()
