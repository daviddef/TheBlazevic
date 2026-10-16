#!/usr/bin/env python3
"""Turn sources/senj-baptism-index2.tsv into notes/senj-baptism-index.md.

The tsv is the FamilySearch index (collection 2040054, Croatia Church Books 1516-1994) for the parish of
Senj: one row per record, «ark \\t Principal [Principal] Fact:date@place; ... \\t Other [Role] | ...».
These are INDEX hits, not readings of a filmed page: the indexer's transcription of the entry, with the
parents the entry names. Nothing here has been checked against the image, and the note says so.
"""
import collections, os, re, sys, unicodedata
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources", "senj-baptism-index2.tsv")
OUT = os.path.join(ROOT, "notes", "senj-baptism-index.md")

FAMS = [  # slug, label, surname stems (folded, -ich -> -ic)
    ("blazevic", "Blažević", ["blazevic", "blasevic"]),
    ("zubrinic", "Žubrinić", ["zubrinic", "xubrinic", "zubranic", "zubrenic"]),
    ("kalanj", "Kalanj", ["kalanj", "calanic", "kalanich"]),
    ("boras", "Boras", ["boras", "borach"]),
    ("pavelic", "Pavelić", ["pavelic"]),
    ("tomljanovic", "Tomljanović", ["tomljan", "tomljen", "tomjan", "temljan", "tomlian", "tomljon", "tomlyan", "fomlyan", "gomljan"]),
    ("krmpotic", "Krmpotić", ["krmpotic", "kermpotic", "krampotic", "krempotic", "kerepatic"]),
    ("babic", "Babić", ["babic"]),
    ("spalj", "Špalj", ["spalj", "spolj", "spal"]),
    ("prpic", "Prpić", ["prpic", "perpic", "perpich", "gerpic"]),
    ("papic", "Papić", ["papic", "papa", "papovic"]),
    ("vukelic", "Vukelić", ["vukelic", "wukelic"]),
    ("pilipic", "Pilipić / Pilepich", ["pilipic", "pilepic", "pilipich", "pillepic"]),
    ("sojat", "Šojat", ["sojat", "shojat"]),
    ("kosina", "Kosina", ["kosina"]),
    ("uroda", "Uroda", ["uroda", "urode"]),
]

NOT_THE_NAME = ("spoljar", "spaljselj")  # other surnames that merely start the same way

def fold(s):
    s = unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z]", "", s)
    return re.sub(r"ich", "ic", s)

def parse(line):
    ark, a, *rest = line.rstrip("\n").split("\t")
    others = rest[0] if rest else ""
    m = re.match(r"(.*?) \[(\w+)\] ?(.*)", a)
    name, role, facts = (m.group(1), m.group(2), m.group(3)) if m else (a, "", "")
    fs = []
    for f in [x.strip() for x in facts.split(";") if x.strip()]:
        t, _, rest2 = f.partition(":")
        d, _, p = rest2.partition("@")
        fs.append((t, d.strip(), p.strip()))
    oth = []
    for o in [x.strip() for x in others.split("|") if x.strip()]:
        mm = re.match(r"(.*?) \[(\w+)\]", o)
        if mm: oth.append((mm.group(1).strip(), mm.group(2)))
    return dict(ark=ark, name=name.strip(), facts=fs, others=oth)

def year(d):
    m = re.search(r"(1[6-9]\d\d)", d or "")
    return int(m.group(1)) if m else None

def fam_of(rec):
    names = [rec["name"]] + [n for n, _ in rec["others"]]
    hit = []
    for slug, label, stems in FAMS:
        for n in names:
            f = fold(n.split()[-1]) if n.split() else ""
            f2 = fold(n)
            if any(f.startswith(x) for x in NOT_THE_NAME[:2]): continue
            if any(f.startswith(s) or (len(s) > 4 and s in f2) for s in stems):
                hit.append(slug); break
    return hit

