# Piano editoriale — San Marino Happens
Generato: 2026-06-30 · **Riallineato: 2026-07-09** (schema fasce 06/07 applicato riga per riga)
Finestra eventi: 28/06 → 23/08/2026
Bozze: `post-2026-06-28.md` (singoli) · `aggregati-luglio-agosto-2026.md` (aggregati)

> ℹ️ **Nota sul riallineo.** Le date qui sotto sono ricalcolate sulla logica decisa il
> 06/07 (aggregati la sera PRIMA alle 18:00). Alcune date sono già nel passato rispetto
> a oggi (09/07): normale, il piano modella l'intera finestra 28/06–23/08 e serve da
> modello corretto — al run vero conteranno solo le date future. Giorni della settimana
> calcolati in Python, non a occhio.

---

## Logica di pubblicazione

### Fasce orarie — schema deciso 06/07/2026 (idea di Michele, validata dal parere SMM)
Due fasce distinte per non far competere i post tra loro:
- **MATTINA (7:00) = contenuto del giorno**: le **storie** (tutti gli eventi di oggi) + l'eventuale **post singolo** del giorno.
- **SERA (18:00) = contenuto di pianificazione (aggregati)**, pubblicato **la sera PRIMA** che la finestra si apra, così non si sovrappone al quotidiano del mattino.

| Tipo | Quando | Contenuto |
|------|--------|-----------|
| Storie | ogni giorno **7:00** | tutti gli eventi del giorno |
| Evento singolo (feed) | **il giorno dell'evento**, mattina | l'evento più importante del giorno |
| Weekend | **giovedì 18:00** | "questo weekend in arrivo" — copre SEMPRE venerdì+sabato+domenica |
| Settimanale | **domenica 18:00** | "questa settimana in Repubblica" (settimana lun–dom successiva) |
| Carosello mensile | **ultimo giorno del mese precedente, 18:00** | tutti gli eventi del mese |
| ~~Bisettimanale~~ | **sospeso (09/07)** | — |

### Regole d'oro (aggiornate 09/07 — seconda passata)
1. **Max 1 feed al mattino + max 1 aggregato alla sera.** I due non si danno fastidio (11 ore di
   distanza) — la cannibalizzazione della reach riguarda solo post ravvicinati nella stessa fascia.
2. **Mai due feed nella stessa fascia mattutina.** Se due eventi "di calibro" cadono lo stesso
   giorno, uno solo va sul feed — l'altro va in storie. **Nessuno dei due cambia data** (vedi regola 4).
3. **Il post singolo del giorno rimanda SEMPRE alle storie** per gli altri eventi
   (*"👉 tutti gli altri eventi di oggi nelle storie"*). Il feed resta pulito, le storie sono il programma completo.
