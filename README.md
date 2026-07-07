# San Marino Happens — Publishing Automation

Automazione della pubblicazione su Instagram per [@sanmarinohappens](https://instagram.com/sanmarinohappens).

## Struttura

- **`.github/workflows/publish.yml`** — GitHub Actions che gira ogni mattina/sera e controlla se c'è qualcosa da pubblicare
- **`scripts/publish.py`** — Script Python che chiama Instagram Graph API
- **`posts/`** — Coppie `AAAAMMGG_nome.png` + `AAAAMMGG_nome.json` (immagine + dati). Ogni PNG ha il suo JSON gemello con `data_pubblicazione` (quando va postato davvero, non è detto coincida con la data nel nome file) e `caption` (testo completo con hashtag).
- **`published.log`** — Registro dei post già pubblicati (evita duplicati)

I file in `posts/` vengono messi in coda dalla skill `smh-pubblica` (gira sul Mac di Michele, non qui).

## Setup

### 1. GitHub Secrets (Settings → Secrets and variables → Actions → Secrets)
- `INSTAGRAM_TOKEN` — access token Instagram
- `INSTAGRAM_USER_ID` — ig_user_id (17841416773686298)
- `TELEGRAM_BOT_TOKEN` — token del bot Telegram (per le notifiche di pubblicazione)
- `TELEGRAM_CHAT_ID` — chat id di Michele

### 2. GitHub Variables (stessa pagina, tab "Variables")
- `PUBLISH_LIVE` — **deve valere `true` per pubblicare davvero su Instagram.** Se assente o diverso da `true`, lo script gira in modalità SIMULAZIONE: fa tutto (trova il post di oggi, prepara la caption, manda una notifica Telegram "🧪 SIMULAZIONE") ma NON chiama l'API di Instagram. È l'interruttore di sicurezza per i test.

## Orari di pubblicazione (ora italiana)

- **7:00** — Post singolo del giorno (se previsto)
- **18:00** — Aggregati (settimanale/weekend/bisettimanale/carosello mensile), quando saranno collegati

Ogni esecuzione controlla i JSON in `posts/` e pubblica solo quelli con `data_pubblicazione` = oggi. Se nessuno corrisponde, non fa nulla.

## Note

- Token Instagram scade ogni ~60 giorni, va rinnovato manualmente (o con refresh automatico da implementare)
- Il log `published.log` evita di ripubblicare lo stesso post
- v1 copre solo i post giornalieri singoli; gli aggregati (settimanale/weekend/carosello) si aggiungono in un secondo momento con lo stesso meccanismo JSON
