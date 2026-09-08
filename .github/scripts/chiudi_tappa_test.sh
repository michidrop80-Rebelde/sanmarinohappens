#!/usr/bin/env bash
# Prove del salvataggio di una tappa del giro in cloud (ticket 08).
#
# PERCHE' PROPRIO QUESTO PEZZO
# Il 07/09/2026 un passo di commit era VERDE e non aveva committato niente: un
# `git add` su un file inesistente faceva fallire tutto il comando, e un `|| true`
# si mangiava l'errore. In un giro vero avrebbe voluto dire perdere il lavoro
# senza che nessuno se ne accorgesse. Qui si prova in un repo finto, con un
# remoto finto, che il salvataggio faccia davvero quello che dice.
#
#   bash .github/scripts/chiudi_tappa_test.sh

set -uo pipefail
QUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OK=0; KO=0

verifica() {  # verifica "descrizione" "condizione già valutata: si/no"
  if [ "$2" = "si" ]; then OK=$((OK+1)); echo "  ✅ $1"; else KO=$((KO+1)); echo "  ❌ $1"; fi
}

# Prepara un repo finto con un remoto finto, e ci copia dentro il necessario.
prepara_scena() {
  SCENA="$(mktemp -d)"
  git init --quiet --bare "$SCENA/remoto.git"
  git init --quiet -b main "$SCENA/repo"
  cd "$SCENA/repo"
  git config user.email prova@example.com
  git config user.name Prova
  mkdir -p scripts .github/scripts dati/eventi/verificati dati/post queue
  cp "$QUI/scripts/conta-giro.py" scripts/
  cp "$QUI/.github/scripts/chiudi-tappa.sh" .github/scripts/
  echo "niente" > LEGGIMI.txt
  git add -A && git commit --quiet -m "inizio"
  git remote add origin "$SCENA/remoto.git"
  git push --quiet origin main:giro-cloud
  export RAMO=giro-cloud
  export GITHUB_OUTPUT="$SCENA/uscite.txt"
  : > "$GITHUB_OUTPUT"
}

uscita() { grep "^$1=" "$GITHUB_OUTPUT" | tail -1 | cut -d= -f2-; }
sul_remoto() { git --git-dir="$SCENA/remoto.git" ls-tree -r --name-only giro-cloud | grep -c "$1"; }

# ---------------------------------------------------------------------------
echo ""
echo "[1] Tappa già fatta: non tocca niente e non committa"
prepara_scena
export DATA=2026-09-14 SALTATA=si ESITO_AGENTE=skipped
PRIMA=$(git rev-parse HEAD)
bash .github/scripts/chiudi-tappa.sh 1 ricerca > /dev/null 2>&1
[ "$(uscita ok)" = "true" ] && verifica "dice che è a posto" si || verifica "dice che è a posto" no
[ "$PRIMA" = "$(git rev-parse HEAD)" ] && verifica "nessun commit nuovo" si || verifica "nessun commit nuovo" no
case "$(uscita stato)" in saltata*) verifica "lo stato dice «saltata»" si;; *) verifica "lo stato dice «saltata»" no;; esac

# ---------------------------------------------------------------------------
echo ""
echo "[2] Tappa riuscita: marcatore scritto, lavoro salvato SUL RAMO"
prepara_scena
export DATA=2026-09-14 SALTATA=no ESITO_AGENTE=success
# ⚠️ Il metro `conta-giro.py` riconosce un evento dal campo "- **Stato:**" sotto
# il titolo, non dal titolo (corretto l'08/09/2026). Senza quel campo qui sotto
# conterebbe 0 e questa prova fallirebbe pur essendo `chiudi-tappa.sh` sano.
printf '# Ricerca eventi\n\n## Evento Uno\n- **Stato:** da-verificare\n\n## Evento Due\n- **Stato:** da-verificare\n' \
  > dati/eventi/eventi-2026-09-14.md
bash .github/scripts/chiudi-tappa.sh 1 ricerca > /dev/null 2>&1
[ "$(uscita ok)" = "true" ] && verifica "dice che è a posto" si || verifica "dice che è a posto" no
[ -f "dati/cloud-giro/2026-09-14/1-ricerca.ok" ] && verifica "il marcatore c'è" si || verifica "il marcatore c'è" no
[ "$(sul_remoto 'eventi-2026-09-14.md')" = "1" ] && verifica "il file degli eventi è arrivato sul remoto" si || verifica "il file degli eventi è arrivato sul remoto" no
[ "$(sul_remoto '1-ricerca.ok')" = "1" ] && verifica "il marcatore è arrivato sul remoto" si || verifica "il marcatore è arrivato sul remoto" no
[ "$(uscita eventi)" = "2" ] && verifica "conta 2 eventi (misurati dal file)" si || verifica "conta 2 eventi (misurati dal file): $(uscita eventi)" no

# ---------------------------------------------------------------------------
echo ""
echo "[3] Tappa CADUTA: nessun marcatore (così la ripresa la rifà), lavoro salvo lo stesso"
prepara_scena
export DATA=2026-09-14 SALTATA=no ESITO_AGENTE=failure
printf '# Ricerca eventi\n\n## Mezzo Evento\n- **Stato:** da-verificare\n' > dati/eventi/eventi-2026-09-14.md
bash .github/scripts/chiudi-tappa.sh 1 ricerca > /dev/null 2>&1
ESITO=$?
[ "$ESITO" != "0" ] && verifica "il passo diventa rosso" si || verifica "il passo diventa rosso" no
[ "$(uscita ok)" = "false" ] && verifica "dice che NON è a posto" si || verifica "dice che NON è a posto" no
[ ! -f "dati/cloud-giro/2026-09-14/1-ricerca.ok" ] && verifica "nessun marcatore: la ripresa la rifarà" si || verifica "nessun marcatore" no
[ "$(sul_remoto 'eventi-2026-09-14.md')" = "1" ] && verifica "il lavoro a metà è salvo sul remoto lo stesso" si || verifica "il lavoro a metà è salvo" no

# ---------------------------------------------------------------------------
echo ""
echo "[4] Tappa riuscita ma senza aver prodotto niente: non inventa un commit"
prepara_scena
export DATA=2026-09-14 SALTATA=no ESITO_AGENTE=success
PRIMA=$(git rev-parse HEAD)
bash .github/scripts/chiudi-tappa.sh 2 postino > /dev/null 2>&1
[ "$PRIMA" != "$(git rev-parse HEAD)" ] && verifica "committa il solo marcatore (è un fatto, va salvato)" si || verifica "committa il solo marcatore" no
[ "$(uscita eventi)" = "-" ] && verifica "dice «-» invece di inventare uno zero" si || verifica "dice «-» invece di inventare uno zero: $(uscita eventi)" no

echo ""
echo "============================================================"
echo "✅ $OK verifiche passate   ❌ $KO fallite"
echo "============================================================"
[ "$KO" = "0" ]
