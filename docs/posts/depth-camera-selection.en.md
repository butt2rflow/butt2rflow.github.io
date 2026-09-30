---
title: "Which Depth Camera — From Mount Position to Distance, From Distance to Camera"
nav_title: "Which Depth Camera"
date: 2026-09-30
tags: [physical-ai, robot-vision, camera, depth-camera, stereo, realsense, orbbec, luxonis]
lang: en
description: "Pick a robot's depth camera by where it's mounted and how far away the object is, not by the maximum range on the spec sheet. The two distance limits of stereo cameras, whether colour and depth come from the same sensor, plain and shiny surfaces, five close-range cameras side by side (D405, Gemini 305/305g, OAK-D SR), choosing for a larger arm, and what to check once the camera arrives."
---

# Which Depth Camera — From Mount Position to Distance, From Distance to Camera

> **Robot Vision · design choices.** [How Many Cameras, and Where](camera-placement.md) settled how many cameras to use and where they go. This post picks **which depth camera** to put there.

On a depth camera's spec sheet the eye goes first to numbers like "up to 10 m" and "1280×800". Pick a camera for a robot's wrist by those numbers and you'll often get it wrong. A wrist camera sees the object at roughly 15–40 cm, and the cameras that see farthest often give no depth at all at that distance. Turn the order around: decide where the camera goes and how far the object will be from there, then pick a camera that suits that distance.

---

## 30-second summary

- Choose in this order: **mount position → distance to the object → a camera whose recommended range includes that distance.** Resolution and precision come after.
- A stereo camera **gives no depth when the object is too close, and its error grows with the square of distance as it moves away.** Cameras with the two lenses close together are strong up close; widely spaced lenses are strong far away.
- Cameras that take colour and depth from the **same sensor** (D405, OAK-D SR) have no alignment problem. A separate colour camera adds an alignment step, and that's where things drift.
- For close wrist work the candidates are the **RealSense D405 and the Orbbec Gemini 305**. The 305 fills the same slot as the D405, sees closer in its close-range preset (4–5 cm) and costs less.
- Whatever you buy, **check that camera's characteristics yourself.** Units of the same model differ.

---

## Mount position → distance → camera

![Distance before resolution](../assets/diagrams_en/dcs-order.svg)

The mount position sets how far the camera is from the object.

- A **wrist or gripper camera** moves with the arm and approaches the object. Just before the grasp, the object is about 15–40 cm away. A short-range camera that holds that whole distance (D405, Gemini 305, 7–50 cm ideal) fits, and it sees the grasp area in detail.
- An **overhead camera** looks down from 50 cm to over 1 m above the table. Put a short-range camera there and it's past its 50 cm upper limit, so there's no depth. Use a mid-range camera with a wide field of view (D435, D455) to see the whole work area in one image.

One camera rarely does both jobs, which is why manipulation kits often ship with both a gripper camera and an external camera. A learned policy that uses only colour images works with either, but a pipeline that computes the object's pose from depth needs a short-range camera on the wrist.

**Example: a wrist camera on a desktop arm.** As the gripper approaches a block, the distance is 15–40 cm. The D405's recommended range of 7–50 cm holds all of it. The D435's recommended range starts at 30 cm, so depth quality drops in the 15–25 cm just before the grasp. Put a short-range camera like the D405 on the wrist and send the D435 overhead.

## The two distance limits of a stereo camera

Stereo cameras such as RealSense, OAK and ZED work like a pair of eyes. They find the same point in the left and right images, measure how many pixels it has shifted (the **disparity**), and turn that shift into distance. Hold a finger in front of your nose and close one eye, then the other: the finger jumps a lot, a distant hill barely moves. Near things have large disparity, far things small. Both limits come from this ([Inside the Three Models](inside-the-models.md) covers the stereo principle in more depth).

- **The near limit.** The camera chip searches disparity only up to a fixed maximum. If the object is so close that its disparity exceeds that, the depth is simply empty. This distance is the **minimum distance (min-Z)**.
- **The far limit.** Farther away the disparity shrinks, so even a sub-pixel matching error becomes a large distance error. Double the distance and the depth error grows about four times.

The distance between the two lenses is the **baseline**. A short baseline is precise up close and weak far away; a long one is the reverse.

![Short baseline up close, long baseline far away](../assets/diagrams_en/dcs-error.svg)

