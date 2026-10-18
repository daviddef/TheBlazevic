#!/usr/bin/env python3
"""The names index for the kit's build-time linker (kit/tools/autolink.py), and the living list that goes with it.

    python3 tools/names_index.py              write site/src/data/names-index.json
    python3 tools/names_index.py --check      CI-safe: re-derive from COMMITTED data only and require the committed
                                              file to agree (see "WHAT --check PROVES")
    python3 tools/names_index.py --living     write the living list (outside the repository) the linker is run with
    python3 tools/names_index.py --selftest   plant a namesake, a living namesake and a recent found person

WHY THIS REPLACES tools/whoindex.py AND public/wholink.js (18 October 2026). The browser linker linked the first three
mentions of a name per page, only to /people/, only for the people the tree holds, and only in a browser that ran its
script: 46% of the resolvable mentions on the twelve longest pages were links in the HTML a crawler or a no-script
reader is served. This file hands the same job to the kit's build-time pass, with the three defects of the old generator
fixed (below), and the kit's gate (checklinks.py) holds the number.

WHAT A NAME IS HERE. Two spellings that differ only in accents or capitals are the SAME name (the register search has
always folded them: namefold.py, «folding an accent needs nobody's permission»). So «Ivan Blažević» and «Ivan Blazevic»
are one key, and a key is unique only if exactly one person bears it. The kit's matcher is case-folding but not
accent-folding, so every spelling of a name that the archive's own data writes is listed as an alias.

THREE DEFECTS OF tools/whoindex.py, FIXED
  1. IT KEYED BY LOWER-CASE, NOT BY FOLDED NAME. A man written Ivan Blazevic and another written Ivan Blažević were two
     "unique" names, and the browser (which folds) then linked both spellings to whichever came last. Here they are one
     key with two bearers, so the name is ambiguous.
  2. IT COUNTED ONLY THE TREE'S PEOPLE AS BEARERS. The register finds under /found/ (859 people with a page of their own)
     and the living with a name-only page bore names too: a find called Mathias Žubrinić and a tree man called Mathias
     Žubrinić were two "unique" names. Every person with a page, living or not, is a bearer here.
  3. IT NEVER LINKED A FIND. A person read out of a register, who has a page at /found/<slug>/, is indexed when the
     find is old enough to be certainly dead (no date from 1900 on) and the name is unique.

WHO IS INDEXED (people[]). A person who
  * has a page the public can reach and search engines may index: /people/<slug>/ (people.json, ancestors.json,
    line.json) or /found/<slug>/ (found.json, the rows that carry no ahnentafel number, because those two keep their
    own /people/ page);
  * is deceased: a recorded death or burial, or born before 1900. A person born from 1900 on with no death on record is
    not indexed (the archive's rule calls them dead from 80 years on, and a link is not the place to test that); a find
    with any date from 1900 on (the Australian relatives) is not indexed;
  * is the ONLY bearer of the name, living and held-out people and the finds included;
  * has a name of two words or more. A bare given name is never indexed.
  The living are never indexed, and a name a living person bears is not indexed either: it is left plain.

WHAT IS AMBIGUOUS (ambiguous[]). A name that two or more people with a page bear, every bearer of whom is a dead person
of the tree OR a register find whose NAME FIELD IS A NAME (a clean find: the same test as above, and old enough to be
certainly dead), AND whose bearers are exactly the people listed on one name page, /who/<slug>/ (src/pages/who/[slug].astro:
everyone whose full name has that slug, and under them the clean finds of that name, from src/data/who-finds.json, which
this tool writes). The name is sent to that page. A name that a descriptive find also bears («Marija Borić, wife of ...»),
a living person bears, or a find from 1900 on bears is left plain: 716 of the 861 finds have no clean name field, and the
tool never splits a description into a name (18 October 2026, the linking standard's L2). A name borne only by finds gets
no name page (the page exists for names the tree or the living list holds). The people table's search (/people/?q=) was tried first and rejected: it does not fold accents, so «Ana
Blazevic» finds nobody who is written Blažević, and a name's bearers are rarely all written one way. A name that fails
either test stays plain text.

THE LIVING LIST (--living) is written OUTSIDE the repository, to ../private/blazevic/autolink-living.json (the same place
as the prose gate's feed, and for the same reason). It holds every spelling of the name of everyone the living rule calls
living or holds out, and the /people/ address of each of them that has a page. From the GEDCOM when the machine has it
(tools/livingset.py, the kit's living_rule.py: the one rule); otherwise, in CI, from the committed living.json alone.
In both modes the index is checked against it: the linker refuses to run (exit 2) if an index entry equals a living name.

WHAT --check PROVES, IN CI WHERE THERE IS NO GEDCOM. The committed file can be stricter than the committed data
(a local run also drops names that a living or held-out person, who is in no committed file, bears) but never looser.
--check re-derives the index from committed data only and fails if the committed one lists a name, an alias or an
address the re-derivation does not, or if any address no longer has a page. A hand edit, or a data change committed
without rerunning this tool, is caught; nothing here can be satisfied by a person's name being absent.

Prints counts only, never the name of a living person.
"""
import json
import os
import re
import sys
import unicodedata
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "src", "data")
OUT = os.path.join(DATA, "names-index.json")
WHOF = os.path.join(DATA, "who-finds.json")
PRIVATE = os.path.join(os.path.dirname(ROOT), "private", "blazevic")
LIVING_OUT = os.path.join(PRIVATE, "autolink-living.json")
FEED = os.path.join(PRIVATE, "living-feed.json")

