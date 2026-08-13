#!/usr/bin/env python3
"""
TEST OFFLINE del TERZO CASO delle buste — non tocca la rete e non pubblica niente.
Si lancia con:  python3 scripts/publish_parziali_test.py

PERCHE' ESISTE (il caso 20260803_Post giornaliero):
Una busta scaduta ha oggi due vie d'uscita: se e' uscita su TUTTI i canali viene
archiviata in silenzio, se non e' MAI uscita finisce fra i non-pubblicati. Una busta
uscita A META' (Facebook si', Instagram no) e ormai scaduta non e' ne' l'una ne'
l'altra: restava in coda a mandare lo stesso avviso Telegram 4 volte al giorno, per
sempre. Per un giornaliero la finestra di recupero e' 0 giorni: quel canale non e' piu'
recuperabile, quindi l'avviso non e' azionabile.
"""

import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent))
# publish.py fa import di requests per le API Meta: in test offline non ce n'è bisogno.
sys.modules["requests"] = SimpleNamespace(post=lambda *a, **k: SimpleNamespace(json=lambda: {}))

import publish

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


def busta_finta(tmp, nome, tipo):
    """Una busta minima ma vera: publish.py legge json_file, immagini, meta, tipo."""
    png = Path(tmp) / f"{nome}.png"
    png.write_bytes(b"finto png")
    jf = Path(tmp) / f"{nome}.json"
    meta = {
        "data_pubblicazione": "2026-08-03T07:00:00",
        "titolo_evento": f"Evento {nome}",
        "caption": "testo",
    }
    jf.write_text(json.dumps(meta))
    return {"json_file": jf, "immagini": [png], "meta": meta,
            "tipo": tipo, "giorni_ritardo": 7}


def main():
    with tempfile.TemporaryDirectory() as tmp:
        # ⚠️ published.log e' un percorso RELATIVO: senza dirottarlo il test scrive nel
        # registro vero del repo (guasto scoperto il 07/08/2026, riga fantasma a.png|ig).
        # E' una STRINGA in publish.py (riga 116), non un Path: si rispetta il tipo.
        publish.PUBLISHED_LOG = str(Path(tmp) / "published.log")
        publish.ARCHIVIO_DIR = Path(tmp) / "archivio"
        publish.FB_ENABLED = True  # Il test verifica entrambi i canali

        giorn = busta_finta(tmp, "20260803_Post giornaliero", "giornaliero")
        aggr = busta_finta(tmp, "20260803_Settimanale", "settimanale")
        completa = busta_finta(tmp, "20260803_Storia", "storia")
        mai = busta_finta(tmp, "20260803_Altro", "giornaliero")

        chiave_g = publish.costruisci_unita(
            giorn["tipo"], giorn["json_file"], giorn["immagini"], giorn["meta"])[0]["chiave"]
        chiave_a = publish.costruisci_unita(
            aggr["tipo"], aggr["json_file"], aggr["immagini"], aggr["meta"])[0]["chiave"]
        chiavi_c = [u["chiave"] for u in publish.costruisci_unita(
            completa["tipo"], completa["json_file"], completa["immagini"], completa["meta"])]

        # Uscite a meta': solo su fb. Completa: su tutti i canali. Mai uscita: niente.
        # Formato: "chiave|canale" (come publish.py legge da published.log)
        pubblicati = {f"{chiave_g}|fb", f"{chiave_a}|fb"}
        for c in chiavi_c:
            for canale in publish.canali_richiesti():
                pubblicati.add(f"{c}|{canale}")

        print("\n[1] Un giornaliero uscito a meta' e scaduto viene CHIUSO")
        segnalare, parziali = publish.separa_parziali_scadute([giorn], pubblicati)
        verifica("finisce fra le parziali", len(parziali) == 1)
        verifica("non resta da segnalare", len(segnalare) == 0)

        print("\n[2] Un AGGREGATO uscito a meta' continua a segnalare")
        segnalare, parziali = publish.separa_parziali_scadute([aggr], pubblicati)
        verifica("l'aggregato resta da segnalare", len(segnalare) == 1)
        verifica("e non viene chiuso", len(parziali) == 0)

        print("\n[3] Le altre due famiglie non vengono rubate")
        segnalare, parziali = publish.separa_parziali_scadute([completa, mai], pubblicati)
        verifica("una busta completa non e' una parziale",
                 all(b is not completa for b in parziali))
        verifica("una mai uscita non e' una parziale",
                 all(b is not mai for b in parziali))
        verifica("restano entrambe da segnalare", len(segnalare) == 2)

        print("\n[4] Si sa DIRE quali canali sono usciti e quali no")
        usciti, mancanti = publish.canali_mancanti(giorn, pubblicati)
        verifica("Facebook risulta uscito", usciti == ["fb"])
        verifica("Instagram risulta mancante", "ig" in mancanti)

        print("\n[5] L'archivio delle parziali e' una cartella SUA")
        verifica("la sottocartella non e' quella dei post usciti",
                 publish.PARZIALI_SOTTOCARTELLA not in ("", None))
        verifica("ed e' diversa da quella dei non-pubblicati",
                 publish.PARZIALI_SOTTOCARTELLA != publish.SCARTI_SOTTOCARTELLA)

    print(f"\n{'='*60}\n✅ {OK} verifiche passate   ❌ {KO} fallite\n{'='*60}")
    return 1 if KO else 0


if __name__ == "__main__":
    sys.exit(main())
