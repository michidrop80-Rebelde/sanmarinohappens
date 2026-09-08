#!/usr/bin/env python3
"""
TEST OFFLINE di allineati.py — non tocca la rete e non tocca il repo vero.
Si lancia con:  python3 scripts/allineati_test.py

COSA PROVA (e perche')
----------------------
Costruisce in una cartella usa-e-getta un finto GitHub (un repo "nudo") e due
cloni: uno fa la parte del CLOUD, l'altro la parte del MAC. Poi mette il Mac in
ognuna delle situazioni che capiteranno davvero, e controlla che allineati.py
faccia la cosa giusta — soprattutto nel caso brutto, dove la cosa giusta e'
FERMARSI senza perdere niente di Michele.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "allineati.py"
falliti = []


def g(cartella, *args):
    p = subprocess.run(("git",) + args, cwd=cartella, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def allinea(cartella):
    env = dict(os.environ)
    env.pop("GITHUB_ACTIONS", None)
    p = subprocess.run([sys.executable, str(SCRIPT), "prova"],
                       cwd=cartella, capture_output=True, text=True, env=env)
    return p.returncode, (p.stdout + p.stderr).strip()


def controlla(titolo, condizione, dettaglio=""):
    print(("  ✅ " if condizione else "  ❌ ") + titolo + (f" — {dettaglio}" if dettaglio and not condizione else ""))
    if not condizione:
        falliti.append(titolo)


def scenario(tmp):
    """Rifà da zero: finto GitHub + clone cloud + clone Mac, allineati."""
    for n in ("origin.git", "cloud", "mac"):
        shutil.rmtree(Path(tmp) / n, ignore_errors=True)
    origine = Path(tmp) / "origin.git"
    g(tmp, "init", "--bare", "-b", "main", str(origine))
    cloud, mac = Path(tmp) / "cloud", Path(tmp) / "mac"
    g(tmp, "clone", str(origine), str(cloud))
    for c in (cloud,):
        g(c, "config", "user.email", "t@t"); g(c, "config", "user.name", "t")
    (cloud / "master.md").write_text("riga di partenza\n")
    (cloud / "bozze.md").write_text("vuoto\n")
    g(cloud, "add", "-A"); g(cloud, "commit", "-m", "base"); g(cloud, "push", "origin", "main")
    g(tmp, "clone", str(origine), str(mac))
    g(mac, "config", "user.email", "m@m"); g(mac, "config", "user.name", "m")
    return cloud, mac


def cloud_lavora(cloud, file, testo):
    (cloud / file).write_text(testo)
    g(cloud, "add", "-A"); g(cloud, "commit", "-m", "lavoro della notte")
    g(cloud, "push", "origin", "main")


def main():
    tmp = tempfile.mkdtemp(prefix="allineati-test-")
    try:
        print("\n[1] Mac già in pari e pulito → non fa niente, esce 0")
        _, mac = scenario(tmp)
        codice, testo = allinea(mac)
        controlla("esce 0", codice == 0, testo)
        controlla("dice «già in pari»", "già in pari" in testo, testo)

        print("\n[2] Mac in pari ma SPORCO → non tocca le modifiche, esce 0")
        _, mac = scenario(tmp)
        (mac / "master.md").write_text("modifica di Michele\n")
        codice, testo = allinea(mac)
        controlla("esce 0", codice == 0, testo)
        controlla("le modifiche sono ancora lì",
                  (mac / "master.md").read_text() == "modifica di Michele\n")

        print("\n[3] IL CASO DI OGNI GIORNO: cloud ha lavorato, Mac sporco su ALTRI file")
        cloud, mac = scenario(tmp)
        cloud_lavora(cloud, "bozze.md", "3 bozze nuove\n")
        (mac / "master.md").write_text("appunto di Michele\n")
        codice, testo = allinea(mac)
        controlla("esce 0", codice == 0, testo)
        controlla("ha preso il lavoro del cloud",
                  (mac / "bozze.md").read_text() == "3 bozze nuove\n")
        controlla("le modifiche di Michele sono al loro posto",
                  (mac / "master.md").read_text() == "appunto di Michele\n")
        controlla("la cassaforte è stata svuotata (niente copie orfane)",
                  g(mac, "stash", "list")[1] == "")

        print("\n[4] IL CASO BRUTTO: stesso file cambiato da tutti e due → si FERMA")
        cloud, mac = scenario(tmp)
        cloud_lavora(cloud, "master.md", "versione del cloud\n")
        (mac / "master.md").write_text("versione di Michele\n")
        codice, testo = allinea(mac)
        controlla("esce 1 (fermati)", codice == 1, testo)
        controlla("dice che niente è andato perso", "niente è andato perso" in testo, testo)
        controlla("nomina il file", "master.md" in testo, testo)
        controlla("il lavoro di Michele è nella cassaforte",
                  "allineati-prova" in g(mac, "stash", "list")[1],
                  g(mac, "stash", "list")[1])
        controlla("l'albero non ha segnaposto di conflitto",
                  "<<<<<<<" not in (mac / "master.md").read_text())
        controlla("sul disco c'è la versione del cloud",
                  (mac / "master.md").read_text() == "versione del cloud\n")
        codice, _ = g(mac, "stash", "pop")
        controlla("il comando suggerito (git stash pop) riporta il suo lavoro",
                  codice != 0 or "versione di Michele" in (mac / "master.md").read_text())

        print("\n[5] Ramo sbagliato → si ferma prima di toccare qualsiasi cosa")
        _, mac = scenario(tmp)
        g(mac, "checkout", "-b", "altro")
        codice, testo = allinea(mac)
        controlla("esce 1", codice == 1, testo)
        controlla("dice qual è il ramo giusto", "main" in testo, testo)

        print("\n[6] GitHub irraggiungibile → si ferma, non lavora su dati vecchi")
        _, mac = scenario(tmp)
        g(mac, "remote", "set-url", "origin", str(Path(tmp) / "non-esiste.git"))
        codice, testo = allinea(mac)
        controlla("esce 1", codice == 1, testo)
        controlla("spiega il rischio (lista vecchia)", "vecchia" in testo, testo)

        print("\n[7] In cloud non fa nulla: il checkout è già fresco")
        _, mac = scenario(tmp)
        env = dict(os.environ); env["GITHUB_ACTIONS"] = "true"
        p = subprocess.run([sys.executable, str(SCRIPT), "prova"], cwd=mac,
                           capture_output=True, text=True, env=env)
        controlla("esce 0", p.returncode == 0, p.stdout + p.stderr)
        controlla("lo dice", "cloud" in p.stdout, p.stdout)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + ("🎉 tutto verde" if not falliti
                  else f"❌ {len(falliti)} falliti: " + " · ".join(falliti)))
    return 1 if falliti else 0


if __name__ == "__main__":
    sys.exit(main())
