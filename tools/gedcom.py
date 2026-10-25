#!/usr/bin/env python3
"""Parse the MyHeritage GEDCOM into a person/family graph the rest of the
archive can walk.

One module, no dependencies. Everything downstream — the ancestry sweep, the
surname clusters, the register — imports `load()` from here so that there is
exactly one place where a GEDCOM line is turned into a fact.
"""
import re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GED = os.path.join(ROOT, "sources", "myheritage-tree4-2026-09-09.ged")

LINE = re.compile(r"^\s*(\d+)\s+(?:(@[^@]+@)\s+)?(_?\w+)(?:\s(.*))?$")

# The event tags we keep, and the label each gets in the output.
EVENTS = {
    "BIRT": "birth", "DEAT": "death", "BURI": "burial", "CHR": "christening",
    "BAPM": "baptism", "MARR": "marriage", "DIV": "divorce", "RESI": "residence",
    "OCCU": "occupation", "EDUC": "education", "IMMI": "immigration",
    "EMIG": "emigration", "NATU": "naturalisation", "CENS": "census",
    "PROB": "probate", "WILL": "will", "RETI": "retirement", "EVEN": "event",
    "MILT": "military", "_MILT": "military", "GRAD": "graduation",
}


class Node:
    """One GEDCOM record, kept as a tree of tags so nothing is silently dropped."""
    __slots__ = ("tag", "xref", "value", "kids")

    def __init__(self, tag, xref=None, value=""):
        self.tag, self.xref, self.value, self.kids = tag, xref, value, []

    def all(self, tag):
        return [k for k in self.kids if k.tag == tag]

    def first(self, tag):
        for k in self.kids:
            if k.tag == tag:
                return k
        return None

    def val(self, tag, default=""):
        k = self.first(tag)
        return k.value if k else default


def parse(path=GED):
    """Read the file into a list of level-0 records."""
    records, stack = [], []
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\r\n")
            m = LINE.match(line)
            if not m:
                continue
            lvl, xref, tag, value = int(m.group(1)), m.group(2), m.group(3), m.group(4) or ""

            # CONC joins with no space, CONT starts a new line. Both belong to
            # the node above them, not to a node of their own.
            if tag in ("CONC", "CONT") and stack:
                parent = stack[-1][1]
                parent.value += ("" if tag == "CONC" else "\n") + value
                continue

            node = Node(tag, xref, value)
            while stack and stack[-1][0] >= lvl:
                stack.pop()
            if not stack:
                records.append(node)
            else:
                stack[-1][1].kids.append(node)
            stack.append((lvl, node))
    return records


def _place(node):
    p = node.val("PLAC")
    return re.sub(r"\s*,\s*", ", ", p).strip(" ,")


def _events(node):
    out = []
    for k in node.kids:
        if k.tag not in EVENTS:
            continue
        date, plac = k.val("DATE"), _place(k)
        # OCCU/EDUC carry their detail in the value, not in a PLAC
        detail = k.value.strip()
        cause = k.val("CAUS")
        note = k.val("NOTE")
        agnc = k.val("AGNC")
        typ = k.val("TYPE")
        if not any([date, plac, detail, cause, note, agnc, typ]):
            continue
        out.append({
            "kind": EVENTS[k.tag], "tag": k.tag, "date": date, "place": plac,
            "detail": detail, "cause": cause, "note": note, "agency": agnc, "type": typ,
        })
    return out


def _notes(node, notes_by_id):
    out = []
    for k in node.all("NOTE"):
        v = k.value.strip()
        if v.startswith("@") and v.endswith("@"):
            out.append(notes_by_id.get(v, ""))
        elif v:
            out.append(v)
    return [n for n in out if n]


def _tsv(name):
    """Rows of data/<name>: `|`-separated, `#` lines and blanks skipped."""
    path = os.path.join(ROOT, "data", name)
    rows = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.strip() and not line.startswith("#"):
                rows.append([x.strip() for x in line.split("|")])
    return rows


