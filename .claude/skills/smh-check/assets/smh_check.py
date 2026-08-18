#!/usr/bin/env python3
"""
smh_check.py — parte MECCANICA del servizio di controllo pre-pubblicazione (/smh-check).

SOLA LETTURA: non pubblica, non modifica, non sposta nulla. Prepara un DOSSIER per ogni
"busta" in coda (i JSON in posts/ del repo sanmarinohappens) con i fatti calcolabili in
automatico. Claude poi COMPLETA il controllo guardando le IMMAGINI (vision) e incrociando
le fonti — vedi SKILL.md. Il vero errore da intercettare (dati stantii SULL'immagine) si
vede solo aprendo il PNG, cosa che uno script non sa fare: per questo la parte "occhio" la
fa Claude, questo script gli apparecchia i dati intorno.

Cosa calcola (deterministico, senza rete):
  - elenco buste: JSON + PNG, tipo, data_pubblicazione, titolo, caption
  - giorno della settimana (IT) della data_pubblicazione e di OGNI data trovata nella caption
    -> serve a confrontare col giorno STAMPATO sull'immagine (che lo script non legge)
  - termini di PREZZO / gratuita' nella caption (stessa regola-equita' di publish.py)
  - righe delle FONTI di verita' (ultimo file verificato + master + aggregati) che citano il
    titolo dell'evento -> cosi' Claude vede subito luogo/ora "giusti" da confrontare

Uso:
  python3 smh_check.py                      # dossier di tutta la coda
  python3 smh_check.py --queue <dir>        # coda diversa
  python3 smh_check.py --project <dir>      # cartella progetto (dove sta dati/)
  python3 smh_check.py --telegram "<testo>" # invia il referto finale su Telegram (sola utilita')
"""

import os
import re
import sys
import json
import glob
import argparse
from pathlib import Path
from datetime import datetime

# --- Percorsi (ricavati dalla posizione dello script, con override via argomenti/env) ---
# .../San Marino Happens/.claude/skills/smh-check/assets/smh_check.py -> parents[4] = progetto
# Il progetto STESSO è un clone di sanmarinohappens (ha una propria posts/): la coda va
# letta da lì, non da un secondo clone hardcoded altrove (bug trovato il 26/07 — quel
# clone duplicato era fermo indietro di un commit, quindi poteva non vedere le buste
# appena copiate nella cartella di lavoro vera).
PROJECT_DEFAULT = Path(__file__).resolve().parents[4]
QUEUE_DEFAULT = PROJECT_DEFAULT / 'posts'
SECRETS_TELEGRAM = PROJECT_DEFAULT / '.claude' / 'secrets' / 'telegram.json'

GIORNI_IT = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']

# Termini di prezzo/gratuita' vietati (stessa regola di publish.py: regola equita').
PREZZI_PATTERN = re.compile(
    r'€'
    r'|\bgratis\b'
    r'|\bgratuit[oaie]\b'
    r'|\bgratuitamente\b'
    r'|\ba\s+pagamento\b'
    r'|\bingresso\s+(?:libero|gratuito|gratis)\b'
    r'|\bentrata\s+(?:libera|gratuita|gratis)\b'
    r'|\bprezzo\b|\bprezzi\b|\bbigliett[oi]\b|\bcosto\b|\bcosti\b',  # extra: /smh-check e' piu' severo di publish.py
    re.IGNORECASE,
)

# Date nella caption: "14/07/2026", "14/07", "18–19/07" (prende la prima del range).
DATA_PATTERN = re.compile(r'\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b')

# Parole poco distintive da NON usare per cercare l'evento nelle fonti.
STOPWORDS = {
    'conference', 'league', 'summer', 'vibes', 'concert', 'concerto', 'band', 'post',
    'giornaliero', 'della', 'delle', 'degli', 'sammarinese', 'repubblica', 'marino',
    'stadium', 'edizione', 'serata', 'serate', 'live', 'tour', 'festival', 'ritorno',
    'turno', 'preliminare', 'gara', 'vs', 'contro', 'san', 'una',
    # generiche/temporali (facevano rumore nel grep delle fonti)
    'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto',
    'settembre', 'ottobre', 'novembre', 'dicembre', 'storie', 'storia', 'weekend',
    'settimana', 'settimanale', 'mensile', 'questo', 'questa', 'eventi', 'evento', 'giorno',
}


def carica_secret_telegram():
    try:
        with open(SECRETS_TELEGRAM, 'r', encoding='utf-8') as f:
            d = json.load(f)
        return d.get('bot_token') or d.get('token'), d.get('chat_id')
    except (OSError, json.JSONDecodeError):
        return None, None


