// ============================================================
// SMH Bot — Cloudflare Worker  (@sanmarinohappens_add_bot)
// ============================================================
// COSA FA:
// 1. Riceve i messaggi del bot Telegram via webhook.
// 2. Controlla che il mittente sia autorizzato (AUTHORIZED_CHAT_IDS).
// 3. Comandi:
//    /smh-aggiungi <descrizione>  aggiunge un evento alla coda
//    /smh-lista                   mostra gli eventi in coda
//    /smh-cancella <numero>       rimuove un evento dalla coda
// 4. Scrive/legge queue/inbox.md nel repo GitHub via Contents API.
//    Da lì il "postino" della catena importerà gli eventi come
//    da-verificare: NIENTE va online in automatico, tutto passa
//    prima dalla revisione umana.
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

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("SMH bot attivo ✅", { status: 200 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("bad request", { status: 400 });
    }

    const message = update.message;
    if (!message || !message.text) {
      // ignora update senza testo (edit, sticker, foto, ecc.)
      return new Response("ok");
    }

    const chatId = String(message.chat.id);
    const authorized = (env.AUTHORIZED_CHAT_IDS || "")
      .split(",")
      .map((id) => id.trim())
      .filter(Boolean);

    if (!authorized.includes(chatId)) {
      // Messaggio gentile e "di marca", ma SENZA svelare i comandi:
      // questo è il bot interno; il pubblico avrà il suo, con la sala d'attesa.
      await sendTelegramMessage(
        env,
        chatId,
        "Ciao! 👋 Questo è il bot interno di San Marino Happens 🇸🇲, per ora riservato allo staff.\n\nSe vuoi segnalarci un evento del Titano, scrivici pure su Instagram o Facebook: @sanmarinohappens. Grazie! 😊"
      );
      return new Response("ok");
    }

    const text = message.text.trim();

    if (text.startsWith("/smh-aggiungi")) {
      const eventText = text.replace("/smh-aggiungi", "").trim();

      if (!eventText) {
        await sendTelegramMessage(
          env,
          chatId,
          "Ci sei quasi! 😊 Scrivimi l'evento subito dopo il comando, così:\n/smh-aggiungi Concerto in Piazza della Libertà sabato alle 21"
        );
        return new Response("ok");
      }

      try {
        await appendToQueue(env, eventText);
        await sendTelegramMessage(
          env,
          chatId,
          "✅ Segnato, grazie della dritta! L'ho messo in lista.\n\nNiente va online da solo: passerà prima dalla revisione. 👀🇸🇲"
        );
      } catch (err) {
        await sendTelegramMessage(env, chatId, "⚠️ Ops, non sono riuscito a salvarlo su GitHub: " + err.message);
      }
    } else if (text === "/smh-lista") {
      try {
        const items = await listQueue(env);
        if (items.length === 0) {
          await sendTelegramMessage(env, chatId, "📭 Per ora la lista è vuota — nessun evento in attesa.\n\nQuando ne scovi uno bello, mandamelo con /smh-aggiungi! 🇸🇲");
        } else {
          const lines = items
            .map((item, i) => `${i + 1}. ${item.text}`)
            .join("\n");
          await sendTelegramMessage(env, chatId, `📋 Ecco cosa c'è in lista:\n\n${lines}\n\nPer toglierne uno: /smh-cancella <numero>`);
        }
      } catch (err) {
        await sendTelegramMessage(env, chatId, "⚠️ Non riesco a leggere la lista: " + err.message);
      }
    } else if (text.startsWith("/smh-cancella")) {
      const arg = text.replace("/smh-cancella", "").trim();
      const index = parseInt(arg, 10);

      if (!arg || isNaN(index) || index < 1) {
        await sendTelegramMessage(env, chatId, "Dimmi quale numero tolgo, così:\n/smh-cancella 2\n\n(i numeri li trovi con /smh-lista)");
        return new Response("ok");
      }

      try {
        const removed = await removeFromQueue(env, index - 1);
        if (removed) {
          await sendTelegramMessage(env, chatId, `🗑 Fatto, ho tolto:\n"${removed}"`);
        } else {
          await sendTelegramMessage(env, chatId, "Mmm, non trovo un evento con quel numero. 🤔\nControlla con /smh-lista quali ci sono.");
        }
      } catch (err) {
        await sendTelegramMessage(env, chatId, "⚠️ Non riesco a cancellarlo: " + err.message);
      }
    } else if (text === "/start" || text === "/aiuto" || text === "/help") {
      await sendTelegramMessage(
        env,
        chatId,
        "Ciao, benvenuto! 👋 Sono il bot di San Marino Happens 🇸🇲\n\n" +
        "Raccolgo gli eventi belli del Titano che mi segnali. I comandi sono semplici, promesso:\n\n" +
        "➕ /smh-aggiungi <evento> — aggiungo un evento alla lista\n" +
        "📋 /smh-lista — ti mostro cosa c'è in lista\n" +
        "🗑 /smh-cancella <numero> — tolgo un evento (il numero lo prendi da /smh-lista)\n\n" +
        "Esempio:\n/smh-aggiungi Concerto in Piazza della Libertà sabato alle 21\n\n" +
        "Una cosa importante: quello che mi mandi non viene pubblicato in automatico — passa sempre da una revisione prima di finire online. Tu segnala pure, al controllo ci pensiamo noi. 😉"
      );
    } else {
      await sendTelegramMessage(env, chatId, "Questo comando non lo conosco. 🤔\nProva con /smh-aggiungi, /smh-lista o /smh-cancella — oppure /start per rivedere le istruzioni.");
    }

    return new Response("ok");
  },
};

