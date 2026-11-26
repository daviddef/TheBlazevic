import { defineConfig } from 'astro/config';
import { readFileSync } from 'node:fs';
import { nameSets, whoRedirects } from './src/lib/namesets.js';

// Served from its own domain since 12 October 2026: blazevic.defranceski.com
// (CNAME -> daviddef.github.io, site/public/CNAME). It was a GitHub Pages
// project site at https://daviddef.github.io/TheBlazevic/; GitHub redirects
// that address, path kept, to the custom domain, so links already published
// still work. archives.json keys this archive on base "" (BASE_URL stripped of
// its trailing slash), which is what astro's base '/' yields.
/* Phase 1 of the seven-archive standardisation: this page was called
   /changed while its own data file was already corrections.json, and four
   other archives call the same page /corrections. Renamed; the old address
   is kept alive because it has been linked to. */
const BASE = '';
/* 25 October 2026: a person recorded twice in the tree and confirmed to be one man is ONE person page. The retired record's page address redirects
   to the survivor's. The list is src/data/merged.json, written by tools/build_site_data.py from data/tree-merges.tsv; Astro writes each as a tiny page
   with a meta refresh and a canonical link (the kit's redirect-stub shape). The retired record's NAME address (/who/<name>/, where nobody else bears
   the name) is a redirect to the survivor's page too: whoRedirects below.
   23 November 2026, ONE PAGE PER PERSON: a name no longer has a page of its own. Every /who/<name>/ address is a static redirect (a meta refresh
   and a canonical, noindex, not in the sitemap): a name one person bears goes to that person's page; a name several bear goes to its first
   bearer's page at #others-of-this-name, the section that lists the others (src/lib/namesets.js: the earliest born who is not living, else slug
   order). "Every Name" (/who/) and its letter pages (/who/names--<initial>/) are the only pages left under /who/. */
const readJson = (p) => JSON.parse(readFileSync(new URL(p, import.meta.url), 'utf8'));
const merged = readJson('./src/data/merged.json');
const mergedRedirects = {};
for (const m of merged) {
  mergedRedirects[`/people/${m.retired.slug}`] = `${BASE}/people/${m.survivor.slug}/`;
}
const whoMap = whoRedirects(
  nameSets(readJson('./src/data/people.json'), readJson('./src/data/living.json'), readJson('./src/data/who-finds.json')),
  merged, BASE);
/* /married-in is now /marriages, on the estate's shared page shape. The address
   has been published, so it redirects rather than 404s. */
const redirects = { ...mergedRedirects, ...whoMap, '/changed': `${BASE}/corrections/`, '/married-in': `${BASE}/marriages/`,
  /* 9 October 2026: folded into /errands/, which is the same subject. */
  '/photograph-these': `${BASE}/errands/#photographs`,
  /* 26 November 2026: «Illegitimate» was the tree's stand-in for a father no entry names, never a person. Its published addresses
     answer with the mother's page. */
  '/people/illegitimate': `${BASE}/people/theresia-blazevic/`, '/who/illegitimate': `${BASE}/people/theresia-blazevic/`,
  /* 5 November 2026: Hedviga's, Milka's and Oto's own pages are their person pages, in story mode (src/lib/lifeStories.js). */
  '/hedviga': `${BASE}/people/hedviga-blazevic/`,
  '/milka': `${BASE}/people/milka-lucia-papic/`, '/oto': `${BASE}/people/oto-blazevic/`,
  /* 23 November 2026 (David: "roots and routes, remove it"): the archive's own Roots & Routes page is retired; the Tree Canvas on the Record
     Atlas replaced it estate-wide. The address answers with a redirect stub to this archive's own trees page. It was noindex, so it was never in
     the sitemap and the stub stays out of it too. /roots/view.html is NOT retired: it is the bare viewer the "Where they lived" frames on a
     person's page load (kit PersonRootsViews), and it stays noindex. */
  '/roots': `${BASE}/trees/` };

export default defineConfig({
  site: 'https://blazevic.defranceski.com',
  base: '/',
  build: { format: 'directory' },
  /* ARCHIVE_OUT was honoured by every kit TOOL and by nothing that writes.
     `ARCHIVE_OUT=dist-mine npm run build` put the pages in dist/ and then sent
     sitemap.py looking in dist-mine/, which does not exist — so the escape
     hatch the kit offers when two sessions collide on one dist could not
     actually be taken. 27 September 2026. */
  outDir: process.env.ARCHIVE_OUT || 'dist',
  redirects,
  /* The kit is BUNDLED, not externalised. Its lib/outlines.js does a plain
     `import RAW from "../data/outlines.json"`, which Vite handles and Node's
     own ESM loader refuses without an import attribute. A kit .astro component
     gets transformed either way, so this never bit until a page of this
     archive imported kit/lib directly — PlaceLocator, for the coastline. */
  vite: { ssr: { noExternal: ['@daviddef/archive-kit'] } },
});
