---
title: "From Teach Pendant to ROS 2 (4) — Isaac ROS and cuMotion: Moving the Slow Parts to the GPU"
date: 2026-09-28
tags: [physical-ai, ros2, isaac-ros, cumotion, nvidia, jetson, moveit2, robotics]
lang: en
description: "Perception that runs a neural network on every frame and planning in a crowded cell are slow on a CPU. Isaac ROS moves only the heavy nodes of the same ROS 2 graph to the GPU, NITROS removes the copies, cuMotion plugs into MoveIt 2's planner slot, versions go together as a set, perception results pass a gate, and one stack serves many robots. Part 4 of 4 (final)."
---

# From Teach Pendant to ROS 2 (4) — Isaac ROS and cuMotion: Moving the Slow Parts to the GPU

> **From Teach Pendant to ROS 2 · Part 4 of 4 (final).** After [Part 1](ros2-for-robot-programmers.md) on ROS 2's wiring, [Part 2](ros2-robot-description.md) on describing the robot and [Part 3](moveit2-goals-not-points.md) on MoveIt 2, this last part looks at NVIDIA's Isaac ROS, which moves the slow parts to the GPU.

Two of the five steps from Part 3 take a long time. Step 1, perception, has to run a neural network (an AI model trained to judge pictures) every time a camera picture comes in, and step 4, planning, has more path candidates to try the more crowded the cell gets. Both repeat the same kind of calculation an enormous number of times, which is exactly what a graphics card (GPU) is good at.

**Isaac ROS** is a set of ROS 2 packages that do this heavy work on the GPU. It isn't a new robot operating system; it's nodes that slot into the graph from Part 1.

---

## The 30-second version

- Isaac ROS nodes are **ordinary ROS 2 nodes**. They join the graph with the same topics and message types and just do the heavy math on the GPU.
- **NITROS** passes images between GPU nodes while keeping them in GPU memory. From Isaac ROS 5.0 the same capability is built into ROS 2 itself.
- **cuMotion** is a GPU planner that plugs into MoveIt 2's planner slot. Keep your code, add the cuMotion pipeline to the MoveIt config and pick it instead of OMPL. Each robot needs a companion file called **XRDF**.
- JetPack, ROS 2 and Isaac ROS go together **as a set** and are upgraded together.
- Perception results feed corrections only after passing a **gate** (confidence, stack-up range); outside it, the cell stops and reports. They never feed the verdict.
- Change robots and **the upper layers stay put**. You swap three things: the blueprint, the driver and the MoveIt configuration.

---

## Same graph, heavy nodes on the GPU

Look at Part 1's pick-cell graph again and the heavy spots are clear.

![Isaac ROS = ROS 2 nodes that use the GPU](../assets/diagrams_en/r2p4-gpu-nodes.svg)

Depth from two cameras (ESS, FoundationStereo), segmentation that cuts the part out of the picture (SAM 2), pose estimation that finds the part's position and orientation from its CAD model (FoundationPose), and path planning (cuMotion); the FoundationStereo and SAM 2 packages arrived in Isaac ROS 4.0. Only these four become Isaac ROS nodes; the rest, like the task node and the robot driver, stays as it is. What each model does and how is covered separately in [From Stereo to Grasp](stereo-to-grasp.md) and [Inside the Three Models](inside-the-models.md).

Isaac ROS has no dedicated screen of its own. Its nodes are ordinary ROS 2 nodes, so you view them with the same tools: `rqt_graph` from Part 1, RViz from Part 2, or a web-based ROS tool such as Foxglove. A graphical editor where you connect blocks with lines does exist, on the simulator side: Isaac Sim's Action Graph (OmniGraph) wires virtual cameras and robots to ROS 2 topics with blocks and lines. That lives inside the simulator, though; in a real cell, nodes are still connected in launch files.

Running neural networks fast on the GPU uses NVIDIA's TensorRT. A model has to be converted for that GPU once in advance (an engine build), and on an edge computer with little memory that step is often the first wall. The [Field Notes](jetson-foundationpose-16gb.md) describe getting past it on an Orin NX 16GB.

