import { defineConfig } from 'astro/config';

// GitHub Pages project site. To serve from a custom domain later,
// set base to '/' and site to that domain.
/* Phase 1 of the seven-archive standardisation: this page was called
   /changed while its own data file was already corrections.json, and four
   other archives call the same page /corrections. Renamed; the old address
   is kept alive because it has been linked to. */
const BASE = '/TheBlazevic';
/* /married-in is now /marriages, on the estate's shared page shape. The address
   has been published, so it redirects rather than 404s. */
const redirects = { '/changed': `${BASE}/corrections/`, '/married-in': `${BASE}/marriages/` };

export default defineConfig({
  site: 'https://daviddef.github.io',
  base: '/TheBlazevic',
  build: { format: 'directory' },
  redirects,
  /* The kit is BUNDLED, not externalised. Its lib/outlines.js does a plain
     `import RAW from "../data/outlines.json"`, which Vite handles and Node's
     own ESM loader refuses without an import attribute. A kit .astro component
     gets transformed either way, so this never bit until a page of this
     archive imported kit/lib directly — PlaceLocator, for the coastline. */
  vite: { ssr: { noExternal: ['@daviddef/archive-kit'] } },
});
