# 06 — Il consumo regge? E quindi che forma prende la catena?

Type: grilling
Status: risolto (07/09/2026)
Blocked by: 05
Modello: Opus — e' una scelta di forma della catena, si sbaglia una volta sola
Sforzo: breve (mezza sessione) — i numeri arrivano gia' dal ticket 05

## Domanda

Con i numeri veri della sonda in mano: un giro agentico **quotidiano** più uno **settimanale**
stanno dentro l'abbonamento e dentro il target di ~€20-25/mese del progetto?

Se sì, la catena va in cloud com'è.

Se no, cambia forma, e la decisione è **quale forma**. Un'ipotesi da mettere alla prova: il giro
quotidiano non ha bisogno di un agente pieno — per gran parte è controllo (le 6 guardie sono script
Python, costano zero) e diventa agente solo quando una guardia trova un buco. Il settimanale invece
è agente per forza: cerca, verifica, scrive.

**Cosa deve produrre la risposta:** la forma scelta delle due sveglie (cosa fa un agente, cosa fa
uno script), con il numero che la giustifica.

## Lavori

- 07/09/2026 — **Misurato il consumo vero delle catene che già girano sul Mac**, non stimato: letti
  i 71 transcript delle sessioni (14/07 → 06/09) in `~/.claude/projects/…/*.jsonl`, sommate le
  `usage` per modello e convertite in valore equivalente con lo stesso metro della sonda.
  Script usato: [`../misura-consumo.py`](../misura-consumo.py) — tenuto, così la misura si può rifare.

## Risposta

**Il consumo regge, e non perché lo speriamo: perché quel consumo c'è già oggi.** Le corse
programmate sul Mac pescano dallo stesso abbonamento delle sessioni in chat. Spostarle su GitHub
Actions **non aggiunge un centesimo**: sposta dove gira lo stesso motore. Il target ~€20-25/mese
resta intatto (Actions è gratis su repo pubblico, Claude gira sull'abbonamento).

Il vincolo vero non sono i soldi: è **il serbatoio condiviso con Michele**.

### I numeri (misurati, 71 sessioni, 14/07 → 06/09/2026)

| chi | corse | peso (valore equivalente) |
|---|---|---|
| `smh-catena` — sere **senza** grafica | 13 | **$0,35 – $2,96** (mediana $0,80) |
| `smh-catena` — sere **con** grafica (Step 2-bis) | 14 | **$5,57 – $32,58** (mediana ~$15) |
| `smh-giro-settimanale` — giro completo del 24/08 | 1 | **$40,85** · 449 turni · 147 M token |
| **Michele davanti allo schermo** | 37 | **$1.068 = il 77% del totale** |

Il «$» non è denaro speso (l'abbonamento è a forfait): è il **metro del peso**, lo stesso della
sonda ($0,285 per 10 turni giocattolo).

**Tre fatti che questi numeri hanno tirato fuori:**

1. **La sera cara è sempre e solo quella con la grafica.** Contate le occorrenze «canva» in ogni
   corsa: le sere da $0,5–3 ne hanno 11–25 (solo il testo della skill), quelle da $11–33 ne hanno
   150–320 (lavoro vero su Canva). **La parte che va in cloud — approvazioni, guardie, referto —
   pesa $0,5–3. La parte cara resta sul Mac, come già deciso.**
2. **Il serbatoio si è già svuotato 9 volte in due mesi.** Sei volte ha fermato Michele mentre
   lavorava; **tre volte ha ucciso una catena programmata**: 04/08 `smh-grafica-pubblica` tagliata
   a metà · **21/08 `smh-catena` morta appena nata sul limite SETTIMANALE** (costo $0,50, lavoro
   zero) · **24/08 il giro settimanale tagliato a metà corsa** (partito 06:24, morto alle 11:06 sul
   limite delle 5 ore) — è proprio la corsa da $40,85. Il rischio del ticket 02 non è futuro: **è
   già successo tre volte e nessuno se n'era accorto.**
3. **Chi svuota il serbatoio non è la catena: è Michele** (77% contro 23%). Quindi la leva giusta
   non è «far consumare meno alla catena», è **non farla consumare quando consuma lui**.

### La forma scelta delle due sveglie (decisa da Michele il 07/09/2026)

1. **Quotidiana — prima gli script, l'agente solo se serve.** Il workflow lancia le 6 guardie
   (Python puro, costo zero) e legge la coda approvazioni. **Se tutte tacciono, finisce lì e non
   sveglia nessun agente.** Claude si accende solo quando una guardia grida o ci sono approvazioni
   da elaborare. Le 13 sere vuote passano da ~$1 a **zero**; l'agente resta intero quando serve.
2. **Settimanale — spezzato in 4 tappe con salvataggio dopo ognuna:** ricerca → postino → verifica
   → testi, ognuna un passo che fa `commit` prima di passare il testimone. Motivo misurato: il giro
   del 24/08 è morto a metà e in cloud si sarebbe perso **tutto il non committato** (ticket 02).
   Se il serbatoio finisce alla terza tappa, le prime due sono salve.
3. **Orario: di notte.** Giro settimanale **lunedì 03:00**, catena quotidiana **02:00**. Non fa
   risparmiare token — fa risparmiare **scontri**: stesso consumo, preso a un'ora in cui Michele
   non lo sta usando, con la finestra delle 5 ore già chiusa quando apre il Mac. ⚠️ Le 18:30 di
   oggi sono l'ora **peggiore**: il limite settimanale si azzera alle 18:00 (Europe/San_Marino) ed
   è il momento di massima contesa.
4. **Serbatoio vuoto = si dice.** Sul 429 il workflow **riprova una volta dopo 6 ore**; se fallisce
   ancora manda **un Telegram di una riga** («catena ferma, serbatoio esaurito, riprovo domani»).
   Costo zero, ed è l'unica cosa che trasforma un silenzio in un'informazione — il 21/08 nessuno
   si era accorto di niente.

⚠️ **Rovescio accettato:** in cloud nessuno può fermare a mano una corsa che sta andando male. Il
freno è la tappa n.2 (spezzare + salvare), non la sorveglianza.

**Queste quattro scelte sono il capitolato dei ticket 08 (giro del lunedì) e 10 (catena quotidiana
e spegnimento):** annotate lì, non vanno riaperte.
