#!/usr/bin/env python3
"""
TEST OFFLINE del FRENO INSTAGRAM — non tocca la rete, non pubblica niente.
Si lancia con:  python3 scripts/publish_blocco_ig_test.py

COSA PROVA (il guasto del 03-06/08/2026):
Instagram ha bloccato la pubblicazione nel FEED (errore code 4 / subcode 2207051
"action is blocked"). Il robot non se ne accorgeva e riprovava 4 volte al giorno:
104+ contenitori immagine creati e mai pubblicati in 3 giorni, cioe' esattamente il
comportamento che tiene vivo il blocco. Intanto le storie IG e Facebook uscivano
benissimo, e le buste scadevano una al giorno per la finestra di recupero.

Il freno deve: riconoscere il blocco, smettere di provare il feed per 24h (senza
toccare storie e Facebook), riprovare UNA volta sola quando la pausa scade, e
tenere in vita gli aggregati (carosello/settimanale/weekend) finche' il blocco dura.
"""

import sys
import json
import types
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Finto 'requests': il python3 del Mac non ce l'ha, e non vogliamo chiamate vere.
# ---------------------------------------------------------------------------
CHIAMATE = []
RISPOSTE = []


class FintaRisposta:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


def finta_post(url, data=None, timeout=None, **kw):
    CHIAMATE.append({'url': url, 'data': dict(data or {})})
    if RISPOSTE:
        return RISPOSTE.pop(0)
    return FintaRisposta(200, {'id': 'FINTO'})


# Cosa risponde il profilo quando lo rileggiamo. None = la lettura fallisce.
MEDIA_SUL_PROFILO = []


def finta_get(url, params=None, timeout=None, **kw):
    if url.endswith('/media') or url.endswith('/stories'):
        if MEDIA_SUL_PROFILO is None:
            return FintaRisposta(500, {'error': {'message': 'boom'}})
        return FintaRisposta(200, {'data': list(MEDIA_SUL_PROFILO)})
    return FintaRisposta(200, {'status_code': 'FINISHED'})


_fake = types.ModuleType('requests')
_fake.RequestException = Exception
_fake.post = finta_post
_fake.get = finta_get
sys.modules['requests'] = _fake

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish  # noqa: E402


# ---------------------------------------------------------------------------
# Mini-impalcatura (niente pytest: deve girare col python3 di sistema)
# ---------------------------------------------------------------------------
ESITI = []


def verifica(descrizione, condizione):
    ESITI.append((descrizione, bool(condizione)))
    print(('  OK   ' if condizione else '  FALLITO ') + descrizione)


# La risposta esatta che Meta ha dato dal 03/08 al 06/08/2026 (copiata dai log
# della run, non inventata).
ERRORE_BLOCCO = {"error": {
    "message": "Application request limit reached",
    "type": "OAuthException", "is_transient": False,
    "code": 4, "error_subcode": 2207051,
    "error_user_title": "action is blocked",
    "error_user_msg": "We restrict certain activity to protect our community.",
    "fbtrace_id": "Afinto"}}

# Un errore diverso, che NON deve far scattare il freno (era il guasto precedente).
ERRORE_CAPTION = {"error": {
    "message": "The caption was too long.", "type": "OAuthException",
    "code": 36004, "error_subcode": 2207010}}


# ---------------------------------------------------------------------------
# 1) Riconoscere il blocco
# ---------------------------------------------------------------------------
def test_riconoscimento():
    print('\n[1] Riconoscere «action is blocked» e non confonderlo con altro')

    verifica('code 4 / subcode 2207051 = blocco',
             publish.errore_e_blocco_ig(ERRORE_BLOCCO['error']))
    verifica('caption troppo lunga NON e\' un blocco',
             not publish.errore_e_blocco_ig(ERRORE_CAPTION['error']))
    verifica('errore vuoto NON e\' un blocco',
             not publish.errore_e_blocco_ig({}))


# ---------------------------------------------------------------------------
# 2) Il freno: aperto, mezzo-aperto, chiuso
# ---------------------------------------------------------------------------
def test_freno():
    print('\n[2] Il freno si arma, mette in pausa, riprova UNA volta, si sgancia')
    tmp = Path(tempfile.mkdtemp())
    publish.IG_BLOCCO_FILE = tmp / 'stato' / 'instagram.json'

    verifica('senza file di stato: il feed IG e\' libero',
             publish.stato_freno_ig() == 'libero')

    publish.arma_freno_ig('prova')
    verifica('dopo un blocco: il feed IG e\' in pausa',
             publish.stato_freno_ig() == 'in-pausa')
    verifica('il file di stato e\' stato scritto', publish.IG_BLOCCO_FILE.exists())

    # Falsifichiamo la scadenza: 24h sono passate.
    tutto = json.loads(publish.IG_BLOCCO_FILE.read_text(encoding='utf-8'))
    tutto['feed']['riprova_dopo'] = (datetime.now(publish.TZ) - timedelta(minutes=1)).isoformat()
    publish.IG_BLOCCO_FILE.write_text(json.dumps(tutto), encoding='utf-8')

    verifica('pausa scaduta: si riprova (una volta sola)',
             publish.stato_freno_ig() == 'prova-singola')

    publish.arma_freno_ig('ancora bloccato')
    verifica('un secondo blocco conta i tentativi',
             publish.leggi_freno_ig('feed')['tentativi_falliti'] == 2)
    verifica('e rimette in pausa', publish.stato_freno_ig() == 'in-pausa')

    publish.sgancia_freno_ig()
    verifica('dopo una pubblicazione riuscita: freno sganciato',
             publish.stato_freno_ig() == 'libero')
    verifica('e il file di stato sparisce', not publish.IG_BLOCCO_FILE.exists())

    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 3) Le buste: gli aggregati non scadono mentre IG e' bloccato, i giornalieri si'
