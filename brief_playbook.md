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

## Findings to date (backfill 2010-09 → 2026-10, n≈4,000; 10-session max-drawdown basis)
| State | n | P(≤−2%) | P(≤−5%) | 20-session return median |
|---|---|---|---|---|
| 🔴 Stress | 1,314 | 40% | 12% | +2.3% |
| 🟡 Hedging | 807 | 21% | 4% | +1.3% |
| 🟢 Calm | 1,907 | 23% | 4% | +1.3% |

- 🟡 hedging was **not followed by worse outcomes** than 🟢. It is a positioning read (big players prepared), not a predictor.
- 🔴 stress had higher drawdown risk but also a higher 20-session median return, so stress often mean-reverts. Don't read 🔴 as "keep falling".
- **V-shape hypothesis** (pre-drop hedge level vs −3% drawdowns, 1991–): with heavy hedging, the 20 days after hitting −3% returned a median +3.0% vs +1.7% with light hedging, and median recovery took 23 days vs 34. The odds of the drawdown deepening past −10% were the same (19% vs 18%). The big declines (2018 Q4, 2020, 2025 Mar–Apr) all started with heavy hedging in place. Prepared markets **bounce faster; they don't fall less**. Small sample (n=21/28).
- Same VIX level (~20) with SKEW in the top 10%: 10-day −2% odds 28% vs 38% across all days at that VIX level. Hedging was followed by fewer drawdowns, not more.

## Open questions (to verify)
- The VVIX ≥ 105 threshold fires too often. Consider a VVIX 1-year percentile or a 5-day change instead.
- Is GEX recomputed at 07:30 ET any different from the overnight snapshot? Compare `gex.net_bn` and `gex.published_net_bn` in `brief_log`.
- Does Yahoo's ^VIX carry Cboe extended-hours (GTH) values before the open?
- Can put/call and VRP thresholds earn a place in the state call? (Needs history; for now, live logs only.)

## Change rules (followed by the monthly review)
- Only change a threshold or a state rule when the group in question has **n ≥ 30** and the difference from the comparison group is clear (e.g. 5pp or more on P(≤−2%)).
- Short of that, record it under "Open questions" or "Findings to date" only.
- Don't widen the scope beyond volatility and insurance premiums.
- Record every change in the review report along with its evidence (table and n).
