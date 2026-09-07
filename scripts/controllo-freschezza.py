#!/usr/bin/env python3
"""
Guardia di freschezza — San Marino Happens

A cosa serve
------------
Prima che un anello della catena parta, guarda la **data del file** che sta per
lavorare e si chiede: e' abbastanza recente? Se no, **ferma l'anello** e manda un
Telegram di una riga. Nessuna bozza viene prodotta: meglio un giro saltato che
un post sbagliato in coda.

Perche' esiste
--------------
`smh-verifica` prende «il file piu' recente» in `dati/eventi/` e `smh-testi` «il
piu' recente» in `dati/eventi/verificati/` — senza chiedersi *quanto* e' recente.
Sul Mac, con Michele che lancia il giro a mano, il file e' sempre di oggi. In
cloud, di notte, a orario fisso, se una notte la ricerca non gira, il giorno dopo
la verifica troverebbe il file di ieri (o di una settimana fa) e ci lavorerebbe
sopra come se niente fosse: bozze su eventi gia' passati, in silenzio.

E' la sorella di `avviso-imminenti.py`: trasforma un fallimento silenzioso in
uno rumoroso.

La regola (decisa nel ticket 01 della mappa «catena-in-cloud», qui si applica soltanto)
--------------------------------------------------------------------------------------
    file di EVENTI      -> deve essere DELLO STESSO GIORNO del giro
    file VERIFICATO     -> al massimo 2 GIORNI

⚠️ La data si legge dal **nome del file** (`eventi-AAAA-MM-GG.md`), MAI dalla data
di modifica sul disco: un `git clone` in cloud riscrive l'mtime di tutti i file al
momento del clone, quindi in cloud «l'ultima modifica» direbbe sempre «oggi» e la
guardia non scatterebbe **mai**.

⚠️ Il giorno di oggi e la differenza in giorni si calcolano sempre in Python, mai
dedotti (regola di progetto).

Uso
---
    python3 scripts/controllo-freschezza.py verifica   # controlla dati/eventi/
    python3 scripts/controllo-freschezza.py testi      # controlla dati/eventi/verificati/
    python3 scripts/controllo-freschezza.py verifica --prova           # non manda il Telegram, stampa e basta
    python3 scripts/controllo-freschezza.py verifica --oggi 2026-09-10 # forza la data di riferimento (per i test)

Codici di uscita
----------------
    0  il file e' abbastanza fresco   -> l'anello PUO' partire
    1  il file e' troppo vecchio      -> l'anello NON parte (Telegram mandato)
    2  non c'e' nessun file da lavorare -> l'anello NON parte (Telegram mandato)
"""

import argparse
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

def _credenziali_telegram():
    """Token e chat_id, da dove capita di girare.

    - In **GitHub Actions**: le env var `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`
      (i segreti del repo), come fa `publish.py` / `avviso-imminenti.py`.
    - Sul **Mac**, lanciata a mano: `.claude/secrets/telegram.json`
      (chiavi `bot_token` / `chat_id`), come fa `.claude/scripts/telegram-giro.py`.
      Quel file è in `.gitignore` e non arriva mai in cloud.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        return token, chat_id
    segreti = REPO / ".claude" / "secrets" / "telegram.json"
    try:
        dati = json.loads(segreti.read_text(encoding="utf-8"))
        return dati.get("bot_token"), str(dati.get("chat_id")) if dati.get("chat_id") else None
    except Exception:
        return token, chat_id


TOKEN, CHAT_ID = _credenziali_telegram()

MESI = [
    "", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
]

# Un anello -> (chiave di config per la cartella, default, regex sul nome file,
#               giorni massimi di eta', nome leggibile).
ANELLI = {
    "verifica": {
        "chiave": "cartella_eventi",
        "default": "dati/eventi/",
        "regex": re.compile(r"^eventi-(\d{4})-(\d{2})-(\d{2})\.md$"),
        "max_giorni": 0,
        "nome": "verifica",
        "esempio": "eventi-AAAA-MM-GG.md",
    },
    "testi": {
        "chiave": "cartella_verificati",
        "default": "dati/eventi/verificati/",
        "regex": re.compile(r"^eventi-verificati-(\d{4})-(\d{2})-(\d{2})\.md$"),
        "max_giorni": 2,
        "nome": "scrittura testi",
        "esempio": "eventi-verificati-AAAA-MM-GG.md",
    },
}


def manda_telegram(testo):
    """Invia il messaggio. Prova `requests`, e se fallisce ripiega su `curl`.

    Stesso doppio tentativo di `avviso-imminenti.py`: su GitHub Actions `requests`
    funziona, ma dal Mac di Michele l'invio da Python fallisce per un problema SSL
    e serve il ripiego su `curl`. Usa gli stessi `TELEGRAM_BOT_TOKEN` /
    `TELEGRAM_CHAT_ID` gia' presenti nei segreti del repo — non aggiunge segreti.
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


