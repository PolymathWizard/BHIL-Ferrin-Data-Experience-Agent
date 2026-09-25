// Turn your private ip-denylist.txt (git-ignored, one term per line) into ip-denylist.sha256.
// The repo stores only hashes, never the names. Run: node scripts/ip-hash.mjs
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
const src = new URL('../ip-denylist.txt', import.meta.url);
if (!existsSync(src)) { console.error('ip-denylist.txt not found (create it locally; it is git-ignored)'); process.exit(1); }
const norm = s => s.toLowerCase().normalize('NFKD').replace(/[^\p{L}\p{N}\s]/gu, ' ').trim().split(/\s+/).join(' ');
const terms = readFileSync(src, 'utf8').split(/\r?\n/).map(norm).filter(t => t && t.split(' ').length <= 2);
const hashes = [...new Set(terms.map(t => createHash('sha256').update(t).digest('hex')))].sort();
writeFileSync(new URL('../ip-denylist.sha256', import.meta.url), hashes.join('\n') + '\n');
console.log(`wrote ${hashes.length} hashes (terms of one or two words) to ip-denylist.sha256`);
