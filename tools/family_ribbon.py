#!/usr/bin/env python3
"""The family pages' ribbons, their «how our line connects» blocks, and the direct-line file (27 October 2026).

    python3 tools/family_ribbon.py            write site/src/data/direct-line.json, family-lines.json and family-pages.json
    python3 tools/family_ribbon.py --check    rebuild all three in memory and fail if a committed file differs
    python3 tools/family_ribbon.py --report   the same, and print every family's decision

WHAT IT MAKES (the kit's contract: kit/docs/family-ribbon.md)
  direct-line.json   who is on our direct line: the story ribbon's persons, and the spouses its cards mark `spouseDirect`
                     (a mother is an ancestor). Made by the kit's own tools/directline.py from site/src/data/story.json,
                     never typed, so the tint cannot drift from the story.
  family-lines.json  for each family page that has a line to draw: its cards (earliest first), its status, and how our
                     line connects (or why it does not yet). Read by components/FamilyRibbon.astro on the family page.
  family-pages.json  every family page of the Families menu, the ones with no ribbon included: what was drawn and why,
                     and for a page with no ribbon the «not connected» note the page prints instead.

IT READS ONLY COMMITTED JSON (people.json, ancestors.json, line.json, evidence.json, readings.json, lines.json,
story.json, families.json, kosina-descent.json, kosina.json), so CI can run --check without the GEDCOM. Nothing here
is typed by hand; every rule below is written down so a reader can check a card against the data.

THE LINE OF A FAMILY. One chain of generations of the name, the one that leads to our line:
  * its foot is the person of the family nearest our line: one of OUR people who is of the name (Milka is a Papić),
    else one OUR people married or were born to (Antonija Prpić, Milka's mother; Zvonimir Vukelić, Milka's first
    husband), else the ancestor of the name whose child on the way down to us is of another name (Matia Pilipić, the
    mother of Josip Papić);
  * from the foot it goes up through the parent of the same name (the father first), and stops at the first person
    of another name, or with no given name (a tree's «Žubrinić» with nothing else is not a generation);
  * «of the name» is the archive's own `family` (tools/build_site_data.py); a person with none who is cited by
    ahnentafel number in the family's own «(ours)» lane of lines.json is of that family (Juraj Papa Antić Papić, 12).
  * The Kosina are not in the tree above Martin: their line is the archive's own decision, kosina-descent.json
    (the generations numbered 1, 2, 3 ...), to the man who married into the family, Pavao.
  * A family that is not in the line's own tree and has no line of its own in the archive (Babić, Boras ...) gets
    NO ribbon: there is no one line of the name to draw, and none is chosen for it.
A CARD is the person as the archive holds them: the display name (lib/displayName.js, ported below), the years
(none for the living), «from» the birthplace as the tree gives it, graded by the person's evidence state exactly as
the kit grades a lane node (read = documented, scanned or indexed = inferred, anything else = the family's tree);
the spouse is the other parent of the next card, or the person the foot married on the way to us; «at» is where
they died when that is not where they came from. A person on our direct line is drawn as the story draws them.

HOW OUR LINE CONNECTS. One block for each place a person of the family is the spouse or a parent of someone on our
direct line (direct-line.json), and on the Blažević page the line's own links, son to father. The GRADE is
  doc   when one register entry this archive has read names both (readings.json: the same page and entry in both
        people's rows, or a row read off the other's entry, or her marriage entry naming him);
  inf   when the story draws that link dashed (the parent above the couple in a chapter's tree, graded inf);
  lore  otherwise: the family's tree. A story that draws a link solid with no entry read for it is NOT promoted: the
        link is lore, and --report lists it as a disagreement for an author.
The «in the story» link is the chapter that draws the two together. A family with no block says why not, from the
tree: the shortest chain of spouses, parents, children and siblings to our line, three steps or fewer.
"""
import json
import os
import re
import sys
import unicodedata
from collections import deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site", "src", "data")
KIT_TOOLS = os.path.join(ROOT, "site", "node_modules", "@daviddef", "archive-kit", "kit", "tools")
STORY_BASE = "/story/"


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- names and places
STRIP_SQUARE = re.compile(r"\[[^\]]*\]")
STRIP_ROUND = re.compile(r"\([^)]*\)")


