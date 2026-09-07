# Scadenze token

Elenco dei token/segreti con scadenza — **per gli umani**. La copia che conta per la macchina è
[`scadenze-token.json`](scadenze-token.json): la legge `scripts/controllo-scadenze-token.py`, che
gira ogni lunedì dentro il workflow *Metriche settimanali* e manda un Telegram quando mancano 21
giorni o meno a una scadenza. Se aggiungi o cambi una riga qui, **cambiala anche nel JSON** (capita
una volta l'anno: i token si rigenerano di rado).

| Token | Dove vive | Creato | Scade | A cosa serve |
|-------|-----------|--------|-------|--------------|
| `CLAUDE_CODE_OAUTH_TOKEN` | Segreti Actions del repo `sanmarinohappens` | 06/09/2026 | **06/09/2027** | Far girare Claude Code nei workflow in cloud usando l'abbonamento (non il consumo API). Si rigenera con `claude setup-token` sul Mac di Michele e si aggiorna nel segreto — **su una riga sola, senza a-capo**. |

⚠️ Il token OAuth di Claude **non avvisa prima di scadere**: quando scade, i workflow in cloud
smettono di autenticarsi (`Invalid auth token`). Rigenerarlo qualche giorno prima del 06/09/2027.
