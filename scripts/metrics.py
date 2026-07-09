#!/usr/bin/env python3
"""
Raccoglitore metriche SETTIMANALE di @sanmarinohappens (v1).

Cosa fa, in parole semplici:
1. Chiede a Instagram i numeri di oggi (follower, post) + gli insight
   (reach, visite profilo, interazioni) e li salva.
2. Li aggiunge come UNA riga settimanale nel database permanente
   metriche/storico.json (che cresce ogni settimana e non si cancella mai).
3. Calcola la crescita follower rispetto alla settimana prima (il segnale
   piu' pulito quando l'account e' piccolo).
4. Rigenera la tabella leggibile metriche/metriche-social.md (settimane + mesi).
5. Manda una notifica Telegram con i numeri della settimana.
6. Controlla la scadenza del token Instagram e avvisa su Telegram se sta
   per scadere (il token serve sia alle metriche sia alla pubblicazione).

SICUREZZA: e' di SOLA LETTURA verso Instagram (non pubblica nulla). Non stampa
mai il token. Usa gli stessi Secret gia' presenti su GitHub.

NOTA TECNICA (onesta): gli insight reach/visite/interazioni sono richiesti con
la finestra 'days_28' (28 giorni), l'unica confermata funzionante nella prova
del 09/07. E' quindi una finestra "mobile" (si sovrappone di settimana in
settimana): buona per il TREND. Il numero settimanale davvero pulito e' la
CRESCITA FOLLOWER, che qui e' esatta perche' i follower sono una fotografia.
Dopo la prima run vera valuteremo se passare reach a una finestra 7 giorni.
"""

import os
import json
import requests
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TOKEN = os.getenv('INSTAGRAM_TOKEN')
USER_ID = os.getenv('INSTAGRAM_USER_ID')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# Solo per test: forza la data "di oggi" invece dell'orologio reale.
TEST_DATE = os.getenv('TEST_DATE')

BASE = 'https://graph.instagram.com'
TZ = ZoneInfo('Europe/San_Marino')

STORICO = Path('metriche/storico.json')
TABELLA = Path('metriche/metriche-social.md')

MESI_IT = ['', 'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
           'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']


def oggi():
    if TEST_DATE:
        return datetime.strptime(TEST_DATE, '%Y-%m-%d').date()
    return datetime.now(TZ).date()


# ---------------------------------------------------------------------------
# Lettura dati da Instagram (robusta: se una chiamata fallisce, salva null e
# va avanti, cosi' la run non si blocca mai per un singolo dato mancante).
# ---------------------------------------------------------------------------

