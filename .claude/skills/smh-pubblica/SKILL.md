---
name: smh-pubblica
description: Sesto anello di San Marino Happens. Prende i PNG già esportati di OGNI tipo (giornalieri, settimanali, weekend, caroselli, storie) + il testo approvato corrispondente, calcola la vera data di pubblicazione dal piano editoriale e mette in coda nel repo GitHub sanmarinohappens (posts/) una "busta" JSON (con campo `tipo` e, per caroselli/storie, la lista `immagini`) + i PNG, con commit+push. Prima del push fa passare OGNI busta dal cancello di controllo automatico `/smh-check` (blocca le buste con errori di contenuto: prezzi, dati stantii sull'immagine, giorno/luogo/ora incoerenti). La pubblicazione vera su Instagram e Facebook scatta poi da sola via GitHub Actions, all'ora giusta, protetta da un interruttore PUBLISH_LIVE (di default in simulazione). Usare quando si vuole "mettere in coda i post per la pubblicazione", "mandare le grafiche al robot di Instagram", o come sesto passo della catena dopo la grafica.
---

# Agente pubblicazione — San Marino Happens

Sei il **sesto anello** della catena di San Marino Happens (`@sanmarinohappens`):
ricerca → verifica → testi → approvazione → grafica → **pubblicazione**.

Il tuo lavoro NON è pubblicare tu stesso: è preparare la "busta" giusta (immagine/i
+ tipo + data + testo) e spedirla nel repo GitHub. Un robot separato (GitHub Actions,
sempre acceso anche a Mac spento) apre le buste una alla volta, al momento giusto, e
pubblica per davvero su Instagram **e** Facebook.

⚠️ **Regola sopra tutto: NON INVENTARE MAI.** Se non trovi con certezza a quale
contenuto corrisponde un PNG, a quale data va, o non trovi il testo approvato,
**fermati e chiedi a Michele** invece di indovinare. Meglio un post mancante che
un post sbagliato su un account pubblico.

## Cosa copre questa skill — TUTTI i tipi

Ogni tipo di post ha il suo **campo `tipo`** nella busta, la sua **cartella di export**
e la sua **sorgente di caption**. Il robot (`publish.py`) legge `tipo` e sceglie da solo
la giusta API Meta (foto singola / carosello / storia).

| `tipo` | Cosa è | Cartella export (Mac) | Nº immagini | Caption |
|--------|--------|-----------------------|-------------|---------|
| `giornaliero` | Foto singola feed, evento del giorno | `marketing/3 Export/1 Giornalieri - Post/` | 1 | da `dati/post/approvati/*.md` |
| `storia` | Storie IG/FB, tutti gli eventi del giorno | `marketing/3 Export/2 Giornalieri - Stories/` | 1..N (una per evento) | **nessuna** (il testo è nella grafica) |
| `settimanale` | Foto singola feed, "questa settimana" | `marketing/3 Export/3 Settimanali - Post/` | 1 | da `aggregati-luglio-agosto-2026.md` sez. `## SETTIMANALE` |
| `weekend` | Foto singola feed, "questo weekend" | `marketing/3 Export/4 Weekend - Post/` | 1 | da `aggregati-luglio-agosto-2026.md` sez. `## WEEKEND` |
| `carosello` | Carosello mensile (più slide) | `marketing/3 Export/5 Mensili/` | 2..10 (slide ordinate) | da `aggregati-luglio-agosto-2026.md` sez. `## CAROSELLO` |

La mappa cartella→tipo è la stessa di `dati/grafica-stato.json` (`cartelle_export`): la
cartella da cui viene un PNG **è** il suo tipo. (Il bisettimanale è sospeso: non si pubblica.)

⚠️ **File di prova = mai in coda.** I PNG col prefisso `PROVA_` sono export di test
usa-e-getta: NON vanno mai messi in coda. Metti in coda solo gli export "puliti" del
run vero.

## Come è fatta la busta JSON (schema)

Ogni busta è un file `.json` in `posts/`. Due forme:

**Foto singola** (`giornaliero`, `settimanale`, `weekend`) — l'immagine è il PNG
"gemello" (stesso nome del JSON, estensione `.png`), quindi NON serve il campo `immagini`:
```json
{
  "tipo": "settimanale",
  "data_pubblicazione": "2026-07-12",
  "ora_pubblicazione": "18:00",
  "titolo_evento": "Settimana 13–19 luglio",
  "caption": "🗓 Questa settimana in Repubblica...\n\n#SanMarinoHappens ..."
}
```

**Campo facoltativo `user_tags`** (solo `giornaliero` e `storia`) — i tag degli
organizzatori, come dizionario **nome-immagine → lista di tag**. Vedi Step 4-tag:
```json
"user_tags": {
  "20260725_Post giornaliero.png": [ {"username": "sanmarinooutlet", "x": 0.5, "y": 0.9} ]
}
```

**Multi-immagine** (`carosello`, `storia`) — la busta elenca i PNG in `immagini`
(ordine = slide del carosello / ordine cronologico delle storie); il JSON può avere
un nome-base diverso dai PNG:
```json
{
  "tipo": "carosello",
  "data_pubblicazione": "2026-06-30",
  "ora_pubblicazione": "18:00",
  "titolo_evento": "Eventi di Luglio 2026",
  "caption": "🎪 Tutto luglio a San Marino, settimana per settimana...\n\n#SanMarinoHappens ...",
  "immagini": [
    "20260630_Carosello_1.png",
    "20260630_Carosello_2.png",
    "20260630_Carosello_3.png"
  ]
}
```
Per le **storie** identico ma con `"tipo": "storia"`, la lista delle storie del giorno
e **senza** `caption` (o `caption` vuota):
```json
{
  "tipo": "storia",
  "data_pubblicazione": "2026-07-05",
  "ora_pubblicazione": "07:00",
  "titolo_evento": "Storie del 5 luglio",
  "immagini": ["20260705_Storia_1.png", "20260705_Storia_2.png"]
}
```

Note:
- `ora_pubblicazione` è **informativo** (per Michele). L'orario vero lo decide il
  workflow GitHub. `data_pubblicazione` è ciò che il robot usa davvero per decidere SE
  pubblicare oggi (regola: pubblica se `data_pubblicazione` ≤ oggi entro 2 giorni di
  recupero; oltre → "scaduta", solo avviso).
- Le storie **non hanno caption**: il robot lo sa e non la pretende. Per tutti gli altri
  tipi la caption è **obbligatoria** (una busta con caption vuota viene segnalata come
  anomala e non pubblicata).
- Il carosello vuole **2..10 immagini**; fuori range → busta anomala.

## Convenzione nomi file in `posts/`
Per tenere la coda ordinata e leggibile, quando copi i PNG in `posts/` usa il **prefisso
data di pubblicazione** `AAAAMMGG_`:
- giornaliero: `AAAAMMGG_Post giornaliero.png` (invariato — qui AAAAMMGG è la data evento)
- settimanale: `AAAAMMGG_Settimanale.png` · weekend: `AAAAMMGG_Weekend.png`
- carosello: `AAAAMMGG_Carosello_1.png`, `_2.png`, … + `AAAAMMGG_Carosello.json`
- storia: `AAAAMMGG_Storia_1.png`, `_2.png`, … + `AAAAMMGG_Storia.json`

(Per aggregati/storie AAAAMMGG = **data di pubblicazione**; è solo un identificatore
leggibile, il valore vero sta comunque dentro il JSON.)

## Base del progetto
- Progetto principale: `/Users/michele/Desktop/PROGETTI/San Marino Happens`
- Repo GitHub (cartella senza spazi): `/Users/michele/Desktop/PROGETTI/San Marino Happens`
- Token GitHub: `.claude/secrets/github.json` (campo `token`) — nel progetto principale
- Piano editoriale: `dati/piano-editoriale.md` (colonna **Tipo**: `F`=giornaliero feed,
  `S`=storie, `AGG`=aggregato → la colonna *Contenuto* dice quale: `WEEKEND…`,
  `SETTIMANALE…`, `CAROSELLO…`)
- Testi giornalieri approvati: `dati/post/approvati/*.md`
- Testi aggregati (settimanale/weekend/carosello): `dati/post/aggregati-luglio-agosto-2026.md`

## ⚠️ Interruttore di sicurezza — leggi prima di iniziare
Il repo pubblica per davvero **solo se** la Variable di GitHub `PUBLISH_LIVE` vale
`true`. Finché Michele non l'ha attivata, tutto quello che metti in coda viene gestito
in **SIMULAZIONE** dal robot (nessun post reale, solo notifica Telegram di prova).
Quindi non serve essere prudenti nel mettere post in coda per fare test — ma dillo
sempre chiaro a Michele nel riepilogo, e non mettere in coda post con
`data_pubblicazione` reale se non te l'ha chiesto (in dubbio, chiedi).

## Flusso

### Step 0 — Riconcilia la coda col piano editoriale (SEMPRE, all'inizio)
Prima di mettere in coda roba nuova, controlla che le buste GIÀ in coda siano ancora
allineate al piano. Il piano può cambiare (è successo con Sarah Toscano: spostata
09→10/07, ma la busta era rimasta al 09 → il robot non l'avrebbe mai trovata).

Per ogni `posts/*.json` nel repo `/Users/michele/Desktop/PROGETTI/San Marino Happens/`:
1. Leggi `tipo`, `titolo_evento`, `data_pubblicazione`.
2. Trova nel piano la riga corrispondente:
   - `giornaliero` → riga **Tipo = F** con quel titolo (o Data evento).
   - `settimanale`/`weekend`/`carosello` → riga **Tipo = AGG** la cui colonna *Contenuto*
     inizia con `SETTIMANALE`/`WEEKEND`/`CAROSELLO` e copre lo stesso periodo.
   - `storia` → riga(he) **Tipo = S** (o le storie del giorno) con quella Data pub.
3. Confronta la **Data pub** del piano con `data_pubblicazione`:
   - **Combaciano** → non toccare nulla.
   - **Diverse** → il piano è cambiato: **correggi** la busta, **ricommitta+pusha**
     (`Riallinea data <titolo> (X → Y) al piano`), e **segnalalo** nel riepilogo.
   - **Non più nel piano** → NON cancellare di tua iniziativa: **fermati e avvisa Michele**.
   - **`data_pubblicazione` già passata** → segnalalo come "busta scaduta in coda".

Questo è il gemello "sul Mac" del controllo che fa `publish.py` su GitHub: il robot vede
solo la DATA (non ha il piano), tu hai il piano e puoi **correggere** prima che sia un problema.

### Step 1 — Trova i contenuti non ancora in coda (per ogni tipo)
Per ciascuna cartella di export (vedi tabella tipi), elenca i PNG **puliti** (escludi
`PROVA_*`). Elenca cosa è già in `posts/` (JSON + immagini). Un contenuto è "da mettere
in coda" se non risulta già presente in `posts/` (né come busta né tra le `immagini`).

- **giornaliero / settimanale / weekend** = 1 PNG → 1 busta.
- **carosello** = il gruppo ordinato di slide di quel mese → 1 busta con `immagini`.
- **storia** = tutte le storie di **uno stesso giorno**, in ordine cronologico → 1 busta
  con `immagini` (una storia per evento del giorno).

⚠️ I nomi dei file di export per aggregati/storie non sono ancora standardizzati (finora
solo `PROVA_`). Se non è ovvio quali PNG appartengono a un carosello/giorno-storie,
**mostra a Michele la mappatura che intendi usare (quali file, in che ordine) e fatti
confermare** prima di procedere. Non indovinare l'ordine delle slide/storie.

Se non c'è nessun contenuto nuovo, dillo a Michele e fermati.

### Step 2 — Determina tipo + vera data di pubblicazione dal piano
Il `tipo` è dato dalla cartella di export. La **data di pubblicazione** viene SEMPRE dal
piano (`dati/piano-editoriale.md`, tabella "Calendario di pubblicazione"), non dedotta:
- `giornaliero` → riga **F** con Data evento = quella del file → prendi **Data pub**
  (per i grandi nomi può essere 1–3 giorni prima; qui è same-day salvo eccezioni).
- `weekend`/`settimanale`/`carosello` → riga **AGG** giusta → **Data pub** (aggregati la
  **sera prima, 18:00**; carosello = ultimo giorno del mese precedente).
- `storia` → le storie escono il **giorno stesso, 7:00** → Data pub = quel giorno.

Da quella riga prendi anche il **Titolo/Contenuto** per ritrovare il testo nello Step 3.
Se non trovi una riga corrispondente, o è ambigua, **fermati e chiedi a Michele**.

### Step 3 — Prendi il testo approvato (caption)
- `giornaliero` → in `dati/post/approvati/*.md`, sezione col titolo che corrisponde
  all'evento. Prendi **Caption** + **Hashtag** e uniscili (caption + riga vuota + hashtag).
- `settimanale`/`weekend`/`carosello` → in `dati/post/aggregati-luglio-agosto-2026.md`,
  sezione `## SETTIMANALE — …` / `## WEEKEND — …` / `## CAROSELLO — …` che copre quel
  periodo. Prendi il blocco caption completo (per il carosello è la **caption-indice**).
- `storia` → **nessuna caption** (il testo è già dentro la grafica). Lascia la busta
  senza `caption`.

Se manca il testo dove serve, **fermati e chiedi a Michele** (magari il PNG è stato
esportato ma il testo non è stato approvato/compilato).

### Step 4 — Prepara la busta (JSON) + i PNG
Componi la busta secondo lo schema sopra (con `tipo`; per carosello/storia con
`immagini`). Copia in `posts/` del repo TUTTI i PNG del contenuto, con i nomi della
convenzione, e scrivi il JSON gemello/di gruppo. Esempio carosello:
```bash
REPO="/Users/michele/Desktop/PROGETTI/San Marino Happens"
SRC="marketing/3 Export/5 Mensili"
cp "$SRC/<slide1>.png" "$REPO/posts/20260630_Carosello_1.png"
cp "$SRC/<slide2>.png" "$REPO/posts/20260630_Carosello_2.png"
# ... e scrivi 20260630_Carosello.json con "immagini":[...] nell'ordine giusto
```
Per giornaliero/settimanale/weekend basta il PNG gemello (stesso nome del JSON):
```bash
cp "marketing/3 Export/1 Giornalieri - Post/AAAAMMGG_Post giornaliero.png" "$REPO/posts/"
# + AAAAMMGG_Post giornaliero.json
```

### Step 4-tag — Tag degli organizzatori (solo giornalieri e storie)
Serve a far arrivare una notifica a chi organizza l'evento: il post finisce nella sua
sezione «post in cui è taggato» e, per le storie, **può ricondividerlo** (reach gratis).
È la leva principale per farci conoscere dagli organizzatori in vista della Fase 2.

**Si applica SOLO ai tipi `giornaliero` e `storia`.** Settimanale, weekend e carosello
**non si taggano mai**: contengono 5-10 eventi, sceglierne tre sarebbe una preferenza
arbitraria — la stessa regola di equità per cui negli aggregati nessun evento è escluso.

**Una busta `storia` contiene più storie, una per evento**: i tag si risolvono **immagine
per immagine**, ciascuna contro il proprio evento. Mai una lista di tag valida per tutta
la busta.

Per ogni immagine:
1. Dal blocco evento nel file verificato (titolo, luogo, descrizione, fonte) individua
   fino a **3 candidati**: chi **organizza**, il **luogo**, l'**artista/ospite**.
2. Cerca ogni candidato in `dati/handle-organizzatori.json`, per `nome` e per `alias`
   (senza distinzione di maiuscole e accenti, su parole intere).
3. Tagga **solo** chi ha `stato: "attivo"` e `instagram` non nullo.

⚠️ **Un handle non registrato NON si inventa mai** — neanche se «si capisce» quale sarebbe
(le Giunte di Castello, per dire, usano schemi tutti diversi fra loro). Se il candidato non
è nel registro, aggiungi al registro una voce con `stato: "da-cercare"`, `instagram: null`
e il nome osservato negli alias, e **quel tag non si mette**. Il post esce lo stesso.

Coordinate da usare (`x`, `y` sono frazioni dell'immagine, da 0.0 a 1.0):

| Contenuto | Quanti | Coordinate |
|---|---|---|
| Post feed | 1 tag | `x 0.50` · `y 0.90` |
| Post feed | 2 tag | `x 0.35` e `0.65` · `y 0.90` |
| Post feed | 3 tag | `x 0.25`, `0.50`, `0.75` · `y 0.90` |
| Storia | 1 tag | `x 0.50` · `y 0.78` |

Nel feed il tag è **invisibile** finché non si tocca la foto, quindi la posizione non
tocca il design. Nelle **storie** invece la menzione **si vede**, è uno sticker sopra la
grafica, e la posizione va scelta guardando il template:

- il blocco descrizione finisce intorno a `y 0.73`;
- la riga di chiusura «Seguici su @sanmarinohappens…» sta fra `y 0.83` e `y 0.86`;
- **l'ultimo 10-12% dell'altezza è coperto dall'interfaccia di Instagram** (barra
  «Invia messaggio»): uno sticker messo lì sotto rischia di essere nascosto o
  non toccabile.

Quindi la fascia libera è **`y 0.75`–`0.82`**, e si usa `y 0.78`. ⚠️ Valore **ancora da
confermare dal vivo**: se lo sticker copre testo o logo, si corregge qui.

Il campo da scrivere nella busta è un **dizionario nome-immagine → lista di tag**:
```json
"user_tags": {
  "20260726_Storia_1.png": [ {"username": "sanmarinocomics", "x": 0.5, "y": 0.92} ],
  "20260726_Storia_2.png": [ {"username": "titanobears", "x": 0.5, "y": 0.92} ]
}
```
Le buste senza il campo funzionano esattamente come prima: il campo è facoltativo.

`publish.py` blocca da solo le buste con tag malformati (più di 3 per immagine, coordinate
fuori da 0-1, chiavi che non corrispondono a nessuna immagine, tag su un aggregato), e se
Instagram rifiuta i tag **ripubblica senza**: un tag non deve mai costare un post.

### Step 4-bis — Cancello di controllo `/smh-check` (OBBLIGATORIO, prima del push)
⛔ **Non pushare NIENTE prima di questo controllo.** È la garanzia che una busta sbagliata
non arrivi mai live: è nato dal caso 13/07 (immagini con dati vecchi uscite senza che nessuno
le fermasse). Gira **sempre** qui in automatico — non è una cosa che Michele deve ricordarsi
di lanciare: fa parte della pubblicazione.

Sulle buste che hai appena preparato in `posts/` (Step 4), esegui il controllo completo della
skill **`/smh-check`** (procedura in `.claude/skills/smh-check/SKILL.md`):
1. Dossier meccanico: `python3 .claude/skills/smh-check/assets/smh_check.py`
2. Per OGNI busta nuova **apri il/i PNG (vision)**, trascrivi giorno·data·titolo·luogo·ora·prezzi,
   incrocia con fonti + caption + aggregato, e classifica coi 5 controlli → **✅ / ⚠️ / ❌**.
3. In base all'esito:
   - **Tutte ✅ (o solo ⚠️)** → prosegui col commit+push (Step 5). I **⚠️ NON bloccano**: escono, ma li segnali.
   - **Qualche ❌** → quella busta **NON deve uscire**: **toglila da `posts/`** (cancella i suoi
     file appena copiati, così non entra nel commit — l'originale sul Mac/Canva resta intatto),
     **non committarla**, e **avvisa Michele** col referto + cosa correggere (di solito
     `/smh-grafica` per rifare un'immagine, o ripulire la caption dai prezzi). Le altre buste ✅
     **procedono normalmente**: la catena non si ferma tutta per una busta.
4. Se c'è anche solo un ⚠️ o un ❌, manda subito il referto dettagliato su **Telegram**:
   `python3 .claude/skills/smh-check/assets/smh_check.py --telegram "<referto>"`
   (Se è tutto ✅ basta il riepilogo generale dello Step 6, che ora va SEMPRE su
   Telegram — vedi sotto — quindi non serve un messaggio separato qui.)

Così la catena resta **autonoma**: se è tutto a posto va avanti da sola; ti chiama solo quando
c'è davvero qualcosa da sistemare.

### Step 5 — Commit + push
(Committa SOLO le buste sopravvissute al cancello: le ❌ le hai già tolte da `posts/`, quindi
`git add posts/` prende in automatico solo le buste ✅/⚠️.)
```bash
cd "/Users/michele/Desktop/PROGETTI/San Marino Happens"
git add posts/
git commit -m "Metti in coda [<tipo>]: <titolo> (pub AAAA-MM-GG)"
```
Per il push, leggi il token e usalo SOLO al volo (mai in `git config`):
```bash
TOKEN=$(python3 -c "import json; print(json.load(open('/Users/michele/Desktop/PROGETTI/San Marino Happens/.claude/secrets/github.json'))['token'])")
git pull --rebase "https://${TOKEN}@github.com/michidrop80-Rebelde/sanmarinohappens.git" main
git push "https://${TOKEN}@github.com/michidrop80-Rebelde/sanmarinohappens.git" HEAD:main
```
(Il `pull --rebase` prima del push evita conflitti con i commit automatici del robot —
es. `published.log`/metriche — come fa il workflow.)

### Step 6 — Riepilogo a Michele (SEMPRE anche su Telegram, non solo in chat)
⚠️ **Manda questo riepilogo su Telegram SEMPRE, anche quando tutto è ✅.** Se questa
skill gira da un task pianificato (senza che nessuno guardi la chat), il messaggio
Telegram è l'UNICO modo per Michele di sapere cosa è stato messo in coda — ed è
anche la sua finestra di veto naturale: la pubblicazione vera scatta solo al
prossimo cron (7:00/18:00), quindi c'è tempo per intervenire a mano su GitHub se
qualcosa non convince. Manda con `sendMessage` (credenziali `.claude/secrets/telegram.json`):
```
🔁 Riconciliazione coda ↔ piano (Step 0):
- <titolo> → data corretta X → Y (piano cambiato) [se ce ne sono]
- ⚠️ <titolo> non più nel piano / busta scaduta → serve decisione di Michele
- (oppure: "tutte le buste in coda sono allineate al piano")

🔎 Cancello /smh-check (Step 4-bis): ✅ X ok · ⚠️ Y da guardare · ❌ Z bloccate
   [se ❌: elenca quali buste ho tolto dalla coda e cosa correggere]

📬 Messi in coda N post (solo quelli passati dal cancello):
- [giornaliero] <titolo> → pubblicazione <data>
- [carosello]  <titolo> → pubblicazione <data> (N slide)
- [storia]     <giorno> → pubblicazione <data> (N storie)
- ...

🧪 Modalità: SIMULAZIONE (PUBLISH_LIVE non attivo) — nessun post reale arriverà su
   Instagram/Facebook. Riceverai comunque la notifica Telegram di prova del robot.
[oppure, se PUBLISH_LIVE=true:]
🟢 Modalità: LIVE — questi post verranno pubblicati per davvero su IG e FB alla data indicata.
```

## Verificare/lanciare il robot GitHub (facoltativo, solo se Michele chiede)
```bash
TOKEN=$(python3 -c "import json; print(json.load(open('/Users/michele/Desktop/PROGETTI/San Marino Happens/.claude/secrets/github.json'))['token'])")
# È attivo?
curl -s -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/michidrop80-Rebelde/sanmarinohappens/actions/workflows/publish.yml | grep '"state"'
# Lancialo ora (test senza aspettare il cron). Opzionale: "test_date" per fingere "oggi":
curl -s -X POST -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/michidrop80-Rebelde/sanmarinohappens/actions/workflows/publish.yml/dispatches \
  -d '{"ref":"main","inputs":{"test_date":""}}'
```
Poi controlla l'esito su github.com → tab Actions (o chiedi a Claude via API `.../actions/runs`).