The blue line is the D405, with an 18 mm baseline. It gives depth from 7 cm, with about 0.4 mm error at 20 cm, but reaches about 1 cm at 1 m. The yellow line is the OAK-D Pro, with a 75 mm baseline. Its error is only about 1.2 mm even at 1 m, but at default settings it gives no depth inside about 80 cm. Lowering the resolution and widening the disparity search brings it to about 20 cm (dashed), at the cost of far range. A disparity shift, which moves the search window, works the same way. It lets a long-baseline camera work a little closer; it doesn't turn it into a short-range camera.

<details>
<summary>The formulas</summary>

Depth Z comes from the focal length f (pixels), the baseline B and the disparity d:

Z = f·B / d

- **Minimum distance:** min-Z = f·B / d_max. For the D405 (848×480, 18 mm baseline, d_max 126) this works out to about 7 cm, matching the datasheet.
- **Far error:** ΔZ ≈ Z²·Δd / (f·B). With a sub-pixel matching precision Δd of 0.08 px, the D405 is about 0.4 mm off at 20 cm and about 1 cm at 1 m; the OAK-D Pro (800P) is about 1.2 mm at 1 m.

Vendors quote a slightly more generous practical figure than the calculation. The chart and the figures above are approximate.

</details>

So when you read a spec sheet, look at the **recommended range, not the maximum**. The datasheet's broad range (7 cm–1 m for the D405) is where depth "comes out"; the range accurate enough for manipulation is narrower.

![Only short-range cameras hold the whole 15–40 cm](../assets/diagrams_en/dcs-ranges.svg)

## Do colour and depth come from the same sensor?

Depth alone rarely tells you which pixels are the part, so the usual approach is to find the object in the colour image and cut out its depth. For that, colour and depth have to point at the same pixels.

![If there's an alignment step, that's where the bugs live](../assets/diagrams_en/dcs-alignment.svg)

On the D405, Gemini 305, OAK-D SR and ZED, one of the stereo sensors also captures the colour image. Colour and depth share pixels from the start, so there's nothing to align. The OAK-D and OAK-D Pro have a separate colour camera between a mono stereo pair. Moving depth into the colour camera's view needs the factory-measured position of one sensor relative to the other (the extrinsics), and that step is where problems appear.

1. **Edges don't line up.** The mono and colour sensors sit a few centimetres apart, so object edges get depth holes or bleeding, worse up close. Cut depth with a segmentation mask and background depth leaks in at the mask boundary, skewing the pose.
2. **Autofocus makes alignment drift.** The colour camera's lens parameters used for alignment hold only at the focus position they were calibrated at. When autofocus moves the lens, the misalignment changes with distance.
3. **The capture moments differ.** A global shutter captures the frame at once, a rolling shutter line by line, so the two sensors capture slightly different instants. On a camera moving with the arm, colour and depth show different moments.
4. **Resolution and cropping differ.** If the camera crops or scales the colour image differently from how it was calibrated, alignment is off.

If you must use a model with a separate colour camera: lock the focus (or order the fixed-focus model) before calibrating, keep the colour resolution the same as during calibration, capture with the robot stopped, and shrink mask edges by a few pixels before using their depth. Running segmentation and pose on the mono image removes the alignment step altogether.

## Plain and shiny surfaces

Stereo matches left and right points using surface texture. On single-colour parts or a white table there's nothing to match, so the **depth has holes**. Cameras that project their own light suffer less, but each kind of light has its own weak spot.

![Each depth type fails somewhere different](../assets/diagrams_en/dcs-surfaces.svg)

- **Passive stereo** (D405, Gemini 305, OAK-D SR over USB) projects nothing. Plain surfaces get holes; shiny surfaces get gaps or wrong depth.
- **Stereo with an IR dot projector** (D435, D455, OAK-D Pro) sprays an invisible dot pattern that gives plain surfaces texture. Much better on plain surfaces, but on mirror-like reflections it can lock onto the wrong depth.
- **Time-of-flight (ToF)** (OAK-D SR PoE, Orbbec Femto Bolt) sends infrared light and times its return at every pixel. No matching is needed, so plain surfaces get depth too. It struggles in strong sunlight, and on shiny metal the light bounces off a second surface before returning, so the part reads farther away than it is, with no sign that anything went wrong.

With passive stereo, put texture stickers or a patterned mat on the parts and table, use low-angle light to bring out surface grain, or add an external pattern projector. Render-and-compare pose methods such as FoundationPose work with partial depth. Neural stereo can fill the holes, but the filled values are estimates. In the mirror-cup test in [the tuning post](jetson-tuning-licensing.md), neural stereo filled in the depth of the pattern reflected in the cup and was quietly wrong. Compare it with measured depth before trusting it for precise poses.

