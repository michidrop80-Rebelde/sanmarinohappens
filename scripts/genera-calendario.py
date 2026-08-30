#!/usr/bin/env python3
"""
genera-calendario.py — riscrive `sito/calendario-eventi.html` leggendo il registro master.

COS'E' (spiegato semplice)
--------------------------
La pagina calendario e' il futuro link-in-bio di @sanmarinohappens. Fino al 25/07/2026 i suoi
eventi erano **incollati a mano** dentro l'HTML: ogni giro bisognava riscriverli, e la pagina
invecchiava da sola. Era il punto 2 della roadmap in `sito/STATO-SITO.md` («rigenerazione
automatica») e il requisito che Michele ha confermato il 12/07 («deve auto-compilarsi dalla
catena»).

Questo script chiude quel punto: legge `dati/calendario/master.md` — il registro unico degli
eventi, che la catena aggiorna da sola — e riscrive la pagina. Nessun dato scritto a mano,
quindi la pagina non puo' piu' andare fuori sincrono col resto del sistema.

Il giorno della settimana NON viene mai scritto nel file: lo calcola il browser a partire dalla
data, cosi' non puo' essere sbagliato (regola del progetto).

USO
---
  python3 scripts/genera-calendario.py

La pagina resta OFFLINE/privata: questo script scrive solo un file locale, non pubblica nulla.
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

PROGETTO = Path(__file__).resolve().parent.parent
MASTER = PROGETTO / "dati" / "calendario" / "master.md"
USCITA = PROGETTO / "sito" / "calendario-eventi.html"

OGGI = date.today()
ANNO = OGGI.year

# Link DIRETTI verificati (organizzatore / biglietti / prenotazione).
# ⚠️ REGOLA: mai aggregatori tipo visitsanmarino — vedi memoria project_strategia_link_e_sito.
LINK = {
    "smiaf": ("https://smiaf.org", "Sito ufficiale"),
    "san marino comics": ("https://sanmarinocomics.com", "Sito ufficiale"),
    "internazionali tennis": ("https://sanmarinotennisopen.com", "Sito ufficiale"),
    "cinema nei castelli": ("https://sanmarinocinema.sm", "Programma"),
    "summer vibes": ("https://sanmarinooutletsummervibes.com", "Prenota"),
}

ICONA = {
    "musica": "🎵", "sport": "🏅", "teatro": "🎭", "cultura": "🎨",
    "sociale": "🤝", "istituzionale": "🏛", "altro": "📌",
}

DISCLAIMER = (
    "Le informazioni sono raccolte da fonti pubbliche e possono cambiare o contenere errori. "
    "Verifica sempre data, orario e luogo sul canale ufficiale dell'organizzatore. "
    "San Marino Happens non è responsabile di eventuali inesattezze o variazioni."
)


# Intervallo col mese scritto UNA volta sola: "03–26/08", "28–30/08".
# Il lookbehind impedisce di agganciare il "07" di "27/07–02/08" (lì i mesi ci sono già
# entrambi): senza, l'intervallo verrebbe letto come 07/08–02/08.
RANGE_MESE_UNICO = re.compile(r"(?<![/.\d])(\d{1,2})\s*[–—-]\s*(\d{1,2})\s*[/.](\d{1,2})")
DATA_COMPLETA = re.compile(r"(\d{1,2})[/.](\d{1,2})")


def _data(giorno: int, mese: int):
    try:
        return date(ANNO, mese, giorno)
    except ValueError:
        return None


def _estremi(campo: str):
    """(inizio, fine) dal campo Data del master.

    Gestisce tre forme: '23/08' · '27/07–02/08' (due date complete) ·
    '03–26/08' (mese scritto una volta sola, in fondo).
    ⚠️ La terza forma prima del 30/07/2026 veniva letta AL CONTRARIO — restituiva
    l'ULTIMO giorno come data d'inizio, così Cinema nei Castelli (03–26/08),
    Mi Gusto (13–17/08) e San Marino Comics (28–30/08) comparivano sul calendario
    pubblico con la data sbagliata.
    """
    m = RANGE_MESE_UNICO.search(campo)
    if m:
        g_inizio, g_fine, mese = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return _data(g_inizio, mese), _data(g_fine, mese)

    tutte = DATA_COMPLETA.findall(campo)
    if not tutte:
        return None, None
    return (_data(int(tutte[0][0]), int(tutte[0][1])),
            _data(int(tutte[-1][0]), int(tutte[-1][1])))


def prima_data(campo: str):
    """Dal campo Data del master ('27/07–02/08', '23/08', '03–26/08') ricava la data d'inizio."""
    return _estremi(campo)[0]


