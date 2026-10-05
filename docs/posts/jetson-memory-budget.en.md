---
title: "Putting the Robot's Brain on the Edge — The Memory Budget: Perception and Motion on One 16 GB Jetson"
nav_title: "Memory budget · perception + motion on one box"
date: 2026-10-05
tags: [physical-ai, jetson, orin, memory, foundationpose, cumotion, soak-test, ros2, universal-robots, field-notes]
lang: en
description: "Like a real cell, camera perception and path planning went onto one Jetson Orin NX 16 GB for long soak tests. Motion alone ran 7.6 hours without trouble, but with continuous object tracking it hit the memory floor after 26 minutes in a dark office, and after 1 h 10 min even with leaner settings. The culprit wasn't cuMotion but FoundationPose, whose memory swings every time it re-finds the object. Taking one pose per cycle has held for 7.7 hours and counting. The post ends with how a real cell would split the work. Field Notes: The Memory Budget."
---

# Putting the Robot's Brain on the Edge — The Memory Budget: Perception and Motion on One 16 GB Jetson

> **Field Notes · The Memory Budget.** Until now perception and motion were tested separately. [The 16GB correction](jetson-foundationpose-16gb.md) checked whether FoundationPose alone fits in 16 GB; [The Simulators](jetson-ursim-planners.md) checked how long cuMotion and the UR driver hold up. A real cell runs both: the camera finds the part pose, and the arm plans and moves to it. So we put both on one Jetson and ran them for hours.

The short answer: one 16 GB box is tight. With continuous tracking, memory ran out in about an hour. But the culprit wasn't the one we expected, and changing how perception is used made a big difference.

*(R&D on the same Jetson Orin NX 16GB as the earlier posts. The camera and perception were real, tracking a mini PC on a desk. The robot was **URSim (a UR12e simulator)**; no real robot moved.)*

---

## 30-second summary

- **On a Jetson, CPU and GPU share one pool of memory.** What the GPU holds can't be swapped out, so a full pool can freeze the whole Jetson. The tests stopped themselves when available memory fell below 1 GB.
- **Motion alone was fine for 7.6 hours.** 98.2 % success, 12 ms replies with no drift, about 4.1 GB in total.
- **With perception added and continuous tracking, it stopped after 26 minutes.** In a dark office, 0.93 GB was left. The biggest block was FoundationPose (6.7 GB).
- **Leaner settings bought 1 h 10 min.** cuMotion's memory dropped by 1.3 GB, but FoundationPose's swings on every re-acquisition were bigger. All 8 CPU cores were saturated for the hour too.
- **Taking one pose per cycle has held for 7.7 hours and counting (as of the night of October 5).** 775 of 776 poses succeeded, about 4 s each. Perception and motion peaks take turns instead of overlapping.
- **A real cell wouldn't put it all on one 16 GB box.** Split it across two Jetsons, use a bigger Jetson (AGX Orin 32/64 GB), slim perception down, or design for one pose per cycle.

---

## Why memory first

![On a Jetson, GPU memory is all of the memory](../assets/diagrams_en/r10-unified.svg)

A regular PC has RAM for the CPU and separate memory on the graphics card, and when RAM runs short it can swap to disk. A Jetson is different: CPU and GPU share one pool. The 16 GB module reports about 15.3 GB in total, and the OS, cameras, neural networks and path planning all have to fit in it.

The catch is that memory the GPU holds can't be swapped out. This Jetson had 7.8 GB of compressed swap (zram), and the tests barely touched it. When the pool fills, things don't just slow down; the whole Jetson can freeze. So every test ran with a watchdog: below 1.5 GB available it logs a warning, and below 1 GB it stops the test and cuMotion to protect the Jetson.

## How the test worked

The robot side reused the soak test from [The Simulators](jetson-ursim-planners.md). One long-lived client repeats a cycle:

1. Pilz PTP to the home pose
2. cuMotion 50 cm over a box
3. Pilz LIN 10 cm down and back up
4. cuMotion back

A cycle takes 30 to 50 seconds. Every step logs success, reply time and planning time, and every container's memory and CPU are logged each minute.

The perception side is the chain built up to [Tuning](jetson-tuning-licensing.md). From the OAK-D camera, Grounding DINO finds the object, SAM2 cuts the mask, ESS computes depth, and FoundationPose estimates and tracks the 6-DoF pose. It runs in two containers: one for FoundationPose, one for camera, detection, segmentation and depth.

## Who uses how much of the 16 GB

![Who uses how much of the 16 GB](../assets/diagrams_en/r10-budget.svg)

| Block | Memory | Note |
|---|---|---|
| FoundationPose container | 5.5 → 6.7–7.0 GB | climbs at first, then swings on every re-acquisition |
| Camera, detection, segmentation, depth | about 3.2–3.4 GB | nearly constant |
| cuMotion | 2.4 → 3.8 GB (defaults) | climbs in the first hour, then flat; a cache, not a leak |
| Driver, MoveIt, test client | about 0.3 GB | nearly constant |
| OS and other | about 1.3–1.7 GB | the rest |