def apply_overlays(people):
    """The two things this archive records about the tree WITHOUT editing the GEDCOM (26 October 2026):

    data/tree-corrections.tsv   id|event|tree year|corrected year|source
        A typing slip in a year (a birth after the parents' deaths), corrected in what the archive PUBLISHES. The day and
        month the tree gives are kept; only the year changes. The event's note says it was corrected and where the
        correction is written (the source is the archive's own correction note in corrections.json). A row whose tree
        year no longer matches the tree stops the build: the tree changed, look again. tools/consistency.py reads the
        tree WITHOUT this (load(corrected=False)): /impossible/ reports what the tree says.
    data/death-confirmations.tsv   id|source|grade
        A death the tree records with a place and no date, confirmed by the family. The confirmation is written on the
        death event as its source and grade (and is not a date: none is invented). It is a RECORDED, sourced death, which
        the kit's living rule counts (a bare flag does not free anybody born in the window).
    """
    for pid, event, was, now, source in (r[:5] for r in _tsv("tree-corrections.tsv")):
        p = people.get(pid)
        if p is None:
            raise SystemExit(f"data/tree-corrections.tsv: {pid} is not in the tree")
        if event != "birth":
            raise SystemExit(f"data/tree-corrections.tsv: only a birth year can be corrected here, not {event!r}")
        e = ev(p, "birth")
        if not e or not e.get("date") or year(e["date"]) != int(was):
            raise SystemExit(f"data/tree-corrections.tsv: {pid} no longer has a birth year of {was} in the tree: look again")
        e["date"] = re.sub(r"\b%s\b" % was, now, e["date"])
        e["corrected_from"] = int(was)
        e["note"] = ("Year corrected by this archive; the correction and its evidence are recorded under What changed (/corrections/) "
                     "and What Cannot Be True (/impossible/). " + (e.get("note") or "")).strip()
    for pid, source, grade in (r[:3] for r in _tsv("death-confirmations.tsv")):
        p = people.get(pid)
        if p is None:
            raise SystemExit(f"data/death-confirmations.tsv: {pid} is not in the tree")
        e = ev(p, "death")
        if not e:
            raise SystemExit(f"data/death-confirmations.tsv: {pid} has no death event in the tree")
        if year(e.get("date", "")):
            raise SystemExit(f"data/death-confirmations.tsv: {pid} already has a dated death: take the row out")
        e["note"] = ("Source: %s. Grade: %s." % (source, grade) + " " + (e.get("note") or "")).strip()
        e["confirmed"] = True
    return people


# Events that happen once in a life: two records of one man hold one of each, and the two are combined, not listed twice.
ONCE = ("birth", "death", "burial", "christening", "baptism")
HEDGE = re.compile(r"\b(ABT|BEF|AFT|EST|CAL|BET|FROM|TO|INT|ABOUT|BEFORE|AFTER)\b", re.I)


def _fold_text(s):
    return re.sub(r"\s+", " ", (s or "").strip().casefold())


def _date_parts(d):
    """How many parts of a date are written: '26 MAR 1862' 3, 'MAR 1862' 2, '1862' 1, no year 0. A hedged date is 0."""
    d = (d or "").strip()
    if not d or HEDGE.search(d) or not re.search(r"\b\d{4}\b", d):
        return 0
    return len(d.split())


def _event_empty(e):
    return not any(e.get(k) for k in ("date", "place", "cause", "note", "agency", "type"))


def _merge_event(keep, drop, label, why):
    """Fold the event `drop` into `keep` (two records of one man's birth, or of his death). Returns True when `keep` took
    anything from `drop`. Nothing is picked silently: where both records give a fact and the two do not agree, the build
    stops, and a person decides how both readings are to be printed."""
    took = False
    # the date: a plain date may be made exact by the other record's date of the same year (1862 and 26 MAR 1862)
    a, b = (keep.get("date") or "").strip(), (drop.get("date") or "").strip()
    if b and not a:
        keep["date"], took = b, True
    elif a and b and _fold_text(a) != _fold_text(b):
        fa, fb = _fold_text(a), _fold_text(b)
        if not (_date_parts(a) and _date_parts(b) and year(a) == year(b)
                and (fa.endswith(" " + fb) or fb.endswith(" " + fa) or fa == fb)):
            raise SystemExit(f"data/tree-merges.tsv: {why}: the two records give a different {label} date ({a!r} and {b!r}). "
                             f"Nothing is chosen silently: decide how both readings are printed, then extend apply_merges")
        if _date_parts(b) > _date_parts(a):
            keep["date"], took = b, True
    # the place: equal, or one a leading part of the other, or one empty
    a, b = (keep.get("place") or "").strip(), (drop.get("place") or "").strip()
    if b and not a:
        keep["place"], took = b, True
    elif a and b and _fold_text(a) != _fold_text(b):
        fa, fb = _fold_text(a), _fold_text(b)
        if fa.startswith(fb):
            pass
        elif fb.startswith(fa):
            keep["place"], took = b, True
        else:
            raise SystemExit(f"data/tree-merges.tsv: {why}: the two records give a different {label} place ({a!r} and {b!r})")
    for k in ("cause", "agency", "type", "detail"):
        a, b = (keep.get(k) or "").strip(), (drop.get(k) or "").strip()
        if b and not a:
            keep[k], took = b, True
        elif a and b and a != b and k != "detail":
            raise SystemExit(f"data/tree-merges.tsv: {why}: the two records give a different {label} {k} ({a!r} and {b!r})")
    a, b = (keep.get("note") or "").strip(), (drop.get("note") or "").strip()
    if b and b not in a:
        keep["note"], took = (a + " " + b).strip() if a else b, True
    return took


