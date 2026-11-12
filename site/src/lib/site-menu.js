/* THE WHOLE MENU, one list. 12 November 2026 (the menu regroup, PR A, after the Defranceski archive's): the seven groups other than
   Research became five, and Research (lib/research-menu.js, unchanged) is the sixth: Start, Our line, People, Places & families, The
   name, Research. The header menu and the drawer (layouts/Base.astro) read THIS list, so there is one place to change a label or move
   a page. MENU ONLY: no page was renamed, merged or deleted, no address changed, no page's text changed; every href below is a page
   that was already built, only its group moved. No family page left the dropdown: tools/familycheck.py requires every family page to be in
   the families menu (the landing site's chips are read from it), so the nineteen smaller surname pages stay, in a second column
   ("More families"), although the /families/ index links each of them and docs/menu-a-reach.md could prove a trim. A trim would need
   that gate changed first: David's decision.
     a menu is  [label, items]
     items      either a flat list of [href, label]            (a short menu: one column)
                or a list of groups { head, href?, items }   (a group is a column; `href` makes its heading a link; an item is [href, label])
   Where the old menus went:
     Start (10)            -> Start keeps Home, The Story, About, How Far Back; The trees, Our line drawn, Roots & Routes, The Timeline
                              -> People > Drawn; The Atlas -> Places & families > Places; What's new -> Research only (it is the
                              "What's new" group of Research, and the pulse button).
     Our line (7)          -> unchanged, plus the Documents menu (6) as a second column.
     The families (30)     -> Places & families > The families.
     Documents (6)         -> Our line > Documents.
     Origins (7)           -> Places & families > Origins and > Places.
     People & places (6)   -> People (the lists, and Drawn) and Places & families > Places.
     The name (3)          -> unchanged.
   The /families/ index does not link /lines/, /zubrinic-roots/ or /kosina/ (an index fix is owed before any of the three could leave). */
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
    { head: "The families", items: [
      ["/families", "The Families"], ["/lines", "Lines of a Name"], ["/connected", "Who They Married"],
      ["/blazevic", "Blažević"], ["/zubrinic", "Žubrinić"], ["/zubrinic-roots", "The Žubrinić Fragments"], ["/papic", "Papić"],
      ["/prpic", "Prpić"], ["/kalanj", "Kalanj"], ["/pavelic", "Pavelić"], ["/kosina/", "Kosina"],
    ] },
    { head: "More families", items: [
      ["/boras", "Boras"], ["/vukelic", "Vukelić"], ["/sestan", "Šestan"], ["/tomljanovic", "Tomljanović"], ["/krmpotic", "Krmpotić"],
      ["/babic", "Babić"], ["/spalj", "Špalj"], ["/loncaric", "Lončarić"], ["/oreskovic", "Orešković"], ["/sekula", "Sekula"],
      ["/maric", "Marić"], ["/antic", "Antić"], ["/pilipic", "Pilipić"], ["/brozovic", "Brozović"], ["/jellicic", "Jelličić"],
      ["/uroda", "Uroda"], ["/luckinic", "Luckinić"], ["/gerkacs", "Gerkacs"], ["/smojver", "Smojver"],
    ] },
    { head: "Places", items: [
      ["/places", "Places"], ["/atlas/", "The Atlas"], ["/gazetteer", "The Map"], ["/port-pirie", "Port Pirie"], ["/abroad/", "The Catch Abroad"],
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
