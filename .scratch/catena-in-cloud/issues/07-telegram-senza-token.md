# 07 — Mandare i pulsanti su Telegram senza dare il token all'agente

Type: grilling
Status: resolved
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

## Answer

**Deciso e costruito il 07/09/2026. Il disegno proposto regge, con quattro precisazioni
prese con Michele.**

Prima di tutto, due punti del ticket erano **già chiusi** e non andavano rifatti:
- il **`giro_id` nei pulsanti c'è dal 10/08/2026** (`approve_20260907-0654-03`), il Worker
  lo passa intero e `/smh-approvazione` sa leggerlo. Verificato sulle 4 approvazioni vere
  di stamattina in `queue/approvazioni.md`. Il punto rimasto aperto in
  `project_catena_solo_il_martedi` era **stantio**.
- il modello «passo stupido col token» era **già provato in cloud** dalla sonda (ticket 05).
  Quello che mancava era farlo **coi pulsanti** e con la mappa del giro.

### Le quattro decisioni (Michele, 07/09/2026)

1. **I pulsanti li disegna lo script, non l'agente.** L'agente passa solo la lista nuda
   degli eventi; testo, blocchi da 3, `giro_id` e pulsanti li costruisce Python. Se una
   pagina web avvelenasse l'agente, il massimo che può fare è mentire su un titolo: la
   forma dei pulsanti non la tocca.
2. **Una strada sola, uguale sul Mac e in cloud.** Sul Mac la barriera è più simbolica (i
   file l'agente li legge comunque), ma una strada che gira ogni giro è collaudata; una che
   gira solo in cloud di notte si scopre rotta il lunedì mattina.
3. **La busta che resta è l'allarme.** `queue/telegram-da-inviare.json` entra in git e viene
   cancellata **solo** dopo la conferma di Telegram. Se domani è ancora lì, l'invio non è
   riuscito — ed è un fatto scritto, non una run rossa che di notte non guarda nessuno.
   `prepara` si rifiuta di sovrascriverne una (uscita 6).
4. **Invio a metà: la mappa si salva comunque.** I pulsanti già arrivati esistono e Michele
   li premerà: senza mappa quelle risposte diventerebbero non mappabili (il guasto
   dell'08/08). Si salva, si manda una riga che dice che la lista è **incompleta**, uscita 3.

### Com'è fatto

`.claude/scripts/telegram-giro.py` ha due comandi:

| comando | ha il token? | cosa fa |
|---|---|---|
| `prepara --events '[...]' [--prova]` | **no** | costruisce riepilogo + blocchi da 3 + pulsanti e scrive la busta `queue/telegram-da-inviare.json` |
| `invia` | **sì, l'unico** | controlla la busta, spedisce, salva `dati/telegram/pending/<giro>.json` + `ultimo-giro.txt`, poi cancella la busta |

- **`invia` non si fida della busta**: `controlla_busta()` pretende `callback_data` del giro
  dichiarato, solo `approve`/`reject`, testo `✅`/`❌`, evento presente in busta, ≤64 byte,
  ≤4096 caratteri. Una busta scritta a mano da un agente ingannato **non parte** (uscita 4).
  È questo che rende vera la decisione 1, invece di lasciarla a un commento.
- **Puntatore versionato** `dati/telegram/pending/ultimo-giro.txt`: in cloud
  `.claude/secrets/telegram-state.json` non esiste e l'approvazione non saprebbe quale mappa
  aprire. Sul Mac il vecchio file resta allineato.
- **Giri di collaudo**: `--prova` mette il prefisso `PROVA-` nel `giro_id`, e
  `/smh-approvazione` chiude quelle righe come collaudo senza toccare niente.
- L'invio con pulsanti è passato in `scripts/telegram_helper.py` (`manda_messaggio`), unico
  posto che tocca il token: `requests` e ripiego su `curl` (l'SSL rotto del Mac). **In
  Actions `requests` funziona** — verificato dal vivo.

### La guardia che rende la decisione durevole

`scripts/controllo-token-agente.py`: legge i workflow e va in rosso se un passo che lancia
`claude` ha in mano una chiave (Telegram/Instagram/Facebook/Canva/PAT) — **anche quando la
chiave è dichiarata a livello di workflow o di job**, che è la trappola che non si vede.
Agganciata a `guardia-integrita.yml`, che gira a ogni push. Provata su casi finti: becca il
caso nel passo, becca quello ereditato, non grida sui workflow senza agente.

### La prova dal vivo

Workflow `prova-pulsanti.yml` (a mano). Passo 1 = l'agente, con **solo**
`CLAUDE_CODE_OAUTH_TOKEN`; prima di partire si guarda le tasche (`env | grep -i telegram`) e
si ferma se trovasse una chiave. Passo 2 = il postino, con **solo** le chiavi Telegram.

- Run [#34155483208](https://github.com/michidrop80-Rebelde/sanmarinohappens/actions/runs/34155483208)
  **verde** (07/09/2026 19:24): messaggio 🧪 PROVA arrivato sul telefono di Michele coi
  **pulsanti veri**, giro `PROVA-20260907-1925`. Michele ha premuto ✅ e il Worker ha scritto
  `- [ ] ... approvato — PROVA-20260907-1925-01` in `queue/approvazioni.md` (commit `6182017`).
  **Giro completo dimostrato, con l'agente che non ha mai visto il token.**
- 🔴 **Difetto trovato proprio verificando** (e questo è il valore della corsa): il passo di
  commit era verde ma **non aveva committato la mappa**. `git add -A dati/telegram
  queue/telegram-da-inviare.json` in un comando solo fallisce **tutto** quando la busta non
  esiste più (invio riuscito), e il `|| true` mangiava l'errore. In un giro vero = mappa
  numero→evento persa. Corretto (`e53d7dd`): due `git add` separati + **rosso** se l'invio è
  riuscito ma non c'è niente da committare. Provato in un repo finto: vecchia riga
  `staged=[]`, nuova `staged=[la mappa]`, invio fallito `staged=[la busta]`.

### Cosa eredita il ticket 08

Il blocco a due passi di `prova-pulsanti.yml` è già collaudato e si copia così com'è. Quello
che lì cambia è solo **cosa** l'agente mette in busta: eventi veri invece di due finti.

### Prove che girano

`telegram_giro_test.py` 38/38 (busta non sovrascritta · dubbio muto · le 6 storpiature di
busta rifiutate · niente inviato → busta intatta e nessuno stato · invio a metà → mappa
salvata + avviso) · `controllo_token_agente_test.py` 7/7 · `controllo-integrita.py` ✅ 130.
