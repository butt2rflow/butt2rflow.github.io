---
title: "From Teach Pendant to ROS 2 (2) — Describing the Robot to ROS: URDF, TF2, ros2_control, RViz"
date: 2026-09-28
tags: [physical-ai, ros2, urdf, tf2, ros2-control, rviz, robotics]
lang: en
description: "A controller already knows its robot; ROS has to be told. URDF as the robot's blueprint, TF2 as the home of UFRAME and UTOOL, ros2_control for swapping in only the robot-specific layer, and RViz for checking it all by eye. Part 2 of 4."
---

# From Teach Pendant to ROS 2 (2) — Describing the Robot to ROS: URDF, TF2, ros2_control, RViz

> **From Teach Pendant to ROS 2 · Part 2 of 4.** [Part 1](ros2-for-robot-programmers.md) showed ROS 2 as wiring made of nodes and messages. This part connects a robot to that wiring. [Part 3](moveit2-goals-not-points.md) covers MoveIt 2, [Part 4](isaac-ros-gpu.md) Isaac ROS and cuMotion.

A FANUC controller already knows which robot it's attached to. Arm lengths, joint ranges and motor characteristics are loaded at the factory, and on the pendant you only set UFRAME and UTOOL.

ROS is different. It's an ordinary program on a PC, so at first it knows nothing about the robot it's connected to. You have to tell it three things, and then check by eye that it understood.

![The controller already knows the robot. ROS has to be told](../assets/diagrams_en/r2p2-what-ros-needs.svg)

This post works through the four rows of that picture from the top.

---

## The 30-second version

- **URDF** is the robot's blueprint file: the chain of links (rigid parts) and joints, joint ranges and 3D shapes. The arm comes from the maker; you attach the gripper and camera.
- **robot_state_publisher** combines the blueprint with the live joint angles to work out where every part of the robot is.
- **TF2** is the frame manager. It plays the role of UFRAME and UTOOL, but instead of picking a few by number, it connects all the frames into a tree. Converting a position the camera saw into robot coordinates is TF2's job too.
- **ros2_control** splits motor control into layers. The controller that follows trajectories is the same for every robot; only the hardware interface at the bottom differs.
- **RViz** shows all of this in 3D. It's where you catch mistakes before the robot moves.

---

## URDF, the robot's blueprint

URDF (Unified Robot Description Format) is a text file that writes a robot down as **a chain of links and joints**.

![A robot = a chain of links and joints](../assets/diagrams_en/r2p2-urdf-chain.svg)

The code on the right is one joint: "a revolute joint connecting the upper arm (upper_arm_link) and forearm (forearm_link), turning up to ±180° about this axis." It's the same information as the joint-range settings on your pendant, kept in a file. Each link is also tied to a 3D shape file, used to draw the robot on screen and to check for collisions.

You rarely write one from scratch. Robot makers ship per-model blueprints as packages. Most are written in **xacro**, which you can think of as URDF with reusable pieces. Your job is to attach your own equipment.

