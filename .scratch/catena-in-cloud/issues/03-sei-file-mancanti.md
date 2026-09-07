# 03 — Portare nel repo pubblico i file che al clone mancano

Type: task
Status: resolved
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

## Answer

**Fatto il 07/09/2026. Commit `2b67c1c` sul repo pubblico.**

### Cosa è entrato

Seguita la lista del ticket 01 (non 6 file: 63). Nel repo pubblico ora ci sono:

- **i 6 file citati e mancanti dal clone:** `dati/config.json`, `dati/fonti-sport.md`,
  `references/formato-grafica.md`, `docs/FIX-APPROVAZIONI-CHE-SCADONO.md`, `sito/STATO-SITO.md`,
  `sito/calendario-eventi.html`
- **l'output della catena:** `dati/eventi/` (12), `dati/eventi/verificati/` (12), `dati/post/` (28),
  `dati/post/approvati/` (10), `dati/telegram/pending/` (6)
- `dati/diario-giro-prova-2026-07-11.md`, `dati/metriche-social.md`, `dati/prompt-sessione-6.md`

### Cosa è rimasto fuori (deciso, vedi ticket 01)

- 🚫 `dati/guida-anello6-facebook.md` e `dati/guida-anello6-tappa1-setup-account.md` — email
  personale di Michele, non servono alla catena. Restano solo nel cervello privato.
- ⚠️ `dati/fonti-sport.md` è entrato **ripulito**: la password Sportity `RBA25` (riga 101,
  password *e* codice canale nella URL) sostituita con `chiedere a Michele`, URL troncata al
  `/channel/`.
- `.claude/secrets/*` — mai nel repo.

### Verifica segreti

Cercati token / password / chat_id / email personali su tutti i 63 file. Nessuno:
i `pending/*.json` hanno solo `giro_id` / `sent_at` / `eventi`; le uniche email trovate nei file
eventi (`consorzioterradisanmarino@gmail.com`, `info.artistincasa@gmail.com`) sono **contatti
pubblici degli organizzatori**, parte legittima del dato evento.

### La guardia resa consapevole dell'ambiente (dal commento della sonda)

`scripts/controllo-integrita.py`: se gira fuori dal Mac (`GITHUB_ACTIONS=true`, oppure manca la
cartella `.claude/secrets/`) allora **non** cerca `~/.claude/scheduled-tasks` e **tollera** i
`.claude/secrets/*.json` — in Actions i segreti sono variabili d'ambiente, non file, e quei
riferimenti terrebbero la guardia sempre rossa. Sul Mac il comportamento non cambia.

### La guardia automatica sul clone (il «In più» del ticket)

Nuovo workflow **`.github/workflows/guardia-integrita.yml`**: gira a ogni push su `main` (il
checkout di Actions *è* un clone pulito), una volta a settimana (lun 05:40) e a mano. Se un file
citato manca dal repo → workflow **rosso** + **Telegram** via `scripts/avviso-integrita.py`.
L'invio Telegram (requests + ripiego su curl) è stato estratto in `scripts/telegram_helper.py`,
un posto solo, così non invecchiano copie diverse.

### Prova che chiude il ticket

- Sul Mac: `python3 scripts/controllo-integrita.py` → ✅ 131/131, exit 0
- Modalità cloud simulata (`GITHUB_ACTIONS=true`): ✅ 113/113, exit 0
- **Su GitHub Actions (clone vero):** run
  [#34148842889](https://github.com/michidrop80-Rebelde/sanmarinohappens/actions/runs/34148842889)
  su commit `2b67c1c` — job *Guardia integrità*, step «Il clone è tutto intero?» → **success**.

### Coda

- Node 20 deprecato su `checkout@v3` / `setup-python@v4` negli **altri** workflow del repo — resta
  nel fog della mappa. Il nuovo workflow usa già `@v4` / `@v5`.

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
