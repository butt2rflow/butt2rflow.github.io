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


# ------------------------------------------------------------------
# Big drops (added 2026-10-27): does the COR/SKEW state help with declines
# of 10% or more, the case a Kelly discount would actually exist for?
# ------------------------------------------------------------------
BIG = -10.0       # % peak-to-trough
FWD = 60          # sessions for the forward max-drawdown test


def states_full() -> pd.DataFrame:
    """Daily states on the full Cboe history (not limited to the backfill)."""
    spx = ud.fetch_spx()
    tenor = {k: ud._fetch_cboe_index(k) for k in ("COR1M", "COR1Y")}
    x = pd.DataFrame({"spx": spx, "cor90d": ud._fetch_cboe_index("COR90D"),
                      "skew": ud._fetch_cboe_index("SKEW"),
                      "spread": tenor["COR1Y"] - tenor["COR1M"]}).sort_index()
    x = x[x.spx.notna()].ffill(limit=3)
    x["cor90d_pct"], x["skew_pct"] = pct_1y(x.cor90d.dropna()), pct_1y(x["skew"].dropna())
    x = x.dropna(subset=["cor90d_pct", "skew_pct", "spread"])
    sp = bucket(x.spread, 0, -5, reverse=True)
    x["fix_group"] = worst(sp, bucket(x.cor90d, 50, 60), bucket(x["skew"], 150, 158))
    x["pct_group"] = worst(sp, bucket(x.cor90d_pct, 0.75, 0.95), bucket(x.skew_pct, 0.75, 0.95))
    x["skew_top5"] = x.skew_pct >= 0.95
    # forward FWD-session max drawdown from each close
    s = x.spx.values
    fwd = np.full(len(s), np.nan)
    for i in range(len(s) - FWD):
        fwd[i] = (s[i + 1:i + 1 + FWD].min() / s[i] - 1) * 100
    x["fwd_dd"] = fwd
    x["pos"] = np.arange(len(x))
    return x


def drawdown_episodes(spx: pd.Series, th=BIG) -> list[dict]:
    """Zigzag: every fall of at least |th|% from a local peak, where a peak is
    the high since the previous such trough (so 2010, 2011 and 2023 count on
    their own instead of merging into the 2007-13 and 2022-24 recoveries)."""
    v, idx = spx.values, spx.index
    out, peak_i, trough_i, falling = [], 0, 0, False
    for i in range(1, len(v)):
        if not falling:
            if v[i] > v[peak_i]:
                peak_i = i
            elif (v[i] / v[peak_i] - 1) * 100 <= th:
                falling, trough_i = True, i
        else:
            if v[i] < v[trough_i]:
                trough_i = i
            elif (v[i] / v[trough_i] - 1) * 100 >= -th:      # rebound of |th|% ends the fall
                seg = v[peak_i:trough_i + 1]
                five = peak_i + int(np.argmax((seg / v[peak_i] - 1) * 100 <= -5))
                out.append({"peak": idx[peak_i], "minus5": idx[five], "trough": idx[trough_i],
                            "depth": (v[trough_i] / v[peak_i] - 1) * 100})
                falling, peak_i = False, i
    return out


def big_drops() -> None:
    x = states_full()
    on = lambda c, d0, d1: x.loc[d0:d1, c].isin(["caution", "danger"]).mean()  # noqa: E731
    rows = []
    for e in drawdown_episodes(x.spx):
        pre = x.index[max(0, x.index.get_loc(e["peak"]) - 20)]
        rows.append({"peak": e["peak"].date(), "trough": e["trough"].date(), "depth": f"{e['depth']:.0f}%",
                     "fixed: 20d before peak on": f"{on('fix_group', pre, e['peak']):.0%}",
                     "pct: 20d before peak on": f"{on('pct_group', pre, e['peak']):.0%}",
                     "fixed @ -5%": x.loc[e["minus5"], "fix_group"], "pct @ -5%": x.loc[e["minus5"], "pct_group"],
                     "SKEW 1y @ peak": f"{x.loc[e['peak'], 'skew_pct']:.0%}",
                     "COR90D 1y @ peak": f"{x.loc[e['peak'], 'cor90d_pct']:.0%}"})
    print(f"## Declines of {abs(BIG):.0f}%+ since {x.index[0].date()} (states need a year of history)")
    print(pd.DataFrame(rows).to_markdown(index=False), "\n")
    y = x.dropna(subset=["fwd_dd"])
    hit = (y.fwd_dd <= BIG).astype(float)
    base_lo, base_hi = _boot_ci(hit, y.pos)
    res = {"all days": {"n": len(y), "P(60d dd <= -10%)": f"{hit.mean():.1%} [{base_lo:.1%}–{base_hi:.1%}]"}}
    for name, m in [("fixed caution+", y.fix_group.isin(["caution", "danger"])), ("fixed danger", y.fix_group.eq("danger")),
                    ("pct caution+", y.pct_group.isin(["caution", "danger"])), ("pct danger", y.pct_group.eq("danger")),
                    ("SKEW 1y top 5%", y.skew_top5), ("group ok (no discount)", y.pct_group.eq("ok"))]:
        g = hit[m]
        lo, hi = _boot_ci(g, y.pos[m])
        res[name] = {"n": int(m.sum()), "episodes": _episodes(pd.Series(True, index=g.index), y.pos[m]),
                     "P(60d dd <= -10%)": f"{g.mean():.1%} [{lo:.1%}–{hi:.1%}]",
                     "<=2019": f"{hit[m & (y.index < '2020')].mean():.1%}", "2020-": f"{hit[m & (y.index >= '2020')].mean():.1%}"}
    print(f"## Forward {FWD}-session max drawdown <= {BIG:.0f}% (block bootstrap, block 20)")
    print(pd.DataFrame(res).T.to_markdown())


if __name__ == "__main__":
    big_drops() if "--big" in sys.argv else main()
