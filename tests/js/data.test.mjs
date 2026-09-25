import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { HOST_BUILTINS } from '../../preview/commands.js';
const read = p => JSON.parse(readFileSync(new URL('../../' + p, import.meta.url)));
const C = read('preview/data/commands.json'), L = read('preview/data/logs.json'), B = read('preview/data/ballast.json'), E = read('preview/data/events.json');
const words = s => s.trim().split(/\s+/).length;
const ROW = /^(idle|running-right|running-left|waving|jumping|failed|waiting|running|review|look:([0-9]|1[0-5]))$/;

test('every line is 12 words or fewer', () => {
  const all = [...C.commands.flatMap(c => c.lines.map(l => l.text)), ...L.logs.map(l => l.text), ...B.tags.map(t => t.line), ...E.events.map(e => e.line),
    ...Object.values(read('voice/lines.json').lines).flat()];
  for (const s of all) assert.ok(words(s) <= 12, `too long: ${s}`);
});
test('rows and reduced-motion rows use the host row names', () => {
  for (const c of C.commands) for (const r of [...c.rows, ...c.reducedMotionRows]) assert.match(r, ROW, `${c.id}: ${r}`);
  for (const e of E.events) for (const r of e.rows) assert.match(r, ROW);
});
test('hidden and rumored entries declare a reduced-motion fallback', () => {
  for (const c of C.commands.filter(c => c.rarity !== 'standard')) assert.ok(c.reducedMotionRows.length > 0, c.id);
});
test('mood deltas stay within -10..+10 and rarity is known', () => {
  for (const c of C.commands) {
    for (const v of Object.values(c.mood)) assert.ok(v >= -10 && v <= 10, c.id);
    assert.ok(['standard', 'rumored', 'hidden', 'rare', 'dated'].includes(c.rarity), c.id);
  }
});
test('verbs are unique and only help overlaps a host built-in (always namespaced)', () => {
  const seen = new Set();
  for (const c of C.commands) for (const v of c.triggers.verbs) {
    assert.ok(!seen.has(v), `duplicate verb ${v}`); seen.add(v);
    if (HOST_BUILTINS.includes(v)) assert.equal(v, 'help');
  }
});
test('skill never documents bare host slash commands', () => {
  const dir = new URL('../../skills/ferrin/', import.meta.url);
  const files = ['SKILL.md', ...readdirSync(new URL('references/', dir)).map(f => 'references/' + f)];
  for (const f of files) {
    const t = readFileSync(new URL(f, dir), 'utf8');
    for (const b of HOST_BUILTINS) assert.ok(!new RegExp(`(^|[\\s\`(])/${b}\\b`).test(t), `${f} mentions /${b}`);
  }
});
test('eight logs, six ballast tags, seven commendations', () => {
  assert.equal(L.logs.length, 8); assert.equal(B.tags.length, 6); assert.equal(E.commendations.length, 7);
});
