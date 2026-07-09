#!/usr/bin/env python3
"""
Script per pubblicare i post su Instagram E su Facebook (Pagina) tramite le API di Meta.

Ogni PNG in posts/ ha un file JSON gemello (stesso nome, estensione .json) con
la data di pubblicazione prevista e la caption. Lo script pubblica SOLO i post
la cui data_pubblicazione e' oggi (fuso orario San Marino/Italia) e non ancora
pubblicati (registrati in published.log).

DUE BINARI INDIPENDENTI:
  - Instagram: sempre attivo (usa INSTAGRAM_TOKEN + INSTAGRAM_USER_ID, via graph.instagram.com).
  - Facebook (Pagina): si attiva SOLO se sono presenti i secret FACEBOOK_PAGE_TOKEN
    + FACEBOOK_PAGE_ID (via graph.facebook.com). Se mancano, Facebook viene semplicemente
    saltato e Instagram procede come sempre — cosi' aggiungere Facebook non rompe nulla.
  I due canali sono indipendenti: se uno fallisce, l'altro va avanti comunque. Il
  registro published.log tiene traccia SEPARATA dei due (righe "nomefile.png|ig" e
  "nomefile.png|fb"), cosi' un post finisce UNA SOLA VOLTA su ciascuna piattaforma
  anche se lo script viene rilanciato.

INTERRUTTORE DI SICUREZZA: se la variabile d'ambiente PUBLISH_LIVE non e'
esattamente "true", lo script gira in modalita' SIMULAZIONE — fa tutto (trova
il post di oggi, prepara la caption, manda una notifica Telegram) tranne
pubblicare per davvero. In simulazione, se Facebook e' configurato, lo script
fa una chiamata di SOLA LETTURA alla Pagina per confermare che il token e' valido
e la Pagina raggiungibile (senza pubblicare nulla). Per andare live: Variable di
repository PUBLISH_LIVE=true su GitHub (Settings -> Secrets and variables -> Actions -> Variables).
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
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
# Solo per test manuali locali: forza la data "di oggi" invece di usare l'orologio reale.
TEST_DATE = os.getenv('TEST_DATE')

POSTS_DIR = Path('posts')
PUBLISHED_LOG = 'published.log'
REPO = 'michidrop80-Rebelde/sanmarinohappens'
FB_API = 'https://graph.facebook.com/v21.0'
TZ = ZoneInfo('Europe/San_Marino')


def oggi():
    if TEST_DATE:
        return datetime.strptime(TEST_DATE, '%Y-%m-%d').date()
    return datetime.now(TZ).date()


# ---------------------------------------------------------------------------
# Registro dei post gia' pubblicati (per-canale)
# Formato riga: "nomefile.png|ig" oppure "nomefile.png|fb".
# Retrocompatibilita': una riga vecchia SENZA "|" viene letta come "|ig"
# (prima esisteva solo Instagram), cosi' non si ripubblica su IG per sbaglio.
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


def gia_pubblicato(png_name, canale, pubblicati):
    return f"{png_name}|{canale}" in pubblicati


def log_published(png_name, canale):
    with open(PUBLISHED_LOG, 'a', encoding='utf-8') as f:
        f.write(f"{png_name}|{canale}\n")


def trova_post_di_oggi():
    """Cerca tra i JSON in posts/ quello/i con data_pubblicazione = oggi (col PNG presente)."""
    data_oggi = oggi().isoformat()
    trovati = []

    if not POSTS_DIR.exists():
        return trovati

    for json_file in sorted(POSTS_DIR.glob('*.json')):
        png_file = json_file.with_suffix('.png')
        if not png_file.exists():
            print(f"⚠️  {json_file.name} non ha il PNG corrispondente ({png_file.name}), salto.")
            continue
        with open(json_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if meta.get('data_pubblicazione') == data_oggi:
            trovati.append((png_file, meta))

    return trovati


# ---------------------------------------------------------------------------
# Instagram (graph.instagram.com) — pubblicazione in due passi
# ---------------------------------------------------------------------------
def ig_create_media_container(image_url, caption):
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media"
    payload = {'image_url': image_url, 'caption': caption, 'access_token': INSTAGRAM_TOKEN}
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return resp.json().get('id')
    print(f"Errore creazione container IG: {resp.status_code} - {resp.text}")
    return None


def ig_publish_media(creation_id):
    url = f"https://graph.instagram.com/{INSTAGRAM_USER_ID}/media_publish"
    payload = {'creation_id': creation_id, 'access_token': INSTAGRAM_TOKEN}
    resp = requests.post(url, data=payload)
    if resp.status_code == 200:
        return resp.json().get('id')
    print(f"Errore pubblicazione IG: {resp.status_code} - {resp.text}")
    return None


def pubblica_instagram(image_url, caption):
    """Ritorna l'id del media pubblicato, oppure None se fallisce."""
    container_id = ig_create_media_container(image_url, caption)
    if not container_id:
        return None
    return ig_publish_media(container_id)


