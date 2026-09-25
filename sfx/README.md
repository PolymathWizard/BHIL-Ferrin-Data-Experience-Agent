# FERRIN Drift Ops SFX

Thirty original sound effects for FERRIN, the salvage-refit shipboard AI. Every sound is synthesized from code in `tools/synth.py`. The pack contains no recorded samples and no third-party audio. Open `index.html` (served over HTTP, for example on GitHub Pages) to audition every cue and play a simulated work session.

## Sound identity

FERRIN sounds like a warm light in a cold metal hold. The palette is built from a few decisions that keep every cue recognizably part of the same character:

The key is **D major pentatonic** (D, E, F♯, A, B), so any two cues that overlap still sound consonant. The signature motif is the **Longwake call**, A4 → D5 → E5 → A5, which plays in full when a task finishes, in slow motion as the LONGWAKE easter egg, and as a two-note fragment when a lore log unlocks. FERRIN's voice is a *lantern tone*: a sine with soft second and third harmonics and a two-voice chorus detuned ±4 cents. The emitter hum sits on A2 (110 Hz) with a second tone half a hertz above it, so the bed slowly beats like a twin trap breathing. The real emitter runs at 40 kHz, far above hearing, so the hum is its audible shadow rather than a recording of it. Faults step outside the scale to C natural, which gives the coral cues their minor color without resorting to alarms. The room is a small Schroeder reverb tuned like a steel compartment.

Levels are set for a desktop companion that shares space with your work: background loops sit around −30 to −34 dBFS RMS, interface cues around −25, and events around −18 to −22, with every peak at or below −1 dBFS.

## Contents

Each sound ships as 48 kHz / 16-bit mono **WAV** (masters), **OGG** Vorbis q5, and **MP3** 160 kbps. `manifest.json` lists every sound with its trigger, duration, loudness and file paths.

### Sprite states

| Sound | Trigger | Length | What it does |
|---|---|---|---|
| `state-idle-loop` (loop) | idle | 8.00 s | Emitter hum with a slow twin-trap beat. Quiet bed while FERRIN stands watch. |
| `state-running-loop` (loop) | running | 4.00 s | Working: soft manifest ticks over the hum, four to a second. |
| `state-waiting-loop` (loop) | waiting | 6.00 s | Waiting on you: one patient mint ping every three seconds. |
| `state-review` | review | 1.90 s | Review: a scanline sweeps the lantern top to bottom, then two soft confirms. |
| `state-wave` | wave | 0.95 s | Wave hello: fin flutter and a rising two-note chirp. |
| `state-jump` | jump | 0.70 s | Hop: a rising blip, a beat of air, a soft landing on the beam. |
| `state-failed` | failed | 1.70 s | Fault: coral descent with a hologram flicker. Serious, never shrill. |
| `state-run` | running-left / running-right | 0.70 s | Scoot: a short hard-light whoosh with a small pitch bend. |

### Lifecycle events

| Sound | Trigger | Length | What it does |
|---|---|---|---|
| `evt-materialize` | app start / FERRIN appears | 5.00 s | Full build: three pips, the column rising in three stages, the swarm gathering, the Longwake call as the optic opens. |
| `evt-dematerialize` | app quit / FERRIN hides | 2.40 s | Stand down: the lantern sweeps away and the swarm scatters to the puck. |
| `evt-emitter-on` | emitter connected | 1.30 s | Puck powers up: low thunk and three pip ticks. No hologram yet. |
| `evt-task-complete` | agent finished | 1.30 s | Task done: the full Longwake call, bright and short. |
| `evt-blocked` | agent blocked / approval needed | 1.10 s | Needs you: two coral notes, repeated once. Firm, not an alarm. |
| `evt-hail` | notification | 0.90 s | Incoming hail: two quick mint pings. |

### Interface

