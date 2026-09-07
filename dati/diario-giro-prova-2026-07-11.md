# Diario intoppi — Giro di prova end-to-end (Sessione 6, 11/07/2026)

Giro completo in SIMULAZIONE sui dati veri: /smh-giro → approvazione → grafica → coda → messaggi 🧪.
Ogni attrito registrato qui: dove, cosa, gravità (🔴 blocca il LIVE · 🟡 fastidio · 🟢 cosmetico), proposta fix.
Le proposte NON vengono applicate in questa sessione — si decide insieme alla fine.

## Pre-checks (prima del giro)

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| P1 | Mac / strumenti | `gh` CLI non installato: impossibile interrogare GitHub comodamente da locale | 🟢 | Opzionale: `brew install gh` oppure continuare con `curl` + PAT |
| P2 | Verifica PUBLISH_LIVE da locale | Il PAT nel portachiavi (Contents+Workflows) non ha lo scope **Actions: read** → la Variable `PUBLISH_LIVE` non è verificabile dal Mac. Confermata spenta solo indirettamente (test 🧪 Sessione 4 di oggi) | 🟡 | O estendere il PAT con Actions:read, o accettare la verifica manuale su github.com prima di ogni decisione delicata |
| P3 | Coda `posts/` | La busta **Sarah Toscano** (`data_pubblicazione: 2026-07-10`) è ancora in coda: in simulazione non si archivia mai (comportamento atteso). Il 12/07 ha generato 4 riannunci 🧪 (7:02 e 18:01 puntuali cron-job.org + 12:26 e 21:56 cron interni in ritardo = rete di sicurezza OK) che hanno confuso Michele | 🟡 | ✅ RISOLTO 12/07 sera: busta archiviata in `archivio/2026-07/` (commit `857b0a5`) — niente più rumore, LIVE al sicuro. Lezione: il messaggio 🧪 potrebbe dire "già annunciata N volte" per ridurre la confusione |

## Anello 1-3 — /smh-giro (ricerca → verifica → testi)

