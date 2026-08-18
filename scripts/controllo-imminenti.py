#!/usr/bin/env python3
"""
Guardia degli imminenti — San Marino Happens

A cosa serve
------------
Risponde ogni sera a una domanda sola e stretta: **nelle prossime 48 ore esce
tutto quello che deve uscire?** Cioè:

  • il post del feed e le storie di DOMANI (slot delle 7:00);
  • gli AGGREGATI in scadenza entro 48 ore (settimanale la domenica 18:00,
    weekend il giovedì 18:00, carosello mensile l'ultimo giorno del mese 18:00).

Per ogni buco che trova va a cercare nel registro master gli eventi veri di
quella data, e dice se il buco è **CHIUDIBILE** (c'è materiale già approvato:
si compila e si mette in coda subito) oppure **NON CHIUDIBILE** e perché.

Perché esiste — ed è diversa da controllo-copertura.py
------------------------------------------------------
`controllo-copertura.py` guarda 14 giorni e stampa una lista lunga in cui i
giorni scoperti sono quasi sempre legittimi (un giorno senza eventi veri resta
vuoto: non si inventano eventi). A furia di elencare cose non azionabili, quella
lista ha smesso di essere letta — e infatti il **settimanale del 16/08/2026** ci
finì dentro, indistinguibile dal rumore, e non uscì. Nemmeno il weekend di
Ferragosto del 13/08 uscì, per la stessa ragione.

La differenza è questa: un giorno senza eventi è vuoto per colpa del calendario,
un aggregato mancante è vuoto **per colpa nostra**. La domenica arriva comunque.
Quindi qui un aggregato che manca è sempre ❌ duro, mai un ⚠️ da leggere e
scrollare.

E soprattutto: questa guardia è fatta per essere **eseguita**, non letta. Chi la
lancia (la catena serale) deve chiudere i buchi chiudibili, non passarne
l'elenco a Michele.

Uso
---
    python3 scripts/controllo-imminenti.py

Codici di uscita
----------------
    0  niente da segnalare: o le 48 ore sono coperte, o i buchi che restano sono
       giorni **legittimamente vuoti** (nessun evento a registro per quelle date)
    1  ci sono buchi che aspettano un ✅ di Michele -> vanno mandati su Telegram
    2  c'è almeno un buco CHIUDIBILE subito -> la catena deve lavorare adesso

Lo 0 mette apposta nello stesso sacco «tutto coperto» e «non c'era niente da
fare»: sono la stessa cosa per chi legge. Un allarme che suona anche per un
martedì senza eventi suonerebbe quasi ogni sera, e in una settimana nessuno lo
leggerebbe più — vedi la memoria `feedback_una_guardia_muta_e_peggio_di_nessuna`.
"""

import collections
import datetime
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MASTER = REPO / "dati" / "calendario" / "master.md"
GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

# Le SERIE ricorrenti (Cinema nei Castelli, Alba sul Monte, Trenino, Giovedì in
# Centro) hanno una riga sola nel master ma tanti appuntamenti distinti, e la
# catena non le ripescava mai: il 18/08/2026 la pagina non pubblicò niente pur
# avendo una proiezione vera quella sera. Qui si espandono nelle loro date.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import serie_ricorrenti  # noqa: E402

GIORNO_SETTIMANALE = 6  # Domenica: esce il settimanale della settimana dopo
GIORNO_WEEKEND = 3      # Giovedì: esce il weekend ven-sab-dom