def apply_merges(people, families):
    """ONE MAN RECORDED TWICE, CONFIRMED BY THE OWNER OF THE TREE (25 October 2026), WITHOUT EDITING THE TREE.

    data/tree-merges.tsv   surviving id|retired id|source|grade
        The two records are one person. The surviving record stays; the retired one leaves the people this archive
        publishes, every family that named it names the survivor (a child listed twice in one family is listed once, so a
        man is no longer his own brother), its facts are folded into the survivor's (an event the survivor lacks is taken;
        an event that is only a flag is filled from the other record; a plain date is made exact by the other record's date
        of the same year; both citations are kept), and its name is kept as a variant (`alt_names`) and in `merged`, which
        the generators print as «also recorded as». Where the two records give a different date, place, cause or sex the
        build STOPS: nothing is chosen silently. The retired page address redirects to the survivor
        (site/src/data/merged.json, astro.config.mjs), and the correction is written on the page What changed.

        Applied after apply_overlays (a corrected year is what the other record is compared with) and before the parent
        links are made. load(corrected=False) is the tree as exported and applies none of it.
    """
    for row in _tsv("tree-merges.tsv"):
        keep, drop, source, grade = (row + ["", "", "", ""])[:4]
        why = f"{keep} <- {drop}"
        for pid in (keep, drop):
            if pid not in people:
                raise SystemExit(f"data/tree-merges.tsv: {pid} is not in the tree")
        if keep == drop:
            raise SystemExit(f"data/tree-merges.tsv: {keep} cannot be merged with itself")
        if not source or not grade:
            raise SystemExit(f"data/tree-merges.tsv: {why}: a merge needs its source and its grade")
        k, d = people[keep], people[drop]
        if k.get("sex") and d.get("sex") and k["sex"] != d["sex"]:
            raise SystemExit(f"data/tree-merges.tsv: {why}: the two records give a different sex")
        # a parent and a child, or two spouses, are not one person
        for f in families.values():
            members = {f["husb"], f["wife"]}
            if keep in members and drop in members:
                raise SystemExit(f"data/tree-merges.tsv: {why}: the two are the two spouses of one family")
            if (keep in members and drop in f["chil"]) or (drop in members and keep in f["chil"]):
                raise SystemExit(f"data/tree-merges.tsv: {why}: one is a parent of the other")
        took = []
        for dev in d["events"]:
            same = [e for e in k["events"] if e["kind"] == dev["kind"]]
            if dev["kind"] in ONCE and same:
                if _merge_event(same[0], dev, dev["kind"], why):
                    took.append(same[0])
            elif not any(e["kind"] == dev["kind"] and e.get("date") == dev.get("date") and e.get("place") == dev.get("place")
                         and e.get("detail") == dev.get("detail") for e in same):
                k["events"].append(dict(dev))
                took.append(k["events"][-1])
        for e in took:
            e["merged"] = True
            tail = "(Folded in from the tree's second record of this man, one person on the tree owner's confirmation: /corrections/.)"
            if tail not in (e.get("note") or ""):
                e["note"] = ((e.get("note") or "") + " " + tail).strip()
        k["sources"] = list(dict.fromkeys(list(k["sources"]) + list(d["sources"])))
        k["cites"] = list(dict.fromkeys(list(k["cites"]) + list(d["cites"])))
        k["notes"] = list(dict.fromkeys(list(k["notes"]) + list(d["notes"])))
        own = display(k)
        alts = [display(d)] + list(d.get("alt_names") or [])
        k["alt_names"] = [n for n in dict.fromkeys(list(k.get("alt_names") or []) + alts) if n and n != own]
        k["merged"] = list(k.get("merged") or []) + [
            {"id": drop, "name": display(d), "given": d["given"], "surname": d["surname"], "source": source, "grade": grade}]
        for f in families.values():
            if f["husb"] == drop:
                f["husb"] = keep
            if f["wife"] == drop:
                f["wife"] = keep
            f["chil"] = list(dict.fromkeys(keep if c == drop else c for c in f["chil"]))
        k["famc"] = list(dict.fromkeys(list(k["famc"]) + list(d["famc"])))
        k["fams"] = list(dict.fromkeys(list(k["fams"]) + list(d["fams"])))
        del people[drop]
    return people


