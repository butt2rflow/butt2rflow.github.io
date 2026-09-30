---
title: "Investing in Physical AI (3) — The Humanoid Power Problem: Batteries, Uptime, and Why Reactors Aren't the Answer"
nav_title: "Part 3 · The humanoid power problem"
date: 2026-09-28
tags: [physical-ai, investing, humanoid, battery, energy, nuclear, smr]
lang: en
description: "A robot arm is on a power cable, but a humanoid has to carry its energy. How long one charge lasts, why a bigger battery gives some of its gain back to weight, how the industry moved from capacity to uptime, the cell supply chain, and why a 'portable reactor' can't power a robot, so the nuclear theme has to be judged separately."
---

# Investing in Physical AI (3) — The Humanoid Power Problem: Batteries, Uptime, and Why Reactors Aren't the Answer

> **Investing in Physical AI · Part 3.** [Part 1](cobot-investing.md) said "the value is moving," and [Part 2](physical-ai-investing-actuators.md) said "joint design decides the direction." This part looks at the energy that moves the joints: **power**. It's information, not investment advice.

A robot arm in a factory can run all day without a thought about power. It's bolted to the floor with a cable plugged in. A humanoid is different.

![The difference is one cable](../assets/diagrams_en/inv3-tether.svg)

So humanoid investing comes with the question "how long does the battery last?", and sometimes with a hope: "won't they carry something like a small reactor one day?" The first has a numeric answer; the second, a one-picture one.

---

## The 30-second version

- Today's humanoids work **1.5–5 hours** on one charge. None covers an 8-hour shift on one battery.
- A bigger battery adds weight, and the joints then draw more power, so capacity alone hits a limit. The industry is moving to **uptime** (hours worked per day), keeping robots running with battery swaps and short charges.
- In cells, **LG Energy Solution** moved first, with reported supply to several humanoid makers; Samsung SDI and SK On are following. Even Korean cells, though, contain **materials processed mostly in China**.
- **Small reactors and nuclear batteries are not robot power.** The first is far too big, the second far too small. Nuclear is a separate theme about power for AI data centers and factories.

---

## How long one charge lasts

![No one covers an 8-hour shift on one battery](../assets/diagrams_en/inv3-runtime.svg)

Most of these numbers come from company statements or reports, and they get shorter under heavy lifting. Boston Dynamics has said Atlas lasts about 2 hours on heavy tasks. Tesla's Optimus carries a 2.3 kWh battery in its torso; Tesla said it was sized for a full day's work, but no measured runtime has been published. Agility's Digit 5 was unveiled in September 2026, with early customer access from the first half of 2027.

## Why not just a bigger battery?

![Add capacity and the weight eats some of it back](../assets/diagrams_en/inv3-spiral.svg)

In electric cars, a bigger battery was the easy answer; for a robot standing on two feet, weight is a burden. The heavier the battery, the harder the leg and waist motors must work to carry it. This ties back to the joint design in [Part 2](physical-ai-investing-actuators.md): more efficient motors mean longer work from the same battery. The supply risk in those motors' rare-earth magnets was covered in Part 2 too.

## Uptime instead of capacity

![Instead of a bigger battery, never stop](../assets/diagrams_en/inv3-uptime.svg)

If a robot can change its own battery in 3 minutes, a battery that lasts only 2 hours can still support a full day of work. For investors, it also means each robot comes with more than one set of batteries.

Figure says the Figure 03 battery enclosure doubles as a torso structural member, saving mass and volume. It has passed the UN38.3 transport safety tests and says it is in the process of certification to UL 2271, a safety standard for light electric vehicle batteries. For robots working beside people, battery safety certification is an important gate too.

## Who supplies the cells

![Korean cell makers moved first](../assets/diagrams_en/inv3-supply.svg)

Humanoids are a tiny share of cell makers' results today. Their share prices and earnings are still driven by the EV market, and humanoids are extra demand far in the future. Solid-state batteries (QuantumScape, Solid Power, Samsung SDI and others) could raise energy density a lot and would suit robots well, but they are not yet commercial and no robot adoption has been confirmed.

## Korean cells, Chinese materials

![Mining is spread out; processing sits in China](../assets/diagrams_en/inv3-materials.svg)

Lithium ore is mined in many places, including Australia, China and Chile, but refining it into chemicals a battery can use happens mostly in China. Graphite for the anode is even more concentrated: over 95% of battery-grade graphite comes from China. It's the same structure as the rare-earth magnets in [Part 2](physical-ai-investing-actuators.md). Even the weak point matches: the processing plant, not the mine.

![Controls switch on and off; the dependence stays](../assets/diagrams_en/inv3-controls.svg)

That's why China's export controls reach Korean cell makers directly. Korean companies aren't standing still: POSCO Future M makes precursors in Korea and has signed an anode deal with a US automaker using Mozambican natural graphite among other sources, widening supply outside China. Still, materials that are over 90% dependent can't be switched in a few years. And humanoid batteries are tiny next to EV volumes, so robot makers have even less power to change this structure.

