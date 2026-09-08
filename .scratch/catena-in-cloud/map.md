# Mappa — La catena si stacca dal Mac

Label: `wayfinder:map` · Aperta: 06/09/2026

## Destinazione

La **preparazione** della catena (ricerca → postino → verifica → testi → approvazioni) gira su
**GitHub Actions** a orario, da sola, senza che l'app Claude sia aperta sul Mac.

Ci siamo arrivati quando: i due task locali (`smh-giro-settimanale`, `smh-catena`) sono **spenti**,
i workflow in cloud girano da soli, e Michele apre il Mac **solo per la grafica** — non a orario,
ma quando gli pare, con la lista già pronta.

## Note

**Dominio:** automazione di una catena di agenti Claude Code per @sanmarinohappens.

**Chi legge:** Michele non programma. Ogni ticket, ogni risposta e ogni referto vanno scritti in
italiano semplice, spiegando cosa fa ogni pezzo. Mai gergo senza traduzione.

**Questa mappa PORTA ANCHE L'ESECUZIONE** (deroga esplicita al «pianifica, non fare» di wayfinder):
il progetto lavora così — una sessione = un pezzo costruito, verificato e consegnato, con il prompt
pronto per la sessione dopo. Un ticket è chiuso quando la cosa **funziona**, non quando è decisa.

**Regole del progetto che valgono in ogni ticket:**
- ⚠️ **MAI inventare** dati, nomi, date, eventi o fonti. Se manca, si scrive «da verificare».
- Una guardia che trova un problema lo **chiude**, non consegna un elenco a Michele.
- Preferire sempre soluzioni gratuite.
- Verificare, non rassicurare: se dico «funziona», deve esserci l'output che lo prova.

**Skill da consultare:** `lavorare-leggeri` a inizio sessione; `/grilling` e `/domain-modeling` sui
ticket di discussione; le skill del progetto (`smh-*`) come fonte di verità sul funzionamento attuale.

**Vincoli duri:**
- Il repo `sanmarinohappens` **è pubblico e deve restarlo** (Meta scarica i PNG da
  raw.githubusercontent senza autenticazione). Quindi **i log delle run sono pubblici**.
- L'agente di ricerca legge pagine web di sconosciuti → è esposto a istruzioni malevole nascoste
  nei contenuti. Non deve avere segreti in mano.
- La **grafica Canva resta sul Mac** in questa mappa. Non è un ripiego: è una scelta.

## Punto di partenza — già deciso e già fatto (06/09/2026, prima della mappa)

- **n8n e Coolify scartati.** n8n è un quadro elettrico per cose meccaniche, la catena *ragiona*;
  riscriverla lì significherebbe perdere il giudizio. n8n Cloud non ha più il piano gratuito ($24/mese).
  Coolify non fa nulla da solo: è un pannello per un server che devi già avere.
- **Scelta la piattaforma: GitHub Actions.** È dove il progetto già abita (publish.py, guardia
  imminenti, cron-job.org). Claude si autentica con `CLAUDE_CODE_OAUTH_TOKEN`, che usa
  **l'abbonamento** e non il consumo API. Scartata per ora la Routine cloud di Anthropic (research
  preview, incerto se regga gli script Python e i push). Server proprio (Oracle Always Free)
  accantonato — servirà per il bot Telegram pubblico, non per questo.
- **Fase 1 = solo i 4 anelli di testo.** La grafica resta sul Mac finché il nodo Canva non è sciolto.
- ✅ **Messa in sicurezza fatta.** Backup cervello aggiornato (era fermo al 13/08, 42 file mai
  salvati) → `sanmarinohappens-cervello` commit `7d3375f`. Time Machine ricollegato e backup
  completato (06/09 19:11, `RESULT = 0`). **Punto di ritorno: tag `prima-del-cloud`** su entrambi
  i repo → `git checkout prima-del-cloud`.
- **Tre conseguenze accettate:** il repo diventa l'unica verità · i task locali si spengono (non
  restano come rete di sicurezza: il lucchetto è un file locale e non vede l'altra macchina) ·
  l'agente in cloud non tocca mai il token Telegram.

## Decisioni prese (indice)

<!-- una riga per ticket chiuso: il succo + il link. Il dettaglio vive nel ticket. -->

