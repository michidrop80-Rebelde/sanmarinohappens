# 15 — La catena serale in cloud come SECONDO PARERE, senza grafica

Type: task
Status: aperto — bloccato
Blocked by: — (sbloccato il 09/09/2026: il ticket 09 è chiuso)
Modello: Sonnet per costruire (è il modello del giro settimanale applicato a un'altra skill) ·
         Opus solo per decidere cosa vuol dire «hanno lavorato uguale»
Sforzo: medio — una sessione per costruirlo, poi settimane di sola osservazione

## Domanda

Prima di rendere il cloud **titolare** della catena serale (ticket 10) e spegnere il task sul Mac,
farlo girare per qualche settimana **accanto** a quello del Mac, senza poter fare danni, e vedere se
lavora uguale. È lo stesso schema che ha funzionato per il giro settimanale (ticket 08), applicato
alla sera.

Fa **tutto tranne la grafica**. Idea di Michele, 08/09/2026.

## Perché non è un guscio vuoto

Tolta la grafica, della catena serale resta la metà che *ragiona*:

| step | cosa fa | va in cloud? |
|---|---|---|
| 0 · 0-bis | lucchetto, allineamento, controllo secco «c'è qualcosa da fare?» | sì |
| 1 | **approvazioni**: legge i ✅/❌ arrivati e aggiorna i file | sì |
| 2 | grafica Canva + messa in coda | ❌ resta sul Mac |
| 2-bis | buchi delle prossime 48h | solo la parte di **testo** (le bozze), non la grafica |
| 3 · 3-bis | segnalazioni del bot, annullamenti | sì |
| 4 | le sei guardie | sì (Python puro, costo zero) |
| 5 · 6 | referto Telegram, rilascio lucchetto | sì |

## Perché si può fare PRIMA che il ticket 09 sia risolto

Il nodo del 09 — il lucchetto è un file locale che non vede l'altra macchina — nasce solo quando due
catene **scrivono nello stesso posto**. Un secondo parere lavora su un **ramo suo** (come
`giro-cloud`) e **non mette niente in coda**: non tocca `posts/` e non tocca `main`. Lo scontro non
è gestito, è **tolto di mezzo**, esattamente come nel ticket 08.

⚠️ Michele ha comunque scelto (08/09/2026) di mettere questo ticket **dietro** al 09: prima si
scioglie il nodo più duro della mappa, che sblocca tutto il resto. Quindi il «Blocked by: 09» è una
scelta di ordine, non un vincolo tecnico — se un giorno servisse invertirli, si può.

## Da decidere quando si apre

1. **Cosa vuol dire «hanno lavorato uguale».** Per il giro settimanale la risposta era un `git diff`
   fra i due rami (`scripts/confronta-giri.py`). Qui l'output è diverso: file di bozze aggiornati,
   stati cambiati da `da-approvare` a `approvato`, esiti delle guardie. Serve il metro prima della
   corsa — ⚠️ e con la lezione del 08/09 in testa: **un metro sbagliato assolve o accusa a
   sproposito**, e non deve poter contare come proprio il lavoro fatto dall'altro.
2. **Il rumore su Telegram.** Due referti a sera. Come per il settimanale: quello del cloud arriva
   **senza pulsanti** e marcato, così non c'è mai dubbio su quale mazzo di ✅/❌ vale.
3. **Quante sere di osservazione bastano** prima di dire «si fida». Il settimanale ne ha 2; qui le
   corse sono quotidiane, quindi le prove arrivano molto più in fretta.
4. **Quanto costa davvero.** Atteso $0,5–3 a sera (ticket 06), e su 27 sere misurate **13 non
   avevano niente da fare** → con il disegno già deciso (prima le guardie-script, l'agente si sveglia
   solo se una grida) quelle sere costano **zero**. Da verificare sul campo, non da dare per buono.

## Fatto quando

Per N sere di fila il cloud e il Mac hanno prodotto lo stesso risultato (misurato, non a occhio), e
le differenze rimaste sono spiegate una per una. A quel punto il ticket 10 può promuoverlo a
titolare con delle prove in mano invece che con la fiducia.
