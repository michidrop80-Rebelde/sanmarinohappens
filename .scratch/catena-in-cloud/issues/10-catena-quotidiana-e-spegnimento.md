# 10 — La catena quotidiana in cloud, e si spengono i task sul Mac

Type: task
Status: aperto
Blocked by: 06, 08, 09, 15
Modello: Sonnet per costruire · Opus per la decisione di spegnere i task
Sforzo: lunga — costruzione + una settimana di osservazione prima di dire fatto

## Domanda

⚠️ **Aggiunto il ticket 15 fra i bloccanti (08/09/2026).** Michele ha chiesto un passo intermedio:
prima di rendere il cloud titolare, farlo girare per qualche settimana **accanto** al Mac come
secondo parere, senza grafica e senza mettere in coda. Questo ticket quindi non costruisce più da
zero — **promuove** quello che il 15 ha già fatto girare, e lo fa con delle prove in mano invece che
con la fiducia. Lo spegnimento dei task sul Mac resta il suo cuore.

L'ultimo passo: il workflow quotidiano che sostituisce `smh-catena` delle 18:30 — legge le
approvazioni arrivate, aggiorna i file, lancia le 6 guardie, manda il referto.

**Si ferma prima della grafica e lo dice.** Quando serve una grafica, il cloud non simula, non salta
e non finge: scrive «pronte 3 grafiche, servi tu» e passa la lista. La grafica resta sul Mac
(scelta, non ripiego).

Poi lo spegnimento: **spegnere `smh-giro-settimanale` e `smh-catena` sul Mac.** Non si lasciano
accesi come rete di sicurezza — due catene che girano insieme fanno danni, non sicurezza.
⚠️ Cambiare orario e stato insieme fa ripartire un task pianificato **subito**: due chiamate
separate, e verificare con `ps` che sia davvero spento.

**Fatto quando:** per una settimana intera Michele non ha aperto l'app per far girare la catena, e
la coda si è riempita lo stesso.

Alla chiusura di questo ticket la mappa è arrivata a destinazione: si rilegge la sezione «Non ancora
specificato» e si vede cosa è maturato.

## Capitolato dal ticket 06 (deciso 07/09/2026 — non si riapre)

- **Prima gli script, l'agente solo se serve.** Il workflow lancia le 6 guardie (Python puro, costo
  zero) e legge la coda approvazioni; **se tutte tacciono finisce lì e non sveglia nessun agente**.
  Claude si accende solo se una guardia grida o ci sono approvazioni da elaborare. Misura: 13 sere
  su 27 non avevano niente da fare e costavano ~$1 l'una solo per scoprirlo.
- **Sveglia: 02:00.** Stesso motivo del ticket 08 (non contendere il serbatoio a Michele); mai alle
  18:30.
- **Sul 429: riprova a +6h, poi un Telegram di una riga.** Un silenzio non è un esito.
- **Peso atteso:** $0,5–3 a sera. Le sere care ($5–33) erano quelle con la grafica, che **resta sul
  Mac** — quindi non entrano in questo workflow.
- ⚠️ **Rovescio accettato:** in cloud nessuno ferma a mano una corsa che va male. Il freno è il
  cancello degli script + le tappe con salvataggio, non la sorveglianza.

## Capitolato dal ticket 07 (07/09/2026)

Fra le guardie-script che girano PRIMA di svegliare qualsiasi agente vanno chiamate anche:
- `scripts/controllo-busta-rimasta.py` — i pulsanti dell'ultimo giro sono partiti davvero?
  Se la busta è ancora lì, Michele non ha mai ricevuto niente da approvare e la catena
  aspetta a vuoto.
- `scripts/controllo-token-agente.py` — nessun passo che lancia `claude` ha in mano una
  chiave. Costa zero (legge solo i file dei workflow) e non ha bisogno di segreti.