4. **Conflitto stesso giorno → cross-mention in caption, MAI spostare la data** (deciso 09/07).
   Il post che vince lo slot feed aggiunge una riga breve che segnala il secondo evento,
   rimandando alle storie: *"Inoltre oggi [Evento], guarda le storie per i dettagli."* Non è un
   anticipo (l'evento è di OGGI, non di giorni futuri) — serve solo a non perdere visibilità sul
   secondo evento importante. **Priorità nel conflitto**: gli eventi istituzionali / organizzati
   da enti pubblici hanno leggera precedenza sui contenuti privati (concerti, festival privati)
   quando comparabili; a parità decide Michele in approvazione.
5. **Niente anticipi multi-giorno per i grandi eventi.** Un grande nome fa **un solo post, il
   giorno dell'evento** (mai giorni prima). L'anticipo lo danno già settimanale e weekend — non
   servono moduli né trafiletti "fra X giorni c'è…" (sarebbe ridondante). Diverso dal
   cross-mention (regola 4), che è sempre e solo same-day.

### Parere SMM (best practice) sullo schema
1. **Separare le fasce (mattina singoli/storie · sera aggregati) è giusto**: due post feed a poche
   ore di distanza si cannibalizzano la reach (l'algoritmo IG tende a spingere solo il primo). La
   sera-prima evita la collisione; mattina + sera invece convivono bene.
2. **Le 18:00–20:00 sono il picco** per contenuto di "pianificazione". In particolare la **domenica
   sera** è il momento migliore per il "cosa fare questa settimana".
3. **Il weekend il giovedì** dà un giorno pieno di anticipo per organizzarsi.
4. **Slot fissi per tipo creano l'abitudine** nell'audience: la costanza vale più dell'orario perfetto.
5. Da testare più avanti coi **dati reali** (Insights IG): l'orario ottimale può spostarsi di 1–2 ore.

### Stories — programma completo giornaliero
Le stories contengono **tutti gli eventi del giorno**, grandi e piccoli (sagre, sport locale, concerti di nicchia).
Il post feed del giorno rimanda alle stories (*"per tutti gli eventi di oggi, guarda le stories"*).
Questo tiene il feed pulito e curato, mentre le stories fungono da programma completo della Repubblica.

### Grandi eventi → post singolo su feed · Piccoli eventi → stories o riepilogo
- **Grande** (post feed): concerti con nome noto, gare europee/nazionali, festival multi-giorno, eventi istituzionali rilevanti.
- **Piccolo** (stories o riepilogo weekend): rassegne di nicchia, feste di paese, sport locale, serie di concerti minori.

> **Un post feed ogni giorno, sempre** (deciso 15/07): ogni giorno con almeno un evento ha
> SEMPRE una riga **F**, mai solo **S**. 1 evento quel giorno → è lui il post feed (anche se
> "piccolo"). 2+ eventi senza nessuno "grande" → si sceglie comunque il più importante tra i
> disponibili come **F**, gli altri restano storie (con cross-mention se di calibro comparabile).
> Solo un giorno senza nessun evento verificato resta senza F. Corregge il caso del 15/07 (2
> eventi piccoli, entrambi finiti in storie, nessun post feed uscito quel giorno).

> **Ogni aggregato contiene TUTTI gli eventi del suo periodo, punto — mai togliere un evento
> perché "ha già un post suo"** (principio deciso 16/07, dopo l'errore sul weekend 18–19/07).
> Un evento con un post feed dedicato **resta comunque** nel weekend che lo contiene, nel
> settimanale che lo contiene, nel carosello mensile che lo contiene: sono livelli diversi
> (oggi / questo weekend / questa settimana / questo mese), non alternative tra cui scegliere
> uno solo. Ogni giorno ha il suo giornaliero (salvo i giorni davvero senza eventi), **ogni
> weekend ha i suoi appuntamenti — fossero anche uno solo**, ogni settimana ha i suoi eventi,
> ogni mese ha i suoi eventi: un evento compare tante volte quanti sono i livelli a cui
> appartiene, senza che questo sia "doppione" (la regola d'oro 1 già lo spiega: le fasce sono
> distanti nel tempo, non competono per la reach). **Caso reale che ha fatto scoprire
> l'errore**: il 12/07, sistemando il weekend 18–19/07 per correggere un riferimento a
> "stasera" ormai sbagliato (la pubblicazione era passata da venerdì a giovedì sera), è stata
> tolta l'INTERA riga di Le Vibrazioni (17/07) invece della sola parola "stasera" — motivato
> col fatto che quel venerdì aveva già il suo post feed. Pubblicato così su IG/FB il 16/07
> (non corretto perché già live). Verificato che settimanale e carosello non hanno mai
> applicato questa esclusione (contengono sempre anche gli eventi con post feed proprio,
> es. Le Vibrazioni è regolarmente nel settimanale 13–19/07) — è stato un errore isolato del
> weekend 18–19/07, non un pattern diffuso, ma la regola va tenuta esplicita per non
> ripeterlo su nessuno dei tre livelli.

---

## ⚠️ Post scaduti — da scartare
Questi 5 eventi sono già conclusi. Le bozze non si pubblicano; aggiornare stato a `scartato` nel master.

| # | Data evento | Titolo |
|---|-------------|--------|
| 01 | 28/06 | Abbronzatissima! — Concert Band |
| 02 | 28/06 | Aspettando Papa Leone — String Rolls |
| 03 | 28/06 | Note di Lavanda — Concerto d'arpa |
| 04 | 29/06 | Trenino Bianco Azzurro — Il Viaggio Riprende |
| 05 | 30/06 | P come Penelope — Paola Fresa |

> ✅ **Nota**: i vecchi ⚠️ "evento pubblicato dopo la data" (bozze 07, 18, 20) sono **risolti** dal
> nuovo schema: le storie escono ORA il giorno stesso dell'evento, non dopo.

---

## 📅 Calendario di pubblicazione — RIALLINEATO
Legenda: **F** = feed singolo (mattina 7:00) · **S** = storie (7:00) · **AGG** = aggregato (sera prima 18:00)

### Giugno 2026
| Data pub | G | Ora | Tipo | # | Contenuto | Data evento | Note |
|----------|---|-----|------|---|-----------|-------------|------|
| 30/06 | Mar | 18:00 | **AGG** | — | CAROSELLO Luglio | tutto luglio | Ultimo giorno di giugno → carosello del mese entrante |

### Luglio 2026
| Data pub | G | Ora | Tipo | # | Contenuto | Data evento | Note |
|----------|---|-----|------|---|-----------|-------------|------|
| 01/07 | Mer | 7:00 | **S** | 06 | Un Monte di Libri | 01/07 | Piccolo → storie |
| 02/07 | Gio | 18:00 | **AGG** | — | WEEKEND 03–05/07 | — | Copre Borgo in Festa, Vespa, Sfida per la Vittoria, Caputo, Galiazzo, Belli |
| 03/07 | Ven | 7:00 | **F** | 09 | Sergio Caputo — Tre Serate | 03/07 | Vince lo slot (Borgo in Festa non ha nome noto). **Cross-mention** in caption: "da oggi anche Borgo in Festa, guarda le storie". + storie: Sfida per la Vittoria, Conferenza Casali |
| 04/07 | Sab | 7:00 | **F** | 12 | Chiara Galiazzo — Tre Serate | 04/07 | Grande nome. + storie: Vespa Titano Day |
| 05/07 | Dom | 7:00 | **F** | 13 | Paolo Belli — Tre Serate | 05/07 | Grande nome (mattina) |
| 05/07 | Dom | 18:00 | **AGG** | — | SETTIMANALE 06–12/07 | — | Feed mattina + aggregato sera: ora si può |
| 07/07 | Mar | 7:00 | **F** | 15 | Tre Fiori vs Larne — UEFA | 07/07 | Sport europeo. + storie: UNESCO 18°, KMs of Resistance |
| 09/07 | Gio | 18:00 | **AGG** | — | WEEKEND 11–12/07 | — | Headline Symbol Remember |
| 09/07 | Gio | 7:00 | **S** | 16 | Chiringuito Faetano | 09/07 | Piccolo → storie |
| 10/07 | Ven | 7:00 | **F** | 17 | Sarah Toscano — Summer Vibes | 10/07 | Grande nome (era anticipato 09/07 → ora giorno stesso). + storie: La Favola di Francesco |
| 11/07 | Sab | 7:00 | **F** | 19 | Symbol Remember — 5ª ed. | 11–12/07 | Grande festival |
| 12/07 | Dom | 18:00 | **AGG** | — | SETTIMANALE 13–19/07 | — | |
| 13/07 | Lun | 7:00 | **S** | 20 | Rassegna Classica — Trio | 13/07 | Piccolo → storie |
| 14/07 | Mar | 7:00 | **F** | 22 | La Fiorita vs UNA Strassen — Conference | 14/07 | Sport europeo. + storie: Swing Concert Band |
| 15/07 | Mer | 7:00 | **F** | 23 | Armonie! Musica sacra del '600 | 15/07 | ⚠️ PROMOSSO 15/07 stessa mattina (regola "un feed sempre", eccezione: pubblicato in ritardo lo stesso giorno perché ancora in tempo). Scelto su 23b perché concerto con rassegna nominata (criterio POST SINGOLO) vs lettura per bambini senza artista nominato. Titolo corretto 11/07, ex "Pianoforte" |
| 15/07 | Mer | 7:00 | **S** | 23b | Un Monte di Libri — Domagnano | 15/07 | Piccolo → storie. Perde lo slot feed odierno a favore di 23 (Armonie) |
| 16/07 | Gio | 7:00 | **F** | 24 | Virtus vs Dila Gori — Conference | 16/07 | Sport europeo (mattina) |
| 16/07 | Gio | 18:00 | **AGG** | — | WEEKEND 18–19/07 | — | Rally + Armonie Barocca (era il "weekend 17/07 headline Le Vibrazioni"). ⚠️ **Pubblicato senza il venerdì 17/07 (Le Vibrazioni) — violava la regola weekend Ven+Sab+Dom, non corretto perché già uscito davvero su IG/FB il 16/07. Errore riconosciuto, non ripetere.** Anche uscito 11 ore prima del previsto (7:00 invece di 18:00) per un bug di `publish.py` che ignorava `ora_pubblicazione` — bug risolto lo stesso giorno |
| 17/07 | Ven | 7:00 | **F** | 25 | Le Vibrazioni — Summer Vibes | 17/07 | Grande nome, vince lo slot feed. + storie: Liscio for Dummies, Concerto della Banda Militare (25b — evento piccolo, conflitto risolto con cross-mention/storie, non sposta data — dec. Michele 11/07) |
| 18/07 | Sab | 7:00 | **F** | 28 | 25° Rally Bianco Azzurro | 18–19/07 | Evento grande. + storie: Armonie! Barocca |
| 19/07 | Dom | 7:00 | **F** | 18b | Titano Bears — Serie B recupero | 19/07 | ⚠️ PROMOSSO 15/07 (regola "un feed sempre"): unico evento del giorno, sale da storie a feed. Già compilato SOLO come storia in coda (`20260719_Storia`) → da rifare: nuovo testo post singolo (smh-testi) + nuova grafica F (smh-grafica) |
| 19/07 | Dom | 18:00 | **AGG** | — | SETTIMANALE 20–26/07 | — | |
| 21/07 | Mar | 7:00 | **F** | 29 | Rassegna Classica — Recital | 21/07 | ⚠️ PROMOSSO 15/07 (regola "un feed sempre"): unico evento del giorno, sale da storie a feed. Già compilato SOLO come storia in coda (`20260721_Storia`) → da rifare: nuovo testo post singolo (smh-testi) + nuova grafica F (smh-grafica) |
| 22/07 | Mer | 7:00 | **F** | 29a | Un Monte di Libri — Borgo Maggiore | 22/07 | ⚠️ PROMOSSO 15/07 (regola "un feed sempre"): unico evento del giorno, sale da storie a feed. Già compilato SOLO come storia in coda (`20260722_Storia`) → da rifare: nuovo testo post singolo (smh-testi) + nuova grafica F (smh-grafica) |
| 23/07 | Gio | 18:00 | **AGG** | — | WEEKEND 25–26/07 | — | Antiqua in corso + Baseball + Alba sul Monte |
| 24/07 | Ven | 7:00 | **F** | 31 | San Marino Antiqua 2026 | 24–26/07 | Grandissimo, apre oggi. Priorità istituzionale su Fred De Palma, stesso giorno (decisione Michele 09/07) |
| 24/07 | Ven | 7:00 | **S** | 30 | Fred De Palma — Summer Vibes | 24/07 | Perde lo slot feed → storie + **cross-mention** nella caption di Antiqua ("stasera anche Fred De Palma, guarda le storie") |
| 24/07 | Ven | 7:00 | **S** | arm-24-07 | Armonie! Viaggi e Intemperie da Bach agli Oasis | 24/07 | ⚠️ AGGIUNTO 14/07 (nuovo, approvato Michele via Telegram) — piccolo → storie; luogo non confermato dalla fonte |
| 25/07 | Sab | 7:00 | **F** | 31b | San Marino Baseball — doppio turno | 25/07 | ⚠️ PROMOSSO 15/07 (regola "un feed sempre"): unico evento del giorno, sale da storie a feed. Non ancora compilato in coda → nessun rifacimento necessario, basta produrlo direttamente come F |
| 26/07 | Dom | 7:00 | **S** | 32 | Alba sul Monte — lancio serie | 26/07–23/08 | ⚠️ AGGIORNATO 14/07: perde lo slot feed a favore di 33 (Tennis Open, stesso giorno d'apertura dopo la correzione data) → storie + **cross-mention** nella caption di 33. Scelta provvisoria dell'agente di approvazione (evento internazionale vs rassegna ricorrente locale) — da confermare/correggere con Michele |
| 26/07 | Dom | 18:00 | **AGG** | — | SETTIMANALE 27/07–02/08 | — | |
| 26/07 | Dom | 7:00 | **F** | 33 | San Marino Tennis Open — ATP Challenger 125 | 26/07–02/08 | ⚠️ AGGIORNATO 14/07: data d'inizio corretta 27/07→26/07 (fonte ufficiale sanmarinotennisopen.com, approvato Michele via Telegram) — ora coincide col lancio di Alba sul Monte (32); vince lo slot feed come evento top internazionale, cross-mention in caption verso Alba sul Monte |
| 29/07 | Mer | 7:00 | **F** | 31d | Un Monte di Libri — Serravalle | 29/07 | ⚠️ PROMOSSO 15/07 (regola "un feed sempre"): unico evento del giorno, sale da storie a feed. Già compilato SOLO come storia in coda (`20260729_Storia`) → da rifare: nuovo testo post singolo (smh-testi) + nuova grafica F (smh-grafica) |
| 30/07 | Gio | 18:00 | **AGG** | — | WEEKEND 01–02/08 | — | SMIAF + San Marino Revival |
| 31/07 | Ven | 7:00 | **F** | 34 | Cristiano Malgioglio & Angie | 31/07 | Grande nome (mattina). + storie: SMIAF apertura |
| 31/07 | Ven | 7:00 | **S** | bb-playoff | San Marino Baseball — Playoff quarti | 31/07 | ⚠️ AGGIUNTO 14/07 (nuovo, approvato Michele via Telegram, nonostante nota 06/07 "non rincorrere") — sport locale → storie |
| 31/07 | Ven | 18:00 | **AGG** | — | CAROSELLO Agosto | tutto agosto | Ultimo giorno di luglio → carosello del mese entrante. 🔴 **USCITO SOLO SU FACEBOOK**: Instagram ha rifiutato la caption (2407 caratteri, limite 2200 — errore 36004), 12 tentativi falliti in silenzio dal 31/07 al 02/08. Caption riscritta a 2166 caratteri (tutti i 29 eventi conservati) e busta rimessa al **03/08 ore 18:00** solo per IG; su FB non si ripubblica (chiave già in published.log). Guardia aggiunta a publish.py il 02/08 |

### Agosto 2026
| Data pub | G | Ora | Tipo | # | Contenuto | Data evento | Note |
|----------|---|-----|------|---|-----------|-------------|------|
| 01/08 | Sab | 7:00 | **F** | 36 | 33° San Marino Revival | 01–02/08 | ⚠️ PROMOSSO 15/07 (regola "un feed sempre"): unico evento del giorno, sale da storie a feed. Non ancora compilato in coda → nessun rifacimento necessario. + storie: SMIAF in corso |
| 02/08 | Dom | 18:00 | **AGG** | — | SETTIMANALE 03–09/08 | — | ⚠️ **SLOT PASSATO A VUOTO**: grafica compilata ed esportata il 30/07 (2 slide, 16 eventi) ma mai messa in coda — stesso schema del 28/07, un PNG esportato non è un post in coda. Recuperata la sera del 02/08 e messa al **03/08 ore 07:00** (1 giorno di ritardo, dentro la finestra di recupero) |
| 03/08 | Lun | 7:00 | **F** | 37 | Rassegna Classica — Duo | 03/08 | ⚠️ PROMOSSO 15/07 (regola "un feed sempre"): unico evento del giorno, sale da storie a feed. Non ancora compilato in coda → nessun rifacimento necessario |
| 05/08 | Mer | 7:00 | **F** | 37d | Quattrocelli 4ET | 05/08 | ⚠️ **SLOT FEED CAMBIATO 28/07** — il piano indicava qui "Un Monte di Libri — Fiorentino" (promosso 15/07 come unico evento del giorno). Poi il giro 27/07 ha verificato un secondo evento lo stesso giorno, **Quattrocelli 4ET** (Orti Borghesi 18:30, rassegna Summer Notes), che la grafica ha compilato come feed. In coda dal 28/07: **feed = Quattrocelli**, **storia = Un Monte di Libri** (`20260805_Storia`, già in coda). Il giorno è coperto da entrambi; se Michele preferisce invertirli va rifatta la grafica di entrambi |
| 06/08 | Gio | 18:00 | **AGG** | — | WEEKEND 08–09/08 | — | Greg, Jannacci, Cammino, Finardi |
| 06/08 | Gio | 7:00 | **F** | 38 | Maestri — Giuseppe Cederna TeatrOUT | 06/08 | ⚠️ PROMOSSO 15/07 (regola "un feed sempre"): unico evento del giorno, sale da storie a feed. Non ancora compilato in coda → nessun rifacimento necessario |
| 07/08 | Ven | 7:00 | **F** | 39 | Benji & Fede — Summer Vibes | 07/08 | Grande nome (era anticipato 04/08 → ora giorno stesso). + storie: Greg |
| 08/08 | Sab | 7:00 | **F** | 41 | Paolo Jannacci — Concert Band | 08/08 | Artista noto |
| 09/08 | Dom | 7:00 | **F** | 43 | Eugenio Finardi — Concert Band | 09/08 | Grande nome (mattina, era anticipato 06/08). + storie: Cammino Monte Titano |
| 09/08 | Dom | 18:00 | **AGG** | — | SETTIMANALE 10–16/08 | — | |
| 10/08 | Lun | 7:00 | **F** | 55 | "Concerto a Lume di Candela" — Da Bach ai Led Zeppelin | 10/08 | ⚠️ AGGIUNTO 04/08 (nuovo, approvato Michele via Telegram): non era nel piano. Unico evento del giorno, giorno stesso 7:00 come da regola standard |
| 12/08 | Mer | 7:00 | **F** | 12-08d | Dialogues — NMP Ensemble | 12/08 | ⚠️ AGGIUNTO 28/07: evento nuovo del giro 27/07 (rassegna "Castellaccio Vibra Musica"), non era nel piano. Compilato e messo in coda il 28/07 alla regola standard (giorno stesso, 7:00) |
| 13/08 | Gio | 7:00 | **F** | arm-13-08 | Armonie! Piano Time — Concerto con Orchestra | 13/08 | ⚠️ AGGIUNTO 14/07 (approvato Michele via Telegram). ⚠️ PROMOSSO 15/07 (regola "un feed sempre"): unico evento del giorno, sale da storie a feed. Non ancora compilato in coda → nessun rifacimento necessario |
| 13/08 | Gio | 18:00 | **AGG** | — | WEEKEND Ferragosto 15–16/08 | — | Headline Molella & Rosa Chemical |
| 14/08 | Ven | 7:00 | **F** | 44 | Molella & Rosa Chemical | 14/08 | Grande nome (era anticipato 13/08 → ora giorno stesso) |
| 15/08 | Sab | 7:00 | **S** | — | Ferragosto in Repubblica | 15/08 | ⚠️ NON PROMOSSO 15/07: la regola "un feed sempre" si applica solo a eventi verificati con dettagli reali — questa riga è un'etichetta generica senza # né dati verificati (luogo/ora/fonte), promuoverla a post singolo costringerebbe a inventare. Resta storia finché non emerge un evento specifico del 15/08 dal giro di ricerca/verifica; altrimenti segnalare a Michele prima di quella data |
| 16/08 | Dom | 7:00 | **F** | 16-08a | Alba sul Monte…in Concerto — "Trinaluna" | 16/08 | ⚠️ AGGIUNTO 28/07: serie "Alba sul Monte", non era nel piano come feed. Compilato e messo in coda il 28/07 (giorno stesso, 7:00). ⚠️ Il master cita un "Ad Parnassum" al 17/08 per la stessa serie — possibile scarto di un giorno fra le fonti, da ricontrollare a ridosso |
| 16/08 | Dom | 18:00 | **AGG** | — | SETTIMANALE 17–23/08 | — | Chiude con Tributo Battisti |
| 17/08 | Lun | 7:00 | **F** | 65 | Leone XIV visto da vicino — Un anno con Papa Prevost | 17/08 | ⚠️ AGGIUNTO 11/08 (catena, nuovo, approvato Michele via Telegram 10/08): non era nel piano. Unico evento verificato del giorno, giorno stesso 7:00 come da regola standard |
| 19/08 | Mer | 7:00 | **F** | 19-08a | Trio Mi Alma | 19/08 | ⚠️ AGGIUNTO 28/07: rassegna "Summer Notes" (ISM), non era nel piano. Compilato e messo in coda il 28/07 (giorno stesso, 7:00) |
| 21/08 | Ven | 7:00 | **F** | 66 | Trenino Bianco Azzurro | 21/08 (anche 22, 23, 28, 29/08) | ⚠️ AGGIUNTO 11/08 (catena, approvato Michele via Telegram 10/08): 3 eventi lo stesso giorno (Trenino, Sagra dell'Uva, Festa dell'Amicizia — righe master 66/69/70), il Trenino vince lo slot feed (bozza già scritta), gli altri due cross-mention + storia. 🔴 **Date corrette 17/08** (fonte diretta usc.sm, modifica approvata da Michele pulsante 20260817-0848-m1): non 14/08 (mai una data reale, già passata) — mancava tutto il weekend 28-29/08. PNG già esportato da ricompilare |
| 20/08 | Gio | 18:00 | **AGG** | — | WEEKEND 22–23/08 | — | Headline ora Visita pastorale di Papa Leone XIV (22/08) + Tributo Battisti (23/08) |
| 22/08 | Sab | 7:00 | **F** | 57 | 🎖️ Visita pastorale di Papa Leone XIV | 22/08 | ⚠️ AGGIUNTO 04/08 (nuovo, approvato Michele via Telegram): non era nel piano. Evento eccezionale (prima visita papale in 15 anni), vince lo slot feed del giorno senza discussione — giorno stesso 7:00 |
| 23/08 | Dom | 7:00 | **F** | 56c | San Marino Baseball vs Fortitudo Bologna — Semifinale gara 6 | 23/08 | ⚠️ AGGIORNATO 22/08 (decisione Michele in chat): priorità al baseball, gara decisiva (serie 3-2 per Bologna) — vince lo slot feed su Quel gran genio — Tributo a Battisti (riga 45), che resta comunque in storia (già presente nella storia doppia con Alba sul Monte) |
| 26/08 | Mer | 7:00 | **F** | 71 | Cena Tramonto & Live — Cena-Concerto di Beneficenza | 26/08 | ⚠️ AGGIUNTO 17/08 (catena, nuovo, approvato Michele via Telegram, pulsante 20260817-0848-n1): non era nel piano. Unico evento verificato del giorno, giorno stesso 7:00 come da regola standard |
| 27/08 | Gio | 7:00 | **F** | M09 | Giovedì in Centro | 27/08 | ⚠️ AGGIUNTO 22/08 (catena, approvato Michele via Telegram pulsante 20260821-1931-M09, 21/08 19:53 UTC): serie ricorrente, occorrenze 30/07·06/08·13/08 passate senza post dedicato, resta solo 27/08. Chiude il buco che c'era tra 26/08 e 28/08. Giorno stesso 7:00 come da regola standard |
| 28/08 | Ven | 7:00 | **F** | 46 | San Marino Comics 2026 | 28–30/08 | Già in coda (`posts/20260828_Post giornaliero.json`). + storia: Noche Argentina (riga master 46b) — ⚠️ AGGIUNTO 17/08 (catena, modificato/luogo corretto, approvato Michele via Telegram pulsante 20260817-0848-m2): storia mai compilata finora, la compila oggi la grafica col luogo corretto (Torraccia) |
| 29/08 | Sab | 7:00 | **F** | 29-08a | 21° Giro dei Castelli di San Marino | 29/08 | ⚠️ AGGIUNTO 28/07: non era nel piano. Vince lo slot feed del 29/08 su Cocktails Ronzanti e Piano-Malferrari (scelta confermata da Michele il 28/07) — gli altri due restano da fare come storie. + storia: Pellegrinaggio sui passi di San Marino e San Francesco (riga master 77) — ⚠️ AGGIUNTO 17/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260817-0848-d2) |
| 30/08 | Dom | 7:00 | **F** | 78 | Viaggio Musicale attorno al Mondo | 30/08 | ⚠️ AGGIUNTO 17/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260817-0848-d1): non era nel piano. Unico evento verificato del giorno, giorno stesso 7:00 come da regola standard. Sede esatta della rassegna "Macinare Cultura" da confermare |
| 31/08 | Lun | 7:00 | **F** | 79 | Calcio al Parco | 31/08 | ⚠️ AGGIUNTO 17/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260817-0848-d3): non era nel piano. Unico evento verificato del giorno. Bozza volutamente vaga (nessuna fonte diretta con luogo/orario) — da arricchire se esce una fonte prima della pubblicazione |

### Settembre 2026
> ⚠️ **Aggiunto 11/07/2026** (decisioni Michele via chat, pulsanti Telegram non disponibili) — prime righe oltre la finestra 28/06–23/08 originale. Il resto di settembre (weekend/settimanali/carosello) sarà completato quando la finestra dati coprirà tutto il mese, nel giro reale.

| Data pub | G | Ora | Tipo | # | Contenuto | Data evento | Note |
|----------|---|-----|------|---|-----------|-------------|------|
| 03/09 | Gio | 7:00 | **F** | 46d | Festa di San Marino — Anniversario fondazione | 03/09 | Evento nazionale, prioritario (nota Michele 11/07): in caso di conflitto stesso giorno con altri eventi ha la precedenza. Nessun altro evento verificato lo stesso giorno |
| 05/09 | Sab | 7:00 | **S** | 46e | Dal Turista al Contadino — 1° weekend | 05–06/09 | ⚠️ NON PROMOSSO 15/07: dati parziali (luogo e orari non specificati, fonte singola non confermata) — promuoverla a feed ora rischierebbe di pubblicare un post con buchi. **Confermato STORIA da Michele il 23/07** (il feed pronto avrebbe luogo/ora vuoti = post con buchi; la storia basta). Da rivalutare a ridosso: se emergono luogo/ora veri, promuovere a feed. ✅ **24/08: dubbio risolto** — fonte diretta usc.sm oggi mostra chiaramente questa prima tappa (5-6/09), che il 17/08 non compariva; Michele riapprovato (pulsante 20260824-0721-59), master riga 59 = `approvato`. Resta STORIA (ora ancora non specificata dalla fonte) |
| 09/09 | Mer | 7:00 | **F** | 80 | Serravalle in Wellness — Settembre 2026 | 09, 16, 23, 30/09 | 🆕 AGGIUNTO 24/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260824-0721-80): unico evento verificato del giorno. Un post solo copre l'intera serie (4 mercoledì, punto di partenza diverso ogni settimana — vedi caption); le occorrenze successive (16,23,30/09) non hanno un post dedicato, coperte dal rimando nella caption |
| 11/09 | Ven | 7:00 | **F** | 46f | Gran Premio Red Bull MotoGP San Marino | 11–13/09 | ⚠️ AGGIUNTO 23/07 (decisione Michele): messo in coda anche se settembre non era ancora nel piano. Grande evento sportivo internazionale (gara Dom 13/09 ore 14:00, Misano World Circuit). **Da ri-verificare a ridosso** (orari/programma) |
| 12/09 | Sab | 7:00 | **F** | 72 | SanMarinoBeerFest — Love Generation 90 (DJ set anni 90) | 12/09 | ⚠️ AGGIUNTO 17/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260816-1750-01): non era nel piano, prende lo slot feed (era vuoto). + storia: Dal Turista al Contadino 2° weekend (12-13/09, riga sotto) |
| 12/09 | Sab | 7:00 | **S** | 46e | Dal Turista al Contadino — 2° weekend | 12–13/09 | Idem sopra (dati parziali, non promossa) — oltre la finestra standard 60gg ma incluso su decisione esplicita di Michele (11/07). 🔴 **24/08: luogo corretto** — due sedi confermate (Via Eugippo + Piazza Mercatale, Borgo Maggiore), non solo Via Eugippo; testo storia aggiornato in `post-2026-08-03.md`; Michele riapprovato (pulsante 20260824-0721-60), master riga 60 = `approvato` |
| 13/09 | Dom | 7:00 | **F** | 81 | 36° Palio Don Bosco | 13/09 | 🆕 AGGIUNTO 24/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260824-0721-81): unico evento verificato del giorno (gara MotoGP già pubblicata l'11/09). Organizzatore non specificato dalla fonte — nessun tag |
| 15/09 | Mar | 7:00 | **F** | 15-09a | 11º Concorso Internazionale di Canto Renata Tebaldi | 15–18/09 | ⚠️ AGGIUNTO 28/07: evento nuovo del giro 27/07, non era nel piano. Teatro Concordia (Borgo Maggiore), ora non specificata. Messo in coda il 28/07 (giorno stesso, 7:00), tag @sanmarinoteatro. **Da ri-verificare a ridosso** (orari/programma) |
| 18/09 | Ven | 7:00 | **F** | 46g | Sport in Fiera 2026 — CONS | 18–20/09 | ⚠️ AGGIUNTO 23/07 (decisione Michele): messo in coda anche se settembre non era ancora nel piano. Rassegna sportiva CONS, Centro Sportivo di Serravalle, ora non specificata (nessuna fonte 2026 affidabile). **Da ri-verificare a ridosso** (orari/programma) |
| 19/09 | Sab | 7:00 | **F** | 19-09a | 36° Gran Premio Nuvolari | 19/09 | ⚠️ AGGIUNTO 28/07: evento nuovo del giro 27/07, non era nel piano. Luogo generico "San Marino" (percorso su strade della Repubblica), ora non specificata. Messo in coda il 28/07 (giorno stesso, 7:00). **Da ri-verificare a ridosso** (orari/percorso) |
| 19/09 | Sab | 7:00 | **S** | 82 | San Marino Special Cup 2026 | 19-20/09 | 🆕 AGGIUNTO 24/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260824-0721-82): 19/09 e 20/09 già occupati da post feed (Nuvolari, Sport in Fiera) — regola conflitto stesso giorno: solo storia, mai un secondo post feed. Cross-mention aggiunta alla caption già in coda di `posts/20260919_Post giornaliero.json` |
| 25/09 | Ven | 7:00 | **F** | 73 | SanMarinoBeerFest — Nirvana.it (Nirvana Tribute) | 25/09 | ⚠️ AGGIUNTO 17/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260816-1750-02): non era nel piano, unico evento verificato del giorno |
| 26/09 | Sab | 7:00 | **F** | 74 | SanMarinoBeerFest — Dicono di Cesare (Cesare Cremonini Tribute) | 26/09 | ⚠️ AGGIUNTO 17/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260816-1750-03): non era nel piano. Anche "Artisti in Casa" (riga 61 master) cade il 26-27/09 — da verificare eventuale conflitto a ridosso |

