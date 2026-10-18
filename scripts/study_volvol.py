"""
VolVol study — tests the blog's own definition (2022-08-28 "VolVol 지표",
2022-12-18 "볼볼 무한매수법") as it was meant to be used: a volatility-regime
switch for leverage, not a next-10-day crash call.

VolVol = VVIX / VIX. Indicator = 5-day MA; frame = 20-day Bollinger band (2σ).
  (B-3) 5MA crosses above the band middle (20MA) → "vol easing → lever up"
        5MA crosses below                       → "vol rising → delever"
  (A-2) 5MA dips below the lower band, then closes back inside → "first buy,
        V-shape possible"
Plus the observation that the ratio's absolute level / trend lines up with
bull vs bear markets.

Every test runs the same rule on VIX alone (and a 200-day SPX MA) so we can
see whether the VVIX half adds anything beyond VIX. Signals act on the next
session (no lookahead). Long-horizon outcomes overlap heavily, so CIs come
from a block bootstrap (60-session blocks).

Run from project root:  PYTHONUTF8=1 python scripts/study_volvol.py
Writes brief_review/volvol_study.png (event study chart).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_dashboard as ud  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RNG = np.random.default_rng(11)
BLOCK = 60
REPS = 500
FIN_COST = 0.02          # annual financing on the borrowed half of 2x
SWITCH_COST = 0.0005     # 5bp per switch


def load() -> pd.DataFrame:
    d = pd.DataFrame({n: ud._fetch_cboe_index(n) for n in ("SPX", "VIX", "VVIX")}).dropna()
    d["ret"] = d.SPX.pct_change()
    d["vv"] = d.VVIX / d.VIX
    for name, s in (("vv", d.vv), ("vix", d.VIX)):
        # The indicator is the 5MA; the Bollinger band (20, 2σ) is drawn on the
        # indicator itself (bands on the raw ratio are never pierced by the 5MA).
        d[f"{name}_ma5"] = ma5 = s.rolling(5).mean()
        d[f"{name}_ma20"] = ma5.rolling(20).mean()
        sd = ma5.rolling(20).std()
        d[f"{name}_lo"] = d[f"{name}_ma20"] - 2 * sd
        d[f"{name}_hi"] = d[f"{name}_ma20"] + 2 * sd
    # Rule states (known at today's close, applied from tomorrow)
    d["vv_on"] = d.vv_ma5 > d.vv_ma20                 # golden = vol easing
    d["vix_on"] = d.vix_ma5 < d.vix_ma20              # VIX-only analog: VIX falling
    d["ma200_on"] = d.SPX > d.SPX.rolling(200).mean() # LRS benchmark
    # Forward outcomes from tomorrow
    r = d.ret
    d["rv20_fwd"] = r[::-1].rolling(20).std()[::-1].shift(-1) * np.sqrt(252) * 100
    d["ret20_fwd"] = (d.SPX.shift(-20) / d.SPX - 1) * 100
    d["ret60_fwd"] = (d.SPX.shift(-60) / d.SPX - 1) * 100
    fwdmin = pd.concat([d.SPX.shift(-k) for k in range(1, 121)], axis=1).min(axis=1)
    d["dd120_fwd"] = (fwdmin / d.SPX - 1) * 100
    # Regime labels
    peak = d.SPX.cummax()
    d["dd_from_peak"] = (d.SPX / peak - 1) * 100
    d = d.dropna(subset=["vv_ma20", "vix_ma20"]).loc["2007":]
    d["pos"] = np.arange(len(d))
    return d


def block_ci(x: pd.DataFrame, f, reps=REPS, block=BLOCK) -> tuple[float, float]:
    blocks = (x.pos // block).values
    keys = np.unique(blocks)
    idx = {k: np.flatnonzero(blocks == k) for k in keys}
    est = []
    for _ in range(reps):
        ix = np.concatenate([idx[k] for k in RNG.choice(keys, len(keys))])
        est.append(f(x.iloc[ix]))
    return tuple(np.nanpercentile(est, [2.5, 97.5]))


# ------------------------------------------------------------------
# 1. Does the state sort *future volatility*? (what the rule claims)
# ------------------------------------------------------------------
def state_table(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rule in ("vv_on", "vix_on", "ma200_on"):
        for on in (True, False):
            x = d[(d[rule] == on)].dropna(subset=["rv20_fwd", "ret20_fwd"])
            lo, hi = block_ci(x, lambda y: y.rv20_fwd.mean())
            rows.append({"rule": rule, "state": "ON(lever)" if on else "OFF(delever)",
                         "share": f"{len(x) / len(d):.0%}",
                         "fwd RV20": f"{x.rv20_fwd.mean():.1f} [{lo:.1f}–{hi:.1f}]",
                         "fwd ret20 mean": f"{x.ret20_fwd.mean():+.2f}%",
                         "≤2019 RV20": f"{x[x.index < '2020'].rv20_fwd.mean():.1f}",
                         "2020– RV20": f"{x[x.index >= '2020'].rv20_fwd.mean():.1f}"})
    return pd.DataFrame(rows)


def incremental(d: pd.DataFrame) -> pd.DataFrame:
    """Does VolVol sort future vol *after* conditioning on the VIX-only rule?"""
    rows = []
    for vix_state in (True, False):
        for vv_state in (True, False):
            x = d[(d.vix_on == vix_state) & (d.vv_on == vv_state)].dropna(subset=["rv20_fwd"])
            lo, hi = block_ci(x, lambda y: y.rv20_fwd.mean())
            rows.append({"VIX rule": "ON" if vix_state else "OFF",
                         "VolVol rule": "ON" if vv_state else "OFF",
                         "share": f"{len(x) / len(d):.0%}",
                         "fwd RV20": f"{x.rv20_fwd.mean():.1f} [{lo:.1f}–{hi:.1f}]",
                         "fwd ret20": f"{x.ret20_fwd.mean():+.2f}%"})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# 2. Leverage-switch backtest (the 볼볼 무한매수법 use): 2x when ON, 1x when OFF
# ------------------------------------------------------------------
def backtest(d: pd.DataFrame, rule: str | None, lev_on=2.0, lev_off=1.0) -> pd.Series:
    if rule is None:
        lev = pd.Series(1.0, index=d.index)
    else:
        lev = np.where(d[rule].shift(1).fillna(False), lev_on, lev_off)
        lev = pd.Series(lev, index=d.index)
    fin = (lev - 1).clip(lower=0) * FIN_COST / 252
    switches = lev.diff().abs().fillna(0) > 0
    r = lev * d.ret.fillna(0) - fin - switches * SWITCH_COST
    return r


def stats(r: pd.Series) -> dict:
    eq = (1 + r).cumprod()
    yrs = len(r) / 252
    cagr = eq.iloc[-1] ** (1 / yrs) - 1
    vol = r.std() * np.sqrt(252)
    mdd = (eq / eq.cummax() - 1).min()
    return {"CAGR": cagr, "vol": vol, "Sharpe(0rf)": cagr / vol if vol else np.nan,
            "MaxDD": mdd, "CAGR/|MaxDD|": cagr / abs(mdd) if mdd else np.nan}


def backtest_table(d: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for label, rule, on, off in (("Buy&hold 1x", None, 1, 1),
                                 ("Buy&hold 2x", None, 2, 2),
                                 ("VolVol: 2x on / 1x off", "vv_on", 2, 1),
                                 ("VIX-only: 2x on / 1x off", "vix_on", 2, 1),
                                 ("200MA: 2x on / 1x off", "ma200_on", 2, 1),
                                 ("VolVol: 1x on / cash off", "vv_on", 1, 0),
                                 ("VIX-only: 1x on / cash off", "vix_on", 1, 0)):
        if rule is None:
            r = d.ret.fillna(0) * on - (on - 1) * FIN_COST / 252
        else:
            r = backtest(d, rule, on, off)
        s = stats(r)
        s["switches/yr"] = (d[rule].astype(int).diff().abs().sum() / (len(d) / 252)) if rule else 0
        for era, m in (("≤2019", d.index < "2020"), ("2020–", d.index >= "2020")):
            s[f"Sharpe {era}"] = stats(r[m])["Sharpe(0rf)"]
        rows[label] = s
    t = pd.DataFrame(rows).T
    # Sharpe difference VolVol vs VIX-only (2x/1x), block bootstrap
    rv, rx = backtest(d, "vv_on"), backtest(d, "vix_on")
    both = pd.DataFrame({"a": rv, "b": rx, "pos": d.pos})
    lo, hi = block_ci(both, lambda y: stats(y.a)["Sharpe(0rf)"] - stats(y.b)["Sharpe(0rf)"])
    t.attrs["sharpe_gap_ci"] = (lo, hi)
    return t


# ------------------------------------------------------------------
# 3. (A-2) lower-band dip then recovery → first buy / V-shape?
# ------------------------------------------------------------------
def a2_events(d: pd.DataFrame, name: str) -> pd.DataFrame:
    below = d[f"{name}_ma5"] < d[f"{name}_lo"] if name == "vv" else d[f"{name}_ma5"] > d[f"{name}_hi"]
    # VolVol: dip below lower band then back above; VIX analog: spike above upper band then back below
    recover = below.shift(1, fill_value=False) & ~below
    ev = d[recover].copy()
    ev = ev[ev.pos.diff().fillna(99) > 20]        # de-cluster: one event per 20 sessions
    return ev


def a2_table(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base = d.dropna(subset=["ret20_fwd", "ret60_fwd"])
    for label, name in (("VolVol 하단 이탈→복귀 (A-2)", "vv"), ("VIX 상단 이탈→복귀 (analog)", "vix")):
        ev = a2_events(d, name).dropna(subset=["ret20_fwd", "ret60_fwd"])
        boot = [ev.sample(len(ev), replace=True, random_state=RNG.integers(1 << 31)).ret20_fwd.mean()
                for _ in range(2000)]
        lo, hi = np.percentile(boot, [2.5, 97.5])
        rows.append({"event": label, "n": len(ev),
                     "ret20 mean": f"{ev.ret20_fwd.mean():+.2f}% [{lo:+.2f}–{hi:+.2f}]",
                     "P(ret20>0)": f"{(ev.ret20_fwd > 0).mean():.0%}",
                     "ret60 mean": f"{ev.ret60_fwd.mean():+.2f}%",
                     "fwd RV20": f"{ev.rv20_fwd.mean():.1f}",
                     "dd at event (median)": f"{ev.dd_from_peak.median():.1f}%"})
    rows.append({"event": "all days", "n": len(base),
                 "ret20 mean": f"{base.ret20_fwd.mean():+.2f}%",
                 "P(ret20>0)": f"{(base.ret20_fwd > 0).mean():.0%}",
                 "ret60 mean": f"{base.ret60_fwd.mean():+.2f}%",
                 "fwd RV20": f"{base.rv20_fwd.mean():.1f}", "dd at event (median)": ""})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# 4. Absolute level ↔ bull/bear (coincident and leading)
# ------------------------------------------------------------------
def level_table(d: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = d.dropna(subset=["dd120_fwd"]).copy()
    x["bear_now"] = x.dd_from_peak <= -20
    x["below200"] = ~x.ma200_on
    x["dd10_ahead"] = x.dd120_fwd <= -10
    qs = pd.qcut(x.vv, 5, labels=["Q1 low", "Q2", "Q3", "Q4", "Q5 high"])
    coin = x.groupby(qs, observed=True).agg(
        vv_range=("vv", lambda s: f"{s.min():.1f}–{s.max():.1f}"),
        VIX_median=("VIX", "median"),
        in_bear_now=("bear_now", "mean"),
        below_200MA=("below200", "mean"),
        dd10_in_next_120d=("dd10_ahead", "mean"),
        ret60_fwd=("ret60_fwd", "mean"))
    # Same question within VIX terciles: does the ratio add anything beyond VIX?
    x["vix_t"] = pd.qcut(x.VIX, 3, labels=["VIX low", "VIX mid", "VIX high"])
    x["vv_hi"] = x.groupby("vix_t", observed=True).vv.transform(lambda s: s >= s.median())
    within = x.groupby(["vix_t", "vv_hi"], observed=True).agg(
        n=("vv", "size"), below_200MA=("below200", "mean"),
        dd10_in_next_120d=("dd10_ahead", "mean"), ret60_fwd=("ret60_fwd", "mean"))
    return coin, within


def slope_table(d: pd.DataFrame) -> pd.DataFrame:
    """Ratio *trend* (60-session change of its 20MA) vs regime ahead, within VIX terciles."""
    x = d.dropna(subset=["dd120_fwd"]).copy()
    x["vv_trend"] = x.vv_ma20 - x.vv_ma20.shift(60)
    x["vix_t"] = pd.qcut(x.VIX, 3, labels=["VIX low", "VIX mid", "VIX high"])
    x["trend"] = np.where(x.vv_trend > 0, "rising", "falling")
    return x.groupby(["vix_t", "trend"], observed=True).agg(
        n=("vv", "size"), dd10_in_next_120d=("dd120_fwd", lambda s: (s <= -10).mean()),
        ret60_fwd=("ret60_fwd", "mean"), rv20_fwd=("rv20_fwd", "mean"))


# ------------------------------------------------------------------
# 5. Event study around major SPX peaks and troughs
# ------------------------------------------------------------------
def major_turns(d: pd.DataFrame, th=-15.0) -> tuple[list, list]:
    """Peaks = 1-year highs followed by a ≥15% decline; trough = the low of
    that decline before SPX makes back half the loss. A rolling 1-year high
    (not all-time) so 2011 / 2015–16 count even though 2007 wasn't regained
    until 2013."""
    s = d.SPX
    hi252 = s.rolling(252, min_periods=60).max()
    peaks, troughs = [], []
    i, n = 0, len(s)
    while i < n:
        if s.iloc[i] / hi252.iloc[i] - 1 <= th / 100:
            pk = s.iloc[max(0, i - 252):i + 1].idxmax()
            pk_v = s[pk]
            j, lo_i = i, i
            while j < n and s.iloc[j] < pk_v - 0.5 * (pk_v - s.iloc[lo_i]):
                if s.iloc[j] < s.iloc[lo_i]:
                    lo_i = j
                j += 1
            if not peaks or pk > troughs[-1]:
                peaks.append(pk)
                troughs.append(s.index[lo_i])
            i = max(j, i + 1)
            continue
        i += 1
    return peaks, troughs


def event_paths(d: pd.DataFrame, dates: list, col: str, w=120) -> pd.DataFrame:
    out = {}
    for t in dates:
        p = d.index.get_loc(t)
        if p - w < 0 or p + w >= len(d):
            continue
        seg = d[col].iloc[p - w:p + w + 1].values
        out[t.strftime("%Y-%m")] = seg / seg[w]          # rebased to 1.0 at the event
    return pd.DataFrame(out, index=range(-w, w + 1))


def chart(d: pd.DataFrame, peaks: list, troughs: list, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
    for row, (dates, name) in enumerate(((peaks, "SPX peak (before ≥15% drawdown)"),
                                         (troughs, "SPX trough"))):
        for col, (series, lab, c) in enumerate((("vv_ma5", "VolVol 5MA (VVIX/VIX)", "#2a78d6"),
                                                ("VIX", "VIX", "#eb6834"))):
            ax = axes[row, col]
            p = event_paths(d, dates, series)
            for k in p.columns:
                ax.plot(p.index, p[k], color=c, alpha=0.25, lw=1)
            ax.plot(p.index, p.median(axis=1), color=c, lw=2.5, label="median")
            ax.axvline(0, color="#6b6a64", ls=":", lw=1)
            ax.axhline(1, color="#6b6a64", lw=0.6)
            ax.set_title(f"{lab} around {name} (n={p.shape[1]})", fontsize=10, loc="left")
            ax.grid(axis="y", color="#e6e5e0")
    for ax in axes[1]:
        ax.set_xlabel("sessions from event")
    fig.suptitle("VolVol vs VIX around major SPX turns (rebased to 1.0 at the event)", x=0.01,
                 ha="left", fontweight="bold")
    fig.tight_layout()
    path.parent.mkdir(exist_ok=True)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def lead_lag(d: pd.DataFrame) -> None:
    """Is VolVol *faster* than VIX? (a) does today's VVIX move add to VIX's
    next-k-day move given today's VIX move, (b) which rule crosses first."""
    dv, dvv = np.log(d.VIX).diff(), np.log(d.VVIX).diff()
    for k in (1, 3, 5, 10):
        X = pd.DataFrame({"dvix": dv, "dvvix": dvv,
                          "y": np.log(d.VIX).shift(-k) - np.log(d.VIX)}).dropna()
        A = np.column_stack([np.ones(len(X)), X.dvix, X.dvvix])
        b, *_ = np.linalg.lstsq(A, X.y.values, rcond=None)
        X["pos"] = np.arange(len(X))
        lo, hi = block_ci(X, lambda y: np.linalg.lstsq(
            np.column_stack([np.ones(len(y)), y.dvix, y.dvvix]), y.y.values, rcond=None)[0][2],
            reps=300, block=20)
        flat = X[X.dvix.abs() < X.dvix.abs().quantile(0.3)]
        print(f"  next {k:2d}d: coef(dVVIX | dVIX) {b[2]:+.3f} [{lo:+.3f},{hi:+.3f}] · "
              f"flat-VIX days corr(dVVIX, future) {flat.dvvix.corr(flat.y):+.3f}")
    print("  xcorr dVVIX(t) vs dVIX(t+L): "
          + "  ".join(f"{L:+d}:{dvv.corr(dv.shift(-L)):+.3f}" for L in range(-2, 3)))
    pos = pd.Series(np.arange(len(d)), index=d.index)
    for label, want in (("delever", -1), ("lever", +1)):
        a = d.vv_on.astype(int).diff(); b_ = d.vix_on.astype(int).diff()
        a, b_ = a[a == want].index, b_[b_ == want].index
        leads = []
        for t in a:
            near = b_[(b_ >= t - pd.Timedelta(days=30)) & (b_ <= t + pd.Timedelta(days=30))]
            if len(near):
                leads.append(pos[min(near, key=lambda u: abs(pos[u] - pos[t]))] - pos[t])
        L = np.array(leads)
        print(f"  {label} crosses (n={len(L)}): VolVol first {np.mean(L > 0):.0%}, same day "
              f"{np.mean(L == 0):.0%}, VIX first {np.mean(L < 0):.0%}, median {np.median(L):+.0f} sessions")


