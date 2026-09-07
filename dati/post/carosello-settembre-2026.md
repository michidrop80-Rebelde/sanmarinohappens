# Carosello mensile — SETTEMBRE 2026 — dossier per la grafica

**Motivo:** guardia `scripts/controllo-imminenti.py` (Step 2-bis della catena, 30/08/2026
sera) — nessun anello aveva ancora prodotto il carosello di settembre. Segnalato anche in
`ULTIMO_REPORT.md` come «prima cosa da guardare al prossimo avvio» (rischio di saltare come
il weekend di Ferragosto se il Mac resta spento).
**Slot di pubblicazione:** **domenica 31/08 ore 18:00** (regolare — il carosello esce sempre
l'ultimo giorno del mese precedente).
**Master Canva:** `SMH - Mensile Master` = **`DAHOd72cNmY`** (20 pagine alternate: dispari =
copertine, pari = interne). Lavorare su una **COPIA** (`copy-design` con `page_numbers`),
identificarla **solo per questo ID**. Copia titolata `🗑 DA ELIMINARE — SMH · Mensile — Settembre`.
**Copertina:** `ultima_copertina_usata` = 2 → questo mese usa la **copertina n.3 = pagina 5**
del master. Nome mese: **SETTEMBRE** (font a larghezza adattabile).
**Interne:** 4 slide-settimana, ognuna a colorazione RANDOM tra le pari (2,4,…,20), preferendo
varianti dove il font contrasta su tutta la sfumatura.

Tutti gli eventi sono già `approvato` a `dati/calendario/master.md` (righe citate). Nessun
dato nuovo. Esclusi gli eventi `da-approvare` (vedi sezione "Esclusi" in fondo).

Giorni della settimana **calcolati in Python (30/08/2026)** — vedi ogni riga.

---

## SLIDE 1 — COPERTINA (pagina 5 del master)
- Solo il nome del mese cambia: **SETTEMBRE**
- Testo fisso del template: "Tutti gli eventi del mese di SETTEMBRE sul territorio della
  Repubblica di San Marino" (non riscrivere il resto).

---

## SLIDE 2 — Settimana 1 · 1–6 settembre (3 righe, COMPILATA)

| # | Data (grafico) | Luogo BREVE | Titolo (grafico) |
|---|---|---|---|
| 1 | 01–02/09 | Serravalle | SM Baseball vs Parma |
| 2 | 03/09 | Città di San Marino | Festa di San Marino |
| 3 | 05–06/09 | Città di San Marino | Dal Turista al Contadino |

Righe master: 56f/56g (baseball finale g4 01/09 e g5 02/09; gara 3 il 31/08 ha il suo
giornaliero del giorno), 47, 59.
**Buonenove 2 (M02) NON inclusa**: mostra in corso dal 15/06, finisce il 3/09 — 2 soli
giorni di settembre, formato data «fino al…» ingombrante sul grafico. Scelta di formato.

## SLIDE 3 — Settimana 2 · 7–13 settembre (6 righe)

| # | Data (grafico) | Luogo BREVE | Titolo (grafico) |
|---|---|---|---|
| 1 | Mercoledì 09/09 | Serravalle | Serravalle in Wellness |
| 2 | Ven–Dom 11–13/09 | Misano | Gran Premio MotoGP |
| 3 | Venerdì 11/09 | Parco di Dogana | BeerFest — Vipers |
| 4 | Sabato 12/09 | Parco di Dogana | BeerFest — Love Generation 90 |
| 5 | Sab–Dom 12–13/09 | Città e Borgo | Dal Turista al Contadino — II |
| 6 | Domenica 13/09 | Borgo Maggiore | Palio Don Bosco |

Righe master: 80 (Serravalle in Wellness, 09/09 Ciarulla), 48, 84, 72, 60, 81.

## SLIDE 4 — Settimana 3 · 14–20 settembre (7 righe)

| # | Data (grafico) | Luogo BREVE | Titolo (grafico) |
|---|---|---|---|
| 1 | Mar–Ven 15–18/09 | Borgo Maggiore | Concorso Renata Tebaldi |
| 2 | Mercoledì 16/09 | Domagnano | Serravalle in Wellness |
| 3 | Ven–Dom 18–20/09 | Serravalle | Sport in Fiera |
| 4 | Venerdì 18/09 | Parco di Dogana | BeerFest — Radiokom |
| 5 | Sabato 19/09 | Repubblica | Gran Premio Nuvolari |
| 6 | Sabato 19/09 | Parco di Dogana | BeerFest — European Afro Tour |
| 7 | Sab–Dom 19–20/09 | Montecchio | San Marino Special Cup |

Righe master: 49, 80 (16/09 Domagnano), 50, 85, 51, 86, 82.

## SLIDE 5 — Settimana 4 · 21–30 settembre (5 righe)

| # | Data (grafico) | Luogo BREVE | Titolo (grafico) |
|---|---|---|---|
| 1 | Mercoledì 23/09 | Montegiardino | Serravalle in Wellness |
| 2 | Venerdì 25/09 | Parco di Dogana | BeerFest — Linkin Revolution |
| 3 | Sabato 26/09 | Parco di Dogana | BeerFest — Dicono di Cesare |
| 4 | Domenica 27/09 | Città | Giornata del Turismo |
| 5 | Mercoledì 30/09 | Parco Ausa | Serravalle in Wellness |

Righe master: 80 (23/09 Montegiardino, 30/09 Parco Ausa), 88, 74, 62.

⚠️ **Ultima slide (Slide 5): cancellare l'elemento FRECCIA "scorri 👉"** (`delete_element`),
non solo il testo. Nessuna slide CTA dedicata: la chiusura vive in caption.

---

## 📝 CAPTION (indice essenziale — ora + gratis/€ dove noti; il resto nel link in bio)

> ⚠️ REGOLA EQUITÀ (13/07/2026): NIENTE prezzi né gratuità in caption («gratis», «gratuito»,
> «€», «ingresso libero»…). `publish.py` blocca in silenzio le buste aggregate che li contengono
> (memoria `feedback_prezzi_in_caption_aggregati_blocca_per_sempre`). Solo orari sono ammessi.

📆 Settembre a San Marino, tutto il mese in un colpo d'occhio 👇

🗓 1–6 settembre
• SM Baseball vs Parma — Finale scudetto, gara 4 (1/9) e gara 5 (2/9) · Serravalle · 20:00
• Festa di San Marino · Centro Storico · dalle 10:00
• Dal Turista al Contadino — I tappa · Centro Storico (5–6/9) · cena su prenotazione

🗓 7–13 settembre
• Serravalle in Wellness · La Ciarulla · 9/9 · dalle 18:00
• Gran Premio Red Bull MotoGP di San Marino · Misano · gara domenica 13/9
• SanMarinoBeerFest · Parco di Dogana · Vipers – Queen Tribute (11/9), Love Generation 90 (12/9) · cucina dalle 20:00
• Dal Turista al Contadino — II tappa · Città e Borgo Maggiore (12–13/9)
• 36° Palio Don Bosco · Borgo Maggiore · 13/9 · messa 11:00, gare 15:30

🗓 14–20 settembre
• 11º Concorso Internazionale di Canto Renata Tebaldi · Teatro Concordia · 15–18/9
• Serravalle in Wellness · Domagnano · 16/9 · dalle 18:00
• Sport in Fiera · Multieventi, Serravalle · 18–20/9
• Gran Premio Nuvolari · strade della Repubblica · 19/9
• SanMarinoBeerFest · Parco di Dogana · Radiokom – Vasco Tribute (18/9), European Afro Tour (19/9)
• San Marino Special Cup — calcio a 5 sport speciali · Montecchio · 19–20/9

🗓 21–30 settembre
• Serravalle in Wellness · Montegiardino (23/9) e Parco Ausa (30/9) · dalle 18:00
• SanMarinoBeerFest · Parco di Dogana · Linkin Revolution (25/9), Dicono di Cesare – Cremonini Tribute (26/9)
• Giornata Mondiale del Turismo · Piazza della Libertà · 27/9 · 09:00–17:00

👉 Orari completi, indirizzi e link di ogni evento nel profilo (link in bio)
📌 Salva il post per averli sempre a portata di mano

**#️⃣ Hashtag**
#SanMarinoHappens #SanMarino #RepubblicaDiSanMarino #MonteTitano #cosafareaSanMarino #eventiSanMarino #SettembreSanMarino #eventiSettembre

---

## Esclusi (e perché)

- **56g gara 5 "eventuale"** → in realtà INCLUSA: la condizione si è sciolta il 30/08 (serie
  1-1, nel meglio-delle-7 la gara 5 si gioca comunque), riga promossa ad `approvato`.
- **61 "Artisti in Casa — Festival di Microspettacoli" (26–27/09, Montegiardino)** — resta
  `da-approvare` a registro. Fuori dal carosello finché non è approvato.
- **M07 "9x9 Opere tra Muri e Pareti" (fino al 03/09)** e **M08 "Icone Sacre Pop" di Simone
  Legno (fino al 30/09)** — entrambe `da-approvare`. Fuori.
- **Baseball gara 3 (31/08)** — è del 31 agosto, non di settembre: ha il suo post giornaliero
  del giorno (`dati/post/post-2026-08-31-baseball-g3.md`).
- **Eventuali gare 6-7 della finale (05–06/09)** — si giocano a Parma: trasferte, regola «di
  San Marino».

**Stato:** approvato (eventi a registro, dossier Step 2-bis)
