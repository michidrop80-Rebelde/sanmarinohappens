#!/usr/bin/env python3
"""
TEST OFFLINE della guardia doppioni — non tocca la rete, non legge dati/, non scrive niente.
Si lancia con:  python3 scripts/segnala_doppioni_test.py

Perche' esiste
--------------
L'08/08/2026 la guardia ha esaminato 6 blocchi su 7 del file dati/post/post-2026-08-08.md:
la bozza `## [19-20/08] — Balamondo World Music Festival` non faceva match con le regex
(che accettavano solo `[GG/MM]`), finiva nella lista di passaggio e non veniva MAI
confrontata con la coda. Il 19/08 aveva gia' la sua busta (posts/20260819_Post giornaliero.json):
un doppione vero, invisibile. E la guardia stampava lo stesso "✅ Nessun doppione".

Qui si prova che:
  1. le intestazioni a intervallo vengono riconosciute (chiave = PRIMA data, convenzione
     di progetto — vedi dati/grafica-stato.json, giro 21/07/2026);
  2. un blocco bozza che NON si riesce a leggere produce un AVVISO, non silenzio;
  3. il testo dei blocchi non riconosciuti viene comunque conservato intatto.
"""

import importlib.util
import sys
from pathlib import Path

PROGETTO = Path(__file__).resolve().parent.parent


def carica_modulo():
    """Il file ha il trattino nel nome: non e' importabile con `import`."""
    percorso = PROGETTO / "scripts" / "segnala-doppioni.py"
    spec = importlib.util.spec_from_file_location("segnala_doppioni", percorso)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


SD = carica_modulo()

ESITI = []


def verifica(descrizione, condizione):
    ESITI.append((descrizione, bool(condizione)))
    print(f"  {'✅' if condizione else '❌'}  {descrizione}")


# ---------------------------------------------------------------------------
# Mattoncini per costruire file bozze finti
# ---------------------------------------------------------------------------
def blocco(intestazione, stato="da-approvare"):
    return (
        f"## {intestazione}\n"
        "\n"
        "**📷 Testo per la grafica**\n"
        "- Titolo breve: qualcosa\n"
        "\n"
        f"**Stato bozza:** {stato}\n"
        "\n---\n\n"
    )


TESTATA = "# Bozze post — 2026-08-08\n\nPremessa che non e' una bozza.\n\n---\n\n"


def date_bozze(elenco):
    """Le etichette-data delle bozze, come le riporta la guardia."""
    return [d for d, _ in elenco]


# ---------------------------------------------------------------------------
# 1. Data singola — il comportamento che gia' funzionava, non deve rompersi
# ---------------------------------------------------------------------------
def test_data_singola():
    print("\n[1] data singola")
    testo = TESTATA + blocco("[10/08] — Concerto a Lume di Candela   ·   tipo: musica")

    r = SD.analizza(testo, {"20260810"})
    verifica("giorno gia' in coda -> doppione", date_bozze(r.doppioni) == ["10/08"])
    verifica("titolo letto bene", r.doppioni[0][1] == "Concerto a Lume di Candela")
    verifica("stato riscritto in gia-in-coda", "**Stato bozza:** gia-in-coda" in r.testo)
    verifica("nessun avviso", r.avvisi == [])

    r = SD.analizza(testo, set())
    verifica("giorno libero -> bozza buona", date_bozze(r.buone) == ["10/08"])
    verifica("niente doppioni", r.doppioni == [])
    verifica("testo non toccato", r.testo == testo)


# ---------------------------------------------------------------------------
# 2. Intervallo — il bug dell'08/08/2026
# ---------------------------------------------------------------------------
def test_intervallo_stesso_mese():
    print("\n[2] intervallo [GG-GG/MM] (il bug dell'08/08)")
    testo = TESTATA + blocco(
        "[19-20/08] — Balamondo World Music Festival   ·   tipo: musica"
    )

    r = SD.analizza(testo, {"20260819"})
    verifica("prima data in coda -> doppione", date_bozze(r.doppioni) == ["19-20/08"])
    verifica("titolo letto bene", r.doppioni[0][1] == "Balamondo World Music Festival")
    verifica("stato riscritto", "**Stato bozza:** gia-in-coda" in r.testo)
    verifica("nessun avviso: e' un formato legittimo", r.avvisi == [])

    r = SD.analizza(testo, set())
    verifica("nessuna busta -> bozza buona", date_bozze(r.buone) == ["19-20/08"])

    # La convenzione di progetto e' PRIMA data: il 20/08 occupato non basta.
    r = SD.analizza(testo, {"20260820"})
    verifica("solo la seconda data in coda -> NON e' doppione", r.doppioni == [])
    verifica("...e resta da approvare", date_bozze(r.buone) == ["19-20/08"])


