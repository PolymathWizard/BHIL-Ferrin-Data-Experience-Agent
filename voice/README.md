# FERRIN comms: voice prototype

Talk to FERRIN out loud. Hold the mic button (or Space) to speak, or type. FERRIN answers with the browser's built-in voice while the 3D lantern reacts: the optic and scan bands pulse with each word, and reply tags make it wave, hop, droop into a fault or run a redraw.

Everything runs in the browser at no cost:

| Stage | How | Notes |
|---|---|---|
| Hearing | Web Speech recognition, push-to-talk | Chrome, Edge and Safari. Not Firefox. Chrome sends audio to Google to transcribe. |
| Thinking | Offline banter manifest, or an optional brain hook | See below. |
| Speaking | Web Speech synthesis | Voice quality depends on the operating system. Choice and mute are saved per browser. |

Open `index.html` over HTTP (GitHub Pages works). Browsers only allow speech after a click, so the page starts with an Open channel button.

## Giving FERRIN a live brain

By default FERRIN answers from a small offline intent table written in its voice. To connect a real model, copy `brain.example.js` to `brain.js` and point it at your own server-side proxy. The page calls `window.FERRIN_BRAIN(prompt)` and speaks the text that comes back; replies may start with a body-language tag such as `[wave]`.

`brain.js` is gitignored. Keep API keys on the server, in an environment variable. Never put a key in the browser or in this repo.

## Ship's log

FERRIN remembers what you tell it, in this browser only. Say "remember that I deploy on Fridays", "forget Fridays" or "what do you remember?". It also picks up a few plain statements on its own ("call me Rowan", "I'm building a trail app") and shows a line in the chat whenever it logs something. With a brain connected, the model can add facts with a `[log: ...]` tag, which the page strips from speech and files through the same filter.

The Ship's log panel switches memory off, deletes single entries, exports or imports a JSON backup, and wipes everything. Anything that looks like a password, key or account number is refused. The preview console shares the same log (`shared/ferrin-memory.js`).

## Scripted lines

`lines.json` holds 31 lines across 18 situations (greetings, agent states, goodbye and each easter egg), every one 12 words or fewer. They pair with the cues in `../sfx`.

## Known limits

Browser speech output cannot be routed through Web Audio, so there is no voice effects chain here. FERRIN's character comes from the voice choice and a lowered pitch, transmission chirps around each line, and the visuals. A local open-weight voice would allow the full effects chain later without changing the rest of the pipeline.

## License

Code is MIT. `lines.json` is CC BY 4.0.
