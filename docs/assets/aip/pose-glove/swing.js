// Swing analysis on the phone: a port of sensor-glove/src/swing_eye.py (find_swings + analyse).
// No DOM here, so node can test it against the Python version (sensor-glove/src/test_swing_js.mjs).
//
// Feed it every glove frame in physical units; it finds each swing (forearm turning faster than 400 deg/s), waits
// for the glove's impact sound (the most exact clock; it arrives about 1.5 s after the hit), and then measures:
//   tempo        backswing time / downswing time (takeaway -> top -> impact)
//   release_ms   when the trail-wrist hinge drops below half its top value, ms from impact (negative = before)
//   hinge_top / hinge_imp   wrist hinge (deg) at its biggest and at impact, from the gyros alone: zero = the wrist at
//                address, so it is a relative angle until the "정렬" routine gives a real zero
//   arm_dps_imp, hand_dps_peak, hand_peak_ms, saturated (samples at the gyro limit)
// Times are glove time (t_us), so missing frames or a 240 vs 400 Hz stream don't change the numbers.

export const SWING_THRESH = 400, PRE_S = 2.2, POST_S = 0.4, GAP_S = 3.0, WAIT_CLIP_S = 2.5;

function gauss(x, sigma) {             // scipy.ndimage.gaussian_filter1d, mode "reflect", truncate 4
  if (sigma <= 0) return x.slice();
  const r = Math.max(1, Math.round(4 * sigma)), k = [];
  let s = 0;
  for (let i = -r; i <= r; i++) { const v = Math.exp(-0.5 * (i / sigma) ** 2); k.push(v); s += v; }
  const n = x.length, out = new Float64Array(n);
  const at = (i) => { while (i < 0 || i >= n) i = i < 0 ? -i - 1 : 2 * n - i - 1; return x[i]; };
  for (let i = 0; i < n; i++) { let a = 0; for (let j = -r; j <= r; j++) a += k[j + r] * at(i + j); out[i] = a / s; }
  return out;
}

// Rotation rate about the sensor's main turning axis (first principal direction of the gyro over the window), so the
// mounting angle doesn't matter. Sign: positive in the downswing (the biggest peak).
export function axisRate(g) {          // g: array of [x, y, z]
  const n = g.length, m = [0, 0, 0];
  for (const v of g) for (let k = 0; k < 3; k++) m[k] += v[k] / n;
  const C = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  for (const v of g) for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) C[a][b] += (v[a] - m[a]) * (v[b] - m[b]);
  let u = [1, 0.7, 0.4];
  for (let it = 0; it < 60; it++) {
    const w = [0, 1, 2].map((a) => C[a][0] * u[0] + C[a][1] * u[1] + C[a][2] * u[2]);
    const L = Math.hypot(...w) || 1; u = w.map((x) => x / L);
  }
  const w = g.map((v) => v[0] * u[0] + v[1] * u[1] + v[2] * u[2]);
  let big = 0; for (const x of w) if (Math.abs(x) > Math.abs(big)) big = x;
  return big < 0 ? w.map((x) => -x) : w;
}

