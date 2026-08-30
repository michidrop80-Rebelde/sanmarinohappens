#!/usr/bin/env python3
"""
controllo-export-in-coda.py — la guardia sul passaggio di consegne fra grafica e pubblicazione.

COS'E' (spiegato semplice)
--------------------------
Fra l'anello 5 (`/smh-grafica`, che compila su Canva ed esporta i PNG) e l'anello 6
(`/smh-pubblica`, che pubblica) il testimone passa a mano: la grafica lascia il PNG in
`marketing/3 Export/`, e qualcuno deve poi creare la **busta** in `posts/` (il `.json`
con caption e data) perche' quel PNG esca davvero.

Se la busta non viene creata, NON succede niente di rumoroso: il PNG resta li', bello e
pronto, il giorno previsto passa a vuoto e nessuno se ne accorge. E' successo tre volte
in una settimana:
  • 28/07/2026 — 11 post giornalieri esportati e mai messi in coda;
  • 30/07/2026 — il settimanale 03-09/08, scoperto solo il 02/08 a slot gia' passato;
  • 14/07/2026 — il buco delle storie, stessa famiglia.

Questo script e' il confronto mancante: per ogni PNG esportato guarda se esiste la busta
corrispondente in `posts/` (ancora da pubblicare) o in `archivio/AAAA-MM/` (gia' uscita).
E' il terzo della famiglia delle guardie:
  • `controllo-copertura.py`  → non mancano i POST rispetto al calendario;
  • `controllo-integrita.py`  → non mancano i PEZZI del sistema (file citati dalle skill);
  • questo                    → non mancano le BUSTE per le grafiche gia' pronte.

COSA CONTA COME "IN CODA"
-------------------------
Non basta che esista una busta con lo stesso nome: la busta deve **portarsi dietro
quel PNG**. Una busta a immagine singola (post giornaliero, weekend a una pagina) non
ha il campo `immagini` e pubblica il file omonimo; una busta a piu' immagini (storie,
settimanale, carosello) elenca i PNG uno per uno. Se il PNG non compare fra quelli,
non uscira' mai — tipicamente e' un export vecchio rimasto li' dopo un rifacimento,
ma puo' anche essere una storia in piu' dimenticata fuori dalla busta.

FINESTRA
--------
Vengono segnalati solo i PNG con data **futura o recente**: un export di due mesi fa
senza busta e' archeologia, non un buco che sta per aprirsi. Di default si guarda
indietro 7 giorni (uno slot mancato la settimana scorsa vale ancora la pena saperlo).

USO
---
    python3 scripts/controllo-export-in-coda.py         # finestra: da 7 giorni fa in poi
    python3 scripts/controllo-export-in-coda.py 30      # da 30 giorni fa in poi

Esce con codice 1 se trova almeno un orfano dentro la finestra, cosi' puo' essere
agganciato a un giro automatico e far scattare un avviso.
"""

import datetime
import json
import pathlib
import re
import subprocess
import sys

# Cartella del progetto = due livelli sopra questo file (scripts/ -> progetto).
# Come nelle altre guardie: punta al clone dove gira davvero lo script, mai a un
# percorso hardcoded (il 26/07 un clone hardcoded era fermo indietro di un commit).
REPO = pathlib.Path(__file__).resolve().parent.parent
EXPORT = REPO / "marketing" / "3 Export"
# Dove si parcheggiano gli export superati da un rifacimento (vedi `png_esportati`).
CESTINO = "_vecchi"
GIORNI =["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

GIORNI_INDIETRO_DEFAULT = 7

# `AAAAMMGG_Tipo.png` oppure `AAAAMMGG_Tipo_N.png` (N = pagina, per storie/caroselli).
NOME_PNG = re.compile(r"^(\d{8})_(.+?)(?:_(\d+))?\.png$")


def buste_su_disco():
    """Indice delle buste presenti sul Mac: base (`AAAAMMGG_Tipo`) -> info.

    Guarda sia `posts/` (ancora da pubblicare) sia `archivio/AAAA-MM/` (gia' uscite):
    una busta pubblicata stamattina e' stata spostata nell'archivio, e senza contarla
    il suo PNG risulterebbe orfano per sbaglio.
    """
    indice = {}
    percorsi = sorted((REPO / "posts").glob("*.json")) + sorted(
        (REPO / "archivio").glob("*/*.json")
    )
    for p in percorsi:
        base = p.stem
        try:
            busta = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            busta = {}
        # Busta a immagine singola: nessun campo `immagini`, pubblica il file omonimo.
        immagini = busta.get("immagini") or [f"{base}.png"]
        indice[base] = {
            "dove": p.relative_to(REPO),
            "immagini": set(immagini),
            "data_pubblicazione": busta.get("data_pubblicazione"),
        }
    return indice


def basi_sul_remoto():
    """Nomi delle buste presenti su `origin/main`, per non gridare al lupo se il clone
    locale e' indietro (le pubblicazioni le fa GitHub Actions, che sposta e committa).

    Se non c'e' rete, o non c'e' un remoto, si tira dritto in silenzio: questa e' una
    rete di sicurezza in piu', non il controllo principale.
    """
    try:
        subprocess.run(
            ["git", "fetch", "-q", "origin"], cwd=REPO, check=False, timeout=60,
            capture_output=True,
        )
        out = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "origin/main", "posts/", "archivio/"],
            cwd=REPO, capture_output=True, text=True, check=True, timeout=60,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return set()
    basi = set()
    for riga in out.splitlines():
        m = re.search(r"(?:^posts/|^archivio/[^/]+/)(\d{8}_.+)\.json$", riga)
        if m:
            basi.add(m.group(1))
    return basi


