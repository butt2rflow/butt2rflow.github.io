// Hand gestures from the glove's hand IMU (phone page). No DOM, so node can test it (sensor-glove/src/test_gesture_js.mjs).
// Gestures are fixed; what each one DOES is set by the user on the page (a command phrase run through voice.js, or
// "listen"). Every gesture is only taken after ~1 s without big motion, and only acted on after the hand is calm
// again for 0.4 s, so a swing, a waggle or walking shouldn't fire one. A swing (hand faster than 1200 deg/s with a
// forearm IMU, 800 without one; or the forearm IMU faster than 400 deg/s) locks gestures out for 2 s.
//   tap2  : two sharp knocks on the back of the hand (accel jump > 1.2 g vs ~5 ms back), 0.10-0.45 s apart
//           (the firmware uses 1.5 g; at 240 Hz a knock's peak can fall between samples, one made-up knock read 1.24 g)
//   hold  : hold a taught pose still for 1 s (gravity within 25 deg of the taught direction, < 25 deg/s)
//   twist : twist the wrist back and forth quickly: one gyro axis crosses +-400 deg/s with alternating sign 3+ times in 1 s
//           (300 let a firm 350 deg/s waggle through; with only the hand IMU a waggle and a twist differ only in size)
//   shake : shake the hand: one accel axis (gravity removed) crosses +-1.5 g with alternating sign 3+ times in 0.8 s
//   dial  : turn the wrist one way like a dial, out of >= 0.4 s of calm: the rotation (as a 3D vector, so the IMU's angle on the
//           glove doesn't matter) reaches >= 90 deg in 0.25-1.0 s (Jae's turns 110-193 deg; a 72 deg hand turn between range shots was a false dial at 60) with a peak >= 300 deg/s (Jae's real turns: 440-850 deg/s, 0.3-0.8 s;
//           a slow 105 deg hand turn after a swing, 170 deg/s over 1.3 s, was a false dial at 150 / 1.5), the net turn is >= 50 % of the
//           turning path (real dials 0.59-0.96 with a bounce-back; swings 0.07-0.24; a twist ~0), accel within 1.5 g of 1 g, then settled (< 80 deg/s) for 0.15 s.
//           Reports dir (+1/-1 along the glove's turn axis, learnt from the first dial; the page maps it to clockwise) and
//           steps (1 per ~150 deg, at most 3). It skips the 1.5 s cool-down so club changes can follow each other.
//   tap4  : four knocks in a row (each 0.10-0.45 s after the last; the run ends 0.5 s after the last knock, so two knocks
//           = tap2, four = tap4, three or five = nothing). The page uses tap4 to switch club-change mode on and off.
// Club-change mode (2026-11-13, Jae; replaces the one-shot dial for the club): after startClubMode() the wrist turn away
// from where it was when the mode began works like a jog dial. The turn is followed along the learnt dial axis (gyro
// integrated, its bias taken in the first 0.25 s): stepping starts past 25 deg and stops under 15 deg (no flicking at the edge); up to 50 deg steps one club every 0.9 s;
// 50-90 deg every 0.45 s; over 90 deg every 0.2 s; the sign picks next/previous ("clubstep" events). Turning back under
// 15 deg stops. A swing or 20 s with no movement ends the mode ("clubmode" with on:false); tap4 again ends it on the page.
// While the mode is on, only tap4 is recognised.
// Frame = [t_s, hand gx gy gz (deg/s), hand ax ay az (g), arm gx gy gz, arm ax ay az] (same as swing.js).

export const GESTURES = ["tap2", "tap4", "hold", "twist", "shake", "dial"];

