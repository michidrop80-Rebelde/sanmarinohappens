# 14 — Le sveglie di GitHub slittano di ore: come si fa partire il giro all'ora giusta?

Type: grilling
Status: DECISO e COSTRUITO 08/09/2026 — resta la prova sul campo di lunedì 14/09
Blocked by: —
Modello: Opus (decisione), poi lavoro meccanico
Sforzo: corto — la strada esiste già nel progetto, va decisa e applicata

## Domanda

Il ticket 06 ha scelto **lunedì 03:00** per una ragione precisa: non contendere il serbatoio
dell'abbonamento a Michele, che di giorno lavora col Mac. Ma i `schedule:` di GitHub Actions non sono
sveglie: sono richieste messe in coda. L'8 settembre 2026 il cron delle **03:00** ha fatto partire la
run alle **07:47** — 4 ore e 47 minuti dopo. Alle 07:47 Michele è sveglio: è esattamente l'ora che
volevamo evitare.

Il progetto **ha già risolto questo problema una volta**: la pubblicazione delle 7:00 e 18:00 non si
fida dei cron di GitHub, la fa partire **cron-job.org** (gratuito) con una chiamata `workflow_dispatch`,
e i cron interni restano come rete di sicurezza. Decisione dell'11/07/2026.

Da decidere:
1. Si applica la stessa ricetta al giro in cloud (un terzo cronjob su cron-job.org, stesso PAT
   fine-grained solo-Actions-write), o l'orario preciso qui non vale il pezzo in più?
2. Se sì: la **ripresa** delle 09:00 va anche lei su cron-job.org, o basta che sia un cron interno
   (tanto è un ripiego, e slittare le fa solo bene)?
3. Il PAT di cron-job.org **non è nella guardia delle scadenze** (`dati/scadenze-token.json`) — è già
   scritto nella fog della mappa. Se si tocca cron-job.org, si chiude anche quello nello stesso giro?

## Perché non è già deciso

Perché il ritardo si è visto solo l'08/09, dopo la corsa #2. Fino a lì «lunedì 03:00» sembrava una
sveglia, e il ticket 06 l'ha decisa credendola tale.

## Fatto quando

Il giro in cloud parte entro pochi minuti dall'ora decisa, provato su una corsa vera, e la mappa dice
perché quell'ora è quella giusta.


---

## Risposta (08/09/2026)

**Sì alla ricetta cron-job.org, e su tutte e due le sveglie.** Scelta di Michele fra tre
alternative.

### Perché non era «solo un'ora scomoda»

Il ticket parlava di «alle 07:47 Michele è sveglio». Il danno vero è un altro, ed è più grosso:
l'abbonamento Claude lavora a **finestre di 5 ore**. Partendo alle 03:00 la finestra si chiude alle
**08:00**, prima che Michele apra il Mac. Partita alle 07:47, si chiude alle **12:47** e gli mangia
la mattinata — cioè esattamente lo scontro per cui il ticket 06 aveva scelto le 03:00. Non è un
fastidio, è la ragione stessa dell'orario notturno che viene annullata.

### Le tre domande del ticket

**1. Si applica la ricetta?** Sì. I numeri del progetto la reggono: le chiamate di cron-job.org
partono alle **07:01 e 18:01**, i cron interni di GitHub lo stesso giorno alle **08:03, 12:26,
21:56**. Nessun pezzo nuovo da inventare, nessun segreto nuovo: stesso PAT fine-grained
solo-Actions-write già in uso per la pubblicazione. I cron interni **restano accesi** come rete di
sicurezza — se cron-job.org muore il giro parte lo stesso, tardi ma parte, e una corsa doppia non fa
danno (le tappe già fatte si saltano e il secondo avviso Telegram non parte, marcatore `avvisato.ok`).

**2. Anche la ripresa delle 09:00?** Sì, ed è quella che rischia **di più**, non di meno. Se la
ripresa slitta a mezzogiorno apre una finestra 13:00–18:00: il cuore della giornata di Michele. Ed è
proprio la corsa che parte quando il serbatoio era già vuoto. Costo di farla puntuale: zero — stesso
PAT, stesso modulo, un cronjob in più.

**3. Il PAT nella guardia delle scadenze?** Sì, nello stesso giro — ma la data **non si inventa**:
è al passo 3 della guida, Michele la legge su GitHub e la riporta. Adesso quel PAT non regge più
solo i trigger 7:00/18:00 della pubblicazione: regge **anche** la sveglia del giro in cloud. Se
scade in silenzio cadono tutte e due insieme.

### Cosa è stato costruito

- **`giro-cloud.yml`** — `workflow_dispatch` ora accetta l'etichetta **`ripresa` (si/no)**, e i due
  `schedule:` sono ridichiarati per quello che sono: **rete di sicurezza, non sveglie**. Il commento
  in cima racconta perché, coi numeri.
- **Il difetto che la modifica ha scoperto:** il workflow riconosceva «questa è la ripresa»
  leggendo il *testo del cron* (`github.event.schedule == '0 7 * * 1'`). Una chiamata di
  cron-job.org non ha nessun cron → una ripresa caduta avrebbe scritto a Michele *«riprovo alle
  09:00»*, alle 09:00. Ora `E_RIPRESA` riconosce **tutte e due le strade**.
- **Guardia nuova, perché il guasto non sia muto:** se la corsa parte da `schedule` invece che da
  `workflow_dispatch`, vuol dire che cron-job.org **non ha chiamato**. Senza avviso il giro
  continuerebbe a girare per sempre all'ora sbagliata senza che nessuno se ne accorga. Il referto
  Telegram ora lo dice e dice cosa controllare (`CHI_SVEGLIA` = `github.event_name`).
- **[`dati/guida-sveglia-giro-cloud.md`](../../../dati/guida-sveglia-giro-cloud.md)** — i 3 passi
  per Michele: i due cronjob (URL, body, header) e la lettura della data di scadenza del PAT.

### Trovato per strada (non era del ticket, corretto lo stesso)

`chiudi_tappa_test.sh` falliva una prova su 14: il metro `conta-giro.py` è stato corretto l'08/09
per riconoscere un evento dal campo `- **Stato:**`, e la scenetta finta del test non ce l'aveva.
Prova stantia, non guasto — sistemata la scenetta.

### Provato

YAML riletto e ricontrollato nella sua struttura (i due `schedule`, l'input `ripresa` con i suoi
valori, i 6 job) · referto **37/37** con 3 prove nuove (sveglia saltata / sveglia arrivata / ripresa
caduta che non promette bugie) · chiudi-tappa **14/14** · conta_giro 13/13 · confronta_giri 25/25 ·
lucchetto 20/20 · publish 71+11+26 · token-agente 12/12 · integrità 133/133.

### Cosa manca per chiudere davvero

I due cronjob su cron-job.org li crea **Michele** (5 minuti, guida sopra): non esiste un modo di
farli da qui. La prova vera è **lunedì 14/09**: la corsa deve risultare partita alle 03:0x e la
pagina della run deve dire `workflow_dispatch`, non `schedule`. Stessa data in cui chiude il
ticket 08.
