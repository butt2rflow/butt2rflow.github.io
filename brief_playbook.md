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
| Stress (🔴) | VVIX 1-year percentile | ≥ 90% | changed 2026-10-18 (was VVIX ≥ 105; see Findings) |
| Display only | SPX/Equity put/call, VRP, VIX9D/VIX | not used in the state call | collecting data |

## Findings to date (backfill 2010-09 → 2026-09, 10-session max-drawdown basis)
Daily rows overlap (10/20-session windows), so judge by **episodes** (runs more than 10 sessions apart) and the **block-bootstrap 95% CI**, not by n.

| State | days | episodes | P(≤−2%) [95% CI] | ≤2019 / 2020– | P(≤−5%) | 20-session return median |
|---|---|---|---|---|---|---|
| 🔴 Stress | 886 | 85 | 40% [33–46] | 37% / 43% | 13% | +2.8% |
| 🟡 Hedging | 1,005 | 104 | 22% [17–27] | 19% / 27% | 4% | +1.4% |
| 🟢 Calm | 2,127 | 43 | 26% [22–30] | 22% / 32% | 5% | +1.2% |

(Current rules, with VVIX as a 1-year percentile. All days: 28% [25–32].)

- 🟡 hedging was **not followed by worse outcomes** than 🟢 (CIs overlap). It was not followed by fewer drawdowns either. It is a positioning read (big players prepared), not a predictor in either direction. None of the hedging signals differs from all days after Holm correction (SKEW 5-day p=0.64, SKEW 1-year p=0.12, COR90D p=0.71).
- **🔴 is largely a VIX-level proxy.** Within VIX bands (🔴 vs the band's all days): VIX 16–20, 35% vs 31%; VIX 20–25, 37% vs 34%; VIX 25–35, 49% vs 47%. Read 🔴 as "stress at this VIX level", not as an independent signal. Its higher 20-session median return is also partly a high-VIX effect, so don't read 🔴 as "keep falling". The stress signals that clear Holm (VIX/VIX3M, VIX9D/VIX, p<0.005) are compared against all days, so they also carry the VIX-level effect.
- **VVIX rule change (2026-10-18):** the fixed VVIX ≥ 105 fired on 79–90% of days in 2020–21 and 2–5% in 2013, 2017, 2019 and 2023 (regime-dependent). Switching to a 1-year percentile ≥ 90% left 🔴's drawdown rate unchanged (40% vs 40%) and brought yearly firing from 1–90% down to 1–43%. It was consistent before and after 2020 and on the holdout (2024-09–: 39%). Neither VVIX rule adds anything over the same VIX band (+0–3pp), so read VVIX as a gauge of how fast fear is rising, not as an independent predictor.
- Same VIX level with SKEW in the top 10% showed fewer drawdowns, but **only after 2020**: ≤2019 34% vs 40% at that VIX level, 2020– 18% vs 37% (37 episodes). Treat it as an observation, not a rule.
- **V-shape hypothesis (not significant):** in −3% drawdown episodes since 1991, heavy pre-drop hedging (n=21) vs light (n=28). The 20-day median return gap was +1.1pp, 95% CI [−1.9, +2.9]. The recovery-day gap was −8 days, 95% CI [−24, +25]. Both CIs include 0. In −5% episodes (n=12/17) the CIs are wider still. Deepening past −10% was the same (19% vs 18%), and the episode definition was not fixed in advance. "Prepared markets bounce faster" is a hypothesis to keep tracking, not a finding (`scripts/study_vshape.py`).

## Open questions (to verify)
- VIX9D/VIX > 1 clears Holm against all days (39%, p<0.005). Check whether it adds information on non-🔴 days and within VIX bands before considering it for the state call.
- Is GEX recomputed at 07:30 ET any different from the overnight snapshot? Compare `gex.net_bn` and `gex.published_net_bn` in `brief_log`. (On 10-16, a weekend, the two were identical, as expected.)
- Does Yahoo's ^VIX carry Cboe extended-hours (GTH) values before the open?
- Can put/call and VRP thresholds earn a place in the state call? (Needs history; for now, live logs only.)
- `FOMC_DATES` in `update_dashboard.py` ends in 2027-06. Extend it before then.

## Change rules (followed by the monthly review)
- Thresholds and state rules are **code constants**. The review can only propose a change in its report, and a person makes it in code together with the table above. The review script reverts any edit to the threshold table.
- A proposal needs **≥ 30 episodes** in the group, a **95% CI that doesn't overlap** the comparison group (same VIX band or all days), and the same direction **before and after 2020**, and for signal-vs-all-days comparisons a Holm-adjusted p < 0.05 (column "vs 전체 p(Holm)"). Before adopting it, check it on a holdout (the last 2 years).
- About 9 signals are compared every month (multiple comparisons). Don't promote a one-off gap to a finding. Base decisions on the full-period table only; the last-12-months table is descriptive.
- Short of that, record it under "Open questions" or "Findings to date" only, and word findings no stronger than the evidence.
- Don't widen the scope beyond volatility and insurance premiums.
- Record every change in the review report along with its evidence (episodes, CI, pre/post 2020).