def letters(s):
    return "".join(ch for ch in s if unicodedata.category(ch).startswith("L"))


def display_name(raw):
    """site/src/lib/displayName.js displayName(), line for line."""
    recorded = re.sub(r"\s+", " ", str(raw or "")).strip()
    if not recorded:
        return ""
    s = STRIP_ROUND.sub(" ", STRIP_SQUARE.sub(" ", recorded))
    if "/" in s:
        parts = [x.strip() for x in s.split("/") if x.strip()]
        tail = parts[-1].split()
        s = " ".join([parts[0]] + tail[1:])
    m = re.search(r'"([^"]+)"', s)
    called = m.group(1).strip() if m else ""
    if len([t for t in re.split(r"[\s/]+", called) if t]) != 1:
        called = ""
    s = re.sub(r'"[^"]*"', " ", s)
    tokens = s.split()
    if len(tokens) < 2:
        return recorded
    surname = tokens[-1]
    given = [t for t in tokens[:-1] if t != surname]
    if not given:
        return recorded
    first = given[0]
    if len(letters(first)) < 2:
        return recorded
    same = letters(called.lower())[:3] == letters(first.lower())[:3]
    return "%s «%s» %s" % (first, called, surname) if called and not same else "%s %s" % (first, surname)


def tidy_place(raw):
    """The town of a tree place: the first part that is not a house number («Br 114», «Krivi Put 136» -> Krivi Put)."""
    for part in str(raw or "").split(","):
        p = re.sub(r"\s*(?:N°|No\.?|Nr\.?|kbr\.?|br\.?|house)?\s*\d+[a-z]?\s*$", "", re.sub(r"\s+", " ", part).strip(), flags=re.I).strip()
        if not p or re.match(r"^(?:br|kbr|no|n°)\b", p, re.I) or re.search(r"\d", p):
            continue
        return p
    return ""


def years_of(p):
    b, d = p.get("byear"), p.get("dyear")
    if b and d:
        return "%s–%s" % (b, d)
    if b:
        return "b. %s" % b
    if d:
        return "† %s" % d
    return ""


def fold(s):
    s = unicodedata.normalize("NFD", str(s or "").lower())
    return "".join(ch for ch in s if not unicodedata.combining(ch)).replace("đ", "d").strip()


# A family page that is not one of the archive's `family` surnames: its people are found by the name itself
# (the /kosina/ page: «Kosina is not one of this archive's eight published surnames», pages/kosina.astro).
SURNAME_ONLY = {"kosina": "kosina", "kozina": "kosina", "kosinar": "kosina"}

EVIDENCE_GRADE = {"read": "doc", "scanned": "inf", "indexed": "inf"}   # the kit's lane rule (lib/familyribbon.js nodeGrade)


