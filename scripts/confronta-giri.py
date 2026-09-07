#!/usr/bin/env python3
"""Confronta il giro del Mac con quello girato in cloud. Chi ha visto cosa?

PERCHE' ESISTE (ticket 08 della mappa "La catena si stacca dal Mac")
Il giro in cloud gira di notte come SECONDO PARERE, sul ramo git `giro-cloud`.
Quello del Mac gira la mattina, dove lavora Michele. Finche' non ci fidiamo del
cloud, la domanda che conta e' una sola: hanno trovato le stesse cose?
Senza questo confronto, "il cloud funziona" resterebbe un'impressione.

COSA FA
Prende i file dei due giri della STESSA data e li mette a fianco:
  - eventi trovati dalla ricerca
  - eventi verificati / da confermare / scartati
  - bozze scritte
Poi dice chi ha visto cosa. I titoli non sono mai identici parola per parola
(due giri a 5 ore di distanza scrivono "36° Palio Don Bosco" e "Palio Don
Bosco 2026"), quindi si confrontano in modo TOLLERANTE: si toglie punteggiatura,
accenti e numeri d'edizione, e si accostano i titoli molto simili.

⚠️ Una differenza NON e' automaticamente un errore del cloud: fra le 03:00 e le
08:05 passano cinque ore, e una fonte puo' pubblicare un evento in mezzo. Serve
a vedere se le differenze sono poche e spiegabili, o tante e strane.

COME SI LANCIA (dal Mac, dopo che sono girati tutti e due)
    python3 scripts/confronta-giri.py
    python3 scripts/confronta-giri.py --data 2026-09-14
    python3 scripts/confronta-giri.py --una-riga     # per il riassunto Telegram

USCITA: 0 sempre (e' un confronto, non una guardia). 3 se il giro in cloud per
quella data non esiste proprio — cosi' chi lo lancia da uno script se ne accorge.
"""

import argparse
import datetime as dt
import importlib.util
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

QUI = Path(__file__).resolve().parent

# Si riusa il lettore di `conta-giro.py`: un secondo lettore degli stessi file
# prima o poi leggerebbe cose diverse, e il confronto mentirebbe senza dirlo.
_spec = importlib.util.spec_from_file_location("conta_giro", QUI / "conta-giro.py")
cg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cg)

FILE_DEL_GIRO = [
    ("dati/eventi", "eventi-{d}.md"),
    ("dati/eventi/verificati", "eventi-verificati-{d}.md"),
    ("dati/post", "post-{d}.md"),
]


def git(*args, dentro=None):
    return subprocess.run(["git", *args], cwd=dentro, capture_output=True, text=True)


# ---------------------------------------------------------------------------
# Confronto tollerante dei titoli
# ---------------------------------------------------------------------------

SOLO_LETTERE = re.compile(r"[^a-z0-9 ]+")
# "36°", "11ª" e l'anno non distinguono un evento da un altro: due giri lo stesso
# giorno scrivono "36° Palio Don Bosco" e "Festa Parrocchiale e Palio Don Bosco 2026".
NUMERO_EDIZIONE = re.compile(r"\b\d{1,3}\s*[°ªa](?![a-z])|\b(19|20)\d{2}\b")
# Parole che non dicono niente su QUALE evento sia.
VUOTE = {
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra", "e", "ed", "o",
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "l",
    "al", "allo", "alla", "ai", "agli", "alle", "del", "dello", "della",
    "dei", "degli", "delle", "dal", "dallo", "dalla", "nel", "nella", "nei",
    "sul", "sulla", "the", "of", "edizione", "ed.",
}