![Maker's blueprint + what you added = your cell](../assets/diagrams_en/r2p2-urdf-compose.svg)

Adding the gripper and camera matters more than it seems. Leave them out and ROS believes there's nothing on the end of the arm, so when it plans a path it has no idea the gripper will catch on the fixture. The same goes for the table and fixed jigs.

## Add joint angles to the blueprint

The blueprint only describes shape; it doesn't know what pose the arm is in right now. That's in the joint angles the robot driver keeps sending (`/joint_states`, the channel from Part 1). The node that combines the two is **robot_state_publisher**.

![Blueprint + joint angles = where every part is](../assets/diagrams_en/r2p2-rsp.svg)

The result goes out on a channel called `/tf`. Where every link of the robot is and which way it faces flows out continuously, and RViz, MoveIt 2 and your own nodes all use it. It's the same calculation the pendant does to show the tool-tip position on the current-position screen; in ROS a separate node does it and broadcasts it to everyone.

## TF2, where UFRAME and UTOOL live in ROS

When you teach P[3] on a pendant, it's stored as "where the UTOOL 1 tip goes, relative to UFRAME 1," because the same point has different numbers depending on which frame you look from. If coordinate frames themselves are new to you, [Frames & Transforms](frames-transforms.md) explains them with pictures.

In ROS, the library responsible for this is **TF2**.

![Same idea, different names and shape](../assets/diagrams_en/r2p2-uframe-utool.svg)

The difference is in the shape. A pendant keeps a few numbered UFRAMEs and UTOOLs and you pick one at a time. TF2 connects every frame into a **tree (the TF tree)**. Under a top-level `world` frame, from the robot base (`base_link`) it follows the joints to the flange (`tool0`), and from there branches go to the gripper tip and the camera. A table frame is another branch hanging off the base.

- **UTOOL** corresponds to the `tool0 → gripper_tip` branch: how far the gripper tip is from the flange.
- **UFRAME** corresponds to a frame attached to the base, like `base_link → table`.
- **The camera** is a branch too. A camera on the arm hangs under `tool0`, and its position is measured once by hand-eye calibration (measuring precisely where the camera sits on the tool).

Because the whole tree is connected, you can ask TF2 for the relationship between any two frames. Once you add a camera, this is the feature you'll use most.

![TF2: where is this point, relative to the base?](../assets/diagrams_en/r2p2-tf-lookup.svg)

A camera reports the part position **relative to the camera**. To send the robot there, you need the position **relative to the base**. Ask TF2 to "restate this point relative to base_link" and it walks the tree for you. You can check the relationship between two frames from a terminal, too.

```text
$ ros2 run tf2_ros tf2_echo base_link tool0
At time 1790561234.512000000
- Translation: [0.412, -0.133, 0.520]
- Rotation: in Quaternion (xyzw) [1.000, 0.000, 0.000, 0.000]
- Rotation: in RPY (degree) [180.000, 0.000, 0.000]
```

Position comes out in meters, and rotation comes out two ways. The quaternion writes an orientation as four numbers and is the format programs use with each other; the RPY (degree) line below it is the pendant's W, P, R. The RPY line is the one to read.

The trap at the bottom of the picture is the most common bug in cells with a camera on the arm. If the arm moved between the moment the picture was taken and the moment you compute, a result based on the camera's position "now" points at the wrong place. TF2 keeps a short history, so you can ask for **the transform at the time the picture was taken**. Pass along the time attached to each message (its timestamp) and you're done.

Cameras usually have two frames. There's `camera_link`, aligned with the camera body, and an optical frame (`..._optical_frame`) whose z axis points out of the lens. If you don't check which one a detection is relative to, you get answers with the axes rotated by 90°.

## ros2_control, swapping in only the robot-specific layer

Now for the part that actually moves the robot. **ros2_control** splits motor control into layers.

![Only the bottom layer differs by robot](../assets/diagrams_en/r2p2-ros2-control.svg)

- The **controller** takes a trajectory and follows it. The most common one, `joint_trajectory_controller`, is the same code for any robot (the UR and FANUC drivers default to `scaled_joint_trajectory_controller`, which follows the pendant's speed slider). It's the controller that receives the "follow this trajectory" action from Part 1. "Controller" here means a software component inside ROS, not the robot controller cabinet next to the robot.
- The **hardware interface** translates those commands into this robot's language. It's the only part that differs between robots, and it's what people usually mean by a "ROS 2 driver."

On a UR, the hardware interface reads state through UR's RTDE real-time data channel and sends a target position every 2 ms (e-Series; 8 ms on CB3) to the External Control program running on the controller. This is the command loop Part 1 said is timing-sensitive. FANUC has published an official ROS 2 driver (`fanuc_driver`), which also works as a ros2_control hardware interface. According to FANUC's documentation it needs an R-30iB Plus or R-50iA family controller with the J519 Stream Motion and R912 Remote Motion options, and Humble users take the `humble` branch. Check the latest documentation before you commit.

To test without a robot, use the **mock** interface: fake hardware that simply answers "moved as commanded" with no robot attached. Like ROBOGUIDE or URSim, it lets you run the whole cell's software before the robot arrives. Moving to the real thing only means changing the hardware interface setting in software; the first moves on the real robot still go slow, inside a risk-assessed cell.

Changing the controller changes how the robot behaves. You might switch from the trajectory-following controller to a force-control controller that pushes with a set force, if the robot supports that.

## RViz, where mistakes get caught before the robot moves

**RViz** brings everything so far onto one screen.

![RViz shows the world as the software believes it is](../assets/diagrams_en/r2p2-rviz.svg)

You turn on what you want from the list on the left: the robot drawn from its blueprint, small axes for each frame, the points the camera sees, and the motion planning panel used in Part 3. In that panel you can drag a goal into place with the mouse, preview the planned path, and then press execute.

RViz **only displays data**. If the camera frame points the wrong way, the part is sunk into the table, or the path skims the fixture, then the data really is wrong. Catch it here, before the robot moves.

If the view is empty, the picture shows where to look (the Fixed Frame is the frame everything is drawn in). The easy thing to confuse is that RViz isn't a simulator. To imitate physics or simulated cameras you need a simulator such as Isaac Sim.

---

## Summary

| Concept | What it does | On the pendant, roughly |
|---|---|---|
| **URDF** | Chain of links and joints, joint ranges, 3D shapes | The controller's built-in robot model and joint ranges |
| **xacro** | URDF made reusable; assembles several pieces | (none) |
| **robot_state_publisher** | Blueprint + joint angles → every link's position on `/tf` | The math behind the position screen |
| **TF2 / TF tree** | Connects frames into a tree; relates any two frames | UFRAME, UTOOL |
| **ros2_control** | Shared controller + robot-specific hardware interface | Motion engine + external motion-command port |
| **mock** | Fake hardware for testing without a robot | ROBOGUIDE, URSim |
| **RViz** | Shows robot, frames, sensors and plans in 3D | The pendant's 3D view |

With the robot now connected to the node graph from Part 1, [the next part](moveit2-goals-not-points.md) finally sends it somewhere: MoveIt 2, which computes a path when you give it just a goal instead of teaching every point. You'll see what FANUC's CONFIG, interference zones and J and L moves become there.

---

*Related: [Part 1 — One Robot Program Becomes a Conversation Between Programs](ros2-for-robot-programmers.md) · [Frames & Transforms — How a Robot Knows Where to Grab](frames-transforms.md) · [Why Robots Learn in a 'Fake World' First](robot-simulation.md)*

### Sources and notices

The behavior of URDF, xacro, robot_state_publisher, TF2, ros2_control and RViz follows the official ROS 2 Humble and ros2_control documentation; the UR driver's hardware interface (RTDE, External Control, command rate) follows the Universal Robots ROS 2 driver documentation; the FANUC driver and its requirements refer to the `fanuc_driver` repository and documentation published by FANUC Corporation. Code and terminal output are illustrative; the numbers are not from a real cell. ROS is a trademark of Open Source Robotics Foundation (Open Robotics); MoveIt of PickNik Inc.; FANUC and ROBOGUIDE of FANUC Corporation; Universal Robots, UR, URSim and URCaps of Universal Robots A/S (a Teradyne company); NVIDIA, Isaac Sim, Isaac ROS and cuMotion of NVIDIA Corporation. They are used here only to refer to those products.

### Glossary

- *URDF (Unified Robot Description Format)*: a blueprint file that writes a robot as a chain of links and joints
- *Link · joint*: a rigid part of the robot · the joint connecting two links
- *xacro*: a way of writing URDF with reusable pieces
- *robot_state_publisher*: the node that computes every link's position from the blueprint and joint angles and publishes it on `/tf`
- *TF2 · TF tree*: the ROS library that manages relationships between frames · the tree those frames form
- *base_link · tool0*: the conventional names for the robot base frame and the flange frame
- *Hand-eye calibration*: measuring precisely where the camera sits on the tool (or in the cell)
- *Quaternion*: a way of writing an orientation as four numbers, used instead of W, P, R
- *Timestamp*: the time attached to each message, when its data was produced
- *Optical frame*: a camera frame whose z axis points out of the lens
- *ros2_control*: the framework that splits motor control into controllers (shared) and hardware interfaces (per robot)
- *Hardware interface*: the part that turns shared commands into one robot's communication; what a "ROS 2 driver" really is
- *Mock hardware*: fake hardware that answers "moved as commanded" with no robot attached
- *RTDE*: UR's channel for exchanging data with the controller in real time
- *RViz*: ROS's 3D viewer; the Fixed Frame is the frame everything is drawn in
