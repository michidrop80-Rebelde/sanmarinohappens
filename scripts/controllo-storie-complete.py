#!/usr/bin/env python3
"""
Guardia di completezza storie — San Marino Happens

A cosa serve
------------
`controllo-copertura.py` dice SE esiste una busta storia per un giorno. Questo
script va un passo oltre: dice se quella busta contiene DAVVERO tutti gli
eventi approvati di quel giorno, non solo "una storia qualsiasi".

Perché esiste
-------------
Chiesto da Michele il 24/08/2026: "nel riepilogo delle storie ci devono
essere TUTTI gli eventi, non deve mancare nulla — anche se uno lo abbiamo
pubblicato come post deve rientrare nel programma delle storie". Verificando
si sono trovati subito 3 casi concreti di eventi approvati che non sono MAI
finiti in nessuna storia:
  - "DiscOttanta Novanta e non solo" (14/08) — sparito quando la sua data è
    stata corretta il giorno stesso da 15/08 a 14/08 (riga 44b del master):
    la storia del 14/08 era già stata compilata sull'informazione vecchia.
  - "Pellegrinaggio sui passi di San Marino e San Francesco" (29/08,
    approvato 17/08) — mai compilato, esiste solo nel riepilogo settimanale.
  - "33° San Marino Revival" — rinviato dal 01-02/08 al 29-30/08 (28/07): la
    storia vecchia (01/08) è stata corretta negli AGGREGATI ma non è mai
    stata ricompilata per le date nuove.
  - "San Marino Comics 2026" (28-30/08, evento multi-giorno) — ha una storia
    solo per il 28/08: il 29 e il 30 sparisce dal riepilogo pur essendo
    ancora in corso.

Il problema di fondo: `smh-grafica` compila le storie di un giorno
guardando cosa gli viene segnalato in quel momento, non incrocia mai
sistematicamente "tutti gli eventi approvati attivi oggi" — quindi un evento
multi-giorno, o corretto/aggiunto dopo che la storia del giorno era già
stata fatta, può restare fuori senza che nessuno se ne accorga.

Come controlla
---------------
Per ogni giorno della finestra: legge da `dati/calendario/master.md` tutti
gli eventi **approvati** (stato post = `approvato`, non barrati, non
scartati) attivi quel giorno — un evento multi-giorno (es. "29–30/08") conta
per OGNI giorno del suo intervallo, non solo il primo. Poi legge il
contenuto della busta storia di quel giorno (coda remota GitHub, `posts/` o
`archivio/`) e cerca una parola-chiave distintiva di ogni evento dentro il
suo `titolo_evento`. Se non la trova, segnala l'evento come probabilmente
assente.

⚠️ È un controllo EURISTICO (parola chiave, non un ID univoco): può dare
qualche falso positivo su titoli molto brevi o generici — è pensato per
essere letto e verificato a occhio, non eseguito alla cieca.

Uso
---
    python3 scripts/controllo-storie-complete.py            # da 21gg fa a 14gg avanti
    python3 scripts/controllo-storie-complete.py 60 0       # ultimi 60gg, nessun giorno avanti

Esce con codice 1 se trova almeno un possibile buco.
"""

import collections
import datetime
import json
import pathlib
import re
import subprocess
import sys
import unicodedata

REPO = pathlib.Path(__file__).resolve().parent.parent
MASTER = REPO / "dati" / "calendario" / "master.md"
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ANNO = datetime.date.today().year

# Stesse regex di scripts/genera-calendario.py (tenute in sync a mano: sono
# poche righe, duplicarle qui evita un import fragile su un modulo con un
# trattino nel nome).
RANGE_MESE_UNICO = re.compile(r"(?<![/.\d])(\d{1,2})\s*[–—-]\s*(\d{1,2})\s*[/.](\d{1,2})")
DATA_COMPLETA = re.compile(r"(\d{1,2})[/.](\d{1,2})")

