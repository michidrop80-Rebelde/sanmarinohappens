# San Marino Happens — Publishing Automation

Automazione della pubblicazione su Instagram per [@sanmarinohappens](https://instagram.com/sanmarinohappens).

## Struttura

- **`.github/workflows/publish.yml`** — GitHub Actions che pubblica automaticamente ai tempi prestabiliti
- **`scripts/publish.py`** — Script Python che chiama Instagram Graph API
- **`posts/`** — Cartella dove vivono i PNG dei post (generati da Canva + Claude)
- **`published.log`** — Registro dei post già pubblicati (evita duplicati)

## Setup

### 1. GitHub Secrets
Aggiungi questi secret al repo (Settings → Secrets and variables → Actions):
- `INSTAGRAM_TOKEN` — access token da `.claude/secrets/instagram.json`
- `INSTAGRAM_USER_ID` — ig_user_id (17841416773686298)

### 2. Metti i PNG in `posts/`
Ogni PNG deve stare in `posts/` con un nome significativo (es. `2026-07-08_evento.png`).

### 3. Commit e push
```bash
git add -A
git commit -m "Add publish workflow"
git push
```

GitHub Actions partirà automaticamente ai tempi prestabiliti.

## Orari di pubblicazione (UTC+2 = ora italiana)

- **7:00** — Singoli post del giorno
- **16:00** (pomeriggio) — Aggregati (preview settimanale/weekend)

## Note

- Token Instagram scade ogni ~60 giorni ma è auto-rinnovabile
- Il log `published.log` evita di ripubblicare lo stesso post
- Caption può venire da un JSON associato al PNG (da implementare)
