#!/bin/bash
#
# backup-cervello.sh — salva il "cervello" di San Marino Happens su un repo GitHub PRIVATO
# ============================================================================================
#
# COS'E' (spiegato semplice)
# --------------------------
# La cartella "San Marino Happens" e' gia' un repo git: quello PUBBLICO
# (github.com/michidrop80-Rebelde/sanmarinohappens), su cui girano le GitHub Actions
# che pubblicano su Instagram e Facebook. Quel repo NON va toccato.
#
# Ma meta' del progetto — i dati, le skill, le istruzioni — non e' mai stata dentro quel
# repo: viveva solo sul Mac. Il 25/07/2026 un `rm -rf` l'ha distrutta (105 file).
#
# Questo script aggiunge un SECONDO repo, PRIVATO, che versiona SOLO quella meta'.
# Non copia i file da nessuna parte: usa gli stessi file al loro posto, ma con una
# "cartella .git" separata, tenuta FUORI dal progetto (in ~/.smh-cervello.git) proprio
# per non confondersi con quella pubblica.
#
# Risultato: due repo che convivono senza pestarsi i piedi.
#   - git normale nella cartella  -> repo PUBBLICO (posts/, marketing/, scripts/...)
#   - questo script               -> repo PRIVATO  (dati/, skill, CLAUDE.md, ...)
#
# COSA SALVA
# ----------
#   CLAUDE.md, ULTIMO_REPORT.md, dati/, references/, docs/, sito/, scripts/,
#   .claude/skills/, .claude/agents/, .claude/scripts/
#
# COSA NON SALVA MAI (e c'e' un controllo automatico che blocca tutto se ci provasse)
# ------------------
#   .claude/secrets/           <- token Telegram, GitHub, Meta
#   .claude/settings.local.json <- contiene token in chiaro
#   marketing/ posts/ archivio/ queue/ metriche/  <- roba del repo pubblico o binari
#
# COME SI USA
# -----------
#   bash scripts/backup-cervello.sh              # salva e manda su GitHub
#   bash scripts/backup-cervello.sh --prova      # mostra solo cosa salverebbe, non tocca nulla
#
set -euo pipefail

# ---------------------------------------------------------------------------- configurazione
PROGETTO="/Users/michele/Desktop/PROGETTI/San Marino Happens"
GITDIR="$HOME/.smh-cervello.git"
REMOTO="https://github.com/michidrop80-Rebelde/sanmarinohappens-cervello.git"
RAMO="main"

SOLO_PROVA=0
[ "${1:-}" = "--prova" ] && SOLO_PROVA=1

# comodita': "gitp" = git del repo privato (p = privato)
gitp() { git --git-dir="$GITDIR" --work-tree="$PROGETTO" "$@"; }

cd "$PROGETTO"

# ------------------------------------------------------------- 1. crea il repo se non c'e'
if [ ! -d "$GITDIR" ]; then
  echo "→ Primo avvio: creo il repo privato in $GITDIR"
  git init --bare "$GITDIR" >/dev/null
  gitp config core.bare false
  gitp config core.worktree "$PROGETTO"
  gitp symbolic-ref HEAD "refs/heads/$RAMO"
fi

# identita' di chi firma i commit (il Mac non ne ha una globale)
gitp config user.name  "Michele (San Marino Happens)"
gitp config user.email "michidrop80@gmail.com"
# lo stesso fix che serviva al repo pubblico: buffer da 1 MB troppo piccolo -> HTTP 400
gitp config http.postBuffer 524288000
gitp config http.version HTTP/1.1

