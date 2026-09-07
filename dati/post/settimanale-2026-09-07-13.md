# Settimanale 07/09–13/09/2026 — dossier per la grafica

**Slot di pubblicazione:** **domenica 06/09 ore 18:00** — slot regolare (copre la settimana
07/09–13/09). Scritto il 04/09/2026 dallo Step 2-bis della catena giornaliera (guardia
`scripts/controllo-imminenti.py` uscita con codice 2: buco «Settimanale del 06/09» dentro
le 48 ore).

**Master Canva:** `SMH - Settimanale Master` = **`DAHORdC0zdY`** — rotazione a pagine:
l'ultimo giro (31/08–06/09) aveva usato la pagina 3 (`ultima_pagina_usata` = 3 in
`dati/grafica-stato.json`), quindi questo giro tocca la **pagina 4**. Si lavora **su COPIA**,
titolata `🗑 DA ELIMINARE — SMH · Settimanale — 07-09_13-09`.
**8 eventi → 1 slide** (template a 8 righe: tutte le righe usate, nessuna cancellazione).

Giorni della settimana **calcolati in Python** il 04/09/2026:
`07/09 Lunedì · 08/09 Martedì · 09/09 Mercoledì · 10/09 Giovedì · 11/09 Venerdì · 12/09 Sabato · 13/09 Domenica`

Fonte di ogni riga: `dati/calendario/master.md` (righe 48, 60, 72, 80, 81, 84, 98, 99).
Nessun dato aggiunto che non sia già nel registro.

---

## Righe per il GRAFICO (giorno·data · titolo · luogo BREVE — niente ora, niente prezzi)

### Slide unica
| # | Giorno/data | Titolo | Luogo breve |
|---|---|---|---|
| 1 | Martedì 08/09 | Concerto Morricone | Orti Borghesi |
| 2 | Mercoledì 09/09 | Serravalle in Wellness | La Ciarulla |
| 3 | Venerdì 11/09 | BeerFest · Queen Tribute | Parco di Dogana |
| 4 | Ven-Dom 11-13/09 | GP MotoGP San Marino | Misano |
| 5 | Sabato 12/09 | Musikfest Adriatica | Centro Storico |
| 6 | Sabato 12/09 | BeerFest · Anni '90 | Parco di Dogana |
| 7 | Sab-Dom 12-13/09 | Dal Turista al Contadino | Città e Borgo |
| 8 | Domenica 13/09 | 36° Palio Don Bosco | Borgo Maggiore |

Titoli entro ~26 caratteri (tetto del box settimanale: font 40 ≈ 25 caratteri, vedi memoria
`reference_geometria_titoli_aggregati`). «BeerFest · Queen Tribute» / «BeerFest · Anni '90»:
due serate distinte dello stesso SanMarinoBeerFest, tenute su due righe perché sono due
appuntamenti diversi (11 e 12/09) e le 8 righe del template bastano. «GP MotoGP San Marino»:
il «°» / numeri edizione si evitano (`feedback_titoli_massimizza`).

---

## ⚠️ Righe da tenere d'occhio (segnalate, non nascoste)

**1) MotoGP (11–13/09) — corre a Misano, non in territorio.** Rientra comunque nel perimetro
della pagina: porta il nome della Repubblica, lo segue il pubblico sammarinese (regola
Michele, `CLAUDE.md`). Riga 48 del master, `approvato`. Ha già la sua busta feed in coda
(`20260911`, gara domenica 13/09 ore 14:00). Nell'aggregato compare comunque (ogni evento
sta in tutti i livelli a cui appartiene).

**2) SanMarinoBeerFest — luogo.** Le bozze vecchie (post-approvati-2026-08-17) dicevano
«Campo Bruno Reffi»: **superato**. Master righe 72 e 84, **corrette il 24/08/2026** sulla
locandina ufficiale (screenshot Facebook di Michele) → **Parco di Dogana, San Marino**. Sul
grafico e in caption vale il master. Nessun orario confermato per la serata Vipers dell'11/09
(la nota BeerFest «cucina dalle 20:00» è documentata solo per la serata del 12/09).

**3) Dal Turista al Contadino — II tappa (12–13/09) — due sedi.** Riga 60, luogo corretto il
24/08 su fonte diretta usc.sm: Via Eugippo (Città di San Marino) **e** Piazza Mercatale
(Borgo Maggiore). Sul grafico «Città e Borgo», in caption entrambe. Ora non specificata né
dalla fonte né da ricerca mirata → nessun orario, nessun placeholder.

