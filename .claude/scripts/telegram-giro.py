#!/usr/bin/env python3
"""
telegram-giro.py — il riepilogo del giro SMH con i pulsanti ✅/❌.

DUE COMANDI, E NON PER CAPRICCIO (ticket 07 della mappa "La catena si stacca dal Mac")
-------------------------------------------------------------------------------------
L'agente che prepara il giro legge pagine web scritte da sconosciuti: se una di
quelle pagine contenesse istruzioni nascoste, l'agente non deve avere in mano
niente di pericoloso. Quindi il lavoro è spezzato in due:

  1) prepara  — NON tocca il token. Prende la lista degli eventi dall'agente e
                scrive la "busta" `queue/telegram-da-inviare.json`: testo,
                pulsanti e `giro_id` li costruisce QUESTO script, non l'agente.
                (Decisione Q1 del ticket 07: se l'agente venisse ingannato, il
                massimo che può fare è mentire su un titolo — la forma dei
                pulsanti non la tocca.)

  2) invia    — il passo "stupido" col token. Legge la busta, la CONTROLLA
                (i pulsanti devono avere la forma giusta, altrimenti non parte
                niente), spedisce, e solo dopo un invio riuscito salva la mappa
                del giro e cancella la busta.

  Uso:
      python3 .claude/scripts/telegram-giro.py prepara --events '[...]' [--summary "..."] [--prova]
      python3 .claude/scripts/telegram-giro.py invia   [--busta queue/telegram-da-inviare.json]

LA BUSTA CHE RESTA È UN ALLARME (decisione Q3 del ticket 07)
------------------------------------------------------------
La busta entra in git col resto del giro e viene cancellata SOLO dopo che
Telegram ha confermato. Se domani quel file è ancora lì, vuol dire nero su
bianco: "i pulsanti non sono partiti". In cloud, di notte, non c'è nessuno che
guarda se la corsa è andata rossa.

--events: JSON array di oggetti:
  [{"id":"09","titolo":"Sergio Caputo","tipo":"nuovo","data":"03/07",
    "luogo":"Campo Bruno Reffi","url":"https://...",
    "dubbio":"...","serve":"..."}]
  tipi validi: "nuovo" | "modificato" | "cancellato" | "dubbio"

CODICI DI USCITA
  prepara: 0 tutto ok · 2 c'è un "dubbio" senza spiegazione (busta scritta lo
           stesso: meglio un buco dichiarato che nessun pulsante) · 5 un evento
           da solo supera i 4096 caratteri di Telegram · 6 c'è già una busta non
           spedita (non la sovrascrivo: prima si capisce perché è rimasta lì)
  invia:   0 tutto partito · 1 NIENTE è partito (busta intatta, nessuno stato
           salvato) · 3 partito a metà (mappa salvata, lista dichiarata
           incompleta) · 4 la busta è malfatta: non spedisco niente
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# La radice del repo: sul Mac ~/Desktop/PROGETTI/San Marino Happens, in GitHub
# Actions la cartella del checkout. Mai un percorso assoluto (ticket 11).
RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE / "scripts"))
from telegram_helper import manda_messaggio  # noqa: E402

BUSTA = RADICE / "queue" / "telegram-da-inviare.json"

# Dove vivono le mappe numero→evento, una per giro.
# ⚠️ NON in .claude/secrets/: backup-cervello.sh esclude quella cartella apposta
# (contiene token), quindi finche' la mappa stava li' non aveva ne' storico ne'
# backup — ed e' esattamente cosi' che le 6 approvazioni dell'08/08/2026 sono
# diventate non piu' riconducibili a nessun evento.
CARTELLA_PENDING = RADICE / "dati" / "telegram" / "pending"

MAX_TELEGRAM = 4096          # limite di caratteri di un messaggio
MAX_CALLBACK = 64            # limite in byte del dato dentro un pulsante

ICONE = {
    "nuovo": "🆕",
    "modificato": "✏️",
    "cancellato": "🗑",
    "dubbio": "⚠️",
}


# ----------------------------------------------------------------------------
# PARTE 1 — PREPARA (nessun token in mano)
# ----------------------------------------------------------------------------

def nuovo_giro_id(prova=False):
    """Identita' del giro: AAAAMMGG-HHMM in UTC. Basta al minuto — due giri nello
    stesso minuto non esistono, e il formato resta corto per stare nei 64 byte di
    callback_data. Con --prova prende il prefisso PROVA-, cosi' l'approvazione
    riconosce a colpo d'occhio le righe di collaudo e non le scambia per vere."""
    stampo = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    return f"PROVA-{stampo}" if prova else stampo


