# FamilySearch finding aids

Image-number → ARK maps for films this archive reads repeatedly.

**Why these exist.** The Deep Zoom tiles are addressed by ARK, and the only way
to learn a film's ARKs is to open its thumbnail grid in the viewer and scrape
the `alt="Image N"` attributes — several minutes of scrolling per film, repeated
every time a session reloads the page. Saving the map turns that into a file
read.

**How to use one.** Load it into the page as `window.__map`, then
`tools/fs_reader.js` works immediately:

```js
window.__map = <paste the json>
await __cell(__map['105'], 0.19, 0.13, 0.32, 0.99, 0)
```

**A caution.** ARKs are stable but image *numbering* is the viewer's, not the
book's. The film's own printed folio numbers are a separate thing and must be
read off the page — see `tools/familysearch.md`.
