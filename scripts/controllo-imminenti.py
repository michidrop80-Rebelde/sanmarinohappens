#!/usr/bin/env python3
"""
Guardia degli imminenti — San Marino Happens

A cosa serve
------------
Risponde ogni sera a una domanda sola e stretta: **nelle prossime 48 ore esce
tutto quello che deve uscire?** Cioè:

  • il post del feed e le storie di DOMANI (slot delle 7:00);
  • gli AGGREGATI in scadenza entro 48 ore (settimanale la domenica 18:00,
    weekend il giovedì 18:00, carosello mensile l'ultimo giorno del mese 18:00).

Per ogni buco che trova va a cercare nel registro master gli eventi veri di
quella data, e dice se il buco è **CHIUDIBILE** (c'è materiale già approvato:
si compila e si mette in coda subito) oppure **NON CHIUDIBILE** e perché.

Perché esiste — ed è diversa da controllo-copertura.py
------------------------------------------------------
`controllo-copertura.py` guarda 14 giorni e stampa una lista lunga in cui i
giorni scoperti sono quasi sempre legittimi (un giorno senza eventi veri resta
vuoto: non si inventano eventi). A furia di elencare cose non azionabili, quella
lista ha smesso di essere letta — e infatti il **settimanale del 16/08/2026** ci
finì dentro, indistinguibile dal rumore, e non uscì. Nemmeno il weekend di
Ferragosto del 13/08 uscì, per la stessa ragione.

La differenza è questa: un giorno senza eventi è vuoto per colpa del calendario,
un aggregato mancante è vuoto **per colpa nostra**. La domenica arriva comunque.
Quindi qui un aggregato che manca è sempre ❌ duro, mai un ⚠️ da leggere e
scrollare.

E soprattutto: questa guardia è fatta per essere **eseguita**, non letta. Chi la
lancia (la catena serale) deve chiudere i buchi chiudibili, non passarne
l'elenco a Michele.

Uso
---
    python3 scripts/controllo-imminenti.py

Codici di uscita
----------------
    0  niente da fare: le prossime 48 ore sono coperte
    2  c'è almeno un buco CHIUDIBILE -> la catena deve lavorare adesso
    1  ci sono buchi ma nessuno chiudibile (serve l'ok di Michele, o
       semplicemente non ci sono eventi) -> solo referto, nessun lavoro
"""

import collections
import datetime
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MASTER = REPO / "dati" / "calendario" / "master.md"
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

GIORNO_SETTIMANALE = 6  # Domenica: esce il settimanale della settimana dopo
GIORNO_WEEKEND = 3      # Giovedì: esce il weekend ven-sab-dom