# ---------------------------------------------------------------------------
# La coda vera è quella su GitHub
# ---------------------------------------------------------------------------
def coda_dal_remoto():
    """Buste presenti su origin/main, per data (AAAAMMGG) -> insieme di tipi.

    Si legge dal RAMO REMOTO e non dal disco: il robot che pubblica fa il
    checkout di origin/main, quindi una busta che esiste solo sul Mac per lui
    non esiste. Si guarda anche in archivio/ perché una busta uscita stamattina
    è già stata spostata lì, e senza contarla il giorno risulterebbe scoperto.
    """
    subprocess.run(["git", "fetch", "-q", "origin"], cwd=REPO, check=False)

    # Normalmente si legge `origin/main`. Ma questa guardia gira anche su GitHub
    # Actions (dentro `avviso-imminenti.py`), dove il checkout è superficiale e il
    # riferimento `origin/main` può non esistere: lì però il codice estratto È
    # origin/main, quindi `HEAD` dice la stessa cosa. Senza questo ripiego la
    # guardia morirebbe in cloud proprio mentre serve.
    riferimento = "origin/main"
    esito = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", riferimento, "posts/", "archivio/"],
        cwd=REPO, capture_output=True, text=True,
    )
    if esito.returncode != 0:
        riferimento = "HEAD"
        print("ℹ️  `origin/main` non raggiungibile: leggo la coda da HEAD "
              "(normale su GitHub Actions, dove il checkout È origin/main).")
        esito = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", riferimento, "posts/", "archivio/"],
            cwd=REPO, capture_output=True, text=True, check=True,
        )
    out = esito.stdout
    buste = collections.defaultdict(set)
    for riga in out.splitlines():
        m = re.search(r"(?:^posts/|^archivio/[^/]+/)(\d{8})_(.+)\.json$", riga)
        if m:
            buste[m.group(1)].add(m.group(2).lower())
    return buste


# ---------------------------------------------------------------------------
# Il registro master: dove stanno gli eventi veri
# ---------------------------------------------------------------------------
def _date_del_campo(campo, anno):
    """Tutte le date che il campo 'data' del master può contenere.

    Il master scrive le date in più modi: '21/08', '21-23/08', '26/07-23/08',
    '21, 22, 23, 28, 29/08'. Qui si estrae l'intervallo coperto (prima e ultima
    data), che basta per sapere se una riga tocca un certo giorno.
    """
    campo = campo.replace("–", "-").replace("—", "-")
    trovate = []
    for g1, m1, g2, m2 in re.findall(r"(\d{1,2})(?:/(\d{1,2}))?\s*-\s*(\d{1,2})/(\d{1,2})", campo):
        mm1 = int(m1) if m1 else int(m2)
        for g, mm in ((int(g1), mm1), (int(g2), int(m2))):
            try:
                trovate.append(datetime.date(anno, mm, g))
            except ValueError:
                pass
    for g, mm in re.findall(r"(\d{1,2})/(\d{1,2})(?!/)", campo):
        try:
            trovate.append(datetime.date(anno, int(mm), int(g)))
        except ValueError:
            pass
    return (min(trovate), max(trovate)) if trovate else None