CERTAIN_BEFORE = 1900           # born before this: certainly dead
HARD = {"đ": "d", "Đ": "D", "ð": "d", "Ð": "D", "ł": "l", "Ł": "L", "ø": "o", "Ø": "O",
        "ß": "ss", "æ": "ae", "Æ": "AE", "œ": "oe", "Œ": "OE"}
# The old browser linker mapped æ to a (one character in, one out, so offsets held). Here nothing is sliced, so the fold
# is the honest one: «Mariæ» (the Latin genitive a register writes) is «Mariae», which is not «Maria».


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------------------------------- names
def fold(s):
    """The key of a name: no accents, no capitals, straight apostrophes, single spaces."""
    s = unicodedata.normalize("NFC", s or "")
    s = "".join(HARD.get(c, c) for c in s)
    s = "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.category(c).startswith("M"))
    s = s.replace("’", "'").replace("‘", "'").replace("ʼ", "'").replace("´", "'").replace("‐", "-").replace("‑", "-")
    return " ".join(s.casefold().split())


PARTICLES = {"de", "da", "di", "del", "della", "der", "den", "du", "van", "von", "vom", "ten", "ter", "la", "le", "el", "al",
             "bin", "ben", "af", "zu", "zur", "op", "het", "y", "e", "dos", "das", "do", "st", "mc"}


def usable(form):
    """A form worth linking in running prose. Not one that begins with a surname particle or a lower-case word (a
    person the tree holds as «de Goede» or «van Bengale» is a surname; «Caap de Goede Hoop» is the Cape of Good Hope,
    and the old browser linker linked it), and not one that says the same word twice («Marija Marija»)."""
    w = form.split()
    if len(w) < 2:
        return False
    if w[0][:1].islower() or fold(w[0]) in PARTICLES:
        return False
    return len({fold(x) for x in w}) > 1


def clean(n):
    """Drop the tree's bracketed alternatives, so 'Joannes (John) Zubrinic' offers 'Joannes Zubrinic'."""
    n = re.sub(r"\s*\(.*?\)\s*", " ", n or "")
    return re.sub(r"\s+", " ", n).strip()


