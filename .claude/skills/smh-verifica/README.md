# smh-verifica

Secondo agente del progetto **San Marino Happens** (`@sanmarinohappens`).
Prende l'ultimo file di eventi dell'agente di ricerca e verifica ogni evento uno
per uno: ricontrolla la fonte, scioglie i dubbi `⚠️`, completa i campi, e separa
gli eventi in **confermati / da confermare da Michele / scartati**.

## Come si usa
Slash command: **`/smh-verifica`** (in una sessione con base sul progetto San Marino Happens).
Oppure: "verifica gli eventi trovati".
Gira **dopo** `/smh-ricerca`.

## Cosa produce
`dati/eventi/verificati/eventi-verificati-AAAA-MM-GG.md` — tre sezioni:
- **✅ Verificati** → pronti per l'agente testi.
- **⚠️ Da confermare (Michele)** → dubbio reale, serve revisione umana.
- **🗑 Scartati** → con motivo (passato, fuori San Marino, doppione, fonte sparita…).

## Posto nella catena
ricerca → verifica **(qui)** → testi → grafica → pubblicazione (Telegram per l'OK di Michele).

## File
```
smh-verifica/
├── SKILL.md                          # istruzioni dell'agente
├── README.md                         # questo file
├── assets/
│   └── evento-verificato-template.md # formato eventi + le 3 sezioni di output
└── references/
    └── regole-verifica.md            # i controlli di verifica in dettaglio
```
Configurazione condivisa: `dati/config.json` (percorsi input/output, finestra giorni).

## Regola d'oro
⚠️ NON INVENTARE MAI. Niente si promuove a `verificato` senza conferma su fonte reale.
Dubbio non sciolto → `da-confermare-michele`, mai un dato falso.
