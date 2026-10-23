// SensorGlove over Web Bluetooth: connect, start/stop, and parse its notifications.
// Protocol (xiao_ble_glove.ino): data notifications are
//   IMU    : seq u32, n u8 (1..8), armOk u8, then n frames of t_us u32 + 12 x i16
//            (hand gyro xyz, hand acc xyz, arm gyro xyz, arm acc xyz)
//   status : seq u32, 0, armOk, vbat u16, charging u8, dropped u32, hz u16
//   clip   : id u16, chunk u16, 0xFE, kind (0 impact, 1 voice); chunk 0 = t_us u32, pre u16, total u16, rate u16, peak u16,
//            chunks 1.. = int16 samples
// ctrl writes: "probe", "start <hz> <batch> <mic>", "stop", "status".
export const SVC = "7e5a0001-2f3b-4c1d-9a8e-0b1c2d3e4f50";
export const DATA = "7e5a0002-2f3b-4c1d-9a8e-0b1c2d3e4f50";
export const CTRL = "7e5a0003-2f3b-4c1d-9a8e-0b1c2d3e4f50";
export const ACC_G = 0.488e-3, GYRO_DPS = 70e-3, SAT_DPS = 2293;

// Parses one notification. `now` is the phone time (ms) it arrived; returns what it was.
export class GloveParser {
  constructor() { this.reset(); }
  reset() {
    this.frames = []; this.status = []; this.clips = new Map();
    this.nextSeq = null; this.missing = 0; this.count = 0; this.probeLen = null; this.armOk = null;
    this.clock = new ClockFit();
  }
  feed(dv, now) {
    if (this.probeLen === null && dv.byteLength > 30 && [0, 1, 2, 3, 4, 5, 6, 7].every((v) => dv.getUint8(v) === v)) {
      this.probeLen = dv.byteLength; return { type: "probe", len: dv.byteLength };
    }
    if (dv.byteLength < 6) return null;
    const n = dv.getUint8(4);
    if (n === 0xFE) return this.clipChunk(dv, now);
    if (n === 0) {
      if (dv.byteLength < 15) return null;
      const s = { now, armOk: dv.getUint8(5), mv: dv.getUint16(6, true), charging: dv.getUint8(8), dropped: dv.getUint32(9, true), hz: dv.getUint16(13, true) };
      this.armOk = s.armOk; this.status.push(s); return { type: "status", ...s };
    }
    const seq = dv.getUint32(0, true);
    if (this.nextSeq !== null && seq !== this.nextSeq) this.missing += (seq - this.nextSeq) >>> 0;
    this.nextSeq = (seq + n) >>> 0; this.armOk = dv.getUint8(5);
    const got = [];
    for (let i = 0; i < n; i++) {
      const off = 6 + 28 * i;
      if (off + 28 > dv.byteLength) break;
      const f = [now, seq + i, dv.getUint32(off, true)];
      for (let k = 0; k < 12; k++) f.push(dv.getInt16(off + 4 + 2 * k, true));
      this.frames.push(f); got.push(f); this.count++;
    }
    if (got.length) this.clock.add(now, got[got.length - 1][2]);
    return { type: "imu", frames: got };
  }
  clipChunk(dv, now) {
    const id = dv.getUint16(0, true), ch = dv.getUint16(2, true), kind = dv.getUint8(5) === 1 ? "voice" : "impact";
    const key = `${kind}${id}`;
    let c = this.clips.get(key);
    if (!c) { c = { kind, id, parts: new Map(), firstNow: now }; this.clips.set(key, c); }
    if (ch === 0 && dv.byteLength >= 18) {
      c.t_us = dv.getUint32(6, true); c.pre = dv.getUint16(10, true); c.total = dv.getUint16(12, true);
      c.rate = dv.getUint16(14, true); c.peak = dv.getUint16(16, true);
    } else {
      c.parts.set(ch, new Int16Array(dv.buffer.slice(dv.byteOffset + 6, dv.byteOffset + dv.byteLength)));
    }
    c.lastNow = now;
    const done = clipDone(c);
    if (done && !c.reported) { c.reported = true; return { type: "clip", clip: c }; }
    return { type: "chunk" };
  }
}

