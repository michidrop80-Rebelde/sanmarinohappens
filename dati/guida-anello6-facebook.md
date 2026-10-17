# Anello 6 — Aggiungere la pubblicazione automatica su Facebook

Obiettivo: far sì che ogni post pubblicato su Instagram esca **automaticamente anche
sulla Pagina Facebook** "San Marino Happens", con lo stesso robot GitHub.

## Perché serve un pezzo in più (in parole semplici)
Il "lasciapassare" (token) che usiamo oggi è di tipo **solo-Instagram**: l'app Meta
"San Marino Happens Publishing" è stata creata col percorso *Instagram Login*, che per
scelta di Meta **non può scrivere su una Pagina Facebook**. Quindi Facebook ha bisogno
di un **secondo lasciapassare dedicato**: il *token della Pagina* Facebook.

## Cosa serve ottenere (solo 2 dati)
1. **FACEBOOK_PAGE_ID** — l'id numerico della Pagina "San Marino Happens".
2. **FACEBOOK_PAGE_TOKEN** — il token che autorizza a pubblicare sulla Pagina.

Vantaggio rispetto a Instagram: il token di una **Pagina** di cui sei admin, se ottenuto
come "lunga durata", **di norma non scade** (a differenza del token IG che va rinnovato
ogni 60 giorni). → Da confermare quando l'avremo in mano.

Come per Instagram, **non serve la lunga App Review di Meta**: pubblichi sulla TUA Pagina,
in modalità sviluppo, quindi funziona subito.

## Dati utili già noti
- App Meta: **San Marino Happens Publishing** — App ID **928486803611116**
- Dashboard app: https://developers.facebook.com/apps/928486803611116/
- Pagina Facebook: "San Marino Happens" (admin: michimorri@gmail.com)

## Procedura consigliata — via Graph API Explorer (tutto da UI, niente codice)
> ⚠️ L'interfaccia di Meta cambia spesso. **Conviene farla insieme a Claude**: apri le
> pagine qui sotto, guarda cosa compare e dillo a Claude, che ti guida passo passo (come
> è stato per il token Instagram). I passi qui sono la traccia di massima.

1. **Abilita l'accesso alle Pagine sull'app** (probabile passo iniziale, perché oggi l'app
   è "pura Instagram Login"): dashboard app → **Aggiungi prodotto** → **Facebook Login
   for Business** (o comunque il prodotto che sblocca i permessi "Pages"). Se l'Explorer
   (passo 2) offre già i permessi Pages, questo passo non serve.

2. Apri il **Graph API Explorer**: https://developers.facebook.com/tools/explorer/
   - In alto a destra scegli l'app **San Marino Happens Publishing**.
   - Menu **User or Page** → **User Token**.
   - Clic su **Add a Permission** e spunta questi tre permessi (nomi esatti):
     - `pages_show_list`
     - `pages_read_engagement`
     - `pages_manage_posts`
   - Clic **Generate Access Token** → fai login e **autorizza** (scegli la Pagina
     "San Marino Happens" quando lo chiede).

