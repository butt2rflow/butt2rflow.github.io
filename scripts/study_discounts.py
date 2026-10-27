"""Do the dashboard's risk-signal discounts improve the Kelly allocation? (2026-10-27)

The cash card sets the equity weight from VIX (3/4 Kelly, mu - r = 5%, cap 100%)
and multiplies one discount per risk group (standard profile: caution x0.90,
danger x0.75):
  - COR/SKEW: worst of COR term spread, COR90D and SKEW (1y-percentile rule)
  - VIX TS:   VX futures M2 - M1 < 0 (backwardation) = danger
  - VolVol:   VVIX/VIX 5-day MA below its 20-day MA = danger, a cross within
              5 sessions = caution
study_corskew.py found the COR/SKEW state is not followed by more drawdowns.
This tests all three the practical way: run the allocation with and without
each discount and compare return, drawdown and Sharpe, with block-bootstrap
CIs on the difference. Plus drawdown rates within VIX bands, since the base
weight already uses VIX.

Weights use today's close and earn tomorrow's SPX return (price only, no
dividends); the rest earns the 3-month T-bill (FRED DTB3). VX futures history
starts 2013, so the common sample is 2013-02 on.

Run: PYTHONUTF8=1 python scripts/study_discounts.py [VX_CSV_DIR]
VX_CSV_DIR holds Cboe's per-expiry VX CSVs (historical_data/VX/VX_<expiry>.csv);
without it they are downloaded.
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
import update_dashboard as ud  # noqa: E402
from study_corskew import bucket, pct_1y, worst  # noqa: E402

FRACTION, PREMIUM = 0.75, 0.05
DISC = {"ok": 1.00, "caution": 0.90, "danger": 0.75}
BLOCK, REPS = 60, 1000
RNG = np.random.default_rng(11)
UA = {"User-Agent": "Mozilla/5.0"}


def _get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read()


def vx_m1_m2(csv_dir: Path | None) -> pd.DataFrame:
    """Daily front (M1) and second (M2) monthly VX settles; a contract stops
    being the front on its expiry day."""
    lst = json.loads(_get("https://www.cboe.com/us/futures/market_statistics/historical_data/product/list/VX/"))
    items = sorted({x["expire_date"]: x for y in lst.values() for x in y if x.get("duration_type") == "M"}.values(),
                   key=lambda x: x["expire_date"])
    frames = []
    for x in items:
        f = csv_dir / f"{x['expire_date']}.csv" if csv_dir else None
        raw = f.read_bytes() if f and f.exists() else _get("https://cdn.cboe.com/" + x["path"])
        if not (f and f.exists()):
            time.sleep(0.15)
        df = pd.read_csv(io.BytesIO(raw), parse_dates=["Trade Date"])
        px = df["Settle"].where(df["Settle"] > 0, df["Close"])
        frames.append(pd.DataFrame({"date": df["Trade Date"], "exp": pd.Timestamp(x["expire_date"]), "px": px}))
    a = pd.concat(frames)
    a = a[(a.px > 0) & (a.date < a.exp)].sort_values(["date", "exp"])
    a["rank"] = a.groupby("date").cumcount()
    w = a[a["rank"] < 2].pivot(index="date", columns="rank", values="px").dropna()
    w.columns = ["m1", "m2"]
    return w


def tbill() -> pd.Series:
    """3-month T-bill (FRED DTB3). Set DTB3_CSV to a downloaded copy when FRED
    throttles scripted requests (it does from the home PC)."""
    import os
    f = os.environ.get("DTB3_CSV")
    raw = Path(f).read_bytes() if f else _get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3&cosd=2006-01-01")
    df = pd.read_csv(io.BytesIO(raw))
    s = pd.Series(pd.to_numeric(df.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(df.iloc[:, 0]))
    return s.dropna() / 100


def load(csv_dir: Path | None) -> pd.DataFrame:
    idx = {k: ud._fetch_cboe_index(k) for k in ("SPX", "VIX", "VVIX", "COR90D", "SKEW", "COR1M", "COR1Y")}
    x = pd.DataFrame(idx).sort_index()
    x = x[x.SPX.notna()].ffill(limit=3)
    x = x.join(vx_m1_m2(csv_dir), how="left").join(tbill().rename("rf"), how="left")
    x["rf"] = x.rf.ffill()
    # COR/SKEW group (live rule)
    sp = bucket(x.COR1Y - x.COR1M, 0, -5, reverse=True)
    x["g_corskew"] = worst(sp, bucket(pct_1y(x.COR90D.dropna()).reindex(x.index), 0.75, 0.95),
                           bucket(pct_1y(x.SKEW.dropna()).reindex(x.index), 0.75, 0.95))
    # VIX TS group
    x["g_ts"] = np.where(x.m2 - x.m1 < 0, "danger", "ok")
    x.loc[x.m1.isna(), "g_ts"] = np.nan
    # VolVol group (same rule as compute_volvol_signal, evaluated every day)
    vv = ud.compute_volvol_df(x.VVIX, x.VIX)
    diff = vv.ma5 - vv.ma20
    crossed = (np.sign(diff) != np.sign(diff.shift(1))) & diff.shift(1).notna()
    recent = crossed.rolling(4, min_periods=1).max().astype(bool)   # a cross among the last 5 values
    st = pd.Series(np.where(diff >= 0, "ok", "danger"), index=vv.index).where(diff.notna())
    st[recent & diff.notna()] = "caution"
    x["g_volvol"] = st.reindex(x.index)
    x["base_w"] = [ud.kelly_weight_at(v, FRACTION, PREMIUM) for v in x.VIX]
    x["ret_next"] = x.SPX.pct_change().shift(-1)
    x["rf_next"] = (x.rf / 252).shift(-1)
    s = x.SPX.values
    for h, col in ((10, "dd10"), (60, "dd60")):
        out = np.full(len(s), np.nan)
        for i in range(len(s) - h):
            out[i] = (s[i + 1:i + 1 + h].min() / s[i] - 1) * 100
        x[col] = out
    return x


def weights(x: pd.DataFrame, groups: list[str]) -> pd.Series:
    w = x.base_w.copy()
    for g in groups:
        w = w * x[g].map(DISC)
    return w


def stats(r: pd.Series, rf: pd.Series, w: pd.Series) -> dict:
    nav = (1 + r).cumprod()
    yrs = len(r) / 252
    ex = r - rf
    return {"CAGR": nav.iloc[-1] ** (1 / yrs) - 1, "vol": r.std() * np.sqrt(252),
            "Sharpe": ex.mean() / ex.std() * np.sqrt(252), "maxDD": (nav / nav.cummax() - 1).min(),
            "avg equity": w.mean()}


def boot_diff(r_a: pd.Series, r_b: pd.Series, rf: pd.Series) -> dict:
    """Block-bootstrap CI for (b - a) in CAGR and Sharpe."""
    n = len(r_a)
    starts = np.arange(0, n - BLOCK)
    A, B, F = r_a.values, r_b.values, rf.values
    dc, ds = [], []
    for _ in range(REPS):
        ix = np.concatenate([np.arange(s, s + BLOCK) for s in RNG.choice(starts, size=n // BLOCK)])
        a, b, f = A[ix], B[ix], F[ix]
        yrs = len(ix) / 252
        dc.append(np.prod(1 + b) ** (1 / yrs) - np.prod(1 + a) ** (1 / yrs))
        ds.append(((b - f).mean() / (b - f).std() - (a - f).mean() / (a - f).std()) * np.sqrt(252))
    lo_c, hi_c = np.percentile(dc, [2.5, 97.5])
    lo_s, hi_s = np.percentile(ds, [2.5, 97.5])
    return {"ΔCAGR 95% CI": f"{lo_c:+.2%} … {hi_c:+.2%}", "ΔSharpe 95% CI": f"{lo_s:+.2f} … {hi_s:+.2f}"}


def backtest(x: pd.DataFrame) -> None:
    d = x.dropna(subset=["g_corskew", "g_ts", "g_volvol", "base_w", "ret_next", "rf_next"])
    print(f"## Allocation backtest {d.index[0].date()} → {d.index[-1].date()} ({len(d)} sessions), "
          f"3/4 Kelly, mu-r 5%, standard discounts, cash at T-bill\n")
    rows = {}
    base_r = None
    for name, gs in [("base (VIX Kelly only)", []), ("× COR/SKEW", ["g_corskew"]), ("× VIX TS", ["g_ts"]),
                     ("× VolVol", ["g_volvol"]), ("× all three (live)", ["g_corskew", "g_ts", "g_volvol"])]:
        w = weights(d, gs)
        r = w * d.ret_next + (1 - w) * d.rf_next
        row = stats(r, d.rf_next, w)
        if base_r is None:
            base_r = r
        else:
            row.update(boot_diff(base_r, r, d.rf_next))
        rows[name] = row
    for name, w in [("SPX buy & hold", pd.Series(1.0, index=d.index))]:
        r = d.ret_next
        rows[name] = stats(r, d.rf_next, w)
    out = pd.DataFrame(rows).T
    for c in ("CAGR", "vol", "maxDD", "avg equity"):
        out[c] = out[c].map(lambda v: f"{v:.1%}")
    out["Sharpe"] = out["Sharpe"].map(lambda v: f"{v:.2f}")
    print(out.fillna("").to_markdown(), "\n")
    for era, m in (("2013–2019", d.index < "2020"), ("2020–", d.index >= "2020")):
        e = d[m]
        line = []
        for name, gs in [("base", []), ("all three", ["g_corskew", "g_ts", "g_volvol"])]:
            w = weights(e, gs)
            r = w * e.ret_next + (1 - w) * e.rf_next
            s = stats(r, e.rf_next, w)
            line.append(f"{name}: CAGR {s['CAGR']:.1%}, Sharpe {s['Sharpe']:.2f}, maxDD {s['maxDD']:.1%}")
        print(f"- {era}: " + " | ".join(line))
    print()


def bands(x: pd.DataFrame) -> None:
    d = x.dropna(subset=["g_ts", "g_volvol", "g_corskew", "dd10"])
    print("## Drawdown rates within VIX bands (signal on = caution or danger)\n")
    rows = {}
    for lo, hi in [(0, 16), (16, 20), (20, 25), (25, 35), (35, 200)]:
        b = d[(d.VIX >= lo) & (d.VIX < hi)]
        row = {"n": len(b), "dd10≤−2% all": f"{(b.dd10 <= -2).mean():.0%}",
               "dd60≤−10% all": f"{(b.dd60 <= -10).mean():.0%}"}
        for g, lab in (("g_corskew", "COR/SKEW"), ("g_ts", "TS"), ("g_volvol", "VolVol")):
            m = b[g].isin(["caution", "danger"])
            row[f"{lab} on n"] = int(m.sum())
            row[f"{lab} on dd10"] = f"{(b[m].dd10 <= -2).mean():.0%}" if m.sum() >= 30 else "—"
            row[f"{lab} off dd10"] = f"{(b[~m].dd10 <= -2).mean():.0%}" if (~m).sum() >= 30 else "—"
        rows[f"VIX {lo}–{hi if hi < 200 else '+'}"] = row
    print(pd.DataFrame(rows).T.to_markdown(), "\n")


def main() -> None:
    csv_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    x = load(csv_dir)
    for g in ("g_corskew", "g_ts", "g_volvol"):
        s = x[g].dropna()
        print(f"{g}: {s.index[0].date()}→, on (caution+danger) {s.isin(['caution', 'danger']).mean():.0%} of days")
    print()
    backtest(x)
    bands(x)


if __name__ == "__main__":
    main()
