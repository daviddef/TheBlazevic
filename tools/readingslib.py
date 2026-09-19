#!/usr/bin/env python3
"""What this archive has read, and for whom — including the people a document
names without being about.

WHY THIS FILE EXISTS. sources/readings.psv is «slug|kind|year|where|citation»,
one row per person per document. The archive's own rule, published on
/open-questions/ as the answer to question 9b, is:

    «A baptism counts as a reading for the child AND for both parents,
     because it names all three.»

That rule was never in any tool. It was carried out BY HAND, sixteen times, as
rows of kind «baptism-of-child» — and missed thirty times. On 20 September 2026
the count was: 22 baptisms read, and **30 parents named on them with no row of
their own**.

WHAT IT COST, and it is not abstract. The Karlobag baptism of 12 January 1779
was read on the 10th and recorded as
«caetano-bacchi|baptism|1779|…|"ex Angelo et Catharina Bacchi"» — the entry
names Angelo and Catharina in the citation itself. Ten days later walls.py still
printed, of both of them:

    «This wall is reachable and HAS NOT BEEN OPENED.»
    «This household is put at Karlobag on the strength of their grandchild's
     death — the tree's own words about the tree's own people, NOT A DOCUMENT.»

Both sentences were false, and the document that falsifies them was in the
archive's own file, quoted, with their names in it. The reading was filed under
the child and the parents were left standing outside it.

SO THE RULE LIVES HERE NOW, and both tools that grade a person read it the same
way. A derived credit is marked `derived=True` and carries the child it came
through, because «a register entry names you» and «a register entry is about
you» are not the same claim and this archive does not blur them.

A HAND-WRITTEN ROW ALWAYS WINS. The sixteen «baptism-of-child» rows carry real
citations — «named as mother, «et Oliva Smoyver, vulgò Vukić, Conjugibus»» — and
a derived credit is never allowed to displace one.
"""
import json
import os


def rows(root):
    """Every row of readings.psv, in order, as dicts."""
    out = []
    path = os.path.join(root, "sources", "readings.psv")
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#") or line.count("|") < 4:
            continue
        f = [x.strip() for x in line.split("|")]
        out.append({"slug": f[0], "kind": f[1], "year": f[2],
                    "where": f[3], "cite": f[4]})
    return out


def by_slug(root, data=None):
    """slug -> list of readings, each {kind, year, where, cite, derived, via}.

    Direct rows first, then the derived parent credits for any baptism whose
    parents have no row of their own for that year.
    """
    data = data or os.path.join(root, "site", "src", "data")
    direct = rows(root)
    index = {}
    for r in direct:
        index.setdefault(r["slug"], []).append({**r, "derived": False, "via": None})

    people = {}
    for f in ("people.json", "ancestors.json"):
        p = os.path.join(data, f)
        if not os.path.exists(p):
            continue
        for row in json.load(open(p, encoding="utf-8")):
            people.setdefault(row["slug"], row)

    seen = {(r["slug"], r["year"]) for r in direct}
    for r in direct:
        # Only a BAPTISM names all three. A death names the dead person, and a
        # marriage names the couple's parents only sometimes — the Otočac
        # marriage register of 1859-1872 has no parents column at all, which
        # this archive established the hard way. So the rule is not widened
        # beyond the one document that always carries it.
        if r["kind"] != "baptism":
            continue
        child = people.get(r["slug"])
        if not child:
            continue
        for par in (child.get("rel") or {}).get("parents") or []:
            ps = par.get("slug")
            if not ps or (ps, r["year"]) in seen:
                continue
            seen.add((ps, r["year"]))
            index.setdefault(ps, []).append({
                "slug": ps, "kind": "named-on-a-child-baptism", "year": r["year"],
                "where": r["where"], "cite": r["cite"],
                "derived": True, "via": r["slug"],
            })
    return index


def read_slugs(root, data=None):
    """Everyone a document has been read for, parents included."""
    return set(by_slug(root, data))


if __name__ == "__main__":
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    idx = by_slug(ROOT)
    d = sum(1 for v in idx.values() for x in v if x["derived"])
    print(f"readings.psv — {len(rows(ROOT))} rows read for {len(idx)} people, "
          f"of which {d} are parents named on a child's baptism")
    for s, v in sorted(idx.items()):
        for x in v:
            if x["derived"]:
                print(f"   {x['year']}  {s:<34} via {x['via']}")