# Righe con un intervallo più lungo di questo NON sono "lo stesso evento attivo ogni
# giorno": sono voci-serie (Cinema nei Castelli 03-26/08, Alba sul Monte 26/07-23/08,
# ognuna con un'occorrenza diversa ogni giorno, il dettaglio giorno-per-giorno vive nelle
# Note del master, non in righe separate) — il controllo qui sotto le confonderebbe con
# un singolo evento multi-giorno reale (es. San Marino Comics, 2 notti) e le segnalerebbe
# ogni santo giorno. Un vero evento multi-giorno in questo calendario dura al massimo
# pochi giorni (feste/sagre di paese: 2-3 notti); oltre, è quasi certo una serie.
INTERVALLO_MASSIMO_EVENTO_SINGOLO = 4  # giorni di differenza fine-inizio

PAROLE_GENERICHE = {
    "san", "marino", "sammarinese", "sammarinesi", "di", "del", "della", "dei", "delle",
    "il", "la", "lo", "i", "gli", "le", "e", "a", "al", "alla", "con", "per", "in", "su",
    "da", "sui", "sulla", "sul", "un", "una", "2026", "smh", "sanmarinohappens",
}


def _accento_via(testo: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", testo) if not unicodedata.combining(c))


def _data(giorno: int, mese: int):
    try:
        return datetime.date(ANNO, mese, giorno)
    except ValueError:
        return None


def _estremi(campo: str):
    m = RANGE_MESE_UNICO.search(campo)
    if m:
        g_inizio, g_fine, mese = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _data(g_inizio, mese), _data(g_fine, mese)
    tutte = DATA_COMPLETA.findall(campo)
    if not tutte:
        return None, None
    return (_data(int(tutte[0][0]), int(tutte[0][1])),
            _data(int(tutte[-1][0]), int(tutte[-1][1])))


def _pulisci(testo: str) -> str:
    testo = re.sub(r"~~(.+?)~~", r"\1", testo)
    testo = re.sub(r"\*\*(.+?)\*\*", r"\1", testo)
    return testo.strip()


def parola_chiave(titolo: str) -> str:
    """La parola più distintiva del titolo: la più lunga tra quelle non generiche."""
    pulito = _accento_via(_pulisci(titolo)).lower()
    pulito = re.sub(r"[^a-z0-9\s]", " ", pulito)
    parole = [p for p in pulito.split() if p not in PAROLE_GENERICHE and len(p) > 2]
    if not parole:
        return _accento_via(_pulisci(titolo)).lower()[:12]
    return max(parole, key=len)


def eventi_approvati():
    """Eventi con stato post = approvato dal registro master, ognuno con
    (inizio, fine, titolo, parola_chiave)."""
    dentro = False
    eventi = []
    for riga in MASTER.read_text(encoding="utf-8").splitlines():
        if riga.startswith("## 🗓"):
            dentro = True
            continue
        if dentro and riga.startswith("## "):
            break
        if not dentro or not riga.startswith("|"):
            continue
        celle = [c.strip() for c in riga.strip().strip("|").split("|")]
        if len(celle) < 7 or celle[0] in ("#", "---") or not celle[0][0].isdigit():
            continue
        _id, data_txt, titolo, _tipo, _luogo, stato = celle[:6]
        stato_post = celle[6]
        if titolo.startswith("~~"):
            continue
        if "scartato" in _pulisci(stato_post).lower():
            continue
        if "da-confermare" in _pulisci(stato).lower():
            continue
        if _pulisci(stato_post).lower() != "approvato":
            continue  # non ancora approvato: non è ancora compito delle storie
        inizio, fine = _estremi(data_txt)
        if inizio is None:
            continue
        if fine and (fine - inizio).days > INTERVALLO_MASSIMO_EVENTO_SINGOLO:
            continue  # voce-serie (occorrenze diverse ogni giorno), non un evento continuo
        eventi.append({
            "id": _id,
            "titolo": _pulisci(titolo),
            "inizio": inizio,
            "fine": fine or inizio,
            "chiave": parola_chiave(titolo),
        })
    return eventi


def buste_storia_dal_remoto():
    """{AAAAMMGG: [percorsi git]} delle buste storia (posts/ e archivio/).

    Un giorno può avere PIÙ buste storia separate (es. una del mattino con la
    storia regolare + una aggiunta più tardi per un evento urgente — è successo
    proprio il 24/08/2026 con la gara 7 di baseball, `..._Storia.json` +
    `..._Storia_2.json`): tutte vanno raccolte e messe insieme, non solo la
    prima trovata."""
    subprocess.run(["git", "fetch", "-q", "origin"], cwd=REPO, check=False)
    out = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "origin/main", "posts/", "archivio/"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout
    percorsi = collections.defaultdict(list)
    for riga in out.splitlines():
        m = re.search(r"^((?:posts|archivio/[^/]+))/(\d{8})_[Ss]toria(?:_\d+)?\.json$", riga)
        if m:
            percorsi[m.group(2)].append(riga)
    return percorsi


def contenuto_busta(percorsi) -> str:
    testo = []
    for percorso in percorsi:
        out = subprocess.run(
            ["git", "show", f"origin/main:{percorso}"],
            cwd=REPO, capture_output=True, text=True, check=False,
        )
        if out.returncode != 0:
            continue
        try:
            d = json.loads(out.stdout)
            testo.append(str(d.get("titolo_evento", "")))
        except json.JSONDecodeError:
            testo.append(out.stdout)
    return _accento_via(" | ".join(testo)).lower()


def main():
    giorni_indietro = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    giorni_avanti = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    oggi = datetime.date.today()
    inizio_finestra = oggi - datetime.timedelta(days=giorni_indietro)
    fine_finestra = oggi + datetime.timedelta(days=giorni_avanti)

    eventi = eventi_approvati()
    buste = buste_storia_dal_remoto()

    print(f"Completezza storie — dal {inizio_finestra.strftime('%d/%m/%Y')} "
          f"al {fine_finestra.strftime('%d/%m/%Y')}\n")

    problemi = []
    giorno = inizio_finestra
    while giorno <= fine_finestra:
        attivi = [e for e in eventi if e["inizio"] <= giorno <= e["fine"]]
        if attivi:
            percorso = buste.get(giorno.strftime("%Y%m%d"))
            testo_busta = contenuto_busta(percorso) if percorso else ""
            if not percorso:
                mancanti = attivi  # nessuna busta = tutti assenti (ma è già il dominio di controllo-copertura)
                stato = "NESSUNA BUSTA STORIA"
            else:
                mancanti = [e for e in attivi if e["chiave"] not in testo_busta]
                stato = "completa" if not mancanti else "INCOMPLETA"
            if mancanti:
                problemi.append((giorno, mancanti, stato))
        giorno += datetime.timedelta(days=1)

    if not problemi:
        print("✅ Nessun buco trovato: ogni evento approvato attivo in questa finestra")
        print("   compare (parola chiave trovata) nella storia del suo giorno.")
        return 0

    print(f"⚠️  {len(problemi)} giorni con probabili eventi mancanti dalle storie:\n")
    for giorno, mancanti, stato in problemi:
        marcatore = "❌" if giorno <= oggi else "⚠️ "
        print(f"{marcatore} {giorno.strftime('%d/%m/%Y')} {GIORNI[giorno.weekday()]} — {stato}")
        for e in mancanti:
            intervallo = (f"{e['inizio'].strftime('%d/%m')}–{e['fine'].strftime('%d/%m')}"
                          if e["fine"] != e["inizio"] else e["inizio"].strftime("%d/%m"))
            print(f"     • {e['titolo']}  (riga {e['id']}, attivo {intervallo}, "
                  f"parola chiave cercata: «{e['chiave']}»)")
        print()

    print("Nota: controllo euristico (parola chiave nel titolo della busta) — verifica a")
    print("occhio prima di ricompilare. I giorni già passati (❌) sono storia ormai persa")
    print("(non recuperabile sui social); quelli futuri (⚠️) si possono ancora chiudere.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