// ------------------------------------------------------------
// Legge il file coda da GitHub (Contents API)
// Ritorna { content, sha } — content è "" e sha undefined se il file non esiste ancora
// ------------------------------------------------------------
async function readQueueFile(env) {
  const apiUrl = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${env.QUEUE_PATH}`;

  const getRes = await fetch(apiUrl, {
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      "User-Agent": "smh-bot",
      Accept: "application/vnd.github+json",
    },
  });

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
    // il file non esiste ancora: verrà creato al primo salvataggio
    return { content: "", sha: undefined };
  } else {
    throw new Error(`GitHub read failed: ${getRes.status}`);
  }
}

// ------------------------------------------------------------
// Scrive (crea o aggiorna) il file coda su GitHub
// ------------------------------------------------------------
async function writeQueueFile(env, content, sha, commitMessage) {
  const apiUrl = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${env.QUEUE_PATH}`;

  const putRes = await fetch(apiUrl, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      "User-Agent": "smh-bot",
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
    },
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

// ------------------------------------------------------------
// Estrae le righe evento (formato "- [ ] timestamp — testo") dal contenuto del file
// ------------------------------------------------------------
function parseQueueLines(content) {
  return content
    .split("\n")
    .filter((line) => line.trim().startsWith("- [ ]"))
    .map((line) => {
      // rimuove il prefisso "- [ ] " e prova a togliere anche il timestamp iniziale
      const withoutPrefix = line.replace(/^- \[ \]\s*/, "");
      const dashIndex = withoutPrefix.indexOf("—");
      const text = dashIndex >= 0 ? withoutPrefix.slice(dashIndex + 1).trim() : withoutPrefix.trim();
      return { raw: line, text };
    });
}

// ------------------------------------------------------------
// Aggiunge un evento in coda
// ------------------------------------------------------------
async function appendToQueue(env, eventText) {
  const { content, sha } = await readQueueFile(env);

  const timestamp = new Date().toISOString();
  const newLine = `- [ ] ${timestamp} — ${eventText}\n`;
  const updatedContent = content + newLine;

  await writeQueueFile(env, updatedContent, sha, `Nuovo evento in coda: ${eventText.slice(0, 50)}`);
}

// ------------------------------------------------------------
// Ritorna la lista degli eventi attualmente in coda
// ------------------------------------------------------------
async function listQueue(env) {
  const { content } = await readQueueFile(env);
  return parseQueueLines(content);
}

// ------------------------------------------------------------
// Rimuove l'evento all'indice indicato (0-based). Ritorna il testo
// rimosso, o null se l'indice non esiste.
// ------------------------------------------------------------
async function removeFromQueue(env, index) {
  const { content, sha } = await readQueueFile(env);
  const items = parseQueueLines(content);

  if (index < 0 || index >= items.length) {
    return null;
  }

  const removed = items[index];
  const remainingLines = items
    .filter((_, i) => i !== index)
    .map((item) => item.raw)
    .join("\n");
  const updatedContent = remainingLines ? remainingLines + "\n" : "";

  await writeQueueFile(env, updatedContent, sha, `Rimosso evento dalla coda: ${removed.text.slice(0, 50)}`);

  return removed.text;
}

// ------------------------------------------------------------
// Risponde su Telegram
// ------------------------------------------------------------
async function sendTelegramMessage(env, chatId, text) {
  const url = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text }),
  });
}
