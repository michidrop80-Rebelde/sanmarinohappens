# Regole di verifica — controlli evento per evento

Carica questo file allo Step 3, quando verifichi gli eventi uno per uno.
Obiettivo: **confermare il vero, isolare il dubbio, scartare il falso** — senza mai
inventare una conferma. La ricerca ha già fatto un controllo di sanità; tu fai il
controllo **profondo** sulla fonte.

## Ordine dei controlli per ogni evento

### 1. Ancora futuro e in finestra
- Data ≥ oggi. Se è passato → `scartato`, motivo "passato".
- Dentro `ricerca.finestra_giorni` della config (default 60 gg). Fuori → `scartato`, motivo "fuori finestra".

### 2. Conferma sulla fonte originale (il controllo centrale)
- Apri la `Fonte` dell'evento con **WebFetch**. L'evento c'è ancora? Data, ora e luogo coincidono con quanto scritto?
  - Coincide tutto → verso `verificato`.
  - La fonte dice una data/luogo **diversi** → aggiorna il dato e nota la correzione nella riga `Verifica`. Se la discordanza è seria e non chiara → `da-confermare-michele`.
  - La fonte **non cita più** l'evento → prova una seconda fonte (Step 3 sotto). Se sparito ovunque → `da-confermare-michele` (potrebbe essere annullato), motivo nel `Dubbio`. Non scartare al primo 404.
- **Fonte irraggiungibile** (404/timeout): non è prova che l'evento sia falso. Prova una seconda fonte; se niente conferma → `da-confermare-michele`, **non** `scartato`.

### 2-bis. Evento VICINO (≤ 21 giorni): caccia al cambiamento, non conferma del vecchio
Vale **anche** per gli eventi che risultano invariati o già verificati nel master.
Il controllo 2 chiede «la fonte dice ancora questo?»; qui la domanda è opposta:
**«è successo qualcosa a questo evento da quando l'abbiamo guardato?»**
- **WebSearch** su nome evento + `rinviato` / `annullato` / `spostato` / `nuova data`.
- Serve perché una pagina evento **non si aggiorna quando l'evento salta**: resta
  identica e continua a confermare il dato vecchio. Nel caso del San Marino Revival
  (28/07/2026) il rinvio di un mese stava su San Marino RTV e Rally Time, **non**
  sulla pagina di partenza: riaprire solo quella avrebbe riconfermato l'errore.
- Trovato un cambiamento → aggiorna data/luogo, cita **due fonti indipendenti**,
  declassa da INVARIATO a MODIFICATO/CANCELLATO e **notifica**.
- Niente di nuovo su nessuna fonte → `verificato`, e annota `Ultimo ricontrollo`.

### 3. Seconda fonte quando serve
- Per eventi importanti o con fonte singola poco affidabile, cerca conferma con **WebSearch** su un'altra fonte (altro aggregatore, sito ufficiale, federazione).
- Doppia conferma → `verificato`. Una sola fonte debole e nessuna conferma → `da-confermare-michele`.

### 4. Geografia: davvero a San Marino
- Il luogo è dentro la Repubblica di San Marino (uno dei 9 castelli / sedi note: San Marino Stadium a Serravalle, Campo La Ciarulla a Serravalle, Campo Bruno Reffi, Teatro Titano, ecc.)?
- Indirizzo in un'altra città (Rimini, ecc.) → `scartato`, motivo "fuori San Marino".

### 5. Sciogli il dubbio dell'`Avviso` (eventi arrivati con ⚠️)
Ogni `⚠️` dalla ricerca porta un `Avviso` con il dubbio preciso. Affrontalo:
- **Data discordante tra fonti** → cerca la fonte ufficiale (es. FSGC/UEFA per il calcio). Risolta → `verificato` con la data giusta; irrisolta → `da-confermare-michele`.
- **Sport casa/trasferta** → conferma che la gara in casa sia allo stadio/palazzetto a San Marino e in quale data (andata o ritorno). Se non confermabile → `da-confermare-michele`.
- **Coppe europee**: la sede può cambiare; fidati solo di fsgc.sm (via home `fsgc.sm/it`) e UEFA.com.

### 6. Completa i campi mancanti
- Campi `non specificato` (ora, luogo preciso): se la fonte li riporta, riempili.
- Se un campo **essenziale** (Data, Luogo, Fonte) resta vuoto → l'evento non può stare in "Verificati": va in "Da confermare".

### 7. Deduplica tra sezioni
- Se due eventi sono lo stesso (titolo simile, stessa data/luogo) tienine uno solo; l'altro → `scartato`, motivo "doppione di [titolo]".

### 8. Verifica autonoma prima di escalare a Michele
Se un dato manca o una pagina non si apre, **non escalare subito a `da-confermare-michele`** — prima esaurire queste opzioni in ordine:

1. **Varianti URL** — prova trattini al posto di underscore, maiuscole diverse, slug alternativi. visitsanmarino.com usa il pattern `/pub1/VisitSM/evento/AAAAMMGG-Titolo-con-trattini.html` (trattini, non underscore, non spazi).
2. **Pagina lista** — WebFetch sulla pagina eventi del sito (es. visitsanmarino.com/eventi.html) per trovare il link corretto all'evento.
3. **Altre fonti** — WebSearch con titolo evento + "San Marino" + anno; WebFetch su giornalesm.com, libertas.sm, sanmarinortv.sm.

Solo se dopo tutti questi tentativi il dato resta irrecuperabile → `da-confermare-michele` con motivo preciso.

## Principio di prudenza
Nel dubbio **non promuovere**: `da-confermare-michele` è sempre preferibile a un
`verificato` falso. Pochi eventi solidi valgono più di tanti eventi gonfiati.
La conferma definitiva degli incerti la dà Michele (in futuro via Telegram).
