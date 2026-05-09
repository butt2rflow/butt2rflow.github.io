---
title: "Expected Return — A Probability View of QQQ vs TQQQ"
date: 2023-02-26
tags: [expected-value, probability, QQQ, TQQQ, leverage, vol-drag]
lang: en
series-prev: "[How is my portfolio actually doing? — TWR vs MWR](portfolio-return.md)"
series-next: "[Cost of Leverage in Derivatives](derivatives-leverage-cost.md)"
---

# Expected Return — A Probability View of QQQ vs TQQQ

> "TQQQ supposedly melts in sideways markets — so it must lose money over time, right?" — Short answer: **no**. Build a probability model from 10 years of data and the negative compounding doesn't fully eat the positive compounding. Here's why, with pictures.

> If the [previous article](portfolio-return.md) covered TWR and MWR, this article is the next step — *expected value*. Estimating future returns by *probability-weighting* the outcomes.

---

## 1. Expected value vs average — what's the difference?

### Average

Roll a die ten times: 2, 3, 4, 6, 1, 2, 6, 1, 5, 1.

Average = (2+3+4+6+1+2+6+1+5+1) / 10 = **3.1**

That's the average of *what already happened*.

### Expected value

Now you're about to start a new game. What's the expected outcome of the next single roll?

| Event | Outcome | Probability |
|:------|:-------:|:----:|
| 1 rolls | 1 | 1/6 |
| 2 rolls | 2 | 1/6 |
| 3 rolls | 3 | 1/6 |
| 4 rolls | 4 | 1/6 |
| 5 rolls | 5 | 1/6 |
| 6 rolls | 6 | 1/6 |

Expected value = (1+2+3+4+5+6) × 1/6 = **3.5**

> **Expected value = sum of (outcome × probability) across all events**
>
> *Estimates a future average* using probabilities you already know.

Ten rolls might average 3.1, or 3.5, or anything close. **Roll an infinite number of times and the average converges on 3.5** (the law of large numbers).

---

## 2. Building a probability model for stock returns

Stocks aren't dice. **You don't know the probabilities in advance.** So you estimate them from *historical data*.

> "The past doesn't repeat exactly" — everyone knows. But *past data is the most defensible starting point*. Even the well-worn phrase "U.S. markets trend up over the long run" is itself an expectation built from historical data.

### The data

- **Asset**: QQQ (Nasdaq-100 ETF)
- **Window**: 2013-02-27 to 2023-02-25 (10 years, 2,517 trading days)
- **Metric**: [Log returns](log-return.md) — daily log return for each trading day

In Google Sheets, one line:

```
=ARRAYFORMULA(IF(B4:B2519, LN(B3:B2518/B4:B2519), ""))
```

### Bucket trading days into "weeks" and "months"

Group each trading day into rolling windows (week = 5 days, month = 20 days for simplicity):

```
Weekly Win    = COUNTIF(prior 5-day returns, ">0")  ← 0–5 (up days in the window)
Weekly Return = SUM(prior 5-day returns)            ← total log return for the window

Monthly Win    = COUNTIF(prior 20-day returns, ">0")  ← 0–20
Monthly Return = SUM(prior 20-day returns)
```

Log returns *just add* to give the window's total return — that's the trick from the [previous article](log-return.md).

---

## 3. Distribution of "up days in 5"

Slide a 5-day window across the last 10 years of QQQ and count up-days:

| Up days in 5 | Count over 10 years | Meaning |
|:------------:|:------------------:|:--------|
| 0 (all down) | 34 | Brief downtrend |
| 1 | ~200 | Mild downtrend |
| 2 | 800+ | **Sideways** |
| 3 | 800+ | **Sideways** |
| 4 | ~400 | Mild uptrend |
| 5 (all up) | 140 | Brief uptrend |

**Cases where up/down counts are similar (2 or 3 up days) overwhelmingly dominate.** It's nearly normally-distributed — that's the nature of the market.

Looking at weekly windows, **sideways was the most common state** over the past 10 years. The same pattern holds for monthly (20-day) windows — peak around 10 up-days, normal-distribution-shaped (with a slight upward bias for QQQ).

---

## 4. Computing expected return — QQQ

Convert event *counts* into *probabilities*, multiply by the average return for each event, sum:

```
Expected return = Σ (avg return for the event × probability of the event)
```

For QQQ over 10 years:

| Window | QQQ expected return |
|:-------|:-------------------:|
| 1 week (5 days) | **+0.29%** |
| 1 month (20 days) | **+1.19%** |

**Annualized: roughly +14% to +15%**. That matches the QQQ growth story over the past decade — a number we recognize.

---

## 5. What about TQQQ? — Not 3×, but more than 2×

Same calculation for TQQQ (3× leveraged):

| Window | QQQ | TQQQ | Ratio |
|:-------|:---:|:----:|:-----:|
| 1 week | +0.29% | **+0.59%** | 2.03× |
| 1 month | +1.19% | **+2.38%** | 2.00× |