### Ottobre 2026
> ⚠️ **Aggiunto 11/08/2026** (catena, Step 1 approvazioni) — prime righe di ottobre, approvate da Michele via Telegram il 10/08. Il resto di ottobre sarà completato quando la finestra dati lo coprirà nel giro reale.

| Data pub | G | Ora | Tipo | # | Contenuto | Data evento | Note |
|----------|---|-----|------|---|-----------|-------------|------|
| 02/10 | Ven | 7:00 | **F** | 75 | SanMarinoBeerFest — Floyd Academy (Pink Floyd Tribute) | 02/10 | ⚠️ AGGIUNTO 17/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260816-1750-04): non era nel piano, unico evento verificato del giorno |
| 03/10 | Sab | 7:00 | **F** | 76 | SanMarinoBeerFest — Voglio Tornare Negli Anni 90 | 03/10 | ⚠️ AGGIUNTO 17/08 (catena, nuovo, approvato Michele via Telegram pulsante 20260816-1750-05): non era nel piano, unico evento verificato del giorno |
| 07/10 | Mer | 7:00 | **F** | 67 | Sal Da Vinci — "Dalla parte del cuore" | 07/10 | ⚠️ AGGIUNTO 11/08: evento nuovo, non era nel piano. Unico evento verificato del giorno, giorno stesso 7:00. **Da ri-verificare a ridosso** |
| 08/10 | Gio | 7:00 | **F** | 68 | Rallylegend 2026 | 08–11/10 | ⚠️ AGGIUNTO 11/08: evento nuovo, non era nel piano. Multi-giorno: pubblicato il primo giorno (come San Marino Comics, riga 46). **Da ri-verificare a ridosso** (orario non ancora pubblicato dalla fonte) |

