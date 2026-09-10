// Prefix a site-root path with the deployment base, so the same links work at
// https://daviddef.github.io/TheBlazevic/ and at a custom domain later.
//
// Astro builds with format:'directory', so every page is served at a path with
// a trailing slash. Linking to "/senj" makes GitHub Pages issue a 301 to
// "/senj/" on every click. The Defranceschi archive writes its links with the
// slash already on; this adds it here instead, so the 30-odd pages here did not
// have to be edited one by one and cannot drift apart again.
//
// Left alone: query strings and fragments, which must keep their own shape.
const BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

export const u = (p = "/") => {
  const path = p.startsWith("/") ? p : "/" + p;
  const m = path.match(/^([^?#]*)([?#].*)?$/);
  let body = m[1];
  const tail = m[2] || "";
  // a real file keeps its extension; a page gets the slash
  if (body && !body.endsWith("/") && !/\.[a-z0-9]{2,5}$/i.test(body)) body += "/";
  return `${BASE}${body}${tail}`;
};
