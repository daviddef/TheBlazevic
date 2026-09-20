# Image 75 reads «Vivõz», and the film enumerates in one call

**21 September 2026.** [Row 7](/worklist/) had one hole in an otherwise complete map: of the
*Pagus* headings in the Otočac *Stanje duša*, every village was mapped —
*Ottosaz, Luka, Dubrava, Novoselia, Lieška, Kostelievo Selo, Obilje, Beljue, Šumećica* —
and **image 75 resisted**.

## What it says

The heading is **written vertically down the left margin**, which is why it resisted: it is
not where the other headings are. Read at **4×** off the full-resolution scan:

> **«Vivõz»** — a macron over the *o* — **written twice**, on two successive openings,
> under the word **Pagus.** A shorter word stands above it, **«Sched…»** or **«Scheiz…»**,
> not read out.

## And it is deliberately NOT identified

**A macron in this hand is an omitted *n* or *m*, so the name may be «Vivonz».** And this
book renders a final **z** as **č** — *«Ottosaz»* is **Otočac** — so the Latin letters are
not the Croatian name. Between the two, a modern identification would be a guess dressed as
a reading.

**What the row wanted was the hole filled, and a transcription is not an identification.**
The letters are on the page now instead of the word «unresolved», which is as far as the
image goes. Naming the village wants a gazetteer of the Otočac parish, not a sharper crop.

**There is a second hole the row does not mention.** `_villages` in the film map records
**image 110** as *«another village»*, equally unnamed. Row 7 says «the one village»; there
are two.

## The part worth more than the village name

The film map carried an instruction: *«rebuild the rest by opening the thumbnail grid in the
viewer and scraping alt="Image N"»*. **That is obsolete. The whole film enumerates in one
call.**

    1. GET any known image's ark with  Accept: application/json   → its `apid`
    2. GET <das>/v2/<apid>/parents                                → the film's parentApid
    3. GET <das>/v2/<parentApid>/children                         → ALL 384 images
                                                                    as {apid, name, order}

where `das` is `https://sg30p0.familysearch.org/service/records/storage/dascloud/das`. For
this film the parent is **`TH-1971-28350-2093-94`**.

**And an image can then be read WITHOUT AN ARK AT ALL**, at `<das>/v2/<apid>/dist.jpg` —
which is how image 75 was read here, since no ark for it had ever been recorded.

**Verified before use**: image 95's apid from `/children` matches the ark this archive
already had for image 95. The enumeration is not a guess about the ordering.

**This bears on [row 21](/worklist/)**, which costs every page read at «about twelve round
trips». Finding the image is no longer part of that cost, and neither is having an ark.
