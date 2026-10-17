#!/usr/bin/env python3
"""Scrive il referto della catena serale in cloud (il testo che Michele legge sul telefono).

Ticket 15. Non tocca nessuna chiave: scrive solo /tmp/referto.txt e /tmp/riepilogo.md;
a spedirlo ci pensa un passo dopo (regola del ticket 07).

LEGGE dall'ambiente: DATA, RIPRESA, LAVORO (si|no), DUBBIO, N_APPR, N_SEGN, N_ANNUL,
IMMINENTI, GRAFICA_DA_FARE, AGENTE_STATO ("" se non e' partito), AGENTE_COSTO,
GUARDIE (testo), RUN_URL, e il file dati/cloud-serata/<DATA>/confronto-ieri.txt +
dati/cloud-serata/storico.md se esistono.
SCRIVE su GITHUB_OUTPUT: manda=si|no

COSA DICE (e perche')
- Il messaggio e' SENZA pulsanti e marcato "secondo parere": un solo mazzo di ✅/❌ in giro.
- Parla di ieri (il confronto si puo' fare solo quando il Mac ha avuto il tempo di
  lavorare) e di stasera (cosa ha fatto il cloud).
- Non manda niente se non c'e' un esito: "non ho fatto niente" ogni sera insegna a
  ignorare i referti. Un agente caduto manda SEMPRE.
"""
import os
import re
from pathlib import Path


def env(n, d=""):
    return os.environ.get(n, d) or d


def prove_vere(storico: Path):
    """(concordi, misurate): serate in cui ENTRAMBI hanno lavorato e il confronto e' possibile."""
    if not storico.exists():
        return 0, 0
    conc = mis = 0
    for r in storico.read_text(encoding="utf-8").splitlines():
        m = re.match(r"(\d{4}-\d{2}-\d{2}) \| (\d) \| (.*)", r)
        if not m:
            continue
        cod, verd = m.group(2), m.group(3)
        if cod == "4" or "niente da fare" in verd:
            continue  # non confrontabile / nessuno aveva da fare: non e' una prova
        mis += 1
        conc += cod == "0"
    return conc, mis


def costruisci():
    data = env("DATA")
    d = Path("dati/cloud-serata")
    ieri = d / data / "confronto-ieri.txt"
    righe = [f"🧪 SECONDO PARERE — catena serale in cloud, {data}", "(nessun pulsante: valgono quelli del Mac)", ""]
    manda = False

    testo_ieri = ieri.read_text(encoding="utf-8").strip() if ieri.exists() else ""
    if testo_ieri:
        righe += ["Serata di ieri, cloud contro Mac:", testo_ieri, ""]
        prima = testo_ieri.splitlines()[0]
        if "niente da fare" not in prima:
            manda = True
        c, m = prove_vere(d / "storico.md")
        if m:
            righe += [f"Prove vere finora: {c} sere concordi su {m} confrontabili.", ""]

    stato = env("AGENTE_STATO")
    if env("LAVORO") == "si":
        manda = True
        quanto = (f"approvazioni {env('N_APPR')} · segnalazioni {env('N_SEGN')} · annullamenti {env('N_ANNUL')} · "
                  f"buchi 48h {env('IMMINENTI')}")
        righe.append(f"Stasera c'era lavoro: {quanto}.")
        if env("DUBBIO") == "si":
            righe.append("⚠️ Un controllo non ha saputo rispondere: sono partito per prudenza.")
        if stato.startswith("fatta"):
            righe.append(f"✅ L'agente ha finito (costo ${env('AGENTE_COSTO', '?')}).")
        else:
            righe.append(f"🔴 L'agente NON ha finito: {stato or 'non è partito'}. Il Mac resta il titolare, ma questa sera non fa da prova.")
        g = env("GUARDIE").strip()
        if g:
            righe += ["Guardie: " + g]
        if env("GRAFICA_DA_FARE") == "si":
            righe.append("🎨 C'è anche grafica da fare: è roba da Mac, qui non si fa.")
    else:
        righe.append("Stasera niente da fare: l'agente non è partito (costo zero).")
    if env("RIPRESA") == "si":
        righe.append("(è una ripresa: il ramo di stasera esisteva già)")
    if env("RUN_URL"):
        righe += ["", env("RUN_URL")]

    testo = "\n".join(righe)
    Path("/tmp/referto.txt").write_text(testo, encoding="utf-8")
    Path("/tmp/riepilogo.md").write_text("```\n" + testo + "\n```\n", encoding="utf-8")
    out = env("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"manda={'si' if manda else 'no'}\n")
    print(testo)
    return manda


if __name__ == "__main__":
    costruisci()
