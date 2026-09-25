"""FERRIN sound effects pack: procedural synthesis.
Every sound is generated from code: no samples, no third-party audio.
Palette: D major pentatonic (D E F# A B). Signature 'Longwake call' = A4 -> D5 -> E5 -> A5.
"""
import numpy as np, json, os, wave
from scipy import signal

SR = 48000
rng = np.random.default_rng(1147)  # fixed seed -> reproducible pack

# ---------------------------------------------------------------- pitch
A4 = 440.0
def hz(note):
    names = {'C':-9,'C#':-8,'D':-7,'D#':-6,'E':-5,'F':-4,'F#':-3,'G':-2,'G#':-1,'A':0,'A#':1,'B':2}
    n, o = note[:-1], int(note[-1])
    return A4 * 2 ** ((names[n] + (o - 4) * 12) / 12)
PENTA = ['D','E','F#','A','B']

# ---------------------------------------------------------------- primitives
def t_(d): return np.arange(int(d * SR)) / SR
def silence(d): return np.zeros(int(d * SR))

def phase_from(freq):
    """freq: scalar or per-sample array -> phase (radians)"""
    f = np.broadcast_to(freq, freq.shape if hasattr(freq, 'shape') else ())
    return 2 * np.pi * np.cumsum(f) / SR

def osc(freq, d, kind='sine', detune_c=0.0):
    n = int(d * SR)
    f = np.full(n, freq, float) if np.isscalar(freq) else np.asarray(freq, float)[:n]
    f = f * 2 ** (detune_c / 1200)
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == 'sine': return np.sin(ph)
    if kind == 'tri':  # soft triangle via few odd harmonics (band-limited enough for these ranges)
        return (np.sin(ph) - np.sin(3 * ph) / 9 + np.sin(5 * ph) / 25) * 0.95
    if kind == 'warm':  # lantern tone: fundamental + gentle 2nd and 3rd
        return np.sin(ph) + 0.32 * np.sin(2 * ph + .3) + 0.12 * np.sin(3 * ph + .7)
    if kind == 'square':
        return sum(np.sin(k * ph) / k for k in (1, 3, 5, 7, 9)) * 0.9
    raise ValueError(kind)

def lantern(freq, d, detune=4.0):
    """FERRIN's voice: warm tone with a two-voice chorus."""
    return (osc(freq, d, 'warm', -detune) + osc(freq, d, 'warm', detune)) * 0.5

def fm_bell(freq, d, ratio=3.5, index=1.5, decay=3.0):
    n = int(d * SR); tt = np.arange(n) / SR
    env_i = np.exp(-tt * decay * 1.6)
    mod = np.sin(2 * np.pi * freq * ratio * tt) * index * env_i
    return np.sin(2 * np.pi * freq * tt + mod)

def env_adsr(n, a=.005, dcy=.05, s=.7, r=.1):
    sr = SR
    A, D, R = int(a * sr), int(dcy * sr), int(r * sr)
    S = max(0, n - A - D - R)
    e = np.concatenate([np.linspace(0, 1, A, endpoint=False) if A else [],
                        np.linspace(1, s, D, endpoint=False) if D else [],
                        np.full(S, s), np.linspace(s, 0, R) if R else []])
    return np.pad(e, (0, max(0, n - len(e))))[:n]

def env_exp(n, a=.004, decay=8.0):
    tt = np.arange(n) / SR
    atk = np.clip(tt / max(a, 1e-4), 0, 1)
    return atk * np.exp(-tt * decay)

def noise(d, color='white'):
    n = int(d * SR); x = rng.standard_normal(n)
    if color == 'pink':
        b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
        x = signal.lfilter(b, a, x) * 3.5
    return x

