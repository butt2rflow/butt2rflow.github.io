---
title: "Why Robots Learn in a 'Fake World' First — Simulation and sim-to-real"
date: 2026-09-18
tags: [robot-vision, physical-ai, simulation, sim-to-real, domain-randomization, Isaac-Sim, MuJoCo, foundation-models]
lang: en
series-prev: "[Model Anatomy](model-anatomy.md)"
description: What "trained in simulation" really means for FoundationStereo and FoundationPose — why robots learn in a fake world, what the sim-to-real gap is, and how domain randomization crosses it. In five pictures.
---

# Why Robots Learn in a 'Fake World' First

*A deep-dive side-branch of the robot-vision series. It digs into the aside that [Inside the Models](inside-the-models.md) and [Model Anatomy](model-anatomy.md) kept dropping — "these models were trained in simulation."*

Across the earlier posts I kept slipping past one sentence: "FoundationStereo and FoundationPose
were trained in simulation." It nagged at me every time. Here I was, telling a story about robots
grasping objects in the real world, while the ability itself was acquired **having never once seen
a real object.** How can something learned in a fake world work in the real one? And when it
doesn't, why not? That's this post.

## Why bother with a fake world

To teach a robot "pick up a part you've never seen," you need examples — **a staggering number** of
them. But gathering that data by repeating grasps with a real arm hits three walls.

1. **Safety** — early in learning, the robot is clumsy. A real arm repeating clumsy motions can
   damage the part, the arm, and — with bad luck — a person.
2. **Cost and time** — a real arm takes seconds per grasp. A million grasps? The math simply
   doesn't close. And you have exactly one arm.
3. **Labels** — to learn, an AI needs an **answer key (labels)**: "the correct pose of this object
   is *this*." Having humans hand-label real photos is slow and expensive, and things like a 6-DoF
   pose are hard to label accurately by eye at all.

**Simulation clears all three walls at once.** In a fake world, a broken arm just resets; you can
run it on **hundreds of computers at once**, compressing time; and above all, you **know the
answer for free.** The program placed the object, so it already knows the pose. No human labeling
needed.

> **The key point:** simulation's real appeal isn't pretty graphics — it's that it manufactures
> **labeled data almost infinitely, for free.**

![The three walls of data collection and how simulation clears them](../assets/diagrams_en/rvd-sim-why.svg)

> **Example — why labels are free.** Say the simulator places a mustard bottle on the desk at
> `(x=0.32, y=−0.10, z=0.04)`, rotated `35°`. At that instant the bottle's 6-DoF ground-truth pose
> is **already known** — we placed it. No human needs to eyeball the angle from a photo. Every time
> you hit "render," an image and its answer key pour out as a pair.

## A tour of the simulators — and why everyone uses Franka

There are several robot simulators, each with a slightly different character.

| Simulator | Made by | Character | Best at |
|---|---|---|---|
| **Isaac Sim / Isaac Lab** | NVIDIA | Photorealistic render + massive GPU parallelism | Perception data, reinforcement learning |
| **MuJoCo** | Google DeepMind (open source) | Fast, accurate contact physics | Control & RL research |
| **PyBullet** | Open source | Light, easy to install | Fast prototyping, teaching |
| **Gazebo** | Open Robotics | Tightly coupled with ROS | Whole-system integration testing |

- **Isaac Sim** is NVIDIA's simulator, rendering **near-photographic** images in bulk on the GPU —
  great for producing training images for perception models. **Isaac Lab**, which runs on top of
  it, is a learning framework that trains by "running thousands of robots at once" (as in RL).
- **MuJoCo** came out of academia and is now maintained open-source by DeepMind. Its **contact
  physics** (the math of things bumping and sliding) is fast and accurate — effectively the
  standard for control and learning research.
- **PyBullet** is light and easy to install — great for **learning first**.
- **Gazebo** rides alongside ROS for **whole-system integration testing.**

### But why does Franka show up in every example?

Open any of these and, as if by agreement, the same arm appears — the **Franka Panda**, a 7-axis
research arm. Papers, tutorials, and demos all use it, so each simulator ships a **Franka model for
free by default**, which in turn cements "everyone uses Franka."