def variants(p):
    """Every form of a person's name worth matching in prose (the logic of tools/whoindex.py, unchanged)."""
    out = set()
    full = clean(p.get("name"))
    if full:
        out.add(full)
    given, surname = clean(p.get("given")), clean(p.get("surname"))
    if given and surname:
        surnames = [x.strip().strip('"') for x in re.split(r"\s*/\s*", surname)]
        surnames = [x for x in surnames if len(x) > 2] or [surname]
        givens = [x.strip().strip('"') for x in re.split(r"\s*/\s*", given)]
        for g in list(givens):
            inline = re.findall(r'"([^"]{3,})"', g)
            bare = re.sub(r'\s*"[^"]*"\s*', " ", g).strip()
            if bare and bare != g:
                givens.append(bare)
            givens.extend(inline)
        nick = (p.get("nick") or "").strip().strip('"')
        if len(nick) > 2:
            givens.append(nick)
        for sn in surnames:
            for g in givens:
                if len(g) > 2:
                    out.add(f"{g} {sn}")
    return {o for o in out if len(o) >= 7 and " " in o}


# ---------------------------------------------------------------------------------------------------- people
def recorded_dead(p):
    return bool(p.get("died") or p.get("dyear") or p.get("burial")
                or any(e.get("kind") in ("death", "burial") for e in (p.get("events") or [])))


def certainly_dead(p):
    if recorded_dead(p):
        return True
    b = p.get("byear")
    return bool(b) and b < CERTAIN_BEFORE


def found_year_late(r):
    ys = [int(y) for y in re.findall(r"\b(1[0-9]{3}|20[0-9]{2})\b", " ".join(str(r.get(k) or "") for k in ("date", "relation", "event")))]
    return any(y >= CERTAIN_BEFORE for y in ys)


def plain_found_name(name):
    """A find is indexed under its name only when the name IS a name: a few words, no comma, no digit. Most of the 859
    finds are named by what the register says of them («Ane Kalanj, daughter of Joso Kalanj and Ruze, died aged 17»)."""
    n = clean(name)
    return 2 <= len(n.split()) <= 4 and not re.search(r"[,;:0-9]", n)


def found_claims(name):
    """The names a find BEARS, for the question 'is this name unique?': its own name and every two-to-four-word start of
    it, cut at the first comma. «Maria Belobarbić newborn died Senj May 1852» bears «Maria Belobarbić», because
    that is who the register is talking about, and a tree man called Maria Belobarbić is then not the only one."""
    n = clean(name).split(",")[0].split(" - ")[0].split(" — ")[0]
    w = n.split()
    out = set()
    for k in range(2, min(len(w), 4) + 1):
        out.add(" ".join(w[:k]))
    return out | variants({"name": name})


def committed_bearers():
    """-> list of dicts {kind, slug, url, name, forms, indexable}. kind: person | found | living."""
    byid = {}
    for fname in ("people.json", "ancestors.json", "line.json"):
        for r in load(fname):
            byid.setdefault(r["id"], r)
    out = []
    for r in byid.values():
        if not r.get("slug") or not r.get("name"):
            continue
        out.append({"kind": "person", "slug": r["slug"], "url": "/people/%s/" % r["slug"], "name": r["name"],
                    "forms": variants(r), "indexable": certainly_dead(r)})
    slugs = {o["slug"] for o in out}
    for r in load("found.json")["rows"]:
        if r.get("ahn") or not r.get("slug"):
            continue                                  # published as an ancestor under /people/
        out.append({"kind": "found", "slug": r["slug"], "url": "/found/%s/" % r["slug"], "name": r["name"],
                    "forms": variants({"name": r["name"]}) if plain_found_name(r["name"]) else set(),
                    "claims": found_claims(r["name"]), "indexable": not found_year_late(r),
                    "clean": plain_found_name(r["name"]), "date": r.get("date") or "", "place": r.get("place") or ""})
    for r in load("living.json"):
        out.append({"kind": "living", "slug": r["slug"], "url": "/people/%s/" % r["slug"], "name": r["name"],
                    "forms": variants({"name": r["name"]}), "indexable": False})
    return out


def vocabulary(bearers):
    """fold(word) -> {case-folded spelling: the spelling to print}: every spelling of every word that a name of the
    archive writes. A shouted spelling (a register's capitals) yields to a normally cased one."""
    voc = {}
    for b in bearers:
        for f in b["forms"]:
            for w in f.split():
                d = voc.setdefault(fold(w), {})
                cur = d.get(w.casefold())
                if cur is None or (cur.isupper() and not w.isupper()):
                    d[w.casefold()] = w if not w.isupper() else w.capitalize()
    return voc


