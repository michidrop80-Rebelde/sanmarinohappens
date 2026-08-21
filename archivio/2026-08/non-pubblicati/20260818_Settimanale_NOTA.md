# 20260818_Settimanale — mai pubblicata, archiviata a mano il 21/08/2026

⚠️ **Questa cartella non è la prova di una pubblicazione.** È l'archivio dei
"non-pubblicati": questa busta non è mai uscita né su Instagram né su Facebook
(verificato su `published.log`, nessuna riga `20260818_Settimanale*`).

## Cosa è successo
- Busta creata il 18/08/2026 (recupero dello slot saltato di domenica 16/08),
  `data_pubblicazione: 2026-08-18`, `tipo: carosello` (usato come trasporto
  multi-immagine per un settimanale a 2 pagine).
- Il workflow GitHub Actions ha girato regolarmente ogni giorno dal 18/08 al
  21/08 (tutte le run concluse `success`), ma questa busta non risulta MAI
  tentata/pubblicata: non compare in `published.log`.
- **Perché non è stata segnalata come "scaduta e mai uscita" e auto-archiviata
  da `publish.py`**: la funzione `separa_scarti_definitivi()` esclude sempre
  gli AGGREGATI (`settimanale`/`weekend`/`carosello`) dall'auto-scarto — per
  loro il ritardo è considerato "sanabile a mano" (si ridatano ed escono lo
  stesso). Quindi restava in coda a **suonare per sempre** a ogni run, in
  attesa di una decisione umana. Non è un bug del robot: è il comportamento
  voluto, la decisione mancava.

## Perché si archivia ora invece di ridatarla
Il contenuto copriva "18–23 agosto". Oggi è il 21/08, quindi:
- I giorni 18-20/08 (Cinema nei Castelli lun-mer, Trio Mi Alma, Balamondo)
  sono **già passati** — non hanno più senso in un post che parla di "questa
  settimana".
- I giorni **ancora validi (21-23/08)** — Trenino Bianco Azzurro, Sagra
  dell'Uva, Festa dell'Amicizia, Visita Papa Leone XIV (22/08), Alba sul Monte
  (23/08) — sono **già coperti** dalla busta `20260820_Weekend`, che è uscita
  regolarmente (`published.log`: `20260820_Weekend|ig`, `20260820_Weekend|fb`).

Ripubblicarla ora sarebbe quindi un **doppione** del weekend già uscito, con in
più contenuti stantii (i primi 3 giorni). Per questo si archivia come
non-pubblicata invece di ridatarla: il buco di copertura che avrebbe dovuto
chiudere è già chiuso da un altro contenuto.

## Segnalato a Michele
Vedi il referto della catena del 21/08/2026 (Step 2-bis) — chiedere conferma
che l'archiviazione vada bene; i file originali restano qui, recuperabili.
