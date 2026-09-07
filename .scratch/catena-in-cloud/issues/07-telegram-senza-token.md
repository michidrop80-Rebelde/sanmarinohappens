# 07 — Mandare i pulsanti su Telegram senza dare il token all'agente

Type: grilling
Status: aperto
Blocked by: 02
Modello: Opus — sicurezza: qui un errore lo paghi, non lo scopri
Sforzo: media (una sessione)

## Domanda

L'agente di ricerca legge pagine web scritte da sconosciuti. Se una contenesse istruzioni malevole
nascoste, non deve avere niente in mano da poter usare. Quindi: **l'agente non tocca mai
`TELEGRAM_BOT_TOKEN`**.

Disegno proposto: l'agente **scrive il messaggio in un file** (es. `queue/telegram-da-inviare.json`),
e un passo separato del workflow — senza AI, stupido — lo spedisce col token. Il token vive solo in
quel passo.

**Da verificare che regga davvero il caso vero**, che non è un messaggio di testo:
- il riepilogo porta i **pulsanti** ✅/❌ sotto ogni evento (`approve_[ID]` / `reject_[ID]`) — la
  forma buona, decisa il 27/07
- serve il **`giro_id`** nei pulsanti (è un punto rimasto aperto in
  `project_catena_solo_il_martedi`) — se lo si sta costruendo da capo, va chiuso adesso
- le risposte tornano nel Worker Cloudflare che scrive in `queue/approvazioni.md`: quel pezzo **non
  cambia** e non va toccato
- ⚠️ da Python su questo Mac l'invio SSL fallisce e si usa `curl`: verificare come si comporta
  dentro Actions, e ricordare che **uno script che non invia non deve salvare lo stato**

**Fatto quando:** il disegno è deciso e c'è un messaggio di prova coi pulsanti veri arrivato sul
telefono di Michele, mandato senza che il passo agentico abbia mai visto il token.