def load(path=GED, corrected=True):
    """Return (people, families) as dicts keyed by GEDCOM xref. `corrected=False` is the tree exactly as it was
    exported (tools/consistency.py: /impossible/ reports what the tree says); see apply_overlays and apply_merges."""
    records = parse(path)

    notes_by_id = {}
    for r in records:
        if r.tag == "NOTE" and r.xref:
            notes_by_id[r.xref] = r.value.strip()

    sources_by_id = {}
    for r in records:
        if r.tag == "SOUR" and r.xref:
            sources_by_id[r.xref] = {
                "title": r.val("TITL"), "abbr": r.val("ABBR"),
                "publication": r.val("PUBL"), "text": r.val("TEXT"),
            }

    people, families = {}, {}

    for r in records:
        if r.tag == "INDI" and r.xref:
            nm = r.first("NAME")
            raw = nm.value if nm else ""
            given = (nm.val("GIVN") if nm else "") or raw.split("/")[0].strip()
            surn = (nm.val("SURN") if nm else "")
            if not surn and "/" in raw:
                surn = raw.split("/")[1]
            nick = (nm.val("NICK") if nm else "")
            # Married-name / alternate NAME records matter for women
            alts = []
            for extra in r.all("NAME")[1:]:
                alts.append(extra.value.replace("/", "").strip())

            srcs = []
            cites = []          # every string a citation carries, for the living rule only
            for s in r.all("SOUR"):
                v = s.value.strip()
                if v.startswith("@"):
                    d = sources_by_id.get(v, {})
                    cites.append(" | ".join(x for x in (
                        d.get("title"), d.get("abbr"), d.get("publication"),
                        (d.get("text") or "")[:300], s.val("PAGE")) if x))
                    t = d.get("title") or d.get("abbr") or ""
                    if s.val("PAGE"):
                        t = (t + " — " + s.val("PAGE")).strip(" —")
                    if t:
                        srcs.append(t)
                elif v:
                    srcs.append(v)
                    cites.append(v)

            people[r.xref] = {
                "id": r.xref,
                "name": raw.replace("/", "").strip() or "(unnamed)",
                "given": given.strip(),
                "surname": surn.strip(),
                "nick": nick.strip(),
                "alt_names": alts,
                "sex": r.val("SEX"),
                "events": _events(r),
                "notes": _notes(r, notes_by_id),
                "sources": srcs,
                "cites": cites,
                "famc": [k.value for k in r.all("FAMC")],   # family as child
                "fams": [k.value for k in r.all("FAMS")],   # family as spouse
                "uid": r.val("_UID"),
                "mh": (r.val("RIN") or r.xref).strip("@I"),
            }

    for r in records:
        if r.tag == "FAM" and r.xref:
            families[r.xref] = {
                "id": r.xref,
                "husb": r.val("HUSB"),
                "wife": r.val("WIFE"),
                "chil": [k.value for k in r.all("CHIL")],
                "events": _events(r),
                "notes": _notes(r, notes_by_id),
            }

    if corrected:
        apply_overlays(people)
        apply_merges(people, families)

    # back-links, so a person knows their parents without a family lookup
    for f in families.values():
        for c in f["chil"]:
            if c in people:
                people[c].setdefault("parents", [])
                for p in (f["husb"], f["wife"]):
                    if p and p in people and p not in people[c]["parents"]:
                        people[c]["parents"].append(p)
    for p in people.values():
        p.setdefault("parents", [])

    return people, families


# ---- convenience helpers used by the other tools -------------------------

def year(datestr):
    m = re.search(r"\b(\d{4})\b", datestr or "")
    return int(m.group(1)) if m else None


def ev(person, kind):
    for e in person["events"]:
        if e["kind"] == kind:
            return e
    return None


def born(person):
    e = ev(person, "birth") or ev(person, "christening") or ev(person, "baptism")
    return e or {}


def died(person):
    e = ev(person, "death") or ev(person, "burial")
    return e or {}


def lifespan(person):
    b, d = year(born(person).get("date", "")), year(died(person).get("date", ""))
    if b and d:
        return f"{b}–{d}"
    if b:
        return f"b. {b}"
    if d:
        return f"d. {d}"
    return ""


