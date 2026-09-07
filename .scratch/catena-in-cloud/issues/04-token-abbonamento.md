# 04 — Il token dell'abbonamento nei segreti di GitHub

Type: task (serve Michele)
Status: resolved
Blocked by: —
Modello: Sonnet — è una guida passo-passo, non c'è niente da decidere
Sforzo: brevissimo (5-10 minuti) — la parte lenta la fa Michele nel browser

## Domanda

Perché Claude possa girare in cloud usando **l'abbonamento** (e non il consumo a pagamento) serve un
token generato da Michele sul suo Mac e incollato tra i segreti del repo.

**Da fare:**
1. Generare il token (`claude setup-token`) — richiede un'autorizzazione nel browser, quindi la fa
   Michele; io lo guido passo passo, un comando alla volta.
2. Metterlo tra i segreti del repo come `CLAUDE_CODE_OAUTH_TOKEN` (Settings → Secrets and variables
   → Actions). ⚠️ Il repo è **pubblico**: il token va nei *segreti*, mai in un file.
3. **Annotare la data di scadenza** da qualche parte che non si perda.
4. Verificare che ci sia (senza stamparlo) con una run di prova.

**Fatto quando:** una run banalissima di GitHub Actions riesce ad autenticarsi come Claude.

Nota: questo ticket si può fare **in parallelo** agli altri — non dipende da niente.

## Answer

✅ **Fatto e verificato il 06/09/2026.**

- Michele ha generato il token con `claude setup-token` (autorizzazione browser, account
  dell'abbonamento — non una API key a pagamento).
- Messo tra i **segreti Actions** del repo `sanmarinohappens` come `CLAUDE_CODE_OAUTH_TOKEN`
  (Settings → Secrets and variables → Actions → Repository secrets). Il repo è pubblico ma i segreti
  restano mascherati nei log.
- **Scadenza: 06/09/2027** (il token dura 1 anno esatto e non avvisa prima). Annotata in
  `dati/scadenze-token.md`, dove il ticket 12 (avviso scadenza) andrà a leggerla.
- **Run di prova:** workflow `.github/workflows/test-auth-claude.yml` (trigger manuale
  `workflow_dispatch`) — installa Claude Code e gli fa dire una frase. Run #3 → **Success** in 14s
  (run/34062097053). Claude si autentica in cloud usando l'abbonamento.

**Intoppi incontrati (per la memoria):**
1. Prima versione del workflow: errore YAML perché la frase di prova conteneva `: ` (due punti +
   spazio) dentro una stringa `run:` non quotata a blocco. Risolto con `run: |`.
2. Primo tentativo di run: `Invalid Authorization header value from CLAUDE_CODE_OAUTH_TOKEN: it
   contains a line break`. Il token era stato incollato nel segreto **con un a-capo in mezzo**
   (preso copiando dal Terminale, dove era andato a capo). Reincollato su una riga sola via TextEdit
   in Solo Testo → run verde.

**Il workflow di prova resta nel repo** come strumento di ri-test manuale (utile quando si rigenera
il token nel 2027).
