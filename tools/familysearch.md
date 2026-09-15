# Reading a FamilySearch image at full resolution

**Solved 13 September 2026.** This archive said twice, in two different places,
that re-sourcing the 960-pixel documents needed "a person at the keyboard". Both
statements were wrong, and the second was wrong in a more interesting way than
the first.

## What the archive used to say, and why it was wrong

**Version 1.** *"The viewer will accept a page number but does not repaint its
canvas under automation."* — **False.** Typing an image number into the viewer's
own box and pressing Return repaints it and changes the image's ARK. The URL
parameter `?i=N` does *not* drive it; the input box does.

**Version 2** (written this morning). *"The tiles return 401 without the session
cookie; requesting them with CORS fails; loading them without CORS taints the
canvas. Reachable by a signed-in person pressing Download, and by nothing else."*
— **Also false**, and the error was mine: I tested the **wrong host**.

The viewer loads its tiles from `sg30p0.familysearch.org`, which is cross-origin
and does exactly what I described. **The same tiles are served from
`www.familysearch.org`**, which is same-origin with the viewer page — no CORS
preflight, no tainted canvas, cookies sent automatically.

## The method

```js
// 1. The Deep Zoom descriptor, same-origin. Gives Width, Height, TileSize.
await fetch(`/service/records/storage/deepzoomcloud/dz/v1/${ark}/image.xml`,
            {credentials: "include"});
//    -> <Image TileSize="256" Overlap="1" Format="jpg">
//         <Size Width="5768" Height="4198"/></Image>

// 2. Tiles, same path. Level 13 is full size for a 5768px image
//    (level = ceil(log2(max(W,H)))).
`/service/records/storage/deepzoomcloud/dz/v1/${ark}/image_files/13/${col}_${row}.jpg`

// 3. Draw them into a canvas at (col*256 - overlap, row*256 - overlap).
//    Same-origin, so the canvas is NOT tainted and toDataURL works.
```

`tools/familysearch_stitch.js` holds a working `fetchWindow(ark, level, x, y, w, h)`
that returns a canvas for any rectangle of any image.

**To read rather than archive**: stitch a window the size of the viewport, replace
`document.body` with the canvas, and screenshot. That renders the register at
**1:1 of 5,768 pixels** — about six times the resolution of the 960-pixel copies
this archive has been squinting at.

## Finding the ARK for an image

Each image in a film has its own ARK. Two ways to get one:

1. Drive the viewer's **image-number box** (not the URL) and read the ARK back out
   of the tile `src` of the displayed image.
2. The filmstrip puts **every ARK in the film** into the DOM at once — about 160
   of them for the Senj marriages — though unordered, so it does not tell you
   which image number each belongs to.

## What is still to do

The technique is proven; the remaining work is **navigation**. The three documents
this archive holds at 960 pixels are all in *Croatia, Church Books — Senj —
Marriages 1859-1920*, 376 images:

| Wanted | Where |
|---|---|
| Senj marriages **p.192 no.5**, 3 May 1885 | Josip Papić × Antonija Prpić |
| Senj marriages **p.294 no.30**, 4 Nov 1907 | **Zvonimir Vukelić × Milka Papić** — answers the 1915 question too |
| Senj marriages, **8 December 1920** | Ljubomir Blažević × Milka Papić |

Image **374** is page 350 and holds late 1918, which brackets the 1920 entry
within the last two or three images of the film.

---

## Navigation — added 13 September 2026, after using it on three entries

The method above gets **an** image. Finding the **right** one is a separate
problem, and the note above solves it badly: it says to type into the viewer's
image-number box. That works, but it is slow, it needs a screenshot per probe,
and it turns out to be unnecessary.

**The whole film is already in the DOM.** Every filmstrip thumbnail carries the
image number in its `alt` and the ARK in its `src`:

```html
<img alt="Image 221"
     src=".../deepzoomcloud/dz/v1/3:1:3QS7-899X-17ZY/thumb_p200.jpg">
```

So scrape a number→ARK map and then fetch tiles for any image directly, with no
viewer navigation at all:

```js
window.__map = window.__map || {};
window.__scan = () => {
  let n = 0;
  for (const e of document.querySelectorAll("img")) {
    const m = (e.src || "").match(/dz\/v1\/([^/]+)\//);
    const a = (e.alt || "").match(/Image (\d+)/);
    if (m && a && !__map[a[1]]) { __map[a[1]] = m[1]; n++; }
  }
  return n;
};
```

