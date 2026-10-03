---
title: "Putting the Robot's Brain on the Edge — The Real Robot: An Edge Computer Moves a Real Arm for the First Time"
nav_title: "Real robot · first motion"
date: 2026-10-02
tags: [physical-ai, jetson, isaac-ros, cumotion, universal-robots, ros2, ur-robot-driver, calibration, edge-ai, field-notes]
lang: en
description: "Up to the motion post, the robot was simulated hardware. This time the same Orin NX 16GB was connected to a UR20 cobot (PolyScope X) that happened to be idle. Starting from a read-only link, the factory calibration cut the tool-position error from 3.95 mm to 0.06 mm, one joint moved ±5°, and a cuMotion-planned move, checked by a person before execution, arrived within 0.1 mm of its goal. Plus the driver-upgrade trap, the speed slider, the floor cuMotion adds without asking, and the safety procedure. Field Notes, real robot."
---

# Putting the Robot's Brain on the Edge — The Real Robot: An Edge Computer Moves a Real Arm for the First Time

> **Field Notes · real robot.** The [motion post](jetson-pose-to-motion.md) checked planning, the obstacle map and the link between them, but the robot stayed **simulated hardware** to the end: a stand-in that only pretends to follow commands. Then a UR20 happened to be sitting idle, so I connected the same edge computer to it. This is the record of an edge computer moving a real robot arm for the first time.

With a real robot, one mistake can hurt a person or the equipment. So instead of connecting everything at once, I broke it into small steps. It started with a link that can't send commands at all, went as far as moving one joint by 5°, and only then executed a cuMotion-planned move. Here are the steps and what caught me on each.

*(An R&D record of the same Jetson Orin NX 16GB as the earlier posts, connected directly to a UR20 cobot running PolyScope X. For every motion step a person stood at the cell holding the enabling switch, and only very small moves were made at low speed. No real task, contact or force was involved.)*

---

## 30-second summary

- **It went up in steps.** Read-only link → factory calibration → one joint ±5° → a cuMotion-planned move. Each step started only after the previous one passed.
- **One calibration file removes 4 mm.** The tool position computed from the standard model was 3.95 mm off from what the robot reports; with this robot's factory calibration it was 0.06 mm. A simulator never shows this gap.
- **The first planned move arrived within 0.1 mm of its goal.** Tool up 5 cm and back down. Planning took 1.3 s; execution waited for a person's OK.
- **Three traps.** Upgrade only the driver and it crashes on the first command because it no longer matches the control packages. At an 18 % speed slider a 5-second trajectory takes 28 seconds. cuMotion quietly adds a floor at the base-plane height when the request has no obstacles.
- **A person stands between planning and execution.** The plan shows the joint changes first, runs only when a person allows it, and stale plans are refused.

---

## Why break it into steps

![Commands come only on the last step](../assets/diagrams_en/r7-ladder.svg)

Simulated hardware follows whatever you send. A real robot doesn't forgive like that: one wrong frame, model dimensions off by a few millimetres, or a safety setting you didn't expect, and the arm goes somewhere else. So each step checked just one thing.

| Step | What was checked | Result |
|---|---|---|
| 0. Read only | Network, the joints and tool position the robot reports, safety state | All readable over a link that can't send commands |
| 1. Calibrate | Whether the ROS model matches the real tool position | 3.95 mm → 0.06 mm |
| 2. One joint | Whether the driver's commands actually move the arm | Wrist joint ±5°, reached exactly |
| 3. Planned move | Whether a cuMotion plan runs as planned on the real robot | Tool up and down 5 cm, 0.1 mm from goal |

## Step 0: a read-only link

The first connection was deliberately one that **can't send commands**. UR robots stream joint angles, tool position and safety state over a real-time data channel called RTDE, and subscribing only to its outputs writes nothing to the robot. That was enough to confirm the network and see what state the robot was in.

One thing to know: PolyScope X robots **don't have the Dashboard server (port 29999)** that older UR robots have. Program state and similar information come from the robot's REST API instead. If you're following older guides and can't reach the dashboard, that's why.

The force sensor read about 34 N with nothing attached. That isn't a fault; it's the un-zeroed default offset. Zero it (`zero_ftsensor`) before any move that uses force.

## Step 1: matching the model with the factory calibration

