// ============================================================
// SMH Bot — Cloudflare Worker  (@sanmarinohappens_add_bot)
// ============================================================
// COSA FA:
// 1. Riceve i messaggi del bot Telegram via webhook.
// 2. Controlla che il mittente sia autorizzato (AUTHORIZED_CHAT_IDS).
// 3. Interfaccia a BOTTONI (tastiera sempre visibile) + comandi:
//    - ➕ Aggiungi evento  → poi scrivi l'evento (anche solo come messaggio!)
//    - 📋 Lista segnalazioni → gli eventi che hai segnalato e non ancora processati
//    - 🗓 Calendario        → i prossimi contenuti già programmati (da posts/)
//    - ❓ Aiuto
//    In più: SCRIVERE un messaggio normale (senza comando) = aggiunge un evento.
//    Per cancellare: bottoni 🗑 sotto ogni segnalazione (inline).
// 4. Comandi testuali equivalenti (per il menù "/" e per abitudine):
//    /aggiungi /segnalazioni /calendario /aiuto  (+ vecchi /smh-aggiungi ecc.)
// 5. Scrive/legge queue/inbox.md nel repo GitHub via Contents API.
//    Da lì il "postino" della catena importa gli eventi come da-verificare:
//    NIENTE va online in automatico, tutto passa prima dalla revisione umana.
//
// Gira 24/7 gratis, anche a Mac spento.
// ============================================================
// VARIABILI (Cloudflare > Worker > Settings > Variables and secrets)
//   TELEGRAM_BOT_TOKEN   (Secret) token del bot da @BotFather
//   GITHUB_TOKEN         (Secret) PAT fine-grained, Contents R/W sul repo
//   GITHUB_OWNER         es. "michidrop80-Rebelde"
//   GITHUB_REPO          es. "sanmarinohappens"
//   QUEUE_PATH           es. "queue/inbox.md"
//   AUTHORIZED_CHAT_IDS  chat_id autorizzati, separati da virgola
// ============================================================

// Etichette dei bottoni (la tastiera che resta sempre in basso).
// NB: quando premi un bottone, Telegram invia ESATTAMENTE questo testo,
// quindi le usiamo anche per riconoscere quale bottone è stato premuto.
const BTN_ADD = "\u2795 Aggiungi evento";
const BTN_LIST = "\ud83d\udccb Lista segnalazioni";
const BTN_CAL = "\ud83d\uddd3 Calendario";
const BTN_CANCEL = "\u26d4 Segnala annullamento";
const BTN_HELP = "\u2753 Aiuto";

// Un evento annullato entro questi giorni dalla pubblicazione = allarme 🚨 urgente
const URGENT_DAYS = 3;

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("SMH bot attivo \u2705", { status: 200 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("bad request", { status: 400 });
    }

    // --- 1) Click su un bottone inline (es. 🗑 elimina segnalazione) ---
    if (update.callback_query) {
      await handleCallback(env, update.callback_query);
      return new Response("ok");
    }

    // --- 2) Messaggio normale ---
    const message = update.message;
    if (!message || !message.text) {
      // ignora update senza testo (edit, sticker, foto, ecc.)
      return new Response("ok");
    }

    const chatId = String(message.chat.id);
    if (!isAuthorized(env, chatId)) {
      await sendTelegramMessage(
        env,
        chatId,
        "Ciao! \ud83d\udc4b Questo \u00e8 il bot interno di San Marino Happens \ud83c\uddf8\ud83c\uddf2, per ora riservato allo staff.\n\nSe vuoi segnalarci un evento del Titano, scrivici pure su Instagram o Facebook: @sanmarinohappens. Grazie! \ud83d\ude0a"
      );
      return new Response("ok");
    }

    const text = message.text.trim();

    try {
      await routeMessage(env, chatId, text);
    } catch (err) {
      await sendTelegramMessage(env, chatId, "\u26a0\ufe0f Ops, qualcosa \u00e8 andato storto: " + err.message, mainKeyboard());
    }

    return new Response("ok");
  },
};

