# 01 — Dove vive il cervello che il cloud deve leggere?

Type: grilling
Status: resolved
Blocked by: —
Modello: Opus — decisione strutturale con conseguenze difficili da annullare
Sforzo: media (una sessione) — discussione + verifica di cosa contiene ogni cartella

## Domanda

Un agente in cloud clona il **repo pubblico**. Ma la memoria di lavoro della catena quasi non c'è
dentro — misurato il 06/09/2026:

| cartella | sul Mac | nel repo pubblico |
|---|---|---|
| `dati/eventi` | 12 | **2** |
| `dati/eventi/verificati` | 12 | **1** |
| `dati/post` | 25 | **8** |
| `dati/post/approvati` | 14 | **4** |
| `dati/telegram/pending` | 6 | **1** |
| `queue` | 4 | 4 ✅ |

Il resto vive solo sul Mac e nel repo **privato** `sanmarinohappens-cervello`.

**Perché è grave:** l'agente verifica legge «l'ultimo file di eventi», quello testi «l'ultimo
verificato». In cloud pescherebbero file di mesi fa e lavorerebbero su dati morti **senza
accorgersene** — nessuna guardia oggi intercetta questo caso. È lo stesso danno della copia
congelata di luglio, in forma nuova.

**Da decidere: dove vive la verità che il cloud legge e scrive.**

- **(a) Tutto nel repo pubblico.** Gli eventi sono dati pubblici per natura (è un aggregatore di
  eventi). Semplice: un repo solo, nessuna chiave in più. Ma: le bozze, i dubbi e le note interne
  diventano pubbliche, e i log delle run pure.
- **(b) Il cloud legge/scrive il repo privato «cervello».** Con una chiave di distribuzione dedicata.
  Niente diventa pubblico. Ma: due repo da tenere in sincrono, una chiave in più da gestire e ruotare,
  e il cervello oggi è un repo «di salvataggio» (fotografie periodiche), non un repo di lavoro — va
  capito se regge quel ruolo.
- **(c) Ibrido.** Nel pubblico ciò che serve alla pubblicazione, nel privato il resto.

**Cosa deve produrre la risposta:** la scelta, il perché, e l'elenco preciso di quali cartelle
vanno dove. Più la risposta alla domanda che ne discende: **come fa il cloud a sapere che sta
guardando l'ultimo file e non uno vecchio?** (una guardia di freschezza, oggi inesistente).

⚠️ Prima di committare qualsiasi cosa nel repo pubblico: **verificare che non contenga segreti o
dati personali**. `dati/handle-organizzatori.json` e i file `dati/telegram/pending/*.json` vanno
guardati uno per uno.

Questo ticket è il perno della mappa: quasi tutto il resto dipende da come finisce.

## Answer

**Deciso il 07/09/2026 con Michele. Scelta: (a) tutto nel repo pubblico.**

### Tre fatti trovati che hanno riscritto la domanda

1. **Quei file non erano esclusi: non erano mai stati committati.** Nessuna regola nel `.gitignore`
   tiene fuori `dati/eventi`, `dati/post`, i verificati o gli approvati — sono rimasti `??` per
   mesi. Non c'era una decisione di riservatezza da rispettare, c'era una dimenticanza. **61 file,
   1,4 MB in tutto.**
2. **Una parte è già pubblica oggi** e non è successo niente: 8 bozze post, 4 approvati, 2 eventi,
   2 pending e **tutta `queue/`** sono nel repo pubblico da mesi.
3. **Cercati i segreti in tutti e 61 i file: nei dati di lavoro non ce n'è nessuno.** Eventi,
   verificati, post, approvati, pending, queue: puliti. I `pending/*.json` hanno solo `giro_id`,
   `sent_at`, `eventi` — nessun `chat_id`, nessun token. `handle-organizzatori.json` sono handle
   Instagram pubblici.