Add it up and a little over 1 GB of the 15.3 GB is left. Motion alone used about 4.1 GB, so perception takes more than twice that.

cuMotion rose from 2.4 to 3.8 GB in the first hour and then stayed there for hours. That's not a leak: it's PyTorch holding on to GPU memory to reuse it. But it doesn't come down while idle either (3.75 → 3.71 GB over 30 idle minutes), and only a process restart releases it. So budget about 4 GB for cuMotion.

## How long each run lasted

![How long each run lasted](../assets/diagrams_en/r10-runs.svg)

| Run | Conditions | Result |
|---|---|---|
| Motion only | no perception | 98.2 % of 3,961 steps over 7.6 h, 12 ms replies with no drift. Ended by choice once the numbers stopped changing |
| Continuous tracking | dark office, default settings | 1.4 GB free after 20 minutes, stopped at **26 min** with 0.93 GB. Tracking 6.8 → 4.5 fps, cuMotion planning 1.3 → 2.0 s |
| Continuous tracking, leaner settings | dark office | stopped at **1 h 10 min** with 0.88 GB. 588 of 625 steps OK |
| One pose per cycle | lit office, default settings | **still running at 7.7 h**. Lowest available 1.21 GB, median 1.61 GB |

The dark office wasn't planned. The tests ran into the night, the lights went off, and the mean image brightness fell to 19 out of 255. The object sat at the edge of the frame, so it was lost and re-found often. We treated those two runs as the worst case and kept going.

## The culprit was FoundationPose, not cuMotion

![FoundationPose memory swings on every re-acquisition](../assets/diagrams_en/r10-swing.svg)

At first we suspected cuMotion. With motion alone, it was the thing whose memory grew the most. With perception added, the picture changed.

FoundationPose does two jobs. When it first finds an object, it generates hundreds of pose hypotheses and scores them all at once (registration); after that, it nudges the previous frame's pose (tracking). Registration is heavy. Here each one took about 2.8 to 3 seconds, and that's when memory swung. Even one-minute samples show swings of 0.4 to 1.0 GB, and another run showed a 1.3 GB swing.

With a little over 1 GB left, one swing is enough to cross the floor. In the dark office, 30 to 50 % of the time went to re-finding the object, so the risky moment came often. That points to the remedy: for memory, re-acquiring less and tracking longer matters most.

## Trimming the settings

The same dark conditions, rerun with leaner settings:

| Change | Effect | Cost |
|---|---|---|
| Desktop off (headless) | +0.2 GB available | small, because no desktop session was logged in; access over SSH only |
| ESS light | depth 64–70 → 45 ms | slightly lower depth quality |
| Fewer cuMotion seeds + PyTorch cache cleanup | memory **flat at 2.33 GB** instead of climbing to 3.8 GB (about 1.3 GB saved), planning 2.0 → 1.4 s | no-plan over the box rose from 6 % to 26 % |

The cuMotion settings paid off. The trouble is that FoundationPose's swings ate the 1.3 GB they saved. The run went from 26 minutes to 1 h 10 min and stopped for the same reason. The settings delayed the crossing; they didn't prevent it.

Two more things showed up besides memory:

- **The CPU was saturated for the whole hour.** Load average on the 8-core Jetson was above 8, against 2.5 for motion alone.
- **The UR driver's link dropped 31 times an hour.** No move failed, and it reconnected between moves, but on a real robot that number can't be ignored. The UR driver has to answer the robot every 2 ms, and the Jetson's Linux isn't a real-time kernel, so a busy CPU delays the reply. The driver died outright once, and the watchdog brought it back in 32 seconds.

There are candidates on the perception side too. Turning off the front/back check should roughly halve registrations (at the risk of 180° flips on symmetric parts); calling an object lost only after several bad frames in a row should cut re-acquisitions; and not loading unused detection models should free an estimated 0.5 to 1 GB. These are unmeasured estimates, to be added after testing. None of them fixes the CPU saturation or the link drops.

## One pose per cycle

![Continuous tracking vs one pose per cycle](../assets/diagrams_en/r10-ondemand.svg)

Think about a real cell again: few of them need the part pose every instant. The part stops on the conveyor, you look once, and you go pick it at that pose. So the test client changed: at the start of each cycle it turns perception on, takes one pose, turns perception off, then plans and moves.

Now perception's peak (registration) and motion's peak (planning) take turns. The pose is taken while the arm stands still, and perception rests while the arm moves. Every cycle starts with a registration, and memory still holds.

| Item | Result (7.7 h, night of October 5) |
|---|---|
| Pose | 775 of 776 succeeded, median 4.0 s, 95 % within 6.4 s |
| Available memory | lowest 1.21 GB, median 1.61 GB; never below 1 GB so far |
| Motion steps | 94 % OK; 17 % no-plan over the box |
| UR driver | died twice, restarted by the watchdog |
| CPU load average | about 6.6 (8 cores) |

