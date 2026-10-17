/* Download register pages at full resolution IN THE BACKGROUND, then take them out in bulk.
   Paste into the console of a signed-in familysearch.org page (javascript_tool). Written 17 Oct 2026.

   WHY. Reading a page through screenshots costs a round trip per screen, and a screenshot is capped
   at the viewport. Instead: stitch each page's left and right columns (level 13 = full size) with a
   few tiles in flight, keep them as base64 JPEGs in window.__store, and return MANY pages in ONE
   javascript_tool result. A result over the tool limit is saved to a file instead of entering the
   conversation, and that works at 15 MB, so a whole batch lands on disk in one call. Then
   tools/fs_unpack.py turns the file into per-page JPEGs and reading sheets (tools/fs_sheet.py).

   The local-sink route in tools/fs_reader.js (__send, POST to 127.0.0.1) did NOT work from the
   browser pane on 17 Oct 2026: fetch, no-cors and <img> to 127.0.0.1 all failed. Use the spill.

   Needs window.__arksD = [ark of image 1, ark of image 2, ...] (see tools/familysearch.md) and
   window.fetchWindow is NOT needed. Page-column geometry below is for a two-page spread of ~6000 px:
   left column x 740..1690, right column x 3100..4050, y 380..4180; adjust for another book.

     await __prefetch([140,141,142])        // queues, returns at once (about 15 s a page)
     [window.__pfSt, window.__pfLog]        // poll
     window.__pack = [140,141,142].flatMap(n => window.__store[n])   // L,R per image
     window.__pack                          // return it: spills to a file; then
                                            // python3 tools/fs_unpack.py SPILLFILE OUTDIR 140,141,142
*/
window.__store = window.__store || {};
window.__cols = async (ark, x, w, y, h, conc = 6) => {
  const T = 256, OV = 1, c = document.createElement("canvas"); c.width = w; c.height = h;
  const g = c.getContext("2d"), c0 = Math.floor(x / T), c1 = Math.floor((x + w - 1) / T),
        r0 = Math.floor(y / T), r1 = Math.floor((y + h - 1) / T), jobs = [];
  for (let a = c0; a <= c1; a++) for (let b = r0; b <= r1; b++) jobs.push([a, b]);
  let i = 0, ok = 0;
  async function wk() {
    while (i < jobs.length) {
      const [a, b] = jobs[i++];
      await new Promise((res) => {
        const im = new Image();
        im.onload = () => { g.drawImage(im, a * T - (a > 0 ? OV : 0) - x, b * T - (b > 0 ? OV : 0) - y); ok++; res(); };
        im.onerror = () => res();
        im.src = `/service/records/storage/deepzoomcloud/dz/v1/${ark}/image_files/13/${a}_${b}.jpg`;
      });
      await new Promise((r) => setTimeout(r, 15));
    }
  }
  await Promise.all(Array.from({ length: conc }, wk));
  return { c, ok, total: jobs.length };
};
window.__b64 = async (c, q = 0.9) => {
  const blob = await new Promise((r) => c.toBlob(r, "image/jpeg", q));
  const buf = new Uint8Array(await blob.arrayBuffer()); let s = "";
  for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
  return btoa(s);
};
window.__prefetch = async (list) => {
  window.__pfLog = []; window.__pfSt = "0/" + list.length;
  (async () => {
    let k = 0;
    for (const n of list) {
      try {
        const ark = window.__arksD[n - 1], t0 = Date.now();
        const L = await __cols(ark, 740, 950, 380, 3800), R = await __cols(ark, 3100, 950, 380, 3800);
        window.__store[n] = [await __b64(L.c), await __b64(R.c)];
        window.__pfLog.push(`${n} L${L.ok}/${L.total} R${R.ok}/${R.total} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      } catch (e) { window.__pfLog.push("ERR " + n + " " + (e && e.message)); }
      window.__pfSt = (++k) + "/" + list.length;
    }
    window.__pfSt = "DONE " + list.length;
  })();
  return "queued " + list.length;
};
