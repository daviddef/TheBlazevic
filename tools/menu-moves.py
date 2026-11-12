#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Every entry of the header menu, old build against new: where each address stood and where it stands now, and for every address that
left the menu, the proof that a reader can still reach it (12 November 2026, the menu regroup, PR A; 13 November 2026, the families trim).

    python3 tools/menu-moves.py BEFORE_DIST AFTER_DIST OUT_MOVES.md OUT_REACH.md

Reads the <nav class="topnav"> of the home page of each build. Exit 1 if
  - an address that was in the menu is in no menu now and is not listed in DROPPED below with its reason, or
  - a DROPPED address is not linked, in the body of the built page, from any page that is still in the menu (the reach proof).
Only the text under <main> of a page counts as a link from it (the header, the drawer and the footer are not part of a page)."""
import html, os, re, sys

# An address that left the dropdown on purpose, and why. Each must be linked, in the body of its page, from a page that is still in the menu
# (for the surname pages and the three added to the index in the same change, that page is /families/, the heading of the families group).
SURNAME = "a surname page: linked from the /families/ index, which the menu links"
DROPPED = {"/%s/" % s: SURNAME for s in (
    "boras", "vukelic", "sestan", "tomljanovic", "krmpotic", "babic", "spalj", "loncaric", "oreskovic", "sekula", "maric",
    "antic", "pilipic", "brozovic", "jellicic", "uroda", "luckinic", "gerkacs", "smojver")}
DROPPED["/kosina/"] = "linked from the /families/ index (added to it in this change)"
DROPPED["/lines/"] = "linked from the /families/ index (added to it in this change)"
DROPPED["/zubrinic-roots/"] = "linked from the /families/ index (added to it in this change)"
DROPPED["/connected/"] = "linked from a note on the /families/ index (already there)"


def norm(h):
    h = re.sub(r"[#?].*$", "", h)
    return h if h.endswith("/") else h + "/"


def menu(dist):
    t = open(dist + "/index.html", encoding="utf-8").read()
    nav = t[t.index('<nav class="topnav"'):]
    nav = nav[:nav.index("</nav>")]
    out = []   # (menu, group, href, label)
    for m in re.finditer(r'<details class="menu">(.*?)</details>', nav, re.S):
        body = m.group(1)
        label = html.unescape(re.search(r"<summary>(.*?)</summary>", body, re.S).group(1))
        grp = ""
        for tok in re.finditer(r'<(?:div class="pg"|a [^>]*href="([^"]+)"[^>]*>(.*?)</a>|span class="ps[^"]*">(.*?)</span>)', body, re.S):
            if tok.group(0).startswith('<div class="pg"'):
                grp = ""
            elif tok.group(3) is not None:
                grp = html.unescape(tok.group(3))
            else:
                href, txt = tok.group(1), html.unescape(re.sub(r"<[^>]+>", "", tok.group(2)))
                if "ph" in tok.group(0)[:40]:
                    grp = txt
                    out.append((label, grp, norm(href), txt + "  (group heading)"))
                else:
                    out.append((label, grp, norm(href), txt))
    return out


def body_links(path):
    raw = open(path, encoding="utf-8").read()
    m = re.search(r"<main\b.*?</main>", raw, re.S | re.I) or re.search(r'<div class="wrap">.*', raw, re.S | re.I)
    return set(norm(h) for h in re.findall(r'href="(/[^"]*)"', m.group(0) if m else raw))


def main():
    before, after, out_moves, out_reach = sys.argv[1:5]
    b, a = menu(before), menu(after)
    bh, ah = {}, {}
    for m, g, h, l in b:
        bh.setdefault(h, []).append((m, g, l))
    for m, g, h, l in a:
        ah.setdefault(h, []).append((m, g, l))
    L = ["# The menu, before and after", "",
         "Every address in the header menu of the old build (%d entries) and of the new one (%d). Only addresses whose place changed are listed." % (len(b), len(a)),
         "", "| address | was | now |", "|---|---|---|"]
    bad = 0
    for h in list(dict.fromkeys([x[2] for x in b] + [x[2] for x in a])):
        was = "; ".join("%s%s: %s" % (m, " / " + g if g else "", l) for m, g, l in bh.get(h, [])) or "—"
        now = "; ".join("%s%s: %s" % (m, " / " + g if g else "", l) for m, g, l in ah.get(h, [])) or "—"
        if h in bh and h not in ah:
            if h in DROPPED:
                now = "not in the dropdown: " + DROPPED[h]
            else:
                now = "**not in the menu**"
                bad += 1
        if was != now:
            L.append("| `%s` | %s | %s |" % (h, was, now))
    gone = [h for h in bh if h not in ah]
    L += ["", "%d address(es) left the dropdown, %d of them with a stated reason; %d without." % (len(gone), len([h for h in gone if h in DROPPED]), bad)]
    # the reach proof
    menu_pages = [h for h in dict.fromkeys(x[2] for x in a) if not h.startswith(("/people/", "/who/"))]
    linked = {}
    for h in menu_pages:
        p = os.path.join(after, h.strip("/"), "index.html")
        if os.path.exists(p):
            for t in body_links(p):
                linked.setdefault(t, []).append(h)
    R = ["# Reach: every address that left the dropdown is linked from a page that stays in it", "",
         "For each address below, the pages that are still in the menu and link it in their body (the first five; the count is of all). "
         "`/families/` must be among them: it is the menu's own heading.", "",
         "| address | why it left | linked from (pages still in the menu) |", "|---|---|---|"]
    for h in gone:
        if h not in DROPPED:
            continue
        who = [x for x in linked.get(h, []) if x != h]
        if "/families/" not in who:
            bad += 1
        R.append("| `%s` | %s | %s |" % (h, DROPPED[h], ("%d: " % len(who) + ", ".join("`%s`" % x for x in who[:5])) if who else "**NONE: keep it in the menu**"))
    open(out_moves, "w", encoding="utf-8").write("\n".join(L) + "\n")
    open(out_reach, "w", encoding="utf-8").write("\n".join(R) + "\n")
    print("\n".join(L[:4] + L[-2:]))
    print("\n".join(R[:3]))
    print("problems:", bad)
    sys.exit(1 if bad else 0)


main()
