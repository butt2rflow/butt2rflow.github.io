# Volatility Briefing Playbook

The morning briefing reads this file every day and passes it to the Claude commentary as its rules.
The monthly review (`scripts/review_briefs.py`) proposes changes to it as a PR, and they apply once a person merges the PR.

## Scope
- Read only volatility and insurance premiums: option premium, skew, put/call volume, dealer gamma, VIX curve, VVIX, bond vol (MOVE), credit spreads.
- No earnings, valuation, news or macro calls. No direction forecasts or trade advice.

## Three lenses
1. **Insurance and downside amplification:** hedging demand (SKEW and COR90D up, SPX put/call above its 20-day average) means the big players are already prepared. Treat it as a **signal to be careful, not a crash forecast**. The dealers who sold that insurance are short gamma on the downside. When GEX is short and SPX sits below the flip, their hedge selling can add to a decline that real selling starts. It amplifies the move; it doesn't drive it (see the GEX rule below).
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

## Reading rules from the blog's indicator posts (added 2026-10-26)
The home dashboard links each indicator to a post the owner wrote and checked. The commentary reads each indicator the way its post does and must not contradict it. Where a post and this playbook's backfill findings differ, follow the findings and name the post section in the monthly review as one to update. Fix the post itself, don't keep two readings. Each rule below was checked against the post text. When a post changes, update this section in the same commit. In the commentary, state the rule itself ("MOVE 80–120 is the normal band"); never cite the blog, a post or this playbook as the source.

- **GEX** (`gex-calculator`, `vanna-charm`): GEX is a *map* of the regime, not a signal. Gamma hedging is the ripple and real order flow (delta) is the wave: "감마의 진짜 역할은 파도를 만드는 게 아니라, 델타가 만든 파도를 키우거나 잠재우는 것". Cboe's own study puts dealer net gamma at 0.04–0.17% of daily S&P futures liquidity, so "dealer hedging dominates the market" is an overstatement. With short gamma below the flip, say dealer hedging **can add to** a decline that selling starts. Never say it causes or drives the decline. Nobody sees dealer inventory directly, so the sign of dealer positioning is estimated. The GEX is built from the prior close's OI.
- **SKEW, COR90D** (`volatility-dashboard`): judged by the 1-year percentile, caution >= 75%, stress >= 95% (as of 2026-10 those lines are about SKEW 149/156 and COR90D 38/48). Fixed levels don't last: the distribution moved from pre-2020 (SKEW ~115, COR90D ~66) to 2020– and again since 2024-10. SKEW paradox: SKEW can be higher in a recovery than right before a crash (puts are already held during the drop, new ones are bought after), so a low SKEW can mean the market is near a bottom. Only call structural stress when the COR term spread, COR90D and SKEW worsen together. A COR spike can be a short event effect (earnings, Fed), and correlation is not causation. Describe the **level** of SKEW and COR90D by its 1-year percentile (`skew_pct`, `cor90d_pct`), not by these fixed bands: the distribution keeps moving. Checked 2026-10-26 on the backfill: COR90D 2020– median 49 / p75 62 / p95 79 (matches the post), but 2024-10– median 38 / p75 42 / p95 51, so 39.6 is the recent median, not "below median". SKEW 2020– 140 / 147 / 160, 2024-10– 146 / 152 / 168. The dashboard's COR90D and SKEW states use the same 1-year percentile (caution >= 75%, danger >= 95%) since 2026-10-26; see Findings. The brief's 🟡 uses SKEW's 1-year percentile and 5-day changes (backfill-tested).
- **VIX futures curve** (`vix-term-structure`): M2−M1 > +1 is deep contango (calm), < 0 is backwardation (stress). There is no reliable single sign that stress is over; M2−M1 back above +1.0 is the suggested check. The curve's value is context, not a short-term trade signal. Don't use it alone.
- **MOVE** (`move-index`): bond-rate implied volatility in bp, a measure of size not direction. Rough levels: under 80 calm, 80–120 normal, 120–160 stress, over 160 a spasm; above 200 has happened only a handful of times. The signal is when MOVE and VIX disagree. Quote the level band next to the percentile, because a 96th percentile at 107 is still "normal" by the post's bands.
- **Credit**: see the next section (`credit-spreads`).
- **Kelly cash allocation** (`cash-allocation`): σ ≈ VIX/100 in f* = (μ−r)/σ², so higher vol means a lower equity weight. Risk signals multiply in extra discounts. The post says this is a buffer against losses compounding after a drop, not a forecasting tool.
- Not used by the commentary: COT and FedWatch (positioning and rate direction are outside this brief's scope), `gex-0dte-patterns` (intraday), `skew` (its SKEW level table is pre-2020 and now points to `volatility-dashboard`), and `implied-correlation` (its 30%/60% table is COR3M at the money, a different index from the brief's COR90D).

