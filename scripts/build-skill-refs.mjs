// Generate skills/ferrin/references/commands.md from preview/data/*.json. Run: node scripts/build-skill-refs.mjs
import { readFileSync, writeFileSync } from 'node:fs';
const read = n => JSON.parse(readFileSync(new URL(`../preview/data/${n}.json`, import.meta.url)));
const C = read('commands'), L = read('logs'), B = read('ballast'), E = read('events');
const where = c => c.surfaces.includes('skill') ? (c.surfaces.includes('preview') ? 'both' : 'skill') : 'preview only';
const rows = [];
rows.push('# Drift Ops catalog', '', `Generated from preview/data/commands.json (v${C.version}). Do not edit by hand.`, '',
  'Invoke as `$ferrin <verb>` (Codex) or `/ferrin <verb>` (Claude Code). Every line is 12 words or fewer.', '',
  '| Verb | Where | Rarity | Lines |', '|---|---|---|---|');
for (const c of C.commands) {
  if (!c.triggers.verbs.length) continue;
  const lines = c.lines.map(l => (l.when ? `(${l.when}) ` : '') + (l.weight <= 2 ? '(rare) ' : '') + l.text).join('<br>');
  rows.push(`| ${c.triggers.verbs.map(v => '`' + v + '`').join(', ')} | ${where(c)} | ${c.rarity} | ${lines} |`);
}
rows.push('', '## Hidden inputs (preview only)', '');
for (const c of C.commands.filter(c => !c.triggers.verbs.length && c.id !== 'unknown'))
  rows.push(`- **${c.id}**: ${c.lines[0].text}`);
rows.push('', '## Recovered Longwake Logs', '', 'Report only logs the user says they have found.', '');
for (const l of L.logs) rows.push(`- **${l.id}** (unlock: ${l.unlock}): ${l.text}`);
rows.push('', '## Ballast Tags', '', 'Cosmetic or voice-only modifiers. They stack and never make anything harder.', '');
for (const t of B.tags) rows.push(`- **${t.name}**: ${t.effect} Line: "${t.line}"`);
rows.push('', '## Dated events', '');
for (const e of E.events) rows.push(`- **${e.name}**: ${e.line}`);
rows.push('', '## Commendations', '', 'Distinct days, never streaks. Nothing is ever lost.', '');
for (const c of E.commendations) rows.push(`- **${c.name}**: ${c.earnedBy}`);
rows.push('', `Unknown verb: "${C.commands.find(c => c.id === 'unknown').lines[0].text}"`, '');
writeFileSync(new URL('../skills/ferrin/references/commands.md', import.meta.url), rows.join('\n'));
console.log('wrote skills/ferrin/references/commands.md');
