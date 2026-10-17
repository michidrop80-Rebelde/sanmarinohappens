#!/usr/bin/env bash
# Chiude la serata in cloud: guardie in Python, salvataggio sul ramo, costo.
# NON lancia mai l'agente (il passo `claude` resta nel workflow, sotto gli occhi
# di scripts/controllo-token-agente.py).
# ENV: DATA · ESITO_AGENTE · EXIT_CLAUDE (codice VERO di claude, non del passo)
# SCRIVE su $GITHUB_OUTPUT: ok · stato · costo · guardie
set -uo pipefail
RAMO="${RAMO:-catena-cloud}"

COSTO=$(python3 -c "
import json
try:
    d=json.load(open('/tmp/claude-serata.json')); d=d[-1] if isinstance(d,list) else d
    print(round(float(d.get('total_cost_usd') or 0),2))
except Exception: print(0)" 2>/dev/null || echo 0)
echo "costo=$COSTO" >> "$GITHUB_OUTPUT"

if [ "${ESITO_AGENTE:-}" = "success" ] && [ "${EXIT_CLAUDE:-1}" = "0" ]; then
  OK=true; STATO="fatta"
else
  OK=false; STATO="FALLITA (claude uscito ${EXIT_CLAUDE:-?})"
fi
echo "ok=$OK" >> "$GITHUB_OUTPUT"; echo "stato=$STATO" >> "$GITHUB_OUTPUT"

# Le guardie sono script: dicono la verita' meglio dell'agente. Nessuna blocca.
G=""
run_g() { # nome comando...
  local n="$1"; shift
  if "$@" > "/tmp/g-$n.txt" 2>&1; then G="$G $n ✅"; else G="$G $n ❌(exit $?)"; fi
}
run_g integrita python3 scripts/controllo-integrita.py
run_g prezzi python3 scripts/controllo-caption-prezzi.py
run_g imminenti python3 scripts/controllo-imminenti.py
echo "guardie=$G" >> "$GITHUB_OUTPUT"
mkdir -p "dati/cloud-serata/$DATA"
{ echo "serata $DATA — agente: $STATO — costo \$$COSTO"; echo "guardie:$G"; } > "dati/cloud-serata/$DATA/esito.txt"

git config --local user.email "action@github.com"
git config --local user.name "GitHub Action (catena serale in cloud)"
# Solo dati/ e queue/: sono le uniche cartelle che gli anelli toccano.
# `posts/` NO, mai: e' l'uscita verso Instagram, e il cloud e' un secondo parere.
git add -A dati queue 2>/dev/null || true
if [ -n "$(git diff --cached --name-only)" ]; then
  git commit -qm "Catena serale in cloud $DATA: $STATO"
  git push origin "HEAD:$RAMO" || { echo "🛑 push sul ramo fallito"; exit 1; }
fi
echo "Serata $DATA: $STATO · costo $COSTO ·$G"
[ "$OK" = "true" ]
