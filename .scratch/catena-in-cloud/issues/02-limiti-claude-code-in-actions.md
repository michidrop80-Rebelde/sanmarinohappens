# 02 — Che limiti ha Claude Code dentro GitHub Actions?

Type: research
Status: risolto
Blocked by: —
Modello: Sonnet — raccolta di fatti, meccanica
Sforzo: risolto — ~8 minuti di agente in sottofondo

## Domanda

Prima di costruire, sapere cosa regge e cosa no. Da accertare su **fonti primarie**
(documentazione Anthropic e GitHub, non blog):

1. **Autenticazione**: `claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN`. Come si genera, quanto
   dura, cosa succede quando scade, come ci si accorge che è scaduto.
2. **Consumo**: una run agentica pesa sull'abbonamento (Pro/Max) o viene fatturata a parte? Ci sono
   limiti d'uso per le esecuzioni non interattive?
3. **Durata**: quanto può durare una run di GitHub Actions su repo pubblico (limite per job), e cosa
   succede a un agente che sfora. Il giro settimanale completo oggi sul Mac dura parecchio.
4. **Skill e subagenti**: in modalità non interattiva (`claude -p`), le skill in `.claude/skills/` e
   i subagenti in `.claude/agents/` vengono caricati? L'orchestratore `/smh-giro` lancia 4 subagenti
   in sequenza — funziona headless?
5. **Permessi**: come si autorizzano gli strumenti senza qualcuno che clicchi «consenti». Quali
   strumenti servono (WebSearch, WebFetch, Bash, Read, Write) e come si concedono in modo mirato.
6. **MCP**: si possono registrare server MCP in Actions? (serve saperlo per la fase 2 di Canva,
   anche se qui è fuori scopo — la risposta orienta la mappa futura).
7. **Sicurezza**: come si impedisce che un agente esposto a contenuti web ostili usi il token del
   repo per fare danni. Permessi minimi del `GITHUB_TOKEN`, e cosa NON va messo tra i segreti
   visibili al passo che ragiona.

Interessa il **fatto verificato con link alla fonte**, non l'impressione. Dove la documentazione non
risponde, dirlo esplicitamente invece di colmare il buco.

## Risposta

Documento completo: [`../research/02-limiti-actions.md`](../research/02-limiti-actions.md)
(7 sezioni, ogni affermazione con link a fonte primaria Anthropic/GitHub).

**Verdetto: può girare, ma non così com'è.**

I fatti che contano:

1. **Token** — `claude setup-token` dura **un anno**, viene solo stampato a schermo (non salvato),
   e fa **solo richieste al modello**. Alla scadenza le run falliscono con `OAuth token has expired`.
   ❌ **Nessun avviso preventivo per la CI**: l'avviso «scade fra 3 giorni» esiste solo per il login
   interattivo. Il primo segnale sarà una run rossa. → nuovo ticket **12**.
2. **Consumo** — le run pesano **sull'abbonamento di Michele**, stesso serbatoio dell'app Claude
   (finestra a 5 ore + limite settimanale). 🔴 **Un giro pesante il lunedì mattina può lasciare
   Michele senza Claude anche sul Mac.** Nessuna quota separata per l'uso non interattivo. I minuti
   di Actions sono gratis perché il repo è pubblico.
3. **Durata** — 6 ore per job; se sfora, il job muore e **si perde tutto il non committato** → il
   giro va spezzato in pezzi con salvataggi intermedi. In più: `claude -p` **abbandona i subagenti
   dopo 10 minuti di attesa a vuoto**, buttando il risultato parziale.
4. **Skill e subagenti** — funzionano headless; la documentazione descrive esattamente il nostro caso
   (checkout + `/nome-skill` come prompt). ⚠️ **Mai `--bare`**: spegne skill, subagenti, MCP e
   CLAUDE.md, e non legge nemmeno il token. Asterisco: «there's no built-in orchestrator» — la
   sequenza di `/smh-giro` è un'istruzione nel prompt, non un meccanismo garantito (come già oggi).
5. **Permessi** — si parte in modalità Manual, va concesso tutto esplicitamente. ⚠️ **Trappola:** in
   una cartella mai «fidata» (= ogni runner GitHub) i `permissions.allow` di `.claude/settings.json`
   vengono **ignorati** → vanno passati dal workflow. Esistono modalità apposta per job non presidiati.
6. **MCP** — registrabili, ma **l'OAuth interattivo non è eseguibile headless**: conferma documentale
   del nodo Canva già registrato il 18/08. La fase 2 dovrà passare dall'API Connect, non dall'MCP.
7. **Sicurezza** — al workflow basta `contents: write`. ⚠️ La documentazione consiglia di negare
   `curl`, ma **noi mandiamo i Telegram con curl** → va concesso stretto, solo verso l'API Telegram.
   ⚠️ `show_full_output` si accende da solo col debug di Actions: su repo pubblico espone tutto.

🔴 **Il blocco vero non è nessun limite di piattaforma: sono i 41 percorsi assoluti
`/Users/michele/...` sparsi in 13 file** fra skill e agenti. Su un runner quella cartella non esiste
e ogni comando fallisce. Verificato in proprio: 13 file, 41 occorrenze. → nuovo ticket **11**.

⚠️ **Resta da provare, non da leggere:** la documentazione **non conferma esplicitamente** che
Actions carichi `.claude/agents/`. È coerente col resto, ma è una deduzione — primo test della sonda.
