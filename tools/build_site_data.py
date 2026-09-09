#!/usr/bin/env python3
"""Turn the parsed GEDCOM into the JSON the site reads.

The living-person rule is applied here, once, at the boundary between the
research data and the published build. Anything that reaches site/src/data is
publishable; anything filtered out here never enters the build at all.
"""
import json, os, re, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gedcom import load, display, born, died, year, ev, classify_living
from ancestry import ancestors, gen_of, fold, SURNAMES, ROOT_PERSON

LIVING = {}
def is_living(p): return LIVING.get(p["id"], True)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "src", "data")

HEDVIGA = "@I17@"

# The families this archive treats as its own, in the order they matter.
FAMILIES = [
    ("blazevic", "Blažević", "the name the archive carries — out of Smokvica Krmpotska"),
    ("zubrinic", "Žubrinić", "Tereza's people of Otočac, written Xubrinich before it was written Žubrinić"),
    ("papic",    "Papić",    "Milka's people of Senj and Selce, porters and innkeepers"),
    ("prpic",    "Prpić",    "Antonija's people of Krivi Put, Bunjevci of the Senj mountain"),
    ("kalanj",   "Kalanj",   "of the Senj hinterland, married into the Blažević line"),
    ("vukelic",  "Vukelić",  "of Lika"),
    ("boras",    "Boras",    "married into the Senj Blaževići"),
    ("sestan",   "Šestan",   "of the Croatian Littoral"),
]

# Placeholder rows the working tree carries that are not people at all: sorting
# buckets, "to be sorted" stubs, and bracketed group labels. These are research
# scaffolding, not ancestors, and publishing them as people would be a lie.
JUNK = re.compile(
    r"(\bto be sort|\bsorting\b|\bfor sorting\b|\bworking\b|\bunknown\b|"
    r"\bfree text\b|\bbrothers?\s*[\[(]|\bsisters?\s*[\[(]|^\s*nn\b|\bplaceholder\b|"
    # "Brothers of Casparus (It Seems)", "Joannes [Brothers of] Zubrinic"
    r"\bbrothers?\s+of\b|\bsisters?\s+of\b|\bit seems\b|"
    # "1800-1830 Birth - Selce Papic (Papa)", "1700 Birth - Selce ..." - a name
    # that opens with a year and a record-word is a bucket, not a person
    r"^\s*\d{4}\s*([-\u2013]\s*\d{4})?\s+(birth|death|marriage|baptism)\b)", re.I)


def junk(p):
    n = display(p)
    return bool(JUNK.search(n)) or n.strip() in ("", "(unnamed)")


# Filled in by main(): id -> slug, for everybody who reaches the build.
SLUGS = {}


def rel(pid, people):
    """A relative, named only if this build publishes them.

    The living-person rule is not just "omit their page": a living person must
    not be named on anybody else's page either. So a relative who is living, or
    who is one of the tree's sorting stubs, is returned as a withheld marker
    rather than a name.
    """
    q = people.get(pid)
    if q is None:
        return None
    if is_living(q):
        return {"withheld": True}
    if junk(q):
        return None
    return {"name": display(q), "slug": SLUGS.get(pid), "id": q["id"],
            "born": year(born(q).get("date", "")),
            "died": year(died(q).get("date", ""))}


def relations(p, people, families):
    """Parents, spouses (with the marriage), siblings and children."""
    out = {"parents": [], "spouses": [], "siblings": [], "children": []}
    for fid in p["famc"]:
        f = families.get(fid)
        if not f:
            continue
        for k in ("husb", "wife"):
            r = rel(f[k], people) if f[k] else None
            if r:
                out["parents"].append(r)
        for c in f["chil"]:
            if c == p["id"]:
                continue
            r = rel(c, people)
            if r:
                out["siblings"].append(r)
    for fid in p["fams"]:
        f = families.get(fid)
        if not f:
            continue
        other = f["wife"] if f["husb"] == p["id"] else f["husb"]
        m = next((e for e in f["events"] if e["kind"] == "marriage"), {})
        r = rel(other, people) if other else None
        if r:
            r = dict(r, marriedDate=m.get("date", ""), marriedPlace=m.get("place", ""))
            out["spouses"].append(r)
        for c in f["chil"]:
            r = rel(c, people)
            if r:
                out["children"].append(r)
    return out


