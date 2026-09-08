# Guida — mettere la sveglia puntuale al giro in cloud (cron-job.org)

Deciso nel **ticket 14** della mappa «La catena si stacca dal Mac», l'08/09/2026.
Questa è la parte che deve fare **Michele a mano**: sono due moduli da riempire su un
sito, non c'è modo di farli da qui.

## Perché

Le sveglie scritte dentro GitHub (`schedule:`) **non sono sveglie**: sono richieste
messe in coda, e partono quando GitHub ha voglia. L'8 settembre 2026 quella delle
**03:00** ha fatto partire il giro alle **07:47**.

Il guaio non è l'ora in sé: è che l'abbonamento Claude lavora a **finestre di 5 ore**.
Partendo alle 03:00 la finestra si chiude alle 08:00, prima che tu apra il Mac.
Partita alle 07:47, si chiude alle **12:47** — e ti mangia la mattinata.

Il progetto ha già la ricetta buona: **cron-job.org** (gratuito) chiama GitHub all'ora
esatta. Lo fa già per la pubblicazione delle 7:00 e 18:00, e si vede: le sue corse
partono alle 07:01 e 18:01, quelle dei cron interni di GitHub alle 08:03, 12:26, 21:56.

## Cosa resta com'è

Le due sveglie interne di GitHub **restano accese** come rete di sicurezza: se
cron-job.org un giorno muore, il giro parte lo stesso — tardi, ma parte. Una corsa in
più non fa danno: il giro riconosce il lavoro già fatto, non lo rifà e non ti manda un
secondo messaggio.

---

## Cosa devi fare — 3 passi, ~5 minuti

### Passo 1 — il cronjob della sveglia (lunedì 03:00)

Vai su **cron-job.org** → accedi → **Create cronjob**. Riempi così:

| campo | valore |
|---|---|
| Title | `SMH — giro in cloud (sveglia lunedì 03:00)` |
| URL | `https://api.github.com/repos/michidrop80-Rebelde/sanmarinohappens/actions/workflows/giro-cloud.yml/dispatches` |
| Schedule | ogni **lunedì**, ore **03:00** — fuso orario **Europe/Rome** |

Poi apri la linguetta **Advanced**:

| campo | valore |
|---|---|
| Request method | `POST` |
| Request body | `{"ref":"main","inputs":{"ripresa":"no"}}` |

E aggiungi tre **Headers** (gli stessi che hai già sui due cronjob della pubblicazione —
copia l'`Authorization` da lì, è lo stesso PAT):

```
Authorization: Bearer IL_TUO_PAT_FINE_GRAINED
Accept: application/vnd.github+json
Content-Type: application/json
```

Salva. Se GitHub risponde **204** è andata: la risposta vuota è quella giusta.

### Passo 2 — il cronjob della ripresa (lunedì 09:00)

Stessa identica cosa, **due sole differenze**:

| campo | valore |
|---|---|
| Title | `SMH — giro in cloud (RIPRESA lunedì 09:00)` |
| Schedule | ogni **lunedì**, ore **09:00** — fuso **Europe/Rome** |
| Request body | `{"ref":"main","inputs":{"ripresa":"si"}}` |

⚠️ Quel `"ripresa":"si"` conta davvero: è come il giro capisce di essere il secondo
tentativo. Senza, se cadesse anche la ripresa ti scriverebbe *«riprovo alle 09:00»* —
alle 09:00, cioè una bugia.

La ripresa parte ogni lunedì anche quando alle 03:00 è andato tutto bene: in quel caso
trova il lavoro già fatto, non tocca niente e **non ti manda nessun messaggio**.

### Passo 3 — un'occhiata al PAT (20 secondi, quasi certamente niente da fare)

Vai su **github.com → Settings → Developer settings → Personal access tokens →
Fine-grained tokens**, trova `cron-job-org-publish` e guarda la riga *Expiration*.

Quando è stato creato (11/07/2026) era stato messo **senza scadenza**, apposta: quel token
sa fare una cosa sola su un repo solo, quindi il danno se trapelasse è minimo, e un token
che non scade non può fermare la pubblicazione di soppiatto. **Se dice ancora
«No expiration», non c'è niente da aggiungere alla guardia delle scadenze** — e va bene
così. Se invece una data c'è, dimmela e la metto in `dati/scadenze-token.json`.

**Quello che davvero può spegnere cron-job.org non è la scadenza, è un'altra cosa:** il
sito ha un interruttore che **disattiva un cronjob dopo troppi fallimenti di fila**, ed è
acceso di default. Per questo su ogni cronjob conviene lasciare accesa anche la notifica
di fallimento (*Notify after 1 failure*). E per questo il giro, da oggi, ti avvisa da solo
se parte dalla rete di sicurezza invece che dalla sveglia (vedi qui sotto).

---

## Come si controlla che abbia funzionato

Lunedì mattina, su **github.com → Actions → «Giro settimanale in cloud»**: la corsa deve
risultare partita alle **03:0x**, non alle 07 e passa. Nella pagina della run, sotto
*«This workflow was triggered by»*, deve dire **workflow_dispatch** (cron-job.org) e non
*schedule* (la rete di sicurezza).