3. **Rendi il token di lunga durata**: clic sul pulsante info (ⓘ) accanto al token →
   **Open in Access Token Tool** (oppure vai su
   https://developers.facebook.com/tools/debug/accesstoken/) → **Extend Access Token**.
   Ottieni un token utente "long-lived" (~60 giorni).

4. **Ricava Page ID + Page Token**: torna all'Explorer, incolla il token esteso, e nella
   barra della query scrivi `me/accounts` → **Submit**. Nella risposta trovi la Pagina
   "San Marino Happens" con:
   - `"id": "..."`  → questo è **FACEBOOK_PAGE_ID**
   - `"access_token": "..."`  → questo è **FACEBOOK_PAGE_TOKEN** (di lunga durata:
     il token-di-Pagina ottenuto da un token-utente esteso di norma non scade).

5. **Salva i due valori nei GitHub Secrets** (stessa pagina dove ci sono già quelli di
   Instagram): github.com → repo `sanmarinohappens` → **Settings → Secrets and variables
   → Actions → Secrets → New repository secret**. Crea:
   - `FACEBOOK_PAGE_ID` = l'id
   - `FACEBOOK_PAGE_TOKEN` = il token
   > I secret NON passano dalla chat: li incolli direttamente su GitHub (come hai fatto
   > per `INSTAGRAM_TOKEN`).

6. **Avvisa Claude** → lui fa il push del codice aggiornato (già pronto e testato) e lancia
   un **test in simulazione** sul robot GitHub. Se la notifica Telegram dice
   *"FB: token OK, Pagina «San Marino Happens»"*, il lasciapassare è buono.

7. **Andare live**: quando decidi, imposta la Variable `PUBLISH_LIVE = true` (è la stessa
   che vale già per Instagram) → da quel momento ogni post esce su **entrambi**.

## ✅ ESITO FINALE (10/07/2026) — BINARIO FACEBOOK COMPLETO E TESTATO
Token Pagina ottenuto (system user token permanente), messo nei GitHub Secrets
`FACEBOOK_PAGE_TOKEN` + `FACEBOOK_PAGE_ID` (= `1199158973289985`), codice pushato
(commit `610ad41` + `e73813a`). **Test in simulazione su GitHub Actions = SUCCESS:** il log
ha stampato *«FB: simulerei la pubblicazione su "San Marino Happens" (token Pagina valido)»* +
*«IG: simulerei…»*. Facebook e Instagram entrambi attivi, nessun post reale. **Manca solo:
`PUBLISH_LIVE=true` per andare live su entrambi.** Come rilanciare il test: GitHub → repo →
Actions → "Publish to Instagram" → Run workflow → campo test_date = `2026-07-09` (data del post
in coda). Il dettaglio del percorso tortuoso è sotto (storico).

## ► STATO SETUP TOKEN — dove siamo arrivati (storico del percorso)

⚠️ **La procedura Graph API Explorer (Strada A originale sopra) NON funziona per questa app.**
Percorso reale seguito con Michele (guidato passo-passo):
- L'app IG esistente "San Marino Happens Publishing" è *solo Instagram Login* → Explorer inutilizzabile.
- **Creata una NUOVA app dedicata: "San Marino Happens Social"** — **App ID `2184885315643638`**,
  caso d'uso *"Gestisci tutto sulla tua Pagina"* (Facebook Login for Business), collegata al
  portfolio business "San Marino Happens". Permessi aggiunti al caso d'uso: `pages_manage_posts`,
  `pages_read_engagement`, `pages_manage_engagement` (+ `pages_show_list` già presente).
- L'Explorer però usa **Facebook Login for Business** → i permessi vengono da una **Configurazione**,
  non dalla lista Permissions. Creata configurazione **"Pubblicazione Pagina" (ID `1814977172554958`)**,
  tipo **Token utente di SISTEMA**, scadenza **Mai**, risorsa **Pagine**, 4 permessi.
- Ma i system user token **NON si generano dall'Explorer** (l'utente di sistema non ha login →
  l'OAuth dà "Sorry, something went wrong"). Si generano dal **Business Manager**.
- In **Business Manager → Utenti di sistema** creato **"Bot Pubblicazione"** — **System User ID
  `61591834229963`**, ruolo Admin. Assegnata la Pagina **San Marino Happens (accesso completo)** e
  l'app **San Marino Happens Social (accesso completo)**. Deciso di aggiungere anche **`read_insights`**
  ai permessi del token (per raccogliere in futuro gli **insight FB** da unire a quelli IG).

🔴 **INTOPPO APERTO — "Genera token" dà "Nessuna autorizzazione disponibile / Assegna un ruolo
dell'app all'utente di sistema".** CAUSA CERTA (doc Meta): **l'app non è ancora *installata* sul
system user** — cosa diversa dall'averle dato accesso (tab "App installate" del Bot = vuoto).
**FIX:**
1. *Via UI:* ricaricare Business Settings, attendere qualche minuto (propagazione lenta), poi
   installare l'app dal tab "App installate" del Bot / riprovare "Genera token".
2. *Via API (metodo ufficiale, se la UI non basta):* `POST /{sysuser-id}/applications` (installa)
   poi `POST /{sysuser-id}/access_tokens` con `scope`=i 5 permessi. Serve l'**App Secret** di
   San Marino Happens Social (Impostazioni app → Basic). ID già noti: sysuser `61591834229963`,
   app `2184885315643638`.

Quando il token c'è → **FACEBOOK_PAGE_ID** = id Pagina San Marino Happens (da `me/accounts` o
Business Settings → Pagine) + **FACEBOOK_PAGE_TOKEN** = il system user token → nei GitHub Secrets →
push del codice → test simulazione. Fonti: developers.facebook.com/docs/business-management-apis/system-users/install-apps-and-generate-tokens/

## Stato del codice (già fatto, 09/07/2026)
- `scripts/publish.py` (repo `sanmarinohappens`) riscritto: **due binari indipendenti**
  IG + FB. Facebook si attiva SOLO se ci sono i due secret; se mancano, resta tutto come
  oggi (solo Instagram). Registro `published.log` ora è **per-canale** (`nome.png|ig` /
  `nome.png|fb`): ogni post esce una volta sola per piattaforma anche se il robot ri-gira.
- In **simulazione** lo script fa una chiamata di **sola lettura** alla Pagina per
  confermare che il token è valido, senza pubblicare.
- `.github/workflows/publish.yml` aggiornato per passare i due secret FB.
- Testato in locale in simulazione: IG-only OK (invariato) + ramo FB OK.
- **Non ancora pushato**: si pusha quando i secret FB sono su GitHub, così testiamo tutto
  insieme in un colpo.

## Punto tecnico da confermare al PRIMO post reale
Nel codice il testo del post Facebook viaggia nel campo `message` dell'endpoint
`/{page-id}/photos`. È la scelta più comune, ma la doc Meta su questo punto è ambigua: se
al primo post reale il testo non comparisse sotto la foto, si cambia `message` in `caption`
(una parola in `pubblica_facebook()`). Da verificare guardando il primo post vero su FB.
