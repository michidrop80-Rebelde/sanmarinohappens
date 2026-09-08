#!/usr/bin/env python3
"""
controllo-allineamento.py — nessuna skill del Mac parte da dati vecchi.
=======================================================================

COS'E' (spiegato semplice)
--------------------------
Da quando la catena dei testi gira su GitHub di notte, ogni skill che Michele lancia
sul Mac deve prima mettersi in pari col cloud (`scripts/allineati.py`). Se non lo fa,
lavora sulla lista di ieri e nessuno se ne accorge: non c'e' nessun errore, nessun
rosso — solo una grafica sbagliata pubblicata al momento giusto.

Il guaio di una regola scritta solo nella testa e' che alla prossima riscrittura della
skill sparisce. Questa guardia la tiene ferma: gira a ogni push e diventa rossa se
una delle skill d'ingresso ha perso il passo di allineamento.

⚠️ PERCHE' NON BASTA CERCARE «allineati» NEL FILE
Deve essere il PRIMO comando che si esegue, non una nota a meta' pagina. Contare le
righe non serve (queste skill hanno pagine di regole prima di cominciare): quello che
conta e' l'ORDINE DEI COMANDI. Quindi la guardia controlla che nessun altro blocco
`bash` venga PRIMA dell'allineamento — se ce n'e' uno, quel comando gira su dati che
nessuno ha ancora messo in pari.

Uscite: 0 = tutto a posto · 1 = una skill non si allinea piu'
"""

import subprocess
import sys
from pathlib import Path

# Le skill che Michele (o una sveglia) lancia SUL MAC e che leggono i dati della
# catena. Gli anelli interni (ricerca/verifica/testi) non sono qui: li lancia sempre
# uno di questi, che si e' gia' allineato per tutti.
INGRESSI = [
    "smh-giro",         # il giro completo
    "smh-catena",       # la catena serale
    "smh-grafica",      # l'unica cosa che resta a Michele quando il cloud e' titolare
    "smh-pubblica",     # legge la coda, che il robot cambia da solo
    "smh-postino",      # legge le code Telegram, scritte sul remoto dal bot
    "smh-approvazione", # legge le approvazioni, scritte sul remoto dal Worker
]

ATTESO = "scripts/allineati.py"


def main():
    radice = Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True).stdout.strip() or ".")

    problemi = []
    print("Chi deve allinearsi col cloud prima di lavorare:\n")

    if not (radice / ATTESO).exists():
        print(f"❌ manca {ATTESO}: il passo di allineamento non esiste più")
        return 1

    for nome in INGRESSI:
        percorso = radice / ".claude" / "skills" / nome / "SKILL.md"
        if not percorso.exists():
            problemi.append(f"{nome}: la skill non esiste più (era un ingresso del Mac)")
            print(f"  ❌ {nome} — skill sparita")
            continue
        righe = percorso.read_text().splitlines()
        posizioni = [i for i, r in enumerate(righe) if ATTESO in r]
        if not posizioni:
            problemi.append(f"{nome}: non chiama più {ATTESO} — partirebbe da dati vecchi")
            print(f"  ❌ {nome} — nessun allineamento")
            continue
        prima = posizioni[0]

        # Quale blocco di comandi viene prima? Due cose sono ammesse perche' non
        # leggono i dati del progetto: il `cd` per andare nella radice, e la presa
        # del lucchetto (stato di QUESTO Mac, tenuto fuori dal repo apposta). Anzi:
        # il lucchetto va preso PRIMA, altrimenti due giri si allineano insieme.
        AMMESSI = ("cd ", "python3 scripts/lucchetto.py")
        dentro, precedente = False, None
        for i, r in enumerate(righe[:prima]):
            testo = r.strip()
            if testo.startswith("```"):
                dentro = testo.startswith("```bash") or testo.startswith("```sh")
                continue
            if dentro and testo and not testo.startswith("#") \
                    and not testo.startswith(AMMESSI):
                precedente = (i + 1, testo)
                break
        if precedente:
            problemi.append(
                f"{nome}: alla riga {precedente[0]} gira già «{precedente[1][:60]}», "
                f"ma l'allineamento è solo alla riga {prima + 1} — quel comando lavora "
                f"su dati non ancora messi in pari")
            print(f"  ❌ {nome} — un comando lo precede (riga {precedente[0]})")
            continue
        print(f"  ✅ {nome} — si allinea prima di ogni altro comando (riga {prima + 1})")

    print()
    if problemi:
        print(f"❌ {len(problemi)} problemi:")
        for p in problemi:
            print(f"   · {p}")
        print("\nRimedio: rimettere `python3 scripts/allineati.py <nome>` come primo\n"
              "comando della skill, prima di qualsiasi lettura dei dati.")
        return 1
    print(f"✅ tutte e {len(INGRESSI)} le skill d'ingresso si allineano col cloud.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
