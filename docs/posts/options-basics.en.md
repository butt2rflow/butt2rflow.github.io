---
title: "Options Basics — Calls and Puts via Car Insurance"
date: 2026-05-09
tags: [options, basics, call, put, strike, expiration, delta, time-value]
lang: en
---

# Options Basics — Calls and Puts via Car Insurance

> "Options are dangerous." "Options are gambling." We've all heard those. The reality: options work *exactly like car insurance*. This single analogy unlocks 80% of options.

> This article is the free intro to options vocabulary, meant to be read *before* [Hedging the Wings](hedging-wings.md), [Cost of Leverage in Derivatives](derivatives-leverage-cost.md), and the paid [Extension (S3 series)](../series/s3-preview.md).

---

## The 30-second version — options = car insurance

| Car insurance | Put option |
|:---|:---|
| Annual **premium** (the cash you pay) | Option **premium** |
| **Coverage limit** (max payout if you crash) | **Strike price** — you can sell at *this price* even if the market drops further |
| Policy term (1 year) | **Expiration** — the date the right disappears |
| No accident → premium is *gone* | No drop → option is *gone* |

Memorize this table and **a put option = car insurance for your stocks**. A call option is just the opposite direction (the right to *buy* at a fixed price if the stock rallies) — same analogy.

---

## 1. Calls and puts — that's it

There are exactly two kinds of options:

| | **Call** | **Put** |
|:---|:---|:---|
| **Right to do what?** | *Buy* the stock | *Sell* the stock |
| When is it valuable? | Stock goes **up** | Stock goes **down** |
| Everyday analogy | Movie ticket pre-sale (right to buy at a discount) | Car insurance (right to sell at a fixed price after a "crash") |
| Who *sells* it? | Stockholders (covered calls) | Market makers, institutions |

**The key**: an option is a *right*, not an *obligation*. Don't exercise → done. Maximum loss = the premium you paid up front.

> "You have the right but don't have to use it" — that's the essence of options. Maximum loss = premium, and that asymmetry is what makes options useful.

---

## 2. Strike price — the *coverage limit*

Both calls and puts have a *strike price*. With SPY at $540:

- **Buy SPY $550 call** → "If SPY goes *above* $550, I'll capture the upside"
- **Buy SPY $530 put** → "If SPY drops *below* $530, I'll collect the insurance payout"

Strike is the insurance *coverage limit*. Whether spot crosses the strike determines the option's state:

| State | Term | Call meaning | Put meaning |
|:---|:---:|:---|:---|
| **In the Money** | ITM | Spot > strike — *profit* if exercised now | Spot < strike — *profit* |
| **At the Money** | ATM | Spot ≈ strike | Same |
| **Out of the Money** | OTM | Spot < strike — *loss* if exercised | Spot > strike — *loss* |

> **Three abbreviations to remember**: ITM = already profitable / ATM = breakeven zone / OTM = no payoff yet.
>
> Option premium is most expensive at ITM and cheapest at OTM — same reason fire insurance is more expensive on a house already on fire.

---

## 3. Expiration — options are *time* you're buying

Car insurance is annual. Options have expirations too — but they range from *daily, weekly, monthly, quarterly, to 1+ year*:

| Expiry | Nickname | Notes |
|:---|:---|:---|
| Same day | **0DTE** | Most volatile and risky. ~60% of SPX volume is now 0DTE |
| 1 week | Weekly | Short-term trading |
| 1–3 months | Monthly | Most common |
| 3–12 months | Quarterly | Mid-term hedging |
| **1 year+** | **LEAP** | Long-term investment / leverage — [the *real* cost of LEAPs](derivatives-leverage-cost.md) |

Longer expiry = more *time value* = more expensive option. As expiry approaches, *time decay* (theta) eats into the option daily.

> **Time decay is the option *buyer's* enemy and the option *seller's* friend.** Buyers lose value over time; sellers collect it. That's why covered calls are a *harvesting* strategy.

---

## 4. Time value vs intrinsic value — price decomposition

The option premium splits into two parts:

```
Option price = Intrinsic value + Time value
```

- **Intrinsic value**: what you'd get by exercising right now. Zero unless ITM.
- **Time value**: a premium for "remaining time + volatility potential"

Example (SPY at $540, buying a 1-year call):

| Strike | Option price | Intrinsic | Time value | Reading |
|:---:|:---:|:---:|:---:|:---|
| $540 (ATM) | $25 | $0 | **$25** | 100% time value — vanishes if stock doesn't move |
| $300 (Deep ITM) | $245 | $240 | **$5** | Almost all intrinsic — time value tiny (the heart of the [Pelosi trade](derivatives-leverage-cost.md)) |
| $700 (Deep OTM) | $1 | $0 | **$1** | Lottery ticket — only pays off on a moonshot |

> **Why deep ITM options are *the* leverage tool**: small time-value ratio = small *daily decay* = stable hold. That's the punchline of [Cost of Leverage in Derivatives](derivatives-leverage-cost.md).

---

## 5. Delta — the *probability of finishing ITM*

Delta means two things at once:

1. **How much the option price moves per $1 in the underlying**
2. **(Approximately) the probability the option finishes ITM at expiration**

| Delta (call) | Reading |
|:---:|:---|
| **0.10** (10Δ) | Deep OTM — ~10% chance of finishing ITM |
| **0.25** (25Δ) | OTM — ~25% chance |
| **0.50** (50Δ) | ATM — 50% (coin flip) |
| **0.75** (75Δ) | ITM — ~75% |
| **0.97** (97Δ) | Deep ITM — practically certain |

Put deltas are negative (−0.10, −0.25, …) — the *downside* direction. In hedging strategies, "buy a 10Δ put" means you're buying insurance against a ~10% downside move — that's the math behind [Hedging the Wings](hedging-wings.md)'s 1:2 Put Ratio.

---

## 6. How to actually trade options as a retail investor

For SPX/SPY options, **Interactive Brokers (IBKR)** is the de-facto standard for serious options traders:

| Mainstream broker (Robinhood, Webull, etc.) | IBKR |
|:---|:---|
| Limited selling (naked-short restrictions) | All strategies supported (spreads, synthetics, etc.) |
| Higher fees | Very low (~$0.65 per contract) |
| Simple UI | Power-user UI (steeper learning curve) |
| Standard margin | Portfolio margin available (lower effective margin) |

If you're running multi-leg strategies (spreads, synthetics, 0DTE, etc.), IBKR is the standard. For simple call/put buying, mainstream brokers are fine.

---

## 7. Summary

| Concept | One line |
|:---|:---|
| **Call option** | Right to buy (bullish) |
| **Put option** | Right to sell (bearish or hedge) |
| **Strike** | Exercise price |
| **Expiration** | Date the right disappears |
| **ITM/ATM/OTM** | Profit state (in/at/out of the money) |
| **Intrinsic value** | Value if exercised now |
| **Time value** | Premium for remaining time and volatility |
| **Delta** | Price sensitivity ≈ probability of finishing ITM |

**The one thing to remember**: an option is a *right*, not an *obligation*. The maximum loss is the premium — and that asymmetry is what makes options *insurance*, and what makes them *leverage*.

---

## What to read next

- Options as *insurance* → [Hedging the Wings — 1:2 Put Ratio Spread](hedging-wings.md)
- Options as *leverage* → [Cost of Leverage in Derivatives](derivatives-leverage-cost.md)
- The *asymmetry* of options markets (why puts cost more than calls) → [Volatility Skew](skew.md)
- Going *deep* on options → [Extension series (S3) — The Nature of Options + Practical Strategies](../series/s3-preview.md)
