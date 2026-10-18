"""
Score morning briefings against what actually happened.

Two inputs:
  brief_log/<date>.json   live briefings (morning_brief.py), scored in place
  brief_log/backfill.csv  the same template read replayed over Cboe history
                          (2008–, first rows after the 252-session warm-up: 2010-09), so the monthly review has a usable sample
                          from day one. No GEX / put-call / VX curve history
                          exists for the replay, so it carries only the
                          signals that do (SKEW, COR90D, VIX/VIX3M, VVIX,
                          VIX9D/VIX, VRP).

Outcomes per horizon h ∈ {5, 10, 20} sessions after the data date:
  ret      SPX close-to-close return (%)
  maxdd    worst close inside the window vs the data-date close (%)
  maxup    best close inside the window (%)
  vix_chg  VIX change to the end of the window (pt)
  rv       realized SPX vol over the window, annualized (%) — compared with
           the VIX on the data date, i.e. did the insurance price the risk
  skew_chg SKEW change (did the hedge unwind?)
  worst_state  worst briefing state inside the window (live logs only)

backfill.csv is rebuilt from Cboe on every review run and is not committed
(~1 MB; regenerating is cheaper than versioning it).

Run from project root:
    python scripts/score_briefs.py              # score live logs + rebuild backfill
    python scripts/score_briefs.py --live-only  # daily, before the briefing
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_dashboard as ud  # noqa: E402
import morning_brief as mb  # noqa: E402

LOG_DIR = mb.LOG_DIR
BACKFILL = LOG_DIR / "backfill.csv"
HORIZONS = (5, 10, 20)
STATE_RANK = {"🟢": 0, "🟡": 1, "🔴": 2}


def load_history() -> pd.DataFrame:
    names = ["SPX", "VIX", "VIX9D", "VIX3M", "VVIX", "SKEW", "COR90D"]
    return pd.DataFrame({n: ud._fetch_cboe_index(n) for n in names}).sort_index()


def outcome_at(h: pd.DataFrame, t: pd.Timestamp, n: int) -> dict | None:
    spx = h["SPX"].dropna()
    if t not in spx.index:
        return None
    i = spx.index.get_loc(t)
    if i + n >= len(spx):
        return None
    base, win = spx.iloc[i], spx.iloc[i + 1:i + n + 1]
    rets = spx.iloc[i:i + n + 1].pct_change().dropna()
    end = spx.index[i + n]
    vix, skew = h["VIX"], h["SKEW"]
    return {
        "end": end.strftime("%Y-%m-%d"),
        "ret": float((win.iloc[-1] / base - 1) * 100),
        "maxdd": float((win.min() / base - 1) * 100),
        "maxup": float((win.max() / base - 1) * 100),
        "vix_chg": float(vix.get(end, np.nan) - vix.get(t, np.nan)),
        "rv": float(rets.std() * np.sqrt(252) * 100),
        "skew_chg": float(skew.get(end, np.nan) - skew.get(t, np.nan)),
    }


# ============================================================
# Live logs
# ============================================================
def score_live(h: pd.DataFrame) -> int:
    logs = sorted(p for p in LOG_DIR.glob("????-??-??.json"))
    recs = {p: json.loads(p.read_text(encoding="utf-8")) for p in logs}
    states = {r["data_date"]: STATE_RANK.get(r["state"]["emoji"], 0) for r in recs.values()}
    inv = {v: k for k, v in STATE_RANK.items()}
    updated = 0
    for p, r in recs.items():
        out = r.get("outcome") or {}
        if out.get("complete"):
            continue
        t = pd.Timestamp(r["data_date"])
        changed = False
        for n in HORIZONS:
            key = f"h{n}"
            if key in out:
                continue
            o = outcome_at(h, t, n)
            if o is None:
                continue
            later = [s for d, s in states.items() if r["data_date"] < d <= o["end"]]
            o["worst_state"] = inv[max(later)] if later else None
            out[key] = o
            changed = True
        out["complete"] = all(f"h{n}" in out for n in HORIZONS)
        if changed:
            r["outcome"] = out
            p.write_text(json.dumps(r, ensure_ascii=False, indent=1, default=float),
                         encoding="utf-8")
            updated += 1
    return updated


# ============================================================
# Backfill — the template read replayed over history
# ============================================================
def build_backfill(h: pd.DataFrame) -> pd.DataFrame:
    d = h.dropna(subset=["SPX", "VIX", "VIX3M", "VVIX", "SKEW", "COR90D"]).copy()
    # Residual needs 2×252 sessions of warm-up; compute before the 2008 cut.
    d["vvix_resid_pct"] = mb.vvix_residual(d.VVIX, d.VIX).pct
    d = d.loc["2008":]
    d["vix_vix3m"] = d.VIX / d.VIX3M
    d["vix9d_vix"] = d.VIX9D / d.VIX
    d["skew_5d"] = d.SKEW.diff(5)
    d["skew_pct"] = d.SKEW.rolling(252).rank(pct=True)
    d["vvix_pct"] = d.VVIX.rolling(252).rank(pct=True)
    d["cor90d_5d"] = d.COR90D.diff(5)
    rv20 = d.SPX.pct_change().rolling(20).std() * np.sqrt(252) * 100
    d["vrp"] = d.VIX - rv20
    d["spx_from_high_20d"] = (d.SPX / d.SPX.rolling(20).max() - 1) * 100
    d = d.dropna(subset=["skew_pct", "vrp"])

    rows = []
    for t, x in d.iterrows():
        m = {"vix_vix3m": x.vix_vix3m, "vvix": x.VVIX, "vvix_pct": x.vvix_pct,
             "skew_5d": x.skew_5d, "skew_pct": x.skew_pct, "cor90d_5d": x.cor90d_5d}
        emoji, _, why = mb.classify({"m": m, "vs": None})
        rows.append({"date": t.strftime("%Y-%m-%d"), "state": emoji, "why": " · ".join(why),
                     "vix": x.VIX, "vix_vix3m": x.vix_vix3m, "vvix": x.VVIX,
                     "vvix_pct": x.vvix_pct, "vvix_resid_pct": x.vvix_resid_pct,
                     "vix9d_vix": x.vix9d_vix, "skew": x.SKEW, "skew_5d": x.skew_5d,
                     "skew_pct": x.skew_pct, "cor90d": x.COR90D, "cor90d_5d": x.cor90d_5d,
                     "vrp": x.vrp, "spx_from_high_20d": x.spx_from_high_20d})
    bf = pd.DataFrame(rows).set_index("date")

    spx, vix, skew = h["SPX"].dropna(), h["VIX"], h["SKEW"]
    for n in HORIZONS:
        fwd = pd.concat([spx.shift(-k) for k in range(1, n + 1)], axis=1)
        ret1 = spx.pct_change()
        rv = ret1[::-1].rolling(n).std()[::-1].shift(-1) * np.sqrt(252) * 100
        o = pd.DataFrame({
            f"h{n}_ret": (spx.shift(-n) / spx - 1) * 100,
            f"h{n}_maxdd": (fwd.min(axis=1) / spx - 1) * 100,
            f"h{n}_maxup": (fwd.max(axis=1) / spx - 1) * 100,
            f"h{n}_vix_chg": vix.reindex(spx.index).shift(-n) - vix.reindex(spx.index),
            f"h{n}_rv": rv,
            f"h{n}_skew_chg": skew.reindex(spx.index).shift(-n) - skew.reindex(spx.index),
        })
        o.loc[o.index[-n:]] = np.nan          # window not finished yet
        o.index = o.index.strftime("%Y-%m-%d")
        bf = bf.join(o)
    bf["synthetic"] = True
    return bf


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-only", action="store_true",
                    help="score brief_log/*.json only; skip the (uncommitted) backfill")
    args = ap.parse_args()

    h = load_history()
    n = score_live(h)
    print(f"Live logs updated: {n}")
    if args.live_only:
        return
    bf = build_backfill(h)
    LOG_DIR.mkdir(exist_ok=True)
    bf.round(4).to_csv(BACKFILL)
    print(f"Backfill: {len(bf)} days ({bf.index[0]} → {bf.index[-1]}), "
          f"states {bf.state.value_counts().to_dict()}")


if __name__ == "__main__":
    main()