# ---------------------------------------------------------------------------
def scrivi_busta(cartella, nome, tipo, data_pub, immagini):
    meta = {'titolo_evento': nome, 'tipo': tipo, 'data_pubblicazione': data_pub,
            'ora_pubblicazione': '07:00', 'caption': 'Testo di prova.',
            'immagini': immagini}
    (cartella / f'{nome}.json').write_text(json.dumps(meta), encoding='utf-8')
    for i in immagini:
        (cartella / i).write_bytes(b'PNG')


def test_scadenze():
    print('\n[3] Con IG bloccato: gli aggregati aspettano, i giornalieri scadono')
    tmp = Path(tempfile.mkdtemp())
    posts = tmp / 'posts'
    posts.mkdir()
    publish.POSTS_DIR = posts
    publish.IG_BLOCCO_FILE = tmp / 'stato' / 'instagram.json'
    publish.TEST_DATE = '2026-08-06'          # giovedi', il giorno del guasto
    publish.GRACE_DAYS = 2

    # Le tre buste vere rimaste indietro, piu' una troppo vecchia per avere senso.
    scrivi_busta(posts, 'carosello_agosto', 'carosello', '2026-08-03',
                 ['c1.png', 'c2.png'])
    scrivi_busta(posts, 'settimanale_0309', 'settimanale', '2026-08-03', ['s1.png'])
    scrivi_busta(posts, 'giornaliero_0308', 'giornaliero', '2026-08-03', ['g1.png'])
    scrivi_busta(posts, 'weekend_vecchio', 'weekend', '2026-07-10', ['w1.png'])

    # --- freno NON armato: si comporta come prima (tutto scaduto) ---
    _, scaduti, _, in_attesa = publish.classifica_buste()
    nomi_scaduti = {b['json_file'].stem for b in scaduti}
    verifica('senza blocco IG: gli aggregati in ritardo scadono come prima',
             {'carosello_agosto', 'settimanale_0309'} <= nomi_scaduti)
    verifica('senza blocco IG: nessuna busta in attesa', in_attesa == [])

    # --- freno armato: gli aggregati ANCORA VALIDI aspettano ---
    publish.arma_freno_ig('prova')
    _, scaduti, _, in_attesa = publish.classifica_buste()
    nomi_attesa = {b['json_file'].stem for b in in_attesa}
    nomi_scaduti = {b['json_file'].stem for b in scaduti}

    verifica('carosello del mese in corso: aspetta lo sblocco',
             'carosello_agosto' in nomi_attesa)
    verifica('settimanale della settimana in corso: aspetta lo sblocco',
             'settimanale_0309' in nomi_attesa)
    verifica('post del giorno: scade lo stesso (era la scelta di Michele)',
             'giornaliero_0308' in nomi_scaduti and
             'giornaliero_0308' not in nomi_attesa)
    verifica('weekend di un mese fa: scade, il blocco non lo resuscita',
             'weekend_vecchio' in nomi_scaduti)

    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 4) In pausa non si tocca la rete per il feed, ma storie e FB passano
# ---------------------------------------------------------------------------
def test_nessuna_chiamata_in_pausa():
    print('\n[4] Due freni indipendenti: feed fermo, storie libere (e viceversa)')
    tmp = Path(tempfile.mkdtemp())
    publish.IG_BLOCCO_FILE = tmp / 'stato' / 'instagram.json'
    publish.arma_freno_ig('prova', 'feed')

    verifica('il feed IG e\' fermo', publish.salta_per_freno_ig('foto') is True)
    verifica('anche il carosello e\' fermo', publish.salta_per_freno_ig('carosello') is True)
    verifica('le storie IG passano lo stesso (era il caso reale del 03-06/08)',
             publish.salta_per_freno_ig('storia') is False)
    verifica('non e\' un blocco totale', publish.ig_bloccato_del_tutto() is False)

    # Se un domani Meta chiude anche le storie, si fermano anche quelle — da sole.
    publish.arma_freno_ig('prova', 'storie')
    verifica('storie bloccate a parte: si fermano', publish.salta_per_freno_ig('storia') is True)
    verifica('ora Instagram e\' chiuso del tutto', publish.ig_bloccato_del_tutto() is True)

    publish.sgancia_freno_ig('storie')
    verifica('sganciare le storie non tocca il feed',
             publish.stato_freno_ig('feed') == 'in-pausa'
             and publish.stato_freno_ig('storie') == 'libero')
    verifica('il file resta (il feed e\' ancora bloccato)', publish.IG_BLOCCO_FILE.exists())

    publish.sgancia_freno_ig('feed')
    verifica('sganciati entrambi: il file sparisce', not publish.IG_BLOCCO_FILE.exists())

    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# 5) La rilettura del profilo: un 403 non prova che il post non sia uscito