def acceleration_test(d: pd.DataFrame) -> None:
    """The 'insurance on insurance = acceleration' idea: if VVIX is VIX's
    acceleration, VVIX should bottom before VIX at the start of a spike and
    peak before VIX at the top. Placebos (VIX9D, VIX3M, SKEW) run the same
    turn-finding window, which by construction favours 'earlier' at the start
    (VIX's start is its own 20-day low, so everything after it is rising)."""
    from math import comb
    vix = d.VIX
    pos = pd.Series(np.arange(len(d)), index=d.index)
    spikes, i, n = [], 25, len(d)
    while i < n:
        lo20 = vix.iloc[i - 20:i + 1].min()
        if vix.iloc[i] >= 1.4 * lo20:
            start = vix.iloc[i - 20:i + 1].idxmin()
            j, pk = i, i
            while j < n and vix.iloc[j] > (vix.iloc[pk] + lo20) / 2:
                pk = j if vix.iloc[j] > vix.iloc[pk] else pk
                j += 1
            spikes.append((start, vix.index[pk]))
            i = j + 5
            continue
        i += 1

    def turn(ser, ref, kind, w=15):
        p = pos[ref]
        seg = ser.iloc[max(0, p - w):p + w + 1]
        return seg.idxmax() if kind == "max" else seg.idxmin()

    def sign_p(e, l):
        k, m = int(min(e, l)), int(e + l)
        return min(1.0, 2 * sum(comb(m, j) for j in range(k + 1)) / 2 ** m) if m else 1.0

    extra = {nm: ud._fetch_cboe_index(nm).reindex(d.index).ffill() for nm in ("VIX9D", "VIX3M", "SKEW")}
    print(f"  VIX spikes (≥+40% over 20-day low): {len(spikes)}; negative = turns before VIX")
    for kind, idx_of, lab in (("min", 0, "bottom at spike start"), ("max", 1, "peak at spike top")):
        for name, ser in (("VVIX", d.VVIX), ("VIX 5d momentum", vix.diff(5)),
                          ("VIX9D (placebo)", extra["VIX9D"]), ("VIX3M (placebo)", extra["VIX3M"]),
                          ("SKEW (placebo)", extra["SKEW"])):
            if kind == "min" and name.startswith("VIX 5d"):
                continue
            L = np.array([pos[turn(ser, sp[idx_of], kind)] - pos[sp[idx_of]] for sp in spikes
                          if ser.loc[:sp[idx_of]].notna().sum() > 20])
            e, l = (L < 0).sum(), (L > 0).sum()
            print(f"  {lab:22s} {name:18s} earlier {e / len(L):.0%} later {l / len(L):.0%} "
                  f"median {np.median(L):+.0f} sign-p {sign_p(e, l):.4f}")


