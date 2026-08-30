#!/usr/bin/env python3
"""
controllo-caption-prezzi.py — guardia PRE-PUSH sui contenuti delle buste in coda.

PERCHE' ESISTE
--------------
La regola equita' tra organizzatori (13/07/2026) vieta prezzi e gratuita' in OGNI
contenuto pubblico — non solo sul grafico, anche in caption. `publish.py` su GitHub
ha gia' questa rete (`caption_prezzi()`), ma **blocca in SILENZIO**: la busta diventa
"anomala", non si pubblica, e l'unico segnale e' un avviso Telegram del robot facile
da non notare. E' successo due volte:
  - settimanale 18-23/08: mai uscito per 3+ giorni, scoperto solo il 21/08.
  - carosello Settembre (30/08): caption con "gratis" ovunque, intercettata a mano
    all'ultimo prima del push.

Questa guardia porta lo stesso controllo **sul Mac, PRIMA del push**, e FALLISCE
(exit 1) invece di lasciar partire una busta che poi resta bloccata per sempre.
Usa lo STESSO pattern di `publish.py` (import diretto: zero rischio di drift).

Controlla anche la **lunghezza caption** (limite Instagram 2200): stesso motivo
(Meta la rifiuta a ogni giro senza che nessuno lo veda — carosello Agosto, 02/08).

USO
---
    python3 scripts/controllo-caption-prezzi.py            # tutte le buste in posts/
    python3 scripts/controllo-caption-prezzi.py posts/20260831_Carosello.json ...

CODICI DI USCITA
    0  tutte le caption sono pulite
    1  almeno una busta ha prezzi/gratuita' o caption fuori limite -> NON pushare
    2  errore di setup (publish.py non importabile, cartella posts/ assente)
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

# Oltre questa finestra publish.py considera la busta "scaduta" e non la tocca comunque
# (stesso GRACE_DAYS del robot): non ha senso far fallire il giro per una busta vecchia
# gia' bloccata da mesi. La guardia serve a fermare le buste che POTREBBERO ancora uscire.
GRACE_DAYS = 2

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from guardia_contenuti import caption_prezzi, lunghezza_caption, IG_CAPTION_MAX
except Exception as e:  # pragma: no cover - solo se guardia_contenuti.py sparisce
    print(f"❌ setup: non riesco a importare guardia_contenuti.py ({e})", file=sys.stderr)
    sys.exit(2)


def buste_da_controllare(argv):
    if argv:
        return [Path(a) if Path(a).is_absolute() else REPO / a for a in argv]
    posts = REPO / "posts"
    if not posts.is_dir():
        print(f"❌ setup: {posts} non esiste", file=sys.stderr)
        sys.exit(2)
    return sorted(posts.glob("*.json"))


def main():
    buste = buste_da_controllare(sys.argv[1:])
    problemi = []
    controllate = 0
    saltate_scadute = 0
    limite_scaduta = date.today() - timedelta(days=GRACE_DAYS)
    espliciti = bool(sys.argv[1:])  # se l'utente passa buste a mano, controllale tutte

    for j in buste:
        try:
            meta = json.loads(j.read_text(encoding="utf-8"))
        except Exception as e:
            problemi.append((j.name, f"JSON illeggibile: {e}"))
            continue

        tipo = meta.get("tipo", "")
        if tipo == "storia":
            continue  # le storie non hanno caption: il testo e' nella grafica

        if not espliciti:
            try:
                dp = date.fromisoformat(str(meta.get("data_pubblicazione", "")))
                if dp < limite_scaduta:
                    saltate_scadute += 1
                    continue  # gia' scaduta: publish.py non la tocca comunque
            except ValueError:
                pass  # data illeggibile: la lascio controllare, male non fa

        caption = (meta.get("caption") or "").strip()
        controllate += 1

        if not caption:
            problemi.append((j.name, "caption vuota (obbligatoria per questo tipo)"))
            continue

        prezzi = caption_prezzi(caption)
        if prezzi:
            problemi.append((
                j.name,
                f"prezzi/gratuita' in caption: {', '.join(prezzi)} "
                f"— regola equita', i costi vanno SOLO nel link in bio",
            ))

        n = lunghezza_caption(caption)
        if n > IG_CAPTION_MAX:
            problemi.append((
                j.name,
                f"caption troppo lunga per Instagram: {n} caratteri "
                f"(limite {IG_CAPTION_MAX}) — accorciala di almeno {n - IG_CAPTION_MAX}",
            ))

    print("Guardia caption — prezzi/gratuita' + lunghezza (regola equita' 13/07/2026)")
    print(f"Buste con caption controllate: {controllate}"
          + (f"  ({saltate_scadute} scadute saltate)" if saltate_scadute else ""))
    print()

    if not problemi:
        print("✅ Tutte le caption sono pulite: nessun prezzo/gratuita', nessuna fuori limite.")
        return 0

    print("❌ BUSTE DA NON PUSHARE (publish.py le bloccherebbe in silenzio):")
    for nome, motivo in problemi:
        print(f"   • {nome}: {motivo}")
    print()
    print("Correggi la caption nella busta (e nel dossier sorgente), poi rilancia.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
