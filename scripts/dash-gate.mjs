// House style: no em dashes (U+2014) or en dashes (U+2013) anywhere in text files. Checks raw bytes.
import { readFileSync } from 'node:fs';
import { textFiles } from './files.mjs';
const EM = Buffer.from([0xe2, 0x80, 0x94]), EN = Buffer.from([0xe2, 0x80, 0x93]);
let bad = 0;
for (const f of textFiles()) {
  const b = readFileSync(f);
  for (const [name, seq] of [['em dash', EM], ['en dash', EN]]) {
    let i = b.indexOf(seq);
    while (i !== -1) { bad++; const line = b.subarray(0, i).toString('utf8').split('\n').length; console.error(`dash-gate: ${name} in ${f}:${line}`); i = b.indexOf(seq, i + 1); }
  }
}
if (bad) process.exit(1);
console.log('dash-gate: clean');