def data_italiana(d):
    return f"{d.day} {MESI[d.month]} {d.year}"


def giorni_fa(n):
    if n == 0:
        return "oggi"
    if n == 1:
        return "1 giorno fa"
    return f"{n} giorni fa"


def cartella_anello(spec):
    """Legge la cartella da dati/config.json, con fallback al default dell'anello."""
    cfg_path = REPO / "dati" / "config.json"
    rel = spec["default"]
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        rel = cfg.get("percorsi", {}).get(spec["chiave"], spec["default"])
    except Exception as e:
        print(f"(config.json non letto: {e} — uso il default {spec['default']})")
    return REPO / rel


def file_piu_recente(cartella, regex):
    """Il file col nome-data piu' avanti. Ordina per DATA NEL NOME, non per mtime."""
    trovati = []
    if cartella.is_dir():
        for p in cartella.iterdir():
            m = regex.match(p.name)
            if m:
                anno, mese, giorno = (int(x) for x in m.groups())
                try:
                    trovati.append((datetime.date(anno, mese, giorno), p))
                except ValueError:
                    continue  # nome con una data impossibile: lo ignoro
    if not trovati:
        return None, None
    trovati.sort(key=lambda t: t[0])
    return trovati[-1]  # (data, path)


def main():
    ap = argparse.ArgumentParser(description="Guardia di freschezza della catena")
    ap.add_argument("anello", choices=sorted(ANELLI), help="quale anello sta per partire")
    ap.add_argument("--prova", action="store_true",
                    help="non manda il Telegram: stampa il messaggio e basta")
    ap.add_argument("--oggi", metavar="AAAA-MM-GG",
                    help="forza la data di riferimento (per i test); default: oggi")
    args = ap.parse_args()

    spec = ANELLI[args.anello]

    if args.oggi:
        oggi = datetime.datetime.strptime(args.oggi, "%Y-%m-%d").date()
    else:
        oggi = datetime.date.today()

    cartella = cartella_anello(spec)
    data_file, path = file_piu_recente(cartella, spec["regex"])

    # --- caso 2: nessun file ------------------------------------------------
    if data_file is None:
        rel = cartella.relative_to(REPO) if cartella.is_relative_to(REPO) else cartella
        msg = (f"🕰️ Freschezza — la {spec['nome']} non parte: in {rel}/ non c'è "
               f"nessun file {spec['esempio']} su cui lavorare. Nessuna bozza prodotta.")
        print(msg)
        if args.prova:
            print("[PROVA] non mando il Telegram.")
        else:
            print("Mandato:", manda_telegram(msg))
        return 2

    eta = (oggi - data_file).days
    nomefile = path.name

    # --- caso 0: file abbastanza fresco -----------------------------------
    if eta <= spec["max_giorni"]:
        print(f"✅ Freschezza OK — {nomefile} è del {data_italiana(data_file)} "
              f"({giorni_fa(eta) if eta >= 0 else 'data futura'}), "
              f"entro il limite di {spec['max_giorni']} giorni. La {spec['nome']} può partire.")
        return 0

    # --- caso 1: file troppo vecchio -------------------------------------
    limite_txt = ("serve un file di oggi" if spec["max_giorni"] == 0
                  else f"il limite è {spec['max_giorni']} giorni")
    msg = (f"🕰️ Freschezza — la {spec['nome']} NON parte: l'ultimo file è "
           f"{nomefile} ({data_italiana(data_file)}, {giorni_fa(eta)}), troppo "
           f"vecchio ({limite_txt}). Nessuna bozza prodotta: la catena si ferma qui.")
    print(msg)
    if args.prova:
        print("[PROVA] non mando il Telegram.")
    else:
        print("Mandato:", manda_telegram(msg))
    return 1


if __name__ == "__main__":
    sys.exit(main())
