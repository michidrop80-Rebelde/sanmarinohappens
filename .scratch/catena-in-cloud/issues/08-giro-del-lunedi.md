# 08 — Il giro del lunedì gira in cloud

Type: task
Status: in lavorazione (sessione 07/09/2026 sera) — Michele
Blocked by: 01, 03, 05, 07, 11
Modello: Opus — orchestrazione + confronto dei risultati fra due catene
Sforzo: lunga — il ticket piu' grosso della mappa, mettere in conto piu' di una sessione

## Domanda

Costruire il workflow settimanale che fa quello che oggi fa `smh-giro-settimanale` sul Mac:
ricerca → postino → verifica → testi, e finisce mandando a Michele le bozze coi pulsanti.

**La regola di questo ticket: il task sul Mac resta ACCESO.** Si fanno girare tutti e due e si
confrontano i risultati — stessi eventi trovati? stesse verifiche? stesse bozze? Finché non ci
fidiamo, il cloud è un secondo parere, non il titolare. (Attenzione ai doppioni: due catene che
scrivono lo stesso file di oggi si sovrascrivono — va gestito prima di lanciare, non dopo.)

**Fatto quando:** un lunedì il cloud ha prodotto un giro che regge il confronto con quello del Mac,
e Michele ha ricevuto un solo riepilogo sensato sul telefono.

## Capitolato dal ticket 06 (deciso 07/09/2026 — non si riapre)

- **4 tappe separate, con `commit` dopo ognuna:** ricerca → postino → verifica → testi. Motivo
  misurato: il giro del 24/08 è morto a metà corsa sul limite delle 5 ore (partito 06:24, morto
  11:06) e in cloud si sarebbe perso tutto il non committato. Se il serbatoio finisce alla terza
  tappa, le prime due restano salve.
- **Sveglia: lunedì 03:00.** Non per risparmiare token (sono gli stessi), ma per non contendere il
  serbatoio a Michele. ⚠️ Mai alle 18:30: il limite settimanale si azzera alle 18:00
  (Europe/San_Marino) ed è il momento di massima contesa.
- **Sul 429 (serbatoio vuoto): una riprova dopo 6 ore, poi un Telegram di una riga** che dice che
  la catena è ferma. Il 21/08 una corsa è morta sul 429 e nessuno se n'è accorto.
- **Peso atteso:** ~$40 di valore equivalente per un giro completo (misura del 24/08).

## Capitolato dal ticket 07 (deciso e provato 07/09/2026 — non si riapre)

