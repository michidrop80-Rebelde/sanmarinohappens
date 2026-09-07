#!/usr/bin/env python3
"""
controllo-token-agente.py — l'agente non deve MAI avere in mano una chiave.

COS'È (spiegato semplice)
-------------------------
L'agente che gira per il web legge pagine scritte da sconosciuti. Se una di
quelle pagine contenesse istruzioni nascoste, l'agente non deve avere niente di
pericoloso a portata: niente chiave di Telegram, di Instagram, di Facebook.
Per questo, nei file che comandano GitHub (`.github/workflows/*.yml`), il passo
che lancia `claude` riceve SOLO il token dell'abbonamento, e a spedire i
messaggi ci pensa un passo separato che non ragiona.

Finora questa regola viveva dentro un commento. Un commento non ferma nessuno:
basta una riga aggiunta con leggerezza fra sei mesi e la regola salta in
silenzio. Questa guardia la fa rispettare: legge i workflow e va in ROSSO se
trova un passo che lancia l'agente avendo in mano una chiave.

Decisione Q5 del ticket 07 della mappa "La catena si stacca dal Mac".

COME SI LANCIA
    python3 scripts/controllo-token-agente.py
    (0 = tutto a posto · 1 = un passo agentico ha in mano una chiave)

PERCHE' NON USA UNA LIBRERIA YAML
Sul Mac di Michele PyYAML non è installato, e una guardia che non gira sul Mac
non serve a niente. Qui basta leggere le righe: i workflow di questo progetto
hanno una forma semplice e prevedibile.
"""

import re
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
CARTELLA = RADICE / ".github" / "workflows"

# Chiavi che l'agente non deve mai vedere: aprono un canale verso il mondo
# (mandare messaggi, pubblicare post, far partire altre corse).
PERICOLOSE = re.compile(r"TELEGRAM|INSTAGRAM|FACEBOOK|META_|PAGE_|CANVA|WEBHOOK|_PAT\b|PAT_")
# Quelle che invece SERVONO all'agente per esistere, e non aprono canali suoi.
AMMESSE = {"CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY", "GITHUB_TOKEN"}

RIF_SEGRETO = re.compile(r"\$\{\{\s*secrets\.([A-Za-z0-9_]+)\s*\}\}")
# "lancia l'agente" = una riga che esegue `claude` con delle opzioni, oppure
# un'azione ufficiale di Claude. `npm install @anthropic-ai/claude-code` no:
# installare non è lanciare.
LANCIA_AGENTE = re.compile(r"(^|[\s|&;(])claude\s+-|uses:\s*anthropics/claude")


def segreti_pericolosi(righe):
    trovati = set()
    for r in righe:
        for nome in RIF_SEGRETO.findall(r):
            if nome not in AMMESSE and PERICOLOSE.search(nome):
                trovati.add(nome)
    return trovati


def passi_del_file(testo):
    """Spezza il workflow nei suoi passi. Ritorna (passi, righe_fuori_dai_passi).

    Un passo comincia con una riga tipo `      - name: ...` sotto `steps:` e
    finisce quando ne comincia un altro alla stessa colonna (o quando si torna
    più a sinistra). Le righe fuori dai passi sono l'`env:` di tutto il
    workflow o del job: quelle valgono per TUTTI i passi, ed è la trappola più
    facile da non vedere."""
    righe = testo.splitlines()
    passi = []
    fuori = []
    dentro = None
    indent_passo = None
    in_steps = False

    for riga in righe:
        nuda = riga.strip()
        if not nuda or nuda.startswith("#"):
            (dentro["righe"] if dentro is not None else fuori).append(riga)
            continue
        indent = len(riga) - len(riga.lstrip())

        if re.match(r"^\s*steps:\s*$", riga):
            in_steps = True
            indent_passo = None
            if dentro is not None:
                passi.append(dentro)
                dentro = None
            fuori.append(riga)
            continue

        if in_steps and nuda.startswith("- "):
            if indent_passo is None or indent == indent_passo:
                indent_passo = indent
                if dentro is not None:
                    passi.append(dentro)
                dentro = {"prima_riga": nuda, "righe": [riga]}
                continue

        if dentro is not None:
            if indent_passo is not None and indent <= indent_passo and not nuda.startswith("- "):
                # siamo tornati fuori dalla lista dei passi (es. un altro job)
                passi.append(dentro)
                dentro = None
                in_steps = False
                indent_passo = None
                fuori.append(riga)
            else:
                dentro["righe"].append(riga)
        else:
            fuori.append(riga)

    if dentro is not None:
        passi.append(dentro)
    return passi, fuori


def controlla(percorso):
    testo = percorso.read_text()
    passi, fuori = passi_del_file(testo)
    problemi = []

    agentici = [p for p in passi if any(LANCIA_AGENTE.search(r) for r in p["righe"])]
    if not agentici:
        return problemi

    ereditate = segreti_pericolosi(fuori)
    if ereditate:
        problemi.append(
            f"{percorso.name}: le chiavi {', '.join(sorted(ereditate))} sono dichiarate "
            f"fuori dai singoli passi (env del workflow o del job), quindi le vede ANCHE "
            f"il passo che lancia l'agente. Vanno spostate nel solo passo che spedisce."
        )

    for p in agentici:
        proprie = segreti_pericolosi(p["righe"])
        if proprie:
            nome = p["prima_riga"][:70]
            problemi.append(
                f"{percorso.name}: il passo «{nome}» lancia l'agente e ha in mano "
                f"{', '.join(sorted(proprie))}. L'agente legge pagine web di sconosciuti: "
                f"non deve avere chiavi. Sposta l'invio in un passo separato."
            )
    return problemi


def main():
    if not CARTELLA.exists():
        print(f"Nessuna cartella {CARTELLA}: niente da controllare.")
        return 0

    file_yml = sorted(list(CARTELLA.glob("*.yml")) + list(CARTELLA.glob("*.yaml")))
    problemi = []
    for f in file_yml:
        problemi += controlla(f)

    print(f"🔎 Controllati {len(file_yml)} workflow in .github/workflows/")
    if not problemi:
        print("✅ Nessun passo che lancia l'agente ha in mano una chiave "
              "(Telegram, Instagram, Facebook, Canva, PAT).")
        return 0

    print(f"\n🛑 {len(problemi)} problemi — l'agente ha in mano una chiave:\n")
    for p in problemi:
        print(f"  · {p}")
    print("\nRegola (ticket 07): l'agente prepara il messaggio, a spedirlo è un passo "
          "separato che non ragiona. Il token vive solo in quel passo.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