def spellings(form, voc, cap=24):
    """Every spelling of `form` that the archive's own names write: each word in each of its spellings."""
    opts = []
    for w in form.split():
        d = dict(voc.get(fold(w), {}))
        d.setdefault(w.casefold(), w)
        opts.append([d[k] for k in sorted(d)])
    total = 1
    for o in opts:
        total *= len(o)
    if total > cap:                       # too many combinations: keep only the words as written, and the folded one
        opts = [[w] for w in form.split()]
    out = [""]
    for o in opts:
        out = [(a + " " + b).strip() for a in out for b in o]
    return set(out)


# ---------------------------------------------------------------------------------------------------- the index
def build(bearers, extra_living_forms=(), unpublished_dead_forms=(), who=None):
    """-> (index dict, stats dict).  extra_living_forms: names of living/held-out people from the GEDCOM (a local run);
    unpublished_dead_forms: names of dead people the tree holds with no page."""
    voc = vocabulary(bearers)
    who = who_pages() if who is None else who
    by_key = {}                                  # fold(form) -> {bearer index}
    for i, b in enumerate(bearers):
        for f in set(b["forms"]) | set(b.get("claims", ())):
            by_key.setdefault(fold(f), set()).add(i)
    living_keys = {fold(f) for f in extra_living_forms}
    outside_keys = {fold(f) for f in unpublished_dead_forms}
    stats = {"people": 0, "aliases": 0, "ambiguous": 0, "ambiguous_aliases": 0, "dropped_living_namesake": 0,
             "dropped_unpublished_namesake": 0, "ambiguous_not_all_tree": 0, "ambiguous_no_page": 0, "unusable": 0, "not_indexable": 0, "short": 0}
    people, ambiguous = [], []
    amb_seen = set()
    for i, b in enumerate(bearers):
        if b["kind"] == "living" or not b["indexable"] or not b["forms"]:
            stats["not_indexable"] += b["kind"] != "living"
            continue
        uniq = []
        for f in sorted(b["forms"], key=lambda x: (-len(x), x)):
            k = fold(f)
            if len(k.split()) < 2:
                stats["short"] += 1
                continue
            if not usable(f):
                stats["unusable"] += 1
                continue
            if by_key[k] != {i}:
                continue
            if k in living_keys:
                stats["dropped_living_namesake"] += 1
                continue
            if k in outside_keys:
                stats["dropped_unpublished_namesake"] += 1
                continue
            uniq.append(f)
        if not uniq:
            continue
        seen, names = set(), []
        for f in uniq:                            # every spelling of every unique form
            for s in sorted(spellings(f, voc), key=lambda x: (-len(x), x)):
                if s.casefold() not in seen:
                    seen.add(s.casefold())
                    names.append(f if s.casefold() == f.casefold() else s)
        # the canonical name is the person's own longest unique form; everything else is an alias
        canon = uniq[0]
        aliases = sorted({n for n in names if n.casefold() != canon.casefold()}, key=lambda x: (-len(x), x))
        people.append({"name": canon, "aliases": aliases, "url": b["url"]})
        stats["people"] += 1
        stats["aliases"] += len(aliases)
    # ambiguous: two or more bearers, all of them dead people of the tree, exactly the people of one /who/ page
    for k, idxs in sorted(by_key.items()):
        if len(idxs) < 2 or len(k.split()) < 2 or k in living_keys:
            continue
        bs = [bearers[j] for j in idxs]
        # every bearer is a dead person of the tree or a clean, old find that writes this very name in its name field
        if any(not (x["kind"] == "person" or (x["kind"] == "found" and x["indexable"] and x["forms"]
                                              and any(fold(f) == k for f in x["forms"]))) for x in bs):
            stats["ambiguous_not_all_tree"] += 1
            continue
        if not usable(next(f for j in idxs for f in sorted(bearers[j]["forms"]) if fold(f) == k)):
            stats["unusable"] += 1
            continue
        pages = {slugify(x["name"]) for x in bs}
        if len(pages) != 1 or who.get(next(iter(pages))) != {x["url"] for x in bs}:
            stats["ambiguous_no_page"] += 1
            continue
        forms = {}
        for j in idxs:
            for f in bearers[j]["forms"]:
                if fold(f) == k:
                    forms.setdefault(f.casefold(), f)
        names = {}
        for f in forms.values():
            for s in spellings(f, voc):
                names.setdefault(s.casefold(), s)
        ordered = sorted(names.values(), key=lambda x: (-len(x), x))
        ambiguous.append({"name": ordered[0], "aliases": ordered[1:], "url": "/who/%s/" % next(iter(pages))})
        stats["ambiguous"] += 1
        stats["ambiguous_aliases"] += len(ordered) - 1
    people.sort(key=lambda r: (r["url"], r["name"]))
    ambiguous.sort(key=lambda r: (fold(r["name"]), r["url"]))
    return {"people": people, "ambiguous": ambiguous}, stats


