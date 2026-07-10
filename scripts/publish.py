#!/usr/bin/env python3
"""
Script per pubblicare i post su Instagram E su Facebook (Pagina) tramite le API di Meta.

Ogni PNG in posts/ ha un file JSON gemello (stesso nome, estensione .json) con
la data di pubblicazione prevista e la caption.

QUANDO PUBBLICA (regola aggiornata — "robot affidabile"):
  Pubblica i post la cui data_pubblicazione e' <= oggi (fuso Europe/San_Marino) e
  non ancora pubblicati, PURCHE' il ritardo non superi la finestra di recupero
  GRACE_DAYS (default 2 giorni). Prima il match era ESATTO (solo == oggi): se il
  cron di GitHub slittava oltre mezzanotte, il post veniva perso PER SEMPRE in
  silenzio. Ora un post che slitta di un giorno viene RECUPERATO il giorno dopo.
  I post piu' vecchi della finestra sono considerati "scaduti": NON si pubblicano
  (sarebbe imbarazzante reclamizzare un evento gia' passato), ma Michele riceve un
  avviso Telegram. Anche le buste "anomale" (JSON illeggibile, PNG mancante, data
  non valida, caption vuota) vengono saltate e segnalate.

DUE BINARI INDIPENDENTI:
  - Instagram: sempre attivo (usa INSTAGRAM_TOKEN + INSTAGRAM_USER_ID, via graph.instagram.com).
  - Facebook (Pagina): si attiva SOLO se sono presenti i secret FACEBOOK_PAGE_TOKEN
    + FACEBOOK_PAGE_ID (via graph.facebook.com). Se mancano, Facebook viene semplicemente
    saltato e Instagram procede come sempre — cosi' aggiungere Facebook non rompe nulla.
  I due canali sono indipendenti: se uno fallisce, l'altro va avanti comunque. Il
  registro published.log tiene traccia SEPARATA dei due (righe "nomefile.png|ig" e
  "nomefile.png|fb"), cosi' un post finisce UNA SOLA VOLTA su ciascuna piattaforma
  anche se lo script viene rilanciato.

ARCHIVIAZIONE (solo in LIVE): quando un post e' stato pubblicato con successo su
  TUTTI i canali attivi, il suo PNG + JSON vengono spostati da posts/ ad
  archivio/AAAA-MM/ nello stesso repo. Cosi' la cartella posts/ resta la "coda"
  (solo cio' che deve ancora uscire) e lo storico non va perso. Gli originali
  restano comunque sul Mac di Michele (marketing/3 Export/). Nessuno spazio cloud
  a pagamento: e' tutto dentro il repo GitHub (gratis).

INTERRUTTORE DI SICUREZZA: se la variabile d'ambiente PUBLISH_LIVE non e'
  esattamente "true", lo script gira in modalita' SIMULAZIONE — fa tutto (trova
  i post di oggi, prepara la caption, segnala scaduti/anomali, manda una notifica
  Telegram) TRANNE pubblicare per davvero e archiviare. In simulazione, se Facebook
  e' configurato, lo script fa una chiamata di SOLA LETTURA alla Pagina per
  confermare che il token e' valido. Per andare live: Variable di repository
  PUBLISH_LIVE=true su GitHub (Settings -> Secrets and variables -> Actions -> Variables).
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

# Finestra di recupero: quanti giorni di ritardo tolleriamo prima di considerare
# una busta "scaduta". Serve a recuperare un cron che slitta oltre mezzanotte SENZA
# ripubblicare per sbaglio eventi di settimane prima. Default 2, sovrascrivibile via env.
try:
    GRACE_DAYS = int(os.getenv('GRACE_DAYS', '2'))
except ValueError:
    GRACE_DAYS = 2

POSTS_DIR = Path('posts')
ARCHIVIO_DIR = Path('archivio')
PUBLISHED_LOG = 'published.log'
REPO = 'michidrop80-Rebelde/sanmarinohappens'
FB_API = 'https://graph.facebook.com/v21.0'
TZ = ZoneInfo('Europe/San_Marino')


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


def segna_pubblicato(png_name, canale, pubblicati):
    """Registra su published.log E aggiorna l'insieme in memoria, cosi' il
    controllo di 'completo su tutti i canali' (archiviazione) resta coerente."""
    with open(PUBLISHED_LOG, 'a', encoding='utf-8') as f:
        f.write(f"{png_name}|{canale}\n")
    pubblicati.add(f"{png_name}|{canale}")


def canali_richiesti():
    """I canali su cui un post DEVE uscire per considerarsi 'completo'.
    Instagram sempre; Facebook solo se configurato."""
    canali = ['ig']
    if FB_ENABLED:
        canali.append('fb')
    return canali


# ---------------------------------------------------------------------------
# Smistamento delle buste in coda
# ---------------------------------------------------------------------------
def classifica_buste():
    """Scorre i JSON in posts/ e li smista in categorie in base alla data_pubblicazione:
      - da_pubblicare: data tra (oggi - GRACE_DAYS) e oggi inclusi, busta valida col PNG.
        Comprende i post 'in ritardo' recuperati (giorni_ritardo > 0) dopo uno slittamento.
      - scaduti: data piu' vecchia di GRACE_DAYS -> NON si pubblicano (troppo tardi), solo avviso.
      - anomali: JSON illeggibile, PNG mancante, data assente/malformata o caption vuota.
      - futuri (data > oggi): ignorati in silenzio, non e' ancora il loro momento.
    Ritorna (da_pubblicare, scaduti, anomali).
      da_pubblicare / scaduti = liste di (png_file, meta, giorni_ritardo)
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
        # 2) PNG presente?
        png_file = json_file.with_suffix('.png')
        if not png_file.exists():
            anomali.append((json_file.name, f"manca il PNG {png_file.name}"))
            continue
        # 3) data valida?
        data_pub = parse_data(meta.get('data_pubblicazione'))
        if data_pub is None:
            anomali.append((json_file.name,
                            f"data_pubblicazione assente o non valida: {meta.get('data_pubblicazione')!r}"))
            continue
        # 4) caption presente?
        if not (meta.get('caption') or '').strip():
            anomali.append((json_file.name, "caption vuota"))
            continue
        # 5) smistamento per data
        giorni_ritardo = (data_oggi - data_pub).days
        if giorni_ritardo < 0:
            continue  # futuro: non e' ancora il momento, si ignora in silenzio
        elif giorni_ritardo <= GRACE_DAYS:
            da_pubblicare.append((png_file, meta, giorni_ritardo))
        else:
            scaduti.append((png_file, meta, giorni_ritardo))

    return da_pubblicare, scaduti, anomali


