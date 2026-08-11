#!/usr/bin/env python3
"""
TEST OFFLINE del LUCCHETTO — non tocca la rete e non tocca il lucchetto vero.
Si lancia con:  python3 scripts/lucchetto_test.py

PERCHE' ESISTE (il guasto del 04/08/2026, ripetuto l'11/08/2026):
smh-check-approvazioni e smh-grafica-pubblica hanno lastRunAt IDENTICO al secondo
(2026-08-11T15:39:41). Non erano partiti ai loro orari: erano partiti insieme alla
riapertura dell'app, in parallelo, sugli stessi file. Senza un lucchetto due giri
possono leggere la stessa coda, graficare lo stesso evento e committare l'uno sopra
l'altro.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lucchetto

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


def main():
    with tempfile.TemporaryDirectory() as tmp:
        # Il lucchetto di prova vive in una cartella usa-e-getta: mai quello vero.
        lucchetto.PERCORSO = Path(tmp) / "lucchetto.json"

        print("\n[1] Presa di un lucchetto libero")
        preso, _ = lucchetto.prendi("giro-a")
        verifica("il primo che arriva lo prende", preso)
        verifica("il file esiste", lucchetto.PERCORSO.exists())

        print("\n[2] Un secondo giro trova occupato")
        preso2, motivo = lucchetto.prendi("giro-b")
        verifica("il secondo NON lo prende", not preso2)
        verifica("il motivo dice chi lo tiene", "giro-a" in motivo)

        print("\n[3] Rilascio solo dal titolare")
        verifica("un estraneo non lo rilascia", not lucchetto.rilascia("giro-b"))
        verifica("il file c'e' ancora", lucchetto.PERCORSO.exists())
        verifica("il titolare lo rilascia", lucchetto.rilascia("giro-a"))
        verifica("il file e' sparito", not lucchetto.PERCORSO.exists())

        print("\n[4] Lucchetto scaduto per TTL: si prende lo stesso")
        lucchetto.prendi("giro-morto")
        # Si invecchia il lucchetto riscrivendo la sua ora di presa.
        dati = lucchetto.stato()
        dati["preso_il"] = "2020-01-01T00:00:00Z"
        lucchetto.PERCORSO.write_text(lucchetto.json.dumps(dati))
        preso3, motivo3 = lucchetto.prendi("giro-c")
        verifica("un lucchetto vecchio di anni si scavalca", preso3)
        verifica("e il referto lo dice", "scaduto" in motivo3.lower())
        lucchetto.rilascia("giro-c")

        print("\n[5] Un pid morto NON basta a scavalcare")
        # ⚠️ Questo test dice il CONTRARIO di come era scritto il piano, ed e' il
        # motivo per cui il lucchetto adesso funziona. Il lucchetto si prende da riga
        # di comando, e quel processo python muore un istante dopo: se il pid morto
        # autorizzasse lo scavalco, il secondo giro passerebbe SEMPRE. Provato dal
        # vivo l'11/08/2026 prima della correzione: passava sempre.
        lucchetto.prendi("giro-zombie")
        dati = lucchetto.stato()
        dati["pid"] = 999999  # pid che non esiste
        lucchetto.PERCORSO.write_text(lucchetto.json.dumps(dati))
        preso4, motivo4 = lucchetto.prendi("giro-d")
        verifica("il lucchetto regge anche se chi lo teneva non c'e' piu'", not preso4)
        verifica("e il motivo dice che e' occupato", "occupato" in motivo4.lower())
        lucchetto.rilascia("giro-zombie")

        print("\n[6] Un file rovinato non blocca la catena per sempre")
        lucchetto.PERCORSO.write_text("{ questo non e' json")
        preso5, motivo5 = lucchetto.prendi("giro-e")
        verifica("un lucchetto illeggibile si scavalca", preso5)
        verifica("e il referto lo dice", "illeggibile" in motivo5.lower())

    print("\n[7] La prova che conta: due giri veri da riga di comando")
    # Le skill non importano il modulo: lanciano `python3 scripts/lucchetto.py prendi`.
    # E' cosi' che va provato, altrimenti si prova qualcosa che nessuno usa.
    with tempfile.TemporaryDirectory() as tmp:
        script = str(Path(__file__).parent / "lucchetto.py")
        ambiente = dict(os.environ, SMH_LUCCHETTO=str(Path(tmp) / "lucchetto.json"))

        def cli(*argomenti):
            return subprocess.run([sys.executable, script, *argomenti],
                                  env=ambiente, capture_output=True, text=True)

        primo = cli("prendi", "smh-catena")
        verifica("il primo giro lo prende (uscita 0)", primo.returncode == 0)
        secondo = cli("prendi", "smh-giro")
        verifica("il secondo giro si ferma (uscita 1)", secondo.returncode == 1)
        verifica("e sa dire chi lo tiene", "smh-catena" in secondo.stdout)
        verifica("un estraneo non lo libera",
                 cli("rilascia", "smh-giro").returncode == 0
                 and cli("stato", "smh").returncode == 1)
        verifica("il titolare lo libera", cli("rilascia", "smh-catena").returncode == 0)
        verifica("e dopo risulta libero", cli("stato", "smh").returncode == 0)

    print(f"\n{'='*60}\n✅ {OK} verifiche passate   ❌ {KO} fallite\n{'='*60}")
    return 1 if KO else 0


if __name__ == "__main__":
    sys.exit(main())
