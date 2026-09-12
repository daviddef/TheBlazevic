# Sweeping the MyHeritage media library

**Status: partly mapped, not automated. 13 September 2026.**

The direct line was swept once and produced `sources/media/manifest.psv` (94
items). The wider register has never been swept: of **1,297 published people,
58 have an image and 1,239 have none**.

## What is known

The site is **Defranceski Site (23Me)**, id
`OYYV7AGVV4FMSGNWXC6TO74JQDUMOYA`, and the photo library holds **4,500 items**.

GraphQL lives at:

```
POST https://www.myheritage.com/web-family-graphql/<operation_name>/
```

Two operations matter:

| Operation | Gives |
|---|---|
| `photo_world_fetch_site_media` | **every item** — id, type, caption, url, width, height. **No person tags.** |
| `photo_world_fetch_individual_media` | the media for one person — this is where the tags are |

A successful `photo_world_fetch_site_media` response looks like:

```json
{"data":{"site":{"media":{"count":4500,"data":[
  {"id":"photo-<SITE>-1-4507830","type":"photo",
   "link":"https://www.myheritage.com/photo-4507830_<SITE>_<SITE>/maria-rosa-melluso",
   "url":"https://sites-cf.mhcache.com/e/1/<signed>/032/978/6671/507830_<hash>_A.jpg",
   "name":"Maria Rosa Melluso","width":175,"height":320, ...}]}}}
```

The numeric id at the end of `photo-<SITE>-1-NNNNNNN` is the `mid` used in
`manifest.psv`.

## The blocker

**Replaying either operation from the page's own JavaScript returns 403**, while
the app's own identical-looking calls return 200. Tried and rejected: no extra
header; `X-XSRF-TOKEN` and `x-mh-xsrf-token` carrying `window.mhXsrfToken` (79
chars, present on the page); several `variables` shapes. Patching `window.fetch`
and `XMLHttpRequest` to capture the app's real request captured **nothing**,
which suggests the calls are issued from a **worker or a bundled client** that
does not go through the patched globals.

So there is an auth element — most likely a **persisted-query hash** or a
request signature — that has not been identified. Guessing further was stopped
as disproportionate.

## What to try next, in order

1. **Read the request, not the response.** The browser tooling here exposes
   response bodies but not request headers. Chrome DevTools with *Copy as cURL*
   on one `photo_world_fetch_site_media` call would settle it in a minute.
2. **Check for a persisted query.** If the body carries
   `extensions.persistedQuery.sha256Hash` rather than a query string, the hash
   must be replayed verbatim.
3. **Failing both, use the UI.** The Photo World page pages through all 4,500;
   scrolling it and reading each `photo_world_fetch_site_media` response out of
   the network log needs no auth work at all — only patience.

## And a caution

4,500 items at full size is a great deal of traffic against somebody else's
service. Fetch **captions and ids first**, decide which are documents, and only
then pull images — as the direct-line sweep did.

---

## The sweep that worked — 13 September 2026

The auth problem was never solved and did not need to be. **The grid renders
every item into the DOM**, and reading the DOM is not a request, so it needs no
auth at all. `document.querySelectorAll('a[href*="/photo-"]')` yields the photo
id from the href and the caption from the child `img`'s `alt`; the caption is
byte-identical to the GraphQL `name` field, which was checked against the one
`photo_world_fetch_site_media` response that did return 200.

The method, for whoever runs it next:

1. Open the Photo World page **with the browser pane visible, or set a viewport**
   — with the pane hidden `innerHeight` is 0, the grid never virtualises, and the
   harvest silently stays empty. This wasted a pass.
2. Accumulate into a `Map` keyed by photo id, because the grid is virtualised and
   drops items from the DOM as they leave the viewport.
3. Scroll to `scrollHeight`, wait ~600–700 ms, re-scan, repeat. Stop after about
   eight passes with no growth.

### What it produced

| | |
|---|---|
| items in the library | 4,500 |
| **items reached** | **3,359 (75%)** |
| carrying a usable caption | 1,519 |
| naming one of this archive's nine surnames, or a place in its gazetteer | **26** |
| of those, not already held | **11** |

The grid stopped feeding at 3,359 and would not restart, so **the last quarter of
the library has not been seen**. Whoever resumes should say so rather than treat
26 as the final count.

Results are in `sources/media/captions-croatian.psv`.

### The one that looked like a breakthrough and was not

`4507711` is captioned *Status Annum — Our Lady of Snow Parish, Krivi Put* — a
status animarum, the household-by-household parish census, for exactly this
archive's parish. It is a real status animarum page: a household block running
1897–1939, with *ž.* (wife), *s.* (son), *k.* (daughter) and *i.* (child of)
against each name.

But it is **not this family's household** — it is tagged to Krešimir Pavelić, and
no Pavelić is published here. And the file is **973×354 and 56.6 KB**, a low
resolution capture rather than a scan. Its right-hand column carries *Iz …43* —
a house number in another place, the very device items 11 and 12 turned on — and
**the place name cannot be read at that resolution**, so it has not been
recorded. The adjacent *v. br. 18/51* is a cross-reference to another household
page, not a house number.

What it does establish is that **status animarum books for Krivi Put survive and
are reachable**, which is worth naming explicitly in the letters to Gospić and
Rijeka. That is a lead, not a finding.