- **Il riepilogo coi pulsanti si manda in DUE passi**, e il passo dell'agente non ha mai in
  mano `TELEGRAM_BOT_TOKEN`: `telegram-giro.py prepara` (l'agente) scrive la busta,
  `telegram-giro.py invia` (passo di shell separato, con la chiave) spedisce. Il blocco YAML
  già collaudato si copia da `.github/workflows/prova-pulsanti.yml`: lì cambia solo **cosa**
  l'agente mette in busta (eventi veri invece dei due finti).
- **La mappa del giro va committata** (`dati/telegram/pending/<giro>.json` +
  `ultimo-giro.txt`): senza, le risposte di Michele non sono riconducibili a nessun evento.
  ⚠️ Due `git add` separati e passo **rosso** se l'invio è riuscito ma non c'è niente da
  committare — la prima corsa del 07/09 era verde e non aveva committato niente.
- **Se la busta resta dopo `invia`, l'invio è fallito**: la corsa deve essere rossa, e la
  busta va lasciata dov'è (non si cancella per far tornare il verde).

---

## Stato al 07/09/2026 (sera) — costruito e provato, MANCA il lunedì vero

Il ticket **resta aperto**: il suo «fatto quando» chiede un lunedì in cui il cloud abbia prodotto
un giro che regge il confronto con quello del Mac. Quel lunedì è il **14/09/2026**. Tutto il resto
è costruito e provato.

### Come è stato risolto il nodo «due catene, stessi file»
Il cloud lavora su un **ramo git separato** (`giro-cloud`), non su `main`. Stessi percorsi, stesse
skill, zero modifiche agli anelli — ma niente di quello che scrive finisce dove lavora il Mac.
Il ramo è usa-e-getta: ogni lunedì riparte da `main`. Il confronto fra i due giri diventa un
`git diff`, e il problema dei doppioni sparisce invece di essere gestito.

### Decisione di Michele (07/09/2026): un solo mazzo di pulsanti
Alle 03:00 il cloud manda **un messaggio senza pulsanti** («secondo parere: N eventi, N verificati,
N bozze»). Alle 08:05 il Mac manda i pulsanti ✅/❌ come sempre. Scartate: il silenzio totale del
cloud (se si rompe di notte non lo sai) e il cloud titolare subito (va contro la regola del ticket).
Il blocco a due passi del ticket 07 resta comunque **esercitato per davvero**: il referto passa da
`prepara --solo-riepilogo` (nessuna chiave) e da `invia` (l'unico passo col token).

### Cosa esiste adesso
- `.github/workflows/giro-cloud.yml` — 6 job: `prepara` + 4 tappe + `avviso`.
  - Sveglia `0 1 * * 1` (lunedì 03:00 locali) e **ripresa** `0 7 * * 1` (09:00): la ripresa salta
    le tappe già uscite bene e rifà solo quelle rimaste indietro. È anche la riprova «a +6h»
    decisa per il 429 (serbatoio vuoto): un solo meccanismo copre tutti e due i casi.
  - Ogni tappa è un **job a sé** → 6 ore di tempo ciascuna invece di 6 in tutto, e il lavoro si
    salva sul ramo prima di passare il testimone.
  - Si ferma con grazia se ricerca e postino danno entrambi zero: la verifica non parte.
- `.github/scripts/chiudi-tappa.sh` — salvataggio + conteggio, in un posto solo per tutte e quattro.
- `.github/scripts/referto-giro-cloud.py` — il testo che Michele legge, nei quattro casi
  (completo · fermato con grazia · caduto · caduto di nuovo alla ripresa).
- `scripts/conta-giro.py` — i numeri di un giro **misurati dai file**, mai chiesti all'agente.
- `scripts/confronta-giri.py` — il confronto Mac/cloud. I titoli si accostano per **contenimento di
  parole**, non per somiglianza: la somiglianza fondeva «San Marino - Finlandia» con «San Marino -
  Albania» (due partite diverse) e separava «Concerto a lume di candela» dal suo stesso concerto
  col sottotitolo.
- `smh-giro` ha un nuovo **Step 3c**: il giro del Mac lancia il confronto e ne mette la riga nel
  messaggio Telegram e nel riassunto. Così Michele lo vede dove già guarda, senza lanciare niente.

### Provato (senza far girare niente in cloud)
`chiudi_tappa_test.sh` 14/14 (repo + remoto finti: marcatore, push sul ramo, caduta che NON scrive
il marcatore) · `referto_giro_cloud_test.py` 23/23 · `confronta_giri_test.py` 20/20 (su titoli veri
del 07/09) · `telegram_giro_test.py` 48/48 · `controllo_token_agente_test.py` 12/12 ·
guardia integrità ✅ 133 riferimenti · guardia token-agente ✅ 10 file.
Confronto provato **end-to-end contro un ramo git vero** in un clone: ha accostato il titolo
riscritto e segnalato nei due versi l'evento scambiato.

### Effetto collaterale utile
`controllo-token-agente.py` aveva un buco: guardava solo `.github/workflows/*.yml` e solo i
`${{ secrets.X }}`. Bastava spostare un passo dentro un'azione composita, o passare la chiave da
`inputs.`, per sfuggirle. Ora guarda anche `.github/actions/*/action.yml` e riconosce la chiave dal
**nome della variabile d'ambiente**, da dovunque arrivi il valore.

### Cosa manca per chiudere
1. Il **primo giro vero**: lunedì 14/09 alle 03:00 (o a mano prima, con *Run workflow*).
2. Guardare il confronto e dire se regge.
3. Deciso di proposito **fuori** da questa fase, e da rimettere quando il cloud diventa titolare
   (ticket 10): lo Step 5 (`/smh-sito`), la guardia export→coda e quella di copertura. Il loro
   rimedio è pubblicare, e pubblicare è ancora affare di `main`, non del ramo di prova.

---

## Corsa #1 (07/09/2026, 21:12) — verde, e completamente a vuoto

Run [#34162080929](https://github.com/michidrop80-Rebelde/sanmarinohappens/actions/runs/34162080929):
tutti e sei i job verdi in 4m43s, Telegram arrivato. **E il cloud non aveva prodotto niente.**

I tempi: tappa 1 l'agente **155s**, tappe 2-3-4 l'agente **1s l'una**, peso **$0,87**. Causa quasi
certa: **serbatoio dell'abbonamento esaurito** (intuizione di Michele; i numeri la reggono, ed è il
rischio già misurato dal ticket 06, che aveva già ucciso tre catene programmate).

**Il guasto vero non è il serbatoio: è che nessuno se n'era accorto.** Tre bugie, tutte corrette:

1. **Il passo dell'agente risultava «riuscito» con `claude` morto.** Il passo finisce con un `tail`,
   e in shell il passo prende il codice dell'**ultimo** comando. Quindi marcatore scritto, tappa
   «fatta», e **la ripresa delle 09:00 — che esiste apposta per il 429 — non l'avrebbe mai rifatta.**
   Il codice vero di `claude` lo salvavo già in `exit_claude` e non lo usavo. Ora `chiudi-tappa.sh`
   lo guarda.
2. **Il confronto diceva «✅ 22/22 identici».** Il ramo nasce come copia di `main`, che contiene già
   i file del giro del Mac: confrontava quei file **con sé stessi**. Ora `materializza_cloud`
   confronta l'impronta git di ogni file col suo omologo su `main` e marca come «non scritto dal
   cloud» quelli identici; le sezioni che ne dipendono dicono **«⛔ non confrontabile»** e
   `--una-riga` esce **4**.
3. **Il referto Telegram diceva «1 Ricerca: 22 eventi — fatta».** Stessa radice. Ora dice
   **«🛑 nessun lavoro prodotto»** e, se tutte le tappe sono a vuoto, apre con «giro passato a vuoto»
   e la causa probabile.

**La regola che ne esce, e che vale oltre questo ticket:** un giro in cloud non si giudica da
«verde», né da quello che l'agente racconta di aver fatto. Si giudica da **cosa ha cambiato nei
file** — e il metro va costruito in modo che non possa scambiare il lavoro di qualcun altro per il
proprio. Qui il metro stava dentro un ramo che partiva già pieno del lavoro del Mac.

Prove aggiunte: `referto_giro_cloud_test.py` sale a **32/32** (due casi nuovi, su repo git veri:
giro tutto a vuoto e una sola tappa a vuoto), `confronta_giri_test.py` a **24/24** (caso [8]).
Il referto corretto è stato fatto girare **sulla corsa vera** e ora dice la verità.

## Corsa #2 — armata per la notte dell'8 settembre

Cron una-tantum `0 1 8 9 *` (03:00) + `0 7 8 9 *` (la ripresa, 09:00). 🔴 **Da togliere dopo.**
Martedì il giro del Mac non gira: questa corsa prova la **macchina**, non l'accordo fra i due giri.
L'accordo si misura lunedì 14/09.

---

## Corsa #2 (08/09/2026) — la macchina funziona. Ha mentito il metro, non il giro.

Run [#34191957597](https://github.com/michidrop80-Rebelde/sanmarinohappens/actions/runs/34191957597).
Questa volta il cloud **ha lavorato davvero**: 4 tappe, 4 commit sul ramo `giro-cloud`, 25 minuti,
$4,90. I file ci sono e sono suoi — `eventi-2026-09-08.md` (22 eventi), `eventi-verificati-2026-09-08.md`
(21 verificati + 1 scartato), `post-2026-09-08.md` (21 bozze), più `fonti.md` e
`handle-organizzatori.json` aggiornati. Le tre bugie corrette dopo la corsa #1 hanno tenuto: il
referto ha detto «fatta» quando era fatta, e non ha spacciato per suo il lavoro del Mac.

**Conferma di passaggio:** la causa della corsa #1 era davvero il **serbatoio esaurito**. Stessa
macchina, stesso codice, serbatoio pieno → $4,90 invece di $0,87 e 25 minuti invece di 4.

### Difetto trovato: il metro gonfiava i numeri
Il Telegram diceva «1 Ricerca: **24** eventi · 3 Verifica: ✅ **25** · 🗑 **0**». I numeri veri sono
**22 · ✅ 21 · 🗑 1**. Due difetti in `conta-giro.py`, tutti e due nel modo di riconoscere un evento:

1. contava per eventi anche le intestazioni di servizio in fondo al file della ricerca
   («⚠️ Fonti non raggiungibili», «🔧 Auto-miglioramento di oggi») — filtrava per nome, e quelle
   cominciano con un'emoji;
2. non riconosceva le intestazioni di sezione del file verificato quando l'agente le scrive
   «## ⚠️ **Sezione 2 —** Da confermare» invece di «## ⚠️ Da confermare». Risultato: le intestazioni
   stesse **e l'evento scartato** finivano contati fra i **verificati**.

Corretto: un evento non si riconosce più dal **nome** dell'intestazione (cambia ogni giorno, e le
sezioni pure) ma dalla **forma del blocco** — un evento ha sempre sotto il campo `- **Stato:**`, una
sezione no. Aggiunto anche il caso «fuori sezione»: un evento che il metro non sa dove mettere viene
**dichiarato**, non buttato via in silenzio. Nuovo `scripts/conta_giro_test.py` **13/13**, che prova
le due forme di intestazione (07/09 e 08/09) sullo stesso contenuto e pretende gli stessi numeri;
`confronta_giri_test.py` sale a **25/25** (i suoi «22 eventi» del 07/09 erano il difetto n.1: sono 20).

**Perché conta:** il «fatto quando» di questo ticket è un **confronto di numeri** lunedì 14/09. Con
il metro gonfio, quel confronto avrebbe potuto dire «i due giri concordano» su numeri sbagliati, o
accusare il cloud di una differenza che non c'era.

### Limite noto, lasciato aperto di proposito
Il conteggio «fuori sezione» si vede nel log della run e lanciando `conta-giro.py` a mano, **non**
nel Telegram: portarlo fin lì vuol dire aggiungere un campo a `chiudi-tappa.sh`, al workflow e a
`referto-giro-cloud.py`. Non è mai scattato; se scatta, il posto dove guardarlo è il log della run.

### Difetto trovato: la sveglia delle 03:00 è partita alle 07:47
Il cron `0 1 8 9 *` (03:00 locali) ha fatto partire la run **alle 07:47** — quasi 5 ore di ritardo.
Le 03:00 erano state scelte dal ticket 06 **apposta** per non contendere il serbatoio a Michele, e a
quell'ora il giro non ci arriva. → **ticket 14**.

### Fatto in questa sessione
- Tolte da `giro-cloud.yml` le due sveglie una-tantum (`0 1 8 9 *`, `0 7 8 9 *`) e il loro
  riferimento in `E_RIPRESA`. Restano solo lunedì 03:00 + ripresa 09:00.

### Cosa manca ancora per chiudere (invariato)
Lunedì **14/09**: il cloud e il Mac girano lo stesso giorno e si confrontano. È l'unica prova che
questo ticket aspetta.
