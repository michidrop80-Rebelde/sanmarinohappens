# Bot Telegram — gestione FOTO (design)
Data: 2026-07-23 · Stato: approvato da Michele, da implementare + deployare

## Problema
Il Worker `smh-bot-worker.js` scarta **ogni messaggio senza testo** (riga: `if (!message || !message.text) return`).
Chi manda una **foto** (anche con didascalia) non riceve **nessuna risposta** e la foto **non viene salvata** da nessuna
parte. Caso reale 21/07/2026: Michele ha mandato 2 foto con appuntamenti sopra → nessuna traccia in `queue/inbox.md`,
appuntamenti persi. (Il testo invece funziona: ha `message.text` → viene instradato, salvato e risponde.)

## Obiettivo
Quando arriva una foto: salvarla, avvisare il mittente, e far sì che gli eventi che ci sono sopra entrino nella catena
come tutti gli altri (`da-verificare` → verifica → …). Chi legge la foto è **Claude** (vision), non Michele.

## Soluzione — due pezzi

### Pezzo 1 — Worker (Cloudflare)
Nuovo ramo per i messaggi con `message.photo`:
1. Prende la foto a risoluzione più alta (`message.photo[last].file_id`).
2. `getFile` → `file_path` → scarica i byte da `https://api.telegram.org/file/bot<token>/<file_path>`.
3. **Committa l'immagine nel repo** in `queue/foto/<ISO-compatta>_<chatId>.jpg` (byte reali, non un riferimento
   Telegram: è l'unico modo perché Claude possa poi vederla dal Mac — il token di questo bot è un secret CF, non è
   sul Mac).
4. Aggiunge una riga in **`queue/foto-inbox.md`**:
   `- [ ] <ISO> — <nome @username> — queue/foto/<file>.jpg — didascalia: <caption o "(nessuna)">`
5. **Risponde** al mittente: «📷 Ho ricevuto la foto e l'ho salvata — la guardo io e ne ricavo gli eventi. Grazie!»

Dettagli:
- **Più foto insieme** (media group): Telegram le manda come messaggi separati → un salvataggio + una risposta
  ciascuna. Semplice e robusto (niente stato tra richieste).
- **Base64 binario**: l'immagine va convertita byte→base64 SENZA il trucco `unescape(encodeURIComponent())` (che è
  per il testo UTF-8). Si usa una conversione binaria diretta (Uint8Array → stringa binaria a blocchi → `btoa`).
- **Autorizzazione**: invariata (`AUTHORIZED_CHAT_IDS`). Bot privato = solo Michele. Repo pubblico ma le foto sono
  manifesti/eventi pubblici → ok committarle.
- Nessun altro comportamento cambia (testo, bottoni, annullamento, calendario restano identici).

### Pezzo 2 — Postino (`/smh-postino`)
Oltre a drenare `queue/inbox.md` (testo), il postino drena anche **`queue/foto-inbox.md`**:
1. Per ogni riga `- [ ]` non ancora processata: **apre l'immagine** `queue/foto/<file>.jpg` (Read/vision).
2. Ne ricava gli eventi e li scrive in `dati/eventi/eventi-AAAA-MM-GG.md` come **`da-verificare`** (stesso schema del
   testo). Regola d'oro: dato mancante → «non specificato», MAI inventato. Se la foto non contiene un evento
   riconoscibile, la segnala e la lascia (non forza).
3. **Archivia**: sposta l'immagine in `queue/foto/archivio/` (o segna la riga `- [x]`) e committa, così non viene
   riletta al giro dopo. La didascalia della riga è un aiuto in più per l'estrazione.
4. Da lì gli eventi proseguono in **verifica** come tutti gli altri.

## Cosa NON cambia
- Niente va online in automatico (sempre revisione umana a valle).
- Il **deploy del Worker** su Cloudflare lo fa **Michele** (Claude non ha le credenziali CF). Passi in `DEPLOY.md`.
- La catena a valle (verifica → testi → …) è identica.

## Test previsti (senza rete)
- Conversione byte→base64 su un buffer noto (round-trip).
- Parsing di `queue/foto-inbox.md` (righe `- [ ]`, con/ senza didascalia).
- Instradamento: un update con `message.photo` (e senza `text`) prende il ramo foto; testo/bottoni invariati.

## File toccati
- `infra/cloudflare/smh-bot-worker.js` (ramo foto + helper download/base64/append)
- `infra/cloudflare/DEPLOY.md` (passo deploy + prova)
- `queue/foto/.gitkeep`, `queue/foto-inbox.md` (nuovi, vuoti)
- `.claude/skills/smh-postino/SKILL.md` + `.claude/agents/smh-postino.md` (lettura foto-inbox)
