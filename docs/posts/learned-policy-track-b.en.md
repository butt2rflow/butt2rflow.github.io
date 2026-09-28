---
title: "Learned Policies (Track B) — Robots That Copy What You Show Them, and Where That Breaks"
date: 2026-09-28
tags: [physical-ai, imitation-learning, robotics, act, lerobot, deterministic]
lang: en
description: "Learned policies let a robot learn tasks a person can show but nobody can write as coordinates. Teaching vs demonstrating, how a policy learns and outputs action chunks, why the data is the quality, quiet failure outside what it learned, the fixed safety layer, real-time ports on industrial arms, and its use in a cell whose verdict must repeat."
---

# Learned Policies (Track B) — Robots That Copy What You Show Them, and Where That Breaks

> **Physical AI · Track B.** [Choosing a Physical AI Approach](choosing-physical-ai.md) put three designs on one axis. This post is about the far right end, step 4 of the staircase: learned policies. Step 3 below it is Track 0/A, where geometry or a neural network finds the part's pose and a planner computes the path.

Imagine writing a TP program that routes a cable into a fixture's groove. The cable bends a little differently every time, and you have to push it in by feel. A handful of points can't capture that. Yet ask a person to show it and anyone can do it in a few seconds.

**Learned policies** (models trained to choose the next move from camera images and joint state) are built for exactly this kind of work: things you can show but can't write as coordinates. They come at a cost worth knowing up front.

---

## The 30-second version

- Teaching records points and replays them exactly; demonstration shows the whole motion so the robot can produce motion in similar new situations.
- A person moves a control arm (the leader), the working arm copies it while joint angles and images are recorded, and a policy is trained on dozens of such demos. Policies like ACT output upcoming actions as a **chunk** at once.
- The data is the quality. If the policy misbehaves, fix the demos before the model.
- Outside what the demos covered it falls apart, with no built-in failure signal. So every command must pass through a fixed safety layer.
- On industrial arms a real-time control port comes first, and a new arm usually means new demonstrations and fine-tuning.
- In a cell whose verdict must repeat, give it only the last few millimeters, and let sensors decide the verdict.

---

## Teaching and demonstrating are different

![Teaching replays points; demonstration generalizes a motion](../assets/diagrams_en/tpb-teach-vs-demo.svg)

TP teaching makes the robot replay, exactly, the points a person chose. Demonstration means a person shows the whole motion several times. Instead of memorizing points, the learned policy looks at the current image to decide the next move, so it can produce a fitting motion even when the object sits a little differently. It needs no camera-to-robot calibration, but the camera has to stay where it was during the demos.

## How a policy learns

![Show, record, train, run](../assets/diagrams_en/tpb-pipeline.svg)

Learning from human demonstrations like this is called **imitation learning**. The leader arm is a control arm a person moves by hand, and the follower arm copies it in real time. One demonstration is one episode, and a single task typically gets dozens of episodes. Tools such as Hugging Face's LeRobot tie recording, training and running into one flow.

![A short segment at once, not one step](../assets/diagrams_en/tpb-chunk.svg)

The widely used ACT (Action Chunking with Transformers) does what its name says: it outputs actions in chunks. Deciding one instant at a time lets small errors pile up until the robot drifts into situations it never saw; deciding several instants at once means fewer decisions and less piling up. Blending the overlapping chunks also smooths out the jumps where one chunk hands over to the next.

## The data is the quality

![If the policy misbehaves, fix the demos before the model](../assets/diagrams_en/tpb-data.svg)

Most of the work with learned policies is data cleanup. Show it going around an obstacle sometimes on the left and sometimes on the right, for example, and a simple model averages the two and heads straight into the middle. Failed demos have to go, and when a policy moves strangely, rewatch the demonstrations before touching the model settings.

## Outside what it learned

![Trust it only where the demos reached](../assets/diagrams_en/tpb-coverage.svg)

It works well within the range where objects sat during the demos, under that lighting and camera position, and falls apart beyond it; that's the biggest weakness of learned policies. Situations the training data didn't cover are called **out of distribution**. The problem is that it falls apart **without a signal**: the quiet failure from [Choosing a Physical AI Approach](choosing-physical-ai.md). Unlike step 3, where the planner reports "no path", the policy has no mechanism for judging reachability and can keep producing plausible-looking motion; working out why it fails means digging back through the demo data.

## A fixed safety layer under the policy

![Whatever the policy outputs, a fixed layer enforces the limits](../assets/diagrams_en/tpb-safety.svg)

Because a policy can produce plausible-looking commands of any kind outside what it learned, a fixed, non-learned layer has to filter them once more. Run the policy only in reduced-speed mode or behind guarding, with someone watching who can hit the e-stop. This software layer is a guard rail, not a certified safety function; the controller's rated safety settings and risk assessment remain what protects people.