# ---------------------------------------------------------------------------
def test_rilettura():
    print('\n[5] Dopo un errore: il post e\' davvero uscito? Si guarda, non si indovina')
    global MEDIA_SUL_PROFILO
    from datetime import timezone

    prima = datetime.now(publish.TZ)

    def istante(delta):
        return (prima + delta).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')

    caption = "🍷 Un film sotto le stelle al Golf Club\n\nAperitivo e proiezione."

    # a) il post c'e' davvero: stessa didascalia, subito dopo il tentativo
    MEDIA_SUL_PROFILO = [{'id': '1', 'timestamp': istante(timedelta(seconds=20)),
                          'caption': caption,
                          'permalink': 'https://instagram.com/p/NUOVO/'}]
    uscito, link = publish.ig_gia_uscito('foto', caption, prima)
    verifica('post presente sul profilo: riconosciuto come uscito', uscito is True)
    verifica('e restituisce il permalink', link == 'https://instagram.com/p/NUOVO/')

    # b) stessa didascalia ma di tre giorni fa: NON e' il nostro tentativo
    #    (senza questo controllo un post ripubblicato ogni anno sembrerebbe uscito)
    MEDIA_SUL_PROFILO = [{'id': '2', 'timestamp': istante(timedelta(days=-3)),
                          'caption': caption,
                          'permalink': 'https://instagram.com/p/VECCHIO/'}]
    uscito, _ = publish.ig_gia_uscito('foto', caption, prima)
    verifica('post vecchio con lo stesso testo: NON conta', uscito is False)

    # c) profilo senza il nostro post -> fallimento vero
    MEDIA_SUL_PROFILO = [{'id': '3', 'timestamp': istante(timedelta(seconds=20)),
                          'caption': 'Tutt\'altro evento',
                          'permalink': 'https://instagram.com/p/ALTRO/'}]
    uscito, _ = publish.ig_gia_uscito('foto', caption, prima)
    verifica('profilo senza il post: fallimento vero', uscito is False)

    # d) rilettura non riuscita -> "non lo so", che NON e' "non e' uscito"
    MEDIA_SUL_PROFILO = None
    uscito, _ = publish.ig_gia_uscito('foto', caption, prima)
    verifica('rilettura fallita: risponde «non lo so» (None), non False',
             uscito is None)

    # e) didascalia con spazi/a capo diversi: deve combaciare lo stesso
    MEDIA_SUL_PROFILO = [{'id': '4', 'timestamp': istante(timedelta(seconds=20)),
                          'caption': "🍷  Un film sotto le stelle al Golf Club   "
                                     "Aperitivo e proiezione.",
                          'permalink': 'https://instagram.com/p/SPAZI/'}]
    uscito, _ = publish.ig_gia_uscito('foto', caption, prima)
    verifica('spaziatura diversa: combacia lo stesso', uscito is True)

    # f) le storie non hanno didascalia: contano solo quelle nuove
    MEDIA_SUL_PROFILO = [{'id': '5', 'timestamp': istante(timedelta(seconds=15))}]
    uscito, _ = publish.ig_gia_uscito('storia', '', prima)
    verifica('storia comparsa dopo il tentativo: uscita', uscito is True)

    MEDIA_SUL_PROFILO = [{'id': '6', 'timestamp': istante(timedelta(hours=-5))}]
    uscito, _ = publish.ig_gia_uscito('storia', '', prima)
    verifica('solo storie vecchie: non e\' uscita', uscito is False)

    MEDIA_SUL_PROFILO = []


if __name__ == '__main__':
    print('TEST FRENO INSTAGRAM — offline, nessuna pubblicazione reale')
    test_riconoscimento()
    test_freno()
    test_scadenze()
    test_nessuna_chiamata_in_pausa()
    test_rilettura()

    falliti = [d for d, ok in ESITI if not ok]
    print(f'\n{len(ESITI) - len(falliti)}/{len(ESITI)} verifiche OK')
    if falliti:
        print('FALLITE:')
        for d in falliti:
            print('  -', d)
        sys.exit(1)
    print('Tutto a posto.')