# ---------------------------------------------------------------------------
# La coda vera è quella su GitHub
# ---------------------------------------------------------------------------
def coda_dal_remoto():
    """Buste presenti su origin/main, per data (AAAAMMGG) -> insieme di tipi.

    Si legge dal RAMO REMOTO e non dal disco: il robot che pubblica fa il
    checkout di origin/main, quindi una busta che esiste solo sul Mac per lui
    non esiste. Si guarda anche in archivio/ perché una busta uscita stamattina
    è già stata spostata lì, e senza contarla il giorno risulterebbe scoperto.
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


# ---------------------------------------------------------------------------
# Il registro master: dove stanno gli eventi veri
# ---------------------------------------------------------------------------
def _date_del_campo(campo, anno):
    """Tutte le date che il campo 'data' del master può contenere.

    Il master scrive le date in più modi: '21/08', '21-23/08', '26/07-23/08',
    '21, 22, 23, 28, 29/08'. Qui si estrae l'intervallo coperto (prima e ultima
    data), che basta per sapere se una riga tocca un certo giorno.
    """
    campo = campo.replace("–", "-").replace("—", "-")
    trovate = []
    for g1, m1, g2, m2 in re.findall(r"(\d{1,2})(?:/(\d{1,2}))?\s*-\s*(\d{1,2})/(\d{1,2})", campo):
        mm1 = int(m1) if m1 else int(m2)
        for g, mm in ((int(g1), mm1), (int(g2), int(m2))):
            try:
                trovate.append(datetime.date(anno, mm, g))
            except ValueError:
                pass
    for g, mm in re.findall(r"(\d{1,2})/(\d{1,2})(?!/)", campo):
        try:
            trovate.append(datetime.date(anno, int(mm), int(g)))
        except ValueError:
            pass
    return (min(trovate), max(trovate)) if trovate else None


def eventi_master(anno):
    """Righe del registro master, con date interpretate. Solo lettura."""
    righe = []
    if not MASTER.exists():
        return righe
    for n, linea in enumerate(MASTER.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.startswith("|"):
            continue
        c = [x.strip() for x in linea.strip().strip("|").split("|")]
        if len(c) < 7 or c[0].lower() in ("id", "colonna") or set(c[0]) <= set("-: "):
            continue
        r = _date_del_campo(c[1], anno)
        if not r:
            continue
        righe.append({
            "id": c[0], "data": c[1], "titolo": c[2], "luogo": c[4],
            "stato_evento": c[5].lower(), "stato_post": c[6].lower(),
            "dal": r[0], "al": r[1], "riga_file": n,
        })
    return righe


def eventi_del_giorno(righe, d):
    """Righe del master che toccano il giorno `d` e non sono già concluse."""
    return [r for r in righe
            if r["dal"] <= d <= r["al"] and "concluso" not in r["stato_evento"]]


def ultimo_giorno_del_mese(d):
    primo_dopo = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    return (primo_dopo - datetime.timedelta(days=1)) == d


# ---------------------------------------------------------------------------
def _scheda_buco(titolo, quando, tipi_mancanti, candidati):
    """Un buco con dentro tutto il necessario per chiuderlo (o per capire
    perché non si può). Mai un ⚠️ nudo: cosa manca, per quando, con che cosa."""
    approvati = [e for e in candidati if e["stato_post"] == "approvato"]
    return {
        "titolo": titolo,
        "quando": quando,
        "manca": tipi_mancanti,
        "candidati": candidati,
        "approvati": approvati,
        "chiudibile": bool(approvati),
    }


def main():
    # Data di riferimento. Normalmente è oggi; si può forzare per PROVARE la guardia
    # su una data qualsiasi senza aspettare che arrivi:
    #     python3 scripts/controllo-imminenti.py 2026-08-16
    # Serve a verificare che sappia ancora accorgersi dei buchi già successi — una
    # guardia che nessuno ha mai visto scattare non è una guardia.
    if len(sys.argv) > 1:
        oggi = datetime.date.fromisoformat(sys.argv[1])
        print(f"⚠️  PROVA: sto usando {oggi.strftime('%d/%m/%Y')} come 'oggi'.\n")
    else:
        oggi = datetime.date.today()
    domani = oggi + datetime.timedelta(days=1)
    dopodomani = oggi + datetime.timedelta(days=2)

    buste = coda_dal_remoto()
    master = eventi_master(oggi.year)

    print("Guardia degli imminenti — le prossime 48 ore\n")
    print(f"Oggi     : {oggi.strftime('%d/%m/%Y')} {GIORNI[oggi.weekday()]}")
    print(f"Orizzonte: fino al {dopodomani.strftime('%d/%m/%Y')} {GIORNI[dopodomani.weekday()]}")
    print(f"Master   : {len(master)} righe con data leggibile\n")

    buchi = []

    # --- 1. Feed e storie di DOMANI (slot 7:00) ------------------------------
    tipi_domani = buste.get(domani.strftime("%Y%m%d"), set())
    manca = []
    if not any("giornaliero" in t for t in tipi_domani):
        manca.append("post feed")
    if not any("storia" in t for t in tipi_domani):
        manca.append("storie")
    if manca:
        buchi.append(_scheda_buco(
            f"Domani {domani.strftime('%d/%m')} {GIORNI[domani.weekday()]} — slot 7:00",
            domani, manca, eventi_del_giorno(master, domani)))

    # --- 2. Aggregati in scadenza entro 48 ore -------------------------------
    # Si guarda anche OGGI: un aggregato delle 18:00 di oggi è ancora in tempo
    # se la catena gira alle 18:30? No — sarebbe in ritardo di 30 minuti, ma
    # rientra nella finestra di recupero di 2 giorni, quindi va comunque fatto.
    for d in (oggi, domani, dopodomani):
        tipi = buste.get(d.strftime("%Y%m%d"), set())
        attesi = []
        if d.weekday() == GIORNO_SETTIMANALE:
            attesi.append(("settimanale", "settimanale",
                           d + datetime.timedelta(days=1), d + datetime.timedelta(days=7)))
        if d.weekday() == GIORNO_WEEKEND:
            attesi.append(("weekend", "weekend",
                           d + datetime.timedelta(days=1), d + datetime.timedelta(days=3)))
        if ultimo_giorno_del_mese(d):
            primo = d + datetime.timedelta(days=1)
            attesi.append(("carosello mensile", "carosello",
                           primo, (primo.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
                           - datetime.timedelta(days=1)))
        for nome, chiave, copre_dal, copre_al in attesi:
            if any(chiave in t for t in tipi):
                continue
            candidati = []
            g = copre_dal
            while g <= copre_al:
                candidati.extend(eventi_del_giorno(master, g))
                g += datetime.timedelta(days=1)
            visti, unici = set(), []
            for e in candidati:
                if e["id"] not in visti:
                    visti.add(e["id"])
                    unici.append(e)
            quando = "OGGI" if d == oggi else ("DOMANI" if d == domani else "dopodomani")
            buchi.append(_scheda_buco(
                f"{nome.capitalize()} del {d.strftime('%d/%m')} {GIORNI[d.weekday()]} "
                f"ore 18:00 ({quando}) — copre {copre_dal.strftime('%d/%m')}"
                f"–{copre_al.strftime('%d/%m')}",
                d, [nome], unici))

    # --- Referto ------------------------------------------------------------
    if not buchi:
        print("✅ Le prossime 48 ore sono coperte: niente da fare.")
        return 0

    chiudibili = [b for b in buchi if b["chiudibile"]]

    for b in buchi:
        segno = "❌" if b["chiudibile"] else "⚪"
        print(f"{segno} {b['titolo']}")
        print(f"   manca: {' e '.join(b['manca'])}")
        if b["approvati"]:
            print(f"   CHIUDIBILE ORA — {len(b['approvati'])} eventi già `approvato` a registro:")
            lunghi = False
            for e in b["approvati"][:12]:
                # Una riga con intervallo lungo (una rassegna, una mostra) non vuol dire
                # che ci sia qualcosa TUTTI i giorni dell'intervallo: le date vere stanno
                # nella nota. Es. "Cinema nei Castelli 03-26/08" proietta solo lun/mar/mer.
                esteso = (e["al"] - e["dal"]).days >= 6
                lunghi = lunghi or esteso
                print(f"      · [{e['id']}] {e['titolo']} — {e['luogo'][:52]} ({e['data']})"
                      + ("  ⟵ intervallo lungo: leggi la NOTA per le date vere" if esteso else ""))
            if lunghi:
                print("   ⚠️  Le righe segnate 'intervallo lungo' sono rassegne o mostre: qui compaiono")
                print("       perché il loro intervallo tocca queste date, NON perché ci sia una data")
                print("       confermata. Prima di metterle in un contenuto, apri la riga nel master")
                print("       e leggi la nota: se quel giorno non c'è, non ci va.")
        elif b["candidati"]:
            print("   NON chiudibile da sola: ci sono eventi ma nessuno è `approvato`.")
            print("   Servono i pulsanti ✅ di Michele su Telegram, e vanno mandati SUBITO:")
            for e in b["candidati"][:12]:
                print(f"      · [{e['id']}] {e['titolo']} — stato post: {e['stato_post']}")
        else:
            print("   Legittimamente vuoto: nel master non c'è nessun evento per queste date.")
            print("   Non si inventano eventi per riempire un giorno.")
        print()

    if chiudibili:
        print(f"➡️  {len(chiudibili)} buchi su {len(buchi)} sono CHIUDIBILI ADESSO.")
        print("   Vanno chiusi in questo giro: compilare la grafica, mettere la busta in")
        print("   coda e spingere su origin/main. Non si consegna questo elenco a Michele.")
        return 2

    print(f"ℹ️  {len(buchi)} buchi, nessuno chiudibile da solo (vedi sopra il perché).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
