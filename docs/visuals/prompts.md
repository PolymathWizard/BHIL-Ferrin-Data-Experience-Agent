# FERRIN Support Visuals: Image Prompt Pack

**REF FERRIN-VIS-001 · v1.0** · For `docs/`, README, social, and release assets

```
┌─ FERRIN VISUAL PIPELINE ──────────────────────────────────────┐
│ LOCK CHARACTER → LOCK PALETTE → RENDER CATALOG → IP QC → SHIP │
└───────────────────────────────────────────────────────────────┘
```

**22** prompts · **6** families · **4** lock blocks · **3** negative stacks

These prompts produce *support* imagery: key art, lore scenes, UI mockups, icons, and marketing cards. They do **not** produce the sprite atlas. The atlas stays code-drawn from `tools/ferrin_spec.py` so it remains deterministic and auditable. Treat every generated image as illustrative and check it against the spec before shipping it.

Each prompt uses slots. Paste the lock blocks in Section 01 wherever a slot appears, then append the listed negative stacks.

---

## Section 01 · Lock Blocks

### `{FERRIN}`: the character, every time

```
FERRIN, a non-humanoid holographic ship intelligence: a compact rounded-hexagon
"tactical lantern" body in warm amber, hard-edged and mostly opaque, crossed by
three thick horizontal darker-amber scanline bands. A dark horizontal visor slot
across the upper third holds a single glowing mint-green pill-shaped eye with a
warm white core. A short stubby antenna on top with a mint tip. Two chevron-shaped
amber fin plates hinged to either side of the body like small hands. A small olive
chevron-over-bar insignia on the lower body. It hovers above a flat gunmetal
emitter puck with three mint status lights, connected by a stepped trapezoid
projection beam made of three opaque bands of deep amber, amber, and warm white.
No face, no mouth, no limbs, no human form.
```

### `{PALETTE_LOCK}`

```
Palette restricted to: holo amber #FFB23F, deep amber #C7771E, warm core white
#FFF3D6, signal mint #34F5B4, mint shadow #1FA57A, outline umber #3A2410,
gunmetal #2A3036, rim grey #4A545E, olive drab #5B6B3A. Alert coral #FF5A4E only
where stated. No blue, no violet, no purple, no pink anywhere in the image.
```

### `{WORLD}`: the setting

```
The Drift: a sparse belt of derelict relay stations and survey debris in deep
space, lit by a distant amber star. Hardware is utilitarian, logistics-first:
cargo crates, stencilled manifest plates, cable runs, riveted gunmetal
bulkheads, worn olive paint. Survey-and-salvage, not warfare.
```

### `{NO_TEXT}`

```
Render no readable text, letters, numbers, logos, watermarks, or signatures,
except where the prompt explicitly asks for blank placeholder panels.
```

### Negative stacks

| Stack | Applies to | Content |
|---|---|---|
| `NEG-F1` IP | All prompts | humanoid hologram, female hologram, translucent blue figure, circuit-pattern skin, glowing tattoo lines, power armour soldier, visored super-soldier, recognisable game or film franchise style, existing character silhouette, licensed vehicle or weapon design, franchise logo or insignia, ring-shaped megastructure |
| `NEG-F2` Character drift | Any prompt showing FERRIN | human face, mouth, teeth, arms, legs, feet, cute chibi eyes, two eyes, round sphere body, cube body, soft glow bloom, heavy translucency, particle sparkles detached from body, blue or purple light |
| `NEG-F3` Render quality | All prompts | gibberish text, warped letters, extra fins, asymmetric fins, melted geometry, muddy palette, oversaturated neon, lens flare streaks, watermark, signature |

Engine notes: in Midjourney, put the stacks in `--no`, keep `--stylize` low (50 to 150) to limit house style, and pin one approved FERRIN render as `--cref`/`--sref` after the first good result. In other engines, add the stacks as a negative prompt, or append the words "Avoid:" followed by the stack.

---

## Section 02 · The Catalog

### F-A · Character Reference

#### A01 · Hero Key Art
> {FERRIN} hovering at centre frame inside a dim riveted cargo bay, its amber light casting warm pools across stacked crates, mint eye glancing slightly toward the viewer. Three-quarter view, slightly low angle, cinematic 35mm, shallow haze in the air, strong rim light from the beam. {WORLD} {PALETTE_LOCK} {NO_TEXT}

| **Style** Cinematic 3D render | **AR** 16:9 | **Use** README hero, release banner | **Neg** F1 · F2 · F3 |

#### A02 · Turnaround Model Sheet
> Character turnaround of {FERRIN}: front, three-quarter, side, back, and top views in a row on a flat warm-grey background, even studio lighting, orthographic, identical scale and baseline across all views, clean silhouettes. {PALETTE_LOCK} {NO_TEXT}

| **Style** Clean 3D model sheet | **AR** 21:9 | **Use** `docs/character-sheet.png`, spec reference | **Neg** F1 · F2 · F3 |

