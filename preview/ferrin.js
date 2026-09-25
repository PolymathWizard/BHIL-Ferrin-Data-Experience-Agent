// FERRIN preview console: sprite player, Drift Ops commands, forgiving mood engine, secrets.
// No network calls beyond loading this folder's own files. Progress lives in localStorage only.
import { rowRef, buildIndex, parse, keySequence, clickBurst, rng, pickLine, fill, dayKey, defaultState,
  applyMood, moodWord, voice, activeEvents, dayLogs, PERIMETER, HULL_ID } from './commands.js';

const $ = s => document.querySelector(s);
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const [C, L, B, E] = await Promise.all(['commands', 'logs', 'ballast', 'events'].map(n => fetch(`data/${n}.json`).then(r => r.json())));
const byId = Object.fromEntries(C.commands.map(c => [c.id, c]));
const index = buildIndex(C.commands); index.set('__unknown__', byId.unknown);

// ---------------------------------------------------------------- state (localStorage, guarded)
const KEY = 'ferrin.state';
let state;
try { state = JSON.parse(localStorage.getItem(KEY)) || null; } catch { state = null; }
const now0 = new Date();
state = Object.assign(defaultState(now0), state || {});
const lastDay = state.days[state.days.length - 1];
const today = () => dayKey(new Date());
if (!state.days.includes(today())) state.days.push(today());
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* private mode: run without saving */ } };
const random = rng(state.seed + state.days.length);
const on = id => state.ballastOn.includes(id);
let MEM = null;
try { MEM = globalThis.FerrinMemory ? FerrinMemory.create(localStorage) : null; } catch { MEM = globalThis.FerrinMemory ? FerrinMemory.create(null) : null; }

// ---------------------------------------------------------------- sprite player
const cv = $('#pet'), g = cv.getContext('2d'); g.imageSmoothingQuality = 'high';
const sheet = new Image(); sheet.src = '../spritesheet.webp';
let queue = [], cur = null, frame = 0, acc = 0, held = false, look = null;
function play(rows, reduced) {
  const seq = reduce.matches ? (reduced || ['idle']) : rows;
  queue = seq.map(rowRef).map(r => ({ ...r, once: true })); cur = null;
}
function draw(ref, f) {
  g.clearRect(0, 0, cv.width, cv.height);
  if (!sheet.complete) return;
  const col = ref.start + (ref.frames > 1 ? f % ref.frames : 0);
  g.drawImage(sheet, col * 192, ref.row * 208, 192, 208, 0, 0, cv.width, cv.height);
}
let last = performance.now(), loopStart = performance.now();
function tick(t) {
  const dt = t - last; last = t;
  if (!held) {
    acc += dt;
    const fps = 8;
    if (!cur) { cur = queue.shift() || null; frame = 0; loopStart = t; }
    if (acc > 1000 / fps) {
      acc = 0; frame++;
      if (cur && frame >= Math.max(cur.frames, cur.frames === 1 ? 4 : 0)) { cur = queue.shift() || null; frame = 0; }
    }
  }
  const idleRef = rowRef(state.power < 45 ? 'waiting' : 'idle');
  const ref = cur || (look !== null && !reduce.matches ? rowRef('look:' + look) : idleRef);
  draw(ref, reduce.matches ? 0 : (cur ? frame : Math.floor(t / 125)));
  requestAnimationFrame(tick);
}
sheet.onload = () => requestAnimationFrame(tick);

// pointer tracking through the 16 look directions (Mirror Watch turns it around)
let lookTimer = 0;
addEventListener('pointermove', e => {
  const r = cv.getBoundingClientRect(); const dx = e.clientX - (r.left + r.width / 2), dy = e.clientY - (r.top + r.height * .35);
  if (Math.hypot(dx, dy) < 30) { look = null; return; }
  let a = Math.atan2(dx, -dy) * 180 / Math.PI; if (a < 0) a += 360;
  if (on('mirror-watch')) a = (a + 180) % 360;
  look = Math.round(a / 22.5) % 16; clearTimeout(lookTimer); lookTimer = setTimeout(() => { look = null; }, 2500);
}, { passive: true });