def slugify(s):
    """The slug of src/pages/who/[slug].astro."""
    s = unicodedata.normalize("NFD", str(s if s is not None else ""))
    s = re.sub(r"[\u0300-\u036f]", "", s)
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


def who_pages():
    """slug -> set of addresses listed on /who/<slug>/: the people of people.json and living.json, as the page does, and
    the clean, old finds of who_finds()."""
    out = {}
    for p in load("people.json") + load("living.json"):
        if p.get("name") and p.get("slug"):
            k = slugify(p["name"])
            if k:
                out.setdefault(k, set()).add("/people/%s/" % p["slug"])
    for k, rows in who_finds().items():
        out.setdefault(k, set()).update("/found/%s/" % r["slug"] for r in rows)
    return out


def who_finds():
    """slug of a name page -> the finds listed under the people of that name: a find with no ahnentafel number (it has a
    /found/ page), whose name field is a name (plain_found_name) and which is certainly dead (no date from 1900 on). Only
    for a name page that exists for another reason (a person of people.json or living.json bears the name): a name borne only
    by finds gets no page. src/data/who-finds.json is this, written by this tool and read by the page."""
    pages = set()
    for p in load("people.json") + load("living.json"):
        if p.get("name") and p.get("slug"):
            k = slugify(p["name"])
            if k:
                pages.add(k)
    out = {}
    for r in load("found.json")["rows"]:
        if r.get("ahn") or not r.get("slug") or not plain_found_name(r["name"]) or found_year_late(r):
            continue
        k = slugify(r["name"])
        if k in pages:
            out.setdefault(k, []).append({"slug": r["slug"], "name": clean(r["name"]), "date": r.get("date") or "",
                                          "place": r.get("place") or ""})
    return {k: sorted(v, key=lambda x: (x["name"], x["slug"])) for k, v in sorted(out.items())}


def dumps(idx):
    return json.dumps(idx, ensure_ascii=False, indent=0, separators=(",", ":")) + "\n"


# ---------------------------------------------------------------------------------------------------- living list
def gedcom_available():
    d = os.path.join(ROOT, "sources")
    return os.path.isdir(d) and any(f.endswith(".ged") for f in os.listdir(d))


def published_ids():
    ids = set()
    for fname in ("people.json", "ancestors.json", "line.json"):
        ids |= {r["id"] for r in load(fname)}
    return ids


def gedcom_names():
    """(living_or_held_forms, unpublished_dead_forms) from the GEDCOM and the kit's rule. An unpublished dead person is
    one the tree holds, the rule calls neither living nor held out, and this archive gives no page."""
    pub = published_ids()
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.join(ROOT, "site", "node_modules", "@daviddef", "archive-kit", "kit", "tools"))
    import gedcom
    import livingnames
    import livingset
    people, families = gedcom.load()
    cls = livingset.classify(people, families)
    living_ids = set(cls["living"]) | set(cls["held"])
    live_forms, dead_forms = [], []
    for i, p in people.items():
        disp = gedcom.display(p)
        if not disp:
            continue
        pseudo = {"name": disp, "given": p.get("given"), "surname": p.get("surname"), "nick": p.get("nick")}
        fs = variants(pseudo) | variants({"name": disp})
        if i in living_ids:
            # the prose gate's own phrases too: the whole recorded name, and first + last
            fs |= set(livingnames.phrases_of(disp))
            live_forms.extend(fs)
        elif i not in pub:
            dead_forms.extend(fs)
    return live_forms, dead_forms


