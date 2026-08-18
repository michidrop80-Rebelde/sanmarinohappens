---
name: smh-check
description: Servizio di CONTROLLO pre-pubblicazione di San Marino Happens — il "cancello" di qualità che, PRIMA che i post vadano live su IG/FB, controlla ogni busta in coda e blocca/segnala i problemi di CONTENUTO. Sei controlli: prezzi/gratuità (regola equità), coerenza cross-fonte dello stesso evento (luogo/ora uguali tra immagine, caption, aggregato e file verificato → scova i dati stantii come quelli del 13/07), giorno della settimana coerente con la data, sport sempre «vs Avversario», niente dati inventati, e tag degli organizzatori presi solo dal registro verificato e pertinenti all'evento. È SOLA LETTURA: apre i PNG (vision), incrocia le fonti, e produce un referto ✅/⚠️/❌ (anche su Telegram). Usare quando Michele dice "controlla la coda", "fai il tagliando", "verifica prima di pubblicare", dopo la grafica/prima della pubblicazione, o come guardia ricorrente.
---

# Servizio di controllo pre-pubblicazione — San Marino Happens

Sei il **cancello di qualità** di `@sanmarinohappens`. Giri **PRIMA** che i post vadano
live e controlli ogni "busta" in coda: se un contenuto è sbagliato, lo **blocchi** (o lo
**segnali**) prima che finisca su Instagram/Facebook.

Nasci da un fatto vero (13/07/2026): sono usciti post con **prezzi** (contro la regola
equità) e con **dati vecchi sulle immagini** (un'immagine giornaliera diceva «Campo Bruno
Reffi 21:15» mentre l'evento era «San Marino Outlet, ore 21:00»). Nessun controllo
automatico li aveva fermati: li ha beccati Michele a occhio, **dopo** la pubblicazione.
Tu esisti perché non succeda più.

⚠️ **SEI SOLA LETTURA.** Non pubblichi, non modifichi, non sposti e non cancelli niente.
Leggi la coda + le fonti, produci un **referto**. Le correzioni le fa Michele (o la skill
di grafica), non tu.

⚠️ **NON INVENTARE.** Un dato è "giusto" solo se compare in una **fonte** (file verificato,
master, aggregati). Se un valore è sull'immagine ma non in nessuna fonte → è sospetto
(possibile invenzione), non "probabilmente ok".

## Come è fatto il cancello (due metà che lavorano insieme)

1. **Questa skill `/smh-check` (sul Mac di Michele) = controllo PRINCIPALE.** Solo qui si
   possono aprire i PNG (vision) e incrociare le FONTI di verità, che stanno sul Mac e
   **non** nel repo GitHub. È l'unico posto che può beccare i **dati stantii sull'immagine**.
   **Gira AUTOMATICAMENTE come Step 4-bis dentro `/smh-pubblica`, prima del commit+push**:
   così nessuna busta nuova entra in coda senza passare da qui, senza che Michele debba
   lanciarlo. Puoi comunque lanciarlo **a mano** su tutta la coda quando vuoi un «tagliando».
2. **La guardia in `publish.py` (su GitHub) = rete AUTOMATICA di sicurezza.** Gira a ogni
   pubblicazione e blocca da sola i casi ovvi che si vedono senza le fonti: **prezzi nella
   caption** (una busta così diventa "anomala" → NON si pubblica + avviso Telegram). Non
   sostituisce `/smh-check`: è la rete se un giorno ci si dimentica di lanciarlo.

## Regola di severità (decisa da Michele, 13/07)
- **❌ = errore CERTO → BLOCCA** (segnala che la busta NON deve uscire finché non è corretta).
- **⚠️ = dubbio → AVVISA** senza bloccare (Michele decide guardando).
- **✅ = tutto torna.**

Meglio un ⚠️ di troppo che un post sbagliato online; ma **non** bloccare (❌) su un dubbio,
solo su una divergenza reale e verificata. Niente falsi allarmi che fermano post buoni.

---

## Flusso

### Step 0 — Prepara il dossier (parte meccanica)
Esegui l'aiutante, che NON fa vision ma apparecchia i fatti automatici (elenco buste,
giorno-settimana calcolato in Python, prezzi in caption, righe delle fonti che citano
l'evento):

```
python3 .claude/skills/smh-check/assets/smh_check.py
```

Se la coda o il progetto stanno altrove: `--queue <dir>` / `--project <dir>`.
Leggi tutto il dossier: è la tua base di partenza per ogni busta.

### Step 1 — Per OGNI busta, apri le immagini (vision)
Questo è il cuore, e lo può fare solo Claude. Per ogni busta apri il/i PNG (in
`posts/`) con lo strumento di lettura immagini e **trascrivi cosa c'è STAMPATO**:
giorno della settimana · data · titolo · **luogo** · **ora** · e se compare qualsiasi
**prezzo/gratuità**. (Per le storie: leggi ogni PNG; per il carosello: ogni slide.)

Non fidarti del nome file o della caption per sapere cosa mostra l'immagine: **guarda
l'immagine**. Il bug del 13/07 stava proprio lì — caption giusta, immagine vecchia.

### Step 2 — I 6 controlli
Per ogni busta confronta ciò che hai letto sull'immagine con il dossier (fonti) e con la
caption della busta:

1. **Prezzi / gratuità (regola equità).** Nessun `€`, «gratis», «gratuito/a», «a
   pagamento», «ingresso libero», «prezzo», «biglietti»… né in **caption** (te lo dice
   già il dossier) né **stampato sull'immagine** (lo vedi tu) né nel **testo-sorgente**
   da cui nasce l'immagine (la bozza «testo per la grafica» / la descrizione della
   storia in `dati/post/`). ⚠️ I prezzi sull'immagine NON si trovano con una ricerca
   testo: si vedono solo aprendo il PNG. Trovato un prezzo ovunque → **❌ BLOCCA**.
   - *Nota:* alcune FONTI contengono la parola «gratuito» (è lecito lì: sono appunti
     interni). Il divieto vale sui **contenuti pubblicati** (immagine + caption), non
     sulle fonti.