// ------------------------------------------------------------
// Instradamento dei messaggi di testo (comandi + bottoni + testo libero)
// ------------------------------------------------------------
async function routeMessage(env, chatId, text) {
  const lower = text.toLowerCase();

  // Benvenuto / aiuto / menù
  if (lower === "/start" || lower === "/aiuto" || lower === "/help" || lower === "/menu" || text === BTN_HELP) {
    await sendWelcome(env, chatId);
    return;
  }

  // Lista segnalazioni in attesa
  if (lower === "/segnalazioni" || lower === "/smh-lista" || lower === "/lista" || text === BTN_LIST) {
    await showSegnalazioni(env, chatId);
    return;
  }

  // Calendario (prossimi contenuti programmati)
  if (lower === "/calendario" || lower === "/smh-calendario" || text === BTN_CAL) {
    await showCalendario(env, chatId);
    return;
  }

  // Segnala un annullamento → mostra i post in programma, si toglie con conferma
  if (text === BTN_CANCEL || lower === "/annulla" || lower === "/annullamento") {
    await showCancellablePosts(env, chatId);
    return;
  }

  // Bottone "Aggiungi evento": chiede di scrivere l'evento
  if (text === BTN_ADD) {
    await sendTelegramMessage(
      env,
      chatId,
      "Perfetto! \u270d\ufe0f Scrivimi l'evento in un messaggio, con quello che sai:\n\nEs: \u00abConcerto in Piazza della Libert\u00e0 sabato 25 alle 21\u00bb\n\n(Non serve nessun comando: quello che scrivi lo metto in lista. \ud83d\ude09)",
      mainKeyboard()
    );
    return;
  }

  // Comando /aggiungi o /smh-aggiungi con testo
  if (lower.startsWith("/aggiungi") || lower.startsWith("/smh-aggiungi")) {
    const eventText = text.replace(/^\/(smh-)?aggiungi/i, "").trim();
    if (!eventText) {
      await sendTelegramMessage(
        env,
        chatId,
        "Ci sei quasi! \ud83d\ude0a Scrivimi l'evento subito dopo il comando, oppure premi \u2795 Aggiungi evento e scrivilo normale.",
        mainKeyboard()
      );
      return;
    }
    await addEvento(env, chatId, eventText);
    return;
  }

  // Comando /cancella N o /smh-cancella N (cancellazione "da esperti"; di solito
  // si usano i bottoni 🗑 sotto la lista)
  if (lower.startsWith("/cancella") || lower.startsWith("/smh-cancella")) {
    const arg = text.replace(/^\/(smh-)?cancella/i, "").trim();
    const index = parseInt(arg, 10);
    if (!arg || isNaN(index) || index < 1) {
      await sendTelegramMessage(env, chatId, "Dimmi quale numero tolgo, cos\u00ec: /cancella 2\n(i numeri li vedi in \ud83d\udccb Lista segnalazioni)", mainKeyboard());
      return;
    }
    const removed = await removeFromQueueByIndex(env, index - 1);
    if (removed) {
      await sendTelegramMessage(env, chatId, `\ud83d\uddd1 Fatto, ho tolto:\n"${removed}"`, mainKeyboard());
    } else {
      await sendTelegramMessage(env, chatId, "Mmm, non trovo un evento con quel numero. \ud83e\udd14\nControlla con \ud83d\udccb Lista segnalazioni.", mainKeyboard());
    }
    return;
  }

  // Comando sconosciuto (inizia con "/") → guida
  if (text.startsWith("/")) {
    await sendTelegramMessage(
      env,
      chatId,
      "Questo comando non lo conosco. \ud83e\udd14\nUsa i bottoni qui sotto, oppure scrivimi direttamente l'evento da segnalare.",
      mainKeyboard()
    );
    return;
  }

  // QUALSIASI ALTRO TESTO = una segnalazione di evento da aggiungere.
  await addEvento(env, chatId, text);
}

