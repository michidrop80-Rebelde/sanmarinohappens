#!/usr/bin/env python3
"""Scrive il referto del giro in cloud: quello che Michele legge sul telefono.

PERCHE' E' UN FILE PYTHON E NON DUE PAGINE DI SHELL (ticket 08)
Questo testo è l'unica cosa che Michele vede di un giro girato di notte mentre
lui dormiva. Deve dire la verità in tutti e quattro i casi — completato, fermato
con grazia, caduto a metà, ripreso — e deve dirla in italiano. In shell sarebbe
un intreccio di `if` illeggibile; qui si legge, e soprattutto si può PROVARE
senza far girare niente in cloud (vedi referto_giro_cloud_test.py).

⚠️ Questo script non tocca nessuna chiave: scrive solo un testo su /tmp.
A spedirlo ci pensa il passo dopo (regola del ticket 07).

LEGGE dall'ambiente: DATA, AVVIO, RIPRESA, INTEGRITA, T1..T4_STATO/_COSTO/
_EVENTI/_VERIFICATI/_BOZZE, T1..T4_RES, RUN_URL, E_RIPRESA, CHI_SVEGLIA
SCRIVE: /tmp/referto.txt (per Telegram) · /tmp/riepilogo.md (pagina della run)
        e `manda=si|no` su GITHUB_OUTPUT
"""

import os
import subprocess
import time
from pathlib import Path

TAPPE = [
    ("1", "Ricerca"),
    ("2", "Postino"),
    ("3", "Verifica"),
    ("4", "Testi"),
]


def env(nome, default=""):
    return os.environ.get(nome, default) or default


# ---------------------------------------------------------------------------
# I FILE FANTASMA
# ---------------------------------------------------------------------------
# Il ramo del giro nasce come copia di `main`, che contiene già i file del giro
# del Mac. Se un anello in cloud non scrive niente, sul ramo resta la copia del
# Mac — e contarla vuol dire dire a Michele «22 eventi trovati» quando il cloud
# non ne ha trovato nemmeno uno. E' successo nella prima corsa (07/09/2026):
# tre anelli morti sul serbatoio esaurito, e il referto che diceva «fatta» a
# tutte e quattro le tappe.
# Un file con la stessa impronta git di `main` NON è lavoro del cloud, punto.

FILE_DELL_ANELLO = {
    "1": "dati/eventi/eventi-{d}.md",
    "2": "dati/eventi/eventi-{d}.md",
    "3": "dati/eventi/verificati/eventi-verificati-{d}.md",
    "4": "dati/post/post-{d}.md",
}


def _git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def fantasma(numero: str) -> bool:
    """True se il file di quell'anello è identico a quello di main (= non scritto)."""
    percorso = FILE_DELL_ANELLO[numero].format(d=env("DATA"))
    qui = _git("rev-parse", f"HEAD:{percorso}")
    if qui is None:
        return True                      # non c'è proprio: di sicuro non l'ha scritto
    for base in ("origin/main", "main"):
        la = _git("rev-parse", f"{base}:{percorso}")
        if la is not None:
            return qui == la
    return False                         # senza main non si può dire: non si accusa


def riga_numeri(n: str) -> str:
    """La riga di numeri di ogni tappa, misurati dai file."""
    if fantasma(n):
        return "NIENTE (il file è la copia di quello del Mac)"
    if n == "1":
        e = env("T1_EVENTI", "-")
        return f"{e} eventi" if e != "-" else "nessun file di eventi"
    if n == "2":
        e = env("T2_EVENTI", "-")
        return f"{e} eventi in tutto" if e != "-" else "nessun file di eventi"
    if n == "3":
        v = env("T3_VERIFICATI", "-")
        if v in ("-", "-/-/-"):
            return "nessun file verificato"
        ok, dubbi, scart = (v.split("/") + ["-", "-", "-"])[:3]
        return f"✅ {ok} · ⚠️ {dubbi} · 🗑 {scart}"
    b = env("T4_BOZZE", "-")
    return f"{b} bozze" if b != "-" else "nessun file di bozze"


def stato_leggibile(n: str) -> str:
    stato = env(f"T{n}_STATO")
    res = env(f"T{n}_RES")
    if stato.startswith("saltata"):
        return "già fatta prima"
    if stato == "fatta":
        # «fatta» senza aver prodotto niente non è fatta: è passata senza lavorare.
        return "🛑 nessun lavoro prodotto" if fantasma(n) else "fatta"
    if res == "skipped":
        return "non partita"
    if res in ("failure", "cancelled"):
        return "CADUTA"
    return res or "?"


def dove_si_e_fermata():
    """Restituisce (numero, nome) della prima tappa caduta, o None."""
    for n, nome in TAPPE:
        if env(f"T{n}_RES") in ("failure", "cancelled"):
            return n, nome
    return None


def fermato_con_grazia() -> bool:
    """Ricerca e postino non hanno trovato niente: non è un guasto, è silenzio."""
    return (env("T1_RES") == "success"
            and env("T2_RES") == "success"
            and env("T2_EVENTI", "-") in ("0", "-")
            and env("T3_RES") == "skipped")


def durata() -> str:
    try:
        secondi = int(time.time()) - int(float(env("AVVIO", "0")))
    except ValueError:
        return "?"
    if secondi <= 0:
        return "?"
    if secondi < 3600:
        return f"{secondi // 60} min"
    return f"{secondi // 3600}h {(secondi % 3600) // 60}min"


def costo() -> str:
    tot = 0.0
    for n, _ in TAPPE:
        try:
            tot += float(env(f"T{n}_COSTO", "0"))
        except ValueError:
            pass
    return f"{tot:.2f}".replace(".", ",")


