#!/usr/bin/env python3
"""
telegram_helper.py — un unico posto per mandare un Telegram a Michele.

COS'È (spiegato semplice)
------------------------
Più script del progetto devono mandare una riga a Michele sul telefono (avviso
imminenti, guardia di freschezza, guardia di integrità...). Tutti hanno bisogno
della **stessa** funzione, con la stessa lezione dentro: dal Mac l'invio da
Python fallisce per un problema SSL, quindi si prova prima `requests` e poi si
ripiega su `curl`. Tenerla in un posto solo evita che una copia invecchi.

USO
---
    from telegram_helper import manda_telegram
    manda_telegram("testo del messaggio")

Legge il token e la chat da `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`
(variabili d'ambiente, come in GitHub Actions). Se mancano, non manda e lo dice.
"""
import json
import os
import subprocess
from pathlib import Path


def _credenziali(token=None, chat_id=None):
    """Dove sono token e chat: prima l'ambiente (è così in GitHub Actions), poi —
    solo se l'ambiente non ce l'ha — il file dei segreti del Mac.

    Senza questo ripiego le guardie che girano SUL MAC erano mute: stampavano
    "Telegram non configurato" e nessun avviso partiva. Una guardia muta è
    peggio di nessuna guardia.
    """
    token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        return token, str(chat_id)
    f = Path(__file__).resolve().parents[1] / ".claude" / "secrets" / "telegram.json"
    if f.exists():
        try:
            d = json.loads(f.read_text())
            return token or d.get("bot_token"), str(chat_id or d.get("chat_id"))
        except (json.JSONDecodeError, OSError):
            pass
    return token, chat_id


def manda_telegram(testo: str) -> bool:
    """Invia il messaggio. Prova `requests`, e se fallisce ripiega su `curl`.

    Il doppio tentativo non è pignoleria: su GitHub Actions `requests` funziona
    benissimo (lo usa già publish.py), ma dal Mac di Michele l'invio da Python
    fallisce per un problema SSL — è stata la vera causa dei «messaggi senza
    pulsanti» di luglio. Con il ripiego su curl lo script si può provare anche
    in locale invece che solo al buio in produzione.
    """
    token, chat_id = _credenziali()
    if not token or not chat_id:
        print("(Telegram non configurato: TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID mancanti)")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        import requests
        r = requests.post(url, data={"chat_id": chat_id, "text": testo}, timeout=15)
        if r.ok:
            return True
        print(f"(requests: Telegram ha risposto {r.status_code}, provo con curl)")
    except Exception as e:
        print(f"(requests non ha funzionato: {e} — provo con curl)")

    try:
        esito = subprocess.run(
            ["curl", "-sS", "-X", "POST", url,
             "--data-urlencode", f"chat_id={chat_id}",
             "--data-urlencode", f"text={testo}"],
            capture_output=True, text=True, timeout=30,
        )
        if esito.returncode == 0 and '"ok":true' in esito.stdout:
            return True
        print(f"(anche curl ha fallito: {esito.returncode} {esito.stdout[:200]})")
    except Exception as e:
        print(f"(curl non disponibile: {e})")
    return False


def manda_messaggio(testo: str, tasti=None, parse_mode: str = None,
                    token: str = None, chat_id: str = None) -> bool:
    """Come `manda_telegram`, ma sa mandare anche i PULSANTI (`tasti`).

    `tasti` è l'oggetto `reply_markup` di Telegram (di norma
    `{"inline_keyboard": [[...]]}`). Quando c'è, il messaggio va spedito in
    JSON — non come campi di modulo — quindi qui il corpo è sempre JSON.

    Il token si può passare a mano (`token`/`chat_id`); se non si passa, si
    legge da `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`. È l'unico punto del
    progetto che tocca il token: chi chiama non deve mai vederlo.
    """
    token, chat_id = _credenziali(token, chat_id)
    if not token or not chat_id:
        print("(Telegram non configurato: TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID mancanti)")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    corpo = {"chat_id": chat_id, "text": testo}
    if parse_mode:
        corpo["parse_mode"] = parse_mode
    if tasti:
        corpo["reply_markup"] = tasti
    dati = json.dumps(corpo)

    try:
        import requests
        r = requests.post(url, data=dati.encode("utf-8"),
                          headers={"Content-Type": "application/json"}, timeout=20)
        if r.ok and r.json().get("ok"):
            return True
        print(f"(requests: Telegram ha risposto {r.status_code} {r.text[:200]} — provo con curl)")
    except Exception as e:
        print(f"(requests non ha funzionato: {e} — provo con curl)")

    try:
        esito = subprocess.run(
            ["curl", "-sS", "--max-time", "20", "-X", "POST", url,
             "-H", "Content-Type: application/json", "-d", dati],
            capture_output=True, text=True, timeout=30,
        )
        if esito.returncode == 0 and '"ok":true' in esito.stdout:
            return True
        print(f"(anche curl ha fallito: {esito.returncode} {esito.stdout[:200]}{esito.stderr[:200]})")
    except Exception as e:
        print(f"(curl non disponibile: {e})")
    return False