// ------------------------------------------------------------
// Click su bottone inline (callback_query) — oggi: elimina segnalazione
// callback_data = "del_<timestamp ISO>"  (stabile anche se la lista cambia)
// ------------------------------------------------------------
async function handleCallback(env, cq) {
  const chatId = String(cq.message.chat.id);
  const data = cq.data || "";

  if (!isAuthorized(env, chatId)) {
    await answerCallback(env, cq.id, "Non autorizzato");
    return;
  }

  if (data.startsWith("del_")) {
    const ts = data.slice(4);
    try {
      const removed = await removeFromQueueByTimestamp(env, ts);
      if (removed) {
        await answerCallback(env, cq.id, "Eliminato \ud83d\uddd1");
      } else {
        await answerCallback(env, cq.id, "Non trovato (forse gi\u00e0 tolto)");
      }
      // ridisegna la lista aggiornata al posto del messaggio vecchio
      await refreshSegnalazioni(env, chatId, cq.message.message_id);
    } catch (err) {
      await answerCallback(env, cq.id, "Errore: " + err.message);
    }
    return;
  }

  // Annullamento evento in programma — 3 fasi: scelta → conferma → rimozione
  if (data.startsWith("cxlok_")) {
    await doCancel(env, cq, data.slice("cxlok_".length));
    return;
  }
  if (data === "cxlno") {
    await answerCallback(env, cq.id, "Ok, lasciato");
    await editMessageText(env, chatId, cq.message.message_id, "\ud83d\udc4d Ok, non ho tolto niente.", { inline_keyboard: [] });
    return;
  }
  if (data.startsWith("cxl_")) {
    await confirmCancel(env, cq, data.slice("cxl_".length));
    return;
  }

  await answerCallback(env, cq.id, "");
}

// ------------------------------------------------------------
// Benvenuto + tastiera bottoni
// ------------------------------------------------------------
async function sendWelcome(env, chatId) {
  const testo =
    "Ciao, benvenuto! \ud83d\udc4b Sono il bot di San Marino Happens \ud83c\uddf8\ud83c\uddf2\n\n" +
    "Raccolgo gli eventi belli del Titano che mi segnali. \u00c8 facilissimo:\n\n" +
    "\u2795 *Aggiungi evento* \u2014 poi scrivimi l'evento (o mandamelo come messaggio normale, senza comandi)\n" +
    "\ud83d\udccb *Lista segnalazioni* \u2014 le cose che mi hai segnalato e non ancora lavorate\n" +
    "\ud83d\uddd3 *Calendario* \u2014 cosa sta per uscire su @sanmarinohappens\n" +
    "\u26d4 *Segnala annullamento* \u2014 un evento salta? Lo togli dal programma prima che esca\n" +
    "\u2753 *Aiuto* \u2014 questo messaggio\n\n" +
    "Una cosa importante: quello che mi mandi non viene pubblicato in automatico \u2014 passa sempre da una revisione prima di finire online. Tu segnala pure, al controllo ci pensiamo noi. \ud83d\ude09";
  await sendTelegramMessage(env, chatId, testo, mainKeyboard(), "Markdown");
}

// ------------------------------------------------------------
// Aggiunge un evento alla coda inbox
// ------------------------------------------------------------
async function addEvento(env, chatId, eventText) {
  try {
    await appendToQueue(env, eventText);
    await sendTelegramMessage(
      env,
      chatId,
      "\u2705 Segnato, grazie della dritta! L'ho messo in lista.\n\nNiente va online da solo: passer\u00e0 prima dalla revisione. \ud83d\udc40\ud83c\uddf8\ud83c\uddf2",
      mainKeyboard()
    );
  } catch (err) {
    await sendTelegramMessage(env, chatId, "\u26a0\ufe0f Ops, non sono riuscito a salvarlo su GitHub: " + err.message, mainKeyboard());
  }
}

// ------------------------------------------------------------
// Mostra la lista delle segnalazioni in attesa, con bottoni 🗑 per eliminare
// ------------------------------------------------------------
async function showSegnalazioni(env, chatId) {
  const items = await listQueue(env);
  if (items.length === 0) {
    await sendTelegramMessage(
      env,
      chatId,
      "\ud83d\udced Nessuna segnalazione in attesa.\n\nQui compaiono SOLO gli eventi che mi segnali e non ancora lavorati (poi passano dalla revisione e spariscono da qui).\n\nPer vedere cosa sta per uscire, premi \ud83d\uddd3 Calendario. Per segnalare, premi \u2795 Aggiungi evento.",
      mainKeyboard()
    );
    return;
  }
  const { text, keyboard } = renderSegnalazioni(items);
  await sendTelegramMessage(env, chatId, text, keyboard);
}

