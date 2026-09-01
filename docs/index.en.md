---
title: Home
---

# butterflow Investment Notes

**Notes for the retail investor who treats volatility as fuel, not as enemy.**

Math- and data-driven investment principles. In an age where AI dominates markets in milliseconds, some things don't change — the math of compounding, the structure of volatility, and time as a weapon.

<!-- DASHBOARD_START -->
<div class="live-dash" markdown>

## 📊 Daily Dashboard

<small>**As of 2026-05-11** · Auto-updates daily after the US close · [Framework details →](posts/cash-allocation.md)</small>

<div class="allocation-master" data-deploy-pct="0" data-main-frac="0.9" data-tactical-frac="0.1">
  <div class="allocation-master__head">
    📊 <strong>Today's mix</strong> — Equity <strong><span data-total-equity>90</span>%</strong> / Cash <strong><span data-total-cash>10</span>%</strong>
  </div>
  <div class="allocation-master__split">
    <span class="allocation-master__split-label">Split:</span>
    <button class="kelly-pill" data-split-set="80-20">80 / 20</button>
    <button class="kelly-pill is-active" data-split-set="90-10">90 / 10</button>
    <button class="kelly-pill" data-split-set="95-5">95 / 5</button>
    <a class="allocation-master__split-info" href="posts/cash-allocation/#choosing-the-split" title="Which split should I pick?">ⓘ</a>
  </div>
  <div class="allocation-master__bar" aria-hidden="true">
    <div class="allocation-master__equity" data-master-equity-fill style="width: 90%"></div>
  </div>
  <div class="allocation-master__formula">
    <span>Main <span data-main-pct>90</span>% × <span data-kelly-equity-mini>100</span>% equity</span>
    <span class="allocation-master__plus">+</span>
    <span>Tactical <span data-tactical-pct>10</span>% × <span data-deploy-mini>0</span>% deploy</span>
    <span class="allocation-master__plus">=</span>
    <strong><span data-total-equity-mini>90</span>% equity</strong>
  </div>
</div>

### 💰 Main Bucket — Suggested Equity / Cash Mix

<div class="kelly-card"
     data-vix="18.4"
     data-base-quarter="37"
     data-base-half="74"
     data-base-threequarter="100"
     data-base-full="100"
     data-state-corskew="ok"
     data-state-vixts="ok"
     data-state-volvol="ok">
  <div class="kelly-controls">
    <span class="kelly-label">Kelly:</span>
    <button class="kelly-pill" data-kelly-set="quarter">¼</button>
    <button class="kelly-pill" data-kelly-set="half">½</button>
    <button class="kelly-pill is-active" data-kelly-set="threequarter">¾</button>
    <button class="kelly-pill" data-kelly-set="full">Full</button>
    <span class="kelly-divider">·</span>
    <span class="kelly-label">Risk sensitivity:</span>
    <button class="kelly-pill" data-discount-set="loose">Loose</button>
    <button class="kelly-pill is-active" data-discount-set="standard">Standard</button>
    <button class="kelly-pill" data-discount-set="tight">Tight</button>
  </div>
  <div class="kelly-controls">
    <span class="kelly-label">Equity premium μ−r:</span>
    <button class="kelly-pill" data-premium-set="conservative">5%</button>
    <button class="kelly-pill is-active" data-premium-set="standard">7%</button>
    <button class="kelly-pill" data-premium-set="aggressive">9%</button>
    <span class="kelly-help" title="μ−r is the equity-risk premium: 5% (conservative, accounts for VIX vol-risk premium drag), 7% (historical SPX average), 9% (post-1990 / bullish). Because VIX runs 3-5 pts above realized vol, 7-9% is roughly equivalent to Kelly applied to realized rather than implied vol.">ⓘ</span>
  </div>
  <table class="kelly-table">
    <thead><tr><th>Step</th><th>Value</th></tr></thead>
    <tbody>
      <tr><td>① Kelly × VIX base (VIX 18.4)</td><td><strong><span data-kelly-base>100</span>%</strong></td></tr>
      <tr><td>② COR/SKEW 🟢 Normal</td><td>× <span data-kelly-d="corskew">1.00</span></td></tr>
      <tr><td>③ VIX TS 🟢 Contango (normal)</td><td>× <span data-kelly-d="vixts">1.00</span></td></tr>
      <tr><td>④ VolVol 🟢 Calm</td><td>× <span data-kelly-d="volvol">1.00</span></td></tr>
      <tr class="kelly-final"><td><strong>Suggested mix</strong></td><td><strong>Equity <span data-kelly-equity>100</span>% / Cash <span data-kelly-cash>0</span>%</strong></td></tr>
    </tbody>
  </table>