## Close-range cameras side by side

For a camera within half a metre of the part, the field narrows. The D405 and Gemini 305 see closest (7–50 cm ideal); the OAK-D SR starts at 20–30 cm but runs AI on the camera itself.

| Model | Depth accuracy | Weight | Power + data | Sealing | AI on camera | List price (USD) |
|---|---|---|---|---|---|---|
| RealSense D405 | ±2% at 50 cm | 60 g | USB-C | Not rated | No | 272 |
| Orbbec Gemini 305 | ±1.8% at 50 cm | 68 g | USB-C | IP54 | No | 229 |
| Orbbec Gemini 305g | ±1.8% at 50 cm | 116 g | GMSL2 coax (12 V + data), USB-C | IP65 | No | 279 |
| Luxonis OAK-D SR | Not published | 72 g | USB | Not rated | Yes (1.4 TOPS) | 329 |
| Luxonis OAK-D SR PoE | ToF <1% indoors, <2% outdoors | Not confirmed | PoE (M12) | IP67 | Yes | 479 |

*Prices are the vendors' store list prices on 30 September 2026, before tax and shipping, and may change.*

How to choose:

- **A USB cable to the wrist is fine:** Gemini 305 or D405. Same size, same baseline (18 mm), and both take colour and depth from the same sensor. The 305 is slightly more accurate (±1.8% vs ±2%), is dust- and splash-rated (IP54, with its cable screwed in) and costs less. Its minimum distance depends on the setting: 9 cm at 1280×800 and 6 cm at 848×530 by default, down to 5 cm and 4 cm in the close-range preset that widens the disparity search to 256. That preset draws more power (1.57 W → 1.88 W) and lowers the maximum operating temperature from 45 °C to 40 °C. It's new (January 2026), and its ROS 2 driver (OrbbecSDK_ROS2) supports it from v2.7.2. Most NVIDIA Isaac ROS examples assume RealSense, so expect to adapt them.
- **The cable flexes every time the arm moves:** Gemini 305g. GMSL2 is a thin coax standard used in vehicles and robots, built to survive bending, and it carries power and data on one cable. The host needs a GMSL2 input; bench-test over USB-C. The 305g isn't a 305 with a module bolted on; it's a separate one-piece model with a GMSL2 serializer built in (FAKRA and SMB connector versions). Optics and depth performance match the 305, and depth grows from 23 mm to 40 mm (about 53 mm with the FAKRA connector). USB-C is for evaluation and setup; in operation it runs on 12 V over GMSL2. Orbbec ships compiled drivers for Jetson AGX Orin-series developer kits, so on any other board, confirm the GMSL2 capture board and driver combination first.
- **Dust or splashing water on site:** the 305g again. The D405 and D435 have no dust or water rating, and their USB connectors don't lock. RealSense's sealed model is the D457 (IP65, GMSL2), but it shares the D455's 95 mm baseline, so its minimum distance is 52 cm (0.6–6 m ideal): right for overhead, wrong for a close wrist. You can put a D405 in a housing, but the front window adds refraction and reflections, so recalibrate and check with the window in place. If it has to survive high-pressure washdown, look at IP67 (OAK-D SR PoE, ZED X Mini).
- **Detection has to run on the camera, with no host GPU:** OAK-D SR. Mount it beyond its near limit (about 20–30 cm).
- **Lots of shiny metal parts:** don't use ToF as the main depth source (the multipath problem above). With passive models, plan texture or lighting.

Both Gemini 305 models are passive stereo with no IR projector, and the datasheet itself says depth should be evaluated on textured objects, so plan lighting for plain surfaces. Check the packaging when buying: the boxed unit includes a 1 m USB-C cable and a guide; bulk is the camera only. Supply is worth watching too: RealSense spun out of Intel in July 2025, and in September 2026 Cognex announced it would acquire the company. Product lines and prices may change, so if you're buying several, pick a fallback candidate.

## On a larger arm

The camera-to-object distance is set by **tool length and where the camera is mounted**, not by the robot's size. A 20 kg-payload collaborative arm (about 1.7 m reach) carries a larger, longer gripper, so the wrist camera ends up farther from the object. The order is the same: mount position, distance, camera.

**Example.** The gripper is about 25 cm long, the camera sits behind the flange (the plate the tool mounts to), and the arm pauses 20–40 cm above the part before grasping. Camera-to-part distance is then about 40–70 cm.