**Ricerca (11/07, ~7 min):** OK — 36 eventi (31 verificabili, 5 ⚠️), file `dati/eventi/eventi-2026-07-11.md`. Sport 8 · Musica 14 · Cultura 6 · Sociale 3 · Istituzionale 1 · Altro 4.

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| R1 | Ricerca / fonti | `giornalesm.com` irraggiungibile (socket error WebFetch) | 🟡 | Se persiste al prossimo giro → marcare ⚠️ in fonti.md come da protocollo; per ora tenuta |
| R2 | Ricerca / fonti | `fibs.it` (baseball) non leggibile dai bot (JavaScript) → i match in casa del Serravalle restano un controllo MANUALE di Michele su Facebook | 🟡 | Già noto (task #3 in ULTIMO_REPORT). Alternativa futura: pagina FB del club via browser |

**Verifica (11/07, ~19 min):** OK — 29 verificati (24 invariati + 4 🆕 + 1 ✏️), 8 ⚠️ da-confermare-Michele, 4 scartati. File `dati/eventi/verificati/eventi-verificati-2026-07-11.md`. La verifica ha lavorato bene: ha smascherato fonti con contenuti residui 2024/2025 e corretto un refuso della fonte ("giugno" → luglio, incrociando i giorni della settimana).

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| V1 | Ricerca → Verifica | La ricerca ha pescato **fonti di edizioni vecchie** (giornalesm 2025 per Classica Giovani; sanmarinortv con residui 2024 per Un Monte di Libri e Cinema nei Castelli) → 4-5 dubbi ⚠️ generati da fonti stantie, non da eventi veri. La verifica li ha catturati tutti (rete funziona), ma il carico dubbi per Michele si gonfia | 🟡 | In smh-ricerca: quando l'articolo ha una data di pubblicazione di un anno precedente, marcarlo subito ⚠️-fonte-vecchia senza estrarre l'evento |
| V2 | Tempistica giro | Eventi scoperti il giorno stesso (Finale Balestra 11/07 ore 21:30, Three Kings 09–11/07) **non sono pubblicabili in tempo** con la cadenza settimanale lun→mar: quando arriva l'approvazione (martedì) l'evento è già passato | 🟡 | Accettarlo (il giro trova, il piano editoriale filtra) oppure valutare in futuro un giro a cadenza più fitta; NON è un bug del giro |
| V3 | Verifica / dubbi | 8 dubbi su 13 eventi segnalati = il grosso del lavoro di Michele su Telegram sarà sciogliere dubbi, non approvare novità | 🟢 | Fisiologico per un giro su dati veri d'estate; da rivalutare dopo 2-3 giri |

**Testi (11/07, ~18 min):** OK — 29 bozze + 29 testi storia in `dati/post/post-2026-07-11.md` (19 singoli, 1 solo-storia per cross-mention Fred De Palma/Antiqua, 2 riepiloghi tematici da 9 eventi minori). Nessun dato inventato (4 descrizioni storia = "non specificato"). Conflitti stesso giorno segnalati in nota, non arbitrati.

**Telegram (Step 4):** OK — riepilogo + 5 messaggi a blocchi con pulsanti ✅/❌, 13 eventi in `pending_events`. Zero errori di invio.

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| T1 | Verifica → Giro (ID eventi) | Il riassunto della verifica NON riporta ID; le bozze di smh-testi NON sono numerate. La skill del giro chiede `id` = "N° bozza o ID master" ma nessuno dei due esiste → l'orchestratore ha dovuto inventarsi lo schema (01–13 progressivi). Funziona (il matching poi è per titolo via pending_events), ma è un punto ambiguo a ogni giro | 🟡 | Formalizzare nello skill smh-verifica: il riassunto strutturato assegna gli ID progressivi lui stesso, e il giro li riusa |
| T2 | Testi (doppioni) | smh-testi ha riscritto le bozze anche per i 24 eventi INVARIATI già approvati in bozze precedenti (post-2026-06-28.md) → ora esistono 2 versioni della stessa bozza (una `approvato` vecchia, una `da-approvare` nuova). Rischio confusione per grafica/archivio + lavoro/token inutili (~29 bozze scritte per 13 eventi in ballo) | 🟡 | smh-testi scrive bozze solo per eventi 🆕/✏️ e per quelli SENZA bozza esistente; per gli invariati rimanda alla bozza già approvata |
| T3 | Verifica (valore!) | Non un intoppo, il contrario: la verifica ha scoperto che 2 post GIÀ APPROVATI (Trio Shelak 13/07, Stefanelli & Pantani 03/08) potrebbero avere la data sbagliata (fonte era edizione 2025) → dubbi girati a Michele coi pulsanti | 🟢 | Nessun fix: la rete di sicurezza funziona |
| T4 | Skill smh-giro (testo) | La skill dice ancora "dillo chiaramente nell'email" (Step 1/2) ma lo Step 4 è ormai Telegram; anche CLAUDE.md parla di "bozza email di riepilogo". Residuo della versione vecchia → ambiguo per un esecutore futuro | 🟢 | Allineare il testo della skill (email → Telegram) |
| T5 | Skill smh-giro (Google Sheet) | La skill chiede di creare un nuovo Sheet calendario "quando il giro produce dati sufficienti", ma i nuovi eventi entrano nel master solo DOPO l'approvazione (anello 4) → momento giusto ambiguo. In questo giro: rimandato a dopo l'approvazione | 🟢 | Spostare l'istruzione Sheet dentro smh-approvazione (o chiarire "dopo l'approvazione") |

## Anello 4 — /smh-approvazione

**Risposte parziali di Michele (11/07, via CHAT, non Telegram):** dubbi 06/07/10 risolti con dati ufficiali (programma Classica Giovani 2026 + locandina Un Monte di Libri). 4 date future di Un Monte di Libri inserite nei verificati via smh-aggiungi (test riuscito del canale manuale). Correzioni applicate a verificati + bozze + master. Restano in attesa: 01–05 (nuovi/modificato) e 08, 09, 11, 12, 13 (dubbi).

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| A1 | Ricerca→Verifica→Testi (contaminazione) | Un evento VERIFICATO portava l'artista dell'edizione 2025: "Michele Castaldo" al posto del recital di **Gianluca Bergamasco** (21/07). La verifica l'ha marcato INVARIATO confrontando solo data+luogo col master (che ha titolo generico "Recital") — il nome sbagliato è passato fino alla bozza e al testo storia. Scoperto SOLO grazie al programma ufficiale fornito da Michele. Se approvato alla cieca, sarebbe finito in grafica con l'artista sbagliato | 🔴 | smh-verifica: quando marca INVARIATO, confrontare anche il TITOLO/artista col master; se la fonte aggiunge dettagli che il master non ha (es. un nome proprio), declassare a dubbio ⚠️. In generale: articolo con data pubblicazione di un anno precedente = mai fonte per dettagli |
| A2 | Protocollo approvazione | Michele ha risposto in CHAT (problemi coi link Telegram dal telefono), canale non previsto: `pending_events` resta aperto per 06/07/10 e l'orchestratore ha dovuto improvvisare (edit manuali + istruzioni extra da passare a smh-approvazione). Il protocollo conosce solo Telegram | 🟡 | Prevedere nella skill smh-approvazione l'input "decisioni comunicate in chat/sessione" oltre ai callback Telegram; oppure regola semplice: le risposte in chat le processa l'orchestratore e le marca in pending_events |
| A3 | Telegram su telefono | Michele segnala "problemi col telefono" sui messaggi coi link/pulsanti (da caratterizzare: link non apribili? messaggi tagliati?) | 🟡 | Chiedere a Michele il sintomo esatto; eventualmente accorciare i messaggi (blocchi da 3 → 1 evento per messaggio) o mettere gli URL su riga propria |
| A4 | Fonti (scoperta utile) | La pagina evento visitsanmarino in formato `pub2/…/en/evento/….html` È leggibile via WebFetch (contenuto completo), mentre le pagine `pub1/…/it/` risultano vuote (JavaScript). Trovata conferma indipendente per Classica Giovani 03/08 | 🟢 | Annotare in `dati/fonti.md`: per visitsanmarino provare la variante `pub2/…/en/` degli URL evento |
| A5 | Canale smh-aggiungi | Test positivo: locandina → 4 blocchi verificati formattati correttamente, zero attriti | 🟢 | Nessun fix |

**Secondo blocco risposte Michele (11/07, chat):** comunicato ufficiale Armonie! 2026 → dubbi **08/09/11 SCARTATI** (la VI edizione ha solo 3 appuntamenti: 27/06 passato, 15/07, 18/07 — quei concerti erano residui di edizioni precedenti).

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| A6 | Dati storici (contaminazione 2ª) | Il titolo del 15/07 era sbagliato FIN DALL'ORIGINE: "Armonie! Pianoforte" nel master/bozza 23 nasceva da un articolo di un ALTRO evento (chiusura rassegna di primavera); la ricerca di oggi ci ha sovrapposto "Piano Time (Malferrari)" che è l'APERTURA del 27/06. Titolo giusto: **"Musica sacra del '600 italiano"** (Chiesa di Sant'Antimo, ore 18). Corretto in 7 punti: verificati, bozza nuova + riepilogo, bozza vecchia 23, master, piano editoriale, aggregati (carosello+caption) | 🔴 | Stesso fix di A1 (confronto titoli) + regola: un titolo con nome proprio/genere musicale deve avere una fonte che lo dica per QUELL'edizione |
| A7 | Carosello Luglio v2 (post di lancio!) | La slide Settimana 3 del carosello GIÀ ESPORTATO (copia `DAHPEeibRG0`, PNG in 5 Mensili/) mostra "Armonie! Pianoforte" → titolo sbagliato nel post di lancio. Da correggere su Canva + RIESPORTARE il PNG (regola feedback_export_riesporta) | 🔴 | Correzione da fare nella fase grafica di questo giro, col «procedi» di Michele — PRIMA del LIVE |
| A8 | Input umano (lezione) | Anche le fonti di Michele possono essere stantie: la locandina Armonie! fornita diceva "27 luglio ore 21:15" (altra edizione) mentre il comunicato 2026 dice "sabato 27 giugno ore 21:00". Smascherato con Python (27/06/2026 = sabato ✓, 27/07/2026 = lunedì ✗) + articolo libertas datato 26/06/2026 | 🟢 | La regola "incrocia 2 fonti + giorno in Python" va applicata anche agli input manuali — ha funzionato |

**Terzo blocco (11/07):** screenshot pagina USC → 01 Finale Balestra confermato + arricchito (ora esatta 21:30, gratuito, descrizione storia riempita); 13 Torneo della Libertà risolto = dentro Antiqua (master 31c aggiornato). Resta da decifrare il riferimento di Michele a un "27 luglio".

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| A9 | Telegram (canale approvazione) | Michele CREDEVA di aver risposto coi pulsanti, ma nella coda del bot c'è UN solo messaggio di testo e **zero callback**: i tap si sono persi (problemi di rete/telefono). In produzione = approvazioni ferme in silenzio fino al check del martedì, senza che nessuno se ne accorga | 🔴 | (1) nel riepilogo Telegram chiedere una conferma finale esplicita ("quando hai finito scrivi FATTO") così la mancanza si vede; (2) smh-approvazione: se 0 risposte ma pending aperti da >2 giorni → sollecito automatico con lista di ciò che manca; (3) i pulsanti già premuti dovrebbero ricevere l'answerCallbackQuery "Ricevuto ✅" — se Michele non vede la conferma, il tap non è arrivato (da spiegargli come segnale) |

**Esito anello 4 (11/07):** ✅ COMPLETATO — 13/13 decisioni (10 approvate di cui 2 non pubblicabili per tempo, 3 scartate). Le decisioni sono passate TUTTE via chat (canale d'emergenza) e l'agente approvazione le ha formalizzate: master +9 righe, Rally riga 28 aggiornata, 5 bozze nuove (4 Monte di Libri + Dal Turista), piano editoriale con sezione Settembre, aggregati aggiornati, `post-approvati-2026-07-11.md` creato, telegram-state ripulito (update 728087660 consumato, pending svuotati), conferma Telegram inviata.

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| A10 | Approvazione → bozze collegate | La cross-mention 17/07 (Le Vibrazioni feed ↔ Banda Militare storie) è documentata nel piano ma la CAPTION di Le Vibrazioni (bozza vecchia) non è stata aggiornata: nessun anello "possiede" l'aggiornamento delle bozze già approvate quando un nuovo evento crea un conflitto | 🟡 | Aggiungere allo Step 6 di smh-approvazione: se un nuovo evento crea un conflitto stesso-giorno, aggiorna anche la caption del post feed esistente con la cross-mention |
| A11 | Approvazione (classificazione) | "Dal Turista al Contadino" classificato storie-non-feed per analogia (Michele non l'ha specificato) — inferenza segnalata onestamente dall'agente nel piano | 🟢 | Sta a Michele confermare o correggere; il default conservativo ha funzionato |

## Anello 5 — /smh-grafica

**Esito FASE 1 (11/07 sera):** ✅ COMPLETATA, con un incidente grave a metà. Compilati (NON esportati): fix carosello Luglio (DAHPEeibRG0, Settimana 3 → "Armonie! Musica sacra del '600") · settimanale 13–19/07 (DAHPHXhygso pag. 2, 8 eventi) · weekend 18–19/07 (DAHPHRDHg5c pag. 1, compattato) · giornaliero Rally (DAHOLS6Zdpw pag. 1) · storie 15/07 (DAHPHW6lO3k) · storie 17/07 (DAHPHYVIcOQ, completate dall'orchestratore dopo il crash). Stato salvato in grafica-stato.json → `in_attesa_conferma`.

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| G1 | Infrastruttura sessioni | Il **limite dell'account Claude** ha ucciso l'agente grafica a metà FASE 1 e ne ha CANCELLATO il transcript: report perso, grafica-stato.json non aggiornato (il salvataggio era il task finale). L'orchestratore ha dovuto ricostruire lo stato ispezionando Canva (search-designs + contenuti + render) e finire a mano le storie 17/07. In un giro automatico del lunedì questo = catena ferma in silenzio con lavoro orfano su Canva | 🔴 | (1) smh-grafica deve aggiornare grafica-stato.json **DOPO OGNI PEZZO**, non alla fine; (2) riepilogo FASE 1 scritto su file man mano (append), non solo in chat; (3) lanciare i giri lunghi lontano dai limiti (o spezzare la FASE 1 in più batch) |
| G2 | Testi/Verifica (giorni settimana) | La bozza Rally diceva "shakedown **venerdì** 18… power stage **sabato** 19" ma 18/07=SABATO e 19/07=DOMENICA (fonte: "sabato 18 e domenica 19"). Giorni DEDOTTI e sbagliati in 3 file (verificati, bozze, approvati) — la regola giorno-in-Python esiste solo per la grafica; i testi scrivono i giorni senza calcolo. La grafica (Sab-Dom) era giusta; corretti i 3 file | 🟡 | Estendere la regola Python a smh-verifica e smh-testi: ogni nome di giorno scritto in un testo va calcolato, mai copiato/dedotto |
| G3 | Validazione (metodo) | Due FALSI ALLARMI da lettura solo-testo: le "righe residue" del weekend erano sulle pagine 2-4 non usate della copia (pag. 1 perfetta), e "Rally BiancoAzzurro" era solo l'a-capo del dump testuale. Il render (thumbnail) ha smentito entrambi | 🟢 | La validazione al contrario va fatta anche sul RENDER, non solo sul testo estratto (già prassi della skill: ribadire) |
| G4 | Export (doppione Rally) | Esistono 2 grafiche Rally: pag. 10 (batch 02/07, GIÀ ESPORTATA come 20260718_Post giornaliero.png, dati superati "San Marino / Tutto il giorno") e pag. 1 (nuova, corretta: Sab-Dom 18-19, Montegiardino, dalle 19:49). Se non si sovrascrive, il robot pubblicherebbe il PNG vecchio | 🟡 | All'export FASE 2: esportare pag. 1 SOVRASCRIVENDO 20260718_Post giornaliero.png (regola feedback_export_riesporta) |
| G5 | Coerenza luogo breve Rally | Prodotti diversi mostrano luoghi diversi: carosello Luglio = "Serravalle", settimanale/weekend/giornaliero = "Montegiardino" (traguardo, dato nuovo). Non è un errore (assistenza a Rovereta/Serravalle), ma nel feed usciranno vicini | 🟢 | Decisione Michele al checkpoint: uniformare (=altra correzione carosello) o lasciare così |
| G6 | Storie (font titoli) | I titoli storia lunghi al font del template vanno su 4 righe e COPRONO la descrizione (visto su Banda Militare e Le Vibrazioni): il template non ha auto-fit. Risolto a 64pt fisso sulle 2 storie del 17/07 | 🟡 | Aggiungere alla skill smh-grafica (sez. Storie): controllo altezza titolo post-compilazione (box ≤3 righe / niente overlap col blocco descrizione), riducendo il font a passi di 1pt |
| G7 | Storie (copertura) | "Liscio for Dummies" (17/07, TeatrOUT, master 26) resta SENZA storia: è del batch vecchio e non ha box 📱 in nessun file di oggi → la giornata del 17/07 avrà 2 storie su 3 eventi | 🟡 | Decidere: o smh-testi genera i box storia anche per gli eventi vecchi ancora futuri (una tantum), o si accetta la copertura parziale fino a esaurimento del batch pre-storie |

**Revisione checkpoint di Michele (12/07):** carosello/weekend/giornaliero OK · settimanale: trovata linea divisoria ORFANA sotto l'ultimo evento di pag. 2 (+ righe vuote penzolanti su pag. 4 residua) → rimosse e salvate · storie: segnalate le "righe bianche di limite" non eliminate.

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| G8 | Canva MCP (storie) | Le **righe bianche di limite** sui template storie NON sono eliminabili dal robot: l'API Canva non le espone tra gli elementi (vede solo testi, sfondo, divisore header e logo) → ogni compilazione storie richiederebbe una pulizia manuale di Michele | 🟡 | Rimuoverle UNA VOLTA dal master `SMH - Storie` (DAHOdNq0R58) a mano: le copie future nasceranno pulite. Per questo giro: rimozione manuale sulle 2 copie |
| G9 | Orchestratore (mea culpa) | Ho dichiarato il settimanale "validato — perfetto" SENZA averne letto davvero il contenuto (l'ho letto solo dopo): la linea orfana l'ha trovata Michele al checkpoint. La validazione al contrario era saltata proprio sul pezzo che lo richiedeva | 🔴 | La regola c'era già (skill riga 171: "controlla via thumbnail che non resti una linea orfana... sotto l'ultimo evento"): va eseguita SEMPRE, su OGNI pezzo, con evidenza (render+contenuto), mai dichiarata senza averla fatta. Il checkpoint umano ha funzionato da rete |
| G10 | Master settimanale (igiene) | Il master `SMH - Settimanale` ha ancora i DATI del vecchio test sulle sue 4 pagine (settimane 6-12/07, 20-26/07, 27/07-02/08, con righe vuote e persino un evento mai entrato nel master come "Fast & Caratelle") → ogni copia nasce sporca e confonde la revisione | 🟡 | Riportare il master a stato di TEMPLATE pulito (righe segnaposto), manualmente o in una sessione dedicata; probabile stesso problema sugli altri master |

**FASE 2 export (12/07 ~22:20, dopo «procedi»):** ✅ 8 PNG pro esportati e verificati a vista (storie PULITE — Michele ha tolto le righe bianche a mano; carosello sett3 col titolo giusto). Sovrascritti il vecchio Rally (20260718) e la slide sett3. Log in grafica-stato.json.

## Anello 6 — /smh-pubblica + run GitHub simulazione

**Esito (12/07 ~22:30):** ✅ CODA CARICATA — commit `a853750`: 8 buste (settimanale 12/07 · giornalieri 14, 16, 17, 18/07 · weekend 16/07 · storie 15/07 ×2 e 17/07 ×2) + 10 PNG. PUBLISH_LIVE spento = tutto in SIMULAZIONE. Riconciliazione Step 0: busta Sarah Toscano (10/07) allineata al piano ma ormai scaduta domani — decisione da prendere PRIMA del LIVE. NON in coda: carosello Luglio (è il post di lancio: la sua data si decide con l'attivazione LIVE) e i giornalieri di eventi passati (03–11/07).

| # | Dove | Cosa è successo | Gravità | Proposta fix |
|---|------|-----------------|---------|--------------|
| Q1 | Grafica ↔ caption (settimanale) | La settimana 13–19 ha 9 eventi ma il grafico ne tiene 8: l'agente grafica ha scartato Casabianca Swing, l'agente approvazione (in caption) aveva scartato Armonie → **grafico e caption raccontavano set diversi**. Nessun anello confronta i due prodotti dello stesso post | 🔴 | Regola per smh-grafica/pubblica: prima della coda, confrontare elenco eventi del grafico vs caption; con >8 eventi la scelta di chi resta fuori va fatta UNA volta sola (e in caption possono stare tutti e 9 — fix applicato così) |
| Q2 | Aggregati (caption stantie) | La caption weekend era la versione vecchia "Le Vibrazioni STASERA" (pensata per pub venerdì), ma il piano aveva spostato la pubblicazione a giovedì con headline Rally: se pubblicata così, il "stasera" era FALSO. Header di sezione anche sbagliati (13/07/14–19 vs 12/07/13–19) | 🔴 | Quando il piano cambia una riga AGG, smh-approvazione deve aggiornare anche la sezione corrispondente del file aggregati (header + caption), non solo il piano. Caption riscritta e ratificanda da Michele |
| Q3 | Archivio approvati (buco) | La caption di **Le Vibrazioni** (evento grande!) non esiste in NESSUN file di `approvati/` — c'è "Liscio for Dummies" ma non lei; recuperata dalla bozza 25 del 28/06 (stato ancora "da-approvare" nel file). Conferma il problema T2/igiene: gli stati delle bozze non riflettono le approvazioni reali | 🟡 | Una sessione "riconciliazione archivio": stati delle bozze allineati alle approvazioni vere; ogni evento approvato DEVE avere il suo blocco in approvati/ |
| Q4 | Push GitHub (skill smh-pubblica) | Il push di ~8 MB di PNG è FALLITO col buffer HTTP di default ("the remote end hung up unexpectedly") e l'output ingannava ("Everything up-to-date" a push non avvenuto). Riuscito con `-c http.postBuffer=524288000` | 🟡 | Aggiungere alla skill: push con postBuffer grande + verifica finale `git ls-remote` (il commit DEVE comparire sul remoto) |
| Q5 | Tempistica checkpoint | Lo slot del settimanale (dom 18:00) è scaduto durante l'attesa del checkpoint umano → il post verrà recuperato domattina dal GRACE_DAYS (+1g). In produzione: la grafica degli aggregati va compilata e approvata PRIMA della sera di pubblicazione | 🟢 | Non è un bug (anzi: test dal vivo del recupero). Regola operativa: giro grafica aggregati entro il pomeriggio del giorno di pubblicazione |

**Cosa aspettarsi adesso (osservazione 🧪, PUBLISH_LIVE spento):**
- lun 13/07 ~7:00 → 🧪 settimanale (recuperato +1g, dentro GRACE_DAYS) + ❗ Sarah Toscano scaduta (oltre +2g)
- mar 14/07 ~7:00 → 🧪 La Fiorita · mer 15/07 → 🧪 storie ×2 · gio 16/07 → 🧪 Virtus (7:00) + weekend (18:00) · ven 17/07 → 🧪 Le Vibrazioni + storie ×2 · sab 18/07 → 🧪 Rally
- (in simulazione le buste non si archiviano: i messaggi si accumulano, è normale)

**Aggiornamento 12/07 sera:** ✅ le 3 caption (settimanale riallineata, weekend riscritta, Vibrazioni con cross-mention) sono state RATIFICATE da Michele in chat. ✅ Busta Sarah archiviata (`857b0a5`).

**🚀 DECISIONE DI MICHELE (12/07 ~23:30): LANCIO LIVE LUNEDÌ 13/07** — anticipato rispetto al piano prudente (motivo: settimana delle coppe europee, La Fiorita 14/07 e Virtus 16/07 già in coda). L'osservazione 🧪 si trasforma in osservazione DAL VIVO. Preparato il pacchetto di lancio (commit `5b6aa01`): carosello Luglio (6 slide, data 13/07) + storia del 13/07 (Classica Giovani – Trio, compilata al volo su copia DAHPNY4gmPQ, pagina 7 del master — PULITA, niente righe bianche: o Michele le ha già tolte dal master o pagina 7 non le aveva) + il settimanale già in coda esce col recupero. Coda totale: 10 buste, 13→18/07. Avviso dato: prima chiamata VERA delle API carosello/storie (mai testate live; FB photo_stories la meno collaudata). ✅ **PUBLISH_LIVE=true attivato da Michele il 12/07 ~23:45** (screenshot verificato). Il giro di prova si chiude qui e diventa LANCIO: primo run reale lunedì 13/07 ore 7:00 (settimanale + carosello Luglio + storia Classica Trio). Decise in extremis anche le **regole di recupero per tipo** (giornaliero/storie 0gg, aggregati 2gg, weekend mai domenica, sovrapposizioni OK) → memoria `project_regole_recupero_pubblicazione`, da implementare in publish.py come primo fix post-lancio.

## Anello 4 — /smh-approvazione

_(non ancora)_

## Anello 5 — /smh-grafica

_(non ancora)_

## Anello 6 — /smh-pubblica + run GitHub simulazione

_(non ancora)_
