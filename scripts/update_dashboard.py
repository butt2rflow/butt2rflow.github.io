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


def fetch_vix_spot() -> float:
    s = _fetch_cboe_index("VIX")
    return float(s.iloc[-1]) if len(s) else float("nan")


# Number of past trading days to keep in the rolling VIX TS animation.
# Each daily PNG is ~80–150 KB, so 365 days ≈ 30–50 MB in repo. GitHub
# repos handle up to ~1 GB comfortably, so feel free to extend if you
# want multi-year scrubbing.
VIX_HISTORY_RETENTION_DAYS = 365


def archive_vix_history(today_chart: Path) -> None:
    """Copy today's VIX TS chart to docs/assets/diagrams[_en]/vix_history/<date>.png,
    then prune anything older than VIX_HISTORY_RETENTION_DAYS, then write
    a manifest.json the homepage's JS player reads."""
    today_str = pd.Timestamp.now(tz="US/Eastern").strftime("%Y-%m-%d")

    for parent in [OUT_KO, OUT_EN]:
        archive_dir = parent / "vix_history"
        archive_dir.mkdir(parents=True, exist_ok=True)
        # Save today's snapshot under the date filename
        dst = archive_dir / f"{today_str}.png"
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
EMOJI = {"ok": "🟢", "caution": "🟡", "danger": "🔴"}
START_MARK = "<!-- DASHBOARD_START -->"
END_MARK = "<!-- DASHBOARD_END -->"
KO_LABEL = {"ok": "정상", "caution": "경계", "danger": "스트레스"}
EN_LABEL = {"ok": "Normal", "caution": "Caution", "danger": "Stressed"}
SHAPE_KO = {"contango": "콘탱고 (정상)", "backwardation": "백워데이션 (스트레스)", "mixed": "혼합"}
SHAPE_EN = {"contango": "Contango (normal)", "backwardation": "Backwardation (stress)", "mixed": "Mixed"}
SHAPE_EMOJI = {"contango": "🟢", "backwardation": "🔴", "mixed": "🟡"}


def render_section_ko(cs, vs):
    spread_label = "역전" if cs["spread_state"] == "danger" else KO_LABEL[cs["spread_state"]]
    parts = [
        START_MARK,
        '<div class="live-dash" markdown>',
        "",
        "## 📊 변동성 라이브 대시보드",
        "",
        f"<small>**{cs['date']} 기준** · 미국 장 마감 후 매일 자동 갱신 · "
        "[자세히 →](posts/volatility-dashboard.md)</small>",
        "",
    ]
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
            "![VIX Futures Term Structure](assets/diagrams/vix_term_structure.png)",
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
        "</div>",
        "",
        "---",
        END_MARK,
    ]
    return "\n".join(parts)


def render_section_en(cs, vs):
    spread_label = "Inverted" if cs["spread_state"] == "danger" else EN_LABEL[cs["spread_state"]]
    parts = [
        START_MARK,
        '<div class="live-dash" markdown>',
        "",
        "## 📊 Live Volatility Dashboard",
        "",
        f"<small>**As of {cs['date']}** · Auto-updates daily after the US close · "
        "[Full article →](posts/volatility-dashboard.md)</small>",
        "",
    ]
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
            "![VIX Futures Term Structure](assets/diagrams_en/vix_term_structure.png)",
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

    vix_spot = fetch_vix_spot()
    print(f"  VIX spot: {vix_spot:.2f}")

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

    if len(vx) > 0:
        render_vix_term_structure(vx, vix_spot, OUT_KO / "vix_term_structure.png")
        print(f"  Saved: {OUT_KO / 'vix_term_structure.png'}")
        shutil.copy2(OUT_KO / "vix_term_structure.png", OUT_EN / "vix_term_structure.png")
        print(f"  Copied: {OUT_EN / 'vix_term_structure.png'}")
        archive_vix_history(OUT_KO / "vix_term_structure.png")

    print("Computing signals...")
    cs = compute_cor_skew_signals(tenor, skew)
    vs = compute_vix_signals(vx, vix_spot) if len(vx) > 0 else None
    print(f"  COR/SKEW: spread={cs['spread']:.2f}, COR90D={cs['cor90d']:.2f}, SKEW={cs['skew']:.2f}")
    if vs:
        print(f"  VIX TS: spot={vs['vix_spot']:.2f}, front={vs['front']:.2f}, "
              f"M2-M1={vs['spread_2_1']:+.2f}, shape={vs['shape']}")

    print("Patching home pages...")
    ko_changed = patch_home(ROOT / "docs" / "index.ko.md", render_section_ko(cs, vs))
    en_changed = patch_home(ROOT / "docs" / "index.en.md", render_section_en(cs, vs))
    print(f"  index.ko.md: {'updated' if ko_changed else 'unchanged'}")
    print(f"  index.en.md: {'updated' if en_changed else 'unchanged'}")
    print("Done.")


if __name__ == "__main__":
    main()
