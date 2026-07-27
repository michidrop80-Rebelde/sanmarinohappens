# Deploy del Worker approvazioni — istruzioni per Michele

Preparato il **27/07/2026**. Serve a far sì che le tue risposte ✅/❌ **non scadano più**
(oggi Telegram le butta dopo 24 ore — vedi `docs/FIX-APPROVAZIONI-CHE-SCADONO.md`).

⚠️ **L'ordine conta.** Appena si accende il webhook, il vecchio metodo (`getUpdates`) smette
di funzionare **per sempre** su quel bot. Quindi si accende **per ultimo**.

| # | Passo | Chi |
|---|-------|-----|
| 1 | Insegnare alla skill a leggere dal file | ✅ **già fatto** |
| 2 | Creare il Worker su Cloudflare e fare Deploy | 👉 **tu** |
| 3 | Accendere il webhook | io, quando mi dici che il 2 è fatto |
| 4 | Prova dal vivo con un pulsante | io + tu |

---

## Passo 2 — cosa devi fare tu (5 minuti)

1. Vai su **dash.cloudflare.com** → *Workers & Pages* → **Create** → *Start with Hello World!*
   → chiamalo **`smh-approvazioni`** → Deploy.
2. Apri **Edit code**, cancella tutto e incolla il contenuto di
   **`infra/cloudflare/smh-approvazioni-worker.js`**. Poi **Deploy**.
3. Vai su **Settings → Variables and Secrets** e aggiungi queste 5 voci
   (le prime due come **Secret**, le altre come Text):

   | Nome | Valore | Tipo |
   |------|--------|------|
   | `TELEGRAM_BOT_TOKEN` | il token di **@sanmarinohappens_bot** (quello delle approvazioni, **non** quello degli eventi) | Secret |
   | `GITHUB_TOKEN` | lo stesso PAT che usa già l'altro Worker | Secret |
   | `GITHUB_OWNER` | `michidrop80-Rebelde` | Text |
   | `GITHUB_REPO` | `sanmarinohappens` | Text |
   | `AUTHORIZED_CHAT_IDS` | il tuo chat id (te lo do io se serve) | Text |

4. Fai **Deploy** di nuovo e copiami l'indirizzo del Worker
   (qualcosa come `https://smh-approvazioni.<tuo-nome>.workers.dev`).

🔐 **Il token non va mai scritto nel codice**, solo nelle variabili: il codice sta su GitHub in
un repo pubblico, le variabili no.

---

## Passo 3 — lo faccio io

Con l'indirizzo del Worker accendo il webhook:

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://smh-approvazioni.<tuo-nome>.workers.dev" \
  -d "allowed_updates=[\"callback_query\",\"message\"]"
```

`allowed_updates` è importante: senza, Telegram potrebbe non mandare i click sui pulsanti.

## Passo 4 — la prova

Tu premi **un** pulsante ✅. Io controllo che compaia una riga in `queue/approvazioni.md`
sul repo. Se c'è, abbiamo finito: da quel momento puoi rispondere quando ti pare, anche
una settimana dopo, e la risposta resta lì ad aspettare.

---

## Se qualcosa va storto

- **Il pulsante gira e non succede niente** → il Worker non risponde: guarda i log in
  Cloudflare (*Workers → smh-approvazioni → Logs*). Quasi sempre è una variabile scritta male.
- **Vuoi tornare indietro** → si spegne il webhook e torna a funzionare `getUpdates`:
  ```bash
  curl -s "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
  ```
- **Le righe non arrivano su GitHub** → è il `GITHUB_TOKEN`: deve avere il permesso di
  scrittura sui contenuti del repo `sanmarinohappens`.

## Nota tecnica (per me, la prossima volta)

Il Worker ha un ciclo di **ritentativi sui conflitti** quando scrive su GitHub. Serve davvero:
premendo 17 pulsanti di fila arrivano 17 richieste in parallelo che scrivono tutte sullo stesso
file, e l'API di GitHub rifiuta quelle con lo `sha` ormai vecchio (409). Senza i ritentativi si
perderebbe la maggior parte delle approvazioni — cioè lo stesso guasto che stiamo riparando.
