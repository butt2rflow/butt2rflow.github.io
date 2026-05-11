#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily live-dashboard updater.

Pulls fresh end-of-day data from yfinance (Cboe COR + SKEW indices) and
the Cboe VIX-futures settlement CSV, regenerates two charts, and patches
the home pages (index.ko.md, index.en.md) with the latest signals.

Charts use English labels so they render on any machine without Korean
fonts; surrounding markdown stays in the page's language.

Run from project root:
    venv/Scripts/python.exe scripts/update_dashboard.py
"""
from __future__ import annotations

import io
import json
import re
import shutil
import urllib.request
from pathlib import Path

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_KO = ROOT / "docs" / "assets" / "diagrams"
OUT_EN = ROOT / "docs" / "assets" / "diagrams_en"

matplotlib.rcParams["axes.unicode_minus"] = False
plt.rcParams.update({"figure.facecolor": "white"})

LOOKBACK_MONTHS = 6

# Kelly × Vol — f* = (μ−r)/σ² with σ = VIX/100 (annualized forward-looking),
# capped at 100% (no leverage suggestion for retail audience).
EQUITY_PREMIUM = 0.05
KELLY_CAP = 1.00
KELLY_FRACTIONS = [("quarter", 0.25, "Quarter (¼)"),
                   ("half",    0.50, "Half (½)"),
                   ("full",    1.00, "Full")]
# Multiplicative discount profiles applied per risk-signal group. The JS
# toggle on the dashboard reads these via data attributes so the user can
# pick a sensitivity level — Python only ships base values + group states.
RISK_DISCOUNT_PROFILES = {
    "loose":    {"ok": 1.00, "caution": 0.95, "danger": 0.85},
    "standard": {"ok": 1.00, "caution": 0.90, "danger": 0.75},
    "tight":    {"ok": 1.00, "caution": 0.85, "danger": 0.65},
}
RISK_DISCOUNT_DEFAULT = "standard"

# Capital layering — the Cash card's percentages apply to the MAIN portion;
# the Tactical bucket is a separate reserve sized at TACTICAL_FRAC of total.
# JS composes the true total equity = MAIN × kelly_eq + TACTICAL × deploy.
MAIN_FRAC = 0.80
TACTICAL_FRAC = 0.20

# Cboe publishes clean CSVs at this pattern; way more reliable than yfinance
# for these indices (yfinance returns 1-row history for COR* indices).
CBOE_INDEX_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{}_History.csv"
TENOR_INDICES = ["COR1M", "COR3M", "COR6M", "COR9M", "COR1Y"]
# COR3M doubles as the ATM baseline on the Delta Skew chart (Cboe doesn't
# publish a COR3MD index — the 50-delta ATM is COR3M itself).
SKEW_INDICES = ["COR10D", "COR30D", "COR3M", "COR70D", "COR90D", "SKEW"]
SKEW_RENAME = {"COR3M": "COR3MD"}

CBOE_SETTLEMENT_URL = "https://www.cboe.com/us/futures/market_statistics/settlement/csv/"


# ============================================================
# Data fetching
# ============================================================
def _fetch_cboe_index(name: str) -> pd.Series:
    """Pull the full daily Close history for a Cboe index from the CDN CSV."""
    url = CBOE_INDEX_URL.format(name)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            df = pd.read_csv(io.BytesIO(r.read()))
    except Exception as e:  # noqa: BLE001
        print(f"  [WARN] {name}: {e}")
        return pd.Series(dtype=float)

    df["DATE"] = pd.to_datetime(df["DATE"])
    if "CLOSE" in df.columns:
        col = "CLOSE"
    else:
        # SKEW.csv has only one numeric column called by the index name
        candidates = [c for c in df.columns if c.upper() not in {"DATE"}]
        col = candidates[-1] if candidates else df.columns[-1]
    s = pd.Series(pd.to_numeric(df[col], errors="coerce").values, index=df["DATE"])
    return s.dropna()


def _trim_to_lookback(df: pd.DataFrame) -> pd.DataFrame:
    cutoff = pd.Timestamp.now() - pd.DateOffset(months=LOOKBACK_MONTHS)
    return df[df["DATE"] >= cutoff].reset_index(drop=True)


def fetch_cor_skew():
    tenor_data = {name: _fetch_cboe_index(name) for name in TENOR_INDICES}
    tenor = pd.DataFrame(tenor_data)
    tenor.index.name = "DATE"
    tenor = tenor.dropna(how="all").reset_index()

    skew_data = {SKEW_RENAME.get(name, name): _fetch_cboe_index(name) for name in SKEW_INDICES}
    skew = pd.DataFrame(skew_data)
    skew.index.name = "DATE"
    skew = skew.dropna(how="all").reset_index()

    return _trim_to_lookback(tenor), _trim_to_lookback(skew)


def fetch_vix_futures():
    """Pull today's Cboe settlement CSV and return monthly VX contracts."""
    req = urllib.request.Request(CBOE_SETTLEMENT_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        df = pd.read_csv(io.BytesIO(r.read()))

    monthly_pat = re.compile(r"^VX/[A-Z]\d+$")
    vx = df[(df["Product"] == "VX") & df["Symbol"].astype(str).str.match(monthly_pat)].copy()
    vx["Expiration Date"] = pd.to_datetime(vx["Expiration Date"])
    vx["Price"] = pd.to_numeric(vx["Price"], errors="coerce")
    vx = vx.dropna(subset=["Price"]).sort_values("Expiration Date").reset_index(drop=True)

    today = pd.Timestamp.now(tz="US/Eastern").normalize().tz_localize(None)
    vx["DTE"] = (vx["Expiration Date"] - today).dt.days
    vx = vx[vx["DTE"] >= 0].reset_index(drop=True)
    return vx


def fetch_vix_history() -> pd.Series:
    return _fetch_cboe_index("VIX")


def fetch_vvix_history() -> pd.Series:
    """Cboe VVIX — implied volatility of VIX itself."""
    return _fetch_cboe_index("VVIX")


def compute_volvol_df(vvix: pd.Series, vix: pd.Series) -> pd.DataFrame:
    """VolVol indicator from the 2022-08-28 series article:
    ratio = VVIX / VIX, smoothed with 5-day MA, framed by 20-day BB (±2σ).
    Cross of 5DMA above/below the BB middle band is the signal."""
    df = pd.DataFrame({"VVIX": vvix, "VIX": vix}).dropna()
    df["ratio"] = df["VVIX"] / df["VIX"]
    df["ma5"] = df["ratio"].rolling(5).mean()
    df["ma20"] = df["ratio"].rolling(20).mean()
    std20 = df["ratio"].rolling(20).std()
    df["bb_upper"] = df["ma20"] + 2 * std20
    df["bb_lower"] = df["ma20"] - 2 * std20
    return df


# Number of past trading days to keep in the rolling VIX TS animation.
# Each daily PNG is ~80–150 KB, so 365 days ≈ 30–50 MB in repo. GitHub
# repos handle up to ~1 GB comfortably, so feel free to extend if you
# want multi-year scrubbing.
VIX_HISTORY_RETENTION_DAYS = 365


def archive_vix_history(today_chart: Path, data_date: str) -> None:
    """Copy the VIX TS chart to docs/assets/diagrams[_en]/vix_history/<data_date>.png,
    then prune anything older than VIX_HISTORY_RETENTION_DAYS, then write
    a manifest.json the homepage's JS player reads.

    `data_date` should be the Cboe settlement date the chart represents
    (not local wall-clock today). On weekends/holidays the settlement CSV
    still serves Friday's data, so using the wall-clock date would file
    stale data under a misleading name."""
    for parent in [OUT_KO, OUT_EN]:
        archive_dir = parent / "vix_history"
        archive_dir.mkdir(parents=True, exist_ok=True)
        dst = archive_dir / f"{data_date}.png"
        try:
            shutil.copy2(today_chart, dst)
        except Exception as e:  # noqa: BLE001
            print(f"  [WARN] could not archive {dst}: {e}")
            continue

        # Prune files older than retention window
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=VIX_HISTORY_RETENTION_DAYS)
        kept = []
        for f in sorted(archive_dir.glob("*.png")):
            try:
                file_date = pd.Timestamp(f.stem)
            except ValueError:
                continue  # ignore non-date filenames
            if file_date < cutoff:
                f.unlink()
                print(f"  Pruned: {f.name}")
            else:
                kept.append(f.stem)

        kept = sorted(kept)
        manifest = {
            "dates": kept,
            "latest": kept[-1] if kept else None,
            "retention_days": VIX_HISTORY_RETENTION_DAYS,
        }
        (archive_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  Archive {parent.name}: {len(kept)} days, latest={manifest['latest']}")


# ============================================================
# Charts
# ============================================================
def fetch_spx() -> pd.Series:
    """Pull S&P 500 close history from Cboe (no auth needed)."""
    s = _fetch_cboe_index("SPX")
    return s


def render_cor_skew(tenor: pd.DataFrame, skew: pd.DataFrame, out_path: Path,
                    spx: pd.Series | None = None):
    # 4 panels now (with SPX paired at top), shared x-axis with date labels
    n_panels = 4 if spx is not None and len(spx) else 3
    fig, axes = plt.subplots(
        n_panels, 1, figsize=(14, 12 if n_panels == 4 else 11), sharex=True,
        gridspec_kw={"height_ratios": [0.7, 1, 1, 0.8] if n_panels == 4 else [1, 1, 0.8]},
    )

    panel = 0
    if n_panels == 4:
        # Trim SPX to lookback window
        cutoff = pd.Timestamp.now() - pd.DateOffset(months=LOOKBACK_MONTHS)
        spx_trim = spx[spx.index >= cutoff]
        axes[panel].plot(spx_trim.index, spx_trim.values, color="#1e40af",
                         linewidth=1.8, label="S&P 500")
        axes[panel].fill_between(spx_trim.index, spx_trim.values, spx_trim.min(),
                                 alpha=0.08, color="#1e40af")
        axes[panel].set_ylabel("S&P 500", fontsize=10)
        axes[panel].set_title("S&P 500 — reference price (paired with vol indicators below)", fontsize=11)
        axes[panel].legend(loc="upper left", fontsize=8)
        axes[panel].grid(alpha=0.3)
        panel += 1
    cor_panel_start = panel
    # Re-bind axes index variables for the rest of the function
    cor_ax = axes[panel]
    skew_ax = axes[panel + 1]
    skew_idx_ax = axes[panel + 2]
    for col, color, lw in [
        ("COR1M", "#F44336", 2), ("COR3M", "#FF9800", 1.5),
        ("COR6M", "#FFC107", 1.2), ("COR9M", "#4CAF50", 1.2),
        ("COR1Y", "#2196F3", 2),
    ]:
        if col in tenor.columns:
            cor_ax.plot(tenor["DATE"], tenor[col], label=col, linewidth=lw, color=color)
    if "COR1M" in tenor.columns and "COR1Y" in tenor.columns:
        cor_ax.fill_between(tenor["DATE"], tenor["COR1M"], tenor["COR1Y"],
                            where=tenor["COR1M"] < tenor["COR1Y"], alpha=0.1, color="green", label="_")
        cor_ax.fill_between(tenor["DATE"], tenor["COR1M"], tenor["COR1Y"],
                            where=tenor["COR1M"] >= tenor["COR1Y"], alpha=0.15, color="red", label="Inverted")
    cor_ax.set_ylabel("Implied Correlation (%)", fontsize=10)
    cor_ax.set_title("Term Structure — COR1M to COR1Y (tightening = caution)", fontsize=11)
    cor_ax.legend(loc="upper left", fontsize=8, ncol=3)
    cor_ax.grid(alpha=0.3)

    for col, color, lw in [
        ("COR10D", "#F44336", 1.2), ("COR30D", "#FF9800", 1.2),
        ("COR3MD", "#FFC107", 1.5), ("COR70D", "#4CAF50", 1.2),
        ("COR90D", "#2196F3", 2),
    ]:
        if col in skew.columns:
            skew_ax.plot(skew["DATE"], skew[col], label=col, linewidth=lw, color=color)
    skew_ax.axhline(50, color="red", ls="--", alpha=0.4, label="COR90D stress (50)")
    skew_ax.set_ylabel("Implied Correlation (%)", fontsize=10)
    skew_ax.set_title("Delta Skew — COR10D to COR90D (COR90D > 50 = stressed)", fontsize=11)
    skew_ax.legend(loc="upper left", fontsize=8, ncol=3)
    skew_ax.grid(alpha=0.3)

    if "SKEW" in skew.columns:
        skew_idx_ax.plot(skew["DATE"], skew["SKEW"], color="#9C27B0", linewidth=2, label="SKEW")
        skew_idx_ax.fill_between(skew["DATE"], skew["SKEW"], 150,
                                 where=skew["SKEW"] > 150, alpha=0.15, color="red")
    skew_idx_ax.axhline(140, color="orange", ls="--", alpha=0.5, label="Caution (140)")
    skew_idx_ax.axhline(150, color="red", ls="--", alpha=0.5, label="High (150)")
    skew_idx_ax.set_ylabel("SKEW Index", fontsize=10)
    skew_idx_ax.set_title("SKEW — tail-risk indicator", fontsize=11)
    skew_idx_ax.legend(loc="upper left", fontsize=8)
    skew_idx_ax.grid(alpha=0.3)

    # x-axis date labels — bi-weekly + minor weekly grid for readability
    last_ax = axes[-1]
    last_ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    last_ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    last_ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    plt.setp(last_ax.get_xticklabels(), rotation=35, ha="right")
    last_ax.tick_params(axis="x", which="major", labelsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def render_vix_term_structure(vx: pd.DataFrame, vix_spot: float, out_path: Path):
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot VIX spot at DTE=0
    if not np.isnan(vix_spot):
        ax.plot([0], [vix_spot], "o", color="#1e40af", markersize=12,
                label=f"VIX spot ({vix_spot:.2f})", zorder=5)

    # Plot futures curve
    ax.plot(vx["DTE"], vx["Price"], "o-", color="#dc2626", linewidth=2,
            markersize=8, label="VIX futures", zorder=4)

    # Annotate each contract
    for _, row in vx.iterrows():
        ax.annotate(
            f"{row['Expiration Date'].strftime('%b')}\n{row['Price']:.2f}",
            xy=(row["DTE"], row["Price"]),
            xytext=(0, 10), textcoords="offset points",
            ha="center", fontsize=8,
        )

    # Determine shape
    front = vx.iloc[0]["Price"] if len(vx) else float("nan")
    back = vx.iloc[-1]["Price"] if len(vx) else float("nan")
    if not np.isnan(vix_spot) and len(vx) >= 2:
        if vix_spot > front:
            shape = "Backwardation"
            shape_color = "#dc2626"
        elif back > front:
            shape = "Contango"
            shape_color = "#16a34a"
        else:
            shape = "Mixed"
            shape_color = "#6b7280"
        ax.text(0.98, 0.05, f"Shape: {shape}", transform=ax.transAxes,
                fontsize=14, ha="right", va="bottom", fontweight="bold",
                bbox=dict(boxstyle="round", facecolor=shape_color, alpha=0.2,
                          edgecolor=shape_color))

    ax.set_xlabel("Days to expiration", fontsize=11)
    ax.set_ylabel("VIX futures price", fontsize=11)
    today_str = pd.Timestamp.now(tz="US/Eastern").strftime("%Y-%m-%d")
    ax.set_title(f"VIX Futures Term Structure — settlement {today_str}",
                 fontsize=13, fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(alpha=0.3)
    ax.set_xlim(-15, max(vx["DTE"].max() if len(vx) else 30, 30) + 15)

    # Fixed Y-axis range (17–30) so the visual position of the curve
    # encodes the absolute volatility level day-to-day, not just the
    # shape. Auto-expand only when actual data falls outside.
    Y_MIN_DEFAULT, Y_MAX_DEFAULT = 17.0, 30.0
    all_values = list(vx["Price"].dropna()) if len(vx) else []
    if not np.isnan(vix_spot):
        all_values.append(vix_spot)
    if all_values:
        data_min = min(all_values)
        data_max = max(all_values)
        # Use the wider of (default range) and (data range with margin)
        y_min = min(Y_MIN_DEFAULT, data_min - 1.0)
        y_max = max(Y_MAX_DEFAULT, data_max + 1.0)
    else:
        y_min, y_max = Y_MIN_DEFAULT, Y_MAX_DEFAULT
    ax.set_ylim(y_min, y_max)

    # Annotate "fixed scale" hint at bottom-left, away from legend (top-left)
    # and shape badge (bottom-right)
    ax.text(0.02, 0.04,
            f"Y-axis: fixed at {Y_MIN_DEFAULT:.0f}–{Y_MAX_DEFAULT:.0f}"
            + ("" if (y_min == Y_MIN_DEFAULT and y_max == Y_MAX_DEFAULT)
               else f" (expanded to {y_min:.0f}–{y_max:.0f})"),
            transform=ax.transAxes, fontsize=8, color="#6b7280",
            ha="left", va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor="#d1d5db", alpha=0.85))

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def kelly_weight_at(vix: float, fraction: float) -> float:
    """Kelly-fraction equity weight at given VIX, capped at KELLY_CAP."""
    if vix is None or np.isnan(vix) or vix <= 0:
        return float("nan")
    sigma2 = (vix / 100.0) ** 2
    f_star = EQUITY_PREMIUM / sigma2
    return min(fraction * f_star, KELLY_CAP)


def render_kelly_curve(vix_spot: float, out_path: Path):
    """Three Kelly fractions vs VIX, with current-VIX markers on each curve."""
    vix_range = np.linspace(5, 60, 220)
    colors = {"quarter": "#16a34a", "half": "#0ea5e9", "full": "#7c3aed"}
    fig, ax = plt.subplots(figsize=(12, 4.6))
    for key, frac, label in KELLY_FRACTIONS:
        weights = np.array([kelly_weight_at(v, frac) for v in vix_range]) * 100
        lw = 2.4 if key == "half" else 1.6
        ls = "-" if key == "half" else "--"
        ax.plot(vix_range, weights, color=colors[key], linewidth=lw, linestyle=ls,
                label=f"{label} Kelly")
    if not np.isnan(vix_spot):
        for key, frac, _ in KELLY_FRACTIONS:
            w = kelly_weight_at(vix_spot, frac) * 100
            ax.plot([vix_spot], [w], "o", color=colors[key], markersize=9, zorder=5)
        w_half = kelly_weight_at(vix_spot, 0.5) * 100
        ax.annotate(f"VIX {vix_spot:.1f}\nHalf → {w_half:.0f}%",
                    xy=(vix_spot, w_half), xytext=(12, 10), textcoords="offset points",
                    fontsize=9, color="#0ea5e9",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor="#0ea5e9", alpha=0.9))
    for boundary in (14, 20, 28, 40):
        ax.axvline(boundary, color="#9ca3af", ls=":", linewidth=0.9, alpha=0.5)
    ax.set_xlabel("VIX (forward-looking σ × 100)", fontsize=10)
    ax.set_ylabel("Equity weight — cash = 100% − equity (%)", fontsize=10)
    ax.set_title(f"Kelly × VIX — equity weight curves (μ−r = {EQUITY_PREMIUM*100:.0f}%, σ = VIX/100)",
                 fontsize=11)
    ax.set_xlim(5, 60)
    ax.set_ylim(0, 105)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def render_volvol(vv: pd.DataFrame, out_path: Path):
    """VolVol = VVIX/VIX with 5DMA and 20-day Bollinger Bands."""
    cutoff = pd.Timestamp.now() - pd.DateOffset(months=LOOKBACK_MONTHS)
    s = vv[vv.index >= cutoff]

    fig, ax = plt.subplots(figsize=(12, 4.2))
    ax.fill_between(s.index, s["bb_lower"], s["bb_upper"],
                    color="#a78bfa", alpha=0.12, label="20-day BB (±2σ)")
    ax.plot(s.index, s["ratio"], color="#9ca3af", linewidth=1, linestyle=":",
            label="VVIX/VIX (raw)", alpha=0.7)
    ax.plot(s.index, s["ma20"], color="#6b7280", linewidth=1, linestyle="--",
            label="BB middle (20-day MA)")
    ax.plot(s.index, s["ma5"], color="#7c3aed", linewidth=2,
            label="VolVol (5-day MA)")
    ax.set_ylabel("VVIX / VIX", fontsize=10)
    ax.set_title("VolVol = VVIX / VIX — 5DMA above middle = calm, below = stressed",
                 fontsize=11)
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(alpha=0.3)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    ax.tick_params(axis="x", which="major", labelsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


# ============================================================
# Signals
# ============================================================
def compute_cor_skew_signals(tenor, skew):
    latest_t = tenor.dropna(subset=["COR1M", "COR1Y"]).iloc[-1]
    latest_s = skew.dropna(subset=["COR90D", "SKEW"]).iloc[-1]
    spread = latest_t["COR1Y"] - latest_t["COR1M"]
    cor90d = latest_s["COR90D"]
    skew_v = latest_s["SKEW"]

    def state(value, ok_max, caution_max, *, reverse=False):
        if reverse:
            if value < 0:
                return "danger"
            if value < 5:
                return "caution"
            return "ok"
        if value >= caution_max:
            return "danger"
        if value >= ok_max:
            return "caution"
        return "ok"

    return {
        "date": pd.Timestamp(max(latest_t["DATE"], latest_s["DATE"])).strftime("%Y-%m-%d"),
        "spread": spread,
        "spread_state": state(spread, 0, 0, reverse=True),
        "cor1m": latest_t["COR1M"], "cor1y": latest_t["COR1Y"],
        "cor90d": cor90d,
        "cor90d_state": state(cor90d, 40, 50),
        "skew": skew_v,
        "skew_state": state(skew_v, 140, 150),
    }


def compute_volvol_signal(vv: pd.DataFrame):
    """5DMA vs 20-day BB middle: above = ok, below = danger.
    Mark as 'caution' if a crossover happened in the last 5 trading days
    (transition state — series flags this as the actionable signal)."""
    if vv is None or not len(vv):
        return None
    df = vv.dropna(subset=["ma5", "ma20"])
    if not len(df):
        return None
    last = df.iloc[-1]
    ma5, ma20 = float(last["ma5"]), float(last["ma20"])
    state = "ok" if ma5 >= ma20 else "danger"
    recent = df.tail(5)
    diffs = (recent["ma5"] - recent["ma20"]).values
    crossed = any(diffs[i] * diffs[i + 1] < 0 for i in range(len(diffs) - 1))
    if crossed:
        state = "caution"
    return {
        "ratio": float(last["ratio"]),
        "ma5": ma5,
        "ma20": ma20,
        "date": pd.Timestamp(last.name).strftime("%Y-%m-%d"),
        "state": state,
        "crossed": crossed,
    }


def _worst(states):
    """Return worst of a list of states (danger > caution > ok)."""
    order = {"ok": 0, "caution": 1, "danger": 2}
    inv = {v: k for k, v in order.items()}
    return inv[max(order[s] for s in states)] if states else "ok"


def compute_kelly_signal(vix_spot: float, cs: dict | None,
                        vs: dict | None, vvs: dict | None) -> dict | None:
    """Base Kelly weights at three fractions + risk-signal group states.

    The dashboard JS computes the final equity weight at runtime from the
    user-selected fraction × user-selected discount profile, so Python only
    ships the building blocks: base[%] per fraction and the worst-sub-signal
    state per group (ok / caution / danger)."""
    if vix_spot is None or np.isnan(vix_spot) or vix_spot <= 0:
        return None

    cor_skew_state = _worst([cs["spread_state"], cs["cor90d_state"],
                             cs["skew_state"]]) if cs else "ok"
    if vs:
        vix_ts_state = {"backwardation": "danger",
                        "mixed": "caution",
                        "contango": "ok"}.get(vs["shape"], "ok")
    else:
        vix_ts_state = "ok"
    volvol_state = vvs["state"] if vvs else "ok"

    fractions = {}
    for key, frac, _ in KELLY_FRACTIONS:
        fractions[key] = round(kelly_weight_at(vix_spot, frac) * 100)
    overall_state = _worst([cor_skew_state, vix_ts_state, volvol_state])
    return {
        "vix": vix_spot,
        "base_pct": fractions,
        "cor_skew_state": cor_skew_state,
        "vix_ts_state": vix_ts_state,
        "volvol_state": volvol_state,
        "vix_ts_shape": vs["shape"] if vs else None,
        "state": overall_state,
    }


def compute_tactical_signal(vix_hist, cs, spx):
    """Tactical-bucket trigger status — three composite extreme-stress
    conditions, each contributing one tranche (1/3) toward full deployment.

    T1: VIX > 50 sustained 5 trading days (single-day spike doesn't count)
    T2: COR90D > 55 AND SKEW > 150 (cross-asset stress)
    T3: 30-day SPX cumulative drawdown ≥ 20% (price-action capitulation)
    """
    # T1
    if vix_hist is not None and len(vix_hist) >= 5:
        recent_vix = vix_hist.tail(5)
        t1 = bool((recent_vix > 50).all())
        vix_5d_min = float(recent_vix.min())
        vix_now = float(vix_hist.iloc[-1])
    else:
        t1 = False
        vix_5d_min = float("nan")
        vix_now = float("nan")

    # T2
    if cs:
        t2 = bool(cs["cor90d"] > 55 and cs["skew"] > 150)
        cor90d = float(cs["cor90d"])
        skew_v = float(cs["skew"])
    else:
        t2 = False
        cor90d = float("nan")
        skew_v = float("nan")

    # T3
    if spx is not None and len(spx) >= 2:
        window = spx.tail(31)  # 30 trading days plus today
        peak = float(window.max())
        current = float(window.iloc[-1])
        drawdown_pct = (current - peak) / peak * 100
        t3 = drawdown_pct <= -20
    else:
        drawdown_pct = float("nan")
        t3 = False

    n_triggers = int(t1) + int(t2) + int(t3)
    deploy_pct = int(round(n_triggers * 100 / 3))
    state, label_ko, label_en = {
        0: ("ok",       "대기",          "Inactive"),
        1: ("caution",  "1차 발동",      "Tranche 1"),
        2: ("warning",  "2차 발동",      "Tranche 2"),
        3: ("danger",   "Capitulation",  "Capitulation"),
    }[n_triggers]

    return {
        "vix_now": vix_now,
        "vix_5d_min": vix_5d_min,
        "cor90d": cor90d,
        "skew": skew_v,
        "spx_drawdown_30d_pct": drawdown_pct,
        "t1": t1, "t2": t2, "t3": t3,
        "n_triggers": n_triggers,
        "deploy_pct": deploy_pct,
        "state": state,
        "label_ko": label_ko,
        "label_en": label_en,
    }


def compute_vix_signals(vx, vix_spot):
    if len(vx) < 2:
        return None
    front = float(vx.iloc[0]["Price"])
    second = float(vx.iloc[1]["Price"])
    spread_2_1 = second - front
    # Mid-curve spread (V7 - V4) — relevant for VXZ/VIXM mid-term VIX ETFs
    spread_7_4 = None
    if len(vx) >= 7:
        spread_7_4 = float(vx.iloc[6]["Price"]) - float(vx.iloc[3]["Price"])
    # Whole-curve steepness (V7 - V1)
    spread_7_1 = None
    if len(vx) >= 7:
        spread_7_1 = float(vx.iloc[6]["Price"]) - front
    if not np.isnan(vix_spot) and vix_spot > front:
        shape = "backwardation"
    elif spread_2_1 > 0:
        shape = "contango"
    else:
        shape = "mixed"
    return {
        "vix_spot": vix_spot,
        "front": front,
        "front_expiry": vx.iloc[0]["Expiration Date"].strftime("%Y-%m-%d"),
        "spread_2_1": spread_2_1,
        "spread_7_4": spread_7_4,
        "spread_7_1": spread_7_1,
        "shape": shape,
        "n_contracts": len(vx),
    }


# ============================================================
# Home-page patching
# ============================================================
EMOJI = {"ok": "🟢", "caution": "🟡", "warning": "🟠", "danger": "🔴"}
START_MARK = "<!-- DASHBOARD_START -->"
END_MARK = "<!-- DASHBOARD_END -->"
KO_LABEL = {"ok": "정상", "caution": "경계", "danger": "스트레스"}
EN_LABEL = {"ok": "Normal", "caution": "Caution", "danger": "Stressed"}
SHAPE_KO = {"contango": "콘탱고 (정상)", "backwardation": "백워데이션 (스트레스)", "mixed": "혼합"}
SHAPE_EN = {"contango": "Contango (normal)", "backwardation": "Backwardation (stress)", "mixed": "Mixed"}
SHAPE_EMOJI = {"contango": "🟢", "backwardation": "🔴", "mixed": "🟡"}


VOLVOL_STATE_KO = {"ok": "안도", "caution": "전환", "danger": "긴장"}
VOLVOL_STATE_EN = {"ok": "Calm", "caution": "Transition", "danger": "Stressed"}


def render_kelly_card_ko(ks: dict, diagrams_path: str) -> list[str]:
    """Cash-allocation card HTML — JS toggles compute final equity weight."""
    vix = ks["vix"]
    bp = ks["base_pct"]
    cs_state = ks["cor_skew_state"]
    vts_state = ks["vix_ts_state"]
    vv_state = ks["volvol_state"]
    shape_ko = SHAPE_KO.get(ks["vix_ts_shape"], "—")
    return [
        "### 💰 권장 현금/주식 비중",
        "",
        f'<div class="kelly-card"\n'
        f'     data-vix="{vix:.1f}"\n'
        f'     data-base-quarter="{bp["quarter"]}"\n'
        f'     data-base-half="{bp["half"]}"\n'
        f'     data-base-full="{bp["full"]}"\n'
        f'     data-state-corskew="{cs_state}"\n'
        f'     data-state-vixts="{vts_state}"\n'
        f'     data-state-volvol="{vv_state}">\n'
        f'  <div class="kelly-controls">\n'
        f'    <span class="kelly-label">Kelly:</span>\n'
        f'    <button class="kelly-pill" data-kelly-set="quarter">¼</button>\n'
        f'    <button class="kelly-pill is-active" data-kelly-set="half">½</button>\n'
        f'    <button class="kelly-pill" data-kelly-set="full">Full</button>\n'
        f'    <span class="kelly-divider">·</span>\n'
        f'    <span class="kelly-label">위험 민감도:</span>\n'
        f'    <button class="kelly-pill" data-discount-set="loose">느슨</button>\n'
        f'    <button class="kelly-pill is-active" data-discount-set="standard">기본</button>\n'
        f'    <button class="kelly-pill" data-discount-set="tight">빡빡</button>\n'
        f'  </div>\n'
        f'  <table class="kelly-table">\n'
        f'    <thead><tr><th>단계</th><th>값</th></tr></thead>\n'
        f'    <tbody>\n'
        f'      <tr><td>① Kelly × VIX 베이스 (VIX {vix:.1f})</td>'
        f'<td><strong><span data-kelly-base>{bp["half"]}</span>%</strong></td></tr>\n'
        f'      <tr><td>② COR/SKEW {EMOJI[cs_state]} {KO_LABEL[cs_state]}</td>'
        f'<td>× <span data-kelly-d="corskew">1.00</span></td></tr>\n'
        f'      <tr><td>③ VIX TS {SHAPE_EMOJI.get(ks["vix_ts_shape"], "—")} {shape_ko}</td>'
        f'<td>× <span data-kelly-d="vixts">1.00</span></td></tr>\n'
        f'      <tr><td>④ VolVol {EMOJI[vv_state]} {VOLVOL_STATE_KO[vv_state]}</td>'
        f'<td>× <span data-kelly-d="volvol">1.00</span></td></tr>\n'
        f'      <tr class="kelly-final"><td><strong>권장 비중</strong></td>'
        f'<td><strong>주식 <span data-kelly-equity>{bp["half"]}</span>% / '
        f'현금 <span data-kelly-cash>{100 - bp["half"]}</span>%</strong></td></tr>\n'
        f'    </tbody>\n'
        f'  </table>\n'
        f'</div>',
        "",
        f"![Kelly × VIX 곡선]({diagrams_path}/kelly_curve.png)",
        "",
        "<small>*위 비중은 **메인 포트폴리오 (전체의 80%) 기준** — Tactical reserve(나머지 20%)는 "
        "다음 카드에서 별도 관리, 합산 비중은 Tactical 카드 하단 참조. "
        "Half-Kelly @ μ−r=5%, σ=VIX/100. 위험 민감도 = 그룹별 multiplier "
        "(loose 0.95/0.85 · standard 0.90/0.75 · tight 0.85/0.65). "
        "**교육 목적 · 투자 권유 아님** · "
        "[자세히 →](posts/cash-allocation.md)*</small>",
        "",
        "---",
        "",
    ]


def _initial_composite(ks: dict | None, ts: dict) -> tuple[int, int]:
    """Initial composite total (no discount applied — JS recomputes on load)."""
    kelly_eq = ks["base_pct"]["half"] if ks else 0
    total_eq = min(round(MAIN_FRAC * kelly_eq + TACTICAL_FRAC * ts["deploy_pct"]), 100)
    return total_eq, 100 - total_eq


def render_tactical_card_ko(ts: dict, ks: dict | None = None) -> list[str]:
    """Tactical bucket card — offensive deploy signal + composite total."""
    mark = lambda b: "✅" if b else "❌"  # noqa: E731
    drawdown_str = (f"{ts['spx_drawdown_30d_pct']:+.1f}%"
                    if not np.isnan(ts['spx_drawdown_30d_pct']) else "—")
    vix_disp = (f"{ts['vix_now']:.1f} (5일 최저 {ts['vix_5d_min']:.1f})"
                if not np.isnan(ts['vix_now']) else "—")
    cor_skew_disp = (f"{ts['cor90d']:.1f} / {ts['skew']:.1f}"
                     if not np.isnan(ts['cor90d']) else "—")
    total_eq, total_cash = _initial_composite(ks, ts)
    return [
        "### ⚡ 공격 자본 (Tactical Bucket) — 위기 발동 신호",
        "",
        f'<div class="tactical-card" data-deploy-pct="{ts["deploy_pct"]}" '
        f'data-main-frac="{MAIN_FRAC}" data-tactical-frac="{TACTICAL_FRAC}">',
        '<div class="dash-tight" markdown>',
        "",
        "| 트리거 | 현재 | 충족 |",
        "|:---|---:|:---:|",
        f"| VIX > 50 (5일 지속) | {vix_disp} | {mark(ts['t1'])} |",
        f"| COR90D > 55 + SKEW > 150 | {cor_skew_disp} | {mark(ts['t2'])} |",
        f"| 30일 SPX 누적 −20% | {drawdown_str} | {mark(ts['t3'])} |",
        f"| **공격 자본 (전체의 20%)** | **{EMOJI[ts['state']]} {ts['deploy_pct']}% 투입 ({ts['label_ko']})** | — |",
        "",
        "</div>",
        "",
        f'<div class="tactical-composite">'
        f'<strong>📊 전체 합산 (메인 80% + 공격 20%)</strong>: '
        f'<strong>주식 <span data-total-equity>{total_eq}</span>% / '
        f'현금 <span data-total-cash>{total_cash}</span>%</strong>'
        f'</div>',
        "</div>",
        "",
        "<small>*공격 자본(전체의 20%)은 *시간 에지를 행사하는 위기 매수 현금*으로 별도 운용. "
        "충족 트리거 수만큼 1/3씩 단계 투입 (laddered deploy). "
        "위 합산은 메인 카드 토글 선택에 따라 실시간 갱신 · "
        "[자세히 →](posts/cash-allocation.md)*</small>",
        "",
        "---",
        "",
    ]


def render_tactical_card_en(ts: dict, ks: dict | None = None) -> list[str]:
    mark = lambda b: "✅" if b else "❌"  # noqa: E731
    drawdown_str = (f"{ts['spx_drawdown_30d_pct']:+.1f}%"
                    if not np.isnan(ts['spx_drawdown_30d_pct']) else "—")
    vix_disp = (f"{ts['vix_now']:.1f} (5d min {ts['vix_5d_min']:.1f})"
                if not np.isnan(ts['vix_now']) else "—")
    cor_skew_disp = (f"{ts['cor90d']:.1f} / {ts['skew']:.1f}"
                     if not np.isnan(ts['cor90d']) else "—")
    total_eq, total_cash = _initial_composite(ks, ts)
    return [
        "### ⚡ Tactical Bucket — Offensive Deploy Signal",
        "",
        f'<div class="tactical-card" data-deploy-pct="{ts["deploy_pct"]}" '
        f'data-main-frac="{MAIN_FRAC}" data-tactical-frac="{TACTICAL_FRAC}">',
        '<div class="dash-tight" markdown>',
        "",
        "| Trigger | Now | Fired |",
        "|:---|---:|:---:|",
        f"| VIX > 50 (sustained 5d) | {vix_disp} | {mark(ts['t1'])} |",
        f"| COR90D > 55 AND SKEW > 150 | {cor_skew_disp} | {mark(ts['t2'])} |",
        f"| 30-day SPX drawdown ≥ 20% | {drawdown_str} | {mark(ts['t3'])} |",
        f"| **Tactical reserve (20%)** | **{EMOJI[ts['state']]} {ts['deploy_pct']}% deploy ({ts['label_en']})** | — |",
        "",
        "</div>",
        "",
        f'<div class="tactical-composite">'
        f'<strong>📊 Combined total (Main 80% + Tactical 20%)</strong>: '
        f'<strong>Equity <span data-total-equity>{total_eq}</span>% / '
        f'Cash <span data-total-cash>{total_cash}</span>%</strong>'
        f'</div>',
        "</div>",
        "",
        "<small>*Tactical bucket (20% of total capital) held separately as *offensive cash to monetise the time edge*. "
        "Each fired trigger deploys 1/3 in laddered tranches. "
        "Combined total above updates live with the Main card toggles · "
        "[Read more →](posts/cash-allocation.md)*</small>",
        "",
        "---",
        "",
    ]


def render_section_ko(cs, vs, vvs, ks, ts=None):
    spread_label = "역전" if cs["spread_state"] == "danger" else KO_LABEL[cs["spread_state"]]
    parts = [
        START_MARK,
        '<div class="live-dash" markdown>',
        "",
        "## 📊 라이브 대시보드",
        "",
        f"<small>**{cs['date']} 기준** · 미국 장 마감 후 매일 자동 갱신</small>",
        "",
    ]
    if ks:
        parts += render_kelly_card_ko(ks, "assets/diagrams")
    if ts:
        parts += render_tactical_card_ko(ts, ks)
    if vs:
        parts += [
            "### VIX Futures Term Structure",
            "",
            '<div class="dash-tight" markdown>',
            "",
            "| 항목 | 값 | 상태 |",
            "|:-----|---:|:-----|",
            f"| VIX 현물 | {vs['vix_spot']:.2f} | — |",
            f"| Front (M1, {vs['front_expiry']}) | {vs['front']:.2f} | — |",
            f"| **M2 − M1** (단기) | {vs['spread_2_1']:+.2f} | "
            f"{SHAPE_EMOJI[vs['shape']]} {SHAPE_KO[vs['shape']]} |",
        ]
        if vs.get("spread_7_4") is not None:
            shape74 = "contango" if vs["spread_7_4"] > 0 else ("backwardation" if vs["spread_7_4"] < 0 else "mixed")
            parts.append(
                f"| **M7 − M4** (중기, VXZ 영역) | {vs['spread_7_4']:+.2f} | "
                f"{SHAPE_EMOJI[shape74]} {SHAPE_KO[shape74]} |"
            )
        parts += [
            "",
            "</div>",
            "",
            '<div id="vix-history-player"></div>',
            "",
            "<small>*Cboe 결제 데이터(CFE) 기준. Vixcentral 대안으로 활용 가능 · "
            "지난 1년 곡선을 슬라이더/▶로 재생 가능 · "
            "[해석 가이드 →](posts/vix-term-structure.md)*</small>",
            "",
            "---",
            "",
        ]
    parts += [
        "### COR + SKEW 대시보드",
        "",
        '<div class="dash-tight" markdown>',
        "",
        "| 신호 | 값 | 상태 |",
        "|:-----|---:|:-----|",
        f"| **Term Structure** (COR1Y − COR1M) | {cs['spread']:.1f} | "
        f"{EMOJI[cs['spread_state']]} {spread_label} |",
        f"| **COR90D** (동조화 수준) | {cs['cor90d']:.1f} | "
        f"{EMOJI[cs['cor90d_state']]} {KO_LABEL[cs['cor90d_state']]} |",
        f"| **SKEW** (꼬리 위험) | {cs['skew']:.1f} | "
        f"{EMOJI[cs['skew_state']]} {KO_LABEL[cs['skew_state']]} |",
        "",
        "</div>",
        "",
        "![변동성 대시보드 (S&P 500 페어)](assets/diagrams/vol_dashboard.png)",
        "",
        "<small>*Cboe COR + SKEW 지수로 본 시장 분산 효과와 꼬리 위험 · "
        "[자세히 →](posts/volatility-dashboard.md)*</small>",
        "",
    ]
    if vvs:
        cross_note = " · 최근 5일 내 크로스 발생" if vvs.get("crossed") else ""
        ko_state = {"ok": "안도 (5DMA > 중간선)",
                    "caution": "전환",
                    "danger": "긴장 (5DMA < 중간선)"}[vvs["state"]]
        parts += [
            "---",
            "",
            "### VolVol — VVIX / VIX 비율 지표",
            "",
            '<div class="dash-tight" markdown>',
            "",
            "| 신호 | 값 | 상태 |",
            "|:-----|---:|:-----|",
            f"| **VolVol = VVIX / VIX** (5DMA) | {vvs['ma5']:.3f} | "
            f"{EMOJI[vvs['state']]} {ko_state}{cross_note} |",
            f"| BB 중간선 (20일 이평) | {vvs['ma20']:.3f} | — |",
            "",
            "</div>",
            "",
            "![VolVol 시계열](assets/diagrams/volvol.png)",
            "",
            "<small>*5일 이평선이 20일 볼린저밴드 중간선 위에 있으면 변동성이 줄어드는 안도 국면, "
            "아래면 긴장 국면. 중간선을 가르는 크로스가 시장 심리 전환 신호. "
            "**공식 지표가 아닌 '심리적' 보조 신호** — 단독 매매 판단보다는 "
            "VIX TS·COR/SKEW와 함께 시장 분위기를 읽는 용도 · "
            "[자세히 →](posts/cash-allocation.md)*</small>",
            "",
        ]
    parts += [
        "</div>",
        "",
        "---",
        END_MARK,
    ]
    return "\n".join(parts)


def render_kelly_card_en(ks: dict, diagrams_path: str) -> list[str]:
    vix = ks["vix"]
    bp = ks["base_pct"]
    cs_state = ks["cor_skew_state"]
    vts_state = ks["vix_ts_state"]
    vv_state = ks["volvol_state"]
    shape_en = SHAPE_EN.get(ks["vix_ts_shape"], "—")
    return [
        "### 💰 Suggested Cash / Equity Mix",
        "",
        f'<div class="kelly-card"\n'
        f'     data-vix="{vix:.1f}"\n'
        f'     data-base-quarter="{bp["quarter"]}"\n'
        f'     data-base-half="{bp["half"]}"\n'
        f'     data-base-full="{bp["full"]}"\n'
        f'     data-state-corskew="{cs_state}"\n'
        f'     data-state-vixts="{vts_state}"\n'
        f'     data-state-volvol="{vv_state}">\n'
        f'  <div class="kelly-controls">\n'
        f'    <span class="kelly-label">Kelly:</span>\n'
        f'    <button class="kelly-pill" data-kelly-set="quarter">¼</button>\n'
        f'    <button class="kelly-pill is-active" data-kelly-set="half">½</button>\n'
        f'    <button class="kelly-pill" data-kelly-set="full">Full</button>\n'
        f'    <span class="kelly-divider">·</span>\n'
        f'    <span class="kelly-label">Risk sensitivity:</span>\n'
        f'    <button class="kelly-pill" data-discount-set="loose">Loose</button>\n'
        f'    <button class="kelly-pill is-active" data-discount-set="standard">Standard</button>\n'
        f'    <button class="kelly-pill" data-discount-set="tight">Tight</button>\n'
        f'  </div>\n'
        f'  <table class="kelly-table">\n'
        f'    <thead><tr><th>Step</th><th>Value</th></tr></thead>\n'
        f'    <tbody>\n'
        f'      <tr><td>① Kelly × VIX base (VIX {vix:.1f})</td>'
        f'<td><strong><span data-kelly-base>{bp["half"]}</span>%</strong></td></tr>\n'
        f'      <tr><td>② COR/SKEW {EMOJI[cs_state]} {EN_LABEL[cs_state]}</td>'
        f'<td>× <span data-kelly-d="corskew">1.00</span></td></tr>\n'
        f'      <tr><td>③ VIX TS {SHAPE_EMOJI.get(ks["vix_ts_shape"], "—")} {shape_en}</td>'
        f'<td>× <span data-kelly-d="vixts">1.00</span></td></tr>\n'
        f'      <tr><td>④ VolVol {EMOJI[vv_state]} {VOLVOL_STATE_EN[vv_state]}</td>'
        f'<td>× <span data-kelly-d="volvol">1.00</span></td></tr>\n'
        f'      <tr class="kelly-final"><td><strong>Suggested mix</strong></td>'
        f'<td><strong>Equity <span data-kelly-equity>{bp["half"]}</span>% / '
        f'Cash <span data-kelly-cash>{100 - bp["half"]}</span>%</strong></td></tr>\n'
        f'    </tbody>\n'
        f'  </table>\n'
        f'</div>',
        "",
        f"![Kelly × VIX curve]({diagrams_path}/kelly_curve.png)",
        "",
        "<small>*This mix applies to the **main portfolio (80% of total)** — the Tactical reserve "
        "(remaining 20%) is managed in the next card; combined total appears at the bottom of the Tactical card. "
        "Half-Kelly @ μ−r=5%, σ=VIX/100. Risk sensitivity = per-group multiplier "
        "(loose 0.95/0.85 · standard 0.90/0.75 · tight 0.85/0.65). "
        "**Educational — not investment advice.** "
        "[Read more →](posts/cash-allocation.md)*</small>",
        "",
        "---",
        "",
    ]


def render_section_en(cs, vs, vvs, ks, ts=None):
    spread_label = "Inverted" if cs["spread_state"] == "danger" else EN_LABEL[cs["spread_state"]]
    parts = [
        START_MARK,
        '<div class="live-dash" markdown>',
        "",
        "## 📊 Live Dashboard",
        "",
        f"<small>**As of {cs['date']}** · Auto-updates daily after the US close · "
        "[Framework details →](posts/cash-allocation.md)</small>",
        "",
    ]
    if ks:
        parts += render_kelly_card_en(ks, "assets/diagrams_en")
    if ts:
        parts += render_tactical_card_en(ts, ks)
    if vs:
        parts += [
            "### VIX Futures Term Structure",
            "",
            '<div class="dash-tight" markdown>',
            "",
            "| Field | Value | State |",
            "|:------|------:|:------|",
            f"| VIX spot | {vs['vix_spot']:.2f} | — |",
            f"| Front (M1, {vs['front_expiry']}) | {vs['front']:.2f} | — |",
            f"| **M2 − M1** (short-term) | {vs['spread_2_1']:+.2f} | "
            f"{SHAPE_EMOJI[vs['shape']]} {SHAPE_EN[vs['shape']]} |",
        ]
        if vs.get("spread_7_4") is not None:
            shape74 = "contango" if vs["spread_7_4"] > 0 else ("backwardation" if vs["spread_7_4"] < 0 else "mixed")
            parts.append(
                f"| **M7 − M4** (mid-term, VXZ zone) | {vs['spread_7_4']:+.2f} | "
                f"{SHAPE_EMOJI[shape74]} {SHAPE_EN[shape74]} |"
            )
        parts += [
            "",
            "</div>",
            "",
            '<div id="vix-history-player"></div>',
            "",
            "<small>*Source: Cboe CFE settlement — a reliable alternative to vixcentral · "
            "Use the slider/▶ to scrub through up to 1 year of past curves · "
            "[Reading guide →](posts/vix-term-structure.md)*</small>",
            "",
            "---",
            "",
        ]
    parts += [
        "### COR + SKEW Dashboard",
        "",
        '<div class="dash-tight" markdown>',
        "",
        "| Signal | Value | State |",
        "|:-------|------:|:------|",
        f"| **Term Structure** (COR1Y − COR1M) | {cs['spread']:.1f} | "
        f"{EMOJI[cs['spread_state']]} {spread_label} |",
        f"| **COR90D** (synchronization) | {cs['cor90d']:.1f} | "
        f"{EMOJI[cs['cor90d_state']]} {EN_LABEL[cs['cor90d_state']]} |",
        f"| **SKEW** (tail risk) | {cs['skew']:.1f} | "
        f"{EMOJI[cs['skew_state']]} {EN_LABEL[cs['skew_state']]} |",
        "",
        "</div>",
        "",
        "![Volatility dashboard (paired with S&P 500)](assets/diagrams_en/vol_dashboard.png)",
        "",
        "<small>*Cboe COR + SKEW indices — market diversification and tail-risk view · "
        "[Full guide →](posts/volatility-dashboard.md)*</small>",
        "",
    ]
    if vvs:
        cross_note = " · crossed in last 5 days" if vvs.get("crossed") else ""
        en_state = {"ok": "Calm (5DMA > middle)",
                    "caution": "Transition",
                    "danger": "Stressed (5DMA < middle)"}[vvs["state"]]
        parts += [
            "---",
            "",
            "### VolVol — VVIX / VIX ratio",
            "",
            '<div class="dash-tight" markdown>',
            "",
            "| Signal | Value | State |",
            "|:-------|------:|:------|",
            f"| **VolVol = VVIX / VIX** (5DMA) | {vvs['ma5']:.3f} | "
            f"{EMOJI[vvs['state']]} {en_state}{cross_note} |",
            f"| BB middle (20-day MA) | {vvs['ma20']:.3f} | — |",
            "",
            "</div>",
            "",
            "![VolVol history](assets/diagrams_en/volvol.png)",
            "",
            "<small>*5-day MA above the 20-day BB middle = vol is decompressing (calm regime); "
            "below = vol is building (stressed). A cross through the middle band marks a sentiment shift. "
            "**Not an official index — a 'psychological' confirmation signal**, best read alongside "
            "VIX TS and COR/SKEW rather than as a standalone trading trigger · "
            "[Read more →](posts/cash-allocation.md)*</small>",
            "",
        ]
    parts += [
        "</div>",
        "",
        "---",
        END_MARK,
    ]
    return "\n".join(parts)


def patch_home(path: Path, section: str) -> bool:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START_MARK) + r".*?" + re.escape(END_MARK), re.DOTALL)
    if pattern.search(text):
        new_text = pattern.sub(section, text)
    else:
        fm_match = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
        offset = fm_match.end() if fm_match else 0
        h1_match = re.search(r"\n# .+?\n", text[offset:])
        insert_at = offset + (h1_match.end() if h1_match else 0)
        new_text = text[:insert_at] + "\n" + section + "\n" + text[insert_at:]
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


