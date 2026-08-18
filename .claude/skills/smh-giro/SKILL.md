---
name: smh-giro
description: Orchestratore di San Marino Happens. Esegue in autonomia il giro completo della catena — ricerca → postino → verifica → testi — lanciando in sequenza i quattro subagenti (smh-ricerca, smh-postino, smh-verifica, smh-testi), riallineando il calendario del sito e lasciando a Michele le bozze di post pronte da approvare su Telegram. Usare quando si vuole "fare il giro completo", "aggiornare tutto", "lanciare la catena", "trovare e preparare i post in un colpo solo", o come task settimanale automatico di @sanmarinohappens.
---

# Orchestratore — giro completo San Marino Happens

Sei il **direttore d'orchestra** di San Marino Happens (`@sanmarinohappens`). Non fai
tu postino/ricerca/verifica/testi: li **deleghi ai quattro subagenti** nell'ordine
giusto, aspetti che ognuno finisca, passi il testimone al successivo e alla fine
avvisi Michele.

Catena: **ricerca → postino → verifica → testi** → (grafica e pubblicazione: fasi future, NON qui).

## Base del progetto
Tutti i percorsi sono relativi a:
`/Users/michele/Desktop/PROGETTI/San Marino Happens`
Config condivisa: `dati/config.json`.

⚠️ **Regola che sta sopra a tutto, valida per tutta la catena: NON INVENTARE MAI.**
Se un subagente non trova/conferma un dato, resta `non specificato` / `da-confermare`.
Meglio poche bozze solide che tante gonfiate.

## Flusso

### Step 0 — Contesto e controlli di guardia
Leggi `dati/config.json` (brand, percorsi). Se manca, segnalalo ma continua coi default.

Poi lancia le **guardie**. Sono controlli di sola lettura: non fermano il giro, ma
quello che dicono va riportato — sono lì apposta perché questi guasti sono silenziosi.

**a) Integrità** — tutti i file citati dalle skill e dagli agenti esistono davvero:
```bash
cd "/Users/michele/Desktop/PROGETTI/San Marino Happens"
python3 scripts/controllo-integrita.py
```
⚠️ **Se segnala file mancanti, NON fermarti ma NON far finta di niente**: un anello a
cui manca il suo file di regole lavora a braccio e sembra riuscito lo stesso — è
esattamente ciò che è successo dal 25 al 27/07/2026, quando la verifica ha girato per
due giorni senza `regole-verifica.md` senza che nessuno se ne accorgesse. Riporta
l'elenco **in cima** al riassunto finale (Step 6) e nel messaggio Telegram, così
Michele lo vede subito. Quasi sempre si recuperano con
`python3 scripts/recupera-da-transcript.py <cartella_temporanea>`.

**b) Export → coda** — le grafiche già esportate hanno la loro busta in `posts/`:
```bash
cd "/Users/michele/Desktop/PROGETTI/San Marino Happens"
python3 scripts/controllo-export-in-coda.py
```
⚠️ Fra grafica (anello 5) e pubblicazione (anello 6) il testimone passa a mano: un PNG
esportato in `marketing/3 Export/` ma mai messo in coda non fa rumore, il giorno passa
a vuoto e non se ne accorge nessuno — 3 volte in una settimana (28/07: 11 giornalieri;
30/07: il settimanale 03-09/08, visto solo il 02/08 a slot passato; 14/07: le storie).

**Se trova orfani, NON scrivere un elenco a Michele: chiudi tu il buco.** Un elenco è
un compito che passa a lui, e lui non deve toccare niente. Lancia il subagente
**smh-pubblica** (`subagent_type` non esiste per questo anello → usa la skill
`/smh-pubblica`) limitato a quei contenuti:
«Metti in coda SOLO questi export orfani: <elenco dei file>. Salta lo Step 1 di ricerca
generale, il lavoro è già individuato. Passa comunque dal cancello `/smh-check` (Step
4-bis) prima del push.»
Il cancello `/smh-check` resta obbligatorio: è quello che impedisce a una busta
sbagliata di uscire, ed è la ragione per cui questo recupero può essere automatico.
Se una busta viene bloccata dal cancello, QUELLA sola la riporti a Michele (con il
motivo) — le altre proseguono.
Nel riassunto finale e su Telegram va una riga sola: quante ne hai recuperate e per
quali date. La pubblicazione vera scatta comunque solo al cron delle 7:00/18:00, quindi
resta la finestra di veto.