# ---------------------------------------------------------------- the archive
class Archive:
    def __init__(self):
        self.people = load("people.json")
        self.by = {}
        for r in self.people:
            self.by[r["slug"]] = dict(r)
        for extra in ("ancestors.json", "line.json"):
            for a in load(extra):
                self.by.setdefault(a["slug"], {}).update(a)
        self.by_id = {p.get("id"): p for p in self.by.values() if p.get("id")}
        self.evidence = load("evidence.json")
        self.readings = load("readings.json")["bySlug"]
        self.lines = load("lines.json")
        self.story = load("story.json")
        self.families = load("families.json")
        self.family_override = {}
        self.ours_lane = {}
        by_ahn = {p["ahn"]: s for s, p in self.by.items() if p.get("ahn")}
        for st in self.lines.get("sets", []):
            for lane in st.get("lanes", []):
                if "(ours)" not in lane.get("label", ""):
                    continue
                self.ours_lane.setdefault(st["slug"], lane)
                for n in lane.get("nodes", []):
                    for ahn in re.findall(r"ahnentafel (\d+)", n.get("why", "") if isinstance(n, dict) else ""):
                        s = by_ahn.get(int(ahn))
                        if s and not self.by[s].get("family"):
                            self.family_override[s] = st["slug"]

    def fam(self, slug):
        p = self.by.get(slug)
        if not p:
            return None
        f = p.get("family") or self.family_override.get(slug)
        if not f and fold(p.get("surname", "")).split(" ")[0] in SURNAME_ONLY:
            f = SURNAME_ONLY[fold(p.get("surname", "")).split(" ")[0]]
        return f

    def rel(self, slug, kind):
        return [x["slug"] for x in ((self.by.get(slug) or {}).get("rel") or {}).get(kind, []) if x.get("slug") in self.by]

    def name(self, slug, dl_names):
        return dl_names.get(slug) or display_name((self.by.get(slug) or {}).get("name", slug))

    def state(self, slug):
        return (self.evidence.get(slug) or {}).get("state", "tree")

    def sex(self, slug):
        return (self.by.get(slug) or {}).get("sex", "")


# ---------------------------------------------------------------- the direct line (the kit's tool)
def direct_line(story_path):
    sys.path.insert(0, KIT_TOOLS)
    import directline  # noqa: E402  kit/tools/directline.py
    out = directline.from_story(json.load(open(story_path, encoding="utf-8")))
    return dict({"_note": "Made by kit/tools/directline.py from the story's ribbon; do not edit by hand."}, **out)


# ---------------------------------------------------------------- grades of a link
REF = re.compile(r"(?:p\.|Str\.|page)\s*(\d+)[,.]?\s*(?:entry|no\.?|red\.? br\.?)\s*(\d+)", re.I)


def reading_rows(A, slug):
    return [r for r in (A.readings.get(slug) or {}).get("rows", []) if not r.get("indexOnly")]


def shared_entry(A, a, b, married=False):
    """A register entry this archive has READ that names both a and b, or None. Returns (year, words)."""
    ra, rb = reading_rows(A, a), reading_rows(A, b)
    for r in ra:
        if r.get("via") == b:
            return r
    for r in rb:
        if r.get("via") == a:
            return r
    refs_b = {}
    for r in rb:
        for m in REF.finditer(r.get("cite", "")):
            refs_b[(m.group(1), m.group(2), r.get("year"))] = r
    for r in ra:
        for m in REF.finditer(r.get("cite", "")):
            if (m.group(1), m.group(2), r.get("year")) in refs_b:
                return r
    # her marriage entry naming him (the other's surname in a marriage row of hers, or the reverse): a marriage only
    for x, y, rows in (((a, b, ra), (b, a, rb)) if married else ()):
        sur = letters(display_name(A.by[y].get("name", "")).split()[-1].lower())
        for r in rows:
            if r.get("kind") == "marriage" and sur and sur in letters(r.get("cite", "").lower()):
                return r
    return None


def entry_words(r):
    """The register and the entry, as the citation writes them: «Senj marriages (Vjenčani) p. 366 entry 41»."""
    cite = re.sub(r"\s+", " ", r.get("cite", ""))
    m = REF.search(cite)
    if m:
        cuts = [(cite.rfind(sep, 0, m.start()), len(sep)) for sep in (". ", " — ", "; ")]
        start = max([i + n for i, n in cuts if i >= 0] + [0])
        return cite[start:m.end()].strip()
    return cite.split(" — ")[0].split(";")[0].strip().rstrip(".")


