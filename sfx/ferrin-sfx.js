/* FERRIN SFX player: tiny Web Audio helper for the Drift Ops sound pack.
 * Usage:
 *   import { FerrinSFX } from './ferrin-sfx.js';
 *   const sfx = new FerrinSFX({ base: './sfx/', format: 'ogg' });  // 'ogg' | 'mp3' | 'wav'
 *   await sfx.load();                 // reads manifest.json and decodes every sound
 *   sfx.setState('running');          // swaps the background loop to match agent status
 *   sfx.play('evt-task-complete');    // one-shot
 *   sfx.volume = 0.6; sfx.muted = true;
 * Browsers only start audio after a user gesture; call sfx.unlock() from a click handler.
 * Loops use WAV by default because MP3 encoders pad the start and end, which breaks seamless looping.
 */
export class FerrinSFX {
  constructor({ base = './', format = 'ogg', loopFormat = 'wav', volume = 0.7 } = {}) {
    this.base = base; this.format = format; this.loopFormat = loopFormat;
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    this.master = this.ctx.createGain(); this.master.connect(this.ctx.destination);
    this.buffers = new Map(); this.manifest = null; this.loop = null; this._vol = volume; this._muted = false;
    this.master.gain.value = volume;
    // agent status -> background loop (null = silence)
    this.stateLoops = { idle: 'state-idle-loop', running: 'state-running-loop', waiting: 'state-waiting-loop', review: 'state-idle-loop', failed: null };
    // agent status -> one-shot played on entry
    this.stateCues = { review: 'state-review', failed: 'state-failed', waiting: 'evt-blocked', done: 'evt-task-complete', wave: 'state-wave', jump: 'state-jump' };
  }
  async load() {
    this.manifest = await (await fetch(this.base + 'manifest.json')).json();
    await Promise.all(this.manifest.sounds.map(async s => {
      const fmt = s.loop ? this.loopFormat : this.format;
      const data = await (await fetch(this.base + s.files[fmt])).arrayBuffer();
      this.buffers.set(s.id, await this.ctx.decodeAudioData(data));
    }));
    return this;
  }
  unlock() { if (this.ctx.state !== 'running') return this.ctx.resume(); }
  get volume() { return this._vol; }
  set volume(v) { this._vol = Math.max(0, Math.min(1, v)); this._apply(); }
  get muted() { return this._muted; }
  set muted(m) { this._muted = !!m; this._apply(); }
  _apply() { this.master.gain.setTargetAtTime(this._muted ? 0 : this._vol, this.ctx.currentTime, 0.03); }
  play(id, { gain = 1 } = {}) {
    const buf = this.buffers.get(id); if (!buf) return null;
    const src = this.ctx.createBufferSource(), g = this.ctx.createGain();
    src.buffer = buf; g.gain.value = gain; src.connect(g).connect(this.master); src.start();
    return src;
  }
  startLoop(id, fade = 0.6) {
    if (this.loop && this.loop.id === id) return;
    this.stopLoop(fade);
    const buf = this.buffers.get(id); if (!buf) return;
    const src = this.ctx.createBufferSource(), g = this.ctx.createGain(), t = this.ctx.currentTime;
    src.buffer = buf; src.loop = true; g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(1, t + fade);
    src.connect(g).connect(this.master); src.start();
    this.loop = { id, src, g };
  }
  stopLoop(fade = 0.6) {
    if (!this.loop) return; const { src, g } = this.loop, t = this.ctx.currentTime;
    g.gain.cancelScheduledValues(t); g.gain.setValueAtTime(g.gain.value, t); g.gain.linearRampToValueAtTime(0, t + fade);
    src.stop(t + fade + 0.05); this.loop = null;
  }
  setState(state) {
    if (this.stateCues[state]) this.play(this.stateCues[state]);
    const loop = this.stateLoops[state];
    if (loop === undefined) return;
    loop ? this.startLoop(loop) : this.stopLoop();
  }
}
