---
title: "Choosing a Physical AI Approach — From Deterministic Automation to Learned Behavior (Track 0, A, B)"
date: 2026-09-28
tags: [physical-ai, robotics, automation, machine-vision, imitation-learning, deterministic]
lang: en
description: "Three designs that turn what a camera sees into robot motion (geometry, neural perception + planner, learned policy) on one axis: when to choose which, what changes from taught-point automation, and why being able to detect failure is the real criterion. A map that connects the Physical AI posts."
---

# Choosing a Physical AI Approach — From Deterministic Automation to Learned Behavior (Track 0, A, B)

> **Physical AI: start here.** Each robot post on this blog goes deep on one piece. This one sits above them and explains why you would choose one approach over another. At the end, the links to the posts that cover each concept in detail are collected in one place.

"Can we put Physical AI on our line?" usually comes with technology names attached: foundation models, imitation learning, NVIDIA Isaac. What you actually have to decide first isn't a technology but **the kind of design**. There are three broad ways to turn what a camera sees into robot motion, and they aren't competing options so much as steps on a staircase.

---

## The 30-second version

- There are three designs from camera to motion: **Track 0** (geometry, no neural networks), **Track A** (neural perception + planner) and **Track B** (a policy learned from demonstrations).
- The further right, the more is learned and the harder it is to look inside. Taught-point automation sits at the far left, step 1.
- You choose by **asking questions in order**: can it be fixed, does it only shift in the plane, can it be described with geometry, can a person demonstrate it. Stop at the step where the answer is yes.
- Track 0 vs A comes down to **engineer hours per new part**; real step 4 is a **hybrid**.
- The real criterion isn't whether something is non-deterministic but **whether its failures can be detected**. That's why acceptance changes from "it repeats" to "X of N succeed, and it knows when it failed."

---

## Same task, three designs

![Same arm, same block, only the design differs](../assets/diagrams_en/cpa-three-designs.svg)

A fair comparison uses the same arm and the same task; otherwise you can't tell whether a difference comes from the design or the hardware. An example of Track A is a pose estimation model such as FoundationPose; an example of Track B is an imitation-learning policy such as ACT. Only Track B starts without CAD, from demonstration data; it needs no camera-to-robot calibration, but the camera has to stay where it was during the demos.

## From deterministic to black box, on one axis

![The more is learned, the harder failure is to notice](../assets/diagrams_en/cpa-spectrum.svg)

**Deterministic** means the same input always gives the same result, as in a cell built from fixtures and taught points, and in Track 0, which has no neural networks. Track A's perception results wobble a little with lighting, but every stage's output can be checked.

Cell design gets easier once you separate motion from the verdict. The robot's **motion** may differ every cycle, but the **verdict**, such as pass or fail, must be the same every time. Use perception and learning to adapt the motion to the variation, and keep the verdict with the existing sensors, gauges and PLC interlocks. [Pendant to ROS 2, Part 1](ros2-for-robot-programmers.md) goes through how.

## Pick the step by asking in order

![Start at the bottom; climb only when forced](../assets/diagrams_en/cpa-staircase.svg)

The rule is to use the lowest step that solves the problem. Using step 3 where step 1 or 2 would do only adds setup, calibration upkeep and lighting sensitivity. Steps 3 and 4 split on one question: if the task can be written as coordinates, it's Track 0 or A; if it can't be written down but a person can show it, it's Track B. Routing a cable is hard to write as coordinates, but anyone can show it by hand.

What step 2 looks like in practice, a taught path shifted by an offset that vision measured, is covered by the automation ladder in [Pendant to ROS 2, Part 3](moveit2-goals-not-points.md).

## Track 0 or A: count the part types

![Choose by engineer hours per new part, not precision](../assets/diagrams_en/cpa-breakeven.svg)

Track 0 (fitting CAD to the point cloud with ICP) is deterministic and easy to explain, but it only finds the nearest answer from its starting pose, so every new part means retuning the starting pose and thresholds. Track A needs no per-object training, so a new part mostly means swapping the CAD (plus pointing the mask or detector at the new part). With few, fixed part types, Track 0; with many or frequently changing ones, Track A. The numbers in the chart are illustrative; work out "hours to add one part × expected number of part types" for your own case.

## Real step 4 is a hybrid

![Approach with geometry; learning only for the last few mm](../assets/diagrams_en/cpa-hybrid.svg)

Using step 4 rarely means handing the whole cell to a learned policy. Step 3's geometry and planner handle the approach and alignment, and the policy takes only the last few millimeters of inserting or pressing. With such a narrow scope the policy can be verified, and when it fails there is a clear place to go back to.

## Quiet failures are more dangerous

![Same situation, three kinds of failure](../assets/diagrams_en/cpa-failure.svg)

The three designs differ most when the object sits out of the arm's reach. Track 0 and A find the pose, and then the planner reports "no path." Track B is quiet because it learned motions from demonstrations with no mechanism for judging reachability; somewhere the demos never covered, it can carry on with a plausible-looking motion and no failure signal. Track A can fail quietly too if the pose itself is wrong, which is why its per-stage outputs (the mask and the pose score) need checks.

So the criterion isn't "is it non-deterministic?" but "**can its failures be detected?**" Measure these tendencies on the same arm by varying position, lighting, a new object, occlusion and reachability.

## What to measure

![Success rate is the surface; time to root cause is the running cost](../assets/diagrams_en/cpa-metrics.svg)

