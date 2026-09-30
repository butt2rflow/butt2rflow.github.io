---
title: "How Many Cameras, and Where — When One Wrist Camera Is Enough and When You Need Overhead"
nav_title: "How Many Cameras, and Where"
date: 2026-09-28
tags: [physical-ai, robot-vision, camera, eye-in-hand, cumotion, nvblox, urdf]
lang: en
description: "How many cameras should a robot cell have, and where? Put fixed things in the design file, changing things to the camera and people to safety devices; when one wrist camera is enough and the four cases that call for overhead; the ghost obstacles that come with more cameras; and a commercial example built on a single wrist camera."
---

# How Many Cameras, and Where — When One Wrist Camera Is Enough and When You Need Overhead

> **Robot vision · a design choice.** [Pendant to ROS 2, Part 2](ros2-robot-description.md) covered the design file (URDF), and [Part 4](isaac-ros-gpu.md) GPU planners such as cuMotion. This post takes the question between them: should a camera watch the whole cell so the planner sees everything, or do more cameras only add confusion?

A camera looking down on the whole cell feels reassuring. It sees the table, the jig and the robot, so it seems the planner could just look and avoid everything. Cells that work well on the floor usually go the other way: they narrow what the camera has to see and write the rest down in advance.

---

## The 30-second version

- Split what is in the cell three ways: **fixed things into the design file (URDF) as measured values**, **things that change every cycle to the camera**, and **people to certified safety devices**.
- If the variation is at the level of tolerance stack-up, **one wrist camera** is often enough, with a single calibration.
- Add overhead when any of **search area, cycle time, a clear-space check or a learned policy** applies. Even then, give the final pose to the wrist camera only.
- More cameras stack calibration errors and easily create **ghost obstacles**. Whether you can manage calibration and overlap matters more than the count.

---

## Split into design file, camera and safety devices first

![Fixed things to the design file, changing things to the camera, people to safety devices](../assets/diagrams_en/cam-three-buckets.svg)

If the camera re-measures the table and jig every time, the same table comes out a few mm thicker or thinner on each capture. That noise goes straight into the planner and the path shifts a little every cycle. Fixed things are faster and always identical when measured once and written into the design file. The values must be **measured from the actual installation**, not taken from CAD: in commissioning, jigs are often installed at dimensions and positions that differ from the CAD (the CAD vs as-built point from [Part 2](ros2-robot-description.md)).

In cuMotion terms, fixed items go in as box or mesh obstacles, and camera depth goes through nvblox (a library that turns depth into voxels and a distance map) only where needed. Handing the whole cell to nvblox sends the fixed items to the planner along with the noise.

## One wrist camera vs wrist + overhead

![Most cells start with one wrist camera](../assets/diagrams_en/cam-wrist-vs-overhead.svg)

A wrist camera (eye-in-hand) goes to a set **observation pose**, stops and captures. When the variation is a few cm, as with pallet position error, conveyor differences or assembly tolerance, one look from that pose puts the part in view.

## Four cases that call for overhead

![Any yes: consider overhead. All no: one wrist camera](../assets/diagrams_en/cam-decision.svg)

The fourth is a little different. Policies learned from demonstrations (ACT-style, [Track B](learned-policy-track-b.md); ACT is a model that learns motions from demonstration data) tend to learn better with both a wrist and an external view, and some SO-101 teaching kits (Advanced or Pro bundles, for example) include a gripper camera and an external camera.

## Seen on the cycle clock

![The saving is about one look motion](../assets/diagrams_en/cam-cycle.svg)

Cycle time alone justifies an overhead camera only when that one look motion is a meaningful share of the whole cycle.

## The ghost obstacles more cameras bring

![Stacked calibration errors create ghost obstacles](../assets/diagrams_en/cam-ghost.svg)

Each camera also adds work. The robot's own body has to be removed from every camera's depth using the design file (Isaac ROS cuMotion provides a robot segmenter, `isaac_ros_cumotion_robot_segmenter`, for this), the cameras need time sync, and each extra depth stream adds compute load on an edge computer such as a Jetson (a small GPU computer on site). Depth noise from metal jigs and glossy surfaces multiplies with the camera count too. So several cameras earn their keep **when one camera clearly cannot see a region because something blocks it**.

