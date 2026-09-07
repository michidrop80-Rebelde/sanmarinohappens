#!/usr/bin/env bash
# Chiude una tappa del giro in cloud: salva sul ramo, conta cosa è uscito,
# e dice come è andata.
#
# PERCHE' E' UN FILE A PARTE (ticket 08)
# Le quattro tappe fanno lavori diversi ma finiscono tutte allo stesso modo. Se
# questo pezzo fosse copiato quattro volte nel workflow, una correzione fatta in
# uno e non negli altri sarebbe invisibile — è esattamente il guasto del
# 07/09/2026 (un `git add` sbagliato che restava verde).
# ⚠️ Qui NON si lancia mai l'agente: il passo `claude` resta scritto dentro il
# workflow, sotto gli occhi di `scripts/controllo-token-agente.py`.
#
# USO:  bash .github/scripts/chiudi-tappa.sh <numero> <nome>
# ENV:  DATA (AAAA-MM-GG) · SALTATA (si/no) · ESITO_AGENTE (success/failure/skipped)
#       EXIT_CLAUDE (il codice d'uscita VERO di `claude`, non quello del passo:
#       il passo finisce con un `tail` e sarebbe verde comunque)
# SCRIVE su $GITHUB_OUTPUT: ok · stato · costo · eventi · verificati · bozze

set -euo pipefail

NUM="$1"
NOME="$2"
MARCATORE="dati/cloud-giro/${DATA}/${NUM}-${NOME}.ok"

# --- quanto è costata (dal referto JSON di Claude, non da una stima) ---------
COSTO="0"
if [ -f /tmp/claude-tappa.json ]; then
  COSTO=$(python3 -c "
import json
try:
    d = json.load(open('/tmp/claude-tappa.json'))
    d = d[-1] if isinstance(d, list) else d
    print(round(float(d.get('total_cost_usd') or 0), 2))
except Exception:
    print(0)
" 2>/dev/null || echo 0)
fi
echo "costo=$COSTO" >> "$GITHUB_OUTPUT"

# --- com'è andata ------------------------------------------------------------
if [ "${SALTATA}" = "si" ]; then
  STATO="saltata (già fatta in una corsa precedente)"
  OK=true
elif [ "${ESITO_AGENTE}" = "success" ] && [ "${EXIT_CLAUDE:-0}" = "0" ]; then
  STATO="fatta"
  OK=true
  mkdir -p "$(dirname "$MARCATORE")"
  {
    echo "tappa $NUM ($NOME) del giro $DATA"
    echo "chiusa il $(date -u +%Y-%m-%dT%H:%M:%SZ) UTC"
    echo "run: ${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-?}/actions/runs/${GITHUB_RUN_ID:-?}"
  } > "$MARCATORE"
else
  # Nessun marcatore: così la ripresa delle 09:00 la rifà invece di darla
  # per buona. Il lavoro parziale si salva lo stesso — meglio di niente.
  if [ "${EXIT_CLAUDE:-0}" != "0" ]; then
    STATO="FALLITA (claude uscito ${EXIT_CLAUDE})"
  else
    STATO="FALLITA"
  fi
  OK=false
fi
echo "ok=$OK" >> "$GITHUB_OUTPUT"
echo "stato=$STATO" >> "$GITHUB_OUTPUT"
echo "Tappa $NUM ($NOME): $STATO · costo $COSTO"

# --- salvataggio sul ramo ----------------------------------------------------
# Solo `dati/` e `queue/`: sono le uniche cartelle che gli anelli toccano.
# Un `git add -A` nudo si porterebbe dietro anche la spazzatura del computer
# di GitHub, e non si saprebbe mai cosa è entrato.
if [ "${SALTATA}" != "si" ]; then
  git config --local user.email "action@github.com"
  git config --local user.name "GitHub Action (giro in cloud)"
  git add -A dati queue 2>/dev/null || true
  if [ -n "$(git diff --cached --name-only)" ]; then
    git commit -m "Giro in cloud $DATA — tappa $NUM ($NOME): $STATO"
    # Nessun `pull --rebase`: le tappe sono in fila indiana e questo ramo lo
    # scrive solo questo workflow. Se il push fallisce è un guasto vero, e la
    # tappa deve diventare rossa invece di far finta di niente.
    git push origin "HEAD:$RAMO"
    echo "Salvato sul ramo $RAMO: $(git rev-parse --short HEAD)"
  else
    echo "Niente di nuovo da salvare."
  fi
fi

# --- i numeri, misurati dai file (mai chiesti all'agente) --------------------
python3 scripts/conta-giro.py --data "$DATA" --json > /tmp/conta.json
python3 - <<'PY' >> "$GITHUB_OUTPUT"
import json, os
m = json.load(open("/tmp/conta.json"))
def n(v):
    return "-" if v is None else v
print(f"eventi={n(m['ricerca']['eventi'])}")
print(f"verificati={n(m['verifica']['verificati'])}/{n(m['verifica']['da_confermare'])}/{n(m['verifica']['scartati'])}")
print(f"bozze={n(m['testi']['totale'])}")
PY
python3 scripts/conta-giro.py --data "$DATA"

if [ "$OK" != "true" ]; then
  exit 1
fi
