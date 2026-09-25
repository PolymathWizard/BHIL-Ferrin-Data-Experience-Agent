/* FERRIN ship's log: a small, local, user-controlled memory shared by the preview and voice pages.
 * Classic script: load with <script src="../shared/ferrin-memory.js"></script>; it defines globalThis.FerrinMemory.
 * Facts only, never transcripts. Stored in localStorage under one key, so every FERRIN page on the same
 * site shares it. Nothing leaves the browser.
 */
(function (root) {
  'use strict';
  var KEY = 'ferrin.memory';
  var MAX_FACTS = 40, MAX_LEN = 160;
  var SECRET = [
    /\b(sk|pk|rk)[-_][A-Za-z0-9-_]{12,}/,            // API-key shapes
    /\b(ghp|gho|github_pat)_[A-Za-z0-9_]{12,}/,
    /\bAKIA[0-9A-Z]{12,}/,
    /\b(password|passwd|passcode|pin|secret|token|api key|apikey|ssn|social security)\b/i,
    /\b(?:\d[ -]?){13,19}\b/,                        // card or account numbers
    /-----BEGIN [A-Z ]*PRIVATE KEY-----/
  ];

  function clean(text) {
    return String(text || '').replace(/\s+/g, ' ').trim().replace(/^(that|to)\s+/i, '').replace(/[.!]+$/, '').slice(0, MAX_LEN);
  }
  function isSecret(text) { return SECRET.some(function (r) { return r.test(text); }); }
  function norm(text) { return clean(text).toLowerCase(); }

  function create(storage, opts) {
    opts = opts || {};
    var store = storage || null;
    var now = opts.now || function () { return new Date(); };
    var state = { enabled: true, facts: [] };
    try { var raw = store && store.getItem(KEY); if (raw) state = Object.assign(state, JSON.parse(raw)); } catch (e) { /* no storage: run in memory */ }
    function save() { try { if (store) store.setItem(KEY, JSON.stringify(state)); } catch (e) { /* ignore */ } }
    function day() { var d = now(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }

    return {
      get enabled() { return state.enabled; },
      set enabled(v) { state.enabled = !!v; save(); },
      facts: function () { return state.facts.slice(); },
      /** Add a fact. Returns {ok, reason, fact}. Duplicates refresh their date instead of repeating. */
      add: function (text, kind) {
        var t = clean(text);
        if (!state.enabled) return { ok: false, reason: 'off' };
        if (t.split(' ').length < 2 && !kind) return { ok: false, reason: 'too short' };
        if (isSecret(t)) return { ok: false, reason: 'secret' };
        var n = t.toLowerCase();
        var existing = state.facts.filter(function (f) { return f.text.toLowerCase() === n; })[0];
        if (existing) { existing.date = day(); save(); return { ok: true, fact: existing, duplicate: true }; }
        if (kind === 'name') state.facts = state.facts.filter(function (f) { return f.kind !== 'name'; });
        var fact = { text: t, kind: kind || 'note', date: day() };
        state.facts.push(fact);
        while (state.facts.length > MAX_FACTS) {                 // keep names and newest; drop the oldest note
          var i = state.facts.findIndex(function (f) { return f.kind !== 'name'; });
          state.facts.splice(i < 0 ? 0 : i, 1);
        }
        save(); return { ok: true, fact: fact };
      },
      /** Remove every fact containing the query. Returns how many were removed. */
      forget: function (query) {
        var q = norm(query); if (!q) return 0;
        var before = state.facts.length;
        state.facts = state.facts.filter(function (f) { return f.text.toLowerCase().indexOf(q) === -1; });
        save(); return before - state.facts.length;
      },
      remove: function (index) { state.facts.splice(index, 1); save(); },
      wipe: function () { state.facts = []; save(); },
      name: function () { var f = state.facts.filter(function (x) { return x.kind === 'name'; })[0]; return f ? f.text.replace(/^Skipper's name is\s+/i, '') : null; },
      /** Compact summary for a prompt: newest first, capped by characters. */
      summary: function (maxChars) {
        maxChars = maxChars || 700; var out = [], used = 0;
        state.facts.slice().reverse().forEach(function (f) { var line = '- ' + f.text; if (used + line.length <= maxChars) { out.push(line); used += line.length + 1; } });
        return out.join('\n');
      },
      exportJSON: function () { return JSON.stringify({ app: 'ferrin', version: 1, facts: state.facts }, null, 2); },
      importJSON: function (json) {
        var data = JSON.parse(json); if (!data || !Array.isArray(data.facts)) throw new Error('not a FERRIN ship\'s log');
        var added = 0; var self = this;
        data.facts.forEach(function (f) { if (f && f.text && self.add(f.text, f.kind === 'name' ? 'name' : 'note').ok) added++; });
        return added;
      }
    };
  }

  /** Pull durable facts out of something the user said. Explicit "remember" wins; a few safe patterns are automatic. */
  function extract(utterance) {
    var s = String(utterance || '').trim(), m;
    if ((m = /^(?:please\s+)?(?:remember|note|log)\s+(?:that\s+)?(.{4,})$/i.exec(s))) return { explicit: true, facts: [{ text: m[1], kind: 'note' }] };
    var facts = [];
    if ((m = /\b(?:[Mm]y name is|[Cc]all me)\s+([A-Z][\w'-]{1,24}(?:\s+[A-Z][\w'-]{1,24})?)/.exec(s))) facts.push({ text: "Skipper's name is " + m[1], kind: 'name' });
    if ((m = /\bI(?:'m| am)\s+(?:working on|building|shipping)\s+(.{3,80}?)(?:[.!?]|$)/i.exec(s))) facts.push({ text: 'Skipper is working on ' + m[1], kind: 'note' });
    if ((m = /\bI (prefer|like|love|hate|don't like)\s+(?!(?:that|this|it|you|them)\b)(.{3,60}?)(?:[.!?]|$)/i.exec(s))) {
      var verb = { prefer: 'prefers', like: 'likes', love: 'loves', hate: 'hates', "don't like": "doesn't like" }[m[1].toLowerCase()];
      facts.push({ text: 'Skipper ' + verb + ' ' + m[2], kind: 'note' });
    }
    return { explicit: false, facts: facts };
  }

  root.FerrinMemory = { create: create, extract: extract, isSecret: isSecret, KEY: KEY, MAX_FACTS: MAX_FACTS };
})(typeof globalThis !== 'undefined' ? globalThis : this);
