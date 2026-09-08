# 09 — Cosa succede se Michele lavora sul Mac mentre gira il cloud

Type: grilling
Status: aperto — FRONTIERA (sbloccato l'08/09/2026, vedi sotto)
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