def png_esportati():
    """Tutti i PNG in `marketing/3 Export/`, sottocartelle comprese.

    Due eccezioni, entrambe di roba che non deve andare in coda per definizione:
    i file di prova (prefisso `PROVA_`, convenzione della skill grafica) e la
    cartella `_vecchi/`, dove finiscono gli export superati da un rifacimento
    (niente cancellazioni: si archivia e si toglie di mezzo, così la guardia
    smette di segnalarli senza che nessuno perda un file).
    """
    if not EXPORT.exists():
        return [], []
    riconosciuti, strani = [], []
    for f in sorted(EXPORT.rglob("*.png")):
        if f.name.startswith("PROVA_") or CESTINO in f.parts:
            continue
        m = NOME_PNG.match(f.name)
        if not m:
            strani.append(f.relative_to(REPO))
            continue
        aaaammgg, tipo, _pagina = m.groups()
        try:
            data = datetime.datetime.strptime(aaaammgg, "%Y%m%d").date()
        except ValueError:
            strani.append(f.relative_to(REPO))
            continue
        riconosciuti.append({
            "file": f,
            "nome": f.name,
            "cartella": f.parent.name,
            "base": f"{aaaammgg}_{tipo}",
            "data": data,
        })
    return riconosciuti, strani


def main():
    giorni_indietro = int(sys.argv[1]) if len(sys.argv) > 1 else GIORNI_INDIETRO_DEFAULT
    oggi = datetime.date.today()
    limite = oggi - datetime.timedelta(days=giorni_indietro)

    esportati, strani = png_esportati()
    if not EXPORT.exists():
        print(f"❌ Cartella di export assente: {EXPORT}")
        print("   È il punto di consegna della grafica: se manca, qualcosa è stato spostato.")
        return 1

    indice = buste_su_disco()
    remoti = basi_sul_remoto()

    orfani_in_finestra = []
    orfani_vecchi = 0
    for png in esportati:
        busta = indice.get(png["base"])
        if busta is not None:
            if png["nome"] in busta["immagini"]:
                continue  # tutto a posto: c'è la busta e porta questo PNG
            motivo = f"la busta {busta['dove']} non elenca questo PNG"
        elif png["base"] in remoti:
            continue  # busta già su GitHub, il clone locale è solo indietro
        else:
            motivo = "nessuna busta in posts/ né in archivio/"

        if png["data"] >= limite:
            orfani_in_finestra.append((png, motivo))
        else:
            orfani_vecchi += 1

    print("Controllo export → coda — le grafiche esportate hanno la loro busta?\n")
    print(f"Oggi                     : {oggi.strftime('%d/%m/%Y')}")
    print(f"Finestra                 : dal {limite.strftime('%d/%m/%Y')} in poi")
    print(f"PNG esportati esaminati  : {len(esportati)}")
    print(f"Buste trovate            : {len(indice)} sul disco"
          + (f" + {len(remoti)} su origin/main" if remoti else " (remoto non letto)"))

    if strani:
        print(f"\n⚠️  {len(strani)} file col nome fuori schema (attesi `AAAAMMGG_Tipo[_N].png`):")
        for s in strani:
            print(f"   • {s}")

    if orfani_vecchi:
        print(f"\nℹ️  {orfani_vecchi} export orfani più vecchi della finestra: ignorati "
              "(archeologia, non buchi che stanno per aprirsi).")

    if not orfani_in_finestra:
        print("\n✅ Nessun export orfano: ogni grafica recente ha la sua busta in coda.")
        return 0

    # Un carosello sono 6 PNG della stessa busta mancante: si stampa una riga sola,
    # altrimenti l'elenco diventa illeggibile proprio quando il buco è grosso.
    raggruppati = {}
    for png, motivo in orfani_in_finestra:
        raggruppati.setdefault((png["base"], motivo), []).append(png)

    print(f"\n❌ {len(raggruppati)} grafiche esportate ma NON in coda "
          f"({len(orfani_in_finestra)} PNG):\n")
    for (_base, motivo), pngs in sorted(
        raggruppati.items(), key=lambda x: (x[1][0]["data"], x[0][0])
    ):
        pngs.sort(key=lambda p: p["nome"])
        d = pngs[0]["data"]
        quando = "FUTURO" if d > oggi else ("OGGI" if d == oggi else "SLOT GIÀ PASSATO")
        pagine = f" ({len(pngs)} pagine)" if len(pngs) > 1 else ""
        print(f"   • {d.strftime('%d/%m/%Y')} {GIORNI[d.weekday()][:3]}  [{quando}]  "
              f"{pngs[0]['nome']}{pagine}")
        print(f"       cartella : {pngs[0]['cartella']}")
        print(f"       motivo   : {motivo}")

    print(
        "\nCosa fare: per ognuna serve la busta in `posts/` — il `.json` con `tipo`,\n"
        "`data_pubblicazione`, `ora_pubblicazione`, `caption` (e `immagini` se sono più\n"
        "di una) più il PNG copiato lì accanto. La caption di solito esiste già nel file\n"
        "dei post approvati: si recupera da lì, non si riscrive.\n"
        "Se la data è già passata vale la finestra di recupero (memoria\n"
        "`project_regole_recupero_pubblicazione`): giornalieri e storie scaduti si\n"
        "scartano, gli aggregati si recuperano entro 2 giorni.\n"
        "Se invece il PNG è un export vecchio rimasto lì dopo un rifacimento, si sposta\n"
        f"in `marketing/3 Export/{CESTINO}/` (non si cancella: si archivia): da lì la\n"
        "guardia non lo guarda più."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
