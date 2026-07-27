/**
 * smh-approvazioni-worker.js — le risposte di Michele non scadono più.
 * ============================================================================
 *
 * COS'E' (spiegato semplice)
 * --------------------------
 * Prima, le approvazioni ✅/❌ venivano lette da Telegram col metodo `getUpdates`.
 * Quel metodo ha due difetti che ci hanno fatto perdere risposte per mesi:
 *   1. consegna UNA VOLTA SOLA: appena qualcuno legge, i messaggi spariscono;
 *   2. conserva al massimo 24 ORE: quello che nessuno legge entro un giorno, Telegram lo butta.
 * Siccome il raccoglitore passava una volta a settimana, le risposte date "fuori finestra"
 * evaporavano senza lasciare traccia.
 *
 * Questo Worker toglie di mezzo il problema: sta acceso 24/7, Telegram gli consegna i click
 * SUBITO (webhook), e lui li scrive in un file del repo GitHub — `queue/approvazioni.md` —
 * dove restano finché qualcuno non li elabora. Michele può rispondere quando vuole.
 *
 * E' un Worker SEPARATO da quello del bot eventi (`smh-bot-worker.js`), apposta: quello è
 * l'unico canale che oggi funziona per le segnalazioni, e non va messo a rischio.
 *
 * VARIABILI D'AMBIENTE da impostare su Cloudflare (mai nel codice!)
 * ------------------------------------------------------------------
 *   TELEGRAM_BOT_TOKEN    token di @sanmarinohappens_bot (quello delle APPROVAZIONI,
 *                         diverso dal bot degli eventi)
 *   GITHUB_TOKEN          PAT con permesso di scrittura sui contenuti del repo
 *   GITHUB_OWNER          michidrop80-Rebelde
 *   GITHUB_REPO           sanmarinohappens
 *   AUTHORIZED_CHAT_IDS   chat id di Michele (elenco separato da virgole)
 *
 * ⚠️ ORDINE DI ACCENSIONE — non invertire:
 *   1) prima si insegna a /smh-approvazione a leggere da `queue/approvazioni.md`  [FATTO]
 *   2) poi si fa il deploy di questo Worker
 *   3) SOLO ALLA FINE si imposta il webhook (setWebhook)
 * Perché: appena il webhook è attivo, `getUpdates` smette di funzionare PER SEMPRE su quel
 * bot (errore 409). Se si accende il webhook prima, la catena resta cieca.
 */

const APPROVAZIONI_PATH = "queue/approvazioni.md";

const INTESTAZIONE =
  "# Coda approvazioni — risposte di Michele dal bot Telegram\n" +
  "\n" +
  "Scritto in automatico dal Worker Cloudflare `smh-approvazioni-worker.js` a ogni click.\n" +
  "Letto e archiviato da `/smh-approvazione`, che segna le righe elaborate con `- [x]`.\n" +
  "A differenza di `getUpdates`, queste righe **non scadono**: restano finché non si elaborano.\n" +
  "\n" +
  "Formato: `- [ ] <ISO> — <esito> — <id> — <mittente> — <riferimento>`\n" +
  "\n";

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("SMH approvazioni attivo ✅", { status: 200 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("bad request", { status: 400 });
    }

    try {
      if (update.callback_query) {
        await gestisciClick(env, update.callback_query);
      } else if (update.message && update.message.text) {
        await gestisciTesto(env, update.message);
      }
    } catch (e) {
      // Non si risponde MAI con un errore a Telegram: rifarebbe la consegna all'infinito.
      // Meglio loggare e assorbire: la riga si recupera dai log del Worker.
      console.error("errore:", e && e.message, JSON.stringify(update).slice(0, 400));
    }
    return new Response("ok");
  },
};

// ------------------------------------------------------------
// Click sui pulsanti ✅/❌  (callback_data: approve_XX / reject_XX)
// ------------------------------------------------------------
async function gestisciClick(env, cq) {
  const chatId = String(cq.message && cq.message.chat ? cq.message.chat.id : "");
  if (!autorizzato(env, chatId)) {
    await rispondiAlClick(env, cq.id, "Non autorizzato");
    return;
  }

  const dati = String(cq.data || "");
  const m = dati.match(/^(approve|reject)_(.+)$/);
  if (!m) {
    await rispondiAlClick(env, cq.id, "Comando non riconosciuto");
    return;
  }
  const esito = m[1] === "approve" ? "approvato" : "scartato";
  const id = m[2];

  // Il testo del messaggio serve solo come riferimento umano nel file.
  const riferimento = primaRiga(cq.message && cq.message.text);

  await aggiungiRiga(env, `- [ ] ${adesso()} — ${esito} — ${id} — ${mittente(cq.from)} — ${riferimento}`);

  // Il pulsante di Michele smette di girare e mostra la conferma.
  await rispondiAlClick(env, cq.id, esito === "approvato" ? "Ricevuto ✅" : "Scartato ❌");
}