**c) Copertura** — nei prossimi giorni non manca niente rispetto al calendario:
```bash
cd "/Users/michele/Desktop/PROGETTI/San Marino Happens"
python3 scripts/controllo-copertura.py
```
⚠️ **Questa esce 1 anche quando va tutto bene**: un giorno senza eventi reali resta
legittimamente scoperto, e non si inventano eventi per riempirlo. Quindi non trattare
il codice d'uscita come un errore — leggi l'elenco e riporta solo i giorni scoperti che
**hanno un evento disponibile** (cioè: c'è materiale approvato o verificato per quel
giorno ma la busta non c'è). Gli altri sono silenzio legittimo, non vanno né in Telegram
né nel riassunto.

### Step 1 — Lancia la RICERCA
Avvia il subagente **smh-ricerca** (Task/Agent tool, `subagent_type: smh-ricerca`).
Istruzione: «Fai il giro completo delle fonti e salva il file eventi datato di oggi,
seguendo la tua skill. Restituisci solo il riassunto.»
Aspetta che finisca. Tieni il suo riassunto (file prodotto, N eventi, fonti giù).
Se la ricerca riporta **zero eventi** nella finestra, non fermarti ancora: passa
comunque allo Step 1.5 — potrebbero esserci segnalazioni in coda dal bot anche se
la ricerca web non ha trovato nulla di nuovo. Fermati solo se ANCHE lo Step 1.5
non produce eventi (vai allo Step 4 e dillo chiaramente nell'email).

### Step 1.5 — Lancia il POSTINO
Avvia il subagente **smh-postino** (`subagent_type: smh-postino`).
Istruzione: «Importa gli eventi in coda su `queue/inbox.md` (bot Telegram) dentro
il file eventi di oggi appena prodotto dalla ricerca, come `da-verificare`, poi
svuota la coda, seguendo la tua skill. Restituisci solo il riassunto.»
Aspetta che finisca. Tieni il riassunto (N importati, N già presenti, coda vuota o
non c'era nulla). **Va lanciato DOPO la ricerca apposta**: `smh-ricerca` salva il
file di oggi da zero (Step 7 della sua skill) — se il postino scrivesse prima,
la ricerca lo sovrascriverebbe in silenzio, perdendo le segnalazioni del bot.
Se **zero eventi in coda** non è un blocco: prosegui normalmente allo Step 2 — è
solo silenzio, non un errore. Se anche la ricerca (Step 1) aveva dato zero eventi
E qui non c'è nulla da importare → fermati, vai allo Step 4.

### Step 2 — Lancia la VERIFICA
Avvia il subagente **smh-verifica** (`subagent_type: smh-verifica`).
Istruzione: «Verifica il file di eventi più recente prodotto oggi dalla ricerca,
seguendo la tua skill. Restituisci solo il riassunto.»
Aspetta. Tieni il riassunto (verificati / da-confermare-Michele / scartati).
Se **zero verificati** → vai allo Step 4: niente testi da scrivere, spiega perché.

### Step 3 — Lancia i TESTI
Avvia il subagente **smh-testi** (`subagent_type: smh-testi`).
Istruzione: «Scrivi le bozze dei post per gli eventi del file verificato più recente,
seguendo la tua skill. Restituisci solo il riassunto.»
Aspetta. Tieni il riassunto (file bozze, N bozze, intervallo date).

### Step 3a — Togli di mezzo i doppioni (obbligatorio)
L'agente dei testi scrive una bozza per **ogni** evento verificato: non sa cosa c'è già in
coda di pubblicazione. Prima di chiedere l'approvazione a Michele, lancia sempre:
```bash
cd "/Users/michele/Desktop/PROGETTI/San Marino Happens"
python3 scripts/segnala-doppioni.py
```
Mette in stato `gia-in-coda` le bozze per giorni che hanno già il loro post giornaliero, così
l'approvazione non le propone. ⚠️ **Perché serve:** il 27/07/2026, su 36 bozze, **19 erano
doppioni** — la prima era il post del giorno stesso, già pubblicato quella mattina. Un «✅
approva tutto» avrebbe fatto ricompilare 19 post già fatti sovrascrivendo buste già
controllate. Riporta nel riassunto finale quanti doppioni ha tolto.

### Step 3b — Filtra solo le differenze
Dal riassunto di smh-verifica estrai SOLO gli eventi non-invariati:
- 🆕 NUOVI
- ✏️ MODIFICATI
- 🗑 POTENZIALMENTE CANCELLATI
- ⚠️ DUBBI

Se non ci sono differenze → salta Step 4 e vai a Step 5 con messaggio "✅ Nessuna novità questa settimana."

### Step 4 — Avvisa Michele su Telegram con pulsanti

⚠️ **NON costruire il JSON dei pulsanti a mano nel curl.** È fragile e in passato è
stato saltato silenziosamente (Michele ha ricevuto testo senza pulsanti). Usa SEMPRE
lo script dedicato, che costruisce l'`inline_keyboard` corretto e salva lo stato.

**Cosa fa lo script `.claude/scripts/telegram-giro.py`:**
1. Manda il **Messaggio 1** = riepilogo numerico (🆕/✏️/🗑/⚠️ con i conteggi).
2. Manda gli eventi **a blocchi di 3**, ogni evento con due pulsanti reali
   `✅ [titolo]` / `❌` (callback_data `approve_[ID]` / `reject_[ID]`).
3. Salva `pending_events` + `sent_at` in `.claude/secrets/telegram-state.json`
   (lo legge poi smh-approvazione).

**Come chiamarlo:** prepara un array JSON degli eventi non-invariati e passalo a `--events`.
Ogni evento è un oggetto con questi campi:

| campo | valore | obbligatorio |
|-------|--------|--------------|
| `id` | N° bozza o ID master (es. `09`, `07c`) | sì |
| `titolo` | titolo evento | sì |
| `tipo` | `nuovo` · `modificato` · `cancellato` · `dubbio` | sì |
| `data` | es. `03/07` | consigliato |
| `luogo` | sede ufficiale | consigliato |
| `url` | **URL specifico dell'evento** (dal campo `Fonte:` del file verificato), NON la home del sito | sì |
| `dubbio` | **cosa non torna**, in una riga concreta (campo preciso + cosa dice la fonte + di che anno è) | **sì se `tipo: dubbio`** |
| `serve` | cosa servirebbe per scioglierlo (es. «una fonte 2026 con data e luogo») | consigliato sui dubbi |

🔴 **Un `⚠️` senza il campo `dubbio` non si manda più.** Regola di Michele del 10/08/2026:
*«quando hai un dubbio bisogna che mi segnali qual è il problema, se no non capisco, non
basta il solo segnale di pericolo»*. Un ⚠️ nudo gli sposta addosso la decisione **senza
l'informazione per prenderla**: preme ✅ per non bloccare la catena e il dubbio entra nel
sistema come un dato verificato — è così che «Mi Gusto» (date 2025) e la chiusura dell'11/08
della Sagra della Tagliatella (dati 2024) sono arrivate a un giorno dalla pubblicazione.
Il testo del dubbio **c'è già**: è il campo `Dubbio:` (e `Cosa serve:`) che `/smh-verifica`
scrive nel file verificato — va copiato, non riscritto.
Lo script fa rispettare la regola: se un evento è `tipo: dubbio` senza `dubbio`, scrive in
chiaro nel messaggio «Dubbio non spiegato — chiedi a Claude cosa non torna» ed **esce con
codice 2**. Michele riceve comunque i pulsanti (meglio un buco dichiarato che un ⚠️ muto),
ma il giro è da completare.

⚠️ **`url`: preferisci il link diretto all'evento** (quello che smh-verifica ha messo
nel riassunto strutturato, campo `🔗 [URL fonte]`). Se per quell'evento esiste solo la
pagina-lista generica (es. `usc.sm/eventi/`), **va bene lo stesso**: mettila lì —
Michele se li spulcia da sé. Meglio la pagina-lista che nessun link.

```bash
cd "/Users/michele/Desktop/PROGETTI/San Marino Happens"
python3 .claude/scripts/telegram-giro.py \
  --secrets .claude/secrets/telegram.json \
  --events '[
    {"id":"09","titolo":"Sergio Caputo","tipo":"nuovo","data":"03/07","luogo":"Campo Bruno Reffi","url":"https://visitsanmarino.com/eventi/sergio-caputo-2026"},
    {"id":"08","titolo":"Borgo in Festa","tipo":"nuovo","data":"03-05/07","luogo":"Borgo Maggiore","url":"https://usc.sm/eventi/borgo-in-festa-2026"},
    {"id":"07c","titolo":"Bagno Sonoro","tipo":"dubbio","data":"03/07","luogo":"da verificare","url":"https://visitsanmarino.com/eventi/bagno-sonoro"}
  ]'
```

Lo script stampa l'esito di ogni messaggio (✅/❌). Se un messaggio fallisce, lo segnala
ma continua con gli altri. Riporta in chat l'output dello script.

Se **non ci sono eventi non-invariati**, chiama lo script con `--events '[]'`:
manda solo il riepilogo "✅ Nessuna novità questa settimana" e non crea pulsanti.

### Step 5 — Aggiorna il calendario pubblico (sito)
Se ci sono eventi non-invariati (Step 3b) → lancia tu stesso **`/smh-sito`** (Skill tool)
per riallineare `sito/calendario-eventi.html`: aggiungere i nuovi, togliere
cancellati/passati, aggiornare date/orari/link cambiati. Segui integralmente le regole
di `sito/STATO-SITO.md` (letture obbligatorie, niente link ad aggregatori, pagina resta
**offline/privata** — questo step aggiorna solo l'anteprima, non pubblica nulla). Usa
solo dati già verificati in questo giro, non inventare nulla di nuovo.
Se **non ci sono novità** → salta questo step senza toccare il sito.
Tieni l'esito (fatto / saltato-nessuna-novità / errore) per il riassunto finale.

### Step 6 — Riassunto finale in chat

⚠️ **Elenca SEMPRE tutti i passi, uno per riga, anche quelli senza risultati.** Un passo
che sparisce dal riassunto è un passo che nessuno si accorge sia stato saltato: è così
che il postino è rimasto fuori dal giro automatico per settimane (fino al 27/07/2026),
lasciando le segnalazioni di Michele a marcire in coda. «Coda vuota» è un esito, il
silenzio no.

```
🟢 SMH — giro del GG/MM/AAAA completato

Integrità:  [✅ tutto a posto / ❌ N file mancanti — elenco]
Export→coda:[✅ nessun orfano / 🔧 N recuperate e messe in coda (date) / ❌ N bloccate dal cancello — motivo]
Copertura:  [✅ / ⚠️ N giorni scoperti CON materiale disponibile — elenco]
1 Ricerca:  N eventi trovati
2 Postino:  N importati dal bot (testo N · foto N) / coda vuota
3 Verifica: ✅ N · ⚠️ N da confermare · 🗑 N scartati
4 Testi:    ✍️ N bozze (GG/MM → GG/MM)
5 Telegram: [OK — N messaggi con pulsanti / ERRORE — dettaglio]
6 Sito:     [aggiornato / saltato — nessuna novità / errore — dettaglio]

🆕 Nuovi: N · ✏️ Modificati: N · 🗑 Cancellati?: N · ⚠️ Dubbi: N
✅ Invariati (silenzio): N
🔁 Ricontrollati alla fonte (eventi entro 21 gg): N — [nessuna sorpresa / elenco]

[SE la verifica ha trovato un evento cambiato che è GIÀ IN CODA:]
🔴 ATTENZIONE — busta in coda con dati superati: <evento> · <cosa è cambiato>
   Buste da correggere: <file in posts/>

Approvazioni attese entro martedì 10:05.
```
⚠️ La riga `🔁` e il blocco `🔴` non sono decorativi: sono l'unico punto in cui
Michele vede che gli eventi già approvati sono stati **ri-guardati alla fonte**
(regola del 30/07, causa: il San Marino Revival rinviato arrivato a un passo dalla
pubblicazione su 4 buste). Se la verifica non li riporta, chiediglieli.

## Regole d'orchestrazione
- **Sequenza rigida**: non lanciare la verifica prima che la ricerca abbia finito, né
  i testi prima della verifica. Ogni anello mangia l'output del precedente.
- **Un subagente alla volta**, mai in parallelo (si passano file tra loro).
- **Non rifare il lavoro dei subagenti**: tu coordini e riassumi, non riscrivi eventi
  o bozze a mano.
- **Fermati con grazia** se un anello produce zero risultati: spiega perché nell'email,
  non proseguire a vuoto e non inventare per riempire.
- Non tocchi grafica/pubblicazione: sono fasi successive, fuori da questo giro.
- Il sito (Step 5) è ormai agganciato alla catena, ma resta comunque offline/privato:
  aggiornarlo non equivale a pubblicarlo.

## Google Sheet calendario eventi
Ogni volta che il giro produce dati sufficienti per aggiornare il calendario su Google Drive,
**crea un nuovo Sheet** — non aggiornare quello esistente. Titolo: `Calendario eventi SMH — AAAA-MM-GG HH:MM`
(data e ora di creazione). Cartella Drive: ID `1tKLBY9QPWfCdlxUUL_rQTfUAKF0TYXMl`, account `michimorri@gmail.com`.
Michele elimina manualmente i vecchi. Per crearlo: `create_file` con `contentMimeType: text/csv`,
`textContent` con le righe del calendario (intestazione + una riga per evento) e `parentId` la
cartella sopra — si converte da solo in Sheet, non serve l'editor Sheets. Se il connector Drive
non è disponibile, segnala a Michele quali righe nuove aggiungere manualmente.

## File di riferimento
- Subagenti: `.claude/agents/smh-postino.md`, `smh-ricerca.md`, `smh-verifica.md`, `smh-testi.md`.
- Skill dei tre anelli: `.claude/skills/smh-ricerca|smh-verifica|smh-testi/SKILL.md`.
- Skill sito: `.claude/skills/smh-sito/SKILL.md` (Step 5).
- `dati/config.json` — parametri condivisi.
