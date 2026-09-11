# Settimanale 14–20/09/2026 — dossier per la grafica

**Motivo:** guardia `scripts/controllo-imminenti.py` (Step 2-bis della catena giornaliera,
11/09/2026 18:30) — usciva con codice 2: buco «Settimanale del 13/09 Domenica ore 18:00»
dentro le 48 ore, a copertura della settimana 14–20/09. Slot regolare: **domenica 13/09
ore 18:00** — ma la catena gira alle 18:30 di *oggi* 11/09, quindi si mette in coda subito,
in anticipo di due giorni sullo slot (nessun recupero necessario).

**Master Canva:** `SMH - Settimanale Master` = **`DAHORdC0zdY`** — identificarlo **solo per
questo ID**, mai per nome. Si lavora su **COPIA** (`copy-design`), titolata
`🗑 DA ELIMINARE — SMH · Settimanale — 14-20/09`.
**Rotazione:** `dati/grafica-stato.json` → `designs.settimanale.ultima_pagina_usata` = 4 di 4
→ questo giro **fa il giro (wrap)** e usa la **pagina 1**.

**7 eventi → 1 slide** (template a 8 righe: la riga 8 non usata va cancellata e il blocco
ricentrato — vedi `/smh-grafica` sezione Aggregati, punto 6).

Giorni della settimana **calcolati in Python** l'11/09/2026:
`14/09 → Lunedì · 15/09 → Martedì · 16/09 → Mercoledì · 17/09 → Giovedì · 18/09 → Venerdì ·
19/09 → Sabato · 20/09 → Domenica`

Fonte di ogni riga: `dati/calendario/master.md` righe 80, 49, 50, 85, 51, 86, 82. Nessun dato
aggiunto che non sia già nel registro o nelle bozze già scritte (`dati/post/post-2026-09-07.md`,
`dati/post/post-2026-08-16.md`) — con una correzione, vedi punto 2 sotto.

---

## Righe per il GRAFICO (giorno·data · titolo · luogo BREVE — niente ora, niente prezzi)

### Slide unica (pagina 1 del master, dopo il wrap) — 7 righe piene, riga 8 cancellata
| # | Giorno/data | Titolo | Luogo breve |
|---|---|---|---|
| 1 | Martedì 15/09 | Concorso Renata Tebaldi | Borgo Maggiore |
| 2 | Mercoledì 16/09 | Serravalle in Wellness | Domagnano |
| 3 | Ven–Dom 18–20/09 | Sport in Fiera | Serravalle |
| 4 | Venerdì 18/09 | BeerFest · Radiokom | Parco di Dogana |
| 5 | Sabato 19/09 | Gran Premio Nuvolari | San Marino |
| 6 | Sabato 19/09 | BeerFest · Afro Tour | Parco di Dogana |
| 7 | Sab–Dom 19-20/09 | Special Cup | Montecchio |

`{N}` = **7** righe evento. Primo evento: 15/09. Ultimo: 20/09.

- Titoli tenuti sotto ~24 caratteri per stare sul font più grande a una riga
  (memoria `reference_geometria_titoli_aggregati`).
- «BeerFest · Radiokom» / «BeerFest · Afro Tour»: due serate distinte dello stesso
  SanMarinoBeerFest, su righe separate (come nel weekend 11-13/09).

---

## ⚠️ Righe da tenere d'occhio (segnalate, non nascoste)

**1) Serravalle in Wellness (16/09) — serie ricorrente, riga master unica [80] con 4 date.**
Il master elenca 09/09 (Ciarulla, già passata), **16/09 Domagnano (parcheggio sotto la
chiesa)**, 23/09 (Montegiardino) e 30/09 (Parco Ausa). Qui entra **solo** l'appuntamento del
16/09, trovato con `scripts/serie_ricorrenti.py 21` — la guardia `controllo-imminenti.py` non
la vede per il buco settimanale (il suo parser di date legge solo l'ultima data della lista,
30/09, per questa riga) e nessun altro anello l'avrebbe ripescata da sola. Il 16/09 **non ha
nessun'altra busta** in coda (né feed né storia): questa riga nel settimanale è la sua unica
copertura per ora.

**2) SanMarinoBeerFest (18–19/09) — luogo corretto in QUESTO dossier, diverso dalle bozze
vecchie.** Le bozze `post-2026-08-16.md` (16/08, ancora presenti nel repo) dicono «Campo
Bruno Reffi, Borgo Maggiore»: è un **dato stantio**. Il master (righe 85/86) fu corretto il
24/08/2026 sulla locandina ufficiale → **Parco di Dogana, San Marino**. Qui uso la versione
del master, non quella delle bozze vecchie.

