"""
Does the VX-curve stress trigger (M2−M1 < 0, backwardation) earn its place in
the 🔴 call? Tested on Cboe's per-expiry VX settles joined to the brief
backfill, with the playbook's change rules: episodes, block-bootstrap 95% CI,
≤2019 vs 2020–, within VIX bands, a holdout (last 2 years), and — the real
question — whether it adds anything on days the tested rules (VIX/VIX3M,
VVIX percentile) haven't already called 🔴. Also checks inversions in the
first sessions after a front-month expiry, when M1 has just rolled.

Run from project root, after score_briefs.py has rebuilt brief_log/backfill.csv:
    PYTHONUTF8=1 python scripts/study_vxcurve.py [VX_CSV_CACHE_DIR]
VX_CSV_CACHE_DIR keeps the downloaded per-expiry CSVs between runs
(default: a vx_cache folder next to this repo's brief_log; keep it out of git).
"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import morning_brief as mb  # noqa: E402
import review_briefs as rb  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0"}
ROLL_SESSIONS = 2      # "just after the roll" = expiry day + the next 2 sessions
HOLDOUT_FROM = "2024-10-01"


def _get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read()


def vx_curve(cache: Path) -> pd.DataFrame:
    """Daily M1/M2 monthly settles plus the front expiry; a contract stops
    being the front on its expiry day (same convention as study_discounts)."""
    cache.mkdir(parents=True, exist_ok=True)
    lst = json.loads(_get("https://www.cboe.com/us/futures/market_statistics/historical_data/product/list/VX/"))
    items = sorted({x["expire_date"]: x for y in lst.values() for x in y
                    if x.get("duration_type") == "M"}.values(), key=lambda x: x["expire_date"])
    frames = []
    for x in items:
        f = cache / f"{x['expire_date']}.csv"
        if not f.exists():
            f.write_bytes(_get("https://cdn.cboe.com/" + x["path"]))
            time.sleep(0.15)
        df = pd.read_csv(f, parse_dates=["Trade Date"])
        px = df["Settle"].where(df["Settle"] > 0, df["Close"])
        frames.append(pd.DataFrame({"date": df["Trade Date"], "exp": pd.Timestamp(x["expire_date"]), "px": px}))
    a = pd.concat(frames)
    a = a[(a.px > 0) & (a.date < a.exp)].sort_values(["date", "exp"])
    a["rank"] = a.groupby("date").cumcount()
    px = a[a["rank"] < 2].pivot(index="date", columns="rank", values="px")
    ex = a[a["rank"] == 0].set_index("date")["exp"]
    w = pd.DataFrame({"m1": px[0], "m2": px[1], "front_exp": ex}).dropna()
    exps = pd.DatetimeIndex(sorted(a.exp.unique()))
    # Sessions since the most recent expiry on or before each date.
    k = np.searchsorted(exps, w.index, side="right") - 1
    w = w[k >= 0].copy()               # days before the first listed expiry have no "last roll"
    last_exp = exps[k[k >= 0]]
    # 0 on the expiry day itself (the new front's first day), 1 the next session, ...
    w["since_exp"] = w.index.searchsorted(w.index) - w.index.searchsorted(last_exp)
    return w


def band_rows(x: pd.DataFrame, a: pd.Series, b: pd.Series, la: str, lb: str) -> str:
    rows = {}
    for lo, hi in [(0, 16), (16, 20), (20, 25), (25, 35), (35, 200)]:
        inb = (x.vix >= lo) & (x.vix < hi)
        for lab, m in ((la, a), (lb, b)):
            g = x[inb & m]
            if len(g):
                r = rb._agg(g)
                rows[f"VIX {lo}–{hi if hi < 200 else '+'} · {lab}"] = {
                    k: r[k] for k in ("n", "에피소드", "P(dd10≤−2%)", "95% CI", "~2019", "2020~")}
    return rb._table(rows)


def main() -> None:
    cache = Path(sys.argv[1]) if len(sys.argv) > 1 else mb.LOG_DIR / "vx_cache"
    bf = pd.read_csv(mb.LOG_DIR / "backfill.csv", index_col="date", parse_dates=True)
    vx = vx_curve(cache)
    x = bf.join(vx, how="inner").dropna(subset=["h10_maxdd", "h20_ret"]).copy()
    x.index = x.index.strftime("%Y-%m-%d")
    x["pos"] = np.arange(len(x))
    x["inv"] = x.m2 < x.m1
    x["roll"] = x.since_exp <= ROLL_SESSIONS
    red = x.state == "🔴"     # backfill 🔴 = VIX/VIX3M or VVIX pct only (no curve)

    groups = {
        "전체": x.vix.notna(),
        "역전 (M2−M1<0)": x.inv,
        "역전 · 다른 🔴 없음": x.inv & ~red,
        "역전 · 만기일~+2거래일": x.inv & x.roll,
        "역전 · 그 외": x.inv & ~x.roll,
        "역전 · 얕음 (−0.5 < M2−M1 < 0)": x.inv & (x.m2 - x.m1 > -0.5),
        "비🔴 · 역전 아님": ~red & ~x.inv,
    }
    tab = {k: rb._agg(x[m]) for k, m in groups.items()}
    tab["전체"]["에피소드"] = np.nan
    p = rb.holm(rb.diff_pvalues(x, {k: m for k, m in groups.items() if k != "전체"}))
    for k, v in p.items():
        tab[k]["vs 전체 p(Holm)"] = f"<{2 / rb.BOOT_REPS:.3f}" if v < 2 / rb.BOOT_REPS else f"{v:.3f}"

    ho = x[x.index >= HOLDOUT_FROM]
    ho_tab = {k: rb._agg(ho[m.loc[ho.index]]) for k, m in groups.items()
              if m.loc[ho.index].sum() >= 5}

    print(f"# VX curve trigger study — {x.index[0]} → {x.index[-1]} ({len(x):,} sessions)\n")
    print(f"Inversion days: {int(x.inv.sum())}, of which not 🔴 by the tested rules: {int((x.inv & ~red).sum())}; "
          f"within {ROLL_SESSIONS} sessions after expiry: {int((x.inv & x.roll).sum())}\n")
    print("## Full period\n")
    print(rb._table(tab))
    print("\n## Non-🔴 days within VIX bands: inversion vs none (does the curve add beyond VIX level?)\n")
    print(band_rows(x[~red], x.inv[~red], ~x.inv[~red], "역전", "역전 아님"))
    print(f"\n## Holdout ({HOLDOUT_FROM} →, descriptive)\n")
    print(rb._table(ho_tab))


if __name__ == "__main__":
    main()