// ---------------------------------------------------------------- output
const log = $('#log'), said = $('#said');
function out(text, cls = 'f') {
  const p = document.createElement('p'); p.className = cls;
  if (cls === 'f') { p.innerHTML = '<b>FERRIN</b>'; p.append(text); } else p.textContent = text;
  log.append(p); log.scrollTop = log.scrollHeight;
}
function say(text, rows, reduced) {
  const t = voice(text, state.ballastOn);
  out(t); said.textContent = t;
  if (rows) play(rows, reduced);
}
const vars = () => on('dead-reckoning')
  ? { p: moodWord(state.power), s: moodWord(state.sync), m: moodWord(state.morale) }
  : { p: state.power, s: state.sync, m: state.morale };
function gauges() {
  for (const [k, id] of [['power', 'p'], ['sync', 's'], ['morale', 'm']]) {
    $('#g' + id).textContent = on('dead-reckoning') ? moodWord(state[k]) : state[k];
    $('#b' + id).style.width = state[k] + '%';
  }
  $('#stage').classList.toggle('night', on('night-cargo'));
  const l = $('#ledger'); l.innerHTML = '';
  const li = s => { const x = document.createElement('li'); x.textContent = s; l.append(x); };
  li(`Days aboard: ${new Set(state.days).size} (distinct days, never a streak)`);
  li(`Logs: ${state.found.logs.length} of 8`);
  li(`Ballast Tags: ${state.found.ballast.length} of 6${state.found.ballast.length ? ' (' + state.found.ballast.map(id => B.tags.find(t => t.id === id).name + (on(id) ? ' on' : '')).join(', ') + ')' : ''}`);
  li(`Commendations: ${state.found.commendations.length} of 7`);
}
function mood(delta) { applyMood(state, delta || {}, today()); gauges(); save(); }

// ---------------------------------------------------------------- unlocks
let sfx = null;
const cue = id => { if (sfx) sfx.play(id); };
function commend(id) {
  if (state.found.commendations.includes(id)) return;
  state.found.commendations.push(id); const c = E.commendations.find(x => x.id === id);
  out(`Commendation stamped: ${c.name}.`, 'sys'); cue('egg-commendation'); save(); gauges();
}
function findBallast(id) {
  if (state.found.ballast.includes(id)) return;
  state.found.ballast.push(id); const t = B.tags.find(x => x.id === id);
  out(`Ballast Tag found: ${t.name}. Toggle with "ballast ${t.id} on".`, 'sys'); cue('egg-ballast-tag');
  if (state.found.ballast.length === 6) commend('full-ballast'); save(); gauges();
}
function findLog(id, quiet) {
  if (state.found.logs.includes(id)) return;
  state.found.logs.push(id); if (!quiet) { out(`Log ${id} recovered. Read it with "decrypt ${id}".`, 'sys'); cue('egg-log-unlocked'); }
  save(); gauges();
}
const graveyard = () => { const h = new Date().getHours(); return h >= 0 && h < 4; };

