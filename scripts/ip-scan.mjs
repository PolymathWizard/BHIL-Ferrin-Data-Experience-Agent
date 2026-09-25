// Fail if any committed text contains a denylisted word or two-word phrase.
// Compares SHA-256 hashes of every lowercase token and bigram against ip-denylist.sha256.
import { readFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { textFiles } from './files.mjs';
const list = new URL('../ip-denylist.sha256', import.meta.url);
if (!existsSync(list)) { console.log('ip-scan: no ip-denylist.sha256, skipping (see scripts/ip-hash.mjs)'); process.exit(0); }
const deny = new Set(readFileSync(list, 'utf8').split('\n').map(s => s.trim()).filter(Boolean));
const h = s => createHash('sha256').update(s).digest('hex');
let hits = 0;
for (const f of textFiles()) {
  const words = readFileSync(f, 'utf8').toLowerCase().normalize('NFKD').replace(/[^\p{L}\p{N}\s]/gu, ' ').split(/\s+/).filter(Boolean);
  words.forEach((w, i) => {
    for (const t of [w, i + 1 < words.length ? w + ' ' + words[i + 1] : null]) {
      if (t && deny.has(h(t))) { hits++; console.error(`ip-scan: denylisted term in ${f} (hash ${h(t).slice(0, 10)})`); }
    }
  });
}
if (hits) { console.error(`ip-scan: ${hits} match(es)`); process.exit(1); }
console.log(`ip-scan: clean (${deny.size} hashed terms)`);
