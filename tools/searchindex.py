#!/usr/bin/env python3
"""One flat index over everything this archive can point at.

Two sources, because neither alone is enough:

  the JSON      people, places, register entries, documents, corrections
  the built HTML  the narrative pages, whose prose exists nowhere else

Reading site/dist means this must run AFTER a build, and it writes into
site/public so the next build ships it. In CI that is build, index, build.
The first run of a brand new page therefore misses it; the second catches it.

Diacritics are folded so that a reader typing Zubrinic finds Žubrinić and
Otocac finds Otočac — which matters more here than in most archives, because
this family's own name is spelled nine ways.
"""
import json, os, re, glob, unicodedata, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "site", "src", "data")
DIST = os.path.join(ROOT, "site", "dist")
L = lambda f: json.load(open(os.path.join(D, f), encoding="utf-8"))

rows, seen = [], set()


def fold(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return (s.replace("đ", "d").replace("Đ", "D")
             .replace("ž", "z").replace("ć", "c").replace("č", "c").replace("š", "s"))


def add(kind, title, sub, href, extra=""):
    if not title or href in seen and kind == "Page":
        return
    raw = " ".join(x for x in (title, sub, extra) if x).lower()
    rows.append({"k": kind, "t": title, "s": sub or "", "h": href,
                 "q": raw + " " + fold(raw)})


# ---- people --------------------------------------------------------------
people = list({p["id"]: p for p in L("people.json") + L("ancestors.json")}.values())
ev = L("evidence.json") if os.path.exists(os.path.join(D, "evidence.json")) else {}
for p in people:
    yrs = f"{p.get('born') or '?'}–{p.get('died') or '?'}"
    where = (p.get("bornPlace") or p.get("diedPlace") or "").split(",")[0]
    a = (ev.get(p["slug"]) or {}).get("ahn")
    sub = " · ".join(x for x in (yrs, where, f"ahnentafel {a}" if a else "") if x)
    add("Person", p["name"], sub, f"/people/{p['slug']}/",
        " ".join(filter(None, [p.get("surname"), p.get("given"), p.get("nick"),
                               p.get("bornPlace"), p.get("diedPlace"),
                               " ".join(o.get("what", "") for o in (p.get("occupations") or []))])))

# ---- places --------------------------------------------------------------
for pl in L("places.json"):
    name = pl.get("place") or pl.get("name") or ""
    add("Place", name, f"{pl.get('n', '')} records",
        f"/people/?q={name.split(',')[0]}")

# ---- the register, the part that is not the tree -------------------------
for r in L("register.json"):
    if r.get("kind") != "swept":
        continue
    add("Record", r["name"], r["detail"][:110],
        f"/people/{r['slug']}/" if r.get("slug") else "/register/",
        r["source"])

# ---- documents -----------------------------------------------------------
for m in L("media.json"):
    if m.get("kind") != "document":
        continue
    who = ", ".join(x["name"] for x in (m.get("people") or [])[:3])
    add("Document", m.get("caption") or m["file"], who, "/pictures/", who)

# ---- corrections ---------------------------------------------------------
for c in L("corrections.json"):
    add("Correction", c["what"], c.get("record", "")[:110],
        c.get("href") or "/changed/", c.get("why", "")[:300])

# ---- the narrative pages, read out of the build --------------------------
STRIP = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
if os.path.isdir(DIST):
    for f in sorted(glob.glob(os.path.join(DIST, "**", "index.html"), recursive=True)):
        href = "/" + os.path.relpath(os.path.dirname(f), DIST).replace(os.sep, "/") + "/"
        if href.startswith("/./"):
            href = "/"
        if href.startswith("/people/") and href != "/people/":
            continue                       # already indexed, and 1,086 of them
        src = open(f, encoding="utf-8").read()
        title = re.search(r"<title>(.*?)</title>", src, re.S)
        title = html.unescape(TAG.sub("", title.group(1))).split(" — ")[0].strip() if title else ""
        dek = re.search(r'<meta name="description" content="(.*?)"', src, re.S)
        dek = html.unescape(dek.group(1)).strip() if dek else ""
        # only <main>: the nav repeats 32 links on every page and would eat
        # the whole budget, pushing the actual prose out of the index. That is
        # why "Therapia" was findable in a correction but not on the page that
        # tells the story.
        m = re.search(r"<main\b[^>]*>(.*?)</main>", src, re.S | re.I)
        body = TAG.sub(" ", STRIP.sub(" ", m.group(1) if m else src))
        body = html.unescape(re.sub(r"\s+", " ", body))[:14000]
        add("Page", title, dek[:120], href, body)
        seen.add(href)

out = os.path.join(ROOT, "site", "public", "searchindex.json")
json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
import collections
print(f"{len(rows)} entries -> {os.path.relpath(out, ROOT)}")
for k, n in collections.Counter(r["k"] for r in rows).most_common():
    print(f"  {n:>5}  {k}")
print(f"  {os.path.getsize(out) // 1024} KB")
