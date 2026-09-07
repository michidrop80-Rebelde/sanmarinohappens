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
import os
import subprocess


def manda_telegram(testo: str) -> bool:
    """Invia il messaggio. Prova `requests`, e se fallisce ripiega su `curl`.

    Il doppio tentativo non è pignoleria: su GitHub Actions `requests` funziona
    benissimo (lo usa già publish.py), ma dal Mac di Michele l'invio da Python
    fallisce per un problema SSL — è stata la vera causa dei «messaggi senza
    pulsanti» di luglio. Con il ripiego su curl lo script si può provare anche
    in locale invece che solo al buio in produzione.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
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
