// Voice commands on the phone: a port of xiao-sense/host/voice.py's matcher (VoiceCommands.match).
// The command list is commands.json, generated from the same commands.example.yaml the PC uses
// (commands_to_json.py). Speech-to-text here is Chrome's own (Web Speech API, ko-KR), not Whisper.
// No DOM, so node can test it against voice.py (sensor-glove/src/test_voice_js.mjs).

export const norm = (s) => s.toLowerCase().replace(/[\s.,!?~'"]+/g, "");

// difflib.SequenceMatcher(None, a, b).ratio() without the junk heuristics (strings here are short)
function longest(a, b, alo, ahi, blo, bhi) {
  let bi = alo, bj = blo, bk = 0, len = new Map();
  for (let i = alo; i < ahi; i++) {
    const nl = new Map();
    for (let j = blo; j < bhi; j++) {
      if (a[i] !== b[j]) continue;
      const k = (len.get(j - 1) || 0) + 1; nl.set(j, k);
      if (k > bk) { bi = i - k + 1; bj = j - k + 1; bk = k; }
    }
    len = nl;
  }
  return [bi, bj, bk];
}
function matches(a, b, alo = 0, ahi = a.length, blo = 0, bhi = b.length) {
  const [i, j, k] = longest(a, b, alo, ahi, blo, bhi);
  if (!k) return 0;
  return k + matches(a, b, alo, i, blo, j) + matches(a, b, i + k, ahi, j + k, bhi);
}
export function ratio(a, b) { const t = a.length + b.length; return t ? (2 * matches(a, b)) / t : 1; }

export class VoiceCommands {
  constructor(cfg) {
    this.minScore = cfg.min_score ?? 0.75;
    this.prefixes = cfg.prefixes || []; this.players = cfg.players || [];
    this.commands = (cfg.commands || []).map((c) => ({ ...c }));
    for (const pl of this.players)      // known players also switch with "<name> 차례" ("친구 차례")
      this.commands.push({ say: pl.say.filter((p) => !p.endsWith("차례")).map((p) => `${p} 차례`), action: "set_player", args: { name: pl.name } });
  }
  static after(text, prefix) {          // the original words after the prefix, trailing particles trimmed
    const flat = text.replace(/ /g, ""), want = prefix.replace(/ /g, ""), j = flat.indexOf(want);
    if (j < 0) return "";
    let k = 0, seen = 0;
    while (k < text.length && seen < j + want.length) { seen += text[k] !== " " ? 1 : 0; k++; }
    const rest = text.slice(k).replace(/^[ .,!?~]+|[ .,!?~]+$/g, "");
    return rest.replace(/(으로|로|이요|요|입니다|이야|야)$/, "").trim();
  }
  player(name) {
    const n = norm(name); let best = [0, name];
    for (const pl of this.players) for (const ph of pl.say) { const r = ratio(norm(ph), n); if (r > best[0]) best = [r, pl.name]; }
    return best[0] >= this.minScore ? best[1] : name;
  }
  match(text) {
    const t = norm(text);
    if (!t) return null;
    for (const c of this.prefixes) for (const ph of c.say) {
      const i = t.indexOf(norm(ph));
      if (i >= 0 && t.length > i + norm(ph).length) {
        let rest = VoiceCommands.after(text, ph);
        if (!rest || this.commands.some((c2) => c2.say.some((f) => norm(f) === norm(rest)))) continue;
        if (c.arg === "name") rest = this.player(rest);
        return { action: c.action, args: { ...(c.args || {}), [c.arg]: rest }, said: ph, score: 1.0, text };
      }
    }
    let best = null;
    for (const c of this.commands) for (const phrase of c.say) {
      const p = norm(phrase);
      let score;
      if (t.includes(p)) score = 1.0 + p.length / 100;
      else {
        const n = p.length; score = 0;
        for (let i = 0; i < Math.max(1, t.length - n + 1); i++) score = Math.max(score, ratio(p, t.slice(i, i + n)));
      }
      if (!best || score > best.score) best = { action: c.action, args: c.args || {}, said: phrase, score: Math.round(score * 1000) / 1000, text, cmd: c };
    }
    if (best && best.score >= this.minScore) {
      const pair = { set_club: "set_swing", set_swing: "set_club" }[best.action];
      if (pair) {
        let hit = null;
        for (const c of this.commands) if (c.action === pair) for (const ph of c.say) if (t.includes(norm(ph)) && (!hit || norm(ph).length > hit[0])) hit = [norm(ph).length, c];
        if (hit) best.also = [{ action: hit[1].action, args: hit[1].args || {}, cmd: hit[1] }];
      }
      return best;
    }
    return { action: "note", args: {}, said: null, score: best ? best.score : 0, text };
  }
}

// Web Speech wrapper: push to talk (listenOnce) or keep listening (setContinuous). Pauses while the phone speaks, so
// it doesn't hear its own reply. onText(alternatives[]) gets Chrome's top guesses for each finished phrase.
export class Listener {
  constructor(onText, onState) {
    const SR = typeof window !== "undefined" && (window.SpeechRecognition || window.webkitSpeechRecognition);
    this.ok = !!SR; this.onText = onText; this.onState = onState || (() => {}); this.cont = false; this.on = false; this.paused = false;
    if (!SR) return;
    const r = new SR(); this.r = r;
    r.lang = "ko-KR"; r.interimResults = false; r.maxAlternatives = 3; r.continuous = false;
    r.onresult = (e) => {
      const res = e.results[e.results.length - 1];
      if (res && res.isFinal) this.onText([...res].map((x) => x.transcript));
    };
    r.onerror = (e) => { this.onState("error", e.error); };
    r.onend = () => {
      this.on = false;
      if (this.cont && !this.paused) setTimeout(() => this.start(), 250); else this.onState("idle");
    };
  }
  start() { if (!this.ok || this.on) return; try { this.r.start(); this.on = true; this.onState("listening"); } catch (e) { this.onState("error", e.message); } }
  listenOnce() { this.cont = false; this.start(); }
  setContinuous(v) { this.cont = v; if (v) this.start(); else if (this.on) this.r.stop(); }
  pause() { this.paused = true; if (this.on) this.r.abort(); }
  resume() { this.paused = false; if (this.cont) this.start(); }
}