// ---------------------------------------------------------------- commands
let pending = null, scuttleCount = 0, busy = false;
function run(input) {
  if (!input.trim()) return;
  out(input, 'u');
  if (pending) { const p = pending; pending = null; if (p(input.trim().toLowerCase())) return; }
  const { cmd, verb, args } = parse(input, index);
  commend('first-manifest');
  const lucky = on('lucky-ledger');
  const line = (c, when) => fill(pickLine(c, { when, random, lucky }).text, vars());
  switch (cmd.id) {
    case 'ward': {
      const up = args[0] !== 'down';
      say(line(cmd, up ? 'up' : 'down'), cmd.rows, cmd.reducedMotionRows); mood(up ? cmd.mood : { power: 5, morale: 0 }); return;
    }
    case 'navfix': {
      const l = pickLine(cmd, { random, lucky });
      say(l.text, cmd.rows, cmd.reducedMotionRows); mood(cmd.mood);
      if (l.weight <= 2) findBallast('dead-reckoning'); return;
    }
    case 'scuttlebutt':
      say(line(cmd), cmd.rows, cmd.reducedMotionRows); mood(cmd.mood); if (++scuttleCount >= 3) findBallast('short-rations'); return;
    case 'drop': return dropGame(cmd);
    case 'drill': return drillGame(cmd);
    case 'contact':
      say(line(cmd), ['waiting'], ['waiting']); cue('game-contact-ping');
      pending = a => {
        if (a !== 'ward' && a !== 'dark') return false;
        say(line(cmd, a), ['review'], ['review']); mood(cmd.mood); findLog('LW-04'); return true;
      };
      return;
    case 'salvage': {
      const n = Math.max(0, Math.round((new Date() - new Date(state.installed + 'T00:00:00')) / 864e5));
      say(fill(cmd.lines[0].text, { n }), cmd.rows, cmd.reducedMotionRows); mood(cmd.mood); return;
    }
    case 'logs': {
      for (const id of dayLogs(state.days)) findLog(id, true);
      if (verb === 'decrypt' || args[0]) {
        const id = (args[0] || '').toUpperCase();
        const log = L.logs.find(x => x.id === id);
        if (!log) return say('Name the log, Skipper. LW-00 through LW-07.', ['idle']);
        if (!state.found.logs.includes(id)) return say(`Log ${id} is still sealed. Keep sailing.`, ['idle']);
        say(`${id}: ${log.text}`, cmd.rows, cmd.reducedMotionRows); mood(cmd.mood); cue('egg-log-unlocked');
        if (id === 'LW-00') findBallast('loud-manifest');
        const others = L.logs.filter(x => x.id !== 'LW-07').every(x => state.found.logs.includes(x.id));
        if (others && graveyard()) findLog('LW-07');
        if (state.found.logs.length === 8) commend('logkeeper');
        return;
      }
      say(fill(cmd.lines[1].text, { k: state.found.logs.length }), cmd.rows, cmd.reducedMotionRows); return;
    }
    case 'ballast': {
      if (args.length) {
        const flag = args[args.length - 1]; const name = args.slice(0, -1).join('-');
        const tag = B.tags.find(t => t.id === name || t.id === args.join('-'));
        if (!tag || !state.found.ballast.includes(tag.id)) return say('No such tag in the hold. Yet.', ['idle']);
        state.ballastOn = state.ballastOn.filter(x => x !== tag.id);
        if (flag !== 'off') { state.ballastOn.push(tag.id); say(tag.line, ['review']); } else say(`${tag.name} stowed.`, ['idle']);
        save(); gauges(); return;
      }
      say(fill(cmd.lines[0].text, { k: state.found.ballast.length }), cmd.rows, cmd.reducedMotionRows); return;
    }
    case 'commendations':
      say(fill(cmd.lines[0].text, { k: state.found.commendations.length }), cmd.rows, cmd.reducedMotionRows); return;
    case 'haul':
      say(line(cmd), cmd.rows, cmd.reducedMotionRows); out('Haul checklists come from the $ferrin skill in your agent.', 'sys'); mood(cmd.mood); return;
    case 'ship-log': {
      if (!MEM || !MEM.facts().length) return say(pickLine(cmd, { when: 'empty', random }).text, cmd.rows);
      const f = MEM.facts(); say(fill(cmd.lines[0].text, { k: f.length, latest: f[f.length - 1].text }), cmd.rows);
      f.forEach(x => out(`${x.date}  ${x.text}`, 'sys')); return;
    }
    case 'remember': {
      const raw = input.trim().replace(/^[$/]ferrin\s+/i, '').slice(verb.length).trim().replace(/^that\s+/i, '');
      if (!MEM || !MEM.enabled) return say(pickLine(cmd, { when: 'off', random }).text, ['idle']);
      const r = MEM.add(raw);
      if (r.reason === 'secret') return say(pickLine(cmd, { when: 'secret', random }).text, ['idle']);
      if (!r.ok) return say('Give me a bit more to log, Skipper.', ['idle']);
      say(cmd.lines[0].text, cmd.rows); out(`Ship's log: ${r.fact.text}`, 'sys'); return;
    }
    case 'forget': {
      const q = args.join(' '); const n = MEM && q ? MEM.forget(q) : 0;
      return say(n ? fill(cmd.lines[0].text, { n }) : pickLine(cmd, { when: 'none', random }).text, cmd.rows);
    }
    case 'wipe-log':
      if (args[0] === 'confirm' && MEM) { MEM.wipe(); return say(pickLine(cmd, { when: 'done', random }).text, cmd.rows); }
      return say(cmd.lines[0].text, cmd.rows);
    case 'help':
      cmd.lines.forEach(l => say(l.text)); play(cmd.rows); return;
    default:
      say(line(cmd), cmd.rows, cmd.reducedMotionRows); mood(cmd.mood);
      if (cmd.id === 'sitrep') cue('cmd-sitrep'); if (cmd.id === 'hail') cue('state-wave'); if (cmd.id === 'scrub') cue('state-failed');
  }
}

