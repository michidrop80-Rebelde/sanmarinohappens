#!/usr/bin/env python3
"""
Script per pubblicare i post su Instagram tramite Meta Graph API.
Legge i PNG da posts/, crea container, pubblica, e invia notifica Telegram.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# Config
INSTAGRAM_TOKEN = os.getenv('INSTAGRAM_TOKEN')
INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
POSTS_DIR = Path('posts')
PUBLISHED_LOG = 'published.log'

def get_published_posts():
    """Legge i post già pubblicati dal log."""
    if Path(PUBLISHED_LOG).exists():
        with open(PUBLISHED_LOG, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def log_published(filename):
    """Aggiunge il post al log dei pubblicati."""
    with open(PUBLISHED_LOG, 'a') as f:
        f.write(f"{filename}\n")

def create_media_container(image_url, caption):
    """Crea un media container su Instagram."""
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': INSTAGRAM_TOKEN,
    }
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return resp.json().get('id')
    else:
        print(f"Errore creazione container: {resp.status_code} - {resp.text}")
        return None

def publish_media(creation_id):
    """Pubblica il media container."""
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media_publish"
    payload = {
        'creation_id': creation_id,
        'access_token': INSTAGRAM_TOKEN,
    }
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return resp.json().get('id')
    else:
        print(f"Errore pubblicazione: {resp.status_code} - {resp.text}")
        return None

def main():
    if not INSTAGRAM_TOKEN or not INSTAGRAM_USER_ID:
        print("Errore: INSTAGRAM_TOKEN o INSTAGRAM_USER_ID non configurati.")
        return

    published = get_published_posts()
    posts_dir = POSTS_DIR

    if not posts_dir.exists():
        print(f"Cartella {posts_dir} non trovata.")
        return

    # Trova il primo PNG non pubblicato
    for png_file in sorted(posts_dir.glob('*.png')):
        if png_file.name in published:
            print(f"Skipping {png_file.name} (già pubblicato)")
            continue

        # TODO: leggere caption da un file JSON associato
        caption = f"San Marino Happens — {png_file.stem}\n\n#SanMarino #Events"

        # URL pubblico del PNG (GitHub Pages o simile)
        # Per ora, username del repo
        image_url = f"https://raw.githubusercontent.com/michidrop80-Rebelde/sanmarinohappens/main/posts/{png_file.name}"

        print(f"Pubblicando {png_file.name}...")
        container_id = create_media_container(image_url, caption)

        if container_id:
            media_id = publish_media(container_id)
            if media_id:
                print(f"✅ Pubblicato: {media_id}")
                log_published(png_file.name)
            else:
                print(f"❌ Errore nella pubblicazione")
        else:
            print(f"❌ Errore creazione container")

if __name__ == '__main__':
    main()
