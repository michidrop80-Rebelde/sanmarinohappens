# Tappa 2 — Ottenere il token Instagram (Strada A: Login Instagram)

## ► STATO A FINE SESSIONE 07/07 — RIPARTIRE DA QUI
Fatto finora: account IG Business @sanmarinohappens + Pagina FB "San Marino Happens" (di
michimorri@gmail.com) collegati in Business Suite; app Meta "San Marino Happens Publishing"
creata (**App ID Meta 928486803611116**, **Instagram App ID 1421000553204146**); permessi
attivati (instagram_business_basic / _content_publish / _manage_insights); @sanmarinohappens
aggiunto come **Tester di Instagram** e **invito ACCETTATO** (tester attivo).

**PROSSIMO STEP:** developers.facebook.com → app → "Configurazione dell'API con Instagram" →
sezione **"2. Genera i token d'accesso"** → **"Aggiungi account"** → login @sanmarinohappens.
Ora che il tester è attivo NON deve più dare "Ruolo di sviluppatore non sufficiente" (se lo dà,
aspettare 5-10 min di propagazione e riprovare). Copiato il token → salvarlo in
`.claude/secrets/instagram.json` → Claude recupera `ig_user_id` → Tappa 3 (GitHub).

---


## Diagnosi (perché il Graph API Explorer NON funziona)
La app "San Marino Happens Publishing" è stata creata col caso d'uso **"Gestisci i messaggi e i contenuti su Instagram"** → Meta l'ha configurata come **Instagram API con Login Instagram** (nuovo flusso 2024+).

Il **Graph API Explorer** serve invece al vecchio **Login Facebook**. Sono due mondi diversi → nell'Explorer:
- dropdown permessi vuoto (i permessi ora stanno nelle "Configurations", non si scelgono a mano)
- errore "Invalid Scopes: manage_pages, pages_show_list" (permessi vecchi)
- "Page access tokens cannot be generated..." (nessun token utente attivo)
- tab "Configurations" → **"Nessuna configurazione disponibile"** = conferma che l'app è pura Login Instagram.

**Conclusione:** abbandonare il Graph API Explorer. Usare il generatore di token dentro la dashboard dell'app (Strada A).

⚠️ **Non serve la App Review di Meta** (quella lunga 2-4 settimane): serve solo per pubblicare sugli account di ALTRI. Per il proprio account @sanmarinohappens si resta in modalità sviluppo e funziona.

## App ID già ottenuto
- **App ID:** 928486803611116
- App Secret (Chiave segreta): sta in Impostazioni app → Basic → "Mostra". NON incollarla in chat.

## Procedura Strada A — generare il token dalla dashboard

1. **developers.facebook.com** → "Le mie app" → apri **San Marino Happens Publishing**.
2. Menu a sinistra: apri il prodotto Instagram — cerca una voce tipo **"Configurazione API con login di Instagram"** (API setup with Instagram login). Di solito si arriva da: caso d'uso "Gestisci i messaggi e i contenuti su Instagram" → **Personalizza** → **Impostazioni**.
   📌 **Verificato il 17/08/2026 — nel menù di sinistra Instagram NON c'è.** Le voci sono:
   Dashboard · Azioni richieste · Casi d'uso · Facebook Login for Bus… (Impostazioni, Avvio
   rapido, Configurazioni, Modelli) · Test · Pubblicazione · Impostazioni app · Ruoli dell'app.
   La strada buona parte dalla **Dashboard**, prima riga: **«Personalizza il caso d'uso per
   gestire i messaggi e i contenuti su Instagram»** (ha già la spunta verde) → freccia **›**.
   In alternativa la voce **"Casi d'uso"** nel menù di sinistra. ⚠️ Non fermarti su "Facebook
   Login for Business": è l'altro mondo, quello del Graph API Explorer che non funziona.
3. Nella pagina di setup ci sono sezioni numerate. Cerca la sezione **"1. Genera token di accesso"** (Generate access tokens).
4. Clicca **"Aggiungi account"** (Add account) → si apre un popup di login Instagram → accedi/autorizza con **@sanmarinohappens** → concedi tutti i permessi richiesti (incluso pubblicazione contenuti).
5. Tornato nella dashboard, l'account @sanmarinohappens compare in lista con un pulsante **"Genera token"** → cliccalo → copia il **token lungo** che appare.
6. **SALVA il token** (NON in chat) nel file segreti del progetto:
   `.claude/secrets/instagram.json` (stessa cartella di telegram.json, già in .gitignore).
   Formato:
   ```json
   {
     "app_id": "928486803611116",
     "ig_user_id": "<lo troviamo dopo>",
     "access_token": "<il token copiato>",
     "token_scaduto_il": "<data +60 giorni>"
   }
   ```