- [01 — Dove vive il cervello che il cloud deve leggere?](issues/01-dove-vive-il-cervello.md) —
  **Tutto nel repo pubblico.** Scoperto che quei file non erano *esclusi*, non erano mai stati
  **committati**: nessuna regola li teneva fuori, e una parte (8 bozze, 4 approvati, tutta `queue/`)
  e' gia' pubblica da mesi. Cercati i segreti in tutti e **61 i file (1,4 MB)**: nei dati di lavoro
  non ce n'e' nessuno. Scartato il repo privato non perche' non reggerebbe — il «cervello» e' un
  repo git vero, non un album di fotografie — ma perche' costringerebbe ogni giro in cloud a
  clonare **due repo nella stessa cartella** e fare due push, col caso «uno riesce, l'altro no».
  🚫 Restano fuori **tre file di documentazione**: due guide con l'email personale di Michele;
  `fonti-sport.md` entra ma **ripulito** dalla password `RBA25`. Il cervello privato **resta un
  backup**, non diventa un canale di lavoro. → allarga il ticket 03 (da 6 file a 61).
  🔴 La domanda che ne discendeva ha aperto il **ticket 13**: oggi verifica e testi prendono «il
  file piu' recente» **senza chiedersi quanto** e' recente — in cloud lavorerebbero dati morti di
  notte, senza accorgersene. Deciso: l'anello **si ferma** e manda un Telegram (eventi = stesso
  giorno, verificati = max 2 giorni).

- [02 — Che limiti ha Claude Code dentro GitHub Actions?](issues/02-limiti-claude-code-in-actions.md) —
  **Può girare, ma non così com'è.** Il token dura un anno e non avvisa prima di scadere; le run
  pesano **sull'abbonamento di Michele** (stesso serbatoio dell'app: un giro pesante può lasciarlo
  senza Claude sul Mac); job max 6 ore e chi sfora perde il non committato; skill e subagenti
  funzionano headless ma i permessi vanno passati dal workflow (quelli del file vengono ignorati su
  cartella non fidata); l'OAuth MCP **non** è eseguibile headless → conferma del muro Canva.
  🔴 Il blocco vero sono **45 percorsi assoluti `/Users/michele/...`** (13 file di skill/agenti + 4
  negli script) → ticket 11. Documento: [`research/02-limiti-actions.md`](research/02-limiti-actions.md)

