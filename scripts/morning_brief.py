"""
Morning volatility briefing → Slack.

Re-uses the home-page dashboard's fetchers and signal functions
(update_dashboard.py) so the briefing and the site never disagree, then adds
what the site doesn't show: 5-day changes, 1-year percentiles, a two-tier
read ("hedging demand rising" vs "stress under way"), and the historical base
rate for the current VIX/SKEW combination. Optionally appends a short Claude
commentary.

Run from project root:
    python scripts/morning_brief.py --dry-run     # print only
    python scripts/morning_brief.py               # send to Slack

Env:
    SLACK_WEBHOOK_URL   Slack Incoming Webhook (required unless --dry-run)
    ANTHROPIC_API_KEY   optional; commentary is skipped when unset
    FRED_API_KEY        optional; credit OAS falls back to the CSV endpoint
    BRIEF_SCHEDULE      the cron string that fired (github.event.schedule);
                        used to send exactly once at 07:30 New York time
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_dashboard as ud  # noqa: E402

NY = ZoneInfo("America/New_York")  # US cash open 09:30 ET; brief at 07:30 ET
SITE_URL = "https://butt2rflow.github.io/"
CLAUDE_MODEL = "claude-opus-5-5"
# Every briefing is archived with its inputs and read, so outcomes (SPX
# path, VIX, credit over the following 5/10/20 sessions) can be scored
# against it later and the playbook tuned from the track record.
LOG_DIR = Path(__file__).resolve().parent.parent / "brief_log"
# Rules and findings the commentary must follow; the monthly review
# (review_briefs.py) proposes edits to it as a PR.
PLAYBOOK = Path(__file__).resolve().parent.parent / "brief_playbook.md"
ROOT = Path(__file__).resolve().parent.parent
CHART_DIR = ROOT / "brief_charts"
PENDING = LOG_DIR / ".pending_slack.json"     # gitignored hand-off between CI steps
# Slack fetches the chart by URL; the workflow pushes it before posting.
RAW_URL = "https://raw.githubusercontent.com/butt2rflow/butt2rflow.github.io/main"

# Two-tier thresholds. Tier 1 = insurance being bought while the index is
# calm; tier 2 = the stress has reached spot vol / the futures curve.
HEDGE_SKEW_5D = 8.0       # SKEW points in 5 sessions
HEDGE_SKEW_PCT = 0.90     # 1-year percentile
HEDGE_COR90D_5D = 4.0     # COR90D points in 5 sessions
STRESS_VIX_VIX3M = 0.95
# VVIX as a 1-year percentile, not a level: the fixed VVIX ≥ 105 fired on
# 79–90% of 2020–21 days and 2–5% of calm years. Backfill 2010–2026: same 🔴
# drawdown rate (40%), yearly firing 1–43% instead of 1–90%, consistent
# ≤2019 / 2020– / 2024-09– holdout (2026-10-18 review).
STRESS_VVIX_PCT = 0.90


# ============================================================
# Schedule gate
# ============================================================
def should_send_now(schedule: str | None) -> bool:
    """GitHub cron is UTC with no DST. Both '30 11' and '30 12' are scheduled;
    keep the one that lands at 07:30 New York time (2h before the US open)
    today. Manual runs always send."""
    if not schedule:
        return True
    utc_hour = int(schedule.split()[1])
    offset_h = int(datetime.now(NY).utcoffset().total_seconds() // 3600)
    return (utc_hour + offset_h) % 24 == 7


# ============================================================
# Data
# ============================================================
def _clean(o):
    """NaN/inf → None so logs and prompts are strict JSON."""
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def _json(o, **kw) -> str:
    return json.dumps(_clean(o), ensure_ascii=False, default=float, allow_nan=False, **kw)


def _chg(s: pd.Series, n: int = 5) -> float:
    s = s.dropna()
    return float(s.iloc[-1] - s.iloc[-1 - n]) if len(s) > n else float("nan")


def _pct_1y(s: pd.Series) -> float:
    s = s.dropna().tail(252)
    return float((s <= s.iloc[-1]).mean()) if len(s) else float("nan")


def base_rate(vix: pd.Series, skew: pd.Series, spx: pd.Series) -> dict:
    """P(SPX trades ≥2% / ≥5% below today's close within 10 sessions), since 2000,
    for days resembling today (VIX within ±10% in log terms, same SKEW
    1y-percentile band) vs all days at the same VIX level.

    Daily rows with a 10-session window overlap, so `n` days is far fewer
    independent observations; `n_ep` counts separate episodes (runs split by
    >10-session gaps) and is the number to judge the sample by."""
    d = pd.DataFrame({"spx": spx, "vix": vix, "sk": skew}).dropna().loc["2000":]
    fwd_min = pd.concat([d.spx.shift(-k) for k in range(1, 11)], axis=1).min(axis=1)
    d["dd10"] = (fwd_min / d.spx - 1) * 100
    d["skpct"] = d.sk.rolling(252).rank(pct=True)
    d["pos"] = np.arange(len(d))
    today = d.iloc[-1]
    hist = d.iloc[:-10].dropna()

    def band(p):
        return 2 if p >= HEDGE_SKEW_PCT else (1 if p >= 0.5 else 0)

    def episodes(x: pd.DataFrame) -> int:
        return int((x.pos.diff().fillna(99) > 10).sum())

    # Control group = same VIX level regardless of SKEW, so the comparison
    # isolates what the insurance reading adds on top of spot vol. A log band
    # keeps "same level" proportional (±2pt was ±17% at VIX 12, ±7% at 30).
    same_vix = hist[(np.log(hist.vix) - np.log(today.vix)).abs() <= np.log(1.1)]
    like = same_vix[same_vix.skpct.apply(band) == band(today.skpct)]
    return {
        "n": int(len(like)),
        "n_ep": episodes(like),
        "p2": float((like.dd10 <= -2).mean()) if len(like) else float("nan"),
        "p5": float((like.dd10 <= -5).mean()) if len(like) else float("nan"),
        "p2_all": float((same_vix.dd10 <= -2).mean()),
        "p5_all": float((same_vix.dd10 <= -5).mean()),
        "band": ["SKEW 하위 50%", "SKEW 50~90%", "SKEW 상위 10%"][band(today.skpct)],
        # A gap that only shows up in one regime isn't a rule (e.g. the
        # same-VIX SKEW-top-10% effect is post-2020 only).
        **{f"{k}_{era}": float((x[x.index < "2020"] if era == "pre" else x[x.index >= "2020"])
                               .dd10.le(-2).mean())
           if len(x[x.index < "2020"] if era == "pre" else x[x.index >= "2020"]) else float("nan")
           for k, x in (("p2", like), ("p2_all", same_vix)) for era in ("pre", "post")},
    }


PUTCALL_URL = "https://cdn.cboe.com/data/us/options/market_statistics/daily/{}_daily_options"
PUTCALL_KEYS = {"EQUITY PUT/CALL RATIO": "equity", "SPX + SPXW PUT/CALL RATIO": "spx"}


def fetch_putcall(dates: list[pd.Timestamp]) -> dict | None:
    """Cboe put/call volume ratios — how much insurance changed hands, the
    quantity side of what SKEW prices. Cboe publishes one JSON per session,
    so only the last ~20 sessions are pulled (today, 5d and 20d averages)."""
    rows = {}
    for t in dates:
        try:
            req = urllib.request.Request(PUTCALL_URL.format(t.strftime("%Y-%m-%d")),
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                ratios = json.load(r).get("ratios", [])
            vals = {PUTCALL_KEYS[x["name"]]: float(x["value"])
                    for x in ratios if x.get("name") in PUTCALL_KEYS}
            if len(vals) == len(PUTCALL_KEYS):
                rows[t] = vals
        except Exception:  # noqa: BLE001
            continue
    if not rows:
        print("  [WARN] Cboe put/call unavailable")
        return None
    df = pd.DataFrame.from_dict(rows, orient="index").sort_index()
    last = df.iloc[-1]
    return {"date": df.index[-1].strftime("%Y-%m-%d"),
            "equity": float(last["equity"]), "spx": float(last["spx"]),
            "equity_5d": float(df.equity.tail(5).mean()), "spx_5d": float(df.spx.tail(5).mean()),
            "equity_20d": float(df.equity.mean()), "spx_20d": float(df.spx.mean()),
            "n": len(df)}


VVIX_RICH, VVIX_CHEAP = 0.80, 0.20     # residual 1y-percentile bands


def vvix_residual(vvix: pd.Series, vix: pd.Series) -> pd.DataFrame:
    """How expensive VIX options (VVIX) are *for the current VIX level*.
    The raw VVIX/VIX ratio is mostly 1/VIX (corr −0.77), so regress log VVIX
    on log VIX over a trailing 252-session window (past data only) and take
    the residual's 1-year percentile. Display-only: in 2010–2026 it predicted
    neither SPX drawdowns, VIX spikes nor rebounds (all CIs overlap) — it
    answers "is hedging via VIX calls cheap or rich vs SPX puts", not
    "where is the market going"."""
    df = pd.DataFrame({"lv": np.log(vvix), "lx": np.log(vix)}).dropna()
    mv, mx = df.lv.rolling(252).mean(), df.lx.rolling(252).mean()
    beta = ((df.lv * df.lx).rolling(252).mean() - mv * mx) / ((df.lx ** 2).rolling(252).mean() - mx ** 2)
    df["resid"] = df.lv - (mv - beta * mx + beta * df.lx)
    df["pct"] = df.resid.rolling(252).rank(pct=True)
    return df[["resid", "pct"]]


def vol_risk_premium(vix: pd.Series, spx: pd.Series) -> dict:
    """VIX minus SPX 20-day realized vol: how expensive insurance is relative
    to the risk actually being realized. Negative = realized vol is running
    above what options price (insurance is cheap / stress is outrunning it)."""
    rv = spx.pct_change().rolling(20).std() * np.sqrt(252) * 100
    vrp = (vix - rv).dropna()
    return {"rv20": float(rv.dropna().iloc[-1]), "vrp": float(vrp.iloc[-1]),
            "vrp_5d": _chg(vrp), "vrp_pct": _pct_1y(vrp)}


def _third_friday(y: int, mth: int) -> pd.Timestamp:
    first = pd.Timestamp(y, mth, 1)
    return first + pd.Timedelta(days=(4 - first.weekday()) % 7 + 14)


def event_calendar(today: pd.Timestamp, vs: dict | None) -> list[dict]:
    """Events that put option hedges on for a reason that expires — FOMC,
    earnings season, monthly opex, VIX expiry. Same SKEW reads differently
    when an event explains it (the hedge unwinds once the event passes).
    Each item: ko (display), en (chart label — no Korean font on CI), date.
    D-N counts weekdays only (US holidays not excluded)."""
    def bd(t):
        return int(np.busday_count(today.date(), t.date()))

    out = []
    fomc = [pd.Timestamp(*x) for x in ud.FOMC_DATES if pd.Timestamp(*x) >= today]
    if fomc:
        out.append({"ko": f"FOMC {fomc[0]:%m/%d} (D-{bd(fomc[0])})", "en": "FOMC",
                    "date": fomc[0].strftime("%Y-%m-%d")})
    else:
        print("  [WARN] FOMC_DATES in update_dashboard.py has no future dates — extend it")
    mth, day = today.month, today.day
    if (mth in (1, 4, 7, 10) and day >= 10) or (mth in (2, 5, 8, 11) and day <= 15):
        out.append({"ko": "어닝 시즌", "en": None, "date": None})
    opex = _third_friday(today.year, mth)
    if opex < today:
        nxt = today + pd.offsets.MonthBegin(1)
        opex = _third_friday(nxt.year, nxt.month)
    out.append({"ko": f"월물 만기 {opex:%m/%d} (D-{bd(opex)})", "en": "OPEX",
                "date": opex.strftime("%Y-%m-%d")})
    if vs and vs.get("front_expiry"):
        vxe = pd.Timestamp(vs["front_expiry"])
        if vxe >= today:
            out.append({"ko": f"VIX 만기 {vxe:%m/%d} (D-{bd(vxe)})", "en": "VIX exp",
                        "date": vxe.strftime("%Y-%m-%d")})
    return out


def _yahoo_5m(ticker: str) -> pd.Series:
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           "?interval=5m&range=5d&includePrePost=true")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        res = json.load(r)["chart"]["result"][0]
    idx = pd.to_datetime(res["timestamp"], unit="s", utc=True).tz_convert(NY)
    return pd.Series(res["indicators"]["quote"][0]["close"], index=idx).dropna()


def fetch_premarket(data_date: str) -> dict | None:
    """What moved between the last cash close and the briefing: ES futures
    (Globex trades overnight) and VIX if Cboe's extended-hours calc has
    printed since the close. Everything else in the brief is end-of-day."""
    close_t = pd.Timestamp(data_date, tz=NY) + pd.Timedelta(hours=16)
    out = {}
    try:
        es = _yahoo_5m("ES%3DF")
        at_close = es[es.index <= close_t]
        if len(at_close) and es.index[-1] > close_t:
            out["es"] = float(es.iloc[-1])
            out["es_chg"] = float((es.iloc[-1] / at_close.iloc[-1] - 1) * 100)
            out["es_time"] = es.index[-1].strftime("%m/%d %H:%M ET")
    except Exception as e:  # noqa: BLE001
        print(f"  [WARN] ES pre-market unavailable ({e})")
    try:
        vx = _yahoo_5m("%5EVIX")
        if vx.index[-1] > close_t + pd.Timedelta(minutes=30):
            out["vix"] = float(vx.iloc[-1])
            out["vix_time"] = vx.index[-1].strftime("%m/%d %H:%M ET")
    except Exception as e:  # noqa: BLE001
        print(f"  [WARN] VIX extended-hours unavailable ({e})")
    return out or None


def fetch_gex_fresh() -> dict | None:
    """Recompute GEX at briefing time and keep the site's overnight snapshot
    alongside it. Unverified whether Yahoo carries the just-finished
    session's OCC open interest by 07:30 ET; if it doesn't, both numbers
    match. The log keeps both so the brief_log answers that question."""
    pub = fetch_gex_published()
    g = None
    try:
        g = ud.fetch_gex()
    except Exception as e:  # noqa: BLE001
        print(f"  [WARN] live GEX failed ({e}); using published snapshot")
    if g:
        g.pop("profile", None)
        g["source"] = "live"
        g["published_net_bn"] = pub["net_bn"] if pub else None
        g["published_flip"] = pub["flip"] if pub else None
        return g
    if pub:
        pub["source"] = "published"
    return pub


def fetch_gex_published() -> dict | None:
    """GEX is expensive (full SPX chain); read the snapshot the site published."""
    try:
        req = urllib.request.Request(ud.GEX_CACHE_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            g = json.load(r)
        g.pop("profile", None)
        return g
    except Exception as e:  # noqa: BLE001
        print(f"  [WARN] GEX snapshot unavailable ({e})")
        return None


def check_freshness(idx: dict[str, pd.Series]) -> list[str]:
    """Each indicator takes its own last value, so flag any whose last date
    lags SPX, and SPX itself if it lags the previous weekday (a US holiday
    also trips this — the warning says so)."""
    warn = []
    spx_last = idx["SPX"].dropna().index[-1]
    for n, s in idx.items():
        last = s.dropna().index[-1]
        if last < spx_last:
            warn.append(f"{n} {last:%m/%d}")
    prev_wd = pd.Timestamp(np.busday_offset(datetime.now(NY).date(), -1, roll="forward"))
    if spx_last < prev_wd:
        warn.insert(0, f"SPX 마지막 종가 {spx_last:%m/%d} (Cboe 미갱신 또는 휴장)")
    return warn


def collect() -> dict:
    idx = {n: ud._fetch_cboe_index(n)
           for n in ["SPX", "VIX", "VIX9D", "VIX3M", "VVIX", "SKEW", "COR90D", "COR1M"]}
    empty = [n for n, s in idx.items() if s.dropna().empty]
    if empty:
        raise RuntimeError(f"Cboe returned no data for {empty} — not sending a partial brief")
    spx, vix, skew = idx["SPX"], idx["VIX"], idx["SKEW"]
    freshness = check_freshness(idx)

    tenor, skew_df = ud.fetch_cor_skew()
    cs = ud.compute_cor_skew_signals(tenor, skew_df)

    vx_stale = None
    try:
        vx = ud.fetch_vix_futures()
    except Exception as e:  # noqa: BLE001
        print(f"  [WARN] VX fetch failed: {e}")
        vx = pd.DataFrame()
    if len(vx) < 2:
        fb_vx, _, fb_date = ud.load_latest_archived_vx()
        if fb_vx is not None:
            vx, vx_stale = fb_vx, fb_date
    vix_spot = float(vix.iloc[-1])
    vs = ud.compute_vix_signals(vx, vix_spot)
    vvs = ud.compute_volvol_signal(ud.compute_volvol_df(idx["VVIX"], vix))
    ks = ud.compute_kelly_signal(vix_spot, cs, vs, vvs)
    ts = ud.compute_tactical_signal(vix, cs, spx)

    credit = ud.fetch_credit_oas()
    credit.pop("series", None)
    move = ud.fetch_move()
    if move:
        move.pop("series", None)

    ratio = (idx["VIX"] / idx["VIX3M"]).dropna()
    r9 = (idx["VIX9D"] / idx["VIX"]).dropna()
    m = {
        "date": spx.index[-1].strftime("%Y-%m-%d"),
        "spx": float(spx.iloc[-1]),
        "spx_1d": float(spx.pct_change().iloc[-1] * 100),
        "spx_from_high_20d": float((spx.iloc[-1] / spx.tail(20).max() - 1) * 100),
        "vix": vix_spot, "vix_5d": _chg(vix),
        "vix9d": float(idx["VIX9D"].iloc[-1]),
        "vix_vix3m": float(ratio.iloc[-1]), "vix_vix3m_5d": _chg(ratio),
        "vvix": float(idx["VVIX"].iloc[-1]), "vvix_5d": _chg(idx["VVIX"]),
        "vvix_pct": _pct_1y(idx["VVIX"]),
        "skew": float(skew.iloc[-1]), "skew_5d": _chg(skew), "skew_pct": _pct_1y(skew),
        "cor90d": float(idx["COR90D"].iloc[-1]), "cor90d_5d": _chg(idx["COR90D"]),
        "cor1m": float(idx["COR1M"].iloc[-1]),
        "vix9d_vix": float(r9.iloc[-1]), "vix9d_vix_5d": _chg(r9),
        **vol_risk_premium(vix, spx),
        "vvix_resid_pct": float(vvix_residual(idx["VVIX"], vix).pct.dropna().iloc[-1]),
    }
    return {"m": m, "cs": cs, "vs": vs, "vx_stale": vx_stale, "vvs": vvs, "ks": ks,
            "ts": ts, "credit": credit, "move": move, "gex": fetch_gex_fresh(),
            "pre": fetch_premarket(m["date"]),
            "pc": fetch_putcall(list(spx.index[-20:])),
            "_series": {k: idx[k] for k in ("SPX", "VIX", "VIX9D", "VIX3M", "SKEW")},
            "freshness": freshness,
            "base": base_rate(vix, skew, spx),
            "events": event_calendar(pd.Timestamp(datetime.now(NY).date()), vs)}


# ============================================================
# Read
# ============================================================
def classify(d: dict) -> tuple[str, str, list[str]]:
    m, vs = d["m"], d["vs"]
    stress = []
    if vs and vs["shape"] == "backwardation":
        stress.append(f"VX 곡선 역전 (M2−M1 {vs['spread_2_1']:+.2f})")
    if m["vix_vix3m"] >= STRESS_VIX_VIX3M:
        stress.append(f"VIX/VIX3M {m['vix_vix3m']:.2f} ≥ {STRESS_VIX_VIX3M}")
    if m["vvix_pct"] >= STRESS_VVIX_PCT:
        stress.append(f"VVIX {m['vvix']:.0f} (1년 {m['vvix_pct']:.0%} 백분위)")
    hedge = []
    if m["skew_5d"] >= HEDGE_SKEW_5D:
        hedge.append(f"SKEW 5일 {m['skew_5d']:+.1f}")
    if m["skew_pct"] >= HEDGE_SKEW_PCT:
        hedge.append(f"SKEW 1년 {m['skew_pct']:.0%} 백분위")
    if m["cor90d_5d"] >= HEDGE_COR90D_5D:
        hedge.append(f"COR90D 5일 {m['cor90d_5d']:+.1f}")
    if stress:
        return "🔴", "스트레스 진행", stress + hedge
    if hedge:
        return "🟡", "주의 — 보험 수요 증가, 큰손들은 대비 중 (지수는 아직 평온)", hedge
    return "🟢", "평온", []


def amplifier(d: dict) -> tuple[bool, str] | None:
    """Puts bought by end users are mostly sold by dealers, who are then
    short gamma on the downside and must sell into a decline. Short GEX with
    spot below the flip = that hedging flow is live."""
    g = d["gex"]
    if not g:
        return None
    on = g["regime"] == "short" and d["m"]["spx"] < g["flip"]
    gap = (d["m"]["spx"] / g["flip"] - 1) * 100
    where = f"flip {g['flip']:,.0f} {'아래' if gap < 0 else '위'} ({gap:+.1f}%)"
    src = "" if g.get("source") == "live" else f" [{g.get('date')} 스냅샷]"
    return on, f"GEX {g['net_bn']:+.1f}B ({g['regime']}) · {where}{src}"


def build_text(d: dict) -> str:
    m, vs, ks, ts, b = d["m"], d["vs"], d["ks"], d["ts"], d["base"]
    emoji, label, why = classify(d)
    hedging = emoji != "🟢"
    L = [f"*{emoji} 변동성 브리핑 — {m['date']} 종가 기준*",
         "_변동성·보험료 관점의 읽기입니다. 방향 예측이나 매매 권유가 아닙니다._",
         *([f"⚠️ 데이터 날짜 확인: {' · '.join(d['freshness'])}"] if d.get("freshness") else []),
         f"상태: *{label}*" + (f"  ({' · '.join(why)})" if why else ""),
         f"SPX {m['spx']:,.0f} ({m['spx_1d']:+.2f}%, 20일 고점 대비 {m['spx_from_high_20d']:+.1f}%)"]
    pre = d.get("pre")
    if pre:
        bits = []
        if "es" in pre:
            bits.append(f"ES {pre['es']:,.0f} (종가 이후 {pre['es_chg']:+.2f}%, {pre['es_time']})")
        if "vix" in pre:
            bits.append(f"VIX {pre['vix']:.2f} (종가 대비 {pre['vix'] - m['vix']:+.2f}, {pre['vix_time']})")
        L.append("프리마켓: " + " · ".join(bits))
    L.append("")

    # ① 보험 → 딜러 short gamma → 하방 증폭
    L.append("*① 보험과 하방 증폭*")
    L.append(f"• 보험: SKEW {m['skew']:.1f} (5일 {m['skew_5d']:+.1f}, 1년 {m['skew_pct']:.0%}) · "
             f"COR90D {m['cor90d']:.1f} (5일 {m['cor90d_5d']:+.1f})")
    amp = amplifier(d)
    if amp:
        on, desc = amp
        verdict = ("하방 증폭 구조 ON — 하락 시 딜러 헤지 매도가 하락을 키울 수 있음" if on
                   else "증폭 구조 OFF — 딜러 헤지가 변동을 흡수하는 쪽")
        L.append(f"• 딜러: {desc} → {verdict}")
    else:
        L.append("• 딜러: GEX 스냅샷 없음")
    pc = d.get("pc")
    if pc:
        L.append(f"• 보험 거래량 (풋/콜): SPX {pc['spx']:.2f} (5일 {pc['spx_5d']:.2f}, 20일 {pc['spx_20d']:.2f}) · "
                 f"Equity {pc['equity']:.2f} (5일 {pc['equity_5d']:.2f}, 20일 {pc['equity_20d']:.2f})")
    cheap = "보험이 실제 위험보다 싸다 — 실현변동성이 옵션 가격을 앞지름" if m["vrp"] < 0 else         ("보험료 비쌈" if m["vrp_pct"] >= 0.8 else "보험료 보통" if m["vrp_pct"] >= 0.3 else "보험료 쌈")
    L.append(f"• 보험료 수준 (VRP): VIX − 20일 실현 {m['rv20']:.1f} = {m['vrp']:+.1f}pt "
             f"(5일 {m['vrp_5d']:+.1f}, 1년 {m['vrp_pct']:.0%}) → {cheap}")
    rp = m["vvix_resid_pct"]
    vv_lbl = ("비쌈 — 꼬리 헤지는 VIX 콜보다 SPX 풋(스프레드)이 상대적으로 유리" if rp >= VVIX_RICH
              else "쌈 — VIX 콜 헤지가 상대적으로 저렴" if rp <= VVIX_CHEAP else "보통")
    L.append(f"• VIX 옵션 보험료 (VIX 대비 VVIX, 잔차 1년 {rp:.0%}): {vv_lbl} · 방향 신호 아님")

    # ② 이벤트 맥락
    L.append("*② 이벤트 맥락*")
    ev = " · ".join(e["ko"] for e in d["events"]) or "가까운 이벤트 없음"
    L.append(f"• {ev}")
    short_fear = m["vix9d_vix"] > 1
    L.append(f"• VIX9D/VIX {m['vix9d_vix']:.2f} (5일 {m['vix9d_vix_5d']:+.2f})"
             + (" → 1 초과: 며칠 안의 이벤트에 헤지가 몰림" if short_fear else " → 단기 이벤트 공포 크지 않음"))
    if hedging and d["events"]:
        L.append("• 이벤트 헤지가 섞였을 수 있음 → 이벤트 후 SKEW가 풀리는지 확인")

    # ③ 과거 확률
    L.append("*③ 과거 확률 (신호 과신 방지)*")
    L.append(f"• 2000~, VIX±10% & {b['band']} ({b['n']}일, 독립 구간 {b['n_ep']}개), 10일 내 하락: "
             f"−2% {b['p2']:.0%} (같은 VIX대 전체 {b['p2_all']:.0%}) · "
             f"−5% {b['p5']:.0%} (같은 VIX대 전체 {b['p5_all']:.0%})")

    def _pp(v):
        return "–" if v is None or not np.isfinite(v) else f"{v:.0%}"
    L.append(f"• −2% 기준 시기별: ~2019 {_pp(b['p2_pre'])} (전체 {_pp(b['p2_all_pre'])}) · "
             f"2020~ {_pp(b['p2_post'])} (전체 {_pp(b['p2_all_post'])}) — 한쪽 시기에만 보이는 차이는 규칙이 아닙니다")

    # 스트레스 / 기타 지표
    L += ["", "*지표*",
          f"• VIX {m['vix']:.2f} (5일 {m['vix_5d']:+.2f}) · VIX9D {m['vix9d']:.2f} · "
          f"VIX/VIX3M {m['vix_vix3m']:.2f} · VVIX {m['vvix']:.1f} (5일 {m['vvix_5d']:+.1f}, 1년 {m['vvix_pct']:.0%})"
          ]
    if vs:
        stale = f" ⚠️ {d['vx_stale']} 스냅샷" if d["vx_stale"] else ""
        L.append(f"• VX 곡선 {vs['shape']} (M1 {vs['front']:.2f}, M2−M1 {vs['spread_2_1']:+.2f}){stale}")
    c = d["credit"]
    L.append(f"• 신용 HY {c['hy']:.0f}bp · CCC−B {c['gap']:.0f}bp" + ("" if c.get("live") else " (스냅샷)")
             + (f" · MOVE {d['move']['value']:.0f} ({d['move']['pct']:.0f}%ile)" if d["move"] else "")
             + f" · COR1M {m['cor1m']:.1f}")
    if ks:
        base = ks["base_pct"].get(ud.KELLY_DEFAULT)
        L.append(f"• 대시보드: 위험신호 {ud.EMOJI[ks['state']]} · ¾ Kelly 기본 비중 {base}% · "
                 f"전술 {ts['label_ko']}")
    return "\n".join(L)


# ============================================================
# Claude commentary
# ============================================================
COMMENTARY_SYSTEM = """당신은 변동성 지표를 읽는 옵션 투자자의 아침 브리핑을 돕습니다.
이 브리핑은 변동성과 보험료(옵션 프리미엄·스큐·신용 스프레드·채권 변동성)의 관점에만 집중합니다.
실적·밸류에이션·뉴스·거시 전망 같은 다른 관점은 다루지 않습니다.
주어진 JSON 지표만 근거로 한국어 3~5줄 해설을 씁니다. 아래 세 관점으로 읽습니다.

1. 보험과 하방 증폭: 보험 수요(SKEW·COR90D 상승)는 사고 예고가 아니라 '큰손들이 이미 대비 중'이라는
   조심해야 할 신호입니다. 큰손이 산 풋은 주로 딜러가 팔았고, 딜러는 하방에서 short gamma라
   가격이 떨어질수록 헤지 매도를 늘립니다. 그래서 GEX가 short이고 지수가 flip 아래면
   보험이 많다는 사실 자체가 하락을 키우는 구조가 됩니다. amp 필드로 이 구조가 켜져 있는지 말합니다.
2. 이벤트 맥락: 누가 왜 샀는지는 SKEW만으로 알 수 없습니다. events의 FOMC·어닝 시즌·만기가 가까우면
   이벤트 헤지가 섞였을 수 있고, 이벤트 헤지는 이벤트가 지나면 풀립니다. 그 가능성을 짚습니다.
3. 과거 확률: 보험 신호만으로 하락을 예측할 수는 없습니다. base 필드의
   −2%·−5% 확률을 같은 VIX대 전체(p2_all·p5_all)와 비교해, 신호의 신뢰도를 과장하지 않습니다.

보험 지표는 가격(SKEW·COR90D), 거래량(pc: 풋/콜 비율), 보험료 수준(m.vrp: VIX − 실현변동성)을 함께 봅니다.
VRP가 음수면 실현변동성이 옵션 가격을 앞지른 상태로, 보험이 위험을 따라가지 못한다는 뜻입니다.
m.vvix_resid_pct는 VIX 수준 대비 VVIX(VIX 옵션 보험료)가 얼마나 비싼지입니다. 어떤 보험(VIX 콜 vs SPX 풋)이
상대적으로 싼지를 말할 때만 쓰고, 방향이나 급등 예측 근거로 쓰지 않습니다(과거 데이터에서 예측력 없음).
m.vix9d_vix가 1을 넘으면 단기 이벤트 헤지가 몰렸다는 뜻이라 2번 관점과 연결합니다.
그 밖에: 보험 수요와 실제 스트레스(VIX/VIX3M·VX 곡선·VVIX)를 구분하고, 지난 5일 변화를 짚습니다.
방향 예측이나 매매 권유는 하지 않습니다. 마크다운 제목·목록 없이 짧은 문장만 씁니다.
JSON 필드 이름(amp, vrp, pc, base 등)을 그대로 쓰지 말고 '하방 증폭 구조', '풋/콜 비율'처럼 우리말로 씁니다.
선물 만기는 '1·2월물'이 아니라 '근월물·차월물'로 씁니다."""


def playbook_section() -> str:
    try:
        return ("\n\n아래는 현재 playbook입니다. 신호 해석과 과거 발견은 이 내용을 따릅니다.\n\n"
                + PLAYBOOK.read_text(encoding="utf-8"))
    except OSError:
        return ""


def commentary(d: dict) -> str | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
    except ImportError:
        print("  [WARN] anthropic SDK not installed; commentary skipped")
        return None
    payload = {k: d[k] for k in ("m", "cs", "vs", "ks", "ts", "credit", "move", "gex", "base", "events", "pre", "pc")}
    amp = amplifier(d)
    payload["amp"] = {"on": amp[0], "desc": amp[1]} if amp else None
    payload["state"] = classify(d)[1]
    try:
        client = anthropic.Anthropic()
        resp = client.beta.messages.create(
            model=CLAUDE_MODEL,
            # Thinking is always on for this model and counts toward max_tokens.
            max_tokens=4000,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default"},
            system=COMMENTARY_SYSTEM + playbook_section(),
            messages=[{"role": "user", "content": _json(payload)}],
        )
    except anthropic.APIStatusError as e:
        print(f"  [WARN] Claude API {e.status_code}: {e.message}")
        return None
    except anthropic.APIConnectionError as e:
        print(f"  [WARN] Claude API connection failed: {e}")
        return None
    except Exception as e:  # noqa: BLE001 — commentary is optional; never block the brief
        print(f"  [WARN] commentary failed ({type(e).__name__}: {e})")
        return None
    if resp.stop_reason in ("refusal", "max_tokens"):
        print(f"  [WARN] commentary dropped (stop_reason={resp.stop_reason})")
        return None
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    return text or None


# ============================================================
# Chart
# ============================================================
# Validated default categorical slots (dataviz palette) + neutral ink.
C_BLUE, C_ORANGE, C_AQUA = "#2a78d6", "#eb6834", "#1baf7a"
C_CRIT, INK, MUTED, GRID, SURF = "#d03b3b", "#1f1f1e", "#6b6a64", "#e6e5e0", "#fcfcfb"


def render_chart(d: dict, days: int = 60) -> Path:
    """Three stacked panels, one per lens, each annotated with what the
    briefing claims: SPX vs the GEX flip (amplifier), SKEW vs its 1-year
    90th percentile (insurance price), VIX9D/VIX/VIX3M (event hedges +
    stress). English labels — CI runners have no Korean font."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    s = d["_series"]
    spx = s["SPX"].dropna().iloc[-days:]
    t0, last = spx.index[0], spx.index[-1]
    skew_all = s["SKEW"].dropna()
    skew = skew_all.loc[t0:]
    p90 = skew_all.rolling(252).quantile(0.9).loc[t0:]
    vix, v9, v3 = (s[k].dropna().loc[t0:] for k in ("VIX", "VIX9D", "VIX3M"))
    m, g = d["m"], d["gex"]

    fig, axes = plt.subplots(3, 1, figsize=(10, 9.5), sharex=True,
                             gridspec_kw={"height_ratios": [1.2, 1, 1]})
    fig.patch.set_facecolor(SURF)
    for ax in axes:
        ax.set_facecolor(SURF)
        ax.grid(axis="y", color=GRID, lw=0.8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=MUTED, labelsize=9)

    def end_label(ax, y, txt, color):
        ax.annotate(txt, (last, y), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=INK,
                    bbox=dict(boxstyle="round,pad=0.2", fc=SURF, ec=color, lw=1))

    # 1 — SPX vs GEX flip
    ax = axes[0]
    ax.plot(spx.index, spx, color=C_BLUE, lw=2)
    ax.scatter([last], [spx.iloc[-1]], color=C_BLUE, s=36, zorder=3, ec=SURF, lw=2)
    end_label(ax, spx.iloc[-1], f"SPX {spx.iloc[-1]:,.0f}", C_BLUE)
    title = "1  SPX vs dealer gamma flip"
    if g:
        ax.axhline(g["flip"], color=MUTED, lw=1.2, ls="--")
        end_label(ax, g["flip"], f"GEX flip {g['flip']:,.0f}", MUTED)
        if g["regime"] == "short" and spx.iloc[-1] < g["flip"]:
            ax.axhspan(min(spx.min(), g["flip"]) * 0.995, g["flip"], color=C_CRIT, alpha=0.06)
            ax.text(0.01, 0.04, "Shaded: below flip + short gamma = dealer hedging amplifies declines",
                    transform=ax.transAxes, fontsize=9, color=C_CRIT,
                    bbox=dict(boxstyle="round,pad=0.25", fc=SURF, ec="none"))
        title += f"   (GEX {g['net_bn']:+.1f}B, {g['regime']})"
    ax.set_title(title, loc="left", fontsize=11, color=INK, fontweight="bold")

    # 2 — SKEW vs its 1-year 90th percentile
    ax = axes[1]
    ax.plot(skew.index, skew, color=C_ORANGE, lw=2)
    ax.plot(p90.index, p90, color=MUTED, lw=1.2, ls="--")
    ax.scatter([skew.index[-1]], [skew.iloc[-1]], color=C_ORANGE, s=36, zorder=3, ec=SURF, lw=2)
    end_label(ax, skew.iloc[-1], f"SKEW {skew.iloc[-1]:.1f}", C_ORANGE)
    end_label(ax, p90.iloc[-1], f"1y 90th pct {p90.iloc[-1]:.0f}", MUTED)
    if len(skew) > 6:
        ax.annotate(f"{m['skew_5d']:+.1f} in 5 sessions",
                    xy=(skew.index[-1], skew.iloc[-1]), xytext=(skew.index[-7], skew.iloc[-1]),
                    fontsize=9, color=INK, ha="right", va="center",
                    arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
    ax.set_title("2  Insurance price: SKEW (OTM put demand)", loc="left",
                 fontsize=11, color=INK, fontweight="bold")

    # 3 — VIX term: 9-day / 30-day / 3-month
    ax = axes[2]
    for ser, c, name in ((v9, C_AQUA, "VIX9D"), (vix, C_BLUE, "VIX"), (v3, C_ORANGE, "VIX3M")):
        ax.plot(ser.index, ser, color=c, lw=2, label=name)
    ax.legend(loc="upper left", frameon=False, fontsize=9, ncol=3, labelcolor=INK)
    end_label(ax, vix.iloc[-1],
              f"VIX9D/VIX {m['vix9d_vix']:.2f}\nVIX/VIX3M {m['vix_vix3m']:.2f}", C_BLUE)
    ax.set_title("3  Short-dated fear vs term (VIX9D > VIX = hedges crowd into the next days)",
                 loc="left", fontsize=11, color=INK, fontweight="bold")

    # Upcoming events (FOMC, expiries) as dotted markers past the last close
    for e in d.get("events", []):
        if not e.get("date") or not e.get("en"):
            continue
        dt = pd.Timestamp(e["date"])
        if last < dt <= last + pd.Timedelta(days=21):
            for a in axes:
                a.axvline(dt, color=MUTED, lw=0.8, ls=":")
            axes[2].text(dt, axes[2].get_ylim()[0], f" {e['en']} {dt:%m/%d}",
                         fontsize=8, color=MUTED, va="bottom", rotation=90)
    axes[2].set_xlim(t0, last + pd.Timedelta(days=24))
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))

    fig.suptitle(f"Volatility briefing  |  close {m['date']}", x=0.01, ha="left",
                 fontsize=13, color=INK, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 0.86, 0.97))
    CHART_DIR.mkdir(exist_ok=True)
    out = CHART_DIR / f"{m['date']}_{datetime.now(timezone.utc):%H%M}.png"
    fig.savefig(out, dpi=110, facecolor=SURF)
    plt.close(fig)
    return out


