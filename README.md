# Down the Rabbit Hole AUST — website

Static HTML site for https://downtherabbitholeaust.com (Canberra lawn mowing and garden maintenance).
No page-builder runtime, no CSS framework: one HTML file per page with the stylesheet inlined, one deferred script.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `about.html`, `services.html`, `<service>.html`, `lawn-mowing-*.html`, `404.html` | Built pages (generated, do not hand-edit) |
| `content/*.json` | Copy for the service, hub and suburb pages (H1, meta, sections, FAQs) |
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
- 301 redirects for the old site's URLs are in `_redirects` / `.htaccess`. The six district pages that are not built yet are temporary 302s to the areas section; delete each line when its page goes live.
- Blog (`/blog`, `/post/…`) is migrated separately and is linked, not rebuilt here. Add the posts to `sitemap.xml` when they are live.

## Quote form and CRM tracking

- The quote form is custom HTML (no iframe): inline in every page's `#contact` section and as a pop-up (`#quote-modal`) opened by every "Get a Free Quote" button. `/#quote` also opens it.
- Field `name`/`data-field` attributes match the GoHighLevel contact fields: `full_name`, `email`, `phone`, `property_address`, `postal_code`, `property_size`, `service_needed`, `job_notes`. A hidden `source_page` carries the page URL and `qf_extra` is a honeypot (named so browser autofill ignores it; a filled honeypot goes straight to the thank-you page without passing the submission on).
- The CRM tracking script (`external-tracking.js`, tracking id `tk_6f4c…`) is loaded deferred in every page's `<head>` and captures the native `submit` event; the page then redirects to `/thank-you` (noindex). There is no form endpoint.
- Both forms use native validation (required fields, email, 4-digit postcode, phone pattern) with an inline error message.

## Placeholders still to fill

- `___HOURS___` (footer, contact section, schema `openingHoursSpecification`) — trading hours not supplied.
- `<!-- REVIEWS: paste 3–5 Google reviews here -->` in `tools/build.py` (homepage proof section).
- ABN number is not published; the site says "ABN Registered".
