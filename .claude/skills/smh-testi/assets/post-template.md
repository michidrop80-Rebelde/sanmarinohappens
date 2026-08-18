# Template della bozza di post

Ogni evento verificato diventa un blocco come questo nel file
`dati/post/post-AAAA-MM-GG.md`. Pensato per essere copiato-incollato così com'è.

```markdown
---
## [GG/MM] — [Titolo evento]   ·   tipo: [sport/cultura/musica/…]

**📷 Testo per la grafica**
- Titolo breve: [max 5-6 parole]
- Sottotitolo: [data + luogo, es. "28 giugno · Campo Bruno Reffi"]

**📝 Caption (Instagram + Facebook)**
[Gancio iniziale di 1 riga]

[2-4 righe: cosa, quando, dove, un dettaglio reale preso dal file verificato.
Niente dati inventati.]

🗓 [GG/MM/AAAA] · 🕗 [ora se presente, altrimenti ometti] · 📍 [luogo]
[CTA da config.post.cta_default]
[disclaimer da config.post.disclaimer]

**#️⃣ Hashtag**
[hashtag fissi] [2-4 hashtag specifici]

**📱 Testo storia** (per la grafica storie — 1 storia per evento)
- Titolo storia: [1 riga; sport → "Squadra vs Avversario", abbrevia (SM) prima di tagliare il "vs"]
- Data: [GG/MM/AAAA]   ← il GIORNO della settimana lo calcola la grafica in Python, non scriverlo
- Ora: [HH:MM oppure "non specificato"]
- Luogo: [luogo ufficiale]
- Descrizione breve: [1-2 righe, ~10-16 parole, voce del brand; aggiunge il "cosa/perché", NON ripete data·ora·luogo; mai prezzi/gratis; solo dati verificati, altrimenti "non specificato"]

**🔗 Fonte:** [URL dal file verificato]
**Stato bozza:** da-approvare
```

## Regole sul formato
- **Una bozza per evento.** Ordina per data crescente.
- **Caption breve** (vedi `post.lunghezza_caption`): leggibile da telefono, niente muri di testo.
- **Emoji con misura** (2-4), mai una ogni parola.
- **Solo dati reali**: data/ora/luogo/dettagli vengono dal file verificato. Campo assente → si omette dalla caption (niente "ore 00:00" o luoghi inventati).
- **📱 Testo storia in OGNI evento** (anche quelli da riepilogo): è ciò che la grafica mette nel template storie. La *descrizione breve* è l'unico testo creativo — voce del brand, mai inventata, mai prezzi, non ripete data/ora/luogo. Dato mancante → "non specificato". Vedi skill Step 4b.
- **Fonte sempre riportata** (serve a Michele per un ultimo controllo prima di pubblicare).
- **Stato bozza:** sempre `da-approvare` all'uscita di questo agente.

## Post riepilogo settimana (opzionale)
Se ci sono molti eventi ravvicinati, in fondo al file puoi aggiungere UN post lista:
```markdown
---
## 📅 [opzionale] La settimana a San Marino ([GG]–[GG] mese)
- [GG/MM] [Titolo] — [luogo]
- [GG/MM] [Titolo] — [luogo]
...
[hashtag fissi]
**Stato bozza:** da-approvare
```
Etichettalo chiaramente come opzionale: Michele sceglie se usarlo.