// One swing's numbers. fr = frames [t_s, hgx, hgy, hgz, hax, hay, haz, agx, agy, agz, aax, aay, aaz] (dps, g),
// tImp = impact time (s, same clock).
// handOnly: no forearm IMU (e.g. a bare XIAO taped to the hand). Phases then come from the hand's own rotation, and
// the wrist hinge (forearm minus hand) can't be measured, so hinge_top / hinge_imp / release_ms are NaN.
export function analyse(fr, tImp, sat = 2290, handOnly = false) {
  const w = fr.filter((f) => f[0] >= tImp - PRE_S && f[0] <= tImp + POST_S);
  if (w.length < 50) return null;
  const tt = w.map((f) => f[0] - tImp);
  // sign: positive in the DOWNSWING, judged by the mean rate 0.30-0.04 s before impact. On real ball strikes (range
  // 2026-10-26) the biggest peak was the impact jolt / recoil, pointing the other way, and one jolt came ~30 ms before
  // the sound time, so a peak-based rule flipped the phases; a short jolt can't outweigh the sustained downswing.
  const downPos = (x) => { let m = 0; for (let i = 0; i < x.length; i++) if (tt[i] > -0.30 && tt[i] < -0.04) m += x[i]; return m < 0 ? x.map((v) => -v) : x; };
  const wh = downPos(axisRate(w.map((f) => [f[1], f[2], f[3]]))), wa = handOnly ? wh : downPos(axisRate(w.map((f) => [f[7], f[8], f[9]])));
  const beta = [0];                      // trail-wrist hinge (deg): integral of forearm minus hand rate
  for (let i = 1; i < w.length; i++) {
    const dt = tt[i] - tt[i - 1];
    beta.push(beta[i - 1] + 0.5 * ((wa[i] - wh[i]) + (wa[i - 1] - wh[i - 1])) * dt);
  }
  const early = beta.filter((_, i) => tt[i] < -PRE_S + 0.4).sort((a, b) => a - b);
  const zero = early.length ? early[Math.floor(early.length / 2)] : 0;
  for (let i = 0; i < beta.length; i++) beta[i] -= zero;
  let i0 = 0; for (let i = 0; i < tt.length; i++) if (Math.abs(tt[i]) < Math.abs(tt[i0])) i0 = i;
  // Top and takeaway from the forearm ANGLE (integral of its rate), not the rate: near the top the rate sits at
  // 0 +- a few deg/s for the pause, so "last negative rate" jumped 40-70 ms; and a rate threshold at takeaway fires
  // 50-90 ms after the arm starts moving (2026-10-26 check against the simulator's true phases).
  // gyro bias (~1 deg/s on these chips) would make the angle drift away from address: remove the rate measured
  // while still at address (the first 0.4 s of the window) before integrating
  const still = wa.filter((_, i) => tt[i] < -PRE_S + 0.4).sort((a, b) => a - b);
  const bias = still.length ? still[Math.floor(still.length / 2)] : 0;
  const phi = [0];
  for (let i = 1; i < w.length; i++) phi.push(phi[i - 1] + 0.5 * (wa[i] + wa[i - 1] - 2 * bias) * (tt[i] - tt[i - 1]));
  let imin = 0; for (let i = 0; i <= i0; i++) if (phi[i] < phi[imin]) imin = i;
  const addr = phi.filter((_, i) => tt[i] < -PRE_S + 0.4).sort((a, b) => a - b);
  const pAddr = addr.length ? addr[Math.floor(addr.length / 2)] : phi[0], amp = Math.max(1, pAddr - phi[imin]);
  let a0 = imin, a1 = imin;                              // the stretch within 1 % of the furthest-back angle
  while (a0 > 0 && phi[a0 - 1] <= phi[imin] + 0.01 * amp) a0--;
  while (a1 < i0 && phi[a1 + 1] <= phi[imin] + 0.01 * amp) a1++;
  const tTop = 0.5 * (tt[a0] + tt[a1]);
  let top = a0; while (top < a1 && tt[top] < tTop) top++;
  // takeaway: the last moment within 1 % of the highest angle in the 1.2 s before the furthest-back point (a hand
  // that settles slightly off its starting angle at address made "1 % of the window's first 0.4 s" fire 0.7 s early)
  let pRef = -Infinity; for (let i = 0; i < imin; i++) if (tt[i] >= tt[imin] - 1.2) pRef = Math.max(pRef, phi[i]);
  if (pRef === -Infinity) pRef = pAddr;
  let take = 0; for (let i = 0; i < imin; i++) if (phi[i] >= pRef - 0.01 * amp) take = i;   // last moment still at address
  let bmax = -Infinity; for (let i = take; i <= i0; i++) bmax = Math.max(bmax, beta[i]);
  let rel = 0; for (let i = top; i <= i0; i++) if (beta[i] < 0.5 * bmax) { rel = tt[i] * 1000; break; }
  let hp = 0; for (let i = 1; i < wh.length; i++) if (wh[i] > wh[hp]) hp = i;
  let saturated = 0; for (const f of w) for (const j of [1, 2, 3, 7, 8, 9]) if (Math.abs(f[j]) >= sat) saturated++;
  const down = -tTop, back = tTop - tt[take];
  return { tempo: back / Math.max(1e-3, down), back_s: back, down_s: down, release_ms: handOnly ? NaN : rel,
           hinge_top: handOnly ? NaN : bmax, hinge_imp: handOnly ? NaN : beta[i0], hand_only: handOnly,
           arm_back_deg: amp, pause_ms: (tt[a1] - tt[a0]) * 1000, arm_dps_imp: wa[i0], hand_dps_peak: wh[hp], hand_peak_ms: tt[hp] * 1000, saturated, frames: w.length,
           rate_hz: (w.length - 1) / (tt[tt.length - 1] - tt[0]) };
}

