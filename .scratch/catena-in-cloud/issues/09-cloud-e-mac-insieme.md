# 09 — Cosa succede se Michele lavora sul Mac mentre gira il cloud

Type: grilling
Status: resolved — 09/09/2026
Blocked by: —
Modello: Opus — ragionamento sui casi limite, e' fatto di 'cosa succede se'
Sforzo: media (una sessione)

## Il «Blocked by: 08» era sbagliato — tolto l'08/09/2026

Messo mentre si disegnava la mappa, sull'idea ragionevole che convenisse sapere se il cloud funziona
prima di scrivere le regole su come convive col Mac. Ma la domanda di questo ticket — **il lucchetto
è un file locale e non vede l'altra macchina** — è decidibile oggi: non cambia risposta a seconda di
come va il confronto di lunedì.

⚠️ Una cosa lunedì 14/09 la aggiunge davvero, ed è utile: sarà il primo giorno in cui il Mac fa un
`git pull` e si trova davanti il lavoro del cloud **mentre ha modifiche locali non salvate** (ce ne
sono sempre: `master.md`, `piano-editoriale.md`, il report). È il secondo punto dell'elenco qui
sotto, e lunedì si vede dal vivo invece che a mente. Gli altri tre punti non aspettano niente.

📌 Quello che lunedì **non** darà: una vera collisione. Il giro in cloud parte alle 03:00 e il task
del Mac alle 08:05, e scrivono su due rami diversi — non si incontrano. Chi si aspetta che lunedì
«si veda cosa succede se si scontrano» resterà a mani vuote: lo scontro oggi è tolto di mezzo per
costruzione, ed è esattamente per questo che la regola va decisa a tavolino.

## Domanda

Il lucchetto anti-doppione (`scripts/lucchetto.py`) è un **file locale** ed è pure escluso dal repo:
non vede l'altra macchina. Finché la catena girava solo sul Mac andava bene. Ora no.

Da sciogliere:
- Michele apre l'app mentre in cloud sta girando un giro: chi vince? cosa si rompe?
- Il `git pull` automatico all'apertura: dove si mette, e cosa fa se trova modifiche locali non
  salvate (oggi ce ne sono sempre — `master.md`, `piano-editoriale.md`, il report)
- Il caso brutto: il cloud ha scritto una bozza, Michele ne ha scritta un'altra sullo stesso file.
  Chi decide? Si può evitare del tutto invece di risolverlo dopo?
- Serve un lucchetto che le due macchine **condividono** (un file nel repo?), o basta togliere di
  mezzo la sovrapposizione?

**Cosa deve produrre la risposta:** la regola, e il pezzo che la fa rispettare da solo. Non un
«ricordati di non…»: Michele non deve doverselo ricordare.


## Answer

### La regola

**Non serve nessun lucchetto condiviso.** La domanda del ticket dava per scontata una
gara fra le due macchine; la gara non c'è, e Michele l'ha visto subito («ma se diventerà
il titolare l'altro sarà spento, no?»). Mezzo giusto: il ticket 10 spegne le **sveglie**
del Mac, non il Mac — `/smh-grafica` continua a scrivere nel repo e a spingerci dentro le
buste. Ma cloud e Mac fanno **lavori diversi, a ore diverse, su file diversi**: il cloud i
quattro anelli di testo di notte, il Mac la grafica di giorno.

Controllato file per file: su decine di file toccati dalla catena, quelli che **entrambi**
possono cambiare sono **due** — `dati/piano-editoriale.md` (ci scrivono `smh-approvazione`
in cloud e `smh-pubblica` sul Mac) e `dati/handle-organizzatori.json` (`smh-verifica` in
cloud, `smh-check`/`smh-pubblica` sul Mac). Tutto il resto è a corsie separate, o sono file
nuovi con la data nel nome, che non si scontrano per costruzione. Un lucchetto condiviso
sarebbe un pezzo nuovo — con un TTL, e col caso «resta chiuso e blocca tutto» — costruito
per un problema che non abbiamo.

**Il pericolo vero era un altro, ed era invisibile:** non che le macchine si scontrino, ma
che il Mac lavori su **dati vecchi in silenzio**. Il cloud stanotte scrive le bozze; Michele
domattina apre `/smh-grafica` e grafica la lista di tre giorni fa. Nessun errore, nessun
rosso — solo una grafica sbagliata pubblicata all'ora giusta.

Trovati due buchi: `/smh-grafica` e `/smh-giro` **non si allineavano affatto**, e le altre
tre (`smh-catena`, `smh-postino`, `smh-approvazione`) facevano un `git pull --rebase` secco
— che sul Mac **si rifiuta di partire**, perché l'albero è sempre sporco (ora ci sono 4 file
non salvati; ce ne sono sempre).

