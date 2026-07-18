# Come aggiornare il bot Telegram `@sanmarinohappens_add_bot`

Il bot è un **Cloudflare Worker** (`smh-bot`) sull'account Cloudflare **dedicato** di
San Marino Happens (separato da quello di famiglia). Il codice vive in
[`smh-bot-worker.js`](smh-bot-worker.js). Cloudflare **non** si aggiorna da solo quando
si fa `git push`: il push serve solo a versionare il codice. Per mandarlo davvero online
bisogna fare il **deploy a mano** dal pannello Cloudflare (2 minuti).

Questi passi servono **solo a Michele**: richiedono l'accesso all'account Cloudflare e a
BotFather, che nessun altro (nemmeno l'assistente AI) può toccare.

---

## 1 · Deploy del codice su Cloudflare (~2 min)

1. Apri il file `infra/cloudflare/smh-bot-worker.js`, seleziona tutto (⌘A) e copia (⌘C).
2. Vai su **dash.cloudflare.com** → entra con l'account **San Marino Happens**.
3. Menù laterale → **Workers & Pages** → clicca sul Worker **`smh-bot`**.
4. In alto a destra → **Edit code** (o «Quick edit»).
5. Nell'editor: seleziona tutto il codice vecchio, cancellalo, **incolla** il nuovo.
6. Clicca **Deploy** (o «Save and deploy»).
7. Fatto. Non c'è nessuna variabile da cambiare (`TELEGRAM_BOT_TOKEN`, `GITHUB_TOKEN`,
   `GITHUB_OWNER`, `GITHUB_REPO`, `QUEUE_PATH`, `AUTHORIZED_CHAT_IDS` restano quelle che sono).

**Verifica veloce:** apri nel browser `https://smh-bot.sanmarinohappens.workers.dev/` →
deve rispondere `SMH bot attivo ✅`.

---

## 2 · Menù comandi su BotFather (~1 min)

Serve perché premendo `/` in chat compaiano i comandi suggeriti. Telegram nel menù accetta
**solo comandi senza trattino** (per questo i vecchi `/smh-lista` non comparivano).

1. Apri **@BotFather** su Telegram.
2. Scrivi `/setcommands`.
3. Scegli **@sanmarinohappens_add_bot**.
4. Incolla **esattamente** questo blocco (poi invia):

```
aggiungi - ➕ Segnala un evento (poi scrivilo)
segnalazioni - 📋 Le segnalazioni in attesa
calendario - 🗓 Cosa sta per uscire
aiuto - ❓ Come funziona il bot
```

> ⚠️ Fai questo passo **dopo** il deploy (passo 1), non prima: altrimenti il menù
> mostrerebbe comandi che il codice vecchio non sa ancora gestire.

---

## 3 · Prova dal telefono (~2 min)

- `/start` → arriva il benvenuto **con la tastiera di bottoni** in basso?
- **🗓 Calendario** → mostra i contenuti già programmati?
- Scrivi un messaggio qualsiasi (es. `Prova evento test`) → risponde «Segnato»?
  Poi **📋 Lista segnalazioni** lo mostra con un bottone **🗑**? Premendo 🗑 sparisce?
- Premi `/` → compaiono i 4 comandi suggeriti?

Se tutto risponde di sì, il bot v2 è completo e live. 🎉

---

## Cosa fa il bot (riassunto)

- **Tastiera di bottoni** sempre visibile: ➕ Aggiungi evento · 📋 Lista segnalazioni ·
  🗓 Calendario · ❓ Aiuto.
- **Aggiungere un evento**: premi ➕ *oppure* scrivi l'evento come messaggio normale
  (qualsiasi testo libero, senza comandi, finisce in lista).
- **📋 Lista segnalazioni**: gli eventi segnalati e non ancora lavorati; ognuno con un
  bottone 🗑 per toglierlo. (Passano poi dalla revisione → spariscono da qui.)
- **🗓 Calendario**: legge i post già programmati nel repo (`posts/*.json`) e mostra cosa
  sta per uscire su @sanmarinohappens.
- **Sicurezza**: solo il chat_id di Michele (`AUTHORIZED_CHAT_IDS`) ha accesso ai comandi;
  chiunque altro riceve solo un messaggio di cortesia. Niente va online in automatico:
  tutto passa dalla revisione umana.