#### A03 · Expression Sheet (Eye States)
> A 3×3 grid of close-ups of {FERRIN}'s visor only, each tile showing one eye state: calm pill, blink slit, happy upward arc, sad downward arc, narrowed scan, wide alert, looking left, looking right, dimmed flicker. Identical framing in every tile, flat dark backdrop. {PALETTE_LOCK} {NO_TEXT}

| **Style** Flat vector | **AR** 1:1 | **Use** Mood reference for skill/preview | **Neg** F1 · F2 · F3 |

#### A04 · Emitter Puck Product Shot
> Product photography of a flat gunmetal emitter puck with a brushed rim and three small mint status lights, resting on dark matte metal, a faint stepped amber projection beam rising from it with nothing projected yet. 100mm macro, softbox from above, crisp reflections. {PALETTE_LOCK} {NO_TEXT}

| **Style** Photoreal product | **AR** 4:5 | **Use** Lore card, "salvage" command art | **Neg** F1 · F3 |

#### A05 · Mood Lineup
> Nine small {FERRIN} figures in a neat row on a dark backdrop, each posed for a state: at rest, leaning right, leaning left, waving one fin, mid-hop, drooping with dimmed amber and a coral antenna tip, tilted and waiting with one fin extended, eye scanning, leaning forward inspecting. Same scale and baseline for every figure. {PALETTE_LOCK} {NO_TEXT}

| **Style** Flat vector | **AR** 21:9 | **Use** README animation table | **Neg** F1 · F2 · F3 |

### F-B · Lore Environments (world only, FERRIN optional)

#### B01 · RSV Longwake, Derelict
> A long, slender survey frigate drifting powered-down among debris, hull patched and scorched, rows of dark portholes, one faint amber light still burning deep in the cargo section. Wide shot, distant amber star low in frame, deep shadow. {WORLD} {PALETTE_LOCK} {NO_TEXT}

| **Style** Matte painting | **AR** 21:9 | **Use** `longwake` lore, LW log header | **Neg** F1 · F3 |

#### B02 · Relay Kestrel-Nine
> A skeletal derelict relay station of truss arms and dish antennas, one dish still slowly tracking, a single mint beacon blinking on its spine, drifting ice crystals. Isometric three-quarter view. {WORLD} {PALETTE_LOCK} {NO_TEXT}

| **Style** Stylised 3D | **AR** 16:9 | **Use** `navfix` art, LW-02 | **Neg** F1 · F3 |

#### B03 · The Salvage Moment
> Gloved hands of an unseen engineer lifting the gunmetal emitter puck out of a dusty wall locker aboard a derelict station; the puck's three mint lights have just flickered on. Close crop, torch light, dust in the beam. {WORLD} {PALETTE_LOCK} {NO_TEXT}

| **Style** Cinematic still | **AR** 3:2 | **Use** `salvage` command, onboarding | **Neg** F1 · F3 |

#### B04 · The Murmur
> A vast dark void beyond a relay station's viewport where faint amber interference ripples bend the starfield like heat haze. Nothing is visible and there is no creature, only the sense of something passing. {FERRIN} small in the foreground with its lantern shuttered to a thin sliver. {PALETTE_LOCK} {NO_TEXT}

| **Style** Atmospheric painting | **AR** 16:9 | **Use** `contact` drill, LW-04 | **Neg** F1 · F2 · F3 |

#### B05 · Tenders One Through Four
> Four small boxy utility drones lined up on a hangar deck, each a different wear state, stencilled amber stripes, a fifth empty charging cradle at the end of the row. {FERRIN} hovering beside them like a quartermaster at inspection. {WORLD} {PALETTE_LOCK} {NO_TEXT}

| **Style** Stylised 3D | **AR** 16:9 | **Use** `muster` command | **Neg** F1 · F2 · F3 |

### F-C · UI and Product Mockups

#### C01 · Preview Console
> Clean UI mockup of a dark browser dashboard: {FERRIN} rendered in a panel on the left, three horizontal gauges labelled with blank placeholder bars on the right, a command input line at the bottom, a small speech panel beside the character. Amber and mint accents on gunmetal, flat design, crisp grid. {PALETTE_LOCK} Blank placeholder panels only, no readable text.

| **Style** Flat UI | **AR** 16:10 | **Use** README screenshot placeholder | **Neg** F1 · F3 |

#### C02 · Log Decrypt Screen
> Terminal-style UI of a document being decrypted: blocky redaction bars dissolving into blank lines, a water-stain texture at the corner, a mint progress bar, and a small {FERRIN} icon in the header. Monospace aesthetic, dark umber background. {PALETTE_LOCK} Blank placeholder lines only.

| **Style** Flat UI | **AR** 16:9 | **Use** Recovered Longwake Logs | **Neg** F1 · F3 |

#### C03 · Desktop Context Shot
> A tidy developer desk at night, a monitor showing an out-of-focus code editor, and a tiny {FERRIN} perched at the lower corner of the screen as a desktop companion, its amber glow reflecting on the desk. 35mm, practical lighting, cosy. {PALETTE_LOCK} Screen content blurred, no readable text.