## NITROS, keeping images on the GPU

Simply chaining GPU nodes together sometimes isn't as fast as you'd hope. The reason is copying.

![The slow part is often the copying, not the math](../assets/diagrams_en/r2p4-nitros.svg)

Ordinary ROS 2 messages live in CPU memory. So the depth node copies its GPU result out to the CPU to send it, and the segmentation node that receives it copies it back up to the GPU. With camera images flowing at dozens per second, the copying alone takes real time.

**NITROS** is how Isaac ROS nodes pass images to each other while keeping them in GPU memory. The effect is most reliable when the nodes share one process (ROS 2 composable nodes). An ordinary ROS node can still listen to the same topic; it receives a normal message, converted once. A mixed graph still works; the speed-up only applies where GPU nodes sit together.

One naming note: from Isaac ROS 5.0 the NITROS packages are gone, and the same keep-it-on-the-GPU idea is built into ROS 2 Lyrical itself (`rosidl::Buffer`), so GPU nodes exchange standard ROS messages. On 3.x and 4.x it's still called NITROS.

## Versions go together as a set

Once you start with Isaac ROS, version numbers multiply. Treat them as one set rather than upgrading pieces separately.

![Upgrade as a set, not one piece at a time](../assets/diagrams_en/r2p4-versions.svg)

**JetPack** is NVIDIA's operating-system bundle for Jetson boards (Linux, GPU drivers, CUDA and so on). ROS 2 sits on top of it and Isaac ROS on top of that, and the three versions have to match. NVIDIA ships containers (Docker development environments) with this combination preinstalled, so pulling one is usually the fastest way to start. It also means everyone on the team works in the same environment.

This series and the Field Notes used JetPack 6 + ROS 2 Humble + Isaac ROS 3.2. Later generations are moving on: Isaac ROS 4.x moved to ROS 2 Jazzy and JetPack 7 (adding the Thor generation), and Isaac ROS 5.0, released in September 2026, moved to Lyrical, the newest ROS 2 long-term support release. The concepts are the same; commands and package names shift a little. If you're starting fresh, pick the newest set available, and upgrade all three together.

## cuMotion, a GPU planner for MoveIt 2's planner slot

Part 3 said MoveIt 2's planner can be swapped. **cuMotion** is NVIDIA's GPU planner for that slot.

![Same inputs, same outputs, only the planner changes](../assets/diagrams_en/r2p4-cumotion-slot.svg)

Only the way the path is found changes. To use it, you add the cuMotion planning pipeline to the MoveIt config next to OMPL and run the cuMotion node alongside. Where OMPL tries candidates one at a time, cuMotion tries and refines many at once on the GPU. With nvblox it can also turn camera depth into obstacles for planning (a planning aid, not a way to protect people). In my [Field Notes](jetson-isaac-foundation-models.md), it planned one path for a 7-axis arm in about 210 ms on an Orin NX 16GB. The number depends on the scene and settings, but it gives a sense that even an edge computer reaches practical speed.

To use cuMotion, each robot needs one more file.

![Collision checks simplified to a few dozen spheres](../assets/diagrams_en/r2p4-xrdf.svg)

**XRDF** is a file that supplements the URDF, and its main part is a collision model that approximates each link of the robot with a set of spheres. Collision checks between complex 3D shapes are slow, but distances between spheres are very fast to compute, which is what lets the GPU filter so many candidates quickly. Link pairs allowed to touch, tool frames, and joint acceleration and jerk (how abruptly acceleration changes) limits go in the same file. NVIDIA's documentation includes a UR10e example, and other robots can be built with the robot description editor in Isaac Sim. If a model looks similar but its link dimensions differ, refit the spheres instead of reusing an existing file.

## Perception results pass through a gate

[Part 1](ros2-for-robot-programmers.md) said the verdict stays with deterministic hardware and perception is used only to adapt the motion. This gate is where the two meet.

![Pass: apply the correction. Fail: stop loudly](../assets/diagrams_en/r2p4-gate.svg)