---

## 📊 Riepilogo (dopo il riallineo del 09/07 — seconda passata)
| Categoria | Conteggio |
|-----------|-----------|
| Post scaduti (da scartare) | 5 (01–05) |
| Post feed singoli (F) | 30 (20 +1 Festa di San Marino 03/09, aggiunta 11/07, +10 promosse 15/07 da storie a feed: 19/07, 21/07, 22/07, 25/07, 29/07, 01/08, 03/08, 05/08, 06/08, 13/08) |
| Post solo storie (S) | 8 (18 − 10 promosse 15/07) — restano Ferragosto 15/08 e le 2 date di Dal Turista al Contadino (dati parziali, non promosse) + tutti gli eventi minori del giorno |
| Aggregati: caroselli | 2 — SOLO mesi completi (Luglio pub 30/06, Agosto pub 31/07). Settembre non ancora coperto (finestra dati parziale) |
| Aggregati: settimanali | 7 (le domeniche 05/07 → 16/08) |
| Aggregati: weekend | 8 (i giovedì 02/07 → 20/08) |
| Aggregati: bisettimanali | **0 — sospesi** |
| Non in piano (evento troppo vicino) | 2 — Finale Tiro con la Balestra e Three Kings Classic (entrambi 11/07, approvati solo a registro master, non pubblicabili in tempo) |