def ultima_data(campo: str):
    """Data di FINE per gli eventi con intervallo; altrimenti la data d'inizio.
    Serve per non far sparire dal calendario un festival ancora in corso."""
    return _estremi(campo)[1]


def link_per(titolo: str):
    t = titolo.lower()
    for chiave, (url, etichetta) in LINK.items():
        if chiave in t:
            return {"url": url, "etichetta": etichetta}
    return None


def _pulisci(testo: str) -> str:
    """Toglie la punteggiatura Markdown dal testo che finisce a video.
    Il master e' un file .md, quindi usa **grassetto** e ~~barrato~~ per parlare a chi lo
    legge; l'HTML invece li stampava letterali, e in pagina si vedeva
    «**Orti dell'Arciprete**, Centro Storico». Qui dentro non si traduce il Markdown in
    tag: si toglie e basta, perche' l'enfasi serviva al registro, non al pubblico."""
    testo = re.sub(r"~~(.+?)~~", r"\1", testo)
    testo = re.sub(r"\*\*(.+?)\*\*", r"\1", testo)
    return testo.strip()


def leggi_eventi():
    if not MASTER.exists():
        sys.exit(f"❌ Manca il registro master: {MASTER}")
    eventi = []
    dentro_registro = False
    for riga in MASTER.read_text().splitlines():
        if riga.startswith("## 🗓"):
            dentro_registro = True
            continue
        if dentro_registro and riga.startswith("## "):
            break  # finito il registro futuro/in corso
        if not dentro_registro or not riga.startswith("|"):
            continue
        celle = [c.strip() for c in riga.strip().strip("|").split("|")]
        if len(celle) < 6 or celle[0] in ("#", "---") or not celle[0][0].isdigit():
            continue
        _id, data_txt, titolo, tipo, luogo, stato = celle[:6]
        stato_post = celle[6] if len(celle) > 6 else ""
        note = celle[9] if len(celle) > 9 else ""
        inizio, fine = prima_data(data_txt), ultima_data(data_txt)
        if inizio is None:
            continue
        # Si mostrano solo gli eventi non ancora finiti. `concluso` nel master e' autorevole.
        if stato == "concluso" or (fine and fine < OGGI):
            continue
        # ...e solo quelli che si TERRANNO davvero. Tre modi in cui il master dice
        # «questo non si fa», che prima passavano tutti: la pagina ha mostrato per giorni
        # la gara 5 dei quarti di baseball (riga 56), che non si e' mai giocata perche' la
        # serie era chiusa 3-0, col titolo barrato stampato letterale a video.
        #   - titolo barrato ~~cosi~~ = convenzione del master per annullato/non disputato;
        #   - stato post `scartato`;
        #   - stato evento `da-confermare` = non ha una fonte valida (es. Mi Gusto San
        #     Marino, le cui date erano del 2025) e non si mette davanti al pubblico.
        #   - titolo con `⚠️` davanti = il master segnala che data/luogo non sono confermati
        #     (es. «⚠️ Campionato Sammarinese di Calcio — 1ª giornata», orari non usciti):
        #     finche' non e' pulito non va sul calendario pubblico.
        if titolo.startswith("~~") or "scartato" in _pulisci(stato_post).lower():
            continue
        if "da-confermare" in _pulisci(stato).lower():
            continue
        if titolo.lstrip().startswith("⚠"):
            continue
        titolo, luogo = _pulisci(titolo), _pulisci(luogo)
        # L'orario, quando c'e', vive nelle Note del master.
        ora = None
        m_ora = re.search(r"ore (\d{1,2}[:.]\d{2})", note)
        if m_ora:
            ora = m_ora.group(1).replace(".", ":")
        eventi.append({
            "id": _id,
            "data": data_txt,
            "iso": inizio.isoformat(),
            "isoFine": (fine or inizio).isoformat(),
            "titolo": titolo,
            "tipo": (tipo or "altro").lower(),
            "luogo": luogo,
            "ora": ora,
            "link": link_per(titolo),
        })
    eventi.sort(key=lambda e: (e["iso"], e["titolo"]))
    return eventi