// Ridisegna la lista (usata dopo un'eliminazione via bottone): modifica il
// messaggio esistente invece di mandarne uno nuovo.
async function refreshSegnalazioni(env, chatId, messageId) {
  const items = await listQueue(env);
  if (items.length === 0) {
    await editMessageText(env, chatId, messageId, "\ud83d\udced Nessuna segnalazione in attesa. Tutto pulito! \u2728", { inline_keyboard: [] });
    return;
  }
  const { text, keyboard } = renderSegnalazioni(items);
  await editMessageText(env, chatId, messageId, text, keyboard);
}

// Costruisce testo + tastiera inline (un bottone 🗑 per riga) della lista
function renderSegnalazioni(items) {
  const lines = items.map((item, i) => `${i + 1}. ${item.text}`).join("\n");
  const text = `\ud83d\udccb Segnalazioni in attesa (${items.length}):\n\n${lines}\n\nPremi \ud83d\uddd1 per togliere quella che non ti serve pi\u00f9.`;
  const inline_keyboard = items.map((item, i) => [
    { text: `\ud83d\uddd1 ${i + 1}. ${short(item.text, 25)}`, callback_data: `del_${item.timestamp}` },
  ]);
  return { text, keyboard: { inline_keyboard } };
}

// ------------------------------------------------------------
// Mostra il calendario = prossimi contenuti già programmati (da posts/*.json)
// ------------------------------------------------------------
async function showCalendario(env, chatId) {
  let eventi;
  try {
    eventi = await getCalendar(env);
  } catch (err) {
    await sendTelegramMessage(env, chatId, "\u26a0\ufe0f Non riesco a leggere il calendario ora: " + err.message, mainKeyboard());
    return;
  }
  if (eventi.length === 0) {
    await sendTelegramMessage(
      env,
      chatId,
      "\ud83d\uddd3 Per ora non c'\u00e8 nessun contenuto in programma nella coda.\n\n(Qui vedi i post gi\u00e0 pronti e schedulati; quando la catena ne prepara di nuovi compaiono qui.)",
      mainKeyboard()
    );
    return;
  }
  const righe = eventi.map((e) => `\ud83d\udcc5 ${formatDateIT(e.date)} \u2014 ${e.titolo}`).join("\n");
  await sendTelegramMessage(
    env,
    chatId,
    `\ud83d\uddd3 Cosa sta per uscire su @sanmarinohappens:\n\n${righe}\n\n\u2139\ufe0f \u00c8 il programma dei post gi\u00e0 pronti (data = giorno di pubblicazione).`,
    mainKeyboard()
  );
}