Minutes versus hours to find a cause looks small for one failure, but multiplied by a year's worth of failures it becomes most of the running cost.

## What changes when you move beyond taught points

For a team that has built taught-point automation, the first thing to know is that acceptance (buy-off) changes.

![From "it repeats" to "X of N succeed, and it knows when it failed"](../assets/diagrams_en/cpa-acceptance.svg)

A taught cell is accepted when "the path repeats." Once perception or learning is involved, results become statistical, so the contract has to define not just a success rate but **whether the cell detects its own failures**, where the operating envelope ends, and what happens on a failure. There are also signals to watch for while scoping.

![When you hear these, check again](../assets/diagrams_en/cpa-redflags.svg)

Taught-point automation is still step 1, and most of the time it's the right answer. The new options don't replace it; they only **extend** the reach to places where a fixture can't guarantee the part's position.

## Map of this blog's Physical AI posts

![This post is the map; the details live in each post](../assets/diagrams_en/cpa-map.svg)

| What you want to know | Read |
|---|---|
| Track A's perception stages (depth, mask, pose) | [From Stereo to Grasp](stereo-to-grasp.md) · [Inside the Three Models](inside-the-models.md) · [Model Anatomy](model-anatomy.md) |
| Turning camera coordinates into robot coordinates | [Frames & Transforms](frames-transforms.md) |
| ROS 2, MoveIt 2, deterministic cell design | [Pendant to ROS 2, Part 1](ros2-for-robot-programmers.md) · [Part 2](ros2-robot-description.md) · [Part 3](moveit2-goals-not-points.md) · [Part 4](isaac-ros-gpu.md) |
| Actually running it on an edge computer | [Field Notes, Part 1](jetson-ros2-setup.md) · [Part 2](jetson-isaac-foundation-models.md) · [correction](jetson-foundationpose-16gb.md) |
| Differences between robot makers | [What Is a Collaborative Robot](cobot-basics.md) · [UR vs FANUC](cobot-ur-vs-fanuc.md) |
| Simulation and sim-to-real | [Why Robots Learn in a 'Fake World' First](robot-simulation.md) |
| Track B, learned policies | [Learned Policies (Track B)](learned-policy-track-b.md) |

---

## Summary

| Concept | In one line |
|---|---|
| **Track 0** | Geometry that fits CAD to the point cloud (ICP). Deterministic; the fit error acts as confidence |
| **Track A** | A neural network estimates pose from CAD and a planner moves. No per-object training; stages can be checked |
| **Track B** | A policy learned from human demos turns images straight into joint commands. For what can't be written as coordinates |
| **Staircase** | Fixture → planar offset → geometry → demonstration. Stop at the first step that works |
| **Break-even** | Track 0 vs A: engineer hours per new part × number of part types |
| **Hybrid** | Approach with geometry; learning only for the last few mm |
| **The real criterion** | Not whether it's non-deterministic, but whether failure can be detected |
| **Acceptance** | "It repeats" → "X of N succeed, and it knows when it failed" |

---

**Series** · [Next: Learned Policies (Track B) →](learned-policy-track-b.md)

*Related: [Pendant to ROS 2, Part 1](ros2-for-robot-programmers.md) · [From Stereo to Grasp](stereo-to-grasp.md) · [Field Notes, Part 2](jetson-isaac-foundation-models.md)*

### Sources and notices

The three-design split, the staircase and the failure comparison are a framework assembled from public sources. ICP follows Besl & McKay's (1992) Iterative Closest Point; FoundationPose and Isaac ROS, NVIDIA's public material; SAM 2, Meta's public paper; ACT (Action Chunking with Transformers), Zhao et al.'s (2023) paper and the Hugging Face LeRobot documentation. The failure behaviors and the time-to-root-cause scale are expected tendencies, not measured results, and the numbers in the break-even chart are illustrative. NVIDIA, Isaac, Isaac ROS and FoundationPose are trademarks of NVIDIA Corporation; Hugging Face and LeRobot of Hugging Face, Inc.; SAM 2 is a model released by Meta Platforms, Inc.; ROS of Open Source Robotics Foundation (Open Robotics); MoveIt of PickNik Inc.; FANUC of FANUC Corporation; Universal Robots and UR of Universal Robots A/S (a Teradyne company). They are used here only to refer to those products.

### Glossary

- *Physical AI*: robot technology that looks, decides and moves, rather than relying only on fixtures and taught points
- *Deterministic · non-deterministic*: the same input always gives the same result · learned behavior whose results are statistical
- *ICP (Iterative Closest Point)*: geometry that nudges and turns a CAD model until it fits the point cloud; the leftover distance (residual) acts as confidence, though symmetric parts or a bad starting pose can give a wrong answer with a small residual
- *Point cloud*: thousands of surface points measured by a depth camera
- *Calibration*: measuring the relationship between camera coordinates and robot coordinates
- *Planner*: a program that computes a collision-free path to a goal pose
- *6-DoF pose*: an object's position and orientation written as six values, three positions and three rotations
- *Mask*: the pixels of an image that belong to the object, cut out
- *Learned policy*: a model trained to take camera images and output robot motion
- *Demonstration*: one recording made, for example, while a person moves a leader arm (a hand-moved control arm) and the robot copies it
- *Hybrid*: approaching with geometry and a planner, and handing only the final contact to a learned policy
- *Acceptance (buy-off)*: the check that equipment meets its requirements before it's handed over
- *Operating envelope*: the boundary of conditions the cell is responsible for, such as position range, lighting and part list
