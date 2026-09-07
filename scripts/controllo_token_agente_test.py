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
    veri = g.CARTELLA
    tutti = []
    for f in sorted(list(veri.glob("*.yml")) + list(veri.glob("*.yaml"))):
        tutti += g.controlla(f)
    verifica(f"{len(list(veri.glob('*.yml')))} workflow, 0 problemi", tutti == [])

    print(f"\n{'='*60}\n✅ {OK} verifiche passate   ❌ {KO} fallite\n{'='*60}")
    return 1 if KO else 0


if __name__ == "__main__":
    sys.exit(main())
