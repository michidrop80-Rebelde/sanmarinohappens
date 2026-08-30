#!/usr/bin/env python3
"""
Guardia di copertura — San Marino Happens

A cosa serve
------------
Dice, giorno per giorno, se nella coda di pubblicazione (repo GitHub
`sanmarinohappens`, cartella `posts/`) esiste davvero la busta del post
giornaliero e quella delle storie.

Perché esiste
-------------
Il 25/07/2026 non è uscito nulla: il post del giorno era previsto dal piano
editoriale ma non era mai stato compilato, quindi in coda non c'era alcuna
busta. Nessun anello della catena confrontava il piano con la coda, così il
buco è passato inosservato (stessa famiglia dei buchi del 14/07 e del 23/07).
Questo script è quel confronto mancante.

Controlla anche gli AGGREGATI (settimanale/weekend/carosello mensile), non
solo feed e storie: il weekend del 23/07 non è mai stato compilato ed è
passato inosservato proprio perché questo script non li guardava (bug
gemello scoperto il 26/07).

Uso
---
    python3 scripts/controllo-copertura.py            # prossimi 14 giorni
    python3 scripts/controllo-copertura.py 30         # prossimi 30 giorni

Esce con codice 1 se trova almeno un giorno scoperto: così può essere
agganciato a un giro automatico e far scattare un avviso.
"""

import collections
import datetime
import pathlib
import re
import subprocess
import sys

# Cartella del progetto = due livelli sopra questo file (scripts/ -> progetto).
# Deve restare "sé stesso": punta al clone dove gira davvero lo script, non a
# un secondo clone hardcoded altrove (bug trovato il 26/07 — quel clone era
# fermo indietro di un commit e sarebbe silenziosamente sparito se cancellato).
REPO = pathlib.Path(__file__).resolve().parent.parent
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

# Cadenza aggregati (memoria project_calendario_pubblicazione, 15/07):
# settimanale -> pubblica la domenica sera (per la settimana lun-dom successiva)
# weekend     -> pubblica il giovedì sera (per il weekend ven-dom successivo)
# carosello   -> pubblica l'ultimo giorno del mese (per il mese intero successivo)
GIORNO_SETTIMANALE = 6  # Domenica
GIORNO_WEEKEND = 3      # Giovedì


def coda_dal_remoto():
    """Legge le buste dal ramo remoto: la coda che conta è quella su GitHub,
    non la copia locale (che può essere indietro).

    Guarda sia in `posts/` (ancora da pubblicare) sia in `archivio/` (già
    pubblicate): una busta uscita stamattina è stata spostata nell'archivio, e
    senza contarla il giorno corrente risulterebbe scoperto per sbaglio.
    """
    subprocess.run(["git", "fetch", "-q", "origin"], cwd=REPO, check=False)
    out = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "origin/main", "posts/", "archivio/"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout
    buste = collections.defaultdict(set)
    for riga in out.splitlines():
        m = re.search(r"(?:^posts/|^archivio/[^/]+/)(\d{8})_(.+)\.json$", riga)
        if m:
            buste[m.group(1)].add(m.group(2).lower())
    return buste


def ultimo_giorno_del_mese(d):
    primo_mese_dopo = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    return (primo_mese_dopo - datetime.timedelta(days=1)) == d


def main():
    giorni_avanti = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    buste = coda_dal_remoto()
    oggi = datetime.date.today()

    scoperti = []
    aggregati_scoperti = []
    print(f"Copertura coda — dal {oggi.strftime('%d/%m/%Y')}, {giorni_avanti} giorni\n")
    print("DATA        GG    FEED  STORIA")
    for i in range(giorni_avanti):
        d = oggi + datetime.timedelta(days=i)
        tipi = buste.get(d.strftime("%Y%m%d"), set())
        feed = any("giornaliero" in t for t in tipi)
        storia = any("storia" in t for t in tipi)
        if not (feed and storia):
            scoperti.append((d, feed, storia))
        print(f"{d.strftime('%d/%m/%Y')}  {GIORNI[d.weekday()][:3]}   "
              f"{'✅' if feed else '❌'}    {'✅' if storia else '❌'}")

        # Aggregati: si controllano solo nel giorno in cui devono essere GIÀ in coda.
        if d.weekday() == GIORNO_SETTIMANALE:
            ok = any("settimanale" in t for t in tipi)
            aggregati_scoperti.append(("settimanale", d, ok)) if not ok else None
        if d.weekday() == GIORNO_WEEKEND:
            ok = any("weekend" in t for t in tipi)
            aggregati_scoperti.append(("weekend", d, ok)) if not ok else None
        if ultimo_giorno_del_mese(d):
            ok = any("carosello" in t for t in tipi)
            aggregati_scoperti.append(("carosello mensile", d, ok)) if not ok else None

    print()
    if aggregati_scoperti:
        print(f"⚠️  {len(aggregati_scoperti)} aggregati scoperti:")
        for nome, d, _ in aggregati_scoperti:
            print(f"   • {nome} del {d.strftime('%d/%m')} {GIORNI[d.weekday()]}: manca la busta in coda")
        print()

    if not scoperti and not aggregati_scoperti:
        print("✅ Nessun giorno scoperto: feed, storie e aggregati sono tutti in coda.")
        return 0

    if scoperti:
        print(f"⚠️  {len(scoperti)} giorni scoperti (feed/storie):")
        for d, feed, storia in scoperti:
            manca = []
            if not feed:
                manca.append("post giornaliero")
            if not storia:
                manca.append("storie")
            print(f"   • {d.strftime('%d/%m')} {GIORNI[d.weekday()]}: manca {' e '.join(manca)}")
    print("\nNota: un giorno senza eventi reali resta legittimamente scoperto —")
    print("non si inventano eventi per riempirlo. Questo elenco va letto, non eseguito.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