2. **Coerenza cross-fonte (il controllo anti-dati-stantii).** Per lo **stesso evento**,
   **luogo** e **ora** devono coincidere fra: immagine ↔ caption ↔ aggregato ↔ file
   verificato/master. Il dossier ti mette sotto gli occhi le righe delle fonti. Se
   l'immagine dice un luogo/ora e la fonte (o la caption, o l'aggregato) ne dice un
   altro → **❌ BLOCCA** e indica la divergenza esatta (es. «immagine: Campo Bruno Reffi
   21:15 · fonte+caption: San Marino Outlet 21:00»).
   - Per gli **aggregati** (settimanale/weekend/carosello) il titolo è generico: controlla
     **riga per riga** ogni evento elencato sull'immagine contro le fonti (data·luogo).

3. **Giorno della settimana = data.** Il giorno STAMPATO sull'immagine deve combaciare
   col giorno reale della data (il dossier te l'ha già calcolato in Python). Es. immagine
   «Martedì 14 Luglio» e Python dice 14/07 = Martedì → ok. Diverso → **❌ BLOCCA**.

4. **Sport sempre «vs Avversario».** Se è un evento sportivo, l'immagine (e il titolo)
   devono mostrare **entrambe** le squadre, «Casa vs Avversario», mai solo quella di
   casa. Manca l'avversario → **❌ BLOCCA** (vedi memoria `feedback_sport_vs_avversario`).

5. **Niente dati inventati.** Ogni valore mostrato deve tracciare a una fonte. Se
   l'immagine mostra un'ora/luogo che **nessuna** fonte conferma → **⚠️ AVVISA** (potrebbe
   essere inventato: da verificare). Se la fonte dice «non specificato» ma l'immagine
   mostra un valore preciso → **❌ BLOCCA** (è inventato).

6. **Tag degli organizzatori (`user_tags`).** Se la busta ha il campo `user_tags`,
   per **ogni** username elencato:
   - deve esistere in `dati/handle-organizzatori.json` con `stato: "attivo"`. Un handle
     che non è nel registro → **❌ BLOCCA** (è stato inventato: non deve mai succedere).
   - deve essere **pertinente a quell'evento**: l'organizzatore, il luogo o l'artista di
     quella specifica immagine. Un handle registrato ma che non c'entra con l'evento →
     **❌ BLOCCA** (es. la Giunta di Serravalle su un evento di Faetano).
   - per le **storie**, ricorda che ogni immagine è un evento diverso: controlla i tag
     dell'immagine 2 contro l'evento dell'immagine 2, non contro il primo.
   - **l'account esiste ancora?** (regola di Michele, 25/07/2026) Un handle verificato
     mesi fa può essere stato chiuso o rinominato — è successo al CONS, il cui sito
     ufficiale linka tuttora un profilo morto. Quindi:
     - apri `https://instagram.com/<username>`. Se la pagina dice **chiaramente** che il
       profilo non esiste → **❌ BLOCCA** e porta la voce a `stato: "non-taggabile"` nel
       registro, scrivendo il motivo e la data.
     - ⚠️ Instagram mostra spesso un **muro di login**: quello **non è** una prova che
       l'account sia sparito. In quel caso non bloccare — il profilo si considera valido.
     - se `verificato_il` della voce è più vecchio di **90 giorni**, → **⚠️ AVVISA**
       («handle da riverificare»), senza bloccare.
     - la rete di sicurezza finale resta comunque `publish.py`: se Instagram rifiuta i
       tag, il post esce **senza tag** e il riepilogo Telegram lo dichiara.

   *La forma (numero di tag, coordinate, chiavi orfane, tag sugli aggregati) è già
   controllata in automatico da `publish.py` su GitHub: qui controlla ciò che il robot
   non può sapere, cioè il registro e la pertinenza.*

### Step 3 — Classifica e scrivi il referto
Per ogni busta assegna **✅ / ⚠️ / ❌** con una riga che spiega il perché (e, se ❌/⚠️, la
divergenza esatta e dove correggere). Poi un riepilogo in testa: quante ✅, quante ⚠️,
quante ❌; se c'è anche solo una ❌ il verdetto complessivo è **«NON pubblicare finché non
corretto»**.

Formato referto (esempio):
```
🔎 CONTROLLO CODA — 7 buste — 13/07 22:40
Verdetto: ❌ 1 da correggere · ⚠️ 1 da guardare · ✅ 5 ok

❌ 20260717 Le Vibrazioni — immagine «Campo Bruno Reffi · 21:15» ma fonte+caption+storia
   «San Marino Outlet · 21:00» (luogo E ora). Rifare l'immagine giornaliera.
⚠️ 20260716 Virtus — ora non presente in nessuna fonte, sull'immagine «21:00»: verificare.
✅ 20260714 La Fiorita — immagine/caption/fonti concordi (San Marino Stadium · 21:00 · Martedì).
✅ …
```

### Step 4 — Consegna
- Mostra il referto a Michele nella chat.
- Mandalo anche su **Telegram** (così lo vede sul telefono):
  ```
  python3 .claude/skills/smh-check/assets/smh_check.py --telegram "<il referto>"
  ```
- Se ci sono **❌**, dillo chiaro: quelle buste **non devono andare live**; indica cosa
  correggere e con quale skill (di solito `/smh-grafica` per rifare un'immagine, o una
  ripulitura caption per i prezzi). **Tu non correggi**: passi la palla.

## Regole d'oro
- **Sola lettura.** Mai pubblicare/modificare/spostare. Solo referto.
- **Non inventare**; «giusto» = confermato da una fonte.
- **Blocca (❌) solo il certo**, avvisa (⚠️) sul dubbio: niente falsi allarmi.
- **Guarda l'immagine**, non fidarti di nome file/caption: il bug tipico è lì.
- Il giorno della settimana si **calcola in Python** (te lo dà il dossier), mai a memoria.
- Puoi girare quante volte vuoi: essendo sola-lettura non rompe niente (è un «tagliando»).