**Not 3×.** That's the [negative compounding effect (vol drag)](https://docs.google.com/spreadsheets/d/1xTr7wYCjaP2IYOMW-rUd6r5ILLpupfemeJAnBJGAMs4/copy) at work in sideways markets — sideways periods are far more numerous, so they pull the average down.

But still **more than 2×**. Vol drag *doesn't quite eat* the positive compounding (the amplification that happens in sustained bull or bear runs).

### Why this works out

Even with a normally-distributed return shape, **rare extreme moves** (sustained bull/bear runs) pull the *expectation* up.

> The market runs *on math*. Lower-probability events necessarily pay more — like a lottery: lower odds of winning the jackpot means a bigger jackpot.

The exponential up-runs in leveraged ETFs are rare, but a single one of them more than compensates for many sideways windows of decay.

---

## 6. Sanity check — 1-year windows

### Bear year (2022-02-25 to 2023-02-25)

| | QQQ | TQQQ |
|:--|:---:|:----:|
| Monthly expected return | ~**−1.6%** | ~**−5.5%** |
| TQQQ/QQQ | | ~3.4× (negative) |

In a sustained bear year, TQQQ is *worse than 3×* — both positive compounding (working in the down direction) and vol drag amplify.

### Bull year (2020-04-01 to 2021-03-31)

| | QQQ | TQQQ |
|:--|:---:|:----:|
| Monthly expected return | ~**+4%** | ~**+15%** |
| TQQQ/QQQ | | ~3.7× |

In a sustained bull year, TQQQ is *better than 3×*. The positive compounding dominates.

### The takeaway

> **Short-term, TQQQ moves at less or more than 3× depending on the regime. But over *long enough* time horizons, positive compounding has historically offset the negative compounding and left roughly 2× the expectation.**

If you believe in the long-run upward trend of U.S. markets, **the *length* of your time horizon matters more than vol drag**.

---

## 7. The big caveat — the era has changed

The past 10 years (2013–2023) were largely a *low-rate* environment. The 2016–2019 hiking cycle did reach 2.5%, but 2013–2015 and 2020–2021 were essentially zero — the decade-long average is roughly 1%.

**Now it's different (4–5% as of 2026).** Leveraged ETFs' operating costs are [directly tied to the policy rate](derivatives-leverage-cost.md). The swap contracts TQQQ uses pay 1-day overnight EFFR + a spread, every day.

So:

- **Zero-rate era (2013–2021)**: leverage cost ~1–2% per year
- **High-rate era (2022–2026)**: leverage cost ~9–10% per year or more

**Same vol drag, same market regime, but the cost is 5× higher.** You can't take past 10-year expectations and apply them blindly to today.

> **Next**: [Cost of Leverage in Derivatives](derivatives-leverage-cost.md) — how much TQQQ pays per year, and whether options are cheaper.

---

## 8. Summary

| Concept | The point |
|:--------|:----------|
| **Expected value** | Future-result estimate = sum of (outcome × probability) |
| **Probability model** | For stocks, must be estimated from historical data |
| **5-day distribution** | Roughly normal — sideways is the dominant state |
| **QQQ monthly EV** | +1.19% (past 10 years) |
| **TQQQ monthly EV** | +2.38% — not 3×, only 2×. Vol drag is the reason |
| **But still positive** | Vol drag doesn't fully eat positive compounding |
| **High-rate caveat** | Leverage costs become a real drag |

**The single thing to remember**: the dominance of sideways periods doesn't mean leveraged ETFs lose money — it means the *rare* explosive bull runs more than offset the sideways decay. That was the conclusion over the past decade. *The high-rate environment can shift that balance*, so be careful applying old data forward.

---

## Example Google Sheets (make a copy)

- [QQQ 10-year probability model](https://docs.google.com/spreadsheets/d/1Ax-CdovPsR5BAaMQXYisgidCS5y2rhvwFhrhfAVXTKY/copy)
- [TQQQ 10-year probability model](https://docs.google.com/spreadsheets/d/1xTr7wYCjaP2IYOMW-rUd6r5ILLpupfemeJAnBJGAMs4/copy)
- [QQQ 1-year (bear)](https://docs.google.com/spreadsheets/d/1NsscBSLiy5vBNWRfVWbNpMdzhJKGGYkkSRnTg7QjjII/copy)
- [QQQ 1-year (bull)](https://docs.google.com/spreadsheets/d/1T4mAqNYYlI1wMAJImDNAGzY583-Mq9t0oiGVJ-lfg2A/copy)

---

*Previous: [How is my portfolio actually doing? — TWR vs MWR](portfolio-return.md) | Next: [Cost of Leverage in Derivatives](derivatives-leverage-cost.md)*

*Related: [Returns, Compounding, and Log Charts](log-return.md) | [Shannon's Demon — arithmetic vs geometric mean (S1 series)](../series/s1-shannons-demon.md)*
