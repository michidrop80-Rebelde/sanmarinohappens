#!/usr/bin/env python3
"""Prove del confronto fra il giro del Mac e quello in cloud (ticket 08).

Il rischio vero di questo confronto non è che si rompa: è che MENTA in silenzio.
Se accostasse male i titoli direbbe «il cloud ha perso 8 eventi» quando li ha
trovati tutti, scritti un po' diversamente — e il cloud verrebbe bocciato per un
difetto che non ha. Qui si prova proprio quello, su titoli veri del progetto.

    python3 scripts/confronta_giri_test.py
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

DATA = "2026-09-07"


def _git(dove, *a):
    subprocess.run(["git", *a], cwd=dove, check=True, capture_output=True)


def scena_git(tmp: Path, scritti):
    """Un repo finto: `main` col giro del Mac, il ramo `giro-cloud` col cloud."""
    percorsi = {
        "eventi": f"dati/eventi/eventi-{DATA}.md",
        "verificati": f"dati/eventi/verificati/eventi-verificati-{DATA}.md",
        "post": f"dati/post/post-{DATA}.md",
    }
    _git(tmp, "init", "--quiet", "-b", "main")
    _git(tmp, "config", "user.email", "prova@example.com")
    _git(tmp, "config", "user.name", "Prova")
    for chiave, percorso in percorsi.items():
        f = tmp / percorso
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(f"# giro del Mac\n\n## Evento {chiave}\n", encoding="utf-8")
    _git(tmp, "add", "-A")
    _git(tmp, "commit", "--quiet", "-m", "giro del Mac")
    _git(tmp, "checkout", "--quiet", "-b", "giro-cloud")
    for chiave in scritti:
        (tmp / percorsi[chiave]).write_text(
            f"# giro del CLOUD\n\n## Evento {chiave} riscritto\n", encoding="utf-8")
    if scritti:
        _git(tmp, "add", "-A")
        _git(tmp, "commit", "--quiet", "-m", "giro del cloud")
    _git(tmp, "checkout", "--quiet", "main")

QUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("confronta", QUI / "confronta-giri.py")
c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c)

OK = KO = 0


def verifica(descrizione, condizione):
    global OK, KO
    if condizione:
        OK += 1
        print(f"  ✅ {descrizione}")
    else:
        KO += 1
        print(f"  ❌ {descrizione}")


# Coppie VERE, prese dai file del 07/09/2026: a sinistra come le ha scritte la
# ricerca, a destra come le ha riscritte la verifica. Sono lo stesso evento.
STESSO_EVENTO = [
    ("36° Palio Don Bosco", "Festa Parrocchiale e Palio Don Bosco 2026"),
    ("San Marino - Kosovo U21 (Qualificazioni Europei 2027)",
     "San Marino U21 vs Kosovo U21 — Qualificazioni Europei U21 2027"),
    ("11ª Renata Tebaldi International Voice Competition",
     "11ª edizione Renata Tebaldi International Voice Competition — Opera Section"),
    ("Concerto a lume di candela",
     "Concerto a Lume di Candela — Tributo a Ennio Morricone"),
    ("Dal Turista al Contadino 2026", '"Dal Turista al Contadino" — II tappa'),
]

EVENTI_DIVERSI = [
    ("San Marino - Finlandia (UEFA Nations League)",
     "San Marino - Albania (UEFA Nations League)"),
    ("San Marino Beer Fest 2026 — I edizione", "Musikfest Adriatica"),
]


def main():
    print("\n[1] Titoli scritti diversamente = stesso evento, non due")
    for a, b in STESSO_EVENTO:
        comuni, solo_a, solo_b = c.accosta([a], [b])
        verifica(f"«{a[:34]}…» ≡ «{b[:34]}…»",
                 len(comuni) == 1 and not solo_a and not solo_b)

    print("\n[2] Due eventi davvero diversi NON vengono fusi")
    for a, b in EVENTI_DIVERSI:
        comuni, solo_a, solo_b = c.accosta([a], [b])
        verifica(f"«{a[:30]}…» ≠ «{b[:30]}…»",
                 not comuni and len(solo_a) == 1 and len(solo_b) == 1)

    print("\n[3] Un evento visto solo da uno dei due viene detto")
    mac = [a for a, _ in STESSO_EVENTO]
    cloud = [b for _, b in STESSO_EVENTO][:-1] + ["Sagra della Tagliatella"]
    comuni, solo_mac, solo_cloud = c.accosta(mac, cloud)
    verifica("4 in comune", len(comuni) == 4)
    verifica("1 visto solo dal Mac", len(solo_mac) == 1)
    verifica("1 visto solo dal cloud", len(solo_cloud) == 1)
    verifica("dice QUALE ha visto solo il cloud",
             solo_cloud == ["Sagra della Tagliatella"])

    print("\n[4] Nessun doppio conteggio: un titolo si accosta a UNO solo")
    comuni, solo_mac, solo_cloud = c.accosta(
        ["San Marino Beer Fest 2026 — I edizione",
         "San Marino Beer Fest 2026 — II edizione"],
        ["San Marino Beer Fest 2026 — I edizione"])
    verifica("un solo accostamento", len(comuni) == 1)
    verifica("l'altro resta scoperto", len(solo_mac) == 1)

    print("\n[5] Legge i file veri del progetto con lo stesso lettore del contatore")
    radice = c.Path(c.cg.radice_repo())
    g = c.leggi(radice, "2026-09-07")
    # 20 e non 22: fino al 08/09/2026 il contatore prendeva per eventi anche le due
    # intestazioni di servizio in fondo al file ("Fonti non raggiungibili",
    # "Auto-miglioramento di oggi"). Ora un evento si riconosce dal campo Stato.
    verifica("20 eventi trovati", len(g["eventi"]) == 20)
    verifica("21 verificati", len(g["verificati"]) == 21)
    verifica("1 scartato (prima finiva fra i verificati o spariva)",
             len(g["scartati"]) == 1)
    verifica("24 bozze", g["bozze"] == 24)
    verifica("i marcatori ⚠️/🗑 non finiscono dentro il titolo",
             all(not t.startswith(("⚠", "🗑", "✅"))
                 for t in g["da_confermare"] + g["scartati"]))

    print("\n[6] Confrontare un giro con sé stesso non trova differenze")
    comuni, solo_mac, solo_cloud = c.accosta(g["eventi"], list(g["eventi"]))
    verifica("tutti in comune, zero differenze",
             len(comuni) == 20 and not solo_mac and not solo_cloud)

    print("\n[7] Se il giro in cloud non c'è, lo dice invece di inventarselo")
    with tempfile.TemporaryDirectory() as tmp:
        dove, errore, _ = c.materializza_cloud("ramo-che-non-esiste-mai",
                                               "2026-09-07", Path(tmp))
        verifica("nessuna cartella", dove is None)
        verifica("spiega perché", "non esiste" in (errore or ""))

    print("\n[8] Il guasto vero del 07/09: un file che il cloud NON ha scritto")
    # Il ramo nasce come copia di main, che ha già i file del giro del Mac. Se un
    # anello in cloud muore, sul ramo resta la copia — e il confronto diceva
    # «✅ identici» confrontando quei file CON SE' STESSI. Era una bugia, ed è
    # esattamente il caso che si è verificato nella prima corsa.
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        scena_git(tmp, scritti=("post",))
        vecchia = os.getcwd()
        try:
            os.chdir(tmp)
            dove, errore, scritti = c.materializza_cloud("giro-cloud", DATA, tmp / "estratti")
            verifica("nessun errore: i file ci sono", errore is None)
            verifica("l'evento NON è considerato scritto dal cloud",
                     scritti[f"dati/eventi/eventi-{DATA}.md"] is False)
            verifica("i verificati NON sono considerati scritti dal cloud",
                     scritti[f"dati/eventi/verificati/eventi-verificati-{DATA}.md"] is False)
            verifica("le bozze SI', quelle le ha riscritte davvero",
                     scritti[f"dati/post/post-{DATA}.md"] is True)
        finally:
            os.chdir(vecchia)

    print(f"\n{'='*60}\n✅ {OK} verifiche passate   ❌ {KO} fallite\n{'='*60}")
    return 1 if KO else 0


if __name__ == "__main__":
    sys.exit(main())