def invia_telegram(testo):
    """Invia il referto su Telegram con `curl`. Non e' un controllo, e' solo comodita'
    per far arrivare il referto sul telefono di Michele.

    ⚠️ NON usare urllib: su questo Mac la verifica del certificato fallisce
    (`self-signed certificate in certificate chain`) e l'invio non parte mai.
    E' lo stesso bug che teneva muto `telegram-giro.py` (bug 9 del 27/07/2026) e che
    qui era rimasto: scoperto dal vivo il 27/07 sera, provando a mandare un referto.
    `curl` invece funziona. Vedi memoria `reference_telegram_urllib_ssl`."""
    import subprocess
    token, chat_id = carica_secret_telegram()
    if not token or not chat_id:
        print("Telegram non configurato (manca .claude/secrets/telegram.json): referto non inviato.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = subprocess.run(
            ['curl', '-s', '-X', 'POST', url,
             '-d', f'chat_id={chat_id}',
             '--data-urlencode', f'text={testo}'],
            capture_output=True, text=True, timeout=30)
        risposta = json.loads(r.stdout or '{}')
        if not risposta.get('ok'):
            print(f"Errore invio Telegram: {str(risposta)[:200]}")
            return False
        return True
    except Exception as e:  # noqa: BLE001 (utilita', non deve mai far crashare il controllo)
        print(f"Errore invio Telegram: {e}")
        return False


def giorno_it(d):
    return GIORNI_IT[d.weekday()]


def date_dalla_caption(caption, anno_default):
    """Ritorna una lista di (testo_data, giorno_settimana) per ogni data trovata."""
    fuori = []
    visti = set()
    for m in DATA_PATTERN.finditer(caption or ''):
        g, mth, y = m.group(1), m.group(2), m.group(3)
        anno = int(y) if y else anno_default
        try:
            d = datetime(anno, int(mth), int(g)).date()
        except ValueError:
            continue
        chiave = (d.day, d.month, d.year)
        if chiave in visti:
            continue
        visti.add(chiave)
        etichetta = m.group(0)
        fuori.append((etichetta, giorno_it(d)))
    return fuori


def prezzi_in(testo):
    trovati = []
    for m in PREZZI_PATTERN.finditer(testo or ''):
        t = m.group(0).strip()
        if t.lower() not in [x.lower() for x in trovati]:
            trovati.append(t)
    return trovati


def token_titolo(titolo):
    """Parole distintive del titolo, da cercare nelle fonti."""
    parole = re.findall(r"[A-Za-zÀ-ÿ']{4,}", titolo or '')
    out = []
    for p in parole:
        if p.lower() in STOPWORDS:
            continue
        out.append(p)
    return out or parole  # se filtrando resta vuoto, tieni tutto


def ultimo_verificato(project):
    files = sorted(glob.glob(str(project / 'dati' / 'eventi' / 'verificati' / 'eventi-verificati-*.md')))
    return Path(files[-1]) if files else None


def righe_fonti(project, tokens):
    """Ritorna righe (etichetta_fonte, testo_riga) delle fonti che citano un token del titolo.
    Fonti: ultimo verificato, master, aggregati. Cap per non allagare l'output."""
    fonti = []
    uv = ultimo_verificato(project)
    if uv:
        fonti.append(('verificato', uv))
    master = project / 'dati' / 'calendario' / 'master.md'
    if master.exists():
        fonti.append(('master', master))
    for agg in sorted(glob.glob(str(project / 'dati' / 'post' / 'aggregati-*.md'))):
        fonti.append(('aggregati', Path(agg)))

    tok_lower = [t.lower() for t in tokens]
    risultati = []
    for etichetta, path in fonti:
        try:
            testo = path.read_text(encoding='utf-8')
        except OSError:
            continue
        viste = 0
        for riga in testo.splitlines():
            rl = riga.lower()
            if any(t in rl for t in tok_lower):
                riga_pulita = riga.strip()
                if riga_pulita and len(riga_pulita) > 3:
                    risultati.append((etichetta, riga_pulita[:200]))
                    viste += 1
            if viste >= 4:  # bastano poche righe per fonte
                break
    return risultati



def handle_attesi(project, titolo, caption):
    """Gli handle ATTIVI del registro che risultano pertinenti a questo evento.
    Si confrontano gli alias del registro col titolo e con la caption: se un alias compare,
    quell'organizzatore c'entra, e allora il post dovrebbe portarne il tag."""
    reg = project / 'dati' / 'handle-organizzatori.json'
    if not reg.exists():
        return []
    try:
        voci = json.loads(reg.read_text()).get('voci', [])
    except Exception:
        return []
    testo = f"{titolo} {caption or ''}".lower()
    trovati = []
    for v in voci:
        if v.get('stato') != 'attivo' or not v.get('instagram'):
            continue
        for a in v.get('alias', []) + [v.get('nome', '')]:
            a = (a or '').strip().lower()
            # alias corti (<4) esclusi: darebbero falsi positivi a raffica
            if len(a) >= 4 and a in testo:
                trovati.append(v['instagram'])
                break
    return sorted(set(trovati))