export class GestureDetector {
  constructor(onGesture, opts = {}) {
    this.on = onGesture;
    this.enabled = { tap2: true, tap4: true, hold: true, twist: true, shake: true, dial: true, ...(opts.enabled || {}) };
    this.holdRef = opts.holdRef || null;           // unit gravity vector of the taught pose, or null (hold off)
    this.armOk = !!opts.armOk;
    this.hist = [];                                  // ~0.1 s of frames for the tap "5 ms back" check
    this.lastBusy = -Infinity; this.lock = -Infinity; this.cool = -Infinity;
    this.taps = []; this.gyroX = [null, null, null]; this.accX = [null, null, null];
    this.lp = null; this.cand = null; this.calmSince = null;
    this.busyStart = -Infinity; this.preCalm = 0;     // start of the current motion, and how long it was calm before it
    this.holdSince = null; this.holdArmed = true; this.last = null;
    this.dl = null; this.prevT = null; this.handLock = -Infinity; this.dialAxis = opts.dialAxis || null;   // dial in progress; swing lock from the hand IMU only
    this.dialLog = [];                              // last few dial checks, accepted or not, with the reason (for tuning on a real glove)
    this.onDialNote = opts.onDialNote || null;      // page hook: keep each check beyond this page's life
    this.mode = null;                               // club-change mode state, or null
  }
  startClubMode(t) { this.mode = { t0: t, ang: [0, 0, 0], biasSum: [0, 0, 0], biasN: 0, lastStep: -Infinity, lastAny: -Infinity, on: false, wait: 0, lastAct: t }; this.dl = null; }
  stopClubMode() { this.mode = null; }
  clubMode(t, g, gm, dt) {
    const M = this.mode;
    if (gm > (this.armOk ? 1200 : 800)) { this.mode = null; this.on({ name: "clubmode", on: false, why: "swing", t }); return; }
    if (t - M.t0 < 0.25) { if (gm < 30) { for (let k = 0; k < 3; k++) M.biasSum[k] += g[k]; M.biasN++; } return; }
    for (let k = 0; k < 3; k++) M.ang[k] += (g[k] - (M.biasN ? M.biasSum[k] / M.biasN : 0)) * dt;
    const mag = Math.hypot(...M.ang);
    if (!this.dialAxis && mag > 25) {                 // no axis learnt yet: the first clear turn sets it (largest component positive)
      const u = M.ang.map((x) => x / mag), big = u.reduce((m, x, k) => (Math.abs(x) > Math.abs(u[m]) ? k : m), 0);
      this.dialAxis = u.map((x) => x * Math.sign(u[big]));
    }
    const th = this.dialAxis ? M.ang[0] * this.dialAxis[0] + M.ang[1] * this.dialAxis[1] + M.ang[2] * this.dialAxis[2] : 0, a = Math.abs(th);
    // stepping starts past 25 deg and stops under 15 deg, so a wrist resting near the edge doesn't flick the club
    // back and forth (first real try, 2026-11-13: -,+,-,+ at 20-21 deg); re-starting within 0.6 s of the last step waits
    if (!M.on && a >= 25) { M.on = true; M.lastStep = -Infinity; M.wait = M.lastAny + 0.6; }
    else if (M.on && a < 15) M.on = false;
    const every = !M.on ? null : a < 50 ? 0.9 : a < 90 ? 0.45 : 0.2;
    if (gm > 30) M.lastAct = t;
    if (every !== null && t >= M.wait && t - M.lastStep >= every) { M.lastStep = t; M.lastAny = t; M.lastAct = t; this.on({ name: "clubstep", dir: th > 0 ? 1 : -1, deg: Math.round(th), t }); }
    if (t - M.lastAct > 20) { this.mode = null; this.on({ name: "clubmode", on: false, why: "idle", t }); }
  }
  setHoldRef(v) { const n = Math.hypot(...v); this.holdRef = n ? v.map((x) => x / n) : null; }

