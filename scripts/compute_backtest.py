#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute a "showing-the-idea" backtest for each Kelly × Premium profile and
write summary metrics to docs/assets/data/backtest_results.json.

The wizard's result screen reads this static JSON to show the user roughly
how their recommended profile would have performed on SPX history. This
is intentionally simplified — see the disclaimer in the JSON output and
the wizard UI for the caveats.

Simplifications:
- SPX price returns only (no dividends; SPX TR would add ~2pt/yr CAGR).
- Cash returns 0% (T-bills would add ~1-3pt/yr drag-relief).
- Discount profile and Split toggles are NOT applied (assumes all signals
  always OK and the tactical bucket sits as cash).
- Kelly base uses each day's prior-close VIX, capped at 100%.

Run from project root:
    venv/Scripts/python.exe scripts/compute_backtest.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from update_dashboard import (
    EQUITY_PREMIUM_PROFILES,
    KELLY_FRACTIONS,
    _fetch_cboe_index,
    kelly_weight_at,
)

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "docs" / "assets" / "data" / "backtest_results.json"

# Periods to summarize. "full" uses whatever data is available; the rest
# are fixed event windows so the user can see how each profile behaved
# during specific stress regimes.
PERIODS = [
    ("full",       None,                    None,                    "전체",       "Full history"),
    ("since_2010", pd.Timestamp("2010-01-01"), None,                    "2010~",      "Since 2010"),
    ("covid_2020", pd.Timestamp("2020-02-01"), pd.Timestamp("2020-12-31"), "코로나 2020",  "Covid 2020"),
    ("bear_2022",  pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"), "베어 2022",    "Bear 2022"),
]

TRADING_DAYS = 252


def simulate_nav(daily_ret_eq: pd.Series, eq_pct_series: pd.Series) -> pd.Series:
    """NAV path assuming `eq_pct_series` fraction in SPX, rest in 0% cash.
    Both inputs must share the same index.

    Convention: eq_pct on day t is decided at t's open using t-1's VIX
    close (the input series is shifted by the caller). NAV step is then
    NAV[t] = NAV[t-1] * (1 + eq_pct[t] * spx_return[t])."""
    port_ret = eq_pct_series * daily_ret_eq
    nav = (1.0 + port_ret.fillna(0.0)).cumprod()
    return nav


def summarize(nav: pd.Series) -> dict:
    """Cum / CAGR / MDD / Vol / Sharpe from a NAV series. Returns 0s if
    the slice is too short to be meaningful."""
    if len(nav) < 2 or nav.iloc[0] == 0:
        return {"cum_pct": 0.0, "cagr_pct": 0.0, "mdd_pct": 0.0, "vol_pct": 0.0, "sharpe": 0.0, "days": int(len(nav))}
    cum = float(nav.iloc[-1] / nav.iloc[0] - 1.0)
    days = int(len(nav))
    years = max(days / TRADING_DAYS, 1e-6)
    cagr = float((nav.iloc[-1] / nav.iloc[0]) ** (1.0 / years) - 1.0)
    roll_max = nav.cummax()
    drawdown = nav / roll_max - 1.0
    mdd = float(drawdown.min())  # most-negative
    daily_ret = nav.pct_change().dropna()
    vol = float(daily_ret.std() * np.sqrt(TRADING_DAYS))
    sharpe = float(cagr / vol) if vol > 1e-9 else 0.0
    return {
        "cum_pct":  round(cum * 100.0, 2),
        "cagr_pct": round(cagr * 100.0, 2),
        "mdd_pct":  round(mdd * 100.0, 2),
        "vol_pct":  round(vol * 100.0, 2),
        "sharpe":   round(sharpe, 2),
        "days":     days,
    }


def slice_period(s: pd.Series, start: pd.Timestamp | None, end: pd.Timestamp | None) -> pd.Series:
    out = s
    if start is not None:
        out = out[out.index >= start]
    if end is not None:
        out = out[out.index <= end]
    return out


def main() -> None:
    print("Fetching SPX history from Cboe CDN...")
    spx = _fetch_cboe_index("SPX").sort_index()
    print(f"  SPX: {len(spx)} rows, {spx.index[0].date()} → {spx.index[-1].date()}")

    print("Fetching VIX history from Cboe CDN...")
    vix = _fetch_cboe_index("VIX").sort_index()
    print(f"  VIX: {len(vix)} rows, {vix.index[0].date()} → {vix.index[-1].date()}")

    # Inner-join on common dates.
    df = pd.DataFrame({"spx": spx, "vix": vix}).dropna()
    df = df.sort_index()
    print(f"  Joined: {len(df)} rows, {df.index[0].date()} → {df.index[-1].date()}")

    df["spx_ret"] = df["spx"].pct_change()

    # eq_pct on day t uses the VIX close from t-1 (no look-ahead).
    df["vix_lag"] = df["vix"].shift(1)

    profiles_metrics: dict[str, dict] = {}

    for frac_key, frac_val, _ in KELLY_FRACTIONS:
        for prem_key, prem_val in EQUITY_PREMIUM_PROFILES.items():
            eq_pct = df["vix_lag"].apply(
                lambda v: kelly_weight_at(v, frac_val, prem_val)
            )
            nav = simulate_nav(df["spx_ret"], eq_pct)
            per_period = {}
            for key, start, end, _, _ in PERIODS:
                sub_nav = slice_period(nav, start, end)
                # Re-anchor to 1.0 at the start of the slice for the cum_pct
                # to read as "+X% over this window," not since 1990.
                if len(sub_nav) >= 2:
                    sub_nav = sub_nav / sub_nav.iloc[0]
                per_period[key] = summarize(sub_nav)
            profile_id = f"{frac_key}|{prem_key}"
            profiles_metrics[profile_id] = per_period
            full = per_period["full"]
            print(
                f"  {profile_id:30s}  full: "
                f"cum={full['cum_pct']:+.1f}%  CAGR={full['cagr_pct']:+.2f}%  "
                f"MDD={full['mdd_pct']:+.2f}%  vol={full['vol_pct']:.1f}%"
            )

    # SPX 100% baseline — same period slicing, eq_pct = 1.0 throughout.
    print("Computing SPX 100% baseline...")
    spx_nav = (1.0 + df["spx_ret"].fillna(0.0)).cumprod()
    spx_baseline = {}
    for key, start, end, _, _ in PERIODS:
        sub = slice_period(spx_nav, start, end)
        if len(sub) >= 2:
            sub = sub / sub.iloc[0]
        spx_baseline[key] = summarize(sub)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data_range": {
            "start": df.index[0].date().isoformat(),
            "end":   df.index[-1].date().isoformat(),
            "rows":  int(len(df)),
        },
        "periods": [
            {"key": key, "start": s.date().isoformat() if s else None,
             "end": e.date().isoformat() if e else None,
             "label_ko": lk, "label_en": le}
            for key, s, e, lk, le in PERIODS
        ],
        "profiles": profiles_metrics,
        "spx_baseline": spx_baseline,
        "disclaimer": {
            "ko": "단순화된 시뮬레이션입니다. 가격 수익률만 (배당 제외), 현금 이자 0%, Discount/Split 토글 미반영, 옵션 프리미엄·세금·슬리피지 무시. 실제 운용 결과가 아닌 예시 수치입니다.",
            "en": "Simplified illustrative simulation only. Price returns only (no dividends), 0% cash interest, Discount/Split toggles ignored, options premiums / taxes / slippage not modeled. NOT actual performance.",
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {OUT_PATH.relative_to(ROOT)} ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
