# 11 — I 45 percorsi assoluti che il cloud non trova

Type: task
Status: risolto
Blocked by: —
Risolto: 07/09/2026 · commit `6735f8f`
Modello: Sonnet — è lavoro meccanico e verificabile
Sforzo: media (una sessione) — 45 modifiche, ma ognuna va provata, non solo sostituita

## Domanda

Le skill e gli agenti contengono **41 percorsi assoluti `/Users/michele/Desktop/PROGETTI/...`
sparsi in 13 file** fra skill e agenti, **piu' altri 4 negli script** (`backup-cervello.sh`,
`recupera-da-transcript.py` e — proprio lui — `controllo-integrita.py`, cioe' una delle guardie).
Su un computer in cloud quella cartella non esiste: ogni comando che la usa fallisce.
Verificato il 06/09/2026 con `grep -ro "/Users/michele" .claude/skills .claude/agents scripts`.

È il blocco più concreto emerso dalla ricerca del ticket 02 — più concreto di qualsiasi limite
della piattaforma.

**Da fare:** sostituirli con percorsi relativi alla cartella del progetto (o una variabile che vale
sia sul Mac sia in cloud), **senza rompere niente sul Mac**.

**Fatto quando:**
- `grep -ro "/Users/michele" .claude/skills .claude/agents scripts` non trova più nulla
- una catena lanciata dal Mac funziona ancora identica (prova vera, non ragionamento)
- gli stessi comandi funzionano dentro un clone in una cartella con un altro nome

⚠️ Attenzione ai casi in cui il percorso assoluto **serviva**: `.claude/secrets/` e i task
pianificati (che ereditano la cartella dalla sessione che li ha creati). Vanno guardati uno per uno,
non sostituiti in blocco.

## Risposta

**Fatto.** I 45 percorsi (erano 45, non 41: la ricerca del ticket 02 ne contava 41 nei soli
file .md, più 4 negli script) tolti da **16 file** — 6 skill, 7 agenti, 3 script. Commit `6735f8f`.

**Come sono stati sostituiti** (una forma diversa per ogni caso d'uso, non un cerca-e-sostituisci
cieco):

| dove | prima | dopo | perché regge in cloud |
|---|---|---|---|
| blocchi `bash` (13 `cd`) | `cd "/Users/michele/.../San Marino Happens"` | `cd "$(git rev-parse --show-toplevel)"` | git trova la radice del repo da qualsiasi sottocartella, su qualsiasi macchina, anche in un clone con un altro nome |
| `REPO=...` in smh-pubblica | path assoluto | `REPO="$(git rev-parse --show-toplevel)"` | idem |
| lettura token GitHub inline (3 volte) | `open('/Users/.../.claude/secrets/github.json')` | `open(<git toplevel>/.claude/secrets/github.json)` via `subprocess` | non dipende più dalla cartella di lavoro corrente; sul Mac punta al file vero, in cloud il file non c'è ma quei blocchi sono comunque solo-Mac (il cloud non tocca i segreti — ticket 07) |
| prosa «## Base del progetto» | `` `/Users/.../San Marino Happens` `` | «la radice del repo (sul Mac `~/Desktop/PROGETTI/San Marino Happens`, in GitHub Actions il checkout)» | è una descrizione, non un percorso: dice a Claude dov'è senza inchiodarlo a una macchina |
| rimandi a `SKILL.md` negli agenti | path assoluto alla skill | `.claude/skills/smh-<x>/SKILL.md` (relativo alla radice) | il runner fa il checkout nella radice |
| `recupera-da-transcript.py` | `"/Users/michele/.claude/projects"` · `BASE="/Users/.../San Marino Happens/"` | `os.path.expanduser("~/.claude/projects")` · `BASE` derivato da `__file__` | è uno strumento di recupero solo-Mac, ma ora non si rompe se il Mac o la cartella cambiano nome |
| `backup-cervello.sh` | `PROGETTO="/Users/.../San Marino Happens"` | `PROGETTO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"` | il path si ricava da dove sta lo script |
| `controllo-integrita.py` (regex, riga 46) | prefisso `/Users/.../San Marino Happens/` **opzionale** nel pattern che scandaglia il testo delle skill | prefisso rimosso | non serve più: nel testo delle skill non ci sono più percorsi assoluti da assorbire. La costante `PROGETTO` di questo script era **già** relativa (`Path(__file__).resolve().parent.parent`) |

**I tre «Fatto quando» verificati:**

1. ✅ `grep -ro "/Users/michele" .claude/skills .claude/agents scripts` → **niente**.
2. ✅ **catena dal Mac ancora identica**: `controllo-integrita.py` (la guardia che legge tutto il
   grafo skill↔agenti↔file) resta **verde, 129/129 riferimenti**. Non ho lanciato un giro completo
   ricerca→testi (costa token veri e traffico web per zero informazione in più: le modifiche sono
   `cd` e descrizioni, non logica).
3. ✅ **clone rinominato**: clonato il repo in `/tmp/smh-rinominato-test`, applicata la patch, gli
   script compilano e girano, `git rev-parse --show-toplevel` risolve giusto, nessun percorso
   assoluto residuo. `controllo-integrita.py` lì esce 1 — ma **per gli 8 file mai committati**
   (`.claude/secrets/*`, `dati/config.json`, `dati/fonti-sport.md`, ecc.): è **esattamente il
   ticket 03**, non questo.

**Fuori dal recinto di questo ticket** (grep del ticket = `.claude/skills .claude/agents scripts`):
- `.claude/task-pianificati/*` — copie-appunti dei due task locali. Contengono ancora percorsi
  assoluti, ma questa mappa **spegne** quei task (ticket 10): non vale la pena toccarli.
- `.claude/scripts/telegram-listener.py` — non tracciato da git (non arriva in cloud) e il percorso
  è dentro un esempio «USO LOCALE (test)». Lasciato com'è.
- `.claude/settings.local.json` e `.claude/worktrees/` — allowlist permessi locali e worktree
  usa-e-getta: per natura legati a questa macchina.
