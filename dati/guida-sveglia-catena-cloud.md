# Guida — la sveglia della catena serale in cloud (cron-job.org)

Ticket 15 della mappa «La catena si stacca dal Mac». È la parte che deve fare **Michele a mano**
(un modulo su un sito), come per il giro del lunedì (`dati/guida-sveglia-giro-cloud.md`).

## Cosa deve succedere
Ogni sera alle **18:05** cron-job.org chiama GitHub e parte la catena serale in cloud. Perché
18:05 e non 18:30: deve partire **prima** del Mac, altrimenti trova le approvazioni già
elaborate e il confronto non dice niente.

## Cosa fare — 1 cronjob, ~3 minuti
Su **cron-job.org** → **Create cronjob**; il modo più sicuro è **duplicare** quello del giro
in cloud e cambiare solo questi campi:

| campo | valore |
|---|---|
| Title | `SMH — catena serale in cloud (18:05)` |
| URL | `https://api.github.com/repos/michidrop80-Rebelde/sanmarinohappens/actions/workflows/catena-cloud.yml/dispatches` |
| Schedule | **ogni giorno**, ore **18:05**, fuso **Europe/Rome** |
| Request body | `{"ref":"main"}` |

Intestazioni e metodo (`POST`) restano quelle del cronjob che hai duplicato.

## Cosa resta com'è
Il workflow ha anche una sveglia interna di GitHub come rete di sicurezza (parte in ritardo,
ma parte). Se la sveglia di cron-job.org non chiama, il referto lo dice? No: il referto non
sa chi ha suonato. Si vede nella pagina Actions (evento `schedule` invece di `workflow_dispatch`).

## Prima di accenderla
Il file `.github/workflows/catena-cloud.yml` deve essere su **`main` di GitHub** (`git push`),
altrimenti il cronjob risponde 404.
