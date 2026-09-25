// Tracked text files (git ls-files when available, otherwise a directory walk).
import { execSync } from 'node:child_process';
import { readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
const TEXT = /\.(md|json|js|mjs|py|html|css|txt|yml|yaml|toml|svg)$|^(Makefile|LICENSE|\.gitignore|\.gitattributes)$/;
const SKIP = /(^|\/)(node_modules|build|\.git|__pycache__)(\/|$)|^ip-denylist\.(txt|sha256)$/;
export function textFiles() {
  let files;
  try { files = execSync('git ls-files', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().split('\n').filter(Boolean); }
  catch { files = walk('.'); }
  return files.filter(f => !SKIP.test(f) && TEXT.test(f.split('/').pop()));
}
function walk(dir) {
  const out = [];
  for (const n of readdirSync(dir)) {
    const p = dir === '.' ? n : join(dir, n);
    if (SKIP.test(p)) continue;
    statSync(p).isDirectory() ? out.push(...walk(p)) : out.push(p);
  }
  return out;
}