## Three roles for an overhead camera

![Three roles rather than live planner input](../assets/diagrams_en/cam-overhead-roles.svg)

A **clear-space check** uses the overhead camera to confirm, before the robot moves, that the path and the drop spot are empty. If something unexpected is there, the robot does not plan a way around it; it stops and calls an operator. This follows the principle from [Choosing a Physical AI Approach](choosing-physical-ai.md): the camera only adjusts how the robot **moves**, while **verdicts** such as pass/fail stay with the existing sensors and PLC.

## A commercial example built on one wrist camera

![One camera visits three bins in turn](../assets/diagrams_en/cam-wrist-example.svg)

In a public webinar, Vention described this setup for bin picking built on GRIIP, its physical AI pipeline (the product is Rapid Operator AI). One low-cost stereo camera does both scanning and picking, and its depth comes from stereo matching with the foundation model FoundationStereo ([Inside the Three Models](inside-the-models.md)). Bin picking has to look again before every pick anyway, so the look motion costs little there.

---

## Summary

| Question | Answer |
|---|---|
| Should a camera watch the whole cell? | No. Fixed things go into the design file as measured values; only changing things go to the camera |
| People? | Certified safety devices (area scanners, safety PLC) |
| Default camera setup | One wrist camera, one hand-eye calibration |
| When to add overhead | Any of search area, cycle time, clear-space check, learned policy |
| With two cameras | Wrist owns the final pose; overhead does rough position and gating |
| Pitfalls of many cameras | Stacked calibration errors (ghost obstacles), time sync, removing the robot body, compute load |

Narrowing **what the camera has to see** makes a cell simpler and more predictable than adding cameras does.

---

*Related: [Pendant to ROS 2, Part 2 — URDF and CAD vs as-built](ros2-robot-description.md) · [Part 4 — Isaac ROS and cuMotion](isaac-ros-gpu.md) · [Choosing a Physical AI Approach](choosing-physical-ai.md) · [From Stereo to Grasp](stereo-to-grasp.md) · [Try it: Hands-on Notes (0)](learn-without-industrial-robot.md)*

### Sources and notices

cuMotion, nvblox and the robot segmentation node follow NVIDIA's public Isaac ROS documentation; the commercial example's camera setup follows a public Vention webinar on GRIIP (2026), and GRIIP, Rapid Operator AI and the use of FoundationStereo follow Vention press releases (2026-02, 2026-03). The example is not an endorsement of any product. Bar lengths in the cycle-time figure are conceptual. NVIDIA, Jetson, Isaac ROS, cuMotion, nvblox and FoundationStereo are trademarks of NVIDIA Corporation; Vention, GRIIP™ and Rapid Operator AI of Vention Inc.; ROS of Open Source Robotics Foundation (Open Robotics). They are used here only to refer to those products.

### Glossary

- *Eye-in-hand (wrist camera)*: a camera on the robot's wrist that moves with the robot
- *Overhead camera*: a camera fixed above the cell, looking down on the work area
- *Observation pose*: a set robot pose where the wrist camera stops to capture the part
- *Hand-eye calibration*: measuring how positions seen by the camera map to robot coordinates
- *Extrinsics*: where a camera sits, and which way it points, relative to the cell or robot
- *Planning scene*: the list of obstacles the planner checks for collisions (design file + added obstacles)
- *nvblox*: an NVIDIA library that turns depth images into voxels and a distance map for the planner
- *Voxel*: a small cube of 3D space; filled voxels count as obstacles
- *Inflation*: a safety margin wrapped around obstacles; the larger it is, the smaller the workspace
- *Commissioning*: tuning and verifying a cell under real conditions after installation, before handover to production
- *Tolerance stack-up*: small errors in parts, jigs and pallets adding up so positions shift slightly each cycle
- *Bin picking*: finding and picking parts one at a time from a bin of mixed parts
- *Deterministic*: always gives the same output for the same input
- *Clear-space check*: before the robot moves, confirm the path and drop spot are empty; if not, stop and call an operator
