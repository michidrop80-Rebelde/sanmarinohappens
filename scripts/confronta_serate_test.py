#!/usr/bin/env python3
"""Prove di confronta-serate.py su un repo git finto. Uso: python3 scripts/confronta_serate_test.py"""
import importlib.util, os, subprocess, sys, tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("cs", Path(__file__).parent / "confronta-serate.py")
cs = importlib.util.module_from_spec(spec); spec.loader.exec_module(cs)

ok = ko = 0
def prova(nome, cond):
    global ok, ko
    print(("✅" if cond else "❌"), nome)
    ok, ko = (ok + 1, ko) if cond else (ok, ko + 1)

def sh(*a, cwd):
    subprocess.run(a, cwd=cwd, check=True, capture_output=True)

def scrivi(d, p, t):
    f = Path(d, p); f.parent.mkdir(parents=True, exist_ok=True); f.write_text(t, encoding="utf-8")

def commit(d, msg):
    sh("git", "add", "-A", cwd=d); sh("git", "commit", "-qm", msg, cwd=d)

def nuovo_repo():
    d = tempfile.mkdtemp()
    sh("git", "init", "-q", "-b", "main", cwd=d)
    sh("git", "config", "user.email", "t@t", cwd=d); sh("git", "config", "user.name", "t", cwd=d)
    scrivi(d, "queue/approvazioni.md", "# coda\n- [ ] 2026-10-16T10:00:00.000Z — approvato — g-01 — M — Concerto Jazz\n- [ ] 2026-10-16T10:00:01.000Z — approvato — g-02 — M — Partita San Marino Albania\n")
    scrivi(d, "dati/post/approvati/post-approvati-2026-10-12.md", "# Approvati\n## 14/10 — Mementi\n")
    commit(d, "base")
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
    return d, base

def lavora(d, ramo, righe_chiuse=(1, 2), titoli=("## 17/10 — Concerto Jazz", "## 18/10 — San Marino - Albania")):
    sh("git", "checkout", "-q", "-B", ramo, "main" if ramo != "main" else "HEAD", cwd=d) if ramo != "main" else None
    t = Path(d, "queue/approvazioni.md").read_text()
    for i in righe_chiuse:
        t = t.replace(f"- [ ] 2026-10-16T10:00:0{i-1}", f"- [x] 2026-10-16T10:00:0{i-1}")
    scrivi(d, "queue/approvazioni.md", t)
    scrivi(d, "dati/post/approvati/post-approvati-2026-10-17.md", "# Approvati\n" + "\n".join(titoli) + "\n")
    commit(d, ramo)

def esegui(d, base, cloud, mac, **kw):
    cwd = os.getcwd(); os.chdir(d)
    try: return cs.confronta(base, cloud, mac, **kw)
    finally: os.chdir(cwd)

# [1] uguali anche con titoli riscritti
d, base = nuovo_repo()
lavora(d, "cloud", titoli=("## 17/10 — Concerto Jazz — Titanico", "## 18/10 — San Marino - Albania"))
sh("git", "checkout", "-q", "main", cwd=d)
lavora(d, "main")
c, v, _ = esegui(d, base, "cloud", "main")
prova("[1] stesso lavoro, titolo riscritto -> concordano (0)", c == 0 and "uguale" in v)

# [2] il Mac non ha lavorato: NON confrontabile, non assoluzione
d, base = nuovo_repo()
lavora(d, "cloud"); sh("git", "checkout", "-q", "main", cwd=d)
c, v, _ = esegui(d, base, "cloud", "main", aveva_lavoro="si")
prova("[2] Mac fermo -> 4 non confrontabile", c == 4 and "Mac non ha lavorato" in v)

# [3] il cloud a vuoto mentre il Mac lavora
d, base = nuovo_repo()
sh("git", "branch", "cloud", cwd=d); lavora(d, "main")
c, v, _ = esegui(d, base, "cloud", "main")
prova("[3] cloud a vuoto -> 1 e lo dice", c == 1 and "vuoto" in v)

# [4] una riga chiusa da uno solo
d, base = nuovo_repo()
lavora(d, "cloud", righe_chiuse=(1,)); sh("git", "checkout", "-q", "main", cwd=d)
lavora(d, "main", righe_chiuse=(1, 2))
c, v, r = esegui(d, base, "cloud", "main")
prova("[4] differenza di una riga -> 1 con 'solo Mac'", c == 1 and any("solo Mac" in x for x in r))

# [5] Albania != Finlandia
d, base = nuovo_repo()
lavora(d, "cloud", titoli=("## 18/10 — San Marino - Albania",)); sh("git", "checkout", "-q", "main", cwd=d)
lavora(d, "main", titoli=("## 18/10 — San Marino - Finlandia",))
c, v, r = esegui(d, base, "cloud", "main")
prova("[5] due partite diverse NON si fondono", c == 1 and any("titolo approvato solo cloud" in x for x in r))

# [6] righe nate DOPO la base (il Worker) non sono lavoro di nessuno
d, base = nuovo_repo()
sh("git", "branch", "cloud", cwd=d)
t = Path(d, "queue/approvazioni.md").read_text() + "- [x] 2026-10-17T05:00:00.000Z — approvato — g-09 — M — Nuova\n"
scrivi(d, "queue/approvazioni.md", t); commit(d, "worker")
c, v, _ = esegui(d, base, "cloud", "main", aveva_lavoro="no")
prova("[6] riga nata dopo la base non conta -> nessuno aveva da fare (0)", c == 0 and "niente da fare" in v)

# [7] entrambi vuoti ma c'era lavoro: non si assolve
d, base = nuovo_repo(); sh("git", "branch", "cloud", cwd=d)
c, v, _ = esegui(d, base, "cloud", "main", aveva_lavoro="si")
prova("[7] entrambi vuoti con lavoro -> 4, non 'uguali'", c == 4)

print(f"\n{ok}/{ok + ko}")
sys.exit(0 if ko == 0 else 1)