def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def lp(x, fc, order=2):
    sos = signal.butter(order, fc, 'lowpass', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def hp(x, fc, order=2):
    sos = signal.butter(order, fc, 'highpass', fs=SR, output='sos'); return signal.sosfilt(sos, x)

def svf_sweep(x, f0, f1, q=4.0, curve='exp'):
    """time-varying band-pass (Chamberlin SVF), for scanline sweeps"""
    n = len(x)
    f = np.geomspace(f0, f1, n) if curve == 'exp' else np.linspace(f0, f1, n)
    F = 2 * np.sin(np.pi * np.minimum(f, SR / 6) / SR); Q = 1 / q
    low = band = 0.0; out = np.empty(n)
    for i in range(n):
        high = x[i] - low - Q * band
        band += F[i] * high
        low += F[i] * band
        out[i] = band
    return out

def reverb(x, mix=.25, size=1.0, damp=3500):
    """small Schroeder room: 4 combs + 2 all-passes, a metal ship compartment"""
    combs = [(int(.0297 * SR * size), .80), (int(.0371 * SR * size), .78), (int(.0411 * SR * size), .76), (int(.0437 * SR * size), .74)]
    pad = np.concatenate([x, np.zeros(int(1.2 * SR * size))])
    wet = np.zeros_like(pad)
    for D, g in combs:
        a = np.zeros(D + 1); a[0] = 1; a[-1] = -g
        wet += signal.lfilter([1], a, pad)
    wet = lp(wet / 4, damp)
    for D, g in [(int(.005 * SR), .7), (int(.0017 * SR), .7)]:
        b = np.zeros(D + 1); b[0] = -g; b[-1] = 1
        a = np.zeros(D + 1); a[0] = 1; a[-1] = -g
        wet = signal.lfilter(b, a, wet)
    return pad * (1 - mix) + wet * mix

def place(buf, x, at, gain=1.0):
    i = int(at * SR); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j - i] * gain
    return buf

def note(freq, d, voice='lantern', a=.006, decay=None, s=.6, r=.08, gain=1.0):
    n = int(d * SR)
    if voice == 'lantern': x = lantern(freq, d)
    elif voice == 'bell': x = fm_bell(freq, d, decay=decay or 3.0)
    elif voice == 'glass': x = osc(freq, d) + .25 * osc(freq * 2.01, d) + .08 * osc(freq * 4.02, d)
    elif voice == 'soft': x = osc(freq, d, 'tri')
    else: x = osc(freq, d, voice)
    e = env_exp(n, a, decay) if decay else env_adsr(n, a, .05, s, r)
    return x * e * gain

def click(gain=1.0, tone=2600, d=.018):
    """a small mechanical tick: resonant noise burst"""
    x = bp(noise(d), tone * .7, tone * 1.4, 2) * env_exp(int(d * SR), .0005, 260)
    return x * gain

def thump(freq=70, d=.25, gain=1.0):
    n = int(d * SR); tt = np.arange(n) / SR
    f = freq * (1 + 1.6 * np.exp(-tt * 38))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, .002, 14) * gain

def grains(d, density=120, lo=2500, hi=9000, rise=False, fall=False, seedshift=0):
    """particle swarm: scattered micro-ticks"""
    buf = silence(d); n = int(d * density)
    times = np.sort(rng.random(n) * d)
    for k, tm in enumerate(times):
        p = tm / d
        if rise and rng.random() > p ** .7: continue
        if fall and rng.random() > (1 - p) ** .7: continue
        g = .15 + .35 * rng.random()
        tone = lo + (hi - lo) * rng.random()
        place(buf, click(g, tone, .006 + .01 * rng.random()), tm)
    return buf

def mix(*xs):
    n=max(len(a) for a in xs); o=np.zeros(n)
    for a in xs: o[:len(a)]+=a
    return o

