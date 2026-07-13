#!/usr/bin/env python3
"""
Script per pubblicare i post su Instagram E su Facebook (Pagina) tramite le API di Meta.

Ogni post in coda e' una "busta": un file JSON in posts/ con la data di pubblicazione,
la caption e il TIPO di post. Il tipo decide quale formato/API usare:

  - "giornaliero"  -> foto singola nel feed (evento del giorno)          [1 immagine]
  - "settimanale"  -> foto singola nel feed (aggregato "questa settimana") [1 immagine]
  - "weekend"      -> foto singola nel feed (aggregato "questo weekend")   [1 immagine]
  - "carosello"    -> carosello (piu' foto in un unico post feed)          [2..10 immagini]
  - "storia"       -> una o piu' Storie (ognuna una storia a se')          [1..N immagini]

  Se il campo "tipo" manca, si assume "giornaliero" (retrocompatibilita' con le buste vecchie).

COME LA BUSTA TROVA LE SUE IMMAGINI:
  - Tipi a foto singola: se la busta NON elenca immagini, si usa il PNG "gemello"
    (stesso nome del JSON, es. "20260710_Post giornaliero.json" -> "...png").
  - Tipi multi-immagine (carosello, storia): la busta DEVE avere un campo "immagini"
    con la lista ORDINATA dei nomi PNG (tutti dentro posts/). Per il carosello l'ordine
    e' l'ordine delle slide; per le storie e' l'ordine cronologico delle storie.

QUANDO PUBBLICA (regola "robot affidabile", invariata dalla Sessione 1):
  Pubblica i post la cui data_pubblicazione e' <= oggi (fuso Europe/San_Marino) e non
  ancora pubblicati, PURCHE' il ritardo non superi la finestra di recupero GRACE_DAYS
  (default 2 giorni). Cosi' un cron che slitta oltre mezzanotte NON perde piu' il post.
  I post piu' vecchi della finestra sono "scaduti" (NON si pubblicano, solo avviso
  Telegram). Le buste "anomale" (JSON illeggibile, PNG mancante, data non valida,
  caption vuota dove serve, numero immagini fuori range) vengono saltate e segnalate.

DUE BINARI INDIPENDENTI:
  - Instagram: sempre attivo (INSTAGRAM_TOKEN + INSTAGRAM_USER_ID, via graph.instagram.com).
  - Facebook (Pagina): attivo SOLO se ci sono i secret FACEBOOK_PAGE_TOKEN + FACEBOOK_PAGE_ID
    (via graph.facebook.com). Se mancano, Facebook viene saltato e Instagram procede.
  I due canali sono indipendenti: se uno fallisce, l'altro va avanti. Il registro
  published.log tiene traccia SEPARATA (righe "chiave|ig" / "chiave|fb"), cosi' un
  contenuto finisce UNA SOLA VOLTA su ciascuna piattaforma anche se lo script si rilancia.
  Per le storie con piu' immagini ogni singola storia ha la sua chiave, cosi' se il
  robot si ferma a meta' non ripubblica le storie gia' uscite.

ARCHIVIAZIONE (solo in LIVE): quando un post e' pubblicato con successo su TUTTI i
  canali attivi, il JSON + TUTTE le sue immagini vengono spostati da posts/ ad
  archivio/AAAA-MM/ nello stesso repo. posts/ resta la "coda" (solo cio' che deve
  ancora uscire); lo storico non va perso; gli originali restano sul Mac di Michele.

INTERRUTTORE DI SICUREZZA: se la variabile d'ambiente PUBLISH_LIVE non e' esattamente
  "true", lo script gira in SIMULAZIONE: fa tutto (trova i post di oggi, prepara le
  caption, segnala scaduti/anomali, manda una notifica Telegram) TRANNE pubblicare
  davvero e archiviare. In simulazione, se Facebook e' configurato, fa una chiamata di
  SOLA LETTURA alla Pagina per confermare che il token e' valido. Per andare live:
  Variable di repository PUBLISH_LIVE=true (Settings -> Secrets and variables -> Actions -> Variables).
"""

import os
import re
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

# --- Instagram (binario sempre attivo) ---
INSTAGRAM_TOKEN = os.getenv('INSTAGRAM_TOKEN')
INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')

# --- Facebook Pagina (binario opzionale: attivo solo se entrambi i secret esistono) ---
FACEBOOK_PAGE_TOKEN = os.getenv('FACEBOOK_PAGE_TOKEN')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
FB_ENABLED = bool(FACEBOOK_PAGE_TOKEN and FACEBOOK_PAGE_ID)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PUBLISH_LIVE = os.getenv('PUBLISH_LIVE', '').strip().lower() == 'true'
# Solo per test manuali: forza la data "di oggi" invece di usare l'orologio reale.
TEST_DATE = os.getenv('TEST_DATE')

