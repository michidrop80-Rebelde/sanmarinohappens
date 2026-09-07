# 08 — Il giro del lunedì gira in cloud

Type: task
Status: aperto
Blocked by: 01, 03, 05, 07, 11
Modello: Opus — orchestrazione + confronto dei risultati fra due catene
Sforzo: lunga — il ticket piu' grosso della mappa, mettere in conto piu' di una sessione

## Domanda

Costruire il workflow settimanale che fa quello che oggi fa `smh-giro-settimanale` sul Mac:
ricerca → postino → verifica → testi, e finisce mandando a Michele le bozze coi pulsanti.

**La regola di questo ticket: il task sul Mac resta ACCESO.** Si fanno girare tutti e due e si
confrontano i risultati — stessi eventi trovati? stesse verifiche? stesse bozze? Finché non ci
fidiamo, il cloud è un secondo parere, non il titolare. (Attenzione ai doppioni: due catene che
scrivono lo stesso file di oggi si sovrascrivono — va gestito prima di lanciare, non dopo.)

**Fatto quando:** un lunedì il cloud ha prodotto un giro che regge il confronto con quello del Mac,
e Michele ha ricevuto un solo riepilogo sensato sul telefono.

## Capitolato dal ticket 06 (deciso 07/09/2026 — non si riapre)

- **4 tappe separate, con `commit` dopo ognuna:** ricerca → postino → verifica → testi. Motivo
  misurato: il giro del 24/08 è morto a metà corsa sul limite delle 5 ore (partito 06:24, morto
  11:06) e in cloud si sarebbe perso tutto il non committato. Se il serbatoio finisce alla terza
  tappa, le prime due restano salve.
- **Sveglia: lunedì 03:00.** Non per risparmiare token (sono gli stessi), ma per non contendere il
  serbatoio a Michele. ⚠️ Mai alle 18:30: il limite settimanale si azzera alle 18:00
  (Europe/San_Marino) ed è il momento di massima contesa.
- **Sul 429 (serbatoio vuoto): una riprova dopo 6 ore, poi un Telegram di una riga** che dice che
  la catena è ferma. Il 21/08 una corsa è morta sul 429 e nessuno se n'è accorto.
- **Peso atteso:** ~$40 di valore equivalente per un giro completo (misura del 24/08).

## Capitolato dal ticket 07 (deciso e provato 07/09/2026 — non si riapre)

- **Il riepilogo coi pulsanti si manda in DUE passi**, e il passo dell'agente non ha mai in
  mano `TELEGRAM_BOT_TOKEN`: `telegram-giro.py prepara` (l'agente) scrive la busta,
  `telegram-giro.py invia` (passo di shell separato, con la chiave) spedisce. Il blocco YAML
  già collaudato si copia da `.github/workflows/prova-pulsanti.yml`: lì cambia solo **cosa**
  l'agente mette in busta (eventi veri invece dei due finti).
- **La mappa del giro va committata** (`dati/telegram/pending/<giro>.json` +
  `ultimo-giro.txt`): senza, le risposte di Michele non sono riconducibili a nessun evento.
  ⚠️ Due `git add` separati e passo **rosso** se l'invio è riuscito ma non c'è niente da
  committare — la prima corsa del 07/09 era verde e non aveva committato niente.
- **Se la busta resta dopo `invia`, l'invio è fallito**: la corsa deve essere rossa, e la
  busta va lasciata dov'è (non si cancella per far tornare il verde).