def calmer_than_priced(d: pd.DataFrame) -> None:
    """The user's claim: VolVol golden = a relatively low-vol market regardless
    of the VIX level. Outcome = next-20-session realized vol / VIX (below 1 =
    calmer than options priced). Gap golden − dead, stratified by VIX band
    (and by the VIX-only rule state), block-bootstrap CI, era + holdout."""
    x = d.dropna(subset=["rv20_fwd"]).copy()
    x["band"] = pd.cut(x.VIX, [0, 15, 20, 25, 35, 200], labels=False)
    x["rv_ratio"] = x.rv20_fwd / x.VIX
    x["pos"] = np.arange(len(x))

    def gap(y, flag, strata):
        gs, w = [], []
        for _, g in y.groupby(list(strata), observed=True):
            a, b = g[g[flag]].rv_ratio, g[~g[flag]].rv_ratio
            if len(a) >= 20 and len(b) >= 20:
                gs.append(a.mean() - b.mean())
                w.append(len(g))
        return float(np.average(gs, weights=w)) if gs else np.nan

    for lab, flag, strata in (("VolVol | VIX band × VIX rule", "vv_on", ("band", "vix_on")),
                              ("VolVol | VIX band", "vv_on", ("band",)),
                              ("VIX rule | VIX band", "vix_on", ("band",))):
        lo, hi = block_ci(x, lambda y: gap(y, flag, strata), reps=300, block=60)
        eras = [gap(x[m], flag, strata) for m in (x.index < "2020",
                                                  (x.index >= "2020") & (x.index < "2024-09"),
                                                  x.index >= "2024-09")]
        print(f"  {lab:30s} {gap(x, flag, strata):+.3f} [{lo:+.3f}, {hi:+.3f}] · ≤2019 {eras[0]:+.3f}"
              f" · 2020–24/08 {eras[1]:+.3f} · holdout 2024/09– {eras[2]:+.3f}")


