# Canva MCP + validazione — riferimento per smh-grafica

Guida operativa per compilare il design Canva, validare "al contrario" e
notificare Michele. Caricare questo file allo Step 3 del flusso.

---

## Design di lavoro

- **Design ID:** `DAHOLS6Zdpw` — "@sanmarinohappens" (post feed).
- È un **banco di lavoro riutilizzabile, non un archivio**: una volta esportato il
  PNG, la pagina può essere sovrascritta al giro dopo. Il PNG salvato ha la data
  evento nel nome, quindi non si perde nulla.
- Al 02/07/2026 il design ha **10 pagine** template (post giornalieri). Il numero
  reale va sempre riletto da Canva (`read-design`, campo `design_metadata`) e
  confrontato con `totale_pagine` in `dati/grafica-stato.json`.

## Elementi del template (post feed) — campi che smh-grafica compila

Struttura tipica di una pagina post giornaliero. **Gli element_id cambiano da
pagina a pagina**: NON fidarsi di questi valori a memoria, rileggere sempre gli
element_id reali della pagina in lavorazione con `read-design` **a transazione
aperta** (vedi sotto: senza transazione i locator_id non compaiono) e mappare per
posizione/ruolo.

| Campo | Contenuto esempio | Note |
|-------|-------------------|------|
| Giorno | "Venerdì" | ⚠️ SEMPRE calcolato in Python dalla data (vedi sotto) |
| Data | "3 Luglio" | giorno numerico + mese in lettere |
| Nome evento | "Sergio Caputo" | font grande viola |
| Luogo | "Campo Bruno Reffi" | nome ufficiale, mai la frazione |
| Ora | "ore 21:15" | se disponibile |

Element_id noti del **template base** (solo come riferimento di partenza, verificare
sempre quelli reali della pagina):
- Giorno: `PBRDMgqj0wFV7ZLL-LBNBYKJ7bqLwkK66`
- Data: `PBRDMgqj0wFV7ZLL-LBrJp4GTGX5s6spZ`
- Nome evento: `PBRDMgqj0wFV7ZLL-LBc06rXvkPck7DgT`
- Luogo: `PBRDMgqj0wFV7ZLL-LBs6kDBb9rwTKknr`
- Ora: `PBRDMgqj0wFV7ZLL-LB3r6Yzc87rkdBRt`

Elementi **fissi da NON toccare**: sottotitolo "Cosa succede in Repubblica?",
handle @sanmarinohappens, CTA "👉 Per tutti gli eventi di oggi guarda le stories",
logo, sfondo.

## Calcolo del giorno della settimana — REGOLA FISSA

I file sorgente riportano solo la data numerica. Il nome del giorno va SEMPRE
calcolato in Python, MAI dedotto a mente (errore reale già accaduto: scritto
"Giovedì" al posto di "Venerdì").

```python
import datetime
GIORNI = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
MESI = ["","Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno",
        "Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]
d = datetime.date(2026, 7, 3)
giorno = GIORNI[d.weekday()]          # -> "Venerdì"
data_estesa = f"{d.day} {MESI[d.month]}"   # -> "3 Luglio"
```

## Regole di composizione (dal formato-grafica)

- Nome evento corto (1 parola, ≤10 char) ~160px · nome lungo (2+ parole) ~120px.
- Un a-capo naturale tra parole (es. "Le / Vibrazioni") va bene; da evitare è
  l'a-capo a metà parola (es. "VIBRA-/ZIONI"): in quel caso ridurre il font.
- Partite sport formato "vs": "Team A\nvs\nTeam B" su tre righe. Attenzione: righe
  in più espandono la text box e possono sovrapporre luogo/ora. **L'API SÌ che
  riposiziona** (operazione `position_element` dentro `edit-design`, con `top`/`left`)
  e può anche cancellare elementi (`delete_element`): quindi le sovrapposizioni si
  possono sistemare spostando gli elementi, non solo passando la palla a Michele.
  Le forme (linee divisorie) si possono cancellare ma **non ricreare** → per questo
  gli aggregati si compilano su una COPIA del template (vedi SKILL.md), così il
  master resta con tutte le righe.
- **Mai** prezzi / "gratuito" / URL nell'immagine.

---

## Sequenza operativa MCP (compilazione)

⚠️ **I nomi dei tool Canva MCP sono cambiati (constatato il 28/07/2026).**
`start-editing-transaction`, `get-design-pages`, `get-design-content` e
`perform-editing-operations` **non esistono più**. Oggi ci sono **due soli tool**:
`read-design` (legge e apre la transazione) e `edit-design` (modifica e chiude la
transazione). Se trovi ancora i vecchi nomi in un file del progetto, è documentazione
vecchia: correggila.

| Cosa serve fare | Come si fa oggi |
|-----------------|-----------------|
| Contare le pagine | `read-design` → `filter.fields: ["design_metadata"]` |
| Aprire la transazione | `read-design` con `open_transaction: true` → restituisce `transaction_id` |
| Leggere gli element_id | `read-design` **a transazione aperta**: `design_content` diventa il CDF con i `[locator_id]` |
| Scrivere i campi | `edit-design` con `transaction_id` + `page_index` + `operations` |
| Vedere l'anteprima delle modifiche non ancora salvate | `read-design` passando il `transaction_id` + `filter.fields: ["thumbnails"]` |
| Salvare | `edit-design` con `finalize: "commit"` e **operations vuoto** |
| Annullare tutto | `edit-design` con `finalize: "cancel"` e **operations vuoto** |