# ------------------------------------------------- 2. la lista di cosa entra e cosa no
# Questo file e' la regola: prima escludo TUTTO (`/*`), poi riammetto solo le voci volute.
# Viene riscritto a ogni esecuzione, cosi' se si rovina si ripara da solo.
cat > "$GITDIR/info/exclude" <<'REGOLE'
# --- Repo PRIVATO "cervello" — generato da scripts/backup-cervello.sh, non modificare a mano
# Regola: tutto escluso, tranne cio' che e' riammesso con "!"
/*

!/CLAUDE.md
!/ULTIMO_REPORT.md
!/dati/
!/references/
!/docs/
!/sito/
!/scripts/

# di .claude entrano SOLO skills/, agents/, scripts/ e la copia dei task pianificati
!/.claude/
/.claude/*
!/.claude/skills/
!/.claude/agents/
!/.claude/scripts/
!/.claude/task-pianificati/
.claude/scripts/__pycache__/

# --- barriere di sicurezza (ridondanti ma esplicite): questi non devono entrare MAI
.claude/secrets/
**/.claude/secrets/
.claude/settings.local.json
**/settings.local.json
*.env

# appartiene al repo PUBBLICO, non a questo
/published.log
REGOLE

# ------------------------------------------- 2-bis. i task pianificati entrano nel backup
# I task in ~/.claude/scheduled-tasks/ vivono FUORI dalla cartella del progetto, quindi
# nessuno dei due repo li vedeva: non erano protetti da niente. Il 27/07/2026 uno di loro
# conteneva una copia congelata dell'orchestratore e per settimane ha fatto girare un giro
# monco — se quel file si perde o si corrompe, non c'e' modo di accorgersene ne' di tornare
# indietro. Qui se ne fa una copia DENTRO il progetto, che il repo privato poi versiona.
#
# Gli ORARI non stanno nel SKILL.md: stanno in un scheduled-tasks.json dentro il supporto
# dell'app, in un percorso pieno di UUID che cambia. Invece di copiare quel file cosi' com'e'
# se ne ricava un elenco leggibile: per ricreare un task servono il suo prompt e il suo cron.
#
# ⚠️ Di quel json NON si copia il contenuto di `approvedPermissions`: fra le regole ci sono
# comandi `curl` verso API, e un token finito dentro una regola entrerebbe nel backup. Si
# salva solo QUANTE sono. E' la stessa ragione per cui .claude/secrets/ resta fuori.
TASK_SORGENTE="$HOME/.claude/scheduled-tasks"
TASK_COPIA="$PROGETTO/.claude/task-pianificati"

if [ -d "$TASK_SORGENTE" ]; then
  rm -rf "$TASK_COPIA"
  mkdir -p "$TASK_COPIA"
  # -a preserva le date: cosi' `git status` non segnala modifiche che non ci sono
  for cartella in "$TASK_SORGENTE"/*/; do
    [ -f "${cartella}SKILL.md" ] || continue
    nome=$(basename "$cartella")
    mkdir -p "$TASK_COPIA/$nome"
    cp -a "${cartella}SKILL.md" "$TASK_COPIA/$nome/SKILL.md"
  done

  python3 - "$TASK_COPIA" <<'PY'
import glob, json, os, sys

destinazione = sys.argv[1]
schema = os.path.expanduser(
    "~/Library/Application Support/Claude/claude-code-sessions/*/*/scheduled-tasks.json")
trovati = glob.glob(schema)

righe = ["# Task pianificati — orari\n",
         "Generato da `scripts/backup-cervello.sh`. Non modificare a mano.\n",
         "Per ricostruire un task servono due cose: il suo `SKILL.md` (nella cartella qui",
         "accanto) e il suo cron, elencato qui sotto.\n"]

if not trovati:
    # Un file che non si trova deve GRIDARE, non produrre un elenco vuoto che sembra sano.
    righe.append("🛑 **scheduled-tasks.json non trovato**: gli orari qui sotto mancano.\n")
    righe.append(f"Cercato in: `{schema}`\n")
else:
    with open(trovati[0]) as f:
        tasks = json.load(f).get("scheduledTasks", [])
    righe.append(f"Letto da: `{trovati[0]}`\n")
    righe.append("| Task | Cron | Attivo | Cartella di lavoro | Permessi approvati |")
    righe.append("|---|---|---|---|---|")
    for t in tasks:
        righe.append("| `{}` | `{}` | {} | `{}` | {} (contenuto non salvato) |".format(
            t.get("id", "?"),
            t.get("cronExpression") or t.get("fireAt") or "—",
            "sì" if t.get("enabled") else "no",
            t.get("cwd", "—"),
            len(t.get("approvedPermissions") or []),
        ))

