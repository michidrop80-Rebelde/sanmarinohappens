# 03 — Portare nel repo pubblico i file che al clone mancano

Type: task
Status: aperto
Blocked by: 01
Modello: Sonnet — meccanico, ma serve un occhio sui segreti prima di pubblicare
Sforzo: breve (mezza sessione)

## Domanda

`scripts/controllo-integrita.py` dà **✅ 129 su 129 sul Mac** e **❌ 8 assenti su un clone pulito**.
Due sono i segreti e mancano giustamente. Gli altri sei sono file veri che le skill citano e che
sul clone non esistono:

- `dati/config.json` — la configurazione condivisa, citata da 6 skill
- **`dati/fonti-sport.md`** — la mappa delle fonti sportive (senza, il giro in cloud cerca eventi
  senza sapere dove sta lo sport)
- `references/formato-grafica.md`
- `docs/FIX-APPROVAZIONI-CHE-SCADONO.md`
- `sito/STATO-SITO.md`
- `sito/calendario-eventi.html`

**Da fare:** aprire i sei file, verificare che nessuno contenga segreti o dati personali, poi
metterli dove il ticket 01 ha deciso.

⚠️ **Il ticket 01 ha allargato questo lavoro (07/09/2026).** Non sono sei file: sono **61**. Il
ticket 01 ha scoperto che tutta la memoria di lavoro della catena non e' mai stata committata (non
e' esclusa da nessuna regola: e' solo rimasta `??` per mesi) e ha deciso che va **tutta nel repo
pubblico**. L'elenco preciso di cosa entra e dei **tre file che restano fuori** (due guide con
l'email personale di Michele; `fonti-sport.md` entra ma **ripulito** dalla password `RBA25`) sta
nella risposta del ticket 01 — leggerlo prima di cominciare.

**Fatto quando:** si clona il repo in una cartella temporanea, si lancia lì
`python3 scripts/controllo-integrita.py`, e dà ✅.

**In più:** aggiungere quel controllo-sul-clone come guardia automatica, così non può ricapitare.
Oggi la guardia guarda il disco dove gira, e sul Mac i file ci sono sempre — per questo nessuno se
n'era accorto in due mesi.

## Comments

- 06/09/2026 (dalla sonda, ticket 05) — Confermato **in ambiente cloud vero** (non un clone locale):
  `controllo-integrita.py` esce **1** su GitHub Actions. Elenco visto dal runner:
  `dati/config.json`, `dati/fonti-sport.md`, `references/formato-grafica.md`,
  `docs/FIX-APPROVAZIONI-CHE-SCADONO.md`, `sito/STATO-SITO.md`, `sito/calendario-eventi.html`
  (i sei di questo ticket) **+** `.claude/secrets/github.json`, `.claude/secrets/telegram.json`
  **+ la cartella `~/.claude/scheduled-tasks`** (assente sul runner: `/home/runner/.claude/...`).
  → Oltre a portare dentro i sei file, la guardia va **resa consapevole dell'ambiente**: in cloud i
  `.claude/secrets/*` non esisteranno MAI (giustamente) e `~/.claude/scheduled-tasks` non ha senso.
  Quei riferimenti vanno esclusi quando gira fuori dal Mac, altrimenti la guardia sarà sempre rossa.
