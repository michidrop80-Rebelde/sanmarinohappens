## ✅ Aggiornamento 26/08/2026 (fuori giro, sera) — la pagina non mostra più eventi già finiti fra una rigenerazione e l'altra + finale scudetto baseball

Michele: «ho aperto l'html degli eventi e c'è ancora un evento del 3 agosto attivo, cosa
sbagliamo?».

**Diagnosi.** Non era un dato sbagliato. Il "3 agosto" era **Cinema nei Castelli** (03–26/08),
una serie lunga un mese: card giusta, ma archiviata sotto "03 · Agosto" → a colpo d'occhio
sembra un evento vecchio ancora lì. Il vero difetto: **la pagina scartava gli eventi passati
solo al momento della generazione**, con la data di *quel* giorno. La pagina è un file statico,
la rigenerazione la fa solo il giro settimanale (`/smh-giro`, lunedì) — quindi da martedì a
domenica ogni evento che finisce si "deposita" a video. Il caso concreto: la **gara 7 della
semifinale di baseball (24/08)** era ancora in pagina il 26/08.

**Correzioni (in `scripts/genera-calendario.py`):**
1. **Filtro data anche nel browser.** `disegna()` ora nasconde gli eventi con `isoFine` <
   oggi, e "oggi" è quello vero del browser, non quello congelato nell'HTML. La pagina si
   ripulisce da sola ogni giorno, anche senza rigenerazione.
2. **Titoli con `⚠️` fuori dal pubblico.** Il master usa `⚠️` davanti al titolo per dire
   "data/luogo non confermati" (es. «⚠️ Campionato Sammarinese di Calcio — 1ª giornata»,
   orari non ancora usciti da FSGC). Ora quelle righe non finiscono sul calendario, come già
   succede per `~~barrato~~`, `scartato` e `da-confermare`.

Rigenerata: **47 eventi**, dal 03/08 (Cinema, ultima proiezione stasera) al 31/12/2026.
Anteprima privata ripubblicata sullo stesso link.

⚠️ **Resta aperto**: il generatore non gira dentro la catena *giornaliera* (`smh-catena`),
solo nel giro settimanale. Il filtro-browser tampona, ma le date/luoghi nuovi entrano in
pagina solo il lunedì. Da valutare se agganciare `genera-calendario.py` allo Step 4 di
`smh-catena` quando il master cambia.

### Finale scudetto baseball aggiunta al master (righe 56e/56f/56g)
San Marino ha vinto gara 7 con Bologna ed è in **finale scudetto vs Parma** (Italian Baseball
Series). Sul calendario entrano solo le gare **in casa a Serravalle**: gara 3 lun 31/08, gara 4
mar 01/09 (in pagina), gara 5 mer 02/09 `da-confermare` (eventuale → fuori dalla pagina finché
non serve). Gare 1-2 e le eventuali 6-7 a Parma → escluse (trasferte).

---

## ✅ Aggiornamento 24/08/2026 (fuori giro, pomeriggio) — Torraccia confermata + luogo/date Beer Fest corretti

Michele ha mandato in chat due locandine ufficiali che risolvono i due dubbi lasciati aperti dal
giro di stamattina. Rigenerata di nuovo (`scripts/genera-calendario.py`): **47 eventi**, dal
03/08 al 31/12/2026 (il Beer Fest aggiunge date fino a fine anno). Anteprima ripubblicata sullo
stesso link. Dettagli completi in cima a `dati/calendario/master.md`.

## ✅ Aggiornamento 24/08/2026 — giro settimanale, 3 eventi nuovi + 2 corretti

Rigenerata dentro il giro del 24/08 (`scripts/genera-calendario.py`): **34 eventi**, dal 03/08
al 11/10/2026. Anteprima privata ripubblicata sullo stesso link (guardie di tema aggiunte alla
copia usa-e-getta: `:root:not([data-theme="light"])` e `:root[data-theme="dark"]`, la pagina
canonica resta invariata). Master.md aggiornato dalla verifica di oggi con 3 righe nuove
(80 Serravalle in Wellness, 81 36° Palio Don Bosco, 82 San Marino Special Cup 2026) e 2 corrette
(59 "Dal Turista al Contadino" I tappa — dubbio risolto, 60 II tappa — luogo con due sedi). La
riga baseball 56d (gara 7) è stata chiusa fuori giro nella stessa sessione: San Marino ha vinto
gara 6 5-0, gara 7 confermata per stasera.

