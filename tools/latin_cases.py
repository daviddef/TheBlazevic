#!/usr/bin/env python3
"""Find people whose recorded given name is a Latin case ending, not a name.

A priest writing *baptizavi Josephum* is writing the accusative of Josephus.
Transcribe that literally and the tree acquires a person called "Josephum" who
was never called that in his life. The same happens with genitives lifted out of
*filius Josephi* and ablatives out of *a Georgio*.

This flags the ones it can justify, and says which case and what the nominative
would be. It does not rename anybody: the tree is the authority on what it says,
and this archive's job is to note where what it says is a grammatical artefact.
"""
import json, os, re, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")

# nominative -> the oblique forms that turn up in these registers
OBLIQUE = {
    "Josephus":   {"josephum": "accusative", "josephi": "genitive", "josepho": "ablative"},
    "Georgius":   {"georgium": "accusative", "georgii": "genitive", "georgio": "ablative"},
    "Joannes":    {"joannem": "accusative", "joannis": "genitive", "joanne": "ablative"},
    "Antonius":   {"antonium": "accusative", "antonii": "genitive", "antonio": "ablative"},
    "Nicolaus":   {"nicolaum": "accusative", "nicolai": "genitive", "nicolao": "ablative"},
    "Michael":    {"michaelem": "accusative", "michaelis": "genitive", "michaele": "ablative"},
    "Thomas":     {"thomam": "accusative", "thomae": "genitive"},
    "Mathias":    {"mathiam": "accusative", "mathiae": "genitive"},
    "Matthaeus":  {"mattheam": "accusative", "matthaeum": "accusative"},
    "Maria":      {"mariam": "accusative", "mariae": "genitive"},
    "Anna":       {"annam": "accusative", "annae": "genitive"},
    "Catharina":  {"catharinam": "accusative", "catharinae": "genitive"},
    "Helena":     {"helenam": "accusative"},
    "Lucia":      {"luciam": "accusative", "luciae": "genitive"},
    "Franciscus": {"franciscum": "accusative", "francisci": "genitive"},
    "Francisca":  {"franciscam": "accusative"},
    "Vincentius": {"vincentium": "accusative", "vincentii": "genitive"},
    "Paulus":     {"paulum": "accusative", "pauli": "genitive"},
    "Stephanus":  {"stephanum": "accusative", "stephani": "genitive"},
    "Elias":      {"eliam": "accusative"},
    "Jacobus":    {"jacobum": "accusative", "jacobi": "genitive"},
    "Lucas":      {"lucam": "accusative"},
    "Margarita":  {"margaritam": "accusative"},
    "Simon":      {"simoni": "dative", "simonem": "accusative"},
    "Angelica":   {"angelicam": "accusative"},
}
LOOKUP = {f: (nom, case) for nom, d in OBLIQUE.items() for f, case in d.items()}


def tokens(given):
    return [t.strip('"(),') for t in re.split(r"[\s/]+", (given or "").strip()) if t.strip('"(),')]


def main():
    people = []
    for f in ("people.json", "ancestors.json"):
        people += json.load(open(os.path.join(DATA, f), encoding="utf-8"))
    seen, hits = set(), []
    for p in people:
        if p["id"] in seen:
            continue
        seen.add(p["id"])
        toks = tokens(p.get("given"))
        if not toks:
            continue
        # only the FIRST token is the person's name; later ones are often the
        # tree's own alternate spellings and are not evidence of a bad transcription
        t = toks[0].lower()
        if t in LOOKUP:
            nom, case = LOOKUP[t]
            hits.append({"id": p["id"], "slug": p.get("slug"), "name": p["name"],
                         "given": p.get("given"), "recorded": toks[0],
                         "nominative": nom, "case": case,
                         "ancestor": bool(p.get("ahn")), "ahn": p.get("ahn")})
    hits.sort(key=lambda h: (not h["ancestor"], h["nominative"], h["name"]))
    json.dump(hits, open(os.path.join(DATA, "latincases.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    byc = collections.Counter(h["case"] for h in hits)
    print(f"{len(seen)} people; {len(hits)} recorded under a Latin case ending")
    print("  " + ", ".join(f"{c}: {n}" for c, n in byc.most_common()) + "\n")
    for h in hits:
        star = "  ← DIRECT ANCESTOR" if h["ancestor"] else ""
        print(f'  {h["recorded"]:<12} {h["case"]:<10} → {h["nominative"]:<11} {h["name"][:44]:<44}{star}')


if __name__ == "__main__":
    main()
