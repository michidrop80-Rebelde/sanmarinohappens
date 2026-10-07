# Mappa — Format sportivo invernale

Label: `wayfinder:map` · Effort: `sport-invernale` · Aperta: 2026-08-26

## Destination

Una **specifica approvata** del format sportivo settimanale invernale di @sanmarinohappens,
pronta da passare a un piano di implementazione. È raggiunta quando non resta nessuna
decisione aperta su: dove vivono i dati delle partite, come il passo sport si aggancia alla
catena esistente, che aspetto ha il format nuovo, e cosa succede quando i dati mancano o lo
sport si ferma.

**Non** è la destinazione: costruire il template su Canva, scrivere la skill, pubblicare il
primo post. Quella è implementazione, e comincia dopo.

## Notes

**In sospeso** (06/10/2026, scelta di Michele): per ora non si porta avanti. Niente giro
notturno: Jhonny la lavora solo se Michele lo chiede.

**Dominio**: San Marino Happens — catena ricerca → verifica → testi → approvazione → grafica →
pubblicazione. Vedi `CLAUDE.md` e `ULTIMO_REPORT.md` in radice.

**Vincoli tipografici scoperti il 31/08** (dettaglio in `issues/07-direzione-visiva.md`): il font
dei titoli non disegna ne' `·` ne' `ª`; la casella data regge ~11 caratteri a corpo 45. Valgono
per qualunque direzione venga scelta.

**Skill da consultare in ogni sessione**: `/grilling` e `/domain-modeling` sui ticket di
discussione; `/lavorare-leggeri` sempre (frugalità di token).

**Il problema che questa mappa risolve.** D'inverno gli eventi culturali crollano e lo sport
diventa l'unica cosa che c'è ogni weekend — ma arriva tutto insieme: il campionato sammarinese
è interamente interno, quindi ogni giornata sono 8 partite tutte sul territorio, più basket,
volley, Serie D, futsal. Un weekend invernale può fare 15+ eventi, più di tutto agosto. Il
sistema di oggi (una riga per evento nel master, una bozza per evento) non regge quel volume.

### Vincoli fissi — decisi da Michele in chat il 26/08/2026, NON si riaprono

1. **Contenitore dedicato.** Lo sport ricorrente ha un formato suo, settimanale. Non invade il
   feed quotidiano né gli aggregati.
2. **Blocco unico.** Il campionato sammarinese occupa UNA riga sul grafico («8ª giornata ·
   8 partite · sab-dom»); l'elenco completo delle partite va in caption. Basket, volley,
   San Marino Calcio e i big hanno una riga ciascuno.
3. **Slot: lunedì 18:00**, copre lunedì→domenica (turni infrasettimanali inclusi).
4. **Format visivamente NUOVO** e diverso dal resto, ma riconducibile al brand: master Canva
   dedicato, stesso logo e stessa famiglia di caratteri, palette e impaginazione proprie.
5. **Sovrapposizione**: settimanale, weekend e carosello NON elencano le partite ricorrenti —
   mettono una riga di rimando al post del lunedì. Le **storie di ogni giorno** le dicono
   sempre, domenica compresa. Deroga voluta alla regola d'oro «ogni aggregato contiene tutto»,
   limitata al solo sport ricorrente, da scrivere nel piano editoriale perché nessun agente la
   "corregga" fra sei mesi.
6. **Discipline**: campionato sammarinese di calcio (+ Nazionale FSGC + Coppa Titano) ·
   Pallacanestro Titano · volley Titan Services · San Marino Calcio (Serie D) · futsal FSGC ·
   motori FAMS.
7. **Dati**: calendario di stagione scaricato una volta + ricontrollo alla fonte della sola
   settimana in uscita (orari, rinvii, recuperi).
8. **Niente risultati.** Solo calendario. I risultati sono un'estensione possibile fra sei
   mesi, non ora.

### Regole ereditate dal progetto, date per acquisite

- Solo quello che **si gioca in Repubblica** (decisione del 27/07/2026): le trasferte delle
  squadre locali non entrano.
- **Settori giovanili e campionati di categoria fuori a prescindere** — decine di partite a
  weekend, nessuno spettatore.
- **NON INVENTARE MAI** un dato: orario, luogo o avversario mancante si scrive «non
  specificato», mai un valore plausibile.

## Decisions so far

<!-- una riga per ticket chiuso: il gist, poi si zooma sul ticket per il dettaglio -->

- [Fonti: le sei competizioni sono davvero leggibili?](issues/02-fonti-leggibilita.md) — campionato e futsal FSGC reggono (ora+campo, tutto in Repubblica); basket, volley e Serie D no (fonte non leggibile/non trovata); motori: niente nov-mar.

## Not yet specified

Nebbia in scope, non ancora abbastanza nitida per diventare un ticket:

- **Tag degli organizzatori sportivi.** Il post del lunedì cita club e federazioni: vanno
  taggati? Con quali handle? Il registro `dati/handle-organizzatori.json` oggi non ha i club
  sportivi, e la regola dei due indizi vale anche per loro. Si chiarisce dopo che si sa cosa
  c'è scritto nel post (ticket 06).
- **Lo sport sul calendario pubblico del sito.** `scripts/genera-calendario.py` legge il
  master: se le partite ci arrivano in forma compatta, la pagina cosa mostra — il blocco o le
  8 partite? Dipende dall'architettura dati (ticket 01).
- **Come si misura se funziona.** Quali metriche dicono che il format regge, e a che soglia
  ha senso aggiungere i risultati. Si vede dopo il debutto.
- **Coppa Titano e Nazionale**: hanno calendari propri, sporadici e non settimanali. Forse
  sono «big» con post dedicato invece che righe del post del lunedì. Dipende da 06 e 09.

## Out of scope

Fuori dalla destinazione di questa mappa. Non graduano: tornano solo se la destinazione viene
ridisegnata, e allora come effort nuovo.

- **Risultati, punteggi e classifiche** — scelta esplicita di Michele (26/08): si parte solo
  con il calendario.
- **Discipline oltre le sei scelte** — rugby, tennistavolo, tennis, ciclismo, arti marziali,
  podismo/outdoor. Si aggiungono dopo, una alla volta, a format rodato.
- **Costruzione materiale del template Canva** e **scrittura della skill `/smh-sport`** — è
  implementazione: comincia quando la spec è approvata.
