---
title: "From Teach Pendant to ROS 2 (3) — MoveIt 2: Give a Goal Instead of Teaching Points"
nav_title: "Part 3 · MoveIt 2"
date: 2026-09-28
tags: [physical-ai, ros2, moveit2, motion-planning, robotics, fanuc, universal-robots]
lang: en
description: "First, whether you need path planning at all (the automation ladder, tolerance stack-up, VOFFSET); then MoveIt 2, which computes the path from a goal. move_group, IK and FANUC's CONFIG, the planning scene and where safety stays, J and L moves with Pilz, and the five steps from camera to grasp. Part 3 of 4."
---

# From Teach Pendant to ROS 2 (3) — MoveIt 2: Give a Goal Instead of Teaching Points

> **From Teach Pendant to ROS 2 · Part 3 of 4.** [Part 1](ros2-for-robot-programmers.md) covered ROS 2's wiring and [Part 2](ros2-robot-description.md) how to describe a robot to ROS. This part is MoveIt 2, which sends the robot to a goal. [Part 4](isaac-ros-gpu.md) covers Isaac ROS and cuMotion.

If you've written a TP program that goes around a fixture to reach a part, you've probably added a few via points. P[2] up and to the left of the fixture, P[3] right above it, P[4] up and to the right. A person decides in their head how the robot should get around, then teaches those points one by one.

When the part arrives in the same place every time, that's the most reliable way to do it. When a camera finds the part somewhere different every time, it isn't. You can't re-teach via points on every cycle.

![Same fixture, two approaches](../assets/diagrams_en/r2p3-teach-vs-goal.svg)

**MoveIt 2** works the way shown on the right. Give it a goal, and it computes how the robot should get around.

---

## The 30-second version

- MoveIt 2's central node, **move_group**, takes the current joint state, a goal pose and the obstacles, produces a **collision-free trajectory**, and hands it to the ros2_control controller as an action.
- Turning a tool pose into joint angles is **IK (inverse kinematics)**. There can be several answers, and FANUC's CONFIG is exactly the record of which one.
- MoveIt 2 avoids only the objects you've put in the **planning scene**. Safety for people and equipment is still the job of the robot controller's safety configuration.
- Motion types are the ones you know: **joint moves (J, movej)**, **straight-line moves (L, movel)** and **arcs (C, movec)**. MoveIt 2's Pilz planner does them as PTP, LIN and CIRC.
- Path planning isn't always the answer. Parts always in the same place: taught points. Flat variation: taught path + offset (VOFFSET). Height and tilt vary too: MoveIt 2. When the same request must give the same path, use Pilz or a stored trajectory.
- From camera to grasp takes five steps: **detect → convert → grasp point → plan → execute**.

---

## First: do you really need path planning?

![Climb one rung only when you have to](../assets/diagrams_en/r2p3-ladder.svg)

The rule is to use the lowest rung that works. If the part always arrives in the same place, rung 1 (a jig plus taught points) is the most reliable and gives the same result every time. The trouble starts when small variations stack up.

![Each is small; added up, they miss the taught point](../assets/diagrams_en/r2p3-stackup.svg)

Even with a fixed fixture, pallet, conveyor and product tolerances (allowed dimensional errors) add up to more than a single taught point can absorb. The expected range of that sum is the **tolerance stack-up**. Define it in advance and any result outside it can be caught and stopped at the gate in [Part 4](isaac-ros-gpu.md). The fix a TP programmer already knows is rung 2: vision measures this cycle's offset and the whole taught path is shifted by it (FANUC's VOFFSET or a PR offset). The path's shape is the same every time and only its position moves, so the motion adapts to the variation and stays predictable. Climb to rung 3, MoveIt 2, when height and tilt vary too, or when the shifted path could hit nearby equipment.

On every rung, the pass/fail verdict stays with the existing measurement hardware (sensors, gauges, PLC interlocks), as in [Part 1](ros2-for-robot-programmers.md). Rung 4, a learned policy (an AI trained on demonstrations that decides the motion), is for tasks that can't be written as coordinates (routing a cable, say); because it carries on without reporting its own failure, it doesn't suit test cells and this series doesn't cover it.

## move_group, three inputs in and one trajectory out

At the center of MoveIt 2 is a node called `move_group`, the one that showed up in `ros2 node list` in Part 1.

![Three inputs in, one trajectory out](../assets/diagrams_en/r2p3-move-group.svg)

The three inputs and three steps in the picture are the whole story. The current joint state comes from the `/joint_states` topic seen in Part 1, and the resulting trajectory goes to Part 2's controller through the action from Part 1.

For this, each robot has a **MoveIt configuration package**. It says which joints are planned together as one arm (planning groups), which link pairs sit against each other and can skip collision checks, and which planner to use by default. Makers often ship one; if not, a tool called the MoveIt Setup Assistant builds one from the blueprint.