def test_intervallo_a_cavallo_di_mese():
    print("\n[3] intervallo [GG/MM-GG/MM]")
    testo = TESTATA + blocco("[30/08-01/09] — Sagra lunga   ·   tipo: gastronomia")

    r = SD.analizza(testo, {"20260830"})
    verifica("chiave = prima data (30/08)", date_bozze(r.doppioni) == ["30/08-01/09"])

    r = SD.analizza(testo, {"20260901"})
    verifica("ultima data in coda -> non e' doppione", r.doppioni == [])


# ---------------------------------------------------------------------------
# 3. I blocchi non devono incollarsi fra loro (il conteggio 6 invece di 7)
# ---------------------------------------------------------------------------
def test_blocchi_non_si_incollano():
    print("\n[4] ogni bozza e' un blocco a se'")
    testo = (
        TESTATA
        + blocco("[10/08] — Uno   ·   tipo: musica")
        + blocco("[15/08] — Due   ·   tipo: sport")
        + blocco("[19-20/08] — Tre   ·   tipo: musica")
        + "## Giorni richiesti senza evento verificato\n\nNessuno.\n"
    )

    r = SD.analizza(testo, set())
    verifica("3 bozze esaminate, non 2", len(r.buone) == 3)
    verifica("in ordine", date_bozze(r.buone) == ["10/08", "15/08", "19-20/08"])
    verifica("la coda del file non e' una bozza: nessun avviso", r.avvisi == [])
    verifica("sezione finale conservata", "Giorni richiesti senza evento" in r.testo)

    # Solo la terza e' in coda: le altre due non devono essere toccate.
    r = SD.analizza(testo, {"20260819"})
    verifica("un solo doppione", date_bozze(r.doppioni) == ["19-20/08"])
    verifica("un solo stato riscritto", r.testo.count("gia-in-coda") == 1)
    verifica("le altre restano da-approvare", r.testo.count("da-approvare") == 2)


# ---------------------------------------------------------------------------
# 4. Un blocco che non si riesce a leggere deve GRIDARE
# ---------------------------------------------------------------------------
def test_bozza_illeggibile_avvisa():
    print("\n[5] blocco `## [` non riconosciuto -> avviso, non silenzio")
    testo = TESTATA + blocco("[data da definire] — Evento misterioso")

    r = SD.analizza(testo, set())
    verifica("un avviso", len(r.avvisi) == 1)
    verifica("l'avviso cita il blocco", "data da definire" in r.avvisi[0])
    verifica("non conta come bozza buona", r.buone == [])
    verifica("testo del blocco conservato", "Evento misterioso" in r.testo)


def test_intestazione_senza_parentesi_avvisa():
    print("\n[6] `## 10/08 —` senza parentesi quadre -> avviso, ma il lavoro si fa")
    testo = TESTATA + blocco("10/08 — Concerto senza parentesi   ·   tipo: musica")

    r = SD.analizza(testo, {"20260810"})
    verifica("riconosciuta lo stesso -> doppione trovato", date_bozze(r.doppioni) == ["10/08"])
    verifica("stato riscritto", "**Stato bozza:** gia-in-coda" in r.testo)
    verifica("ma avvisa del formato", len(r.avvisi) == 1)
    verifica("l'avviso spiega cosa manca", "[" in r.avvisi[0])


def test_nessuna_bozza_letta_ma_da_approvare_presente():
    print("\n[7] file pieno di `da-approvare` e zero bozze lette -> allarme")
    # Nessun `##` affatto: la guardia non puo' leggere niente, ma il file dice
    # chiaramente che c'e' roba da approvare.
    testo = "# Bozze post\n\n**Stato bozza:** da-approvare\n"

    r = SD.analizza(testo, set())
    verifica("zero bozze lette", r.buone == [] and r.doppioni == [])
    verifica("ma avvisa", r.avvisi != [])


# ---------------------------------------------------------------------------
# 5. Le bozze gia' processate non si toccano
# ---------------------------------------------------------------------------
def test_solo_da_approvare():
    print("\n[8] si guardano solo le bozze `da-approvare`")
    testo = TESTATA + blocco("[10/08] — Gia' vista", stato="approvato")

    r = SD.analizza(testo, {"20260810"})
    verifica("non e' un doppione da segnalare", r.doppioni == [])
    verifica("non e' una bozza buona", r.buone == [])
    verifica("nessun avviso", r.avvisi == [])
    verifica("testo intatto", r.testo == testo)


def main():
    print("TEST guardia doppioni (offline)")
    test_data_singola()
    test_intervallo_stesso_mese()
    test_intervallo_a_cavallo_di_mese()
    test_blocchi_non_si_incollano()
    test_bozza_illeggibile_avvisa()
    test_intestazione_senza_parentesi_avvisa()
    test_nessuna_bozza_letta_ma_da_approvare_presente()
    test_solo_da_approvare()

    falliti = [d for d, ok in ESITI if not ok]
    print(f"\n{'-' * 60}")
    if falliti:
        print(f"❌ {len(falliti)} controlli falliti su {len(ESITI)}:")
        for d in falliti:
            print(f"   - {d}")
        return 1
    print(f"✅ tutti i {len(ESITI)} controlli passati.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