def costruisci_html(eventi):
    dati = json.dumps(eventi, ensure_ascii=False, indent=1)
    tipi = sorted({e["tipo"] for e in eventi})
    bottoni = "\n".join(
        f'      <button class="filtro" data-tipo="{html.escape(t)}">'
        f'{ICONA.get(t, "📌")} {html.escape(t.capitalize())}</button>'
        for t in tipi
    )
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Calendario eventi — San Marino Happens</title>
<style>
  :root {{
    --sfondo:#faf9f7; --carta:#fff; --testo:#1d1d1b; --tenue:#6b6b6b;
    --bordo:#e6e3de; --accento:#8c52ff; --accento2:#ff914d;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --sfondo:#141317; --carta:#1e1d23; --testo:#f2f1ef; --tenue:#a5a3ad;
             --bordo:#302e38; --accento:#a97dff; --accento2:#ffa46b; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--sfondo); color:var(--testo);
         font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; line-height:1.5; }}
  .involucro {{ max-width:820px; margin:0 auto; padding:24px 16px 64px; }}
  header {{ text-align:center; padding:24px 0 8px; }}
  h1 {{ font-size:clamp(1.6rem,5vw,2.3rem); margin:0 0 6px;
        background:linear-gradient(90deg,var(--accento),var(--accento2));
        -webkit-background-clip:text; background-clip:text; color:transparent; }}
  .sottotitolo {{ color:var(--tenue); margin:0 0 4px; }}
  .barra {{ display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin:20px 0 8px; }}
  .filtro {{ border:1px solid var(--bordo); background:var(--carta); color:var(--testo);
             border-radius:999px; padding:7px 14px; font-size:.9rem; cursor:pointer; }}
  .filtro[aria-pressed="true"] {{ background:var(--accento); border-color:var(--accento); color:#fff; }}
  .conteggio {{ text-align:center; color:var(--tenue); font-size:.88rem; margin:10px 0 18px; }}
  .mese {{ font-size:1.05rem; text-transform:uppercase; letter-spacing:.08em;
           color:var(--tenue); margin:28px 0 10px; }}
  .evento {{ background:var(--carta); border:1px solid var(--bordo); border-radius:14px;
             padding:14px 16px; margin-bottom:10px; display:flex; gap:14px; align-items:flex-start; }}
  .quando {{ min-width:82px; text-align:center; }}
  .giorno {{ font-size:1.5rem; font-weight:700; line-height:1; }}
  .settimana {{ font-size:.76rem; text-transform:uppercase; color:var(--tenue); }}
  .titolo {{ font-weight:600; margin:0 0 3px; }}
  .meta {{ color:var(--tenue); font-size:.9rem; }}
  .oggi {{ border-color:var(--accento); box-shadow:0 0 0 2px color-mix(in srgb,var(--accento) 22%,transparent); }}
  .etichetta {{ display:inline-block; font-size:.72rem; text-transform:uppercase; letter-spacing:.05em;
                color:var(--tenue); border:1px solid var(--bordo); border-radius:6px;
                padding:1px 6px; margin-left:6px; }}
  a.biglietti {{ display:inline-block; margin-top:6px; font-size:.85rem; color:var(--accento);
                 text-decoration:none; font-weight:600; }}
  a.biglietti:hover {{ text-decoration:underline; }}
  .vuoto {{ text-align:center; color:var(--tenue); padding:40px 0; }}
  footer {{ margin-top:48px; padding-top:20px; border-top:1px solid var(--bordo);
            color:var(--tenue); font-size:.85rem; }}
  .avviso {{ background:var(--carta); border:1px solid var(--bordo); border-left:4px solid var(--accento2);
             border-radius:10px; padding:14px 16px; margin-top:16px; }}
</style>
</head>
<body>
<div class="involucro">
  <header>
    <h1>Eventi a San Marino</h1>
    <p class="sottotitolo">Il calendario di @sanmarinohappens</p>
  </header>

  <div class="barra" id="filtri">
    <button class="filtro" data-tipo="tutti" aria-pressed="true">✨ Tutti</button>
{bottoni}
  </div>
  <p class="conteggio" id="conteggio"></p>

  <main id="elenco"></main>

  <footer>
    <div class="avviso"><strong>Attenzione.</strong> {html.escape(DISCLAIMER)}</div>
    <p style="text-align:center;margin-top:18px">
      Seguici su Instagram e Facebook: <strong>@sanmarinohappens</strong>
    </p>
  </footer>
</div>

<script>
// I dati arrivano da dati/calendario/master.md tramite scripts/genera-calendario.py.
// NON modificare a mano questo blocco: viene riscritto a ogni rigenerazione.
const EVENTI = {dati};

const GIORNI = ['Domenica','Lunedì','Martedì','Mercoledì','Giovedì','Venerdì','Sabato'];
const MESI = ['Gennaio','Febbraio','Marzo','Aprile','Maggio','Giugno',
              'Luglio','Agosto','Settembre','Ottobre','Novembre','Dicembre'];
const ICONE = {json.dumps(ICONA, ensure_ascii=False)};

const oggiISO = new Date().toISOString().slice(0,10);
let filtro = 'tutti';

// Il giorno della settimana si calcola qui, dalla data: non e' mai scritto nei dati,
// cosi' non puo' essere sbagliato.
function pezziData(iso) {{
  const [a,m,g] = iso.split('-').map(Number);
  const d = new Date(a, m-1, g);
  return {{ giorno: g, settimana: GIORNI[d.getDay()], mese: MESI[m-1], meseIdx: m }};
}}

function disegna() {{
  const elenco = document.getElementById('elenco');
  // Nascondi gli eventi gia' finiti: il confronto e' fatto QUI nel browser, con la data di
  // oggi vera, non con quella "congelata" al momento della rigenerazione. Cosi' la pagina
  // resta pulita anche se non viene rigenerata per giorni (prima la gara 7 di baseball del
  // 24/08 restava a video il 26/08). `isoFine` e' YYYY-MM-DD, il confronto fra stringhe basta.
  const visibili = EVENTI.filter(e =>
    e.isoFine >= oggiISO && (filtro === 'tutti' || e.tipo === filtro));
  document.getElementById('conteggio').textContent =
    visibili.length + (visibili.length === 1 ? ' evento in programma' : ' eventi in programma');

  if (!visibili.length) {{
    elenco.innerHTML = '<p class="vuoto">Nessun evento di questo tipo in programma.</p>';
    return;
  }}

  let html = '', meseCorrente = '';
  for (const e of visibili) {{
    const d = pezziData(e.iso);
    const etichettaMese = d.mese;
    if (etichettaMese !== meseCorrente) {{
      meseCorrente = etichettaMese;
      html += '<h2 class="mese">' + etichettaMese + '</h2>';
    }}
    const inCorso = e.iso <= oggiISO && oggiISO <= e.isoFine;
    const piuGiorni = e.iso !== e.isoFine;
    html += '<article class="evento' + (inCorso ? ' oggi' : '') + '">' +
      '<div class="quando"><div class="giorno">' + d.giorno + '</div>' +
      '<div class="settimana">' + d.settimana.slice(0,3) + '</div></div>' +
      '<div><p class="titolo">' + (ICONE[e.tipo] || '📌') + ' ' + e.titolo +
      (inCorso ? '<span class="etichetta">in corso</span>' : '') + '</p>' +
      '<p class="meta">' + (piuGiorni ? e.data + ' · ' : '') +
      (e.ora ? 'ore ' + e.ora + ' · ' : '') + e.luogo + '</p>' +
      (e.link ? '<a class="biglietti" href="' + e.link.url +
        '" target="_blank" rel="noopener">' + e.link.etichetta + ' →</a>' : '') +
      '</div></article>';
  }}
  elenco.innerHTML = html;
}}

document.getElementById('filtri').addEventListener('click', ev => {{
  const b = ev.target.closest('.filtro');
  if (!b) return;
  filtro = b.dataset.tipo;
  document.querySelectorAll('.filtro').forEach(x =>
    x.setAttribute('aria-pressed', x === b ? 'true' : 'false'));
  disegna();
}});

disegna();
</script>
</body>
</html>
"""


def main():
    eventi = leggi_eventi()
    if not eventi:
        sys.exit("❌ Nessun evento futuro trovato nel master: non riscrivo la pagina.")
    USCITA.parent.mkdir(parents=True, exist_ok=True)
    USCITA.write_text(costruisci_html(eventi))
    per_tipo = {}
    for e in eventi:
        per_tipo[e["tipo"]] = per_tipo.get(e["tipo"], 0) + 1
    print(f"✅ Pagina rigenerata: {USCITA.relative_to(PROGETTO)}")
    print(f"   {len(eventi)} eventi (dal {eventi[0]['iso']} al {eventi[-1]['isoFine']})")
    print("   " + " · ".join(f"{t} {n}" for t, n in sorted(per_tipo.items())))
    con_link = sum(1 for e in eventi if e["link"])
    print(f"   {con_link} con link diretto all'organizzatore")
    print("   La pagina resta OFFLINE/privata: nessuna pubblicazione.")


if __name__ == "__main__":
    main()
