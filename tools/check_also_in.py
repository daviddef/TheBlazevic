#!/usr/bin/env python3
"""Does every confirmed cross-archive pair show its pointer on this archive's page, and nobody else?

Written 17 October 2026, after D'Arcy's tools/check_also_in.py. The kit keeps the list of people
documented in two archives (kit/data/cross-archive.json) and draws «Also documented in …» for a
pair marked CONFIRMED. The component is silent for everything else, which is exactly why this
reads the BUILT page: a template that forgets to pass `archive` or `path` renders nothing, says
nothing, and every gate that reads the source or the list sees a correct input.

It checks both directions, because a rule checked one way drifts the other:
  - every CONFIRMED pair that names a page of this archive: that page carries the pointer, once
    per pair, and it links to the other archive's page at the address the ring gives
  - no OTHER page carries one, and above all no LIVING page does: a living page is a name,
    a relationship and a place, and a pointer to another archive is none of those

It refuses an empty build (no person pages examined means nothing was checked).
Only the dead are named in its output; nothing here prints a living person.

  python3 tools/check_also_in.py                 reads site/$ARCHIVE_OUT (default site/dist)
  python3 tools/check_also_in.py --selftest      plants each fault in a scratch build and shows it is caught
"""
import argparse, glob, json, os, re, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# ARCHIVE_OUT is where this session's build actually went (see tools/check_site.py).
DIST = os.path.join(ROOT, "site", os.environ.get("ARCHIVE_OUT") or "dist")
KIT = os.path.join(ROOT, "site", "node_modules", "@daviddef", "archive-kit", "kit", "data")
ME = "blazevic"
ALSO = re.compile(r'data-also-in="(\d+)"')
BLOCK = re.compile(r'<p[^>]*data-also-in[^>]*>(.*?)</p>', re.S)
HREFS = re.compile(r'href="([^"]+)"')
NOINDEX = re.compile(r'<meta\s+name="robots"\s+content="noindex"')