# ---------------------------------------------------------------------------
# Archiviazione (solo LIVE, solo a post completo)
# ---------------------------------------------------------------------------
def archivia_busta(png_file, meta):
    """Sposta PNG + JSON gemello da posts/ ad archivio/AAAA-MM/ (stesso repo).
    AAAA-MM viene dalla data_pubblicazione. Chiamata SOLO in LIVE, dopo che il post
    e' stato pubblicato su tutti i canali attivi. Ritorna la cartella di destinazione,
    o None se qualcosa va storto (non deve bloccare il resto)."""
    data_pub = parse_data(meta.get('data_pubblicazione'))
    if data_pub is None:
        return None
    dest = ARCHIVIO_DIR / f"{data_pub.year:04d}-{data_pub.month:02d}"
    dest.mkdir(parents=True, exist_ok=True)
    json_file = png_file.with_suffix('.json')
    try:
        for f in (png_file, json_file):
            if f.exists():
                f.rename(dest / f.name)
    except OSError as e:
        print(f"⚠️  Archiviazione di {png_file.name} fallita: {e}")
        return None
    return dest


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
    da_pubblicare, scaduti, anomali = classifica_buste()

    # Se non c'e' proprio nulla di cui parlare (nessun post di oggi, niente scaduto,
    # niente anomalo — al massimo post futuri ancora in attesa), restiamo in silenzio.
    if not da_pubblicare and not scaduti and not anomali:
        print(f"Nessuna busta da pubblicare, scaduta o anomala per oggi ({oggi().isoformat()}). Niente da fare.")
        return

    modalita = "🟢 LIVE" if PUBLISH_LIVE else "🧪 SIMULAZIONE (PUBLISH_LIVE non attivo)"
    stato_fb = "attivo" if FB_ENABLED else "NON configurato (solo Instagram)"
    print(f"Modalita': {modalita} — Facebook: {stato_fb} — finestra recupero: {GRACE_DAYS} giorni")

    pubblicati = get_published()
    righe_report = []  # per la notifica Telegram riepilogativa

    for png_file, meta, giorni_ritardo in da_pubblicare:
        caption = meta.get('caption', '')
        nome = png_file.name
        image_url = f"https://raw.githubusercontent.com/{REPO}/main/posts/{nome}"
        etichetta_ritardo = "" if giorni_ritardo == 0 else f"  ⏰ IN RITARDO di {giorni_ritardo}g (recuperato)"
        righe_report.append(f"• {nome}{etichetta_ritardo}")

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
                segna_pubblicato(nome, 'ig', pubblicati)
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
                segna_pubblicato(nome, 'fb', pubblicati)
                righe_report.append("   FB: ✅ pubblicato")
            else:
                righe_report.append("   FB: ❌ errore")

        # ---------- ARCHIVIAZIONE (solo LIVE, solo a post completo) ----------
        # Un post e' "completo" quando risulta pubblicato su tutti i canali attivi
        # (IG sempre; FB se configurato). Solo allora lo togliamo dalla coda posts/
        # e lo mettiamo in archivio/AAAA-MM/. In simulazione non si archivia mai.
        if PUBLISH_LIVE:
            completo = all(gia_pubblicato(nome, c, pubblicati) for c in canali_richiesti())
            if completo:
                dest = archivia_busta(png_file, meta)
                if dest:
                    print(f"📦 {nome} archiviato in {dest.as_posix()}/")
                    righe_report.append(f"   📦 archiviato in {dest.as_posix()}/")

    # ---------- SEZIONI DI AVVISO (scaduti / anomali) ----------
    if scaduti:
        if righe_report:
            righe_report.append("")
        righe_report.append(f"⚠️ BUSTE SCADUTE (NON pubblicate, oltre {GRACE_DAYS}g di ritardo):")
        for png_file, meta, giorni_ritardo in scaduti:
            righe_report.append(
                f"   • {png_file.name} — prevista {meta.get('data_pubblicazione')} "
                f"({giorni_ritardo}g fa) → aggiorna la data nel piano o rimuovila dalla coda"
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
