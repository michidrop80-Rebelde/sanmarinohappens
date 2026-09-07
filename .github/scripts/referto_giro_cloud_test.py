#!/usr/bin/env python3
"""Prove del referto del giro in cloud (ticket 08).

Il referto è l'unica cosa che Michele vede di un giro girato di notte. Se
mentisse — «tutto bene» su un giro caduto, o «nessuna novità» su un giro pieno
di eventi — non se ne accorgerebbe nessuno. Qui i quattro casi si provano senza
far girare niente in cloud.

    python3 .github/scripts/referto_giro_cloud_test.py
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

QUI = Path(__file__).resolve().parent
SCRIPT = QUI / "referto-giro-cloud.py"

OK = KO = 0


def verifica(descrizione, condizione):
    global OK, KO
    if condizione:
        OK += 1
        print(f"  ✅ {descrizione}")
    else:
        KO += 1
        print(f"  ❌ {descrizione}")


BASE = {
    "DATA": "2026-09-14",
    "AVVIO": "0",
    "RIPRESA": "no",
    "INTEGRITA": "✅",
    "RUN_URL": "https://github.com/x/y/actions/runs/1",
    "E_RIPRESA": "false",
}

COMPLETO = {
    "T1_STATO": "fatta", "T1_COSTO": "1.20", "T1_EVENTI": "22", "T1_RES": "success",
    "T2_STATO": "fatta", "T2_COSTO": "0.30", "T2_EVENTI": "24", "T2_RES": "success",
    "T3_STATO": "fatta", "T3_COSTO": "1.10", "T3_VERIFICATI": "21/2/2", "T3_RES": "success",
    "T4_STATO": "fatta", "T4_COSTO": "0.40", "T4_BOZZE": "24", "T4_RES": "success",
}

VUOTO = {
    "T1_STATO": "fatta", "T1_COSTO": "0.50", "T1_EVENTI": "0", "T1_RES": "success",
    "T2_STATO": "fatta", "T2_COSTO": "0.10", "T2_EVENTI": "0", "T2_RES": "success",
    "T3_STATO": "", "T3_COSTO": "", "T3_VERIFICATI": "", "T3_RES": "skipped",
    "T4_STATO": "", "T4_COSTO": "", "T4_BOZZE": "", "T4_RES": "skipped",
}

CADUTO = {
    "T1_STATO": "fatta", "T1_COSTO": "1.20", "T1_EVENTI": "22", "T1_RES": "success",
    "T2_STATO": "fatta", "T2_COSTO": "0.30", "T2_EVENTI": "24", "T2_RES": "success",
    "T3_STATO": "FALLITA", "T3_COSTO": "0.80", "T3_VERIFICATI": "-", "T3_RES": "failure",
    "T4_STATO": "", "T4_COSTO": "", "T4_BOZZE": "", "T4_RES": "skipped",
}

RIPRESA_A_VUOTO = {
    "T1_STATO": "saltata (già fatta in una corsa precedente)", "T1_COSTO": "0",
    "T1_EVENTI": "22", "T1_RES": "success",
    "T2_STATO": "saltata (già fatta in una corsa precedente)", "T2_COSTO": "0",
    "T2_EVENTI": "24", "T2_RES": "success",
    "T3_STATO": "saltata (già fatta in una corsa precedente)", "T3_COSTO": "0",
    "T3_VERIFICATI": "21/2/2", "T3_RES": "success",
    "T4_STATO": "saltata (già fatta in una corsa precedente)", "T4_COSTO": "0",
    "T4_BOZZE": "24", "T4_RES": "success",
}


def corri(extra, gia_avvisato=False):
    """Lancia il referto in una cartella usa-e-getta e restituisce (testo, manda)."""
    with tempfile.TemporaryDirectory() as tmp:
        amb = dict(os.environ)
        amb.update(BASE)
        amb.update({k: str(v) for k, v in extra.items()})
        uscite = Path(tmp) / "github_output"
        uscite.write_text("")
        amb["GITHUB_OUTPUT"] = str(uscite)
        if gia_avvisato:
            d = Path(tmp) / "dati" / "cloud-giro" / BASE["DATA"]
            d.mkdir(parents=True)
            (d / "avvisato.ok").write_text("spedito")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=tmp, env=amb,
                       check=True, capture_output=True)
        testo = Path("/tmp/referto.txt").read_text(encoding="utf-8")
        manda = "si" if "manda=si" in uscite.read_text() else "no"
        return testo, manda


def main():
    print("\n[1] Giro completo: dice i numeri veri, e dice che i pulsanti non sono suoi")
    t, manda = corri(COMPLETO)
    verifica("manda il messaggio", manda == "si")
    verifica("dice 22 eventi", "22 eventi" in t)
    verifica("dice ✅ 21 · ⚠️ 2 · 🗑 2", "✅ 21 · ⚠️ 2 · 🗑 2" in t)
    verifica("dice 24 bozze", "24 bozze" in t)
    verifica("somma il peso delle quattro tappe ($3,00)", "$3,00" in t)
    verifica("avvisa che i pulsanti li manda il Mac", "il Mac alle 08:05" in t)
    verifica("NON dice che è caduto", "🔴" not in t)

    print("\n[2] Ricerca e bot a vuoto: silenzio dichiarato, non un guasto")
    t, manda = corri(VUOTO)
    verifica("manda il messaggio lo stesso", manda == "si")
    verifica("è giallo, non rosso", t.startswith("🟡") and "🔴" not in t)
    verifica("dice a chiare lettere che non è un guasto",
             "non è un guasto" in t.lower())
    verifica("spiega di essersi fermato prima della verifica",
             "prima della verifica" in t)

    print("\n[3] Caduto a metà, prima corsa: dice DOVE, cosa è salvo, e che riprova")
    t, manda = corri(CADUTO)
    verifica("manda il messaggio", manda == "si")
    verifica("è rosso", t.startswith("🔴"))
    verifica("dice a quale tappa", "tappa 3 (verifica)" in t)
    verifica("dice cosa è salvo sul ramo", "Ricerca, Postino".lower() in t.lower())
    verifica("promette la ripresa delle 09:00", "alle 09:00" in t)

    print("\n[4] Caduto DI NUOVO alla ripresa: non promette una riprova che non farà")
    t2, _ = corri(CADUTO | {"E_RIPRESA": "true"})
    verifica("dice che era già la ripresa", "ERA già la ripresa" in t2)
    verifica("NON promette un'altra riprova automatica",
             "Riprovo da solo alle 09:00" not in t2)
    verifica("rassicura che il Mac non è toccato", "Mac non è toccato" in t2)

    print("\n[5] Ripresa che non aveva niente da fare: non manda un doppione")
    t, manda = corri(RIPRESA_A_VUOTO, gia_avvisato=True)
    verifica("NON rimanda il messaggio", manda == "no")
    t, manda = corri(COMPLETO, gia_avvisato=True)
    verifica("ma se ha davvero lavorato, avvisa lo stesso", manda == "si")

    print("\n[6] Integrità: se grida finisce nel messaggio, se tace non fa rumore")
    t, _ = corri(COMPLETO)
    verifica("silenzio quando è a posto", "Integrità" not in t)
    t, _ = corri(COMPLETO | {"INTEGRITA": "❌ file mancanti (vedi la run)"})
    verifica("compare quando manca qualcosa", "Integrità: ❌ file mancanti" in t)

    print(f"\n{'='*60}\n✅ {OK} verifiche passate   ❌ {KO} fallite\n{'='*60}")
    return 1 if KO else 0


if __name__ == "__main__":
    sys.exit(main())
