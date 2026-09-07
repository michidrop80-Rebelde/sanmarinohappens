# Fix: le approvazioni non devono più scadere

Traccia preparata il **27/07/2026** per la sessione della sera. Non è ancora stato fatto niente:
questo file è il piano.

---

## Il problema, in una riga

**Le risposte di Michele scadono dopo 24 ore, e il raccoglitore passa una volta a settimana.**

### Perché succede

Il bot delle approvazioni (`@sanmarinohappens_bot`) riceve le risposte con il metodo
**`getUpdates`**, che ha due proprietà scomode:

1. **Consegna una volta sola.** Appena qualcuno legge, i messaggi spariscono dai server di
   Telegram. Non esiste un «già letto» da rileggere. Il 27/07 una mia lettura diagnostica ha
   distrutto 3 approvazioni di Michele in tempo reale — recuperate solo perché le avevo
   trascritte a mano un attimo prima.
2. **Conserva per un massimo di 24 ore.** Quello che nessuno legge entro un giorno, Telegram lo
   butta. Senza errori, senza traccia: sparisce.

Ora si guardi la cadenza della catena:

| Quando | Cosa succede |
|---|---|
| lunedì 08:05 | il giro manda a Michele la lista da approvare |
| martedì 08:05 | il raccoglitore passa a leggere le risposte |
| martedì 11:06 | la grafica compila gli approvati |

Michele ha **poco più di 24 ore** per rispondere. Se risponde martedì pomeriggio, mercoledì, o
nel weekend, **la risposta evapora prima che qualcuno la legga** — e nessuno se ne accorge,
perché non lascia traccia da nessuna parte.

**È molto probabilmente questa la causa delle «approvazioni che non prendevano» andate avanti per
mesi.** Non era Michele che dimenticava, e non era l'app: era la casella che si svuotava.

### Cosa NON è (già verificato il 27/07)

- ❌ **Non è l'app desktop.** Provato dal vivo: un click dal computer è arrivato pulito e
  immediato (`approve_01`, chat corretta).
- ❌ **Non è un webhook che dirotta.** `getWebhookInfo` → `url` vuoto.
- ❌ **Non è un processo che consuma.** Nessun listener in esecuzione (`ps`).
- ❌ **Non sono i pulsanti.** Funzionano: 17 click su 17 sono arrivati correttamente.

---

## La soluzione

**Smettere di dipendere da una casella che scade.** Le risposte devono finire subito in un file
del repo GitHub, dove possono restare settimane senza deteriorarsi.

L'infrastruttura **c'è già ed è gratuita**: il Cloudflare Worker dell'altro bot
(`@sanmarinohappens_add_bot`) è acceso 24 ore su 24, riceve via **webhook** e scrive nel repo.
E soprattutto — verificato il 27/07 — **`smh-bot-worker.js` sa già gestire i `callback_query`**
(riga ~64: `if (update.callback_query) await handleCallback(...)`).

### Come funzionerebbe

```
Michele preme ✅  →  Telegram chiama SUBITO il Worker (webhook, niente coda che scade)
                  →  il Worker scrive la risposta in  queue/approvazioni.md  su GitHub
                  →  /smh-approvazione legge quel FILE, non più getUpdates
```

Le risposte diventano **permanenti**: Michele può rispondere quando vuole, anche una settimana
dopo, e la catena le trova comunque.

---

## ⚠️ La trappola da non sbagliare

**Webhook e `getUpdates` si escludono a vicenda.** Nel momento in cui si imposta un webhook sul
bot delle approvazioni, `getUpdates` smette di funzionare **per sempre** su quel bot (risponde
errore 409). Quindi l'ordine dei lavori non è opzionale:

1. **prima** si insegna a `/smh-approvazione` a leggere dal file;
2. **poi** si accende il webhook.

Se si inverte, la catena resta cieca fino al fix successivo.

Si torna indietro con `deleteWebhook` — ma solo se il passo 1 non è ancora stato fatto.

---

## Passi per stasera

1. **Decidere il canale.** Due strade:
   - **(a) un solo Worker per due bot** — si aggiunge una rotta col secondo token. Meno pezzi da
     mantenere, ma si tocca un Worker che oggi funziona.
   - **(b) un secondo Worker dedicato** alle approvazioni. Più isolato, il bot degli eventi non
     rischia niente. **Consigliata**, visto che l'altro bot è l'unico canale che oggi regge.
2. **Scrivere il ramo approvazioni** nel Worker: da `callback_query` con `approve_XX`/`reject_XX`
   → riga in `queue/approvazioni.md` (id, esito, titolo, data ISO, mittente), + risposta
   `answerCallbackQuery` così il pulsante di Michele smette di girare e mostra «Ricevuto ✅».
3. **Riscrivere lo Step di lettura di `/smh-approvazione`**: legge `queue/approvazioni.md`,
   incrocia con `pending_events`, e **archivia le righe consumate** (`- [x]`) invece di
   cancellarle — così restano tracciabili, come già si fa per le foto.
4. **Solo alla fine**: `setWebhook` sul bot delle approvazioni. Poi prova dal vivo con un
   pulsante e verifica che la riga compaia nel repo.
5. **Aggiornare** `CLAUDE.md` (anello 4) e la memoria [[reference_telegram_urllib_ssl]].

## Cosa serve dalle mani di Michele

- Incollare il codice del Worker su Cloudflare e premere **Deploy** (come già fatto il 23/07 per
  le foto — la procedura è in `infra/cloudflare/DEPLOY.md`).
- Il token del bot delle approvazioni va messo come **variabile d'ambiente del Worker**, mai nel
  codice.

## Regola valida da subito, anche prima del fix

🚫 **Non «sbirciare» mai la posta del bot con `getUpdates` per curiosità o per diagnosi.** Ogni
lettura la svuota. Legge solo `/smh-approvazione`, e quando legge **salva sul disco nello stesso
passaggio**, prima di elaborare.
