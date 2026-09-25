# FERRIN (fork of ruvnet/ruPet, MIT)

## Commands
- make art      # draw frames -> compose atlas -> previews
- make verify   # atlas validator + unit tests + IP scan + dash gate (must pass before any commit)
- make package  # dist/ferrin.zip, dist/ferrin-skill.zip, dist/SHA256SUMS.txt

## Rules
- IMPORTANT: original IP only. No names, lore, logos or signature looks from any existing franchise. Honor ./ip-denylist.txt (git-ignored; never print or commit it).
- Never alter the ruvnet line in LICENSE. Credits live in ATTRIBUTION.md.
- Atlas contract is fixed: 1536x2288, 8x11, 192x208, rows and frames per tools/ferrin_spec.py. Edit art only through ferrin_spec.py.
- No text, glow, shadows or detached effects in sprites. No blue or violet hues.
- Command data has one source of truth: preview/data/*.json. Run `make refs` after editing it.
- No em dashes or en dashes in any text file (scripts/dash-gate.mjs).
- Never commit keys. voice/brain.js is git-ignored and must point at a server-side proxy.
- Memory stores facts, never transcripts or secrets. Skill rules: skills/ferrin/references/memory.md. Browser: shared/ferrin-memory.js.

## Workflow
- Plan first for multi-file changes; after art changes, open docs/contact-sheet.png and review every row.
- Conventional commits scoped to the area: feat(ferrin):, fix(preview):, docs:, chore(ci):.