// Impact time without a sound clip: the strongest jolt in the hand accel near the forearm's speed peak (the ball
// strike rings the accelerometer); a practice swing without a ball falls back to the peak itself.
export function impactFromMotion(fr, tPeak) {
  const w = fr.filter((f) => f[0] >= tPeak - 0.15 && f[0] <= tPeak + 0.25);
  if (w.length < 5) return { t: tPeak, source: "arm peak" };
  const ax = [4, 5, 6].map((j) => gauss(Float64Array.from(w.map((f) => f[j])), 0.7));
  let best = -1, bi = 0;
  for (let i = 0; i < w.length; i++) {
    let s = 0;
    for (let a = 0; a < 3; a++) { const v = w[i][4 + a]; if (Math.abs(v) < 15.9) s += (v - ax[a][i]) ** 2; }
    if (s > best) { best = s; bi = i; }
  }
  return Math.sqrt(best) > 0.8 ? { t: w[bi][0], source: "accel" } : { t: tPeak, source: "arm peak" };
}

export class SwingDetector {
  // onSwing(result) is called once per swing: { n, t_imp (s, glove clock), source, ...analyse() }
  constructor(onSwing, opts = {}) {
    this.onSwing = onSwing; this.thresh = opts.thresh ?? SWING_THRESH;
    this.buf = []; this.keep = PRE_S + WAIT_CLIP_S + 2;
    this.sm = []; this.pending = null; this.nextOk = -Infinity; this.n = 0; this.sounds = [];
  }
  // f = [t_s, 12 values in dps / g]
  frame(f) {
    this.buf.push(f);
    while (this.buf.length && this.buf[0][0] < f[0] - this.keep) this.buf.shift();
    if (Math.abs(f[7]) + Math.abs(f[8]) + Math.abs(f[9]) + Math.abs(f[10]) + Math.abs(f[11]) + Math.abs(f[12]) > 0) this.armSeen = true;
    const arm = this.armSeen ? [f[7], f[8], f[9]] : [f[1], f[2], f[3]];   // no forearm IMU: use the hand (as the firmware does)
    this.sm.push([f[0], Math.hypot(...arm)]);   // forearm speed, smoothed over ~20 ms
    while (this.sm.length && this.sm[0][0] < f[0] - 0.02) this.sm.shift();
    const v = this.sm.reduce((a, r) => a + r[1], 0) / this.sm.length;
    // hand-only: the hand already passes ~440 deg/s in the backswing (the wrist cocks), so wait for the downswing
    const thr = this.armSeen ? this.thresh : Math.max(this.thresh, 800);
    if (!this.pending && v > thr && f[0] >= this.nextOk) this.pending = { t0: f[0] };
    if (this.pending && !this.pending.peak && f[0] >= this.pending.t0 + 0.5) {
      // forearm speed peak in the 0.5 s after the swing started, then the impact estimate from the hand accel
      const w = this.buf.filter((r) => r[0] >= this.pending.t0 && r[0] <= this.pending.t0 + 0.5);
      const s = gauss(Float64Array.from(w.map((r) => this.armSeen ? Math.hypot(r[7], r[8], r[9]) : Math.hypot(r[1], r[2], r[3]))), 4 * (w.length / 0.5) / 400);
      let pk = 0; for (let i = 1; i < s.length; i++) if (s[i] > s[pk]) pk = i;
      this.pending.peak = w[pk][0];
    }
    if (this.pending && this.pending.peak && !this.pending.est && f[0] >= this.pending.peak + 0.3) {
      this.pending.est = impactFromMotion(this.buf, this.pending.peak);
    }
    if (this.pending && this.pending.est) {
      const snd = this.sounds.find((t) => Math.abs(t - this.pending.est.t) < 0.3);
      if (snd !== undefined) this.finish(snd, "sound");
      else if (f[0] >= this.pending.est.t + WAIT_CLIP_S) this.finish(this.pending.est.t, this.pending.est.source);
    }
  }
  // the glove's impact sound clip arrived (its t_us -> s); it may come before or after the swing is found
  sound(t) {
    this.sounds.push(t); this.sounds = this.sounds.filter((x) => x > t - 10);
  }
  finish(tImp, source) {
    this.pending = null; this.nextOk = tImp + GAP_S;
    const a = analyse(this.buf, tImp, 2290, !this.armSeen);
    if (a) this.onSwing({ n: ++this.n, t_imp: tImp, source, ...a });
  }
}

// One short spoken line for a swing (Korean, plain numbers; no judgement until real swings give references).
export function swingLine(s) {
  if (s.hand_only || Number.isNaN(s.release_ms)) return `템포 ${s.tempo.toFixed(1)} 대 1.`;
  const rel = Math.round(-s.release_ms);
  const when = rel > 5 ? `임팩트 ${rel}밀리초 전` : rel < -5 ? `임팩트 ${-rel}밀리초 뒤` : "임팩트 때";
  return `템포 ${s.tempo.toFixed(1)} 대 1. 손목은 ${when} 풀렸어요.`;
}
