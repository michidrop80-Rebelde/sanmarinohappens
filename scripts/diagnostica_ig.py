#!/usr/bin/env python3
"""
DIAGNOSTICA INSTAGRAM — SOLA LETTURA. Non pubblica, non cancella, non modifica nulla.

Perche' esiste: il 06/08/2026, davanti al blocco del feed (403 · code 4 · subcode
2207051 "action is blocked"), non c'era modo di sapere COSA fosse davvero. Nell'app
Instagram non compariva nessun avviso di restrizione — quindi non era l'account di
Michele a essere limitato — ma dal Mac non si puo' chiedere niente a Meta: il token
sta solo nei Secret di GitHub. Questo script gira dentro GitHub Actions e fa le tre
domande che distinguono i casi possibili, senza toccare niente:

  1) IL TOKEN E' VIVO?          GET /me
     Se risponde, il token non e' scaduto e l'account esiste.

  2) QUANTO ABBIAMO PUBBLICATO? GET /{ig-user-id}/content_publishing_limit
     Instagram limita i post pubblicati via API in una finestra mobile di 24h.
     Se la quota e' esaurita, NON e' un blocco anti-spam: e' un tetto, e si aspetta
     che la finestra scorra. Sintomo identico, rimedio opposto — per questo va letto
     invece che indovinato.

  3) L'ERRORE E' ANCORA QUELLO? GET /{ig-user-id}/media (una lettura banale)
     Se anche una lettura innocua viene rifiutata con code 4, il blocco e' sull'app
     intera; se passa, e' mirato alla sola pubblicazione.

Si lancia da GitHub Actions (workflow "Diagnostica Instagram", a mano) oppure in
locale se si hanno le variabili INSTAGRAM_TOKEN / INSTAGRAM_USER_ID.
"""

import os
import json
import requests

INSTAGRAM_TOKEN = os.getenv('INSTAGRAM_TOKEN')
INSTAGRAM_USER_ID = os.getenv('INSTAGRAM_USER_ID')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# publish.py usa graph.instagram.com; teniamo anche l'altro host come ripiego,
# perche' a seconda di come e' collegato l'account una delle due porte puo' essere
# chiusa. Non e' un tentativo alla cieca: le risposte le stampiamo entrambe.
HOSTS = ['https://graph.instagram.com', 'https://graph.facebook.com/v21.0']

righe = []


def dillo(testo):
    print(testo)
    righe.append(testo)


def chiedi(host, percorso, campi=None):
    """Una GET di sola lettura. Ritorna (ok, dati_o_errore)."""
    params = {'access_token': INSTAGRAM_TOKEN}
    if campi:
        params['fields'] = campi
    try:
        r = requests.get(f"{host}{percorso}", params=params, timeout=30)
    except requests.RequestException as e:
        return False, {'errore_di_rete': str(e)}
    try:
        dati = r.json()
    except ValueError:
        return False, {'risposta_non_json': r.text[:300]}
    if r.status_code == 200:
        return True, dati
    return False, dati.get('error', dati)


def riga_errore(err):
    if not isinstance(err, dict):
        return str(err)
    return (f"code={err.get('code')} subcode={err.get('error_subcode')} "
            f"«{err.get('message') or err.get('error_user_title') or err}»")


