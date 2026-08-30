#!/usr/bin/env python3
"""
segnala-doppioni.py — impedisce che si approvi due volte lo stesso giorno.

COS'E' (spiegato semplice)
--------------------------
L'agente dei testi scrive una bozza per OGNI evento verificato. Ma non sa niente di cosa
sia gia' in coda di pubblicazione: e' cieco. Cosi' capita che riscriva la bozza di un post
gia' pronto — o addirittura gia' uscito.

Successo davvero il 27/07/2026: delle 36 bozze del giro del mattino, **19 erano per giorni
che avevano gia' il loro post giornaliero** in coda o nell'archivio. La prima della lista era
il 27/07 stesso, pubblicato quella mattina. Se Michele avesse risposto «✅ approva tutto»,
la grafica avrebbe ricompilato 19 post gia' fatti, sovrascrivendo buste che avevano gia'
passato il cancello di controllo.

Questo script chiude il buco: confronta le bozze con la coda vera (letta dal remoto, come fa
`controllo-copertura.py`) e mette le bozze doppione in stato `gia-in-coda`, cosi' l'agente di
approvazione — che cerca solo `da-approvare` — non le propone piu'.

USO
---
  python3 scripts/segnala-doppioni.py            # segnala e CORREGGE il file bozze piu' recente
  python3 scripts/segnala-doppioni.py --prova    # dice solo cosa farebbe, non tocca niente

Va lanciato SUBITO DOPO l'agente dei testi (Step 3 di /smh-giro), prima di chiedere
l'approvazione a Michele.
"""
import re
import subprocess
import sys
from pathlib import Path

PROGETTO = Path(__file__).resolve().parent.parent
CARTELLA_BOZZE = PROGETTO / "dati" / "post"
ANNO = 2026

SOLO_PROVA = "--prova" in sys.argv


def coda_dal_remoto():
    """Le date (AAAAMMGG) che hanno gia' un post giornaliero in coda o in archivio.
    Si legge dal REMOTO perche' e' li' che vive la verita': il Mac puo' essere indietro."""
    subprocess.run(["git", "fetch", "-q", "origin"], cwd=PROGETTO, check=False)
    out = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "origin/main", "posts/", "archivio/"],
        cwd=PROGETTO, capture_output=True, text=True, check=True,
    ).stdout
    date = set()
    for riga in out.splitlines():
        m = re.search(r"(\d{8})_(.+)\.json$", riga)
        if m and "giornaliero" in m.group(2).lower():
            date.add(m.group(1))
    return date


def ultimo_file_bozze():
    candidati = sorted(CARTELLA_BOZZE.glob("post-????-??-??*.md"))
    for f in reversed(candidati):
        if "da-approvare" in f.read_text():
            return f
    return None


def main():
    f = ultimo_file_bozze()
    if f is None:
        print("ℹ️  Nessun file bozze con post da approvare: niente da fare.")
        return 0

    gia_in_coda = coda_dal_remoto()
    testo = f.read_text()
    # Un blocco bozza va da un "## [GG/MM] — Titolo" al successivo.
    blocchi = re.split(r"(?m)^(?=## \[\d{2}/\d{2}\])", testo)

    doppioni, buone, nuovo = [], [], []
    for b in blocchi:
        intestazione = re.match(r"## \[(\d{2})/(\d{2})\] — (.+?)(?:\s+·|\n)", b)
        if not intestazione or "**Stato bozza:** da-approvare" not in b:
            nuovo.append(b)
            continue
        giorno, mese, titolo = intestazione.groups()
        chiave = f"{ANNO}{mese}{giorno}"
        if chiave in gia_in_coda:
            doppioni.append((f"{giorno}/{mese}", titolo.strip()))
            b = b.replace(
                "**Stato bozza:** da-approvare",
                "**Stato bozza:** gia-in-coda\n"
                "**Nota automatica:** questo giorno ha gia' un post giornaliero in coda o "
                "pubblicato — bozza NON proposta per l'approvazione (scripts/segnala-doppioni.py).",
                1,
            )
        else:
            buone.append((f"{giorno}/{mese}", titolo.strip()))
        nuovo.append(b)

    print(f"File bozze: {f.relative_to(PROGETTO)}")
    print(f"🔴 doppioni (giorno gia' coperto): {len(doppioni)}")
    for d, t in doppioni:
        print(f"   {d}  {t[:60]}")
    print(f"🟢 bozze davvero da approvare: {len(buone)}")
    for d, t in buone:
        print(f"   {d}  {t[:60]}")

    if SOLO_PROVA:
        print("\n🔍 Prova soltanto: non ho toccato il file.")
        return 0
    if doppioni:
        f.write_text("".join(nuovo))
        print(f"\n✅ {len(doppioni)} bozze messe in stato `gia-in-coda`: "
              "l'approvazione non le propone piu'.")
    else:
        print("\n✅ Nessun doppione: file lasciato com'era.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