def living_list(bearers, ged):
    """The names (every spelling) and addresses of everyone living or held out. A name a dead person also bears is
    carried too: the linker's own rule 2 then keeps a dead name from being linked INSIDE a longer living name."""
    voc = vocabulary(bearers)
    names, urls = set(), set()
    for b in bearers:
        if b["kind"] == "living":
            urls.add(b["url"])
            for f in b["forms"]:
                names |= spellings(f, voc)
    if ged:
        live_forms, _ = ged
        for f in live_forms:
            names |= spellings(f, voc)
    return {"names": sorted(n for n in names if len(n.split()) >= 2), "urls": sorted(urls)}


def living_conflicts(idx, living):
    """How many index names equal a living name or an address is a living address (counts only)."""
    ln = {fold(n) for n in living["names"]}
    lu = set(living["urls"])
    n = 0
    for r in idx["people"] + idx["ambiguous"]:
        if r["url"] in lu or any(fold(x) in ln for x in [r["name"]] + r.get("aliases", [])):
            n += 1
    return n


# ---------------------------------------------------------------------------------------------------- commands
def public_index():
    bearers = committed_bearers()
    return build(bearers), bearers


def full_index():
    bearers = committed_bearers()
    ged = gedcom_names() if gedcom_available() else None
    if ged:
        published = {fold(f) for b in bearers for f in b["forms"]}
        # a dead tree person with no page of their own who bears a name an indexed person also bears
        outside = [f for f in ged[1] if fold(f) in published]
    else:
        outside = []
    idx, stats = build(bearers, extra_living_forms=(ged[0] if ged else ()), unpublished_dead_forms=outside)
    return idx, stats, bearers, ged


def cmd_write():
    idx, stats, bearers, ged = full_index()
    pub, _ = build(bearers)
    open(OUT, "w", encoding="utf-8").write(dumps(idx))
    wf = who_finds()
    open(WHOF, "w", encoding="utf-8").write(json.dumps(wf, ensure_ascii=False, indent=0, separators=(",", ":")) + "\n")
    print("names  %d name pages list a clean find under the people of that name (%d finds)"
          % (len(wf), sum(len(v) for v in wf.values())))
    print("names  %d people (%d aliases), %d ambiguous names (%d aliases); %s" % (
        stats["people"], stats["aliases"], stats["ambiguous"], stats["ambiguous_aliases"],
        "GEDCOM present: names a living, held-out or unpublished person also bears were dropped (%d, %d)"
        % (stats["dropped_living_namesake"], stats["dropped_unpublished_namesake"]) if ged
        else "no GEDCOM: built from committed data only"))
    print("names  not indexed: %d people with a page but not shown to be dead; ambiguous names left plain: %d with a find or living bearer, %d with no one name page"
          % (stats["not_indexable"], stats["ambiguous_not_all_tree"], stats["ambiguous_no_page"]))
    return 0


def cmd_living(argv):
    idx = json.load(open(OUT, encoding="utf-8"))
    bearers = committed_bearers()
    ged = gedcom_names() if gedcom_available() else None
    lv = living_list(bearers, ged)
    path = LIVING_OUT
    for a in argv:
        if a.startswith("--out="):
            path = a[6:]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(lv, fh, ensure_ascii=False)
    os.chmod(path, 0o600)
    bad = living_conflicts(idx, lv)
    print("living list: %d names, %d addresses (%s); written outside the repository" % (
        len(lv["names"]), len(lv["urls"]), "GEDCOM and the kit's rule" if ged else "committed living.json only: CI mode"))
    if bad:
        print("living list: %d index entr%s equal a living name or address" % (bad, "y" if bad == 1 else "ies"))
        return 2
    return 0