def leggi_buste(queue):
    buste = []
    for jf in sorted(Path(queue).glob('*.json')):
        try:
            meta = json.loads(jf.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as e:
            buste.append({'json': jf, 'errore': f"JSON illeggibile: {e}"})
            continue
        # immagini: campo 'immagini' oppure il PNG gemello
        lista = meta.get('immagini')
        if isinstance(lista, list) and lista:
            imgs = [Path(queue) / str(n) for n in lista]
        else:
            imgs = [jf.with_suffix('.png')]
        buste.append({'json': jf, 'meta': meta, 'immagini': imgs})
    return buste


def stampa_dossier(queue, project):
    buste = leggi_buste(queue)
    if not buste:
        print(f"Nessuna busta in coda ({queue}).")
        return
    print(f"╔═══ DOSSIER CONTROLLO — {len(buste)} buste in coda ═══╗")
    print(f"coda:    {queue}")
    print(f"progetto:{project}")
    uv = ultimo_verificato(project)
    print(f"verificato piu' recente: {uv.name if uv else '(nessuno)'}")
    print("(Questo e' il lavoro MECCANICO. Ora Claude apre ogni PNG e completa i controlli — vedi SKILL.md.)\n")

    for b in buste:
        jf = b['json']
        print("═" * 70)
        print(f"BUSTA: {jf.name}")
        if 'errore' in b:
            print(f"  ❌ {b['errore']}  → busta ANOMALA (publish.py la salterebbe)")
            continue
        meta = b['meta']
        tipo = (meta.get('tipo') or 'giornaliero').strip().lower()
        titolo = meta.get('titolo_evento', jf.stem)
        caption = meta.get('caption', '') or ''
        dp_raw = meta.get('data_pubblicazione', '')
        try:
            dp = datetime.strptime(dp_raw, '%Y-%m-%d').date()
            dp_g = giorno_it(dp)
            anno = dp.year
        except (ValueError, TypeError):
            dp, dp_g, anno = None, '(data non valida!)', 2026

        print(f"  tipo: {tipo}   |   data_pubblicazione: {dp_raw} ({dp_g})")
        print(f"  titolo: {titolo}")
        print(f"  immagini: {', '.join(p.name for p in b['immagini'])}")
        mancanti = [p.name for p in b['immagini'] if not p.exists()]
        if mancanti:
            print(f"  ⚠️ PNG mancanti: {', '.join(mancanti)}")

        # giorno-settimana delle date nella caption (da confrontare col giorno stampato)
        if tipo != 'storia' and caption:
            dc = date_dalla_caption(caption, anno)
            if dc:
                print("  date nella caption → giorno reale (Python):")
                for et, g in dc:
                    print(f"     {et} = {g}")

        # prezzi
        if tipo == 'storia':
            print("  prezzi caption: (storia, nessuna caption)")
        else:
            pz = prezzi_in(caption)
            print(f"  PREZZI in caption: {'⚠️ ' + ', '.join(pz) if pz else 'nessuno ✅'}")

        # TAG mancanti: un post senza tag non e' un errore in se' (l'organizzatore puo' non
        # essere nel registro), ma se il registro lo conosce ed e' `attivo` allora e' un tag
        # PERSO. Aggiunto il 27/07/2026: il post del 27/07 (Fluxo) e' uscito senza tag e se
        # n'e' accorto solo Michele guardando Instagram — nessun controllo lo vedeva.
        if tipo in ('giornaliero', 'storia'):
            tags = meta.get('user_tags') or {}
            n_tag = sum(len(v) for v in tags.values()) if isinstance(tags, dict) else 0
            attesi = handle_attesi(project, titolo, caption)
            if n_tag:
                print(f"  TAG: {n_tag} presenti ✅")
            elif attesi:
                print(f"  TAG: ❌ NESSUNO, ma il registro conosce → {', '.join('@'+h for h in attesi)}"
                      f"  (tag perso: aggiungerlo alla busta)")
            else:
                print("  TAG: nessuno — nessun organizzatore noto nel registro per questo evento "
                      "(se ne esiste uno, va prima registrato: Step 4-bis di /smh-verifica)")

        # fonti di verita'
        righe = righe_fonti(project, token_titolo(titolo))
        if righe:
            print("  FONTI di verita' (righe che citano il titolo — controlla luogo/ora qui):")
            for et, riga in righe:
                print(f"     [{et}] {riga}")
        else:
            print("  FONTI: nessuna riga trovata per il titolo → verifica a mano il file verificato/master.")

        print("  → CLAUDE (vision): apri il/i PNG, trascrivi GIORNO·DATA·TITOLO·LUOGO·ORA + eventuali")
        print("    PREZZI stampati; confronta con le FONTI e con la caption; classifica ✅/⚠️/❌.")
    print("═" * 70)


def main():
    ap = argparse.ArgumentParser(description="Dossier meccanico per il controllo pre-pubblicazione /smh-check.")
    ap.add_argument('--queue', default=os.getenv('SMH_QUEUE', str(QUEUE_DEFAULT)))
    ap.add_argument('--project', default=os.getenv('SMH_PROJECT', str(PROJECT_DEFAULT)))
    ap.add_argument('--telegram', metavar='TESTO', help="Invia il referto finale su Telegram e basta.")
    args = ap.parse_args()

    if args.telegram is not None:
        ok = invia_telegram(args.telegram)
        print("Referto inviato su Telegram ✅" if ok else "Invio Telegram fallito.")
        return

    stampa_dossier(Path(args.queue), Path(args.project))


if __name__ == '__main__':
    main()