// ------------------------------------------------------------
// Risposte di TESTO (il vecchio protocollo: "✅", "❌ 3,5", "✅ 1,2")
// Si registrano com'è: a interpretarle è /smh-approvazione, non il Worker.
// ------------------------------------------------------------
async function gestisciTesto(env, message) {
  const chatId = String(message.chat.id);
  if (!autorizzato(env, chatId)) return;

  const testo = String(message.text || "").trim();
  if (!testo) return;
  // Solo messaggi che sembrano una risposta di approvazione: il resto è rumore.
  if (!/[✅❌]|^\s*(ok|tutto ok|approva|scarta)/i.test(testo)) return;

  await aggiungiRiga(env, `- [ ] ${adesso()} — testo — — ${mittente(message.from)} — ${short(testo, 120)}`);
  await inviaMessaggio(env, chatId, "📝 Risposta registrata. La elaboro al prossimo giro.");
}

// ------------------------------------------------------------
// Scrittura su GitHub, a prova di click ravvicinati
// ------------------------------------------------------------
/**
 * ⚠️ IL PUNTO PIU' DELICATO DI TUTTO IL WORKER.
 * Michele preme i pulsanti a raffica: 17 click in pochi secondi = 17 richieste in parallelo,
 * tutte che leggono-modificano-scrivono LO STESSO file. L'API di GitHub rifiuta le scritture
 * con lo `sha` ormai vecchio (409 Conflict): senza questo ciclo di ritentativi la maggior
 * parte delle approvazioni andrebbe persa — cioè esattamente il guasto che stiamo riparando.
 * Quindi: a ogni conflitto si RILEGGE il file aggiornato e si riprova, con attesa crescente.
 */
async function aggiungiRiga(env, riga) {
  const MAX = 6;
  for (let tentativo = 1; tentativo <= MAX; tentativo++) {
    const { content, sha } = await leggiFile(env, APPROVAZIONI_PATH);
    const base = content && content.trim() ? content.replace(/\s*$/, "\n") : INTESTAZIONE;
    const nuovo = base + riga + "\n";
    const esito = await scriviFile(env, APPROVAZIONI_PATH, nuovo, sha,
      `Approvazione da Telegram: ${short(riga, 60)}`);
    if (esito.ok) return true;
    if (esito.status !== 409 && esito.status !== 422) {
      throw new Error(`scrittura fallita: ${esito.status} ${esito.testo}`);
    }
    // 409/422 = qualcun altro ha scritto un istante prima: si rilegge e si riprova.
    await attendi(120 * tentativo + Math.floor(Math.random() * 120));
  }
  throw new Error("scrittura fallita dopo troppi conflitti");
}

async function leggiFile(env, path) {
  const enc = path.split("/").map(encodeURIComponent).join("/");
  const url = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${enc}`;
  const res = await fetch(url, { headers: intestazioniGh(env) });
  if (res.status === 200) {
    const data = await res.json();
    // Decodifica UTF-8 corretta: atob() da solo spezzerebbe accenti e trattini lunghi.
    return { content: decodeURIComponent(escape(atob(data.content.replace(/\n/g, "")))), sha: data.sha };
  }
  if (res.status === 404) return { content: "", sha: undefined };
  throw new Error(`lettura fallita: ${res.status}`);
}

async function scriviFile(env, path, content, sha, messaggio) {
  const enc = path.split("/").map(encodeURIComponent).join("/");
  const url = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${enc}`;
  const res = await fetch(url, {
    method: "PUT",
    headers: { ...intestazioniGh(env), "Content-Type": "application/json" },
    body: JSON.stringify({
      message: messaggio,
      content: btoa(unescape(encodeURIComponent(content))),
      sha,
    }),
  });
  if (res.ok) return { ok: true };
  return { ok: false, status: res.status, testo: short(await res.text(), 200) };
}

function intestazioniGh(env) {
  return {
    Authorization: `Bearer ${env.GITHUB_TOKEN}`,
    "User-Agent": "smh-approvazioni",
    Accept: "application/vnd.github+json",
  };
}

// ------------------------------------------------------------
// Telegram
// ------------------------------------------------------------
async function rispondiAlClick(env, callbackQueryId, testo) {
  await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/answerCallbackQuery`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ callback_query_id: callbackQueryId, text: testo || "" }),
  });
}

async function inviaMessaggio(env, chatId, testo) {
  await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text: testo }),
  });
}

// ------------------------------------------------------------
// Utility
// ------------------------------------------------------------
function autorizzato(env, chatId) {
  const ammessi = (env.AUTHORIZED_CHAT_IDS || "").split(",").map((s) => s.trim()).filter(Boolean);
  return ammessi.includes(String(chatId));
}

function mittente(from) {
  if (!from) return "sconosciuto";
  const nome = [from.first_name, from.last_name].filter(Boolean).join(" ");
  return from.username ? `${nome} @${from.username}` : nome || String(from.id);
}

function primaRiga(testo) {
  if (!testo) return "(nessun riferimento)";
  const r = String(testo).split("\n").find((x) => x.trim());
  return short((r || "").replace(/[\r\n|]/g, " ").trim(), 90) || "(nessun riferimento)";
}

function short(s, max) {
  s = String(s || "");
  return s.length > max ? s.slice(0, max - 1) + "…" : s;
}

function adesso() {
  return new Date().toISOString();
}

function attendi(ms) {
  return new Promise((r) => setTimeout(r, ms));
}