def normalizza(titolo: str) -> str:
    t = unicodedata.normalize("NFKD", titolo.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = NUMERO_EDIZIONE.sub(" ", t)
    t = SOLO_LETTERE.sub(" ", t)
    return " ".join(t.split())


def parole(titolo: str) -> set:
    return {w for w in normalizza(titolo).split() if w not in VUOTE}


def stesso_evento(a: set, b: set) -> bool:
    """Due titoli sono lo stesso evento se uno CONTIENE l'altro.

    ⚠️ Qui non si usa la somiglianza fra stringhe, e per un motivo preciso:
    sbaglia in tutti e due i versi. «San Marino - Finlandia (UEFA Nations
    League)» e «San Marino - Albania (UEFA Nations League)» si somigliano
    quasi del tutto e sono due partite DIVERSE; «Concerto a lume di candela»
    e «Concerto a Lume di Candela — Tributo a Ennio Morricone» si somigliano
    poco e sono lo STESSO concerto.
    Il contenimento li separa per costruzione: nel primo caso «finlandia» e
    «albania» stanno una fuori dall'altra, nel secondo il titolo corto è tutto
    dentro quello lungo.
    Servono almeno due parole vere: «Concerto» da solo starebbe dentro mezza
    stagione teatrale.
    """
    if len(a) < 2 or len(b) < 2:
        return a == b and bool(a)
    return a <= b or b <= a


def accosta(a: list, b: list):
    """Accoppia i titoli dei due giri. Restituisce (comuni, solo_a, solo_b).

    ⚠️ Si lavora su LISTE, non su insiemi: due titoli diversi che si riducono
    alla stessa forma non devono sparire in silenzio. Un confronto che perde
    per strada un evento direbbe una bugia proprio dove serve la verità.
    """
    sinistra = [(t, parole(t)) for t in a]
    destra = [(t, parole(t), False) for t in b]
    destra = [list(x) for x in destra]

    comuni, solo_a = [], []
    for titolo, pa in sinistra:
        preso = None
        # Prima gli identici: se c'è una corrispondenza esatta è quella giusta.
        for voce in destra:
            if not voce[2] and pa == voce[1] and pa:
                preso = voce
                break
        if preso is None:
            for voce in destra:
                if not voce[2] and stesso_evento(pa, voce[1]):
                    preso = voce
                    break
        if preso is None:
            solo_a.append(titolo)
        else:
            preso[2] = True
            comuni.append(titolo)
    return comuni, solo_a, [v[0] for v in destra if not v[2]]


# ---------------------------------------------------------------------------
# Lettura dei due giri
# ---------------------------------------------------------------------------

def impronta(rif: str, percorso: str):
    """L'impronta git del file su quel riferimento, o None se lì non c'è."""
    r = git("rev-parse", f"{rif}:{percorso}")
    return r.stdout.strip() if r.returncode == 0 else None


def base_del_ramo(ramo: str) -> str:
    """Da dove è nato il ramo: è la copia di partenza, non il lavoro del cloud."""
    for candidato in ("origin/main", "main"):
        if git("rev-parse", "--verify", "--quiet", candidato).returncode == 0:
            return candidato
    return ""


def materializza_cloud(ramo: str, data: str, dove: Path):
    """Tira fuori dal ramo i file del giro e li appoggia in una cartella finta.

    Cosi' si possono leggere con LO STESSO lettore usato per i file del Mac.

    ⚠️ Restituisce anche quali file il cloud ha DAVVERO scritto. Il ramo nasce
    come copia di `main`, che contiene già i file del giro del Mac: se un anello
    in cloud non scrive niente, sul ramo resta la copia del Mac — e il confronto
    direbbe «✅ identici» confrontando quei file CON SE' STESSI.
    E' successo davvero nella prima corsa (07/09/2026): tre anelli morti in un
    secondo, e il confronto che dava tutto identico. Un file la cui impronta git
    è la stessa di `main` NON è lavoro del cloud, ed è una bugia contarlo.
    """
    rif = None
    for candidato in (f"origin/{ramo}", ramo):
        if git("rev-parse", "--verify", "--quiet", candidato).returncode == 0:
            rif = candidato
            break
    if rif is None:
        return None, f"il ramo «{ramo}» non esiste (né in locale né su origin)", {}

    base = base_del_ramo(ramo)
    trovato = False
    scritti = {}
    for cartella, modello in FILE_DEL_GIRO:
        percorso = f"{cartella}/{modello.format(d=data)}"
        r = git("show", f"{rif}:{percorso}")
        if r.returncode != 0:
            scritti[percorso] = False
            continue
        trovato = True
        scritti[percorso] = not (base and impronta(rif, percorso) == impronta(base, percorso))
        f = dove / percorso
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(r.stdout, encoding="utf-8")
    if not trovato:
        return None, f"su «{rif}» non c'è nessun file del giro del {data}", {}
    return dove, None, scritti


def leggi(radice: Path, data: str) -> dict:
    e = radice / "dati" / "eventi" / f"eventi-{data}.md"
    v = radice / "dati" / "eventi" / "verificati" / f"eventi-verificati-{data}.md"
    p = radice / "dati" / "post" / f"post-{data}.md"
    ver = cg.titoli_verificati(v) or {}
    return {
        "eventi": cg.titoli_eventi(e) or [],
        "verificati": ver.get("verificati", []),
        "da_confermare": ver.get("da_confermare", []),
        "scartati": ver.get("scartati", []),
        "bozze": (cg.conta_bozze(p) or {}).get("totale", 0),
    }


# ---------------------------------------------------------------------------

def blocco(nome, a, b, mostra=8):
    comuni, solo_mac, solo_cloud = accosta(a, b)
    righe = [f"\n{nome}: Mac {len(a)} · cloud {len(b)} · in comune {len(comuni)}"]
    for etichetta, elenco in (("solo il Mac", solo_mac), ("solo il cloud", solo_cloud)):
        if elenco:
            righe.append(f"  {etichetta} ({len(elenco)}):")
            for t in elenco[:mostra]:
                righe.append(f"    · {t}")
            if len(elenco) > mostra:
                righe.append(f"    … e altri {len(elenco) - mostra}")
    if not solo_mac and not solo_cloud:
        righe.append("  ✅ identici")
    return "\n".join(righe), len(solo_mac), len(solo_cloud)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=dt.date.today().isoformat())
    ap.add_argument("--ramo", default="giro-cloud")
    ap.add_argument("--una-riga", action="store_true",
                    help="solo la riga di riassunto, da mettere nel messaggio Telegram")
    a = ap.parse_args()

    radice_mac = Path(cg.radice_repo())
    git("fetch", "--quiet", "origin", a.ramo)      # se non c'è rete, si prosegue col locale

    with tempfile.TemporaryDirectory() as tmp:
        radice_cloud, errore, scritti = materializza_cloud(a.ramo, a.data, Path(tmp))
        if errore:
            print(f"⚠️ Nessun giro in cloud da confrontare per il {a.data}: {errore}.")
            print("   (Non è un guasto se il giro in cloud non ha ancora girato oggi.)")
            return 3

        # Quali anelli in cloud hanno davvero scritto qualcosa?
        fantasmi = [p for p, vero in scritti.items() if not vero]
        if len(fantasmi) == len(scritti):
            print(f"🛑 Il giro in cloud del {a.data} NON HA PRODOTTO NIENTE.")
            print("   Tutti i file sul ramo sono la copia identica di quelli di main,")
            print("   cioè del giro del Mac: gli anelli in cloud non hanno scritto nulla.")
            print("   Non c'è niente da confrontare — e «identici» qui sarebbe una bugia.")
            print("   Guarda i log della run: quasi certamente l'agente è morto subito.")
            return 4

        mac = leggi(radice_mac, a.data)
        cloud = leggi(radice_cloud, a.data)

        if a.una_riga:
            if fantasmi:
                print("Confronto col cloud: NON CONFRONTABILE — il cloud non ha "
                      f"scritto {len(fantasmi)} file su {len(scritti)} (sono la copia "
                      "di quelli del Mac). Guarda i log della run.")
                return 4
            c, sm, sc = accosta(mac["eventi"], cloud["eventi"])
            cv, svm, svc = accosta(mac["verificati"], cloud["verificati"])
            print(f"Confronto col cloud: eventi {len(mac['eventi'])}/{len(cloud['eventi'])} "
                  f"({len(c)} in comune) · verificati {len(mac['verificati'])}/"
                  f"{len(cloud['verificati'])} ({len(cv)} in comune) · "
                  f"bozze {mac['bozze']}/{cloud['bozze']}")
            return 0

        print(f"Confronto del giro del {a.data} — Mac contro cloud (ramo {a.ramo})")
        print("=" * 66)
        if fantasmi:
            print("\n⚠️ Questi file il cloud NON li ha scritti: sul ramo c'è la copia")
            print("   identica di main, cioè il lavoro del Mac. Le sezioni che ne")
            print("   dipendono qui sotto NON dicono niente sul cloud.")
            for f in fantasmi:
                print(f"     · {f}")

        f_eventi = f"dati/eventi/eventi-{a.data}.md"
        f_verif = f"dati/eventi/verificati/eventi-verificati-{a.data}.md"
        f_post = f"dati/post/post-{a.data}.md"
        for nome, chiave, sorgente in (("Eventi trovati", "eventi", f_eventi),
                                       ("Verificati", "verificati", f_verif),
                                       ("Da confermare", "da_confermare", f_verif),
                                       ("Scartati", "scartati", f_verif)):
            if sorgente in fantasmi:
                print(f"\n{nome}: ⛔ non confrontabile — il cloud non ha scritto "
                      f"{sorgente.split('/')[-1]}")
                continue
            testo, _, _ = blocco(nome, mac[chiave], cloud[chiave])
            print(testo)
        if f_post in fantasmi:
            print("\nBozze scritte: ⛔ non confrontabile — il cloud non ha scritto "
                  f"{f_post.split('/')[-1]}")
        else:
            print(f"\nBozze scritte: Mac {mac['bozze']} · cloud {cloud['bozze']}")
        print("\n⚠️ Fra i due giri passano cinque ore: qualche differenza è normale.")
        print("   Quello che conta è che non siano tante, e che si sappia spiegare "
              "perché ci sono.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