## Credit spreads (display only, added 2026-10-26)
- Read the **level** and the **gap between ratings** separately. HY OAS (level) can stay low while CCC widens away from B and BBB. Then the index hides that the bottom of the market is being repriced on its own.
- The brief shows HY as a number (no 🟢: low is not safe), CCC−B with its change this year (🟡 ≥ +30bp, 🔴 ≥ +100bp, the dashboard's `_credit_state`), and CCC−BBB (bottom of HY vs bottom of investment grade) with its change this year and 1-year percentile.
- When the CCC−B gap is 🟡/🔴 or CCC−BBB is at or above the 1-year 90th percentile, the commentary must not call credit "stable". It says the index is calm but the lowest ratings are widening on their own, and whether that agrees with the other stress signals.
- **Why** the gap widens (defaults, sectors, news) is out of scope. Say how unusual it is, not what caused it.
- A low HY level is **thin compensation, not safety** (blog post `credit-spreads`: HY near its historic low means implied default ≈ realized default, so almost no risk premium). Don't write "calm" or "stable" for a low HY number.
- Read it with VIX, as the post says: calm equity vol plus widening credit dispersion means the two markets disagree. Say that plainly; don't pick a side.
- These states are dashboard rules, not tested against SPX outcomes here. They are not used in the 🟢/🟡/🔴 call. Credit is not in the backfill: since 2026-04 FRED serves only the last 3 years of these ICE BofA series, so a test needs the live logs to accumulate.

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
- **VolVol (VVIX/VIX), tested against the blog's own definition (2022-08-28 and 2022-12-18 posts; 5MA, a 20-day 2σ Bollinger band drawn on the 5MA, 2007–2026; `scripts/study_volvol.py`):**
  - **The ratio is essentially VIX inverted.** Its correlation with VIX is −0.77, and in high-VIX regimes the correlation between its trend and VIX's trend is −0.78. Bear phases with a low ratio and bull phases with a high ratio, plus the ratio falling at a peak and bottoming at a trough, all show up exactly the same way in VIX. Around major turns (7 drawdowns ≥15%) the ratio gives no early warning before a peak and bottoms at the same time as the trough.
  - Golden/dead cross as a leverage switch (2x/1x): Sharpe 0.39 vs 0.34 for the same rule on VIX alone. The gap's CI [−0.05, +0.17] includes 0. The 200-day MA rule did better (0.45).
  - Golden/dead state vs realized vol over the next 20 days: 14.1 vs 18.5, about the same split as the VIX-only rule (14.7 vs 18.4).
  - (A-2) A dip below the lower band then back inside (73 events): 20-day return +0.65% [−0.56, +1.77], vs +0.80% on all days. No V-shape effect.
  - In high-VIX regimes, a rising ratio trend went with fewer drawdowns of 10% or more over the next 120 days (18% vs 38%). A falling VIX trend gives exactly the same split (18% vs 39%), and once VIX's trend is controlled for, the gap disappears (16% vs 24%, CIs overlap widely, about 15 episodes).
  - **First conclusion (direction, timing):** in level and direction, VolVol is a re-expression of VIX. The leverage switch, (A-2) and the event study showed no information beyond VIX.
  - **Revised (2026-10-18, sections 8–9): golden = "calmer than priced" — the user's claim holds.** Outcome is realized vol over the next 20 days ÷ VIX. Golden − dead gap, with VIX band and VIX-only rule state held fixed: **−8.9% [−15.1, −3.1]**. By era: ≤2019 −7.8% · 2020–24/08 −3.6% · holdout 2024/09– −16.6%. The same test on the VIX-only rule shows nothing (−3.6% [−9.6, +1.0], holdout +6.0%). So VolVol golden marks a phase where actual volatility comes in below what VIX priced, independent of the VIX level. (On "smart money is coming in": forward returns favoured golden only in the VIX 25–35 band (60-day +8.7% vs +4.0%); elsewhere the CIs overlap, so that part is not established.)
  - **Shoulder/knee use (10 declines ≥10% since 2007; switch must hold 5 sessions):**
    - VolVol: risk-off at SPX −2.5% from the peak (all 10 already on), risk-on at +6.9% above the trough (8 sessions after).
    - VIX rule: −2.8%, and +5.1% (6 sessions after).
    - 200-day MA: −8.3%, and +10.1% (36 sessions after).
    - Both vol detectors catch the shoulder about 6pp of SPX earlier and the knee about 30 sessions earlier than the 200-day MA. But false alarms are frequent: 71% of VolVol risk-off switches and 74% of VIX-rule switches were not followed by a ≥5% decline within 40 sessions. Read a dead switch as "shoulder candidate", not a confirmed decline.
  - **In the brief:**
    - Shows the VolVol state (golden/dead, days in state) with the meaning above, display only.
    - Also shows the "VIX option premium" (VVIX residual vs VIX), which has no predictive power and only compares hedge costs.
    - Both are tracked in the monthly review. VolVol is not used in the 🟢/🟡/🔴 call.
- Same VIX level with SKEW in the top 10% showed fewer drawdowns, but **only after 2020**: ≤2019 34% vs 40% at that VIX level, 2020– 18% vs 37% (37 episodes). Treat it as an observation, not a rule.
- **V-shape hypothesis (not significant):** in −3% drawdown episodes since 1991, heavy pre-drop hedging (n=21) vs light (n=28). The 20-day median return gap was +1.1pp, 95% CI [−1.9, +2.9]. The recovery-day gap was −8 days, 95% CI [−24, +25]. Both CIs include 0. In −5% episodes (n=12/17) the CIs are wider still. Deepening past −10% was the same (19% vs 18%), and the episode definition was not fixed in advance. "Prepared markets bounce faster" is a hypothesis to keep tracking, not a finding (`scripts/study_vshape.py`).

- **COR90D / SKEW dashboard thresholds (2026-10-26, `scripts/study_corskew.py`, 2010-09 → 2026-10, 2,879 sessions):** fixed COR90D 50/60 fired caution on 76% of days (0–100% by year; 5% in the last two years); the 1-year percentile rule (>= 75% caution, >= 95% danger) fires 0–47% by year (COR90D) and 0–65% (SKEW), 44–53 episodes. P(dd10 <= −2%) after caution+: fixed COR90D 28% [23–33], percentile 25% [17–33], all days 27% [23–31]; no rule differs from all days (Holm p >= 0.12) or within VIX bands, before and after 2020. Switched the dashboard to the percentile rule on firing stability, as with VVIX. **Neither rule was followed by more drawdowns**, so the COR/SKEW Kelly discount has no drawdown support; (the discount itself was later removed, see the allocation backtest below). SKEW at its 1-year top 5% saw fewer drops (16% [10–24], n.s.). T2 (COR90D > 55 AND SKEW > 150) fired 2.7% of days, 0% in the last two years; untested, unchanged.
- **Big drops (2026-10-27, `study_corskew.py --big`, 2007–2026):** 17 declines of 10%+ (zigzag peaks and troughs). The percentile COR/SKEW group was on for at least half of the 20 sessions before the peak in 12 of 17, but it is on 54% of all days, so that is about chance (n = 17). It missed 2008-05→10 (−37%), 2015-05, 2018-01, 2022-01 and 2022-08. The fixed rule "caught" almost all of them only because it was on nearly every day before 2022 (and missed 2018-01 and 2023). Forward 60-session max drawdown of −10% or worse: all days 14.9% [10.4–18.8], percentile caution+ 15.4% [10.9–20.9], danger 16.4% [9.8–24.4], group ok 14.4% [9.8–19.7]; SKEW 1-year top 5% 17.0% [8.5–26.3] but 24% ≤2019 vs 6% 2020– (not consistent). **No support for the discount on big drops either.**
- **All three Kelly discounts, as an allocation (2026-10-27, `study_discounts.py`, 2013-01 → 2026-10, 3,474 sessions, 3/4 Kelly, mu-r 5%, standard profile, cash at T-bill, SPX price only):** base VIX-Kelly CAGR 9.6%, Sharpe 0.68, maxDD −20.6%, avg equity 90%. With all three discounts (live): CAGR 7.9%, Sharpe 0.67, maxDD −15.2%, avg equity 73%. A constant cut to the same average equity (×0.81) gives CAGR 8.2%, Sharpe 0.68, maxDD −16.7%; discount minus constant ΔSharpe CI −0.12…+0.09, ΔCAGR −1.4%…+0.8%. Same for each group alone (COR/SKEW vs ×0.93, VolVol vs ×0.89). **The discounts add no timing; they act like holding less equity**, which a lower Kelly fraction does more simply. Within VIX bands only VolVol shows a consistent direction (10-session −2% drawdowns 22/35/38/45% when on vs 16/24/32/41% when off across VIX 0–35), untested for significance; COR/SKEW and VIX TS show none. VIX level itself sorts drawdowns (19% → 45% from VIX < 16 to 25–35). **Decision 2026-10-27 (Jae):** COR/SKEW and VIX TS discounts removed; both groups are shown as state only (`DISCOUNT_GROUPS = ("volvol",)` in update_dashboard.py, `data-discount-groups` in kelly-toggle.js). VolVol keeps its discount until it gets its own test.

## Open questions (to verify)
- **VolVol discount:** the only group with a consistent within-VIX-band tilt (more 10-session −2% drops when on). Test it properly (block-bootstrap CI on the within-band gap, episodes, pre/post 2020, holdout) and against a constant cut; drop the discount too if it doesn't hold. `study_discounts.py` has the pieces.
- **VolVol speed hypothesis (in-sample, needs holdout validation):** VolVol does not react faster than VIX.
  - Delever crosses: VolVol first 40% / VIX first 44%. Lever crosses: VIX first 64%, with VolVol a median 2 sessions later. The daily-change cross-correlation is lag ±1 ≈ 0.
  - On days VIX moves, though, how far VVIX moves with it relates to the next 1–5 days of VIX, given today's VIX move. The 3-day coefficient is +0.21 [+0.12, +0.33]. If VVIX moves with VIX, the move tends to persist; if only VIX jumps, it tends to revert faster.
  - VVIX moving alone on calm VIX days predicts nothing (corr +0.02).
  - To test it as a "VIX spike persistence" read, check it on live records and the holdout. See `study_volvol.py` section 6.
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