| Camera | Recommended range | At 40–70 cm |
|---|---|---|
| RealSense D405 | 7–50 cm | Partly. The far end is past its range, and error rises fast beyond 60 cm |
| Luxonis OAK-D SR | 0.3–1 m | The whole range fits |
| Luxonis OAK-D Pro | ~0.8 m+ by default | Too close at default settings |
| Stereolabs ZED X Mini | 0.1–8 m | Fits; global shutter and IP67, but the GMSL2 host has to be supported |

The OAK-D SR has a lot going for it on a large arm. Colour and depth come from the same sensor, so there's no alignment step; fixed focus keeps the lens parameters steady; and a global shutter doesn't smear during fast moves. The PoE model (OAK ToF) adds long cable runs and ToF depth. With a 20 mm baseline, though, error near 1 m is centimetre-level, so use it to find the part roughly and finish with contact, force sensing or mechanical guides.

For the ZED X family, check the host first. Depth is computed on the host's NVIDIA GPU, and the GMSL2 capture-card driver supports only specific carrier boards. Seeed reComputer carriers aren't on the list, and there are reports of the camera not being detected. It works on NVIDIA developer kits and Stereolabs' ZED Box. The documented minimum for the neural depth modes is 0.3 m, so treat the 0.1 m lens figure with care.

## Once it arrives: check your camera first

A spec sheet gives the model's typical values. The unit you actually receive behaves differently per resolution mode, per calibration state and per focus type. The camera in [the scanning post](jetson-scan-no-cad.md) put every distance 5.6 % short because of the default lens parameters for its 1080p mode, had stereo rectification 1.9 px off vertically, and changed its focal length by 3.3 % up close because of autofocus. None of it produced an error message. When a new camera arrives, check three things before real work:

1. **Lens parameters:** in the resolution mode you'll use, put a board of known size at several distances and compare the distance computed from the lens parameters with the stereo distance. With fixed focus, the error should stay the same at every distance.
2. **Stereo rectification:** in the rectified left and right images, matching points should sit within 0.5 px vertically.
3. **Focus:** with an autofocus camera, find the distance where the factory values hold, and **don't get closer than that.** If you have to work closer, use a fixed-focus model.

Write the result as one line, "this camera is within ○ % from ○ to ○ cm". That's the camera's real recommended range.

## What to check when buying

