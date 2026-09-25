# Visual Pipeline

[← README](../../README.md) · [Gallery](../gallery.md) · [Prompt pack](prompts.md)

FERRIN has two separate visual tracks.

| Track | Source | Output | Deterministic |
|---|---|---|---|
| **Sprite atlas** | `tools/ferrin_spec.py` → `tools/draw_frames.py` | `spritesheet.webp` | Yes |
| **Illustrations** | [`prompts.md`](prompts.md) → image model | `docs/images/*.webp` | No. Recorded in the manifest |

Illustrations never feed the atlas.

## Adding an illustration

1. Generate it from a prompt ID in `prompts.md`. Reuse `images/ferrin-cargo-bay-clipboard.webp` as the character reference so FERRIN stays consistent.
2. Run it through the QC checklist in `prompts.md` §03. It must have no face or limbs, no blue or violet, no stray text, and no franchise resemblance.
3. Convert it to WebP (max width 1600, quality ~84) and give it a kebab-case name under `docs/images/`.
4. Add an entry to `docs/images/manifest.json` with the file, `prompt_id`, `alt`, `page`, engine, date, sha256, and hue-guard result.
5. Link it with alt text from the right page, and add it to `docs/gallery.md`.

## Current QC status (v1.0, 2026-09-25)

- All 16 images pass the hue guard (0% saturated blue/violet above near-black).
- The commendation badges image was flattened onto dark gunmetal and cropped to remove transparent areas.
- `social-preview.png` (1280×640) is cropped from the hero banner. Upload it under **Settings → General → Social preview** on GitHub.
- The illustrations show a faceted octagonal body, while the sprite spec uses a flat hexagon. See [Character → canon](../character.md#illustration-canon-vs-sprite-canon).
