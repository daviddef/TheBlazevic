#!/usr/bin/env python3
"""Walk the ancestry of the root person out of the GEDCOM and write it down.

Three outputs:
  data/ancestors.tsv    every ancestor found, with the Ahnentafel number that
                        says exactly where they sit (1 = the root person,
                        2 = father, 3 = mother, 2n / 2n+1 upward from there)
  data/blazevic-spine.tsv the male Blazevic line only — the pedigree the family
                        carries, generation by generation
  data/surname-*.tsv    every bearer of a surname of interest in the tree

Ahnentafel is used rather than a home-made numbering because it is the standard
and because it makes a gap obvious: a missing number is a missing ancestor.
"""
import csv, os, sys, collections
from gedcom import load, display, lifespan, born, died, year, ev, classify_living

LIVING = {}


def is_living(p):
    return LIVING.get(p["id"], True)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
ROOT_PERSON = "@I17@"         # Hedviga "Seka" Blazevic (1926-2001), the root of this archive
# Croatian surnames in this tree are spelled many ways, because the records were
# kept in three orthographies over two centuries: Venetian-Italian (where X wrote
# the sound Z, hence Xubrinich), Habsburg-German-Latin (Zubrinich, -ich endings),
# and modern Croatian (Zubrinic, with the hacek). They are one name each, so the
# match is on a folded key rather than on the literal string.
FOLD = str.maketrans({"z": "z", "c": "c", "c": "c", "s": "s", "d": "d",
                      "Z": "z", "C": "c", "C": "c", "S": "s", "D": "d"})


# slug -> the folded keys that belong to that family name
SURNAMES = {
    "blazevic": ["blazevic"],
    "zubrinic": ["zubrinic"],
    "papic":    ["papic"],
    "prpic":    ["prpic", "perpic"],     # Prpic and Perpic are the same name
    "kalanj":   ["kalanj"],
    "vukelic":  ["vukelic"],
    "boras":    ["boras"],
    "sestan":   ["sestan"],
}

# every spelling that belongs to a family -> that family's key
FAMILY_OF = {v: slug for slug, vs in SURNAMES.items() for v in vs}


def _one(tok):
    """Fold a single surname token to its key."""
    t = tok.strip().strip('"').strip(",")
    if t.startswith("x"):                # Venetian X wrote the sound Z
        t = "z" + t[1:]
    if t.endswith("ich"):                # -ich is the Latin/German rendering of -ic
        t = t[:-3] + "ic"
    if t.endswith("ch"):
        t = t[:-2] + "c"
    return t


def fold(name):
    """Reduce a surname to the key its variants share.

    The tree often writes one surname several ways in a single field -
    "Zubrinic / Xubrinich", "Prpic Perpic", "Kalanj Kalain Kallayn". An earlier
    version split on "(" only, so those strings folded to themselves and never
    matched the surname list. That excluded 63 Zubrinici, 21 Perpici and 6
    Kalanji who are the parent, child or spouse of somebody already published -
    among them Elias Ilija Zubrinic and Casparus Zubrinic, who are the subjects
    of two of this archive's own open questions.

    So: a parenthetical is still dropped, because "Papic (Papa)" and
    "Pavelic (Blazevic)" mark a DIFFERENT name - a by-name or an alias, and the
    archive has argued at length about what those mean. But a slash- or
    space-joined string collapses **only when every token folds to the same
    key**, which is what makes it one surname spelled several ways rather than
    two surnames. "Antic Papic", "Smojver Vukic" and "Shambul Maric" are two
    names and stay two names.
    """
    n = name.strip().lower().translate(FOLD)
    n = n.replace("\u017e", "z").replace("\u0107", "c").replace("\u010d", "c")
    n = n.replace("\u0161", "s").replace("\u0111", "d")
    n = n.split("(")[0].strip()          # "Papic (Papa)" -> "Papic"
    toks = [t for t in n.replace("/", " ").split() if t]
    if len(toks) > 1:
        keys = [_one(t) for t in toks]
        fams = {FAMILY_OF.get(k) for k in keys}
        if len(set(keys)) == 1:                       # one spelling, repeated
            return keys[0]
        if len(fams) == 1 and None not in fams:       # Prpic Perpic -> prpic
            return fams.pop()
        # Kalanj Kalain Kallayn: manglings of one name, so the lead token wins -
        # but only when they actually look like each other. Antic Papic shares
        # no prefix, is two real families, and is the whole of question 5; it
        # must never collapse.
        head = keys[0]
        if all(k[:3] == head[:3] for k in keys):
            return head
        return " ".join(keys)
    return _one(n) if toks else n