def _get(path, params):
    params = dict(params)
    params['access_token'] = TOKEN
    r = requests.get(f'{BASE}/{path}', params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def leggi_profilo():
    """Fotografia di oggi: follower, n. post, chi seguiamo."""
    try:
        d = _get(USER_ID, {'fields': 'username,followers_count,media_count,follows_count'})
        return {
            'username': d.get('username'),
            'follower': d.get('followers_count'),
            'post_totali': d.get('media_count'),
            'seguiti': d.get('follows_count'),
        }
    except Exception as e:
        print(f'  ⚠️  profilo non letto: {e}')
        return {'username': None, 'follower': None, 'post_totali': None, 'seguiti': None}


def leggi_insight():
    """Insight account (finestra mobile 28 giorni). Ogni metrica indipendente."""
    metriche = ['reach', 'profile_views', 'accounts_engaged', 'total_interactions']
    risultati = {}
    for m in metriche:
        try:
            d = _get(f'{USER_ID}/insights',
                     {'metric': m, 'period': 'days_28', 'metric_type': 'total_value'})
            valore = None
            for voce in d.get('data', []):
                tv = voce.get('total_value') or {}
                valore = tv.get('value')
            risultati[m] = valore
        except Exception as e:
            print(f'  ⚠️  insight {m} non letto: {e}')
            risultati[m] = None
    return risultati


# ---------------------------------------------------------------------------
# Database storico.json
# ---------------------------------------------------------------------------

def carica_storico():
    if STORICO.exists():
        with open(STORICO, encoding='utf-8') as f:
            return json.load(f)
    # Struttura iniziale se il file non esistesse.
    return {
        'meta': {
            'descrizione': 'Archivio permanente metriche @sanmarinohappens. Una riga per settimana.',
            'account': '@sanmarinohappens',
            'ig_user_id': USER_ID,
        },
        'token': {
            'rilasciato_il': oggi().isoformat(),
            'validita_giorni': 60,
            'nota': 'Aggiorna "rilasciato_il" ogni volta che rigeneri il token IG su GitHub.',
        },
        'settimane': [],
    }


def salva_storico(dati):
    STORICO.parent.mkdir(parents=True, exist_ok=True)
    with open(STORICO, 'w', encoding='utf-8') as f:
        json.dump(dati, f, indent=2, ensure_ascii=False)
        f.write('\n')


def aggiorna_settimane(dati, profilo, insight):
    """Aggiunge (o sostituisce, se rilanciato lo stesso giorno) la riga di oggi."""
    settimane = dati.setdefault('settimane', [])
    data_str = oggi().isoformat()

    # follower della lettura precedente (per il delta), saltando la riga di oggi se gia' presente.
    precedenti = [s for s in settimane if s.get('data_lettura') != data_str]
    follower_prec = precedenti[-1]['follower'] if precedenti and precedenti[-1].get('follower') is not None else None
    follower_oggi = profilo.get('follower')
    delta = (follower_oggi - follower_prec) if (follower_oggi is not None and follower_prec is not None) else None

    riga = {
        'data_lettura': data_str,
        'follower': follower_oggi,
        'follower_delta': delta,
        'seguiti': profilo.get('seguiti'),
        'post_totali': profilo.get('post_totali'),
        'reach_28g': insight.get('reach'),
        'profile_views_28g': insight.get('profile_views'),
        'accounts_engaged_28g': insight.get('accounts_engaged'),
        'total_interactions_28g': insight.get('total_interactions'),
    }

    # Sostituisci la riga se oggi e' gia' stato letto, altrimenti aggiungi.
    settimane[:] = [s for s in settimane if s.get('data_lettura') != data_str]
    settimane.append(riga)
    settimane.sort(key=lambda s: s['data_lettura'])
    return riga


# ---------------------------------------------------------------------------
# Tabella leggibile metriche-social.md (rigenerata da storico.json)
# ---------------------------------------------------------------------------

def _n(v):
    return str(v) if v is not None else 'n.d.'


def _delta(v):
    if v is None:
        return ''
    if v > 0:
        return f' (+{v})'
    if v < 0:
        return f' ({v})'
    return ' (=)'


def riepilogo_mensile(settimane):
    """Per ogni mese: ultima lettura del mese = fotografia di fine mese."""
    per_mese = {}
    for s in settimane:
        mese = s['data_lettura'][:7]  # AAAA-MM
        per_mese[mese] = s  # sovrascrive: resta l'ultima del mese (ordinate crescenti)
    righe = []
    mesi_ordinati = sorted(per_mese)
    for i, mese in enumerate(mesi_ordinati):
        s = per_mese[mese]
        # crescita follower nel mese = ultima del mese - ultima del mese precedente
        cresc = None
        if i > 0:
            prec = per_mese[mesi_ordinati[i - 1]]
            if s.get('follower') is not None and prec.get('follower') is not None:
                cresc = s['follower'] - prec['follower']
        anno, mm = mese.split('-')
        etichetta = f'{MESI_IT[int(mm)]} {anno}'
        righe.append((etichetta, s, cresc))
    return righe


def scrivi_tabella(dati):
    settimane = dati.get('settimane', [])
    token = dati.get('token', {})
    ultimo = settimane[-1] if settimane else None

    stato_token = ''
    if token.get('rilasciato_il'):
        scad = date.fromisoformat(token['rilasciato_il']) + timedelta(days=token.get('validita_giorni', 60))
        giorni = (scad - oggi()).days
        stato_token = (f"- **Token Instagram**: rilasciato il {token['rilasciato_il']}, "
                       f"scadenza stimata **{scad.isoformat()}** (~{giorni} giorni). "
                       f"Alla scadenza si ferma sia la raccolta metriche sia la pubblicazione.\n")

    out = []
    out.append('# Registro metriche social — @sanmarinohappens\n')
    out.append('> ⚙️ **File generato automaticamente** dal raccoglitore settimanale '
               '(`scripts/metrics.py`, ogni lunedì). Non modificarlo a mano: viene riscritto.\n')
    out.append('> La fonte dei dati è il database permanente `metriche/storico.json`.\n')
    out.append('\n⚠️ Regola del progetto: **mai inventare numeri**. Dove il dato manca → `n.d.`\n')
    if stato_token:
        out.append('\n## Stato token\n')
        out.append(stato_token)

    out.append('\n## Andamento settimanale (ultime 12 letture)\n')
    out.append('| Lettura | Follower | Cresc. sett. | Post | Reach 28g | Visite prof. 28g | Interazioni 28g |\n')
    out.append('|---------|----------|--------------|------|-----------|------------------|-----------------|\n')
    for s in settimane[-12:]:
        out.append('| {d} | {f}{dl} | {dl2} | {p} | {r} | {v} | {i} |\n'.format(
            d=s['data_lettura'],
            f=_n(s.get('follower')),
            dl='',
            dl2=_delta(s.get('follower_delta')).strip() or '—',
            p=_n(s.get('post_totali')),
            r=_n(s.get('reach_28g')),
            v=_n(s.get('profile_views_28g')),
            i=_n(s.get('total_interactions_28g')),
        ))

    out.append('\n## Riepilogo mensile (fotografia di fine mese)\n')
    out.append('| Mese | Follower fine mese | Crescita mese | Reach 28g | Interazioni 28g |\n')
    out.append('|------|--------------------|---------------|-----------|-----------------|\n')
    for etichetta, s, cresc in riepilogo_mensile(settimane):
        out.append('| {m} | {f} | {c} | {r} | {i} |\n'.format(
            m=etichetta,
            f=_n(s.get('follower')),
            c=(f'+{cresc}' if (cresc is not None and cresc >= 0) else (str(cresc) if cresc is not None else '—')),
            r=_n(s.get('reach_28g')),
            i=_n(s.get('total_interactions_28g')),
        ))

    out.append('\nLegenda: *Reach 28g* = account unici raggiunti negli ultimi 28 giorni (finestra mobile) · '
               '*Interazioni* = like + commenti + salvataggi + condivisioni · '
               '*Cresc. sett.* = follower guadagnati/persi dalla lettura precedente.\n')
    out.append('\n> Nota Facebook: questa raccolta automatica copre **solo Instagram** (l’API disponibile è quella IG). '
               'I numeri Facebook, se servono, vanno letti a mano da Meta Business Suite.\n')

    TABELLA.parent.mkdir(parents=True, exist_ok=True)
    with open(TABELLA, 'w', encoding='utf-8') as f:
        f.write(''.join(out))


# ---------------------------------------------------------------------------
# Telegram: notifica settimanale + promemoria token
# ---------------------------------------------------------------------------

def notifica_telegram(testo):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print('(Telegram non configurato: notifica saltata)')
        return
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    try:
        requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': testo}, timeout=10)
    except requests.RequestException as e:
        print(f'Errore notifica Telegram: {e}')


def controlla_token(dati):
    """Se il token scade entro 10 giorni, manda un avviso su Telegram."""
    token = dati.get('token', {})
    if not token.get('rilasciato_il'):
        return
    scad = date.fromisoformat(token['rilasciato_il']) + timedelta(days=token.get('validita_giorni', 60))
    giorni = (scad - oggi()).days
    if giorni <= 10:
        notifica_telegram(
            f'⚠️ Token Instagram in scadenza tra {giorni} giorni (stimata {scad.isoformat()}).\n\n'
            f'Quando scade si fermano SIA le metriche SIA la pubblicazione. '
            f'Rigenera il token e aggiorna il Secret INSTAGRAM_TOKEN su GitHub, '
            f'poi correggi "rilasciato_il" in metriche/storico.json.'
        )
        print(f'  ⚠️  avviso token inviato ({giorni} giorni alla scadenza)')


def main():
    if not TOKEN or not USER_ID:
        print('Manca INSTAGRAM_TOKEN o INSTAGRAM_USER_ID. Stop.')
        return

    print(f'Lettura metriche del {oggi().isoformat()} (account {USER_ID})')

    profilo = leggi_profilo()
    insight = leggi_insight()

    dati = carica_storico()
    riga = aggiorna_settimane(dati, profilo, insight)
    salva_storico(dati)
    scrivi_tabella(dati)

    print('  riga salvata:', json.dumps(riga, ensure_ascii=False))

    # Notifica settimanale con i numeri chiave.
    mese_it = f'{MESI_IT[oggi().month]} {oggi().year}'
    notifica_telegram(
        f'📊 Metriche settimana {oggi().isoformat()} registrate\n\n'
        f'👥 Follower: {_n(riga.get("follower"))}{_delta(riga.get("follower_delta"))}\n'
        f'📈 Reach (28g): {_n(riga.get("reach_28g"))}\n'
        f'👀 Visite profilo (28g): {_n(riga.get("profile_views_28g"))}\n'
        f'❤️ Interazioni (28g): {_n(riga.get("total_interactions_28g"))}\n'
        f'📝 Post totali: {_n(riga.get("post_totali"))}\n\n'
        f'Archivio aggiornato: metriche/metriche-social.md ({mese_it}).'
    )

    controlla_token(dati)
    print('Fatto.')


if __name__ == '__main__':
    main()
