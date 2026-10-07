# Architettura dati: magazzino stagione o registro unico?

Type: grilling
Status: aspetta Michele: ticket con Michele pronto (07/10 07:29)
Modello: Opus · medium (dato da Jhonny il 07/10 07:29, regola di lavorare-leggeri)
Blocked by: —

## Question

Dove vivono le partite? Oggi tutto il progetto ruota attorno a `dati/calendario/master.md`
(159 righe dopo tre mesi): ci leggono dentro le guardie, `scripts/genera-calendario.py` e
l'agente testi. Una stagione di solo campionato sammarinese sono ~240 partite.

**Proposta sul tavolo** (fatta in chat il 26/08, non ancora approvata):

- **`dati/sport/stagione-2026-27.md`** — file nuovo, il calendario grezzo delle sei
  competizioni. Una riga per partita. Non è un file di contenuti: nessuno pubblica da qui,
  è il magazzino da cui si pesca.
- **Il master resta il registro di cosa si pubblica** e riceve una riga compatta per ogni
  *giorno* con sport («dom 18/10 · 8ª giornata di campionato · 8 partite»), più una riga per
  il post settimanale. Da 240 righe a ~10 al mese.
- Le righe sportive proiettate portano una **marcatura di categoria** che dice «negli
  aggregati scritti non ci vado»: è così che settimanale e weekend sanno di saltarla e mettere
  il rimando, mentre le storie sanno di doverla dire (vincolo 5).

**Perché così**: le storie di ogni giorno si costruiscono dal master. Con la proiezione
compatta, storie, guardie e calendario del sito continuano a leggere una sorgente sola e non
va toccato niente a valle. L'alternativa — far leggere due sorgenti a tutti gli strumenti —
costringe a rimettere le mani su ogni guardia e sul generatore del sito.

**Da decidere qui**: la divisione regge? La marcatura di categoria è il meccanismo giusto o
serve altro? E la proiezione la fa la skill del lunedì, o un passo separato?
