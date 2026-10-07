# Fonti: le sei competizioni sono davvero leggibili?

Type: research
Status: in corso (Jhonny · sessione jhonny-sport-invernale-02 · 07/10 07:28)
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
