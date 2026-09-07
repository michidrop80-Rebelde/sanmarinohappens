# 12 — Accorgersi che il token è scaduto PRIMA che la catena si fermi

Type: task
Status: resolved
Blocked by: 04
Modello: Sonnet — c'è già un esempio da imitare nel progetto
Sforzo: breve (mezza sessione)

## Domanda

Dalla ricerca del ticket 02: il token dell'abbonamento **dura un anno**, e alla scadenza le run
falliscono con `OAuth token has expired`. ❌ **Non esiste nessun avviso preventivo per la CI** —
l'avviso «scade fra 3 giorni» vale solo per il login interattivo sul Mac.

Tradotto: senza far niente, il primo segnale sarà **la catena che smette di girare**. E siccome
Michele non guarda le run, se ne accorgerebbe dai post che non escono — cioè troppo tardi.

**Da fare:** un avviso che arriva su Telegram *prima* della scadenza.

**C'è già un precedente da copiare nel progetto**: l'avviso di scadenza del token Instagram, in
`metriche/` (la data vive in `metriche/storico.json`). Stessa forma, stesso canale, stesso stile.

**Fatto quando:** la data di scadenza è registrata da qualche parte che non si perde, e c'è un
controllo automatico che manda un Telegram con un anticipo ragionevole. Verificato **forzando la
data**, non aspettando un anno.

## Answer

**Fatto.** Commit `dd47ba5`.

### Cosa c'è adesso
- **`dati/scadenze-token.json`** — la lista-macchina delle scadenze. Oggi una voce:
  `CLAUDE_CODE_OAUTH_TOKEN`, scade `2027-09-06`, soglia d'avviso `anticipo_giorni: 21`.
  Ogni voce porta con sé anche «se scade cosa succede» e «come si rigenera», così
  il Telegram è azionabile da solo.
- **`scripts/controllo-scadenze-token.py`** — legge il JSON, per ogni token calcola
  i giorni mancanti (`datetime.date`, mai a occhio) e:
  - `giorni > soglia` → stampa «a posto», exit 0;
  - `0 ≤ giorni ≤ soglia` → «⚠️ Token in scadenza …», Telegram, exit 1;
  - `giorni < 0` → «🔴 Token GIÀ SCADUTO …», Telegram, exit 1;
  - JSON mancante/rotto → exit 2.
  Flag `--prova` (non manda) e `--oggi AAAA-MM-GG` (forza la data). Telegram: stesso
  helper della guardia di freschezza (env var in Actions → `.claude/secrets/telegram.json`
  sul Mac → ripiego su `curl`).
- **`dati/scadenze-token.md`** resta la copia leggibile per gli umani, con in testa
  il rimando al JSON come fonte-macchina.

### Dove gira
Passo `Controllo scadenze token` (con `continue-on-error: true`) del workflow
`Metriche settimanali` (`.github/workflows/metrics.yml`), che parte **ogni lunedì**.
Con soglia 21 giorni l'avviso arriva ~3 lunedì di fila prima della scadenza. Non
ho creato un workflow nuovo apposta: le metriche giravano già lì ogni settimana,
con i segreti Telegram già passati.

### Perché non dentro `metrics.py` (che ha già `controlla_token` per IG)
`metrics.py` fa `return` subito se manca `INSTAGRAM_TOKEN`: se un giorno è quello
a rompersi, il controllo del token di Claude non partirebbe. Meglio uno script a
parte, che tra l'altro si prova da solo (come le altre guardie del progetto).

### Verifiche (output reale)
- oggi (2026-09-07) → «fra 364 giorni — a posto», **exit 0**.
- `--oggi 2027-08-20` (17 gg prima) → «⚠️ … fra 17 giorni», **exit 1**, messaggio con
  cosa succede + come rigenerare.
- `--oggi 2027-08-16` (esattamente 21 gg = soglia) → avviso, **exit 1**.
- `--oggi 2027-09-10` (scaduto da 4 gg) → «🔴 Token GIÀ SCADUTO», **exit 1**.
- `controllo-integrita.py` verde. `py_compile` OK. JSON valido.

### Invio Telegram reale — da confermare (10 s per Michele)
Non l'ho mandato io: sarebbe un messaggio d'allarme finto sul telefono di Michele,
e mandare messaggi per conto suo va chiesto. Il codice d'invio è identico a quello
già confermato dal vivo nel ticket 13. Conferma:

    python3 scripts/controllo-scadenze-token.py --oggi 2027-08-20

(deve arrivare un Telegram «⚠️ Token in scadenza: CLAUDE_CODE_OAUTH_TOKEN …».)

### Lasciato per dopo (non in questo ticket)
- Quando esiste la **catena quotidiana** in cloud (ticket 08/10), conviene chiamare
  questa guardia anche lì, non solo il lunedì.
- Il **PAT fine-grained di cron-job.org** (quello che fa `workflow_dispatch` alle
  7:00/18:00) è un altro token che scade e che, se muore, ferma i trigger puntuali.
  Non conosco la sua data di scadenza → va aggiunta al JSON quando Michele la
  recupera da GitHub (Settings → Developer settings → Personal access tokens).