## ✅ Aggiornamento 17/08/2026 — giro settimanale, 2 correzioni + 1 evento nuovo

Rigenerata dentro il giro del 17/08 (`scripts/genera-calendario.py`): **32 eventi**, dal 26/07
al 11/10/2026. Anteprima privata ripubblicata sullo stesso link. Master.md aggiornato prima
della rigenerazione con le correzioni confermate dalla verifica di oggi (righe 66, 46b, +71
nuova) — vedi dettagli in cima a `dati/calendario/master.md`. Le stesse correzioni valgono
anche per le buste già in coda su IG/FB (Trenino, Noche Argentina), segnalate a parte a Michele
via Telegram: qui si è corretto solo il registro/l'anteprima, non le buste di pubblicazione.

# Stato — Sito / Calendario pubblico (San Marino Happens)

Sotto-progetto: la **presenza web pubblica** di @sanmarinohappens (futuro link-in-bio / sito vero).
Per ora è **una pagina calendario eventi**. ⚠️ **OFFLINE finché non pronto** — solo anteprima privata, non collegata a bio/Linktree.

**Come richiamarlo in una chat nuova:** scrivi **`/smh-sito`** (oppure "lavoriamo al sito / al calendario web").
Leggi anche la memoria `project_strategia_link_e_sito` (strategia dei link + decisione offline).

---

## ✅ Aggiornamento 08/08/2026 — la pagina non mostra più eventi che non si fanno

Rigenerata dentro il giro dell'08/08: **39 eventi**, dal 26/07 al 01/10/2026. Anteprima privata
ripubblicata sullo stesso link. Il 🔴 di sotto (master fermo al 06/07) **è rientrato**: il master
è stato riallineato al verificato dell'08/08 (+5 righe, e la riga Mi Gusto corretta).

Trovati leggendo la pagina generata — non erano difetti del master, erano del generatore:

1. 🔴 **Mostrava eventi cancellati.** In pagina c'era «⚠️ Baseball — Gara 5 playoff (quarti),
   San Marino vs Crocetta» del 10/08, che **non si gioca** (serie chiusa 3-0 il 05/08), e
   «L'Anima del Monte Titano» annullato. Il master li marca **barrando il titolo** (`~~così~~`)
   e con stato post `scartato`, ma `leggi_eventi()` filtrava **solo** `stato == "concluso"`:
   tutto il resto passava. Un calendario pubblico che annuncia una partita che non esiste è
   peggio di un calendario incompleto. Ora si scartano: titolo barrato · stato post `scartato` ·
   stato evento `da-confermare` (quest'ultimo tiene fuori roba come Mi Gusto, le cui date erano
   del 2025).
2. **Il Markdown finiva a video.** Si leggeva letteralmente `**Orti dell'Arciprete**, Centro
   Storico` e `~~L'Anima del Monte Titano~~`: il master è un `.md` e usa l'enfasi per parlare a
   chi lo legge, l'HTML la stampava tale e quale. Aggiunta `_pulisci()`, che la toglie (non la
   traduce in tag: serviva al registro, non al pubblico).

⚠️ **Nota sull'anteprima Artifact:** va pubblicata **senza** i tag `<!doctype>`/`<html>`/`<head>`/
`<body>`, perché l'involucro lo mette l'Artifact — la versione precedente li conteneva e finivano
annidati. `sito/calendario-eventi.html` resta invece il file **completo e autonomo** (doppio click
nel browser): per l'anteprima si estrae `<style>` + contenuto del `<body>` in una copia usa-e-getta.

## ⚠️ Aggiornamento 27/07/2026 — la pagina ora SI GENERA DA SOLA (chiuso il punto 2)

