# Creating or changing FERRIN's artwork

FERRIN's sprite atlas is drawn in code. There is no image-generation step.

1. Edit `tools/ferrin_spec.py`. It holds the palette, geometry and every pose, row by row. Never hand-edit PNGs.
2. Run `make art`. This renders frames (`tools/draw_frames.py`), composes `spritesheet.webp` (`tools/compose_atlas.py`) and rebuilds the previews (`tools/make_previews.py`).
3. Run `make verify`. The validator checks the host contract (1536 x 2288 lossless RGBA WebP, 8 x 11 cells of 192 x 208, exact frame counts), 10% padding, a stable puck baseline, no RGB residue under transparent pixels, and the hue guard (no blue or violet).
4. Open `docs/contact-sheet.png` and review every row: running-left faces left, idle is visibly alive, failed is sympathetic rather than scary.
5. Run `make package` to refresh `dist/`.

Style rules: no text, speech bubbles, glows, shadows, speed lines or detached effects in sprites. Every effect touches the character. Amber and mint only; coral appears only in the failed row.