// Legge posts/*.json dal repo e restituisce gli eventi futuri, ordinati per data
async function getCalendar(env) {
  const apiUrl = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/posts`;
  const res = await fetch(apiUrl, { headers: ghHeaders(env) });
  if (res.status === 404) return []; // cartella posts/ vuota o assente
  if (!res.ok) throw new Error(`GitHub list failed: ${res.status}`);
  const files = await res.json();
  const jsons = Array.isArray(files) ? files.filter((f) => f.name.endsWith(".json")) : [];

  const eventi = [];
  for (const f of jsons) {
    try {
      const r = await fetch(f.download_url);
      if (!r.ok) continue;
      const data = await r.json();
      if (data.data_pubblicazione && data.titolo_evento) {
        eventi.push({ file: f.name, date: data.data_pubblicazione, titolo: data.titolo_evento });
      }
    } catch {
      // salta il file rotto, non bloccare tutto il calendario
    }
  }

  const oggi = todayISO();
  return eventi
    .filter((e) => e.date >= oggi)
    .sort((a, b) => a.date.localeCompare(b.date));
}

// ------------------------------------------------------------
// ANNULLAMENTO di un evento già in programma (dai post in coda)
// Flusso a 3 tap: scegli l'evento → conferma → rimozione.
// ------------------------------------------------------------

// Fase 1: mostra i post in programma, ognuno con un bottone per annullarlo
async function showCancellablePosts(env, chatId) {
  let eventi;
  try {
    eventi = await getCalendar(env);
  } catch (err) {
    await sendTelegramMessage(env, chatId, "\u26a0\ufe0f Non riesco a leggere il programma ora: " + err.message, mainKeyboard());
    return;
  }
  if (eventi.length === 0) {
    await sendTelegramMessage(env, chatId, "\ud83d\uddd3 Non c'\u00e8 nessun evento in programma da annullare al momento.", mainKeyboard());
    return;
  }
  const inline_keyboard = eventi.map((e) => [
    { text: `\u26d4 ${formatDateIT(e.date)} \u00b7 ${short(e.titolo, 28)}`, callback_data: `cxl_${e.file}` },
  ]);
  await sendTelegramMessage(
    env,
    chatId,
    "\u26d4 Quale evento \u00e8 stato ANNULLATO?\n\nToccalo per toglierlo dal programma \u2014 ti chieder\u00f2 conferma prima di rimuoverlo davvero.",
    { inline_keyboard }
  );
}

// Fase 2: chiede conferma per il post scelto (con l'avviso urgenza se imminente)
async function confirmCancel(env, cq, file) {
  const chatId = String(cq.message.chat.id);
  const post = await readPost(env, file);
  if (!post) {
    await answerCallback(env, cq.id, "Non trovato");
    await editMessageText(env, chatId, cq.message.message_id, "\ud83e\udd14 Non trovo pi\u00f9 quel post (forse gi\u00e0 tolto).", { inline_keyboard: [] });
    return;
  }
  await answerCallback(env, cq.id, "");
  const text =
    `Confermi? Sto per TOGLIERE dal programma:\n\n` +
    `\u26d4 ${post.titolo}\n\ud83d\udcc5 ${formatDateIT(post.date)} \u2014 ${urgencyLabel(post.date)}\n\n` +
    `Non verr\u00e0 pubblicato su Instagram/Facebook. Sei sicuro?`;
  const keyboard = {
    inline_keyboard: [
      [{ text: "\u2705 S\u00ec, togli dal programma", callback_data: `cxlok_${file}` }],
      [{ text: "\u274c No, lascia com'\u00e8", callback_data: "cxlno" }],
    ],
  };
  await editMessageText(env, chatId, cq.message.message_id, text, keyboard);
}

// Fase 3: rimuove davvero il post (JSON + immagini) dalla coda posts/
async function doCancel(env, cq, file) {
  const chatId = String(cq.message.chat.id);
  await answerCallback(env, cq.id, "Sto togliendo\u2026");
  const post = await readPost(env, file);
  const titolo = post ? post.titolo : file;
  const images = post ? post.images : [];
  const paths = [`posts/${file}`, ...images.map((img) => `posts/${img}`)];

  let deleted = 0;
  const errors = [];
  for (const p of paths) {
    try {
      const sha = await getSha(env, p);
      if (!sha) continue; // già assente
      await deleteFile(env, p, sha, `Annullato: rimosso dal programma ${titolo}`.slice(0, 72));
      deleted++;
    } catch (e) {
      errors.push(p.split("/").pop());
    }
  }

  let msg;
  if (deleted > 0 && errors.length === 0) {
    msg = `\u2705 Fatto! \u00ab${titolo}\u00bb tolto dal programma.\n\nNon uscir\u00e0 su Instagram/Facebook. \ud83d\udee1\ufe0f`;
  } else if (deleted > 0) {
    msg = `\u26a0\ufe0f \u00ab${titolo}\u00bb tolto solo in parte. Non sono riuscito a rimuovere: ${errors.join(", ")}.\nControlla la cartella posts/ a mano.`;
  } else {
    msg = `\ud83e\udd14 Non ho tolto niente (forse era gi\u00e0 stato rimosso). Controlla con \ud83d\uddd3 Calendario.`;
  }
  await editMessageText(env, chatId, cq.message.message_id, msg, { inline_keyboard: [] });
}

// Legge un post da posts/ (via raw, repo pubblico). Ritorna { titolo, date, images } o null.
async function readPost(env, file) {
  try {
    const r = await fetch(rawUrl(env, `posts/${file}`));
    if (!r.ok) return null;
    const d = await r.json();
    const basename = file.replace(/\.json$/i, "");
    const images = Array.isArray(d.immagini) && d.immagini.length ? d.immagini : [basename + ".png"];
    return { titolo: d.titolo_evento || file, date: d.data_pubblicazione || "", images };
  } catch {
    return null;
  }
}

// ------------------------------------------------------------
// Helper GitHub Contents API
// ------------------------------------------------------------
function ghHeaders(env) {
  return {
    Authorization: `Bearer ${env.GITHUB_TOKEN}`,
    "User-Agent": "smh-bot",
    Accept: "application/vnd.github+json",
  };
}

// URL raw (repo pubblico) con ogni segmento del path codificato (gestisce gli spazi nei nomi)
function rawUrl(env, path) {
  const enc = path.split("/").map(encodeURIComponent).join("/");
  return `https://raw.githubusercontent.com/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/main/${enc}`;
}