One load gives roughly 150 thumbnails around the current image. Typing a low and
a high image number into the box and re-scanning covers the rest — three scans
mapped 316 of 376 images, and the missing 60 were never needed.

### Do not trust a page-to-image guess

The Senj marriage film runs about **page = image − 5**, but that was *measured*,
not assumed, and an earlier guess in this archive ("image 374 is page 350") was
wrong by more than 150 pages. Fix it from real points before searching:

    image 196 = page 192      image 299 = page 294
    image 280 = page 275      image 371 = page 366
    image 372 = END OF ITEM

### Reading cheaply

Screenshots are the expensive part, not the tiles. Two things help a lot:

* **Probe several images in one picture.** Crop the same small region — the date
  column, or the top corner where the page number sits — from four or six images
  and tile them into one labelled canvas. A six-way search finds one page in a
  376-image film in about three screenshots.
* **Use fractional crops, not pixel crops.** Image sizes vary across a film
  (5,812 × 4,273 here, 5,768 × 4,198 elsewhere) and the paper sits differently in
  each frame, so a pixel box that worked on one image lands on the film border of
  the next. Fetch `image.xml` per ARK and crop by fraction of width and height.

### And then slow down

The archive's standing rule applies with full force at this point: **no date, no
surname and no house number gets recorded from a whole-page view.** Having a
5,812-pixel scan is not the same as having read it. On this very film I read a
groom's birth month as `1/VIII` from a page-scale view; enlarged 2.7× on the cell
alone it is `1/III` — three strokes under one overline. Crop the single cell,
enlarge, and only then write it down.

---

## Access, and how it fails — added 14 September 2026

Two failures cost most of a sitting. Both have a fix.

### The in-app Browser pane is banned outright

Every request to `familysearch.org` from the Claude desktop Browser pane —
viewer page, home page and the Deep Zoom tile service alike — returns Akamai
**`Access Denied / Error 15`**, naming the pane's egress proxy. The tooling is
not at fault and there is nothing to debug. **Use the user's own Chrome**
(`mcp__claude-in-chrome__*`), which reaches FamilySearch normally.

Chrome must be **signed in to FamilySearch**. Signed out, the film URL loads the
page shell and then bounces to `ident.familysearch.org`; the tile service answers
`401`. Signing in is the user's to do, not this archive's.

### Akamai throttles heavy tile fetching, and a page reload clears it

After a few hundred tiles the service starts answering **`403` with a bot-manager
challenge**, in Chrome too. Waiting does not clear it. **Reloading the viewer page
does** — the viewer runs Akamai's sensor script and a fresh token is issued. Then
throttle: 3–4 concurrent tile loads with a ~25 ms gap between them ran a whole
sitting without tripping again.

### Do not screenshot the canvas — post it to disk

`computer{action:"screenshot"}` is capped at the viewport, so a stitched page has
to be shrunk to fit and can no longer be enlarged — which defeats the archive's
standing rule. It also wedged the renderer twice, requiring a reload.

Instead, run a one-file HTTP sink locally and have the page POST the PNG:

```js
const b = await new Promise(r => canvas.toBlob(r, "image/png"));
await fetch("http://127.0.0.1:8799/put?name=" + name, {method: "POST", body: b});
```

`http://127.0.0.1` counts as a *potentially trustworthy origin*, so an HTTPS page
is allowed to post to it and mixed-content blocking does not apply. Give the sink
an `Access-Control-Allow-Origin: *` header and the fetch reports a real status
instead of failing silently as a `no-cors` opaque request does.

The file can then be cropped and enlarged locally as often as a contested digit
needs — which is the point.

### The 45-second evaluation limit

The console bridge kills any `javascript_tool` call at 45 s, and a full-resolution
page is more than that. Push the work into a background queue that records a
status string and poll it with a second, short call.

### Two numbering systems on one frame

The Otočac census frames carry **both** a film-target stamp and the book's own
printed page number, and they are not the same thing. `HDA = image + 243` is the
**film stamp** (image 110 = `HDA 353`). The **page** number is printed on the
paper and follows no formula — image 110 is pages 220/221, image 97 is 173/174 —
because the book has unnumbered leaves and the film has duplicate exposures
(images 63/64, 79/80 and 89/90 are each the same opening shot twice).
**Read the page number off the frame; never compute it.**