The lighting changed too, so we can't say whether it holds because of the mode or because the room was lit. That's as far as this result goes: for a cell where the part doesn't move during the cycle, one 16 GB box can be realistic.

The open issues are clear too. A 17 % no-plan rate is nearly three times the 6 % with motion alone. Sharing the Jetson's resources looks like the cause, but we haven't confirmed it. The test client counts a cycle as failed at the first failure and doesn't retry, so about one cycle in four was logged as failed, and that number includes failures while the simulator moved to another PC. A real cell must have retries and a fallback path. The 24-hour result will be added when the run ends.

## In a real cell

![How a real cell would split it](../assets/diagrams_en/r10-options.svg)

The conclusion from these tests: **motion plus continuous tracking on one 16 GB Orin NX doesn't survive bad conditions.** Settings delayed it but didn't prevent it. Designing a real cell, pick from four options:

1. **Two Jetsons.** One for perception, one for motion. They stop stealing each other's memory and CPU; the pose goes over the network.
2. **A bigger Jetson.** Put the same stack on an AGX Orin 32 GB or 64 GB. Price and power go up.
3. **Lighter perception.** A detector trained on the part instead of Grounding DINO, load only the models in use, fewer re-acquisitions, better lighting. This ties back to the "lowest step that solves it" principle in [Start Here](choosing-physical-ai.md).
4. **One pose per cycle.** The cheapest fix for cells where the part sits still. The cycle gets longer by the pose time (about 4 s), and nothing that changes during the motion is seen.

Whichever you pick, a few things come with it:

- **A driver watchdog.** One dropped link kills the UR control node, and it doesn't come back on its own ([The Simulators](jetson-ursim-planners.md)).
- **A real-time kernel and dedicated CPU cores for the UR driver.** A busy CPU delays the 2 ms reply.
- **Retries and a fallback path for no-plan.**
- **A multi-day test under the worst conditions.** Here too, the problem showed up in the dark at night, not in daylight. A few demos won't show it.

Also, nvblox (the live obstacle map) wasn't running in these tests. A cell that maps live needs more memory.

## What others have found

We found no published data that logs memory while running FoundationPose, cuMotion and the UR driver together on one Jetson for hours. NVIDIA publishes throughput and latency, not memory for several models running together over time.

The closest is a 2026 paper from UC Berkeley and Microsoft, "Offload or Overload". Running a mobile manipulator's full workload (perception, mapping, a learned policy and more) plus the OS needed about 50 GB, so it couldn't all run at once on a 32 GB AGX Orin. The same learned policy (π0.5) had 440 ms latency and 30 % success on the AGX Orin, against 144 ms and 80 % on the larger Jetson Thor. The scale differs, but the conclusion points the same way: whether everything fits on one edge computer is settled by a memory budget and a soak test, not a demo.

## Wrap-up

| Checked | Result | Gotcha |
|---|---|---|
| Motion only | 7.6 h, 98.2 %, about 4.1 GB | cuMotion's cache isn't released when idle → budget about 4 GB |
| Continuous tracking, dark | memory floor at 26 min | FoundationPose 6.7 GB, swinging on every re-acquisition |
| Leaner settings | cuMotion saves 1.3 GB, 1 h 10 min | CPU saturated, 26 % no-plan, 31 link drops per hour |
| One pose per cycle | still running at 7.7 h, poses 775/776, about 4 s | 17 % no-plan; lighting also differs, so no single cause |
| A real cell | two Jetsons, AGX Orin 32/64 GB, lighter perception, one pose per cycle | driver watchdog, real-time kernel, retries, long tests in bad conditions |

- **A working demo isn't a working cell.** This stack had no trouble in a few-minute demo either.
- **Budget memory for the peak, not the average.** What overflowed was the swing at re-acquisition, not the average.
- **How you use perception matters as much as the hardware.** Watching continuously or looking once per cycle decides the memory and CPU picture.

---

### Glossary

- *Unified memory*: CPU and GPU share the same memory, as on a Jetson
- *Swap (zram)*: moving less-used memory elsewhere (disk or compressed memory) when memory runs short. It can't be used for what the GPU holds
- *Soak test*: repeating the same work for hours or days to see whether anything slows down or leaks
- *Registration and tracking*: FoundationPose's step that scores many pose hypotheses at once when it first finds an object (registration), and the step that nudges the previous frame's pose afterwards (tracking)
- *Cache*: memory held for reuse. Unlike a leak, it levels off
- *Load average*: the average number of tasks running or waiting to run. Equal to the core count means the CPU is full
- *Real-time kernel*: a Linux kernel built to answer within a fixed time, used for programs like robot drivers that must reply every few ms
- *Headless*: running without a screen (desktop)
- *nvblox*: an NVIDIA library that builds a live obstacle map from camera depth

---

**Series** · [← Previous: Isaac Sim — a virtual work cell on an RTX 3090 PC and a cloud GPU](isaac-sim-pc-and-cloud.md)
