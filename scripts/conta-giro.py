#!/usr/bin/env python3
"""Conta cosa ha prodotto un giro della catena, leggendo i file veri.

PERCHE' ESISTE (ticket 08 della mappa "La catena si stacca dal Mac")
Il giro in cloud e quello sul Mac vanno confrontati. Se i numeri li dicesse
l'agente, staremmo confrontando due racconti, non due lavori: un agente che
sbaglia il conto lo sbaglia anche nel riassunto. Qui i numeri si MISURANO dai
file prodotti — nessun agente in mezzo.

COSA CONTA (per una data, di solito oggi):
  - ricerca   -> dati/eventi/eventi-AAAA-MM-GG.md            : quanti eventi
  - verifica  -> dati/eventi/verificati/eventi-verificati-... : verificati /
                 da-confermare / scartati
  - testi     -> dati/post/post-AAAA-MM-GG.md                : bozze per stato

COME SI LANCIA
  python3 scripts/conta-giro.py                 # oggi, in italiano
  python3 scripts/conta-giro.py --data 2026-09-14
  python3 scripts/conta-giro.py --json          # per gli script e i workflow
  python3 scripts/conta-giro.py --radice /altra/copia/del/repo

USCITA: sempre 0. Questo non e' una guardia, e' un metro: un file che manca
e' un'informazione (contato come "assente"), non un errore.
"""

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path


def radice_repo() -> Path:
    """La radice del repo, da ovunque venga lanciato lo script."""
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:
        return Path(__file__).resolve().parent.parent


# I titoli degli eventi sono "## Titolo". Le sezioni del file verificato sono
# anch'esse "## " ma cominciano con un'emoji: vanno riconosciute e non contate
# come eventi.
SEZIONI_VERIFICATO = {
    "verificati": re.compile(r"^##\s*✅"),
    "da_confermare": re.compile(r"^##\s*⚠️\s*Da confermare"),
    "scartati": re.compile(r"^##\s*🗑\s*Scartati"),
}
RIGA_TITOLO = re.compile(r"^##\s+(.*\S)\s*$")
# Un titolo che comincia con una di queste emoji e' un marcatore di stato messo
# davanti al nome dell'evento (es. "## ⚠️ Artisti in Casa"): l'evento va contato.
EMOJI_STATO = "✅⚠️🗑🆕✏️🔁"


def _righe(p: Path):
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else None


# ⚠️ I TITOLI si estraggono qui, in un posto solo. `scripts/confronta-giri.py`
# li riusa importando questo file: se ognuno si scrivesse il suo lettore, prima
# o poi conterebbero cose diverse e il confronto mentirebbe senza dirlo.

def titoli_eventi(p: Path):
    """File della ricerca: ogni '## Titolo' e' un evento. None se il file manca."""
    righe = _righe(p)
    if righe is None:
        return None
    fuori = []
    for r in righe:
        m = RIGA_TITOLO.match(r)
        if m and not m.group(1).startswith(("Fonti", "Note", "Riepilogo")):
            fuori.append(m.group(1))
    return fuori


def titoli_verificati(p: Path):
    """File dei verificati: i titoli, divisi per sezione. None se il file manca."""
    righe = _righe(p)
    if righe is None:
        return None
    esito = {"verificati": [], "da_confermare": [], "scartati": []}
    sezione = None
    for r in righe:
        cambiata = False
        for nome, rx in SEZIONI_VERIFICATO.items():
            # Un'intestazione di sezione ha SOLO l'emoji + il nome della sezione.
            if rx.match(r) and ("Verificati" in r or "Da confermare" in r or "Scartati" in r):
                sezione, cambiata = nome, True
                break
        if cambiata:
            continue
        m = RIGA_TITOLO.match(r)
        if sezione and m:
            # Il marcatore di stato davanti al nome ("⚠️ Artisti in Casa") non
            # fa parte del titolo: toglierlo permette di confrontare i due giri.
            esito[sezione].append(m.group(1).lstrip(EMOJI_STATO + " "))
    return esito


def conta_eventi(p: Path):
    t = titoli_eventi(p)
    return None if t is None else len(t)


def conta_verificati(p: Path):
    t = titoli_verificati(p)
    return None if t is None else {k: len(v) for k, v in t.items()}


RIGA_STATO = re.compile(r"^\*\*Stato bozza:\*\*\s*([a-z-]+)")


def conta_bozze(p: Path):
    """File delle bozze: si contano gli stati, non i titoli."""
    righe = _righe(p)
    if righe is None:
        return None
    stati = {}
    for r in righe:
        m = RIGA_STATO.match(r)
        if m:
            stati[m.group(1)] = stati.get(m.group(1), 0) + 1
    return {"totale": sum(stati.values()), "per_stato": stati}


def misura(radice: Path, data: str) -> dict:
    f_eventi = radice / "dati" / "eventi" / f"eventi-{data}.md"
    f_verif = radice / "dati" / "eventi" / "verificati" / f"eventi-verificati-{data}.md"
    f_post = radice / "dati" / "post" / f"post-{data}.md"
    return {
        "data": data,
        "radice": str(radice),
        "ricerca": {"file": str(f_eventi.relative_to(radice)),
                    "presente": f_eventi.exists(),
                    "eventi": conta_eventi(f_eventi)},
        "verifica": {"file": str(f_verif.relative_to(radice)),
                     "presente": f_verif.exists(),
                     **(conta_verificati(f_verif) or
                        {"verificati": None, "da_confermare": None, "scartati": None})},
        "testi": {"file": str(f_post.relative_to(radice)),
                  "presente": f_post.exists(),
                  **(conta_bozze(f_post) or {"totale": None, "per_stato": {}})},
    }


def _n(v):
    return "assente" if v is None else str(v)


def stampa_italiano(m: dict) -> None:
    print(f"Giro del {m['data']}  ({m['radice']})")
    r, v, t = m["ricerca"], m["verifica"], m["testi"]
    print(f"  1 Ricerca : "
          + (f"{r['eventi']} eventi" if r["presente"]
             else "file non prodotto"))
    print(f"  3 Verifica: "
          + (f"✅ {v['verificati']} · ⚠️ {v['da_confermare']} · 🗑 {v['scartati']}"
             if v["presente"] else "file non prodotto"))
    stati = ", ".join(f"{k} {n}" for k, n in sorted(t["per_stato"].items())) or "—"
    print(f"  4 Testi   : "
          + (f"{t['totale']} bozze ({stati})" if t["presente"]
             else "file non prodotto"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=dt.date.today().isoformat(),
                    help="data del giro, formato AAAA-MM-GG (default: oggi)")
    ap.add_argument("--radice", default="",
                    help="radice del repo da misurare (default: quella corrente)")
    ap.add_argument("--json", action="store_true", help="uscita per gli script")
    a = ap.parse_args()

    radice = Path(a.radice).resolve() if a.radice else radice_repo()
    m = misura(radice, a.data)
    print(json.dumps(m, ensure_ascii=False, indent=2) if a.json else "", end="")
    if not a.json:
        stampa_italiano(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