rows = [parse(l) for l in open(SRC, encoding="utf-8") if l.strip()]
by = collections.defaultdict(list)
for r in rows:
    for slug in fam_of(r): by[slug].append(r)

def link(r): return "[index](https://www.familysearch.org/ark:/61903/%s)" % r["ark"]
def parents(r, role):
    return ", ".join(n for n, rl in r["others"] if rl == role) or ""

out = ["# Senj baptisms, from the FamilySearch index (14–16 October 2026)", "",
 "**What this is.** The index of *Croatia, Church Books, 1516–1994* (collection 2040054), paged by surname and "
 "by date, keeping every record whose place is the parish of **Senj**. %d records were saved, and the families "
 "of this archive account for %d of them." % (len(rows), len({r["ark"] for l in by.values() for r in l})),
 "", "**What it is not.** These are the indexer's transcriptions of the entries, with the parents the entry names. "
 "No filmed page has been opened for any of them, so none has a snapshot, and every spelling and date below is "
 "the index's, not a reading. They are the places to open, and a few of them are marked as such below.", "",
 "**Coverage, and a blind spot.** 67 surname spellings were paged, each in 15-year date windows from 1690 to 1900 (a window with more than 5,900 entries is halved). **The paging is not reliable for common surnames:** the index returns its results in an order that shifts between pages, so a window of thousands of entries loses some. A search by a parent's name found five Senj baptisms of Augustinus Babich's children (1826–1840) that the surname sweep never returned. So a family absent from a year here is not shown to be absent; and spellings not tried (a *y*, a *w*, a doubled letter) are not here at all. "
 "**What it cannot say.** The index is not complete: it is a volunteer transcription, and it reaches Senj "
 "baptisms of 1739–1861 in three overlapping collections. A family's absence from a year is not evidence "
 "that it was not baptising.", ""]

def own(r, stems):
    f = fold(r["name"].split()[-1]) if r["name"].split() else ""
    if any(f.startswith(x) for x in NOT_THE_NAME[:2]): return False
    return any(f.startswith(s) for s in stems)

INTRO = os.path.join(ROOT, "sources", "senj-baptism-index-intro.md")
if os.path.exists(INTRO):
    out += [open(INTRO, encoding="utf-8").read().rstrip("\n"), ""]

for slug, label, stems in FAMS:
    rs = by.get(slug, [])
    if not rs: continue
    bap_own, bap_par = [], []
    other = collections.Counter()
    for r in rs:
        bf = [f for f in r["facts"] if f[0] == "Baptism" and re.search(r"^Senj\b", f[2])]
        if bf:
            (bap_own if own(r, stems) else bap_par).append((year(bf[0][1]) or 0, bf[0][1], r))
        else:
            for f in r["facts"]:
                if f[2].startswith("Senj"): other[f[0]] += 1
    bap_own.sort(key=lambda x: (x[0], x[1])); bap_par.sort(key=lambda x: (x[0], x[1]))
    yrs = [x[0] for x in bap_own + bap_par if x[0]]
    out += ["## %s" % label, "",
            "%d baptisms of a child named %s, and %d in which a %s is named as a parent (%s–%s)%s." % (
                len(bap_own), label.split(" /")[0], len(bap_par), label.split(" /")[0],
                min(yrs) if yrs else "?", max(yrs) if yrs else "?",
                "; the index also holds %s at Senj for the name" % ", ".join("%d %s" % (n, k.lower()) for k, n in other.items()) if other else ""), ""]
    for title, lst in (("The child bears the name", bap_own), ("The name is a parent's", bap_par)):
        if not lst: continue
        out += ["**%s**" % title, "", "| baptised | child | father | mother | |", "|---|---|---|---|---|"]
        for y, d, r in lst:
            out.append("| %s | %s | %s | %s | %s |" % (d or y, r["name"], parents(r, "Father"), parents(r, "Mother"), link(r)))
        out.append("")
open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote", OUT, "rows", len(rows), {k: len(v) for k, v in by.items()})
