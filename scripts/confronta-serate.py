#!/usr/bin/env python3
"""Confronta la catena serale del cloud con quella del Mac, sui FATTI.

PERCHE' ESISTE (ticket 15 della mappa "La catena si stacca dal Mac")
Il cloud gira come SECONDO PARERE su un ramo suo (`catena-cloud`), il Mac sul
suo `main`. Per fidarci del cloud serve un metro che dica "hanno lavorato
uguale" con dei numeri, non a occhio.

COSA SI CONFRONTA (gli EFFETTI, non i racconti dell'agente)
  1. le righe delle code (approvazioni, segnalazioni, annullamenti) passate da
     `- [ ]` a `- [x]`: stessa chiave = stesso timestamp della riga;
  2. i titoli nuovi nei file `post-approvati-*.md`;
  3. i file nuovi in dati/eventi, dati/post, dati/post/approvati.
Ogni lato si misura contro la STESSA base: lo SHA di `main` al momento in cui il
cloud ha staccato il ramo. Cloud = base..ramo. Mac = base..main.

LE TRE LEZIONI DELL'08/09 (ticket 08) COSTRUITE DENTRO
  - un metro non deve poter contare il lavoro dell'ALTRO come proprio: ogni lato
    si legge dai file alla base e al suo punto d'arrivo, mai da un ramo che
    nasce gia' pieno; le righe `[ ]` arrivate DOPO la base (il Worker ne scrive
    a ogni click) non contano come lavoro di nessuno;
  - "verde" non e' "fatto": un lato senza nessun effetto viene detto "a vuoto",
    non "uguale";
  - se il Mac non ha lavorato (la coda su main e' ancora aperta, nessun suo
    effetto) il confronto e' "NON CONFRONTABILE", non un'assoluzione.

USCITA: 0 = concordano (o nessuno aveva da fare) · 1 = differenze · 4 = non
confrontabile.
USO: confronta-serate.py --base SHA --cloud origin/catena-cloud --mac origin/main
     [--aveva-lavoro si|no] [--una-riga]
"""
import argparse
import re
import subprocess
import sys
import unicodedata

CODE = ["queue/approvazioni.md", "queue/inbox.md", "queue/foto-inbox.md", "queue/annullamenti.md"]
CARTELLE = ["dati/eventi/", "dati/post/"]
APPROVATI = "dati/post/approvati/"


def git(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def file_a(rif, path):
    return git("show", f"{rif}:{path}") or ""


def chiave(riga):
    m = re.match(r"- \[[ x]\] (\S+)", riga)
    return m.group(1) if m else None


def aperte(testo):
    return {chiave(r) for r in testo.splitlines() if r.startswith("- [ ]") and chiave(r)}


def chiuse(testo):
    return {chiave(r) for r in testo.splitlines() if r.startswith("- [x]") and chiave(r)}


def titoli(testo):
    return {t.strip() for t in re.findall(r"^##\s+(.+)$", testo, re.M)}


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return re.sub(r"[^a-z0-9 ]+", " ", "".join(c for c in t if not unicodedata.combining(c)))


def parole(t):
    return {w for w in norm(t).split() if len(w) > 2 and not w.isdigit()}


def stesso(a, b):
    """Due titoli sono lo stesso evento se uno CONTIENE l'altro (come confronta-giri.py).

    Non la somiglianza: «San Marino - Finlandia» e «San Marino - Albania» si
    somigliano e sono due partite diverse. Servono almeno due parole vere.
    """
    pa, pb = parole(a), parole(b)
    if len(pa) < 2 or len(pb) < 2:
        return pa == pb and bool(pa)
    return pa <= pb or pb <= pa


def file_nuovi(base, rif):
    out = git("diff", "--name-status", "--diff-filter=A", base, rif, "--", *CARTELLE) or ""
    return {r.split("\t", 1)[1] for r in out.splitlines() if "\t" in r}


def effetti(base, rif):
    """Cosa ha FATTO questo lato rispetto alla base."""
    chiuse_ = set()
    for p in CODE:
        prima, dopo = file_a(base, p), file_a(rif, p)
        # solo righe che alla base erano aperte: quelle nate dopo non sono lavoro
        chiuse_ |= {(p, k) for k in aperte(prima) & chiuse(dopo)}
    nuovi_t = set()
    elenco = git("ls-tree", "--name-only", rif, APPROVATI) or ""
    for p in elenco.splitlines():
        if p.endswith(".md"):
            nuovi_t |= titoli(file_a(rif, p)) - titoli(file_a(base, p))
    return {"chiuse": chiuse_, "titoli": nuovi_t, "file": file_nuovi(base, rif)}


def n_effetti(e):
    return len(e["chiuse"]) + len(e["titoli"]) + len(e["file"])


def accosta_titoli(a, b):
    solo_a = [x for x in a if not any(stesso(x, y) for y in b)]
    solo_b = [y for y in b if not any(stesso(x, y) for x in a)]
    return solo_a, solo_b


def confronta(base, cloud, mac, aveva_lavoro="?"):
    ec, em = effetti(base, cloud), effetti(base, mac)
    nc, nm = n_effetti(ec), n_effetti(em)
    righe = [f"cloud: {len(ec['chiuse'])} righe di coda chiuse · {len(ec['titoli'])} titoli approvati · {len(ec['file'])} file nuovi",
             f"Mac:   {len(em['chiuse'])} righe di coda chiuse · {len(em['titoli'])} titoli approvati · {len(em['file'])} file nuovi"]
    if nc == 0 and nm == 0:
        if aveva_lavoro == "no":
            return 0, "✅ nessuno dei due aveva niente da fare (il controllo secco del cloud ha detto no)", righe
        # codici aperti su main alla base e ancora aperti: il Mac non ha girato
        return 4, "⛔ non confrontabile: né il cloud né il Mac hanno prodotto niente, ma c'era lavoro", righe
    if nm == 0:
        return 4, "⛔ non confrontabile: il Mac non ha lavorato su questa sera (sul suo ramo non cambia niente)", righe
    if nc == 0:
        return 1, "🔴 il cloud è rimasto a vuoto mentre il Mac ha lavorato", righe
    diff = []
    for p, k in sorted(ec["chiuse"] ^ em["chiuse"]):
        lato = "solo cloud" if (p, k) in ec["chiuse"] else "solo Mac"
        diff.append(f"riga {p} {k}: {lato}")
    sc, sm = accosta_titoli(ec["titoli"], em["titoli"])
    diff += [f"titolo approvato solo cloud: {t}" for t in sc] + [f"titolo approvato solo Mac: {t}" for t in sm]
    if ec["file"] != em["file"]:
        diff.append(f"file nuovi: solo cloud {sorted(ec['file'] - em['file'])} · solo Mac {sorted(em['file'] - ec['file'])}")
    if diff:
        return 1, f"🟡 {len(diff)} differenze da spiegare", righe + ["  - " + d for d in diff]
    return 0, "✅ hanno lavorato uguale", righe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--cloud", default="origin/catena-cloud")
    ap.add_argument("--mac", default="origin/main")
    ap.add_argument("--aveva-lavoro", default="?")
    ap.add_argument("--una-riga", action="store_true")
    a = ap.parse_args()
    cod, verdetto, righe = confronta(a.base, a.cloud, a.mac, a.aveva_lavoro)
    print(verdetto)
    if not a.una_riga:
        print("\n".join(righe))
    return cod


if __name__ == "__main__":
    sys.exit(main())
