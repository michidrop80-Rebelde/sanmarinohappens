#!/usr/bin/env bash
# Sonda RTV dentro il giro in cloud: San Marino RTV risponde a questo computer?
#
# PERCHE' ESISTE (16/09/2026)
# Il 14/09 alle 03:00 la ricerca in cloud ha trovato sanmarinortv.sm bloccata
# (403) e ha perso 4 eventi. Il 16/09 sera la sonda a mano (sonda-rtv.yml) dal
# cloud passava tutto. Tre spiegazioni possibili, e questa sonda le separa:
#   1. blocco a tempo (di notte, o dopo tante richieste) -> la sonda DOPO la
#      ricerca da' 403, quella PRIMA no;
#   2. blocco di certi computer di GitHub -> gia' la sonda PRIMA da' 403;
#   3. blocco dello strumento di lettura di Claude -> le due sonde danno 200 ma
#      il file eventi di oggi mette RTV fra le «Fonti non raggiungibili».
#
# USO:  bash .github/scripts/sonda-rtv.sh <prima|dopo>
# ENV:  DATA (AAAA-MM-GG)
# SCRIVE: dati/cloud-giro/<DATA>/sonda-rtv.txt (in coda; lo salva chiudi-tappa.sh)
# ⚠️ Non fallisce MAI: e' un termometro, non deve fermare la ricerca.

set -u

QUANDO="${1:-?}"
FILE="dati/cloud-giro/${DATA:-senza-data}/sonda-rtv.txt"
mkdir -p "$(dirname "$FILE")"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

codice() {
  curl -s -L -o /dev/null -m 30 "$@" -w "%{http_code}" 2>/dev/null || true
}

{
  echo "--- sonda $QUANDO la ricerca · $(date -u +%Y-%m-%dT%H:%M:%SZ) UTC"
  echo "ip-computer $(curl -s -m 15 https://api.ipify.org 2>/dev/null || echo non-letto)"
  echo "visitsanmarino $(codice https://www.visitsanmarino.com/)"
  echo "rtv-eventi-programma $(codice https://www.sanmarinortv.sm/eventi)"
  echo "rtv-eventi-browser $(codice -A "$UA" https://www.sanmarinortv.sm/eventi)"
  echo "rtv-sport-programma $(codice https://www.sanmarinortv.sm/sport)"
  echo "rtv-rss-programma $(codice https://www.sanmarinortv.sm/rss.xml)"
} | tee -a "$FILE"

exit 0