def read(f):
    with open(f, encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def expected(pairs, ring):
    """my page path -> [hrefs the pointer must carry], from the CONFIRMED pairs of this archive."""
    expect = {}
    for p in pairs:
        if p.get("status") != "confirmed":
            continue
        if p["a"]["archive"] == ME:
            mine, other = p["a"], p["b"]
        elif p["b"]["archive"] == ME:
            mine, other = p["b"], p["a"]
        else:
            continue
        if other["archive"] not in ring:
            continue
        expect.setdefault(mine["path"], []).append(ring[other["archive"]]["url"].rstrip("/") + other["path"])
    return expect


def examine(dist, pairs, ring):
    """-> (findings, pointers shown, pairs expected, person pages examined)"""
    pages = glob.glob(os.path.join(dist, "people", "*", "index.html"))
    if not pages:
        return [f"no built person pages under {dist}: nothing was examined"], 0, 0, 0
    expect = expected(pairs, ring)
    fails, shown = [], 0
    for path, hrefs in expect.items():
        f = os.path.join(dist, path.strip("/"), "index.html")
        if not os.path.exists(f):
            fails.append(f"{path} has a confirmed pair and no built page")
            continue
        html = read(f)
        if NOINDEX.search(html):
            # The template is right and the list is wrong: a living page never gets a pointer.
            fails.append(f"{path} is a LIVING person's page and a confirmed pair names it; a pointer is never "
                         f"drawn for the living, so the kit's cross-archive list should not hold this pair")
            continue
        m = ALSO.search(html)
        if not m:
            fails.append(f"{path} has a confirmed pair and the page carries no pointer: the template is not passing its props")
            continue
        shown += 1
        b = BLOCK.search(html)
        got = HREFS.findall(b.group(1)) if b else []
        for h in hrefs:
            if h not in got:
                fails.append(f"{path} does not point at {h}")
        for g in got:
            if g not in hrefs:
                fails.append(f"{path} points at {g}, which no confirmed pair gives")
        if int(m.group(1)) != len(hrefs):
            fails.append(f"{path} draws {m.group(1)} pointer(s) and {len(hrefs)} pair(s) are confirmed")
    for f in pages:
        slug = f.split(os.sep)[-2]
        path = f"/people/{slug}/"
        html = read(f)
        if ALSO.search(html):
            if NOINDEX.search(html):
                fails.append(f"{path} is a LIVING page and carries a pointer to another archive")
            elif path not in expect:
                fails.append(f"{path} carries a pointer and no confirmed pair names it")
    return fails, shown, len(expect), len(pages)


def load_kit():
    pairs = json.load(open(os.path.join(KIT, "cross-archive.json"), encoding="utf-8"))["pairs"]
    ring = {a["key"]: a for a in json.load(open(os.path.join(KIT, "archives.json"), encoding="utf-8"))["archives"]}
    return pairs, ring


def report(fails, shown, want, n):
    if fails:
        print(f"  FAIL  alsoin     {len(fails)} finding(s) across {n} person page(s)")
        for m in fails[:8]:
            print(f"          {m}")
        return 1
    print(f"  ok    alsoin     {shown} of {want} confirmed pair(s) show their pointer on this archive's page, to the "
          f"address the ring gives; no other page and no living page carries one ({n} checked)")
    return 0


def page(slug_html):
    return "<html><head><title>x</title></head><body>" + slug_html + "</body></html>"


def selftest():
    ring = {"blazevic": {"url": "https://blazevic.test/"}, "defranceski": {"url": "https://archive.test/"}}
    pairs = [{"a": {"archive": ME, "path": "/people/ada/"}, "b": {"archive": "defranceski", "path": "/person/ada-1/"}, "status": "confirmed"},
             {"a": {"archive": ME, "path": "/people/bob/"}, "b": {"archive": "defranceski", "path": "/person/bob-1/"}, "status": "confirmed"},
             {"a": {"archive": ME, "path": "/people/cyd/"}, "b": {"archive": "defranceski", "path": "/person/cyd-1/"}, "status": "candidate"}]
    ptr = lambda href: f'<p class="also-in" data-also-in="1">Also documented in <a href="{href}">X</a>.</p>'
    good = {"ada": ptr("https://archive.test/person/ada-1/"), "bob": ptr("https://archive.test/person/bob-1/"),
            "cyd": "", "eve": "", "liv": '<meta name="robots" content="noindex">'}

    def build(mod):
        d = tempfile.mkdtemp(prefix="alsoin-")
        files = dict(good)
        mod(files)
        for slug, body in files.items():
            if body is None:
                continue
            os.makedirs(os.path.join(d, "people", slug))
            with open(os.path.join(d, "people", slug, "index.html"), "w") as fh:
                fh.write(page(body))
        return d

    faults = [
        ("a clean build passes", lambda f: None, False),
        ("a confirmed pair whose page lacks the pointer", lambda f: f.update(ada=""), True),
        ("a pointer to the wrong address", lambda f: f.update(bob=ptr("https://archive.test/person/zzz-9/")), True),
        ("a pointer on a page in no confirmed pair (a candidate)", lambda f: f.update(cyd=ptr("https://archive.test/person/cyd-1/")), True),
        ("a pointer on a page in no pair at all", lambda f: f.update(eve=ptr("https://archive.test/person/eve-1/")), True),
        ("a pointer on a living page", lambda f: f.update(liv='<meta name="robots" content="noindex">' + ptr("https://archive.test/person/liv-1/")), True),
        ("a confirmed pair whose page is noindex (the list names a living page)", lambda f: f.update(ada='<meta name="robots" content="noindex">'), True),
        ("a confirmed pair with no built page", lambda f: f.pop("bob"), True),
        ("an empty build", lambda f: [f.pop(k) for k in list(f)], True),
    ]
    bad = 0
    for label, mod, should_fail in faults:
        d = build(mod)
        try:
            fails, *_ = examine(d, pairs, ring)
        finally:
            shutil.rmtree(d)
        caught = bool(fails)
        ok = caught == should_fail
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'}  selftest  {label}: {'refused' if caught else 'passed'}")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dist", default=DIST)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    try:
        pairs, ring = load_kit()
    except Exception as e:
        print(f"  FAIL  alsoin     cannot read the kit's cross-archive data: {e}")
        return 1
    return report(*examine(a.dist, pairs, ring))


if __name__ == "__main__":
    sys.exit(main())