## Could a "portable reactor" be the answer?

In the comics, Astro Boy ran on nuclear power. In the 1950s nuclear energy looked like the answer to everything, and in 1958 Ford even showed the Nucleon, a concept car with a small reactor in the trunk. Only scale models were made; no working car was ever built. What stopped it is what stops humanoids now: the shielding is too heavy, and an accident would be dangerous.

![Too small, or too big](../assets/diagrams_en/inv3-scale.svg)

At one end, a **nuclear battery** lasts for decades, but its output is in microwatts, suited to sensors or medical devices. At the other, **microreactors** and **small modular reactors (SMRs)** are "small" only in reactor terms: megawatt-scale, with tonnes of shielding, meant for military bases, remote sites and data centers. The hundreds of watts to 1 kW a humanoid needs sits in between.

In between, a nuclear-powered robot does exist: the Mars rovers Curiosity and Perseverance. They use not a reactor but a radioisotope thermoelectric generator (RTG), which turns the heat of decaying plutonium-238 into electricity: about 110 W, roughly a quarter of a humanoid's average draw, from about 45 kg of hardware. The rover charges batteries from it slowly and draws on them as needed. But plutonium-238 is scarce (the US targets about 1.5 kg of oxide a year, and output has been below that), and a robot walking beside people with radioactive material on board is hard to imagine getting approved. Mars works because nobody is there. For humanoids on Earth, nothing but batteries fills the gap for now.

That doesn't make nuclear irrelevant to Physical AI. The link just runs through **the power demand of the data centers that train robots and the factories that build them**, not the robot's body. Four privately developed microreactors in a US Department of Energy pilot program reached zero-power criticality by July 4, 2026, but that is a first step, far from commercial power.

## Keep the two themes apart

![Same word 'power', different drivers](../assets/diagrams_en/inv3-two-themes.svg)

The right side hangs on data-center power contracts and reactor licensing timelines, and it splits further. Oklo has no power-sales revenue yet (only about $1.2 million in Q2 2026, from acquired services businesses), so its share price leans heavily on expectations, and it has a history of issuing new shares to raise money. Constellation and Vistra already earn revenue from operating plants, so even under one nuclear label their shares move for different reasons.

The numbers make the gap plainer (as of the 2026-09-29 close).

- **Oklo (OKLO, NYSE):** about $6.9B in market cap on roughly $1.2 million of trailing-12-month revenue, so there is no P/E to speak of. It holds about $2.5B in cash, but its share count grew about 30% in a year, and the stock is down about 66% from a year ago.
- **Constellation (CEG, Nasdaq):** about $94B market cap, roughly 21x forward earnings, down about 20% over one year.
- **Vistra (VST, NYSE):** about $47B market cap, roughly 14x forward earnings, down about 32% over one year.

All three fell over the year, but CEG and VST have earnings underneath them, while Oklo moves on expectations alone.

## What to watch

![In the end: how many humanoids sell](../assets/diagrams_en/inv3-checks.svg)

Until humanoids sell in the tens of thousands a year, cell contracts and solid-state adoption stay small numbers in cell makers' results. One date outside the picture is worth marking: the end of China's export-control suspension. It originally ran to November 10, 2026; after the September US–China summit, the US Treasury Secretary said the deal is extended to January 10, 2027 (2026-09-25). The reported extension covers rare earths, though, and whether the suspension of the battery-material controls (MOFCOM No. 58 of 2025) is extended with it has not yet been confirmed by a Chinese Ministry of Commerce notice (as of 2026-09-29).

---

## Summary

| Question | Answer |
|---|---|
| Why only humanoids | The arm is on a cable; the humanoid carries its energy |
| Where things stand | 1.5–5 hours per charge. Nothing covers an 8-hour shift |
| Industry direction | Uptime over capacity: autonomous swaps (~3 min), docking, wireless charging |
| Cell supply | LG Energy Solution first, Samsung SDI and SK On following. Robots are still a small share of sales |
| Materials | Processing is concentrated in China (graphite 95%+, cathode ~85%). The suspension originally ran to Nov 10, 2026; the US–China deal is extended to Jan 10, 2027 (battery materials unconfirmed) |
| Reactors | Not robot power. A separate theme: AI data-center and factory power |
| What to watch | Uptime claims, cell contract size, solid-state timelines, humanoid output, a notice extending the battery-material suspension |

Part 3's conclusion: **the humanoid power problem is not about a bigger battery but about never stopping, and nuclear is an infrastructure story, not a robot-body story.**

---

**Series** · [← Part 2: Value Shifts Seen Through One Joint](physical-ai-investing-actuators.md) · [Part 1: Investing in Physical AI](cobot-investing.md)

