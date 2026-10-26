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
// Frame = [t_s, hand gx gy gz (deg/s), hand ax ay az (g), arm gx gy gz, arm ax ay az] (same as swing.js).

export const GESTURES = ["tap2", "hold", "twist", "shake"];

export class GestureDetector {
  constructor(onGesture, opts = {}) {
    this.on = onGesture;
    this.enabled = { tap2: true, hold: true, twist: true, shake: true, ...(opts.enabled || {}) };
    this.holdRef = opts.holdRef || null;           // unit gravity vector of the taught pose, or null (hold off)
    this.armOk = !!opts.armOk;
    this.hist = [];                                  // ~0.1 s of frames for the tap "5 ms back" check
    this.lastBusy = -Infinity; this.lock = -Infinity; this.cool = -Infinity;
    this.taps = []; this.gyroX = [null, null, null]; this.accX = [null, null, null];
    this.lp = null; this.cand = null; this.calmSince = null;
    this.busyStart = -Infinity; this.preCalm = 0;     // start of the current motion, and how long it was calm before it
    this.holdSince = null; this.holdArmed = true; this.last = null;
  }
  setHoldRef(v) { const n = Math.hypot(...v); this.holdRef = n ? v.map((x) => x / n) : null; }

  frame(f) {
    const t = f[0], g = [f[1], f[2], f[3]], a = [f[4], f[5], f[6]];
    const gm = Math.hypot(...g), am = Math.hypot(...a);
    if (this.lastBusy === -Infinity) this.lastBusy = t;   // the stream's start doesn't count as calm
    const armFast = this.armOk && Math.hypot(f[7], f[8], f[9]) > 400;
    if (gm > (this.armOk ? 1200 : 800) || armFast) { this.lock = t + 2; this.cand = null; this.taps = []; }
    const busy = gm > 150 || Math.abs(am - 1) > 0.35;
    const quietFor = t - this.lastBusy;               // calm time BEFORE this frame
    // gravity estimate (slow low-pass) for the shake check
    if (!this.lp) this.lp = a.slice(); else for (let k = 0; k < 3; k++) this.lp[k] += 0.02 * (a[k] - this.lp[k]);
    this.hist.push(f); while (this.hist.length && this.hist[0][0] < t - 0.1) this.hist.shift();
    const open = t >= this.lock && t >= this.cool;

    // a candidate waits for 0.4 s of calm, then fires; big motion meanwhile cancels it
    if (this.cand) {
      if (!open) this.cand = null;
      else if (busy) this.calmSince = null;
      else if (this.calmSince === null) this.calmSince = t;
      else if (t - this.calmSince >= 0.4 && !(this.cand.name === "tap2" && t - this.cand.t < 0.5)) this.fire(this.cand.name, t);
    }
    if (busy) { if (quietFor > 0.05) { this.busyStart = t; this.preCalm = quietFor; } this.lastBusy = t; }
    const fromCalm = (t0) => this.preCalm >= 1.0 && t0 - this.busyStart < 0.6;   // began within 0.6 s of leaving >= 1 s of calm
    if (!open || this.cand) { this.gyroX = [null, null, null]; this.accX = [null, null, null]; return; }

    // tap2
    if (this.enabled.tap2) {
      const old = this.hist.find((h) => h[0] >= t - 0.0055) || this.hist[0];
      const jump = Math.max(...[4, 5, 6].map((j) => Math.abs(f[j] - old[j])));
      if (jump > 1.2 && gm < 400) {
        const prev = this.taps[this.taps.length - 1];
        if (!prev || t - prev > 0.06) {              // one knock rings for ~10-20 ms: count it once
          if (prev || fromCalm(t)) {   // the first knock must come out of >= 1 s of calm
            this.taps.push(t); this.taps = this.taps.filter((x) => x > t - 0.6);
            const n = this.taps.length;
            if (n >= 2) {
              const d = this.taps[n - 1] - this.taps[n - 2];
              if (d >= 0.10 && d <= 0.45) { this.cand = { name: "tap2", t }; this.calmSince = null; this.taps = []; return; }
            }
          }
        }
      }
      if (this.taps.length && t - this.taps[this.taps.length - 1] > 0.6) this.taps = [];
    }
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
  fire(name, t) {
    this.cand = null; this.calmSince = null; this.cool = t + 1.5; this.last = { name, t };
    this.gyroX = [null, null, null]; this.accX = [null, null, null]; this.taps = [];
    this.on({ name, t });
  }
}
