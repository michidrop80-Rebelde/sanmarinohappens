import json,os,glob,collections
d=os.path.expanduser("~/.claude/projects/-Users-michele-Desktop-PROGETTI-San-Marino-Happens")
rows=[]
for f in glob.glob(d+"/*.jsonl"):
    agg=collections.defaultdict(lambda:[0,0,0,0])
    first=None; ts0=None; ts1=None; n=0
    for line in open(f,errors="replace"):
        try: o=json.loads(line)
        except: continue
        t=o.get("timestamp")
        if t:
            ts0=ts0 or t; ts1=t
        if o.get("type")=="user" and first is None:
            c=o.get("message",{}).get("content")
            if isinstance(c,list):
                c="".join(x.get("text","") for x in c if isinstance(x,dict))
            if isinstance(c,str) and c.strip():
                first=c.strip().replace("\n"," ")[:150]
        m=o.get("message") or {}
        u=m.get("usage")
        if u:
            n+=1
            k=m.get("model","?")
            a=agg[k]
            a[0]+=u.get("input_tokens",0); a[1]+=u.get("cache_creation_input_tokens",0)
            a[2]+=u.get("cache_read_input_tokens",0); a[3]+=u.get("output_tokens",0)
    if not agg: continue
    rows.append(dict(f=os.path.basename(f)[:8],ts0=ts0,ts1=ts1,n=n,first=first,agg={k:v for k,v in agg.items()}))
rows.sort(key=lambda r: r["ts0"] or "")
print(json.dumps(rows,ensure_ascii=False,indent=0))