def is_living(person, today_year=2026):
    """Per-person fallback. Prefer classify_living(), which uses the whole graph."""
    if died(person).get("date"):
        return False
    b = year(born(person).get("date", ""))
    if b is not None and today_year - b > 100:
        return False
    for e in person["events"]:
        y = year(e.get("date", ""))
        if y is not None and today_year - y > 100:
            return False
    return True


MIN_PARENT_AGE = 14      # nobody is a parent younger than this
MAX_PARENT_AGE = 60      # nor older than this


def classify_living(people, families, today_year=2026, horizon=100):
    """Decide who is living, using the family graph and not just their own dates.

    A tree of this size is full of people with no dates at all — medieval
    nobility, unnamed spouses, half-remembered great-aunts. Judging those by
    their own record alone marks every one of them 'living', which is safe but
    useless: it withholds the fourteenth century.

    So for each person we compute an **upper bound on their birth year** — the
    latest year they could possibly have been born — and treat them as dead only
    when even that latest possible birth is more than `horizon` years ago.

    Every rule below is a genuine upper bound, never a guess:

      · a recorded birth or christening        → born in that year, exactly
      · any recorded event in year E           → born no later than E
      · a child born in year C                 → born no later than C - 14
      · a marriage in year M                   → born no later than M - 14
      · a parent whose bound is P              → born no later than P + 60

    A *recorded* birth is authoritative and is never overridden by inference,
    because an inference that made a living person look older would publish
    them. Where nothing at all is known the bound stays unknown and the person
    is presumed living, which is the safe direction to be wrong in.
    """
    fixed, bound = {}, {}

    def tighten(pid, y):
        if y is None:
            return False
        if pid in fixed:
            return False                     # a recorded birth is not negotiable
        if pid not in bound or y < bound[pid]:
            bound[pid] = y
            return True
        return False

    dead_by_record = set()
    for pid, p in people.items():
        if died(p).get("date"):
            dead_by_record.add(pid)
        b = year(born(p).get("date", ""))
        if b is not None:
            fixed[pid] = b
            bound[pid] = b
            continue
        for e in p["events"]:                # they existed at their own events
            tighten(pid, year(e.get("date", "")))

    kids_of, parents_of = {}, {}
    for f in families.values():
        pair = [x for x in (f["husb"], f["wife"]) if x]
        for par in pair:
            for c in f["chil"]:
                kids_of.setdefault(par, []).append(c)
                parents_of.setdefault(c, []).append(par)
        for e in f["events"]:                # married, so already of age
            y = year(e.get("date", ""))
            for par in pair:
                tighten(par, None if y is None else y - MIN_PARENT_AGE)

    for _ in range(60):
        moved = False
        for pid in people:
            for c in kids_of.get(pid, []):   # older than their children
                if c in bound:
                    moved |= tighten(pid, bound[c] - MIN_PARENT_AGE)
            for par in parents_of.get(pid, []):   # younger than their parents
                if par in bound:
                    moved |= tighten(pid, bound[par] + MAX_PARENT_AGE)
        if not moved:
            break

    out = {}
    for pid in people:
        if pid in dead_by_record:
            out[pid] = False
            continue
        b = bound.get(pid)
        out[pid] = not (b is not None and today_year - b > horizon)
    return out


def display(person):
    n = person["name"]
    if person["nick"]:
        n = f'{person["given"]} "{person["nick"]}" {person["surname"]}'.strip()
    n = re.sub(r"\s+", " ", n).strip()
    # The tree repeats particles: "Conrad V Von von Degenfeld", "Meinhard von
    # von Schonburg", "Adelmann Adelmann von Adelmannsfelden". Collapse an
    # adjacent repeat of the same word, keeping the second form's casing.
    n = re.sub(r"\b(\w+)\s+(\1)\b", lambda m: m.group(2),
               n, flags=re.IGNORECASE)
    return n.strip()


if __name__ == "__main__":
    people, families = load()
    print(f"{len(people)} people, {len(families)} families")
    surname = sys.argv[1] if len(sys.argv) > 1 else "D'Arcy"
    hits = [p for p in people.values() if p["surname"].lower() == surname.lower()]
    print(f"{len(hits)} with surname {surname}")
    for p in sorted(hits, key=lambda x: year(born(x).get("date", "")) or 9999):
        print(f'  {p["id"]:>8}  {display(p):<38} {lifespan(p):<12} '
              f'{born(p).get("place","")[:44]}')
