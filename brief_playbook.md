# Volatility Briefing Playbook

The morning briefing reads this file every day and passes it to the Claude commentary as its rules.
The monthly review (`scripts/review_briefs.py`) proposes changes to it as a PR, and they apply once a person merges the PR.

## Scope
- Read only volatility and insurance premiums: option premium, skew, put/call volume, dealer gamma, VIX curve, VVIX, bond vol (MOVE), credit spreads.
- No earnings, valuation, news or macro calls. No direction forecasts or trade advice.

## Three lenses
1. **Insurance and downside amplification:** hedging demand (SKEW and COR90D up, SPX put/call above its 20-day average) means the big players are already prepared. Treat it as a **signal to be careful, not a crash forecast**. The dealers who sold that insurance are short gamma on the downside. When GEX is short and SPX sits below the flip, a decline gets amplified by their hedge selling.
2. **Event context:** SKEW alone doesn't say who bought insurance or why. Near FOMC, earnings season or an expiry, event hedges may be mixed in, and those unwind once the event passes. VIX9D/VIX > 1 means hedges are crowded into the next few days.
3. **Historical base rate:** compare against days at the same VIX level and don't overstate the signal.

## Signals and current thresholds
| Signal | Definition | Threshold | Status |
|---|---|---|---|
| Hedging (🟡) | SKEW 5-day change | ≥ +8 | keep |
| Hedging (🟡) | SKEW 1-year percentile | ≥ 90% | keep |
| Hedging (🟡) | COR90D 5-day change | ≥ +4 | keep |
| Stress (🔴) | VX curve M2−M1 | < 0 (backwardation) | keep |
| Stress (🔴) | VIX/VIX3M | ≥ 0.95 | keep |
| Stress (🔴) | VVIX | ≥ 105 | **under review** (fires on 24% of days, see below) |
| Display only | SPX/Equity put/call, VRP, VIX9D/VIX | not used in the state call | collecting data |

## Findings to date (backfill 2010-09 → 2026-09, 10-session max-drawdown basis)
Daily rows overlap (10/20-session windows), so judge by **episodes** (runs more than 10 sessions apart) and the **block-bootstrap 95% CI**, not by n.

| State | days | episodes | P(≤−2%) [95% CI] | ≤2019 / 2020– | P(≤−5%) | 20-session return median |
|---|---|---|---|---|---|---|
| 🔴 Stress | 1,314 | 66 | 40% [34–45] | 38% / 41% | 12% | +2.3% |
| 🟡 Hedging | 806 | 97 | 21% [16–26] | 18% / 26% | 4% | +1.3% |
| 🟢 Calm | 1,898 | 46 | 23% [20–27] | 22% / 27% | 4% | +1.3% |

- 🟡 hedging was **not followed by worse outcomes** than 🟢 (CIs overlap). It was not followed by fewer drawdowns either. It is a positioning read (big players prepared), not a predictor in either direction.
- **🔴 is largely a VIX-level proxy.** Within VIX bands the gap shrinks: VIX 16–20, 🔴 38% vs 🟢 29%; VIX 20–25, 37% vs 28%; VIX 25–35, 47% vs 45%. Read 🔴 as "stress at this VIX level", not as an independent signal. Its higher 20-session median return is also partly a high-VIX effect, so don't read 🔴 as "keep falling".
- VVIX ≥ 105 decides 🔴 on its own on about 42% of 🔴 days, and its firing rate depends on the regime: it fired on 79% of days in 2020 and 90% in 2021, but only 2–5% in 2013, 2017, 2019 and 2023. VIX/VIX3M ≥ 0.95 is the more stable stress rule.
- Same VIX level with SKEW in the top 10% showed fewer drawdowns, but **only after 2020** (about 35 episodes; no difference before 2020). Treat it as an observation, not a rule.
- **V-shape hypothesis (not significant):** in −3% drawdown episodes since 1991, heavy pre-drop hedging (n=21) vs light (n=28) showed a median 20-day return of +3.0% vs +1.7% and median recovery of 23 vs 34 days. Deepening past −10% was the same (19% vs 18%). The gaps sit inside sampling noise, recovery times are censored, and the episode definition was not fixed in advance. Read it as a hypothesis worth tracking that prepared markets bounce faster rather than fall less. It is not a finding.

## Open questions (to verify)
- **Proposed (needs Jae's OK, a code change):** replace VVIX ≥ 105 with a VVIX 1-year percentile ≥ 90% (or require 2 of the 3 stress conditions). Adopt only if it holds before and after 2020 and on a holdout (the last 2 years).
- Is GEX recomputed at 07:30 ET any different from the overnight snapshot? Compare `gex.net_bn` and `gex.published_net_bn` in `brief_log`. (On 10-16, a weekend, the two were identical, as expected.)
- Does Yahoo's ^VIX carry Cboe extended-hours (GTH) values before the open?
- Can put/call and VRP thresholds earn a place in the state call? (Needs history; for now, live logs only.)
- `FOMC_DATES` in `update_dashboard.py` ends in 2027-06. Extend it before then.

## Change rules (followed by the monthly review)
- Thresholds and state rules are **code constants**. The review can only propose a change in its report, and a person makes it in code together with the table above. The review script reverts any edit to the threshold table.
- A proposal needs **≥ 30 episodes** in the group, a **95% CI that doesn't overlap** the comparison group (same VIX band or all days), and the same direction **before and after 2020**. Before adopting it, check it on a holdout (the last 2 years).
- About 9 signals are compared every month (multiple comparisons). Don't promote a one-off gap to a finding. Base decisions on the full-period table only; the last-12-months table is descriptive.
- Short of that, record it under "Open questions" or "Findings to date" only, and word findings no stronger than the evidence.
- Don't widen the scope beyond volatility and insurance premiums.
- Record every change in the review report along with its evidence (episodes, CI, pre/post 2020).