When ROS computes the arm's pose, it uses the standard dimensions in the URDF. But every real robot has its own assembly tolerances, so UR measures each robot's actual dimensions at the factory and stores them in the controller. The UR ROS 2 driver has a tool to pull them out (`ur_calibration`).

![One factory calibration file removes the tool-position error](../assets/diagrams_en/r7-calib.svg)

At the same joint angles, I compared the tool position the robot reports with the one computed from the ROS model. The standard model was **3.95 mm and 0.40°** off; with this robot's calibration file it dropped to **0.06 mm and 0.01°**. Four millimetres means that however precisely the camera finds an object, the arm misses by that much.

The simulator (URSim) never shows this gap, because its robot is an ideal one with the standard dimensions. Skip the calibration when you move to the real robot and things that worked in simulation miss by a few millimetres. The calibration file has to go everywhere the driver and the model are built.

## Step 2: connecting the driver and moving one joint

To send commands to a real robot you install a UR extension called **External Control** (a URCapX) on the robot, build a program containing its node, and run that program from the pendant. Only while that program is running can the edge computer's driver move the robot.

A few things on PolyScope X weren't what I expected:

- External Control comes in versions matched to the robot software; pick the right one. Installing it needs the admin password.
- The edge computer's address (Host IP) is stored **per program**, not in the robot-wide settings. A new program needs it entered again.
- There was no need to switch to remote-control or automatic mode. Running the program from the pendant in manual mode, with motion only while the 3-position enabling switch is held, was enough.

### Upgrade only the driver and it dies on the first command

The UR driver in the Isaac ROS 3.2 image is version 2.9, too old to connect to a real robot; on ARM (Jetson) 2.14 or later is recommended. So I upgraded only the UR driver packages, and once the controllers were up, **the driver crashed the moment it handled the first command.**

The cause was version pairing. The new UR controller was built against a newer ros2_control, but apt left ros2_control at the old version without stopping the install. The error message doesn't make it obvious that this is a version problem. Upgrading **the UR packages and the ros2_control packages together** fixed it. "Change versions as a set", from [Part 4](isaac-ros-gpu.md), applies at the package level too.

### Wrist ±5°, and why 5 seconds became 28

The first move was the last wrist joint, +5° and then −5°. Both ended with "goal reached", and no other joint moved even 0.001°.

But a trajectory planned for 5 seconds took **27.8 seconds**. That isn't a fault either. The pendant's speed slider was at 18 %, and the UR driver's default trajectory controller stretches time by that slider (5 s ÷ 0.18 ≈ 28 s). A low slider is right for first tests, but if your program waits for "done in 5 seconds", the move will look hung or get cut short. Wait for the planned time divided by the slider fraction.

## Step 3: a cuMotion-planned move

Now the cuMotion from the [motion post](jetson-pose-to-motion.md) went onto the real robot. Planning used the UR20 cuMotion configuration (the one built in the motion post) and the calibrated model, and planning and execution were split so that execution happens only after a person checks the plan.

![A person stands between planning and execution](../assets/diagrams_en/r7-gate.svg)

The planning program doesn't move the arm; it only shows how many degrees each joint will move. When the person at the cell has looked and allowed it, the execution program moves. If the arm has moved more than 0.5° since planning, the plan is treated as stale and refused. It's a way for a person to look at a new path once before it runs.

The result: the tool went up 5 cm and back down. Planning took 1.3 s, and execution took 43 s and 37 s (slider about 18 %). Both moves arrived **within 0.1 mm of the goal**, and after coming back down the joints were exactly at their starting angles.

### The floor cuMotion adds without asking

One thing stopped me here: every plan failed with "start state in collision".

![The floor cuMotion adds without asking](../assets/diagrams_en/r7-table.svg)

When a request carries no obstacles at all, the cuMotion planner node adds a 2 m × 2 m plate at height 0 of the robot base frame as a floor. That's a sensible default for a tabletop robot. But this UR20 sits on a pedestal and works **below** its base plane, so the tool was inside that plate from the start. Any obstacle in the request removes the plate entirely, so I sent one tiny dummy object far away, leaving **self-collision checks only**.

That's a stopgap. To avoid real obstacles, the camera has to be calibrated against the robot base so that the obstacle map from the [motion post](jetson-pose-to-motion.md) lands in this robot's frame. This time the arm moved only 5 cm through empty space, so self-collision checks were enough.

## Why a person has to be there

The most important part of this record is the procedure, more than the numbers.

