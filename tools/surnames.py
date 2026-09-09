#!/usr/bin/env python3
"""How a surname is spelled in this tree is mostly a fact about *where and when*
it was written down, not about which family someone belonged to.

Three things the register conflates, separated here:

  variants  one family, several spellings, profiled by place and date.
            Papic is written Papa in Selce and Papic in Senj; Zubrinic is
            written Zubrinich in Port Pirie. The spelling is a postmark.

  crossed   a name the tree itself cannot assign to one family - "Papic or
            Perpic". Real uncertainty, and rare. These people have no page of
            their own but surface in the relation lists on pages that do.

  unnamed   a person carrying no usable surname at all. Almost all are women,
            entered under a Christian name because that is all the register
            gave. Seven of them are direct ancestors.

Slash-joined names (Joannes / Juan / Ivan) are deliberately NOT counted as
uncertainty: that is one name in Latin, Spanish and Croatian, and given_names.py
already folds it.
"""
import json, re, collections, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ancestry import fold                      # one fold, shared with the site
from build_site_data import JUNK               # the same sorting-bucket filter
import gedcom

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "site" / "src" / "data"

# Prpic and Perpic are one family on the site; group them that way here too.
ALIAS = {"perpic": "prpic"}
def key(s): return ALIAS.get(fold(s), fold(s))

published = list({p["id"]: p for p in
                  json.load(open(DATA / "people.json", encoding="utf-8")) +
                  json.load(open(DATA / "ancestors.json", encoding="utf-8"))}.values())
anc = {a["id"]: (a.get("ahnentafel") or a.get("ahn"))
       for a in json.load(open(DATA / "ancestors.json", encoding="utf-8"))}

def village(p):
    s = p.get("bornPlace") or p.get("baptisedPlace") or p.get("diedPlace") or ""
    return re.sub(r"\s*\d+\s*$", "", s.split(",")[0]).strip().strip('"')

# ---- variants -------------------------------------------------------------
groups = collections.defaultdict(list)
for p in published:
    if (p.get("surname") or "").strip():
        groups[key(p["surname"])].append(p)

variants = []
for k, members in groups.items():
    spellings = collections.Counter((m.get("surname") or "").strip() for m in members)
    if len(spellings) < 2:
        continue
    forms = []
    for sp, n in spellings.most_common():
        grp = [m for m in members if (m.get("surname") or "").strip() == sp]
        yrs = sorted(m["byear"] for m in grp if m.get("byear"))
        vil = collections.Counter(village(m) for m in grp if village(m))
        forms.append({
            "spelling": sp, "n": n,
            "from": yrs[0] if yrs else None, "to": yrs[-1] if yrs else None,
            "median": yrs[len(yrs) // 2] if yrs else None,
            "places": [{"place": v, "n": c} for v, c in vil.most_common(3)],
        })
    variants.append({"key": k, "n": len(members), "forms": forms})

# ---- crossed: read the GEDCOM, because these people have no page ----------
people_g, fams_g = gedcom.load()
CROSS = re.compile(r"\bor\b|\?", re.I)

# Only people this archive actually shows: the published set plus everyone
# named in one of its relation lists. Without this the sweep drags in the
# other family trees that share the export.
insight = {p["id"] for p in published}
for p in published:
    for grp in (p.get("rel") or {}).values():
        for r in (grp if isinstance(grp, list) else []):
            if isinstance(r, dict) and r.get("id"):
                insight.add(r["id"])

crossed = []
for xref, rec in people_g.items():
    if xref not in insight:
        continue
    sn = (rec.get("surname") or "").strip()
    if not sn or not CROSS.search(sn):
        continue
    parts = [x for x in re.split(r"\bor\b|/", sn) if key(x)]
    if len(set(key(x) for x in parts)) < 2:
        continue
    # Can the tree's own structure settle it? A sibling's surname would be
    # evidence - but only if the household is a real one. Where the parent is a
    # "to be sorted" bucket the siblings were grouped by whoever compiled the
    # tree, not by a register, and grouping them proves nothing.
    sibs, bucket = [], False
    for fid in rec.get("famc") or []:
        fam = fams_g.get(fid) or {}
        for par in (fam.get("husb"), fam.get("wife")):
            if par in people_g and JUNK.search(people_g[par].get("name") or ""):
                bucket = True
        for c in fam.get("chil") or []:
            if c != xref and c in people_g:
                nm = people_g[c].get("name") or ""
                s2 = (people_g[c].get("surname") or "").strip()
                if s2 and not JUNK.search(nm):
                    sibs.append(s2)
    settles = sorted({key(x) for x in sibs if key(x)})
    crossed.append({
        "id": xref, "given": (rec.get("given") or "").strip(), "surname": sn,
        "candidates": sorted({key(x) for x in parts}),
        "siblings": sibs,
        "bucket": bucket,
        "settledBy": None if bucket else (settles[0] if len(settles) == 1 else None),
        "suggests": settles[0] if (bucket and len(settles) == 1) else None,
    })

# ---- unnamed --------------------------------------------------------------
unnamed = []
for p in published:
    sn, gn = (p.get("surname") or "").strip(), (p.get("given") or "").strip()
    if sn and not sn.endswith("?") and sn != "?":
        continue
    spouses = [x.get("name") for x in ((p.get("rel") or {}).get("spouses") or [])
               if isinstance(x, dict) and x.get("name")]
    unnamed.append({"slug": p["slug"], "name": p.get("name"), "given": gn,
                    "surname": sn, "byear": p.get("byear"), "sex": p.get("sex"),
                    "place": village(p), "ahn": anc.get(p["id"]),
                    "spouse": ", ".join(spouses)})

out = {"variants": sorted(variants, key=lambda v: -v["n"]),
       "crossed": sorted(crossed, key=lambda r: r["given"]),
       "unnamed": sorted(unnamed, key=lambda r: (r["ahn"] is None, r["ahn"] or 0))}
(DATA / "surnames.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                    encoding="utf-8")

print(f"{len(out['variants'])} surnames written more than one way")
for v in out["variants"]:
    print(f"  {v['key']:<10} n={v['n']:<4} " + " | ".join(
        f"{f['spelling']} {f['n']}"
        f"{' ' + f['places'][0]['place'] if f['places'] else ''}"
        f"{' med ' + str(f['median']) if f['median'] else ''}" for f in v["forms"]))
print(f"\n{len(out['crossed'])} crossed between two families")
for r in out["crossed"]:
    print(f"  {r['given']} {r['surname']}  sibs={r['siblings'] or '-'}  "
          f"{'BUCKET, suggests ' + str(r['suggests']) if r['bucket'] else ''}"
          f"settled={r['settledBy'] or 'OPEN'}")
print(f"\n{len(out['unnamed'])} without a usable surname, "
      f"{sum(1 for r in out['unnamed'] if r['ahn'])} direct ancestors "
      f"({sum(1 for r in out['unnamed'] if r['sex']=='F')} women)")
