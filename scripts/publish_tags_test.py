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


# ---------------------------------------------------------------------------
# 2) Trasporto: ogni unita' pubblicabile porta i SUOI tag
# ---------------------------------------------------------------------------
def test_trasporto():
    print('\n[2] I tag arrivano alla singola immagine')
    jf = Path('/finta/cartella/20260726_Storia.json')
    tre = [img('20260726_Storia_1.png'),
           img('20260726_Storia_2.png'),
           img('20260726_Storia_3.png')]
    meta = {'user_tags': {
        '20260726_Storia_1.png': [{'username': 'primo', 'x': 0.5, 'y': 0.92}],
        '20260726_Storia_2.png': [{'username': 'secondo', 'x': 0.5, 'y': 0.92}],
    }}
    unita = publish.costruisci_unita('storia', jf, tre, meta)

    verifica('tre storie -> tre unita', len(unita) == 3)
    verifica('la storia 1 porta il suo tag',
             unita[0]['user_tags'] == [{'username': 'primo', 'x': 0.5, 'y': 0.92}])
    verifica('la storia 2 porta il SUO tag (non quello della 1)',
             unita[1]['user_tags'] == [{'username': 'secondo', 'x': 0.5, 'y': 0.92}])
    verifica('la storia 3, senza handle registrato, resta senza tag',
             unita[2]['user_tags'] == [])

    jf2 = Path('/finta/cartella/20260725_Post giornaliero.json')
    una = [img('20260725_Post giornaliero.png')]
    meta2 = {'user_tags': {'20260725_Post giornaliero.png':
                           [{'username': 'tizio', 'x': 0.5, 'y': 0.9}]}}
    u2 = publish.costruisci_unita('giornaliero', jf2, una, meta2)
    verifica('il post feed porta il suo tag',
             u2[0]['user_tags'] == [{'username': 'tizio', 'x': 0.5, 'y': 0.9}])

    u3 = publish.costruisci_unita('giornaliero', jf2, una, {})
    verifica('busta senza user_tags: unita con lista vuota (nessun errore)',
             u3[0]['user_tags'] == [])

    u4 = publish.costruisci_unita('giornaliero', jf2, una)
    verifica('costruisci_unita senza il parametro meta: funziona come prima',
             u4[0]['user_tags'] == [] and u4[0]['chiave'] == '20260725_Post giornaliero.png')


# ---------------------------------------------------------------------------
# 3) Invio a Instagram + regola d'oro
# ---------------------------------------------------------------------------
def _reset_finto():
    CHIAMATE.clear()
    RISPOSTE.clear()
    publish.TAG_SALTATI.clear()
    publish.INSTAGRAM_TOKEN = 'TOKEN_FINTO'
    publish.INSTAGRAM_USER_ID = '123'


def test_invio():
    print('\n[3] Invio a Instagram e regola d\'oro')
    import json as _json

    _reset_finto()
    tags = [{'username': 'tizio', 'x': 0.5, 'y': 0.9}]
    publish.ig_create_media_container('http://esempio/x.png', 'didascalia', tags)
    inviato = CHIAMATE[0]['data']
    verifica('user_tags finisce nel payload', 'user_tags' in inviato)
    verifica('user_tags e\' serializzato in JSON',
             _json.loads(inviato['user_tags']) == tags)

    _reset_finto()
    publish.ig_create_media_container('http://esempio/x.png', 'didascalia', [])
    verifica('nessun tag -> il payload resta come prima',
             'user_tags' not in CHIAMATE[0]['data'])

    # Regola d'oro: il primo tentativo (con tag) fallisce, il secondo (senza) riesce.
    _reset_finto()
    RISPOSTE.append(FintaRisposta(400, {'error': {'message': 'utente non taggabile'}}))
    RISPOSTE.append(FintaRisposta(200, {'id': 'CONTAINER_OK'}))
    RISPOSTE.append(FintaRisposta(200, {'id': 'POST_PUBBLICATO'}))
    esito = publish.ig_pubblica_foto('http://esempio/x.png', 'didascalia', tags)
    verifica('il post esce lo stesso quando i tag vengono rifiutati',
             esito == 'POST_PUBBLICATO')
    verifica('il secondo tentativo e\' senza tag',
             'user_tags' not in CHIAMATE[1]['data'])
    verifica('il tag saltato viene registrato per il riepilogo',
             len(publish.TAG_SALTATI) == 1)

    # Se fallisce anche senza tag, non si insiste all'infinito.
    _reset_finto()
    RISPOSTE.append(FintaRisposta(400, {'error': 'x'}))
    RISPOSTE.append(FintaRisposta(400, {'error': 'x'}))
    verifica('fallimento vero: ritorna None dopo due tentativi',
             publish.ig_pubblica_foto('http://esempio/x.png', 'didascalia', tags) is None)
    verifica('due tentativi, non di piu', len(CHIAMATE) == 2)

    # La storia manda i suoi tag.
    _reset_finto()
    publish.ig_pubblica_storia('http://esempio/s.png', tags)
    verifica('la storia manda i tag',
             _json.loads(CHIAMATE[0]['data']['user_tags']) == tags)
    verifica('la storia resta media_type=STORIES',
             CHIAMATE[0]['data']['media_type'] == 'STORIES')

    # pubblica_unita passa i tag dell'unita'.
    _reset_finto()
    unita = {'kind': 'foto', 'chiave': 'x.png', 'immagini': [], 'etichetta': 'foto',
             'user_tags': tags}
    publish.pubblica_unita('ig', unita, ['http://esempio/x.png'], 'didascalia')
    verifica('pubblica_unita inoltra i tag dell\'unita',
             _json.loads(CHIAMATE[0]['data']['user_tags']) == tags)


def main():
    test_guardia()
    test_trasporto()
    test_invio()
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
