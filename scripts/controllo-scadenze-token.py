#!/usr/bin/env python3
"""
Guardia scadenze token — San Marino Happens

A cosa serve
------------
Alcuni token da cui dipende la catena **scadono** — e non tutti avvisano prima.
Il caso che ha aperto questo ticket: `CLAUDE_CODE_OAUTH_TOKEN` (l'abbonamento che
fa girare Claude nei workflow in cloud) **dura un anno e non manda nessun avviso
alla CI**. Quando scade, le run falliscono con «Invalid auth token» e la catena
smette di girare — e siccome Michele non guarda le run, se ne accorgerebbe solo
dai post che non escono, cioe' troppo tardi.

Questa guardia legge `dati/scadenze-token.json`, calcola quanti giorni mancano a
ogni scadenza (in Python, mai a occhio) e, quando si scende sotto la soglia
`anticipo_giorni` del token, manda **un** Telegram che dice cosa scade, quando, e
come rigenerarlo.

E' la stessa forma del promemoria del token Instagram in `scripts/metrics.py`
(`controlla_token`): stesso canale, stesso stile, stessa idea.

Dove gira
---------
Un passo del workflow `Metriche settimanali` (`.github/workflows/metrics.yml`),
che parte ogni lunedi'. Con `anticipo_giorni: 21` l'avviso arriva ~3 lunedi' di
fila prima della scadenza: impossibile non vederlo.

Uso
---
    python3 scripts/controllo-scadenze-token.py
    python3 scripts/controllo-scadenze-token.py --prova            # non manda, stampa e basta
    python3 scripts/controllo-scadenze-token.py --oggi 2027-08-20  # forza la data (per i test)

Codici di uscita
----------------
    0  nessun token vicino alla scadenza
    1  almeno un token e' entro la soglia (o gia' scaduto) -> Telegram mandato
    2  `dati/scadenze-token.json` manca o e' illeggibile
"""

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SCADENZE = REPO / "dati" / "scadenze-token.json"


def _credenziali_telegram():
    """env var (GitHub Actions) -> altrimenti .claude/secrets/telegram.json (Mac)."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        return token, chat_id
    segreti = REPO / ".claude" / "secrets" / "telegram.json"
    try:
        dati = json.loads(segreti.read_text(encoding="utf-8"))
        cid = dati.get("chat_id")
        return dati.get("bot_token"), str(cid) if cid else None
    except Exception:
        return token, chat_id


TOKEN, CHAT_ID = _credenziali_telegram()


def manda_telegram(testo):
    """Prova `requests`, ripiega su `curl` (SSL rotto da Python sul Mac di Michele)."""
    if not TOKEN or not CHAT_ID:
        print("(Telegram non configurato: TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID mancanti)")
        return False
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        import requests
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": testo}, timeout=15)
        if r.ok:
            return True
        print(f"(requests: Telegram ha risposto {r.status_code}, provo con curl)")
    except Exception as e:
        print(f"(requests non ha funzionato: {e} — provo con curl)")
    try:
        esito = subprocess.run(
            ["curl", "-sS", "-X", "POST", url,
             "--data-urlencode", f"chat_id={CHAT_ID}",
             "--data-urlencode", f"text={testo}"],
            capture_output=True, text=True, timeout=30,
        )
        if esito.returncode == 0 and '"ok":true' in esito.stdout:
            return True
        print(f"(anche curl ha fallito: {esito.returncode} {esito.stdout[:200]})")
    except Exception as e:
        print(f"(curl non disponibile: {e})")
    return False


def main():
    ap = argparse.ArgumentParser(description="Guardia scadenze token")
    ap.add_argument("--prova", action="store_true",
                    help="non manda il Telegram: stampa e basta")
    ap.add_argument("--oggi", metavar="AAAA-MM-GG",
                    help="forza la data di riferimento (per i test); default: oggi")
    args = ap.parse_args()

    oggi = (datetime.datetime.strptime(args.oggi, "%Y-%m-%d").date()
            if args.oggi else datetime.date.today())

    try:
        elenco = json.loads(SCADENZE.read_text(encoding="utf-8")).get("token", [])
    except Exception as e:
        print(f"❌ {SCADENZE.relative_to(REPO)} non leggibile: {e}")
        return 2

    if not elenco:
        print(f"(nessun token elencato in {SCADENZE.relative_to(REPO)})")
        return 0

    avvisi = []
    for t in elenco:
        try:
            scade = datetime.date.fromisoformat(t["scade"])
        except (KeyError, ValueError):
            print(f"(salto una voce senza data valida: {t.get('nome', '???')})")
            continue
        giorni = (scade - oggi).days
        soglia = int(t.get("anticipo_giorni", 21))
        stato_ok = f"{t['nome']}: scade il {scade.isoformat()} (fra {giorni} giorni) — a posto."
        if giorni > soglia:
            print(f"✅ {stato_ok}")
            continue
        if giorni < 0:
            testa = f"🔴 Token GIÀ SCADUTO: {t['nome']} è scaduto il {scade.isoformat()} ({-giorni} giorni fa)."
        else:
            testa = f"⚠️ Token in scadenza: {t['nome']} scade il {scade.isoformat()} (fra {giorni} giorni)."
        corpo = (f"{testa}\n\nSe scade: {t.get('se_scade', 'non specificato')}.\n"
                 f"Rigenera: {t.get('rigenera_con', 'non specificato')}.\n"
                 f"Dove: {t.get('dove', 'non specificato')}.")
        avvisi.append(corpo)
        print(f"  -> avviso per {t['nome']} ({giorni} giorni)")

    if not avvisi:
        return 0

    messaggio = "\n\n———\n\n".join(avvisi)
    print("\n" + messaggio + "\n")
    if args.prova:
        print("[PROVA] non mando il Telegram.")
    else:
        print("Mandato:", manda_telegram(messaggio))
    return 1


if __name__ == "__main__":
    sys.exit(main())
