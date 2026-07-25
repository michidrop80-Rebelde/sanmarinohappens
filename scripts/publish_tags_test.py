#!/usr/bin/env python3
"""
TEST OFFLINE dei tag utente Instagram — non tocca la rete, non pubblica niente,
non scrive niente. Si lancia con:  python3 scripts/publish_tags_test.py

Il python3 del Mac non ha 'requests', e comunque non vogliamo chiamate vere:
prima di importare publish.py mettiamo in sys.modules un finto modulo 'requests'
che registra le chiamate invece di eseguirle.
"""

import sys
import types
from pathlib import Path

# ---------------------------------------------------------------------------
# Finto 'requests': registra le POST e risponde quello che gli diciamo noi.
# ---------------------------------------------------------------------------
CHIAMATE = []          # ogni POST finisce qui: {'url':..., 'data':...}
RISPOSTE = []          # coda di risposte da dare, in ordine


class FintaRisposta:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


def finta_post(url, data=None, timeout=None, **kw):
    CHIAMATE.append({'url': url, 'data': dict(data or {})})
    if RISPOSTE:
        return RISPOSTE.pop(0)
    return FintaRisposta(200, {'id': 'CONTAINER_FINTO'})


def finta_get(url, params=None, timeout=None, **kw):
    return FintaRisposta(200, {'status_code': 'FINISHED'})


_fake = types.ModuleType('requests')
_fake.RequestException = Exception
_fake.post = finta_post
_fake.get = finta_get
sys.modules['requests'] = _fake

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish  # noqa: E402


# ---------------------------------------------------------------------------
# Mini-impalcatura di test (niente pytest: deve girare col python3 di sistema)
# ---------------------------------------------------------------------------
ESITI = []


def verifica(descrizione, condizione):
    ESITI.append((descrizione, bool(condizione)))
    print(('  OK   ' if condizione else '  FALLITO ') + descrizione)


def img(nome):
    """Path finto: a noi serve solo il .name."""
    return Path('/finta/cartella') / nome


# ---------------------------------------------------------------------------
# 1) Guardia: tag_anomalie
# ---------------------------------------------------------------------------
def test_guardia():
    print('\n[1] Guardia sui tag malformati')
    una = [img('20260725_Post giornaliero.png')]

    verifica('busta senza user_tags: nessun problema',
             publish.tag_anomalie({}, 'giornaliero', una) == [])

    buona = {'user_tags': {'20260725_Post giornaliero.png':
                           [{'username': 'tizio', 'x': 0.5, 'y': 0.9}]}}
    verifica('busta con un tag valido: nessun problema',
             publish.tag_anomalie(buona, 'giornaliero', una) == [])

    verifica('tag su un aggregato: bloccato',
             any('aggregat' in p for p in
                 publish.tag_anomalie(buona, 'weekend', una)))

    orfana = {'user_tags': {'immagine_che_non_esiste.png':
                            [{'username': 'tizio', 'x': 0.5, 'y': 0.9}]}}
    verifica('chiave orfana: bloccata',
             any('orfana' in p for p in
                 publish.tag_anomalie(orfana, 'giornaliero', una)))

    troppi = {'user_tags': {'20260725_Post giornaliero.png':
                            [{'username': f'u{i}', 'x': 0.5, 'y': 0.9} for i in range(4)]}}
    verifica('4 tag su una immagine: bloccati',
             any('massimo' in p for p in
                 publish.tag_anomalie(troppi, 'giornaliero', una)))

    fuori = {'user_tags': {'20260725_Post giornaliero.png':
                           [{'username': 'tizio', 'x': 1.4, 'y': 0.9}]}}
    verifica('coordinata fuori da 0-1: bloccata',
             any('0.0' in p for p in
                 publish.tag_anomalie(fuori, 'giornaliero', una)))

    senza_nome = {'user_tags': {'20260725_Post giornaliero.png':
                                [{'x': 0.5, 'y': 0.9}]}}
    verifica('tag senza username: bloccato',
             any('username' in p for p in
                 publish.tag_anomalie(senza_nome, 'giornaliero', una)))

    non_dizionario = {'user_tags': [{'username': 'tizio', 'x': 0.5, 'y': 0.9}]}
    verifica('user_tags come lista invece che dizionario: bloccato',
             publish.tag_anomalie(non_dizionario, 'giornaliero', una) != [])


def main():
    test_guardia()
    falliti = [d for d, ok in ESITI if not ok]
    print('\n' + '=' * 60)
    print(f'{len(ESITI) - len(falliti)}/{len(ESITI)} verifiche passate')
    if falliti:
        for d in falliti:
            print(f'  FALLITO: {d}')
        sys.exit(1)
    print('Tutto a posto. (Nessuna chiamata di rete, niente pubblicato.)')


if __name__ == '__main__':
    main()