## On industrial arms, a real-time port comes first

![A policy streams commands dozens of times a second. Is there a port?](../assets/diagrams_en/tpb-interfaces.svg)

A planned path from step 3 only needs a goal pose, so any arm can follow it, even through its own robot language. A learned policy sends new joint targets every instant, so the robot needs a port that accepts commands from outside in real time. UR has one built in; FANUC needs an option such as Stream Motion. [UR vs FANUC](cobot-ur-vs-fanuc.md) covers each maker's openness.

Switching arms isn't simple either. A policy trained on one arm generally can't just be loaded onto another. Large models trained on many different arms exist, but a new arm still usually needs its own demonstrations and additional training (fine-tuning). To collect demos on a large arm, a small leader arm modeled on the target arm gives cleaner data than dragging the big arm by hand.

## If the verdict must repeat every cycle

![The policy owns a narrow segment; sensors own the verdict](../assets/diagrams_en/tpb-in-a-cell.svg)

In a place like a test cell, where pass/fail must come out the same every time, the learned policy owns **one narrow segment**, not the whole cell. A narrow scope is what makes acceptance by N trials per condition possible. [Pendant to ROS 2, Part 1](ros2-for-robot-programmers.md) goes into separating motion from the verdict.

## When to use it, and when not to

![When you can show it but can't write it down](../assets/diagrams_en/tpb-when.svg)

The rule is the staircase from [Choosing a Physical AI Approach](choosing-physical-ai.md). Learned policies are for what the three steps below can't solve: work a person can show but nobody can write as coordinates.

The much-discussed VLA (vision-language-action) models belong to the same family: large policies that take natural-language instructions and handle many tasks. They do broader work, but they still don't report their own failures and still need a fixed safety layer.

---

## Summary

| Concept | In one line |
|---|---|
| **Learned policy** | A model trained on demonstrations to output the next motion from camera images and joint state |
| **Demonstration · episode** | A motion a person shows with a leader arm · one recording of it |
| **Action chunk (ACT)** | Outputs several instants at once to limit error build-up, and blends overlaps for smoothness |
| **Data is quality** | Inconsistent demos, mixed approaches and failed demos become the policy's flaws |
| **Out of distribution** | Falls apart when position, lighting or camera change, and can carry on without a signal |
| **Fixed safety layer** | A non-learned layer enforcing joint, speed and workspace limits on every command; not a certified safety function |
| **Real-time port** | A prerequisite for streamed policies on industrial arms; a new arm usually needs new demos and fine-tuning |
| **Use in a cell** | A narrow segment only; sensors decide the verdict; acceptance by N-trial statistics |

---

**Series** · [← Choosing a Physical AI Approach](choosing-physical-ai.md)

*Related: [Pendant to ROS 2, Part 1](ros2-for-robot-programmers.md) · [UR vs FANUC (openness)](cobot-ur-vs-fanuc.md) · [Why Robots Learn in a 'Fake World' First](robot-simulation.md)*

### Sources and notices

ACT, action chunking and the blending of overlapping chunks follow Zhao et al., "Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware" (RSS 2023, arXiv:2304.13705); leader/follower recording and the training flow follow the Hugging Face LeRobot documentation; the small leader arm modeled on a large arm follows GELLO (Wu et al., 2023). Training across many arms refers to work such as Open X-Embodiment. Real-time interfaces on industrial arms refer to each maker's public material; command rates and option names vary by model and version, so check the maker's documentation. The failure behaviors describe expected tendencies. Hugging Face and LeRobot are trademarks of Hugging Face, Inc.; FANUC of FANUC Corporation; Universal Robots and UR of Universal Robots A/S (a Teradyne company); Franka of Franka Robotics GmbH; ABB of ABB Ltd; KUKA of KUKA SE & Co. KGaA. RTDE, FCI, Stream Motion, EGM and RSI are product names of their respective makers. They are used here only to refer to those products.

### Glossary

- *Learned policy*: a model trained to output robot motion from camera images and joint state
- *Imitation learning*: learning motions by watching human demonstrations
- *Leader arm · follower arm*: a control arm a person moves by hand · the real working arm that copies it
- *Episode*: one recorded demonstration (joint angles + camera images)
- *ACT (Action Chunking with Transformers)*: an imitation-learning policy that predicts actions in chunks of several instants
- *Out of distribution*: a situation the training data didn't cover, where learned policies fall apart
- *Fixed safety layer*: a layer of non-learned rules that checks commands and clamps them to the limits or stops
- *Real-time port (streaming interface)*: a channel through which an outside computer keeps sending joint targets to the robot at a short interval
- *Fine-tuning*: training an already-trained model a little more on new data
- *VLA (vision-language-action)*: a large learned policy that takes images and natural-language instructions and outputs motion
