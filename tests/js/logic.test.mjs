import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildIndex, parse, keySequence, clickBurst, applyMood, defaultState, activeEvents, voice, pickLine, rng, rowRef, PERIMETER, HULL_ID } from '../../preview/commands.js';
const C = JSON.parse(readFileSync(new URL('../../preview/data/commands.json', import.meta.url)));
const E = JSON.parse(readFileSync(new URL('../../preview/data/events.json', import.meta.url)));
const idx = buildIndex(C.commands); idx.set('__unknown__', C.commands.find(c => c.id === 'unknown'));
const key = (k, typing = false) => ({ key: k, target: typing ? { closest: () => true } : { closest: () => null } });

test('parser handles namespaces, multi-word verbs and unknowns', () => {
  assert.equal(parse('$ferrin sitrep', idx).cmd.id, 'sitrep');
  assert.equal(parse('/ferrin ward down', idx).args[0], 'down');
  assert.equal(parse('Tell me a joke!', idx).cmd.id, 'scuttlebutt');
  assert.equal(parse('status report', idx).cmd.id, 'sitrep');
  assert.equal(parse('decrypt LW-03', idx).args[0], 'lw-03');
  assert.equal(parse('blorp', idx).cmd.id, 'unknown');
});
test('Perimeter Sweep matches, ignores typing, resets after timeout, tolerates overlap', () => {
  let s = keySequence(PERIMETER), t = 0, hit = false;
  for (const k of PERIMETER) hit = s(key(k), t += 100);
  assert.ok(hit);
  s = keySequence(PERIMETER); t = 0; hit = false;
  for (const k of PERIMETER) hit = s(key(k, true), t += 100) || hit;
  assert.ok(!hit, 'must ignore keys typed into a field');
  s = keySequence(PERIMETER); t = 0; hit = false;
  for (const [i, k] of PERIMETER.entries()) hit = s(key(k), t += (i === 4 ? 5000 : 100));
  assert.ok(!hit, 'must reset after a pause');
  s = keySequence(PERIMETER); t = 0; hit = false;
  for (const k of ['ArrowUp', ...PERIMETER]) hit = s(key(k), t += 100);
  assert.ok(hit, 'an overlapping prefix still matches');
  const h = keySequence(HULL_ID); t = 0; hit = false;
  for (const ch of 'LONGWAKE') hit = h(key(ch), t += 100);
  assert.ok(hit, 'typed hull ID is case-insensitive');
});
test('click burst needs 5 clicks inside the window', () => {
  const b = clickBurst(5, 2000);
  assert.ok(![0, 300, 600, 900].some(t => b(t))); assert.ok(b(1200));
  const c = clickBurst(5, 2000); [0, 900, 1800, 2700].forEach(t => c(t)); assert.ok(!c(3600));
});
test('mood is forgiving: floor 25, cap 100, +15 per day, morale never drops, no decay', () => {
  const s = defaultState(new Date(2026, 0, 1)); s.power = 30; s.morale = 90;
  applyMood(s, { power: -10 }, 'd1'); assert.equal(s.power, 25);
  applyMood(s, { morale: -10 }, 'd1'); assert.equal(s.morale, 90);
  applyMood(s, { sync: 10 }, 'd1'); applyMood(s, { sync: 10 }, 'd1'); assert.equal(s.sync, 95);
  applyMood(s, { morale: 10 }, 'd2'); assert.equal(s.morale, 100);
  const before = JSON.stringify([s.power, s.sync, s.morale]);
  applyMood(s, {}, 'd31'); assert.equal(JSON.stringify([s.power, s.sync, s.morale]), before, '30 days away changes nothing');
});
test('dated events fire only on their dates, including the year rollover', () => {
  const on = d => activeEvents(d, E.events, '2025-06-01').map(e => e.id);
  assert.ok(on(new Date(2026, 10, 14, 12)).includes('longwake-launch-day'));
  assert.ok(!on(new Date(2026, 10, 15, 12)).includes('longwake-launch-day'));
  assert.ok(on(new Date(2026, 11, 31, 12)).includes('year-end-stocktake'));
  assert.ok(on(new Date(2027, 0, 1, 12)).includes('year-end-stocktake'));
  assert.ok(!on(new Date(2027, 0, 2, 12)).includes('year-end-stocktake'));
  assert.ok(on(new Date(2026, 5, 1, 12)).includes('salvage-day'));
  assert.ok(on(new Date(2026, 5, 2, 2)).includes('graveyard-watch'));
  assert.ok(!on(new Date(2026, 5, 2, 5)).includes('graveyard-watch'));
});
test('Short Rations keeps every line to 5 words; Loud Manifest shouts', () => {
  for (const c of C.commands) for (const l of c.lines) assert.ok(voice(l.text, ['short-rations']).split(/\s+/).length <= 5);
  assert.match(voice('Holding station.', ['loud-manifest']), /^MF-\d{4}: HOLDING STATION\.$/);
});
test('Lucky Ledger triples rare lines; rows resolve to atlas cells', () => {
  const nav = C.commands.find(c => c.id === 'navfix'); const count = lucky => { const r = rng(7); let n = 0; for (let i = 0; i < 4000; i++) if (pickLine(nav, { random: r, lucky }).weight === 1) n++; return n; };
  assert.ok(count(true) > count(false) * 2);
  assert.deepEqual(rowRef('look:9'), { row: 10, start: 1, frames: 1 });
  assert.deepEqual(rowRef('failed'), { row: 5, start: 0, frames: 8 });
});