**4) Serravalle in Wellness (09/09) — serie ricorrente, primo dei 4 mercoledì.** Riga 80,
`approvato`. Ha già la sua busta feed per il 09/09. Gli appuntamenti 16, 23, 30/09 NON hanno
post dedicato per decisione di Michele del 24/08 (coperti dal rimando in caption del post del
09/09). Nell'aggregato compare solo la data che cade in settimana (09/09).

**5) Musikfest Adriatica (12/09) — solo storia come post singolo, feed occupato dal BeerFest.**
Riga 99. Nell'aggregato compare comunque.

**6) Concerto Morricone (08/09) — prenotazione obbligatoria.** Riga 98. Ha già la sua busta
feed per l'08/09. In caption si segnala la prenotazione.

**7) Mostre da-approvare che toccano la settimana — NON incluse.** `M03`/`M04` (fino al
04/10), `M08` «Icone Sacre Pop» (fino al 30/09): tutte ancora `da-approvare` a registro. Non
entrano finché Michele non le approva. `M02` Buonenove 2 ha chiuso il 03/09 → fuori finestra.

**8) Nessun evento verificato per lunedì 07/09 e giovedì 10/09.** Il grafico parte da martedì:
è il calendario, non un buco nostro. Non si inventano eventi per riempire una casella.

---

## CAPTION (ora · indirizzo · link — NIENTE prezzi né «gratis», regola equità 13/07/2026)

```
📅 La settimana a San Marino, dal 7 al 13 settembre — 8 appuntamenti da segnare 👇

MARTEDÌ 08/09
🎬 21:00 · Concerto a Lume di Candela, omaggio a Ennio Morricone: tributo al maestro e alla musica da film, tra centinaia di candele — prenotazione obbligatoria · Orti Borghesi, Centro Storico, Città di San Marino

MERCOLEDÌ 09/09
🚶 18:00 · Serravalle in Wellness, camminata di gruppo a media intensità (prima dei quattro mercoledì di settembre, punto di partenza diverso ogni settimana) · La Ciarulla (parcheggio Globo), Serravalle

VENERDÌ 11/09
🎶 SanMarinoBeerFest: Vipers, Queen Tribute band · Parco di Dogana, San Marino
🏍 11–13/09 · Gran Premio MotoGP di San Marino, tre giorni di gare e spettacolo per il Gran Premio intitolato alla Repubblica (gara domenica 13/09 ore 14:00) · Misano World Circuit Marco Simoncelli, Misano Adriatico (RN)

SABATO 12/09
🎺 11:30–13:30 · Musikfest Adriatica, incontro internazionale di bande musicali per le vie del centro · Centro Storico, Città di San Marino
🎶 SanMarinoBeerFest: Love Generation 90, DJ set "Il tuo viaggio negli anni 90", cucina dalle 20:00 · Parco di Dogana, San Marino
🍇 12–13/09 · "Dal Turista al Contadino" — II tappa, food truck e degustazioni della tradizione sammarinese su due sedi · Via Eugippo, Città di San Marino e Piazza Mercatale, Borgo Maggiore

DOMENICA 13/09
🏆 11:00 · 36° Palio Don Bosco: Santa Messa, pranzo comunitario sotto i portici e nel pomeriggio le gare tra le sei frazioni (caratelle, trampoli, funi, palo della cuccagna) · Piazza Grande, Borgo Maggiore

Salva il post 📌 e seguici per gli eventi di ogni giorno
ℹ️ Date e orari possono cambiare: verifica sempre sulla fonte ufficiale dell'organizzatore (link in bio).

#SanMarinoHappens #SanMarino #RepubblicaDiSanMarino #MonteTitano #cosafareaSanMarino #eventiSanMarino #MotoGP #GPSanMarino #SanMarinoBeerFest #PalioDonBosco #EnnioMorricone #Musikfest
```

⚠️ **Nessun prezzo/gratuità in caption, di proposito** — la regola equità del 13/07/2026
vieta «€», «gratis», «gratuito», «ingresso libero» ecc. ovunque, grafico E caption
(memoria `feedback_prezzi_in_caption_aggregati_blocca_per_sempre`). `publish.py` blocca in
automatico e in silenzio qualsiasi caption con questi termini.

---

## Hook footer del grafico

`📅 La settimana a San Marino: 8 eventi da segnare 👇` — variante neutra. Non la «settimana
piena» (serve un tono diverso). `{N}` = 8 = numero esatto di righe evento sul grafico.