def person(p, ahn=None):
    b, d = born(p), died(p)
    bur, chr_ = ev(p, "burial") or {}, ev(p, "christening") or ev(p, "baptism") or {}
    occs = [e for e in p["events"] if e["kind"] == "occupation"]
    out = {
        "id": p["id"], "slug": slug(p), "name": display(p),
        "given": p["given"], "surname": p["surname"], "nick": p["nick"], "sex": p["sex"],
        "born": b.get("date", ""), "bornPlace": b.get("place", ""),
        "died": d.get("date", ""), "diedPlace": d.get("place", ""),
        "cause": d.get("cause", ""), "burial": bur.get("place", ""),
        "baptised": chr_.get("date", ""), "baptisedPlace": chr_.get("place", ""),
        "occupations": [
            {"what": (o.get("detail") or "").strip(), "where": (o.get("place") or "").strip()}
            for o in occs if (o.get("detail") or o.get("place"))
        ],
        "byear": year(b.get("date", "")), "dyear": year(d.get("date", "")),
        "sources": p["sources"][:6],
        "notes": [clean(n) for n in p["notes"] if clean(n)],
        "events": [
            {"kind": e["kind"], "date": e.get("date", ""), "place": e.get("place", ""),
             "detail": (e.get("detail") or "").strip()[:600], "note": (e.get("note") or "").strip()[:900]}
            for e in p["events"] if e["kind"] not in ("occupation",)
        ],
    }
    out["family"] = next((sl for sl, ks in SURNAMES.items() if fold(p["surname"]) in ks), None)
    if ahn:
        out["ahn"], out["gen"] = ahn, gen_of(ahn)
    return out


TAG = re.compile(r"<[^>]+>")
REF = re.compile(r"\*?\s*Reference:.*?SmartCopy\]:\s*''[^']*''", re.S)
UPD = re.compile(r"\*?\s*Updated from.*?SmartCopy\]:\s*''[^']*''", re.S)


def clean(n):
    """Strip the SmartCopy boilerplate and HTML the tree carries, keep the prose."""
    if not n:
        return ""
    n = REF.sub("", n)
    n = UPD.sub("", n)
    n = n.replace("</p>", "\n").replace("<br>", "\n").replace("<br/>", "\n")
    n = TAG.sub("", n)
    n = n.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<")
    n = re.sub(r"-{3,}", "", n)
    n = re.sub(r"\n{2,}", "\n", n)
    n = re.sub(r"[ \t]{2,}", " ", n)
    return n.strip()


_slugs = {}
def slug(p):
    if p["id"] in _slugs:
        return _slugs[p["id"]]
    base = re.sub(r"[^a-z0-9]+", "-",
                  f'{p["given"]} {p["surname"]}'.lower().translate(
                      str.maketrans("žćčšđáéíóúü", "zccsdaeiouu"))).strip("-") or "unknown"
    s, n = base, 2
    while s in _slugs.values():
        s, n = f"{base}-{n}", n + 1
    _slugs[p["id"]] = s
    return s


# The tree writes the same Croatian place many ways, because the county names
# changed twice in a century and MyHeritage re-geocodes on every edit. Only
# literally-identical parts are merged; nothing distinct is collapsed.
_DROP = {"austria-hungary", "austria", "hrvatska", "yugoslavia", "kingdom of yugoslavia"}
_COUNTY = {"opcina senj": "", "licko-senjska zupanija": "Lika-Senj County",
           "lika-senj county": "Lika-Senj County", "lika": "Lika-Senj County",
           "primorsko-goranska zupanija": "Primorje-Gorski Kotar County",
           "primorje-gorski kotar county": "Primorje-Gorski Kotar County"}
_FOLD = str.maketrans("zccsd", "zccsd")


