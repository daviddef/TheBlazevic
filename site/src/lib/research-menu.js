/* THE RESEARCH MENU: one list, read by the header menu (layouts/Base.astro), the drawer, the hub page /research/ and the group
   pages. 12 November 2026 (the research-menu trial, wave 3, after the Defranceski archive and the three wave-2 archives): the
   "Evidence" and "Investigations" menus became one "Research" menu with four groups. Nothing is renamed or removed: every item keeps
   the address it had, and the labels of the eight pages the estate's Evidence canon names (kit data/evidence-menu.json) are unchanged.
   `asks` is the canon's question for those pages and, for the others, one plain line taken from the page's own standfirst.
   `atlas` marks the pages whose registers and places are also on the Record Atlas.
   THE FOURTH GROUP, "Checks", is a proposal that David has not confirmed (the plan's recommendation): the four generated audits
   (What Rests on a Document, What Cannot Be True, The Same Person, Twice, Labels Where the Father Should Be) fit none of the three
   groups, so they are a group page of their own, which is easy to fold elsewhere: delete the entry below and the page
   src/pages/research/checks/. The pages are generated; only their place in the menu moves.
   23 NOVEMBER 2026 (the estate clean-up, David: "menus, do all"): the menu itself is cut to the eight core pages in their three groups plus ONE
   entry, "Deep dives", whose heading is a link to the hub page /research/deep-dives/. Every item marked `deep: true` below left the menu for that
   hub (eleven pages: What Is Left to Read, What the Registers Say, The Pages Themselves, Which Books Are Indexed, the three long studies and the
   four checks). Nothing moved or was renamed: each keeps its address, its row on its group page (/research/to-do/, /research/sources-and-method/,
   /research/checks/) and its place on /research/. The menu (`navGroups`) and the hub (`DEEP`) are both made from this one list, so they cannot
   disagree. */
export const RESEARCH = [
  { id: "to-do", head: "To do", href: "/research/to-do/", deepHead: "Books still to be read",
    deepNote: "Which books this archive can open, and what each would give: a study of its own rather than a task.",
    dek: "What is not known yet, what has been asked of other people, what is being worked on, and which books are still to be read.",
    items: [
      { href: "/open-questions/", label: "Open Questions", asks: "What is not known, and what would settle it?" },
      { href: "/errands/", label: "Errands", asks: "What has been asked of other people, or needs someone standing in a place?" },
      { href: "/worklist/", label: "The work list", asks: "What is being done, by whom, since when?" },
      { deep: true, href: "/harvest/", label: "What Is Left to Read", atlas: true,
        asks: "Which people were written in a parish whose films can be opened, and what would each book give?" },
    ] },
  { id: "whats-new", head: "What's new", href: "/whats-new/",
    dek: "What was read, found and taken back lately, newest first, and the same record in full.",
    items: [
      { href: "/searched/", label: "What Has Been Read", asks: "What was looked at, and what did it not turn up?" },
      { href: "/corrections/", label: "Corrections", asks: "What did this archive get wrong?" },
      { href: "/changes/", label: "What changed", asks: "What happened, most recent first?" },
    ] },
  { id: "sources-and-method", head: "Sources & method", href: "/research/sources-and-method/", deepHead: "The registers, page by page",
    deepNote: "What each register page says, the pages themselves, and which books can be searched as text.",
    dek: "What this archive stands on, how it reads a register, what the registers say, and the long studies of single sources.",
    items: [
      { href: "/sources/", label: "Sources", asks: "What does this stand on, and where do I check?" },
      { href: "/method/", label: "Method", asks: "What would make you believe or not believe this?" },
      { deep: true, href: "/readings/", label: "What the Registers Say", asks: "What does each document read off a page say, in the register's own words?" },
      { deep: true, href: "/snapshots/", label: "The Pages Themselves", asks: "What does the register page behind a reading look like?" },
      { deep: true, href: "/indexed/", label: "Which Books Are Indexed", atlas: true, asks: "Can this book be searched as text, or must it be read?" },
      { sub: "Deep dives", id: "deep-dives",
        note: "Long studies, each of one kind of source. They are linked from the Sources page too.",
        items: [
          { deep: true, href: "/stones/", label: "The Stones", asks: "What do the memorials themselves say, photographed at Otočac and Senj?" },
          { deep: true, href: "/hungarian-press/", label: "The Hungarian Press", atlas: true,
            asks: "What did the Budapest-era press and official lists print about these surnames?" },
          { deep: true, href: "/found/", label: "Found Beside the Tree", asks: "Who has been read off a page that the family tree has never heard of?" },
        ] },
    ] },
  { id: "checks", head: "Checks", href: "/research/checks/", deepHead: "The archive checking itself",
    dek: "Four pages the build generates from the tree and the research data: the archive checking itself.",
    items: [
      { deep: true, href: "/coverage/", label: "What Rests on a Document", asks: "Which people on the direct line have had a record read, and which rest on the tree alone?" },
      { deep: true, href: "/impossible/", label: "What Cannot Be True", asks: "What do the records say that cannot all be true at once?" },
      { deep: true, href: "/duplicates/", label: "The Same Person, Twice", asks: "Who has been counted as two people?" },
      { deep: true, href: "/buckets/", label: "Labels Where the Father Should Be", asks: "Which labels stand where a parent should be, and how much stands on them?" },
    ] },
];
/* the header menu's shape: [group, ...] with { head, href, items: [[href, label]] }. Only the pages that are not `deep` are in it, and the
   last group is "Deep dives", a heading that is a link and nothing under it. */
const inMenu = (g) => g.items.filter((x) => !x.sub && !x.deep);
export const DEEP_HREF = "/research/deep-dives/";
export const navGroups = [
  ...RESEARCH.filter((g) => inMenu(g).length).map((g) => ({ head: g.head, href: g.href, items: inMenu(g).map((x) => [x.href, x.label]) })),
  { head: "Deep dives", href: DEEP_HREF, items: [] },
];
/* the hub page's sections (src/pages/research/deep-dives/index.astro): every `deep` page, in the order of the groups, under the heading its
   group gives it. A "Deep dives" sub-group inside a group (the three long studies) is a section of its own. */
export const DEEP = RESEARCH.flatMap((g) => {
  const direct = g.items.filter((x) => !x.sub && x.deep);
  const subs = g.items.filter((x) => x.sub).map((x) => ({ id: x.id, head: "Long studies of one source", note: x.note, items: x.items.filter((y) => y.deep) }));
  return [
    ...(direct.length ? [{ id: g.id, head: g.deepHead || g.head, note: g.deepNote || g.dek, items: direct }] : []),
    ...subs.filter((x) => x.items.length),
  ];
});