// URL della Contents API per un path (segmenti codificati)
function contentsUrl(env, path) {
  const enc = path.split("/").map(encodeURIComponent).join("/");
  return `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${enc}`;
}

// Ritorna lo sha di un file (serve per cancellarlo), o null se non esiste
async function getSha(env, path) {
  const r = await fetch(contentsUrl(env, path), { headers: ghHeaders(env) });
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`getSha ${r.status}`);
  const d = await r.json();
  return d.sha;
}

// Cancella un file dal repo (Contents API DELETE)
async function deleteFile(env, path, sha, message) {
  const r = await fetch(contentsUrl(env, path), {
    method: "DELETE",
    headers: { ...ghHeaders(env), "Content-Type": "application/json" },
    body: JSON.stringify({ message, sha, branch: "main" }),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(`delete ${r.status} ${t}`);
  }
}

// Legge il file coda da GitHub. Ritorna { content, sha } — content "" e sha
// undefined se il file non esiste ancora.
async function readQueueFile(env) {
  const apiUrl = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${env.QUEUE_PATH}`;
  const getRes = await fetch(apiUrl, { headers: ghHeaders(env) });

  if (getRes.status === 200) {
    const data = await getRes.json();
    return {
      // Decodifica UTF-8 CORRETTA: atob() da solo restituisce byte "latin-1",
      // spezzando accenti (à è é) e trattini (—) in caratteri sbagliati (es. "â").
      // escape()+decodeURIComponent() ricostruisce i caratteri veri — è lo
      // specchio esatto di unescape(encodeURIComponent()) usato in scrittura.
      content: decodeURIComponent(escape(atob(data.content.replace(/\n/g, "")))),
      sha: data.sha,
    };
  } else if (getRes.status === 404) {
    return { content: "", sha: undefined };
  } else {
    throw new Error(`GitHub read failed: ${getRes.status}`);
  }
}

// Scrive (crea o aggiorna) il file coda su GitHub
async function writeQueueFile(env, content, sha, commitMessage) {
  const apiUrl = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${env.QUEUE_PATH}`;
  const putRes = await fetch(apiUrl, {
    method: "PUT",
    headers: { ...ghHeaders(env), "Content-Type": "application/json" },
    body: JSON.stringify({
      message: commitMessage,
      content: btoa(unescape(encodeURIComponent(content))),
      sha,
    }),
  });
  if (!putRes.ok) {
    const errText = await putRes.text();
    throw new Error(`GitHub write failed: ${putRes.status} ${errText}`);
  }
}

// Estrae le righe evento dal contenuto del file.
// Formato riga: "- [ ] 2026-07-18T08:30:00.000Z — testo"
// Ritorna { raw, timestamp, text }.
function parseQueueLines(content) {
  return content
    .split("\n")
    .filter((line) => line.trim().startsWith("- [ ]"))
    .map((line) => {
      const withoutPrefix = line.replace(/^- \[ \]\s*/, "");
      const dashIndex = withoutPrefix.indexOf("\u2014");
      let timestamp = "";
      let text = withoutPrefix.trim();
      if (dashIndex >= 0) {
        timestamp = withoutPrefix.slice(0, dashIndex).trim();
        text = withoutPrefix.slice(dashIndex + 1).trim();
      }
      return { raw: line, timestamp, text };
    });
}

async function appendToQueue(env, eventText) {
  const { content, sha } = await readQueueFile(env);
  const timestamp = new Date().toISOString();
  const newLine = `- [ ] ${timestamp} \u2014 ${eventText}\n`;
  const updatedContent = content + newLine;
  await writeQueueFile(env, updatedContent, sha, `Nuovo evento in coda: ${eventText.slice(0, 50)}`);
}

async function listQueue(env) {
  const { content } = await readQueueFile(env);
  return parseQueueLines(content);
}

// Rimuove per indice (0-based). Ritorna il testo rimosso o null.
async function removeFromQueueByIndex(env, index) {
  const { content, sha } = await readQueueFile(env);
  const items = parseQueueLines(content);
  if (index < 0 || index >= items.length) return null;
  const removed = items[index];
  await writeRemaining(env, items, index, sha, removed.text);
  return removed.text;
}

// Rimuove la riga con quel timestamp (stabile anche se la lista è cambiata).
// Ritorna il testo rimosso o null.
async function removeFromQueueByTimestamp(env, timestamp) {
  const { content, sha } = await readQueueFile(env);
  const items = parseQueueLines(content);
  const index = items.findIndex((it) => it.timestamp === timestamp);
  if (index < 0) return null;
  const removed = items[index];
  await writeRemaining(env, items, index, sha, removed.text);
  return removed.text;
}

async function writeRemaining(env, items, index, sha, removedText) {
  const remainingLines = items
    .filter((_, i) => i !== index)
    .map((item) => item.raw)
    .join("\n");
  const updatedContent = remainingLines ? remainingLines + "\n" : "";
  await writeQueueFile(env, updatedContent, sha, `Rimosso evento dalla coda: ${removedText.slice(0, 50)}`);
}

// ------------------------------------------------------------
// Telegram API
// ------------------------------------------------------------
function mainKeyboard() {
  return {
    keyboard: [
      [{ text: BTN_ADD }],
      [{ text: BTN_LIST }, { text: BTN_CAL }],
      [{ text: BTN_CANCEL }],
      [{ text: BTN_HELP }],
    ],
    resize_keyboard: true,
    is_persistent: true,
  };
}

async function sendTelegramMessage(env, chatId, text, replyMarkup, parseMode) {
  const url = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;
  const body = { chat_id: chatId, text };
  if (replyMarkup) body.reply_markup = replyMarkup;
  if (parseMode) body.parse_mode = parseMode;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

async function editMessageText(env, chatId, messageId, text, inlineKeyboard) {
  const url = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/editMessageText`;
  const body = { chat_id: chatId, message_id: messageId, text };
  if (inlineKeyboard) body.reply_markup = inlineKeyboard;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

async function answerCallback(env, callbackQueryId, text) {
  const url = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/answerCallbackQuery`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ callback_query_id: callbackQueryId, text: text || "" }),
  });
}

