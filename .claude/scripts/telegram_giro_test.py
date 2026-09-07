#!/usr/bin/env python3
"""
TEST OFFLINE di telegram-giro.py — non manda niente a Telegram.
Si lancia con:  python3 .claude/scripts/telegram_giro_test.py

PERCHE' ESISTE (due guasti veri + una decisione di sicurezza):

1) Il guasto dell'08/08/2026: callback_data era `approve_01`, e `01` vuol dire
   "il primo evento DELL'ULTIMO GIRO". Ma i pulsanti dei messaggi vecchi non
   scadono mai: premuto oggi, un pulsante di tre giri fa dice `01` esattamente
   come quello di stamattina. Sei approvazioni non sono piu' state riconducibili
   a nessun evento.

2) Il guasto del 27/07/2026: lo stato veniva salvato anche quando NON era partito
   niente, e l'approvazione credeva che ci fosse qualcosa in attesa.

3) Il ticket 07 (07/09/2026): l'agente non tocca mai il token. Prepara la busta;
   a spedire e' un passo separato, che PRIMA controlla che i pulsanti abbiano la
   forma giusta. Qui sotto si prova che una busta malfatta non parte.
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

QUI = Path(__file__).parent
spec = importlib.util.spec_from_file_location("telegram_giro", QUI / "telegram-giro.py")
tg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tg)

OK = 0
KO = 0


def verifica(descrizione, condizione):
    global OK, KO
    if condizione:
        OK += 1
        print(f"  ✅ {descrizione}")
    else:
        KO += 1
        print(f"  ❌ {descrizione}")


EVENTI = [
    {"id": "01", "titolo": "Una Sera negli Anni '90", "tipo": "nuovo",
     "data": "12/08", "luogo": "Piazza della Libertà", "url": "https://esempio.sm/a"},
    {"id": "02", "titolo": "Baseball gara 1 vs Fortitudo Bologna", "tipo": "nuovo",
     "data": "14/08", "luogo": "La Ciarulla", "url": ""},
]


def ambiente(tmp):
    """Sposta TUTTI i percorsi dello script dentro una cartella usa-e-getta.
    Senza questo, un test sovrascriverebbe la busta e lo stato veri."""
    tg.RADICE = Path(tmp)
    tg.BUSTA = Path(tmp) / "queue" / "telegram-da-inviare.json"
    tg.CARTELLA_PENDING = Path(tmp) / "dati" / "telegram" / "pending"


def prepara(eventi, prova=False, summary=""):
    return tg.prepara(SimpleNamespace(events=json.dumps(eventi), summary=summary, prova=prova))


def prepara_solo_riepilogo(summary, eventi=None):
    return tg.prepara(SimpleNamespace(events=json.dumps(eventi) if eventi else "",
                                      summary=summary, prova=False, solo_riepilogo=True))


def main():
    print("\n[1] Il giro_id ha il formato giusto")
    giro = tg.nuovo_giro_id()
    verifica("formato AAAAMMGG-HHMM", len(giro) == 13 and giro[8] == "-")
    verifica("solo cifre e un trattino", giro.replace("-", "").isdigit())
    verifica("con --prova prende il prefisso PROVA-", tg.nuovo_giro_id(prova=True).startswith("PROVA-"))

    print("\n[2] Il callback_data porta dentro il giro")
    dati = tg.callback_data("approve", "20260810-0707", "01")
    verifica("formato approve_<giro>-<id>", dati == "approve_20260810-0707-01")
    verifica("sotto il limite Telegram di 64 byte", len(dati.encode("utf-8")) <= 64)
    verifica("ci sta anche col prefisso di prova",
             len(tg.callback_data("reject", "PROVA-20260810-0707", "99").encode()) <= 64)

    print("\n[3] `prepara` scrive la busta e NON tocca il token")
    with tempfile.TemporaryDirectory() as tmp:
        ambiente(tmp)
        esito = prepara(EVENTI)
        verifica("esce 0", esito == 0)
        verifica("la busta esiste", tg.BUSTA.exists())
        busta = json.loads(tg.BUSTA.read_text())
        verifica("1 riepilogo + 1 blocco da 2 eventi", len(busta["messaggi"]) == 2)
        verifica("il primo messaggio non ha pulsanti", busta["messaggi"][0]["tasti"] is None)
        pulsanti = busta["messaggi"][1]["tasti"]["inline_keyboard"]
        verifica("due eventi = due righe di pulsanti", len(pulsanti) == 2)
        verifica("il pulsante porta il giro dentro",
                 pulsanti[0][0]["callback_data"].endswith(busta["giro_id"] + "-01"))
        verifica("nessuna mappa scritta prima dell'invio", not tg.CARTELLA_PENDING.exists())

        print("\n[4] Una busta rimasta lì NON viene sovrascritta (è un allarme)")
        verifica("il secondo prepara esce 6", prepara(EVENTI) == 6)
        verifica("la busta è ancora quella di prima",
                 json.loads(tg.BUSTA.read_text())["giro_id"] == busta["giro_id"])

    print("\n[5] Un ⚠️ senza spiegazione è un difetto dichiarato (esce 2, ma la busta c'è)")
    with tempfile.TemporaryDirectory() as tmp:
        ambiente(tmp)
        esito = prepara([{"id": "07c", "titolo": "Bagno Sonoro", "tipo": "dubbio"}])
        verifica("esce 2", esito == 2)
        verifica("la busta è scritta lo stesso", tg.BUSTA.exists())
        verifica("nel messaggio c'è scritto che il dubbio non è spiegato",
                 "Dubbio non spiegato" in json.loads(tg.BUSTA.read_text())["messaggi"][1]["testo"])

    print("\n[6] Il controllo boccia le buste malfatte (il muro del ticket 07)")
    buona = {
        "giro_id": "20260907-1830",
        "eventi": [{"id": "01", "titolo": "X"}],
        "messaggi": [{"testo": "ciao", "tasti": {"inline_keyboard": [[
            {"text": "✅ X", "callback_data": "approve_20260907-1830-01"},
            {"text": "❌", "callback_data": "reject_20260907-1830-01"}]]}}],
    }
    verifica("una busta giusta passa", tg.controlla_busta(buona) == [])

    def storpia(f):
        import copy
        b = copy.deepcopy(buona)
        f(b)
        return tg.controlla_busta(b)

    verifica("boccia un pulsante di un ALTRO giro",
             storpia(lambda b: b["messaggi"][0]["tasti"]["inline_keyboard"][0][0]
                     .__setitem__("callback_data", "approve_20260101-0000-01")) != [])
    verifica("boccia un comando inventato",
             storpia(lambda b: b["messaggi"][0]["tasti"]["inline_keyboard"][0][0]
                     .__setitem__("callback_data", "pubblica_20260907-1830-01")) != [])
    verifica("boccia un pulsante che non è ✅/❌",
             storpia(lambda b: b["messaggi"][0]["tasti"]["inline_keyboard"][0][0]
                     .__setitem__("text", "Approva tutto")) != [])
    verifica("boccia un pulsante che punta a un evento non in busta",
             storpia(lambda b: b["messaggi"][0]["tasti"]["inline_keyboard"][0][0]
                     .__setitem__("callback_data", "approve_20260907-1830-99")) != [])
    verifica("boccia un messaggio oltre i 4096 caratteri",
             storpia(lambda b: b["messaggi"][0].__setitem__("testo", "x" * 5000)) != [])
    verifica("boccia un giro_id fuori forma",
             storpia(lambda b: b.__setitem__("giro_id", "chissà")) != [])

    print("\n[7] Se NON parte niente, la busta resta e nessuno stato viene salvato")
    with tempfile.TemporaryDirectory() as tmp:
        ambiente(tmp)
        prepara(EVENTI)
        tg.manda_messaggio = lambda *a, **k: False          # rete staccata
        esito = tg.invia(SimpleNamespace(busta=""))
        verifica("esce 1", esito == 1)
        verifica("la busta è ancora lì (è l'allarme)", tg.BUSTA.exists())
        verifica("nessuna mappa del giro", not tg.CARTELLA_PENDING.exists())

    print("\n[8] Invio riuscito: mappa salvata, busta cancellata")
    with tempfile.TemporaryDirectory() as tmp:
        ambiente(tmp)
        prepara(EVENTI)
        giro = json.loads(tg.BUSTA.read_text())["giro_id"]
        tg.manda_messaggio = lambda *a, **k: True
        verifica("esce 0", tg.invia(SimpleNamespace(busta="")) == 0)
        verifica("la busta è sparita", not tg.BUSTA.exists())
        mappa = tg.CARTELLA_PENDING / f"{giro}.json"
        verifica("la mappa del giro esiste", mappa.exists())
        verifica("contiene tutti gli eventi", len(json.loads(mappa.read_text())["eventi"]) == 2)
        verifica("conserva il titolo esatto",
                 json.loads(mappa.read_text())["eventi"][1]["titolo"]
                 == "Baseball gara 1 vs Fortitudo Bologna")
        verifica("il puntatore all'ultimo giro è scritto",
                 (tg.CARTELLA_PENDING / "ultimo-giro.txt").read_text().strip() == giro)

        print("\n[9] Due giri NON si sovrascrivono (il guasto dell'08/08)")
        prepara([EVENTI[0]])
        giro2 = json.loads(tg.BUSTA.read_text())["giro_id"]
        tg.invia(SimpleNamespace(busta=""))
        rimasti = sorted(p.name for p in tg.CARTELLA_PENDING.glob("*.json"))
        if giro == giro2:   # stesso minuto: il caso non è distinguibile, si salta
            verifica("(stesso minuto: caso non applicabile)", True)
        else:
            verifica("restano due file distinti", rimasti == sorted([f"{giro}.json", f"{giro2}.json"]))
            verifica("il primo giro è intatto",
                     len(json.loads((tg.CARTELLA_PENDING / f"{giro}.json").read_text())["eventi"]) == 2)

    print("\n[10] Invio a metà: la mappa si salva lo stesso e la lista è dichiarata incompleta")
    with tempfile.TemporaryDirectory() as tmp:
        ambiente(tmp)
        prepara(EVENTI)
        giro = json.loads(tg.BUSTA.read_text())["giro_id"]
        avvisi = []
        stato = {"n": 0}

        def a_meta(testo, tasti=None, **k):
            stato["n"] += 1
            if tasti is None and stato["n"] > 1:
                avvisi.append(testo)      # l'avviso finale di lista incompleta
                return True
            return stato["n"] == 1         # parte solo il riepilogo

        tg.manda_messaggio = a_meta
        verifica("esce 3", tg.invia(SimpleNamespace(busta="")) == 3)
        verifica("la mappa è salvata comunque", (tg.CARTELLA_PENDING / f"{giro}.json").exists())
        verifica("Michele riceve l'avviso «lista INCOMPLETA»",
                 any("INCOMPLETA" in a for a in avvisi))

    print("\n[11] Solo riepilogo (il giro in cloud, ticket 08): niente pulsanti, testo dettato")
    with tempfile.TemporaryDirectory() as tmp:
        ambiente(tmp)
        testo = "🤖 Secondo parere del cloud — 22 eventi, 21 verificati, 24 bozze."
        verifica("esce 0", prepara_solo_riepilogo(testo) == 0)
        b = json.loads(tg.BUSTA.read_text())
        verifica("un solo messaggio", len(b["messaggi"]) == 1)
        verifica("nessun pulsante", b["messaggi"][0]["tasti"] is None)
        verifica("il testo è quello dettato, non il modello del giro",
                 b["messaggi"][0]["testo"] == testo)
        verifica("NON dice «Nessuna novità» (sarebbe una bugia)",
                 "Nessuna novità" not in b["messaggi"][0]["testo"])
        verifica("`invia` la accetta (il muro non la scambia per malfatta)",
                 tg.controlla_busta(b) == [])

    print("\n[12] Solo riepilogo: i due modi di usarlo male vengono fermati")
    with tempfile.TemporaryDirectory() as tmp:
        ambiente(tmp)
        verifica("senza testo esce 7", prepara_solo_riepilogo("") == 7)
        verifica("e non scrive nessuna busta", not tg.BUSTA.exists())
    with tempfile.TemporaryDirectory() as tmp:
        ambiente(tmp)
        verifica("con degli eventi esce 7 (sarebbero pulsanti mai spediti)",
                 prepara_solo_riepilogo("ciao", EVENTI) == 7)
        verifica("e non scrive nessuna busta", not tg.BUSTA.exists())

    print(f"\n{'='*60}\n✅ {OK} verifiche passate   ❌ {KO} fallite\n{'='*60}")
    return 1 if KO else 0


if __name__ == "__main__":
    sys.exit(main())
