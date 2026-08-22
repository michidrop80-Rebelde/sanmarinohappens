# Settimanale 24–30/08/2026 — dossier per la grafica

**Slot di pubblicazione:** **domenica 23/08 ore 18:00** — slot regolare (copre la settimana
24–30/08). Scritto il 21/08/2026 dallo Step 2-bis della catena (guardia imminenti-48h:
`controllo-imminenti.py` usciva con codice 2).

**Master Canva:** `SMH - Settimanale Master` = **`DAHORdC0zdY`** — verificare in
`dati/grafica-stato.json` la pagina successiva alla rotazione (l'ultimo giro, 18-23/08,
aveva usato le pagine 3 e 4). Si lavora **su COPIA**, titolata
`🗑 DA ELIMINARE — SMH · Settimanale — 24-30/08`.
**15 eventi → 2 slide** (8 + 7).

Giorni della settimana **calcolati in Python** il 21/08/2026:
`24/08 Lunedì · 25/08 Martedì · 26/08 Mercoledì · 27/08 Giovedì · 28/08 Venerdì · 29/08 Sabato · 30/08 Domenica`

Fonte di ogni riga: `dati/calendario/master.md` (righe 36, 36b, 46, 46b, 46d, 46e, 66, 71, 77,
78, M02). Nessun dato aggiunto che non sia già nel registro.

---

## Righe per il GRAFICO (giorno·data · titolo · luogo BREVE — niente ora, niente prezzi)

### Slide 1
| # | Giorno/data | Titolo | Luogo breve |
|---|---|---|---|
| 1 | Lunedì 24/08 | Cinema: Rental Family | Domagnano |
| 2 | Martedì 25/08 | Cinema: Rapunzel | Domagnano |
| 3 | Mercoledì 26/08 | Cinema: Jumpers | Domagnano |
| 4 | Mercoledì 26/08 | Cena Tramonto & Live | Faetano |
| 5 | Giovedì 27/08 | Giovedì in Centro | Centro Storico |
| 6 | Ven-Sab 28-29/08 | Trenino Bianco Azzurro | Piazzale Stazione |
| 7 | Venerdì 28/08 | Noche Argentina | Torraccia |
| 8 | Ven-Dom 28-30/08 | San Marino Comics | Centro Storico |

### Slide 2
| # | Giorno/data | Titolo | Luogo breve |
|---|---|---|---|
| 9 | Sab-Dom 29-30/08 | 33° San Marino Revival | Serravalle |
| 10 | Sabato 29/08 | 21° Giro dei Castelli | 9 Castelli |
| 11 | Sabato 29/08 | Piano: Malferrari | Fiorentino |
| 12 | Sabato 29/08 | Cocktails Ronzanti | Montecchio |
| 13 | Sabato 29/08 | Pellegrinaggio | Vari luoghi |
| 14 | Domenica 30/08 | Viaggio Musicale | Teatro Titano |
| 15 | Fino al 03/09 | Buonenove 2 - Arte Urbana | 9 Castelli |

✅ **Aggiornamento 22/08/2026 (catena, Step 1):** Michele ha approvato entrambi via
Telegram (pulsanti `20260821-1931-M09` e `20260821-1931-46c`, 21/08 19:53 UTC) — reinseriti
come riga 5 di Slide 1 (Giovedì in Centro) e riga 12 di Slide 2 (Cocktails Ronzanti), con
numerazione e split 8+7 ricalcolati come da piano originale. **La busta era già in coda su
GitHub** (`posts/20260823_Settimanale.json`, senza questi due eventi): va ricompilata su
Canva e rimessa in coda prima della pubblicazione di domani 23/08 18:00.

Tutti i titoli stanno entro **26 caratteri** (tetto del box settimanale: font 40 ≈ 25 caratteri,
vedi memoria `reference_geometria_titoli_aggregati`). Titolo al font più grande che sta **su una riga**.

---

## ⚠️ Righe da tenere d'occhio (segnalate, non nascoste)

**1) Giovedì in Centro (27/08) — ✅ RISOLTO 22/08: approvato, reinserito.**
Riga M09 del master (serie ricorrente): 4 date confermate dalla fonte (30/07, 06/08, 13/08,
27/08), tutte reali — la riga aveva stato post `da-approvare`, mai passata da nessun agente
testi. Michele ha premuto ✅ su Telegram (pulsante `20260821-1931-M09`, 21/08 19:53 UTC):
ora riga 5 di Slide 1. Bozza singola in `dati/post/post-2026-08-03.md` (narrowed a solo
27/08, le occorrenze 30/07·06/08·13/08 erano ormai passate senza post dedicato).

**2) Cocktails Ronzanti (29/08) — ✅ RISOLTO 22/08: confermato, reinserito.**
Riga 46c del master: evento reale, confermato su volantino ufficiale del Consorzio, stato
post era `non pianificato` con la domanda aperta "confermare se entra nel piano editoriale".
Michele ha premuto ✅ su Telegram (pulsante `20260821-1931-46c`, 21/08 19:53 UTC): ora riga
12 di Slide 2. La storia dedicata era già in coda da prima (`posts/20260829_Storia.json`) —
qui si aggiunge solo la riga nell'aggregato settimanale.

