# Prova di Jev su eventi veri — 13/10/2026

Chiesta da Michele. È la prova del punto 2 di `PROGETTI/JEV.md`: prima di affidare a Jev un lavoro
ricorrente, lo si misura su casi veri di cui si sa già la risposta.

**Jev non è collegato al giro.** Questa è solo una misura: la catena di San Marino Happens gira
come prima. Collegarlo è una decisione a parte.

Costo di tutto: 53.193 token, **0,002 $**. Circa 10 secondi per 30 casi.

## Prova A — la categoria dell'evento: **24 su 30**

**Casi:** 30 eventi distinti sorteggiati (seme fisso) fra i 56 dei giri del 05/10 e del 12/10 con
una categoria «pulita» (una delle sei di `dati/config.json`). A Jev arrivano titolo, luogo e
descrizione. **Risposta giusta:** il campo `Tipo` scritto dalla ricerca.

**Domanda** (`domande.json`): una `choice` fra sport · cultura · musica · sociale · istituzionale ·
altro, ognuna con una riga di descrizione **scritta da me**: nel progetto le sei categorie non hanno
una definizione.

| | |
|---|---|
| coincide con la catena | **24 su 30** (80%) |
| con le voci in ordine rovesciato | 23 su 30 · la risposta resta la stessa in 27 casi su 30 |
| quando Jev è sicuro (fiducia ≥ 0,8) | 24 casi, **22 giusti** |

I 6 disaccordi, guardati uno per uno:

| Evento | Catena | Jev | Chi ha ragione |
|---|---|---|---|
| Sal Da Vinci, Teatro Nuovo («Esibizione musicale/teatrale») | musica | cultura | **la catena**: Jev non sa chi è, e la descrizione non lo dice |
| San Marino Beer Fest (due weekend) | musica | sociale | discutibile: festa della birra con concerti. Dipende da come si definisce «sociale» |
| AzzuChef («Evento culinario») | cultura | sociale | discutibile: nella mia descrizione il cibo sta in «sociale» |
| Convegno sulla prevenzione del rischio | istituzionale | cultura | discutibile: è un convegno (cultura) organizzato da un ente (istituzionale) |
| Corsi serali di lingua | istituzionale | altro (incerto: 0,51) | discutibile |

**Lettura:** un errore vero su 30 (manca la conoscenza di chi è l'artista). Gli altri cinque sono
casi di confine, dove la «risposta giusta» è una convenzione mai scritta. Per usarlo sulle
categorie servirebbe prima **scrivere cosa vuol dire ogni categoria**; e comunque qui il guadagno è
piccolo, perché la categoria la ricerca la scrive già mentre compila la scheda.

## Prova B — «è lo stesso evento?»: **30 su 30**

**Casi:** 30 coppie di eventi veri **dello stesso giorno**, presi da giri diversi (da luglio a
ottobre): 22 con la stessa pagina-fonte e 8 con fonti diverse. **Risposta giusta:** decisa a mano
da me leggendo le coppie, **prima** di chiedere a Jev (`chiave_coppie.json`): 12 «stesso evento»,
18 «eventi diversi». A Jev arrivano titolo, luogo e descrizione dei due eventi, **senza date e
orari** (quelli li confronta il codice).

**Domanda** (`domande_coppie.json`): un `noul`, «descrivono lo stesso evento reale, anche se scritto
in modo diverso?».

| | |
|---|---|
| giuste | **30 su 30** |
| «stesso evento» | Jev risponde da **0,60 a 0,92** |
| «eventi diversi» | Jev risponde da **0,01 a 0,07** |
| risposte incerte (fra 0,3 e 0,7) | 1: «⚠️ Calcio al Parco» contro «Calcio al Parco», 0,60 — comunque dal lato giusto |

Esempi riconosciuti come lo stesso evento: «Molella & Rosa Chemical» / «Summer Vibes 2026 — Molella
e Rosa Chemical in concerto»; «Festa di San Marino» / «Festa di San Marino e di Fondazione della
Repubblica»; «11º Concorso Internazionale di Canto Renata Tebaldi» / «11° Concorso Internazionale
Voci "Renata Tebaldi"». Riconosciuti come diversi anche due eventi nello stesso posto lo stesso
giorno («Alba sul Monte…in Concerto» e «Yoga agli Orti», Orti dell'Arciprete).

**Lettura:** qui Jev è netto, e le due nuvole di risposte non si toccano: una soglia a 0,3 le
separa tutte. **Limiti della prova:** quasi tutte le coppie «diverse» sono eventi molto diversi fra
loro; le coppie difficili (stessa serie in due date, stessa rassegna con artisti diversi) sono
poche. Le date non sono state messe alla prova apposta: Jev sui numeri sbaglia.

## Cosa se ne ricava

| Uso | Verdetto |
|---|---|
| trovare i doppioni fra gli eventi nuovi e il calendario (stesso giorno, scritti in modo diverso) | **promettente**: 30 su 30. Prima di affidarglielo, una seconda prova con più coppie difficili |
| assegnare la categoria | **non ancora**: 24 su 30, e prima vanno scritte le definizioni |

## Per rifarla

I file sono in questa cartella. Da una cartella qualunque:

```
python3 /Users/michele/.claude/bin/jev.py chiedi --domande domande.json --righe casi.jsonl --esce r1.jsonl
python3 /Users/michele/.claude/bin/jev.py chiedi --domande domande_coppie.json --righe coppie.jsonl --esce rc.jsonl
```