| Sound | Trigger | Length | What it does |
|---|---|---|---|
| `ui-click` | click | 0.03 s | Tactile tick for buttons. |
| `ui-hover` | hover | 0.05 s | Barely-there brush for hover. |
| `ui-toggle-on` | toggle on | 0.22 s | Switch on: up a fourth. |
| `ui-toggle-off` | toggle off | 0.22 s | Switch off: down a fourth. |
| `ui-panel-open` | open panel | 0.38 s | Panel unfolds: short rising air and a light tick. |
| `ui-panel-close` | close panel | 0.32 s | Panel folds away: falling air. |
| `ui-error` | error | 0.30 s | Invalid input: a dull double buzz, low and brief. |

### Drift Ops commands and games

| Sound | Trigger | Length | What it does |
|---|---|---|---|
| `cmd-sitrep` | $ferrin sitrep | 1.00 s | Status report: teletype chatter and a closing tone. |
| `game-contact-ping` | contact game | 2.20 s | Contact: a sonar-style ping with a long metallic tail. |
| `game-score` | game score | 0.40 s | Point scored in drop or drill. |
| `game-miss` | game miss | 0.25 s | Missed: a flat downward blip, no scolding. |

### Easter eggs

| Sound | Trigger | Length | What it does |
|---|---|---|---|
| `egg-perimeter-sweep` | Perimeter Sweep code | 1.80 s | Key code accepted: four compass blips (up, right, down, left) then an open chord. |
| `egg-longwake` | LONGWAKE typed code | 4.50 s | LONGWAKE: a distant ship horn under the call, slowed down, in a cold empty hold. |
| `egg-commendation` | commendation unlocked | 1.80 s | Commendation earned: a bright pentatonic arpeggio with a shimmer. |
| `egg-log-unlocked` | LW log unlocked | 1.50 s | Lore log found: tape spin-up, teletype, and the first two notes of the call. |
| `egg-ballast-tag` | Ballast Tag earned | 1.10 s | Ballast Tag stamped: a cargo stamp thunk with a ring. |

## Using it

`ferrin-sfx.js` is a dependency-free Web Audio helper. It loads the manifest, decodes every sound, and maps agent status to a background loop and an entry cue.

```js
import { FerrinSFX } from './sfx/ferrin-sfx.js';
const sfx = new FerrinSFX({ base: './sfx/', format: 'ogg' });
await sfx.load();
button.onclick = () => sfx.unlock();   // browsers need one user gesture before audio

sfx.play('evt-materialize');
sfx.setState('running');   // working ticks loop
sfx.setState('waiting');   // 'needs you' cue, then the patient ping loop
sfx.setState('done');      // Longwake call
sfx.setState('idle');      // back to the emitter hum
sfx.volume = 0.5; sfx.muted = false;
```

Play loops from the WAV files. MP3 encoders add silence at the start and end of a file, which leaves an audible gap on every repeat. OGG and WAV loop cleanly.

Keep FERRIN polite: default to muted or a low volume, give users a one-click mute, and don't play the idle loop unless they opt in. A pet that hums at you unasked gets uninstalled.

## Rebuilding or changing sounds

`tools/synth.py` is a build tool, not part of the runtime. Unlike the rest of the repo it needs NumPy and SciPy for filtering and reverb, plus ffmpeg for the OGG and MP3 exports. Nothing at runtime depends on it: the pet, the audition page and the voice prototype only read the rendered files.

```bash
pip install numpy scipy
python3 tools/synth.py .     # rewrites wav/, ogg/, mp3/ and manifest.json in place
```

The random seed is fixed, so the same code always renders the same files. Each sound is a small decorated function, which makes it easy to change a note, a length or a level and re-render.

## Integrity

`SHA256SUMS` lists a hash for every rendered file. Re-rendering with the fixed seed reproduces the same audio; a changed hash means a sound changed.

## License

Code (`ferrin-sfx.js`, `tools/synth.py`, `index.html`) is MIT. The rendered audio files and `manifest.json` descriptions are CC BY 4.0.