There are two ways to try it. In RViz's motion planning panel you drag a goal into place with the mouse and press "Plan" and "Execute." Or you call it from code: `MoveGroupInterface` in C++, and there is a Python API (MoveItPy, installable on Humble as `ros-humble-moveit-py`). Its Humble examples are thin and the API changed in later releases, so the RViz panel is the easier way to get a feel for it first.

## IK, one tool pose and several joint answers

To put the tool tip at a given position and orientation, how many degrees should each of the six joints be? That calculation is **inverse kinematics (IK)**. Going from joint angles to the tool pose (forward kinematics) has one answer, but going the other way can have several.

![IK: one tool pose, several joint answers](../assets/diagrams_en/r2p3-ik.svg)

FANUC programmers already know this. The CONFIG attached to position data (a notation like N U T, 0, 0, 0) records which of these answers you mean. With a different CONFIG, the tool can be in the same place while the arm takes a completely different shape. MoveIt 2 usually picks the answer closest to the current joint state, and you can steer it by limiting the range of particular joints.

Sometimes there's no answer at all: the goal is out of reach or past a joint limit. Small teaching arms with only five joints lack the freedom to match both position and orientation at once, so they're often set up to hit the position exactly and the orientation only approximately.

## The planning scene, and where safety stays

The list of obstacles MoveIt 2 plans around is the **planning scene**: the robot itself (Part 2's blueprint) plus the objects you've told it about, like the table, fixture and part.

![MoveIt 2 avoids only what you told it about](../assets/diagrams_en/r2p3-scene.svg)

If someone puts a box on the table and nobody adds it to the planning scene, MoveIt 2 will calmly plan a path straight through it. So fixed equipment goes into the blueprint or a scene file, and moving objects are seen by the camera and filled into the scene (this is for planning, not for detecting people). In a cell that must give the same result every time, keep fixed equipment at measured values as in [Part 2](ros2-robot-description.md) and use the camera map for checking.

And the planning scene is **for planning paths**, not a safety device. The speed limits, work-area limits, and people detection and stopping you configure in FANUC DCS or the UR safety settings remain the job of the robot controller and safety equipment when you use ROS. Copying your interference zones into MoveIt 2 is no reason to delete the safety settings on the robot controller.

## Joint moves and straight-line moves don't change

The motion types are exactly the ones you use on the pendant.

![The tool tip traces a different line](../assets/diagrams_en/r2p3-joint-vs-line.svg)

MoveIt 2 lets you plug in different ways of finding paths (planners). **OMPL**, widely used by default, finds any collision-free path, whatever its shape, which is good for getting around in open space; because it draws candidates at random, though, the default setup produces a different path for the same request every time. If you want the fixed shapes of an industrial robot, the **Pilz** planner does PTP (joint move), LIN (straight line) and CIRC (arc) directly. Both check for collisions, but only OMPL goes around obstacles; Pilz computes the fixed shape and rejects the whole plan if it collides.

Straight-line moves come with one condition: there has to be an IK answer at every point along the line. If the line passes a joint limit or a singularity (a pose, such as a fully stretched arm, where some directions become impossible), it breaks off partway. MoveIt 2's straight-line path calculation reports how much of the line it could plan; anything short of 100% means part of it is unreachable. It's the same thing as an L move alarming near a singularity in TP.

## Keeping motion predictable

Part 1 said motion may differ every cycle, but it should still be predictable. A robot whose cycle time jumps around, or that swings left today and right tomorrow, is hard to trust on the floor. Approaches differ in whether the same request gives the same path.

| Approach | Same path for the same request? | Where to use it |
|---|---|---|
| Taught path + offset (rung 2) | Same shape, only shifted | When the variation stays in the plane |
| Pilz PTP · LIN · CIRC | Yes (fixed shapes) | Approaching and leaving the part |
| A path planned once, validated and stored | Yes | Long moves repeated every cycle |
| OMPL (default setup) | No (random) | Setup, getting around obstacles |
| cuMotion | May vary slightly (random starts) | Crowded scenes, fast planning ([Part 4](isaac-ros-gpu.md)) |

The start pose matters too. IK usually picks the answer closest to the current joint state, so starting every cycle from the same home position keeps the arm's shape on the same side.

## Five steps from camera to grasp

Put the pieces so far together and you have one vision-picking cycle.

![From "I see it" to "I've got it"](../assets/diagrams_en/r2p3-loop.svg)

1. **Detect.** Vision finds the part. The result is a position relative to the camera.
2. **Convert.** TF2 restates it relative to the base, using the transform from the moment the picture was taken, as in Part 2.
3. **Grasp point.** Add "where on the part, and in which direction, to grip it" to the part pose. Like UTOOL in TP, keep this as a frame or a setting rather than a number buried in the code, so that changing grippers doesn't touch anything else.
4. **Plan.** Go above the part, straight down, grip, straight up.
5. **Execute.** The trajectory goes through ros2_control to the robot controller.

If the gripper misses by a few centimeters, check steps 1 and 2 (noted under the picture) before suspecting the robot.

Seen from the side, step 4 looks almost exactly like a TP pick program.

![Fast up high, straight up close](../assets/diagrams_en/r2p3-approach.svg)

The one difference is that P[2] and P[3] are computed every time instead of taught. Written as code it looks like this. (This is concept code showing the flow, not real API names.)

```python
part = wait_for_message("/part_pose")                  # 1 detect (camera frame)
part_in_base = tf.transform(part, "base_link",
                            at=part.header.stamp)      # 2 convert at the picture's time
grasp = part_in_base * grasp_offset                    # 3 grasp point (a setting, like UTOOL)
above = offset_z(grasp, 0.10)                          #   10 cm above = TP's P[2]

plan_and_run(above)                                    # 4 joint move (J)
plan_and_run(grasp, straight_line=True)                #   straight down (L)
gripper.close()                                        #   gripper service (DO[1]=ON)
plan_and_run(above, straight_line=True)                #   straight up (L)
```

When the last few millimeters involve pressing or inserting the part, force control often takes over from path planning. On a UR, the driver's force-mode controller calls URScript's `force_mode()` (the [motion post](jetson-pose-to-motion.md) confirmed the controller comes up); on a FANUC, force control is built into the controller. Each robot does it differently, so follow the maker's documentation here.

To follow a moving target or nudge the arm little by little, the way you'd jog it from the pendant, use **MoveIt Servo** instead of "plan, then execute." It keeps sending small motion commands in real time.

---

## Summary

| Concept | What it does | On the pendant, roughly |
|---|---|---|
| **Automation ladder** | Lowest rung first: jig → 2D offset → 3D pose | Teaching → VOFFSET → (new) |
| **move_group** | current joint state + goal + obstacles → trajectory | The path you used to plan in your head |
| **IK** | tool pose → joint angles; may have several answers | FANUC's CONFIG choice |
| **Planning scene** | The objects path planning avoids | Interference zones (but not a safety function) |
| **OMPL** | Any collision-free path, any shape | (none) |
| **Pilz PTP · LIN · CIRC** | Moves with a fixed shape | J · L · C, movej · movel · movec |
| **Five steps** | detect → convert → grasp point → plan → execute | Vision offset + pick program |
| **MoveIt Servo** | Small real-time motions | Jogging |
| **Stored trajectory** | Reuse a validated path every cycle | A taught path |

One concern remains. Step 1's perception has to run a neural network on every picture, which is slow, and in a crowded cell planning takes time too. [The last part](isaac-ros-gpu.md) looks at NVIDIA's Isaac ROS and cuMotion, which move these slow parts onto the GPU.

---

**Series** · [← Previous: Part 2 — Describing the Robot to ROS](ros2-robot-description.md) · [Next: Part 4 — Isaac ROS and cuMotion →](isaac-ros-gpu.md)

*Related: [Choosing a Physical AI Approach](choosing-physical-ai.md) · [Part 2 — Describing the Robot to ROS](ros2-robot-description.md) · [From Stereo to Grasp](stereo-to-grasp.md) · [UR vs FANUC — openness](cobot-ur-vs-fanuc.md)*

### Sources and notices

The behavior of move_group, the planning scene, OMPL, the Pilz industrial motion planner (PTP, LIN, CIRC), the achieved fraction of Cartesian paths, MoveItPy and MoveIt Servo follows the official MoveIt 2 documentation (moveit.picknik.ai). FANUC's CONFIG and DCS and UR's safety settings and force mode refer to each maker's public material. The code is concept code showing the flow, not a real API. ROS is a trademark of Open Source Robotics Foundation (Open Robotics); MoveIt of PickNik Inc.; Pilz of Pilz GmbH & Co. KG; NVIDIA, Isaac ROS and cuMotion of NVIDIA Corporation; FANUC of FANUC Corporation; Universal Robots and UR of Universal Robots A/S (a Teradyne company). They are used here only to refer to those products.

### Glossary

- *MoveIt 2*: ROS 2's motion planning framework; give it a goal and it computes a collision-free trajectory
- *move_group*: MoveIt 2's central node
- *IK (inverse kinematics)*: turning a tool position and orientation into joint angles; there may be several answers or none
- *Forward kinematics*: working out the tool pose from joint angles; one answer
- *CONFIG*: the notation on FANUC position data recording which IK answer is meant
- *Planning scene*: the objects MoveIt 2 avoids when planning
- *Planner*: a method for finding paths; OMPL (any shape), Pilz (PTP, LIN, CIRC) and others plug in
- *Singularity*: a pose, such as a fully stretched arm, where some directions of motion become impossible
- *MoveIt Servo*: sends small motion commands in real time, without planning
- *Automation ladder*: jig → 2D vision + offset → 3D pose from CAD → learned policy; use the lowest rung that works
- *Tolerance · stack-up*: allowed dimensional error · the expected range when several tolerances add up
- *VOFFSET · PR offset*: FANUC features that shift a taught path by the offset vision measured
- *Stored trajectory*: a path planned once, validated and reused every cycle
- *Force control (force mode)*: moving to push with a set force rather than to a position
