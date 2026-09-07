# Formato grafica — @sanmarinohappens
Aggiornato: 2026-07-02

Questo file definisce **come è composta visivamente ogni tipologia di post**.
Viene letto da smh-testi (per compilare il campo "Testo per la grafica") e da
smh-grafica (per costruire il template Canva corretto).

Regola generale: **l'immagine deve bastare da sola.** Il lettore non deve aprire
la caption per capire cos'è, quando è, dove è. La caption è solo il contorno.

---

## Dimensioni standard

| Formato | Dove | Dimensioni |
|---------|------|------------|
| Quadrato | Feed IG/FB — post singolo, aggregati | 1080 × 1080 px (1:1) |
| Verticale feed | Feed IG — alternativa post singolo | 1080 × 1350 px (4:5) |
| Story | Stories IG/FB | 1080 × 1920 px (9:16) |
| Carosello slide | Ogni slide del carosello | 1080 × 1080 px (1:1) |

Usare **sempre il quadrato** come default per feed, salvo note specifiche per tipo.

---

## Tipi di post e composizione grafica

---

### 1. POST SINGOLO (evento grande — feed)

**Quando:** concerti con artista nominato, gare europee, festival multi-giorno,
eventi istituzionali, qualsiasi evento che merita un post dedicato.

**Formato:** quadrato 1080×1080 (o verticale 4:5)

**Elementi nell'immagine — tutti obbligatori se disponibili:**
- 🏷 **Nome/titolo evento** — font grande, leggibile, elemento principale
- 📅 **Data** — giorno + mese (es. "3 luglio")
- 🕗 **Ora** — se disponibile (es. "ore 21:00")
- 📍 **Luogo** — nome ufficiale del posto (es. "Campo Bruno Reffi" — non "Serravalle")
- 🏔 **Logo/handle** @sanmarinohappens — in basso

**Elementi facoltativi nell'immagine:**
- Edizione (es. "12ª edizione") se è un tratto caratteristico dell'evento
- Nome artista/compagnia se diverso dal titolo evento

**Cosa NON va nell'immagine:**
- Prezzi o "ingresso gratuito" (regola equità — vale sempre, nessuna eccezione)
- URL, link, "prenotazione su…"
- Descrizioni lunghe o testo corpo

**Caption corrispondente:**
Solo CTA standard + hashtag. Niente contenuto, perché è tutto nell'immagine.

---

### 2. CAROSELLO MENSILE (1° e 15 del mese)

**Quando:** 1° di ogni mese (panoramica mese corrente + successivo) e 15
(aggiornamento mid-month). È il contenuto più ricco — più slide, più valore.

**Formato:** carosello — ogni slide 1080×1080

**Struttura slide:**

| Slide | Contenuto |
|-------|-----------|
| **1 — Cover** | "📅 [Mese] in Repubblica" · eventuale sottotitolo (es. "20+ eventi") · logo |
| **2-N — Un evento per slide** | Titolo · Data · Ora (se disponibile) · Luogo · tipo evento (icona) |
| **Ultima — CTA** | "Seguici per non perderti niente 👉 @sanmarinohappens" |

**Regola slide eventi:** ogni slide deve essere leggibile in 2 secondi.
Max 4 righe di testo per slide. Se l'evento ha un titolo lungo, spezzalo su 2 righe.

**Caption corrispondente:**
Riga breve di apertura (es. "Da luglio ad agosto, San Marino non si ferma.") + CTA + hashtag.
⚠️ Mai "sono pieni" o formule che suonano promozionali — già scartato da Michele.

---

### 3. POST SETTIMANALE (ogni lunedì)

**Quando:** ogni lunedì mattina — "Questa settimana in Repubblica".

**Formato:** quadrato 1080×1080 con lista eventi

**Elementi nell'immagine:**
- 🏷 **Titolo fisso:** "Questa settimana in Repubblica 🗓" (o "Questa settimana sul Titano")
- **Lista eventi della settimana:** max 5-6 righe, formato compatto:
  ```
  📅 Lun 07 · Tre Fiori — UEFA Champions League
  📅 Mar 08 · Chiringuito Faetano
  📅 Gio 10 · Sarah Toscano — Summer Vibes
  📅 Ven-Sab 11-12 · Symbol Remember
  ```
- 🏔 Logo @sanmarinohappens in basso