# ---------------------------------------------------------------------------
# Facebook Pagina (graph.facebook.com) — pubblicazione foto in un passo
# ---------------------------------------------------------------------------
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


def pubblica_facebook(image_url, message):
    """Pubblica la foto sul feed della Pagina. Ritorna l'id del post, oppure None.
    Nota: il testo del post viaggia nel campo 'message'. Se al primo post reale il
    testo non dovesse comparire sotto la foto, provare a rinominare 'message' in
    'caption' (e' l'unico punto incerto della doc Meta per l'endpoint /photos)."""
    url = f"{FB_API}/{FACEBOOK_PAGE_ID}/photos"
    payload = {'url': image_url, 'message': message, 'access_token': FACEBOOK_PAGE_TOKEN}
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
    stato_fb = "attivo" if FB_ENABLED else "NON configurato (solo Instagram)"
    print(f"Modalita': {modalita} — Facebook: {stato_fb}")

    pubblicati = get_published()
    righe_report = []  # per la notifica Telegram riepilogativa

    for png_file, meta in trovati:
        caption = meta.get('caption', '')
        nome = png_file.name
        image_url = f"https://raw.githubusercontent.com/{REPO}/main/posts/{nome}"
        righe_report.append(f"• {nome}")

        # ---------- INSTAGRAM ----------
        if gia_pubblicato(nome, 'ig', pubblicati):
            print(f"IG: {nome} gia' pubblicato, salto.")
            righe_report.append("   IG: già pubblicato (salto)")
        elif not PUBLISH_LIVE:
            print(f"🧪 IG: simulerei la pubblicazione di {nome}")
            righe_report.append("   IG: 🧪 simulazione (non pubblicato)")
        else:
            print(f"IG: pubblico {nome}...")
            media_id = pubblica_instagram(image_url, caption)
            if media_id:
                print(f"✅ IG pubblicato: {media_id}")
                log_published(nome, 'ig')
                righe_report.append("   IG: ✅ pubblicato")
            else:
                righe_report.append("   IG: ❌ errore")

        # ---------- FACEBOOK ----------
        if not FB_ENABLED:
            righe_report.append("   FB: — non configurato")
        elif gia_pubblicato(nome, 'fb', pubblicati):
            print(f"FB: {nome} gia' pubblicato, salto.")
            righe_report.append("   FB: già pubblicato (salto)")
        elif not PUBLISH_LIVE:
            # In simulazione non pubblichiamo, ma verifichiamo DAVVERO che il token
            # Pagina funzioni con una chiamata di sola lettura.
            ok, dettaglio = fb_verifica_pagina()
            if ok:
                print(f"🧪 FB: simulerei la pubblicazione su «{dettaglio}» (token Pagina valido)")
                righe_report.append(f"   FB: 🧪 simulazione — token OK, Pagina «{dettaglio}»")
            else:
                print(f"🧪 FB: token Pagina NON valido → {dettaglio}")
                righe_report.append(f"   FB: ⚠️ token/Pagina non raggiungibile ({dettaglio})")
        else:
            print(f"FB: pubblico {nome}...")
            post_id = pubblica_facebook(image_url, caption)
            if post_id:
                print(f"✅ FB pubblicato: {post_id}")
                log_published(nome, 'fb')
                righe_report.append("   FB: ✅ pubblicato")
            else:
                righe_report.append("   FB: ❌ errore")

    intestazione = ("🟢 PUBBLICAZIONE LIVE" if PUBLISH_LIVE
                    else "🧪 SIMULAZIONE (nessun post reale)")
    if not FB_ENABLED and not PUBLISH_LIVE:
        intestazione += "\n(Facebook non ancora configurato: aggiungi i secret FACEBOOK_PAGE_TOKEN e FACEBOOK_PAGE_ID)"
    notifica_telegram(intestazione + "\n\n" + "\n".join(righe_report))


if __name__ == '__main__':
    if not INSTAGRAM_TOKEN or not INSTAGRAM_USER_ID:
        print("Errore: INSTAGRAM_TOKEN o INSTAGRAM_USER_ID non configurati.")
    else:
        main()