### Cosa è cambiato col riallineo (09/07, seconda passata)
1. **Aggregati spostati alla sera-prima 18:00**: settimanale ora **domenica** (era lunedì), weekend ora **giovedì** (era venerdì), carosello **ultimo giorno del mese prima** (era il 1°/15).
2. **Bisettimanali sospesi** (4 post): bozze archiviate in `aggregati-luglio-agosto-2026.md`, non in calendario.
3. **Grandi eventi sul giorno reale** (mai anticipi multi-giorno): Sarah Toscano, ATP, Benji&Fede, Molella, Battisti, ecc.
4. **Caroselli: solo mesi completi.** Restano SOLO Luglio e Agosto (mese pieno). Le bozze ibride
   "Agosto+Settembre" e "Fine estate" sono state **eliminate** dal file bozze aggregati (non solo
   archiviate) — erano parziali/ridondanti. Settembre avrà il suo carosello quando la finestra dati
   coprirà tutto il mese (nel giro reale, a fine agosto).
5. **Borgo in Festa resta candidato al feed** (non è degradato a priori): in questa finestra perde
   comunque tutti i suoi 3 giorni (03–05/07) perché ci sono concerti con nome noto — va in
   storie + weekend + **cross-mention** nella caption del 03/07 (giorno di apertura).
