#!/usr/bin/env python3
"""Prove di controllo-secco.py. Uso: python3 scripts/controllo_secco_test.py"""
import importlib.util, sys, tempfile
from pathlib import Path
spec = importlib.util.spec_from_file_location("cs", Path(__file__).parent / "controllo-secco.py")
cs = importlib.util.module_from_spec(spec); spec.loader.exec_module(cs)
ok = ko = 0
def prova(n, c):
    global ok, ko
    print("✅" if c else "❌", n); ok, ko = (ok + 1, ko) if c else (ok, ko + 1)
def repo(imm_exit, **code):
    d = Path(tempfile.mkdtemp()); (d / "queue").mkdir(); (d / "scripts").mkdir()
    (d / "scripts/controllo-imminenti.py").write_text(f"import sys;sys.exit({imm_exit})")
    for nome, t in code.items(): (d / "queue" / f"{nome}.md").write_text(t)
    return d
r = cs.controlla(repo(0, approvazioni="- [x] a\n"))
prova("[1] tutto chiuso e nessun buco -> niente da fare", r["lavoro"] == "no")
r = cs.controlla(repo(0, approvazioni="- [ ] a\n- [ ] b\n"))
prova("[2] due approvazioni aperte -> lavoro, conta 2", r["lavoro"] == "si" and r["approvazioni"] == 2)
r = cs.controlla(repo(0, **{"foto-inbox": "- [ ] foto\n"}))
prova("[3] una foto in coda conta come segnalazione", r["lavoro"] == "si" and r["segnalazioni"] == 1)
r = cs.controlla(repo(2))
prova("[4] guardia imminenti exit 2 -> lavoro", r["lavoro"] == "si" and r["imminenti"] == "si")
r = cs.controlla(repo(1))
prova("[5] guardia rotta -> nel dubbio si lavora (e lo dice)", r["lavoro"] == "si" and r["dubbio"] == "si")
r = cs.controlla(repo(0, annullamenti="- [ ] x\n"))
prova("[6] annullamento aperto -> lavoro", r["lavoro"] == "si" and r["annullamenti"] == 1)
print(f"\n{ok}/{ok+ko}"); sys.exit(0 if ko == 0 else 1)
