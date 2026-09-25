import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = p => readFileSync(new URL('../../' + p, import.meta.url), 'utf8');
test('preview plays the committed atlas', () => { assert.match(read('preview/ferrin.js'), /\.\.\/spritesheet\.webp/); });
test('preview and voice make no calls to outside hosts', () => {
  for (const f of ['preview/ferrin.js', 'preview/commands.js']) assert.ok(!/fetch\(\s*['"`]https?:/.test(read(f)), f);
  const v = read('voice/index.html');
  assert.ok(!/api\.anthropic|api\.openai|sk-[a-z]{2,}-/i.test(v), 'no provider endpoints or keys in the voice page');
});
test('voice brain hook is opt-in and git-ignored', () => {
  assert.match(read('.gitignore'), /^voice\/brain\.js$/m);
  assert.match(read('voice/index.html'), /FERRIN_BRAIN/);
});