def data_italiana(iso: str) -> str:
    p = iso.split("-")
    return f"{p[2]}/{p[1]}/{p[0]}" if len(p) == 3 else iso


def costruisci() -> tuple[str, bool]:
    """Restituisce (testo del referto, qualcosa_e_stato_fatto)."""
    data = env("DATA", "?")
    lavorato = any(env(f"T{n}_STATO") == "fatta" for n, _ in TAPPE)
    caduta = dove_si_e_fermata()
    righe = []

    if caduta:
        n, nome = caduta
        salve = [nm for k, nm in TAPPE if env(f"T{k}_STATO") in ("fatta",)
                 or env(f"T{k}_STATO", "").startswith("saltata")]
        salve = [nm for nm in salve if nm != nome]
        righe.append(f"🔴 <b>SMH — il giro in cloud del {data_italiana(data)} "
                     f"si è fermato</b>")
        righe.append("")
        righe.append(f"Caduto alla tappa {n} ({nome.lower()}).")
        if salve:
            righe.append(f"Salvo sul ramo giro-cloud: {', '.join(salve).lower()}.")
        else:
            righe.append("Niente di salvato: è caduto subito.")
        righe.append("")
        if env("E_RIPRESA") == "true":
            righe.append("⚠️ Questa ERA già la ripresa delle 09:00: il giro in "
                         "cloud è fermo e non riprova più da solo fino a lunedì "
                         "prossimo. Il giro del Mac non è toccato.")
        else:
            righe.append("Riprovo da solo alle 09:00, ripartendo da dove mi sono "
                         "fermato (le tappe già fatte non si rifanno).")
    elif fermato_con_grazia():
        righe.append(f"🟡 <b>SMH — giro in cloud del {data_italiana(data)}</b>")
        righe.append("")
        righe.append("Nessun evento: né la ricerca sulle fonti né la coda del bot "
                     "hanno prodotto qualcosa. Mi sono fermato prima della "
                     "verifica invece di girare a vuoto. Non è un guasto.")
    else:
        vuote = [nome for n, nome in TAPPE if fantasma(n)]
        if len(vuote) == len(TAPPE):
            righe.append(f"🛑 <b>SMH — giro in cloud del {data_italiana(data)}: "
                         f"passato a vuoto</b>")
            righe.append("")
            righe.append("Le tappe risultano finite ma NON hanno prodotto niente: sul "
                         "ramo ci sono ancora i file del giro del Mac, copiati uguali. "
                         "Di solito vuol dire che l'agente è morto subito — la causa "
                         "più probabile è il serbatoio dell'abbonamento esaurito.")
            righe.append("")
        else:
            righe.append(f"🤖 <b>SMH — giro in cloud del {data_italiana(data)}</b> "
                         f"(secondo parere)")
            righe.append("")
        for n, nome in TAPPE:
            righe.append(f"{n} {nome}: {riga_numeri(n)} — {stato_leggibile(n)}")

    righe.append("")
    if env("INTEGRITA") and not env("INTEGRITA").startswith("✅"):
        righe.append(f"Integrità: {env('INTEGRITA')}")
    righe.append(f"Peso: ${costo()} · durata {durata()}")
    if env("RIPRESA") == "si":
        righe.append("(questa corsa era una ripresa)")
    # La sveglia buona la suona cron-job.org (ticket 14): arriva come
    # `workflow_dispatch`. Se invece la corsa è partita da `schedule`, vuol dire
    # che cron-job.org NON ha chiamato e ha coperto la rete di sicurezza di
    # GitHub — che parte con ore di ritardo. Senza questa riga il guasto sarebbe
    # muto: il giro gira lo stesso, solo all'ora sbagliata, per sempre.
    if env("CHI_SVEGLIA") == "schedule":
        righe.append("")
        righe.append("⚠️ Questa corsa è partita dalla rete di sicurezza di GitHub, "
                     "non dalla sveglia puntuale di cron-job.org — che quindi non "
                     "ha chiamato (PAT scaduto? cronjob spento?). Il giro gira lo "
                     "stesso, ma all'ora che decide GitHub: anche 5 ore dopo. "
                     "Controlla i cronjob su cron-job.org.")
    righe.append("")
    righe.append("I pulsanti ✅/❌ te li manda il Mac alle 08:05, come sempre: "
                 "da qui non arriva niente da approvare.")
    righe.append(f"Run: {env('RUN_URL')}")
    return "\n".join(righe), lavorato


def main() -> int:
    testo, lavorato = costruisci()
    Path("/tmp/referto.txt").write_text(testo, encoding="utf-8")

    # Già avvisato per questo giro? Il marcatore vive sul ramo, quindi la
    # ripresa delle 09:00 che non trova niente da fare non manda un secondo
    # messaggio identico. Ma se ha davvero lavorato, si avvisa lo stesso.
    gia = Path(f"dati/cloud-giro/{env('DATA')}/avvisato.ok").exists()
    manda = "no" if (gia and not lavorato) else "si"

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"manda={manda}\n")

    riepilogo = ["## Giro settimanale in cloud", "",
                 "| tappa | numeri | esito | peso |", "|---|---|---|---|"]
    for n, nome in TAPPE:
        riepilogo.append(f"| {n} {nome} | {riga_numeri(n)} | {stato_leggibile(n)} "
                         f"| ${env(f'T{n}_COSTO', '0')} |")
    riepilogo += ["", f"Totale ${costo()} · durata {durata()} · "
                      f"avviso su Telegram: {manda}", "", "### Referto spedito",
                  "", "```", testo, "```"]
    Path("/tmp/riepilogo.md").write_text("\n".join(riepilogo), encoding="utf-8")

    print(testo)
    print(f"\n---\nmanda={manda} (già avvisato: {gia} · ha lavorato: {lavorato})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