- [03 — Portare nel repo pubblico i file che al clone mancano](issues/03-sei-file-mancanti.md) —
  **Fatto** (commit `2b67c1c`). Entrati i 6 file citati e mai committati + tutta la memoria di
  lavoro della catena (63 file: eventi, verificati, post, approvati, pending, config, metriche,
  diario). Fuori le 2 guide con l'email personale di Michele; `fonti-sport.md` entra **ripulito**
  dalla password `RBA25`. Segreti cercati sui 63 file: nessuno. `controllo-integrita.py` ora sa se
  gira **fuori dal Mac** (in cloud non cerca `~/.claude/scheduled-tasks`, tollera i
  `.claude/secrets/*`). Nuova guardia automatica: workflow `guardia-integrita.yml` a ogni push su
  `main` (il checkout è un clone pulito) → rosso + Telegram se manca un file. Verificato: run
  Actions [#34148842889](https://github.com/michidrop80-Rebelde/sanmarinohappens/actions/runs/34148842889)
  verde sul clone vero.

- [05 — La sonda: un giro finto che prova tutto](issues/05-la-sonda.md) —
  **La strada regge.** Workflow `sonda-catena.yml` (`workflow_dispatch`), run verde 06/09: Claude in
  cloud si autentica con l'abbonamento, legge `master.md` e **cita un evento vero**, fa una ricerca
  web, scrive un referto, commit+push, Telegram. **I due numeri:** un giro-giocattolo dura **47 s** e
  vale **$0,285** (10 turni) — base di partenza per il ticket 06, non più una stima. `controllo-
  integrita.py` esce 1 ma **non** per i percorsi assoluti (ticket 11): per 9 file/segreti che in cloud
  mancano → alimenta il ticket 03. Subagenti `.claude/agents/` ancora non esercitati. Node 20
  deprecato su checkout@v3 / setup-python@v4 in tutti i workflow del repo (manutenzione, non blocca).

- [04 — Il token dell'abbonamento nei segreti di GitHub](issues/04-token-abbonamento.md) —
  **Fatto.** `CLAUDE_CODE_OAUTH_TOKEN` (da `claude setup-token`, usa l'abbonamento non l'API a
  pagamento) è nei segreti Actions del repo. Scade **06/09/2027**, non avvisa → annotato in
  `dati/scadenze-token.md`. Verificato: workflow `test-auth-claude.yml` (trigger manuale) run #3
  verde — Claude si autentica in cloud. Attenzione all'a-capo quando si incolla il token nel segreto.

- [06 — Il consumo regge? E quindi che forma prende la catena?](issues/06-consumo-sostenibile.md) —
  **Regge, perché quel consumo c'è già oggi**: le corse programmate sul Mac pescano dallo stesso
  abbonamento, spostarle in cloud non aggiunge nulla. Misurati i 71 transcript (14/07–06/09): la
  sera **senza** grafica pesa $0,5–3, quella **con** grafica $5–33 (e la grafica resta sul Mac); il
  giro settimanale completo $40,85. 🔴 **Il serbatoio si è già svuotato 9 volte in 2 mesi** e 3
  volte ha ucciso una catena programmata (21/08 e 24/08 in testa) — il rischio del ticket 02 è
  passato. Chi lo svuota è **Michele al 77%**, non la catena. **Forma decisa:** quotidiana =
  guardie-script prima, agente solo se una grida · settimanale = 4 tappe con `commit` fra l'una e
  l'altra · **sveglie di notte** (lun 03:00 e 02:00; le 18:30 sono l'ora peggiore, il limite
  settimanale si azzera alle 18:00) · sul 429 riprova a +6h poi **un Telegram di una riga**.

- [11 — I 45 percorsi assoluti che il cloud non trova](issues/11-percorsi-assoluti.md) —
  **Tolti tutti.** 45 percorsi `/Users/michele/...` da **16 file** (6 skill, 7 agenti, 3 script).
  Regola per caso d'uso: i `cd` dei blocchi bash → `cd "$(git rev-parse --show-toplevel)"` (git
  trova la radice del repo da ovunque, anche in un clone rinominato); le letture-token inline →
  risolte via lo stesso comando; la prosa «## Base del progetto» → una **descrizione** («la radice
  del repo, sul Mac ~/…, in Actions il checkout») invece di un percorso; gli script → path da
  `__file__` / `~`. `controllo-integrita.py` aveva **già** la radice relativa: gli ho solo tolto il
  prefisso assoluto opzionale dalla regex. Verificato: grep pulito · guardia integrità verde sul Mac
  (129/129) · in un clone rinominato tutto gira e non resta nessun assoluto. Commit `6735f8f`.
  Restano fuori (fuori dal grep del ticket) i task-appunti in `.claude/task-pianificati/` — ma
  questa mappa spegne quei task (ticket 10) — e un esempio in `telegram-listener.py`, non tracciato.

