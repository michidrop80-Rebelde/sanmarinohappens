#!/usr/bin/env python3
"""
TEST della guardia `controllo-token-agente.py` — non tocca i workflow veri.
Si lancia con:  python3 scripts/controllo_token_agente_test.py

Una guardia che dice sempre ✅ è peggio di nessuna guardia: qui si prova che
sa anche dire ❌, e che non grida su casi innocui.
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

QUI = Path(__file__).parent
spec = importlib.util.spec_from_file_location("guardia", QUI / "controllo-token-agente.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

OK = 0
KO = 0


def verifica(descrizione, condizione):
    global OK, KO
    if condizione:
        OK += 1
        print(f"  ✅ {descrizione}")
    else:
        KO += 1
        print(f"  ❌ {descrizione}")


BUONO = """
name: Giro in cloud
on: workflow_dispatch
jobs:
  giro:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Installa Claude Code
        run: npm install -g @anthropic-ai/claude-code
      - name: L'agente prepara la busta
        env:
          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: |
          claude -p "prepara il giro" --max-turns 20
      - name: Spedisci (l'unico passo con la chiave)
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python3 .claude/scripts/telegram-giro.py invia
"""

CATTIVO_PASSO = BUONO.replace(
    """        env:
          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}""",
    """        env:
          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}""")

CATTIVO_JOB = """
name: Giro in cloud
on: workflow_dispatch
env:
  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
jobs:
  giro:
    runs-on: ubuntu-latest
    steps:
      - name: L'agente lavora
        env:
          CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
        run: claude -p "fai il giro"
"""

SENZA_AGENTE = """
name: Pubblica
on: workflow_dispatch
jobs:
  pubblica:
    runs-on: ubuntu-latest
    steps:
      - name: Pubblica su IG
        env:
          INSTAGRAM_TOKEN: ${{ secrets.INSTAGRAM_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        run: python3 scripts/publish.py
"""


# La chiave NON arriva da `secrets.` ma da un input di un'azione composita:
# il valore cambia strada, il nome della variabile no. Prima passava liscia.
CATTIVO_INPUT = """
name: Finto
on: workflow_dispatch
jobs:
  x:
    runs-on: ubuntu-latest
    steps:
      - name: L'agente con la chiave passata di nascosto
        env:
          CLAUDE_CODE_OAUTH_TOKEN: ${{ inputs.claude }}
          TELEGRAM_BOT_TOKEN: ${{ inputs.tg }}
        run: claude -p "ciao"
"""

# Un'azione composita: stessa forma di un workflow, ma vive in
# .github/actions/<nome>/action.yml. Deve essere controllata uguale.
AZIONE_COMPOSITA = """
name: Tappa
inputs:
  telegram-token:
    description: nome minuscolo, e' solo una dichiarazione, non una env
    required: false
runs:
  using: composite
  steps:
    - name: L'agente dentro l'azione composita
      env:
        TELEGRAM_BOT_TOKEN: ${{ inputs.telegram-token }}
      shell: bash
      run: claude -p "ciao"
"""


def problemi(contenuto):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "prova.yml"
        f.write_text(contenuto)
        return g.controlla(f)


def main():
    print("\n[1] Il caso giusto passa (l'agente ha solo il token dell'abbonamento)")
    verifica("nessun problema", problemi(BUONO) == [])

    print("\n[2] La chiave nel passo dell'agente viene BECCATA")
    p = problemi(CATTIVO_PASSO)
    verifica("almeno un problema", len(p) >= 1)
    verifica("dice quale chiave", any("TELEGRAM_BOT_TOKEN" in x for x in p))

    print("\n[3] La trappola vera: chiave dichiarata per TUTTO il workflow")
    p = problemi(CATTIVO_JOB)
    verifica("beccata anche se non è dentro il passo", len(p) >= 1)
    verifica("spiega che la vede anche l'agente", any("fuori dai singoli passi" in x for x in p))

    print("\n[4] Un workflow SENZA agente può avere tutte le chiavi che vuole")
    verifica("nessun falso allarme", problemi(SENZA_AGENTE) == [])

    print("\n[5] I workflow VERI del repo passano")
    veri = g.file_da_controllare()
    tutti = []
    for f in veri:
        tutti += g.controlla(f)
    verifica(f"{len(veri)} file (workflow + azioni), 0 problemi", tutti == [])

    print("\n[6] La chiave passata da `inputs.` invece che da `secrets.`")
    p = problemi(CATTIVO_INPUT)
    verifica("beccata lo stesso (conta il NOME della variabile)", len(p) >= 1)
    verifica("dice quale chiave", any("TELEGRAM_BOT_TOKEN" in x for x in p))

    print("\n[7] Un'azione composita non è un nascondiglio")
    p = problemi(AZIONE_COMPOSITA)
    verifica("l'agente dentro l'azione composita viene beccato", len(p) >= 1)
    verifica("la dichiarazione `inputs:` minuscola non fa falsi allarmi",
             not any("fuori dai singoli passi" in x for x in p))
    verifica("la cartella .github/actions/ è fra i posti guardati",
             ".github/actions" in str(g.CARTELLA_AZIONI))

    print(f"\n{'='*60}\n✅ {OK} verifiche passate   ❌ {KO} fallite\n{'='*60}")
    return 1 if KO else 0


if __name__ == "__main__":
    sys.exit(main())
