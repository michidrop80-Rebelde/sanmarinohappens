#!/usr/bin/env python3
"""
guardia_contenuti.py — UNICA fonte di verita' per i controlli sul CONTENUTO delle
caption (prezzi/gratuita' + lunghezza Instagram).

PERCHE'
-------
Fino al 30/08/2026 lo stesso pattern "prezzi/gratuita'" era copiato in TRE posti
(`scripts/publish.py`, `.claude/skills/smh-check/assets/smh_check.py`, e ogni nuova
guardia), e le istruzioni nelle skill erano rimaste alla regola PRE-13/07 ("ora +
gratis/€ dove noti"). Risultato: il carosello di Settembre e' arrivato in coda con
"gratis" ovunque e sarebbe stato bloccato in silenzio da publish.py — come gia' il
settimanale 18-23/08. Da qui in avanti il pattern vive SOLO qui e tutti lo importano.

Nessuna dipendenza esterna (publish.py importa `requests`, questo modulo no): cosi'
lo possono usare anche le guardie che girano sul Mac senza le librerie del robot.

REGOLA (equita' tra organizzatori, 13/07/2026)
---------------------------------------------
Nessun prezzo ne' gratuita' nei contenuti pubblici — ne' grafica ne' caption, per
TUTTI i tipi (giornaliero, settimanale, weekend, carosello). I costi vanno SOLO nel
link in bio. Gli orari invece sono ammessi in caption.
"""
import re

# Limite caption Instagram (Meta rifiuta oltre 2200, contato in unita' UTF-16 nel
# caso peggiore — gli emoji possono valere 2). Vedi carosello Agosto (02/08/2026).
IG_CAPTION_MAX = 2200

# Set "certo e ad alta confidenza" — i termini indicati da Michele. E' quello che
# BLOCCA davvero su GitHub (publish.py). Sta qui perche' non deve mai divergere.
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

# Set piu' severo — usato da /smh-check sul Mac, che vede anche il testo-sorgente e
# le immagini e puo' permettersi di segnalare i casi sfumati. NON blocca la
# pubblicazione (quello lo fa publish.py col set sopra), ma alza un ⚠️/❌ nel referto.
PREZZI_PATTERN_SEVERO = re.compile(
    PREZZI_PATTERN.pattern
    + r'|\bprezzo\b|\bprezzi\b|\bbigliett[oi]\b|\bcosto\b|\bcosti\b',
    re.IGNORECASE,
)


def caption_prezzi(testo, severo=False):
    """Lista (senza duplicati, nell'ordine trovato) dei termini di prezzo/gratuita'
    presenti nel testo. Lista vuota = nessun problema.
    severo=True usa il set esteso di /smh-check."""
    pattern = PREZZI_PATTERN_SEVERO if severo else PREZZI_PATTERN
    trovati = []
    for m in pattern.finditer(testo or ''):
        termine = m.group(0).strip()
        if termine.lower() not in [t.lower() for t in trovati]:
            trovati.append(termine)
    return trovati


def lunghezza_caption(caption):
    """Lunghezza della caption in unita' UTF-16 (come la conta Meta nel caso peggiore)."""
    return len((caption or '').encode('utf-16-le')) // 2
