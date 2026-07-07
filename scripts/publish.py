#!/usr/bin/env python3
"""
Script per pubblicare i post su Instagram tramite Meta Graph API.

Ogni PNG in posts/ ha un file JSON gemello (stesso nome, estensione .json) con
la data di pubblicazione prevista e la caption. Lo script pubblica SOLO i post
la cui data_pubblicazione e' oggi (fuso orario San Marino/Italia) e non ancora
pubblicati (registrati in published.log).

INTERRUTTORE DI SICUREZZA: se la variabile d'ambiente PUBLISH_LIVE non e'
esattamente "true", lo script gira in modalita' SIMULAZIONE — fa tutto (trova
il post di oggi, prepara la caption, manda una notifica Telegram) tranne
chiamare davvero l'API di Instagram. Serve per testare il meccanismo senza
pubblicare per sbaglio. Si attiva impostando la Variable di repository
PUBLISH_LIVE=true su GitHub (Settings -> Secrets and variables -> Actions -> Variables).
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

INSTAGRAM_TOKEN = os.getenv('INSTAGRAM_TOKEN')
INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PUBLISH_LIVE = os.getenv('PUBLISH_LIVE', '').strip().lower() == 'true'
# Solo per test manuali locali: forza la data "di oggi" invece di usare l'orologio reale.
TEST_DATE = os.getenv('TEST_DATE')

POSTS_DIR = Path('posts')
PUBLISHED_LOG = 'published.log'
REPO = 'michidrop80-Rebelde/sanmarinohappens'
TZ = ZoneInfo('Europe/San_Marino')


def oggi():
    if TEST_DATE:
        return datetime.strptime(TEST_DATE, '%Y-%m-%d').date()
    return datetime.now(TZ).date()


def get_published_posts():
    if Path(PUBLISHED_LOG).exists():
        with open(PUBLISHED_LOG, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def log_published(filename):
    with open(PUBLISHED_LOG, 'a') as f:
        f.write(f"{filename}\n")


def trova_post_di_oggi():
    """Cerca tra i JSON in posts/ quello/i con data_pubblicazione = oggi, non ancora pubblicati."""
    published = get_published_posts()
    data_oggi = oggi().isoformat()
    trovati = []

    if not POSTS_DIR.exists():
        return trovati

    for json_file in sorted(POSTS_DIR.glob('*.json')):
        png_file = json_file.with_suffix('.png')
        if png_file.name in published:
            continue
        if not png_file.exists():
            print(f"⚠️  {json_file.name} non ha il PNG corrispondente ({png_file.name}), salto.")
            continue
        with open(json_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if meta.get('data_pubblicazione') == data_oggi:
            trovati.append((png_file, meta))

    return trovati


def create_media_container(image_url, caption):
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': INSTAGRAM_TOKEN,
    }
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return resp.json().get('id')
    print(f"Errore creazione container: {resp.status_code} - {resp.text}")
    return None


def publish_media(creation_id):
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media_publish"
    payload = {
        'creation_id': creation_id,
        'access_token': INSTAGRAM_TOKEN,
    }
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return resp.json().get('id')
    print(f"Errore pubblicazione: {resp.status_code} - {resp.text}")
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


def main():
    trovati = trova_post_di_oggi()

    if not trovati:
        print(f"Nessun post con data_pubblicazione = {oggi().isoformat()}. Niente da fare.")
        return

    modalita = "🟢 LIVE" if PUBLISH_LIVE else "🧪 SIMULAZIONE (PUBLISH_LIVE non attivo)"
    print(f"Modalita': {modalita}")

    for png_file, meta in trovati:
        caption = meta.get('caption', '')
        image_url = f"https://raw.githubusercontent.com/{REPO}/main/posts/{png_file.name}"

        if not PUBLISH_LIVE:
            print(f"🧪 SIMULEREI la pubblicazione di {png_file.name}")
            notifica_telegram(
                f"🧪 SIMULAZIONE — avrei pubblicato ora:\n{png_file.name}\n\n"
                f"(PUBLISH_LIVE non e' attivo: nessun post reale su Instagram. "
                f"Per andare live: Settings > Secrets and variables > Actions > Variables > PUBLISH_LIVE = true)"
            )
            continue

        print(f"Pubblicando {png_file.name}...")
        container_id = create_media_container(image_url, caption)

        if not container_id:
            notifica_telegram(f"❌ Errore creazione container per {png_file.name}")
            continue

        media_id = publish_media(container_id)
        if media_id:
            print(f"✅ Pubblicato: {media_id}")
            log_published(png_file.name)
            notifica_telegram(f"✅ Pubblicato su Instagram: {png_file.name}")
        else:
            notifica_telegram(f"❌ Errore nella pubblicazione di {png_file.name}")


if __name__ == '__main__':
    if not INSTAGRAM_TOKEN or not INSTAGRAM_USER_ID:
        print("Errore: INSTAGRAM_TOKEN o INSTAGRAM_USER_ID non configurati.")
    else:
        main()