# ============================================================
# Send
# ============================================================
def slack_payload(text: str, image_url: str | None, date: str) -> dict:
    """Section blocks cap at 3000 chars, so split on paragraphs."""
    blocks, chunk = [], ""
    for para in text.split("\n\n"):
        if chunk and len(chunk) + len(para) + 2 > 2900:
            blocks.append(chunk)
            chunk = ""
        chunk = f"{chunk}\n\n{para}" if chunk else para
    if chunk:
        blocks.append(chunk)
    out = [{"type": "section", "text": {"type": "mrkdwn", "text": b[:2990]}} for b in blocks]
    if image_url:
        # Chart right after the headline + lens sections, before the commentary
        out.insert(1, {"type": "image", "image_url": image_url,
                       "alt_text": f"Volatility briefing chart {date}"})
    return {"text": text.split("\n", 1)[0], "blocks": out}


def post_slack(payload: dict) -> None:
    """Slack fetches image_url while validating the post and rejects the
    whole message (invalid_blocks) if it can't — e.g. raw CDN lag after the
    push. Retry once without the image so the brief still goes out."""
    url = os.environ["SLACK_WEBHOOK_URL"]

    def send(p: dict) -> None:
        req = urllib.request.Request(url, data=json.dumps(p).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            r.read()

    try:
        send(payload)
    except urllib.error.HTTPError as e:
        blocks = [b for b in payload.get("blocks", []) if b.get("type") != "image"]
        if len(blocks) == len(payload.get("blocks", [])):
            raise
        print(f"  [WARN] Slack rejected the post ({e.code}); retrying without the chart")
        send({**payload, "blocks": blocks})


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="print + render chart locally")
    mode.add_argument("--stage", action="store_true",
                      help="build, render chart, log, write the Slack payload to PENDING (CI step 1)")
    mode.add_argument("--send-pending", action="store_true",
                      help="post PENDING to Slack (CI step 2, after the chart is pushed)")
    args = ap.parse_args()

    if args.send_pending:
        if not PENDING.exists():
            print("Nothing pending.")
            return
        post_slack(json.loads(PENDING.read_text(encoding="utf-8")))
        PENDING.unlink()
        print("Sent to Slack.")
        return

    if not should_send_now(os.environ.get("BRIEF_SCHEDULE")):
        print("Not 07:30 New York time for this cron slot — skipping.")
        return

    d = collect()
    date = d["m"]["date"]
    # A holiday morning and the next session's morning read the same close;
    # don't re-brief (and don't overwrite that day's log). Manual runs force.
    force = os.environ.get("BRIEF_FORCE") == "1"
    if args.stage and (LOG_DIR / f"{date}.json").exists() and not force:
        note_txt = (f"📭 새 미국장 종가가 없습니다 — 마지막 브리핑은 {date} 종가 기준입니다 "
                    f"(휴장일이거나 Cboe 미갱신).")
        PENDING.write_text(_json({"text": note_txt}), encoding="utf-8")
        print(note_txt)
        return
    text = build_text(d)
    note = commentary(d)
    if note:
        text += "\n\n*해설 (Claude)*\n" + note
    text += f"\n\n<{SITE_URL}|대시보드 열기>"
    print(text)

    chart = None
    try:
        chart = render_chart(d)
        print(f"Chart: {chart}")
    except Exception as e:  # noqa: BLE001
        print(f"  [WARN] chart failed ({e}); sending text only")

    if args.stage:
        url = f"{RAW_URL}/{chart.relative_to(ROOT).as_posix()}" if chart else None
        PENDING.write_text(_json(slack_payload(text, url, date)), encoding="utf-8")
        write_log(d, text, note)
    elif not args.dry_run:
        # One-shot local send: no pushed chart to point at, so text only.
        post_slack(slack_payload(text, None, date))
        print("Sent to Slack.")
        write_log(d, text, note)


def write_log(d: dict, text: str, note: str | None) -> None:
    emoji, label, why = classify(d)
    amp = amplifier(d)
    rec = {
        "data_date": d["m"]["date"],
        "sent_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "state": {"emoji": emoji, "label": label, "why": why},
        "amp_on": amp[0] if amp else None,
        "inputs": {k: d[k] for k in ("m", "cs", "vs", "vvs", "ks", "ts", "credit",
                                       "move", "gex", "base", "events", "pre", "pc", "freshness")},
        "vx_stale": d["vx_stale"],
        "commentary": note,
        "model": CLAUDE_MODEL if note else None,
        "text": text,
        "outcome": None,   # filled in later by the scorer
    }
    LOG_DIR.mkdir(exist_ok=True)
    path = LOG_DIR / f"{d['m']['date']}.json"
    if path.exists():   # forced re-run: keep any outcome already scored
        try:
            rec["outcome"] = json.loads(path.read_text(encoding="utf-8")).get("outcome")
        except ValueError:
            pass
    path.write_text(_json(rec, indent=1), encoding="utf-8")
    print(f"Logged: {path}")


if __name__ == "__main__":
    main()