with open(os.path.join(destinazione, "ORARI.md"), "w") as f:
    f.write("\n".join(righe) + "\n")
print(f"   task pianificati copiati: {len(glob.glob(os.path.join(destinazione, '*', 'SKILL.md')))}")
PY
else
  echo "⚠️  $TASK_SORGENTE non esiste: nessun task pianificato da salvare."
fi

# ---------------------------------------------------------------- 3. metti in scena i file
# Elenco ESPLICITO: e' questa la lista che comanda davvero. Il file di regole qui sopra
# serve solo a tenere pulito `git status` del repo privato.
# (Nota: non si usa `add -A` liscio perche' il .gitignore della cartella e' condiviso con
#  il repo pubblico e riammetteva published.log, che appartiene a quello pubblico.)
CONTENUTI=(
  CLAUDE.md
  ULTIMO_REPORT.md
  dati
  references
  docs
  sito
  scripts
  .claude/skills
  .claude/agents
  .claude/scripts
  .claude/task-pianificati
)
gitp add -A -- "${CONTENUTI[@]}"

# --------------------------------------- 4. CONTROLLO DI SICUREZZA prima di qualsiasi commit
# Se anche un solo file proibito e' finito in scena, si ferma tutto.
PROIBITI=$(gitp diff --cached --name-only | grep -Ei 'secrets/|settings\.local\.json|\.env$|id_rsa|\.pem$' || true)
if [ -n "$PROIBITI" ]; then
  echo ""
  echo "🛑 FERMO TUTTO: fra i file da salvare ci sono dei SEGRETI."
  echo "$PROIBITI" | sed 's/^/   /'
  echo ""
  echo "   Non ho committato niente. Controlla le regole in $GITDIR/info/exclude"
  gitp reset >/dev/null
  exit 1
fi

# --------------------------------------------------------------------- 5. mostra il bilancio
NUM=$(gitp diff --cached --name-only | wc -l | tr -d ' ')
echo ""
echo "📦 File che finiscono nel repo privato: $NUM"
gitp diff --cached --name-only | sed 's/^/   /' | head -60
[ "$NUM" -gt 60 ] && echo "   ... e altri $((NUM - 60))"
echo ""

if [ "$SOLO_PROVA" = "1" ]; then
  echo "🔍 Prova soltanto (--prova): non ho committato ne' inviato nulla."
  gitp reset >/dev/null
  exit 0
fi

# ----------------------------------------------------------------------- 6. commit e invio
# Nota: anche quando non c'e' niente di nuovo da committare si prosegue lo stesso fino al
# push. Puo' infatti esserci un commit gia' fatto in locale che non e' mai arrivato su
# GitHub (e' successo davvero la prima volta: il repo remoto non esisteva ancora).
if [ "$NUM" = "0" ]; then
  echo "ℹ️  Nessun file cambiato: controllo solo che GitHub sia allineato."
else
  gitp commit -q -m "Backup cervello — $(date '+%Y-%m-%d %H:%M')"
  echo "✅ Commit fatto in locale."
fi

if ! gitp remote get-url origin >/dev/null 2>&1; then
  gitp remote add origin "$REMOTO"
fi

echo "→ Invio su GitHub ($REMOTO)..."
if gitp push -u origin "$RAMO"; then
  echo "🎉 Fatto: il cervello del progetto e' al sicuro su GitHub (repo privato)."
else
  echo ""
  echo "⚠️  Il commit locale c'e' (i file NON sono persi), ma l'invio a GitHub e' fallito."
  echo "    Causa piu' probabile: il repo privato non esiste ancora su GitHub."
  echo "    Crealo qui (vuoto, senza README):  https://github.com/new"
  echo "    Nome esatto: sanmarinohappens-cervello   ·   visibilita': Private"
  exit 1
fi
