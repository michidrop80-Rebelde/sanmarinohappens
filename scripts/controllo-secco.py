#!/usr/bin/env python3
"""Il controllo secco della catena serale: c'e' davvero qualcosa da fare?

PERCHE' ESISTE (ticket 15 della mappa "La catena si stacca dal Mac")
Lo Step 0-bis di `smh-catena` lo fa l'agente con una manciata di comandi. In
cloud lo facciamo fare a uno SCRIPT, prima di svegliare qualsiasi agente: se le
domande rispondono tutte "no", la sera costa ZERO (13 sere su 27 misurate dal
ticket 06 non avevano niente da fare). L'agente parte solo se serve.

LE DOMANDE (le stesse di smh-catena, meno quella della grafica che in cloud non c'e')
  1. sono arrivate approvazioni?          righe `- [ ]` in queue/approvazioni.md
  3. sono arrivate segnalazioni?          righe `- [ ]` in queue/inbox.md o foto-inbox.md
  4. sono arrivati annullamenti?          righe `- [ ]` in queue/annullamenti.md
  5. manca qualcosa nelle prossime 48h?   controllo-imminenti.py esce con 2
La domanda 2 ("approvato non ancora graficato") e' roba da Mac: qui si riporta
solo come informazione (`grafica_da_fare`), non fa partire l'agente.

USO
  python3 scripts/controllo-secco.py [--radice DIR] [--json]
SCRIVE su $GITHUB_OUTPUT (se c'e'): lavoro=si|no, approvazioni, segnalazioni,
annullamenti, imminenti (si|no), grafica_da_fare (si|no|?)
USCITA: sempre 0 — e' un metro, non una guardia. Nel dubbio dice `lavoro=si`
("una guardia che sbaglia a fermare la catena e' peggio di un giro speso").
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

RIGA_APERTA = re.compile(r"^- \[ \]", re.M)


def conta_aperte(path: Path):
    """Righe `- [ ]` di un file. None se il file non si legge (= dubbio)."""
    if not path.exists():
        return 0  # nessun file = nessuna coda = zero righe
    try:
        return len(RIGA_APERTA.findall(path.read_text(encoding="utf-8")))
    except Exception:
        return None


def imminenti(radice: Path):
    """True se controllo-imminenti.py esce 2; None se non si riesce a lanciare."""
    try:
        r = subprocess.run([sys.executable, str(radice / "scripts" / "controllo-imminenti.py")],
                           capture_output=True, text=True, cwd=radice, timeout=300)
    except Exception:
        return None
    if r.returncode == 2:
        return True
    if r.returncode == 0:
        return False
    return None  # qualunque altro codice e' un guasto della guardia: dubbio


def grafica_da_fare(radice: Path):
    """Come la domanda 2: ultimo file approvati piu' recente dell'ultimo data_giro?"""
    try:
        appr = sorted((radice / "dati/post/approvati").glob("post-approvati-*.md"))
        if not appr:
            return "no"
        ultimo = re.search(r"(\d{4}-\d{2}-\d{2})", appr[-1].name).group(1)
        st = json.loads((radice / "dati/grafica-stato.json").read_text(encoding="utf-8"))
        date = [r.get("data_giro", "") for r in st.get("log", []) if r.get("data_giro")]
        return "si" if (not date or ultimo > max(date)) else "no"
    except Exception:
        return "?"


def controlla(radice: Path):
    q = radice / "queue"
    appr = conta_aperte(q / "approvazioni.md")
    inbox = conta_aperte(q / "inbox.md")
    foto = conta_aperte(q / "foto-inbox.md")
    annul = conta_aperte(q / "annullamenti.md")
    segn = None if (inbox is None or foto is None) else inbox + foto
    imm = imminenti(radice)
    dubbio = appr is None or segn is None or annul is None or imm is None
    lavoro = dubbio or bool(appr) or bool(segn) or bool(annul) or bool(imm)
    return {
        "lavoro": "si" if lavoro else "no",
        "dubbio": "si" if dubbio else "no",
        "approvazioni": "?" if appr is None else appr,
        "segnalazioni": "?" if segn is None else segn,
        "annullamenti": "?" if annul is None else annul,
        "imminenti": "?" if imm is None else ("si" if imm else "no"),
        "grafica_da_fare": grafica_da_fare(radice),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--radice", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    radice = Path(a.radice) if a.radice else Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip())
    r = controlla(radice)
    if a.json:
        print(json.dumps(r, ensure_ascii=False))
    else:
        print(f"approvazioni {r['approvazioni']} · segnalazioni {r['segnalazioni']} · "
              f"annullamenti {r['annullamenti']} · imminenti 48h {r['imminenti']} · "
              f"grafica da fare (info) {r['grafica_da_fare']}")
        print("➡️  c'è lavoro per l'agente" + (" (per dubbio: un controllo non ha saputo rispondere)"
              if r["dubbio"] == "si" else "") if r["lavoro"] == "si" else "➡️  niente da fare: l'agente non parte")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            for k, v in r.items():
                f.write(f"{k}={v}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