def main():
    dillo("🔎 DIAGNOSTICA INSTAGRAM (sola lettura)")
    dillo("")

    # ---------- 1) il token e' vivo? ----------
    dillo("1) Il token risponde?")
    token_ok = False
    for host in HOSTS:
        ok, dati = chiedi(host, '/me', 'id,username')
        etichetta = host.split('//')[1].split('/')[0]
        if ok:
            token_ok = True
            dillo(f"   ✅ {etichetta}: account @{dati.get('username', '?')} "
                  f"(id {dati.get('id', '?')}) — il token e' valido")
        else:
            dillo(f"   ❌ {etichetta}: {riga_errore(dati)}")
    if not token_ok:
        dillo("   → nessuna delle due porte risponde: il problema e' il token, "
              "non un blocco di pubblicazione.")

    # ---------- 2) la quota di pubblicazione ----------
    dillo("")
    dillo("2) Quota di pubblicazione nelle ultime 24h (il tetto di Instagram):")
    quota_letta = False
    for host in HOSTS:
        ok, dati = chiedi(host, f"/{INSTAGRAM_USER_ID}/content_publishing_limit",
                          'config,quota_usage')
        etichetta = host.split('//')[1].split('/')[0]
        if not ok:
            dillo(f"   ❌ {etichetta}: {riga_errore(dati)}")
            continue
        quota_letta = True
        voci = dati.get('data') or []
        if not voci:
            dillo(f"   ⚠️ {etichetta}: risposta vuota — {json.dumps(dati)[:200]}")
            continue
        for v in voci:
            usati = v.get('quota_usage')
            config = v.get('config') or {}
            tetto = config.get('quota_total')
            dillo(f"   📊 {etichetta}: usati {usati} su {tetto} "
                  f"(finestra {config.get('quota_duration', '?')}s)")
            if isinstance(usati, int) and isinstance(tetto, int):
                if usati >= tetto:
                    dillo("   🔴 QUOTA ESAURITA: non e' un blocco anti-spam, e' il tetto. "
                          "Si sblocca da solo appena la finestra di 24h scorre.")
                else:
                    dillo("   🟢 Quota NON esaurita: il rifiuto non e' un problema di "
                          "quantita' → e' una restrizione vera sull'azione.")
    if not quota_letta:
        dillo("   → quota non leggibile: vedi l'errore qui sopra.")

    # ---------- 3) una lettura innocua passa? ----------
    dillo("")
    dillo("3) Anche una semplice lettura viene rifiutata? E cosa risulta pubblicato?")
    for host in HOSTS:
        ok, dati = chiedi(host, f"/{INSTAGRAM_USER_ID}/media",
                          'id,timestamp,media_type,permalink,caption')
        etichetta = host.split('//')[1].split('/')[0]
        if not ok:
            dillo(f"   ❌ {etichetta}: {riga_errore(dati)}")
            continue
        voci = dati.get('data') or []
        dillo(f"   ✅ {etichetta}: lettura OK ({len(voci)} media)")
        dillo("   → l'app NON e' bloccata in lettura: la restrizione riguarda "
              "solo la pubblicazione.")
        # Gli ultimi media, per capire cosa e' DAVVERO uscito. Serve a smentire (o
        # confermare) il sospetto peggiore: che un post dato per "fallito" con 403
        # sia in realta' finito sul profilo. Se cosi' fosse, ripubblicarlo a blocco
        # rientrato creerebbe un doppione.
        dillo("   Ultimi 5 contenuti realmente presenti sul profilo:")
        for v in voci[:5]:
            didascalia = (v.get('caption') or '').replace('\n', ' ')[:60]
            dillo(f"     • {v.get('timestamp')} · {v.get('media_type')} · "
                  f"{v.get('permalink', '?')}")
            if didascalia:
                dillo(f"       «{didascalia}…»")

    # ---------- 4) DOPPIONI ----------
    # La scoperta del 06/08: un 403 «action is blocked» sul media_publish NON vuol
    # dire che il post non e' uscito. Esce, e il robot — che lo crede fallito — lo
    # ripubblica al giro dopo. Il danno non e' un post mancante: sono post doppi sul
    # profilo. Qui li contiamo per didascalia, che e' l'unica cosa che li distingue.
    dillo("")
    dillo("4) DOPPIONI sul profilo (stesso testo pubblicato piu' volte):")
    ok, dati = chiedi(HOSTS[0], f"/{INSTAGRAM_USER_ID}/media",
                      'id,timestamp,media_type,permalink,caption')
    if not ok:
        dillo(f"   ❌ non leggibile: {riga_errore(dati)}")
    else:
        gruppi = {}
        for v in dati.get('data') or []:
            chiave = (v.get('caption') or v.get('id') or '')[:80]
            gruppi.setdefault(chiave, []).append(v)
        doppi = {k: v for k, v in gruppi.items() if len(v) > 1}
        if not doppi:
            dillo("   ✅ nessun doppione fra i contenuti letti.")
        else:
            tot = sum(len(v) - 1 for v in doppi.values())
            dillo(f"   🔴 {len(doppi)} contenuti pubblicati piu' volte "
                  f"({tot} copie di troppo). Da cancellare A MANO dall'app: "
                  f"l'API di Instagram non sa cancellare.")
            for testo, voci in sorted(doppi.items(),
                                      key=lambda kv: kv[1][0].get('timestamp') or ''):
                voci = sorted(voci, key=lambda v: v.get('timestamp') or '')
                titolo = testo.replace('\n', ' ')[:55]
                dillo(f"   • «{titolo}…» — {len(voci)} copie:")
                for i, v in enumerate(voci):
                    tieni = "  ⬅️ TIENI (la prima)" if i == 0 else "  ❌ da cancellare"
                    dillo(f"       {v.get('timestamp')} {v.get('permalink')}{tieni}")

    dillo("")
    dillo("Nessuna scrittura effettuata: questo controllo non pubblica e non cancella nulla.")

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                          data={'chat_id': TELEGRAM_CHAT_ID, 'text': "\n".join(righe)},
                          timeout=15)
        except requests.RequestException as e:
            print(f"(Telegram non inviato: {e})")


if __name__ == '__main__':
    if not INSTAGRAM_TOKEN or not INSTAGRAM_USER_ID:
        print("Errore: INSTAGRAM_TOKEN o INSTAGRAM_USER_ID non configurati.")
    else:
        main()
