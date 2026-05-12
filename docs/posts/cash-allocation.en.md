---
title: "Vol-Based Cash Allocation — Kelly meets risk signals"
date: 2026-05-11
tags: [kelly, volatility, vix, position-sizing, cor, skew, volvol, cash-allocation]
lang: en
---

# Vol-Based Cash Allocation — Kelly meets risk signals

> **Where this fits**: The [Principles series](../series/index.md) Part 3 (Kelly's Criterion, paid) gives the Kelly fraction; this article plugs **VIX into σ** to turn it into a daily cash/equity allocation. [Part 1 — Shannon's Demon](../series/s1-shannons-demon.md) closes with "cash is the fuel for rebalancing"; this article is the *how-much* answer. It's the math behind the first card on the daily dashboard.

---

## TL;DR

> **Cut cash when vol is low, raise cash when vol rises** — Kelly's formula makes this intuition quantitative.

**f\* = (μ − r) / σ²** — substitute σ with VIX, and a *doubling* of volatility *quarters* the suggested equity weight (the σ² in the denominator does the work). On top of that base, three extra risk-signal groups (COR/SKEW, VIX TS backwardation, VolVol) layer multiplicative discounts when they fire, raising cash one more notch.

---

## 1. Why volatility is itself a loss — vol drag and the geometric mean

The σ² in Kelly's formula isn't arbitrary. It maps directly to a concrete mechanism: **volatility itself erodes wealth, even when the average return is unchanged.** This is the *real* reason institutions and "smart money" raise cash when vol rises.

### Arithmetic vs geometric mean

There are two ways to average returns:

- **Arithmetic mean**: simple yearly average. "On average, what % per year?"
- **Geometric mean**: the *compounded* return. "What multiple of my capital after 10 years?"

Compounding is multiplicative, so what actually shows up in your account is the **geometric** mean. And the two diverge as volatility rises:

```
Geometric ≈ Arithmetic − σ² / 2
```

This gap is called **vol drag** (or "variance drain", negative compounding). The fact that σ enters *squared* is the whole story.

### Money disappears in sideways markets

| Scenario | Year 1 | Year 2 | Arithmetic mean | Geometric (actual P&L) |
|:---|---:|---:|---:|---:|
| Low vol | +5% | −5% | 0% | **−0.13%** |
| Mid vol | +15% | −15% | 0% | **−1.13%** |
| **High vol** | +30% | −30% | 0% | **−4.6%** |
| Crisis-level | +50% | −50% | 0% | **−13.4%** |

All rows have arithmetic mean 0%, but *actual capital* shrinks faster as vol rises. Look at the last row: +50% then −50% feels like break-even, but capital goes 100 → 150 → 75. **25% loss over 2 years, with zero expected return**.

Money evaporating while you do nothing — that's vol drag.

### Annual drag by VIX level

vol drag per year ≈ σ²/2:

| σ | VIX regime | Drag (annual) |
|:---|:---|---:|
| 16% | Calm VIX | **−1.3%** (tolerable) |
| 20% | Mild stress | −2.0% |
| 25% | Caution | **−3.1%** (meaningful) |
| 30% | Stressed | −4.5% |
| 40% | Crisis | **−8.0%** (overwhelming) |

S&P 500's long-run *arithmetic* mean is ~9%. In a crisis-level vol regime (VIX 40), the 8% drag **eats almost the entire expected return**. Just holding becomes a loss.

### Why smart money reacts to vol signals

Retail investors typically think in *arithmetic* terms: "long-run average is +9%, so just hold". Institutions and hedge funds think in *geometric* terms (= actual long-run growth rate) or in *probability of survival*. They know mathematically that **same arithmetic mean with different vol = completely different long-run outcome**.

Smart-money reasoning:
> "Arithmetic expectation +5% but σ=40% → vol drag is 8% → geometric mean is negative → **holding guarantees long-run loss** → raise cash now."

