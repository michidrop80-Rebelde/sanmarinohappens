#!/usr/bin/env python3
"""
lucchetto.py — un solo giro alla volta.
=======================================

COS'E' (spiegato semplice)
--------------------------
I task pianificati di Claude Code girano solo quando l'app e' aperta. Se l'app resta
chiusa oltre l'orario di un task, alla riapertura i task arretrati partono TUTTI INSIEME.
E' successo davvero due volte: il 04/08/2026 e l'11/08/2026, quando
smh-check-approvazioni e smh-grafica-pubblica hanno lastRunAt identico al secondo
(15:39:41). Due giri in parallelo sugli stessi file significa leggere la stessa coda
due volte, graficare lo stesso evento due volte e committare l'uno sopra l'altro.

Questo file e' il semaforo: chi arriva primo lavora, chi arriva dopo lo scopre e si ferma.

PERCHE' O_CREAT|O_EXCL E NON "leggo, controllo, scrivo"
-------------------------------------------------------
"Guardo se il file c'e', se non c'e' lo creo" e' proprio la corsa che vogliamo evitare:
fra il guardare e il creare ci sta l'altro giro. O_EXCL chiede al sistema operativo di
creare il file SOLO se non esiste, in un'operazione sola e indivisibile.

QUANDO UN LUCCHETTO SI SCAVALCA
-------------------------------
Un giro puo' morire a meta' (sessione chiusa, app terminata) e lasciare il lucchetto
chiuso per sempre. Si scavalca quando: e' piu' vecchio del TTL, oppure il file e'
illeggibile. In entrambi i casi il fatto finisce nel referto: non deve succedere in
silenzio.

⚠️ PERCHE' IL PID NON DECIDE NIENTE (buco trovato l'11/08/2026, prima di andare in
produzione). La prima stesura scavalcava anche il lucchetto il cui processo non
esisteva piu'. Ma il lucchetto si prende da riga di comando, e QUEL processo python
muore un istante dopo aver scritto il file: al controllo successivo il pid e' sempre
morto, quindi il semaforo sarebbe stato sempre verde. Provato dal vivo: il secondo
giro scavalcava il primo ogni volta. Il pid resta scritto perche' e' utile leggerlo
nel referto, ma a liberare un lucchetto dimenticato pensa solo il TTL.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Stato di macchina, non contenuto: sta fuori da git (vedi .gitignore).
# La variabile d'ambiente SMH_LUCCHETTO esiste per i test: permette di far girare la
# riga di comando vera su un file usa-e-getta, senza toccare il lucchetto di questo Mac.
PERCORSO = Path(os.environ.get("SMH_LUCCHETTO") or
                (Path(__file__).resolve().parent.parent / ".claude" / "stato" / "lucchetto.json"))

# Quanto puo' durare al massimo un giro. Oltre, si assume che sia morto per strada.
# Tre ore stanno larghe sul giro piu' lungo (grafica Canva) e sono molto meno delle
# dieci ore che separano le due sveglie della catena.
TTL_ORE = 3


def _adesso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stato():
    """Cosa dice il lucchetto adesso, o None se e' libero o illeggibile."""
    try:
        return json.loads(PERCORSO.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _scavalcabile(dati, ttl_ore):
    """(sì/no, motivo) — perche' un lucchetto esistente si puo' prendere lo stesso."""
    if dati is None:
        return True, "lucchetto illeggibile (file rovinato): lo sostituisco"
    try:
        preso = datetime.strptime(dati["preso_il"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except (KeyError, ValueError, TypeError):
        return True, "lucchetto senza data valida: lo sostituisco"
    ore = (datetime.now(timezone.utc) - preso).total_seconds() / 3600
    if ore >= ttl_ore:
        return True, (f"lucchetto scaduto: «{dati.get('titolare')}» lo teneva da "
                      f"{ore:.1f} ore (limite {ttl_ore}), lo sostituisco")
    return False, (f"occupato da «{dati.get('titolare')}» dalle {dati.get('preso_il')} "
                   f"({ore:.1f} ore fa)")


def prendi(nome, ttl_ore=TTL_ORE):
    """Prova a prendere il lucchetto. Ritorna (preso?, motivo leggibile)."""
    PERCORSO.parent.mkdir(parents=True, exist_ok=True)
    contenuto = json.dumps({
        "titolare": nome,
        "pid": os.getpid(),
        "preso_il": _adesso(),
    }, ensure_ascii=False)

    try:
        fd = os.open(str(PERCORSO), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        scavalca, motivo = _scavalcabile(stato(), ttl_ore)
        if not scavalca:
            return False, motivo
        # Si sostituisce con una scrittura atomica: file temporaneo + rename.
        temporaneo = PERCORSO.with_suffix(".tmp")
        temporaneo.write_text(contenuto)
        temporaneo.replace(PERCORSO)
        return True, motivo
    with os.fdopen(fd, "w") as f:
        f.write(contenuto)
    return True, "libero"


def rilascia(nome):
    """Rilascia il lucchetto SOLO se e' nostro. True se rilasciato."""
    dati = stato()
    if dati is not None and dati.get("titolare") != nome:
        return False
    try:
        PERCORSO.unlink()
        return True
    except FileNotFoundError:
        return True
    except OSError:
        return False


def main():
    if len(sys.argv) < 2:
        print("uso: lucchetto.py prendi|rilascia|stato [nome]", file=sys.stderr)
        return 2
    azione = sys.argv[1]
    nome = sys.argv[2] if len(sys.argv) > 2 else "smh"

    if azione == "stato":
        dati = stato()
        if dati is None:
            print("🔓 libero")
            return 0
        print(f"🔒 occupato da «{dati.get('titolare')}» dalle {dati.get('preso_il')} "
              f"(pid {dati.get('pid')})")
        return 1
    if azione == "prendi":
        preso, motivo = prendi(nome)
        print(("🔒 preso — " if preso else "⛔ NON preso — ") + motivo)
        return 0 if preso else 1
    if azione == "rilascia":
        print("🔓 rilasciato" if rilascia(nome) else "⚠️ non era mio: lasciato dov'era")
        return 0

    print(f"azione sconosciuta: {azione}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
