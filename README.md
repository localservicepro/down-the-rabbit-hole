# Down the Rabbit Hole AUST — website

Static HTML site for https://downtherabbitholeaust.com (Canberra lawn mowing and garden maintenance).
No page-builder runtime, no CSS framework: one HTML file per page with the stylesheet inlined, one deferred script.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `about.html`, `contact.html`, `areas.html`, `blog.html`, `services.html`, `<service>.html`, `lawn-mowing-*.html`, `thank-you.html`, `404.html` | Built pages (generated, do not hand-edit) |
| `content/*.json` | Copy for the service, hub, suburb and district pages (H1, meta, sections, FAQs) |
| `content/posts/*.md` | Blog post bodies (parsed from the old site) |
| `tools/build.py` | Generator: templates, homepage copy, schema, redirects, sitemap |
| `tools/verify.py` | Checks: one H1 with keyword, title ≤ 60, description 150–160, canonicals, JSON-LD, links, alt text, image caps, keyword density |
| `tools/serve.py` | Local preview server that maps `/lawn-mowing` → `lawn-mowing.html` and returns a real 404 |
| `tools/fetch_images.py` + `.github/workflows/fetch-images.yml` | One-off helper that pulled the client's job photos from Google Drive and converted them to WebP |
| `assets/site.css`, `assets/site.js`, `assets/fonts/` | Styles (inlined at build), behaviour, self-hosted Outfit + Hanken Grotesk |
| `images/` | Self-hosted WebP photos (1600 / 800 / 400 px variants) and logo files |
| `_redirects`, `.htaccess`, `robots.txt`, `sitemap.xml` | Hosting config (Netlify/Cloudflare Pages style and Apache) |

## Build and check

```
python3 tools/build.py      # regenerates every page and the static files
python3 tools/verify.py     # SEO / structure checks, exits non-zero on problems
python3 tools/serve.py 8080 # preview at http://127.0.0.1:8080
```

Requires Python 3.10+ (Pillow only for the image tooling).

## Hosting notes

- Serve clean URLs: `/lawn-mowing` must serve `lawn-mowing.html` (Netlify and Cloudflare Pages do this by default; Apache uses the rewrite in `.htaccess`).
- Unknown URLs must return **HTTP 404** with `404.html`.
- 301 redirects for the old site's URLs are in `vercel.json`, `_redirects` and `.htaccess`.
- `/blog` is the guides index and the 19 posts are built from `content/posts/*.md` into `post/<slug>.html`.
- Every page is written twice: `page.html` and `page/index.html`, so `/page` resolves on hosts with or without clean-URL support. `vercel.json` covers Vercel (clean URLs plus the 301 map); `_redirects` covers Netlify/Cloudflare; `.htaccess` covers Apache; meta-refresh stubs cover the old URLs on hosts that ignore all three.

## Hero video and generated imagery

- The homepage hero plays `images/hero-video.webm` / `.mp4` (6 s, silent, loops) over the poster frame `hero-video-poster.webp`, which is also the LCP image and the schema/OG image. The video loads only after page load and only when the visitor has not asked for reduced motion or data saving.
- `hero-video` and `about-branded-trailer` were generated with Higgsfield from the client's photos (Michael in his hi-vis vest, the branded trailer, the badge logo). `tools/assets.json` lists the source URLs and `.github/workflows/fetch-assets.yml` downloads and converts them (mp4/webm/poster, WebP sizes) on demand.

## Navigation and areas map

- Header: Home · Services (mega-menu) · About · Areas · Blog (mega-menu of nine guides, list in `BLOG_MENU`) · Contact, plus phone and the quote button. Mobile menu mirrors both mega-menus as accordions.
- The Areas page hero is an inline SVG map of the seven districts with hover/focus pins (`area_map()` in `tools/build.py`); each pin links to its district page.
- "Find us on Google" links use the short Maps link; the schema `sameAs` carries both the short link and the place-id URL.

## Quote form and CRM tracking

- The quote form is custom HTML (no iframe): inline in every page's `#contact` section and as a pop-up (`#quote-modal`) opened by every "Get a Free Quote" button. `/#quote` also opens it.
- Field `name`/`data-field` attributes match the GoHighLevel contact fields: `full_name`, `email`, `phone`, `property_address`, `postal_code`, `property_size`, `service_needed`, `job_notes`. A hidden `source_page` carries the page URL and `qf_extra` is a honeypot (named so browser autofill ignores it; a filled honeypot goes straight to the thank-you page without passing the submission on).
- The CRM tracking script (`external-tracking.js`, tracking id `tk_6f4c…`) is loaded deferred in every page's `<head>` and captures the native `submit` event; the page then redirects to `/thank-you` (noindex). There is no form endpoint.
- Both forms use native validation (required fields, email, 4-digit postcode, phone pattern) with an inline error message.

## Business hours

Mon–Thu 8am–5pm, Fri 9am–5pm, closed weekends. Set in `HOURS` and `openingHoursSpecification` in `tools/build.py`.

## Keyword ownership (data-backed review, Oct 2026)

Canberra searchers use the city name, not the district, so one page owns each "[service] Canberra" phrase:

| Phrase | Page | Notes |
|---|---|---|
| gardener canberra | `/gardening-services` | One-off and project jobs only |
| garden maintenance canberra | `/garden-maintenance` | Recurring visits only; cross-linked once each way with `/gardening-services` |
| lawn mowing canberra | `/lawn-mowing` | No "grass mowing" in the title (same query). The homepage, areas hub and every district page link here with the anchor "lawn mowing Canberra" |
| lawn care canberra | `/lawn-care` | The garden maintenance guide links here |
| (business entity) | `/` | H1 "Lawn & Garden Care Across Canberra"; the exact mowing phrase is used naturally, not repeated |

- Four posts that competed for the mowing phrase were retitled to informational angles and link to `/lawn-mowing`: `grass-mowing-canberra-guide`, `canberra-lawn-mowing-services-guide`, `best-lawn-mowing-services-canberra`, `top-rated-canberra-lawn-maintenance-providers`. URLs are unchanged.
- In JSON copy, `[anchor](/path)` in intro, paragraph and bullet strings renders as an internal link.
- Expect the homepage's positions for the mowing cluster to dip while `/lawn-mowing` picks them up.

## Launch checks

- Redirects are 301 in `vercel.json`, `_redirects` and `.htaccess`. After deploy, confirm each old URL returns 301 (not 302) with a header checker, and pull the Search Console page list for any indexed URL the old sitemap missed.
- `*.vercel.app` hosts send `X-Robots-Tag: noindex, nofollow` (see `VERCEL["headers"]`), so previews stay out of the index. Confirm the production domain does not send it.
- All 19 posts are in `sitemap.xml`; confirm they return 200 after launch.

## Business facts used in copy

The owner is Michael Robinson. The business is owner-operated, so copy never refers to a team, crew or staff. Copy only states: fully insured, ABN registered, 60+ Canberra lawns maintained, residential and commercial, locally operated, est. 2021, upfront quotes, green waste removal *available* with mowing, garden maintenance and clean-ups, and no need to be home with clear access. It is a registered DVA provider (confirmed by the client), but copy never says DVA will approve or fund a job; eligibility is DVA's call. It does not state prices or price ranges (copy points to a free quote instead), reply times, travel-charge policies or statistics without a source.

## Placeholders still to fill

- `<!-- REVIEWS: paste 3–5 Google reviews here -->` in `tools/build.py` (homepage proof section).
- ABN number is not published; the site says "ABN Registered".