def callback_data(azione, giro_id, ev_id):
    """Il dato che viaggia dentro il pulsante.

    Prima era `approve_01`, e `01` significava "il primo evento DELL'ULTIMO GIRO".
    Ma i pulsanti dei messaggi vecchi restano cliccabili per sempre: premuto oggi,
    un pulsante di tre giri fa diceva `01` come quello di stamattina. Con il giro
    dentro, ogni pulsante dice da solo a quale lista appartiene."""
    return f"{azione}_{giro_id}-{ev_id}"


def blocchi(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def riga_evento(ev):
    """Il testo di UN evento dentro il messaggio. Ritorna (testo, dubbio_muto)."""
    icona = ICONE.get(str(ev.get("tipo", "dubbio")).lower(), "⚠️")
    riga = f"{icona} <b>{ev.get('titolo', '?')}</b>"
    if ev.get("data"):
        riga += f"\n📅 {ev['data']}"
    if ev.get("luogo"):
        riga += f" · 📍 {ev['luogo']}"
    if ev.get("url"):
        riga += f"\n🔗 {ev['url']}"

    # ⚠️ Un dubbio DEVE dire qual e' il problema (regola di Michele, 10/08/2026:
    # «non basta il solo segnale di pericolo»). Un ⚠️ nudo sposta la decisione su
    # di lui senza dargli l'informazione per deciderla: preme ✅ per non bloccare
    # la catena e il dubbio entra nel sistema come un dato verificato — e' cosi'
    # che «Mi Gusto» (date 2025) e la chiusura dell'11/08 della Sagra della
    # Tagliatella (dati 2024) sono arrivate a un giorno dalla pubblicazione.
    dubbio = (ev.get("dubbio") or "").strip()
    serve = (ev.get("serve") or "").strip()
    muto = False
    if dubbio:
        riga += f"\n⚠️ Cosa non torna: {dubbio}"
    elif str(ev.get("tipo", "")).lower() == "dubbio":
        riga += ("\n⚠️ <b>Dubbio non spiegato</b> — chiedi a Claude cosa non torna "
                 "prima di premere ✅")
        muto = True
    if serve:
        riga += f"\n👉 Per scioglierlo: {serve}"
    return riga, muto


def tastiera(eventi, giro_id):
    righe = []
    for ev in eventi:
        titolo = str(ev.get("titolo", "?"))
        corto = titolo[:20] + "…" if len(titolo) > 20 else titolo
        ev_id = ev.get("id", "?")
        righe.append([
            {"text": f"✅ {corto}", "callback_data": callback_data("approve", giro_id, ev_id)},
            {"text": "❌", "callback_data": callback_data("reject", giro_id, ev_id)},
        ])
    return {"inline_keyboard": righe}


def prepara(args):
    if BUSTA.exists():
        vecchia = json.loads(BUSTA.read_text())
        print(f"🛑 C'è già una busta NON spedita: giro {vecchia.get('giro_id')} "
              f"({len(vecchia.get('eventi', []))} eventi), creata {vecchia.get('creata_il')}.\n"
              f"   Vuol dire che l'ultimo invio non è riuscito. Non la sovrascrivo:\n"
              f"   prima si spedisce (`invia`) o si capisce perché è rimasta lì.\n"
              f"   File: {BUSTA}", file=sys.stderr)
        return 6

    eventi = json.loads(args.events)
    giro_id = nuovo_giro_id(prova=args.prova)

    conta = {"nuovo": 0, "modificato": 0, "cancellato": 0, "dubbio": 0}
    for e in eventi:
        t = str(e.get("tipo", "dubbio")).lower()
        if t in conta:
            conta[t] += 1

    oggi = datetime.now(timezone.utc).strftime("%d/%m/%Y")
    intestazione = "🧪 <b>PROVA</b> — " if args.prova else ""
    riepilogo = (
        f"{intestazione}🟢 <b>SMH — giro del {oggi}</b>\n\n"
        f"🆕 Nuovi: {conta['nuovo']}\n"
        f"✏️ Modificati: {conta['modificato']}\n"
        f"🗑 Potenzialmente cancellati: {conta['cancellato']}\n"
        f"⚠️ Dubbi: {conta['dubbio']}\n"
    )
    if args.summary:
        riepilogo += f"\n{args.summary}\n"
    riepilogo += ("\nSeguono i dettagli con i pulsanti 👇" if eventi
                  else "\n✅ Nessuna novità questa settimana.")

    messaggi = [{"testo": riepilogo, "tasti": None}]
    dubbi_muti = []
    troppo_lunghi = []

    for blocco in blocchi(eventi, 3):
        righe = []
        for ev in blocco:
            testo_ev, muto = riga_evento(ev)
            righe.append(testo_ev)
            if muto:
                dubbi_muti.append(f"{ev.get('id')} {ev.get('titolo')}")
        testo = "\n\n".join(righe)
        if len(testo) <= MAX_TELEGRAM:
            messaggi.append({"testo": testo, "tasti": tastiera(blocco, giro_id)})
            continue
        # Troppo lungo per Telegram: invece di farlo rifiutare in silenzio,
        # si spezza a un evento per messaggio. Non si taglia MAI il testo:
        # un dubbio troncato a metà è peggio di un messaggio in più.
        for ev in blocco:
            testo_ev, _ = riga_evento(ev)
            if len(testo_ev) > MAX_TELEGRAM:
                troppo_lunghi.append(f"{ev.get('id')} {ev.get('titolo')}")
                continue
            messaggi.append({"testo": testo_ev, "tasti": tastiera([ev], giro_id)})

    busta = {
        "giro_id": giro_id,
        "creata_il": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prova": bool(args.prova),
        "messaggi": messaggi,
        "eventi": [
            {
                "id": e.get("id"),
                "titolo": e.get("titolo"),
                "tipo": e.get("tipo"),
                "data": e.get("data", ""),
                "luogo": e.get("luogo", ""),
                "url": e.get("url", ""),
            }
            for e in eventi
        ],
    }
    BUSTA.parent.mkdir(parents=True, exist_ok=True)
    BUSTA.write_text(json.dumps(busta, ensure_ascii=False, indent=2))
    print(f"📨 Busta scritta: {BUSTA}")
    print(f"   Giro {giro_id} · {len(eventi)} eventi · {len(messaggi)} messaggi da spedire.")
    print("   Il token NON serve a questo passo: a spedire ci pensa `invia`.")

    if troppo_lunghi:
        print("🛑 Eventi troppo lunghi per un messaggio Telegram (>4096 caratteri), "
              "NON messi in busta: " + ", ".join(troppo_lunghi), file=sys.stderr)
        return 5
    if dubbi_muti:
        print("🛑 " + str(len(dubbi_muti)) + " eventi marcati 'dubbio' SENZA il campo "
              "`dubbio`: " + ", ".join(dubbi_muti) + "\n"
              "   Michele non può decidere su un ⚠️ nudo (sua regola, 10/08/2026).\n"
              "   La busta è scritta lo stesso (meglio un buco dichiarato che nessun "
              "pulsante), ma il giro è da completare.", file=sys.stderr)
        return 2
    return 0


# ----------------------------------------------------------------------------
# PARTE 2 — INVIA (il passo stupido, l'unico che tocca il token)
# ----------------------------------------------------------------------------

def controlla_busta(busta):
    """La busta è scritta da uno script, ma NON si dà per scontato.

    Se un domani l'agente scrivesse il file a mano (saltando `prepara`), qui si
    vede: i pulsanti devono avere esattamente la forma decisa, e ogni pulsante
    deve appartenere al giro dichiarato. Un pulsante fuori forma = non si
    spedisce niente. È il muro che rende vera la decisione Q1 del ticket 07.
    """
    problemi = []
    giro_id = str(busta.get("giro_id", ""))
    if not re.fullmatch(r"(PROVA-)?\d{8}-\d{4}", giro_id):
        problemi.append(f"giro_id fuori forma: {giro_id!r}")
        return problemi  # senza un giro valido non si controlla altro

    messaggi = busta.get("messaggi")
    if not isinstance(messaggi, list) or not messaggi:
        problemi.append("la busta non contiene nessun messaggio")
        return problemi

    id_eventi = {str(e.get("id")) for e in busta.get("eventi", [])}
    atteso = re.compile(r"^(approve|reject)_" + re.escape(giro_id) + r"-([A-Za-z0-9_.:-]{1,24})$")

    for i, m in enumerate(messaggi, 1):
        testo = m.get("testo", "")
        if not isinstance(testo, str) or not testo.strip():
            problemi.append(f"messaggio {i}: testo vuoto")
        elif len(testo) > MAX_TELEGRAM:
            problemi.append(f"messaggio {i}: {len(testo)} caratteri, oltre il limite {MAX_TELEGRAM}")
        tasti = m.get("tasti")
        if tasti is None:
            continue
        righe = (tasti or {}).get("inline_keyboard")
        if not isinstance(righe, list) or not righe:
            problemi.append(f"messaggio {i}: pulsanti fuori forma")
            continue
        for riga in righe:
            for b in riga:
                testo_b = str(b.get("text", ""))
                dato = str(b.get("callback_data", ""))
                if not (testo_b.startswith("✅") or testo_b.startswith("❌")):
                    problemi.append(f"messaggio {i}: pulsante che non è ✅/❌: {testo_b!r}")
                if len(dato.encode("utf-8")) > MAX_CALLBACK:
                    problemi.append(f"messaggio {i}: callback_data oltre i {MAX_CALLBACK} byte")
                m_ok = atteso.match(dato)
                if not m_ok:
                    problemi.append(f"messaggio {i}: callback_data fuori forma: {dato!r}")
                elif id_eventi and m_ok.group(2) not in id_eventi:
                    problemi.append(f"messaggio {i}: il pulsante punta a un evento "
                                    f"che non è in busta: {m_ok.group(2)!r}")
    return problemi


def salva_mappa_giro(busta):
    """Scrive dati/telegram/pending/<giro_id>.json e ritorna il percorso.
    Un file per giro: niente slot unico da sovrascrivere."""
    CARTELLA_PENDING.mkdir(parents=True, exist_ok=True)
    giro_id = busta["giro_id"]
    percorso = CARTELLA_PENDING / f"{giro_id}.json"
    percorso.write_text(json.dumps({
        "giro_id": giro_id,
        "sent_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prova": busta.get("prova", False),
        "eventi": busta.get("eventi", []),
    }, ensure_ascii=False, indent=2))
    # Il puntatore all'ultimo giro sta anche QUI, versionato: in cloud il file
    # .claude/secrets/telegram-state.json non esiste, e senza puntatore
    # l'approvazione non saprebbe quale mappa aprire.
    (CARTELLA_PENDING / "ultimo-giro.txt").write_text(giro_id + "\n")
    return percorso


def aggiorna_stato_mac(giro_id):
    """Sul Mac esiste ancora .claude/secrets/telegram-state.json: lo si tiene
    allineato per non rompere chi lo legge. In cloud quella cartella non c'è e
    questo passo semplicemente non fa nulla."""
    stato_path = RADICE / ".claude" / "secrets" / "telegram-state.json"
    if not stato_path.parent.exists():
        return
    try:
        stato = json.loads(stato_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        stato = {}
    stato["sent_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stato["ultimo_giro_id"] = giro_id
    stato.pop("pending_events", None)
    stato["_nota_pending"] = (
        "La mappa numero→evento NON sta piu' qui: sta in "
        "dati/telegram/pending/<giro_id>.json, un file per giro, versionato in git. "
        "Il puntatore all'ultimo giro sta in dati/telegram/pending/ultimo-giro.txt."
    )
    stato_path.write_text(json.dumps(stato, ensure_ascii=False, indent=2))


def credenziali_mac():
    """Ripiego per il Mac: se le variabili d'ambiente non ci sono, si legge il
    file dei segreti locale. In GitHub Actions questo file non esiste e le
    credenziali arrivano solo dall'ambiente del passo che spedisce."""
    f = RADICE / ".claude" / "secrets" / "telegram.json"
    if not f.exists():
        return None, None
    try:
        d = json.loads(f.read_text())
        return d.get("bot_token"), str(d.get("chat_id"))
    except (json.JSONDecodeError, OSError):
        return None, None


def invia(args):
    busta_path = Path(args.busta) if args.busta else BUSTA
    if not busta_path.exists():
        print(f"Nessuna busta da spedire ({busta_path}). Niente da fare.")
        return 0

    busta = json.loads(busta_path.read_text())
    problemi = controlla_busta(busta)
    if problemi:
        print("🛑 BUSTA MALFATTA — non spedisco niente:", file=sys.stderr)
        for p in problemi:
            print(f"   · {p}", file=sys.stderr)
        print("   La busta resta dov'è. I pulsanti devono avere la forma decisa "
              "dal ticket 07: chi l'ha scritta non l'ha fatto con `prepara`.", file=sys.stderr)
        return 4

    import os
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        token, chat_id = credenziali_mac()

    messaggi = busta["messaggi"]
    ok = err = 0
    for i, m in enumerate(messaggi, 1):
        riuscito = manda_messaggio(m["testo"], tasti=m.get("tasti"),
                                   parse_mode="HTML", token=token, chat_id=chat_id)
        print(f"  messaggio {i}/{len(messaggi)}: {'✅' if riuscito else '❌'}")
        ok += 1 if riuscito else 0
        err += 0 if riuscito else 1

    # ⚠️ Se NON e' partito niente, non si tocca lo stato (corretto il 27/07/2026).
    # Prima lo stato veniva salvato comunque: risultato, il sistema diceva
    # "17 eventi in attesa di risposta" mentre Michele non aveva ricevuto nulla.
    # Meglio fallire rumorosamente — e la busta che RESTA è l'allarme.
    if ok == 0:
        print("🛑 Nessun messaggio inviato: NON salvo la mappa e NON cancello la busta.\n"
              f"   La busta resta in {busta_path}: finché è lì, l'invio non è riuscito.",
              file=sys.stderr)
        return 1

    percorso = salva_mappa_giro(busta)
    aggiorna_stato_mac(busta["giro_id"])
    busta_path.unlink()
    print(f"Giro {busta['giro_id']}: mappa salvata in {percorso} "
          f"({len(busta.get('eventi', []))} eventi). Busta spedita e rimossa.")

    if err:
        # I pulsanti già arrivati ESISTONO e Michele li premerà: la mappa va
        # salvata comunque (decisione Q4 del ticket 07), ma lui deve sapere che
        # la lista è monca — se no crede di aver visto tutto.
        avviso = (f"⚠️ SMH — giro {busta['giro_id']}: la lista che hai ricevuto è "
                  f"INCOMPLETA. {err} messaggi su {len(messaggi)} non sono partiti. "
                  f"Le risposte che dai sui pulsanti arrivati valgono comunque.")
        manda_messaggio(avviso, token=token, chat_id=chat_id)
        print(f"⚠️ {err} messaggi non inviati: la lista su Telegram è INCOMPLETA.",
              file=sys.stderr)
        return 3
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)

    pp = sub.add_parser("prepara", help="scrive la busta (NON serve il token)")
    pp.add_argument("--events", required=True, help="JSON array degli eventi")
    pp.add_argument("--summary", default="", help="riga di riepilogo opzionale")
    pp.add_argument("--prova", action="store_true",
                    help="giro di collaudo: giro_id con prefisso PROVA-")

    pi = sub.add_parser("invia", help="spedisce la busta (l'unico passo col token)")
    pi.add_argument("--busta", default="", help=f"percorso busta (default {BUSTA})")

    args = p.parse_args()
    return prepara(args) if args.comando == "prepara" else invia(args)


if __name__ == "__main__":
    sys.exit(main())
