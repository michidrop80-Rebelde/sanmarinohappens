# Template di un evento

Ogni evento trovato va salvato nel file `dati/eventi/eventi-AAAA-MM-GG.md` con esattamente questo formato:

```markdown
## [Titolo evento]
- **Data:** GG/MM/AAAA — ore HH:MM
- **Luogo:** [castello/città — indirizzo se disponibile]
- **Tipo:** [sport | cultura | musica | sociale | istituzionale | altro]
- **Descrizione:** [2-3 righe]
- **Fonte:** [URL della pagina dove l'hai trovato — serve solo a verificare]
- **Fonte tipo:** [diretta | aggregatore]
- **Link pubblico:** [URL diretto organizzatore/biglietti/prenotazione — oppure `non disponibile`]
- **Stato:** da-verificare
```

## Regole sul formato
- **Campo mancante** → scrivi `non specificato`. Non inventare MAI un valore plausibile.
- **Evento che non supera l'auto-verifica** → aggiungi `⚠️` davanti al titolo e una riga `- **Avviso:** [motivo del dubbio]`. Non scartarlo: lo decide Michele.
- **Stesso evento su più fonti** → tienilo una volta sola ed elenca tutte le fonti nel campo `Fonte`.
- **`Link pubblico`** = solo pagina **diretta** (organizzatore/biglietti/prenotazione), MAI un aggregatore (visitsanmarino, usc, portali). Solo aggregatore disponibile → `non disponibile`. È il link che userà il sito pubblico; l'aggregatore serve solo a verificare.
- Lo **Stato** all'uscita di questo agente è sempre `da-verificare`: la conferma la fa l'agente di verifica.

## Sezioni di chiusura del file
Dopo l'elenco eventi, aggiungi se serve:

```markdown
---
## ⚠️ Fonti non raggiungibili
- [nome fonte] — [errore: 403 / 404 / timeout]

## 🔧 Auto-miglioramento di oggi
- [cosa hai aggiunto/aggiornato nei file fonti]
```
