"""
One-time backfill: populate docs/assets/diagrams[_en]/vix_history/ with
historical VIX TS snapshots going back N days. Cboe's settlement CSV
endpoint accepts a ?dt=YYYY-MM-DD parameter, so iterate weekdays and
fetch each historical curve.

Run once locally and commit the resulting PNGs + JSONs + updated
manifest. The daily cron continues to append from there.

Usage:
    python scripts/backfill_vix_history.py [--days N] [--skip-existing]

Defaults: --days 365 --skip-existing
"""
import argparse
import io
import json
import re
import shutil
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Reuse the live updater's logic (chart render, snapshot builder, paths)
sys.path.insert(0, str(Path(__file__).parent))
import update_dashboard as ud  # noqa: E402


# US market closures the Cboe CSV won't have data for. Maintained loosely —
# fetch_settlement_at returns empty for any missing day anyway, so the
# list is just an optimisation to skip obvious holidays without an HTTP roundtrip.
# Cboe's settlement CSV (?dt=DATE) returns only contracts that *still*
# exist in their database — already-expired monthly contracts have been
# purged. For dates more than ~8 months back the front-end of the curve
# can be empty, leaving a half-baked chart. Skip those.
MIN_CONTRACTS = 5

US_MARKET_HOLIDAYS = {
    # 2025
    "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26",
    "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27", "2025-11-28",
    "2025-12-24", "2025-12-25",
    # 2026
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-11-27",
    "2026-12-24", "2026-12-25",
}


def fetch_settlement_at(date_str: str) -> pd.DataFrame:
    """Fetch Cboe VIX futures settlement for a specific historical date.
    Returns an empty DataFrame if the date has no data (holiday, weekend,
    pre-listing window, etc.)."""
    url = f"{ud.CBOE_SETTLEMENT_URL}?dt={date_str}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            df = pd.read_csv(io.BytesIO(r.read()))
    except Exception as e:
        print(f"  [WARN] {date_str}: fetch failed: {e}")
        return pd.DataFrame()
    if df.empty:
        return df

    monthly_pat = re.compile(r"^VX/[A-Z]\d+$")
    vx = df[(df["Product"] == "VX") & df["Symbol"].astype(str).str.match(monthly_pat)].copy()
    if vx.empty:
        return pd.DataFrame()
    vx["Expiration Date"] = pd.to_datetime(vx["Expiration Date"])
    vx["Price"] = pd.to_numeric(vx["Price"], errors="coerce")
    vx = vx.dropna(subset=["Price"]).sort_values("Expiration Date").reset_index(drop=True)
    # DTE measured from the settlement date (not wall-clock today, which is
    # how update_dashboard's live fetcher computes it).
    settle_date = pd.Timestamp(date_str)
    vx["DTE"] = (vx["Expiration Date"] - settle_date).dt.days
    vx = vx[vx["DTE"] >= 0].reset_index(drop=True)
    return vx


def rebuild_manifests(archive_dirs: list[Path]):
    """Rebuild manifest.json from whatever PNG files actually exist on disk."""
    for d in archive_dirs:
        existing = sorted(
            f.stem for f in d.glob("*.png")
            if f.stem != "manifest" and not f.stem.startswith(".")
        )
        manifest = {
            "dates": existing,
            "latest": existing[-1] if existing else None,
            "retention_days": ud.VIX_HISTORY_RETENTION_DAYS,
            "data_format": "png + json (per-date)",
        }
        (d / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  Manifest {d.parent.name}/{d.name}: {len(existing)} entries, latest={manifest['latest']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=365,
                        help="Calendar days to look back (default 365 ≈ 252 weekdays)")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                        help="Skip dates whose PNG already exists (default on)")
    parser.add_argument("--no-skip-existing", dest="skip_existing", action="store_false")
    parser.add_argument("--sleep", type=float, default=0.3,
                        help="Seconds between Cboe requests (default 0.3)")
    args = parser.parse_args()

    print(f"Backfill window: {args.days} days, skip_existing={args.skip_existing}")
    print("Fetching full VIX cash history (Cboe direct)...")
    vix_hist = ud.fetch_vix_history()
    print(f"  {len(vix_hist)} bars, {vix_hist.index.min().date()} → {vix_hist.index.max().date()}")

    today = pd.Timestamp.now(tz="US/Eastern").normalize().tz_localize(None)
    start = today - pd.Timedelta(days=args.days)
    business_days = pd.date_range(start=start, end=today, freq="B")
    target_dates = [
        d.strftime("%Y-%m-%d") for d in business_days
        if d.strftime("%Y-%m-%d") not in US_MARKET_HOLIDAYS
    ]
    print(f"Targeting {len(target_dates)} business days ({target_dates[0]} → {target_dates[-1]})")

    archive_dirs = [ud.OUT_KO / "vix_history", ud.OUT_EN / "vix_history"]
    for d in archive_dirs:
        d.mkdir(parents=True, exist_ok=True)

    rendered, skipped_existing, skipped_no_data = 0, 0, 0
    for i, date_str in enumerate(target_dates, 1):
        png_path = archive_dirs[0] / f"{date_str}.png"
        if args.skip_existing and png_path.exists():
            skipped_existing += 1
            continue

        # Need VIX cash spot for that day (used by the chart's marker + JSON snapshot)
        spot_date = pd.Timestamp(date_str)
        available_vix = vix_hist[vix_hist.index <= spot_date]
        if not len(available_vix) or available_vix.index[-1].strftime("%Y-%m-%d") != date_str:
            # VIX cash hasn't published this day → genuinely non-trading
            skipped_no_data += 1
            print(f"[{i}/{len(target_dates)}] {date_str}: no matching VIX spot, skip")
            continue
        vix_spot = float(available_vix.iloc[-1])

        # Pull the futures curve for this exact settlement date
        vx = fetch_settlement_at(date_str)
        if vx.empty:
            skipped_no_data += 1
            print(f"[{i}/{len(target_dates)}] {date_str}: settlement CSV empty, skip")
            time.sleep(args.sleep)
            continue
        if len(vx) < MIN_CONTRACTS:
            skipped_no_data += 1
            print(f"[{i}/{len(target_dates)}] {date_str}: only {len(vx)} contracts "
                  f"(< {MIN_CONTRACTS}), Cboe purged expired front-end — skip")
            time.sleep(args.sleep)
            continue

        # Render chart with the historical settlement date in the title,
        # then archive PNG + JSON under that date in both locales.
        ud.render_vix_term_structure(vx, vix_spot, png_path, settlement_date=date_str)
        shutil.copy2(png_path, archive_dirs[1] / f"{date_str}.png")

        snapshot = ud._vix_ts_data_snapshot(vx, vix_spot, date_str)
        snapshot_json = json.dumps(snapshot, ensure_ascii=False, indent=2)
        for d in archive_dirs:
            (d / f"{date_str}.json").write_text(snapshot_json, encoding="utf-8")

        rendered += 1
        shape = snapshot.get("shape", "?")
        n_contracts = len(snapshot.get("contracts", []))
        print(f"[{i}/{len(target_dates)}] {date_str}: ✓ VIX {vix_spot:.2f}, "
              f"{n_contracts} contracts, {shape}")
        time.sleep(args.sleep)

    print(f"\nDone. Rendered: {rendered}, skipped (existed): {skipped_existing}, "
          f"skipped (no data): {skipped_no_data}")
    rebuild_manifests(archive_dirs)


if __name__ == "__main__":
    main()
