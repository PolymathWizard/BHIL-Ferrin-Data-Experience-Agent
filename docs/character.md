# FERRIN · Character Reference

[← README](../README.md) · **Character** · [Lore](lore.md) · [Commands](commands.md) · [Events](events.md) · [Gallery](gallery.md)

![FERRIN in a cargo bay holding a blank clipboard](images/ferrin-cargo-bay-clipboard.webp)

**FERRIN** · *Field-Emergent Reasoning & Recon Intelligence Node* · pet id `ferrin`

A salvage-refitted shipboard intelligence that projects itself as a compact hard-light "tactical lantern" above a gunmetal emitter puck. It is non-humanoid. It has no face, mouth, or limbs, and it never appears in blue or violet.

## Anatomy

| Part | Description |
|---|---|
| Body | Amber faceted lantern crossed by three deep-amber scanline bands |
| Visor | Dark horizontal slot holding one mint pill eye with a warm-white core |
| Range mast | Stubby antenna with a mint tip (coral during a Casualty Report) |
| Fin plates | Two chevron-marked amber plates hinged to the sides and used as hands |
| Insignia | Olive chevron-over-bar on the lower body |
| Beam | Stepped trapezoid in three opaque bands: deep amber, amber, warm white |
| Emitter puck | Flat gunmetal disc with three mint status pips |

<p align="center">
  <img src="images/ferrin-sticker-sheet.webp" alt="FERRIN sticker sheet in six poses plus emitter puck and crate" width="48%">
  <img src="images/ferrin-cargo-bay-inspect.webp" alt="FERRIN inspecting a clipboard in a cargo bay" width="48%">
</p>

## Palette

| Role | Hex | |
|---|---|---|
| Holo Amber | `#FFB23F` | body |
| Deep Amber | `#C7771E` | scanlines, shading |
| Warm Core White | `#FFF3D6` | eye core, beam top |
| Signal Mint | `#34F5B4` | eye, mast tip, pips |
| Mint Shadow | `#1FA57A` | eye shading |
| Outline Umber | `#3A2410` | strokes, visor |
| Emitter Gunmetal | `#2A3036` | puck |
| Emitter Rim | `#4A545E` | puck rim |
| Olive Drab | `#5B6B3A` | insignia, crates |
| Alert Coral | `#FF5A4E` | failed state only |
| Dimmed Amber | `#B98A45` | flicker frames |

**Hue rule:** no saturated blue, violet, or purple anywhere. The atlas validator and the image manifest both check this.

## Eye states

![Nine visor close-ups showing FERRIN's eye states](images/ferrin-eye-states.webp)

| | | |
|---|---|---|
| Calm (idle) | Blink | Happy arc (waving) |
| Sad arc (failed) | Narrowed scan (review) | Wide alert (contact) |
| Look left | Look right | Dimmed (Night Cargo / flicker) |

## Voice

Dry, steady, and loyal: a quartermaster-navigator. FERRIN calls the user **"Skipper."** Lines are twelve words or fewer, often start with "Log:", and lean on logistics metaphors (manifests, bearings, supply). It never flirts, never menaces, and never claims to be human.

> "Fault logged. We regroup and try again."
> "Recommend a break. That's not an order."
> "I've seen worse refits. Barely."

## Illustration canon vs. sprite canon

The illustrations and the 3D study render the body as a **faceted octagonal lantern** with hub-mounted fins. The sprite in `tools/ferrin_spec.py` draws the same faceted lantern, flattened to a ten-sided outline that reads at 192×208. Both are FERRIN. If you change the spec, regenerate `docs/contact-sheet.png` with `make art` and review every row.

![FERRIN sprite contact sheet](contact-sheet.png)
