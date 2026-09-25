// FERRIN preview logic. Pure functions only: no DOM, no network, no timers.
// ferrin.js wires these to the page; tests/js exercises them directly.

export const ROWS = ['idle', 'running-right', 'running-left', 'waving', 'jumping', 'failed', 'waiting', 'running', 'review'];
export const FRAMES = { idle: 6, 'running-right': 8, 'running-left': 8, waving: 4, jumping: 5, failed: 8, waiting: 6, running: 6, review: 6 };
export const HOST_BUILTINS = ['status', 'review', 'compact', 'help', 'pet', 'init', 'clear'];
export const PERIMETER = ['ArrowUp', 'ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'ArrowRight', 'ArrowDown', 'ArrowLeft', 'Enter'];
export const HULL_ID = [...'longwake'];
export const MOOD_FLOOR = 25, MOOD_CAP = 100, DAILY_GAIN_CAP = 15;

/** Resolve a row name ("idle", "look:5") to atlas coordinates. */
export function rowRef(name) {
  const m = /^look:(\d+)$/.exec(name);
  if (m) { const i = Number(m[1]); return { row: 9 + Math.floor(i / 8), start: i % 8, frames: 1 }; }
  const r = ROWS.indexOf(name);
  if (r < 0) throw new Error('unknown row ' + name);
  return { row: r, start: 0, frames: FRAMES[name] };
}

/** verb (one or two words) -> command */
export function buildIndex(commands) {
  const idx = new Map();
  for (const c of commands) for (const v of c.triggers.verbs || []) idx.set(v.toLowerCase(), c);
  return idx;
}

/** Parse console input such as "$ferrin ward up", "/ferrin sitrep" or "decrypt LW-03". */
export function parse(input, index) {
  const s = String(input).trim().toLowerCase().replace(/^([$/]ferrin\s+|[/>]\s*)/, '').replace(/[.!?]+$/, '');
  const words = s.split(/\s+/).filter(Boolean);
  for (let n = Math.min(4, words.length); n >= 1; n--) {
    const key = words.slice(0, n).join(' ');
    if (index.has(key)) return { cmd: index.get(key), verb: key, args: words.slice(n) };
  }
  return { cmd: index.get('__unknown__') || null, verb: words[0] || '', args: words.slice(1) };
}

const isTyping = e => !!(e && e.target && typeof e.target.closest === 'function' && e.target.closest('input, textarea, select, [contenteditable]'));

/** Key sequence detector. Returns a handler(event, nowMs) -> true when the sequence completes. */
export function keySequence(seq, { timeoutMs = 1500 } = {}) {
  let i = 0, last = -Infinity;
  return (e, now) => {
    if (isTyping(e)) return false;
    if (now - last > timeoutMs) i = 0;
    last = now;
    const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
    if (k === seq[i]) { if (++i === seq.length) { i = 0; return true; } }
    else i = k === seq[0] ? 1 : 0;
    return false;
  };
}

/** Click burst detector: returns tick(nowMs) -> true when count clicks land within windowMs. */
export function clickBurst(count, windowMs) {
  let hits = [];
  return now => {
    hits = [...hits.filter(t => now - t < windowMs), now];
    if (hits.length >= count) { hits = []; return true; }
    return false;
  };
}

/** Small seeded RNG (mulberry32). One seed per install gives each FERRIN its own rare-line luck. */
export function rng(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

/** Pick a line: filter by `when`, weight rare (weight 1) lines x3 under Lucky Ledger. */
export function pickLine(cmd, { when = null, random = Math.random, lucky = false } = {}) {
  let pool = cmd.lines.filter(l => (when ? l.when === when : !l.when));
  if (!pool.length) pool = cmd.lines.filter(l => !l.when);
  if (!pool.length) pool = cmd.lines;
  const w = l => (lucky && l.weight <= 2 ? l.weight * 3 : l.weight);
  const total = pool.reduce((s, l) => s + w(l), 0);
  let r = random() * total;
  for (const l of pool) { r -= w(l); if (r < 0) return l; }
  return pool[pool.length - 1];
}

export const fill = (text, vars = {}) => text.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? String(vars[k]) : m));

/** Local ISO date (YYYY-MM-DD) for distinct-day counting. Never a streak. */
export const dayKey = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

export function defaultState(now = new Date()) {
  return { power: 80, sync: 80, morale: 80, gained: {}, days: [dayKey(now)], installed: dayKey(now),
           found: { logs: [], ballast: [], commendations: [] }, ballastOn: [], seed: (now.getTime() * 2654435761) >>> 0 };
}

/**
 * Forgiving mood: gains capped at +15 per mood per day, values clamped to 25..100,
 * morale never drops, and nothing decays with absence (there is no decay function at all).
 */
export function applyMood(state, delta, day) {
  const g = state.gained[day] || (state.gained[day] = { power: 0, sync: 0, morale: 0 });
  for (const k of ['power', 'sync', 'morale']) {
    let d = delta[k] || 0;
    if (k === 'morale' && d < 0) d = 0;
    if (d > 0) { d = Math.min(d, DAILY_GAIN_CAP - g[k]); g[k] += Math.max(0, d); }
    state[k] = Math.max(MOOD_FLOOR, Math.min(MOOD_CAP, state[k] + d));
  }
  return state;
}

export const moodWord = v => (v >= 85 ? 'strong' : v >= 65 ? 'steady' : v >= 45 ? 'thin' : 'running on fumes');

/** Voice modifiers from active Ballast Tags. */
export function voice(text, on = []) {
  let t = text;
  if (on.includes('short-rations')) { const w = t.split(/\s+/); if (w.length > 5) t = w.slice(0, 5).join(' ').replace(/[,;:.!?]+$/, '') + '.'; }
  if (on.includes('loud-manifest')) t = 'MF-' + String(t.length * 37 % 9000 + 1000) + ': ' + t.toUpperCase();
  return t;
}

/** Calendar and clock triggers active at `now`. */
export function activeEvents(now, events, installed) {
  const m = now.getMonth() + 1, d = now.getDate(), h = now.getHours(), out = [];
  for (const e of events) {
    if (e.time) { if (h >= e.time.from && h < e.time.to) out.push(e); continue; }
    const dates = Array.isArray(e.date) ? e.date : [e.date];
    for (const dt of dates) {
      if (!dt) continue;
      if (dt.anniversary === 'install') {
        if (!installed) continue;
        const [y, im, id] = installed.split('-').map(Number);
        if (im === m && id === d && now.getFullYear() > y) out.push(e);
      } else if (dt.month === m && dt.day === d) out.push(e);
    }
  }
  return out;
}

/** Which Longwake logs are unlocked by distinct days of use. */
export function dayLogs(days) {
  const n = new Set(days).size, out = ['LW-01'];
  if (n >= 2) out.push('LW-02'); if (n >= 3) out.push('LW-03'); if (n >= 4) out.push('LW-05');
  return out;
}