### ⚠️ Errore "Ruolo di sviluppatore non sufficiente" (Insufficient developer role)
Compare quando @sanmarinohappens NON ha un ruolo sull'app (l'app è di michimorri@gmail.com,
l'IG è un'identità separata). In modalità sviluppo solo admin/sviluppatore/**tester** possono
autorizzare. Fix (una volta sola):
1. Dashboard app → **"Ruoli dell'app"** → **"Ruoli"** → scorri a **"Tester di Instagram"** →
   **"Aggiungi tester di Instagram"** → username **sanmarinohappens** → invia invito.
2. Loggato come @sanmarinohappens apri **https://www.instagram.com/accounts/manage_access/**
   → scheda **"Inviti tester"** → **Accetta**.
3. Torna a step 2 "Genera token" → "Aggiungi account". (Propagazione ruolo: 5-10 min possibili.)

### Se al passo 4-5 chiede un "URL di reindirizzamento" (redirect URI)
Metti un URL HTTPS placeholder qualsiasi (es. `https://sanmarinohappens.github.io/`) nella sezione
**"Impostazioni di login aziendale"** (Business login settings). Lo sistemeremo per bene quando
si costruisce GitHub (Tappa 3). Per il generatore della dashboard di solito NON serve.

## Dopo aver ottenuto il token
- **Trovare l'ID account Instagram** (serve per pubblicare). Con il token si fa una chiamata:
  `GET https://graph.instagram.com/me?fields=user_id,username&access_token=IL_TOKEN`
  (lo esegue Claude con curl). Il `user_id` va in `instagram.json`.
- **Durata token:** 60 giorni, ma **rinnovabile all'infinito** con:
  `GET https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=IL_TOKEN`
  → GitHub Actions lo rinnoverà da solo (Tappa 3).

---

# Tappa 3 — GitHub Actions + Secrets (✅ COMPLETATA 07/07 sera)

## ► STATO A FINE SESSIONE 07/07 sera — TAPPA 3 CHIUSA, SI PARTE DA TAPPA 4

✅ Token Instagram ottenuto — valori noti:
- app_id: 928486803611116
- ig_user_id: 17841416773686298
- token_scaduto_il: 2026-09-05
- ⚠️ **il file locale `.claude/secrets/instagram.json` NON esiste** (cercato e non trovato — probabilmente
  non fu mai scritto su disco nonostante il report precedente lo desse per fatto). **Non è bloccante**:
  il valore vero del token vive già nel GitHub Secret `INSTAGRAM_TOKEN` (verificato presente). Se in
  futuro serve il file locale (es. per rinnovare il token da Mac), va rigenerato dalla dashboard Meta
  o recuperato da chi ha accesso ai GitHub Secrets (i secret non sono leggibili via API, solo via UI).

✅ Repo GitHub creato: `sanmarinohappens` (public) — `michidrop80-Rebelde/sanmarinohappens`

✅ Struttura base committata e **pushata** (era ferma in locale, risolto 07/07 sera):
- `.github/workflows/publish.yml` — cron GitHub Actions (singoli 7:00, aggregati 16:00)
- `scripts/publish.py` — script Python per Instagram Graph API
- `posts/` — cartella per i PNG
- `README.md` — documentazione

✅ **Push risolto via Personal Access Token (PAT), non SSH** — niente `gh`/SSH/Homebrew installati sul
Mac, quindi la via più rapida è stata: Michele genera un PAT classic su github.com/settings/tokens/new
con scope `repo` + `workflow` (il push su file dentro `.github/workflows/` richiede ESPLICITAMENTE lo
scope `workflow`, altrimenti GitHub rifiuta con "refusing to allow a Personal Access Token to create or
update workflow ... without `workflow` scope" — primo tentativo fallito proprio per questo). Comando:
`git push https://<TOKEN>@github.com/michidrop80-Rebelde/sanmarinohappens.git main` (token passato al
volo nell'URL, mai scritto su `git config`/remote — verificato dopo che `git remote -v` resta pulito).

✅ **GitHub Secrets aggiunti da Michele** (verificati presenti su Settings → Secrets): `INSTAGRAM_TOKEN`,
`INSTAGRAM_USER_ID`.

✅ **Workflow verificato ATTIVO** via `GET /repos/.../actions/workflows` → `"state": "active"`, id
308973139, cron letti correttamente.

⚠️ **Nota sicurezza:** durante il debug sono stati generati 2 PAT (uno senza scope `workflow`, scartato;
uno con `repo`+`workflow`, usato con successo, scadenza 30gg = 2026-08-06). Entrambi sono passati in
chat quindi vanno considerati esposti. Il primo (il "doppione" senza permessi) va eliminato da
github.com/settings/tokens; il secondo resta valido 30gg per eventuali push manuali futuri da Mac.

**PROSSIMO STEP — Tappa 4 (da fare in sessione nuova/pulita):**
1. Creare la skill `smh-pubblica` che legge i post approvati (`dati/post/approvati/`), prende i PNG
   già esportati (`marketing/3 Export/`), li carica nella cartella `posts/` del repo GitHub, e triggera
   la pubblicazione (il workflow gira da solo al cron, oppure si può forzare con `workflow_dispatch`).
2. Test end-to-end su un post vero (o un post di prova "usa e getta") per vedere la pubblicazione reale
   su Instagram.
3. Decidere il meccanismo esatto di "aggiungi PNG al repo": la skill fa un commit+push diretto? Oppure
   carica solo il file e un'Action separata lo pubblica? (da progettare in Tappa 4)

## Publishing (per memoria, Tappa 3-4)
Due passi via `graph.instagram.com`:
1. crea container: `POST /{ig-user-id}/media` con `image_url` (link PUBBLICO al PNG) + `caption`
2. pubblica: `POST /{ig-user-id}/media_publish` con `creation_id`
Storie e caroselli hanno parametri dedicati. L'immagine DEVE stare a un URL pubblico (lo dà GitHub).