// ---------------------------------------------------------------- mini-games
function dropGame(cmd) {
  if (busy) return; busy = true;
  let n = 0, hits = 0; const crate = $('#crate'); say(fill(cmd.lines[0].text), ['waiting'], ['waiting']);
  const next = () => {
    if (n++ >= 5) { busy = false; crate.style.display = 'none'; if (hits >= 5) { findBallast('lucky-ledger'); commend('steady-catch'); } return; }
    const dur = 1700, t0 = performance.now(); crate.style.display = 'block'; let caught = false;
    const onKey = e => {
      if (e.code !== 'Space' || e.target.matches('input')) return; e.preventDefault();
      const p = (performance.now() - t0) / dur;
      if (p > .62 && p < 1) { caught = true; }
      finish();
    };
    const finish = () => {
      removeEventListener('keydown', onKey); cancelAnimationFrame(raf); crate.style.display = 'none';
      if (caught) { hits++; say(pickLine(cmd, { when: 'hit', random }).text, ['jumping'], ['idle']); mood(cmd.mood); cue('game-score'); }
      else { say(pickLine(cmd, { when: 'miss', random }).text, ['failed'], ['idle']); cue('game-miss'); }
      setTimeout(next, 900);
    };
    let raf;
    const fall = t => {
      const p = (t - t0) / dur; crate.style.top = (reduce.matches ? 60 : p * 72) + '%';
      if (p >= 1) return finish();
      raf = requestAnimationFrame(fall);
    };
    addEventListener('keydown', onKey); raf = requestAnimationFrame(fall);
  };
  setTimeout(next, 600);
}
function drillGame(cmd) {
  if (busy) return; busy = true;
  const dirs = [['ArrowUp', 0], ['ArrowRight', 4], ['ArrowDown', 8], ['ArrowLeft', 12]];
  let round = 0, score = 0; say(cmd.lines[0].text, ['idle']);
  const ask = () => {
    if (round++ >= 4) { busy = false; say(pickLine(cmd, { when: score === 4 ? 'win' : 'partial', random }).text, ['waving']); return; }
    const [key, dir] = dirs[Math.floor(random() * 4)]; play([`look:${dir}`, `look:${dir}`, `look:${dir}`], [`look:${dir}`]);
    const onKey = e => {
      if (!e.key.startsWith('Arrow') || e.target.matches('input')) return; e.preventDefault(); removeEventListener('keydown', onKey);
      if (e.key === key) { score++; mood(cmd.mood); cue('game-score'); } else cue('game-miss');
      setTimeout(ask, 400);
    };
    addEventListener('keydown', onKey);
  };
  setTimeout(ask, 700);
}