# ============================================================
# Main
# ============================================================
def main():
    print("Fetching COR + SKEW data...")
    tenor, skew = fetch_cor_skew()
    print(f"  Tenor: {len(tenor)} rows, Skew: {len(skew)} rows")

    print("Fetching VIX futures settlement...")
    try:
        vx = fetch_vix_futures()
        print(f"  VIX futures: {len(vx)} contracts")
    except Exception as e:  # noqa: BLE001
        print(f"  [WARN] Cboe fetch failed: {e}")
        vx = pd.DataFrame()

    print("Fetching VIX + VVIX history...")
    vix_hist = fetch_vix_history()
    vvix_hist = fetch_vvix_history()
    vix_spot = float(vix_hist.iloc[-1]) if len(vix_hist) else float("nan")
    print(f"  VIX history: {len(vix_hist)} rows, spot: {vix_spot:.2f}")
    print(f"  VVIX history: {len(vvix_hist)} rows")
    volvol_df = compute_volvol_df(vvix_hist, vix_hist)
    print(f"  VolVol (ratio rows after align): {len(volvol_df)}")

    print("Fetching S&P 500 reference series...")
    spx = fetch_spx()
    print(f"  SPX history: {len(spx)} rows")

    print("Rendering charts...")
    render_cor_skew(tenor, skew, OUT_KO / "vol_dashboard.png", spx=spx)
    print(f"  Saved: {OUT_KO / 'vol_dashboard.png'}")
    # Same chart (English labels) for both languages
    import shutil
    shutil.copy2(OUT_KO / "vol_dashboard.png", OUT_EN / "vol_dashboard.png")
    print(f"  Copied: {OUT_EN / 'vol_dashboard.png'}")

    if len(volvol_df):
        render_volvol(volvol_df, OUT_KO / "volvol.png")
        print(f"  Saved: {OUT_KO / 'volvol.png'}")
        shutil.copy2(OUT_KO / "volvol.png", OUT_EN / "volvol.png")
        print(f"  Copied: {OUT_EN / 'volvol.png'}")

    print("Computing signals...")
    cs = compute_cor_skew_signals(tenor, skew)
    vs = compute_vix_signals(vx, vix_spot) if len(vx) > 0 else None
    vvs = compute_volvol_signal(volvol_df)
    ks = compute_kelly_signal(vix_spot, cs, vs, vvs)
    ts = compute_tactical_signal(vix_hist, cs, spx)

    if len(vx) > 0:
        render_vix_term_structure(vx, vix_spot, OUT_KO / "vix_term_structure.png")
        print(f"  Saved: {OUT_KO / 'vix_term_structure.png'}")
        shutil.copy2(OUT_KO / "vix_term_structure.png", OUT_EN / "vix_term_structure.png")
        print(f"  Copied: {OUT_EN / 'vix_term_structure.png'}")
        archive_vix_history(OUT_KO / "vix_term_structure.png", cs["date"])

    if ks:
        render_kelly_curve(vix_spot, OUT_KO / "kelly_curve.png")
        print(f"  Saved: {OUT_KO / 'kelly_curve.png'}")
        shutil.copy2(OUT_KO / "kelly_curve.png", OUT_EN / "kelly_curve.png")
        print(f"  Copied: {OUT_EN / 'kelly_curve.png'}")

    print(f"  COR/SKEW: spread={cs['spread']:.2f}, COR90D={cs['cor90d']:.2f}, SKEW={cs['skew']:.2f}")
    if vs:
        print(f"  VIX TS: spot={vs['vix_spot']:.2f}, front={vs['front']:.2f}, "
              f"M2-M1={vs['spread_2_1']:+.2f}, shape={vs['shape']}")
    if vvs:
        print(f"  VolVol: 5DMA={vvs['ma5']:.3f}, BB-mid={vvs['ma20']:.3f}, "
              f"state={vvs['state']}, crossed={vvs.get('crossed')}")
    if ks:
        print(f"  Kelly: VIX={ks['vix']:.1f}, base Q/H/F = "
              f"{ks['base_pct']['quarter']}/{ks['base_pct']['half']}/{ks['base_pct']['full']}%, "
              f"states corskew={ks['cor_skew_state']}/vixts={ks['vix_ts_state']}/volvol={ks['volvol_state']}")
    if ts:
        print(f"  Tactical: triggers T1/T2/T3={int(ts['t1'])}/{int(ts['t2'])}/{int(ts['t3'])}, "
              f"deploy={ts['deploy_pct']}% ({ts['label_en']}), "
              f"SPX 30d dd={ts['spx_drawdown_30d_pct']:+.1f}%")

    print("Patching home pages...")
    ko_changed = patch_home(ROOT / "docs" / "index.ko.md", render_section_ko(cs, vs, vvs, ks, ts))
    en_changed = patch_home(ROOT / "docs" / "index.en.md", render_section_en(cs, vs, vvs, ks, ts))
    print(f"  index.ko.md: {'updated' if ko_changed else 'unchanged'}")
    print(f"  index.en.md: {'updated' if en_changed else 'unchanged'}")
    print("Done.")


if __name__ == "__main__":
    main()
