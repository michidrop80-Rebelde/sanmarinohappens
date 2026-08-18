# smh-ricerca

Primo agente del progetto **San Marino Happens** (`@sanmarinohappens`).
Cerca gli eventi futuri a San Marino su tutte le fonti, li auto-verifica, aggiorna
da solo la mappa delle fonti e produce un file datato pronto per l'agente di verifica.

## Come si usa
Slash command: **`/smh-ricerca`** (in una sessione con base sul progetto San Marino Happens).
Oppure: "cerca eventi nuovi a San Marino".

## Cosa produce
`dati/eventi/eventi-AAAA-MM-GG.md` — elenco eventi con stato `da-verificare`,
eventi dubbi marcati `⚠️`, più sezioni su fonti non raggiungibili e auto-miglioramento.

## Posto nella catena
ricerca **(qui)** → verifica → testi → grafica → pubblicazione (Telegram per l'OK di Michele).

## File
```
smh-ricerca/
├── SKILL.md                          # istruzioni dell'agente
├── README.md                         # questo file
├── assets/
│   └── evento-template.md            # formato di ogni evento
└── references/
    ├── auto-verifica.md              # controlli di sanità
    └── auto-miglioramento.md         # regole aggiornamento fonti
```
Configurazione condivisa: `dati/config.json` (brand, percorsi, categorie, finestra giorni).

## Regola d'oro
⚠️ NON INVENTARE MAI dati, date, luoghi o fonti. Dato mancante → `non specificato`.
