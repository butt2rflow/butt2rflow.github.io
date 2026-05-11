---
title: "Vol-Based Cash Allocation — Kelly meets risk signals"
date: 2026-05-11
tags: [kelly, volatility, vix, position-sizing, cor, skew, volvol, cash-allocation]
lang: en
---

# Vol-Based Cash Allocation — Kelly meets risk signals

> **Where this fits**: Series [Part 3 — Kelly's formula](../series/s1-shannons-demon.md) gave the Kelly fraction; this article plugs **VIX into σ** to turn it into a daily cash/equity allocation. It's the math behind the first card on the live dashboard.

---

## TL;DR

> **Cut cash when vol is low, raise cash when vol rises** — Kelly's formula makes this intuition quantitative.

**f\* = (μ − r) / σ²** — substitute σ with VIX, and a *doubling* of volatility *quarters* the suggested equity weight (the σ² in the denominator does the work). On top of that base, three extra risk-signal groups (COR/SKEW, VIX TS backwardation, VolVol) layer multiplicative discounts when they fire, raising cash one more notch.

---

## 1. Kelly's formula in one line

Kelly maximises the long-run growth rate of a portfolio under a return distribution. For continuous assets like equities:

```
f* = (μ − r) / σ²
```

| Symbol | Meaning |
|:---|:---|
| **f\*** | Fraction of capital to deploy (the rest sits in cash) |
| **μ** | Asset expected return (annualised) |
| **r** | Risk-free rate (annualised) |
| **σ** | Asset return standard deviation (annualised vol) |

For the S&P 500, long-run μ ≈ 9%, r ≈ 4%, so **μ − r = 5%** is a reasonable baseline equity premium. σ runs ~16–20% in calm regimes, spikes to 40–50% in crises.

> **Why σ² and not σ?** The squared denominator is the key. Doubling vol *quarters* the optimal weight. The asymmetric "raise cash quickly" instinct lives in that squared term.

---

## 2. What to plug into σ — VIX

Kelly needs *forward-looking* σ. Historical realised vol tells you the past; you need the future.

**VIX is the cleanest forward-looking estimate.** It is the S&P 500 options market's consensus expectation of 30-day realised vol, annualised, updated tick-by-tick. No single statistical estimator can match the wisdom-of-crowds quality of a deeply liquid options market.

```
σ ≈ VIX / 100
```

VIX = 17 → σ ≈ 0.17. VIX = 30 → σ ≈ 0.30.

| VIX | σ² | Half-Kelly @ μ−r=5% |
|---:|---:|---:|
| 12 | 0.0144 | 173% → **100% (capped)** |
| 17 | 0.0289 | **86%** |
| 22 | 0.0484 | 52% |
| 30 | 0.0900 | 28% |
| 40 | 0.1600 | 16% |

When vol rises 17 → 30 (1.8×), the suggested weight falls 86% → 28% (1/3). That's where the rough rule "VIX in the high 20s → cut equity in half" comes from — it's the same curve.

![Kelly × VIX curve](../assets/diagrams_en/kelly_curve.png)

---

## 3. Kelly fraction — the first user toggle

**Full Kelly (f\* as-is) is theoretically optimal but practically dangerous** for retail. Two reasons:

1. **Estimation error in μ and σ**: realised average return often runs below estimate; realised vol can run above. Full Kelly is exquisitely sensitive — small errors compound.
2. **Drawdown volatility**: Full Kelly has maximum long-run growth, but the *path* is violent. -50% to -70% drawdowns are normal — most people cannot hold through them.

Practitioners almost always use **Half-Kelly** or **Quarter-Kelly** (see series [Part 4 — No-Edge](../series/s1-shannons-demon.md)).

| Fraction | Calm (VIX 17) | Stress (VIX 30) | Crisis (VIX 40) |
|:---|---:|---:|---:|
| **Quarter (¼)** | 43% | 14% | 8% |
| **Half (½) ← default** | 86% → 100% (cap) | 28% | 16% |
| **Full (1×)** | 100% (cap) | 56% | 31% |

The dashboard's first toggle picks one of these:

- **Quarter**: Conservative. Most robust to estimation error. Used by many institutional desks.
- **Half**: Matches the series "No-Edge" article's tone. Default — balances long-run growth against drawdown.
- **Full**: Theoretical max. Only if you have strong conviction in μ/σ estimates *and* the mental/liquidity buffer for big drawdowns.

> **Pick your fraction once and barely change it.** The point is not to react to markets by changing the fraction — it's to let the *same* fraction produce different weights as vol moves.

---

## 4. Why VIX alone isn't enough

VIX alone misses **"smoke without fire"** setups. Example:

- VIX 17 (looks calm)
- But SKEW = 155 (tail risk priced rich)
- COR90D = 55 (correlation regime breaking down)
- VIX futures in backwardation (front > spot)

VIX itself didn't move, but the options market is quietly pricing panic into other surfaces. Riding Kelly@VIX = 86% here usually ends badly within a few days.

Fix: **when other risk-signal groups fire, apply a multiplicative discount to the Kelly base.**

The three groups on the dashboard:

| Group | What it watches | 🟢 Normal | 🟡 Caution | 🔴 Stressed |
|:---|:---|:---|:---|:---|
| **COR/SKEW** | Term-structure spread · COR90D · SKEW | Calm | Mild correlation | Diversification breaks |
| **VIX TS shape** | Futures-curve shape (M1 vs spot, etc.) | Contango | Mixed | Backwardation |
| **VolVol** | VVIX/VIX 5DMA vs 20-day BB middle | Calm | Transition | Stressed |

Each group's worst sub-signal sets the group state, and the state maps to a multiplier on the Kelly base.

---

## 5. Risk sensitivity — the second user toggle

How aggressively those multipliers bite is **your risk-aversion choice**. Three profiles:

| Profile | 🟡 caution | 🔴 danger | All-red cumulative |
|:---|---:|---:|---:|
| **Loose** | × 0.95 | × 0.85 | 0.85³ ≈ 0.61 |
| **Standard** | × 0.90 | × 0.75 | 0.75³ ≈ 0.42 |
| **Tight** | × 0.85 | × 0.65 | 0.65³ ≈ 0.27 |

Reading:

- **Loose**: weak reaction to signals. Even all-red leaves you at 61% of the Kelly base. For people who don't want to rotate frequently.
- **Standard**: matches the series's conservative tone. All-red reduces to ~42% of base — e.g., 86% becomes ~36%.
- **Tight**: strong reaction. All-red drops to 27% of base. For people whose top priority is avoiding tail losses.

> **Picking**: if you hate frequent rebalancing → *Loose*; if "risk signal = big cash" is your philosophy → *Tight*; otherwise → *Standard*.

---

## 6. Final formula — one line

```
Equity Weight = min( f × (μ − r) / σ², 100% ) × d_CS × d_VTS × d_VV
```

| Term | Meaning | User toggle |
|:---|:---|:---|
| **f** | Kelly fraction (¼ / ½ / 1) | **First toggle** |
| **σ = VIX/100** | Forward-looking vol | (auto) |
| **d_CS** | COR/SKEW group multiplier | **Second toggle sets the strength** |
| **d_VTS** | VIX TS shape multiplier | same |
| **d_VV** | VolVol multiplier | same |

**Cash weight = 100% − Equity weight.**

---

## 7. How to use the live dashboard

The first card on the [live dashboard](../index.md) recomputes this every day.

**What you can do inside the card:**

1. **Kelly fraction toggle** (¼ / ½ / Full) — set once and rarely change
2. **Risk sensitivity toggle** (Loose / Standard / Tight) — set to match your philosophy
3. **Decision table** — base value, each group's multiplier, final equity/cash split at a glance
4. **Kelly curve chart** — visualises the VIX → weight relationship with a current-VIX marker

Both selections are saved in browser `localStorage`, so they persist across visits.

**Typical workflow:**

- Check the dashboard ~weekly
- All 🟢 → "stay at current suggested allocation"
- One group flips 🟡 → "start trimming slowly"
- Two or more 🔴 → "raise cash hard, de-risk now"
- After the storm passes → re-deploy gradually as signals normalise

---

## 8. Caveats

This framework **automates a mathematical intuition** — it is not a back-tested production system.

1. **μ = 5% assumption**: if the future equity premium is 3–4% (which many estimates suggest), this overstates the optimal weight. Pick Quarter Kelly to bake in extra conservatism.
2. **VRP bias**: VIX averages 3–5 vol points *above* realised vol (the Volatility Risk Premium). So Kelly base runs slightly conservative — generally safe, but not exactly optimal.
3. **VIX is 30-day forward**: longer holding horizons (6+ months) would want a different σ proxy (e.g., VIX futures average).
4. **Signals aren't independent**: COR/SKEW, VIX TS, and VolVol all view the same underlying stress through different lenses. The multiplicative discount could over-react. The chosen multipliers (≥ 0.75 in Standard) are deliberately mild for this reason.
5. **Post-crisis false positive**: signals like VolVol mechanically lag during recoveries, which can delay re-entry.

> **This is not investment advice.** It is an *educational visualisation* of how Kelly and vol interact. Real decisions need to factor in your risk tolerance, taxes, liquidity, and behavioural limits.

---

## Related reading

- [Series Part 1 — Shannon's Demon](../series/s1-shannons-demon.md): why volatility can be fuel, not enemy
- [Implied Correlation indices](implied-correlation.md): COR3M, IV Surface, Delta Skew
- [Volatility Dashboard (Google Sheets)](volatility-dashboard.md): the manual COR/SKEW tracker
- [VIX Futures Term Structure](vix-term-structure.md): reading the shape

---

*This article focuses on the *mathematical honesty* of vol-driven allocation. Real-world execution layers on transaction costs, taxes, and behavioural limits.*
