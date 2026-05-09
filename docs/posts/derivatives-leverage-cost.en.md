---
title: "Cost of Leverage in Derivatives — Same 3×, Wildly Different Bills"
date: 2023-02-19
tags: [leverage, derivatives, futures, swaps, options, TQQQ, LEAP]
lang: en
series-prev: "[Expected Return — QQQ vs TQQQ](expected-return.md)"
---

# Cost of Leverage in Derivatives — Same 3×, Wildly Different Bills

> "TQQQ's expense ratio is 0.88%, so it's cheap, right?" — On the surface. But the *real* cost goes far beyond that. Leverage itself has a *price*. And depending on which derivative you use, that price ranges from **under 1% to over 70% per year**. There's even a way to get paid for using it.

---

## The 30-second version — where you buy your leverage decides everything

Suppose you want roughly 3× exposure (or similar market exposure) to the same market via five different methods:

| Method | Leverage | Annual cost |
|:-------|:--------:|:-----------:|
| **E-Mini S&P 500 futures (ES)** | 18.87× | **~74% / yr** |
| **Swap contracts (used by TQQQ)** | 3× | **~9.9% / yr** |
| **SPX ATM call (1-year expiration)** | 5.32× | **18.79% / yr** |
| **SPX deep-ITM call (1-year expiration)** | 1.87× | **0.80% / yr** |
| **Synthetic long (long call + short put)** | 6.78× | **0% or *negative* (you receive credit)** |

**More than a 70× spread on the cost of buying the same exposure to the same market.** This article walks through how each method gets to its number.

> All numbers below as of February 2023, SPX = $4,079.09. Numbers shift with rates and volatility, but the *relative cost structure* stays similar.

---

## 1. E-Mini S&P 500 futures (ES) — the cost is invisible until expiry

The S&P 500 futures contract on CME (ticker ES). The [market standard for index leverage](https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.contractSpecs.html).

### Contract specs

| Field | Value |
|:------|:------|
| Contract size | $50 per SPX point |
| Initial margin | $10,600 per contract |
| At SPX = $4,000, market exposure | **$200,000** = $50 × $4,000 |
| **Leverage** | **18.87×** = $200,000 / $10,600 |

### Where the cost comes from — cost of carry

The futures price is set by:

```
Futures price = spot price × exp(risk-free rate × months_to_expiry / 12)
```

Using 10-year Treasury yield (3.86%) as the risk-free rate, a 1-year ES contract:

```
$4,000 × exp(0.0386 × 12/12) = $4,000 × 1.0394 = $4,157
```

If SPX is unchanged at expiry, ES settles at $4,000 — the holder loses **$157 points = $7,850**:

```
Annual cost = $7,850 / $10,600 initial margin = 74.05% per year
```

> **Hold 18.87× leverage for a full year and your P&L absorbs 74% of your initial margin in carry — even if SPX is unchanged.** Reduce leverage (post more margin to keep the same exposure) and the cost scales down proportionally.

---

## 2. Swap contracts — what TQQQ-style leveraged ETFs actually use

