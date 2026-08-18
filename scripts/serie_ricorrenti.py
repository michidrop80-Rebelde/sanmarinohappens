#!/usr/bin/env python3
"""
Serie ricorrenti — San Marino Happens

Il problema che risolve
-----------------------
Alcuni eventi del registro master non sono UN evento: sono una **serie di
appuntamenti distinti**, ognuno con la sua data e spesso col suo programma.
Esempi veri:

    Cinema nei Castelli   03–26/08   12 proiezioni, un film diverso ogni volta
    Alba sul Monte        26/07–23/08  5 concerti la domenica, programma diverso
    Trenino Bianco Azzurro  21, 22, 23, 28, 29/08
    Giovedì in Centro     30/07, 06/08, 13/08, 27/08

La catena non li vede. `/smh-ricerca` → `/smh-verifica` → `/smh-testi` scrivono
bozze **solo per gli eventi nuovi** dell'ultimo giro; una serie già archiviata
nel master come `approvato` non viene mai ripescata, e le sue singole date
restano senza post. Michele aveva deciso il 06/07/2026 che «ogni proiezione va
ri-inserita nei riepiloghi settimana/giorno», ma quella regola era scritta nella
nota del master e implementata da nessuna parte.

Conseguenza concreta: il **18/08/2026** la pagina non ha pubblicato niente pur
avendo un evento vero e verificato (Cinema nei Castelli, «Il robot selvaggio»,
Fiorentino, 21:00, gratis). Stessa sorte per il 24, 25 e 26/08.

Cosa fa
-------
Espande le righe-serie del master nelle loro **occorrenze singole**: una data,
un titolo, un luogo. Riconosce due modi di scrivere le date, che sono i due che
Michele e gli agenti usano davvero:

  A) **elenco nel campo data** — `21, 22, 23, 28, 29/08`
  B) **programma nella nota** — `03/08 Follemente · 04/08 Sonic 3 · ...`
     oppure `**02/08** "La voce degli animali" · **09/08** "Sonate e Danze"`

Non tocca gli eventi che durano più giorni di fila (una sagra di tre giorni, una
mostra di tre mesi): quelli non sono una serie, sono **un** evento, e un post ce
l'hanno già. Il filtro è: si considera serie solo chi ha **almeno 2 date
distinte** ricavate da A o da B.

⚠️ Il titolo estratto è un PUNTATORE, non testo pronto da pubblicare
--------------------------------------------------------------------
Le note del master sono prosa scritta a mano: il titolo viene ritagliato al
meglio, ma prima di metterlo in un contenuto **si apre la riga del master e si
legge**. Questo strumento serve a non dimenticare una data, non a scrivere il
post al posto tuo. Vale la regola di sempre: non si inventa niente.

Uso
---
    python3 scripts/serie_ricorrenti.py            # prossimi 14 giorni
    python3 scripts/serie_ricorrenti.py 30         # prossimi 30 giorni
    python3 scripts/serie_ricorrenti.py 14 2026-08-15   # come se fosse il 15/08

Il nome del file usa l'underscore (non il trattino come le altre guardie) perché
questo è anche un **modulo importabile**: `controllo-imminenti.py` lo usa per
sapere se domani c'è un appuntamento di una serie.

Esce con codice 1 se almeno una occorrenza nella finestra è **senza busta**.
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

# Separatori con cui le note elencano gli appuntamenti.
SEPARATORI = re.compile(r"\s*[;·]\s*")
# Un "cappello di luogo" dentro la nota: **Serravalle, Piazza Bertoldi** —
CAPPELLO_LUOGO = re.compile(r"\*\*([^*]{3,60}?)\*\*\s*[—–-]\s*")
# Data in grassetto: marcatore esplicito di programma, sempre affidabile.
DATA_GRASSETTO = re.compile(r"\*\*(\d{1,2}/\d{1,2})\*\*\s*")
# Data nuda a inizio pezzo (dopo un eventuale cappello di luogo).
DATA_INIZIALE = re.compile(r"^(\d{1,2}/\d{1,2})(?!/)\s+(.+)$")


def _ritaglia_titolo(testo):
    """Ritaglia il titolo dell'appuntamento dalla prosa che lo segue.

    Le note continuano spesso con commenti ("Luogo corretto da…", "esecutori
    verificati…"). Si tiene la parte che è davvero il titolo.
    """
    testo = testo.strip()
    # Titolo fra virgolette -> è tutto lì dentro.
    m = re.match(r'^[«"“]([^»"”]{2,80})[»"”]', testo)
    if m:
        return m.group(1).strip()
    # Altrimenti si taglia al primo segno che introduce un commento.
    testo = re.split(r"\s+[—–]\s+|\.\s+[A-Z⚠️🔴✅]|\s*\(", testo)[0]
    return testo.strip(" .,;:").strip()[:80]


def _date_da_elenco(campo, anno):
    """Caso A: date elencate nel campo data — `21, 22, 23, 28, 29/08`.

    I giorni senza mese ereditano il mese dalla prima data completa che segue,
    che è come vengono scritti davvero ("21, 22, 23, 28, 29/08" = tutti agosto).
    """
    pezzi = [p.strip() for p in campo.split(",")]
    if len(pezzi) < 2:
        return []
    date, in_attesa = [], []
    for p in pezzi:
        m = re.match(r"^(\d{1,2})/(\d{1,2})(?:/\d{4})?$", p)
        if m:
            g, mm = int(m.group(1)), int(m.group(2))
            for g_attesa in in_attesa:          # i giorni nudi prendono questo mese
                try:
                    date.append(datetime.date(anno, mm, g_attesa))
                except ValueError:
                    pass
            in_attesa = []
            try:
                date.append(datetime.date(anno, mm, g))
            except ValueError:
                pass
        elif re.match(r"^\d{1,2}$", p):
            in_attesa.append(int(p))
        else:
            return []                            # forma non riconosciuta: meglio niente
    return sorted(set(date))


def _date_da_nota(nota, anno):
    """Caso B: programma dentro la nota. Ritorna [(data, titolo, luogo|None)]."""
    trovate, luogo_corrente = [], None
    for pezzo in SEPARATORI.split(nota):
        if not pezzo.strip():
            continue
        # Un cappello di luogo vale per questo pezzo e per quelli che seguono,
        # finché non ne compare un altro (è così che è scritto Cinema nei Castelli).
        cappelli = list(CAPPELLO_LUOGO.finditer(pezzo))
        if cappelli:
            ultimo = cappelli[-1]
            luogo_corrente = ultimo.group(1).strip()
            pezzo = pezzo[ultimo.end():]

        m = DATA_GRASSETTO.search(pezzo)
        if m:
            data_txt, resto = m.group(1), pezzo[m.end():]
        else:
            m = DATA_INIZIALE.match(pezzo.strip())
            if not m:
                continue                          # nessuna data in testa: è prosa, si salta
            data_txt, resto = m.group(1), m.group(2)

        g, mm = (int(x) for x in data_txt.split("/"))
        try:
            d = datetime.date(anno, mm, g)
        except ValueError:
            continue
        titolo = _ritaglia_titolo(resto)
        if titolo:
            trovate.append((d, titolo, luogo_corrente))
    return trovate


def occorrenze_serie(anno):
    """Tutte le occorrenze singole delle righe-serie del master.

    Serie = riga con almeno 2 date distinte ricavabili. Un evento che dura più
    giorni di fila (sagra, mostra) NON è una serie e non compare qui.
    """
    fuori = []
    if not MASTER.exists():
        return fuori

    for n, linea in enumerate(MASTER.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.startswith("|"):
            continue
        c = [x.strip() for x in linea.strip().strip("|").split("|")]
        if len(c) < 7 or c[0].lower() in ("id", "colonna") or set(c[0]) <= set("-: "):
            continue
        if "concluso" in c[5].lower():
            continue

        id_, campo_data, titolo, luogo, stato_post = c[0], c[1], c[2], c[4], c[6].lower()
        nota = c[9] if len(c) > 9 else ""

        # A) elenco nel campo data -> ogni data è un appuntamento, stesso titolo
        appuntamenti = [(d, titolo, None) for d in _date_da_elenco(campo_data, anno)]
        # B) programma nella nota -> ogni data ha il suo titolo
        if len(appuntamenti) < 2:
            appuntamenti = _date_da_nota(nota, anno)

        if len({d for d, _, _ in appuntamenti}) < 2:
            continue                              # non è una serie

        for d, tit, lg in appuntamenti:
            fuori.append({
                "id": id_, "serie": titolo, "data": d,
                "titolo": tit if tit != titolo else titolo,
                "programma": tit if tit != titolo else None,
                "luogo": lg or luogo, "stato_post": stato_post, "riga_file": n,
            })
    return sorted(fuori, key=lambda x: (x["data"], x["id"]))


def occorrenze_del_giorno(occorrenze, d):
    return [o for o in occorrenze if o["data"] == d]


# ---------------------------------------------------------------------------
def _coda_dal_remoto():
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


def main():
    giorni = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    oggi = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date.today()

    occ = occorrenze_serie(oggi.year)
    buste = _coda_dal_remoto()
    fine = oggi + datetime.timedelta(days=giorni)

    serie = sorted({(o["id"], o["serie"]) for o in occ})
    print(f"Serie ricorrenti — dal {oggi.strftime('%d/%m/%Y')}, {giorni} giorni\n")
    print(f"Righe-serie riconosciute nel master: {len(serie)}")
    for id_, nome in serie:
        quante = len([o for o in occ if o["id"] == id_])
        print(f"   • [{id_}] {nome[:58]} — {quante} appuntamenti")
    print()

    nella_finestra = [o for o in occ if oggi <= o["data"] <= fine]
    if not nella_finestra:
        print("Nessun appuntamento di serie nella finestra.")
        return 0

    scoperte = []
    print("DATA        GG    BUSTA  APPUNTAMENTO")
    for o in nella_finestra:
        tipi = buste.get(o["data"].strftime("%Y%m%d"), set())
        coperto = any("giornaliero" in t for t in tipi) or any("storia" in t for t in tipi)
        if not coperto:
            scoperte.append(o)
        prog = f" — {o['programma']}" if o["programma"] else ""
        print(f"{o['data'].strftime('%d/%m/%Y')}  {GIORNI[o['data'].weekday()][:3]}   "
              f"{'✅' if coperto else '❌'}     [{o['id']}] {o['serie'][:26]}{prog[:40]}")

    print()
    if scoperte:
        print(f"❌ {len(scoperte)} appuntamenti di serie SENZA nessuna busta quel giorno:")
        for o in scoperte:
            prog = f" — {o['programma']}" if o["programma"] else ""
            marchio = "" if o["stato_post"] == "approvato" else f"  ⟵ a registro è `{o['stato_post']}`"
            print(f"   • {o['data'].strftime('%d/%m')} {GIORNI[o['data'].weekday()]}: "
                  f"{o['serie']}{prog} · {o['luogo'][:44]}{marchio}")
        da_approvare = [o for o in scoperte if o["stato_post"] != "approvato"]
        print(f"\n   {len(scoperte) - len(da_approvare)} sono già `approvato` a registro: si compilano subito.")
        if da_approvare:
            print(f"   {len(da_approvare)} NO: servono prima i pulsanti ✅ di Michele su Telegram.")
        print("   Prima di scrivere, apri la riga del master e leggi la nota: il titolo")
        print("   qui sopra è ritagliato dalla prosa, non è testo pronto.")
        return 1

    print("✅ Ogni appuntamento di serie nella finestra ha almeno una busta quel giorno.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
