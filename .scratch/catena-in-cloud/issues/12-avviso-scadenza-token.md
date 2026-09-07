# 12 — Accorgersi che il token è scaduto PRIMA che la catena si fermi

Type: task
Status: aperto
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
