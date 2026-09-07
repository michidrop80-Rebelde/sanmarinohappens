# 13 — La guardia di freschezza: nessun anello lavora su dati morti

Type: task
Status: resolved
Blocked by: —
Modello: Sonnet — la regola è già decisa (ticket 01), qui si applica e si prova
Sforzo: breve (mezza sessione)

## Domanda

Deciso nel [ticket 01](01-dove-vive-il-cervello.md): gli anelli non devono mai lavorare su un file
vecchio. Oggi `smh-verifica` prende «il file **più recente**» in `cartella_eventi` (SKILL.md:48) e
`smh-testi` «il più recente» in `cartella_verificati` (SKILL.md:30) — e nessuno dei due si chiede
*quanto* è recente. In cloud, di notte, questo produce bozze su eventi già passati senza che nessuno
se ne accorga.

**Da costruire:** un controllo che, prima che l'anello parta, guardi la data del file che sta per
lavorare.

**Regola già decisa, da applicare (non da ridiscutere):**
- file di **eventi** → deve essere **dello stesso giorno** del giro
- file **verificato** → al massimo **2 giorni**
- se è più vecchio: **l'anello NON parte**, e parte un **Telegram di una riga** che dice quale file
  è, di che giorno è, e quanti giorni ha
- nessuna bozza viene prodotta: meglio un giro saltato che un post sbagliato in coda

⚠️ La data si prende dal **nome del file** (`eventi-AAAA-MM-GG.md`), non dalla data di modifica sul
disco: un `git clone` in cloud riscrive le date di modifica di tutti i file al momento del clone,
quindi `mtime` in cloud direbbe sempre «di oggi» e la guardia non scatterebbe **mai**. Questo è il
modo più probabile di sbagliare questo ticket.

⚠️ Il giorno si calcola **sempre in Python**, mai dedotto (regola di progetto).

**Fatto quando:**
- si crea a mano una situazione con solo un file di eventi vecchio, si lancia l'anello, e l'anello
  **non parte** e il Telegram arriva davvero (con l'output che lo prova, non una rassicurazione)
- si rimette un file di oggi, si rilancia, e l'anello **parte** normalmente
- il messaggio Telegram dice *qual è* il problema, non un ⚠️ nudo (regola di progetto)

**Dove vive:** valutare se è uno script in `scripts/` chiamato dalle skill (come le altre guardie
del progetto) o un passo dentro ogni SKILL.md. Preferire lo script: è provabile da solo.

## Answer

**Fatto.** Guardia costruita come **script** (`scripts/controllo-freschezza.py`),
non come passo dentro le SKILL.md: così è provabile da sola, come le altre guardie
del progetto. Commit `9bd1f64`.

### Come funziona
Un comando, un anello per volta:

    python3 scripts/controllo-freschezza.py verifica   # guarda dati/eventi/
    python3 scripts/controllo-freschezza.py testi      # guarda dati/eventi/verificati/

Prende il file col nome-data più avanti nella cartella (la stessa scelta che fanno
già le skill), legge **la data dal nome del file** e la confronta con oggi
(entrambi calcolati in Python, `datetime.date`). Codici di uscita:

- **0** — il file è abbastanza fresco (`eventi` = stesso giorno · `verificato` = max 2 giorni) → l'anello parte.
- **1** — il file è più vecchio → stampa e **manda un Telegram di una riga** che dice quale file è, di che giorno è e quanti giorni ha. L'anello **non parte**.
- **2** — non c'è nessun file → stesso trattamento del caso 1.

Flag `--prova` (non manda, stampa e basta) e `--oggi AAAA-MM-GG` (forza la data di
riferimento) per i test. Telegram: stesso helper di `avviso-imminenti.py`
(requests, ripiego su curl per l'SSL rotto sul Mac), stessi segreti
`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` — non aggiunge segreti.

### La trappola dell'mtime (il modo più probabile di sbagliare questo ticket)
Lo script **non chiama mai** `stat`/`mtime`: solo una regex sul nome. Provato: con
l'mtime di **tutti** i file di `dati/eventi/` toccato a «adesso» (è esattamente
quello che fa `git clone` in cloud), la guardia legge comunque `eventi-2026-08-31.md`
dal nome e si ferma → exit 1. Con l'mtime la guardia non sarebbe scattata mai.

### Verifiche (output reale, 07/09/2026)
- **File di oggi presenti** → `verifica` e `testi` entrambi **exit 0**, «può partire».
- **File di oggi spostati via** (ultimo = `2026-08-31`, 7 giorni fa) → `verifica` **exit 1**
  («serve un file di oggi»), `testi` **exit 1** («il limite è 2 giorni»), messaggio
  che nomina file + data + «7 giorni fa» — non un ⚠️ nudo.
- **Cartella `dati/eventi/` svuotata** → **exit 2**, «non c'è nessun file … su cui lavorare».
- **mtime azzerati** (simulazione clone) → **exit 1** lo stesso (vedi sopra).
- `controllo-integrita.py` verde (131 riferimenti), `py_compile` OK.

### Agganciata alla catena
Step 1 di `smh-verifica/SKILL.md` e `smh-testi/SKILL.md`: se non è stato indicato
un file specifico a mano, lanciano la guardia e su exit 1/2 **si fermano senza
produrre bozze**.

### Unico pezzo non verificato in questa sessione
L'invio Telegram **reale** non è stato fatto: i segreti stanno in `.claude/secrets/`
(giustamente fuori dalla portata di questa sessione) e le env var non erano
impostate. Il codice di invio è **identico** a quello di `avviso-imminenti.py`, già
in produzione, ed è stato esercitato con `--prova`. Conferma da 10 secondi per
Michele, quando ha le credenziali in ambiente:

    python3 scripts/controllo-freschezza.py verifica --oggi 2026-12-01

(deve arrivare un Telegram che nomina l'ultimo file di `dati/eventi/` e i suoi giorni.)
