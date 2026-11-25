/* 23 NOVEMBER 2026 (the estate clean-up, David: "menus, do all"; Booyzen's menu of 12 November is the reference):
     People > Drawn: the five drawn pages became ONE link, "Drawn", to the hub /drawn/ (the list is DRAWN below).
     Places & families: the heading is now the hub link "All the families" (/families/) with the four named families under it, the own line
       first and then A to Z (Kalanj, Papić, Pavelić). Prpić and Žubrinić, two of the four families of Hedviga's line, left the dropdown: each is
       linked from /families/ (tools/familycheck.py asks it, and docs/menu-cleanup-reach.md proves it).
     Research: the eight core pages in their three groups plus ONE "Deep dives" heading that links /research/deep-dives/ (lib/research-menu.js).
   12 November 2026, as first written:
   THE WHOLE MENU, one list. 12 November 2026 (the menu regroup, PR A, after the Defranceski archive's): the seven groups other than
   Research became five, and Research (lib/research-menu.js, unchanged) is the sixth: Start, Our line, People, Places & families, The
   name, Research. The header menu and the drawer (layouts/Base.astro) read THIS list, so there is one place to change a label or move
   a page. MENU ONLY: no page was renamed, merged or deleted, no address changed, no page's text changed; every href below is a page
   that was already built, only its group moved.
   THE FAMILIES DROPDOWN IS TRIMMED (13 November 2026, David, one rule for all eight archives; the review proposed it on 12 November):
   the /families/ index (the heading), the own line, and the five largest other surname pages (Kalanj, Papić, Pavelić, Prpić, Žubrinić).
   tools/familycheck.py now asks that every family page be linked from this menu OR from the /families/ index, which this menu links;
   the nineteen smaller surname pages and Kosina, Lines of a Name, Who They Married and The Žubrinić Fragments left the dropdown and are
   reached from the index (Kosina, Lines and the Fragments were added to it in the same change; docs/menu-trim-reach.md proves each).
   FAMILY ORDER (13 November 2026, David: "own line first then A to Z"; the estate's family-menu-rule.md): the heading "The families" is
   itself the link to the /families/ index (no second "The Families" link under it), then Blažević (the own line), then every other surname
   in ONE run A to Z with accents folded (Žubrinić under Z). "Places" likewise: its heading links /places. (`cols: 2`, which let the long
   list flow into two CSS columns, is no longer used here; the option stays in Base.astro and styles.css for a longer list.)
     a menu is  [label, items]
     items      either a flat list of [href, label]            (a short menu: one column)
                or a list of groups { head, href?, items }   (a group is a column; `href` makes its heading a link; an item is [href, label])
   Where the old menus went:
     Start (10)            -> Start keeps Home, The Story, About, How Far Back; The trees, Our line drawn, Roots & Routes, The Timeline
                              -> People > Drawn; The Atlas -> Places & families > Places; What's new -> Research only (it is the
                              "What's new" group of Research, and the pulse button).
     Our line (7)          -> unchanged, plus the Documents menu (6) as a second column.
     The families (30)     -> Places & families > The families (the index, the own line and five surname pages; the rest through the index).
     Documents (6)         -> Our line > Documents.
     Origins (7)           -> Places & families > Origins and > Places.
     People & places (6)   -> People (the lists, and Drawn) and Places & families > Places.
     The name (3)          -> unchanged.
   Left the dropdown, reached from the /families/ index (or, for Who They Married, from its note): the 19 smaller surname pages, /kosina/, /lines/,
   /connected/, /zubrinic-roots/. */
import { navGroups } from "./research-menu.js";

/* THE DRAWN PAGES, listed on the hub page /drawn/ (src/pages/drawn.astro), which reads this list. 23 November 2026 (the estate clean-up, David:
   "menus, do all"): the five drawn pages left People > Drawn for ONE link "Drawn", and Roots & Routes, which was one of them, was retired
   (/roots/ redirects to /trees/). No page was renamed, moved or deleted. The Spine and The Lines of a Name are drawn too: the Spine stays
   in Our line, the Lines is reached from All the families, and both are listed here as well. */
export const DRAWN = [
  { href: "/tree", label: "Our line, drawn", blurb: "Where each branch of Hedviga's ancestry ends, and why: nothing cut for space, so every place it stops is a place the line really stops. The picture is drawn on the Tree Canvas." },
  { href: "/trees/", label: "The trees", blurb: "Every family this archive follows, each drawn; most of them are webs rather than lines, which is what the evidence is." },
  { href: "/bloodline/", label: "Blood relatives, drawn", blurb: "Choose a person and they go to the middle of the chart: parents above, brothers and sisters beside, children below, and through them the aunts, uncles and cousins." },
  { href: "/timeline", label: "The Timeline", blurb: "The line's places against the states that held them: Senj alone ran through the Uskoks, the Military Frontier, Austria\u2013Hungary and Yugoslavia." },
  { href: "/direct-line", label: "The Spine", blurb: "From a boy born about 1750 to Hedviga at Senj in 1926: the line the tree asserts, with the joint that cannot yet bear weight marked." },
  { href: "/lines/", label: "The Lines of a Name", blurb: "Wherever the registers show several households of one name, each gets a lane of its own, and a join between lanes is dotted until a document makes it." },
];

export const MENU = [
  ["Start", [
    ["/", "Home"], ["/story/", "The Story"], ["/about/", "About"], ["/how-far-back", "How Far Back"],
  ]],
  ["Our line", [
    { head: "The line", items: [
      ["/direct-line", "The Spine"], ["/people/hedviga-blazevic/", "Hedviga"], ["/people/milka-lucia-papic/", "Milka, her mother"],
      ["/senj", "Senj"], ["/senj-1943", "Senj, 1943"], ["/people/oto-blazevic/", "The Brother"], ["/rhodes", "Rhodes"],
    ] },
    { head: "Documents", items: [
      ["/marriage-1920", "The Wedding of 1920"], ["/certificate", "The Certificate"], ["/grave", "The Grave"],
      ["/arolsen", "The Arolsen Cards"], ["/pictures", "The Pictures"], ["/faces", "The Faces"],
    ] },
  ]],
  ["People", [
    { head: "Lists", items: [
      ["/people", "The People"], ["/who/", "Every Name"], ["/register", "The Register"], ["/marriages/", "The Marriages"],
    ] },
    /* ONE link to the hub page /drawn/ (23 November 2026): the drawn pages are listed there, from DRAWN below */
    { head: "Drawn", href: "/drawn/", items: [] },
  ]],
  ["Places & families", [
    { head: "All the families", href: "/families", items: [
      ["/blazevic", "Blažević"], ["/kalanj", "Kalanj"], ["/papic", "Papić"], ["/pavelic", "Pavelić"],
    ] },
    { head: "Places", href: "/places", items: [
      ["/atlas/", "The Atlas"], ["/gazetteer", "The Map"], ["/port-pirie", "Port Pirie"],
      ["/abroad/", "The Catch Abroad"],
    ] },
    { head: "Origins", items: [
      ["/bunjevci", "The Bunjevci"], ["/frontier", "The Frontier"], ["/work", "What They Did"], ["/america", "The Other Emigration"],
    ] },
  ]],
  /* THE NAME IS ITS OWN GROUP: Say Your Name and The Second Name were once filed under Origins, which is about where the family came
     from; three archives in this estate already kept a group called The name. */
  ["The name", [["/name", "The Name"], ["/by-names", "The Second Name"], ["/your-name/", "Say Your Name"]]],
  /* the Research menu (lib/research-menu.js): four groups, of which Checks is a proposal David has not confirmed */
  ["Research", navGroups],
];
