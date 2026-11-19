---
title: "Why I Used LTX for the Robot Arm and H3 for the Classroom"
nav_title: "LTX and H3 on an RTX 3090"
date: 2026-11-19
tags: [rtx-3090, video-generation, ltx-2-5, minimax-h3, flux, codex]
lang: en
description: "Making a promo on one RTX 3090 came down to watching the foot of a robot arm and the space above the kids’ heads. LTX kept the first frame remarkably well. That helped in one shot and got in the way in the other."
---

# Why I Used LTX for the Robot Arm and H3 for the Classroom

Watch the edge of the desk as the robot arm moves. The clamp that’s supposed to hold the black arm down stays put. The base of the arm quietly slides away from it. I spotted this in a MiniMax H3 shot while making a promo for my robotics course.

## The 30-second version

- For the robot shot (S06), I removed a stray clamp and corrected the shape of the base in the opening image. When LTX-2.5 animated it, the base stayed put.
- The same fidelity worked against me in the classroom (S11). LTX kept the kids’ heads right up against the edge of the projection screen. I kept the H3 take.
- On my RTX 3090, about six seconds of video took roughly 30–55 seconds with LTX and 2–10 minutes with H3. Those were execution times for the two workflows I used for the promo.

## The base was already wrong in the drawing

There are two arms in S06. A person moves the black leader arm and the white follower copies the motion. The joints can turn, but both bases should stay planted on the desk. I gave H3 a motion reference video. In all three takes, the base pulled away from the clamp. The desk edge makes a handy fixed point to watch.

<video muted loop playsinline controls preload="metadata" poster="../../../assets/ltx-vs-h3/s06-original-comparison-poster.jpg" src="../../../assets/ltx-vs-h3/s06-original-comparison.mp4" style="width:100%" aria-label="Original S06 comparison"></video>

*H3 is on the left and LTX-2.5 is on the right. Watch the base against the desk edge. The people are AI-generated illustrations.*

LTX followed the opening image closely, so I went back to the drawing before asking for another move. I used FLUX to erase the stray C-clamp. When I animated that frame with LTX, the black base held its position. Once it sat still, I could see what else was wrong. The real bases are the same part in different colors. The black one in the drawing had a skinny post and a long, thin foot.

On the first repair I masked the black base and asked FLUX to redraw it. I got the same post and foot, plus a pale rectangle at the front of the desk. For the second try, I had the part I needed right there in the picture. I cut out the white base, turned it black and lined it up in perspective under the black arm. I patched the desk and used FLUX to blend the base into its surroundings. The host ran the generation job, and Codex helped inspect the new opening frame. Every pixel outside the repair mask matched the original.

<img alt="Repaired S06 opening frame" src="../../../assets/ltx-vs-h3/s06-repaired-first-frame.jpg">

*I fitted the shape of the white base under the black leader arm. The people are AI-generated illustrations.*

<video muted loop playsinline controls preload="metadata" poster="../../../assets/ltx-vs-h3/s06-final-ltx-poster.jpg" src="../../../assets/ltx-vs-h3/s06-final-ltx.mp4" style="width:100%" aria-label="Final S06 take with LTX-2.5"></video>

*The black base stays planted on the desk as the arm moves. The people are AI-generated illustrations.*

I ran that frame through LTX again. The black base stayed planted while the arm moved. That’s the take I put into version seven of the promo.

## Why keep H3 for the classroom?

In the classroom, watch the space above the kids’ heads. In the opening image, the children’s heads overlapped the edge of the projection screen behind them. Starting from the same picture, LTX carried that overlap into the shot. I liked the framing in the H3 take better.

<img alt="S11 classroom comparison" src="../../../assets/ltx-vs-h3/s11-comparison.jpg">

*Both frames are from the same moment. H3 is on top and LTX-2.5 (seed 19) is below. The circles in the lower frame mark where the children’s heads overlap the screen edge. The people are AI-generated illustrations.*

I tried fixing this drawing too. A masked edit made the heads easier to see, but added an odd yellow panel. An edit using a reference image gave the kids crowns. I kept the existing H3 classroom shot in v7.

## Two shots on one 3090

For the initial comparison, both models got the same opening image for each scene, and I ran three seeds with LTX. Its GPU memory use peaked at about 23 GB for these roughly six-second clips. H3 took about ten minutes on the arm with the motion reference and about two on the classroom. The resolutions and generation settings also differed. The timings tell me how long another take would cost on my machine.

Next time I make a robot shot, I’ll look at the two bases side by side in the still. For a classroom, I’ll look for lines running behind the kids’ heads. Once the drawing is ready, picking the take gets easier if I know exactly where to look when the picture starts to move.

**Related** [How Claude and Codex share one RTX 3090](ai-workbench-routing.md) · [Let a local AI do the reading](local-llm-reading.md)
