# Auto-verifica — controlli di sanità sugli eventi

Carica questo file quando devi applicare i controlli prima di salvare un evento.
Obiettivo: non salvare spazzatura, ma **non scartare nulla in silenzio**. Gli eventi
dubbi si salvano con `⚠️` così Michele decide.

## I controlli

### 1. Data sensata
- Non nel passato (uguale o successiva a oggi).
- Non impossibile (es. 30 febbraio, mese 13).
- Dentro la finestra `ricerca.finestra_giorni` della config (default 60 giorni).
- Se manca l'anno o è ambigua → deducila dal contesto e marca l'evento con `⚠️`.

### 2. Doppia fonte quando possibile
- Se un evento importante compare su **una sola fonte poco affidabile**, prova a
  confermarlo con una seconda ricerca.
- Confermato → bene, salva normale.
- Non confermato → salva con `⚠️` e `Stato: da-verificare`.

### 3. Coerenza interna
- Luogo e tipo evento hanno senso insieme? Esempi di campanelli d'allarme:
  - una partita di baseball nello stadio di calcio;
  - un concerto in un museo chiuso di sera;
  - un evento "a San Marino" con indirizzo in un'altra città.
- Incoerenza → `⚠️` + riga `Avviso`.

### 4. Sport — verifica casa/trasferta
- Includi solo le **partite in casa** delle squadre sammarinesi.
- Controlla che lo stadio/palazzetto sia effettivamente a San Marino
  (es. San Marino Stadium, Serravalle).
- Coppe europee: la sede può cambiare — se discordante tra fonti, `⚠️`.

## Come marcare un evento dubbio
Davanti al titolo metti `⚠️` e aggiungi una riga:
```markdown
- **Avviso:** [motivo specifico del dubbio]
```
Mai eliminare un evento solo perché dubbio: l'avviso serve a far decidere Michele.
