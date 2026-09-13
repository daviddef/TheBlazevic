import { defineConfig } from 'astro/config';

// GitHub Pages project site. To serve from a custom domain later,
// set base to '/' and site to that domain.
/* Phase 1 of the seven-archive standardisation: this page was called
   /changed while its own data file was already corrections.json, and four
   other archives call the same page /corrections. Renamed; the old address
   is kept alive because it has been linked to. */
const BASE = '/TheBlazevic';
const redirects = { '/changed': `${BASE}/corrections/` };

export default defineConfig({
  site: 'https://daviddef.github.io',
  base: '/TheBlazevic',
  build: { format: 'directory' },
  redirects,
});
