#!/usr/bin/env python3
"""Find a Grave's Zubrinich memorials, matched against this archive's people.

A cemetery index is not a register and this tool says so in its output: a date
here may be the burial rather than the death, and a plot number is Find a
Grave's transcription of a cemetery's own record. What it is very good for is
the thing a parish register cannot do — it puts people in the SAME GROUND.

Shared plot is the whole point. «CC, Lot 26, 1» holds John Zubrinich and two
children who died at eight and at six months. «PRF, Lot 5, 10» holds Thomas Leo
and a woman this archive has never heard of. That is a household, read off a
lot number.

Nothing here is merged into the tree. The output marks each memorial as matched
to a published person or not, and where a matched date disagrees it prints the
disagreement rather than choosing.

Writes site/src/data/graves.json.
"""
import json
import os
import re
import unicodedata
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRCDIR = os.path.join(ROOT, "sources", "findagrave")
DATA = os.path.join(ROOT, "site", "src", "data")

MONTH = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}

# Every harvest file in sources/findagrave/ is read, not just the first one.
# A file may declare, in its header comments:
#     # surname: Zubrinich          what to call it
#     # match: zubrini              the stem to match this archive's people on
#     # stop: zubrinich, zubrinic   surname forms to drop from a given-name match
# and anything it does not declare is taken from the filename stem.


def flat(s):
    return unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()


def toks(name, stop):
    return {t for t in re.findall(r"[a-z]+", flat(name)) if t not in stop and len(t) > 1}


def parse(s):
    """'6 Mar 1860' -> date; '1860' -> (1860, None); '' -> None."""
    s = str(s or "").strip()
    if not s:
        return None
    m = re.match(r"(\d{1,2})\s+([A-Za-z]{3})[a-z]*\s+(\d{4})$", s)
    if m:
        return date(int(m.group(3)), MONTH[m.group(2).lower()], int(m.group(1)))
    m = re.search(r"\b(1[789]\d\d|20\d\d)\b", s)
    return date(int(m.group(1)), 1, 1) if m else None


def year(s):
    d = parse(s)
    return d.year if d else None


def exact(s):
    return bool(re.match(r"\d{1,2}\s+[A-Za-z]{3}", str(s or "").strip()))


def read_file(path):
    """One harvest file -> (meta, rows)."""
    meta, rows = {}, []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("#"):
            m = re.match(r"#\s*(surname|match|stop)\s*:\s*(.+)$", line, re.I)
            if m:
                meta[m.group(1).lower()] = m.group(2).strip()
            continue
        if not line.strip():
            continue
        name, b, d, cem, place, plot = (line.split("|") + [""] * 6)[:6]
        rows.append({"name": name, "born": b, "died": d, "cemetery": cem,
                     "place": place, "plot": plot})
    stem = re.split(r"[-_0-9]", os.path.basename(path))[0]
    meta.setdefault("surname", stem.title())
    meta.setdefault("match", flat(stem)[:7])
    stop = {flat(x) for x in meta.get("stop", meta["surname"]).split(",") if x.strip()}
    stop |= {flat(meta["surname"])}
    for r in rows:
        r["surname"] = meta["surname"]
    return meta, stop, rows


def main():
    people = json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8"))

    files = sorted(f for f in os.listdir(SRCDIR) if f.endswith(".psv"))
    if not files:
        print("no harvest files in sources/findagrave/")
        return 1

    rows, stops, matched_pool = [], {}, {}
    for f in files:
        meta, stop, rs = read_file(os.path.join(SRCDIR, f))
        rows += rs
        stops[meta["surname"]] = stop
        matched_pool[meta["surname"]] = [
            p for p in people if meta["match"] in flat(p.get("name"))]

    # --- match each memorial to a published person -----------------------
    conflicts = []
    for r in rows:
        stop = stops[r["surname"]]
        zub = matched_pool[r["surname"]]
        g, by, dy = toks(r["name"], stop), year(r["born"]), year(r["died"])
        best, bestscore = None, 0
        for p in zub:
            pg = toks(p.get("name"), stop)
            if not (g & pg):
                continue
            pb, pd = p.get("byear"), p.get("dyear")
            # a two-year gap on BOTH dates is a different person
            if by and pb and abs(pb - by) > 2 and dy and pd and abs(pd - dy) > 2:
                continue
            score = len(g & pg) + (2 if by and pb == by else 0) + (2 if dy and pd == dy else 0)
            if score > bestscore:
                best, bestscore = p, score
        if best and bestscore >= 3:
            r["slug"], r["archiveName"] = best["slug"], best["name"]
            r["archiveBorn"], r["archiveDied"] = best.get("born", ""), best.get("died", "")
            gd, ad = parse(r["died"]), parse(best.get("died"))
            if gd and ad and exact(r["died"]) and exact(best.get("died")) and gd != ad:
                conflicts.append({"name": r["name"], "slug": best["slug"],
                                  "grave": r["died"], "tree": best.get("died"),
                                  "days": (gd - ad).days})

    # --- who lies in the same ground -------------------------------------
    plots = {}
    for r in rows:
        if not r["plot"] or not r["cemetery"]:
            continue
        key = f"{r['cemetery']} · {r['plot']}"
        plots.setdefault(key, []).append(r)
    shared = [{"plot": k, "cemetery": v[0]["cemetery"], "place": v[0]["place"],
               "people": sorted(v, key=lambda x: year(x["born"]) or year(x["died"]) or 9999),
               "known": sum(1 for x in v if x.get("slug")),
               "unknown": sum(1 for x in v if not x.get("slug"))}
              for k, v in plots.items() if len(v) > 1]
    shared.sort(key=lambda s: (-s["unknown"], s["plot"]))

    where = {}
    for r in rows:
        c = r["cemetery"] or "unrecorded"
        where[c] = where.get(c, 0) + 1

    surnames = {}
    for r in rows:
        surnames[r["surname"]] = surnames.get(r["surname"], 0) + 1

    out = {
        "source": "Find a Grave, searched 14 September 2026",
        "files": files,
        "surnames": sorted(surnames.items(), key=lambda kv: -kv[1]),
        "n": len(rows),
        "matched": sum(1 for r in rows if r.get("slug")),
        "unmatched": sum(1 for r in rows if not r.get("slug")),
        "cemeteries": sorted(where.items(), key=lambda kv: (-kv[1], kv[0])),
        "shared": shared,
        "conflicts": sorted(conflicts, key=lambda c: -abs(c["days"])),
        "rows": rows,
    }
    json.dump(out, open(os.path.join(DATA, "graves.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"graves.json — {out['n']} memorials from {len(files)} file(s), "
          f"{out['matched']} matched to a person here, "
          f"{len(shared)} shared plots, {len(conflicts)} date disagreements")


if __name__ == "__main__":
    main()