**Sequenza:**
1. `read-design` sul design (es. `DAHOLS6Zdpw`) con `open_transaction: true`
   → prendi `transaction_id` e i `locator_id` reali delle pagine che ti servono.
   Il `locator_id` (forma `PBxxx-LByyy`) è ciò che va messo come `element_id`.
2. Per **ogni pagina** da compilare: una chiamata `edit-design` con
   `transaction_id`, `page_index` (1-based) e le `operations` con i 5 campi
   (`replace_text` su giorno, data, nome evento, luogo, ora).
   ⚠️ **Tutte le operazioni di una chiamata devono stare sulla stessa pagina**:
   più pagine = più chiamate. Il `finalize` resta `keep_open` (è il default).
3. **Validazione PRIMA del commit** (vedi sotto): rileggi con `read-design` +
   `transaction_id` — così vedi le modifiche non ancora salvate.
4. `edit-design` con `finalize: "commit"` e nessuna operazione. **Irreversibile.**

⚠️ **Non si possono combinare `operations` e `finalize: "commit"/"cancel"` nella
stessa chiamata**: la chiamata viene rifiutata. Prima si modifica, poi si chiude.

Se qualcosa va storto a metà: `edit-design` con `finalize: "cancel"` (operations
vuoto) e segnala a Michele, non lasciare il design in stato incoerente.

**Campi da rispecchiare da `read-design`:** `edit-design` accetta `is_responsive`,
`is_empty` e `is_editable` — vanno riportati come li dichiara `read-design` per
quella pagina. Una pagina marcata `(NON-EDITABLE)` rifiuta l'intero blocco di
operazioni.

---

## Validazione — "controllo al contrario" (prima rete)

Serve a intercettare un errore di TRASCRIZIONE di Claude su Canva, non del sorgente.
Il controllo normale guarda il sorgente; questo guarda l'OUTPUT contro il sorgente.

💡 **Meglio PRIMA del commit che dopo.** Con l'API attuale si può rileggere la
pagina modificata ma non ancora salvata (`read-design` col `transaction_id` della
transazione aperta): se un campo non torna si annulla con `finalize: "cancel"`
invece di lasciare una pagina sbagliata sul design. Se il commit è già stato fatto,
la validazione si fa lo stesso — cambia solo che la pagina sbagliata resta lì.

Per ogni pagina compilata:
1. Rileggi il contenuto reale della pagina via `read-design` (col `transaction_id`
   se la transazione è ancora aperta, altrimenti senza).
2. Confronta **campo per campo** col post approvato sorgente:
   - Giorno → deve combaciare col giorno calcolato in Python dalla data.
   - Data (numero + mese) → uguale al sorgente.
   - Nome evento → uguale (a meno di a-capo estetici).
   - Luogo → uguale (nome ufficiale).
   - Ora → uguale.
3. Ogni discrepanza va **elencata nel messaggio Telegram** a Michele (pagina + campo
   + valore Canva vs valore atteso), così sa dove guardare.

⚠️ Questa validazione **decide da sola** (dal 14/07/2026 non c'è più un checkpoint
umano prima dell'export): pagina pulita → si esporta subito; pagina con
discrepanza netta → NON si esporta, resta su Canva così com'è e si segnala
chiaramente su Telegram/chat (es. "⚠️ pag. 13: giorno = «Giovedì» ma il 10/07 è
Venerdì"), mentre le altre pagine proseguono normalmente.

---

## Export PNG (subito dopo la validazione, per ogni pagina pulita)

- ⚠️ **Prima di esportare va chiamato `get-export-formats` su quel design**: è
  obbligatorio e l'export fallisce se si tira a indovinare il formato.
- `export-design` sulle sole pagine che hanno superato la validazione, formato
  **PNG**, qualità **pro** (`format: { type: "png", export_quality: "pro",
  pages: [n] }`).
- ⚠️ I link di export Canva **scadono in fretta**: scaricare i PNG SUBITO con `curl`.
- Nome file: `AAAAMMGG_<Tipo>.png` (AAAAMMGG = data evento/pubblicazione secondo il
  tipo), cartella del tipo in `marketing/3 Export/` (vedi SKILL.md, tabella
  "Cartelle di export"). Es. `20260703_Post giornaliero.png`.
- Controllo sanità: se un file scaricato è ~3KB il link era già scaduto → riesportare
  quella pagina.

---

## Notifica Telegram — SOLO testo

- Credenziali in `.claude/secrets/telegram.json` (`bot_token`, `chat_id`).
- **Un solo messaggio a fine giro**, sempre (anche se tutto ✅): elenco PNG
  esportati + eventuali pagine saltate per discrepanza o errore Canva → API `sendMessage`.
- ⚠️ **NON inviare i PNG su Telegram** (niente `sendPhoto`): decisione di Michele
  (02/07/2026) — le immagini occupano spazio inutilmente in chat. I PNG restano
  solo esportati sul Mac.
- Se l'invio fallisce, riprova una volta, poi continua comunque e segnalalo nel
  riassunto in chat (è l'unica notifica quando il giro parte da un task pianificato).

Esempio conferma finale:
```bash
curl -s "https://api.telegram.org/bot{TOKEN}/sendMessage" \
  -d chat_id="{CHAT_ID}" \
  -d text="✅ Esportati 3 post giornalieri sul Mac → marketing/Post giornalieri/"
```