// ---------------------------------------------------------------- hidden inputs
const sweep = keySequence(PERIMETER), hull = keySequence(HULL_ID);
let lastInput = Date.now(), idleSaid = false;
addEventListener('keydown', e => {
  lastInput = Date.now(); idleSaid = false;
  if ((e.key === 'h' || e.key === 'H') && !e.target.matches('input')) toggleHold();
  if (busy) return;
  const t = performance.now();
  if (sweep(e, t)) {
    const c = byId['perimeter-sweep']; say(c.lines[0].text, c.rows, c.reducedMotionRows); mood(c.mood); cue('egg-perimeter-sweep');
    findLog('LW-06'); findBallast('mirror-watch'); commend('perimeter-clear');
  }
  if (hull(e, t)) { const c = byId['hull-id']; say(c.lines[0].text, c.rows); mood(c.mood); cue('egg-longwake'); findLog('LW-00'); }
});
const tickle = clickBurst(5, 2000);
$('#puck').addEventListener('click', () => { if (tickle(performance.now())) { const c = byId['puck-tickle']; say(c.lines[0].text, c.rows, c.reducedMotionRows); } });
setInterval(() => { if (!idleSaid && Date.now() - lastInput > 10 * 60 * 1000) { idleSaid = true; const c = byId['long-idle']; say(c.lines[0].text, c.rows); } }, 30000);

// ---------------------------------------------------------------- dates and clock
function checkDates() {
  const d = today(); state.shown = state.shown || {};
  for (const ev of activeEvents(new Date(), E.events, state.installed)) {
    const k = d + ':' + ev.id; if (state.shown[k]) continue; state.shown[k] = 1;
    say(ev.line, ev.rows); mood({ morale: 3 });
    if (ev.id === 'graveyard-watch') { commend('graveyard-watch'); findBallast('night-cargo'); }
  }
  save();
}

// ---------------------------------------------------------------- controls
function toggleHold() { held = !held; $('#hold').setAttribute('aria-pressed', held); }
$('#hold').onclick = toggleHold;
$('#sound').onclick = async () => {
  if (!sfx) {
    try { const { FerrinSFX } = await import('../sfx/ferrin-sfx.js'); sfx = new FerrinSFX({ base: '../sfx/', format: 'ogg' }); await sfx.unlock(); await sfx.load(); }
    catch { out('Sound pack not found next to the preview.', 'sys'); sfx = null; return; }
    $('#sound').setAttribute('aria-pressed', 'true'); $('#sound').textContent = 'Sound on';
  } else { sfx.muted = !sfx.muted; $('#sound').setAttribute('aria-pressed', String(!sfx.muted)); $('#sound').textContent = sfx.muted ? 'Sound off' : 'Sound on'; }
};
$('#work').onclick = () => { play(['running', 'running', 'review'], ['review']); say('Crunching numbers. Coffee would help, if I drank it.'); setTimeout(() => say("Work's done. Inspect at your leisure."), 2400); cue('state-running-loop'); };
$('#error').onclick = () => { play(['failed', 'idle'], ['failed']); say('Fault logged. We regroup and try again.'); cue('state-failed'); };
$('#dock').onclick = () => { mood({ power: 15, sync: 15, morale: 15 }); say('Docked. Topping off. Thanks, Skipper.', ['waving']); };
$('#form').addEventListener('submit', e => { e.preventDefault(); const v = $('#cmd').value; $('#cmd').value = ''; run(v); });

// ---------------------------------------------------------------- start
gauges();
const away = lastDay && lastDay !== today();
if (away) say('Shore leave logged. Welcome back, Skipper.', ['waving']);
else say('Holding station, Skipper. All quiet on the manifest.', ['idle']);
for (const id of dayLogs(state.days)) findLog(id, true);
if (new Set(state.days).size >= 7) commend('seven-ports');
checkDates(); setInterval(checkDates, 10 * 60 * 1000);
save();
