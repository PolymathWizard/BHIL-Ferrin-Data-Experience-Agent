import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
await import('../../shared/ferrin-memory.js');
const M = globalThis.FerrinMemory;
const store = () => { const m = new Map(); return { getItem: k => m.get(k) ?? null, setItem: (k, v) => m.set(k, String(v)), _m: m }; };
const fixed = () => new Date(2026, 8, 25);

test('adds, dedupes and persists facts', () => {
  const s = store(), a = M.create(s, { now: fixed });
  assert.ok(a.add('Prefers short commit messages').ok);
  assert.ok(a.add('prefers short commit messages.').duplicate);
  const b = M.create(s, { now: fixed });
  assert.equal(b.facts().length, 1); assert.equal(b.facts()[0].date, '2026-09-25');
});
test('never stores secrets', () => {
  const a = M.create(store());
  for (const t of ['my password is hunter22', 'api key sk-test-abcdef1234567890', 'card 4111 1111 1111 1111', 'token ghp_abcdefghijklmnop1234'])
    assert.equal(a.add(t).reason, 'secret', t);
  assert.equal(a.facts().length, 0);
});
test('forget, remove and wipe', () => {
  const a = M.create(store());
  a.add('Working on the auth service'); a.add('Likes dark themes'); a.add('Auth service ships Friday');
  assert.equal(a.forget('auth'), 2); assert.equal(a.facts().length, 1);
  a.remove(0); assert.equal(a.facts().length, 0);
  a.add('One more thing'); a.wipe(); assert.equal(a.facts().length, 0);
});
test('switching memory off records nothing', () => {
  const a = M.create(store()); a.enabled = false;
  assert.equal(a.add('Something durable here').reason, 'off');
});
test('caps the log and keeps the name', () => {
  const a = M.create(store()); a.add("Skipper's name is Rowan", 'name');
  for (let i = 0; i < M.MAX_FACTS + 10; i++) a.add(`fact number ${i}`);
  assert.equal(a.facts().length, M.MAX_FACTS); assert.equal(a.name(), 'Rowan');
  assert.ok(a.summary(200).length <= 200);
});
test('export and import round-trip', () => {
  const a = M.create(store()); a.add('Ships on Fridays'); a.add("Skipper's name is Ada", 'name');
  const b = M.create(store()); assert.equal(b.importJSON(a.exportJSON()), 2); assert.equal(b.name(), 'Ada');
  assert.throws(() => b.importJSON('{"nope":1}'));
});
test('extracts explicit and safe automatic facts', () => {
  assert.deepEqual(M.extract('remember that I deploy on Fridays').facts[0].text, 'I deploy on Fridays');
  assert.equal(M.extract('Call me Rowan').facts[0].text, "Skipper's name is Rowan");
  assert.equal(M.extract('call me later').facts.length, 0);
  assert.equal(M.extract("I'm building a bird-watching app.").facts[0].text, 'Skipper is working on a bird-watching app');
  assert.equal(M.extract('I prefer tabs over spaces').facts[0].text, 'Skipper prefers tabs over spaces');
  assert.equal(M.extract('I like that').facts.length, 0);
});
test('memory module makes no network calls', () => {
  const src = readFileSync(new URL('../../shared/ferrin-memory.js', import.meta.url), 'utf8');
  assert.ok(!/fetch\(|XMLHttpRequest|sendBeacon|WebSocket/.test(src));
});
