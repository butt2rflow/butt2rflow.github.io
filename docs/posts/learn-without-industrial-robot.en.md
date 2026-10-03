---
title: "Hands-on Notes (0) — Learning Without a Real Industrial Robot: SO-101 and URSim"
nav_title: "Part 0 · Learning without a real robot"
date: 2026-09-28
tags: [physical-ai, hands-on, ros2, moveit2, isaac-ros, so-101, ursim, jetson]
lang: en
description: "Learning on a real UR or FANUC is hard to arrange. Using virtual controllers (URSim, ROBOGUIDE) and a small real arm (SO-101) as practice grounds: what each teaches and doesn't, what carries over to the real robot, how to wire them to a Jetson Orin NX, and the hands-on plan ahead."
---

# Hands-on Notes (0) — Learning Without a Real Industrial Robot: SO-101 and URSim

> **Hands-on Notes · Part 0.** The first post of a series that records actually doing what the concept posts ([Pendant to ROS 2](ros2-for-robot-programmers.md), [Choosing a Physical AI Approach](choosing-physical-ai.md)) explain. This part is a plan for choosing practice grounds; results will be written after they're done.

Once you've read about ROS 2, MoveIt 2 and Isaac ROS, the next step is moving a robot yourself. But while you're learning, hooking up a real UR or FANUC isn't easy.

![Three reasons a real robot is hard to use while learning](../assets/diagrams_en/hon-why-not-real.svg)

This post compares the ones available, what each teaches, and what carries over to a real robot.

---

## The 30-second version

- There are two broad kinds of practice ground: virtual controllers that run the real controller software, **URSim** (UR) and **ROBOGUIDE** (FANUC), and **SO-101**, a small real teaching arm.
- What they teach barely overlaps. Industrial drivers and safety setup on URSim; cameras, physics and learning from demos on SO-101.
- Task logic, frames, how to use MoveIt and vision code carry straight over to a real robot; you only swap the blueprint (URDF), driver and MoveIt configuration. Real safety certification and payloads are learned only on the real thing.
- A Jetson Orin NX is the ROS 2 brain for both, and the next six parts will write up what actually happens.

---

## Three practice grounds and the real thing

![What each teaches barely overlaps](../assets/diagrams_en/hon-four-grounds.svg)

**URSim** is UR's free virtual controller. It even brings up the pendant screen, and when you connect the real UR ROS 2 driver, commands flow almost exactly the way they would with a real robot. You can also see industrial behavior such as speed scaling and protective stops. On the **FANUC** side, the official ROS 2 driver can control ROBOGUIDE's virtual robots, but ROBOGUIDE is a paid license, and even the virtual controller needs the streaming options (J519, R912). Mock hardware ([Pendant Part 2](ros2-robot-description.md)), which just answers "moved as commanded" with no robot, is supported by both the UR and FANUC drivers, so the driver and MoveIt connection can be practiced for free.

**SO-101** is an open-source teaching arm a leader arm you move by hand, paired with a follower arm that copies it. With five joints and a gripper it can pick up real objects, and with a camera added, one arm covers everything from perception to learning from demonstrations.

## What carries over to the real robot

![Upper layers carry over, lower ones swap, the bottom is learned on the real robot](../assets/diagrams_en/hon-what-transfers.svg)

This is "one stack, many robots" from [Pendant to ROS 2, Part 4](isaac-ros-gpu.md), seen from the practice side. The bottom layer can't be substituted, so moving to the real robot starts again with low speed and a risk assessment.

## The URSim setup

![A real ROS 2 driver on a virtual UR controller](../assets/diagrams_en/hon-ursim-setup.svg)

The e-Series URSim is x86-only, so the straightforward setup runs it on a PC with the Jetson joining over the same network. The PolyScope X simulator ships an arm64 image, but when the [motion post](jetson-pose-to-motion.md) tried it directly on an Orin, the simulator container it launches inside was x86-only and wouldn't run. So PolyScope X also belongs on an x86 PC with the Jetson joining over the network (that route uses the External Control URCapX).

## The SO-101 setup

![One small real arm for both neural perception and a learned policy](../assets/diagrams_en/hon-so101-setup.svg)

Geometry, neural perception and learned policies are the three designs from [Choosing a Physical AI Approach](choosing-physical-ai.md). LeRobot supports SO-101 natively, so recording demos and training a policy can start right away. The ROS 2 side (neural perception + planner) uses community-made packages; several repositories provide the URDF, a ros2_control driver for the servos and a MoveIt 2 configuration. Part 2 will note which one was chosen and why.

## Pairing practice grounds with concept posts

![Each concept post gets a hands-on partner](../assets/diagrams_en/hon-map.svg)

