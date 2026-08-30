#!/usr/bin/env python3
"""
Ricostruisce i file del progetto San Marino Happens dai transcript delle sessioni Claude.

Perché funziona: ogni volta che Claude legge (Read) o scrive (Write) un file, il
CONTENUTO INTERO finisce nel .jsonl della sessione. Gli Edit registrano old_string/
new_string. Quindi si può ricostruire la versione finale di un file così:

  1. prendi lo snapshot completo piu' RECENTE (Write, oppure Read de-numerato)
  2. riapplica in ordine tutti gli Edit avvenuti DOPO quello snapshot

Uso:  python3 recupera.py <cartella_destinazione>
"""
import json, glob, os, re, sys, collections

# ⚠️ Si guardano TUTTE le cartelle di transcript, non solo quella del progetto.
# Motivo (scoperto il 27/07/2026): le sessioni aperte dalla cartella padre PROGETTI
# finiscono in `-Users-michele-Desktop-PROGETTI`, non in `...-San-Marino-Happens`.
# Il recupero del 25/07 ne guardava una sola: e' per questo che 43 file risultavano
# "non recuperabili". Il filtro sui percorsi (BASE) basta a tenere fuori gli altri progetti.
TRANSCRIPTS_ROOT = "/Users/michele/.claude/projects"
BASE = "/Users/michele/Desktop/PROGETTI/San Marino Happens/"
DEST = sys.argv[1]

# ---------------------------------------------------------------- raccolta
# eventi[path] = lista di (timestamp, tipo, dati)
eventi = collections.defaultdict(list)
# per collegare un tool_result di Read al suo file_path serve la mappa id->path
pending_read = {}

records = []
for f in sorted(glob.glob(os.path.join(TRANSCRIPTS_ROOT, "*", "*.jsonl"))):
    for line in open(f, errors="ignore"):
        try:
            o = json.loads(line)
        except Exception:
            continue
        records.append((o.get("timestamp") or "", o))
records.sort(key=lambda x: x[0])

def blocks(o):
    m = o.get("message") or {}
    c = m.get("content")
    return c if isinstance(c, list) else []

for ts, o in records:
    for b in blocks(o):
        if not isinstance(b, dict):
            continue
        # --- chiamate agli strumenti
        if b.get("type") == "tool_use":
            name, inp = b.get("name"), (b.get("input") or {})
            p = inp.get("file_path", "")
            if not p.startswith(BASE):
                continue
            rel = p[len(BASE):]
            if name == "Write":
                eventi[rel].append((ts, "full", inp.get("content", "")))
            elif name == "Edit":
                eventi[rel].append((ts, "edit", (
                    inp.get("old_string", ""),
                    inp.get("new_string", ""),
                    bool(inp.get("replace_all")),
                )))
            elif name == "Read":
                # una Read parziale (offset/limit) non e' uno snapshot affidabile
                if not inp.get("offset") and not inp.get("limit"):
                    pending_read[b.get("id")] = (rel, ts)
        # --- risultati (qui vive il contenuto delle Read)
        elif b.get("type") == "tool_result":
            key = b.get("tool_use_id")
            if key not in pending_read:
                continue
            rel, ts_r = pending_read.pop(key)
            c = b.get("content")
            if isinstance(c, list):
                c = "".join(x.get("text", "") for x in c if isinstance(x, dict))
            if not isinstance(c, str) or "system-reminder" in c[:200] and "\t" not in c[:200]:
                continue
            # formato "cat -n": "   12\ttesto"
            righe = c.split("\n")
            num = [r for r in righe if re.match(r"^\s*\d+\t", r)]
            if len(num) < max(1, len(righe) // 2):
                continue  # non sembra un file letto -> scarta
            testo = "\n".join(re.sub(r"^\s*\d+\t", "", r) for r in num)
            eventi[rel].append((ts_r, "full", testo))

# ---------------------------------------------------------------- ricostruzione
os.makedirs(DEST, exist_ok=True)
ok, parziali, falliti = [], [], []

for rel, evs in sorted(eventi.items()):
    evs.sort(key=lambda x: x[0])
    # ultimo snapshot completo
    idx = max((i for i, e in enumerate(evs) if e[1] == "full"), default=None)
    if idx is None:
        falliti.append((rel, "solo Edit, nessuno snapshot completo"))
        continue
    testo = evs[idx][2]
    applicati = saltati = 0
    for ts, tipo, d in evs[idx + 1:]:
        if tipo != "edit":
            continue
        old, new, allrep = d
        if old and old in testo:
            testo = testo.replace(old, new) if allrep else testo.replace(old, new, 1)
            applicati += 1
        else:
            saltati += 1
    out = os.path.join(DEST, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(testo)
    (parziali if saltati else ok).append((rel, evs[idx][0][:16], applicati, saltati))

print(f"RICOSTRUITI PULITI : {len(ok)}")
print(f"CON EDIT NON APPLICATI: {len(parziali)}")
print(f"NON RICOSTRUIBILI  : {len(falliti)}")
if parziali:
    print("\n-- da ricontrollare (qualche Edit non ha trovato aggancio) --")
    for rel, ts, a, s in parziali:
        print(f"   {rel}  (snapshot {ts}, edit ok {a}, saltati {s})")
if falliti:
    print("\n-- non ricostruibili --")
    for rel, why in falliti:
        print(f"   {rel}: {why}")