- **Specify fixed focus.** Autofocus moves the lens parameters (webcams, phones, autofocus OAK models). Luxonis sells fixed-focus versions to order.
- **Compare the working distance with the recommended range, not the maximum.** If you shift the search window to see closer, account for the shorter far range.
- **On Luxonis, don't combine a disparity shift with on-camera alignment.** depthai-core has an open known limitation that RGB-depth alignment doesn't work with a disparity shift enabled (issue #831). If you need both, check the alignment yourself.
- **If depth will be cut with a segmentation mask, choose a model with colour and depth on the same sensor** (D405, Gemini 305, OAK-D SR, ZED).
- **For many plain or shiny parts,** look at a projector (D435, OAK-D Pro), ToF, or, for millimetre-level matching, a structured-light industrial camera (Zivid, Photoneo and others).
- **Choose the software too.** RealSense uses librealsense/realsense-ros, Orbbec uses OrbbecSDK_ROS2, Luxonis uses DepthAI/depthai-ros, Stereolabs uses the ZED SDK (needs an NVIDIA GPU). Mix them in one cell or one classroom and troubleshooting splits into several paths.
- **On-camera AI** (Luxonis) matters when there's no host PC and power is tight. With a GPU host it adds little.
- **In an industrial cell,** start with the dust and water rating (305g IP65 for a close wrist, D457 IP65 overhead, IP67 for washdown). Where the cable flexes every cycle, a locking connector and a flex-rated cable (GMSL2, M12 PoE) are better, and USB 3 beyond about 3 m needs an active or optical extension. Check the product lifecycle too: for a cell that will run for years, being able to keep buying the same model matters.

## Summary

| Step | What to do |
|---|---|
| 1 | Decide where the camera goes (wrist, overhead) |
| 2 | Measure the distance to the object from there |
| 3 | Pick a camera whose **recommended range** includes it: short baseline for close, long for far |
| 4 | If a mask cuts the depth, check that colour and depth share a sensor |
| 5 | Match the depth type to the part surfaces (plain, shiny) |
| 6 | Check the received camera's lens parameters, rectification and focus yourself |

The D405 is still the default for close wrist work, and the Gemini 305 is a candidate for the same slot that is slightly more accurate and costs less. Either way, trust the numbers you measure on the camera you received over the spec sheet.

---

*Related: [How Many Cameras, and Where](camera-placement.md) · [Scanning post](jetson-scan-no-cad.md) · [Tuning post](jetson-tuning-licensing.md) · [Inside the Three Models](inside-the-models.md) · [From Stereo to Grasp](stereo-to-grasp.md)*

### Sources and notices

Figures follow each vendor's public specs and documentation: [RealSense D400 datasheet (Mar 2026)](https://www.realsenseai.com/wp-content/uploads/2026/03/RealSense-D400-Series-Datasheet-Mar-2026.pdf) · [RealSense camera comparison](https://www.realsenseai.com/stereo-depth/compare/) · [Orbbec Gemini 305](https://www.orbbec.com/gemini-305/) · [Gemini 305 datasheet V1.0 (Jan 2026)](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8888/Orbbec_Gemini-305-Datasheet.pdf) · [Gemini 305 store](https://store.orbbec.com/products/gemini-305) · [Gemini 305g store](https://store.orbbec.com/products/gemini-305g) · [Gemini 305g datasheet V1.0](https://orbbec-debian-repos-aws.s3.amazonaws.com/product/Orbbec_Gemini%20305g%20Datasheet%20V1.0.pdf) · [orbbec_camera (ROS 2)](https://index.ros.org/p/orbbec_camera/) · [Luxonis OAK-D SR](https://docs.luxonis.com/hardware/products/OAK-D%20SR) · [OAK ToF (OAK-D SR PoE)](https://shop.luxonis.com/products/oak-d-sr-poe) · [OAK-D Pro](https://docs.luxonis.com/hardware/products/OAK-D%20Pro) · [Luxonis focus types](https://docs.luxonis.com/hardware/platform/sensors/focus-type) · [Luxonis stereo configuration (disparity shift)](https://docs.luxonis.com/projects/api/en/latest/tutorials/configuring-stereo-depth/) · [depthai-core #831](https://github.com/luxonis/depthai-core/issues/831) · [RealSense D457](https://realsenseai.com/products/d457-gmsl-fakra/) · [Stereolabs ZED X](https://www.stereolabs.com/products/zed-x) · [ZED drivers](https://www.stereolabs.com/developers/drivers) · [ZED depth modes](https://docs.stereolabs.com/docs/depth-sensing/depth-modes.md) · [RealSense spin-out (Jul 2025)](https://www.realsenseai.com/news-insights/news/realsense-completes-spin-out-from-intel-raises-50-million-to-accelerate-ai-powered-vision-for-robotics-and-biometrics/) · [Cognex to acquire RealSense (Sep 2026)](https://www.cognex.com/en/company/press-releases/cognex-to-acquire-realsense). The minimum-distance and error chart values are approximations from Z = f·B/d. Prices and specs change; confirm with the vendor before buying. This is not a product endorsement. RealSense is a trademark of RealSense Inc.; Orbbec, Gemini and Femto of Orbbec Inc.; Luxonis, OAK and DepthAI of Luxonis; ZED of Stereolabs; NVIDIA, Jetson and Isaac ROS of NVIDIA Corporation. They are used for identification only.

### Glossary

- *Depth camera*: a camera that measures, for every pixel, the distance to that point
- *Stereo camera*: a depth camera that computes distance from the shift between two lenses' images
- *Disparity*: how many pixels the same point shifts between the left and right images; larger when closer
- *Baseline*: the distance between a stereo camera's two lenses; short is strong up close, long is strong far away
- *Minimum distance (min-Z)*: the distance closer than which no depth comes out
- *Recommended range*: the distance span where depth is accurate enough for manipulation; narrower than the datasheet's maximum range
- *Lens parameters (intrinsics, K)*: focal length and image centre, used to turn pixels into distance and direction
- *Extrinsics*: the position and orientation of one sensor relative to another (or of the camera relative to the robot)
- *Global shutter / rolling shutter*: capturing the whole frame at once / line by line; a global shutter is better on a moving camera
- *Passive stereo*: stereo that projects no light and relies on surface texture alone
- *IR dot projector*: a device that sprays an invisible infrared dot pattern to give plain surfaces texture
- *Time-of-flight (ToF)*: measuring distance by timing light's round trip
- *Multipath error*: light bouncing off a second surface before returning, so the distance reads farther than it is
- *GMSL2*: a coax camera-link standard used in vehicles and robots; good for long, flexing cable runs
- *PoE*: power over Ethernet, power and data on one Ethernet cable
- *IP54 / IP65 / IP67*: ratings for dust and water resistance; higher numbers resist more
- *Flange*: the plate at the end of a robot arm where a tool such as a gripper mounts