def shoulders_knees(d: pd.DataFrame, hold: int = 5) -> None:
    """Not tops/bottoms — how early each detector flags the shoulder (first
    lasting risk-off switch, SPX % from the peak) and the knee (first lasting
    risk-on switch after the trough, SPX % above it), for declines ≥10%.
    A switch counts only if the new state holds `hold` sessions."""
    peaks, troughs = major_turns(d, th=-10.0)
    pos = pd.Series(np.arange(len(d)), index=d.index)
    det = {"VolVol": d.vv_on, "VIX rule": d.vix_on, "200MA": d.ma200_on}

    def lasting(on, start, end, want):
        for t in on.loc[start:end].index:
            p = pos[t]
            if bool(on.iloc[p]) == want and (p == 0 or bool(on.iloc[p - 1]) != want) \
                    and all(bool(v) == want for v in on.iloc[p:p + hold]):
                return t
        return None

    res = {k: {"off": [], "on": [], "on_s": []} for k in det}
    for pk, tr in zip(peaks, troughs):
        for k, on in det.items():
            t_off = lasting(on, d.index[max(0, pos[pk] - 30)], tr, False)
            t_on = lasting(on, tr, d.index[min(len(d) - 1, pos[tr] + 120)], True)
            if t_off is not None:
                res[k]["off"].append((d.SPX[t_off] / d.SPX[pk] - 1) * 100)
            if t_on is not None:
                res[k]["on"].append((d.SPX[t_on] / d.SPX[tr] - 1) * 100)
                res[k]["on_s"].append(pos[t_on] - pos[tr])
    fwd_min40 = pd.concat([d.SPX.shift(-k) for k in range(1, 41)], axis=1).min(axis=1) / d.SPX - 1
    print(f"  {len(peaks)} declines ≥10% since 2007")
    for k, on in det.items():
        sw = on.astype(int).diff()
        offs = sw[sw == -1].index
        offs = offs[offs < d.index[-41]]
        print(f"  {k:9s} shoulder: risk-off at SPX {np.median(res[k]['off']):+.1f}% from peak · "
              f"knee: risk-on at {np.median(res[k]['on']):+.1f}% above trough, "
              f"{np.median(res[k]['on_s']):.0f} sessions after · risk-off switches/yr "
              f"{len(offs) / (len(d) / 252):.1f}, false alarm {np.mean(fwd_min40.loc[offs] > -0.05):.0%}")


