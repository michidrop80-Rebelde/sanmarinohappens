#!/usr/bin/env python3
"""
controllo-busta-rimasta.py — i pulsanti sono partiti davvero?

COS'È (spiegato semplice)
-------------------------
Il riepilogo del giro con i tasti ✅/❌ si manda in due tempi (ticket 07):
`prepara` scrive la busta `queue/telegram-da-inviare.json`, `invia` la spedisce
e — solo se Telegram conferma — la cancella.

Quindi: **se la busta è ancora lì, l'invio NON è riuscito.** Michele crede di
non avere niente da approvare, e invece la catena è ferma ad aspettarlo.

Questa guardia guarda se la busta c'è. Se c'è, lo dice chiaro (e prova a
mandare un Telegram: magari il guasto di ieri era passeggero e oggi la riga
arriva) ed esce 1, così la corsa diventa rossa.

COME SI LANCIA
    python3 scripts/controllo-busta-rimasta.py
    (0 = nessuna busta in giro · 1 = c'è una busta mai spedita)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADICE / "scripts"))
from telegram_helper import manda_telegram  # noqa: E402

BUSTA = RADICE / "queue" / "telegram-da-inviare.json"


def main():
    if not BUSTA.exists():
        print("✅ Nessuna busta in giro: l'ultimo riepilogo coi pulsanti è partito.")
        return 0

    try:
        b = json.loads(BUSTA.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"🛑 C'è una busta in {BUSTA} e non si riesce nemmeno a leggerla: {e}")
        return 1

    giro = b.get("giro_id", "?")
    creata = b.get("creata_il", "?")
    eventi = len(b.get("eventi", []))
    giorni = "?"
    try:
        quando = datetime.strptime(creata, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        giorni = (datetime.now(timezone.utc) - quando).days
    except ValueError:
        pass

    print(f"🛑 BUSTA MAI SPEDITA — giro {giro}, {eventi} eventi, creata {creata} "
          f"({giorni} giorni fa).")
    print(f"   File: {BUSTA}")
    print("   Vuol dire che i pulsanti NON sono arrivati a Michele: lui crede di non avere")
    print("   niente da approvare e la catena resta ferma.")
    print("   Cosa fare: rilancia l'invio")
    print("     python3 .claude/scripts/telegram-giro.py invia")
    print("   Se fallisce ancora, il problema è il canale (token o rete), non la busta.")

    manda_telegram(
        f"🛑 SMH — i pulsanti del giro {giro} ({eventi} eventi, {giorni} giorni fa) "
        f"non sono mai partiti. La busta è ancora in coda: la catena aspetta la tua "
        f"approvazione di eventi che non hai mai ricevuto."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
