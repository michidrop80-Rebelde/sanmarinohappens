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

RILETTURA DEL PROFILO — la regola piu' importante di questo file (06/08/2026):
  **Un errore di scrittura di Meta NON prova che la scrittura non sia avvenuta.**
  media_publish puo' rispondere 403 «action is blocked» e pubblicare il post lo stesso.
  Prima che ce ne accorgessimo, il robot dava per fallito un post uscito davvero, non
  lo scriveva in published.log e lo ripubblicava al giro dopo: 5 contenuti finiti sul
  profilo in 19 copie (fino a 7 dello stesso post). Il "blocco" anti-spam di Meta era
  la REAZIONE ai doppioni, non la causa — token valido, quota 1 su 100, letture OK.
  Ora, dopo ogni errore su Instagram, si rilegge il profilo (ig_gia_uscito):
    - il contenuto c'e'  -> si segna come pubblicato, non si ripubblica
    - non c'e'           -> fallimento vero
    - non si e' potuto controllare -> "non lo so", che NON e' "non e' uscito": ci si
      ferma comunque, perche' insistere al buio e' cio' che ha creato i doppioni.

FRENO INSTAGRAM (aggiunto 06/08/2026, dopo il blocco del 03-06/08):
  Quando Meta risponde "action is blocked" (code 4 / subcode 2207051) NON e' la busta
  a essere sbagliata: e' Instagram che ha chiuso, e riprovare peggiora le cose (ogni
  tentativo ricarica le immagini creando un "contenitore" che resta orfano — in 3
  giorni ne erano rimasti 104+, cioe' il profilo di comportamento che i sistemi
  anti-spam puniscono). Al primo blocco il reparto colpito va in pausa per 24h; alla
  scadenza si riprova UNA volta sola. Lo stato vive in stato/instagram.json (versionato,
  cosi' una run di GitHub Actions si ricorda cosa ha visto la precedente).
  I reparti sono DUE e indipendenti — 'feed' (foto + caroselli) e 'storie' — perche'
  nel guasto vero il feed era chiuso mentre le storie uscivano regolarmente.
  Gli AGGREGATI (settimanale/weekend/carosello) non scadono mentre il feed e' bloccato,
  purche' il contenuto sia ancora sensato (VALIDITA_AGGREGATO_GIORNI); i post del giorno
  scadono lo stesso, perche' «oggi c'e' X» pubblicato giorni dopo e' falso.

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
from datetime import datetime, timedelta
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

# Tag utente Instagram: si taggano SOLO i contenuti di un singolo evento.
# Gli aggregati (settimanale, weekend, carosello) contengono 5-10 eventi:
# taggarne alcuni sarebbe una preferenza arbitraria, contro la regola di equita'.
TIPI_TAGGABILI = {'giornaliero', 'storia'}
MAX_TAG_PER_IMMAGINE = 3

# Tag rifiutati da Instagram e ripubblicati senza: righe per il riepilogo Telegram.
TAG_SALTATI = []

# ---------------------------------------------------------------------------
# FRENO INSTAGRAM ("action is blocked") — aggiunto 06/08/2026
# ---------------------------------------------------------------------------
# Dal 03/08 al 06/08/2026 Instagram ha rifiutato OGNI post nel feed con
#   403 · code 4 · subcode 2207051 · "Application request limit reached / action is blocked"
# mentre le Storie IG e Facebook uscivano regolarmente. Il robot non lo capiva e
# riprovava 4 volte al giorno: ogni tentativo ricaricava tutte le immagini (un
# "contenitore" ciascuna) per poi prendersi il 403. In 3 giorni: 104+ contenitori
# creati e mai pubblicati — cioe' esattamente il comportamento che i sistemi
# anti-spam di Meta puniscono. Il blocco si autoalimentava.
#
# Il freno spezza il circolo: al primo 403 di questo tipo il feed IG si ferma per
# 24 ore (Storie e Facebook proseguono, sono su binari indipendenti). Alla
# scadenza si riprova UNA volta sola: se passa, il freno si sgancia; se no, altre
# 24 ore. Da 20 tentativi al giorno a 1.
IG_BLOCCO_FILE = Path('stato/instagram.json')
IG_PAUSA_ORE = 24
# I codici con cui Meta dice "questa azione e' bloccata" (non "questo contenuto e'
# sbagliato": una caption troppo lunga NON deve far scattare il freno).
IG_CODICI_BLOCCO = {4}
IG_SOTTOCODICI_BLOCCO = {2207051}
# Il freno e' per REPARTO, non per tutto Instagram: nel guasto del 03-06/08 il feed
# era chiuso mentre le storie uscivano regolarmente, e fermare anche quelle sarebbe
# stato un danno gratuito. Due freni indipendenti, stesso meccanismo: cosi' se un
# domani Meta chiude le storie non ricominciamo a martellare dalla porta accanto.
IG_KIND_FEED = {'foto', 'carosello'}
IG_REPARTI = ('feed', 'storie')

# Ultimo errore restituito da Meta su una chiamata IG. Riempito dalle funzioni di
# pubblicazione, letto da main(): evita di cambiare la firma di mezzo file solo
# per far risalire un codice di errore.
IG_ULTIMO_ERRORE = {}

# Quante volte il feed IG e' gia' stato saltato in questo giro (per il report).
IG_SALTATI = []
# Contenuti che Instagram ha dato per falliti ma che erano usciti davvero: senza la
# rilettura sarebbero diventati altrettanti doppioni al giro successivo.
RILETTURE_SALVATE = []


def oggi():
    if TEST_DATE:
        return datetime.strptime(TEST_DATE, '%Y-%m-%d').date()
    return datetime.now(TZ).date()


def ora_corrente():
    """Ritorna l'ora corrente 'HH:MM' nel fuso Europe/San_Marino. TEST_DATE da solo
    finge fine giornata (TEST_TIME default '23:59') cosi' un test che forza solo la
    data continua a pubblicare tutto cio' che e' datato per quel giorno, indipendente
    dall'ora_pubblicazione della busta; TEST_TIME permette di testare anche il caso
    'non ancora ora' (es. TEST_TIME=08:00 con una busta delle 18:00)."""
    if TEST_DATE:
        return os.getenv('TEST_TIME', '23:59')
    return datetime.now(TZ).strftime('%H:%M')


def parse_data(s):
    """Ritorna un date da 'AAAA-MM-GG', oppure None se il formato non e' valido."""
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def parse_ora(s):
    """Ritorna 'HH:MM' se il valore e' un orario valido, altrimenti None (campo
    assente/malformato = nessun vincolo d'orario, per retrocompatibilita' con le
    buste vecchie create prima di questo campo)."""
    if not isinstance(s, str) or not re.match(r'^([01]\d|2[0-3]):[0-5]\d$', s.strip()):
        return None
    return s.strip()


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
def tag_per_immagine(meta, chiave):
    """Tag utente della SINGOLA immagine 'chiave'. Lista vuota se la busta non ha
    tag o non ne ha per quell'immagine. Una busta 'storia' pubblica piu' storie di
    eventi diversi: i tag sono per immagine, mai per busta."""
    if not isinstance(meta, dict):
        return []
    mappa = meta.get('user_tags')
    if not isinstance(mappa, dict):
        return []
    tags = mappa.get(chiave)
    return tags if isinstance(tags, list) else []


def costruisci_unita(tipo, json_file, immagini, meta=None):
    if tipo in TIPI_FOTO_SINGOLA:
        chiave = immagini[0].name
        return [{'kind': 'foto', 'chiave': chiave,
                 'immagini': [immagini[0]], 'etichetta': 'foto',
                 'user_tags': tag_per_immagine(meta, chiave)}]
    if tipo == 'carosello':
        # gli aggregati non si taggano: user_tags resta vuoto per costruzione
        return [{'kind': 'carosello', 'chiave': json_file.stem,
                 'immagini': list(immagini), 'etichetta': f'carosello ({len(immagini)} foto)',
                 'user_tags': []}]
    if tipo == 'storia':
        n = len(immagini)
        return [{'kind': 'storia', 'chiave': img.name, 'immagini': [img],
                 'etichetta': f'storia {i}/{n}',
                 'user_tags': tag_per_immagine(meta, img.name)}
                for i, img in enumerate(immagini, 1)]
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
# Guardia FORMATO: lunghezza della caption (limite Instagram)
# ---------------------------------------------------------------------------
# Instagram rifiuta le caption oltre 2200 caratteri con l'errore 36004 "The caption
# was too long", e lo fa DOPO che il post e' partito: il container non viene creato,
# la busta resta in coda e il robot ci riprova a ogni giro senza mai riuscire.
# E' successo davvero col carosello di Agosto (02/08/2026): caption di 2407
# caratteri, uscita su Facebook (che ha un limite molto piu' alto) e MAI su
# Instagram, 12 tentativi falliti di fila. Meglio saperlo qui, dove la busta viene
# marcata "anomala" e finisce nell'avviso Telegram, che scoprirlo dai log di Actions.
# Si conta in unita' UTF-16 (il modo piu' severo: gli emoji possono valere 2), con un
# piccolo margine, cosi' il controllo non e' mai piu' permissivo di quello di Meta.
IG_CAPTION_MAX = 2200


def lunghezza_caption(caption):
    """Lunghezza della caption in unita' UTF-16 (come la conta Meta nel caso peggiore)."""
    return len((caption or '').encode('utf-16-le')) // 2


def tag_anomalie(meta, tipo, immagini):
    """Controlla il campo 'user_tags' di una busta. Ritorna la lista dei problemi
    (vuota = tutto a posto). E' la rete AUTOMATICA lato GitHub, gemella del
    controllo che /smh-check fa sul Mac: qui verifichiamo solo la FORMA (il robot
    non ha il registro degli handle, che vive sul Mac), sul Mac si verifica che
    ogni handle sia davvero registrato e pertinente.

    Forma attesa: {'nome-immagine.png': [{'username': str, 'x': float, 'y': float}]}
    """
    mappa = meta.get('user_tags')
    if mappa is None:
        return []                      # busta senza tag: e' il caso normale
    if not isinstance(mappa, dict):
        return ["user_tags non e' un dizionario nome-immagine -> lista di tag"]

    problemi = []
    if tipo not in TIPI_TAGGABILI:
        problemi.append(f"user_tags su tipo '{tipo}': gli aggregati non si taggano")

    nomi_immagini = {p.name for p in immagini}
    for chiave, tags in mappa.items():
        if chiave not in nomi_immagini:
            problemi.append(f"user_tags: chiave orfana '{chiave}' "
                            "(nessuna immagine della busta si chiama cosi')")
            continue
        if not isinstance(tags, list):
            problemi.append(f"user_tags['{chiave}'] non e' una lista")
            continue
        if len(tags) > MAX_TAG_PER_IMMAGINE:
            problemi.append(f"user_tags['{chiave}']: {len(tags)} tag "
                            f"(massimo {MAX_TAG_PER_IMMAGINE})")
        for t in tags:
            if not isinstance(t, dict) or not str(t.get('username') or '').strip():
                problemi.append(f"user_tags['{chiave}']: tag senza username")
                continue
            for asse in ('x', 'y'):
                v = t.get(asse)
                # attenzione: in Python True e' un int, va escluso esplicitamente
                if isinstance(v, bool) or not isinstance(v, (int, float)) or not (0.0 <= v <= 1.0):
                    problemi.append(f"user_tags['{chiave}'] @{t.get('username')}: "
                                    f"{asse}={v!r} fuori dall'intervallo 0.0-1.0")
    return problemi


# ---------------------------------------------------------------------------
# Freno Instagram: riconoscere il blocco e ricordarselo fra una run e l'altra
# ---------------------------------------------------------------------------
def errore_e_blocco_ig(errore):
    """True se l'errore Meta e' un blocco dell'AZIONE (non un contenuto sbagliato).
    Distinzione che conta: 'caption troppo lunga' (36004) si risolve correggendo la
    busta e riprovare ha senso; 'action is blocked' (4 / 2207051) NON si risolve
    riprovando — riprovare lo peggiora."""
    if not isinstance(errore, dict):
        return False
    return (errore.get('code') in IG_CODICI_BLOCCO
            or errore.get('error_subcode') in IG_SOTTOCODICI_BLOCCO)


def _registra_errore_ig(resp):
    """Memorizza l'errore Meta dell'ultima chiamata IG andata male."""
    global IG_ULTIMO_ERRORE
    try:
        IG_ULTIMO_ERRORE = (resp.json() or {}).get('error', {}) or {}
    except (ValueError, AttributeError):
        IG_ULTIMO_ERRORE = {}


def reparto_ig(kind):
    """A quale freno risponde questa unita': 'feed' (foto e caroselli) o 'storie'."""
    return 'feed' if kind in IG_KIND_FEED else 'storie'


def _leggi_stato_ig():
    """Tutto il file di stato: {'feed': {...}, 'storie': {...}}."""
    try:
        with open(IG_BLOCCO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f) or {}
    except (OSError, json.JSONDecodeError):
        return {}


def leggi_freno_ig(reparto='feed'):
    """Lo stato di UN reparto, o {} se quel reparto non e' bloccato."""
    dati = _leggi_stato_ig().get(reparto)
    return dati if isinstance(dati, dict) else {}


def stato_freno_ig(reparto='feed'):
    """Tre stati, come un semaforo:
      'libero'        -> nessun blocco noto, si pubblica normalmente
      'in-pausa'      -> blocco attivo, quel reparto non si tocca (zero chiamate)
      'prova-singola' -> la pausa e' scaduta: si riprova UNA volta sola, e in base
                         all'esito il freno si sgancia o si riarma per altre 24h
    """
    dati = leggi_freno_ig(reparto)
    if not dati.get('riprova_dopo'):
        return 'libero'
    try:
        riprova_dopo = datetime.fromisoformat(dati['riprova_dopo'])
    except ValueError:
        return 'libero'
    return 'in-pausa' if datetime.now(TZ) < riprova_dopo else 'prova-singola'


def ig_bloccato_del_tutto():
    """True se NESSUN reparto Instagram e' pubblicabile in questo momento."""
    return all(stato_freno_ig(r) != 'libero' for r in IG_REPARTI)


def arma_freno_ig(motivo, reparto='feed'):
    """Ferma un reparto IG per IG_PAUSA_ORE. Tiene il conto dei tentativi falliti:
    se il numero cresce di giorno in giorno, il blocco non e' un incidente."""
    tutto = _leggi_stato_ig()
    dati = tutto.get(reparto) if isinstance(tutto.get(reparto), dict) else {}
    adesso = datetime.now(TZ)
    dati['bloccato_dal'] = dati.get('bloccato_dal') or adesso.isoformat()
    dati['ultimo_blocco'] = adesso.isoformat()
    dati['riprova_dopo'] = (adesso + timedelta(hours=IG_PAUSA_ORE)).isoformat()
    dati['tentativi_falliti'] = int(dati.get('tentativi_falliti', 0)) + 1
    dati['motivo'] = motivo
    tutto[reparto] = dati
    IG_BLOCCO_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(IG_BLOCCO_FILE, 'w', encoding='utf-8') as f:
        json.dump(tutto, f, ensure_ascii=False, indent=2)
    return dati


def sgancia_freno_ig(reparto='feed'):
    """Quel reparto ha ripubblicato: il suo blocco e' finito."""
    tutto = _leggi_stato_ig()
    tutto.pop(reparto, None)
    try:
        if tutto:
            with open(IG_BLOCCO_FILE, 'w', encoding='utf-8') as f:
                json.dump(tutto, f, ensure_ascii=False, indent=2)
        else:
            IG_BLOCCO_FILE.unlink()
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Rilettura del profilo: un errore di scrittura NON prova che il post non sia uscito
# ---------------------------------------------------------------------------
# Scoperta del 06/08/2026: media_publish puo' rispondere 403 «action is blocked» e
# pubblicare il post lo stesso. Il robot lo dava per fallito, non lo segnava in
# published.log e lo ripubblicava al giro dopo: 5 contenuti finiti sul profilo in
# 19 copie. Da qui la regola: prima di dichiarare fallito qualcosa, si guarda.
def _normalizza_caption(testo):
    """Meta restituisce la didascalia con spaziatura sua: confrontiamo il testo
    'compattato', non carattere per carattere."""
    return ' '.join((testo or '').split())[:120]


def _leggi_edge_ig(edge, campi, limite=10):
    """GET di sola lettura sul profilo. Ritorna la lista, o None se non si e'
    riusciti a leggere (che NON e' la stessa cosa di 'lista vuota')."""
    try:
        r = requests.get(f"{IG_API}/{INSTAGRAM_USER_ID}/{edge}",
                         params={'fields': campi, 'limit': limite,
                                 'access_token': INSTAGRAM_TOKEN}, timeout=30)
    except requests.RequestException as e:
        print(f"⚠️ Rilettura profilo IG ({edge}) non riuscita — rete: {e}")
        return None
    if r.status_code != 200:
        print(f"⚠️ Rilettura profilo IG ({edge}) non riuscita: "
              f"{r.status_code} - {r.text[:200]}")
        return None
    try:
        return r.json().get('data') or []
    except ValueError:
        print(f"⚠️ Rilettura profilo IG ({edge}): risposta non leggibile.")
        return None


def ig_gia_uscito(kind, caption, iniziato):
    """Dopo un errore su Instagram: il contenuto e' uscito lo stesso?
    Ritorna (True, permalink) se e' sul profilo, (False, None) se non c'e',
    (None, None) se NON siamo riusciti a controllare.
    I tre casi sono diversi apposta: 'non lo so' non deve mai essere trattato come
    'non e' uscito', altrimenti si torna a creare doppioni.
    `iniziato` e' l'istante subito prima del tentativo: serve a non scambiare per
    nostro un post identico pubblicato giorni fa."""
    if kind == 'storia':
        # Le storie non hanno didascalia e non compaiono in /media: l'unica cosa
        # che possiamo confrontare e' l'orario. Regge perche' su questo account
        # pubblica solo il robot, una unita' per volta.
        voci = _leggi_edge_ig('stories', 'id,timestamp')
    else:
        voci = _leggi_edge_ig('media', 'id,timestamp,permalink,caption')
    if voci is None:
        return None, None

    atteso = _normalizza_caption(caption)
    margine = iniziato - timedelta(seconds=60)
    for v in voci:
        try:
            quando = datetime.strptime(v.get('timestamp', ''), '%Y-%m-%dT%H:%M:%S%z')
        except (ValueError, TypeError):
            continue
        if quando < margine:
            continue  # troppo vecchio: non e' il tentativo di adesso
        if kind == 'storia' or _normalizza_caption(v.get('caption')) == atteso:
            return True, v.get('permalink')
    return False, None


def riconcilia_con_profilo(buste, pubblicati):
    """PASSO 0: cio' che e' in coda e' gia' sul profilo?

    Serve perche' i doppioni del 03-06/08 hanno lasciato una situazione storta: post
    usciti (anche 7 volte) ma MAI scritti in published.log, perche' Meta aveva
    risposto errore. Senza questo passo, al primo giro utile il robot li
    ripubblicherebbe un'altra volta — la rilettura post-tentativo non basta, perche'
    guarda solo cio' che compare DOPO il tentativo.

    Confronta la didascalia di ogni busta in coda con quelle presenti sul profilo,
    senza finestra temporale: se c'e', si segna come gia' pubblicata su IG.
    Ritorna la lista delle righe da mostrare nel riepilogo. Sola lettura verso Meta.
    Le storie restano fuori: non hanno didascalia da confrontare e durano 24h."""
    righe = []
    da_controllare = [b for b in buste if b['tipo'] != 'storia']
    if not da_controllare:
        return righe

    voci = _leggi_edge_ig('media', 'id,timestamp,permalink,caption', limite=50)
    if voci is None:
        righe.append("⚠️ Non sono riuscito a rileggere il profilo Instagram: "
                     "non posso escludere che qualcosa in coda sia già uscito.")
        return righe

    sul_profilo = {}
    for v in voci:
        chiave = _normalizza_caption(v.get('caption'))
        if chiave and chiave not in sul_profilo:
            sul_profilo[chiave] = v

    for busta in da_controllare:
        caption = (busta['meta'].get('caption') or '').strip()
        trovato = sul_profilo.get(_normalizza_caption(caption))
        if not trovato:
            continue
        unita = costruisci_unita(busta['tipo'], busta['json_file'],
                                 busta['immagini'], busta['meta'])
        nuove = [u for u in unita if not gia_pubblicato(u['chiave'], 'ig', pubblicati)]
        if not nuove:
            continue
        for u in nuove:
            segna_pubblicato(u['chiave'], 'ig', pubblicati)
        titolo = busta['meta'].get('titolo_evento', busta['json_file'].stem)
        print(f"🔎 Riconciliazione: «{titolo}» era GIA' su Instagram "
              f"({trovato.get('permalink')}) ma non risultava. Segnato, non ripubblico.")
        righe.append(f"   • {titolo} — già su Instagram ({trovato.get('permalink')})")
    return righe


def salta_per_freno_ig(kind):
    """True se questa unita' NON va nemmeno tentata su Instagram adesso."""
    return stato_freno_ig(reparto_ig(kind)) == 'in-pausa'


def quando_riprova_ig(reparto='feed'):
    """Testo leggibile ('07/08 alle 07:00') per il riepilogo Telegram."""
    try:
        d = datetime.fromisoformat(leggi_freno_ig(reparto)['riprova_dopo'])
    except (KeyError, ValueError, TypeError):
        return "al prossimo giro"
    return d.strftime('%d/%m alle %H:%M')


# ---------------------------------------------------------------------------
# Smistamento delle buste in coda
# ---------------------------------------------------------------------------
# Aggregati: parlano di piu' giorni, quindi hanno senso anche in ritardo. I post
# del giorno no — «oggi c'e' X» pubblicato cinque giorni dopo e' semplicemente
# falso, e infatti Michele ha scelto di lasciarli scadere (decisione 06/08/2026).
TIPI_AGGREGATI = {'settimanale', 'weekend', 'carosello'}
# Fin quando un aggregato resta sensato, contato dalla sua data di pubblicazione.
# Non e' una stima: viene dal calendario editoriale (il weekend esce il giovedi per
# sab+dom, il settimanale la domenica sera per i 7 giorni dopo, il carosello
# l'ultimo giorno del mese precedente per tutto il mese).
VALIDITA_AGGREGATO_GIORNI = {'weekend': 3, 'settimanale': 8, 'carosello': 32}


def classifica_buste():
    """Scorre i JSON in posts/ e li smista in base a validita', data_pubblicazione e
    ora_pubblicazione:
      - da_pubblicare: data tra (oggi - GRACE_DAYS) e oggi inclusi, busta valida, E
        se e' proprio oggi (giorni_ritardo == 0) l'ora corrente ha gia' raggiunto
        l'ora_pubblicazione della busta (altrimenti aspetta il run successivo -
        es. un weekend delle 18:00 non deve uscire al giro delle 7:00). Un ritardo
        di 1+ giorni non aspetta piu' l'ora: e' gia' in recupero, esce appena trovato.
      - scaduti: data piu' vecchia di GRACE_DAYS -> NON si pubblicano, solo avviso.
        ATTENZIONE: qui dentro finiscono anche buste che erano gia' USCITE davvero
        (published.log non viene letto in questa funzione). A separarle ci pensa
        separa_gia_pubblicate() in main(): quelle si archiviano, non si segnalano.
      - in_attesa: aggregati oltre GRACE_DAYS che pero' NON sono colpa loro — il
        feed Instagram e' bloccato (freno armato) e il contenuto e' ancora sensato.
        Restano in coda senza scadere finche' il blocco dura; non si tenta nulla.
      - anomali: JSON illeggibile, tipo sconosciuto, immagini mancanti/fuori range,
        data assente/malformata, caption vuota (dove serve).
      - futuri (data > oggi, o data == oggi ma ora_pubblicazione non ancora arrivata):
        ignorati in silenzio.
    Ritorna (da_pubblicare, scaduti, anomali, in_attesa).
      da_pubblicare / scaduti / in_attesa = liste di dict
        {json_file, meta, tipo, immagini, giorni_ritardo}
      anomali = lista di (nome_json, motivo)
    """
    data_oggi = oggi()
    ora_adesso = ora_corrente()
    da_pubblicare, scaduti, anomali, in_attesa = [], [], [], []
    # Il freno si legge UNA volta sola: se cambiasse a meta' giro, meta' buste
    # verrebbero giudicate con una regola e meta' con un'altra. Gli aggregati sono
    # contenuti da feed, quindi e' il freno del feed a decidere se aspettarli.
    ig_bloccato = stato_freno_ig('feed') != 'libero'

    if not POSTS_DIR.exists():
        return da_pubblicare, scaduti, anomali, in_attesa

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
            # 6a-bis) caption troppo lunga per Instagram? -> blocca e segnala QUI,
            # invece di farla rifiutare da Meta a ogni giro senza che nessuno lo veda.
            n_car = lunghezza_caption(caption_txt)
            if n_car > IG_CAPTION_MAX:
                anomali.append((json_file.name,
                                f"caption troppo lunga per Instagram: {n_car} caratteri "
                                f"(limite {IG_CAPTION_MAX}) — accorciala di almeno "
                                f"{n_car - IG_CAPTION_MAX}"))
                continue
            # 6b) PREZZI/GRATUITA' in caption? Regola equita' -> blocca e segnala.
            prezzi = caption_prezzi(caption_txt)
            if prezzi:
                anomali.append((json_file.name,
                                "prezzo/gratuità in caption (regola equità, i costi vanno solo "
                                f"nel link in bio): «{'», «'.join(prezzi)}»"))
                continue
        # 6c) TAG UTENTE malformati? -> blocca e segnala (vale anche per le storie,
        # che non passano dal controllo caption qui sopra).
        problemi_tag = tag_anomalie(meta, tipo, immagini)
        if problemi_tag:
            anomali.append((json_file.name, "tag utente: " + " · ".join(problemi_tag)))
            continue
        # 7) smistamento per data (+ ora, solo se e' proprio oggi)
        giorni_ritardo = (data_oggi - data_pub).days
        busta = {'json_file': json_file, 'meta': meta, 'tipo': tipo,
                 'immagini': immagini, 'giorni_ritardo': giorni_ritardo}
        if giorni_ritardo < 0:
            continue  # futuro: non e' ancora il giorno
        elif giorni_ritardo == 0:
            ora_pub = parse_ora(meta.get('ora_pubblicazione'))
            if ora_pub is not None and ora_adesso < ora_pub:
                continue  # e' oggi ma non ancora l'ora (es. weekend delle 18:00 al run delle 7:00)
            da_pubblicare.append(busta)
        elif giorni_ritardo <= GRACE_DAYS:
            da_pubblicare.append(busta)  # in recupero: l'ora non conta piu', esce appena trovata
        elif (ig_bloccato and tipo in TIPI_AGGREGATI
              and giorni_ritardo <= VALIDITA_AGGREGATO_GIORNI[tipo]):
            # Non e' in ritardo per colpa nostra: Instagram e' chiuso. Finche' il
            # contenuto copre giorni ancora da venire lo teniamo in vita, cosi' un
            # carosello del mese in corso non muore per un blocco di 3 giorni.
            in_attesa.append(busta)
        else:
            scaduti.append(busta)

    return da_pubblicare, scaduti, anomali, in_attesa


# ---------------------------------------------------------------------------
# Archiviazione (solo LIVE, solo a post completo)
# ---------------------------------------------------------------------------
def archivia_busta(json_file, immagini, meta, sottocartella=None):
    """Sposta JSON + TUTTE le immagini da posts/ ad archivio/AAAA-MM/ (stesso repo).
    AAAA-MM viene dalla data_pubblicazione. Chiamata SOLO in LIVE, a post completo su
    tutti i canali attivi. Ritorna la cartella di destinazione, o None se qualcosa va
    storto (non deve bloccare il resto).

    `sottocartella` inserisce un livello prima di AAAA-MM (es. 'non-pubblicati'). Serve
    perche' archivio/AAAA-MM/ vuol dire «questo e' uscito»: mettere lì una busta mai
    pubblicata renderebbe l'archivio una prova falsa per chi lo guarda."""
    data_pub = parse_data(meta.get('data_pubblicazione'))
    if data_pub is None:
        return None
    dest = ARCHIVIO_DIR
    if sottocartella:
        dest = dest / sottocartella
    dest = dest / f"{data_pub.year:04d}-{data_pub.month:02d}"
    dest.mkdir(parents=True, exist_ok=True)
    try:
        for f in [json_file, *immagini]:
            if f.exists():
                f.rename(dest / f.name)
    except OSError as e:
        print(f"⚠️  Archiviazione di {json_file.name} fallita: {e}")
        return None
    return dest


def busta_completa(busta, pubblicati):
    """True se TUTTE le unita' della busta risultano gia' pubblicate su TUTTI i canali
    attivi, secondo published.log. Stessa definizione di "completo" usata per archiviare
    una busta appena pubblicata: qui pero' si guarda solo lo storico, senza pubblicare."""
    unita = costruisci_unita(busta['tipo'], busta['json_file'],
                             busta['immagini'], busta['meta'])
    if not unita:
        return False
    return all(gia_pubblicato(u['chiave'], c, pubblicati)
               for u in unita for c in canali_richiesti())


def busta_mai_uscita(busta, pubblicati):
    """True se NESSUNA unita' della busta risulta pubblicata su NESSUN canale.
    Non e' il contrario di busta_completa(): in mezzo c'e' la busta uscita a meta'
    (es. IG si', FB no), che non e' ne' finita ne' intatta e va trattata a parte."""
    unita = costruisci_unita(busta['tipo'], busta['json_file'],
                             busta['immagini'], busta['meta'])
    if not unita:
        return False
    return not any(gia_pubblicato(u['chiave'], c, pubblicati)
                   for u in unita for c in canali_richiesti())


# Nome della sottocartella d'archivio per cio' che non e' mai stato pubblicato e non
# lo sara' mai. Tenuta separata da archivio/AAAA-MM/, che e' la prova dei post usciti.
SCARTI_SOTTOCARTELLA = 'non-pubblicati'


def separa_scarti_definitivi(scaduti, pubblicati):
    """Divide le buste scadute in (da_segnalare, scarti_definitivi).

    Uno "scarto definitivo" e' una busta che non ha nessuna via d'uscita: e' scaduta,
    NON e' un aggregato (i giornalieri e le storie hanno finestra di recupero 0 giorni
    — decisione del 12/07/2026: «oggi c'e' X» pubblicato in ritardo e' falso) e non e'
    mai uscita da nessuna parte. Nessun giro futuro potra' pubblicarla, quindi l'avviso
    che la riguarda non e' azionabile: si limita a suonare a ogni run, per sempre. Fu
    il caso di 20260803_Post giornaliero, rimasto in coda a strillare per 5 giorni.
    Va archiviata fra i non-pubblicati (una riga sola nel referto, poi silenzio).

    Restano invece da_segnalare — cioe' continuano a suonare, ed e' giusto:
      - gli AGGREGATI scaduti: si possono ancora ridatare a mano, il contenuto copre
        piu' giorni e un weekend mai uscito e' un buco di copertura da sanare;
      - le buste uscite a META' (un canale si', l'altro no): li' il problema non e' la
        scadenza ma un canale che ha fallito, e nascondere quel segnale lo perderebbe.
    """
    da_segnalare, scarti = [], []
    for busta in scaduti:
        e_scarto = (busta['tipo'] not in TIPI_AGGREGATI
                    and busta_mai_uscita(busta, pubblicati))
        (scarti if e_scarto else da_segnalare).append(busta)
    return da_segnalare, scarti


def separa_gia_pubblicate(scaduti, pubblicati):
    """Divide le buste scadute in (scadute_davvero, gia_pubblicate).

    Perche' serve: una busta esce dalla finestra GRACE_DAYS anche DOPO essere uscita
    davvero — succede ogni volta che la pubblicazione riesce ma il giro successivo
    arriva a finestra chiusa (tipico dopo una pausa del freno Instagram). Prima di
    questa separazione finiva fra le "scadute" e ci restava per sempre: mai archiviata
    (archivia_busta si chiamava solo nel ramo "pubblicata adesso") e ri-segnalata a
    ogni giro. Un avviso che suona sempre smette di essere un avviso — ed e' proprio il
    rumore che aveva nascosto i 12 fallimenti del carosello di Agosto.

    Una busta pubblicata solo a meta' (es. IG si', FB no) resta "scaduta davvero":
    quella e' una segnalazione vera."""
    scadute_davvero, gia_pubblicate = [], []
    for busta in scaduti:
        (gia_pubblicate if busta_completa(busta, pubblicati) else scadute_davvero).append(busta)
    return scadute_davvero, gia_pubblicate


# Nome della sottocartella per cio' che e' uscito A META' e non e' piu' recuperabile.
# Tenuta separata sia da archivio/AAAA-MM/ (che vuol dire «questo e' uscito», e metterci
# una mezza uscita renderebbe l'archivio una prova falsa) sia da archivio/non-pubblicati/
# (che vuol dire «questo non e' mai uscito», e sarebbe falso al contrario).
PARZIALI_SOTTOCARTELLA = 'parziali'

# Dove si registra, una volta per sempre, quello che il pubblico non ha visto.
BUCHI_COPERTURA = Path('dati/buchi-copertura.md')


def canali_mancanti(busta, pubblicati):
    """(usciti, mancanti) — su quali canali attivi la busta e' uscita e su quali no.
    Serve per scrivere una nota che dica la verita' invece di «non pubblicata»."""
    unita = costruisci_unita(busta['tipo'], busta['json_file'],
                             busta['immagini'], busta['meta'])
    usciti, mancanti = [], []
    for canale in canali_richiesti():
        if unita and all(gia_pubblicato(u['chiave'], canale, pubblicati) for u in unita):
            usciti.append(canale)
        else:
            mancanti.append(canale)
    return usciti, mancanti


def separa_parziali_scadute(scaduti, pubblicati):
    """Divide le buste scadute in (da_segnalare, parziali_chiuse).

    Il TERZO caso, quello che cadeva fra le due regole esistenti: una busta uscita su
    ALMENO UN canale ma non su tutti, e ormai scaduta. Non e' completa (quindi
    separa_gia_pubblicate non la prende) e non e' mai uscita (quindi
    separa_scarti_definitivi non la prende): restava in coda a suonare per sempre.
    Fu il caso di 20260803_Post giornaliero, archiviato a mano il 10/08/2026.

    Si chiude solo se il tipo NON e' un aggregato: per gli aggregati il ritardo e'
    ancora sanabile a mano (si ridatano e coprono comunque piu' giorni), quindi devono
    continuare a segnalare. Per un giornaliero o una storia la finestra di recupero e'
    0 giorni: quel canale non e' piu' recuperabile e l'avviso non e' azionabile.
    """
    da_segnalare, parziali = [], []
    for busta in scaduti:
        e_parziale = (busta['tipo'] not in TIPI_AGGREGATI
                      and not busta_completa(busta, pubblicati)
                      and not busta_mai_uscita(busta, pubblicati))
        (parziali if e_parziale else da_segnalare).append(busta)
    return da_segnalare, parziali


def scrivi_nota_parziale(cartella, busta, usciti, mancanti):
    """Accanto alla busta archiviata lascia una nota che dice cosa e' uscito davvero.
    Generata dai dati di published.log, non scritta a mano: e' la differenza fra una
    prova e un ricordo."""
    chiave = busta['json_file'].stem
    testo = (
        f"# {chiave} — uscita a meta'\n\n"
        f"⚠️ **Questa cartella non e' la prova di una pubblicazione completa.**\n\n"
        f"| | |\n|---|---|\n"
        f"| Prevista per | {busta['meta'].get('data_pubblicazione')} |\n"
        f"| Ritardo alla chiusura | {busta['giorni_ritardo']} giorni |\n"
        f"| Uscita su | {', '.join(usciti) if usciti else 'nessun canale'} |\n"
        f"| **NON** uscita su | {', '.join(mancanti) if mancanti else 'nessuno'} |\n\n"
        f"Tipo `{busta['tipo']}`: finestra di recupero 0 giorni, quindi il canale "
        f"mancante non e' piu' recuperabile da nessun giro futuro. La busta viene "
        f"chiusa qui perche' l'avviso non era azionabile e suonava a ogni run.\n"
    )
    try:
        (cartella / f"NOTA-{chiave}.md").write_text(testo)
    except OSError as e:
        print(f"⚠️  Nota per {chiave} non scritta: {e}")


def registra_buco_copertura(busta, usciti, mancanti):
    """Una riga permanente in dati/buchi-copertura.md. Il pubblico di quel canale non
    ha visto quel post: e' un fatto da tenere scritto una volta, non da strillare
    quattro volte al giorno."""
    riga = (f"- **{busta['meta'].get('data_pubblicazione', '?')[:10]}** · "
            f"`{busta['json_file'].stem}` ({busta['tipo']}) — uscita su "
            f"{', '.join(usciti) if usciti else 'nessun canale'}, "
            f"**mai su {', '.join(mancanti)}**\n")
    try:
        if not BUCHI_COPERTURA.exists():
            BUCHI_COPERTURA.parent.mkdir(parents=True, exist_ok=True)
            BUCHI_COPERTURA.write_text(
                "# Buchi di copertura\n\n"
                "Post usciti solo su una parte dei canali e non piu' recuperabili.\n"
                "Scritto in automatico da `scripts/publish.py`. Una riga per busta,\n"
                "poi silenzio: l'avviso ripetuto copriva quelli veri.\n\n")
        with BUCHI_COPERTURA.open('a') as f:
            f.write(riga)
    except OSError as e:
        print(f"⚠️  Buco di copertura non registrato: {e}")


# ---------------------------------------------------------------------------
# Instagram (graph.instagram.com)
# ---------------------------------------------------------------------------
def ig_create_media_container(image_url_str, caption, user_tags=None):
    payload = {'image_url': image_url_str, 'caption': caption, 'access_token': INSTAGRAM_TOKEN}
    if user_tags:
        # Meta vuole una lista di {username, x, y} serializzata.
        payload['user_tags'] = json.dumps(user_tags)
    resp = requests.post(f"{IG_API}/{INSTAGRAM_USER_ID}/media", data=payload)
    if resp.status_code == 200:
        return resp.json().get('id')
    _registra_errore_ig(resp)
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
    _registra_errore_ig(resp)
    print(f"Errore pubblicazione IG: {resp.status_code} - {resp.text}")
    return None


def ig_pubblica_foto(image_url_str, caption, user_tags=None):
    """Foto singola nel feed: container + publish. Ritorna l'id, o None.
    REGOLA D'ORO: un tag non deve mai costare un post. Se il container viene
    rifiutato E avevamo dei tag (account diventato privato, handle cambiato...),
    si riprova UNA volta senza tag: il post esce comunque e il riepilogo lo dice."""
    container_id = ig_create_media_container(image_url_str, caption, user_tags)
    if not container_id and user_tags:
        nomi = ', '.join('@' + str(t.get('username')) for t in user_tags)
        print(f"⚠️ container IG rifiutato con i tag ({nomi}): riprovo senza tag.")
        container_id = ig_create_media_container(image_url_str, caption, None)
        if container_id:
            TAG_SALTATI.append(f"{image_url_str.rsplit('/', 1)[-1]}: pubblicato SENZA tag ({nomi})")
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
            _registra_errore_ig(resp)
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
        _registra_errore_ig(resp)
        print(f"Errore container CAROUSEL IG: {resp.status_code} - {resp.text}")
        return None
    parent_id = resp.json().get('id')
    if not parent_id:
        return None
    return ig_publish_media(parent_id)


def ig_pubblica_storia(image_url_str, user_tags=None):
    """Storia IG: container con media_type=STORIES, poi publish. Ritorna l'id, o None.
    Le storie non hanno caption (il testo e' dentro la grafica). Vale la stessa
    REGOLA D'ORO della foto: se i tag fanno rifiutare il container, si riprova senza."""
    def crea(tags):
        payload = {'image_url': image_url_str, 'media_type': 'STORIES',
                   'access_token': INSTAGRAM_TOKEN}
        if tags:
            payload['user_tags'] = json.dumps(tags)
        resp = requests.post(f"{IG_API}/{INSTAGRAM_USER_ID}/media", data=payload)
        if resp.status_code == 200:
            return resp.json().get('id')
        _registra_errore_ig(resp)
        print(f"Errore container STORIES IG: {resp.status_code} - {resp.text}")
        return None

    container_id = crea(user_tags)
    if not container_id and user_tags:
        nomi = ', '.join('@' + str(t.get('username')) for t in user_tags)
        print(f"⚠️ container storia rifiutato con i tag ({nomi}): riprovo senza tag.")
        container_id = crea(None)
        if container_id:
            TAG_SALTATI.append(f"{image_url_str.rsplit('/', 1)[-1]}: storia pubblicata SENZA tag ({nomi})")
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
    tags = unita.get('user_tags') or None
    if canale == 'ig':
        if kind == 'foto':
            return ig_pubblica_foto(image_urls[0], caption, tags)
        if kind == 'carosello':
            return ig_pubblica_carosello(image_urls, caption)
        if kind == 'storia':
            return ig_pubblica_storia(image_urls[0], tags)
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
    da_pubblicare, scaduti, anomali, in_attesa = classifica_buste()

    # Se non c'e' nulla di cui parlare (nessun post di oggi, niente scaduto/anomalo —
    # al massimo post futuri), restiamo in silenzio.
    if not da_pubblicare and not scaduti and not anomali and not in_attesa:
        print(f"Nessuna busta da pubblicare, scaduta o anomala per oggi ({oggi().isoformat()}). Niente da fare.")
        return

    modalita = "🟢 LIVE" if PUBLISH_LIVE else "🧪 SIMULAZIONE (PUBLISH_LIVE non attivo)"
    stato_fb = "attivo" if FB_ENABLED else "NON configurato (solo Instagram)"
    print(f"Modalita': {modalita} — Facebook: {stato_fb} — finestra recupero: {GRACE_DAYS} giorni")

    # ---------- FRENO INSTAGRAM (uno per reparto: feed e storie) ----------
    # 'in-pausa'      -> quel reparto non si tocca proprio (zero contenitori creati)
    # 'prova-singola' -> le 24h sono passate: UN solo tentativo, poi si decide
    freno = {r: stato_freno_ig(r) for r in IG_REPARTI}
    ig_prova_disponibile = {r: freno[r] == 'prova-singola' for r in IG_REPARTI}
    for r in IG_REPARTI:
        if freno[r] == 'in-pausa':
            print(f"⏸ Instagram — {r} IN PAUSA (blocco Meta): non provo, "
                  f"riprovo il {quando_riprova_ig(r)}. Facebook prosegue.")
        elif freno[r] == 'prova-singola':
            print(f"🔁 Pausa Instagram ({r}) scaduta: provo UNA volta sola.")

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

    # ---------- BUSTE SCADUTE MA GIA' USCITE ----------
    # Prima di dare dello "scaduto" a qualcosa, si guarda published.log: se la busta
    # e' gia' uscita su tutti i canali attivi non e' un problema da segnalare, e'
    # solo coda da sgombrare. Si archivia in silenzio (una riga nel log della run,
    # niente allarme a Michele).
    scaduti, gia_uscite = separa_gia_pubblicate(scaduti, pubblicati)
    if PUBLISH_LIVE:
        for busta in gia_uscite:
            dest = archivia_busta(busta['json_file'], busta['immagini'], busta['meta'])
            if dest:
                print(f"📦 {busta['json_file'].name} era gia' pubblicata su tutti i canali "
                      f"→ archiviata in {dest.as_posix()}/")
    elif gia_uscite:
        nomi = ', '.join(b['json_file'].name for b in gia_uscite)
        print(f"🧪 {len(gia_uscite)} buste gia' pubblicate da archiviare (in LIVE): {nomi}")

    # ---------- SCARTI DEFINITIVI: scadute, mai uscite, senza via d'uscita ----------
    # Un giornaliero (o una storia) scaduto non verra' mai pubblicato da nessun giro
    # futuro: la sua finestra di recupero e' 0 giorni. Finche' restava in coda, l'unico
    # effetto era un avviso Telegram identico a ogni run — e un allarme che suona
    # sempre smette di essere un allarme, coprendo quelli veri. Lo si chiude qui: una
    # riga nel referto (perche' Michele deve sapere che un giorno e' rimasto scoperto),
    # poi la busta esce dalla coda e non si ripresenta piu'.
    scaduti, scarti = separa_scarti_definitivi(scaduti, pubblicati)
    righe_scarti = []
    if PUBLISH_LIVE:
        for busta in scarti:
            meta = busta['meta']
            dest = archivia_busta(busta['json_file'], busta['immagini'], meta,
                                  sottocartella=SCARTI_SOTTOCARTELLA)
            if dest:
                titolo = meta.get('titolo_evento', busta['json_file'].stem)
                print(f"🗑 {busta['json_file'].name} scaduta e mai pubblicata "
                      f"({busta['giorni_ritardo']}g di ritardo) → {dest.as_posix()}/")
                righe_scarti.append(
                    f"   • [{busta['tipo']}] {titolo} — prevista "
                    f"{meta.get('data_pubblicazione')}, mai uscita → archiviata fra i "
                    f"non-pubblicati (quel giorno resta scoperto)")
    elif scarti:
        nomi = ', '.join(b['json_file'].name for b in scarti)
        print(f"🧪 {len(scarti)} buste scadute e mai uscite da scartare (in LIVE): {nomi}")

    # ---------- PASSO 0: la coda e' gia' sul profilo? ----------
    # Va PRIMA di qualunque tentativo: i doppioni del 03-06/08 hanno lasciato in coda
    # buste gia' pubblicate ma non registrate, e senza questo controllo il primo giro
    # utile le rimanderebbe fuori un'altra volta.
    righe_riconciliate = []
    if PUBLISH_LIVE:
        righe_riconciliate = riconcilia_con_profilo(da_pubblicare + in_attesa, pubblicati)
    # Pubblicazioni RIFIUTATE dalla piattaforma (non buste malformate: quelle sono
    # "anomale"). Vanno contate a parte perche' devono gridare: una riga "❌ errore"
    # persa in mezzo al riepilogo e' passata inosservata per 12 giri di fila
    # (carosello di Agosto, 31/07-02/08/2026). Ora alzano l'intestazione del messaggio.
    fallimenti = []

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

        unita = costruisci_unita(tipo, json_file, immagini, meta)

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
                elif (canale == 'ig'
                      and (freno[reparto_ig(u['kind'])] == 'in-pausa'
                           or (freno[reparto_ig(u['kind'])] == 'prova-singola'
                               and not ig_prova_disponibile[reparto_ig(u['kind'])]))):
                    # NON creiamo nemmeno il contenitore: era proprio quello a tenere
                    # vivo il blocco (104+ contenitori orfani in 3 giorni, 03-06/08/2026).
                    rep = reparto_ig(u['kind'])
                    print(f"⏸ IG: salto {u['kind']} «{titolo}» — {rep} in pausa "
                          f"fino al {quando_riprova_ig(rep)}.")
                    righe_report.append(f"{prefisso} ⏸ Instagram in pausa (blocco Meta)")
                    IG_SALTATI.append(f"{u['kind']} · {titolo}")
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
                    rep = reparto_ig(u['kind']) if canale == 'ig' else None
                    if rep and freno[rep] == 'prova-singola':
                        ig_prova_disponibile[rep] = False  # la prova di oggi e' questa
                    iniziato = datetime.now(TZ)
                    esito = pubblica_unita(canale, u, url_list, caption)

                    # ---- RILETTURA: l'errore di Instagram dice la verita'? ----
                    # Un 403 su media_publish non prova che il post non sia uscito
                    # (06/08/2026: 19 doppioni nati proprio da questa illusione).
                    uscito_lo_stesso = None
                    if not esito and rep:
                        uscito_lo_stesso, permalink = ig_gia_uscito(
                            u['kind'], caption, iniziato)
                        if uscito_lo_stesso:
                            print(f"🔎 {et}: l'errore era falso — «{titolo}» e' sul "
                                  f"profilo ({permalink}). Lo segno come pubblicato.")
                            righe_report.append(
                                f"{prefisso} ✅ pubblicato (Instagram aveva risposto "
                                f"errore, ma il post c'è: verificato sul profilo)")
                            segna_pubblicato(u['chiave'], canale, pubblicati)
                            esito = permalink or 'verificato-sul-profilo'
                            RILETTURE_SALVATE.append(f"{u['kind']} · {titolo}")

                    if esito:
                        if not uscito_lo_stesso:
                            print(f"✅ {et} pubblicato: {esito}")
                            segna_pubblicato(u['chiave'], canale, pubblicati)
                            righe_report.append(f"{prefisso} ✅ pubblicato")
                        if rep and freno[rep] != 'libero':
                            # E' uscito: quel reparto pubblica, punto. Vale anche se
                            # Meta ha risposto errore — l'errore era falso, e tenere
                            # il freno fermerebbe una coda che invece funziona.
                            sgancia_freno_ig(rep)
                            freno[rep] = 'libero'
                            print(f"🟢 Instagram ha riaccettato {rep}: freno sganciato.")
                            righe_report.append(f"   🟢 blocco Instagram ({rep}) RIENTRATO")
                    else:
                        # Qui il post NON e' uscito (rilettura negativa) oppure non
                        # siamo riusciti a controllare. I due casi non sono uguali.
                        non_verificabile = (rep is not None and uscito_lo_stesso is None)
                        if non_verificabile:
                            righe_report.append(
                                f"{prefisso} ⚠️ errore, e NON sono riuscito a "
                                f"controllare sul profilo se è uscito")
                        else:
                            righe_report.append(f"{prefisso} ❌ errore "
                                                + ("(verificato: NON è sul profilo)"
                                                   if rep else ""))
                        fallimenti.append(f"{et} · {u['kind']} · {titolo} ({u['chiave']})")
                        if rep and (errore_e_blocco_ig(IG_ULTIMO_ERRORE) or non_verificabile):
                            # Blocco vero, oppure dubbio: in entrambi i casi ci si
                            # ferma. Insistere al buio e' esattamente cio' che ha
                            # riempito il profilo di doppioni.
                            motivo = ('esito non verificabile' if non_verificabile else
                                      (IG_ULTIMO_ERRORE.get('error_user_title')
                                       or IG_ULTIMO_ERRORE.get('message') or 'azione bloccata'))
                            arma_freno_ig(motivo, rep)
                            freno[rep] = 'in-pausa'
                            print(f"⏸ Instagram — {rep} in pausa ({motivo}): "
                                  f"{IG_PAUSA_ORE}h, non riprovo.")

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
    if righe_scarti:
        if righe_report:
            righe_report.append("")
        righe_report.append("🗑 SCARTATE (scadute e mai uscite: nessun giro futuro "
                            "potrebbe pubblicarle). Ultimo avviso, poi silenzio:")
        righe_report.extend(righe_scarti)

    if scaduti:
        if righe_report:
            righe_report.append("")
        righe_report.append(f"⚠️ BUSTE SCADUTE RECUPERABILI (NON pubblicate, oltre "
                            f"{GRACE_DAYS}g di ritardo):")
        for busta in scaduti:
            meta = busta['meta']
            righe_report.append(
                f"   • [{busta['tipo']}] {meta.get('titolo_evento', busta['json_file'].stem)} — "
                f"prevista {meta.get('data_pubblicazione')} ({busta['giorni_ritardo']}g fa) "
                f"→ aggiorna la data nel piano o rimuovila dalla coda"
            )

    if in_attesa:
        if righe_report:
            righe_report.append("")
        righe_report.append("⏸ IN ATTESA CHE INSTAGRAM SI SBLOCCHI (non scadono, "
                            "escono appena il feed riapre):")
        for busta in in_attesa:
            meta = busta['meta']
            righe_report.append(
                f"   • [{busta['tipo']}] {meta.get('titolo_evento', busta['json_file'].stem)} — "
                f"ferma da {busta['giorni_ritardo']}g"
            )

    if anomali:
        if righe_report:
            righe_report.append("")
        righe_report.append("⚠️ BUSTE ANOMALE (saltate):")
        for nome_json, motivo in anomali:
            righe_report.append(f"   • {nome_json} — {motivo}")

    if TAG_SALTATI:
        righe_report.append("")
        righe_report.append("⚠️ Tag saltati (post pubblicati lo stesso):")
        for riga in TAG_SALTATI:
            righe_report.append(f"   • {riga}")

    if fallimenti:
        if righe_report:
            righe_report.append("")
        righe_report.append("🔴 PUBBLICAZIONI RIFIUTATE dalla piattaforma "
                            "(la busta resta in coda e ritentera' fino alla scadenza):")
        for riga in fallimenti:
            righe_report.append(f"   • {riga}")
        righe_report.append("   → il motivo esatto e' nel log della run su GitHub Actions")

    if righe_riconciliate:
        if righe_report:
            righe_report.append("")
        righe_report.append("🔎 GIÀ SU INSTAGRAM, non ripubblicati (erano usciti "
                            "durante i giorni dei doppioni senza essere registrati):")
        righe_report.extend(righe_riconciliate)

    if RILETTURE_SALVATE:
        if righe_report:
            righe_report.append("")
        righe_report.append(
            f"🔎 DOPPIONI EVITATI: {len(RILETTURE_SALVATE)} contenuti che Instagram "
            f"aveva dato per falliti erano già sul profilo. Segnati come pubblicati "
            f"invece di essere ripubblicati:")
        for riga in RILETTURE_SALVATE:
            righe_report.append(f"   • {riga}")

    reparti_in_pausa = [r for r in IG_REPARTI if stato_freno_ig(r) == 'in-pausa']
    if IG_SALTATI or reparti_in_pausa:
        if righe_report:
            righe_report.append("")
        righe_report.append("⏸ INSTAGRAM IN PAUSA — Meta ha bloccato la pubblicazione. "
                            "Non ho riprovato: insistere tiene vivo il blocco.")
        for r in reparti_in_pausa:
            d = leggi_freno_ig(r)
            righe_report.append(
                f"   • {r}: «{d.get('motivo', 'azione bloccata')}» — bloccato dal "
                f"{d.get('bloccato_dal', '?')[:10]} ({d.get('tentativi_falliti', 1)} "
                f"tentativi falliti) → riprovo il {quando_riprova_ig(r)}")
        liberi = [r for r in IG_REPARTI if r not in reparti_in_pausa]
        if liberi:
            righe_report.append(f"   Instagram — {', '.join(liberi)}: regolari.")
        righe_report.append(f"   Facebook: regolare. Contenuti in attesa: {len(IG_SALTATI)}.")
        righe_report.append("   👉 Controlla l'app Instagram: se c'è un avviso di "
                            "restrizione, si può contestare da lì.")

    intestazione = ("🟢 PUBBLICAZIONE LIVE" if PUBLISH_LIVE
                    else "🧪 SIMULAZIONE (nessun post reale)")
    if fallimenti:
        intestazione = f"🔴 {intestazione} — {len(fallimenti)} PUBBLICAZIONE/I FALLITA/E"
    elif reparti_in_pausa:
        intestazione = (f"⏸ {intestazione} — INSTAGRAM IN PAUSA "
                        f"({', '.join(reparti_in_pausa)}, blocco Meta)")
    elif scaduti or anomali or righe_scarti:
        intestazione = "❗ " + intestazione + " — CI SONO BUSTE DA CONTROLLARE"
    if not FB_ENABLED and not PUBLISH_LIVE:
        intestazione += "\n(Facebook non ancora configurato: aggiungi i secret FACEBOOK_PAGE_TOKEN e FACEBOOK_PAGE_ID)"
    notifica_telegram(intestazione + "\n\n" + "\n".join(righe_report))


if __name__ == '__main__':
    if not INSTAGRAM_TOKEN or not INSTAGRAM_USER_ID:
        print("Errore: INSTAGRAM_TOKEN o INSTAGRAM_USER_ID non configurati.")
    else:
        main()
