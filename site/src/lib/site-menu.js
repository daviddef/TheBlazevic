/* THE WHOLE MENU, one list. 12 November 2026 (the menu regroup, PR A, after the Defranceski archive's): the seven groups other than
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
    { head: "Drawn", items: [
      ["/tree", "Our line, drawn"], ["/trees/", "The trees"], ["/roots/", "Roots & Routes"], ["/timeline", "The Timeline"],
      ["/bloodline/", "Blood relatives, drawn"],
    ] },
  ]],
  ["Places & families", [
    { head: "The families", href: "/families", items: [
      ["/blazevic", "Blažević"],
      ["/kalanj", "Kalanj"], ["/papic", "Papić"], ["/pavelic", "Pavelić"], ["/prpic", "Prpić"], ["/zubrinic", "Žubrinić"],
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