- [13 — La guardia di freschezza: nessun anello lavora su dati morti](issues/13-guardia-freschezza.md) —
  **Fatta.** `scripts/controllo-freschezza.py verifica|testi` legge la data **dal nome** del file
  più recente (mai l'mtime: un `git clone` in cloud lo azzera e la guardia non scatterebbe mai —
  provato) e ferma l'anello se è vecchio: `eventi` = stesso giorno, `verificato` = max 2 giorni.
  Su stop manda un Telegram di una riga (file + data + giorni), stesso helper di
  `avviso-imminenti.py`. Step 1 di `smh-verifica` e `smh-testi` ora la invocano e si fermano senza
  bozze su exit 1/2. Verificato con file veri (exit 0 / 1 / 2, mtime azzerati) **e con l'invio
  Telegram reale** (Michele l'ha lanciata: messaggio arrivato via ripiego su `curl`). Credenziali:
  env var `TELEGRAM_*` in Actions, `.claude/secrets/telegram.json` sul Mac. Commit `9bd1f64` + 2.

- [12 — Accorgersi che il token è scaduto PRIMA che la catena si fermi](issues/12-avviso-scadenza-token.md) —
  **Fatto.** `scripts/controllo-scadenze-token.py` legge `dati/scadenze-token.json` (lista-macchina
  delle scadenze: oggi solo `CLAUDE_CODE_OAUTH_TOKEN` → 06/09/2027, soglia 21 giorni), calcola i
  giorni in Python e manda un Telegram azionabile («⚠️ in scadenza» / «🔴 già scaduto», con come
  rigenerare). Gira come passo `continue-on-error` del workflow *Metriche settimanali* (ogni lunedì),
  che aveva già i segreti Telegram. Stessa forma del promemoria token IG in `metrics.py`, ma script
  a parte perché quello si ferma se manca `INSTAGRAM_TOKEN`. Provato forzando la data (17 gg / soglia
  esatta / scaduto). Commit `dd47ba5`. Resta da confermare l'invio Telegram dal vivo (10 s Michele) e,
  vedi sotto, il PAT di cron-job.org.

- [07 — Mandare i pulsanti su Telegram senza dare il token all'agente](issues/07-telegram-senza-token.md) —
  **Fatto e provato in cloud.** `telegram-giro.py` si spezza in `prepara` (nessuna chiave:
  costruisce testo, blocchi da 3 e pulsanti, e scrive la busta `queue/telegram-da-inviare.json`)
  e `invia` (l'unico passo col token). Quattro decisioni di Michele: i pulsanti li disegna lo
  **script**, non l'agente · **una strada sola**, Mac e cloud · **la busta che resta è
  l'allarme** (si cancella solo dopo la conferma di Telegram) · invio a metà = **mappa salvata
  comunque** + avviso «lista incompleta». `invia` **rifiuta una busta malfatta** (callback del
  giro giusto, solo approve/reject, ✅/❌, evento in busta): è il muro che regge la prima
  decisione. Due punti del ticket erano **stantii**: il `giro_id` c'è dal 10/08 e il modello
  «passo stupido col token» era già provato dalla sonda. Nuove guardie:
  `controllo-token-agente.py` (rosso se un passo che lancia `claude` ha in mano una chiave,
  **anche ereditata dall'env del job**) agganciata a `guardia-integrita.yml`, e
  `controllo-busta-rimasta.py` (i pulsanti non sono mai partiti). Prova dal vivo: run
  [#34155483208](https://github.com/michidrop80-Rebelde/sanmarinohappens/actions/runs/34155483208)
  verde, messaggio 🧪 PROVA coi pulsanti veri sul telefono di Michele, suo ✅ tornato in
  `queue/approvazioni.md` — **l'agente non ha mai visto il token**. 🔴 La corsa ha scoperto un
  difetto vero (passo di commit verde che non committava la mappa del giro): corretto e provato.
  Commit `978efbd` + `e53d7dd`.

- [14 — Le sveglie di GitHub slittano di ore](issues/14-sveglie-che-slittano.md) —
  **La sveglia la suona cron-job.org, su tutte e due le corse.** Il danno non era «alle 07:47
  Michele è sveglio»: l'abbonamento lavora a **finestre di 5 ore**, e partendo alle 07:47 la
  finestra si chiude alle **12:47** — cioè l'orario notturno del ticket 06 viene annullato in pieno.
  Numeri del progetto: cron-job.org parte alle 07:01/18:01, i cron interni alle 08:03/12:26/21:56.
  Anche la **ripresa** va puntuale, ed è quella che rischia di più (slittata apre una finestra
  13:00–18:00). I cron interni **restano** come rete di sicurezza. Costruito: input `ripresa` nel
  `workflow_dispatch`; corretto un difetto scoperto strada facendo (il giro riconosceva la ripresa
  dal *testo del cron*, quindi via dispatch avrebbe scritto «riprovo alle 09:00» **alle 09:00**);
  **nuova guardia** contro il guasto muto — se la corsa parte da `schedule` il referto dice che
  cron-job.org non ha chiamato. 👉 I due cronjob li crea Michele:
  [`dati/guida-sveglia-giro-cloud.md`](../../dati/guida-sveglia-giro-cloud.md). Prova vera lunedì
  14/09 (stessa data del ticket 08).

## Ticket aperti

| | ticket |
|---|---|
| 🟢 frontiera | **08** il giro del lunedì gira in cloud — *la macchina funziona (corsa #2, 08/09), aspetta il confronto vero di lunedì 14/09* · **14** sveglie: *deciso e costruito 08/09, aspetta i 2 cronjob di Michele e la prova di lunedì 14/09* |
| 🔴 bloccati | **09** cloud e Mac insieme (aspetta 08) → **10** catena quotidiana + spegnere i task locali (aspetta 08, 09) |

## Non ancora specificato

- **Aggiornare Node 20 → 24 in tutti i workflow del repo.** La sonda ha fatto emergere l'avviso di
  deprecazione su `actions/checkout@v3` e `actions/setup-python@v4`: riguarda anche publish, metrics,
  guardia-imminenti. Manutenzione trasversale, non blocca la catena in cloud — da fare in un colpo.

- **Dove rientrano i pezzi lasciati fuori dal giro in cloud.** Il workflow del ticket 08 fa i
  quattro anelli e basta: restano fuori lo Step 5 (`/smh-sito`, il calendario pubblico), la guardia
  export→coda e quella di copertura. Non è una dimenticanza — il rimedio di quelle due guardie è
  **pubblicare**, e pubblicare è affare di `main`, non del ramo di prova su cui gira il secondo
  parere. Quando il cloud diventa titolare (ticket 10) devono rientrare da qualche parte, e va
  deciso dove: nel giro settimanale, nella catena quotidiana, o in un terzo posto.

- **Il passaggio di consegne cloud → Mac per la grafica.** Il cloud arriva a «pronte 3 grafiche» e si
  ferma. In che forma arriva a Michele quella lista, e come fa lui a ripartire da lì senza rileggersi
  tutto. Si potrà specificare quando la catena quotidiana esiste davvero.
- **Se il backup del cervello va automatizzato.** Oggi è un comando a mano e si era fermato 24 giorni.
  Il ticket 01 ha confermato che il cervello **resta un backup** (non diventa il canale di lavoro),
  quindi la domanda sopravvive tale e quale: un backup a mano si dimentica. Da riguardare quando la
  catena quotidiana in cloud esiste — a quel punto il repo pubblico si riempie da solo ogni notte e
  il rischio si sposta su cosa il backup **non** copre.

- **Le altre scadenze da mettere nella guardia del ticket 12.** Il meccanismo
  (`dati/scadenze-token.json` + `controllo-scadenze-token.py`) è generico: manca solo aggiungere le
  righe. Due candidati noti: (a) il **PAT fine-grained di cron-job.org** — ⬆️ **il ticket 14 ha
  alzato la posta**: adesso quel PAT non regge più solo i trigger 7:00/18:00 della pubblicazione,
  regge **anche la sveglia del giro in cloud**, e se scade in silenzio cadono tutte e due insieme
  (restano i cron interni, in ritardo di ore). La riga è pronta da scrivere: manca **solo la data**,
  che Michele legge su GitHub (passo 3 di `dati/guida-sveglia-giro-cloud.md`) — non si inventa;
  (b) l'`INSTAGRAM_TOKEN`, oggi seguito solo da `metrics.py`. Da fare appena Michele riporta le date.
  Quando esiste la catena quotidiana in cloud, chiamare la guardia anche lì, non solo il lunedì.

- **L'accumulo dei file di catena.** Il giro quotidiano aggiungerà ~1.000 file l'anno (6 MB circa).
  Deciso nel ticket 01 di **non archiviare nulla adesso**: sarebbe un pezzo in più che può spostare
  il file sbagliato e far diventare «il più recente» quello sbagliato. Si riguarda quando dà noia
  davvero — oggi è un problema che non abbiamo.

## Fuori scopo

- **La grafica Canva in cloud.** È la fase 2, decisa esplicitamente fuori da questa mappa. Il nodo è
  l'OAuth Canva agganciato all'utente su questo Mac; esiste una via (API Connect server-to-server con
  refresh token) ma va costruita e autorizzata a mano una volta. Si riapre come mappa nuova.
- **Bot Telegram pubblico H24 e server proprio** (Oracle Always Free). Stessa infrastruttura, altro
  obiettivo: non serve per staccare la catena.
- **La rotazione dei token già in debito** (`project_sicurezza_token_in_chiaro`). Resta aperta ma è
  un debito preesistente, non un passo di questa strada.
