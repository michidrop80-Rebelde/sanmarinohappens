#!/usr/bin/env python3
"""
Invia il riepilogo del giro SMH su Telegram con pulsanti inline.

Uso:
  python3 telegram-giro.py --secrets .claude/secrets/telegram.json --events '[...]'

--events: JSON array di oggetti:
  [
    {"id": "09", "titolo": "Sergio Caputo", "tipo": "nuovo", "data": "03/07", "luogo": "Campo Bruno Reffi", "url": "https://..."},
    ...
  ]

tipos validi: "nuovo" | "modificato" | "cancellato" | "dubbio"

L'icona viene scelta in base al tipo:
  nuovo       -> 🆕
  modificato  -> ✏️
  cancellato  -> 🗑
  dubbio      -> ⚠️
"""

import sys
import json
import argparse
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


ICONE = {
    "nuovo": "🆕",
    "modificato": "✏️",
    "cancellato": "🗑",
    "dubbio": "⚠️",
}


def send(token: str, chat_id: str, text: str, reply_markup=None) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    # ⚠️ Si invia con `curl`, NON con urllib (corretto il 27/07/2026).
    # Perche': su questo Mac urllib fallisce la verifica del certificato
    # ("self-signed certificate in certificate chain") e NESSUN messaggio parte,
    # mentre curl usa il portachiavi di sistema e funziona. Era un guasto silenzioso:
    # lo script diceva "errore di rete" in una riga sola e il giro proseguiva, quindi
    # Michele restava senza i pulsanti di approvazione senza che nessuno lo notasse.
    data = json.dumps(payload)
    try:
        esito = subprocess.run(
            ["curl", "-s", "--max-time", "20", "-X", "POST", url,
             "-H", "Content-Type: application/json", "-d", data],
            capture_output=True, text=True, check=False,
        )
        if esito.returncode != 0:
            print(f"  ❌ curl fallito (codice {esito.returncode}): {esito.stderr.strip()}",
                  file=sys.stderr)
            return False
        result = json.loads(esito.stdout or "{}")
        if not result.get("ok"):
            print(f"  ⚠️ Telegram ha rifiutato: {result}", file=sys.stderr)
            return False
        return True
    except (json.JSONDecodeError, OSError) as e:
        print(f"  ❌ Invio non riuscito: {e}", file=sys.stderr)
        return False


def chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


# Dove vivono le mappe numero→evento, una per giro.
# ⚠️ NON in .claude/secrets/: backup-cervello.sh esclude quella cartella apposta
# (contiene token), quindi finche' la mappa stava li' non aveva ne' storico ne'
# backup — ed e' esattamente cosi' che le 6 approvazioni dell'08/08/2026 sono
# diventate non piu' riconducibili a nessun evento.
CARTELLA_PENDING = Path(__file__).resolve().parent.parent.parent / "dati" / "telegram" / "pending"


def nuovo_giro_id():
    """Identita' del giro: AAAAMMGG-HHMM in UTC. Basta al minuto — due giri nello
    stesso minuto non esistono, e il formato resta corto per stare nei 64 byte di
    callback_data."""
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")


def callback_data(azione, giro_id, ev_id):
    """Il dato che viaggia dentro il pulsante.

    Prima era `approve_01`, e `01` significava "il primo evento DELL'ULTIMO GIRO".
    Ma i pulsanti dei messaggi vecchi restano cliccabili per sempre: premuto oggi,
    un pulsante di tre giri fa diceva `01` come quello di stamattina. Con il giro
    dentro, ogni pulsante dice da solo a quale lista appartiene."""
    return f"{azione}_{giro_id}-{ev_id}"