That's the mechanism. Smart money exits early on vol signals not because of news headlines, but because of multiplicative arithmetic.

### Direct link to Kelly

Once you see this, the σ² in Kelly's formula becomes self-evident:

```
f* = (μ − r) / σ²
```

The denominator σ² *is* the magnitude of vol drag. Kelly is saying: "trim exposure by exactly the amount that variance is eating, so that geometric growth is maximised." Why σ² and not σ? Because vol drag is σ²/2 — same term.

> **Takeaway**: vol creates multiplicative loss (vol drag) → institutions think in geometric terms and react early to vol signals → Kelly's σ² formalises this reaction curve mathematically.

---

## 2. Kelly's formula in one line

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

For the S&P 500, long-run μ ≈ 9%, r ≈ 4%, so **μ − r = 5%** is a *conservative* baseline equity premium. Academic estimates span 3%–9% depending on dataset and methodology — the daily dashboard exposes three preset premia as a toggle (5% / 7% / 9%); see §6½ μ−r toggle for the full comparison. σ runs ~16–20% in calm regimes, spikes to 40–50% in crises.

> **Why σ² and not σ?** The squared denominator is the key. Doubling vol *quarters* the optimal weight. The asymmetric "raise cash quickly" instinct lives in that squared term.

---

## 3. What to plug into σ — VIX

Kelly needs *forward-looking* σ. Historical realised vol tells you the past; you need the future.

**VIX is the cleanest forward-looking estimate.** It is the S&P 500 options market's consensus expectation of 30-day realised vol, annualised, updated tick-by-tick. No single statistical estimator can match the wisdom-of-crowds quality of a deeply liquid options market.

```
σ ≈ VIX / 100
```

VIX = 17 → σ ≈ 0.17. VIX = 30 → σ ≈ 0.30.

| VIX | σ² | Half-Kelly @ μ−r=5% *(conservative)* | Half-Kelly @ μ−r=7% | Half-Kelly @ μ−r=9% |
|---:|---:|---:|---:|---:|
| 12 | 0.0144 | 173% → **100%** | 100% | 100% |
| 17 | 0.0289 | **86%** | 100% (cap) | 100% (cap) |
| 22 | 0.0484 | 52% | 72% | 93% |
| 30 | 0.0900 | 28% | 39% | 50% |
| 40 | 0.1600 | 16% | 22% | 28% |

When vol rises 17 → 30 (1.8×), the suggested weight falls 86% → 28% (1/3). That's where the rough rule "VIX in the high 20s → cut equity in half" comes from — it's the same curve.

![Kelly × VIX curve (μ−r=7%, default)](../assets/diagrams_en/kelly_curve_standard.png)

> On the daily dashboard the same curve shape shifts up/down with the 5% / 7% / 9% toggle (full comparison in §6½). The chart above shows the new default — **7%**.

---

## 4. Kelly fraction — the first user toggle

**Full Kelly (f\* as-is) is theoretically optimal but practically dangerous** for retail. Two reasons:

1. **Estimation error in μ and σ**: realised average return often runs below estimate; realised vol can run above. Full Kelly is exquisitely sensitive — small errors compound.
2. **Drawdown volatility**: Full Kelly has maximum long-run growth, but the *path* is violent. -50% to -70% drawdowns are normal — most people cannot hold through them.

Practitioners almost always use **Half-Kelly** or **Quarter-Kelly** (see the [Principles series](../series/index.md) Part 4 "No Edge in the Game" — paid). The daily dashboard also exposes **¾ Kelly** as a compromise — it's the meaningful middle ground in the VIX 19+ region where Half feels over-conservative and Full feels reckless.

| Fraction | Calm (VIX 17) | Stress (VIX 30) | Crisis (VIX 40) |
|:---|---:|---:|---:|
| **Quarter (¼)** | 43% | 14% | 8% |
| **Half (½)** | 86% → 100% (cap) | 28% | 16% |
| **¾ Kelly ← default** | 100% (cap) | 42% | 23% |
| **Full (1×)** | 100% (cap) | 56% | 31% |

