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
        body: `She was born into a household of **seven children** in a town whose economy had already collapsed — the railway had bypassed Senj half a century before she was born. Her mother supervised women rolling cigarettes; her father went to sea. [Milka's two marriages →](${u("/people/milka-lucia-papic/")})

She is the reason this archive exists, and she is also its best-documented person. Her own birth is confirmed from outside the family tree by the sworn translation of her son's Yugoslav birth extract. [Read what it says →](${u("/certificate/")})`,
      },
      {
        title: "The war, 1941 to 1945", grade: "inf",
        body: `She was **fifteen** when the Independent State of Croatia was declared and the war reached the coast, and **nineteen** when it ended and her brother [Oto](${u("/people/oto-blazevic/")}) did not come home. Her husband, [Ivan Anton Defranceski](${u("/people/ivan-anton-defranceski/")}) (1925–1995), spent part of the war as a sixteen-year-old labourer in a German power works. [The Arolsen cards →](${u("/arolsen/")})`,
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
        settle: `The setting is on the pages for [Oto](${u("/people/oto-blazevic/")}) and [the Arolsen cards](${u("/arolsen/")}).`,
      },
      {
        n: 3, grade: "lore · no record either way",
        said: "She sang at the **Hotel Therapia** in Crikvenica, her husband's home town, where their first child was born.",
        verdict: "The tree records no occupation for her whatsoever. Her entire event list is three lines: born, immigrated, died. Set against her mother, entered nadglednica u tvornici duhana (a supervisor in the tobacco factory), and her grandmother, a nadničarka, that silence is its own kind of record. This is the only thing anyone has ever said about what Hedviga did.",
        settle: `The venue is checkable, which lore rarely is. The Therapia opened in **1895** as the *Nadvojvoda Josip* (Archduke Joseph) with 120 beds, and was renamed **Hotel Therapia in 1899** when a hydropathic institute was established inside it. With the Miramare of 1906 it is the building that turned Crikvenica from a village into an Austro-Hungarian health resort. A woman singing there was singing in the grandest room on that stretch of coast. [Her mother, the tobacco-factory supervisor →](${u("/people/milka-lucia-papic/")})`,
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

  "milka-lucia-papic": (u) => ({
    lede: "Hedviga's mother is the best-documented person in this archive: a birth entry, two marriage entries, a gravestone and a factory. Her life can be told almost entirely from records, and it is not the life the family tree describes.",
    chapters: [
      {
        title: "Born 9 October 1886, Senj baptisms, page 122, entry 96", grade: "doc",
        body: `The tree carries **Milka Lucia Papić** as the wife of Ljubomir Blažević and the mother of seven. The registers carry a woman who was **married twice**, **widowed at twenty-eight**, and spent **more than forty years** in the same tobacco factory — going in as a floor worker and coming out supervising it.

**Name:** Milka Lucia — *zakonita*, legitimate.
**Born / baptised:** **9 October 1886**, baptised **17 October**, by the chaplain (*kapelan*) at Senj.
**Father:** [Josip Papić](${u("/people/josip-anton-papic/")}), ***trhonoša***, a load-carrier.
**Mother:** [Tonka *rođ.* Prpić](${u("/people/antonija-tonka-perpic-prpic/")}).
**Godparents:** Josip Glavičić, also a *trhonoša*, and Ivka Filipović.
**Later annotation:** the margin was written up again when she died: the register records the death entry and the date **7.9.1971**, endorsed at Senj **30.9.1971**.

**A small correction.** The family tree gives her baptism as **19 October**. The register says **17**. The archive follows the register.

Both her father and her godfather are *trhonoše* — men who carried other people's goods on their backs for a fee. That is not a coincidence; it is a social world. In a port town whose port had died, [the porters knew the porters](${u("/senj/")}).`,
      },
      {
        title: "First marriage, 4 November 1907", grade: "doc",
        body: `Aged twenty-one, she married [**Zvonimir M. Vukelić**](${u("/people/zvonimir-matei-vukelic/")}) — and nothing in the family tree's account of her had ever mentioned it. The entry is Senj marriages, page 294, entry 30.

**Date:** **4 *studenoga* (November) 1907**, Senj.
**Groom:** Zvonimir M. Vukelić, *gostioničarski pomoćnik* — innkeeper's assistant. Born 13 January 1883. Bachelor.
**Bride:** Milka Papić, ***radnica u tvornici duhana*** — a worker in the tobacco factory. Born 9 October 1886. Unmarried.
**His parents:** Vukelić *pl.* Petar, *gostioničar* — innkeeper — and **† Vjekoslava**, surname read as Putnić (possibly Putinić — not settled). **The dagger stands before Vjekoslava, not before Petar:** it is the *mother* who was dead in 1907.
**Her parents:** Joso Papić, *gostioničar*, and Tonka *rođ.* Prpić.
**Witnesses:** Koloman *pl.* Vukelić, ***meštar u tvornici duhana*** — **master** in the tobacco factory, not a broker — and Franjo Olivieri, *trgovac*, merchant.
**Banns:** married by **episcopal dispensation**, with the banns read once — on **3 November**, the day before the wedding — instead of the usual three times.

**Read again at full resolution, 13 September 2026 — and three things on this table changed.** The copy held in the tree is **960 pixels** wide; the same opening was fetched from FamilySearch at **5,812 × 4,273** (image 299, 3:1:3QS7-L99X-175J). This page had Petar Vukelić *marked deceased* and his wife as **Vica**. The register reads “Vukelić pl. Petar gostioničar, i † Vjekoslava Putnić” — the cross belongs to **Vjekoslava**, and her name is not Vica. And Koloman was called a *broker* here; the word is ***meštar***, master — a grade this archive already maps on [the factory ladder](${u("/work/")}).

**What did not change:** both Vukelić men carry *pl.*, Milka is already a tobacco-factory worker in 1907, and her birth is written “1886, 9/10” — which her 1920 entry repeats as “9/X”, thirteen years apart in two different hands. [What changed →](${u("/corrections/")})

**Her father has changed trade.** In 1886 Josip Papić is a *trhonoša*. By 1907 the register calls him ***gostioničar*** — an innkeeper. The tree lists his occupations as “Trhonosa, bremenar, gostionicar”, and the registers show that string is a **sequence**: the porter kept the money and bought a bar. **And the middle term now has its own document.** His own marriage entry — Senj, 3 May 1885, read at full size the same day — enters him as ***bremenar***, and the 1891 baptism of a child calls him *težak*. Four documents, four points on one line: trhonoša 1886 · bremenar 1885 · težak 1891 · gostioničar 1907. [The Papići →](${u("/papic/")})

The one-day dispensation is worth noticing without over-reading. Her daughter **Miroslava** was born in **1907**. A hurried wedding and a child in the same year is a familiar shape, but the register does not date the birth and this archive does not claim to know which came first.`,
      },
      {
        title: "Two children, and a widow at twenty-eight, 1915", grade: "tree",
        body: `**The Vukelić children.** [Miroslava “Mica” / “Nana” Vukelić](${u("/people/miroslava-mica-nana-vukelic/")}) (1907–1993), who married **Rahamin Levi** (1904–1984) of **Pirot**; and [Josip Vukelić](${u("/people/josip-vukelic/")}) (1913–2004), born at Senj. They are **Hedviga's half-brother and half-sister**, and they were in the tree all along — invisible to the first build of this archive only because a sweep of somebody's *ancestors* never walks sideways.

Zvonimir Vukelić **died in 1915**, aged thirty-two, in the middle of the First World War. Milka was **twenty-eight**, with a girl of eight and a boy of two. Nothing in this archive says how he died, and 1915 is a year in which a man of thirty-two might die many ways. [Open questions →](${u("/open-questions/")})`,
      },
      {
        title: "Second marriage, 8 December 1920", grade: "doc",
        body: `Thirteen years after the first wedding and five years after the death, she married [**Ljubomir Blažević**](${u("/people/ljubomir-blazevic/")}), a sailor, at Senj (marriages, page 366, entry 41). The register enters her under her married name: **Milka Vukelić, *udova*** — widow.

She is still ***radnica u tvornici duhana***. Thirteen years on from her first marriage entry, the same job, the same words. [The full entry →](${u("/marriage-1920/")})

Seven children followed, of whom [**Hedviga**](${u("/people/hedviga-blazevic/")}) was the fourth, born 3 August 1926 — and [Oto](${u("/people/oto-blazevic/")}), who did not come home from the war.`,
      },
      {
        title: "The factory, after 1920: from worker to supervisor", grade: "",
        body: `**1907, aged 21:** *radnica u tvornici duhana* — **worker**, per the marriage register.
**1920, aged 34:** *radnica u tvornici duhana* — still a **worker**, per the marriage register.
**Later:** **supervisor of workers** at the cigarette factory, per the family tree — at *Ul. Stjepana Radića 4*, “now a textile factory”.
**And beside her:** **Anka Blažević** (1893–1953), her husband's sister, a *radnica* in the same factory.

This is the only career progression documented anywhere in this archive, and it belongs to a woman. In a town where the men are recorded as day labourers, porters and sailors, **the steady wage was hers**. [Why there was no other work →](${u("/senj/")})`,
      },
      {
        title: "Died at Senj, 7 September 1971", grade: "doc",
        body: `She died at Senj, aged eighty-four, and is on the family stone as **MILKA BLAŽEVIĆ *rod.* PAPIĆ ✳ 1886 † 1971** — under her *maiden* name, not the Vukelić name she carried into her second wedding, and beside the son whose body was never found. [The grave →](${u("/grave/")})`,
      },
      {
        title: "", grade: "",
        body: `**What is still missing.** This archive does not hold Zvonimir Vukelić's death entry for 1915, which would say how she was widowed; Miroslava's 1907 birth entry, which would fix the order of wedding and child; or any record of what Milka did between 1915 and 1920, alone with two children in a town with no work.`,
      },
    ],
    lore: [],
    photos: [
      { src: "/photos/line/4505839-milka-lucia-birth-1886.jpg", alt: "Senj baptismal register 1886, page 122, entry 96 — Milka Lucia Papić",
        cap: "Senj, Roman Catholic baptisms, <em>Str. 122</em>, entry 96. Her entry is the second from the bottom of the left-hand page." },
      { src: "/photos/line/4502611-zvonomir-and-milka-marriage.jpg", alt: "Senj marriage register 1907, page 294, entry 30",
        cap: "Senj marriages, page 294, entry 30, boxed in red on the scan as held in the tree." },
    ],
  }),

  "oto-blazevic": (u) => ({
    lede: "Died at twenty-two in the last year of the war. The family preserves two accounts of how; they cannot both be true, and there is no grave to ask.",
    chapters: [
      {
        title: "Senj, October 1943", grade: "inf",
        body: `He was **twenty** when [German aircraft destroyed about half of Senj on 7–8 October 1943](${u("/senj-1943/")}), killing thirty of the town's residents — among them, on the second day, his uncle by marriage **Pavao Kosina**. He had already seen the war close up.`,
      },
      {
        title: "The Syrmian Front, 1944 to 1945", grade: "inf",
        body: `The war in Slavonia in **1945** is not a vague setting. It is one of the best-documented killing grounds of the European war's last months. The **Syrmian Front** ran from **21 October 1944 to 12 April 1945** across Syrmia, **Slavonia** and Baranja. The Yugoslav Partisans lost **more than 13,500 killed** covering roughly 140 kilometres between Belgrade and Vinkovci over nearly six months of winter fighting. When the front broke on 12 April, the 1st and 3rd Armies advanced **west through Slavonia**.

A man born in 1923 was **twenty-one or twenty-two** in that campaign — precisely the cohort mobilised into it, much of it from newly-liberated Croatia with minimal training. And an unknown grave is the ordinary outcome, not the strange one: thousands of those dead were buried where they fell.

**The detail that rings true.** That the family *cut his name into his grandparents' stone* because there was no body is a specific, unglamorous, expensive act. People do it when someone does not come back from somewhere far away. It is much harder to explain if he died of a snakebite on the hill above the town.`,
      },
      {
        title: "Died in 1945: how this archive leaves it", grade: "tree",
        body: `**Documented:** born 1923, Senj. Died 1945, with the death place entered in the tree as **Senj**. Son of Ljubomir Blažević and Milka Papić; brother of Leo, Karmela, Hedviga, Ljubomir, Mario and Anton.

**Contradiction: still unresolved as to cause.** The tree's own *death place* of Senj agrees with neither account cleanly — it contradicts Slavonia outright, and it is also exactly what a family would enter when the real place was unknown.

**What would settle it.** The Croatian State Archives hold Second World War military and civil death records, and the *Yugoslav war victims register* (*Popis žrtava rata*) is searchable by name and birth year. A single entry for **Oto Blažević, b. 1923, Senj** would end the question in either direction. Nobody has yet looked. [Open questions →](${u("/open-questions/")})`,
      },
      {
        title: "Grave: his name is cut into the family stone", grade: "doc",
        body: `A photograph of [the Blažević plot at Senj](${u("/grave/")}) — recovered from the MyHeritage media library in September 2026, where it had been sitting untouched — can be checked against Nives Blažević's account line by line. **It matches.**

**She said:** “they put his name in … [the] grave”. **The stone:** **OTO BLAŽEVIĆ ✳ 1923 † 1945** is cut into it, between his mother and his brother Mario.
**She said:** “and now **Leo** is there, and **Katica**”. **The stone:** a separate, later, black plaque below reads **LEO ✳ 1920 † 2008** and **KATA ✳ 1924 † 2007** — Katica.
**She said:** “his grandmother's and grandfather's grave”. **The stone:** the names are Oto's *parents*. But **Nives Blažević is a generation younger** — Ljubomir and Milka were *her* grandparents. She is describing the grave from where she stands in the family, which is what people do.

**What this does and does not settle.** It does *not* show that Oto died in Slavonia. It shows that the witness who said so **knew this grave in exact detail**, including two burials added more than sixty years after his death — and that the family commemorated him on a stone rather than at a grave of his own, which is what you do for a man who does not come back. **The snakebite account now sits second.**`,
      },
      {
        title: "", grade: "",
        body: `This archive keeps both accounts because pretending otherwise is how family myths become family history — and because one of these two people was right. [Method →](${u("/method/")})`,
      },
    ],
    loreDek: "This page exists because the record contains a contradiction that has been kept rather than tidied away. Both accounts are written into the same note on Oto's entry, attributed to two different people, and this archive reproduces them exactly as they stand.",
    lore: [
      {
        n: 1, grade: "lore · now second",
        said: "“Bitten by snake.” Attributed in the tree to **Ivan Defranceski**.",
        verdict: "Ivan Anton Defranceski (1925–1995) was Hedviga's husband and Oto's brother-in-law — two years younger than Oto, and alive in the same town at the time. The Velebit has the horned viper, Vipera ammodytes, Europe's most dangerous snake, and a shepherd or a labourer on that mountain was genuinely at risk.",
        settle: `The tree's own death place of Senj fits this account no better than the other. The Croatian State Archives' death records and the *Popis žrtava rata* are searchable by name and birth year. [Open questions →](${u("/open-questions/")})`,
      },
      {
        n: 2, grade: "lore · corroborated in its checkable parts",
        said: "“The late Otto Blažević was the brother of Ljuba, Leo, Aunt Karma, Aunt Seka … he died in the war somewhere in **Slavonia**, his grave is unknown, so they put his name in his grandmother's and grandfather's grave — and now Leo is there, and Katica.” Attributed in the tree to **Nives Blažević**.",
        verdict: "This one names his siblings correctly, including “Aunt Seka” — Hedviga's own nickname — which is a good sign that the speaker knew the family well. Its checkable parts match the stone: his name is on the family grave, and Leo and Katica were added to it later. It does not show that he died in Slavonia.",
        settle: `The stone is read line by line in the chapter on the grave above. [The grave →](${u("/grave/")})`,
      },
    ],
    photos: [
      { src: "/photos/line/4503429-blazevic-grave.jpg", alt: "The Blažević family grave at Senj, with Oto's name on it",
        cap: "LJUBOMIR BLAŽEVIĆ ✳1891 †1966 · MILKA BLAŽEVIĆ <em>rod.</em> PAPIĆ ✳1886 †1971 · <strong>OTO BLAŽEVIĆ ✳1923 †1945</strong> · MARIO BLAŽEVIĆ ✳1933 †1984 — and, on a later plaque, KATA ✳1924 †2007 and LEO ✳1920 †2008." },
    ],
  }),
};
