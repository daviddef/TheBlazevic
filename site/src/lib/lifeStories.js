/* THE LIVES TOLD IN FULL (people pages v2, story mode). A page in story mode tells a life on a timeline (kit/lib/personstory.js storyOf): where the
   person came from, birth, life, death, what they left behind. The family is the first stop, so the story mode draws no chart.

   Each entry here is hand-written prose that used to be a page of its own (Hedviga's was /hedviga/, 211 lines of Astro); it is the same words, moved
   under the person's page and cut into the stops. `chapters` are {title, body, grade} in markdown (grade: doc | inf | lore | tree), `lore` the claims the
   family makes beside what the record holds, and `photos` the pictures. The entry is a function of u() so a link carries the deployment base.
   A person with no entry here keeps the chart page. Nothing about a living person goes in an entry: their name and relationship are drawn from the
   family data under the living rule, and the prose may not give them a date or a place. */
export const STORIES = {
  "hedviga-blazevic": (u) => ({
    lede: "Born in a dying port on the Adriatic, died seventy-five years later on the Highveld, having crossed a world war, a country that stopped existing, and two continents.",
    chapters: [
      {
        title: "Born at Senj, 3 August 1926", grade: "doc",
        body: `She was born into a household of **seven children** in a town whose economy had already collapsed — the railway had bypassed Senj half a century before she was born. Her mother supervised women rolling cigarettes; her father went to sea. [Milka's two marriages →](${u("/milka/")})

She is the reason this archive exists, and she is also its best-documented person. Her own birth is confirmed from outside the family tree by the sworn translation of her son's Yugoslav birth extract. [Read what it says →](${u("/certificate/")})`,
      },
      {
        title: "The war, 1941 to 1945", grade: "inf",
        body: `She was **fifteen** when the Independent State of Croatia was declared and the war reached the coast, and **nineteen** when it ended and her brother [Oto](${u("/oto/")}) did not come home. Her husband, [Ivan Anton Defranceski](${u("/people/ivan-anton-defranceski/")}) (1925–1995), spent part of the war as a sixteen-year-old labourer in a German power works. [The Arolsen cards →](${u("/arolsen/")})`,
      },
      {
        title: "Marriage and three children", grade: "tree",
        body: `She married into the Defranceski family. Her first two children were born in **Yugoslavia**, at Crikvenica and Senj. The record has her at **Senj in the early 1950s**, where her youngest child was born.

The tree also lists [Ladislav Carr](${u("/people/ladislav-carr/")}) as a spouse, with no date or place.`,
      },
      {
        title: "Twenty years and more this archive cannot account for", grade: "lore",
        body: `Between Senj in the early 1950s and South Africa in April 1975 there is **nothing at all** — more than twenty years, an emigration, and an entire country she is only known to have been in because of the words *“from Zimbabwe”* on the later entry.

Three things are remembered in the family about that crossing. They are set down below as **what is said**, beside what the record holds, and the two do not entirely agree.`,
      },
      {
        title: "From Zimbabwe to South Africa, April 1975", grade: "tree",
        body: `It is worth being exact about the order, because the record is: she was in **Zimbabwe first**, and came south to **South Africa in April 1975**.

She is described as having married [Santou (Shemtov) Isaac Codron](${u("/rhodes/")}) (1913–1997), born on Rhodes, around **1973**, which places that marriage in the Rhodesian years, not the South African ones.`,
      },
      {
        title: "Died at Johannesburg, 30 October 2001", grade: "tree",
        body: `She died at **Johannesburg on 30 October 2001**, aged 75. The cause is written down plainly: cancer of the rectum, spread to the liver.

Her husband Ivan Anton Defranceski died at Senj on **30 October 1995** — six years earlier, to the day. This archive records the coincidence and claims nothing by it. Both dates come from the family tree rather than from a certificate seen here, and a shared date is exactly the kind of detail that gets tidied into place by memory. **Two death certificates would settle it**, and they are the first documents on the wanted list. [Open questions →](${u("/open-questions/")})`,
      },
      {
        title: "", grade: "",
        body: `The notes attached to her record are **machine-written**: a SmartCopy reference from Geni, and a MyHeritage record link. There is no biography in her own words. Her record cites two independent trees, the *Defranceski Family Site* and the *Boras Web Site*, which is corroboration between witnesses, not between documents. This archive keeps that distinction. [Why →](${u("/method/")})`,
      },
    ],
    loreDek: "Family lore, recorded September 2026. Each of these is set down as it was told, beside what the record holds. A migration leaves paper — a passenger list, a permit, a naturalisation file, a school enrolment for three children — and none of it has been looked for, because until now this archive did not know there was a Rhodesian decade to look in.",
    lore: [
      {
        n: 1, grade: "lore · the record does not allow it",
        said: "“They went in 1948.” Remembered as the year Ivan and Hedviga left.",
        verdict: "The record does not allow it. Their second and third children were born at Senj, in the 1950s, so the family was in Croatia for years after 1948. The year may be anchored to another event in the family: the first child was born at Crikvenica. A date attaching itself to the wrong event is the commonest thing in this archive.",
        settle: `That is how [a man came to be born after his own granddaughter](${u("/people/caetano-bacchi/")}). A passenger list, a permit or a naturalisation file would fix the year. [What would find it →](${u("/open-questions/")})`,
      },
      {
        n: 2, grade: "lore · the record is silent",
        said: "Why they went: a **post-war migration**, for better and safer conditions.",
        verdict: "Nothing in the record speaks to motive at all; not a single document here says why anyone left. What the record does supply is the setting: a town whose economy had collapsed seventy years earlier, a brother dead in 1945 with no grave, and a husband who had spent the war from the age of sixteen as a labourer in a German power works.",
        settle: `The setting is on the pages for [Oto](${u("/oto/")}) and [the Arolsen cards](${u("/arolsen/")}).`,
      },
      {
        n: 3, grade: "lore · no record either way",
        said: "She sang at the **Hotel Therapia** in Crikvenica, her husband's home town, where their first child was born.",
        verdict: "The tree records no occupation for her whatsoever. Her entire event list is three lines: born, immigrated, died. Set against her mother, entered nadglednica u tvornici duhana (a supervisor in the tobacco factory), and her grandmother, a nadničarka, that silence is its own kind of record. This is the only thing anyone has ever said about what Hedviga did.",
        settle: `The venue is checkable, which lore rarely is. The Therapia opened in **1895** as the *Nadvojvoda Josip* (Archduke Joseph) with 120 beds, and was renamed **Hotel Therapia in 1899** when a hydropathic institute was established inside it. With the Miramare of 1906 it is the building that turned Crikvenica from a village into an Austro-Hungarian health resort. A woman singing there was singing in the grandest room on that stretch of coast. [Her mother, the tobacco-factory supervisor →](${u("/milka/")})`,
      },
      {
        n: 4, grade: "lore · corrected",
        said: "“I believe it closed down.”",
        verdict: "It did not. The building stands and is still a hotel. It was bought in 2013 by the Austrian hotelier Wilfried Holleis, renovated, and renamed Kvarner Palace: four stars, 92 rooms. What closed was the name, not the house.",
        settle: "The room she is remembered singing in is still there and can be walked into, and that is a rarer thing than a document.",
      },
    ],
    photosDek: `Recovered from MyHeritage, September 2026. None of these are in the GEDCOM, because MyHeritage does not export media. They are **480-pixel renderings**, not the originals; the CDN signs each URL against its size, so a bigger one cannot simply be asked for.`,
    photos: [
      { src: "/photos/hedviga/hedviga-06-500804.jpg", alt: "Portrait of a woman in a bold floral print raising a glass, late 1960s",
        cap: "<strong>Almost certainly Hedviga</strong>, <em>c.</em> late 1960s — the best likeness in the set, and the same face as the 1980s group below." },
      { src: "/photos/hedviga/hedviga-05-500852-granny-heddies-photos-25.jpg", alt: "Colour family photograph, 1980s, with television and video recorder",
        cap: "Captioned <em>“Granny Heddies Photos-25”</em>. Colour, <em>c.</em> 1980s, a television and a video recorder behind — this is Africa, not Senj." },
      { src: "/photos/hedviga/hedviga-01-504176.jpg", alt: "Multi-generational family group in a garden, 1950s",
        cap: "Eleven people in a garden, <em>c.</em> 1950s. The two older women seated at the centre are in black — widows' mourning. Nobody in it is identified." },
    ],
    withheld: [
      "<strong>Two photographs of the family with its children are not shown.</strong> The children in them are living, and this archive shows no photograph of a living person.",
      `<strong>Not a photograph, and not shown.</strong> The sworn translation of her son's Yugoslav birth extract — the one document here that confirms her own birth from outside the family tree. The scan carries the date of birth of a man who died in 2026, and it is held back. <a href="${u("/certificate/")}">Read what it says →</a>`,
    ],
    photosNote: "<strong>Two of these three photographs are unidentified.</strong> The tree carries them as filenames — <em>1595624858.9990501</em>, <em>1134835622</em> — with no names, dates or places attached. Anyone who can put a name to a face in them should say so; that is the single most useful thing that could happen to this page.",
  }),
};
