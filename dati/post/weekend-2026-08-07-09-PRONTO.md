# Weekend 07–09/08/2026 — dossier pronto per la grafica

**Stato:** contenuto chiuso e verificato alla fonte il 07/08/2026. **Manca solo la compilazione su Canva** (MCP non connesso dal 05/08).
**Slot di pubblicazione:** recupero **ven 07/08 ore 18:00** — lo slot regolare (gio 06/08 18:00) è passato a vuoto per il blocco Canva. Dentro la finestra di recupero weekend (2 giorni, mai di domenica).
**Master Canva:** `SMH - Weekend` = **`DAHOp1t_N1A`** — lavorare su una **COPIA** (`copy-design`), identificarlo **solo per questo ID** (17 design omonimi in account).
**Stima:** 9 righe evento + 3 intestazioni giorno → **2 slide** (come il weekend 31/07–02/08: 8 eventi → 2 slide).

Giorni della settimana **calcolati in Python** il 07/08/2026:
`2026-08-07 → Venerdì · 2026-08-08 → Sabato · 2026-08-09 → Domenica`

---

## Righe per il GRAFICO (giorno · titolo · luogo BREVE — niente ora, niente prezzi)

### VEN 7 AGOSTO
| Titolo | Luogo breve |
|---|---|
| Aperitivo con Battisti | Uliveto, Falciano |
| Benji & Fede — Summer Vibes | SM Outlet, Falciano |
| Greg — Tre Serate di Emozioni | Campo Bruno Reffi |
| Sagra della Tagliatella (fino al 10/08) | Piazza Cailungo |

### SAB 8 AGOSTO
| Titolo | Luogo breve |
|---|---|
| San Francesco: Passi sul Titano | Partenza Borgo Maggiore |
| Concerto per l'Europa — Harmonie Mont Saint Martin | Cava dei Balestrieri |
| Paolo Jannacci — Tre Serate di Emozioni | Campo Bruno Reffi |

### DOM 9 AGOSTO
| Titolo | Luogo breve |
|---|---|
| Alba sul Monte — «Sonate e Danze» | Orti dell'Arciprete |
| Eugenio Finardi — Tre Serate di Emozioni | Campo Bruno Reffi |

⚠️ **Scelta fatta sulla Sagra della Tagliatella** (06–10/08, tutti e tre i giorni): messa **una volta sola**, il venerdì, con la dicitura «fino al 10/08». Ripeterla su tutti e tre i giorni occupava 3 righe su 9 e sbilanciava il grafico. In caption è invece richiamata per ogni giorno.

---

## CAPTION (ora · indirizzo · prezzi — questo NON va sul grafico)

```
🌞 Il weekend a San Marino — dal 7 al 9 agosto.

VENERDÌ 7
🕖 19:00 · Aperitivo con Battisti — tributo a Lucio Battisti con Martin Navello · Uliveto, Str. La Zanetta 65, Falciano
🕘 21:00 · Benji & Fede — Summer Vibes · San Marino Outlet, Falciano · prenotazione obbligatoria su sanmarinooutlet.com
🕘 21:15 · Greg — Tre Serate di Emozioni · Campo Bruno Reffi
🕕 dalle 18:00 · Festa di San Rocco, Sagra della Tagliatella · Piazza Cailungo, Via Cà Carlo 6 · fino al 10/08

SABATO 8
🕗 08:00 · San Francesco: Passi sul Monte Titano — cammino spirituale guidato, rientro previsto 11:30 · partenza dalla Chiesa del Suffragio, Piazza Mercatale, Borgo Maggiore
🕕 18:00 · Concerto per l'Europa — Harmonie Municipale di Mont Saint Martin · Cava dei Balestrieri, Centro Storico
🕘 21:15 · Paolo Jannacci — Tre Serate di Emozioni · Campo Bruno Reffi
🕕 dalle 18:00 · Sagra della Tagliatella · Piazza Cailungo

DOMENICA 9
🕕 06:00 · Alba sul Monte, «Sonate e Danze» con Anna Bodnar (fisarmonica) e Riccardo Guazzini (sax) · Orti dell'Arciprete, Centro Storico · colazione inclusa, prenotazione consigliata 337 1008856
🕘 21:15 · Eugenio Finardi — Tre Serate di Emozioni · Campo Bruno Reffi
🕕 dalle 18:00 · Sagra della Tagliatella · Piazza Cailungo

Salva il post 📌 e seguici per gli eventi di ogni giorno
ℹ️ Date e orari possono cambiare: verifica sempre sulla fonte ufficiale dell'organizzatore (link in bio).

#SanMarinoHappens #SanMarino #RepubblicaDiSanMarino #MonteTitano #cosafareaSanMarino #eventiSanMarino #weekend #TreSerateDiEmozioni #CampoBrunoReffi
```

✅ Caption ripulita da prezzi e «gratis» il 07/08 (regola di equità — la guardia di publish.py blocca le buste che li contengono).
⚠️ Contare la caption in **UTF-16** prima di mettere in coda (limite Instagram 2200 — la guardia in `publish.py` blocca la busta se sfora).

---

## Ricontrollo alla fonte — Step 3-bis (eventi entro 21 giorni)

🔁 **Ricontrollati alla fonte: 6** · nessun evento rinviato, annullato o spostato.

| Evento | Esito | Fonti (2 indipendenti dove possibile) |
|---|---|---|
| Greg / Jannacci / Finardi | ✅ confermati · **trovato l'orario mancante: 21:15**, tutti e tre gratuiti | GiornaleSM + San Marino RTV |
| Harmonie Municipale Mont Saint Martin | ✅ 08/08, 18:00, Cava dei Balestrieri, gratis | San Marino RTV (comunicato dedicato) |
| San Francesco: Passi sul Monte Titano | ✅ · **trovato il punto di ritrovo che mancava**: partenza 08:00 Chiesa del Suffragio, Piazza Mercatale, Borgo Maggiore; rientro 11:30 | GiornaleSM + Libertas |
| Alba sul Monte — «Sonate e Danze» | ✅ 09/08, 06:00, Orti dell'Arciprete · **trovati gli esecutori**: Anna Bodnar (fisarmonica), Riccardo Guazzini (sax) | San Marino RTV |
| Benji & Fede | ✅ · **trovato l'orario: 21:00**, gratis previa prenotazione | San Marino RTV + Altarimini |
| Festa di San Rocco — Sagra della Tagliatella | ✅ date 06–10/08 confermate (ordinanza di chiusura al traffico del Parco di Cailungo dal 06/08 ore 16:00 al 10/08 mezzanotte) | GiornaleSM |

📌 Le 5 informazioni nuove sono state **scritte nel master** (`dati/calendario/master.md`, righe 32, 39, 40, 41, 41b, 43) così non vanno ricercate al prossimo giro.

## Buste già in coda per questi giorni — nessuna da correggere

Controllate una per una: `20260807`, `20260808` (post + storia), `20260809` (post + storia) riportano già **21:15** e i luoghi giusti. Il PNG della storia dell'8 è stato riletto a vista: giorno «Sabato 8 Agosto» corretto, 08:00 e 21:15 corretti. **Nessun 🔴 di busta da correggere.**