[Swap contracts](https://en.wikipedia.org/wiki/Swap_(finance)) don't get much retail attention, but **they're the core institutional tool for leveraged ETFs like TQQQ**.

### How TQQQ actually runs

ProShares' TQQQ, in its November 30, 2022 annual report, shows:

> 220% market exposure delivered via swap contracts

So a **$10,000 TQQQ purchase becomes ~$8,000 in spot + a swap that adds another $22,000 of exposure**, for a total 300% market exposure.

### The cost of swaps

Swaps settle daily at **1-day overnight EFFR + a spread**.

As of November 2022, TQQQ's average swap rate was ≈ **4.5%**.

### Annual cost

Suppose NDX is flat for a year:

```
Swap exposure   = $10,000 × 220% = $22,000
Annual interest = $22,000 × 4.5% = $990
Annual cost     = $990 / $10,000 = 9.9% per year
```

> **9.9% per year** — that's the *real* leverage cost, on top of the 0.88% expense ratio.

### After 2023 — costs explode

The 4.5% swap rate from the 2022 report has climbed to the **high 5%s** as the Fed raised rates aggressively. TQQQ's *true annual cost* is now:

- 2021 (zero-rate era): ~1–2% per year
- **2023–2026 (4–5% policy rate)**: **~9–13% per year**

The cost is 5–10× higher for the same TQQQ. This is exactly the caveat raised in the [previous article on expected returns](expected-return.md).

---

## 3. Options — the only tool where you can *adjust* the cost

Futures and swaps charge what the market dictates. Options let you **change the strike and expiration to dial in your cost** — and even take it negative.

Three cases (all SPX = $4,079.09).

### 3-A. ATM (Near At-The-Money) call, 1-year expiration

```
+SPX Feb162024 4100 call @ 383.25 debit
```

| Field | Value |
|:------|:------|
| Option price | $383.25 (points) |
| Cost (margin) | $38,325 = $383.25 × 100 |
| Delta | 0.50 (ATM) |
| Market exposure | $203,955 = $4,079.09 × 100 × 0.50 |
| **Leverage** | **5.32×** |

**Time value = 100% of cost** (ATM option has zero intrinsic value).

If SPX is unchanged at expiry, the entire $38,325 of time value goes to zero:

```
Annual cost = time value / market exposure = $38,325 / $203,955 = 18.79% per year
```

### 3-B. Deep ITM (In-The-Money) call, 1-year expiration

```
+SPX Feb162024 2000 call @ 2,110.80 debit
```

| Field | Value |
|:------|:------|
| Option price | $2,110.80 |
| Intrinsic value | $4,079.09 − $2,000 = $2,079.09 |
| Time value | $2,110.80 − $2,079.09 = **$31.71** |
| Cost (margin) | $211,080 |
| Delta | 0.97 (deep ITM) |
| Market exposure | $395,672 = $4,079.09 × 100 × 0.97 |
| **Leverage** | **1.87×** |

```
Time value $    = $31.71 × 100 = $3,171
Annual cost     = $3,171 / $395,672 = 0.80% per year
```

> **0.80% per year.** While TQQQ is paying 9.9%, you can buy 1.87× leverage at *0.80%*.

This is the structure famously associated with **Paul Pelosi** (husband of former Speaker Nancy Pelosi) — deep-ITM 1-year-out calls. The cost-efficiency sweet spot is exactly why it gets attention.

### 3-C. Synthetic long — get paid to use leverage

Combine a long call and a short put at the same strike and expiration:

```
+SPX Mar1723 4100 call / -SPX Mar1723 4100 put
```

```
Call price (4,100 long):   $70.70
Put price (4,100 short):   $84.70
Net cost:                  -$14.00 → -$1,400 per 100-share contract (you receive $1,400)
```

| Field | Value |
|:------|:------|
| Margin (IBKR) | $59,175 (= $69,575 − $1,400 credit) |
| Delta | 1.00 (synthetic = 100% of underlying) |
| Market exposure | $407,909 |
| **Leverage** | **6.78×** |

> **6.78× leverage AND a $1,400 credit upfront.**

This is possible when there's *skew* in the option market. In the example above, the strike ($4,100) is slightly off the exact ATM ($4,080) — the put is richer than the call, and selling the put gives more credit than buying the call costs. Not always available, but option-market skew creates these windows often.

> Hedge funds use synthetic positions extensively as [hedging tools](https://www.optionsplaybook.com/option-strategies/synthetic-long-stock/).

---

## 4. Five methods at a glance

| Method | Leverage | Annual cost | Margin | Notes |
|:-------|:--------:|:-----------:|:------:|:------|
| ES futures | 18.87× | ~74% | $10,600 | Most expensive at full leverage |
| Swap (TQQQ) | 3× | ~10% | (built into ETF price) | Costs explode in rate-hike cycles |
| ATM call (1Y) | 5.32× | 18.8% | $38,325 | Risk of full time-value loss |
| **Deep ITM call (1Y)** | **1.87×** | **0.80%** | $211,080 | **The "Pelosi trade"** — minimal time value |
| **Synthetic long** | **6.78×** | **0% to −** | $59,175 | Exploits market skew |

### Key insights

| Insight | Meaning |
|:--------|:--------|
| ES's ~74% is *at full leverage* | Post more margin to drop to 5× → ~20%, to 3× → ~12% |
| Swaps accumulate cost daily | Daily EFFR + spread — costs build until rates ease |
| Deep-ITM calls are *dramatically* cheap | There's a reason Pelosi trades them |
| Synthetic-long margin = short-put risk | If the short put goes ITM, margin requirements explode |

---

## 5. So how do you actually use this?

### Long-term investor

The **LEAP deep-ITM call** discussed in the [Extension series (S3)](../series/s3-preview.md) is the cost-efficiency winner. Buying 1.87× leverage at *under 1% per year* is far more attractive than holding TQQQ.

### Short-term trader

ATM calls are time-decayed *fast*, but they're rational when you're aiming for *a big move in a short window*. Just remember the time value evaporates rapidly.

### TQQQ holder

The [previous article](expected-return.md) showed that *time horizon* matters more than vol drag. But **9–10% per year leverage cost in the high-rate era** is no longer a number you can ignore. It's worth at least evaluating cheaper alternatives (deep-ITM, synthetic long) for the same 3× exposure.

---

## 6. Summary

| Concept | The point |
|:--------|:----------|
| **Futures (ES)** | Cost of carry = risk-free rate. Expensive at full leverage |
| **Swaps (TQQQ)** | EFFR + spread, daily. Explodes in rate-hike cycles |
| **ATM call** | 100% time value. Expensive but useful for short windows |
| **Deep ITM call** | Almost zero time value — the most cost-efficient *leverage tool* |
| **Synthetic long** | Long call + short put. Negative cost possible via skew |

**The single thing to remember**: same market, same exposure — the cost can vary by 70×. Picking the right tool for your time horizon, strategy, and market regime makes a *bigger* difference than picking the right asset.

---

*Previous: [Expected Return — A Probability View of QQQ vs TQQQ](expected-return.md) | Related: [Extension series (S3) — Options in practice](../series/s3-preview.md)*

*Glossary*:
- *Cost of carry* — the risk-free cost of holding an asset (net of dividends and interest)
- *EFFR* — Effective Federal Funds Rate, the overnight inter-bank lending rate in the US
- *Time value* — the part of an option's price beyond intrinsic value; decays to zero as expiration approaches
- *Intrinsic value* — `max(spot − strike, 0)` for a call; the value if exercised right now
- *Delta* — how much the option price moves per $1 move in the underlying
