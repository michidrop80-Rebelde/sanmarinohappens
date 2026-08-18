# Auto-miglioramento — mantieni viva la mappa delle fonti

Carica questo file quando, durante la ricerca, vuoi aggiornare i file fonti
(`dati/fonti.md` e `dati/fonti-sport.md`).

Principio: l'agente migliora la mappa da solo, ma **non promuove nulla senza Michele**.
Le scoperte vanno in una sezione "da confermare"; le conferme le fa lui.

## Cosa fare in ciascun caso

### Nuova fonte scoperta
Se trovi una squadra, una federazione, un locale, un teatro o un calendario rilevante
che NON è ancora nei file fonti:
- aggiungilo in fondo al file giusto, nella sezione
  `## 🆕 Fonti trovate dall'agente (da confermare)`;
- scrivi una riga con **nome, URL e un breve perché**;
- NON spostarlo nelle sezioni principali: lo conferma Michele.

### Fonte che blocca i bot (403 o simili)
- marcala con `⚠️` nel file fonti accanto alla voce;
- le prossime esecuzioni la salteranno.

### Fonte morta (404, dominio sparito)
- marcala con `❌` nel file fonti.

### Voce incompleta completata
- se trovi il dato mancante (es. la pagina Facebook di un castello segnata `[ ]`),
  aggiornala direttamente nel file.

## Tracciamento
Tutto ciò che aggiungi o modifichi va riassunto, a fine esecuzione, nella sezione
`## 🔧 Auto-miglioramento di oggi` del file eventi del giorno, così Michele vede
in un colpo d'occhio come è cambiata la mappa.
