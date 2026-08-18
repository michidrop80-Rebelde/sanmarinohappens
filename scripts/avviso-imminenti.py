#!/usr/bin/env python3
"""
Avviso imminenti — San Marino Happens

A cosa serve
------------
Rende **rumorosa l'assenza della catena**. Gira su GitHub Actions la sera, dopo
l'orario in cui la catena delle 18:30 avrebbe dovuto lavorare, e si limita a
chiedere: «è rimasto un buco che qualcuno avrebbe dovuto chiudere?». Se sì,
manda un Telegram a Michele.

Perché esiste
-------------
La catena serale gira **solo mentre l'app Claude è aperta sul Mac**. Se il Mac è
spento, non parte — e non lo dice a nessuno. La pubblicazione invece è già
immune (GitHub Actions + cron-job.org pubblicano col Mac spento): l'unica parte
fragile è la preparazione.

Questo script non sposta la catena e non prova a fare il suo lavoro. Trasforma
solo un **fallimento silenzioso** in uno rumoroso, che è la differenza fra
accorgersene la sera stessa e scoprirlo giovedì. Gira dove gira già il robot di
pubblicazione, quindi non costa niente di nuovo e non aggiunge segreti: usa gli
stessi `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` già presenti nel repo.

Quando suona (e quando tace)
----------------------------
Chiama `controllo-imminenti.py` e si regola sul suo codice di uscita:

    0  -> **tace**. O le 48 ore sono coperte, o i buchi che restano sono giorni
          legittimamente vuoti. Un avviso ogni sera insegnerebbe a ignorarlo.
    1  -> ⚠️  ci sono buchi che aspettano un ✅ di Michele: li mostra.
    2  -> 🔴 c'era da lavorare e nessuno ha lavorato: o la catena non è partita
          (Mac spento) o è partita e ha fallito.

Uso
---
    python3 scripts/avviso-imminenti.py            # manda davvero
    python3 scripts/avviso-imminenti.py --prova    # stampa e basta, non manda
"""

import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
GUARDIA = REPO / "scripts" / "controllo-imminenti.py"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LIMITE_TELEGRAM = 3500  # il limite vero è 4096: si tiene margine per l'intestazione


def manda_telegram(testo):
    """Invia il messaggio. Prova `requests`, e se fallisce ripiega su `curl`.

    Il doppio tentativo non è pignoleria: su GitHub Actions `requests` funziona
    benissimo (lo usa già publish.py), ma **dal Mac di Michele l'invio da Python
    fallisce per un problema SSL** — è stata la vera causa dei «messaggi senza
    pulsanti» di luglio. Con il ripiego su curl questo script si può provare
    anche in locale invece che solo al buio in produzione.
    """
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


def _corpo_per_michele(referto):
    """Toglie dal referto il blocco finale di istruzioni.

    La guardia parla all'**agente** che deve chiudere i buchi, e chiude con righe
    tipo «Non si consegna questo elenco a Michele». Qui il lettore è Michele: quelle
    righe, arrivate sul suo telefono, sarebbero al meglio confuse. Si tiene la parte
    che descrive i FATTI e si taglia quella che dà ordini a qualcun altro.
    """
    righe = []
    for r in referto.splitlines():
        spoglia = r.strip()
        if spoglia.startswith("➡️") or (spoglia.startswith("⚠️") and " buchi" in spoglia):
            break
        if spoglia.startswith("Guardia degli imminenti"):
            continue  # l'intestazione ce l'ha già il messaggio
        righe.append(r)
    return "\n".join(righe).strip()


def main():
    prova = "--prova" in sys.argv

    esito = subprocess.run(
        [sys.executable, str(GUARDIA)],
        cwd=REPO, capture_output=True, text=True,
    )
    referto = (esito.stdout or "").strip()
    codice = esito.returncode

    print(referto)
    if esito.stderr.strip():
        print("--- errori ---")
        print(esito.stderr.strip())

    # La guardia stessa può rompersi. Se succede, il silenzio sarebbe la cosa
    # peggiore: un controllo che non riesce a leggere l'input deve GRIDARE, non
    # far finta che vada tutto bene (lezione dell'08/08 sui doppioni).
    if codice not in (0, 1, 2):
        testo = (f"🔴 SMH — la guardia degli imminenti è ANDATA IN ERRORE (codice {codice}).\n\n"
                 f"Non so dirti se le prossime 48 ore sono coperte: il controllo non è "
                 f"arrivato in fondo. Va guardato a mano.\n\n"
                 f"{(esito.stderr or referto)[:1200]}")
        manda_telegram(testo) if not prova else print("\n[PROVA] avrei mandato:\n" + testo)
        return 1

    if codice == 0:
        print("\n→ Niente da segnalare: nessun Telegram. (È il comportamento giusto: un "
              "avviso ogni sera insegnerebbe a ignorarlo.)")
        return 0

    if codice == 2:
        intestazione = (
            "🔴 SMH — c'era da lavorare e nessuno ha lavorato.\n\n"
            "Alle 18:30 la catena avrebbe dovuto chiudere questi buchi. Non l'ha fatto: "
            "o non è partita (app Claude chiusa sul Mac) o è partita ed è fallita.\n"
            "La pubblicazione NON è a rischio di suo — il robot pubblica lo stesso ciò che "
            "è già in coda. Il rischio è che a queste date non esca niente.\n\n"
        )
    else:
        intestazione = (
            "⚠️ SMH — servono i tuoi ✅ per coprire le prossime 48 ore.\n\n"
            "Ci sono eventi veri, ma non sono approvati a registro: senza i pulsanti "
            "non possono diventare un post.\n\n"
        )

    corpo = _corpo_per_michele(referto)[:LIMITE_TELEGRAM]
    if len(_corpo_per_michele(referto)) > LIMITE_TELEGRAM:
        corpo += "\n\n[…referto troncato: il resto sul Mac]"

    if codice == 2:
        chiusura = ("\n\n👉 Se il Mac era spento: apri Claude e lancia /smh-catena — "
                    "chiude i buchi da sola, non devi fare altro.\n"
                    "Se invece il giro è partito, allora è fallito a metà: quello va guardato.")
    else:
        chiusura = "\n\n👉 Ti bastano i pulsanti ✅/❌ qui su Telegram."

    testo = intestazione + corpo + chiusura

    if prova:
        print("\n[PROVA] avrei mandato questo messaggio:\n")
        print(testo)
        return 0

    if manda_telegram(testo):
        print("\n→ Avviso mandato su Telegram.")
        return 0

    print("\n→ ⚠️ NON sono riuscito a mandare l'avviso: guarda il referto qui sopra.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
