# Aggancio alla catena: quando gira il passo sport

Type: grilling
Status: aspetta Michele: ticket con Michele pronto (07/10 07:29)
Modello: Opus · medium (dato da Jhonny il 07/10 07:29, regola di lavorare-leggeri)
Blocked by: —

## Question

Il post esce **lunedì alle 18:00**, ma la catena `smh-catena` gira alle **18:30**. Se il passo
sport girasse lunedì, arriverebbe mezz'ora dopo il treno.

**Ipotesi da verificare e decidere**: il passo sport gira nella catena di **domenica sera
(18:30)** e produce la busta con data di pubblicazione lunedì 18:00, che cron-job.org fa
partire puntuale. Nessun task pianificato nuovo, nessun costo nuovo. In più il timing del
ricontrollo alla fonte è ottimo: domenica sera i calendari della settimana sono usciti.

Da chiarire:

- Regge davvero? La busta va in coda su GitHub la domenica sera per uscire il lunedì: è lo
  stesso schema degli aggregati (weekend prodotto il mercoledì per il giovedì)?
- Il post sportivo passa dal cancello `/smh-check`? Quali dei sei controlli hanno senso su un
  contenuto sportivo (il «vs Avversario» sì di sicuro; i prezzi probabilmente no).
- Passa dall'approvazione ✅/❌ su Telegram come tutto il resto, o è talmente ripetitivo che
  l'approvazione diventa rumore settimanale?
- Che **tipo** è la busta (`tipo: sportivo`)? Il robot di pubblicazione va istruito?
