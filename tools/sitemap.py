"""SUPERSEDED, AND KEPT ONLY SO NOBODY WRITES IT AGAIN.

This is the archive's own sitemap writer. The build has not called it since
the kit took the job over: site/package.json runs
    node_modules/@daviddef/archive-kit/kit/tools/sitemap.py
which resolves its output through kit/tools/outdir.py and therefore honours
ARCHIVE_OUT. THIS FILE DOES NOT. It computes site/dist and takes no argument,
so running it while a sibling session holds site/dist writes a sitemap for
somebody else's build - which is the exact fault that was found in this
archive's searchindex.py and check_site.py on 27 September 2026.

It is not deleted because the estate keeps what it replaced and says why.
It refuses to run instead.
"""
import sys
sys.exit("tools/sitemap.py is superseded by the kit's sitemap.py, which "
         "honours ARCHIVE_OUT. Run: npm run sitemap")

# ---- the original, unreachable, kept for the record ----
#!/usr/bin/env python3
"""Write sitemap.xml and robots.txt from what was actually built.

Generated from the HTML rather than from the route list on purpose: several of
these archives publish person pages for living relatives with
<meta name="robots" content="noindex">, and a sitemap built from routes would
hand exactly those pages to search engines. This reads each built file and
skips anything that noindexes itself, so the sitemap can never disagree with
the privacy rule the pages already state.
"""
import os, re, sys, json, datetime

here = os.path.dirname(os.path.abspath(__file__))
site = os.path.join(here, "..", "site")
dist = os.path.join(site, "dist")
cfg = open(os.path.join(site, "astro.config.mjs"), encoding="utf-8").read()

origin = re.search(r"site:\s*['\"]([^'\"]+)", cfg).group(1).rstrip("/")
base = re.search(r"base:\s*['\"]([^'\"]+)", cfg)
base = base.group(1).rstrip("/") if base else ""

NOINDEX = re.compile(r'name=["\']robots["\'][^>]*noindex', re.I)
urls, skipped = [], 0
for dp, _, fns in os.walk(dist):
    for fn in fns:
        if fn != "index.html":
            continue
        p = os.path.join(dp, fn)
        html = open(p, encoding="utf-8", errors="ignore").read()
        if NOINDEX.search(html[:4000]):
            skipped += 1
            continue
        if "http-equiv=\"refresh\"" in html[:400]:   # redirect stubs
            skipped += 1
            continue
        rel = os.path.relpath(dp, dist).replace(os.sep, "/")
        path = "" if rel == "." else rel + "/"
        urls.append(f"{origin}{base}/{path}")

urls.sort()
today = datetime.date.today().isoformat()
body = "\n".join(
    f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in urls)
open(os.path.join(dist, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f"{body}\n</urlset>\n")

robots = os.path.join(site, "public", "robots.txt")
if not os.path.exists(robots):
    os.makedirs(os.path.dirname(robots), exist_ok=True)
    open(robots, "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nSitemap: {origin}{base}/sitemap.xml\n")
# and copy whatever robots.txt exists into dist, since public/ was already copied
print(f"sitemap: {len(urls)} urls, {skipped} withheld (noindex or redirect)")