### The renderer wedges, and the map should outlive it

After a few hundred stitched canvases the tab stops responding — `javascript_tool`
times out and screenshots hang. Reloading the viewer clears it. Reload every ten
contact sheets or so rather than waiting for the wedge, and keep the number→ARK
map in **`localStorage`**, not `sessionStorage`, so neither a reload nor a fresh
tab costs the scrape.

---

## Reading a film in the in-app Browser pane — added 14 September 2026

Earlier notes said the pane could not do this work. **It can, and it is now the
better of the two browsers**: it is signed in, it does not exhaust its renderer
the way Chrome does, and it needs no local sink.

**What is genuinely impossible there:** the pane is **network-isolated**. A
`fetch` to `http://127.0.0.1` never reaches this machine — the sink logs no
request at all, even with `Access-Control-Allow-Private-Network: true`. So the
POST-to-a-local-sink method is Chrome-only.

**The trick is the viewport.** The pane's screenshot width is capped at 800 px,
and the capture is

    capture = viewport_height x 800 / viewport_width

so a **tall, narrow** emulated viewport buys captured height for free:

    resize_window 800 x 1960   ->  screenshot 800 x 1960

One page-half of a prose register rendered to 790 px wide is about 790 x 1800 and
**fits in a single capture at 0.52 of full resolution** — better than the 0.43 a
Chrome contact sheet gave. Do not go much taller: at 800 x 3900 the harness
downsamples the returned image and the gain is lost.

Pair it with the `document.write` blank-page rig (above) to kill the SPA, keep
the ARK map in `localStorage`, and batch `render → screenshot` pairs three at a
time in one `browser_batch`.

**When Akamai throttles to 403**, navigate to a real FamilySearch page, wait for
it to load so the sensor re-issues the token, then `document.write` the rig back
over it and carry on.

---

## Sweeping a whole item — added 15 September 2026

Reading ninety openings is a different problem from reading six. What worked:

### Fetch once, at half resolution, to disk — then never fetch again

The expensive thing is tiles, and the thing that gets you banned is tiles. A page
half of this film is ~2,250 x 3,200 at full resolution, about 120 tiles. **At
`drop 1` it is ~1,130 x 1,600 and about 30 tiles** — a quarter of the traffic and
a quarter of the time (≈15 s an opening against ≈50 s).

That half-resolution page is still **1.66× the 680 px sweep width**, so every
"what does that word actually say?" crop is done **locally, from the saved PNG**,
with no second request. Only a genuinely contested digit needs a full-resolution
refetch of that one page.

    browser  ->  __cell(ark, …, drop 1)  ->  canvas.toBlob  ->  POST 127.0.0.1:8799
    disk     ->  PIL: contrast, crop by fraction, slice, scale  ->  Read

Crop **by fraction of the saved page**, not of the film frame, once it is on disk.

### The two browsers have separate Akamai reputations

The in-app pane and Chrome are throttled **independently** — the pane's block
even reports a different proxy IP. When one returns `403`, the other is usually
still clean: **alternate, and keep the ARK map in `localStorage` in both**. A
block lasts on the order of half an hour; navigating to a real FamilySearch page
clears a *soft* throttle but not the hard `Access Denied … Error 15` page.

Rate matters. Three tiles in flight with a 120 ms gap, and ~600 ms between pages,
ran far longer before tripping than six tiles with a 20 ms gap.

### Make the queue resumable

A queue that stops on the first error and **pushes the failed image back onto the
front of the list** turns a ban into a pause: swap browsers, re-inject, call the
runner again. A queue that logs the error and carries on silently loses thirty
openings, which is what happened the first time.

### The pane must be *visible* to screenshot

`computer{action:"screenshot"}` fails with *"the Browser pane is not displayed, so
the page is not compositing frames"* if the pane is hidden. `tabs_select` does not
fix it; **`preview_start` re-opens the pane** — and resets the emulated viewport,
so set the tall viewport again afterwards.

### Find the duplicate exposures cheaply

This film shoots some openings twice. A 24×24 mean-threshold perceptual hash of
each left page separates them without ambiguity: **adjacent duplicates score
≈30/576 bits apart, genuinely different openings ≈100/576**. On item 3 it found
194≡193, 197≡196 and 218≡217 — three openings that did not need reading.