**Regola:** se gli eventi della settimana sono più di 6, tieni i più grandi e aggiungi
"+ altri eventi 👇" — non intasare l'immagine.

**Caption corrispondente:**
"Cosa c'è questa settimana in Repubblica 👇" + CTA + hashtag.

---

### 4. POST BISETTIMANALE (ogni mercoledì)

**Quando:** ogni mercoledì — outlook sulle prossime 2 settimane.

**Formato:** quadrato 1080×1080 — stesso stile del settimanale ma con orizzonte più ampio.

**Elementi nell'immagine:**
- 🏷 **Titolo fisso:** "Le prossime 2 settimane in Repubblica 🗓"
- **Lista eventi:** stesso formato compatto del settimanale, max 6-8 righe
  (se ci sono molti eventi, priorità ai grandi)
- 🏔 Logo @sanmarinohappens in basso

**Caption corrispondente:**
"Cosa bolle sul Titano nelle prossime due settimane 👇" + CTA + hashtag.

---

### 5. POST WEEKEND (ogni venerdì)

**Quando:** ogni venerdì — anteprima del weekend in arrivo (sabato + domenica).

**Formato:** quadrato 1080×1080

**Elementi nell'immagine:**
- 🏷 **Titolo fisso:** "Questo weekend in Repubblica 🎉" (o "Weekend sul Titano")
- **Evento principale in evidenza:** titolo grande, data, luogo — quello di punta del weekend
- **Separatore visivo** + lista degli altri eventi weekend in formato compatto
- 🏔 Logo @sanmarinohappens in basso

**Regola evento principale:** l'evento più grande (concerto noto, gara, festival) va
in evidenza grafica — font più grande o colore diverso. Gli altri in lista sotto.
Se tutti gli eventi del weekend sono "piccoli", usa solo la lista senza evidenza.

**Caption corrispondente:**
"Questo weekend in Repubblica 👇" + CTA + hashtag.

---

### 6. STORIES (giornaliero — evento del giorno)

**Quando:** ogni giorno con un evento rilevante. Non sempre — solo se c'è qualcosa.

**Formato:** verticale 1080×1920 (9:16)

**Elementi nell'immagine:**
- 🏷 **Titolo evento** — grande, al centro (sport → "Squadra vs Avversario")
- 📅 **Giorno** (della settimana, calcolato in Python) + **Data**
- 🕗 Ora (se presente)
- 📍 Luogo
- 📝 **Descrizione breve** — 1-2 righe, ~10-14 parole. **La scrive `smh-testi`** (box
  📱 Testo storia della bozza), non si compone a mano in fase grafica. È l'unico testo
  redazionale della storia; regole voce/no-prezzi in `.claude/skills/smh-testi/`.
- **CTA per posizione:** "👉 scorri…" sulle storie intermedie; **CTA di chiusura**
  sull'ultima (o sull'unica del giorno) — mai "scorri" sull'ultima.
- Logo @sanmarinohappens

**Note:** le stories hanno vita breve (24h) — devono essere immediate, niente testo
lungo. Un colpo d'occhio e basta. 1 storia per evento, ordine cronologico (impianto in
memoria `project-storie-architettura`).

**Caption:** non applicabile (le stories non hanno caption tradizionale — il testo è
tutto nell'immagine, descrizione breve compresa).

---

## Palette colori e font

⚠️ **Da definire con Michele prima di creare i template Canva.**
Segnaposto attuale:

| Elemento | Valore provvisorio | Da confermare |
|----------|-------------------|---------------|
| Colore primario | — | Sì |
| Colore secondario | — | Sì |
| Font titoli | — | Sì |
| Font corpo | — | Sì |
| Stile sfondo | — | Sì (foto evento? colore piatto? gradiente?) |

Queste scelte vanno prese PRIMA di creare i template Canva — ogni scelta qui
si propaga su tutti i ~70 post della stagione.

---

## Regole trasversali (valgono per ogni tipo)

- **Nome luogo = nome ufficiale**, mai la frazione/comune. "San Marino Outlet" non "Falciano".
- **Niente prezzi** nell'immagine (né "gratuito" né importi). Nessuna eccezione.
- **Handle @sanmarinohappens** presente in ogni immagine (logo o testo in basso).
- **Testo leggibile su mobile**: font minimo 28-30px equivalente, mai testo su sfondo
  con scarso contrasto.
- **Italiano** — niente anglicismi inutili nell'immagine.