6. **Conflitto 24/07** (Fred De Palma vs San Marino Antiqua): **nessuna data spostata** (era un
   errore della prima passata). Antiqua vince lo slot feed il 24/07 — giorno reale di apertura —
   per priorità istituzionale; Fred De Palma va in storie lo stesso giorno con cross-mention nella
   caption di Antiqua.
7. **Nuova regola generale**: conflitto stesso giorno tra due eventi di calibro → si risolve SEMPRE
   con **cross-mention in caption**, mai spostando la data. Vedi "Regole d'oro" n.4.
8. **Aggiornamento 11/07/2026** (approvazioni via chat, pulsanti Telegram non disponibili): +Festa di
   San Marino (03/09, F, prioritaria) e +Dal Turista al Contadino (05–06/09 e 12–13/09, S, entrambi
   weekend) in una nuova sezione Settembre; +4 righe S per "Un Monte di Libri" (15/07, 22/07, 29/07,
   05/08); Concerto della Banda Militare (17/07) risolto come "piccolo" → storie, cross-mention nella
   nota del feed di Le Vibrazioni (stesso giorno). Finale Tiro con la Balestra e Three Kings Classic
   (entrambi 11/07) restano FUORI dal piano: eventi della sera stessa, non pubblicabili in tempo.
9. **Aggiornamento 15/07/2026** — nuova regola "un post feed ogni giorno, sempre" (vedi sezione
   "Grandi eventi → post singolo su feed", causata dal 15/07 stesso: 2 eventi piccoli, entrambi
   finiti in storie, nessun post feed uscito). Applicata retroattivamente a tutti i giorni futuri
   non ancora pubblicati con solo storie: 10 righe promosse S→F (19/07, 21/07, 22/07, 25/07,
   29/07, 01/08, 03/08, 05/08, 06/08, 13/08). **7 di queste erano già compilate SOLO come storia
   in coda GitHub** (19/07, 21/07, 22/07, 29/07, 05/08 — vedi note riga) e vanno rifatte con
   smh-testi + smh-grafica prima della loro data di pubblicazione. **3 righe NON promosse**
   nonostante fossero le uniche del giorno, perché mancano dati verificati sufficienti per un
   post singolo senza inventare: Ferragosto in Repubblica (15/08, etichetta generica senza
   fonte) e Dal Turista al Contadino (05/09, 12/09, dati parziali) — da rivalutare quando
   arrivano dati più solidi, altrimenti restano storie. 15/07 stesso NON è stato corretto
   retroattivamente: è già pubblicato, non si tocca il passato.

---

## ✅ Prossimi passi

1. **Claude**: quando parte il run vero, `smh-pubblica` legge la colonna "Data pub" da questa tabella.
2. **Fase futura**: rivalutare gli orari con gli Insights IG reali; decidere se riattivare i bisettimanali.
3. **Aperto (09/07)**: policy di pulizia/archiviazione dei contenuti vecchi (Canva, repo GitHub,
   file bozze) — solo discusso, non deciso. Vedi memoria `project_pulizia_contenuti_vecchi`.