If you've read Pendant Parts 1–3, start with URSim; if you've read the learned-policy post, start with SO-101.

## The limits of practice grounds

![What the practice grounds won't tell you](../assets/diagrams_en/hon-limits.svg)

Virtual controllers hide things too. The robot in URSim has nominal dimensions, so on moving to a real UR20 the tool position was 3.95 mm off without the factory calibration ([Field Notes real-robot post](jetson-real-robot-first-move.md)). Code learned on a practice ground carries over, but calibration and the safety procedure start over on the real robot.

When an SO-101 grasp fails, the first question is whether the vision was wrong or the arm was imprecise. So the comparison experiment (Part 6) will repeat the same arm, block and conditions 20 times each, and measure the arm's own repeatability separately.

## The hands-on plan

![Written as it gets done](../assets/diagrams_en/hon-roadmap.svg)

My reasoning for the order: seeing an arm copy a demo first should give the stamina for dull steps like calibration, and debugging perception and control separately should make causes easier to find. Each part will be written after it's actually done, including where things got stuck and how they were solved.

---

## Summary

| Practice ground | Teaches | Doesn't teach |
|---|---|---|
| **URSim** (free) | UR driver, External Control, speed scaling, protective stops, Pendant Parts 1–3 | Cameras, physics, grasping |
| **FANUC virtual** (ROBOGUIDE paid) | FANUC driver connection, MoveIt setup | (on the ROS 2 path) Cameras, physics |
| **Mock hardware** (free, UR and FANUC) | Driver and MoveIt connection | Any real controller behavior |
| **SO-101** (cheap) | Physics, cameras, calibration, Isaac ROS, learning from demos | Industrial controller behavior, precision |
| **A real industrial robot** | Everything, especially safety certification and real payloads | (hard to get) |

---

**Series** · Next: Hands-on Notes, Part 1: Building the SO-101 and Recording Demos (in preparation)

*Related: [Pendant to ROS 2, Part 1](ros2-for-robot-programmers.md) · [Choosing a Physical AI Approach](choosing-physical-ai.md) · [Learned Policies](learned-policy-track-b.md) · [Putting the Robot's Brain on the Edge (1)](jetson-ros2-setup.md) · [How Many Cameras, and Where](camera-placement.md)*

### Sources and notices

URSim's Docker images and supported architectures follow Universal Robots' ROS 2 driver documentation and the official Docker Hub images (universalrobots/ursim_e-series, ursim_polyscopex); the FANUC virtual robot and mock mode follow FANUC Corporation's FANUC ROS 2 Driver documentation; the SO-101 hardware design is TheRobotStudio's open-source SO-ARM100 repository; ROS 2 support for SO-101 refers to community repositories and the Hugging Face LeRobot documentation. This post is a plan made before the hands-on work, and the setup and results may change as it's done. Universal Robots, UR, URSim, URCaps and PolyScope are trademarks of Universal Robots A/S (a Teradyne company); FANUC, ROBOGUIDE and HandlingPRO of FANUC Corporation; NVIDIA, Jetson, Orin, Isaac ROS, cuMotion and FoundationPose of NVIDIA Corporation; Feetech of Shenzhen Feetech RC Model Co., Ltd.; Hugging Face and LeRobot of Hugging Face, Inc.; Docker of Docker, Inc.; ROS of Open Source Robotics Foundation (Open Robotics); MoveIt of PickNik Inc. They are used here only to refer to those products.

### Glossary

- *Practice ground*: an environment for learning in place of a real industrial robot: a virtual controller or a small real arm
- *URSim*: UR's virtual controller; runs the real controller software and pendant screen on a PC
- *ROBOGUIDE*: FANUC's offline programming and simulation software (paid)
- *Mock mode*: fake hardware that answers "moved as commanded" with no robot attached
- *SO-101*: an open-source teaching arm made of a leader arm and a follower arm; five joints + a gripper
- *External Control*: the add-on (URCap; URCapX on PolyScope X) that lets a UR controller accept commands from an outside computer
- *URDF*: the blueprint file describing a robot's links, joints and shapes
- *ros2_control*: ROS 2's standard framework for exchanging commands with motor drivers; real hardware and mock can be swapped
- *Geometry, neural perception, learned policy*: this blog's names for the three designs: geometric matching (no neural net), neural perception + planner, a policy learned from demos
- *Leader arm · follower arm*: the arm you move by hand · the arm that copies it
- *Hand-eye calibration*: measuring how camera positions map to robot coordinates
- *Speed scaling · protective stop*: slowing the robot from the pendant · the state where the robot stops itself on a collision or limit breach
- *Emulation*: running a program built for a different processor by imitating it; can be slow
- *Repeatability*: how closely the arm returns to the same spot when sent to the same point repeatedly