**3) BeerFest Radiokom (18/09) e Afro Tour (19/09) — «solo storia» per il post SINGOLO, ma
compaiono comunque nell'aggregato.** Il motivo del "solo storia" è che il feed di quei
giorni è già occupato (Sport in Fiera il 18, Nuvolari il 19) — non riguarda il settimanale,
che elenca sempre tutti gli eventi approvati della settimana (regola
`feedback_weekend_venerdi_sabato_domenica`).

**4) San Marino Special Cup (19-20/09) — stessa logica del punto 3.** «Solo storia» per il
post del giorno (19/09 e 20/09 già occupati da Nuvolari/Sport in Fiera), ma entra
nell'aggregato.

**5) Concorso Renata Tebaldi (15-18/09) — sul grafico solo il giorno di apertura (15/09).**
Il programma vero è eliminatorie 15, semifinale 16, prove con orchestra 17, finale con
orchestra 18 (ore 21:00) — dettagliato in caption, non sul grafico (spazio della riga
insufficiente per 4 sotto-date).

**6) Nessun evento per lunedì 14/09.** Il registro non ha righe che tocchino quel giorno:
resta scoperto perché il calendario è vuoto lì, non per un errore nostro.

---

## CAPTION (ora · indirizzo · link — NIENTE prezzi né «gratis», regola equità 13/07/2026)

```
📅 La settimana a San Marino — dal 14 al 20 settembre.

MARTEDÌ 15
🎤 11ª edizione del Concorso Internazionale di Canto Renata Tebaldi, sezione Opera —
eliminatorie il 15, semifinale il 16, prove con orchestra il 17, finale con orchestra il 18
ore 21:00 · Teatro Concordia, Borgo Maggiore

MERCOLEDÌ 16
🚶 Serravalle in Wellness, camminata a media intensità (18:00-20:00 ca.) · Domagnano,
partenza dal parcheggio sotto la chiesa

VENERDÌ 18
🤸 Sport in Fiera, la rassegna multidisciplinare del CONS con le federazioni sportive — per
la prima volta su tre giorni, venerdì mattina dedicato alle scuole elementari · Multieventi
Sport Domus, Serravalle
🎶 SanMarinoBeerFest: Radiokom, tributo a Vasco Rossi, cucina dalle 20:00 · Parco di Dogana,
San Marino
🎤 21:00 · finale con orchestra del Concorso Renata Tebaldi · Teatro Concordia, Borgo
Maggiore

SABATO 19
🏎 17:00 · 36° Gran Premio Nuvolari, passaggio e gala della gara di regolarità per auto
d'epoca (300 equipaggi, ~1100 km) · San Marino, tappa sammarinese del percorso
🎶 SanMarinoBeerFest: serata "European Afro Tour", cucina dalle 20:00 · Parco di Dogana, San
Marino
⚽ San Marino Special Cup 2026, torneo di calcio a 5 per sport speciali, 10 squadre tra cui
San Marino · Campo Sportivo di Montecchio (19-20/09)

DOMENICA 20
🤸 Ultimo giorno di Sport in Fiera · Multieventi Sport Domus, Serravalle
⚽ Ultimo giorno di San Marino Special Cup 2026 · Campo Sportivo di Montecchio

Salva il post 📌 e seguici per gli eventi di ogni giorno
ℹ️ Date e orari possono cambiare: verifica sempre sulla fonte ufficiale dell'organizzatore (link in bio).

#SanMarinoHappens #SanMarino #RepubblicaDiSanMarino #MonteTitano #cosafareaSanMarino #eventiSanMarino #RenataTebaldi #SportInFiera #SanMarinoBeerFest #GranPremioNuvolari #SpecialCup #SerravalleInWellness
```

⚠️ **Nessun prezzo/gratuità in caption, di proposito** — regola equità 13/07/2026: vietati
«€», «gratis», «gratuito», «ingresso libero» ovunque, grafico E caption
(`feedback_prezzi_in_caption_aggregati_blocca_per_sempre`). Rimossi rispetto alle fonti:
biglietto finale Tebaldi (€20), ingresso gratuito Sport in Fiera, gratuità Serravalle in
Wellness. `publish.py`/`controllo-caption-prezzi.py` bloccano in silenzio se restano.

---

## Hook footer del grafico

`📅 La settimana a San Marino: 7 eventi da segnare 👇` — `{N}` = 7 = numero esatto di righe
evento sul grafico.

**Slot:** in coda oggi 11/09 (in anticipo sullo slot regolare di domenica 13/09 18:00) ·
**Tipo busta:** settimanale · **Tag:** nessuno (aggregato).