</div>

<img class="kelly-curve-img" src="../assets/diagrams_en/kelly_curve_standard.png" alt="Kelly × VIX curve" data-kelly-curve-prefix="../assets/diagrams_en/kelly_curve_">

<small>*This mix is **internal to the main bucket** — the tactical bucket is sized in the next card, and the whole-portfolio composite plus the split (80/20·90/10·95/5) live in the master bar at the top. Formula: f* = (μ−r) ÷ (VIX/100)², capped at 100%. Kelly fraction (¼·½·¾·Full) × premium (5·7·9%) × risk sensitivity (loose 0.95/0.85 · standard 0.90/0.75 · tight 0.85/0.65) compose the final weight. Both the curve chart and the card numbers update with the selected μ−r. **Educational — not investment advice.** [Read more →](posts/cash-allocation.md)*</small>

---

### ⚡ Tactical Bucket — Offensive Deploy Signal

<div class="tactical-card" markdown>
<div class="dash-tight" markdown>

| Trigger | Now | Tier / Fired |
|:---|---:|:---:|
| VIX sustained 5d — 40+ ×½ / 50+ ×1 / 60+ ×1½ | 18.4 (5d min 17.1) | 🟢 Inactive (0) |
| COR90D > 55 AND SKEW > 150 | 33.0 / 140.2 | ❌ (0) |
| 30-day SPX drawdown ≥ 20% | +0.0% | ❌ (0) |
| **Tactical bucket deploy** | **🟢 0% (Inactive)** | — |

</div>
</div>

<small>*Tactical bucket holds *offensive cash to monetise the time edge*. T1 (VIX sustained) is laddered 40/50/60 with weights ½/1/1½; T2 and T3 are binary 0/1. Total weight ÷ 3 → deploy %, capped at 100. Deploy % shown above is **internal to the tactical bucket** — see the master bar at the top for the whole-portfolio composite and the split selector · [Read more →](posts/cash-allocation.md)*</small>

---

### VIX Futures Term Structure

<div class="dash-tight" markdown>

| Field | Value | State |
|:------|------:|:------|
| VIX spot | 18.38 | — |
| Front (M1, 2026-05-19) | 19.47 | — |
| **M2 − M1** (short-term) | +1.52 | 🟢 Contango (normal) |
| **M7 − M4** (mid-term, VXZ zone) | +0.75 | 🟢 Contango (normal) |

</div>

<div id="vix-history-player"></div>

<small>*Source: Cboe CFE settlement — a reliable alternative to vixcentral · Use the slider/▶ to scrub through up to 1 year of past curves · [Reading guide →](posts/vix-term-structure.md)*</small>

---

### COR + SKEW Dashboard

<div class="dash-tight" markdown>

| Signal | Value | State |
|:-------|------:|:------|
| **Term Structure** (COR1Y − COR1M) | 5.3 | 🟢 Normal |
| **COR90D** (synchronization) | 33.0 | 🟢 Normal |
| **SKEW** (tail risk) | 140.2 | 🟢 Normal |

</div>

![Volatility dashboard (paired with S&P 500)](assets/diagrams_en/vol_dashboard.png)

<small>*Cboe COR + SKEW indices — market diversification and tail-risk view · [Full guide →](posts/volatility-dashboard.md)*</small>

---

### VolVol — VVIX / VIX ratio

<div class="dash-tight" markdown>

| Signal | Value | State |
|:-------|------:|:------|
| **VolVol = VVIX / VIX** (5DMA) | 5.463 | 🟢 Calm (5DMA > middle) |
| BB middle (20-day MA) | 5.330 | — |

</div>

![VolVol history](assets/diagrams_en/volvol.png)

<small>*5-day MA above the 20-day BB middle = vol is decompressing (calm regime); below = vol is building (stressed). A cross through the middle band marks a sentiment shift. **Not an official index — a 'psychological' confirmation signal**, best read alongside VIX TS and COR/SKEW rather than as a standalone trading trigger · [Read more →](posts/cash-allocation.md)*</small>