There's a welcome implication here for anyone learning. A **real Franka (FR3) is tens of thousands
of dollars of research equipment** — not an easy buy. But its **digital twin is free inside every
simulator.** So you can learn the concepts and most of the practice **on the simulated Franka**, do
hands-on work on a **cheap arm**, and do real integration on an **industrial cobot** in the
field — climbing the ladder at almost no cost.

![The four simulators' characters and their common Franka](../assets/diagrams_en/rvd-sim-tools.svg)

> **Example — purpose picks the tool.** "I need 100k training images for a perception model" →
> **Isaac Sim**, strong at photoreal rendering. "I want to see the exact instant the gripper slips
> on the object" → **MuJoCo**, accurate contact physics. "I just want an arm on screen to see the
> idea fast" → light **PyBullet**. Same problem — **what you want to observe** decides the tool.

## The gap between fake and real — sim-to-real

So far simulation sounds like a cure-all. But there's a trap: **a robot that was flawless in the
fake world often flounders once it steps into the real one.** This gap is called the **sim-to-real
gap.**

Why does it open? Because simulation is an **approximation** of reality.

- Real cameras have **noise and motion blur**; fake renders are too clean.
- Real objects vary in **surface texture, reflectance, lighting**; simulation simplifies to a few.
- Real physics has **tiny frictions and slack**; the physics engine idealizes it away.

So a model trained only in simulation grows used to a "clean world it has seen," and collapses in
messy reality — like **someone who only ever solved textbook problems freezing on a real-world
application question.**

![Simulation is clean, reality is messy — the sim-to-real gap](../assets/diagrams_en/rvd-sim2real-gap.svg)

### The fix — deliberately messing things up (domain randomization)

There's a clever detour: **domain randomization.** Instead of straining to make simulation *match*
reality — you can't do it perfectly anyway — you do the opposite and **shake the simulation into
extreme variety.** Lighting, background, object color and texture, camera angle, even physics
coefficients — randomized every scene.

The model then learns "this world is arbitrary by nature." When the real world arrives as **one of
those countless variations**, it's just **another variation** to the model, and it takes it in
stride. Rather than imitating reality, the strategy is to learn **broadly enough to contain it.**

> **One-line analogy:** someone raised hearing every accent in the world understands a brand-new
> accent better than someone raised on a single one. Domain randomization is playing the model
> **every accent in advance.**

![Domain randomization — learn broadly to contain reality](../assets/diagrams_en/rvd-domain-randomization.svg)

> **Example — one scene, twenty times.** Take a single mustard bottle on a desk and render 20
> frames, each with randomized lighting (morning · fluorescent · sunset), background (white wall ·
> wood grain · factory floor), and bottle color (yellow · faded yellow · orange-ish). To the eye
> they're "20 different photos," yet the **answer — the object's pose — is identical in all 20.**
> The model learns "a yellow bottle sits at this pose whatever the lighting or background."

### Where this connects to the earlier posts

In [Model Anatomy](model-anatomy.md) you saw a table with rows like "add sensor noise / motion blur
to close the gap with real capture" and "render in Isaac Sim while randomizing lighting, background,
clutter." That is exactly the **domain randomization** just described, in practice. And the split in
[Inside the Models](inside-the-models.md) — "FoundationStereo/Pose learned from simulation, SAM from
real photos" — meets us here too: **simulation gives depth/pose answer-labels for free, but it
cannot hand you the *meaning* label "this is object X,"** so SAM took the road of 11 million real
photos.

## So, in the field

Simulation is a **starting point**, not a destination. The realistic flow is:

1. **Learn in simulation at scale** (broadly, via domain randomization).
2. **Fine-tune on a little real data**, or at minimum **validate on the real thing.**
3. Close the remaining gap with **calibration** (camera calibration, frame alignment — the
   [Frames & Transforms](frames-transforms.md) material earns its keep here).

![The field flow — sim learning → real validation → calibration → deploy](../assets/diagrams_en/rvd-sim-field-flow.svg)

An ability learned in a fake world working in the real one isn't magic. It's the payoff of a
three-beat rhythm — **learn broadly, validate on hardware, close the remaining gap with
calibration.** Don't just read about the sim-to-real gap; live it once, and you'll feel in your
hands why the three beats come in that order.

---

*NVIDIA Isaac Sim · Isaac Lab, MuJoCo (Google DeepMind), PyBullet, Gazebo (Open Robotics), and
Franka · Franka Panda are trademarks of their respective owners, used for identification only. All
diagrams were drawn by hand.*