def eventi_master(anno):
    """Righe del registro master, con date interpretate. Solo lettura."""
    righe = []
    if not MASTER.exists():
        return righe
    for n, linea in enumerate(MASTER.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.startswith("|"):
            continue
        c = [x.strip() for x in linea.strip().strip("|").split("|")]
        if len(c) < 7 or c[0].lower() in ("id", "colonna") or set(c[0]) <= set("-: "):
            continue
        r = _date_del_campo(c[1], anno)
        if not r:
            continue
        righe.append({
            "id": c[0], "data": c[1], "titolo": c[2], "luogo": c[4],
            "stato_evento": c[5].lower(), "stato_post": c[6].lower(),
            "dal": r[0], "al": r[1], "riga_file": n,
        })
    return righe


def eventi_del_giorno(righe, d):
    """Righe del master che toccano il giorno `d` e non sono già concluse."""
    return [r for r in righe
            if r["dal"] <= d <= r["al"] and "concluso" not in r["stato_evento"]]


def ultimo_giorno_del_mese(d):
    primo_dopo = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    return (primo_dopo - datetime.timedelta(days=1)) == d


# ---------------------------------------------------------------------------
def _scheda_buco(titolo, quando, tipi_mancanti, candidati, serie=()):
    """Un buco con dentro tutto il necessario per chiuderlo (o per capire
    perché non si può). Mai un ⚠️ nudo: cosa manca, per quando, con che cosa."""
    approvati = [e for e in candidati if e["stato_post"] == "approvato"]
    return {
        "titolo": titolo,
        "quando": quando,
        "manca": tipi_mancanti,
        "candidati": candidati,
        "approvati": approvati,
        "serie": list(serie),
        "chiudibile": bool(approvati) or any(o["stato_post"] == "approvato" for o in serie),
    }


def main():
    # Data di riferimento. Normalmente è oggi; si può forzare per PROVARE la guardia
    # su una data qualsiasi senza aspettare che arrivi:
    #     python3 scripts/controllo-imminenti.py 2026-08-16
    # Serve a verificare che sappia ancora accorgersi dei buchi già successi — una
    # guardia che nessuno ha mai visto scattare non è una guardia.
    if len(sys.argv) > 1:
        oggi = datetime.date.fromisoformat(sys.argv[1])
        print(f"⚠️  PROVA: sto usando {oggi.strftime('%d/%m/%Y')} come 'oggi'.\n")
    else:
        oggi = datetime.date.today()
    domani = oggi + datetime.timedelta(days=1)
    dopodomani = oggi + datetime.timedelta(days=2)

    buste = coda_dal_remoto()
    master = eventi_master(oggi.year)
    occorrenze_serie = serie_ricorrenti.occorrenze_serie(oggi.year)

    print("Guardia degli imminenti — le prossime 48 ore\n")
    print(f"Oggi     : {oggi.strftime('%d/%m/%Y')} {GIORNI[oggi.weekday()]}")
    print(f"Orizzonte: fino al {dopodomani.strftime('%d/%m/%Y')} {GIORNI[dopodomani.weekday()]}")
    print(f"Master   : {len(master)} righe con data leggibile, "
          f"{len(occorrenze_serie)} appuntamenti di serie ricorrenti\n")

    buchi = []

    # --- 1. Feed e storie di DOMANI (slot 7:00) ------------------------------
    tipi_domani = buste.get(domani.strftime("%Y%m%d"), set())
    manca = []
    if not any("giornaliero" in t for t in tipi_domani):
        manca.append("post feed")
    if not any("storia" in t for t in tipi_domani):
        manca.append("storie")
    if manca:
        buchi.append(_scheda_buco(
            f"Domani {domani.strftime('%d/%m')} {GIORNI[domani.weekday()]} — slot 7:00",
            domani, manca, eventi_del_giorno(master, domani),
            serie=serie_ricorrenti.occorrenze_del_giorno(occorrenze_serie, domani)))

    # --- 2. Aggregati in scadenza entro 48 ore -------------------------------
    # Si guarda anche OGGI: un aggregato delle 18:00 di oggi è ancora in tempo
    # se la catena gira alle 18:30? No — sarebbe in ritardo di 30 minuti, ma
    # rientra nella finestra di recupero di 2 giorni, quindi va comunque fatto.
    for d in (oggi, domani, dopodomani):
        tipi = buste.get(d.strftime("%Y%m%d"), set())
        attesi = []
        if d.weekday() == GIORNO_SETTIMANALE:
            attesi.append(("settimanale", "settimanale",
                           d + datetime.timedelta(days=1), d + datetime.timedelta(days=7)))
        if d.weekday() == GIORNO_WEEKEND:
            attesi.append(("weekend", "weekend",
                           d + datetime.timedelta(days=1), d + datetime.timedelta(days=3)))
        if ultimo_giorno_del_mese(d):
            primo = d + datetime.timedelta(days=1)
            attesi.append(("carosello mensile", "carosello",
                           primo, (primo.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
                           - datetime.timedelta(days=1)))
        for nome, chiave, copre_dal, copre_al in attesi:
            if any(chiave in t for t in tipi):
                continue
            candidati = []
            g = copre_dal
            while g <= copre_al:
                candidati.extend(eventi_del_giorno(master, g))
                g += datetime.timedelta(days=1)
            visti, unici = set(), []
            for e in candidati:
                if e["id"] not in visti:
                    visti.add(e["id"])
                    unici.append(e)
            quando = "OGGI" if d == oggi else ("DOMANI" if d == domani else "dopodomani")
            buchi.append(_scheda_buco(
                f"{nome.capitalize()} del {d.strftime('%d/%m')} {GIORNI[d.weekday()]} "
                f"ore 18:00 ({quando}) — copre {copre_dal.strftime('%d/%m')}"
                f"–{copre_al.strftime('%d/%m')}",
                d, [nome], unici))

    # --- Referto ------------------------------------------------------------
    if not buchi:
        print("✅ Le prossime 48 ore sono coperte: niente da fare.")
        return 0

    chiudibili = [b for b in buchi if b["chiudibile"]]

    for b in buchi:
        segno = "❌" if b["chiudibile"] else "⚪"
        print(f"{segno} {b['titolo']}")
        print(f"   manca: {' e '.join(b['manca'])}")
        if b["serie"]:
            # Questi sono i più insidiosi: una serie ricorrente è già `approvato` da
            # settimane, non ripassa mai dalla ricerca, e nessuno si accorge che il
            # suo appuntamento di domani non ha un post. È il buco del 18/08/2026.
            print("   📌 SERIE RICORRENTI con un appuntamento quel giorno "
                  "(la catena non le ripesca da sola):")
            for o in b["serie"]:
                prog = f" — {o['programma']}" if o["programma"] else ""
                marchio = "" if o["stato_post"] == "approvato" else f"  ⟵ `{o['stato_post']}`"
                print(f"      · [{o['id']}] {o['serie']}{prog} · {o['luogo'][:44]}{marchio}")
            print("      Apri la riga nel master e leggi la nota prima di scrivere:")
            print("      il titolo qui sopra è ritagliato dalla prosa, non è testo pronto.")
        if b["approvati"]:
            print(f"   CHIUDIBILE ORA — {len(b['approvati'])} eventi già `approvato` a registro:")
            lunghi = False
            for e in b["approvati"][:12]:
                # Una riga con intervallo lungo (una rassegna, una mostra) non vuol dire
                # che ci sia qualcosa TUTTI i giorni dell'intervallo: le date vere stanno
                # nella nota. Es. "Cinema nei Castelli 03-26/08" proietta solo lun/mar/mer.
                esteso = (e["al"] - e["dal"]).days >= 6
                lunghi = lunghi or esteso
                print(f"      · [{e['id']}] {e['titolo']} — {e['luogo'][:52]} ({e['data']})"
                      + ("  ⟵ intervallo lungo: leggi la NOTA per le date vere" if esteso else ""))
            if lunghi:
                print("   ⚠️  Le righe segnate 'intervallo lungo' sono rassegne o mostre: qui compaiono")
                print("       perché il loro intervallo tocca queste date, NON perché ci sia una data")
                print("       confermata. Prima di metterle in un contenuto, apri la riga nel master")
                print("       e leggi la nota: se quel giorno non c'è, non ci va.")
        elif b["candidati"]:
            print("   NON chiudibile da sola: ci sono eventi ma nessuno è `approvato`.")
            print("   Servono i pulsanti ✅ di Michele su Telegram, e vanno mandati SUBITO:")
            for e in b["candidati"][:12]:
                print(f"      · [{e['id']}] {e['titolo']} — stato post: {e['stato_post']}")
        else:
            print("   Legittimamente vuoto: nel master non c'è nessun evento per queste date.")
            print("   Non si inventano eventi per riempire un giorno.")
        print()

    if chiudibili:
        print(f"➡️  {len(chiudibili)} buchi su {len(buchi)} sono CHIUDIBILI ADESSO.")
        print("   Vanno chiusi in questo giro: compilare la grafica, mettere la busta in")
        print("   coda e spingere su origin/main. Non si consegna questo elenco a Michele.")
        return 2

    # Restano i buchi non chiudibili. Ma sono due cose diverse, e confonderle
    # trasformerebbe l'avviso in rumore: c'è chi aspetta un ✅ di Michele (azionabile,
    # va detto) e c'è il giorno semplicemente senza eventi (normale, deve tacere).
    # Un allarme che suona anche per il secondo caso suonerebbe quasi ogni sera, e
    # nel giro di una settimana nessuno lo leggerebbe più.
    aspettano_ok = [b for b in buchi if b["candidati"] and not b["approvati"]]
    if aspettano_ok:
        print(f"⚠️  {len(aspettano_ok)} buchi su {len(buchi)} aspettano l'ok di Michele.")
        print("   Vanno mandati su Telegram coi pulsanti, dicendo entro quando servono.")
        return 1

    print(f"✅ {len(buchi)} buchi, tutti legittimamente vuoti: nessun evento a registro")
    print("   per quelle date. Non c'è niente da fare e non c'è niente da segnalare.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