| **Style** Photoreal lifestyle | **AR** 16:9 | **Use** Launch post, social | **Neg** F1 · F2 · F3 |

### F-D · Icons, Badges, Stickers

#### D01 · App / Repo Icon
> Icon of {FERRIN}'s front view only, centred on a rounded-square gunmetal tile, bold simplified shapes, thick umber outline, readable at 32px. {PALETTE_LOCK} {NO_TEXT}

| **Style** Flat vector icon | **AR** 1:1 | **Use** Favicon, repo avatar | **Neg** F1 · F2 · F3 |

#### D02 · Commendation Badges (set of 7)
> Seven circular stamped-metal commendation badges in a row, olive and amber enamel, each with a different simple emblem: a single crate, a compass rose with sixteen ticks, an open ledger, a crescent moon over a lantern, six stacked tags, seven dots in an arc, a crate caught in two fins. Uniform size and bevel, dark background. {PALETTE_LOCK} {NO_TEXT}

| **Style** Flat vector, embossed | **AR** 21:9 | **Use** `commendations` ledger | **Neg** F1 · F3 |

#### D03 · Ballast Tags (set of 6)
> Six rectangular stamped cargo tags on short chains, worn gunmetal with coloured edges, each marked with a distinct simple glyph: a hidden gauge needle, a cut ration bar, a loudspeaker cone, a mirrored arrow pair, a crescent moon, a four-leaf clover. Laid out flat on a crate lid, top-down. {PALETTE_LOCK} {NO_TEXT}

| **Style** Photoreal props | **AR** 3:2 | **Use** `ballast` hub | **Neg** F1 · F3 |

#### D04 · Sticker Sheet
> Die-cut sticker sheet of {FERRIN} in six poses (waving, hopping, inspecting, drooping, scanning, resting) plus the emitter puck and a single cargo crate, each with a thick white border, flat shading, on a light grey backing sheet. {PALETTE_LOCK} {NO_TEXT}

| **Style** Flat vector sticker | **AR** 4:5 | **Use** Merch, social, community | **Neg** F1 · F2 · F3 |

### F-E · Seasonal Events

#### E01 · Longwake Launch Day (Nov 14)
> {FERRIN} hovering beside a small vintage photo frame on a bulkhead shelf; the frame holds a silhouette of a frigate at launch; a single lit amber candle-style lamp beside it. Warm, quiet, commemorative. {PALETTE_LOCK} {NO_TEXT}

| **AR** 1:1 | **Neg** F1 · F2 · F3 |

#### E02 · Manifest Mix-up (Apr 1)
> {FERRIN} with a startled wide eye, hovering above an overflowing cargo crate bursting with rolled-up socks spilling across the deck. Comedic, bright. {WORLD} {PALETTE_LOCK} {NO_TEXT}

| **AR** 1:1 | **Neg** F1 · F2 · F3 |

#### E03 · Derelict Night (Oct 31)
> A derelict relay corridor with flickering amber strip lights, long shadows, and {FERRIN} peeking around a bulkhead edge with a narrowed eye. Spooky but gentle, no monsters. {PALETTE_LOCK} {NO_TEXT}

| **AR** 4:5 | **Neg** F1 · F2 · F3 |

#### E04 · Year-End Stocktake (Dec 31)
> {FERRIN} holding a small clipboard between its fins beside a neat stack of labelled crates (blank labels), with a distant amber starburst through a viewport. Satisfied, celebratory. {PALETTE_LOCK} {NO_TEXT}

| **AR** 1:1 | **Neg** F1 · F2 · F3 |

### F-F · Marketing Cards

#### F01 · Social Launch Card
> {FERRIN} on the left third, emitter beam catching drifting dust, with a large clean empty gunmetal panel on the right two-thirds reserved for headline text added later. Strong amber rim light, minimal background. {PALETTE_LOCK} {NO_TEXT}

| **Style** 3D render | **AR** 1.91:1 (OG image) | **Use** GitHub social preview, LinkedIn | **Neg** F1 · F2 · F3 |

---

## Section 03 · QC Checklist (before any image ships)

1. **Character match.** Rounded-hexagon body, one mint pill eye in a visor slot, two chevron fins, stubby antenna, puck and stepped beam. Reject renders with a face, limbs, or two eyes.
2. **Palette.** Sample the image. Any blue, violet, or purple area fails, which mirrors the atlas hue guard.
3. **IP.** Read the image against `NEG-F1`. If it reminds anyone of a specific franchise character, vehicle, or armour, regenerate it. Run file names and alt text through `scripts/ip-scan.mjs`.
4. **Text.** No stray pseudo-text. Add real text in your design tool, never in the engine.
5. **Provenance.** Record engine, version, seed, and prompt ID (e.g. `FERRIN-VIS-001/A01`) in `docs/visuals/manifest.json`, and label the images AI-generated in the README credits.