Neural-network perception wobbles a little with lighting and reflections, so don't take its result at face value; check two things. Is the model's confidence, or its fit error (the distance left over after fitting the CAD), within the threshold? And is the result inside the tolerance stack-up range from [Part 3](moveit2-goals-not-points.md)? If it's outside, either perception is wrong or the part really is somewhere odd, so stop and report instead of carrying on quietly. A quiet failure is more dangerous than a loud one.

Results can wobble in two more places. Even with the same model, rebuilding the TensorRT engine can change its internal choices and shift results very slightly, so pin the engine files as part of the version set and, when you change them, compare against old results using the rosbag2 recordings from [Part 2](ros2-robot-description.md). cuMotion also optimizes from several random starting points, so the same request can give slightly different paths. When you need the same shape every time, use Pilz or a stored trajectory from Part 3.

## One stack, many robots

Does practice on mock hardware or a desktop teaching arm (like the five-joint kind mentioned in Part 3) carry over to a factory robot?

![Change robots and the upper layers stay put](../assets/diagrams_en/r2p4-one-stack.svg)

It does. Most of the code you write, such as the task sequence, vision, frames, goal poses and grasp points, stays the same when the robot changes. What you swap is Part 2's blueprint (URDF) and driver (ros2_control hardware interface), and Part 3's MoveIt configuration. UR provides the three as the `ur_description`, `ur_robot_driver` and `ur_moveit_config` packages, with the External Control URCap installed on the controller (URCap on PolyScope 5, URCapX on PolyScope X). FANUC publishes official ROS 2 description, driver and MoveIt configuration packages as well (`fanuc_description`, `fanuc_driver`, `fanuc_moveit_config`). To keep the swap this small, don't hard-code robot names or joint numbers into your own code.

## Six traps almost every newcomer hits

Finally, the traps from this series in one place, plus two you'll meet when you move to real hardware.

![Six common traps, and how to check](../assets/diagrams_en/r2p4-traps.svg)

Most of the debugging time in the first few weeks goes into these six boxes. The first four came up in [Part 1](ros2-for-robot-programmers.md) and [Part 2](ros2-robot-description.md), and "wrong frame" includes Part 2's timing trap (not using the transform from the moment the picture was taken). A port conflict looks like this: leave the camera maker's setup tool open while starting the ROS camera driver, or have a pendant-side tool and the ROS driver try to hold the same robot connection at once, and one of them fails to open the device with an unhelpful error. Contact forces in simulation are only approximate, and real robots have calibration errors a simulator doesn't know about, so start real robots at low speed (as in T1 on a pendant) with the e-stop within reach.

---

## The whole series on one page

![From camera to controller: what each part covered](../assets/diagrams_en/r2p4-series-map.svg)

| What you did on the pendant | In ROS 2 | Where |
|---|---|---|
| One program | A graph of nodes | Part 1 |
| Signals, registers, `CALL` | Topics, services, actions | Part 1 |
| The controller's built-in robot model | URDF | Part 2 |
| UFRAME · UTOOL | TF2 / the TF tree | Part 2 |
| Motion engine + external command port | ros2_control (controller + hardware interface) | Part 2 |
| ROBOGUIDE · URSim | Mock hardware | Part 2 |
| The pendant's 3D view | RViz | Part 2 |
| Teaching via points | Giving move_group a goal | Part 3 |
| CONFIG | Choosing the IK answer | Part 3 |
| J · L · C | Pilz PTP · LIN · CIRC | Part 3 |
| Jogging | MoveIt Servo | Part 3 |
| Interference zones | The planning scene (safety stays on the controller) | Part 3 |
| Vision offset (VOFFSET) | Taught path + offset (still valid, ladder rung 2) | Part 3 |
| Pass/fail verdict | Unchanged: sensors, gauges, PLC interlocks (perception only adapts motion, through a gate) | Parts 1, 4 |
| (Perception and planning, slow on a CPU) | Isaac ROS · NITROS · cuMotion | Part 4 |