def ancestors(people, families, start, maxgen=40):
    """Ahnentafel walk. Returns {ahn: person_id} and {person_id: [ahn, ...]}."""
    by_ahn, queue = {}, collections.deque([(1, start)])
    seen_edges = set()
    while queue:
        ahn, pid = queue.popleft()
        if ahn > 2 ** maxgen or pid is None:
            continue
        by_ahn[ahn] = pid
        p = people.get(pid)
        if not p:
            continue
        # the family this person is a child of gives the parents
        for fid in p["famc"]:
            f = families.get(fid)
            if not f:
                continue
            for parent, slot in ((f["husb"], 0), (f["wife"], 1)):
                if not parent or parent not in people:
                    continue
                edge = (ahn, parent)
                if edge in seen_edges:
                    continue
                seen_edges.add(edge)
                queue.append((ahn * 2 + slot, parent))
    return by_ahn


def kindred(people, families, start=ROOT_PERSON, maxgen=40):
    """Everyone related to `start` BY BLOOD: the ancestors, and all of their
    descendants.

    WHY THIS EXISTS, added 21 September 2026. Until today a person was published
    if their SURNAME was one of the eight this archive carries. That is not the
    same question as «are they family», and a reader put a finger on the gap:

        Hedviga's aunt ANKA BLAŽEVIĆ married Pavao KOSINA. Her five children
        are Hedviga's first cousins and carry her blood — and every one of them
        was invisible here, because a daughter's children take their father's
        name and the surname test cannot see them.

    Measured across the whole tree the hole is TWO HUNDRED AND FIFTY-EIGHT
    people, of whom 234 are publishable once the living rule has run: 37
    Pavelići across four spellings, 11 Špalj, 9 Sekula, 7 Kosina, 6 Rivosechi,
    6 Krmpotići. All of them blood.

    A surname is how a family is FILED. Descent is what a family IS, and this
    archive had been publishing the filing.

    NOTE WHAT THIS DOES NOT DO. It returns blood only. A spouse who married in
    is not here unless their own surname is one of the eight -- Pavao Kosina
    himself is not in this set, though all five of his children are. That is the
    correct boundary for a descent test, and the surname list still carries the
    in-laws it always did.
    """
    kin = {start}
    anc = set()
    stack = [start]
    while stack:
        pid = stack.pop()
        for f in (people[pid].get("famc") or []):
            fam = families.get(f, {})
            for role in ("husb", "wife"):
                o = fam.get(role)
                if o in people and o not in anc:
                    anc.add(o)
                    stack.append(o)
    kin |= anc
    stack = list(anc) + [start]
    while stack:
        pid = stack.pop()
        for f in (people[pid].get("fams") or []):
            for c in (families.get(f, {}).get("chil") or []):
                if c in people and c not in kin:
                    kin.add(c)
                    stack.append(c)
    return kin


def gen_of(ahn):
    """Generation number: 1 for the root, 2 for parents, and so on."""
    g = 0
    while ahn >= 2 ** (g + 1):
        g += 1
    return g + 1


def spouse_of(people, families, pid):
    out = []
    for fid in people[pid]["fams"]:
        f = families.get(fid)
        if not f:
            continue
        other = f["wife"] if f["husb"] == pid else f["husb"]
        if other and other in people:
            m = next((e for e in f["events"] if e["kind"] == "marriage"), {})
            out.append((other, m.get("date", ""), m.get("place", "")))
    return out


def occupation(p):
    e = ev(p, "occupation")
    return (e or {}).get("detail") or (e or {}).get("note") or ""


REDACT = True   # never write a living person's details to a committed file


