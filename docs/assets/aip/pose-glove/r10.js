// R10 shots from the R10 Bridge app on the same phone (ws://127.0.0.1:8765), paired with glove swings.
// The app relays the Garmin Golf app's E6 link: one {"type":"shot", shot, t_wall_ms, ball, club} per shot.
// See sensor-glove/android/r10bridge/README.md.

export const R10_URL = "ws://127.0.0.1:8765";

// A shot reaches the page a little after the impact (R10 → Garmin app → bridge), and the glove's swing row
// arrives ~2 s after its impact too, so either can come first. A shot pairs with the latest unpaired swing whose
// impact is MIN_LAG_MS..MAX_LAG_MS before the shot's arrival; until then the shot waits up to WAIT_MS.
export const MIN_LAG_MS = 150, MAX_LAG_MS = 8000, WAIT_MS = 6000;

/** Pure pairing step. swings: [{n, impactPhoneMs}], shots: [{arrivalMs, swing}] (swing null = unpaired).
 *  Fills shot.swing / shot.lagMs where possible; returns the shots it paired now. */
export function pairShots(swings, shots, nowMs) {
  const used = new Set(shots.filter((s) => s.swing != null).map((s) => s.swing));
  const paired = [];
  // oldest shot first, so two quick shots take the two swings in order
  for (const s of shots.filter((x) => x.swing == null && !x.gaveUp).sort((a, b) => a.arrivalMs - b.arrivalMs)) {
    let best = null;
    for (const w of swings) {
      if (w.impactPhoneMs == null || used.has(w.n)) continue;
      const lag = s.arrivalMs - w.impactPhoneMs;
      if (lag < MIN_LAG_MS || lag > MAX_LAG_MS) continue;
      if (!best || w.impactPhoneMs > best.impactPhoneMs) best = w;
    }
    if (best) {
      s.swing = best.n; s.lagMs = +(s.arrivalMs - best.impactPhoneMs).toFixed(1);
      used.add(best.n); paired.push(s);
    } else if (nowMs - s.arrivalMs > WAIT_MS) {
      s.gaveUp = true;   // no swing showed up: R10 saw a ball the glove missed, or the glove was off
    }
  }
  return paired;
}

/** WebSocket client that reconnects on its own. onShot(msg, arrivalMs), onState(text, connected). */
export class R10Link {
  constructor(onShot, onState, url = R10_URL) {
    this.onShot = onShot; this.onState = onState; this.url = url;
    this.ws = null; this.want = false; this.timer = null;
  }
  start() { this.want = true; this.open(); }
  stop() {
    this.want = false; clearTimeout(this.timer);
    if (this.ws) { this.ws.onclose = null; this.ws.close(); this.ws = null; }
    this.onState("꺼짐", false);
  }
  open() {
    if (!this.want) return;
    let ws;
    try { ws = new WebSocket(this.url); } catch (e) { this.retry("열 수 없음: " + e.message); return; }
    this.ws = ws;
    ws.onopen = () => this.onState("R10 Bridge 연결됨", true);
    ws.onmessage = (e) => {
      const t = performance.now();
      let m; try { m = JSON.parse(e.data); } catch { return; }
      if (m.type === "shot") this.onShot(m, t);
      else if (m.type === "status") this.onState(m.text, true);
    };
    ws.onclose = () => this.retry("R10 Bridge 앱이 꺼져 있어요 (3초 뒤 다시 시도)");
    ws.onerror = () => {};
  }
  retry(why) {
    this.ws = null;
    if (!this.want) return;
    this.onState(why, false);
    clearTimeout(this.timer); this.timer = setTimeout(() => this.open(), 3000);
  }
}

/** One spoken/printed line for a paired shot. Signs follow the R10 app: + = right of target for a right-hander. */
export function shotLine(m) {
  const b = m.ball || {}, c = m.club || {};
  const side = (v, l, r) => (v > 0.5 ? `${r} ${Math.abs(v).toFixed(0)}도` : v < -0.5 ? `${l} ${Math.abs(v).toFixed(0)}도` : "똑바로");
  return `볼 ${(b.BallSpeed ?? 0).toFixed(0)}, 출발 ${side(b.LaunchDirection ?? 0, "왼쪽", "오른쪽")}, 패스 ${side(c.ClubAnglePath ?? 0, "아웃인", "인아웃")}`;
}