  frame(f) {
    const t = f[0], g = [f[1], f[2], f[3]], a = [f[4], f[5], f[6]];
    const gm = Math.hypot(...g), am = Math.hypot(...a);
    if (this.lastBusy === -Infinity) this.lastBusy = t;   // the stream's start doesn't count as calm
    const armFast = this.armOk && Math.hypot(f[7], f[8], f[9]) > 400;
    if (gm > (this.armOk ? 1200 : 800) || armFast) { this.lock = t + 2; this.cand = null; this.taps = []; }
    // the dial is a forearm roll, so the forearm IMU races past 400 deg/s on every dial; only the hand lock applies to it
    if (gm > (this.armOk ? 1200 : 800)) this.handLock = t + 2;
    const busy = gm > 150 || Math.abs(am - 1) > 0.35;
    const quietFor = t - this.lastBusy;               // calm time BEFORE this frame
    // gravity estimate (slow low-pass) for the shake check
    if (!this.lp) this.lp = a.slice(); else for (let k = 0; k < 3; k++) this.lp[k] += 0.02 * (a[k] - this.lp[k]);
    this.hist.push(f); while (this.hist.length && this.hist[0][0] < t - 0.1) this.hist.shift();
    const open = t >= this.lock && t >= this.cool;
    const dt = this.prevT === null ? 0 : Math.min(0.05, t - this.prevT); this.prevT = t;
    if (this.mode) this.clubMode(t, g, gm, dt);

    // dial: its own small state machine, so a candidate of another gesture doesn't block it. The rotation is followed as a
    // 3D vector because the hand IMU sits at an angle on the glove: a real wrist turn showed up split between x and z
    // (e.g. +122 / -98 deg, 2026-11-13), so "one gyro axis" rejected every turn.
    if (this.enabled.dial && t >= this.handLock && !this.mode) {
      if (!this.dl) {
        if (gm > 60 && quietFor >= 0.4) this.dl = { t0: t, tEnd: t, ang: [0, 0, 0], path: 0, peak: 0, accDev: 0, calm: null };
        else if (gm > 300 && quietFor < 0.4 && t - (this.noCalmAt || -9) > 1.5) {   // a fast turn that started without a pause: log it for tuning
          this.noCalmAt = t; this.dialLog.push({ why: `no pause before (calm ${quietFor.toFixed(2)} s, needs 0.4)`, peak: Math.round(gm) });
          if (this.dialLog.length > 12) this.dialLog.shift();
          if (this.onDialNote) this.onDialNote(this.dialLog[this.dialLog.length - 1]);
        }
      } else {
        const d = this.dl;
        for (let k = 0; k < 3; k++) d.ang[k] += g[k] * dt;
        d.path += gm * dt; d.peak = Math.max(d.peak, gm); d.accDev = Math.max(d.accDev, Math.abs(am - 1));
        if (gm < 80) { if (d.calm === null) d.calm = t; } else { d.calm = null; d.tEnd = t; }   // a hand held in the air drifts ~20-40 deg/s; after a turn it settles slower
        if (t - d.t0 > 2.0) { this.dialNote(d, "too long (no stop within 2 s)"); this.dl = null; }
        else if (d.calm !== null && t - d.calm >= 0.15) {
          const mag = Math.hypot(...d.ang), straight = d.path ? mag / d.path : 0, dur = d.tEnd - d.t0;
          this.dl = null;
          const why = mag < 90 ? "angle < 90" : d.peak < 300 ? "too slow (peak < 300 deg/s)" : straight < 0.5 ? "not one way (back-and-forth or wobbly)"
            : dur < 0.25 ? "too quick (< 0.25 s)" : dur > 1.0 ? "too long (> 1.0 s)" : d.accDev >= 1.5 ? "too jerky (accel)" : "ok";
          this.dialNote(d, why, dur, straight);
          if (why === "ok") {
            // which way: the sign along the glove's own turn axis. The first dial sets the axis (sign fixed so its largest
            // component is positive, so it doesn't depend on which way that first turn went); later dials refine it.
            const u = d.ang.map((x) => x / mag);
            if (!this.dialAxis) { const big = u.reduce((m, x, k) => (Math.abs(x) > Math.abs(u[m]) ? k : m), 0); this.dialAxis = u.map((x) => x * Math.sign(u[big])); }
            const dot = u[0] * this.dialAxis[0] + u[1] * this.dialAxis[1] + u[2] * this.dialAxis[2], dir = dot >= 0 ? 1 : -1;
            const ax = this.dialAxis.map((x, k) => 0.8 * x + 0.2 * dir * u[k]), n = Math.hypot(...ax); this.dialAxis = ax.map((x) => x / n);
            this.cand = null; this.calmSince = null; this.gyroX = [null, null, null]; this.accX = [null, null, null]; this.taps = [];
            this.last = { name: "dial", t };
            this.on({ name: "dial", t, dir, deg: Math.round(dir * mag), steps: Math.max(1, Math.min(3, Math.floor((mag + 70) / 150))) });
            return;
          }
        }
      }
    } else this.dl = null;

    // a candidate waits for 0.4 s of calm, then fires; big motion meanwhile cancels it
    if (this.cand) {
      if (!open) this.cand = null;
      else if (busy) this.calmSince = null;
      else if (this.calmSince === null) this.calmSince = t;
      else if (t - this.calmSince >= 0.4) this.fire(this.cand.name, t);
    }
    if (busy) { if (quietFor > 0.05) { this.busyStart = t; this.preCalm = quietFor; } this.lastBusy = t; }
    const fromCalm = (t0) => this.preCalm >= 1.0 && t0 - this.busyStart < 0.6;   // began within 0.6 s of leaving >= 1 s of calm
    // a run of knocks ends 0.5 s after the last one: 2 = tap2, 4 = tap4 (in club-change mode only tap4 counts)
    if (this.taps.length && t - this.taps[this.taps.length - 1] > 0.5) {
      const n = this.taps.length; this.taps = [];
      const name = n === 2 ? "tap2" : n === 4 ? "tap4" : null;
      if (name && this.enabled[name] && open && !this.cand && (!this.mode || name === "tap4")) { this.cand = { name, t }; this.calmSince = null; }
    }
    if (!open || this.cand) { this.gyroX = [null, null, null]; this.accX = [null, null, null]; return; }

    // knocks (tap2 / tap4 are decided when the run ends, above)
    if (this.enabled.tap2 || this.enabled.tap4) {
      const old = this.hist.find((h) => h[0] >= t - 0.0055) || this.hist[0];
      const jump = Math.max(...[4, 5, 6].map((j) => Math.abs(f[j] - old[j])));
      if (jump > 1.2 && gm < 400) {
        const prev = this.taps[this.taps.length - 1];
        if (!prev || t - prev > 0.06) {              // one knock rings for ~10-20 ms: count it once
          if (prev && t - prev <= 0.45) { if (t - prev >= 0.10) this.taps.push(t); }
          else if (fromCalm(t) || this.mode) this.taps = [t];   // a run starts out of >= 1 s of calm (in the mode the wrist may have just turned)
        }
      }
    }
    if (this.mode) return;                            // in club-change mode nothing else is recognised
    // shake: gravity-removed accel alternating past +-1.5 g
    if (this.enabled.shake) {
      for (let k = 0; k < 3; k++) {
        const v = a[k] - this.lp[k], s = v > 1.5 ? 1 : v < -1.5 ? -1 : 0;
        const x = this.accX[k];
        if (s && (!x || x.sign !== s)) {
          const cont = x && t - x.t0 < 0.8, list = cont ? x.list.concat([t]) : [t];
          this.accX[k] = { sign: s, t0: list[0], list, ok: cont ? x.ok : fromCalm(t) };
          if (list.length >= 3 && this.accX[k].ok) { this.cand = { name: "shake", t }; this.calmSince = null; return; }
        }
      }
    }
    // twist: one gyro axis alternating past +-300 deg/s, with only moderate accel (else it's a shake)
    if (this.enabled.twist) {
      for (let k = 0; k < 3; k++) {
        const s = g[k] > 400 ? 1 : g[k] < -400 ? -1 : 0, x = this.gyroX[k];
        if (s && (!x || x.sign !== s)) {
          const cont = x && t - x.t0 < 1.0, list = cont ? x.list.concat([t]) : [t];
          this.gyroX[k] = { sign: s, t0: list[0], list, ok: cont ? x.ok : fromCalm(t) };
          if (list.length >= 3 && Math.abs(am - 1) < 2.5 && this.gyroX[k].ok) { this.cand = { name: "twist", t }; this.calmSince = null; return; }
        }
      }
    }
    // hold a taught pose
    if (this.enabled.hold && this.holdRef) {
      const cos = (a[0] * this.holdRef[0] + a[1] * this.holdRef[1] + a[2] * this.holdRef[2]) / (am || 1);
      const near = cos > Math.cos(25 * Math.PI / 180), far = cos < Math.cos(40 * Math.PI / 180);
      if (far) this.holdArmed = true;
      if (near && gm < 25 && Math.abs(am - 1) < 0.15 && this.holdArmed) {
        if (this.holdSince === null) this.holdSince = t;
        else if (t - this.holdSince >= 1.0) { this.holdArmed = false; this.holdSince = null; this.fire("hold", t); }
      } else this.holdSince = null;
    }
  }
  dialNote(d, why, dur = null, straight = null) {
    this.dialLog.push({ why, ang: d.ang.map((x) => Math.round(x)), mag: Math.round(Math.hypot(...d.ang)), peak: Math.round(d.peak),
      dur: dur === null ? null : +dur.toFixed(2), straight: straight === null ? null : +straight.toFixed(2), accDev: +d.accDev.toFixed(2) });
    if (this.dialLog.length > 12) this.dialLog.shift();
    if (this.onDialNote) this.onDialNote(this.dialLog[this.dialLog.length - 1]);
  }
  fire(name, t) {
    this.cand = null; this.calmSince = null; this.cool = t + 1.5; this.last = { name, t };
    this.gyroX = [null, null, null]; this.accX = [null, null, null]; this.taps = [];
    this.on({ name, t });
  }
}