The dashboard's first toggle picks one of these:

- **Quarter (¼)**: Most conservative. Most robust to μ/σ estimation error. Used by many institutional desks and fits pre-retirement / withdrawal-phase profiles where drawdown depth doubles as a redemption risk.
- **Half (½)**: The academic standard. **Minimises CAGR variance** — i.e. "slightly slower long-run growth but smoothest path." Matches the conservative tone of [Principles Part 4](../series/index.md) ("No Edge in the Game").
- **¾ Kelly (default)**: Meaningful middle ground between Half and Full. Below VIX 19 it caps at 100% the same as Full, but in the VIX 20–35 caution zone it sits squarely between Half (over-conservative for most accumulators) and Full (over-aggressive given σ uncertainty). Chosen as the new-visitor default for retail accumulators.
- **Full (1×)**: Theoretical max. Only if you have strong conviction in μ/σ estimates *and* the mental/liquidity buffer for −50% to −70% drawdowns. Rarely recommended in the literature.

> **Pick your fraction once and barely change it.** The point is not to react to markets by changing the fraction — it's to let the *same* fraction produce different weights as vol moves.

### Deep dive: Is it reckless to bump fraction up during a crash?

Common question — would shifting from Half to Full mid-crash be reckless?

**Math has a defensible answer.** Forward μ−r likely expands as prices fall — a 5% → 8–10% jump is reasonable in deep drawdowns. Full Kelly at VIX 60 with μ−r = 10% gives ~28%; Half Kelly at the same VIX with μ−r = 5% gives 7%. The 4× difference is meaningful, but absolute risk stays modest given the 80%+ cash you're already holding.

**Don't modulate the fraction itself, though:**

- **Catching falling knives** — VIX > 60 *looks* like a bottom, but 2008 had two such spikes a year apart. "Deep enough?" only resolves with hindsight.
- **Estimation-error paradox** — σ is most uncertain precisely when μ estimation is also most uncertain. Bumping fraction at the moment of maximum estimation noise is the opposite of conservative.
- **Behavioural risk** — touching the toggle at peak fear is by definition an emotional act. The whole point of a fixed fraction is to remove that lever.
- **Backfit triggers** — "VIX > 50 sustained 5 days" reads well in hindsight but is fitted to past crises; no guarantee it generalises.

### Tactical bucket is the framework's *essential complement*

Stopping here misses something important. Recall the series' two core claims:

1. **Long-run upward drift** — over long-enough windows, equities beat bonds/cash.
2. **Time is the retail edge** — retail investors have a *structural* advantage in being able to wait without redemption pressure.

Combining the two implies: **forward risk premium expands most precisely at peak crisis**. Without a mechanism to deploy capital in that moment, you claim a time edge but *don't use it when it's most valuable* — a self-contradiction.

**What the defensive framework alone misses:**