*Related: [Choosing a Physical AI Approach](choosing-physical-ai.md) · [Putting the Robot's Brain on the Edge (1)](jetson-ros2-setup.md) · [UR vs FANUC (openness)](cobot-ur-vs-fanuc.md)*

### Sources and notices

Runtimes and battery swap and charging methods follow each company's statements and reporting: Figure 03 and its battery development, Figure AI's official announcements (battery development 2025-07-17, Figure 03 2025-10); Atlas's autonomous battery swap, Interesting Engineering; UBTech Walker S2, CnEVPost (2025-07-17); Agility Digit 5, Agility Robotics' announcement (2026-09) and The Robot Report; the uptime race, Digital Today; Optimus battery capacity, Tesla AI Day (2022); LG Energy Solution's humanoid cell supply, KED Global (2026-07-02) and Digitimes (2026-07-07); nuclear batteries, reporting on Betavolt's announcement (Tom's Hardware, 2024-01); the microreactor pilot program, the American Nuclear Society (2025-11), Neutron Bytes (2026-07-08) and World Nuclear News; the Mars rover RTG, NASA's MMRTG fact sheet and JPL; plutonium-238 production, Oak Ridge National Laboratory and the US Department of Energy; the Ford Nucleon, an American Nuclear Society article; Samsung SDI's solid-state schedule, battery-news (2026-08-03); the Hyundai and Kia agreement, Hyundai News; Oklo's finances, its quarterly SEC filing (Q2 2026); share prices and P/E for the three nuclear names, StockAnalysis (2026-09-29 close). Some supply relationships and runtimes are reports the companies have not officially confirmed, and the humanoid's average power draw is an estimate computed from public specs. China's shares of battery materials follow the IEA Global Critical Minerals Outlook 2025 and Global EV Outlook 2026, the Cobalt Institute's market report (2026-05) and the USGS Mineral Commodity Summaries 2026; export controls and their suspension, China's Ministry of Commerce announcements (No. 39 of 2023, Nos. 58 and 70 of 2025), the MOFCOM–MOST export-restricted technology catalogue revision (2025-07-15), Benchmark Mineral Intelligence and Herbert Smith Freehills Kramer; the September 2026 extension, Rinnovabili (2026-09-25) and Rare Earth Exchanges; Korea's material dependence and diversification, Energy Innovation Reform Project data (2024-05) cited by the Korea Economic Institute of America (2025-08-25), KED Global (2025-10-15) and the POSCO newsroom. Reference years differ by material. All figures are values at the time of research (2026-09-28) and will change. Company and product names are trademarks of their owners, used here only for reference. **This post is not a recommendation to buy or sell any stock, nor investment advice, and the author accepts no responsibility for any investment outcome.** Investment decisions and their results are entirely the reader's own.

### Glossary

- *kWh (kilowatt-hour)*: an amount of energy; 1 kW used for one hour. The unit of battery capacity
- *kW · MW · MWe*: instantaneous power. 1 MW = 1,000 kW; MWe is a reactor's electrical output
- *Uptime*: the share of the day a robot actually works
- *Hot-swap*: changing a battery without shutting the robot down
- *Energy density*: how much energy fits in a given weight (or volume)
- *Cell*: the smallest unit of a battery; cells are grouped into packs
- *2170 · 4680*: cylindrical cell sizes (21 mm × 70 mm, 46 mm × 80 mm)
- *Solid-state battery*: a battery with a solid electrolyte instead of a liquid one; expected to be denser and safer, not yet commercial
- *BMS (battery management system)*: the electronics that watch cell voltage and temperature and control charging and discharging
- *Wireless inductive charging*: sending power without a cable through the magnetic field between coils
- *Nuclear (betavoltaic) battery*: a cell that makes a tiny current for decades from electrons emitted by a radioisotope
- *Microreactor · SMR (small modular reactor)*: a reactor of a few MW · a factory-built modular reactor of tens to hundreds of MW
- *Refining*: turning mined ore into chemicals pure enough for batteries
- *Cathode · anode material*: the materials of a battery's positive and negative sides; cathodes use lithium, nickel, cobalt and so on, anodes mostly graphite
- *Precursor*: the intermediate material (mostly nickel, cobalt and manganese compounds) made just before the cathode
- *RTG (radioisotope thermoelectric generator)*: a device that turns the heat of decaying radioactive material into electricity; not a reactor
- *UN38.3*: the international safety tests for shipping lithium batteries
- *Criticality*: the point where the chain reaction in a reactor sustains itself; the first step toward commercial power
- *UL 2271*: a US safety standard for batteries in light electric vehicles (overcharge, impact, fire tests)
- *Log scale*: each tick is 10× the last
- *Shielding*: thick concrete or metal that blocks radiation
- *PPA (power purchase agreement)*: a long-term contract to buy power between a generator and a user such as a data center