### Il pezzo che la fa rispettare da sola

**`scripts/allineati.py`** — il passo di allineamento, chiamato come primo comando dalle
**6 skill d'ingresso** del Mac (`smh-giro`, `smh-catena`, `smh-grafica`, `smh-pubblica`,
`smh-postino`, `smh-approvazione`). Mette da parte il non salvato, prende il lavoro del
cloud, lo rimette a posto. Nel caso normale non se ne accorge nessuno.

Scelta di Michele sul caso raro (stesso file cambiato da tutti e due): **si ferma e lo dice**,
senza mai chiedergli di sbrogliare git. Perciò usa `stash apply` e **non** `pop`: `pop`
cancella la copia appena riesce, e su conflitto lascerebbe i segnaposto nei file con la copia
già persa di vista. Con `apply` la copia resta nella cassaforte finché non è andato tutto bene
— nel caso brutto il lavoro di Michele è ancora lì, intero, e il messaggio nomina i file e dà
il comando per riprenderlo. I nomi si leggono **prima** di ripulire l'albero: dopo, l'albero è
immacolato e non direbbe più quali erano (difetto trovato dal test `[4]` e corretto).

Si ferma anche in altri due casi: **ramo sbagliato**, e **GitHub irraggiungibile** — lì
lavorare vorrebbe dire rischiare la lista vecchia senza poterlo sapere. In GitHub Actions non
fa nulla: il checkout è già fresco.

**`scripts/controllo-allineamento.py`** — la guardia contro la regressione, perché una regola
che vive solo dentro una skill sparisce alla prossima riscrittura (è già successo in questo
progetto: la regola dei 60 giorni della grafica). Diventa rossa se una delle 6 skill perde il
passo, **o se un altro comando lo precede**. Il primo metro che avevo scritto contava le righe
(«dev'essere nel primo quinto del file»): sbagliato — queste skill hanno pagine di regole prima
di cominciare, e la guardia dava 4 falsi rossi. Il metro buono è l'**ordine dei comandi**: nessun
blocco `bash` prima dell'allineamento. Ammessi solo il `cd` e la presa del **lucchetto** — quello
è stato di *questa* macchina, tenuto fuori dal repo apposta, e va preso **prima**, altrimenti due
giri del Mac si allineano insieme. Agganciata a `guardia-integrita.yml`, gira a ogni push.

### Verificato

- `scripts/allineati_test.py`: **18 prove verdi** su un finto GitHub costruito apposta (un repo
  nudo + due cloni, uno «cloud» e uno «Mac»). Coperti tutti e sette gli scenari: già in pari ·
  in pari ma sporco · **il caso di ogni giorno** (cloud ha lavorato, Mac sporco su altri file) ·
  **il caso brutto** (stesso file: si ferma, nomina il file, niente segnaposto di conflitto, il
  lavoro è nella cassaforte, e il comando suggerito lo riporta indietro davvero) · ramo sbagliato ·
  GitHub irraggiungibile · in cloud non fa nulla.
- La guardia **morde**: tolto a mano l'allineamento da `smh-grafica`, esce 1 e dice quale. Rimesso,
  torna verde su tutte e 6.
- Guardia di integrità verde (137 riferimenti), `lucchetto` 20/20, `token-agente` 12/12,
  `publish` 71/71, `conta_giro` 13/13, `confronta_giri` 25/25.
- Commit `243772e`.

### Cosa passa al ticket 10

Quando il cloud diventerà titolare e scriverà su `main` (oggi scrive sul ramo usa-e-getta
`giro-cloud`), l'altra metà della regola tocca a lui: **il job in cloud deve fare
`git pull --rebase` prima del push su `main`**, perché nel frattempo il Mac può aver spinto
una busta. Git rifiuta il push e basta — non si perde niente — ma il giro morirebbe all'ultimo
passo dopo aver fatto tutto il lavoro.

### Due prove che restano fuori dalla portata di qui

`metrics_test.py` non parte (manca `requests` sul Mac) e `segnala_doppioni_test.py` è **stantio**
(chiama `analizza`, una funzione che nel modulo non esiste più). Nessuna delle due è toccata da
questo ticket, ed erano già rotte prima: annotate, non nascoste.
