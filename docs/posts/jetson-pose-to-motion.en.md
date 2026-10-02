---
title: "Putting the Robot's Brain on the Edge — Motion: After the Pose Comes Movement, and an Obstacle Map That Failed Its First Try"
nav_title: "Motion · Planning and the Obstacle Map"
date: 2026-10-02
tags: [physical-ai, jetson, isaac-ros, cumotion, nvblox, moveit2, universal-robots, ros2, edge-ai, field-notes]
lang: en
description: "Once you know the object's pose, the arm has to move. On the same Orin NX 16GB: cuMotion planning (about 186 ms per plan, with a 16-second warm-up only the first time), the nvblox obstacle map (accurate to one 2 cm cell on a scene with a known answer, but the board vanished from the map on the first live-camera try), bringing up the UR ROS 2 driver without a robot, and how far force control goes on this stack. Field Notes, motion."
---

# Putting the Robot's Brain on the Edge — Motion: After the Pose Comes Movement, and an Obstacle Map That Failed Its First Try

> **Field Notes · Motion.** From [the correction post](jetson-foundationpose-16gb.md) to [the scanning post](jetson-scan-no-cad.md), everything was on the camera side: give an instruction in words, find the object, and output its 6-DoF pose (position and orientation). But a pose is just numbers, and the robot hasn't moved an inch. This post records tests of **the side that turns a pose into motion**, on the same edge computer.

The [From Teach Pendant to ROS 2](ros2-for-robot-programmers.md) series covered the concepts: MoveIt 2 and planners in [Part 3](moveit2-goals-not-points.md), the GPU planner cuMotion and the nvblox obstacle map in [Part 4](isaac-ros-gpu.md). This time I ran them on the Orin NX 16GB and checked them **with numbers**. Some worked, and one failed on its first try. The failure is here too.

*(This is a general R&D record on the same Jetson Orin NX 16GB and OAK-D 3D camera as the earlier posts, on an office desk. No real robot moved, and no real force was measured.)*

---

## 30-second summary

- **cuMotion is fast on the edge too.** With the UR10e configuration, a median of about 186 ms per plan. The first plan needs a 16-second GPU warm-up, so do it when the program starts, not on the first pick.
- **nvblox was accurate on a scene with a known answer.** Fed computed depth (a box at 0.6 m, a wall at 1.0 m), the map put them at 0.610 m and 1.000 m, within one 2 cm cell.
- **The first live-camera try failed.** Speed was fine (3.8 ms per depth frame), but the middle of a board 0.39 m away vanished from the map. False far depth readings probably erased it, but that's still a theory.
- **The UR driver comes up without a robot.** On simulated hardware all 13 controllers loaded, force mode included. On this version the argument is `use_fake_hardware`.
- **Force control on this stack means UR force mode.** NVIDIA's learned insertion example is an Isaac ROS 4.x feature; to try it on Orin you need at least Isaac ROS 4.6 and JetPack 7.2.

---

## Three things you need after the pose

Knowing the object's pose doesn't let the robot go and pick it up yet. Three more pieces are needed.

1. **Motion planning:** a collision-free path from the arm's current pose to the front of the object. Here, cuMotion.
2. **An obstacle map:** where the things you must not hit are. What you know from CAD (table, jigs) goes into the planning scene; what you don't (a toolbox someone left, a sagging cable) has to be seen by the camera. Here, nvblox.
3. **A robot driver:** the channel that hands the computed path to the real robot controller. Here, the Universal Robots (UR) ROS 2 driver.