**3) Campionato Sammarinese di Calcio 2026-27, 1ª giornata (28-30/08) — NON incluso.**
Riga 58: giorno esatto e orari **non ancora pubblicati da FSGC** (solo il weekend è
confermato). Stesso trattamento della semifinale baseball esclusa la settimana scorsa: non si
mette una partita su un grafico senza sapere che giorno si gioca. Da riprendere quando FSGC
pubblica il calendario dettagliato.

**4) Baseball — Semifinale playoff gara 7 (24/08, eventuale) — NON inclusa.**
Riga 56d: condizionale, esiste solo se la serie è 3-3 dopo gara 6 (23/08/2026) — che al
momento in cui scrivo (21/08) non si è ancora giocata. Non si può sapere se questa partita
esisterà. Da valutare nel prossimo giro, dopo il 23/08.

**5) Trenino Bianco Azzurro — solo venerdì e sabato in questa finestra.**
Riga 66: le date della serie sono 21,22,23,28,29/08. Il 21-23 era già coperto dal settimanale
recuperato del 18-23/08: qui riporto solo le due date nuove (28-29/08), niente doppioni.

**6) 33° San Marino Revival — orari non ancora pubblicati.**
Riga 36: evento rinviato dall'01-02/08 al 29-30/08 per motivi di salute del presidente
federale; gli orari della nuova data non sono ancora usciti. Riportato solo come "29-30/08",
niente orario inventato.

**7) Pellegrinaggio sui passi di San Marino e San Francesco (29/08) — punto di partenza
esatto non confermato.** Riga 77: percorso e data certi (fonte diretta, org. Segreteria di
Stato Turismo), manca solo il punto di partenza esatto tra quelli elencati. Sul grafico:
"Vari luoghi". In caption: percorso per esteso, senza inventare un punto di partenza preciso.

---

## CAPTION (ora · indirizzo · prezzi — NON va sul grafico)

```
📅 La settimana a San Marino — dal 24 al 30 agosto.

LUNEDÌ 24
🎬 21:00 · Cinema nei Castelli, "Rental Family" · Parco Don Elvirio, Domagnano

MARTEDÌ 25
🎬 21:00 · Cinema nei Castelli, "Rapunzel" · Parco Don Elvirio, Domagnano

MERCOLEDÌ 26
🎬 21:00 · Cinema nei Castelli, "Jumpers" · Parco Don Elvirio, Domagnano
🍽 20:15 · Cena Tramonto & Live, cena-concerto di beneficenza pro Vivere Meglio · InPerfetto Bar e Cucina, Piazza della Porta Vecchia, Faetano

GIOVEDÌ 27
🛍 Fino alle 23:00 · Giovedì in Centro, negozi aperti, giro col Treno Bianco Azzurro, artisti di strada · Centro Storico, Piazza della Libertà

VENERDÌ 28
🚂 Trenino Bianco Azzurro · Piazzale della Stazione · ven e sab 10:00-12:00 e 14:30-17:30
🕖 19:00 · Noche Argentina, asado e grigliata, musica argentina dei Locos · Torraccia, Cooperativa Allevatori Sammarinesi
🎭 San Marino Comics 2026, tema "Press Play" · Centro Storico + Campo Bruno Reffi · ven-sab 10:00-01:00, dom 10:00-20:00

SABATO 29
🏎 33° San Marino Revival, auto storiche · Multieventi Sport Domus, Serravalle · orari non ancora pubblicati
🚗 21° Giro dei Castelli di San Marino, raduno auto storiche · percorso panoramico nei 9 castelli
🕡 18:30 · Piano, Stefano Malferrari · Castellaccio di Fiorentino
🐝 19:00 · Cocktails Ronzanti, mixology e aperitivo nel verde del Parco · Bioparco Apistico San Marino, Str. di Montecchio
🚶 08:30 · Pellegrinaggio sui passi di San Marino e San Francesco · percorso Costa dell'Arnella → Città → Chiesa della Meditazione e del Silenzio → Chiesa di San Francesco → Basilica del Santo → Tre Torri

DOMENICA 30
🎭 San Marino Comics 2026 (ultimo giorno) · Centro Storico + Campo Bruno Reffi · 10:00-20:00
🕠 17:30 · Viaggio Musicale attorno al Mondo, rassegna "Macinare Cultura 2026" · Teatro Titano

🎨 Fino al 3 settembre · Buonenove 2, arte urbana nei 9 Castelli

Salva il post 📌 e seguici per gli eventi di ogni giorno
ℹ️ Date e orari possono cambiare: verifica sempre sulla fonte ufficiale dell'organizzatore (link in bio).

#SanMarinoHappens #SanMarino #RepubblicaDiSanMarino #MonteTitano #cosafareaSanMarino #eventiSanMarino #SanMarinoComics #SanMarinoRevival #GiovediInCentro #CocktailsRonzanti
```

⚠️ **Nessun prezzo/gratuità in caption, di proposito** (non solo "omesso perché non trovato"):
la regola equità del 13/07/2026 vieta prezzi e "gratis" ovunque, grafico E caption — vedi
`.claude/skills/smh-testi/SKILL.md:63`. La bozza iniziale di questa caption li conteneva
ancora (retaggio del formato usato prima del 13/07 per gli aggregati); rimossi prima di
mettere la busta in coda, perché `publish.py` blocca in automatico (e silenziosamente per
sempre, trattandosi di un aggregato) qualsiasi caption con questi termini — è la causa,
scoperta oggi, per cui la busta gemella della settimana scorsa (`20260818_Settimanale`) non
è mai uscita in 3+ giorni nonostante il robot girasse regolarmente.
