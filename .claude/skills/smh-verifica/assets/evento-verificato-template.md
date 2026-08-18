# Template del file verificato

L'output va salvato in `dati/eventi/verificati/eventi-verificati-AAAA-MM-GG.md`
(stessa data del file di input) con **tre sezioni in quest'ordine**.

## Intestazione del file
```markdown
# Eventi verificati — AAAA-MM-GG
Input: dati/eventi/eventi-AAAA-MM-GG.md
Verifica: [data/ora] · finestra AAAA-MM-GG → AAAA-MM-GG
```

## Sezione 1 — ✅ Verificati (pronti per i testi)
Un evento per blocco, con questo formato:
```markdown
## [Titolo evento]
- **Data:** GG/MM/AAAA — ore HH:MM
- **Luogo:** [luogo confermato]
- **Tipo:** [sport | cultura | musica | sociale | istituzionale | altro]
- **Descrizione:** [2-3 righe]
- **Fonte:** [URL confermato]
- **Verifica:** [come l'hai confermato in una riga — es. "confermato su visitsanmarino + sanmarinortv, data e luogo coincidono"]
- **Stato:** verificato
```
Regola dura: in questa sezione **Data, Luogo e Fonte non possono essere `non specificato`**.
Se manca un campo essenziale e non lo trovi → l'evento va in "Da confermare", non qui.

## Sezione 2 — ⚠️ Da confermare (Michele)
Eventi reali ma con un dubbio non risolvibile da soli:
```markdown
## ⚠️ [Titolo evento]
- **Data:** ... (o "incerta: GG/MM o GG/MM")
- **Luogo:** ...
- **Tipo:** ...
- **Fonte:** [URL]
- **Dubbio:** [cosa NON sei riuscito a confermare e perché — specifico]
- **Cosa serve:** [l'azione che Michele deve fare — es. "scegliere la data giusta", "confermare casa/trasferta"]
- **Stato:** da-confermare-michele
```

## Sezione 3 — 🗑 Scartati
Eventi rimossi dal flusso, **mai cancellati**, sempre con motivo:
```markdown
## 🗑 [Titolo evento]
- **Motivo:** [passato | fuori San Marino | doppione di "X" | fonte sparita | evento inesistente | fuori finestra]
- **Fonte controllata:** [URL]
- **Stato:** scartato
```

## Regole sul formato
- Ogni evento sta in **una sola** delle tre sezioni: niente doppioni tra sezioni.
- **Non inventare** un valore per riempire un campo: se non c'è sulla fonte, resta `non specificato` e l'evento scende in "Da confermare".
- Mantieni il `Tipo` tra le categorie di `config.json`.
- Riporta sempre la **Fonte** (URL) anche per gli scartati: serve a Michele per ricontrollare.
