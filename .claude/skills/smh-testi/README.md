# smh-testi

Terzo agente del progetto **San Marino Happens** (`@sanmarinohappens`).
Prende gli eventi **verificati** e scrive per ognuno una bozza di post pronta per
Instagram e Facebook: caption, hashtag, testo per la grafica e nota.

## Come si usa
Slash command: **`/smh-testi`** (in una sessione con base sul progetto San Marino Happens).
Oppure: "scrivi i post degli eventi" / "prepara le bozze".
Gira **dopo** `/smh-verifica`.

## Cosa produce
`dati/post/post-AAAA-MM-GG.md` — una bozza per ogni evento verificato, ordinate per
data, pronte da approvare (✅/❌) e copiare-incollare.

## Su cosa lavora
SOLO la sezione **✅ Verificati** del file verificato. Salta "Da confermare" e "Scartati".

## Posto nella catena
ricerca → verifica → testi **(qui)** → grafica → pubblicazione (Telegram per l'OK di Michele).

## File
```
smh-testi/
├── SKILL.md                 # istruzioni dell'agente
├── README.md                # questo file
├── assets/
│   └── post-template.md     # formato della bozza di post
└── references/
    └── voce-e-stile.md      # voce del brand, regole emoji/hashtag
```
Configurazione condivisa: `dati/config.json` (tono, hashtag fissi, CTA, percorsi).

## Regola d'oro
⚠️ NON INVENTARE MAI. Solo i dati del file verificato. Niente prezzi, orari o ospiti
non scritti lì. Se un dato manca, il post va scritto senza.