def _key(x):
    return (x.lower().replace("\u017e", "z").replace("\u0107", "c").replace("\u010d", "c")
             .replace("\u0161", "s").replace("\u0111", "d").strip())


def canonical_place(place):
    """Collapse the tree's spelling variants so that a count counts places.

    Four safe moves: a leading house number is kept but split off, repeated
    parts are dropped wherever they appear (not only adjacent), the vanished
    empires are dropped, and county names are put in one form.
    """
    parts = [x.strip() for x in re.split(r"\s*,\s*", place) if x.strip()]
    out, seen = [], set()
    for x in parts:
        k = _key(x)
        if k in _DROP or not k:
            continue
        k2 = _COUNTY.get(k, None)
        if k2 is not None:
            if not k2:
                continue
            x, k = k2, _key(k2)
        if k in seen:
            continue
        seen.add(k)
        out.append(x)
    # Put the country last, once, if a Croatian county is named at all.
    if "croatia" in seen:
        out = [o for o in out if _key(o) != "croatia"] + ["Croatia"]
    elif any(_key(o) in ("lika-senj county", "primorje-gorski kotar county") for o in out):
        out.append("Croatia")
    return ", ".join(out)


def by_ahn_ids(people, families):
    return list(ancestors(people, families, HEDVIGA).values())


def main():
    global LIVING
    people, families = load()
    LIVING = classify_living(people, families)
    os.makedirs(OUT, exist_ok=True)

    pub = {pid: p for pid, p in people.items() if not is_living(p) and not junk(p)}
    print(f"{len(people)} people; {sum(LIVING.values())} judged living; {len(pub)} publishable")

    # Slugs must exist for everybody the build will emit *before* relationships
    # are written, or a parent link points at a page that has no slug yet.
    keys_all = {k for ks in SURNAMES.values() for k in ks}
    emitted = set(by_ahn_ids(people, families)) | {
        pid for pid, p in pub.items() if fold(p["surname"]) in keys_all}
    for pid in sorted(emitted):
        if pid in pub:
            SLUGS[pid] = slug(pub[pid])

    # ---- the direct line and every ancestor -------------------------------
    by_ahn = ancestors(people, families, HEDVIGA)
    anc = []
    for ahn, pid in sorted(by_ahn.items()):
        p = people[pid]
        if is_living(p) or junk(p):
            continue
        r = person(p, ahn)
        r["rel"] = relations(p, people, families)
        anc.append(r)
    dump("ancestors.json", anc)

    spine, ahn = [], 1
    while ahn in by_ahn:
        p = people[by_ahn[ahn]]
        if not is_living(p):
            spine.append(person(p, ahn))
        ahn *= 2
    dump("line.json", spine)

    # ---- the register ------------------------------------------------------
    keys = keys_all
    reg = []
    for p in pub.values():
        if fold(p["surname"]) not in keys:
            continue
        r = person(p)
        r["rel"] = relations(p, people, families)
        reg.append(r)
    reg.sort(key=lambda r: (r["surname"], r["byear"] or 9999, r["name"]))
    dump("people.json", reg)

    fam = []
    for sl, label, dek in FAMILIES:
        ks = SURNAMES[sl]
        rows = [r for r in reg if fold(r["surname"]) in ks]
        yrs = [r["byear"] for r in rows if r["byear"]]
        pls = collections.Counter(canonical_place(r["bornPlace"]) for r in rows if r["bornPlace"])
        fam.append({"slug": sl, "label": label, "dek": dek, "count": len(rows),
                    "earliest": min(yrs) if yrs else None, "latest": max(yrs) if yrs else None,
                    "places": pls.most_common(8),
                    "spellings": collections.Counter(
                        r["surname"] for r in rows).most_common(12)})
    dump("families.json", fam)

    # ---- places ------------------------------------------------------------
    pc = collections.Counter()
    for r in reg:
        for k in ("bornPlace", "diedPlace"):
            if r[k]:
                pc[canonical_place(r[k])] += 1
    dump("places.json", [{"place": k, "n": v} for k, v in pc.most_common(60)])


def dump(name, obj):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    print(f"  {len(obj):>5}  {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