def cmd_check():
    """Committed data only. The committed index may be stricter, never looser."""
    if not os.path.exists(OUT):
        print("names-index  MISSING: run tools/names_index.py")
        return 1
    have = json.load(open(OUT, encoding="utf-8"))
    (want, _), bearers = public_index()

    def table(idx):
        t = {}
        for kind in ("people", "ambiguous"):
            for r in idx[kind]:
                for n in [r["name"]] + list(r.get("aliases", [])):
                    t[(kind, fold(n), n.casefold())] = r["url"]
        return t
    th, tw = table(have), table(want)
    extra = [k for k, u in th.items() if tw.get(k) != u]
    urls = {b["url"] for b in bearers if b["kind"] != "living"}
    gone = sorted({r["url"] for r in have["people"] if r["url"] not in urls})
    living = {b["url"] for b in bearers if b["kind"] == "living"}
    lnames = {fold(f) for b in bearers if b["kind"] == "living" for f in b["forms"]}
    liv = sum(1 for r in have["people"] + have["ambiguous"]
              if r["url"] in living or any(fold(n) in lnames for n in [r["name"]] + r.get("aliases", [])))
    bad = 0
    wf_want = who_finds()
    try:
        wf_have = json.load(open(WHOF, encoding="utf-8"))
    except (OSError, ValueError):
        wf_have = None
    if wf_have != wf_want:
        print("  FAIL  src/data/who-finds.json is not what the committed data derives (run tools/names_index.py)")
        bad = 1
    if not have["people"]:
        print("names-index  EMPTY: a check that examined nothing has not passed")
        return 1
    print("names-index  %d people, %d ambiguous in the committed file; the committed-data re-derivation holds %d, %d"
          % (len(have["people"]), len(have["ambiguous"]), len(want["people"]), len(want["ambiguous"])))
    if extra:
        print("  FAIL  %d name or alias in the committed index is not derivable from the committed data" % len(extra))
        bad = 1
    if gone:
        print("  FAIL  %d address in the committed index has no page" % len(gone))
        bad = 1
    if liv:
        print("  FAIL  %d committed entr%s a living name or address" % (liv, "y is" if liv == 1 else "ies are"))
        bad = 1
    if not bad:
        print("names-index  ok: nothing in it that the committed data does not support; no living name or address; every address is a page")
    return bad


