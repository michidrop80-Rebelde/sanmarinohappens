#!/usr/bin/env python3
"""
controllo-integrita.py — la guardia che controlla che il "cervello" sia tutto intero.

COS'E' (spiegato semplice)
--------------------------
Le skill e gli agenti del progetto si rimandano l'un l'altro a dei file: la skill di
verifica dice «carica references/regole-verifica.md», l'orchestratore dice «usa
.claude/scripts/telegram-giro.py», e cosi' via.

Se uno di quei file sparisce, NON succede niente di rumoroso: l'agente parte lo stesso,
non trova il file, e va avanti a braccio. Il giro sembra riuscito ma ha lavorato senza
le sue regole. E' esattamente cio' che e' successo dopo il `rm -rf` del 25/07/2026:
per due giorni la verifica ha girato senza `regole-verifica.md` e nessuno se n'e' accorto.

Questo script legge tutti i file di istruzioni, tira fuori ogni percorso citato, e
controlla che esista davvero. E' il gemello di `controllo-copertura.py`: quello guarda
che non manchino i POST, questo guarda che non manchino i PEZZI DEL SISTEMA.

USO
---
  python3 scripts/controllo-integrita.py

Esce con codice 1 se manca qualcosa, cosi' si puo' agganciare a un giro automatico.
"""
import re
import sys
from pathlib import Path

PROGETTO = Path(__file__).resolve().parent.parent
TASK_PIANIFICATI = Path.home() / ".claude" / "scheduled-tasks"

# Cartelle di istruzioni da spulciare
SORGENTI = [
    PROGETTO / ".claude" / "skills",
    PROGETTO / ".claude" / "agents",
    TASK_PIANIFICATI,
]

# Percorsi citati che NON sono file veri: sono modelli con dei buchi da riempire
# (`AAAA-MM-GG` = una data), o esempi. Non ha senso cercarli sul disco.
SEGNAPOSTO = re.compile(r"AAAA|MM-GG|AAAAMMGG|<[^>]+>|\{|\*")

# Cosa cerchiamo dentro il testo: percorsi che finiscono con un'estensione nota.
PERCORSO = re.compile(
    r"(?:/Users/michele/Desktop/PROGETTI/San Marino Happens/)?"
    r"((?:\.claude/|dati/|references/|assets/|scripts/|sito/|docs/|queue/|posts/|marketing/)"
    r"[A-Za-z0-9 ._/-]+\.(?:md|py|json|html|sh|js))"
)

# Percorsi noti che vivono FUORI dal progetto o che sono legittimamente assenti.
# Ognuno con il motivo scritto: se un giorno il motivo non vale piu', si toglie da qui.
TOLLERATI = {
    ".claude/secrets/telegram-state.json": "creato al volo dal primo giro con pulsanti",
}


def radice_skill(da_file: Path) -> Path | None:
    """Risale dalla posizione del file fino alla cartella della skill (quella che
    contiene SKILL.md). Serve perche' un file dentro `references/` che cita
    `assets/x.md` intende la cartella della SKILL, non la propria."""
    for cartella in [da_file.parent, *da_file.parents]:
        if (cartella / "SKILL.md").exists():
            return cartella
    return None


def risolvi(citato: str, da_file: Path) -> list[Path]:
    """Un percorso citato dentro una skill puo' essere relativo alla radice del
    progetto (`dati/x.md`), alla cartella della skill (`references/x.md`), oppure
    a un'ALTRA skill: le skill si citano legittimamente fra loro (smh-aggiungi usa
    `assets/evento-template.md` «in smh-ricerca»).
    Restituisce i candidati plausibili: basta che UNO esista."""
    candidati = [PROGETTO / citato]
    if citato.startswith(("references/", "assets/")):
        propria = radice_skill(da_file)
        if propria:
            candidati.append(propria / citato)
        # gli agenti in .claude/agents/ citano le reference della skill omonima
        candidati.append(PROGETTO / ".claude" / "skills" / da_file.stem / citato)
        # rimando a un'altra skill: basta che il file esista in una qualsiasi
        candidati += list((PROGETTO / ".claude" / "skills").glob(f"*/{citato}"))
    return candidati


def main() -> int:
    mancanti: list[tuple[str, str]] = []
    controllati = 0
    file_letti = 0

    for radice in SORGENTI:
        if not radice.exists():
            mancanti.append((str(radice), "CARTELLA INTERA ASSENTE"))
            continue
        for f in sorted(radice.rglob("*.md")):
            file_letti += 1
            testo = f.read_text(errors="ignore")
            for citato in sorted(set(PERCORSO.findall(testo))):
                if SEGNAPOSTO.search(citato):
                    continue  # e' un modello, non un file
                if citato in TOLLERATI:
                    continue
                controllati += 1
                if not any(c.exists() for c in risolvi(citato, f)):
                    dove = f.relative_to(f.parents[len(f.parents) - 4]) if len(f.parents) > 3 else f.name
                    mancanti.append((citato, str(dove)))

    print("Controllo integrita' — i file citati dalle istruzioni esistono davvero?\n")
    print(f"File di istruzioni letti : {file_letti}")
    print(f"Riferimenti controllati  : {controllati}")

    if not mancanti:
        print("\n✅ Tutto a posto: ogni file citato esiste.")
        return 0

    # un file citato da piu' skill compare una volta sola, con l'elenco di chi lo cita
    raggruppati: dict[str, list[str]] = {}
    for citato, dove in mancanti:
        raggruppati.setdefault(citato, []).append(dove)

    print(f"\n❌ {len(raggruppati)} file citati ma ASSENTI dal disco:\n")
    for citato, chi in sorted(raggruppati.items()):
        print(f"   • {citato}")
        for c in sorted(set(chi)):
            print(f"       citato da: {c}")
    print(
        "\nCosa fare: quasi sempre si recuperano dai transcript delle sessioni con\n"
        "  python3 scripts/recupera-da-transcript.py <cartella_temporanea>\n"
        "e poi si copiano al loro posto (con `cp -n`, per non sovrascrivere nulla)."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
