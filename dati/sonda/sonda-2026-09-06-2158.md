# Esito sonda di prova — ambiente GitHub Actions

**Data e ora:** 2026-09-06 21:58 UTC

## 1. Evento vero dal registro (dati/calendario/master.md)

**San Marino Antiqua 2026** — 24-26/07/2026, Centro Storico, Città di San Marino
(rievocazione storica, 800 figuranti — riga 31 del registro, stato "concluso/approvato").

Il file è leggibile e contiene il registro master completo di San Marino Happens (270 righe).

## 2. Ricerca web (visitsanmarino.com eventi San Marino settembre 2026)

La ricerca ha restituito risultati sensati e pertinenti: link diretti a visitsanmarino.com,
sanmarinortv.sm, sanmarinosite.com, e un riepilogo testuale di eventi di settembre 2026
(es. "Dal Turista al Contadino" 04-06/09, tributo a Morricone 08/09, Bunta's Car Meeting,
MotoGP a Misano 11-13/09) coerenti con quanto già presente nel registro master.

## 3. Guardia di progetto (scripts/controllo-integrita.py)

**Codice di uscita: 1**

Nessun problema di percorso assoluto tipo `/Users/michele/...` (il ticket 11 citato nelle
istruzioni non si è manifestato in questa esecuzione). Il fallimento è di natura diversa:
lo script segnala **9 file citati dalle istruzioni di progetto (SKILL.md/agents) ma assenti
dal disco**, tra cui:

- `.claude/secrets/github.json`, `.claude/secrets/telegram.json`
- `dati/config.json`, `dati/fonti-sport.md`
- `references/formato-grafica.md`
- `sito/STATO-SITO.md`, `sito/calendario-eventi.html`
- `docs/FIX-APPROVAZIONI-CHE-SCADONO.md`
- `/home/runner/.claude/scheduled-tasks` (cartella intera assente)

Lo script suggerisce di recuperarli dai transcript delle sessioni con
`scripts/recupera-da-transcript.py`, ma questo esula dai compiti della sonda.

## Giudizio

**Si rompe qui:** l'ambiente GitHub Actions può leggere il registro, fare ricerche web e
lanciare la guardia — ma la guardia stessa fallisce (exit 1) perché mancano su questo
ambiente diversi file che il progetto si aspetta (segreti Telegram/GitHub, config, file del
sito, cartella scheduled-tasks). Non è il problema del percorso assoluto `/Users/michele/...`
(ticket 11): è un problema di file/segreti mancanti in questo ambiente cloud, da risolvere
prima che la catena vera possa girare qui.