- Kelly × VIX auto-deleverage takes you 100% → 2% during a crash ✓ (cascade absorbed)
- VIX cools → auto-rebuild — but you buy back at *recovery* prices, *not bottom* prices
- Net: vol drag avoided, but real buy-low never happens. Of [Shannon's Demon](../series/s1-shannons-demon.md)'s "rebalancing = buy low + sell high", only sell-high engaged.

So **split cash into two kinds** — that completes the structure the series argues for:

| Bucket | Role | Mechanism |
|:---|:---|:---|
| **Main bucket** | Defensive — *fuel for survival* | Kelly × VIX + risk signals. Auto-deleverage / auto-re-entry. |
| **Tactical bucket** | Offensive — *fuel for attack* | Composite extreme triggers (VIX, COR/SKEW, SPX drawdown), laddered deploy. Monetises the time edge. |

The split between the two is itself a toggle — the daily dashboard's master bar lets you pick **80/20 · 90/10 · 95/5**. New-visitor default is **90/10** (90% main, 10% tactical). The tradeoff table + situation-based recommendations live in "Choosing the split" below.

### Tactical bucket operating rules

- **Size**: 5–20% of total (dashboard toggle). Too large destabilises the main framework and inflates normal-regime cash drag; too small makes deployment symbolic. The default 10% is the middle compromise.
- **Composite triggers** — T1 is laddered, T2/T3 binary:
    - **T1 (VIX sustained 5 days, tiered)**
        - 5-day VIX min > **40** → weight **0.5** (mild partial entry)
        - 5-day VIX min > **50** → weight **1.0** (standard tranche)
        - 5-day VIX min > **60** → weight **1.5** (deep stress, large tranche)
    - **T2 (cross-asset stress)**: COR90D > 55 AND SKEW > 150 simultaneously → weight **1.0**
    - **T3 (price capitulation)**: 30-day cumulative SPX decline ≥ **20%** → weight **1.0**
- **Laddered deploy** — total weight ÷ 3 → deploy %, capped at 100:
    - e.g., 5-day VIX min = 45 (T1=0.5) + COR/SKEW fired (T2=1.0) + SPX −22% (T3=1.0) → total 2.5 → 83% deploy
    - All signals max (VIX 60+, T2, T3) → total 3.5 → cap 100% (capitulation)
- **State labels** — deploy % maps to 5 tiers:

    | Deploy % | 0% | 1–33% | 34–66% | 67–99% | 100% |
    |:---|:---:|:---:|:---:|:---:|:---:|
    | State | 🟢 Inactive | 🟡 Tranche 1 | 🟠 Tranche 2 | 🔴 Tranche 3 | 🔴 Capitulation |

- **Refill gradually in recovery** — once vol calms, refill tactical bucket from the main framework's exposure-reduction proceeds or from gains. Don't leave it empty forever after one deployment.
- **Pre-defined rules only** — no "feel". Deploy *only* on pre-specified conditions. If conditions aren't met, sit still. (Blocks emotional entries.)

> **Bottom line**: Never modulate the Kelly fraction itself. *Instead*, pair the main framework with a tactical bucket. The framework owns *survival*; the tactical bucket *monetises the time edge*. Together, the two are what completes the series' "**volatility as fuel**" thesis.

### Choosing the split {: #choosing-the-split }

The live-dashboard master bar lets you pick between **80/20 · 90/10 · 95/5**. The trade-off in one line: **cash drag in normal conditions vs crisis-buy firepower**.

**Cash drag (normal regime)**

The tactical bucket sits in 100% cash by default — it only deploys when T1/T2/T3 fire, which is *most days*. Assuming long-run SPX ≈ 9%/yr:

| Split | Idle cash (normal regime) | Annual opportunity cost (CAGR) | 20-year compounded |
|:---|:---:|:---:|:---:|
| 80/20 | 20% | −1.8% | ≈ −30% |
| 90/10 | 10% | −0.9% | ≈ −16% |
| 95/5  | 5%  | −0.45% | ≈ −8% |

**Crisis firepower**

Even if the tactical bucket fully deploys, its impact on the *total* portfolio depends on the split:

| Split | Max additional buy (whole portfolio) | Intuition |
|:---|:---:|:---|
| 80/20 | +20% buy | Meaningful entry at VIX 60 + capitulation |
| 90/10 | +10% buy | Supplementary; main framework's auto-re-entry does the heavy lifting |
| 95/5  | +5% buy | Almost symbolic — meaningful only at real capitulation (T3, SPX −20%) |

**Trigger frequency (2010–2024, rough)**

| Trigger | Days fired | % of days |
|:---|:---:|:---:|
| T1 VIX>40 sustained 5d | ~25 | 0.6% |
| T2 COR>55 & SKEW>150 | ~10 | 0.25% |
| T3 SPX 30d −20% | ~12 | 0.3% |

**99% of days, the tactical bucket = just idle cash**. The question is how much you're willing to immobilise for that 1%.

**Recommendations (by situation)**

| Situation | Split | Why |
|:---|:---:|:---|
| Accumulation (long horizon, early career) | **95/5** | Maximise compounding via time edge. Reserve only for real capitulation (T3). |
| Mid-stage (late accumulation, wealth-building) | **90/10 ← default** | Minimise drag while preserving meaningful entry at VIX>60. New-visitor default. |
| Conservative (pre-retirement, withdrawal phase, behavioural concerns) | **80/20** | Sequence-of-returns defence. Crisis firepower + emotional buffer. |

> **Honest take**: 80/20 is largely a *behavioural insurance premium*. Mathematically, Kelly is already discounted (½ or ¾) and σ=VIX/100 already responds to volatility — adding another 20% cash buffer is a triple safety margin. That's why the retail-accumulator default lands on **90/10** — it halves the normal-regime cash drag while still keeping 10% of the portfolio as deploy firepower. Pick 95/5 if you trust yourself not to touch the toggle mid-crash; 80/20 if sequence-of-returns risk worries you.

---

## 5. Why VIX alone isn't enough

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
| **COR/SKEW** | Term-structure spread · COR90D · SKEW | All sub-signals normal | Any one caution | Any one danger |
| **VIX TS shape** | M1 vs VIX spot, M2 − M1 | Contango (M2 > M1, spot < M1) | Mixed (M2 ≤ M1 but spot ≤ M1) | Backwardation (spot > M1) |
| **VolVol** | VVIX/VIX 5DMA vs 20-day BB middle | 5DMA > middle | Cross within last 5 days | 5DMA < middle |

Each group's worst sub-signal sets the group state, and the state maps to a multiplier on the Kelly base.

> **Indicator deep-dives**: COR/SKEW in the [Implied Correlation article](implied-correlation.md), VIX TS shape in the [VIX Futures Term Structure article](vix-term-structure.md), VolVol (VVIX/VIX ratio with 5DMA + 20-day BB) in the [live-dashboard VolVol card](../index.md) and upcoming Execution series Part 3 — *Vol-of-vol and market sentiment* (paid).

---

## 6. Risk sensitivity — the second user toggle

How aggressively those multipliers bite is **your risk-aversion choice**. Three profiles:

| Profile | 🟡 caution | 🔴 danger | All-red cumulative |
|:---|---:|---:|---:|
| **Loose** | × 0.95 | × 0.85 | 0.85³ ≈ 0.61 |
| **Standard ← default** | × 0.90 | × 0.75 | 0.75³ ≈ 0.42 |
| **Tight** | × 0.85 | × 0.65 | 0.65³ ≈ 0.27 |

Reading:

- **Loose**: weak reaction to signals. Even all-red leaves you at 61% of the Kelly base. For people who don't want to rotate frequently.
- **Standard (default)**: matches the [Principles series](../series/index.md) conservative tone. All-red reduces to ~42% of base — e.g., ¾ Kelly at 100% (cap) becomes ~42%.
- **Tight**: strong reaction. All-red drops to 27% of base. For people whose top priority is avoiding tail losses.

> **Picking**: if you hate frequent rebalancing → *Loose*; if "risk signal = big cash" is your philosophy → *Tight*; otherwise → *Standard*.

---

## 6½. Equity premium μ−r — the third user toggle

The numerator of `f* = (μ−r) / σ²` is the **equity risk premium**: "how much *more* do you expect equities to earn over the risk-free rate, annualised?"

The problem: you can't know this number exactly. Academic estimates span **3% to 9%** depending on dataset, time window, and computation method — your choice almost doubles the suggested weight in some regions. The daily dashboard exposes three preset premia:

| Profile | μ−r | Rationale | Half @ VIX 18 | Half @ VIX 22 | Half @ VIX 30 |
|:---|:---:|:---|---:|---:|---:|
| **Conservative** | **5%** | Long-run academic estimate (Damodaran et al.). Implicitly absorbs the VIX vol-risk-premium drag — i.e. acknowledges VIX ≈ realised σ + 4pt on average, so you're effectively inflating σ. | 74% | 52% | 28% |
| **Standard ← default** | **7%** | Long-run SPX historical average ex-WWII. The closest single-number match to "Kelly applied to *realised* vol" once VIX's vol-risk premium is netted out. | 100% (cap) | 72% | 39% |
| **Aggressive** | **9%** | Post-1990 SPX bullish view. Treats the VIX vol-risk-premium drag as a recoverable inefficiency rather than a baked-in cost. | 100% (cap) | 93% | 50% |

### Why 5% is "conservative" — the VIX vol-risk-premium story

The key intuition: **VIX runs 3–5 pts above realised vol on average** (the Vol Risk Premium — option buyers pay an insurance premium). VIX = 18 typically corresponds to ~14% actual realised vol over the following 30 days.

Plugging σ = VIX/100 into Kelly with that bias makes σ² = (0.18)² = 0.0324 — about 1.65× larger than the "true" σ² = (0.14)² = 0.0196. **A 1.65× larger denominator means a 1.65× smaller suggested weight** — so the Kelly base already comes out conservative just from how σ is sourced.

Two ways to compensate:
1. Plug in realised vol directly (hard to estimate live).
2. Bump μ−r in the numerator to offset the inflated denominator.

**μ−r = 5% + σ = VIX/100** is effectively "conservative-Kelly + conservative-σ" — *doubly* conservative. Raising μ−r to 7–9% unwinds the σ inflation, producing weights that line up much closer to what a realised-vol Half-Kelly would give.

### Which value to pick?

| Your view | Recommended μ−r |
|:---|:---:|
| "Future SPX could underperform history (lost-decade scenario)" | **5%** |
| "Long-run, SPX delivers historical-average premium" (most-cited single number) | **7% ← default** |
| "Post-1990 US exceptionalism + AI tailwinds continue (bullish)" | **9%** |

The default lands on **7% (Standard)** because:
- It matches the most-cited long-run historical SPX premium.
- It best offsets VIX's vol-risk-premium drag, making the framework approximate realised-vol Kelly without requiring you to estimate realised vol live.

> **Like the Kelly fraction (¼/½/¾), pick once and barely touch it.** This isn't a market-condition toggle — it's a one-time declaration of your *long-run market view*.

### The chart curve moves with the toggle too

The Kelly × VIX curve below the card is rendered as three separate PNGs (one per premium); selecting a μ−r swaps the image. The 5% curve sits lowest, 9% highest — visually showing how the same VIX level maps to wildly different suggested weights depending on your premium assumption.

---

## 7. Final formula — one line

```
Equity Weight = min( f × (μ − r) / σ², 100% ) × d_CS × d_VTS × d_VV
```

| Term | Meaning | User toggle |
|:---|:---|:---|
| **f** | Kelly fraction (¼ / ½ / ¾ / 1) | **First toggle** |
| **μ−r** | Expected equity premium (5% / 7% / 9%) | **Third toggle** |
| **σ = VIX/100** | Forward-looking vol | (auto) |
| **d_CS** | COR/SKEW group multiplier | **Second toggle sets the strength** |
| **d_VTS** | VIX TS shape multiplier | same |
| **d_VV** | VolVol multiplier | same |

**Cash weight = 100% − Equity weight.**

---

## 8. How to use the daily dashboard

The first card on the [daily dashboard](../index.md) recomputes this every day.

**What you can do inside the card** (defaults marked with †):

1. **Kelly fraction toggle** (¼ / ½ / **¾†** / Full) — set once and rarely change. Full comparison in §4.
2. **Risk sensitivity toggle** (Loose / **Standard†** / Tight) — how aggressively signals discount. Full comparison in §6.
3. **Equity premium μ−r toggle** (5% / **7%†** / 9%) — your view on long-run SPX premium. Full comparison in §6½.
4. **Decision table** — base value, each group's multiplier, final equity/cash split at a glance.
5. **Kelly curve chart** — visualises the VIX → weight relationship. **Syncs with the μ−r toggle** (three pre-rendered PNG variants, JS swaps `src`). Current-VIX marker included.
6. **Master-bar split selector** (80/20 · **90/10†** · 95/5) — main/tactical bucket ratio. Full comparison in §4 "Choosing the split."

All selections persist in browser `localStorage` and carry over between visits.

**Typical workflow:**

- Check the dashboard ~weekly
- All 🟢 → "stay at current suggested allocation"
- One group flips 🟡 → "start trimming slowly"
- Two or more 🔴 → "raise cash hard, de-risk now"
- After the storm passes → re-deploy gradually as signals normalise

---

## 9. Real-world behavior — first gap vs the cascade

The framework's value lies in the *cascade* that follows the first shock, not the first shock itself. A −3% or −5% gap on day 1 is the entry cost — outside of insiders or lucky timing, no rule-based system can avoid it. The real difference shows up in the *days and weeks after*.

| Phase | Market | Auto-response |
|:---|:---|:---|
| **Day 1 gap** | Sudden −5% | Taken at full position (entry cost of a reactive framework) |
| **Day 2 ~ N** | VIX spikes → σ² × 4 → Kelly base ÷ 4 + all-red signals × 0.42 | Subsequent drops hit an *already shrunken* equity base |

### Historical examples

**March 2020 COVID crash** *(scenario uses Half-Kelly @ μ−r=5% — the most conservative toggle combo)*:

| Date | VIX | Half-Kelly @ 5% base | Signals | Suggested mix |
|:---|---:|---:|:---|---:|
| Feb 14 (calm) | 14 | 100% (cap) | All 🟢 | Equity 100% / Cash 0% |
| Feb 24 (−3.4% first gap) | 28 | 32% | Some 🟡 | Equity ~25% / Cash ~75% |
| Mar 16 (bottom) | 82 | 4% | All 🔴 | **Equity ~2% / Cash ~98%** |

VIX 14 → 82 (6×) cuts the suggested weight from 100% to 2%. The additional ~−25% drawdown across this month lands on a *much smaller* equity base, dramatically reducing cumulative loss vs a static fully-invested position.

> **Under the new defaults (¾ Kelly @ μ−r=7%)** the same VIX path produces a base of 67% at VIX 28 and 8% at VIX 82 — starting higher, but deleveraging at the same rate. The absolute numbers differ, but the *slope* of the response is identical. The scenario's lesson — cascade absorption — is invariant to which toggle combo you pick; only the starting point shifts.

**September 2008 Lehman week:**

The first week after Lehman's bankruptcy (−10%) is unavoidable. But the additional −25% over the following month lands on an already deleveraged portfolio, so cumulative loss runs roughly half of what a static fully-invested position would take (illustrative).

> **TL;DR**: The framework is a *cascade buffer*, not a forecaster. The first gap is the entry cost; the value is in shrinking the cumulative loss that follows.

---

## 10. Caveats

This framework **automates a mathematical intuition** — it is not a back-tested production system.

1. **μ − r assumption is uncertain**: academic estimates of the equity-risk premium span 3–9% across studies. The daily dashboard's **μ−r toggle (5% / 7%(default) / 9%)** lets you swap your own view (full breakdown in §6½). 5% is conservative and effectively bakes in the VIX vol-risk-premium drag; default 7% is the long-run SPX historical average and the closest match to realised-vol Kelly; 9% is a post-1990 bullish view.
2. **VRP bias**: VIX averages 3–5 vol points *above* realised vol (the Volatility Risk Premium). So Kelly base with μ−r=5% runs *substantially* conservative — the default 7% is closer to realised-vol Kelly, and 9% approaches the "VRP fully recoverable" assumption. The toggle is the explicit handle for this trade-off.
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
