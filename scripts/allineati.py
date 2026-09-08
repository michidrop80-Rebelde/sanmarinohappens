#!/usr/bin/env python3
"""
allineati.py — prima di lavorare sul Mac, prendi quello che il cloud ha fatto stanotte.
=======================================================================================

COS'E' (spiegato semplice)
--------------------------
Da quando la catena dei testi gira su GitHub (di notte, da sola), le macchine che
scrivono nel progetto sono DUE: il computer di GitHub e il Mac di Michele.

Non e' una gara: fanno lavori diversi, a ore diverse, quasi sempre su file diversi.
Il pericolo non e' che si scontrino — e' che Michele apra il Mac e lavori su una
lista VECCHIA senza accorgersene, perche' il lavoro della notte e' su GitHub e non
ancora sul suo disco.

Questo script e' il passo di allineamento: si mette in pari con GitHub prima che
si tocchi qualsiasi cosa. Se ci riesce, non se ne accorge nessuno. Se NON ci riesce,
si FERMA e dice esattamente cosa non torna — non chiede mai a Michele di sbrogliare
un pasticcio di git, e non butta mai via niente di suo.

PERCHE' NON BASTA `git pull --rebase`
-------------------------------------
Sul Mac ci sono SEMPRE modifiche non salvate (master.md, piano-editoriale.md, il
report). Con l'albero sporco `git pull --rebase` si rifiuta di partire, e le skill
che oggi lo chiamano allo Step 0 si troverebbero un errore secco invece di un
allineamento. Qui le modifiche si mettono da parte, si prende il lavoro del cloud,
e si rimettono a posto.

PERCHE' `apply` E NON `pop`
---------------------------
`pop` cancella la copia messa da parte appena riesce. Se il rimettere-a-posto va in
conflitto, si resta con dei segnaposto di conflitto nei file e la copia gia' persa
di vista. Con `apply` la copia resta nella cassaforte finche' non e' andato tutto
bene: nel caso brutto il lavoro di Michele e' ancora li', intero, e lo script lo
dice con il comando per riprenderlo.

USO
---
    python3 scripts/allineati.py <nome-di-chi-chiama>

Uscite:  0 = allineato (o gia' in pari, o siamo in cloud e non serve)
         1 = FERMATI: c'e' qualcosa che non si incastra, il messaggio dice cosa
         2 = errore d'uso
"""

import os
import subprocess
import sys
from datetime import datetime


def git(*args, check=False):
    """Lancia un comando git nella radice del repo. Ritorna (codice, testo)."""
    p = subprocess.run(("git",) + args, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} → {p.stderr.strip()}")
    return p.returncode, (p.stdout + p.stderr).strip()


def in_cloud():
    return os.environ.get("GITHUB_ACTIONS") == "true"


def radice():
    codice, testo = git("rev-parse", "--show-toplevel")
    return testo if codice == 0 else None


def sporco():
    """Elenco dei file cambiati e non salvati (tracciati o no). Vuoto = pulito."""
    _, testo = git("status", "--porcelain")
    return [r for r in testo.splitlines() if r.strip()]


def ramo():
    _, testo = git("rev-parse", "--abbrev-ref", "HEAD")
    return testo


def main():
    nome = sys.argv[1] if len(sys.argv) > 1 else "smh"

    # In cloud il checkout e' appena stato fatto: e' gia' la versione buona.
    if in_cloud():
        print("☁️  in cloud: il checkout è già fresco, niente da allineare")
        return 0

    base = radice()
    if base is None:
        print("⛔ non siamo dentro il repo del progetto: non allineo niente",
              file=sys.stderr)
        return 2
    os.chdir(base)

    ramo_attuale = ramo()
    if ramo_attuale != "main":
        print(f"⛔ FERMATI — sei sul ramo «{ramo_attuale}», non su «main».\n"
              f"   Il lavoro del cloud arriva su main. Torna lì prima di lavorare:\n"
              f"       git checkout main")
        return 1

    # 1. C'E' DAVVERO QUALCOSA DA PRENDERE?
    codice, testo = git("fetch", "origin", "main")
    if codice != 0:
        print("⛔ FERMATI — non riesco a raggiungere GitHub, quindi non posso sapere\n"
              "   se il cloud ha lavorato stanotte. Lavorare adesso vorrebbe dire\n"
              "   rischiare di graficare una lista vecchia.\n"
              "   Controlla la connessione e rilancia.\n"
              f"   (git dice: {testo.splitlines()[-1] if testo else 'nessun dettaglio'})")
        return 1

    _, dietro = git("rev-list", "--count", "HEAD..origin/main")
    dietro = int(dietro) if dietro.isdigit() else 0
    modifiche = sporco()

    if dietro == 0:
        print(f"✅ già in pari con GitHub"
              + (f" · {len(modifiche)} file non salvati, lasciati dove sono"
                 if modifiche else ""))
        return 0

    # 2. METTI DA PARTE IL LAVORO NON SALVATO
    etichetta = f"allineati-{nome}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    messo_da_parte = False
    if modifiche:
        codice, testo = git("stash", "push", "-u", "-m", etichetta)
        if codice != 0:
            print("⛔ FERMATI — non riesco a mettere da parte le tue modifiche.\n"
                  "   Non ho toccato niente.\n"
                  f"   (git dice: {testo})")
            return 1
        messo_da_parte = True

    # 3. PRENDI IL LAVORO DEL CLOUD
    codice, testo = git("pull", "--rebase", "origin", "main")
    if codice != 0:
        git("rebase", "--abort")
        if messo_da_parte:
            git("stash", "pop")
        print(f"⛔ FERMATI — non riesco a prendere il lavoro del cloud ({dietro} "
              f"cambiamenti in attesa).\n"
              "   Ho rimesso tutto com'era: non hai perso niente.\n"
              f"   (git dice: {testo.splitlines()[-1] if testo else 'nessun dettaglio'})")
        return 1

    # 4. RIMETTI A POSTO IL LAVORO NON SALVATO
    if messo_da_parte:
        codice, testo = git("stash", "apply")
        if codice != 0:
            # Caso raro e vero: lo stesso file cambiato da tutti e due.
            # Il lavoro di Michele NON e' perduto: la copia e' ancora nella
            # cassaforte. Riporto l'albero pulito e glielo dico.
            # I nomi si prendono PRIMA di ripulire: dopo la pulizia
            # l'albero e' immacolato e non direbbe piu' quali file erano.
            _, elenco = git("diff", "--name-only", "--diff-filter=U")
            if not elenco.strip():
                _, elenco = git("stash", "show", "--name-only", "stash@{0}")
            in_conflitto = [r for r in elenco.splitlines() if r.strip()] or [
                "(vedi git stash show)"]
            git("checkout", "-f", "HEAD", "--", ".")
            print("⛔ FERMATI — il cloud e tu avete cambiato lo stesso file.\n"
                  "   Ho preso il lavoro del cloud. Le TUE modifiche sono al sicuro,\n"
                  "   niente è andato perso: sono nella cassaforte di git.\n"
                  "   File coinvolti: " + ", ".join(in_conflitto) + "\n"
                  "   Per rivederle:   git stash show -p stash@{0}\n"
                  "   Per riprenderle: git stash pop\n"
                  "   Non fare la grafica finché non è chiaro quale versione vale.")
            return 1
        git("stash", "drop")

    print(f"✅ allineato con GitHub — presi {dietro} cambiamenti dal cloud"
          + (f", le tue {len(modifiche)} modifiche non salvate sono al loro posto"
             if messo_da_parte else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
