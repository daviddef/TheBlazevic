import { defineConfig } from 'astro/config';

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
/* /married-in is now /marriages, on the estate's shared page shape. The address
   has been published, so it redirects rather than 404s. */
const redirects = { '/changed': `${BASE}/corrections/`, '/married-in': `${BASE}/marriages/`,
  /* 9 October 2026: folded into /errands/, which is the same subject. */
  '/photograph-these': `${BASE}/errands/#photographs` };

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