def story_tree_grade(story, parent, child):
    """The grade the story gives the link parent -> child: a chapter tree with the parent above and the child in the couple."""
    for ch in story.get("chapters", []):
        rows = (ch.get("tree") or {}).get("rows", [])
        above = [n for r in rows if r.get("kind") == "above" for n in r.get("nodes", [])]
        couple = [n for r in rows if r.get("kind") == "couple" for n in r.get("nodes", [])]
        if any(n.get("person") == parent for n in above) and any(n.get("person") == child for n in couple):
            g = [n.get("grade") for n in above if n.get("person") == parent][0]
            note = (ch.get("tree") or {}).get("note", "")
            return g, ch["id"], note
    return None, None, ""


def story_chapter_of_couple(story, a, b=None):
    """The chapter whose tree draws a in the couple row (and b beside or under them, if given)."""
    for ch in story.get("chapters", []):
        rows = (ch.get("tree") or {}).get("rows", [])
        couple = {n.get("person") for r in rows if r.get("kind") == "couple" for n in r.get("nodes", [])}
        anyone = {n.get("person") for r in rows for n in r.get("nodes", [])}
        if a in couple and (b is None or b in anyone):
            return ch["id"]
    return None


# ---------------------------------------------------------------- the build
class Builder:
    def __init__(self, A, dl):
        self.A, self.dl = A, dl
        self.line = [p["slug"] for p in dl["people"]]
        self.partners = [p["slug"] for p in dl["partners"]]
        self.ours = self.line + self.partners
        self.gen = {p["slug"]: p["generation"] for p in dl["people"] + dl["partners"]}
        self.chapter = {p["slug"]: p["storyChapter"] for p in dl["people"] + dl["partners"]}
        self.dl_names = {p["slug"]: p.get("name", "") for p in dl["people"] + dl["partners"] if p.get("name")}
        self.story_cards = {c["person"]: c for c in A.story["ribbon"]["cards"] if c.get("person")}
        self.story_spouse = {c["spousePerson"]: c for c in A.story["ribbon"]["cards"] if c.get("spousePerson")}
        self.disagreements = []

    def nm(self, slug):
        return self.A.name(slug, self.dl_names)

    # ------------------------------------------------ connections
    def connections_for(self, fid):
        A, out = self.A, []
        for o in self.ours:
            if A.fam(o) == fid:
                continue
            for y in A.rel(o, "spouses"):
                if A.fam(y) == fid and y not in self.line:
                    out.append(self.conn(o, y, "married"))
            for y in A.rel(o, "parents"):
                if A.fam(y) == fid and y not in self.line:
                    out.append(self.conn(o, y, "son of" if A.sex(o) == "M" else "daughter of" if A.sex(o) == "F" else "child of"))
        if fid == self.line_family():
            for o in self.line:
                for y in A.rel(o, "parents"):
                    if y in self.line:
                        out.append(self.conn(o, y, "son of" if A.sex(o) == "M" else "daughter of" if A.sex(o) == "F" else "child of"))
        seen, uniq = set(), []
        for c in out:
            k = (c["ourSlug"], c["theirSlug"], c["relation"])
            if k not in seen:
                seen.add(k)
                uniq.append(c)
        return sorted(uniq, key=lambda c: (c["ourGeneration"], c["ourSlug"], c["theirSlug"]))

    def line_family(self):
        fams = {self.A.fam(s) for s in self.line}
        return fams.pop() if len(fams) == 1 else None

    def conn(self, o, y, relation):
        A = self.A
        r = shared_entry(A, o, y, married=(relation == "married"))
        parent, child = (y, o) if relation != "married" else (None, None)
        sg, sch, snote = story_tree_grade(A.story, parent, child) if parent else (None, None, "")
        if r is not None:
            grade = "doc"
            note = "Named together in %s (%s)." % (entry_words(r), r.get("year"))
        elif sg == "inf":
            grade = "inf"
            note = snote.split(". ")[0].rstrip(".") + "."
        else:
            grade = "lore"
            note = ("From the family's tree; no register entry naming both has been read here."
                    if relation == "married" else
                    "From the family's tree; no register entry naming the parent has been read here.")
            if sg == "doc":
                self.disagreements.append("%s %s %s: the story draws the link solid, and no entry this archive has read names both" % (o, relation, y))
        # the chapter that draws the two together
        if relation == "married":
            ch = story_chapter_of_couple(A.story, o, y) or self.chapter[o]
        elif sch:
            ch = sch
        elif y in self.gen:
            ch = story_chapter_of_couple(A.story, y, o) or self.chapter[y]
        else:
            ch = self.chapter[o]
        c = {"ourSlug": o, "ourGeneration": self.gen[o], "ourName": self.nm(o), "theirSlug": y, "theirName": self.nm(y),
             "relation": relation, "grade": grade, "storyHref": "%s#%s" % (STORY_BASE, ch), "note": note}
        origin = self.origin(y)[0]
        if origin:
            c["theirOrigin"] = "of %s" % origin
        return c

    # ------------------------------------------------ the line of a family
    def origin(self, slug):
        """(town, grade) for a card's «from»"""
        A = self.A
        sc = self.story_cards.get(slug)
        if sc:
            return sc.get("origin", ""), sc.get("originGrade", "lore")
        town = tidy_place(A.by[slug].get("bornPlace", ""))
        if not town and slug in self.story_spouse:
            town = re.sub(r"^of\s+", "", self.story_spouse[slug].get("spouseOrigin", ""))
            town = "" if town == "place not known" else town
        return town, EVIDENCE_GRADE.get(A.state(slug), "lore")

    def foot(self, fid):
        """(slug, how far from our line, the path down to our line) of the person of the family nearest it, or None."""
        A = self.A
        cands = []
        for o in self.ours:
            if A.fam(o) == fid:
                kids_ours = [c for c in A.rel(o, "children") if c in self.ours and A.fam(c) == fid]
                if not kids_ours:
                    cands.append((0, o, [o]))
        for o in self.ours:
            for y in A.rel(o, "spouses") + A.rel(o, "parents"):
                if A.fam(y) == fid and y not in self.ours:
                    cands.append((1, y, [y, o]))
        # ancestors of our people, of the name, whose child on the way down is of another name
        for o in self.ours:
            q, seen = deque([(o, [o])]), {o}
            while q:
                s, path = q.popleft()
                for par in A.rel(s, "parents"):
                    if par in seen:
                        continue
                    seen.add(par)
                    np = [par] + path
                    if A.fam(par) == fid and A.fam(s) != fid and par not in self.ours:
                        cands.append((len(np) - 1, par, np))
                    q.append((par, np))
        if not cands:
            return None
        cands.sort(key=lambda c: (c[0], -len(self.chain_up(c[1], fid)), c[1]))
        return cands[0]

    def chain_up(self, slug, fid):
        A, chain, s = self.A, [slug], slug
        while True:
            pars = [p for p in A.rel(s, "parents") if A.fam(p) == fid and p not in chain]
            pars.sort(key=lambda p: (A.sex(p) != "M", p))
            if not pars:
                break
            p = pars[0]
            if not letters((A.by[p].get("given") or "")):
                break
            chain.append(p)
            s = p
        return list(reversed(chain))

    def card(self, slug, spouse_slug=None):
        A = self.A
        p = A.by[slug]
        sc = self.story_cards.get(slug)
        if sc:
            c = {k: sc.get(k, "") for k in ("name", "years", "origin", "originGrade", "spouse", "spouseOrigin", "atPlace", "atYear")}
            c["living"] = bool(sc.get("living"))
            c["person"] = slug
            if sc.get("spousePerson"):
                c["spousePerson"] = sc["spousePerson"]
            if sc.get("title"):
                c["title"] = sc["title"]
            return c
        town, grade = self.origin(slug)
        c = {"name": self.nm(slug), "years": years_of(p), "origin": town, "originGrade": grade,
             "spouse": "", "spouseOrigin": "", "atPlace": "", "atYear": "", "living": False, "person": slug}
        died = tidy_place(p.get("diedPlace", ""))
        if died and died != town and p.get("dyear"):
            c["atPlace"], c["atYear"] = died, str(p["dyear"])
        if spouse_slug == "":
            c["spouse"] = "spouse not named in the records"
        elif spouse_slug:
            c["spouse"] = self.nm(spouse_slug)
            st, _ = self.origin(spouse_slug)
            c["spouseOrigin"] = "of %s" % st if st else "place not known"
            c["spousePerson"] = spouse_slug
        ev = A.state(slug)
        c["title"] = {"read": "A register or certificate has been read for this person",
                      "scanned": "An image is attached to this person that has not been read out",
                      "indexed": "An index names this person; no document read here",
                      "line": "A direct ancestor, with no record of their own read here",
                      "disputed": "This archive has shown something recorded about this person to be wrong",
                      }.get(ev, "The family tree is all there is for this person")
        return c

    def tree_cards(self, fid):
        A = self.A
        f = self.foot(fid)
        if f is None:
            return None, None
        dist, foot, path = f
        chain = self.chain_up(foot, fid)
        cards = []
        for i, s in enumerate(chain):
            if i + 1 < len(chain):
                nxt = chain[i + 1]
                others = [p for p in A.rel(nxt, "parents") if p != s]
                sp = others[0] if others else ""
            else:
                # the foot: the person they married on the way to our line, or the other parent of the child on the way
                if len(path) >= 2 and path[1] in A.rel(s, "spouses"):
                    sp = path[1]
                elif len(path) >= 2:
                    others = [p for p in A.rel(path[1], "parents") if p != s]
                    sp = others[0] if others else ""
                else:
                    sps = A.rel(s, "spouses")
                    sp = sps[0] if sps else None
            cards.append(self.card(s, sp))
        return cards, f

    def kosina_cards(self):
        A = self.A
        D, K = load("kosina-descent.json"), load("kosina.json")
        found = {x.get("slug"): x for k in ("above", "household") for x in K.get(k, []) if x.get("slug")}
        rows = [r for r in D["rows"] if isinstance(r.get("gen"), int)]
        rows.sort(key=lambda r: r["gen"])
        cards = []
        for r in rows:
            if r.get("person"):
                p = A.by_id.get(r["person"])
                if not p:
                    break
                sp = A.by_id.get(r.get("spousePerson") or "")
                c = self.card(p["slug"], sp["slug"] if sp else None)
                if not c["origin"] and "," in r.get("born", ""):
                    c["origin"] = tidy_place(r["born"].split(",", 1)[1])
                cards.append(c)
                if sp and sp["slug"] and any(sp["slug"] in A.rel(s, "siblings") + A.rel(s, "children") + A.rel(s, "spouses") for s in self.ours):
                    break   # the man who married into the family: the line stops where it meets ours
            else:
                fd = found.get(r["found"], {})
                m = re.findall(r"\d{4}", r.get("era", ""))
                years = "–".join(m[:2]) if len(m) >= 2 else ("b. %s" % m[0] if m else "")
                spouse = r.get("spouseName") or (display_name(found.get(r.get("spouseFound"), {}).get("name", "")) if r.get("spouseFound") else "")
                card = {"name": r.get("name") or display_name(fd.get("name", r["found"])).replace('"', ""),
                        "years": years, "origin": tidy_place(r.get("place", "")),
                        "originGrade": "doc" if r.get("fromRegister") else "lore",
                        "spouse": spouse, "spouseOrigin": "place not known" if spouse else "",
                        "atPlace": "", "atYear": "", "living": False,
                        # a person read out of a register has a page of their own under /found/ (FamilyLine.astro links «found:»)
                        "person": "found:%s" % r["found"],
                        "title": "Read out of a parish register; not in the family tree"}
                if r.get("spouseFound"):
                    card["spouseHref"] = "/found/%s/" % r["spouseFound"]
                cards.append(card)
        return cards

    # ------------------------------------------------ why not connected
    def path_to_ours(self, fid, limit=3):
        A = self.A
        start = [s for s in A.by if A.fam(s) == fid]
        dist = {s: (s, None, None) for s in self.ours}
        q = deque(self.ours)
        found = []
        depth = {s: 0 for s in self.ours}
        while q:
            s = q.popleft()
            if depth[s] >= limit:
                continue
            for kind in ("spouses", "parents", "children", "siblings"):
                for t in A.rel(s, kind):
                    if t in depth:
                        continue
                    depth[t] = depth[s] + 1
                    dist[t] = (t, kind, s)   # t is s's <kind>
                    q.append(t)
                    if A.fam(t) == fid:
                        found.append(t)
        if not found:
            return None
        best = min(found, key=lambda t: (depth[t], A.by[t].get("byear") or 9999, t))
        steps, t = [], best
        while dist[t][1] is not None:
            _, kind, s = dist[t]
            steps.append((t, kind, s))
            t = s
        return steps   # from the family's person toward our person

    def path_sentence(self, steps):
        """In plain names (no «called» form), so the build's linker can link each one to its page."""
        A = self.A
        plain = lambda s: re.sub(r"\s*«[^»]*»", "", self.nm(s))

        def what(a, kind, b):
            """a is b's <kind> -> what a is to b"""
            sx = A.sex(a)
            return {"spouses": "the husband of" if sx == "M" else "the wife of" if sx == "F" else "the spouse of",
                    "parents": "the father of" if sx == "M" else "the mother of" if sx == "F" else "a parent of",
                    "children": "a son of" if sx == "M" else "a daughter of" if sx == "F" else "a child of",
                    "siblings": "a brother of" if sx == "M" else "a sister of" if sx == "F" else "a sibling of"}[kind]
        parts = []
        for i, (a, kind, b) in enumerate(steps):
            w = what(a, kind, b)
            if i == 0:
                verb = "married" if kind == "spouses" else "was " + w
                parts.append("%s %s %s" % (plain(a), verb, plain(b)))
            else:
                parts.append("%s %s" % (w, plain(b)))
        return ", ".join(parts) + ", who is on our line."

    def descent_sentence(self, path):
        """path from the foot down to our person: [foot, child, ..., ours]"""
        steps = [(path[i], "parents", path[i + 1]) for i in range(len(path) - 1)]
        return self.path_sentence(steps)

    # ------------------------------------------------ one family
    def family(self, fid, title, page):
        A = self.A
        rec = {"id": fid, "title": title, "page": page}
        conns = self.connections_for(fid)
        if fid == "kosina":
            cards, f = self.kosina_cards(), None
        else:
            cards, f = self.tree_cards(fid)
        lane = A.ours_lane.get(fid)
        ancestral = f is not None and f[0] >= 2 and not conns
        if cards:
            if lane:
                rec["status"] = lane.get("status")
                if lane.get("statusNote"):
                    rec["statusNote"] = lane["statusNote"]
                if lane.get("span"):
                    rec["span"] = lane["span"]
            else:
                grades = [c["originGrade"] for c in cards]
                ndoc = grades.count("doc")
                rec["status"] = "documented" if ndoc == len(cards) else "origin-unknown" if ndoc else "family-lore"
                rec["statusNote"] = ("%d of %d %s read from a register" % (ndoc, len(cards), "generation" if len(cards) == 1 else "generations")
                                     if ndoc else "the family's tree only")
                ys = [int(y) for c in cards if c["originGrade"] == "doc" for y in re.findall(r"\d{4}", c.get("years", ""))]
                if ys:
                    rec["span"] = [min(ys), None]
            rec["cards"] = cards
        why = ""
        if not conns:
            lead = "No %s married or was a parent of anyone on the story's line" % title
            if ancestral:
                why = "%s; the family is further up its tree. %s" % (lead, self.descent_sentence(f[2]))
            else:
                steps = self.path_to_ours(fid)
                if steps:
                    why = "%s. %s" % (lead, self.path_sentence(steps))
        if conns:
            rec["connections"] = conns
        elif cards:
            rec["notConnected"] = {"why": why or "%s, and the family's tree joins none to it in three steps or fewer." % ("No %s married or was a parent of anyone on the story's line" % title)}
        kind = ("ribbon and connections" if cards and conns else "ribbon, not connected" if cards else
                "connections, no ribbon" if conns else "no ribbon, not connected")
        why_no = "" if cards else ("no %s is an ancestor of anyone on our line, and the archive keeps no one line of the name to draw" % title)
        page_rec = {"id": fid, "title": title, "page": page, "drawn": kind, "generations": len(cards or []),
                    "connections": len(conns), "grades": sorted({c["grade"] for c in conns}),
                    "foot": f[1] if f else None, "noRibbonWhy": why_no, "notConnectedWhy": why if not conns else ""}
        return (rec if cards else None), page_rec


