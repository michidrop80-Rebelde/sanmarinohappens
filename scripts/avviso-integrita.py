#!/usr/bin/env python3
"""
avviso-integrita.py — fa gridare la guardia di integrità quando gira in cloud.

COS'È (spiegato semplice)
------------------------
`controllo-integrita.py` controlla che ogni file citato dalle skill esista
davvero. Fin qui girava solo sul Mac di Michele, dove i file **ci sono sempre**
anche quando non sono stati messi nel repo: per due mesi nessuno si è accorto
che 6 file veri (config.json, fonti-sport.md, ecc.) non erano mai stati
committati. In cloud quei file non esistono e la catena lavorerebbe monca.

Questo script lancia la guardia e, **se trova un buco**, manda un Telegram di
poche righe a Michele e chiude con codice 1 (così il workflow diventa rosso).
Stessa forma di `avviso-imminenti.py` — trasforma un fallimento silenzioso in
uno rumoroso.

USO
---
  python3 scripts/avviso-integrita.py

Pensato per girare in GitHub Actions a ogni push (dove il checkout È un clone
pulito) e una volta a settimana. In locale funziona lo stesso: se non trova
niente da dire, tace ed esce 0.
"""
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
GUARDIA = REPO / "scripts" / "controllo-integrita.py"

# Riusa l'invio Telegram già collaudato (requests con ripiego su curl).
sys.path.insert(0, str(REPO / "scripts"))
from telegram_helper import manda_telegram  # type: ignore  # noqa: E402


def main() -> int:
    esito = subprocess.run(
        [sys.executable, str(GUARDIA)],
        capture_output=True, text=True,
    )
    referto = (esito.stdout + esito.stderr).strip()
    print(referto)

    if esito.returncode == 0:
        return 0

    # Tiene solo la parte "cosa manca", taglia il blocco finale di istruzioni.
    righe = []
    for r in referto.splitlines():
        if r.strip().startswith("Cosa fare:"):
            break
        righe.append(r)
    corpo = "\n".join(righe).strip()

    manda_telegram(
        "🔴 San Marino Happens — guardia di integrità\n\n"
        "Un file citato dalle skill NON è nel repo. In cloud la catena "
        "lavorerebbe senza quel pezzo.\n\n" + corpo
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
