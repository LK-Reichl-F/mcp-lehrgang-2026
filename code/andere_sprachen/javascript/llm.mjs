// LLM-Aufruf in JavaScript (Node.js) – entspricht lab01/hallo_llm.py (Python)
// Start: node --env-file=../../python/.env llm.mjs "Ihre Frage"
const basis = process.env.LLM_BASE_URL ?? "http://localhost:11434/v1";
const frage = process.argv[2] ?? "Erkläre in zwei Sätzen, was ein Sprachmodell ist.";
const extra = process.env.LLM_REASONING_EFFORT ? { reasoning_effort: process.env.LLM_REASONING_EFFORT } : {};

const antwort = await fetch(`${basis}/chat/completions`, {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: `Bearer ${process.env.LLM_API_KEY ?? "ollama"}` },
  body: JSON.stringify({ model: process.env.LLM_MODEL, messages: [{ role: "user", content: frage }], ...extra }),
});
const daten = await antwort.json();
console.log(daten.choices[0].message.content);
console.log(`--- Modell: ${daten.model}`);
