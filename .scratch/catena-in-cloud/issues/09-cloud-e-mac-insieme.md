# 09 — Cosa succede se Michele lavora sul Mac mentre gira il cloud

Type: grilling
Status: aperto
Blocked by: 08
Modello: Opus — ragionamento sui casi limite, e' fatto di 'cosa succede se'
Sforzo: media (una sessione)

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
