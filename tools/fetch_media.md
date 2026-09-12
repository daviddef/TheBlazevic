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
