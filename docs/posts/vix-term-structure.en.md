---
title: "VIX Futures Term Structure — Reading Contango and Backwardation"
date: 2026-05-09
tags: [VIX, futures, term-structure, contango, backwardation, volatility, vixcentral]
lang: en
---

# VIX Futures Term Structure — Reading Contango and Backwardation

> Auto-updates daily after the US close · Source: Cboe CFE settlement data · [Live chart on home page](../index.md)

---

## Today's VIX futures curve

<!-- VIX_TS_LIVE_START -->
![VIX Futures Term Structure](../assets/diagrams_en/vix_term_structure.png)
<!-- VIX_TS_LIVE_END -->

The chart above auto-updates every business day. It uses **official settlement prices** from the Cboe Futures Exchange (CFE), published once per day after the US market close. No subscription or login required — this is public data anyone can pull.

---

## VIX spot vs VIX futures

| | VIX spot (^VIX) | VIX futures (VX/K6, VX/M6, …) |
|:--|:----------------|:-------------------------------|
| What it is | **30-day expected volatility** as of right now | **Forward volatility** for a specific expiration |
| Used for | Sentiment indicator | Hedging and trading directly |
| Tradable? | ❌ (index only) | ✅ (contract trades on CFE) |
| Expirations | None (it's a calculation) | Monthly (Wednesday-anchored) |

**The point**: VIX spot is the expected volatility *at one point in time*. VIX futures price *future expected volatility* — different prices at different expirations. Connect those prices and you get a **term structure** curve.

---

## Contango vs Backwardation — what the curve says

### Contango — the normal state

```
Price
 │
 │              ●  Far month (high)
 │           ●
 │       ●
 │   ●
 │●  Spot / Front (low)
 └──────────────── Maturity
```

**Near < Far** — the market's default state.

Reading: "Things are calm right now, but volatility could be higher later."

VIX futures sit in **contango more than 50% of the time**. That's because volatility is mean-reverting — when current vol is low, the market prices in "this calm won't last forever."

What contango means in practice:

- **Friendly to vol-sellers (XIV, SVXY, short-VIXY)**: contracts decay toward spot as expiration approaches → naturally profitable for short positions (the "roll yield")
- **An environment where volatility itself is harvestable**: strategies that sell vol and collect premium *work* in contango
- **2009–2018 — nine years almost entirely in contango**: SVXY-style ETFs returned over +10,000%

### Backwardation — the stress state

```
Price
 │
 │●  Spot / Front (high)
 │   ●
 │       ●
 │           ●
 │              ●  Far month (low)
 └──────────────── Maturity
```

**Near > Far** — the crisis signal.

Reading: "Volatility is extreme right now, and we expect it to settle down later."

Backwardation occurs **less than 20% of the time**. When it does, the market is in panic:

- **October 2008**: Global Financial Crisis. Front-month VIX futures near 80, backwardation of +13 pts (the largest on record)
- **February 5, 2018**: "Volmageddon" — VIX +115% in a day, [SVXY −90%](skew.md), brief backwardation
- **March 2020**: COVID panic, VIX hit 82
- **January–February 2022**: brief backwardation right before the Ukraine invasion
- **April 2025**: just after the Trump tariff announcement

What backwardation means in practice:

- **Vol-selling strategies get crushed instantly** — exactly the mechanism that took SVXY −90% in 2018
- **Buying volatility makes sense** — VXX, UVXY become viable for short windows
- **Portfolio hedges are working** — strategies like [Hedging the Wings](hedging-wings.md) shine in this environment

---

## Reading the curve fast — four signals

| Signal | Reading | Color |
|:-------|:--------|:------|
| **VIX spot < Front month** | Most common state (contango setup) | 🟢 Normal |
| **VIX spot > Front month** | **Backwardation** — short-term stress | 🔴 Warning |
| **M2 − M1 > +1** | Deep contango (strong calm) | 🟢 Calm |
| **M2 − M1 < 0** | Backwardation (stress) | 🔴 Risk |
| **Curve nearly flat** | Even volatility expectation (transition) | 🟡 Caution |

---

## Why this page instead of vixcentral

[vixcentral.com](https://vixcentral.com) was the de-facto standard for viewing the VIX futures term structure for years, but data feeds have become unreliable lately and the ad load has gone up. This page:

- **Uses Cboe's official settlement data directly** — no middleman, always accurate
- **Hosted on GitHub Pages** — no ads, no tracking
- **Reproducible code** — the script is public; you can run it yourself
- **Free, and free forever**

Data source: `https://www.cboe.com/us/futures/market_statistics/settlement/csv/`

Cboe publishes settlement prices each business day after the close (typically 16:30 ET). This page's chart refreshes shortly after, at 22:00 UTC (≈ 17:00 ET), via a GitHub Actions cron job.

---

## How to use it

### 1. Timing — sell vs buy volatility

| Situation | Suggestion |
|:----------|:-----------|
| Contango, M2−M1 > +1.5 | Vol-selling environment (caveat: vol-selling always carries the risk of an abrupt regime flip — this article is about *reading* the regime, not endorsing the trade) |
| Contango → curve flattening | Reduce vol-short, consider adding hedges |
| Backwardation appears | Stop-loss any vol-short. Time to activate protective trades like [Hedging the Wings](hedging-wings.md) |

### 2. Combine with other signals

Don't trade off VIX term structure alone. Pair it with the other signals from the [Volatility Dashboard](volatility-dashboard.md):

- **COR term-structure inversion (COR1M > COR1Y)**: short-term fear surging — usually fires near-simultaneously with VIX TS backwardation
- **COR90D > 50**: synchronization broadening — diversification breaking down
- **SKEW > 150**: institutional tail-risk pricing rising

All three deteriorating + VIX backwardation = **unmistakable crisis signal**.

### 3. Historical recovery times

| Event | Backwardation duration |
|:------|:-----------------------|
| 2008 GFC | ~3 months |
| 2011 US credit downgrade | ~2 weeks |
| 2015 Yuan devaluation | ~1 week |
| 2018 Volmageddon | 4 days |
| 2020 COVID | ~6 weeks |
| 2025 Trump tariff | ~2 weeks |

Most events return to contango **within days to a few weeks**. That recovery point is a candidate for re-entering vol-short strategies, though there's no single reliable indicator that says "we're back" — using **M2−M1 returning to +1.0 or above** is a workable rule of thumb.

---

## Wrap-up

The VIX futures term structure is **a cross-section of market volatility psychology**. One picture per day tells you:

- How panicked the market is *right now*
- The market's bet on *future* volatility
- Whether vol-selling strategies are in a working environment
- When to strengthen hedges

For a long-term investor, the value here isn't a short-term trade signal — it's **context**. A tool to judge whether a sudden vol spike is *structural or transient*.

---

*Related: [Volatility Dashboard — Tracking Correlation + Skew](volatility-dashboard.md) | [Hedging the Wings — Cheap Tail-Risk Insurance](hedging-wings.md) | [Volatility Skew](skew.md)*