def fade(x, fi=.003, fo=.01):
    n = len(x); a = min(int(fi * SR), n // 2); b = min(int(fo * SR), n // 2)
    if a: x[:a] *= np.linspace(0, 1, a)
    if b: x[-b:] *= np.linspace(1, 0, b) ** 1.5
    return x

# ---------------------------------------------------------------- loudness
def rms_db(x):
    active = x[np.abs(x) > 1e-4]
    if len(active) == 0: return -120
    return 20 * np.log10(np.sqrt(np.mean(active ** 2)) + 1e-12)

def normalize(x, target_rms_db, peak_db=-1.0):
    x = x - np.mean(x)
    g = 10 ** ((target_rms_db - rms_db(x)) / 20)
    x = x * g
    pk = np.max(np.abs(x)); lim = 10 ** (peak_db / 20)
    if pk > lim:
        x = np.tanh(x / lim * 0.9) * lim / np.tanh(0.9) if pk > lim * 1.6 else x * (lim / pk)
    return x

def make_loop(render, L, xf=.35):
    """render(total_seconds) -> array; returns a seamless loop of length L"""
    y = render(L + xf)
    n, m = int(L * SR), int(xf * SR)
    head, tail = y[:m].copy(), y[n:n + m]
    w = np.linspace(0, np.pi / 2, m)
    y = y[:n].copy(); y[:m] = head * np.sin(w) + tail * np.cos(w)
    return y

# ---------------------------------------------------------------- the pack
SOUNDS = []
def sfx(id, group, desc, trigger, level, loop=False):
    def deco(fn):
        SOUNDS.append(dict(id=id, group=group, desc=desc, trigger=trigger, level=level, loop=loop, fn=fn)); return fn
    return deco

HUM = 110.0  # A2, the emitter's audible 'shadow'. The real array runs at 40 kHz, far above hearing.

def emitter_hum(d, beat=.5, bright=1.0):
    tt = t_(d)
    x = (np.sin(2 * np.pi * HUM * tt) + .5 * np.sin(2 * np.pi * (HUM + beat) * tt) +
         .22 * np.sin(2 * np.pi * 2 * HUM * tt + 1) + .08 * bright * np.sin(2 * np.pi * 3 * (HUM + beat / 2) * tt))
    shimmer = lp(noise(d, 'pink'), 1400) * .05 * bright
    return x * .5 + shimmer

LONGWAKE = [('A4', 0), ('D5', .12), ('E5', .24), ('A5', .38)]

# ---- states (map to the 9 sprite rows the host app drives) ----
@sfx('state-idle-loop', 'states', 'Emitter hum with a slow twin-trap beat. Quiet bed while FERRIN stands watch.', 'idle', -34, loop=True)
def _():
    def r(d):
        x = emitter_hum(d, beat=.5)
        tt = t_(d); x *= .85 + .15 * np.sin(2 * np.pi * .125 * tt)
        return x
    return make_loop(r, 8.0)

@sfx('state-running-loop', 'states', 'Working: soft manifest ticks over the hum, four to a second.', 'running', -30, loop=True)
def _():
    L = 4.0
    def r(d):
        x = emitter_hum(d, beat=1.0, bright=.6) * .55
        seq = ['D6', 'A5', 'E6', 'A5', 'F#6', 'A5', 'E6', 'B5']
        for k in range(int(d * 4) + 1):
            f = hz(seq[k % len(seq)])
            place(x, note(f, .09, 'glass', decay=38, gain=.22), k * .25)
            place(x, click(.12, 3200), k * .25 + .125)
        return x
    return make_loop(r, L, xf=.08)

@sfx('state-waiting-loop', 'states', 'Waiting on you: one patient mint ping every three seconds.', 'waiting', -32, loop=True)
def _():
    def r(d):
        x = emitter_hum(d, beat=.33) * .35
        for k in range(int(d / 3) + 1):
            p = note(hz('D6'), 1.4, 'bell', decay=3.2, gain=.5); place(p, note(hz('A6'), 1.0, 'bell', decay=5, gain=.12), 0)
            place(x, reverb(p, .3)[:int(2.4 * SR)], k * 3.0 + .2)
        return x
    return make_loop(r, 6.0, xf=.2)

@sfx('state-review', 'states', 'Review: a scanline sweeps the lantern top to bottom, then two soft confirms.', 'review', -24)
def _():
    d = 1.9; x = silence(d)
    sweep = svf_sweep(noise(1.1, 'pink'), 7000, 900, q=6) * env_adsr(int(1.1 * SR), .08, .1, .8, .3)
    place(x, sweep * .6, 0)
    place(x, note(hz('A5'), .35, 'lantern', decay=9, gain=.5), 1.05)
    place(x, note(hz('D6'), .5, 'lantern', decay=7, gain=.5), 1.25)
    return reverb(x, .2)[:int(d * SR)]

@sfx('state-wave', 'states', 'Wave hello: fin flutter and a rising two-note chirp.', 'wave', -22)
def _():
    d = .95; x = silence(d)
    for k in range(3): place(x, bp(noise(.09), 900, 3000) * env_exp(int(.09 * SR), .01, 30) * .35, .05 + k * .14)
    n = int(.4 * SR); f = np.geomspace(hz('A5'), hz('D6'), n)
    place(x, lantern(f, .4) * env_adsr(n, .01, .05, .7, .15) * .45, .32)
    return reverb(x, .18)[:int(d * SR)]

@sfx('state-jump', 'states', 'Hop: a rising blip, a beat of air, a soft landing on the beam.', 'jump', -22)
def _():
    d = .7; x = silence(d); n = int(.16 * SR)
    place(x, osc(np.geomspace(hz('D5'), hz('A6'), n), .16, 'tri') * env_exp(n, .003, 14) * .5, 0)
    place(x, mix(thump(95, .22, .5), note(hz('A4'), .2, 'lantern', decay=20, gain=.25)), .42)
    return x

@sfx('state-failed', 'states', 'Fault: coral descent with a hologram flicker. Serious, never shrill.', 'failed', -22)
def _():
    d = 1.7; x = silence(d)
    for k, (nm, at) in enumerate([('E5', 0), ('C5', .18), ('A4', .38)]):
        nn = note(hz(nm), .5 if k < 2 else 1.0, 'lantern', r=.25, gain=.5)
        wob = 1 + .004 * np.sin(2 * np.pi * 7 * t_(len(nn) / SR))
        place(x, nn * wob, at)
    flick = grains(.9, density=60, lo=1500, hi=5000, fall=True) * .7
    place(x, flick, .35)
    tt = t_(d); gate = 1 - .35 * (np.sin(2 * np.pi * 9 * tt) > .6) * (tt > .4) * (tt < 1.2)
    x = lp(x * gate, 4200)
    return reverb(x, .22)[:int(d * SR)]

@sfx('state-run', 'states', 'Scoot: a short hard-light whoosh with a small pitch bend.', 'running-left / running-right', -26)
def _():
    d = .7; n = int(d * SR)
    x = svf_sweep(noise(d, 'pink'), 600, 2600, q=2.5) * env_adsr(n, .12, .1, .7, .35)
    x += osc(np.linspace(hz('D4'), hz('A4'), n), d, 'sine') * env_adsr(n, .1, .1, .5, .3) * .12
    return x

# ---- lifecycle events ----
@sfx('evt-materialize', 'events', 'Full build: three pips, the column rising in three stages, the swarm gathering, the Longwake call as the optic opens.', 'app start / FERRIN appears', -18)
def _():
    d = 5.0; x = silence(d)
    for k in range(3): place(x, mix(click(.6, 2100), note(hz('D6'), .12, 'glass', decay=30, gain=.18)), .1 + k * .4)
    place(x, thump(55, .6, .8), 1.25)
    for k, nm in enumerate(['D3', 'A3', 'D4']):
        n = int(1.6 * SR)
        place(x, lantern(hz(nm), 1.6) * env_adsr(n, .25, .2, .6, .9) * .3, 1.4 + k * .45)
    place(x, lp(grains(2.4, density=260, lo=2000, hi=9000, rise=True), 7000) * .38, 2.0)
    n = int(2.2 * SR); sweep = svf_sweep(noise(2.2, 'pink'), 400, 6000, q=5) * env_adsr(n, .6, .2, .7, .6)
    place(x, sweep * .24, 2.0)
    for nm, at in LONGWAKE: place(x, mix(note(hz(nm), .7, 'bell', decay=3.4, gain=.34), note(hz(nm), .7, 'lantern', decay=5, gain=.2)), 3.85 + at)
    x = reverb(x, .26, size=1.3)
    return fade(x[:int(d * SR)], fo=.3)

@sfx('evt-dematerialize', 'events', 'Stand down: the lantern sweeps away and the swarm scatters to the puck.', 'app quit / FERRIN hides', -20)
def _():
    d = 2.4; x = silence(d); n = int(1.6 * SR)
    place(x, svf_sweep(noise(1.6, 'pink'), 6000, 350, q=5) * env_adsr(n, .05, .2, .7, .7) * .45, 0)
    place(x, grains(1.6, density=220, lo=2000, hi=9000, fall=True) * .6, .1)
    for k, nm in enumerate(['A5', 'E5', 'D5']): place(x, note(hz(nm), .5, 'lantern', decay=6, gain=.25), .15 + k * .16)
    place(x, thump(50, .5, .5), 1.55)
    return fade(reverb(x, .25)[:int(d * SR)], fo=.2)

@sfx('evt-emitter-on', 'events', 'Puck powers up: low thunk and three pip ticks. No hologram yet.', 'emitter connected', -22)
def _():
    d = 1.3; x = silence(d)
    place(x, thump(62, .5, 1.0), 0)
    n = int(.9 * SR); place(x, osc(np.geomspace(55, 110, n), .9, 'warm') * env_adsr(n, .3, .1, .6, .4) * .22, .05)
    for k in range(3): place(x, click(.55, 2200), .5 + k * .18)
    return x

@sfx('evt-task-complete', 'events', 'Task done: the full Longwake call, bright and short.', 'agent finished', -18)
def _():
    d = 1.3; x = silence(d)
    for nm, at in LONGWAKE: place(x, mix(note(hz(nm), .55, 'lantern', decay=5.5, gain=.42), note(hz(nm) * 2, .5, 'bell', decay=5, gain=.12)), at)
    return reverb(x, .22)[:int(d * SR)]

@sfx('evt-blocked', 'events', 'Needs you: two coral notes, repeated once. Firm, not an alarm.', 'agent blocked / approval needed', -20)
def _():
    d = 1.1; x = silence(d)
    for r0 in (0, .42):
        place(x, note(hz('F#5'), .16, 'lantern', decay=12, gain=.45), r0)
        place(x, note(hz('C5'), .22, 'lantern', decay=9, gain=.45), r0 + .15)
    return reverb(x, .15)[:int(d * SR)]

@sfx('evt-hail', 'events', 'Incoming hail: two quick mint pings.', 'notification', -21)
def _():
    d = .9; x = silence(d)
    place(x, note(hz('E6'), .4, 'bell', decay=6, gain=.4), 0)
    place(x, note(hz('A6'), .5, 'bell', decay=5, gain=.4), .11)
    return reverb(x, .25)[:int(d * SR)]

# ---- UI ----
@sfx('ui-click', 'ui', 'Tactile tick for buttons.', 'click', -26)
def _(): return fade(mix(click(1.0, 2600, .03), note(hz('A5'), .03, 'soft', decay=90, gain=.25)))

@sfx('ui-hover', 'ui', 'Barely-there brush for hover.', 'hover', -34)
def _(): return fade(bp(noise(.05), 3000, 7000) * env_exp(int(.05 * SR), .004, 70) * .6)

@sfx('ui-toggle-on', 'ui', 'Switch on: up a fourth.', 'toggle on', -25)
def _():
    x = silence(.22); place(x, note(hz('D5'), .08, 'lantern', decay=30, gain=.5), 0); place(x, note(hz('A5'), .12, 'lantern', decay=22, gain=.5), .06); return fade(x)

@sfx('ui-toggle-off', 'ui', 'Switch off: down a fourth.', 'toggle off', -26)
def _():
    x = silence(.22); place(x, note(hz('A5'), .08, 'lantern', decay=30, gain=.5), 0); place(x, note(hz('E5'), .12, 'lantern', decay=22, gain=.5), .06); return fade(x)

@sfx('ui-panel-open', 'ui', 'Panel unfolds: short rising air and a light tick.', 'open panel', -26)
def _():
    d = .38; n = int(.3 * SR); x = silence(d)
    place(x, svf_sweep(noise(.3, 'pink'), 800, 5000, q=3) * env_adsr(n, .08, .05, .6, .12) * .5, 0)
    place(x, click(.5, 3000), .27); return fade(x)

@sfx('ui-panel-close', 'ui', 'Panel folds away: falling air.', 'close panel', -27)
def _():
    d = .32; n = int(.3 * SR); x = silence(d)
    place(x, svf_sweep(noise(.3, 'pink'), 5000, 700, q=3) * env_adsr(n, .02, .05, .6, .18) * .5, 0); return fade(x)

@sfx('ui-error', 'ui', 'Invalid input: a dull double buzz, low and brief.', 'error', -25)
def _():
    x = silence(.3)
    for at in (0, .13):
        nn = int(.09 * SR); place(x, lp(osc(hz('D3'), .09, 'square'), 1200) * env_adsr(nn, .003, .02, .7, .03) * .5, at)
    return fade(x)

# ---- Drift Ops commands & easter eggs ----
@sfx('cmd-sitrep', 'commands', 'Status report: teletype chatter and a closing tone.', '$ferrin sitrep', -24)
def _():
    d = 1.0; x = silence(d)
    for k in range(9): place(x, click(.35 + .3 * rng.random(), 1800 + 1400 * rng.random(), .012), .03 + k * .065 + .02 * rng.random())
    place(x, note(hz('D6'), .35, 'glass', decay=10, gain=.3), .68); return x

@sfx('game-contact-ping', 'commands', 'Contact: a sonar-style ping with a long metallic tail.', 'contact game', -22)
def _():
    d = 2.2; x = silence(d)
    p = osc(hz('B5'), 1.6, 'sine') * env_exp(int(1.6 * SR), .002, 2.6) + .3 * osc(hz('B5') * 2.76, 1.6) * env_exp(int(1.6 * SR), .002, 6)
    place(x, p * .5, 0); return fade(reverb(x, .4, size=1.6)[:int(d * SR)], fo=.3)

@sfx('game-score', 'commands', 'Point scored in drop or drill.', 'game score', -23)
def _():
    x = silence(.4)
    for k, nm in enumerate(['A5', 'D6', 'F#6']): place(x, note(hz(nm), .15, 'glass', decay=20, gain=.35), k * .05)
    return fade(x)

@sfx('game-miss', 'commands', 'Missed: a flat downward blip, no scolding.', 'game miss', -25)
def _():
    n = int(.25 * SR); x = osc(np.geomspace(hz('A4'), hz('E4'), n), .25, 'tri') * env_exp(n, .004, 12) * .5; return fade(x)

@sfx('egg-perimeter-sweep', 'eggs', 'Key code accepted: four compass blips (up, right, down, left) then an open chord.', 'Perimeter Sweep code', -19)
def _():
    d = 1.8; x = silence(d)
    for k, nm in enumerate(['D5', 'E5', 'A4', 'B4', 'D5', 'E5', 'A4', 'B4']):
        place(x, note(hz(nm), .07, 'glass', decay=35, gain=.3), k * .085)
    for nm in ['D5', 'A5', 'E6']: place(x, note(hz(nm), 1.0, 'lantern', a=.02, r=.5, gain=.22), .78)
    return reverb(x, .25)[:int(d * SR)]

@sfx('egg-longwake', 'eggs', 'LONGWAKE: a distant ship horn under the call, slowed down, in a cold empty hold.', 'LONGWAKE typed code', -20)
def _():
    d = 4.5; x = silence(d); n = int(3.0 * SR)
    horn = (osc(hz('D2'), 3.0, 'warm') + .6 * osc(hz('A2'), 3.0, 'warm', 6)) * env_adsr(n, .5, .3, .7, 1.2)
    place(x, lp(horn, 700) * .45, 0)
    for nm, at in LONGWAKE: place(x, note(hz(nm), 1.4, 'bell', decay=1.6, gain=.3), .9 + at * 2.4)
    x = reverb(x, .45, size=2.0, damp=2500)
    return fade(x[:int(d * SR)], fo=.6)

@sfx('egg-commendation', 'eggs', 'Commendation earned: a bright pentatonic arpeggio with a shimmer.', 'commendation unlocked', -19)
def _():
    d = 1.8; x = silence(d)
    for k, nm in enumerate(['D5', 'E5', 'F#5', 'A5', 'B5', 'D6']): place(x, note(hz(nm), .7, 'bell', decay=4.5, gain=.28), k * .07)
    place(x, grains(.9, density=90, lo=6000, hi=11000, fall=True) * .25, .45)
    return reverb(x, .3)[:int(d * SR)]

@sfx('egg-log-unlocked', 'eggs', 'Lore log found: tape spin-up, teletype, and the first two notes of the call.', 'LW log unlocked', -21)
def _():
    d = 1.5; x = silence(d); n = int(.35 * SR)
    place(x, osc(np.geomspace(80, 420, n), .35, 'square') * env_adsr(n, .05, .05, .6, .1) * .08, 0)
    for k in range(6): place(x, click(.4, 2000 + 900 * (k % 3), .012), .35 + k * .06)
    place(x, note(hz('A4'), .5, 'lantern', decay=5, gain=.35), .78); place(x, note(hz('D5'), .6, 'lantern', decay=4, gain=.35), .92)
    return reverb(x, .2)[:int(d * SR)]

@sfx('egg-ballast-tag', 'eggs', 'Ballast Tag stamped: a cargo stamp thunk with a ring.', 'Ballast Tag earned', -20)
def _():
    d = 1.1; x = silence(d)
    place(x, mix(thump(85, .3, .9), bp(noise(.05), 400, 2500) * env_exp(int(.05 * SR), .001, 60) * .6), 0)
    place(x, note(hz('A5'), .9, 'bell', decay=3.5, gain=.18), .03)
    return reverb(x, .2)[:int(d * SR)]

# ---------------------------------------------------------------- render
def write_wav(path, x):
    y = np.clip(x, -1, 1); pcm = (y * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

if __name__ == '__main__':
    import subprocess, sys
    out = sys.argv[1]; os.makedirs(out + '/wav', exist_ok=True); os.makedirs(out + '/ogg', exist_ok=True); os.makedirs(out + '/mp3', exist_ok=True)
    manifest = []
    for s in SOUNDS:
        x = np.asarray(s['fn'](), float)
        if not s['loop']: x = fade(x, .002, .02)
        x = normalize(x, s['level'])
        f = s['id']
        write_wav(f'{out}/wav/{f}.wav', x)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{out}/wav/{f}.wav', '-c:a', 'libvorbis', '-q:a', '5', f'{out}/ogg/{f}.ogg'], check=True)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{out}/wav/{f}.wav', '-c:a', 'libmp3lame', '-b:a', '160k', f'{out}/mp3/{f}.mp3'], check=True)
        pk = 20 * np.log10(np.max(np.abs(x)) + 1e-12)
        manifest.append(dict(id=f, group=s['group'], trigger=s['trigger'], description=s['desc'], loop=s['loop'],
                             duration_s=round(len(x) / SR, 3), rms_dbfs=round(rms_db(x), 1), peak_dbfs=round(pk, 1),
                             files=dict(wav=f'wav/{f}.wav', ogg=f'ogg/{f}.ogg', mp3=f'mp3/{f}.mp3')))
        print(f"{f:24s} {len(x)/SR:5.2f}s  rms {rms_db(x):6.1f}  peak {pk:5.1f}  loop={s['loop']}")
    json.dump(dict(name='FERRIN Drift Ops SFX', version='1.0.0', sample_rate=SR, channels=1, bit_depth=16,
                   key='D major pentatonic', motif='Longwake call: A4 D5 E5 A5', sounds=manifest), open(out + '/manifest.json', 'w'), indent=2)
