# Prompt pronto — SESSIONE 6: Giro di prova end-to-end

> Ultimo dei 6 fix pre-lancio (vedi `project_roadmap_pre_lancio` item 6).
> Lanciare in una **sessione nuova e pulita**, con modello **Fable 5** selezionato.
> Prompt scritto "alla Fable": tutta la specifica davanti in un solo turno.

---

San Marino Happens — SESSIONE 6: Giro di prova end-to-end in simulazione.

Prima di tutto: leggi ULTIMO_REPORT.md e CLAUDE.md (cartella progetto). Poi la
memoria project_roadmap_pre_lancio (item 6) e project_lancio_globale_prova.
NON rispondere prima di aver letto ULTIMO_REPORT.md.

── OBIETTIVO ──
Fare UN giro completo end-to-end sui dati VERI, tutto in SIMULAZIONE, per scovare
ogni intoppo PRIMA di decidere il LIVE. È l'ultimo dei 6 fix pre-lancio: gli anelli
1→6 sono costruiti e testati singolarmente; qui li mettiamo in fila e li guardiamo
girare tutti insieme come farebbero il giorno del lancio.

── LA CATENA DA PERCORRERE (in ordine, uno alla volta) ──
1. RICERCA + VERIFICA + TESTI: lancia /smh-giro (orchestratore dei tre subagenti in
   sequenza). Si ferma con grazia se un anello dà zero risultati e prepara la bozza
   email di riepilogo. A fine giro parte l'avviso Telegram a Michele.
2. APPROVAZIONE: dopo che Michele risponde ✅/❌ al bot Telegram, gira
   /smh-approvazione (protocollo: ✅ = tutto · ❌ 3,5 = tutto tranne 3 e 5 · ✅ 1,2 =
   solo 1 e 2). Output: file post-approvati-AAAA-MM-GG.md.
3. GRAFICA: /smh-grafica sui post approvati. Flusso a DUE FASI con checkpoint umano:
   compila su una COPIA del template Canva, si FERMA, ed esporta i PNG SOLO dopo il
   «procedi» di Michele. Giorno della settimana SEMPRE calcolato in Python.
4. PUBBLICAZIONE: /smh-pubblica mette PNG+JSON in coda nel repo GitHub. Da lì il
   workflow GitHub Actions gira in SIMULAZIONE (PUBLISH_LIVE resta su false/simulazione)
   e nei 2-3 giorni giusti arrivano i messaggi 🧪 su Telegram, senza pubblicare nulla
   di reale.

── VINCOLI FERREI ──
- PUBLISH_LIVE resta SPENTO per tutto il giro. Nessun post reale su IG/FB. Se in
  qualsiasi punto stai per fare un'azione che pubblica davvero, FERMATI e chiedi.
- NON INVENTARE MAI dati, date, eventi, fonti. Dato mancante → "non specificato" /
  "da verificare", mai un valore plausibile inventato.
- Rispetta i checkpoint umani: dopo la grafica NON esportare da solo, aspetta il
  «procedi». Dopo il giro di ricerca, quando serve un controllo umano manda a Michele
  il LINK esatto da aprire (ma prima muoviti da solo: incrocia 2 fonti, non fidarti
  di un singolo riassunto automatico).
- Lavora sempre su COPIE dei template Canva, mai sul master.

── COSA VOGLIO CHE TU FACCIA, OLTRE AD ESEGUIRE ──
Sei in modalità "caccia agli intoppi". Mentre percorri la catena, tieni un DIARIO
degli attriti: ogni punto in cui qualcosa si è inceppato, è stato ambiguo, ha
richiesto un mio intervento manuale che si poteva evitare, o dove un anello ha
passato all'altro un dato sporco/incompleto. Alla fine consegnami:
1. Esito: la catena ha girato fino in fondo? Dove si è fermata e perché.
2. Lista intoppi trovati, ciascuno con: dove, cosa è successo, gravità, e una
   proposta di fix (senza applicarla ora — decidiamo insieme).
3. La tua raccomandazione: siamo pronti per PUBLISH_LIVE=true, o restano blocchi?

── QUANDO HO BISOGNO DI TE ──
Sei tu che guidi il giro, ma io (Michele) sono l'anello umano su tre punti:
approvazione Telegram ✅/❌, «procedi» sull'export grafica, e la decisione finale
LIVE. Quando arrivi a uno di questi, fermati e dimmi ESATTAMENTE cosa devo fare
(che messaggio mandare, che link aprire, che pulsante premere) — secco, una riga.

── A FINE SESSIONE ──
Aggiorna project_roadmap_pre_lancio (item 6) e ULTIMO_REPORT.md con l'esito e la
lista intoppi. Se il giro è pulito, prepara il prompt della sessione successiva
(decisione + attivazione LIVE). Se restano intoppi, prepara il prompt del fix
prioritario (uno per sessione — vedi feedback_una_sessione_alla_volta).