def row_for(people, families, pid, ahn=None):
    p = people[pid]
    if REDACT and is_living(p):
        # The same rule the site build applies, applied here too, because this
        # repository is public and these files are committed to it.
        return {"ahn": ahn or "", "gen": gen_of(ahn) if ahn else "", "id": p["id"],
                "mh": "", "name": "— living, withheld —", "sex": "", "born": "",
                "born_place": "", "died": "", "died_place": "", "cause": "",
                "burial": "", "occupation": "", "spouses": "", "living": "yes",
                "n_notes": "", "sources": ""}
    b, d = born(p), died(p)
    bur = ev(p, "burial") or {}
    sp = spouse_of(people, families, pid)
    return {
        "ahn": ahn or "",
        "gen": gen_of(ahn) if ahn else "",
        "id": p["id"],
        "mh": p["mh"],
        "name": display(p),
        "sex": p["sex"],
        "born": b.get("date", ""),
        "born_place": b.get("place", ""),
        "died": d.get("date", ""),
        "died_place": d.get("place", ""),
        "cause": d.get("cause", ""),
        "burial": bur.get("place", ""),
        "occupation": occupation(p),
        # A living spouse is named nowhere, even on a deceased person's row.
        "spouses": " | ".join(
            ("— living, withheld —" if is_living(people[s]) else display(people[s]))
            + (f' (m. {dt})' if dt and not is_living(people[s]) else "")
            for s, dt, _ in sp),
        "living": "yes" if is_living(p) else "",
        "n_notes": len(p["notes"]),
        "sources": " | ".join(p["sources"][:4]),
    }


FIELDS = ["ahn", "gen", "id", "mh", "name", "sex", "born", "born_place", "died",
          "died_place", "cause", "burial", "occupation", "spouses", "living",
          "n_notes", "sources"]


def write(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"  {len(rows):>5} rows  {os.path.relpath(path, ROOT)}")


def main():
    global LIVING
    people, families = load()
    LIVING = classify_living(people, families)
    print(f"{len(people)} people, {len(families)} families "
          f"({sum(LIVING.values())} judged living)")

    by_ahn = ancestors(people, families, ROOT_PERSON)
    print(f"\n{len(by_ahn)} ancestors of the root person "
          f"(deepest generation {max(gen_of(a) for a in by_ahn)})")

    rows = [row_for(people, families, pid, ahn)
            for ahn, pid in sorted(by_ahn.items())]
    write(os.path.join(DATA, "ancestors.tsv"), rows)

    # The male Blazevic spine: ahnentafel 1, 2, 4, 8, 16 ... doubling each time.
    spine, ahn = [], 1
    while ahn in by_ahn:
        spine.append(row_for(people, families, by_ahn[ahn], ahn))
        ahn *= 2
    write(os.path.join(DATA, "blazevic-spine.tsv"), spine)

    for slug, keys in SURNAMES.items():
        hits = [p for p in people.values() if fold(p["surname"]) in keys]
        hits.sort(key=lambda p: year(born(p).get("date", "")) or 9999)
        write(os.path.join(DATA, f"surname-{slug}.tsv"),
              [row_for(people, families, p["id"]) for p in hits])

    print("\nThe Blazevic spine, as the tree currently asserts it:")
    for r in spine:
        print(f'  g{r["gen"]:<3} {r["name"]:<44} {r["born"][-4:] or "?":>4}'
              f'–{r["died"][-4:] or "?":<4}  {r["born_place"][:40]}')

    # how many generations have a source attached at all
    with_src = sum(1 for r in spine if r["sources"])
    print(f"\n{with_src} of {len(spine)} spine generations carry a source string "
          f"in the tree; {len(spine) - with_src} carry none.")


if __name__ == "__main__":
    main()


def parents_closure(people, families, seed):
    """Everyone in `seed`, plus their parents, plus THEIR parents, to the root.

    WHY A CLOSURE AND NOT ONE PASS. This exists to close a dangling reference:
    a person page that says «child of X» where X has no page. On 22 September
    2026 the Kosina page showed «Pavao Kosina» unlinked directly above his own
    daughter «Otilija Kosina» linked, because Pavao married in and Otilija is
    Anka Blažević's child — and this archive had read three documents for him
    and one for her.

    One pass over the parents fixes the rows you are looking at and creates the
    same fault one generation further out: 376 new people, each of whom now says
    «child of Y» with Y unpublished. Iterating to a fixed point is the only form
    of the rule that is actually true of every page. It took six rounds and 446
    people, and it terminates because the tree does.

    It is deliberately PARENTS ONLY. Adding siblings or spouses of the newly
    published would walk sideways into the whole 15,643-person tree; a parent is
    the one edge a person page always draws.
    """
    cur = set(seed)
    frontier = set(cur)
    while frontier:
        nxt = set()
        for pid in frontier:
            p = people.get(pid)
            if not p:
                continue
            for fid in p.get("famc", []) or []:
                fam = families.get(fid) or {}
                for role in ("husb", "wife"):
                    v = fam.get(role)
                    for x in (v if isinstance(v, list) else [v] if v else []):
                        if x and x not in cur:
                            nxt.add(x)
        cur |= nxt
        frontier = nxt
    return cur