# Finestra di recupero: quanti giorni di ritardo tolleriamo prima di considerare una
# busta "scaduta". Recupera un cron che slitta oltre mezzanotte SENZA ripubblicare per
# sbaglio eventi di settimane prima. Default 2, sovrascrivibile via env.
try:
    GRACE_DAYS = int(os.getenv('GRACE_DAYS', '2'))
except ValueError:
    GRACE_DAYS = 2

POSTS_DIR = Path('posts')
ARCHIVIO_DIR = Path('archivio')
PUBLISHED_LOG = 'published.log'
REPO = 'michidrop80-Rebelde/sanmarinohappens'
IG_API = 'https://graph.instagram.com'
FB_API = 'https://graph.facebook.com/v21.0'
TZ = ZoneInfo('Europe/San_Marino')

# Tipi di post riconosciuti, raggruppati per comportamento.
TIPI_FOTO_SINGOLA = {'giornaliero', 'settimanale', 'weekend'}  # 1 immagine, feed
TIPI_VALIDI = TIPI_FOTO_SINGOLA | {'carosello', 'storia'}


def oggi():
    if TEST_DATE:
        return datetime.strptime(TEST_DATE, '%Y-%m-%d').date()
    return datetime.now(TZ).date()


def parse_data(s):
    """Ritorna un date da 'AAAA-MM-GG', oppure None se il formato non e' valido."""
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def normalizza_tipo(meta):
    """Legge il campo 'tipo' della busta, con default 'giornaliero' (buste vecchie)."""
    return (meta.get('tipo') or 'giornaliero').strip().lower()


def get_immagini(json_file, meta):
    """Ritorna la lista ORDINATA dei Path immagine della busta.
    - Se la busta ha un campo 'immagini' (lista non vuota) -> quelli (dentro posts/).
    - Altrimenti -> il PNG gemello (stesso nome del JSON). Cosi' le buste a foto
      singola restano compatibili con lo schema vecchio (nessun campo 'immagini')."""
    lista = meta.get('immagini')
    if isinstance(lista, list) and lista:
        return [POSTS_DIR / str(nome) for nome in lista]
    return [json_file.with_suffix('.png')]


def image_url(png_name):
    """URL RAW GitHub del PNG in posts/. Il nome viene percent-encoded (i file hanno
    spazi, es. 'Post giornaliero.png' -> '...%20giornaliero.png'): senza encoding la
    fetch lato Meta fallirebbe su un URL con spazi."""
    return f"https://raw.githubusercontent.com/{REPO}/main/posts/{quote(png_name)}"


