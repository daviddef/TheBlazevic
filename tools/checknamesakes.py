#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One page per person: does every person's page list exactly the other people of their name, and does every old name address land?

    python3 ../tools/checknamesakes.py --dist "${ARCHIVE_OUT:-dist}"        # from site/; `npm run check:namesakes`
    python3 ../tools/checknamesakes.py --selftest --dist "${ARCHIVE_OUT:-dist}"   # plants one fault per rule

WHAT CHANGED (23 November 2026, rolled out from Booyzen, TheBooyzen PR #36). A name used to have a page, /who/<name>/, beside the
person's page. The name pages are gone: a person's page lists the other people who carry the same name (#others-of-this-name), and every
old /who/<name>/ address is a static redirect. This archive had no gate for name pages (the kit's checknamepages.py was never wired
here), so this is the first. It checks the NEW rule, from the BUILD and from nothing the page generator used:

  sets      The sets are derived here from the <title> of every built person page (/people/<slug>/): the full name as the page carries it
            (the h1 drops a qualifier, "Nicolaus Blažević (Sojat)" has the h1 "Nicolaus Blažević"), accents, case and punctuation folded.
            The others of a page are the rest of its set, plus the register finds the committed src/data/who-finds.json lists under that
            name (each has a page of its own at /found/<slug>/).
  missing   a page's "Others of this name" list lacks a person (or find) of its name.
  extra     it lists a page that does not carry the name, or itself.
  absent    a name is shared and the page has no list, or the page has a list and nobody shares its name.
  stub      an address under /who/ that is not a redirect (or the index, or one of its letter pages) is a name page that is still drawn;
            a redirect whose target is not built, whose #fragment is not on the target, that lands on a page that does not carry the
            name, on a living person's page when somebody who has died bears it, or that is in the sitemap; a name some person
            bears with no redirect at all.
  index     the letter pages under /who/names--<initial>/ link a /who/<name>/ address, or do not link a person page of somebody who
            has died. (A name borne only by the living is not listed, and a living person is never linked from the index.)

A living person is never named in a message (their slug can carry a year): their page is reported as "a living person's page"
(any page that says noindex). Exit 0 clean, 1 findings, 2 it could not see what it checks (no build, no person page, no stub).
"""
import argparse
import html
import json
import os
import re
import sys
import unicodedata

SECTION = "others-of-this-name"
LETTER = re.compile(r"^/who/names--[a-z0-9]+/$")
HERE = os.path.dirname(os.path.abspath(__file__))
FINDS = os.path.join(os.path.dirname(HERE), "site", "src", "data", "who-finds.json")


def fold(s):
    s = unicodedata.normalize("NFD", html.unescape(s or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def read_pages(dist):
    """Only what this gate reads: the person pages, everything under /who/, and the sitemap."""
    pages = {}
    for top in ("people", "who"):
        for root, _dirs, files in os.walk(os.path.join(dist, top)):
            if "index.html" in files:
                rel = os.path.relpath(root, dist).replace(os.sep, "/")
                with open(os.path.join(root, "index.html"), encoding="utf-8", errors="replace") as f:
                    pages["/" + rel + "/"] = f.read()
    sm = os.path.join(dist, "sitemap.xml")
    sitemap = open(sm, encoding="utf-8").read() if os.path.exists(sm) else ""
    # the kit writes sitemap-0.xml beside an index; read every sitemap file there is
    for name in sorted(os.listdir(dist)):
        if name.startswith("sitemap") and name.endswith(".xml") and name != "sitemap.xml":
            sitemap += open(os.path.join(dist, name), encoding="utf-8").read()
    return pages, sitemap


def finds_by_name():
    """fold(name) -> {/found/<slug>/}: the finds the committed who-finds.json lists under each name (key = the slug of the name)."""
    try:
        d = json.load(open(FINDS, encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {fold(k.replace("-", " ")): {"/found/%s/" % r["slug"] for r in v} for k, v in d.items()}


def is_stub(raw):
    return 'http-equiv="refresh"' in raw[:900]


def stub_target(raw):
    m = re.search(r'http-equiv="refresh" content="0;url=([^"]+)"', raw[:1200])
    return html.unescape(m.group(1)) if m else None


def name_of(raw):
    """the full name a person page carries: its <title> without the site name"""
    m = re.search(r"<title>(.*?)</title>", raw, re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))) if m else ""
    return t.rsplit(" — ", 1)[0].strip()


def listed(raw):
    """(has the section, the pages its list links to, in order)"""
    m = re.search(r'id="%s"' % SECTION, raw)
    if not m:
        return False, []
    tail = raw[m.end():]
    ul = re.search(r'<ul class="oth-list[^"]*"[^>]*>(.*?)</ul>', tail, re.S)
    hrefs = re.findall(r'href="(/(?:people|found)/[^"#?]+/)"', ul.group(1)) if ul else []
    return True, hrefs


def check(pages, sitemap, finds):
    """(findings, counts, setof) over an in-memory build: route -> html."""
    findings = []
    persons = {}
    for route, raw in pages.items():
        if route.startswith("/people/") and route != "/people/" and "data-person-page" in raw and not is_stub(raw):
            persons[route] = {"name": name_of(raw), "living": bool(re.search(r'<meta name="robots" content="[^"]*noindex', raw[:6000]))}
    stubs = {r: s for r, s in pages.items() if r.startswith("/who/") and r != "/who/" and is_stub(s)}
    named = {r: s for r, s in pages.items() if r.startswith("/who/") and r != "/who/" and not is_stub(s) and not LETTER.match(r)}
    letters = {r: s for r, s in pages.items() if LETTER.match(r) and not is_stub(s)}
    if not persons or "/who/" not in pages:
        return None, {}, {}
    label = lambda r: "a living person's page" if persons.get(r, {}).get("living") else r

    # ---- the sets, from the built titles
    key_of = {r: fold(p["name"]) for r, p in persons.items()}
    group = {}
    for r, k in key_of.items():
        if k:
            group.setdefault(k, set()).add(r)
    setof = {}
    for k, members in group.items():
        for r in members:
            setof[r] = (members - {r}) | finds.get(k, set())
    shared_sets = {k for k, m in group.items() if len(m) + len(finds.get(k, ())) > 1}

    with_section = 0
    for r, others in sorted(setof.items()):
        has, got = listed(pages[r])
        if has:
            with_section += 1
        if others and not has:
            findings.append("absent: %s shares its name with %d other page(s) and has no #%s section" % (label(r), len(others), SECTION))
            continue
        if has and not others:
            findings.append("absent: %s has a #%s section and nobody shares its name" % (label(r), SECTION))
        miss = sorted(others - set(got))
        extra = sorted(set(got) - others)
        if miss:
            findings.append("missing: %s does not list %d of its name: %s" % (label(r), len(miss), ", ".join(label(x) for x in miss[:6])))
        if extra:
            findings.append("extra: %s lists %d that do not carry its name: %s" % (label(r), len(extra), ", ".join(label(x) for x in extra[:6])))
        if len(got) != len(set(got)):
            findings.append("extra: %s lists somebody twice" % label(r))

    # ---- the old addresses: one for every name some person bears, and every one lands on a person of that name
    for r, raw in sorted(stubs.items()):
        tgt = stub_target(raw)
        if not tgt:
            findings.append("stub: %s is a redirect with no target" % r)
            continue
        path, _, frag = tgt.partition("#")
        if path not in persons:
            findings.append("stub: %s lands on %s, which is not a built person page" % (r, path))
            continue
        key = fold(r[len("/who/"):-1].replace("-", " "))
        must = key in shared_sets          # a name several carry lands on the section that lists the others
        if key in group and path not in group[key]:
            findings.append("stub: %s lands on %s, which does not carry the name" % (r, label(path)))
        elif key in group and persons[path]["living"] and not all(persons[x]["living"] for x in group[key]):
            findings.append("stub: %s lands on a living person's page while somebody who has died bears the name" % r)
        if frag and frag != SECTION:
            findings.append("stub: %s lands on #%s, which is not the section" % (r, frag))
        elif must and not frag:
            findings.append("stub: %s is a name %d people carry and has no #%s fragment" % (r, len(group.get(key, ())) + len(finds.get(key, ())), SECTION))
        elif frag and 'id="%s"' % SECTION not in pages[path]:
            findings.append("stub: %s lands on #%s, which is not on %s" % (r, SECTION, label(path)))
        elif frag and not must:
            findings.append("stub: %s has a #%s fragment and nobody shares the name" % (r, SECTION))
        if re.search(r"<loc>[^<]*%s</loc>" % re.escape(r), sitemap):
            findings.append("stub: %s is in the sitemap" % r)
    have = {fold(r[len("/who/"):-1].replace("-", " ")) for r in stubs}
    # the merged record's old name address is a redirect too, to a person of ANOTHER name: only the names that persons bear are required
    lost = sorted(k for k in group if k not in have)
    if lost:
        findings.append("stub: %d name(s) a person bears have no redirect from /who/ (first: %s)" % (len(lost), lost[0] if not any(persons[x]["living"] for x in group[lost[0]]) else "a living person's"))
    for r, raw in sorted(named.items()):
        findings.append("stub: %s is a page, and a name that a person page carries has no page of its own" % r)

    # ---- the index: its letter pages
    if not letters:
        findings.append("index: /who/ has no letter page")
    linked_people = set()
    for r, idx in sorted(letters.items()):
        for h in sorted(set(re.findall(r'href="(/who/[^"#?]+/)"', idx))):
            if h != "/who/" and not LETTER.match(h):
                findings.append("index: %s links %s, which is the address of a name" % (r, h))
        linked_people |= set(re.findall(r'href="(/people/[^"#?]+/)"', idx))
    hub = pages["/who/"]
    for h in sorted(set(re.findall(r'href="(/who/[^"#?]+/)"', hub))):
        if h != "/who/" and not LETTER.match(h):
            findings.append("index: /who/ links %s, which is the address of a name" % h)
        elif LETTER.match(h) and h not in letters:
            findings.append("index: /who/ links %s, which is not built" % h)
    # (a person whose name has no letter or digit, "?" or "-", has never had a name page, and has no entry)
    gone = sorted(r for r, p in persons.items() if not p["living"] and key_of[r] and r not in linked_people)
    if gone:
        findings.append("index: the letter pages do not link %d person page(s): %s" % (len(gone), ", ".join(label(x) for x in gone[:6])))
    seen_living = sorted(r for r, p in persons.items() if p["living"] and r in linked_people)
    if seen_living:
        findings.append("index: the letter pages link %d living person's page(s)" % len(seen_living))
    counts = {"person pages": len(persons), "with a list": with_section, "shared names": len(shared_sets),
              "old name addresses (redirects)": len(stubs), "letter pages": len(letters), "name pages left": len(named)}
    return findings, counts, setof


def selftest(pages, sitemap, finds):
    f0, _c, setof = check(pages, sitemap, finds)
    ok = True
    print("  control: the untouched build -> %d finding(s)%s" % (len(f0), "" if not f0 else "  <-- SHOULD BE 0"))
    if f0:
        ok = False
    shared = sorted(r for r, o in setof.items() if o and any(x.startswith("/people/") for x in o))
    solo = sorted(r for r, o in setof.items() if not o)
    if not shared or not solo:
        print("  no shared name or no unshared person to plant against: refusing")
        return False
    a = shared[0]

    def planted(name, mutate, want, sm=None):
        nonlocal ok
        v = dict(pages)
        mutate(v)
        got, _c, _s = check(v, sitemap if sm is None else sm, finds)
        hit = any(g.startswith(want) for g in (got or []))
        print("  %-58s %s" % (name, "caught" if hit else "MISSED  <-- the gate cannot see this"))
        ok = ok and hit

    other = sorted(x for x in setof[a] if x.startswith("/people/"))[0]
    planted("a person of the name left off a list", lambda v: v.__setitem__(a, re.sub(r'<li[^>]*>(?:(?!</li>).)*?href="%s".*?</li>' % re.escape(other), "", v[a], count=1, flags=re.S)), "missing")

    def add_stranger(v):
        i = v[a].index('<ul class="oth-list')
        j = v[a].index("</ul>", i)
        v[a] = v[a][:j] + '<li><a href="%s">x</a></li>' % solo[0] + v[a][j:]
    planted("a stranger added to a list", add_stranger, "extra")
    planted("a list on a name nobody shares",
            lambda v: v.__setitem__(solo[0], v[solo[0]].replace("</main>", '<section id="%s"><ul class="oth-list"><li><a href="%s">x</a></li></ul></section></main>' % (SECTION, a), 1)), "absent")
    planted("a shared name with no section", lambda v: v.__setitem__(a, v[a].replace('id="%s"' % SECTION, 'id="nothing"')), "absent")
    stub = sorted(r for r in pages if r.startswith("/who/") and is_stub(pages[r]))[0]
    planted("a redirect to a page that was never built", lambda v: v.__setitem__(stub, v[stub].replace("/people/", "/nowhere/")), "stub")
    planted("a name page for a name a person carries", lambda v: v.__setitem__(stub, pages[solo[0]]), "stub")
    # a redirect that lands on a person who does not carry the name
    stranger = next(r for r in solo if r not in stub_target(pages[stub]))
    planted("a redirect to a person of another name",
            lambda v: v.__setitem__(stub, re.sub(r"/people/[^\"#/]+/", stranger, v[stub])), "stub")
    sh = next(r for r in sorted(pages) if r.startswith("/who/") and is_stub(pages[r]) and "#" + SECTION in pages[r][:900])
    planted("a shared name's redirect without the section", lambda v: v.__setitem__(sh, v[sh].replace("#" + SECTION, "")), "stub")
    planted("a redirect in the sitemap", lambda v: None, "stub", sm=sitemap + "<loc>https://x%s</loc>" % stub)
    letter = sorted(r for r in pages if LETTER.match(r))[0]
    planted("a link on a letter page to a name's address", lambda v: v.__setitem__(letter, v[letter].replace("</main>", '<a href="%s">x</a></main>' % stub, 1)), "index")
    dead = next(r for r in solo if "noindex" not in pages[r][:6000])
    planted("a person page the letter pages never link", lambda v: v.__setitem__(letter, v[letter].replace('href="%s"' % dead, 'href="/nowhere/"')), "index")
    planted("a stub deleted for a name a person bears", lambda v: v.pop(stub), "stub")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dist", default="dist")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.dist):
        print("checknamesakes: %s is not a directory; nothing was checked" % a.dist)
        return 2
    pages, sitemap = read_pages(a.dist)
    finds = finds_by_name()
    if a.selftest:
        return 0 if selftest(pages, sitemap, finds) else 1
    findings, counts, _setof = check(pages, sitemap, finds)
    if findings is None:
        print("checknamesakes: no person page or no /who/ index in %s; nothing was checked" % a.dist)
        return 2
    if not [r for r in pages if r.startswith("/who/") and r != "/who/" and is_stub(pages[r])]:
        print("checknamesakes: no redirect under /who/ in %s; nothing was checked" % a.dist)
        return 2
    for f in findings:
        print("  FAIL  " + f)
    print("checknamesakes: " + ", ".join("%d %s" % (v, k) for k, v in counts.items()) + "; %d finding%s" % (len(findings), "" if len(findings) == 1 else "s"))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
