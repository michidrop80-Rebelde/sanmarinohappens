#!/usr/bin/env python3
"""Prove del metro che conta un giro della catena (scripts/conta-giro.py).

PERCHE' ESISTE
La notte dell'8 settembre 2026 il giro in cloud ha mandato a Michele un referto che
diceva «Ricerca 24 eventi · Verifica ✅ 25 · 🗑 0». Gli eventi veri erano **22**, i
verificati **21** e lo scartato **1**. Nessuno se n'era accorto: i numeri erano
gonfi ma plausibili. Due difetti, tutti e due nel modo di riconoscere un evento:

  1. contava per eventi anche le intestazioni di servizio in fondo al file della
     ricerca ("⚠️ Fonti non raggiungibili", "🔧 Auto-miglioramento di oggi");
  2. non riconosceva le intestazioni di sezione del file verificato quando l'agente
     le scriveva "## ⚠️ Sezione 2 — Da confermare" invece di "## ⚠️ Da confermare":
     risultato, l'evento SCARTATO finiva contato fra i VERIFICATI, insieme alle
     intestazioni stesse.

Il metro e' l'unico giudice del giro in cloud (ticket 08: «un giro non si giudica da
verde, si giudica da cosa ha cambiato nei file»). Un metro che gonfia i numeri e'
peggio di nessun metro. Qui si prova che non lo fa piu'.

    python3 scripts/conta_giro_test.py
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "conta_giro", Path(__file__).resolve().parent / "conta-giro.py")
cg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cg)

OK = FAIL = 0


def verifica(cosa, condizione):
    global OK, FAIL
    if condizione:
        OK += 1
        print(f"  ✅ {cosa}")
    else:
        FAIL += 1
        print(f"  ❌ {cosa}")


def scrivi(cartella: Path, nome: str, testo: str) -> Path:
    f = cartella / nome
    f.write_text(testo, encoding="utf-8")
    return f


# --- i pezzi veri, copiati nella forma in cui li scrivono gli anelli ------------
EVENTO = """## {titolo}
- **Data:** 11/09/2026 — ore 21:00
- **Luogo:** Parco di Dogana
- **Tipo:** musica
- **Fonte:** https://esempio.sm
- **Stato:** {stato}
"""

SERVIZIO_FONTI = """## ⚠️ Fonti non raggiungibili
- **https://www.giornalesm.com** — WebFetch senza output
"""

SERVIZIO_AUTO = """## 🔧 Auto-miglioramento di oggi
- ✅ **https://www.libertas.sm** torna leggibile dai bot.
"""

SCARTATO = """## 🗑 {titolo}
- **Motivo:** doppione, gia' nel master.
- **Fonte controllata:** https://esempio.sm
- **Stato:** scartato
"""


def main():
    print("=" * 60)
    print("PROVE — il metro che conta un giro")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)

        print("\n[1] File della ricerca: le intestazioni di servizio NON sono eventi")
        f = scrivi(d, "ricerca.md", "# Eventi San Marino — 2026-09-08\n\n"
                   + EVENTO.format(titolo="Musikfest Adriatica", stato="da-verificare")
                   + EVENTO.format(titolo="36° Palio Don Bosco", stato="da-verificare")
                   + "\n---\n\n" + SERVIZIO_FONTI + "\n" + SERVIZIO_AUTO)
        verifica("2 eventi, non 4 (era il difetto del 08/09)", cg.conta_eventi(f) == 2)

        print("\n[2] Un evento con un marcatore davanti resta un evento")
        f = scrivi(d, "ricerca2.md", "# Eventi\n\n"
                   + EVENTO.format(titolo="⚠️ San Marino Special Cup", stato="da-verificare")
                   + SERVIZIO_FONTI)
        titoli = cg.titoli_eventi(f)
        verifica("contato", len(titoli) == 1)
        verifica("e il marcatore ⚠️ non finisce dentro il nome",
                 titoli == ["San Marino Special Cup"])

        print("\n[3] File verificato, intestazioni CORTE (forma del 07/09)")
        f = scrivi(d, "v1.md", "# Eventi verificati\n\n"
                   + "## ✅ Verificati (pronti per i testi)\n\n"
                   + EVENTO.format(titolo="Musikfest Adriatica", stato="verificato")
                   + EVENTO.format(titolo="36° Palio Don Bosco", stato="verificato")
                   + "\n## ⚠️ Da confermare (Michele)\n\n"
                   + EVENTO.format(titolo="⚠️ Artisti in Casa", stato="da-confermare-michele")
                   + "\n## 🗑 Scartati\n\n"
                   + SCARTATO.format(titolo="San Marino Beer Fest 2026")
                   + "\n## Note di verifica\n- nessun contenuto sospetto.\n")
        verifica("✅ 2 · ⚠️ 1 · 🗑 1",
                 cg.conta_verificati(f) == {"verificati": 2, "da_confermare": 1,
                                            "scartati": 1, "fuori_sezione": 0})

        print("\n[4] Stesso file, intestazioni LUNGHE (forma del 08/09) — stessi numeri")
        f = scrivi(d, "v2.md", "# Eventi verificati\n\n"
                   + "## ✅ Sezione 1 — Verificati (pronti per i testi)\n\n"
                   + EVENTO.format(titolo="Musikfest Adriatica", stato="verificato")
                   + EVENTO.format(titolo="36° Palio Don Bosco", stato="verificato")
                   + "\n---\n\n## ⚠️ Sezione 2 — Da confermare (Michele)\n\n"
                   + EVENTO.format(titolo="⚠️ Artisti in Casa", stato="da-confermare-michele")
                   + "\n---\n\n## 🗑 Sezione 3 — Scartati\n\n"
                   + SCARTATO.format(titolo="San Marino Beer Fest 2026")
                   + "\n---\n\n## 📌 Note di processo\n- registro aggiornato.\n")
        verifica("✅ 2 · ⚠️ 1 · 🗑 1 anche cosi' (era ✅ 5 · ⚠️ 0 · 🗑 0)",
                 cg.conta_verificati(f) == {"verificati": 2, "da_confermare": 1,
                                            "scartati": 1, "fuori_sezione": 0})

        print("\n[5] Una sezione vuota conta zero, non conta la frase che lo dice")
        f = scrivi(d, "v3.md", "# Eventi verificati\n\n"
                   + "## ✅ Sezione 1 — Verificati\n\n"
                   + EVENTO.format(titolo="Musikfest Adriatica", stato="verificato")
                   + "\n## ⚠️ Sezione 2 — Da confermare (Michele)\n\n"
                   + "_(nessun evento in questa sezione)_\n\n"
                   + "## 🗑 Sezione 3 — Scartati\n\n_(nessuno)_\n")
        verifica("✅ 1 · ⚠️ 0 · 🗑 0",
                 cg.conta_verificati(f) == {"verificati": 1, "da_confermare": 0,
                                            "scartati": 0, "fuori_sezione": 0})

        print("\n[6] Un evento che il metro non sa dove mettere GRIDA, non sparisce")
        f = scrivi(d, "v4.md", "# Eventi verificati\n\n"
                   + EVENTO.format(titolo="Evento senza sezione", stato="verificato")
                   + "\n## ✅ Sezione 1 — Verificati\n\n"
                   + EVENTO.format(titolo="Musikfest Adriatica", stato="verificato"))
        c = cg.conta_verificati(f)
        verifica("1 verificato", c["verificati"] == 1)
        verifica("1 fuori sezione, dichiarato", c["fuori_sezione"] == 1)

        print("\n[7] Un file che manca resta 'assente', non zero")
        verifica("ricerca assente", cg.conta_eventi(d / "non-esiste.md") is None)
        verifica("verificati assenti", cg.conta_verificati(d / "non-esiste.md") is None)

    print("\n[8] I file veri del 07/09 sul Mac")
    radice = cg.radice_repo()
    m = cg.misura(radice, "2026-09-07")
    verifica("20 eventi trovati dalla ricerca", m["ricerca"]["eventi"] == 20)
    verifica("✅ 21 · ⚠️ 2 · 🗑 1",
             (m["verifica"]["verificati"], m["verifica"]["da_confermare"],
              m["verifica"]["scartati"]) == (21, 2, 1))
    verifica("nessun evento fuori sezione", m["verifica"]["fuori_sezione"] == 0)

    print("\n" + "=" * 60)
    print(f"{'✅' if not FAIL else '❌'} {OK} verifiche passate   ❌ {FAIL} fallite")
    print("=" * 60)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