def selftest():
    who = {"zzpero-zzkovic": {"/people/c/", "/people/d/"}, "zzvida-zzlist": {"/people/k/", "/found/l/"},
           "zzjosa-zzclaim": {"/people/m/", "/found/n/"}, "zzmila-zzlate": {"/people/o/", "/found/p/"}}
    bearers = [
        {"kind": "person", "slug": "a", "url": "/people/a/", "name": "Zzivo Zzakan", "forms": variants({"name": "Zzivo Zzakan"}), "indexable": True},
        {"kind": "person", "slug": "b", "url": "/people/b/", "name": "Zzmaria Zzakan", "forms": variants({"name": "Zzmaria Žžakan"}), "indexable": True},
        {"kind": "person", "slug": "c", "url": "/people/c/", "name": "Zzpero Zzkovic", "forms": variants({"name": "Zzpero Zzković"}), "indexable": True},
        {"kind": "person", "slug": "d", "url": "/people/d/", "name": "Zzpero Zzkovic", "forms": variants({"name": "Zzpero Zzkovic"}), "indexable": True},
        {"kind": "found", "slug": "e", "url": "/found/e/", "name": "Zzluka Zzovac", "forms": variants({"name": "Zzluka Zzovac"}), "indexable": True},
        {"kind": "person", "slug": "f", "url": "/people/f/", "name": "Zzluka Zzovac", "forms": variants({"name": "Zzluka Zzovac"}), "indexable": True},
        {"kind": "person", "slug": "g", "url": "/people/g/", "name": "Zzana Zzlive", "forms": variants({"name": "Zzana Zzlive"}), "indexable": True},
        {"kind": "living", "slug": "h", "url": "/people/h/", "name": "Zzana Zzlive", "forms": variants({"name": "Zzana Zzlive"}), "indexable": False},
        {"kind": "found", "slug": "i", "url": "/found/i/", "name": "Zzdora Zzrecent", "forms": variants({"name": "Zzdora Zzrecent"}), "indexable": False},
        {"kind": "person", "slug": "j", "url": "/people/j/", "name": "Zzbara Zzunique", "forms": variants({"name": "Zzbara Zzunique"}), "indexable": True},
        # a tree person and a CLEAN find of one name, both dead, on one name page: ambiguous, sent to the page
        {"kind": "person", "slug": "k", "url": "/people/k/", "name": "Zzvida Zzlist", "forms": variants({"name": "Zzvida Zzlist"}), "indexable": True},
        {"kind": "found", "slug": "l", "url": "/found/l/", "name": "Zzvida Zzlist", "forms": variants({"name": "Zzvida Zzlist"}),
         "claims": found_claims("Zzvida Zzlist"), "indexable": True},
        # the same, plus a DESCRIPTIVE find that bears the name («Zzjosa Zzclaim, wife of ...»): left plain, nothing is guessed
        {"kind": "person", "slug": "m", "url": "/people/m/", "name": "Zzjosa Zzclaim", "forms": variants({"name": "Zzjosa Zzclaim"}), "indexable": True},
        {"kind": "found", "slug": "n", "url": "/found/n/", "name": "Zzjosa Zzclaim", "forms": variants({"name": "Zzjosa Zzclaim"}),
         "claims": found_claims("Zzjosa Zzclaim"), "indexable": True},
        {"kind": "found", "slug": "q", "url": "/found/q/", "name": "Zzjosa Zzclaim, wife of Zzpero, died aged 40", "forms": set(),
         "claims": found_claims("Zzjosa Zzclaim, wife of Zzpero, died aged 40"), "indexable": True},
        # a find from 1900 on bears the name: the name stays plain (the living rule)
        {"kind": "person", "slug": "o", "url": "/people/o/", "name": "Zzmila Zzlate", "forms": variants({"name": "Zzmila Zzlate"}), "indexable": True},
        {"kind": "found", "slug": "p", "url": "/found/p/", "name": "Zzmila Zzlate", "forms": variants({"name": "Zzmila Zzlate"}),
         "claims": found_claims("Zzmila Zzlate"), "indexable": False},
    ]
    idx, st = build(bearers, who=who)
    names = {r["url"]: r for r in idx["people"]}
    amb = {fold(r["name"]) for r in idx["ambiguous"]}
    checks = [
        ("a unique name is indexed", "/people/j/" in names),
        ("the accented spelling is an alias of its one bearer", "/people/a/" in names),
        ("two spellings of one name, two bearers: ambiguous, sent to the one name page", "zzpero zzkovic" in amb and idx["ambiguous"][0]["url"] == "/who/zzpero-zzkovic/" and "/people/c/" not in names and "/people/d/" not in names),
        ("a find and a tree man of one name: neither is unique", "/people/f/" not in names and "/found/e/" not in names),
        ("a tree person and a clean old find of one name: ambiguous, sent to the one name page that lists both",
         "zzvida zzlist" in amb and "/people/k/" not in names and "/found/l/" not in names),
        ("a descriptive find that bears the name keeps it plain", "zzjosa zzclaim" not in amb and "/people/m/" not in names),
        ("a find from 1900 on keeps the name plain", "zzmila zzlate" not in amb and "/found/p/" not in names and "/people/o/" not in names),
        ("a name a living person bears is left plain", "/people/g/" not in names and "zzana zzlive" not in amb),
        ("a recent find is not indexed", "/found/i/" not in names),
        ("no living address is indexed", "/people/h/" not in names),
    ]
    idx2, _ = build(bearers, extra_living_forms=["Zzbara Zzunique"], who=who)
    checks.append(("a GEDCOM living namesake removes a name", "/people/j/" not in {r["url"] for r in idx2["people"]}))
    ok = all(c for _, c in checks)
    for label, c in checks:
        print("  %s  %s" % ("ok  " if c else "FAIL", label))
    print("names  selftest " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return cmd_check()
    if "--living" in argv:
        return cmd_living(argv)
    return cmd_write()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