4. **Il «cervello» non è un album di fotografie** (l'ipotesi del ticket era pessimista): è un repo
   git vero, storia completa, che lavora **sugli stessi file al loro posto** con un `.git` separato
   in `~/.smh-cervello.git`. Tecnicamente reggerebbe il ruolo di repo di lavoro.

### Perché non la (b), visto che reggerebbe

Il costo della (b) non è «una chiave in più». Pubblico e cervello **condividono la stessa cartella
di lavoro** e si dividono per percorso (`posts/ marketing/ queue/ scripts/` da una parte,
`dati/ .claude/skills/ references/ .scratch/` dall'altra). In cloud vuol dire **due repo clonati
nella stessa directory, due `.git`, due commit e due push per ogni giro** — con il caso in cui uno
riesce e l'altro no e i due repo raccontano storie diverse a metà catena. Più una deploy key da
gestire e ruotare. Tutto questo per proteggere dati che sono **bozze di cose che escono su
Instagram fra tre giorni**. La (c) è la (b) più l'obbligo di decidere, per ogni cartella nuova che
nasce, da che parte sta.

### L'elenco preciso: cosa va nel repo pubblico

| cosa | file | nota |
|---|---|---|
| `dati/eventi/` | 10 | output della ricerca |
| `dati/eventi/verificati/` | 11 | output della verifica |
| `dati/post/` | 17 | bozze |
| `dati/post/approvati/` | 10 | pronti per la grafica |
| `dati/telegram/pending/` | 5 | verificati: nessun `chat_id`, nessun token |
| `dati/config.json` | 1 | già nel ticket 03 |
| `dati/fonti-sport.md` | 1 | **ripulito** — vedi sotto |
| `dati/metriche-social.md`, `dati/scadenze-token.md`, `dati/diario-giro-prova-2026-07-11.md`, `dati/prompt-sessione-6.md` | 4 | nessun segreto |
| `queue/` | già dentro | ✅ |

**Il cervello privato resta esattamente com'è: fa il backup, non il lavoro.** Non gli si cambia
ruolo, non lo tocca nessun agente in cloud.

### Cosa NON va nel pubblico (deciso, non dimenticato)

Tre file di documentazione contengono roba personale. Non sono dati di lavoro:

- 🚫 `dati/guida-anello6-facebook.md` — contiene **`michimorri@gmail.com`**, l'email personale di
  Michele. Al cloud non serve (guida di un setup già fatto). Resta solo nel cervello privato.
- 🚫 `dati/guida-anello6-tappa1-setup-account.md` — stessa natura, guida di setup già eseguito.
  Resta solo nel cervello privato.
- ⚠️ `dati/fonti-sport.md` — contiene la password **`RBA25`** di Sportity, app di cronometraggio
  di terzi. Questo file **serve alla catena** (senza, l'agente ricerca in cloud non sa dove
  guardare per lo sport) → si carica **ripulito**: la password sostituita con
  `password: chiedere a Michele`.

Scartata l'idea di caricare tutto così com'è: l'email personale nel repo pubblico è un regalo agli
spammer e resta nella storia di git anche se la togli dopo.

### La domanda che ne discendeva: come fa il cloud a sapere che sta guardando l'ultimo file?

**Oggi non lo sa, e la falla è reale.** Verificato nelle skill: `smh-verifica` prende «il file **più
recente** in `cartella_eventi`» (SKILL.md:48), `smh-testi` «il più recente in `cartella_verificati`»
(SKILL.md:30). **Nessuno dei due si chiede *quanto* è recente.** Se l'ultimo file di eventi è del
30 giugno, lo lavorano come se fosse di stamattina. Sul Mac te ne accorgi perché sei lì; in cloud
gira di notte e la mattina trovi bozze su eventi già passati, che poi passano approvazione e
grafica. È il danno della copia congelata di luglio in forma nuova.

**Deciso — comportamento:** la guardia **ferma l'anello** e manda un Telegram di una riga. Non
prosegue-e-segnala: un post sbagliato costa molto più di un giro saltato, perché una volta prodotto
attraversa approvazione e grafica e può uscire davvero.

**Deciso — soglie (strette):**
- file di **eventi** → deve essere **dello stesso giorno** del giro
- file **verificato** → al massimo **2 giorni**

In un giro quotidiano sano questa guardia non scatta mai: scatta solo quando qualcosa a monte si è
già rotto, che è esattamente il suo mestiere. Con soglie larghe (3/5 giorni) la falla resterebbe
socchiusa proprio nei casi che ci interessano.

→ La costruzione della guardia è il **ticket 13**.

### Accumulo dei file: nessuna pulizia

Il giro quotidiano aggiunge ~1.000 file l'anno, piccolissimi: 1,4 MB oggi, forse 6 MB fra un anno.
Git li digerisce senza accorgersene, e lo storico completo è ciò che ha salvato il progetto a
luglio. **Niente archiviazione automatica**: sarebbe un altro pezzo da costruire, da provare e che
può spostare il file sbagliato facendo diventare «il più recente» quello sbagliato. Annotato nel
fog, non aperto come ticket.