def main():
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    d = load()
    print(f"Data {d.index[0]:%Y-%m-%d} → {d.index[-1]:%Y-%m-%d}, {len(d)} sessions\n")

    print("== 1. Rule state vs future 20-session realized vol (what the rule claims) ==")
    print(state_table(d).to_string(index=False))
    print("\n-- VolVol given the VIX-only rule (does VVIX add anything?) --")
    print(incremental(d).to_string(index=False))

    print("\n== 2. Leverage switch backtest (T+1, 2% financing, 5bp/switch) ==")
    t = backtest_table(d)
    fmt = t.copy()
    for c in fmt.columns:
        fmt[c] = [f"{v:.2f}" if "Sharpe" in c or "/" in c or "switch" in c else f"{v:.1%}" for v in t[c]]
    print(fmt.to_string())
    lo, hi = t.attrs["sharpe_gap_ci"]
    print(f"Sharpe gap VolVol − VIX-only (2x/1x): 95% CI [{lo:+.2f}, {hi:+.2f}]")

    print("\n== 3. (A-2) dip/recover events, de-clustered ==")
    print(a2_table(d).to_string(index=False))

    print("\n== 4. Absolute level vs bull/bear ==")
    coin, within = level_table(d)
    print(coin.to_string(float_format=lambda v: f"{v:.2f}"))
    print("\n-- within VIX terciles: ratio at/above vs below the tercile median --")
    print(within.to_string(float_format=lambda v: f"{v:.2f}"))
    print("\n-- ratio trend (60-session change of 20MA) within VIX terciles --")
    print(slope_table(d).to_string(float_format=lambda v: f"{v:.2f}"))

    peaks, troughs = major_turns(d)
    print(f"\n== 5. Major turns (≥15% drawdowns): peaks {[p.strftime('%Y-%m') for p in peaks]}")
    for name, dates in (("peak", peaks), ("trough", troughs)):
        for col in ("vv_ma5", "VIX"):
            p = event_paths(d, dates, col)
            m = p.median(axis=1)
            print(f"  {col:6s} around {name}: median at −60 {m[-60]:.2f}, −20 {m[-20]:.2f}, "
                  f"+20 {m[20]:.2f}, +60 {m[60]:.2f}  (rebased 1.0 at event)")
    print("\n== 6. Is VolVol faster than VIX? (lead/lag) ==")
    lead_lag(d)
    print("\n== 7. 'Insurance on insurance = acceleration': does VVIX turn before VIX? ==")
    acceleration_test(d)
    print("\n== 8. Golden = calmer than priced, regardless of VIX level? (future RV20 / VIX) ==")
    calmer_than_priced(d)
    print("\n== 9. Shoulders and knees (not tops/bottoms) ==")
    shoulders_knees(d)
    out = ROOT / "brief_review" / "volvol_study.png"
    chart(d, peaks, troughs, out)
    print(f"\nChart: {out}")


if __name__ == "__main__":
    main()