def salva_mappa_giro(giro_id, eventi):
    """Scrive dati/telegram/pending/<giro_id>.json e ritorna il percorso.
    Un file per giro: niente slot unico da sovrascrivere."""
    CARTELLA_PENDING.mkdir(parents=True, exist_ok=True)
    percorso = CARTELLA_PENDING / f"{giro_id}.json"
    percorso.write_text(json.dumps({
        "giro_id": giro_id,
        "sent_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
    }, ensure_ascii=False, indent=2))
    return percorso


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--secrets", required=True, help="Path to telegram.json")
    parser.add_argument("--events", required=True, help="JSON array of events")
    parser.add_argument("--summary", default="", help="Optional summary line")
    args = parser.parse_args()

    with open(args.secrets) as f:
        secrets = json.load(f)
    token = secrets["bot_token"]
    chat_id = str(secrets["chat_id"])

    events = json.loads(args.events)
    giro_id = nuovo_giro_id()

    # Count by type
    counts = {"nuovo": 0, "modificato": 0, "cancellato": 0, "dubbio": 0}
    for e in events:
        t = e.get("tipo", "dubbio").lower()
        if t in counts:
            counts[t] += 1

    today = datetime.now(timezone.utc).strftime("%d/%m/%Y")

    # Messaggio 1: riepilogo numerico
    summary_text = (
        f"🟢 <b>SMH — giro del {today}</b>\n\n"
        f"🆕 Nuovi: {counts['nuovo']}\n"
        f"✏️ Modificati: {counts['modificato']}\n"
        f"🗑 Potenzialmente cancellati: {counts['cancellato']}\n"
        f"⚠️ Dubbi: {counts['dubbio']}\n"
    )
    if args.summary:
        summary_text += f"\n{args.summary}\n"
    if events:
        summary_text += "\nSeguono i dettagli con i pulsanti 👇"
    else:
        summary_text += "\n✅ Nessuna novità questa settimana."

    ok = send(token, chat_id, summary_text)
    print(f"Messaggio riepilogo: {'✅' if ok else '❌'}")

    if not events:
        return

    # Messaggi successivi: blocchi da 3 con pulsanti
    sent_ok = 0
    sent_err = 0
    dubbi_senza_spiegazione = []
    for block in chunk(events, 3):
        lines = []
        keyboard_rows = []
        for ev in block:
            icona = ICONE.get(ev.get("tipo", "dubbio").lower(), "⚠️")
            titolo = ev.get("titolo", "?")
            data = ev.get("data", "")
            luogo = ev.get("luogo", "")
            url = ev.get("url", "")
            ev_id = ev.get("id", "?")

            line = f"{icona} <b>{titolo}</b>"
            if data:
                line += f"\n📅 {data}"
            if luogo:
                line += f" · 📍 {luogo}"
            if url:
                line += f"\n🔗 {url}"

            # ⚠️ Un dubbio DEVE dire qual e' il problema (regola di Michele, 10/08/2026:
            # «non basta il solo segnale di pericolo»). Un ⚠️ nudo sposta la decisione su
            # di lui senza dargli l'informazione per deciderla: preme ✅ per non bloccare
            # la catena e il dubbio entra nel sistema come un dato verificato — e' cosi'
            # che «Mi Gusto» (date 2025) e la chiusura dell'11/08 della Sagra della
            # Tagliatella (dati 2024) sono arrivate a un giorno dalla pubblicazione.
            dubbio = (ev.get("dubbio") or "").strip()
            serve = (ev.get("serve") or "").strip()
            if dubbio:
                line += f"\n⚠️ Cosa non torna: {dubbio}"
            elif ev.get("tipo", "").lower() == "dubbio":
                # Meglio un buco dichiarato che un ⚠️ muto: Michele vede che manca la
                # spiegazione e sa di doverla chiedere, invece di approvare al buio.
                line += ("\n⚠️ <b>Dubbio non spiegato</b> — chiedi a Claude cosa non torna "
                         "prima di premere ✅")
                dubbi_senza_spiegazione.append(f"{ev_id} {titolo}")
            if serve:
                line += f"\n👉 Per scioglierlo: {serve}"
            lines.append(line)

            short = titolo[:20] + "…" if len(titolo) > 20 else titolo
            keyboard_rows.append([
                {"text": f"✅ {short}",
                 "callback_data": callback_data("approve", giro_id, ev_id)},
                {"text": "❌", "callback_data": callback_data("reject", giro_id, ev_id)},
            ])

        text = "\n\n".join(lines)
        reply_markup = {"inline_keyboard": keyboard_rows}
        ok = send(token, chat_id, text, reply_markup)
        if ok:
            sent_ok += 1
        else:
            sent_err += 1

    print(f"Messaggi eventi: ✅ {sent_ok} inviati, ❌ {sent_err} errori")

    # ⚠️ Se NON e' partito niente, non si tocca lo stato (corretto il 27/07/2026).
    # Prima lo stato veniva salvato comunque: risultato, `telegram-state.json` diceva
    # "17 eventi in attesa di risposta" mentre Michele non aveva ricevuto nulla, e
    # l'agente di approvazione ci avrebbe creduto. Meglio fallire rumorosamente.
    if sent_ok == 0:
        print("🛑 Nessun messaggio inviato: NON aggiorno telegram-state.json.\n"
              "   L'approvazione non deve credere che ci sia qualcosa in attesa.",
              file=sys.stderr)
        sys.exit(1)
    if sent_err:
        print(f"⚠️ {sent_err} blocchi non inviati: la lista su Telegram e' INCOMPLETA.",
              file=sys.stderr)

    # La mappa numero→evento va in un file SUO, uno per giro.
    percorso_mappa = salva_mappa_giro(giro_id, events)

    # In telegram-state.json resta solo cio' che serve al polling (last_update_id) piu'
    # il puntatore all'ultimo giro. `pending_events` non si scrive piu': era uno slot
    # unico e il giro successivo lo sovrascriveva, facendo perdere la mappa delle
    # approvazioni non ancora elaborate (guasto dell'08/08/2026).
    state_path = args.secrets.replace("telegram.json", "telegram-state.json")
    try:
        with open(state_path) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}

    state["sent_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["ultimo_giro_id"] = giro_id
    state.pop("pending_events", None)
    state["_nota_pending"] = (
        "La mappa numero→evento NON sta piu' qui: sta in "
        "dati/telegram/pending/<giro_id>.json, un file per giro, versionato in git. "
        "Qui era uno slot solo e veniva sovrascritto a ogni giro."
    )
    with open(state_path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"Giro {giro_id}: mappa salvata in {percorso_mappa} ({len(events)} eventi)")

    # Un dubbio senza spiegazione e' un difetto del giro, non un dettaglio: Michele ha
    # ricevuto i pulsanti (meglio che niente) ma non puo' decidere. Si esce con codice
    # d'errore perche' chi ha lanciato il giro se ne accorga e completi la spiegazione.
    if dubbi_senza_spiegazione:
        print("🛑 " + str(len(dubbi_senza_spiegazione)) + " eventi marcati 'dubbio' SENZA "
              "il campo `dubbio`: " + ", ".join(dubbi_senza_spiegazione) + "\n"
              "   Michele non puo' decidere su un ⚠️ nudo (sua regola, 10/08/2026).\n"
              "   Aggiungi `dubbio` (e possibilmente `serve`) e rimanda quegli eventi.",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
