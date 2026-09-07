# 05 — La sonda: un giro finto che prova tutto

Type: task
Status: resolved
Blocked by: 02, 04
Modello: Sonnet per scrivere il workflow · Opus se si impunta e serve capire perche'
Sforzo: media (una sessione)

## Domanda

Prima di costruire la catena vera, un giro finto che dimostri che la strada regge. La lezione di
agosto applicata qui: se non regge, lo scopriamo in mezz'ora invece che a lavoro fatto.

**Un workflow lanciabile a mano** (`workflow_dispatch`) che fa cinque cose e riferisce:

1. si sveglia e clona il repo
2. si autentica come Claude e legge `dati/calendario/master.md` — deve **citare un evento vero**
   preso da lì (prova che vede i dati, non che dice di vederli)
3. fa **una** ricerca web su una fonte del progetto
4. lancia uno script Python del progetto (una guardia) e ne riporta l'uscita
   ⚠️ `controllo-integrita.py` contiene un percorso assoluto (ticket 11): se fallisce per quello,
   e' un'informazione utile, non un fallimento della sonda — annotarlo e proseguire
5. scrive un file, fa commit e push
6. manda un Telegram con l'esito

**Deve anche misurare**, perché è l'unica cosa che ad agosto era rimasta «da misurare, non da
stimare»: quanto dura la run, e quanto abbonamento consuma. Il numero va scritto nella risposta.

**Fatto quando:** la run è verde, il Telegram arriva, il commit c'è, e ho i due numeri in mano.

Se qualcosa non passa, il ticket si chiude lo stesso — con scritto **cosa** non passa. Una sonda che
fallisce ha fatto il suo lavoro: ci ha risparmiato la costruzione.

## Lavori

- 06/09/2026 — Scritto e messo online il workflow `.github/workflows/sonda-catena.yml`
  (commit `1444390`, su `main`). `workflow_dispatch` puro: non parte da solo. Il passo di Claude
  ha in mano **solo** `CLAUDE_CODE_OAUTH_TOKEN`; commit/push e Telegram sono passi di shell separati.
  Misura durata (orologio della run + `duration_ms` di Claude), turni, costo `$` equivalente e token
  da `--output-format json`.
- **In attesa**: Michele lancia la run a mano (Actions → «Sonda catena» → Run workflow → `main`) e
  riporta esito + Telegram + i due numeri. Senza quello il ticket resta `claimed`.

## Answer

**LA STRADA REGGE.** Run verde il 06/09/2026 21:58 UTC
([run 34062579733](https://github.com/michidrop80-Rebelde/sanmarinohappens/actions/runs/34062579733),
referto committato `1cb9c8d`, Telegram arrivato). Tutti e sei i passi passati:

1. ✅ clona il repo — ok
2. ✅ Claude si autentica con l'abbonamento e **cita un evento vero** dal registro:
   «San Marino Antiqua 2026, 24-26/07, Centro Storico» (riga 31). Vede i dati, non lo dice e basta.
3. ✅ una ricerca web su visitsanmarino.com — risultati pertinenti e coerenti col registro
4. ⚠️ `controllo-integrita.py` **esce 1** — ma **NON** per il percorso assoluto del ticket 11
   (quello non si è manifestato). Esce 1 perché in cloud mancano 9 file che le istruzioni citano:
   `.claude/secrets/github.json` + `telegram.json` (giusto che manchino, sono gitignorati),
   `dati/config.json`, `dati/fonti-sport.md`, `references/formato-grafica.md`,
   `sito/STATO-SITO.md`, `sito/calendario-eventi.html`, `docs/FIX-APPROVAZIONI-CHE-SCADONO.md`,
   e la cartella `~/.claude/scheduled-tasks`. → alimenta i **ticket 03 e 11**.
5. ✅ scrive il referto, 6. ✅ commit+push, 7. ✅ Telegram.

### I DUE NUMERI (l'unica cosa che ad agosto era «da misurare»)

| | valore | lettura |
|---|---|---|
| **Durata** | **47 s** totali (46,2 s dentro Claude) | un giro-giocattolo è quasi istantaneo; il collo di bottiglia sarà il lavoro vero, non l'infrastruttura |
| **Consumo** | **$0,285** valore equivalente · 10 turni · out 3.158 tok · cache-read 332k + cache-create 41k · input vero 14 tok | **questa è la base per il ticket 06**: un giro reale (ricerca + verifica + testi su 5-10 eventi) sarà molte volte tanto — ora c'è un metro, non una stima |

### Scoperte da portarsi dietro

- **L'autenticazione OAuth headless + i tool base (Read, WebSearch, Bash) funzionano in cloud.**
  Il muro Canva resta (non provato qui, ma già confermato). I **subagenti** `.claude/agents/` non
  sono stati esercitati dalla sonda → il dubbio del ticket 02 «l'Action carica davvero gli agenti?»
  resta da chiudere quando si costruisce l'orchestratore vero (ticket 08/10).
- **`controllo-integrita.py` pretende file che in cloud non esisteranno mai** (`.claude/secrets/*`).
  Va reso consapevole dell'ambiente, o quei riferimenti vanno tolti dalle istruzioni → ticket 03.
- **Node 20 deprecato** su `actions/checkout@v3` e `setup-python@v4`: vale per **tutti** i workflow
  del repo (publish, metrics, guardia-imminenti…), non solo la sonda. Manutenzione a parte, non blocca.
