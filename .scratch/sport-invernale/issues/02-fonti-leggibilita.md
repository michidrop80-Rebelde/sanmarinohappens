# Fonti: le sei competizioni sono davvero leggibili?

Type: research
Status: resolved (07/10/2026)
Modello: Sonnet · medium (dato da Jhonny il 07/10 07:28, regola di lavorare-leggeri)
Blocked by: —

## Question

Il vincolo 7 (calendario di stagione + ricontrollo settimanale) regge solo se le fonti si
lasciano leggere davvero. `dati/fonti-sport.md` oggi dice cose che vanno verificate una per
una, e su almeno tre punti è esplicitamente incerto.

Per **ognuna** delle sei competizioni serve sapere: esiste un calendario di stagione
pubblicato in un posto solo? È leggibile da WebFetch (o è JavaScript, o blocca i bot)? Riporta
**orario** e **campo**? Si capisce **casa/trasferta**? E come si vede un **rinvio o un
recupero**?

Le sei:

1. **Campionato Sammarinese di calcio** (+ Coppa Titano, Nazionale) — `fsgc.sm`, segnata ✅.
   Nota già a registro: gli orari FSGC mancavano ad agosto (riga 58 del master).
2. **Pallacanestro Titano**, Serie C — `basketmarche.it` ✅, ma il sito ufficiale del club ha
   il **certificato SSL scaduto** (verificato 10/08) e non è leggibile.
3. **Titan Services**, volley — `federvolleysm.org` ✅ · `emiliaromagnasport.com`. Da
   verificare anche il dato a registro «femminile, Serie D italiana»: è ancora vero?
4. **San Marino Calcio**, Serie D girone F — `tuttocampo.it` ✅ · `acsanmarinocalcio.sm` 🆕.
5. **Futsal / calcio a 5 FSGC** — 🆕 **fonte mai mappata**: è la vera novità da trovare.
6. **Motori FAMS** — `fams.sm` ✅, ma la copertura invernale è tutta da verificare (i motori a
   San Marino sono un fatto primaverile-estivo: forse d'inverno non c'è nulla).

Lezione da non ripetere: sul **baseball** i bot non sono mai riusciti a stabilire casa/trasferta,
e per mesi il dato l'ha portato Michele a mano. Se una delle sei ha lo stesso problema, va
saputo **adesso**, non a dicembre.

L'esito va scritto come aggiornamento a `dati/fonti-sport.md`.

## Risposta (07/10/2026)

Tabella completa in `dati/fonti-sport.md`, sezione «Leggibilità delle fonti per il format sportivo invernale».

- **Reggono**: campionato sammarinese e **futsal FSGC** (trovato: stessa piattaforma `fsgc.sm`, pagina partita con data, ora, stadio, giornata, stato). Casa/trasferta non serve (tutto in Repubblica). Sono il grosso del volume.
- **Non reggono ancora**: **basket** (basketmarche.it non mostra il calendario del club dalla home; sito club con SSL scaduto), **volley** (`federvolleysm.org` ora porta a `fspav.sm`; nessun calendario del campionato trovato; «femminile Serie D» non confermato), **San Marino Calcio** (tuttocampo.it dà 403 ai bot). Per queste tre manca una fonte leggibile verificata: rischio «baseball bis», casa/trasferta potrebbe doverla portare Michele.
- **Motori FAMS**: nessun evento da novembre 2026 a marzo 2027 (solo Rallylegend 8-11/10 e Halloween Ronde 30-31/10). Non è contenuto settimanale: fuori dal post del lunedì, al più eventi singoli.
- **Non verificato** (detto onestamente): link a un elenco completo di stagione FSGC, come appare un rinvio, orari delle tre fonti non reggenti.
- Correzioni: campionato = 14 squadre (non 16).

Conseguenza per la spec: i ticket successivi possono contare su 2 fonti solide; per basket/volley/Serie D la spec deve prevedere un ripiego («non specificato» / dato di Michele) e un lavoro di ricerca in implementazione.