# ---------------------------------------------------------------------------
# Registro dei contenuti gia' pubblicati (per-canale, per-unita')
# Formato riga: "chiave|ig" oppure "chiave|fb". La "chiave" identifica l'unita' di
# pubblicazione (una foto, un carosello, una singola storia) — vedi costruisci_unita().
# Retrocompatibilita': una riga vecchia SENZA "|" viene letta come "|ig" (prima
# esisteva solo Instagram), cosi' non si ripubblica su IG per sbaglio.
# ---------------------------------------------------------------------------
def get_published():
    pubblicati = set()
    if Path(PUBLISHED_LOG).exists():
        with open(PUBLISHED_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                riga = line.strip()
                if not riga:
                    continue
                if '|' not in riga:
                    riga = f"{riga}|ig"  # righe vecchie = solo Instagram
                pubblicati.add(riga)
    return pubblicati


def gia_pubblicato(chiave, canale, pubblicati):
    return f"{chiave}|{canale}" in pubblicati


def segna_pubblicato(chiave, canale, pubblicati):
    """Registra su published.log E aggiorna l'insieme in memoria, cosi' il controllo
    'completo su tutti i canali' (archiviazione) resta coerente."""
    with open(PUBLISHED_LOG, 'a', encoding='utf-8') as f:
        f.write(f"{chiave}|{canale}\n")
    pubblicati.add(f"{chiave}|{canale}")


def canali_richiesti():
    """I canali su cui un post DEVE uscire per considerarsi 'completo'.
    Instagram sempre; Facebook solo se configurato."""
    canali = ['ig']
    if FB_ENABLED:
        canali.append('fb')
    return canali


# ---------------------------------------------------------------------------
# Unita' di pubblicazione
# Un'unita' e' la cosa piu' piccola che si pubblica in UNA chiamata e che va tracciata
# a se' per l'idempotenza. Per ogni busta:
#   - foto singola  -> 1 unita' (kind 'foto'),     chiave = nome del PNG
#   - carosello     -> 1 unita' (kind 'carosello'),chiave = nome-base del JSON (atomica)
#   - storia        -> N unita' (kind 'storia'),   una per immagine, chiave = nome del PNG
# La chiave del carosello e' il nome-base del JSON (non un PNG) perche' e' UN post solo
# anche se contiene piu' immagini; le storie invece sono post distinti -> chiave per PNG.
# ---------------------------------------------------------------------------
def costruisci_unita(tipo, json_file, immagini):
    if tipo in TIPI_FOTO_SINGOLA:
        return [{'kind': 'foto', 'chiave': immagini[0].name,
                 'immagini': [immagini[0]], 'etichetta': 'foto'}]
    if tipo == 'carosello':
        return [{'kind': 'carosello', 'chiave': json_file.stem,
                 'immagini': list(immagini), 'etichetta': f'carosello ({len(immagini)} foto)'}]
    if tipo == 'storia':
        n = len(immagini)
        return [{'kind': 'storia', 'chiave': img.name, 'immagini': [img],
                 'etichetta': f'storia {i}/{n}'} for i, img in enumerate(immagini, 1)]
    return []


# ---------------------------------------------------------------------------
# Guardia CONTENUTI: prezzi / gratuita' in caption (regola equita')
# ---------------------------------------------------------------------------
# Regola di equita' tra organizzatori: nessun prezzo ne' gratuita' nei contenuti
# pubblici (i costi vanno SOLO nel link in bio) — vedi .claude/skills/smh-testi/SKILL.md.
# Questa e' la RETE AUTOMATICA lato GitHub: una busta la cui caption contiene questi
# termini diventa "anomala" e NON si pubblica (+ avviso Telegram). Blocca solo i casi
# CERTI e ad alta confidenza (i termini indicati da Michele); i dubbi piu' sfumati e i
# prezzi che stanno SULL'IMMAGINE (non leggibili da qui) li intercetta /smh-check sul
# Mac, che vede anche il testo-sorgente e le immagini. Le storie non hanno caption.
PREZZI_PATTERN = re.compile(
    r'€'
    r'|\bgratis\b'
    r'|\bgratuit[oaie]\b'          # gratuito / gratuita / gratuiti / gratuite
    r'|\bgratuitamente\b'
    r'|\ba\s+pagamento\b'
    r'|\bingresso\s+(?:libero|gratuito|gratis)\b'
    r'|\bentrata\s+(?:libera|gratuita|gratis)\b',
    re.IGNORECASE,
)


def caption_prezzi(caption):
    """Ritorna la lista (senza duplicati, nell'ordine trovato) dei termini di
    prezzo/gratuita' presenti nella caption. Lista vuota = nessun problema."""
    trovati = []
    for m in PREZZI_PATTERN.finditer(caption or ''):
        termine = m.group(0).strip()
        if termine.lower() not in [t.lower() for t in trovati]:
            trovati.append(termine)
    return trovati


# ---------------------------------------------------------------------------
# Smistamento delle buste in coda
# ---------------------------------------------------------------------------
def classifica_buste():
    """Scorre i JSON in posts/ e li smista in base a validita' e data_pubblicazione:
      - da_pubblicare: data tra (oggi - GRACE_DAYS) e oggi inclusi, busta valida.
      - scaduti: data piu' vecchia di GRACE_DAYS -> NON si pubblicano, solo avviso.
      - anomali: JSON illeggibile, tipo sconosciuto, immagini mancanti/fuori range,
        data assente/malformata, caption vuota (dove serve).
      - futuri (data > oggi): ignorati in silenzio.
    Ritorna (da_pubblicare, scaduti, anomali).
      da_pubblicare / scaduti = liste di dict {json_file, meta, tipo, immagini, giorni_ritardo}
      anomali = lista di (nome_json, motivo)
    """
    data_oggi = oggi()
    da_pubblicare, scaduti, anomali = [], [], []

    if not POSTS_DIR.exists():
        return da_pubblicare, scaduti, anomali

    for json_file in sorted(POSTS_DIR.glob('*.json')):
        # 1) JSON leggibile?
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            anomali.append((json_file.name, f"JSON illeggibile: {e}"))
            continue
        # 2) tipo riconosciuto?
        tipo = normalizza_tipo(meta)
        if tipo not in TIPI_VALIDI:
            anomali.append((json_file.name,
                            f"tipo sconosciuto: {tipo!r} (attesi: {', '.join(sorted(TIPI_VALIDI))})"))
            continue
        # 3) immagini presenti (tutte)?
        immagini = get_immagini(json_file, meta)
        mancanti = [p.name for p in immagini if not p.exists()]
        if mancanti:
            anomali.append((json_file.name, f"PNG mancante/i: {', '.join(mancanti)}"))
            continue
        # 4) numero immagini coerente col tipo?
        n = len(immagini)
        if tipo in TIPI_FOTO_SINGOLA and n != 1:
            anomali.append((json_file.name, f"tipo {tipo}: attesa 1 immagine, trovate {n}"))
            continue
        if tipo == 'carosello' and not (2 <= n <= 10):
            anomali.append((json_file.name, f"carosello: servono 2..10 immagini, trovate {n}"))
            continue
        if tipo == 'storia' and n < 1:
            anomali.append((json_file.name, "storia: serve almeno 1 immagine"))
            continue
        # 5) data valida?
        data_pub = parse_data(meta.get('data_pubblicazione'))
        if data_pub is None:
            anomali.append((json_file.name,
                            f"data_pubblicazione assente o non valida: {meta.get('data_pubblicazione')!r}"))
            continue
        # 6) caption presente? (le storie NON hanno caption: il testo e' dentro la grafica)
        if tipo != 'storia':
            caption_txt = (meta.get('caption') or '').strip()
            if not caption_txt:
                anomali.append((json_file.name, "caption vuota"))
                continue
            # 6b) PREZZI/GRATUITA' in caption? Regola equita' -> blocca e segnala.
            prezzi = caption_prezzi(caption_txt)
            if prezzi:
                anomali.append((json_file.name,
                                "prezzo/gratuità in caption (regola equità, i costi vanno solo "
                                f"nel link in bio): «{'», «'.join(prezzi)}»"))
                continue
        # 7) smistamento per data
        giorni_ritardo = (data_oggi - data_pub).days
        busta = {'json_file': json_file, 'meta': meta, 'tipo': tipo,
                 'immagini': immagini, 'giorni_ritardo': giorni_ritardo}
        if giorni_ritardo < 0:
            continue  # futuro: non e' ancora il momento
        elif giorni_ritardo <= GRACE_DAYS:
            da_pubblicare.append(busta)
        else:
            scaduti.append(busta)

    return da_pubblicare, scaduti, anomali


# ---------------------------------------------------------------------------
# Archiviazione (solo LIVE, solo a post completo)
# ---------------------------------------------------------------------------
def archivia_busta(json_file, immagini, meta):
    """Sposta JSON + TUTTE le immagini da posts/ ad archivio/AAAA-MM/ (stesso repo).
    AAAA-MM viene dalla data_pubblicazione. Chiamata SOLO in LIVE, a post completo su
    tutti i canali attivi. Ritorna la cartella di destinazione, o None se qualcosa va
    storto (non deve bloccare il resto)."""
    data_pub = parse_data(meta.get('data_pubblicazione'))
    if data_pub is None:
        return None
    dest = ARCHIVIO_DIR / f"{data_pub.year:04d}-{data_pub.month:02d}"
    dest.mkdir(parents=True, exist_ok=True)
    try:
        for f in [json_file, *immagini]:
            if f.exists():
                f.rename(dest / f.name)
    except OSError as e:
        print(f"⚠️  Archiviazione di {json_file.name} fallita: {e}")
        return None
    return dest


# ---------------------------------------------------------------------------
# Instagram (graph.instagram.com)
# ---------------------------------------------------------------------------
def ig_create_media_container(image_url_str, caption):
    payload = {'image_url': image_url_str, 'caption': caption, 'access_token': INSTAGRAM_TOKEN}
    resp = requests.post(f"{IG_API}/{INSTAGRAM_USER_ID}/media", data=payload)
    if resp.status_code == 200:
        return resp.json().get('id')
    print(f"Errore creazione container IG: {resp.status_code} - {resp.text}")
    return None


def ig_container_pronto(container_id, tentativi=20, attesa=3):
    """Aspetta che un container IG sia 'FINISHED' prima di pubblicarlo.
    Dopo aver creato un container (foto, carosello o storia) Instagram lo elabora
    per qualche secondo; se si pubblica troppo presto risponde 'The media is not
    ready for publishing' (errore visto al primo giro reale su carosello e storia).
    Interroga lo stato del container finche' non e' FINISHED. Ritorna True se pronto,
    False se lo stato e' ERROR/EXPIRED o se scade il tempo (tentativi*attesa secondi)."""
    for _ in range(tentativi):
        try:
            resp = requests.get(f"{IG_API}/{container_id}",
                                params={'fields': 'status_code', 'access_token': INSTAGRAM_TOKEN}, timeout=15)
        except requests.RequestException as e:
            print(f"Errore di rete controllando lo stato del container IG {container_id}: {e}")
            time.sleep(attesa)
            continue
        if resp.status_code == 200:
            stato = resp.json().get('status_code')
            if stato == 'FINISHED':
                return True
            if stato in ('ERROR', 'EXPIRED'):
                print(f"Container IG {container_id} in stato {stato}: non pubblicabile.")
                return False
        time.sleep(attesa)
    print(f"Container IG {container_id}: non pronto dopo {tentativi * attesa}s, rimando al prossimo giro.")
    return False


def ig_publish_media(creation_id):
    # Prima di pubblicare, assicurati che Instagram abbia finito di elaborare il
    # container: pubblicare un container non ancora 'FINISHED' e' la causa dell'errore
    # 'media not ready' visto su carosello e storia al primo giro reale.
    if not ig_container_pronto(creation_id):
        return None
    payload = {'creation_id': creation_id, 'access_token': INSTAGRAM_TOKEN}
    resp = requests.post(f"{IG_API}/{INSTAGRAM_USER_ID}/media_publish", data=payload)
    if resp.status_code == 200:
        return resp.json().get('id')
    print(f"Errore pubblicazione IG: {resp.status_code} - {resp.text}")
    return None


def ig_pubblica_foto(image_url_str, caption):
    """Foto singola nel feed: container + publish. Ritorna l'id, o None."""
    container_id = ig_create_media_container(image_url_str, caption)
    if not container_id:
        return None
    return ig_publish_media(container_id)


def ig_pubblica_carosello(image_urls, caption):
    """Carosello: un container 'figlio' per ogni immagine (is_carousel_item), poi un
    container padre media_type=CAROUSEL che li unisce, poi publish. Ritorna l'id, o None."""
    child_ids = []
    for url in image_urls:
        payload = {'image_url': url, 'is_carousel_item': 'true', 'access_token': INSTAGRAM_TOKEN}
        resp = requests.post(f"{IG_API}/{INSTAGRAM_USER_ID}/media", data=payload)
        if resp.status_code != 200:
            print(f"Errore container figlio IG (carosello): {resp.status_code} - {resp.text}")
            return None
        cid = resp.json().get('id')
        if not cid:
            return None
        child_ids.append(cid)
    payload = {'media_type': 'CAROUSEL', 'children': ','.join(child_ids),
               'caption': caption, 'access_token': INSTAGRAM_TOKEN}
    resp = requests.post(f"{IG_API}/{INSTAGRAM_USER_ID}/media", data=payload)
    if resp.status_code != 200:
        print(f"Errore container CAROUSEL IG: {resp.status_code} - {resp.text}")
        return None
    parent_id = resp.json().get('id')
    if not parent_id:
        return None
    return ig_publish_media(parent_id)


def ig_pubblica_storia(image_url_str):
    """Storia IG: container con media_type=STORIES, poi publish. Ritorna l'id, o None.
    Le storie non hanno caption (il testo e' dentro la grafica)."""
    payload = {'image_url': image_url_str, 'media_type': 'STORIES', 'access_token': INSTAGRAM_TOKEN}
    resp = requests.post(f"{IG_API}/{INSTAGRAM_USER_ID}/media", data=payload)
    if resp.status_code != 200:
        print(f"Errore container STORIES IG: {resp.status_code} - {resp.text}")
        return None
    container_id = resp.json().get('id')
    if not container_id:
        return None
    return ig_publish_media(container_id)


# ---------------------------------------------------------------------------
# Facebook Pagina (graph.facebook.com)
# ---------------------------------------------------------------------------
def fb_ottieni_page_token(token_configurato):
    """Ricava un vero 'token di Pagina' a partire dal token FB configurato.
    Alcune chiamate (pubblicare come Pagina, caricare foto non pubblicate) esigono
    che il token agisca COME la Pagina: col token 'utente/system-user' Meta risponde
    '(#200) Unpublished posts must be posted to a page as the page itself' (errore
    visto su TUTTO Facebook al primo giro reale). Chiediamo il campo access_token del
    nodo Pagina: se torna un token, quello agisce come la Pagina. Ritorna
    (page_token, None) se riuscito, altrimenti (None, motivo)."""
    try:
        resp = requests.get(f"{FB_API}/{FACEBOOK_PAGE_ID}",
                            params={'fields': 'access_token', 'access_token': token_configurato}, timeout=15)
    except requests.RequestException as e:
        return None, f"errore di rete: {e}"
    if resp.status_code == 200:
        tok = resp.json().get('access_token')
        if tok:
            return tok, None
        return None, "il nodo Pagina non ha restituito un access_token (permessi mancanti?)"
    return None, f"HTTP {resp.status_code}: {resp.text[:150]}"


def fb_verifica_pagina():
    """SOLA LETTURA: conferma che il token Pagina e' valido e la Pagina raggiungibile.
    Ritorna (True, nome_pagina) oppure (False, descrizione_errore). Non pubblica nulla."""
    url = f"{FB_API}/{FACEBOOK_PAGE_ID}"
    try:
        resp = requests.get(url, params={'fields': 'name', 'access_token': FACEBOOK_PAGE_TOKEN}, timeout=15)
    except requests.RequestException as e:
        return False, f"errore di rete: {e}"
    if resp.status_code == 200:
        return True, resp.json().get('name', '(senza nome)')
    return False, f"HTTP {resp.status_code}: {resp.text[:200]}"


def fb_pubblica_foto(image_url_str, message):
    """Foto singola sul feed della Pagina (/photos). Ritorna l'id del post, o None.
    Nota: il testo viaggia nel campo 'message'. Se al primo post reale il testo non
    comparisse sotto la foto, provare a rinominare 'message' in 'caption' (unico punto
    incerto della doc Meta per /photos)."""
    url = f"{FB_API}/{FACEBOOK_PAGE_ID}/photos"
    payload = {'url': image_url_str, 'message': message, 'access_token': FACEBOOK_PAGE_TOKEN}
    try:
        resp = requests.post(url, data=payload, timeout=60)
    except requests.RequestException as e:
        print(f"Errore di rete FB: {e}")
        return None
    if resp.status_code == 200:
        dati = resp.json()
        return dati.get('post_id') or dati.get('id')
    print(f"Errore pubblicazione FB: {resp.status_code} - {resp.text}")
    return None


def fb_carica_foto_non_pubblicata(image_url_str, temporary=False):
    """Carica una foto sulla Pagina SENZA pubblicarla (published=false) e ritorna il
    suo id, da riusare per un post multi-foto o per una storia. Ritorna None se fallisce.
    temporary=True per le storie: la doc Meta di /photo_stories vuole la foto caricata
    come temporanea (per i post multi-foto invece basta published=false)."""
    url = f"{FB_API}/{FACEBOOK_PAGE_ID}/photos"
    payload = {'url': image_url_str, 'published': 'false', 'access_token': FACEBOOK_PAGE_TOKEN}
    if temporary:
        payload['temporary'] = 'true'
    try:
        resp = requests.post(url, data=payload, timeout=60)
    except requests.RequestException as e:
        print(f"Errore di rete FB (upload foto): {e}")
        return None
    if resp.status_code == 200:
        return resp.json().get('id')
    print(f"Errore upload foto FB non pubblicata: {resp.status_code} - {resp.text}")
    return None


def fb_pubblica_multifoto(image_urls, message):
    """Post multi-foto sul feed della Pagina: carica ogni foto come non pubblicata, poi
    crea un post /feed che le allega tutte (attached_media). E' l'equivalente FB del
    carosello IG. Ritorna l'id del post, o None."""
    media_fbids = []
    for url in image_urls:
        pid = fb_carica_foto_non_pubblicata(url)
        if not pid:
            return None
        media_fbids.append(pid)
    payload = {'message': message, 'access_token': FACEBOOK_PAGE_TOKEN}
    for i, pid in enumerate(media_fbids):
        payload[f'attached_media[{i}]'] = json.dumps({'media_fbid': pid})
    try:
        resp = requests.post(f"{FB_API}/{FACEBOOK_PAGE_ID}/feed", data=payload, timeout=60)
    except requests.RequestException as e:
        print(f"Errore di rete FB (multifoto): {e}")
        return None
    if resp.status_code == 200:
        return resp.json().get('id')
    print(f"Errore pubblicazione multifoto FB: {resp.status_code} - {resp.text}")
    return None


def fb_pubblica_storia(image_url_str):
    """Storia della Pagina FB: carica la foto come non pubblicata, poi la promuove a
    storia (/photo_stories). Ritorna un id/esito, o None.
    Nota onesta: fra tutte le chiamate, le Page Stories sono la parte meno collaudata
    della doc Meta (endpoint /photo_stories, permessi pages_manage_posts). Se in LIVE
    dovesse dare errore, IG non ne risente (binari indipendenti) e lo vedremo nei log."""
    pid = fb_carica_foto_non_pubblicata(image_url_str, temporary=True)
    if not pid:
        return None
    url = f"{FB_API}/{FACEBOOK_PAGE_ID}/photo_stories"
    payload = {'photo_id': pid, 'access_token': FACEBOOK_PAGE_TOKEN}
    try:
        resp = requests.post(url, data=payload, timeout=60)
    except requests.RequestException as e:
        print(f"Errore di rete FB (storia): {e}")
        return None
    if resp.status_code == 200:
        dati = resp.json()
        return dati.get('post_id') or dati.get('id') or 'ok'
    print(f"Errore pubblicazione storia FB: {resp.status_code} - {resp.text}")
    return None


# ---------------------------------------------------------------------------
# Dispatch: dato il kind dell'unita', chiama la funzione giusta per il canale
# ---------------------------------------------------------------------------
def pubblica_unita(canale, unita, image_urls, caption):
    """Pubblica UNA unita' su UN canale. Ritorna l'id/esito (truthy) o None.
    image_urls = lista di URL (1 elemento per foto/storia, N per carosello)."""
    kind = unita['kind']
    if canale == 'ig':
        if kind == 'foto':
            return ig_pubblica_foto(image_urls[0], caption)
        if kind == 'carosello':
            return ig_pubblica_carosello(image_urls, caption)
        if kind == 'storia':
            return ig_pubblica_storia(image_urls[0])
    elif canale == 'fb':
        if kind == 'foto':
            return fb_pubblica_foto(image_urls[0], caption)
        if kind == 'carosello':
            return fb_pubblica_multifoto(image_urls, caption)
        if kind == 'storia':
            return fb_pubblica_storia(image_urls[0])
    return None


def notifica_telegram(testo):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("(Telegram non configurato: TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID mancanti, notifica saltata)")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': testo}, timeout=10)
    except requests.RequestException as e:
        print(f"Errore notifica Telegram: {e}")


# Nome canale -> etichetta per il report
ETICHETTA_CANALE = {'ig': 'IG', 'fb': 'FB'}


def main():
    da_pubblicare, scaduti, anomali = classifica_buste()

    # Se non c'e' nulla di cui parlare (nessun post di oggi, niente scaduto/anomalo —
    # al massimo post futuri), restiamo in silenzio.
    if not da_pubblicare and not scaduti and not anomali:
        print(f"Nessuna busta da pubblicare, scaduta o anomala per oggi ({oggi().isoformat()}). Niente da fare.")
        return

    modalita = "🟢 LIVE" if PUBLISH_LIVE else "🧪 SIMULAZIONE (PUBLISH_LIVE non attivo)"
    stato_fb = "attivo" if FB_ENABLED else "NON configurato (solo Instagram)"
    print(f"Modalita': {modalita} — Facebook: {stato_fb} — finestra recupero: {GRACE_DAYS} giorni")

    # Facebook: ricava il vero token di Pagina dal token configurato e sovrascrivi il
    # token globale. Le pubblicazioni FB (foto, foto non pubblicate, storie) devono
    # partire COME la Pagina, non come utente: senza questo passo Meta risponde
    # "Unpublished posts must be posted to a page as the page itself".
    if FB_ENABLED:
        global FACEBOOK_PAGE_TOKEN
        page_token, motivo = fb_ottieni_page_token(FACEBOOK_PAGE_TOKEN)
        if page_token:
            FACEBOOK_PAGE_TOKEN = page_token
            print("FB: token di Pagina ricavato correttamente.")
        else:
            print(f"⚠️ FB: non ho ricavato il token di Pagina ({motivo}); uso quello configurato.")

    pubblicati = get_published()
    righe_report = []  # per la notifica Telegram riepilogativa

    # In simulazione, verifichiamo UNA volta sola che il token Pagina FB sia valido
    # (una chiamata di sola lettura), invece di ripeterlo per ogni unita'.
    fb_sim_ok, fb_sim_nome = (None, None)
    if FB_ENABLED and not PUBLISH_LIVE:
        fb_sim_ok, fb_sim_nome = fb_verifica_pagina()

    for busta in da_pubblicare:
        json_file = busta['json_file']
        meta = busta['meta']
        tipo = busta['tipo']
        immagini = busta['immagini']
        caption = meta.get('caption', '')
        giorni_ritardo = busta['giorni_ritardo']

        etichetta_ritardo = "" if giorni_ritardo == 0 else f"  ⏰ IN RITARDO di {giorni_ritardo}g (recuperato)"
        titolo = meta.get('titolo_evento', json_file.stem)
        righe_report.append(f"• [{tipo}] {titolo}{etichetta_ritardo}")

        unita = costruisci_unita(tipo, json_file, immagini)

        for canale in ['ig', 'fb']:
            et = ETICHETTA_CANALE[canale]
            if canale == 'fb' and not FB_ENABLED:
                righe_report.append("   FB: — non configurato")
                continue

            for u in unita:
                url_list = [image_url(p.name) for p in u['immagini']]
                prefisso = f"   {et} · {u['etichetta']}:"

                if gia_pubblicato(u['chiave'], canale, pubblicati):
                    print(f"{et}: {u['chiave']} gia' pubblicato, salto.")
                    righe_report.append(f"{prefisso} già pubblicato (salto)")
                elif not PUBLISH_LIVE:
                    if canale == 'fb':
                        if fb_sim_ok:
                            righe_report.append(f"{prefisso} 🧪 simulazione — token OK, Pagina «{fb_sim_nome}»")
                        else:
                            righe_report.append(f"{prefisso} ⚠️ token/Pagina non raggiungibile ({fb_sim_nome})")
                    else:
                        righe_report.append(f"{prefisso} 🧪 simulazione (non pubblicato)")
                    print(f"🧪 {et}: simulerei {u['kind']} di «{titolo}» ({u['chiave']})")
                else:
                    print(f"{et}: pubblico {u['kind']} «{titolo}» ({u['chiave']})...")
                    esito = pubblica_unita(canale, u, url_list, caption)
                    if esito:
                        print(f"✅ {et} pubblicato: {esito}")
                        segna_pubblicato(u['chiave'], canale, pubblicati)
                        righe_report.append(f"{prefisso} ✅ pubblicato")
                    else:
                        righe_report.append(f"{prefisso} ❌ errore")

        # ---------- ARCHIVIAZIONE (solo LIVE, solo a post completo) ----------
        # "Completo" = tutte le unita' pubblicate su TUTTI i canali attivi (IG sempre;
        # FB se configurato). Solo allora togliamo la busta dalla coda posts/ e la
        # mettiamo in archivio/AAAA-MM/. In simulazione non si archivia mai.
        if PUBLISH_LIVE:
            completo = all(gia_pubblicato(u['chiave'], c, pubblicati)
                           for u in unita for c in canali_richiesti())
            if completo:
                dest = archivia_busta(json_file, immagini, meta)
                if dest:
                    print(f"📦 {json_file.name} archiviato in {dest.as_posix()}/")
                    righe_report.append(f"   📦 archiviato in {dest.as_posix()}/")

    # ---------- SEZIONI DI AVVISO (scaduti / anomali) ----------
    if scaduti:
        if righe_report:
            righe_report.append("")
        righe_report.append(f"⚠️ BUSTE SCADUTE (NON pubblicate, oltre {GRACE_DAYS}g di ritardo):")
        for busta in scaduti:
            meta = busta['meta']
            righe_report.append(
                f"   • [{busta['tipo']}] {meta.get('titolo_evento', busta['json_file'].stem)} — "
                f"prevista {meta.get('data_pubblicazione')} ({busta['giorni_ritardo']}g fa) "
                f"→ aggiorna la data nel piano o rimuovila dalla coda"
            )

    if anomali:
        if righe_report:
            righe_report.append("")
        righe_report.append("⚠️ BUSTE ANOMALE (saltate):")
        for nome_json, motivo in anomali:
            righe_report.append(f"   • {nome_json} — {motivo}")

    intestazione = ("🟢 PUBBLICAZIONE LIVE" if PUBLISH_LIVE
                    else "🧪 SIMULAZIONE (nessun post reale)")
    if scaduti or anomali:
        intestazione = "❗ " + intestazione + " — CI SONO BUSTE DA CONTROLLARE"
    if not FB_ENABLED and not PUBLISH_LIVE:
        intestazione += "\n(Facebook non ancora configurato: aggiungi i secret FACEBOOK_PAGE_TOKEN e FACEBOOK_PAGE_ID)"
    notifica_telegram(intestazione + "\n\n" + "\n".join(righe_report))


if __name__ == '__main__':
    if not INSTAGRAM_TOKEN or not INSTAGRAM_USER_ID:
        print("Errore: INSTAGRAM_TOKEN o INSTAGRAM_USER_ID non configurati.")
    else:
        main()
