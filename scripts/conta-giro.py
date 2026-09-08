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


# I titoli degli eventi sono "## Titolo". Anche le INTESTAZIONI DI SEZIONE del file
# verificato sono "## ", e vanno riconosciute per non contarle come eventi.
#
# ⚠️ COME SI RICONOSCE UN EVENTO (corretto il 08/09/2026 — vedi in fondo al file)
# NON dal nome dell'intestazione: i nomi cambiano ogni giorno, e le sezioni pure
# ("## ✅ Verificati" il 07/09, "## ✅ Sezione 1 — Verificati (pronti per i testi)"
# il 08/09). Si riconosce dalla FORMA del blocco: un evento ha sempre sotto il
# campo "- **Stato:**", una sezione no. Cosi' "## ⚠️ San Marino Special Cup" viene
# contato (e' un evento con un marcatore davanti) e "## 🔧 Auto-miglioramento di
# oggi" no (e' una sezione), senza dover indovinare dalle parole.
RIGA_TITOLO = re.compile(r"^##\s+(.*\S)\s*$")
# Un evento ha SEMPRE il campo Stato (da-verificare / verificato /
# da-confermare-michele / scartato) — anche quando non ha la Data, come i blocchi
# della sezione "Scartati", che hanno Motivo al posto di Data. La Data resta come
# seconda prova, per un evento a cui lo Stato fosse sfuggito.
CAMPO_EVENTO = re.compile(r"^\s*-\s+\*\*(Stato|Data):?\*\*")
# Un titolo che comincia con una di queste emoji e' un marcatore di stato messo
# davanti al nome dell'evento (es. "## ⚠️ Artisti in Casa"): l'emoji non fa parte
# del nome e si toglie, altrimenti il confronto fra i due giri non accosta nulla.
EMOJI_STATO = "✅⚠️🗑🆕✏️🔁"


def _blocchi(righe):
    """Spezza il file in blocchi: ogni "## intestazione" con le righe che la seguono."""
    blocchi, corrente = [], None
    for r in righe:
        m = RIGA_TITOLO.match(r)
        if m:
            grezzo = m.group(1)
            corrente = {"titolo": grezzo.lstrip(EMOJI_STATO + " "),
                        "grezzo": grezzo, "righe": []}
            blocchi.append(corrente)
        elif corrente is not None:
            corrente["righe"].append(r)
    return blocchi


def _e_evento(blocco) -> bool:
    """True se il blocco e' un evento (ha il campo Stato, o almeno la Data),
    False se e' un'intestazione di sezione o un blocco di servizio."""
    return any(CAMPO_EVENTO.match(r) for r in blocco["righe"])


def _quale_sezione(grezzo):
    """A quale sezione del file verificato corrisponde questa intestazione.
    Prima le parole (reggono se cambia l'emoji), poi l'emoji (regge se cambiano le
    parole). None = intestazione che non apre nessuna delle tre sezioni note
    (es. "## 📌 Note di verifica"): da li' in poi non si conta piu' niente."""
    t = grezzo.lower()
    if "da confermare" in t:
        return "da_confermare"
    if "scartat" in t:
        return "scartati"
    if "verificat" in t:
        return "verificati"
    if grezzo.startswith("⚠"):
        return "da_confermare"
    if grezzo.startswith("🗑"):
        return "scartati"
    if grezzo.startswith("✅"):
        return "verificati"
    return None


def _righe(p: Path):
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else None


# ⚠️ I TITOLI si estraggono qui, in un posto solo. `scripts/confronta-giri.py`
# li riusa importando questo file: se ognuno si scrivesse il suo lettore, prima
# o poi conterebbero cose diverse e il confronto mentirebbe senza dirlo.

def titoli_eventi(p: Path):
    """File della ricerca: i titoli degli eventi. None se il file manca.
    Le intestazioni di servizio in fondo al file ("Fonti non raggiungibili",
    "Auto-miglioramento di oggi") NON sono eventi e non si contano: si riconoscono
    perche' sotto non hanno il campo Data."""
    righe = _righe(p)
    if righe is None:
        return None
    return [b["titolo"] for b in _blocchi(righe) if _e_evento(b)]


def titoli_verificati(p: Path):
    """File dei verificati: i titoli, divisi per sezione. None se il file manca.

    `fuori_sezione` raccoglie gli eventi che stanno PRIMA di qualunque intestazione
    di sezione, o dopo un'intestazione che non e' nessuna delle tre note. Non si
    buttano via in silenzio: un evento che il metro non sa dove mettere e' un file
    fatto in modo diverso dal previsto, e chi guarda i numeri deve vederlo."""
    righe = _righe(p)
    if righe is None:
        return None
    esito = {"verificati": [], "da_confermare": [], "scartati": [], "fuori_sezione": []}
    sezione = None
    for b in _blocchi(righe):
        if _e_evento(b):
            esito[sezione or "fuori_sezione"].append(b["titolo"])
        else:
            sezione = _quale_sezione(b["grezzo"])
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
                        {"verificati": None, "da_confermare": None,
                         "scartati": None, "fuori_sezione": None})},
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
    riga_v = (f"✅ {v['verificati']} · ⚠️ {v['da_confermare']} · 🗑 {v['scartati']}"
              if v["presente"] else "file non prodotto")
    if v["presente"] and v.get("fuori_sezione"):
        riga_v += (f"  ⚠️ {v['fuori_sezione']} evento/i FUORI SEZIONE "
                   f"(il file non ha la forma attesa: vanno guardati a mano)")
    print(f"  3 Verifica: " + riga_v)
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