`sito/calendario-eventi.html` era andato **perso** nel `rm -rf` del 25/07 e non era recuperabile
dai transcript (c'erano solo modifiche parziali, mai una copia intera). Invece di reincollare a
mano i 44 eventi — cioè di ricreare esattamente il problema di prima — è stato costruito
**`scripts/genera-calendario.py`**, che legge `dati/calendario/master.md` e riscrive la pagina:

```bash
python3 scripts/genera-calendario.py
```

Questo chiude il **punto 2 della roadmap** («rigenerazione automatica») e il requisito che Michele
aveva confermato il 12/07 («deve auto-compilarsi dalla catena»). Nessun evento è più scritto a mano
nell'HTML: se il master cambia, basta rilanciare lo script. Il **giorno della settimana** non è
scritto da nessuna parte, lo calcola il browser dalla data — così non può essere sbagliato.
Il **disclaimer** richiesto il 12/07 è dentro la pagina, in fondo, nella versione presentabile.
La pagina ha `noindex` e resta **offline/privata**: lo script scrive solo un file locale.

🔴 **PROBLEMA APERTO, da risolvere prima di mettere la pagina online:** il master è fermo al
**06/07/2026** e arriva solo al 23/08, quindi la pagina rigenerata mostra **24 eventi** invece dei
**29 di solo agosto** che stanno in `dati/eventi/verificati/eventi-verificati-2026-07-27.md`.
Non è un difetto del generatore: è il master che non viene più aggiornato dalla verifica
(lo Step del master è dominio di `/smh-verifica`). Finché non si riallinea il master, la pagina
resta incompleta. È il prossimo passo del sotto-progetto.

## Cos'è (aggiornato al 09/07/2026)
- **Pagina:** `sito/calendario-eventi.html` — HTML autonomo (si apre col doppio click nel browser), tema chiaro/scuro, responsive.
- **Anteprima privata (claude.ai):** https://claude.ai/code/artifact/a834cd43-d4be-45ae-946f-3e767f7c051d — **privata**, la vedi solo tu. NON è il link-in-bio definitivo.
- **Contenuto:** 44 eventi estate 2026 da `dati/calendario/master.md`. Filtri per categoria (musica/sport/teatro/cultura/sociale/altro) + vista per mese (In corso · Luglio · Agosto). Giorno della settimana calcolato a runtime (mai scritto a mano).
- **Dati mostrati:** solo eventi futuri/confermati. Esclusi: conclusi (rispetto a oggi), Anime Prave (scaduta 07/07), Torneo della Libertà 31c (⚠️ irrisolto).

## Link agli eventi (strategia in `project_strategia_link_e_sito`)
Regola: link SOLO a organizzatore/biglietti/prenotazione, **mai** aggregatori (visitsanmarino). Aggiunti finora (10 eventi):
- Summer Vibes ×6 → sanmarinooutletsummervibes.com (Prenota)
- SMIAF → smiaf.org
- San Marino Comics → sanmarinocomics.com
- Internazionali Tennis (San Marino Open) → sanmarinotennisopen.com
- Cinema nei Castelli → sanmarinocinema.sm

## Regole di questa pagina
- **Aggiornare a OGNI giro:** quando c'è un nuovo giro calendario (nuovi/cancellati/modifiche nel master) la pagina va ricontrollata e aggiornata. Si fa da `/smh-sito`.
- **Orario preciso** → sempre inserito quando la fonte lo dà (memoria `feedback_orari_ricerca_specifica`).
- **Link** → solo diretti (organizzatore/biglietti), MAI aggregatori (memoria `project_strategia_link_e_sito`).
- **Controlli** → muoviti da solo incrociando le fonti; se serve un check umano, manda a Michele il link esatto (memoria `feedback_controlli_e_autonomia`).

## Prossimi step (in ordine)
1. **Arricchire i link** degli altri eventi (calcio UEFA, baseball, rally, eventi Consorzio, ecc.) — gradualmente, solo link diretti verificati.
2. **Rigenerazione automatica** della pagina dal master (ora i 44 eventi sono "incollati" a mano nell'HTML → invecchia). Idea: uno script che legge `master.md` e riscrive la parte dati.
3. **Contatore/redirect sui click** → metriche di vendita per la Fase 2.
4. **Host pubblico vero** (l'URL claude.ai non è adatto come bio permanente).
5. Decidere **se/quando** collegarlo al Linktree/bio (ora NO: offline).

## Aggiornamento 12/07/2026 (Michele) — priorità confermate + nuovo requisito
- Questo calendario HTML **È il link-in-bio ufficiale** di @sanmarinohappens (obiettivo dichiarato, non più "se/quando"). Resta offline finché non pronto, ma la meta è quella.
- Deve **auto-compilarsi dalla catena**: quando `smh-verifica` conferma o scarta un evento (→ `master.md`), la pagina si rigenera da sola (chiude lo step 2 "rigenerazione automatica") → sempre allineata senza incollare a mano.
- **Disclaimer grande in fondo** (nuovo requisito): non-responsabilità sulle info + invito a verificare all'origine. Michele lo vuole netto/schietto; la versione PUBBLICATA va resa presentabile (in Fase 2 si vendono spazi agli organizzatori: un disclaimer volgare mina la credibilità) mantenendo lo spirito. Bozza pubblicabile: *"Le informazioni sono raccolte da fonti pubbliche e possono cambiare o contenere errori. Verifica sempre data, orario e luogo sul canale ufficiale dell'organizzatore. San Marino Happens non è responsabile di eventuali inesattezze o variazioni."*

## Note di verifica
- **Tennis San Marino Open** — CONFERMATO (09/07) dal testo del sito ufficiale: *"da domenica 26 luglio (giorno di inizio delle qualificazioni) a domenica 2 agosto"*. Quindi 26/07 = qualificazioni, tabellone principale dal 27/07. Il calendario mostra **27/07–02/08** (il torneo vero) con nota "qualificazioni dal 26/7". Nessun errore nei dati: la lezione era solo di metodo (ragionare/incrociare prima di segnalare) → memoria `feedback_controlli_e_autonomia`.
- **Armonie! (Camerata del Titano)** — ⚠️ DA VERIFICARE. Il master ha #23 "Pianoforte" il 15/07 a Borgo Maggiore, ma le fonti dicono che il concerto di piano era il 27/06 (già passato) e che "Armonie!" è una rassegna con molti concerti estivi (le fonti si contraddicono su titoli/sedi del 15 e 18/07). Sul calendario: Armonie Barocca 18/07 → aggiunto 18:00 (Sant'Antimo, coerente); Armonie "Pianoforte" 15/07 → lasciato invariato in attesa di conferma. Link da controllare: https://www.cameratatitano.com/news/ (+ libertas.sm). Il master (dominio smh-verifica) andrebbe corretto.
- **Orari aggiunti (09/07):** Concert Band Campo Bruno Reffi = 21:15 (Casabianca/Greg/Jannacci/Finardi/Quel gran genio); Classica Giovani = 21:00 (Trio/Recital/Duo); La Favola di Francesco = 21:15; Liscio for Dummies = 21:00 (sede vera: Piazzetta A. Preda Ferri, Montegiardino); Maestri = 21:00 (sede vera: Anfiteatro Capicchioni, Chiesanuova); Armonie Barocca = 18:00; La Fiorita = 19:00.
- **Ancora senza orario** (non trovato / da confermare): Virtus vs Dila Gori (16/07), Chiringuito Faetano, Symbol Remember, L'Anima del Monte Titano, e i festival multi-giorno (San Marino Antiqua, SMIAF, San Marino Revival, San Marino Comics). Nel master le sedi "San Marino TeatrOUT" sono generiche → da correggere (Montegiardino, Chiesanuova).

## Come lavorarci
- Il file **canonico** è `sito/calendario-eventi.html`: modifica lì.
- Per far vedere le modifiche a Michele: **ripubblica l'Artifact** da quel file (resta privato). Ripubblicando dalla stessa path si aggiorna; il link sopra potrebbe cambiare se si riparte da zero.
- I dati veri stanno in `dati/calendario/master.md` (registro unico eventi).