</div>

---
<!-- DASHBOARD_END -->

## Free articles

### Returns 101

- [**Returns, Compounding, and Log Charts**](posts/log-return.md) — Why arithmetic and log returns are different and why log charts exist
- [**How is my portfolio actually doing?**](posts/portfolio-return.md) — TWR vs MWR, same trade two answers
- [**Expected Return — QQQ vs TQQQ**](posts/expected-return.md) — A probability view of leverage and vol drag
- [**Cost of Leverage in Derivatives**](posts/derivatives-leverage-cost.md) — Same 3×, wildly different bills
- [**Quadruple Witching Is Whole Again**](posts/ssf-relaunch.md) — Single stock futures are back after 6 years, and why they fit a directional earnings bet

### Options analysis

- [**Options Basics**](posts/options-basics.md) — Calls, puts, strike, expiration, delta — explained via car insurance (start *here* if options are new)
- [**Volatility Skew**](posts/skew.md) — The "smirk" in S&P 500 index options, Implied Correlation, the CBOE SKEW Index
- [**The Bond Market's VIX — MOVE Index**](posts/move-index.md) — the fear gauge for Treasury yields; in bp not %, and the divergence from VIX is the signal
- [**Hedging the Wings**](posts/hedging-wings.md) — Low-cost tail-risk hedging (1:2 put ratio, with a concrete SPY example)
- [**Market-Sentiment Volatility Indices**](posts/implied-correlation.md) — COR3M, the IV Surface, Delta Skew + a TradingView Pine Script

### Market data tools

- [**The COT Report**](posts/cot.md) — Reading institutional intent in the futures market
- [**The FedWatch Tool**](posts/fedwatch.md) — Pricing rate moves with Fed Funds futures
- [**Reading Credit Spreads as an Indicator**](posts/credit-spreads.md) — The index is calm while the CCC−B gap widens; a late-cycle signal you can read on FRED without trading CDS

### Tools

- [**Monte Carlo Simulation**](posts/monte-carlo.md) — Backtesting investments with Google Sheets + Python
- [**The Almanac Trader**](posts/almanac.md) — Monthly seasonality analysis (Google Sheets + Python)
- [**Calculating GEX Yourself**](posts/gex-calculator.md) — Gamma exposure with Google Sheets + Python
- [**0DTE Gamma Patterns**](posts/gex-0dte-patterns.md) — How GEX shifts intraday
- [**Volatility Dashboard**](posts/volatility-dashboard.md) — Tracking Correlation + Skew (Google Sheets + Python)
- [**VIX Futures Term Structure**](posts/vix-term-structure.md) — Reading contango/backwardation (vixcentral alternative)

---

## Series (paid e-books)

**How to use volatility as fuel — a complete curriculum for the retail investor, written with math and data.**

- **13 articles / 167 pages**, with **90+ original diagrams**
- Formulas at arithmetic level only, the rest is analogies and pictures
- Each Gumroad listing includes **both English and Korean PDFs**

| Series | What's inside | Articles | Gumroad |
|:-------|:--------------|:---------|:--------|
| [**Principles (61p)**](series/s1-shannons-demon.md) | Shannon's Demon to Kelly's Criterion | 4 (part 1 free) | [Buy](https://butt2rflow.gumroad.com/l/aejfrj) |
| [**Execution (35p)**](series/s2-preview.md) | Read VIX, size positions with ETFs + cash | 3 | [Buy](https://butt2rflow.gumroad.com/l/ozijat) |
| [**Extension (32p)**](series/s3-preview.md) | LEAP, Protective Put, Covered Call | 2 | [Buy](https://butt2rflow.gumroad.com/l/ozuyjb) |
| [**Depth (39p)**](series/s4-preview.md) | Gamma, dynamic hedging, GEX, 0DTE | 4 | [Buy](https://butt2rflow.gumroad.com/l/cwwzss) |
| **Complete bundle (167p)** | Principles + Execution + Extension + Depth | 13 | [**Buy**](https://butt2rflow.gumroad.com/l/dbkyt) |

<small>The bundle collects all four series in one.</small>

---

*All content is for educational purposes only. This is not investment advice or a recommendation to buy or sell any specific security. All investments carry the risk of capital loss.*