FAMILY_ORDER_NOTE = "The families of the menu «The families», in its order: the 25 surname pages and /kosina/."


def build():
    A = Archive()
    dl = direct_line(os.path.join(DATA, "story.json"))
    B = Builder(A, dl)
    fams, pages = [], []
    menu = [(f["slug"], f["label"], "/%s/" % f["slug"]) for f in A.families]
    menu.insert(menu.index(next(m for m in menu if m[0] == "vukelic")), ("kosina", "Kosina", "/kosina/"))
    for fid, title, page in menu:
        rec, prec = B.family(fid, title, page)
        if rec:
            fams.append(rec)
        pages.append(prec)
    fl = {"_note": "Made by tools/family_ribbon.py from the archive's own data (see its header); do not edit by hand.", "families": fams}
    fp = {"_note": "Made by tools/family_ribbon.py: every family page of the menu, what its ribbon draws and why. " + FAMILY_ORDER_NOTE,
          "pages": pages}
    return dl, fl, fp, B


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def main():
    argv = sys.argv[1:]
    dl, fl, fp, B = build()
    outs = {"direct-line.json": dl, "family-lines.json": fl, "family-pages.json": fp}
    if "--check" in argv or "--report" in argv:
        bad = []
        for name, obj in outs.items():
            path = os.path.join(DATA, name)
            have = open(path, encoding="utf-8").read() if os.path.exists(path) else None
            if have != dump(obj):
                bad.append(name)
        if "--report" in argv:
            for p in fp["pages"]:
                print("  %-12s %-26s gens %d  conns %d %s  foot %s" % (p["id"], p["drawn"], p["generations"], p["connections"], ",".join(p["grades"]), p["foot"]))
            for d in B.disagreements:
                print("  DISAGREE  " + d)
        for name in bad:
            print("  STALE  site/src/data/%s is not what tools/family_ribbon.py makes from the data; run it and commit the result" % name)
        if not bad:
            print("ok    family ribbon: direct-line.json, family-lines.json and family-pages.json are what the data makes "
                  "(%d family pages, %d with a ribbon, %d on our line)" % (len(fp["pages"]), len(fl["families"]), len(dl["people"]) + len(dl["partners"])))
        return 1 if bad else 0
    for name, obj in outs.items():
        open(os.path.join(DATA, name), "w", encoding="utf-8").write(dump(obj))
    print("family_ribbon: wrote direct-line.json (%d people, %d partners, %d unlinked), family-lines.json (%d families), family-pages.json (%d pages)"
          % (len(dl["people"]), len(dl["partners"]), len(dl["unlinked"]), len(fl["families"]), len(fp["pages"])))
    for d in B.disagreements:
        print("  note: " + d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
