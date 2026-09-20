#!/usr/bin/env python3
"""Is anybody in sources/found.psv actually in the tree after all?

found.psv means one thing: «read out of a register, and NOT in the family
tree». That claim has been made wrongly twice.

  · 15 September 2026, the Karlobag wives. A check concluded none of six was
    in the tree. All six were there — as PARENT REFERENCES on their children,
    with no page of their own. Searching the published people is not searching
    the tree.

  · the same day, IVAN DEFRANČESKI. His gravestone was photographed at Senj
    and recorded here as «the surname does not occur once in this tree». It
    occurs on Hedviga Blažević's own marriage: he is her husband, born 1925,
    died 1995, and his slug is null because he is not published. The archive
    had just failed to recognise the grave of the man at the centre of it.

So this looks everywhere a name can hide — published people AND every name in
every rel.parents, rel.spouses, rel.siblings and rel.children list — and tests
each found person two ways:

    name + year      the given name matches and the years are within one
    name + parents   the given name matches and BOTH parents named in the
                     relation text match that candidate's parents

A hit is not proof. It is a person this archive said was not in the tree who
looks very much like somebody in it, and the row needs a human decision. The
check prints them and exits non-zero so a build cannot carry the claim
silently.

Run: python3 tools/foundcheck.py [--quiet]
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
FOUND = os.path.join(ROOT, "sources", "found.psv")

# Rows that have been looked at by a person and settled. A found.psv row is
# listed here with the reason it is NOT the tree person it resembles.
SETTLED = {
    "Maria Magdalena Theresia Žubrinić":
        "resembles Maria Magdalena Žubrinić 1845 and Maria Žubrinić 1847, but "
        "neither has Maria Marković as a mother — the parents are the test and "
        "they fail it",
    "Maria Žubrinić":
        "1858 is a common year for this name; no candidate has Magdalena "
        "Glavinić as a mother",
    "Joanna Perpić":
        "resembles Joanna Kalanj 1875, and the resemblance is a given name and "
        "one year apart. Different surname, and a different father — Joannes "
        "Perpić of Krivi Put against Ivan Kalanj. The parents are the test and "
        "they fail it",
    "Maria Rosaria Antic":
        "ahnentafel 24 has no children published at all, so there is nothing "
        "to match her against; the name-and-year candidates are other families",
    "Matilda Papić":
        "she IS probably in the tree, as Franka or Sulka Papić, both born 1895 "
        "with no death recorded. That is the open question the row exists to "
        "state, not an error",
    "Ivan Defrančeski":
        "IN THE TREE — Hedviga Blažević's husband, born 1925, died 1995, "
        "unpublished. Kept here only until his grave is recorded against him",
}


def flat(s):
    return unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()


def toks(s):
    return {t for t in re.findall(r"[a-z]+", flat(s)) if len(t) > 2}


def year(s):
    m = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", str(s or ""))
    return int(m.group(1)) if m else None


def main():
    quiet = "--quiet" in sys.argv
    people = json.load(open(os.path.join(DATA, "people.json"), encoding="utf-8"))
    if isinstance(people, dict):
        people = people.get("rows", [])
    by = {p.get("slug"): p for p in people}

    # Every name in the tree, wherever it hides.
    cands = []
    for p in people:
        cands.append((p.get("name"), year(p.get("born")), "published", p.get("slug")))
        for kind, lst in (p.get("rel") or {}).items():
            for x in (lst or []):
                if not x.get("name"):
                    continue
                b = x.get("born")
                cands.append((x["name"], b if isinstance(b, int) else year(b),
                              f"{kind} of {p.get('slug')}", x.get("slug")))

    def parents_of(slug):
        p = by.get(slug)
        return [q.get("name") for q in ((p or {}).get("rel", {}) or {}).get("parents") or []]

    rows = []
    for line in open(FOUND, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#") or line.count("|") != 6:
            continue
        rows.append([x.strip() for x in line.split("|")])

    problems = []
    for name, ahn, relation, event, date, place, cite in rows:
        ft, fy = toks(name), year(date)
        given = (re.findall(r"[a-z]+", flat(name)) or [""])[0]
        rel_t = toks(relation)
        hits = []
        for cname, cy, src, cslug in cands:
            ct = toks(cname)
            if given not in ct or not (ft & ct):
                continue
            # A year that is known on both sides and far apart settles it on its
            # own. Without this a Stephanus of 1769 «matches» one of 1858 because
            # his father was also a Michael.
            if fy and cy and abs(cy - fy) > 3:
                continue
            by_year = fy and cy and abs(cy - fy) <= 1
            par = [p for p in parents_of(cslug) if p]
            # Both parents must match, and a parent matches only when BOTH its
            # given name and its surname are in the relation text. One shared
            # «Maria» is not a parent in common.
            def parent_matches(p):
                pt = [t for t in re.findall(r"[a-z]+", flat(p)) if len(t) > 2]
                need = 2 if len(pt) > 1 else 1
                return sum(1 for t in set(pt) if t in rel_t) >= need
            by_parents = bool(par) and all(parent_matches(p) for p in par)
            if by_year or by_parents:
                hits.append((cname, cy, src, cslug, by_parents))
        seen, uniq = set(), []
        for h in hits:
            k = (flat(h[0]), h[1], h[3])
            if k not in seen:
                seen.add(k)
                uniq.append(h)
        if uniq:
            problems.append((name, fy, uniq))

    unsettled = [p for p in problems if p[0] not in SETTLED]
    if not quiet:
        for name, fy, uniq in problems:
            mark = "settled" if name in SETTLED else "UNSETTLED"
            print(f"  {mark:9} {name} ({fy or 'no year'}) — {len(uniq)} candidate(s)")
            for cname, cy, src, cslug, bp in uniq[:4]:
                flagp = " ← PARENTS AGREE" if bp else ""
                print(f"            {cname} {cy or '?'} [{src}]{flagp}")
            if name in SETTLED:
                print(f"            settled: {SETTLED[name]}")
    print(f"found.psv — {len(rows)} people, {len(problems)} resemble somebody in the tree, "
          f"{len(unsettled)} of them unsettled")
    if unsettled:
        print("\nA found.psv row claims somebody is NOT in the tree and they look like "
              "somebody who is.\nDecide, then add the name to SETTLED in this file with "
              "the reason, or take the row out.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