// ------------------------------------------------------------
// Utility
// ------------------------------------------------------------
function isAuthorized(env, chatId) {
  const authorized = (env.AUTHORIZED_CHAT_IDS || "")
    .split(",")
    .map((id) => id.trim())
    .filter(Boolean);
  return authorized.includes(String(chatId));
}

function short(s, max) {
  return s.length > max ? s.slice(0, max - 1) + "\u2026" : s;
}

// Data di oggi in fuso San Marino, formato YYYY-MM-DD.
// Con fallback a UTC se il runtime non supporta i fusi in Intl (robustezza al deploy).
function todayISO() {
  try {
    return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/San_Marino" }).format(new Date());
  } catch {
    return new Date().toISOString().slice(0, 10);
  }
}

// "2026-07-19" → "dom 19 lug"
function formatDateIT(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  const date = new Date(Date.UTC(y, m - 1, d));
  const giorni = ["dom", "lun", "mar", "mer", "gio", "ven", "sab"];
  const mesi = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"];
  return `${giorni[date.getUTCDay()]} ${d} ${mesi[m - 1]}`;
}

// Giorni da oggi (fuso San Marino) alla data indicata; null se data vuota
function daysUntil(dateISO) {
  if (!dateISO) return null;
  const [ty, tm, td] = todayISO().split("-").map(Number);
  const [dy, dm, dd] = dateISO.split("-").map(Number);
  return Math.round((Date.UTC(dy, dm - 1, dd) - Date.UTC(ty, tm - 1, td)) / 86400000);
}

// Etichetta di urgenza per un evento annullato (soglia URGENT_DAYS)
function urgencyLabel(dateISO) {
  const n = daysUntil(dateISO);
  if (n === null) return "data non chiara";
  if (n < 0) return "gi\u00e0 passato";
  if (n === 0) return "\ud83d\udea8 \u00c8 OGGI!";
  if (n === 1) return "\ud83d\udea8 \u00e8 DOMANI (urgente)";
  if (n <= URGENT_DAYS) return `\ud83d\udea8 tra ${n} giorni (urgente)`;
  return `tra ${n} giorni`;
}
