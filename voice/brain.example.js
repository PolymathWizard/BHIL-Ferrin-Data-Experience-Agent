/* FERRIN brain hook (example).
 * Copy to voice/brain.js to give FERRIN a live model. voice/brain.js is gitignored.
 * The page calls window.FERRIN_BRAIN(prompt) and speaks whatever text comes back.
 *
 * Point it at YOUR OWN server-side proxy. The proxy holds the API key in an
 * environment variable and forwards the prompt to your model provider.
 * Never put an API key in this file or anywhere in the browser.
 */
window.FERRIN_BRAIN = async (prompt) => {
  const res = await fetch('http://localhost:8787/ferrin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
  if (!res.ok) throw new Error('relay ' + res.status);
  const data = await res.json();
  return data.text;   // e.g. "[wave] Ferrin on channel. Good to see you."
};