- **A person was at the cell for every motion step,** holding the 3-position enabling switch; letting go puts the robot in a safeguard stop. The emergency stop was within reach too.
- **Only small moves at low speed:** slider about 18 %, 5° on one joint, 5 cm at the tool.
- **The edge computer never uploaded robot programs remotely.** Creating and saving robot programs was done by a person on the pendant.
- Moving on to work near people, unattended runs, or contact and force needs speed and force limits, the real payload settings, and a risk assessment and sign-off from whoever owns the cell first. As [How Many Cameras, and Where](camera-placement.md) put it, collision-avoiding path planning is not a safety function.

## Not done yet

| Next step | Why it's needed |
|---|---|
| Camera-to-robot-base calibration (board on the flange, 10–15 poses) | To bring object poses and the obstacle map into robot coordinates |
| A foundation-model pose as the real robot's goal | The motion post's "pose → goal", on the real arm |
| A cell model (pedestal, table, fence) | Right now only self-collision is checked |
| Contact and force (zero the sensor first) | The last few millimetres: inserting, pressing |

## Summary

| Step | Result | What caught me |
|---|---|---|
| 0. Read only | Joints, tool and safety state all readable | No Dashboard server (PolyScope X), force-sensor zero |
| 1. Calibrate | 3.95 mm → 0.06 mm | A gap the simulator never shows |
| 2. One joint | ±5°, reached exactly | Driver-only upgrade crashes; at an 18 % slider 5 s becomes 28 s |
| 3. Planned move | 5 cm up and down, 0.1 mm from goal | cuMotion's default floor |

- **Approach a real robot in steps.** Read only → calibrate → one joint → planned move.
- **Calibrate from the start.** The few millimetres a simulator hides show up on the real arm.
- **Upgrade versions in pairs.** The driver and the control packages together.
- **Doubt the defaults.** The speed slider and cuMotion's floor both change the result without an error.
- **Put a person between planning and execution.** The edge computer plans, a person checks, and safety belongs to the robot controller and the enabling switch.

---

<details>
<summary>Notes: where these results come from</summary>

The numbers were **measured directly** on 2 October 2026 with a Jetson Orin NX 16GB and a UR20 running PolyScope X (10.12) (Isaac ROS 3.2, ROS 2 Humble, UR ROS 2 driver 2.14, External Control URCapX 1.2.0). Each result is one run on one robot, so read them as tendencies, not statistics. Every move was made in manual mode at low speed with a person holding the enabling switch; no real task, contact or force was involved. This post records a procedure; applying it to a real cell must follow that robot's safety configuration and risk assessment.

The UR driver's calibration tool, External Control, operating modes and the default trajectory controller's speed scaling are based on the Universal Robots ROS 2 driver documentation; the cuMotion planner node's default floor is based on the Isaac ROS cuMotion source.

Universal Robots, UR, UR20, PolyScope, URCap and URSim are trademarks of Universal Robots A/S; NVIDIA, Jetson, Orin, Isaac ROS, cuMotion and cuRobo of NVIDIA Corporation; ROS of Open Robotics. They are used for identification only.

</details>

**Series** · [← Previous: Motion — After the Pose Comes Movement, Planning Around an Obstacle Map](jetson-pose-to-motion.md)

*Related: [From Teach Pendant to ROS 2 (4) — Isaac ROS and cuMotion](isaac-ros-gpu.md) · [How Many Cameras, and Where](camera-placement.md) · [Try it: Hands-on Notes (0) — SO-101 and URSim](learn-without-industrial-robot.md)*

### Glossary

- *PolyScope X*: UR's latest controller software, including the pendant screen
- *Pendant*: the hand-held panel beside the robot for building and running programs
- *RTDE*: the data channel UR robots use to exchange joint and tool positions and state in real time
- *External Control*: a UR extension (URCapX) that lets an external computer's ROS 2 driver move the robot
- *3-position enabling switch*: a switch that must be held at its middle position for the robot to move; releasing it or pressing it fully stops the robot
- *Factory calibration*: each robot's actual dimensions, measured by UR and stored in its controller
- *URDF*: the description file with the robot's link lengths and joint layout
- *ros2_control*: the ROS 2 framework that starts and manages robot controllers
- *Speed slider*: the pendant control that scales the robot's overall speed as a percentage
- *Self-collision*: the robot arm hitting another part of itself
- *Risk assessment*: the process of finding the hazards in a robot cell and deciding the measures against them
