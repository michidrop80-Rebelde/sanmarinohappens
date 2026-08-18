# Voce e stile — testi @sanmarinohappens

Carica questo file allo Step 3, quando scrivi le caption. Vale per ogni post
Instagram/Facebook di San Marino Happens. La parte tecnica (tono, hashtag fissi,
CTA, lunghezza) vive in `dati/config.json` → `post`; qui c'è il **come si scrive**.

⚠️ Sopra tutto: **non inventare**. Ogni dato in caption viene dal file verificato.
Campo assente → si omette, non si riempie a fantasia (mai "ore 00:00", mai un luogo
plausibile). Vedi anche `assets/post-template.md`.

## La voce in una riga
Amico del posto che ti segnala la cosa bella da non perdere: **informativo, caldo,
orgoglio sammarinese senza retorica**. Mai urlato, mai pubblicità aggressiva.

## Tono
- **Diretto e concreto**: prima cosa succede, poi il dettaglio. Niente giri di parole.
- **Orgoglio locale misurato**: "sul Titano", "in Repubblica", "a casa nostra" sì;
  enfasi gonfiata ("evento imperdibile dell'anno!!!") no.
- **Parli a una persona**, non a una folla: "ti aspettiamo", "segna la data".
- **Italiano corretto e scorrevole**, leggibile da telefono. Frasi brevi.

## Struttura della caption — FORMATO CORTO (obbligatorio)

@sanmarinohappens è un **calendario**, non uno spazio promozionale. Il lettore vuole
sapere cosa c'è, non essere convinto ad andarci. Caption brevi, fatti concreti, stop.

1. **Gancio** (1 riga): emoji + frase secca. Chi/cosa + 1 aggettivo o fatto. Es. "⚽ La Champions League arriva al San Marino Stadium."
2. **Corpo** (max 1-2 righe): 1 solo dettaglio utile (prenotazione / n° edizione / contesto — MAI prezzi o gratuità). Se non c'è niente di utile da aggiungere, il gancio basta da solo.
3. **Riga pratica**: `🗓 data · 🕗 ora (se c'è, altrimenti ometti) · 📍 luogo`.
4. **CTA**: `config.post.cta_default`.
5. **Disclaimer**: `config.post.disclaimer`.

**Limite assoluto**: se la caption (righe 1+2) supera 3 righe, è troppo lunga — taglia.
La riga pratica, CTA e disclaimer non contano nel limite: sono struttura fissa.

## Emoji — con misura (2-4 a post)
- Servono a **dare ritmo e segnalare** (🗓 data, 📍 luogo, 🎶 musica, ⚽ sport, 🎭 teatro),
  non a decorare ogni parola.
- Mai due emoji di fila per enfasi. Mai emoji al posto di una parola necessaria.
- Coerenti col tipo evento: musica 🎶/🎤, sport ⚽/🎾/🏎, cultura 🎭/📖, sociale 🎉,
  istituzionale 🇸🇲, alba/Monte 🌅.

## Hashtag — pochi e mirati
- `post.hashtag_fissi` (già 6) + **2-4 specifici** dell'evento: tipo, luogo/castello,
  nome proprio (artista, manifestazione). Totale ~8-10, mai muri da 30.
- Specifici in CamelCase leggibile: `#SergioCaputo`, `#BorgoMaggiore`, `#MonteTitano`,
  `#TennisSanMarino`. Niente hashtag generici inutili (`#fun`, `#instagood`).
- Vanno in coda, mai dentro il corpo della caption.

## Cosa evitare
- Punti esclamativi a raffica, MAIUSCOLE urlate, clickbait ("non crederai…").
- Promesse o giudizi non nei dati ("il miglior concerto", "imperdibile") se la fonte
  non lo dice.
- Prezzi/orari/ospiti non presenti nel file verificato.
- Anglicismi inutili quando esiste la parola italiana.

## Differenze IG vs FB
La caption è **una sola**, valida per entrambi. Instagram vive di gancio + salvataggio,
Facebook regge una riga in più di contesto: se serve, la riga pratica e la fonte
bastano a coprire entrambi. Non scrivere due versioni diverse salvo richiesta esplicita.

## Mini-esempio (tono giusto)
> 🎶 Abbronzatissima! I successi estivi anni '60 tornano dal vivo
>
> La San Marino Concert Band riporta in piazza i grandi tormentoni dell'estate.
> Un grande classico dell'estate, sotto le stelle del Titano.
>
> 🗓 28/06/2026 · 🕗 21:15 · 📍 Campo Bruno Reffi
> Salva il post 📌 e seguici per non perdere gli eventi di San Marino
