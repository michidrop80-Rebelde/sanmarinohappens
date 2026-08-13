#!/usr/bin/env python3
"""
TEST OFFLINE di telegram-giro.py — non manda niente a Telegram.
Si lancia con:  python3 .claude/scripts/telegram_giro_test.py

PERCHE' ESISTE (il guasto dell'08/08/2026):
callback_data era `approve_01`, e `01` vuol dire "il primo evento DELL'ULTIMO GIRO".
Ma i pulsanti dei messaggi Telegram vecchi non scadono mai: premuto oggi, un pulsante
di tre giri fa dice `01` esattamente come quello di stamattina. Il 08/08 Michele ha
premuto su un messaggio vecchio e quelle 6 approvazioni non sono piu' riconducibili
a nessun evento. In piu' pending_events era uno slot solo, sovrascritto a ogni giro.
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

QUI = Path(__file__).parent
spec = importlib.util.spec_from_file_location("telegram_giro", QUI / "telegram-giro.py")
tg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tg)

OK = 0
KO = 0


def verifica(descrizione, condizione):
    global OK, KO
    if condizione:
        OK += 1
        print(f"  ✅ {descrizione}")
    else:
        KO += 1
        print(f"  ❌ {descrizione}")


EVENTI = [
    {"id": "01", "titolo": "Una Sera negli Anni '90", "tipo": "nuovo",
     "data": "12/08", "luogo": "Piazza della Libertà", "url": "https://esempio.sm/a"},
    {"id": "02", "titolo": "Baseball gara 1 vs Fortitudo Bologna", "tipo": "nuovo",
     "data": "14/08", "luogo": "La Ciarulla", "url": ""},
]


def main():
    print("\n[1] Il giro_id ha il formato giusto")
    giro = tg.nuovo_giro_id()
    verifica("formato AAAAMMGG-HHMM", len(giro) == 13 and giro[8] == "-")
    verifica("solo cifre e un trattino", giro.replace("-", "").isdigit())

    print("\n[2] Il callback_data porta dentro il giro")
    dati = tg.callback_data("approve", "20260810-0707", "01")
    verifica("formato approve_<giro>-<id>", dati == "approve_20260810-0707-01")
    verifica("sotto il limite Telegram di 64 byte", len(dati.encode("utf-8")) <= 64)
    lungo = tg.callback_data("reject", "20260810-0707", "99")
    verifica("anche il reject piu' lungo ci sta", len(lungo.encode("utf-8")) <= 64)

    print("\n[3] La mappa si scrive in un file PER GIRO")
    with tempfile.TemporaryDirectory() as tmp:
        tg.CARTELLA_PENDING = Path(tmp)
        percorso = tg.salva_mappa_giro("20260810-0707", EVENTI)
        verifica("il file porta il nome del giro", percorso.name == "20260810-0707.json")
        salvato = json.loads(percorso.read_text())
        verifica("contiene il giro_id", salvato["giro_id"] == "20260810-0707")
        verifica("contiene tutti gli eventi", len(salvato["eventi"]) == 2)
        verifica("conserva il titolo esatto",
                 salvato["eventi"][1]["titolo"] == "Baseball gara 1 vs Fortitudo Bologna")
        verifica("conserva data e luogo", salvato["eventi"][0]["luogo"] == "Piazza della Libertà")

        print("\n[4] Due giri NON si sovrascrivono (il guasto vero)")
        tg.salva_mappa_giro("20260811-0800", [EVENTI[0]])
        rimasti = sorted(p.name for p in Path(tmp).glob("*.json"))
        verifica("restano due file distinti",
                 rimasti == ["20260810-0707.json", "20260811-0800.json"])
        primo = json.loads((Path(tmp) / "20260810-0707.json").read_text())
        verifica("il primo giro e' intatto", len(primo["eventi"]) == 2)

    print(f"\n{'='*60}\n✅ {OK} verifiche passate   ❌ {KO} fallite\n{'='*60}")
    return 1 if KO else 0


if __name__ == "__main__":
    sys.exit(main())