// Same rule as host/stream.py: header seen, last chunk seen, at most 2 chunks lost (left silent).
export function clipLayout(c) {
  if (c.total === undefined || c.parts.size === 0) return null;
  let per = 0; for (const p of c.parts.values()) per = Math.max(per, p.length);
  const n = Math.ceil(c.total / per), missing = [];
  for (let k = 1; k <= n; k++) if (!c.parts.has(k)) missing.push(k);
  return { per, n, missing };
}
export function clipDone(c) {
  const L = clipLayout(c);
  return !!L && (c.parts.has(L.n) || L.missing.length === 0) && L.missing.length <= 2;
}
export function clipSamples(c) {
  const L = clipLayout(c), out = new Int16Array(c.total);
  for (const [k, p] of c.parts) { const s0 = (k - 1) * L.per; out.set(p.subarray(0, Math.max(0, Math.min(p.length, c.total - s0))), s0); }
  return out;
}

// Web Bluetooth connection (Android Chrome / desktop Chrome). onPacket(result) is called per parsed notification.
export class Glove {
  constructor(onPacket, onState) { this.parser = new GloveParser(); this.onPacket = onPacket; this.onState = onState || (() => {}); this.batch = 1; }
  async connect() {
    if (!navigator.bluetooth) throw new Error("no-web-bluetooth");
    this.device = await navigator.bluetooth.requestDevice({ filters: [{ name: "SensorGlove" }, { services: [SVC] }], optionalServices: [SVC] });
    this.device.addEventListener("gattserverdisconnected", () => this.onState("disconnected"));
    const server = await this.device.gatt.connect();
    const svc = await server.getPrimaryService(SVC);
    this.data = await svc.getCharacteristic(DATA); this.ctrl = await svc.getCharacteristic(CTRL);
    this.data.addEventListener("characteristicvaluechanged", (e) => {
      const r = this.parser.feed(e.target.value, e.timeStamp || performance.now());
      if (r) this.onPacket(r);
    });
    await this.data.startNotifications();
    this.onState("connected");
    // Probe: the glove answers with a 244-byte notification; what arrives sets the batch (frames per packet).
    this.parser.probeLen = null;
    await this.send("probe");
    const t0 = performance.now();
    while (this.parser.probeLen === null && performance.now() - t0 < 2000) await new Promise((r) => setTimeout(r, 50));
    const len = this.parser.probeLen || 20;
    this.batch = Math.max(1, Math.min(8, Math.floor((len - 6) / 28)));
    return { probeLen: this.parser.probeLen, batch: this.batch };
  }
  send(text) { return this.ctrl.writeValueWithoutResponse(new TextEncoder().encode(text)); }
  start(hz = 200, mic = 1) { this.parser.nextSeq = null; return this.send(`start ${hz} ${this.batch} ${mic}`); }
  stop() { return this.send("stop"); }
  disconnect() { if (this.device && this.device.gatt.connected) this.device.gatt.disconnect(); }
}

// Glove clock -> phone clock (ms). Each packet's newest frame gives one point: arrival time minus glove time.
// Bluetooth only ever delays, so the lowest points in each 2 s window trace the true offset; a line through
// those window minima (offset + drift) is the fit. On the S25 the residual was about +-8 ms (2026-10-22 logs).
export class ClockFit {
  constructor(win = 2000, keep = 60) { this.win = win; this.keep = keep; this.mins = new Map(); this.a = 0; this.b = null; this.t0 = null; }
  add(phoneMs, gloveUs) {
    const g = gloveUs / 1000, off = phoneMs - g;
    if (this.t0 === null) this.t0 = g;
    const k = Math.floor((g - this.t0) / this.win), m = this.mins.get(k);
    if (!m || off < m[1]) { this.mins.set(k, [g, off]); this.refit(); }
    if (this.mins.size > this.keep) this.mins.delete(Math.min(...this.mins.keys()));
  }
  refit() {
    const pts = [...this.mins.values()];
    if (pts.length < 3) { this.a = 0; this.b = Math.min(...pts.map((p) => p[1])); return; }
    let sx = 0, sy = 0, sxx = 0, sxy = 0; const n = pts.length;
    for (const [x0, y] of pts) { const x = x0 - this.t0; sx += x; sy += y; sxx += x * x; sxy += x * y; }
    // Both crystals are good to ~+-50 ppm, so a steeper slope is window noise in a short log: clamp it.
    this.a = Math.max(-150e-6, Math.min(150e-6, (n * sxy - sx * sy) / (n * sxx - sx * sx))); this.b = (sy - this.a * sx) / n;
  }
  ready() { return this.b !== null; }
  toPhone(gloveUs) { const g = gloveUs / 1000; return g + this.b + this.a * (g - this.t0); }
}
