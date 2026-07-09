#!/usr/bin/env python3
"""
PROVA di sola lettura — NON pubblica niente, NON scrive niente.

Interroga l'API di Instagram per capire QUALI metriche ci restituisce oggi
per @sanmarinohappens. Stampa il risultato di ogni chiamata (stato + corpo)
cosi' vediamo cosa e' effettivamente disponibile prima di costruire la
raccolta automatica.

Sicurezza: NON stampa mai il token. Usa lo stesso INSTAGRAM_TOKEN /
INSTAGRAM_USER_ID gia' presenti nei GitHub Secrets.
"""

import os
import json
import requests

TOKEN = os.getenv('INSTAGRAM_TOKEN')
USER_ID = os.getenv('INSTAGRAM_USER_ID')
BASE = 'https://graph.instagram.com'


def chiama(descrizione, path, params):
    """Esegue una GET e stampa in modo leggibile cosa torna (senza il token)."""
    params = dict(params)
    params['access_token'] = TOKEN
    print('\n' + '=' * 60)
    print(f'PROVA: {descrizione}')
    print(f'  endpoint: {path}')
    safe = {k: v for k, v in params.items() if k != 'access_token'}
    print(f'  parametri: {safe}')
    try:
        r = requests.get(f'{BASE}/{path}', params=params, timeout=20)
        print(f'  stato HTTP: {r.status_code}')
        try:
            print('  risposta: ' + json.dumps(r.json(), indent=2, ensure_ascii=False))
        except ValueError:
            print('  risposta (testo): ' + r.text[:800])
    except requests.RequestException as e:
        print(f'  ERRORE di rete: {e}')


def main():
    if not TOKEN or not USER_ID:
        print('Manca INSTAGRAM_TOKEN o INSTAGRAM_USER_ID. Stop.')
        return

    print(f'Account in prova (user id): {USER_ID}')

    # 1) Dati base del profilo: follower, n. post, chi seguiamo.
    chiama(
        'Dati base profilo (follower, media, follows)',
        USER_ID,
        {'fields': 'username,followers_count,media_count,follows_count'},
    )

    # 2) Insight a livello di account, ultimi 30 giorni (metriche a valore totale).
    chiama(
        'Insight account 30 giorni (reach)',
        f'{USER_ID}/insights',
        {'metric': 'reach', 'period': 'days_28', 'metric_type': 'total_value'},
    )

    # 3) Altre metriche account comuni (potrebbero non essere tutte attive).
    chiama(
        'Insight account (profile_views, accounts_engaged, total_interactions)',
        f'{USER_ID}/insights',
        {'metric': 'profile_views,accounts_engaged,total_interactions',
         'period': 'days_28', 'metric_type': 'total_value'},
    )

    # 4) Elenco ultimi post (per poi leggere gli insight per singolo post).
    chiama(
        'Ultimi post pubblicati (id, tipo, data, caption breve)',
        f'{USER_ID}/media',
        {'fields': 'id,caption,media_type,timestamp,permalink', 'limit': 5},
    )

    print('\n' + '=' * 60)
    print('Fine prova. (Nessun dato scritto, nessun post pubblicato.)')


if __name__ == '__main__':
    main()
