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
| 5 | Ven-Sab 28-29/08 | Trenino Bianco Azzurro | Piazzale Stazione |
| 6 | Venerdì 28/08 | Noche Argentina | Torraccia |
| 7 | Ven-Dom 28-30/08 | San Marino Comics | Centro Storico |
| 8 | Sab-Dom 29-30/08 | 33° San Marino Revival | Serravalle |

### Slide 2
| # | Giorno/data | Titolo | Luogo breve |
|---|---|---|---|
| 9 | Sabato 29/08 | 21° Giro dei Castelli | 9 Castelli |
| 10 | Sabato 29/08 | Piano: Malferrari | Fiorentino |
| 11 | Sabato 29/08 | Pellegrinaggio | Vari luoghi |
| 12 | Domenica 30/08 | Viaggio Musicale | Teatro Titano |
| 13 | Fino al 03/09 | Buonenove 2 - Arte Urbana | 9 Castelli |

⚠️ 13 righe di contenuto certo (non 15): **Giovedì in Centro (27/08) e Cocktails Ronzanti
(29/08) sono stati tenuti fuori**, vedi sezione dubbi sotto — il conteggio "15 eventi" nel
titolo include questi due, da ridurre a 13 se restano esclusi in via definitiva. Se Michele
approva Giovedì in Centro in tempo, va reinserito come riga 5 di Slide 1 (Giovedì 27/08,
Centro Storico) e la numerazione slitta.

Tutti i titoli stanno entro **26 caratteri** (tetto del box settimanale: font 40 ≈ 25 caratteri,
vedi memoria `reference_geometria_titoli_aggregati`). Titolo al font più grande che sta **su una riga**.

---

## ⚠️ Righe da tenere d'occhio (segnalate, non nascoste)

**1) Giovedì in Centro (27/08) — NON incluso: manca l'ok di Michele, mandato su Telegram.**
Riga M09 del master (serie ricorrente): 4 date confermate dalla fonte (30/07, 06/08, 13/08,
27/08), tutte reali — ma la riga ha stato post **`da-approvare`**, mai passata da nessun
agente testi. `scripts/serie_ricorrenti.py 30` lo segnala esplicitamente: "servono prima i
pulsanti ✅ di Michele su Telegram". Diverso dal caso Balamondo (18-23/08): lì l'evento aveva
già una bozza in attesa del solo click; qui non esiste ancora nessuna bozza né decisione. Ho
mandato a Michele l'approvazione via Telegram con i pulsanti per questo evento specifico
(vedi referto). Se non risponde entro stasera, il 27/08 resta scoperto nel settimanale — è
una scelta sua, non un buco della catena.

**2) Cocktails Ronzanti (29/08) — NON incluso: decisione editoriale in sospeso, non un dubbio
sul fatto.** Riga 46c del master: evento reale, confermato su volantino ufficiale del
Consorzio, ma stato post **`non pianificato`** con nota esplicita di chi ha verificato:
"⚠️ a margine della finestra 60gg — confermare se entra nel piano editoriale". Non è un dubbio
sulla data o il luogo (certi), è una domanda aperta se Michele lo vuole nel piano editoriale
per niente. Non decido io al posto suo: resta fuori finché non risponde.

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

VENERDÌ 28
🚂 Trenino Bianco Azzurro · Piazzale della Stazione · ven e sab 10:00-12:00 e 14:30-17:30
🕖 19:00 · Noche Argentina, asado e grigliata, musica argentina dei Locos · Torraccia, Cooperativa Allevatori Sammarinesi
🎭 San Marino Comics 2026, tema "Press Play" · Centro Storico + Campo Bruno Reffi · ven-sab 10:00-01:00, dom 10:00-20:00

SABATO 29
🏎 33° San Marino Revival, auto storiche · Multieventi Sport Domus, Serravalle · orari non ancora pubblicati
🚗 21° Giro dei Castelli di San Marino, raduno auto storiche · percorso panoramico nei 9 castelli
🕡 18:30 · Piano, Stefano Malferrari · Castellaccio di Fiorentino
🚶 08:30 · Pellegrinaggio sui passi di San Marino e San Francesco · percorso Costa dell'Arnella → Città → Chiesa della Meditazione e del Silenzio → Chiesa di San Francesco → Basilica del Santo → Tre Torri

DOMENICA 30
🎭 San Marino Comics 2026 (ultimo giorno) · Centro Storico + Campo Bruno Reffi · 10:00-20:00
🕠 17:30 · Viaggio Musicale attorno al Mondo, rassegna "Macinare Cultura 2026" · Teatro Titano

🎨 Fino al 3 settembre · Buonenove 2, arte urbana nei 9 Castelli

Salva il post 📌 e seguici per gli eventi di ogni giorno
ℹ️ Date e orari possono cambiare: verifica sempre sulla fonte ufficiale dell'organizzatore (link in bio).

#SanMarinoHappens #SanMarino #RepubblicaDiSanMarino #MonteTitano #cosafareaSanMarino #eventiSanMarino #SanMarinoComics #SanMarinoRevival
```

⚠️ **Nessun prezzo/gratuità in caption, di proposito** (non solo "omesso perché non trovato"):
la regola equità del 13/07/2026 vieta prezzi e "gratis" ovunque, grafico E caption — vedi
`.claude/skills/smh-testi/SKILL.md:63`. La bozza iniziale di questa caption li conteneva
ancora (retaggio del formato usato prima del 13/07 per gli aggregati); rimossi prima di
mettere la busta in coda, perché `publish.py` blocca in automatico (e silenziosamente per
sempre, trattandosi di un aggregato) qualsiasi caption con questi termini — è la causa,
scoperta oggi, per cui la busta gemella della settimana scorsa (`20260818_Settimanale`) non
è mai uscita in 3+ giorni nonostante il robot girasse regolarmente.