![The four steps after the pose: what was checked and what wasn't](../assets/diagrams_en/mot-status.svg)

The results first: planning worked, the obstacle map half worked, and the driver was checked only in simulation. One at a time.

## cuMotion: a long warm-up once, then short plans

cuMotion is the plugin that puts NVIDIA's GPU motion-planning library, cuRobo, into MoveIt 2. I tested it with the UR10e configuration file that ships with cuRobo, planning five times from different start poses.

![A 16.4-second GPU warm-up once, then about 0.19 s per plan](../assets/diagrams_en/mot-warmup.svg)

| Item | Result |
|---|---|
| GPU warm-up, first time only | 16.4 s |
| One plan | median ~186 ms (61–190 ms) |
| Success | 4 of 5 |
| GPU memory | +0.2 GB peak |

The one failure was a start pose I offset by a large amount on purpose. When planning fails, cuMotion answers "no path found" and the arm doesn't move. It stops rather than handing back a strange path, which is the behaviour you want. Your program can take that answer and retry from another standby pose, or call a person.

The number to use in practice is the **16 seconds**. cuRobo spends a long time preparing its GPU work on the first plan and is fast after that. Plan for the first time when the first part arrives, and only that first cycle is 16 seconds longer. Run any plan once when the program starts and the problem goes away.

I won't put this next to the 210 ms from [Part 2 of the field notes](jetson-isaac-foundation-models.md) (a 7-axis arm, the demo Franka configuration) and call it faster. The arm and the scene are different. What I can say is that both land around 0.2 s on the same edge computer. If you use a different UR model, you need a cuMotion configuration for it (joint limits, collision spheres). UR's MoveIt configuration covers several models, but the cuMotion configuration is separate.

[Part 3](moveit2-goals-not-points.md) covered how to choose a planner, so briefly:

| Planner | What it does | Where to use it |
|---|---|---|
| OMPL (RRT family) | Grows a random tree until it reaches the goal. Finds a path almost anywhere, but it differs each run and can wander | Setup, detours through open space |
| cuMotion | Refines many candidate paths in parallel on the GPU. Smooth and short | Travel through cluttered scenes |
| Pilz | Exact shapes (joint move, straight line, arc) | The last few centimetres before the part |

A common split is **travel with cuMotion or OMPL, final approach with a Pilz straight line**. The Isaac ROS 3.2 environment I installed already had OMPL, Pilz, CHOMP and the cuMotion plugin.

## Start the obstacle map on a scene with a known answer

nvblox takes depth images, divides space into small cubes (voxels), and writes "distance to the nearest surface" into each one (see "What does cuMotion avoid?" in [Part 4](isaac-ros-gpu.md)). I wanted to plug the camera straight in, but tested **a scene with a known answer** first. If the live map looks wrong, you can't tell whether the camera or the setup is at fault.

So I computed a depth image: a box 0.6 m in front of the camera and a wall at 1.0 m. I fed it to nvblox and measured where the two surfaces landed in the map.

![On a computed scene with a known answer, the map landed in place](../assets/diagrams_en/mot-synth.svg)

| Item | Result |
|---|---|
| Box face (truth 0.6 m) | 0.610 m |
| Wall (truth 1.0 m) | 1.000 m |
| Map cell size | 2 cm |
| Time to add one depth frame | ~0.6 ms |
| Map output | ~11 Hz |
| Memory | +0.4 GB |

Both surfaces fell within one cell (2 cm), so it **passed**. That confirms the nvblox settings, the coordinate transform (the robot base frame `base_link`) and the topic wiring. The only variable left is the camera.

## With the live camera, the board disappeared

Now the real camera. I published the OAK-D's stereo depth as a ROS 2 topic and had nvblox build a map from it, with a checkerboard standing 0.39 m in front of the camera.

Speed wasn't a problem. The camera sent 13.5 frames a second, nvblox's map output ran at about 14 Hz, adding one depth frame took 3.8 ms, and memory grew by 0.5 GB. That's enough for the edge computer to keep up.

But the map was wrong.

![Left: the depth the camera measured. Right: the nvblox map built from it, redrawn from the same viewpoint. The middle of the board is empty](../assets/demos/jetson-nvblox-live-compare.png)

*Left is the depth the camera measured; right is the nvblox map redrawn from the same viewpoint (colour is distance, black is no value). The large board in the middle on the left is mostly missing on the right.*

Here is how I checked the map: redraw the map's points from the camera's viewpoint and compare each with the depth the camera measured at that pixel. Only **14 %** of points agreed within 3 cm. If a large plane right in front, like the board, is missing from the map, the planner treats that space as empty and can send the arm through it.

### Why it vanished (still a theory)

The frame's depth statistics hold a clue. 53 % of pixels had valid depth, and the median was 0.41 m, matching the board. But **the top 5 % were beyond 6.9 m**. A camera looking at a desk 0.39 m away shouldn't see anything near 7 m, so those are false readings. The office lighting was dim, and the camera's IR projector (which sprays dots onto featureless surfaces to help stereo) was off.

![One false far reading erases the near board (working theory)](../assets/diagrams_en/mot-carving.svg)

For every depth point, a map like this casts a ray from the camera to that point and **records the cells the ray passes through as empty**. That's how objects you remove get erased from the map. But if a pixel wrongly reads 6.9 m, its ray passes through the board's cells at 0.39 m and marks them "empty here". The correct pixels keep writing "surface here", and the false ones keep erasing it.

It's a plausible explanation, but **I haven't confirmed it yet**. The next test changes three things:

- clip depth at 1.5 m (drop anything beyond the work area)
- turn the lights on
- turn the IR projector on

If clipping alone brings the board back, the theory holds. I'll add the result to this post when I have it.

What to take from this is the check, more than the numbers. nvblox produced a map at 14 Hz with no errors. Judging by speed alone, I'd have believed it worked. One check, redrawing the map from the camera's viewpoint and comparing it with real depth, exposed the problem. If you use an obstacle map, run that check at least once. And as [Part 4](isaac-ros-gpu.md) said, nvblox is not a device for protecting people. Human safety belongs to the robot controller's safety functions and safety sensors.

<details>
<summary>Things that tripped me up while wiring it</summary>

- nvblox doesn't build a map without a `base_link` transform (TF). The depth topic (`/camera_0/depth/image`) and the camera-info topic (`/camera_0/depth/camera_info`) also had to have exactly these names.
- The camera program (DepthAI) and nvblox lived in different Docker containers, so I set both to the same `ROS_DOMAIN_ID` so they could see each other's topics.
- Only one program can hold a USB camera. If the pose-estimation demo has it, stop that first.

</details>

## Bringing up the UR driver without a robot

You can check everything up to the driver without a robot. The UR ROS 2 driver (2.9.0 on ROS 2 Humble here) has ros2_control's **simulated hardware**, which just echoes the commands it receives instead of moving a robot. That's enough to see whether the controllers come up and commands flow.

All **13 controllers** loaded: the joint trajectory controller, plus force mode, freedrive (moving the arm by hand) and tool-contact detection.

One thing caught me. Current docs give the simulated-hardware argument as `use_mock_hardware:=true`, but **the Humble 2.9.0 driver doesn't know that name**. You have to write `use_fake_hardware:=true`. The unknown argument is ignored without an error, and the driver starts with its real-robot setup. If you think you launched on simulated hardware but get robot-connection errors, check this first. From the ROS 2 Jazzy driver onward, the name is `use_mock_hardware`.

![What simulated hardware, URSim and a physics simulator each check](../assets/diagrams_en/mot-where.svg)

Simulated hardware checks only the wiring. To move like a real UR controller you need UR's simulator, **URSim**, and it didn't run on the Orin. There is an arm64 build of the PolyScope X URSim image, but the simulator container it launches inside is x86-only. So URSim runs on an x86 PC on the same network, and the Orin connects to it over the network.

Add a recorded camera stream (a ROS bag) and you can run the whole flow **with no camera and no robot**: the recording gives the pose, cuMotion plans, and the virtual UR in URSim moves. Neither of these simulates force or contact, though. That takes a physics simulator (Isaac Sim, with an RTX GPU) or a real robot.

## How far force control goes now

The last few millimetres, where a part is pressed or inserted, are usually handled by force control rather than path planning ([Part 3](moveit2-goals-not-points.md)). On this stack, what's available is the UR controller's own force mode.

![UR force mode compared with NVIDIA's learned insertion](../assets/diagrams_en/mot-force.svg)

Through the ROS 2 driver's force-mode controller you pass a reference frame, the axes that should comply (move with the force), a target force and speed limits; the force control itself runs inside the UR controller. It amounts to calling URScript's `force_mode()` from ROS 2. This time I only checked that the controller loads.

From Isaac ROS 4.0, NVIDIA has shipped a **learned gear-insertion** example: a policy trained with reinforcement learning in simulation drives the arm directly through the UR10e's low-level torque interface. It isn't in Isaac ROS 3.2, which I used. Isaac ROS 4.x only started supporting Orin with 4.6 in August 2026, so trying it on Orin means moving the whole stack to at least Isaac ROS 4.6 and JetPack 7.2 (Ubuntu 24.04, ROS 2 Jazzy). I haven't checked whether the example then works on Orin as is. Following [Part 4](isaac-ros-gpu.md)'s rule of changing versions as one set, I saw no reason to rush while the current chain works end to end.

## A few rows missing from Part 4's table

The "whole series on one page" table in [Part 4](isaac-ros-gpu.md) mapped J, L and C moves, teaching and interference zones to ROS 2. Looking into the driver this time filled in a few rows it didn't have. There's no automatic converter from pendant programs to ROS 2, so you port by hand with a table like this.

| Pendant / URScript | ROS 2 side |
|---|---|
| Blending (`movel` radius), FANUC `CNT` | Pilz motion sequence (several moves chained into one request) |
| Digital outputs (`set_digital_out`, `DO[]`) | The UR driver's IO controller service |
| `force_mode()`, FANUC force control | The force-mode controller |
| Stop on contact (FANUC `SKIP`) | The tool-contact controller |
| Taught points (Euler angles, UR rotation vector) | Convert to quaternions, or re-teach |

The last row takes more work than it looks. FANUC writes orientation as W·P·R Euler angles and UR as a rotation vector (axis and angle), while ROS uses quaternions. The conversion formulas are fixed, but get one angle order or reference frame wrong and the tool points somewhere else. Check ported points on simulated hardware or URSim first.

In the bigger picture, "taught point + vision offset" becomes **"object pose from the foundation model + a pre-grasp approach offset"**, with cuMotion planning the path in between around obstacles from the nvblox map. But as the automation ladder in [Part 3](moveit2-goals-not-points.md) showed, when the variation is small, a taught path with an offset is still simpler and more predictable.

## Summary

| Step | Result | Next |
|---|---|---|
| cuMotion planning | ~186 ms per plan; 16 s warm-up only the first time | Warm up at program start; write the cuMotion config for the UR model you'll use |
| nvblox (known-answer scene) | Both surfaces within one 2 cm cell | — |
| nvblox (live camera) | Fast enough, but the board's middle vanished (14 % agreement) | Retry with depth clipped at 1.5 m, lights on, IR projector on |
| UR driver (simulated hardware) | All 13 controllers, force mode included | Whole flow with URSim and a ROS bag on an x86 PC |
| Force control | UR force mode works on this stack | Measure force on a real robot |

- **Planning runs at working speed on the edge.** Just move the 16-second warm-up out of the cycle.
- **Test an obstacle map on a scene with a known answer first.** Then, when it's wrong live, you can narrow the problem to the camera.
- **Fast is not the same as right.** One check, redrawing the map from the camera's viewpoint and comparing it with real depth, exposed this failure.
- **Each kind of fake checks something different.** Simulated hardware checks the wiring, URSim checks controller behaviour, and a physics simulator or a real robot checks force and contact.

---

<details>
<summary>Notes: where these results come from</summary>

The numbers were **measured directly** on a Jetson Orin NX 16GB with an OAK-D 3D camera on 1 October 2026 (Isaac ROS 3.2, ROS 2 Humble, JetPack 6). cuMotion was timed over five plans with cuRobo's UR10e configuration file; the live nvblox result is the first try on one scene in one session. The cause of the failure is written up as an unconfirmed theory. No real robot moved and no real force was measured.

The learned gear-insertion example and the UR10e low-level torque interface are based on NVIDIA's technical blog post "Bridging the Sim-to-Real Gap for Industrial Robotic Assembly Applications Using NVIDIA Isaac Lab" and the Isaac ROS 4.0 announcement. Orin and JetPack 7.2 support in Isaac ROS 4.6.0 (18 August 2026) is from the Isaac ROS release notes. The `use_fake_hardware` (Humble) vs `use_mock_hardware` (Jazzy) difference is from the Universal Robots ROS 2 driver documentation (docs.ros.org).

NVIDIA, Jetson, Orin, JetPack, Isaac ROS, Isaac Sim, cuMotion, cuRobo, nvblox and RTX are trademarks of NVIDIA Corporation; OAK-D and DepthAI of Luxonis; Universal Robots, UR, UR10e, URSim and PolyScope of Universal Robots A/S; FANUC of FANUC Corporation; MoveIt of PickNik Inc.; ROS of Open Robotics; Pilz of Pilz GmbH & Co. KG; Docker of Docker, Inc. They are used for identification only.

</details>

**Series** · [← Previous: Scanning — No CAD? One Printed Board and Twenty Photos](jetson-scan-no-cad.md)

*Related: [From Teach Pendant to ROS 2 (3) — MoveIt 2](moveit2-goals-not-points.md) · [From Teach Pendant to ROS 2 (4) — Isaac ROS and cuMotion](isaac-ros-gpu.md) · [How Many Cameras, and Where](camera-placement.md) · [Hands-on Notes (0) — SO-101 and URSim](learn-without-industrial-robot.md)*