Leave "moving safely" on the robot controller where it was, and let programs from many companies talk to each other to compute only the "where and how" a person used to teach: that's what all four parts were about. Experience with a teach pendant stays useful. People who already understand frames and tools, motion types and safety pick up ROS much faster.

### Where to read next

Read them in this order; each builds on the one before. Pick the documentation for the version you use (e.g. Humble).

1. **ROS 2 tutorials** (docs.ros.org): nodes, topics, launch, TF2
2. **MoveIt 2 tutorials** (moveit.picknik.ai): planning, the planning scene, Pilz
3. **Universal Robots ROS 2 driver documentation** (docs.universal-robots.com): URSim, External Control, force mode
4. **FANUC ROS 2 driver** (FANUC-CORPORATION/fanuc_driver): connecting a FANUC
5. **Isaac ROS documentation** (nvidia-isaac-ros.github.io): GPU packages, NITROS, cuMotion, XRDF

---

**Series** · [← Previous: Part 3 — MoveIt 2](moveit2-goals-not-points.md)

*Related: [Choosing a Physical AI Approach — Track 0, A, B](choosing-physical-ai.md) · [Part 3 — MoveIt 2](moveit2-goals-not-points.md) · [Putting the Robot's Brain on the Edge (2) — Isaac ROS and Foundation Models](jetson-isaac-foundation-models.md) · [Inside the Three Models](inside-the-models.md)*

### Sources and notices

Isaac ROS's structure, NITROS, cuMotion and its MoveIt 2 plugin, the contents of XRDF, and the versions each release targets (3.2 Humble / JetPack 6, 4.x Jazzy / JetPack 7, 5.0 ROS 2 Lyrical with NITROS folded into ROS 2) follow NVIDIA's official Isaac ROS documentation and release notes. The 210 ms figure was measured first-hand in the [Field Notes](jetson-isaac-foundation-models.md) and varies with scene, settings and version. The UR packages and External Control (URCap/URCapX) follow the Universal Robots ROS 2 driver documentation; the FANUC driver refers to FANUC Corporation's `fanuc_driver` repository. ROS is a trademark of Open Source Robotics Foundation (Open Robotics); MoveIt of PickNik Inc.; NVIDIA, Isaac ROS, Isaac Sim, Jetson, Orin, Thor, JetPack, TensorRT, CUDA, cuMotion and nvblox of NVIDIA Corporation; Docker of Docker, Inc.; Linux of Linus Torvalds; Pilz of Pilz GmbH & Co. KG; SAM of Meta; FANUC and ROBOGUIDE of FANUC Corporation; Universal Robots, UR, URSim, URCaps and PolyScope of Universal Robots A/S (a Teradyne company). They are used here only to refer to those products.

### Glossary

- *Isaac ROS*: NVIDIA's set of ROS 2 packages that do heavy computation on the GPU
- *GPU*: a graphics processor that handles huge numbers of identical calculations at once
- *TensorRT · engine build*: NVIDIA's tool for running neural networks fast on a GPU · converting a model for that GPU in advance
- *NITROS*: in Isaac ROS 3.x and 4.x, how nodes pass data while it stays in GPU memory; from 5.0 replaced by a built-in ROS 2 Lyrical feature
- *Composable node*: the ROS 2 way of running several nodes inside one process
- *JetPack*: NVIDIA's operating-system bundle for Jetson boards (Linux, GPU drivers, CUDA and more)
- *Container*: a way of packaging a whole software environment so it runs identically on any computer (Docker)
- *cuMotion*: NVIDIA's GPU motion planner that plugs into MoveIt 2's planner slot
- *XRDF*: a file supplementing the URDF for cuMotion: collision spheres, self-collision rules, tool frames, acceleration and jerk limits
- *URCap · URCapX*: add-ons installed on the UR pendant (PolyScope 5 · PolyScope X)
- *Gate*: the step that checks a perception result's confidence and stack-up range before it is used for motion
- *Confidence · fit error*: the model's own certainty score · the distance left after fitting the CAD
- *frame_id*: the name attached to a ROS message saying which frame it is relative to
