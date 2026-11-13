# Down the Rabbit Hole AUST — website

Static HTML site for https://downtherabbitholeaust.com (Canberra lawn mowing and garden maintenance).
No page-builder runtime, no CSS framework: one HTML file per page with the stylesheet inlined, one deferred script.

## Layout

| Path | What it is |
|---|---|
| `index.html`, `about.html`, `contact.html`, `areas.html`, `blog.html`, `services.html`, `<service>.html`, `lawn-mowing-*.html`, `thank-you.html`, `404.html` | Built pages (generated, do not hand-edit) |
| `content/*.json` | Copy for the service, hub, suburb and district pages (H1, meta, sections, FAQs) |
| `content/posts/*.md` | Blog post bodies (parsed from the old site) |
| `tools/post_meta.json` | Published title and meta description for each blog post (originally from the old site's crawl). Edit here to change one |
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
- Field `name`/`data-field` attributes match the LSP (Local Service Pro CRM) contact fields: `full_name`, `email`, `phone`, `property_address`, `suburb`, `postal_code`, `property_size`, `service_needed`, `job_notes`, `how_did_you_find_us` and `who_referred_you` (the last three match fields that already exist in the client's LSP account). A hidden `source_page` carries the page URL and `qf_extra` is a honeypot (named so browser autofill ignores it; a filled honeypot goes straight to the thank-you page without passing the submission on).
- The CRM tracking script (`external-tracking.js`, tracking id `tk_6f4c…`) is loaded deferred in every page's `<head>` and captures the native `submit` event; the page then redirects to `/thank-you` (noindex). There is no form endpoint.
- **Service needed is multi-select.** Checkboxes write one comma-separated value (for example `Lawn Mowing, Hedge Trimming`) into the single `service_needed` field, so the CRM still receives one value. At least one service is required. In LSP, `contact.service_needed` should be a text field (or a multi-option field), because a single-option dropdown cannot hold the combined value.
- **Used us before?** The form opens with a required "Have you used Down the Rabbit Hole AUST before?" question (`returning_customer` = `Yes` / `No`). Either answer goes straight to `/thank-you`, which says "Thanks for coming back, <first name>!" or "Thanks, <first name>, your quote request is in". The first name passes in `sessionStorage` (this tab only), never in the URL.
- **How did you find us?** Optional dropdown (`how_did_you_find_us`). Its label and the "Who referred you?" label must read exactly like the LSP field names, or LSP also logs them as unmapped fields; the "(optional…)" hints are drawn by CSS from `data-hint`. Choosing "Friend, family or neighbour" shows an optional "Who referred you?" box (`who_referred_you`); choosing anything else hides and clears it. Options are `HEARD_OPTIONS` in `tools/build.py`.
- **Photos go to LSP as files.** The photo picker is named `attach_a_photo`, matching the client's LSP file-upload field "Attach a photo" (`contact.attach_a_photo`), the one the old site's form used. The LSP tracking script uploads the files in a named file input when the form is submitted. Because the picker is emptied after each pick (so photos can be added in several goes), `site.js` puts the shrunk JPEGs back into it just before the submission goes out (`attachPhotos`). "Attach a photo" must allow multiple files, or LSP keeps only one.
- There is no second step. The old quick-questions page (`/quote-details`) was removed and 301-redirects to `/contact`.
- The form uses native validation (required fields, email, 4-digit postcode, phone pattern) with an inline error message.

## ServiceM8

The website does not talk to ServiceM8. Quote requests go to LSP only, and the client's LSP app connector creates the ServiceM8 jobs. The old direct integration (`api/quote.js`) was removed, so there is no serverless function and no `SERVICEM8_API_KEY` to set.

**Leaving the page.** After a submit, the page waits until the LSP tracking script has finished sending (it watches the script's requests to `/external-tracking/events`, at most 25 seconds), then goes to `/thank-you`. This matters for photos: a form with photos goes out as one multipart upload, which the browser cancels if the page leaves first, and on a slow phone connection that upload can take several seconds.

## Performance notes

- **Lazy third-party scripts.** The CRM tracking script (`external-tracking.js`, about 267KB uncompressed) and the Facebook pixel load on the visitor's first interaction (scroll, tap, key or mouse move), or 5 seconds after the page loads, whichever comes first.
  - The tracking ID sits on `<html data-tracking-id>`.
  - The tracker sets itself up at once when loaded after the page is ready, and attaches to every form. A quote submit also waits for it (`ensureTracker` in `site.js`), so no submission is missed.
- **Hero video.** The video has no `autoplay` attribute and no `poster` attribute, because either one makes the browser download a file up front. The `<img>` underneath is the poster.
  - On screens 760px or narrower, the video starts on first interaction or after 5 seconds.
  - On desktop it starts after the load event.
- **Service card images.** The homepage service cards use `-card.webp` crops (560×420, quality 50) plus the 400px versions.
- **Measured locally** with Lighthouse mobile on the homepage:

  | | Before | After |
  |---|---|---|
  | Performance score | 75 | 98 |
  | Total Blocking Time | 770ms | 0–30ms |
  | Largest Contentful Paint | 3.1s | 2.3s |
  | Bytes on load | 1,175KB | 320KB |

  The third-party scripts were blocked in that test. On the live site, delaying them removes their cost from the first load as well.

## Service-area weighting

Weston Creek is the priority area (Fisher, Waramanga, Chapman, Weston and Rivett first), then Woden Valley and the Kambah end of Tuggeranong. The site reflects that in the homepage hero, the nav descriptors, the suburbs listed on service pages, the district page each service links to, and a "Priority area" tag on Weston Creek. The far-district pages (Belconnen, Inner North, Inner South, Queanbeyan) keep their URLs and H1s but lead with garden maintenance, hedging and clean-ups, with mowing offered as part of a garden schedule rather than as standalone recurring mowing.

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
- No noindex header is sent on any host, so PageSpeed scores the `.vercel.app` preview the same as production. Every page's canonical points to https://downtherabbitholeaust.com, which tells Google which copy to index.
- All 19 posts are in `sitemap.xml`; confirm they return 200 after launch.

## Business facts used in copy

The owner is Michael Robinson, and his name appears only on the About page (copy and the Person schema there). Every other page, post, form and thank-you message stays neutral about who quotes or does the work: it says locally owned and operated, never "deal with the owner", "Michael will quote" or team, crew or staff wording. Copy only states: fully insured, ABN registered, 60+ Canberra lawns maintained, residential and commercial, locally operated, est. 2021, upfront quotes, green waste removal *available* with mowing, garden maintenance and clean-ups, and no need to be home with clear access. It is a registered DVA provider (confirmed by the client), but copy never says DVA will approve or fund a job; eligibility is DVA's call. It does not state prices or price ranges (copy points to a free quote instead), reply times, travel-charge policies or statistics without a source.

## Reviews widget

The homepage (after the before-and-after gallery) and the About page show the review widget from the CRM's reputation module (`REVIEW_WIDGET_JS` / `REVIEW_WIDGET_SRC` in `tools/build.py`). `site.js` loads the widget script and iframe only when the section is about 600px from the viewport, so it does not slow the first paint.

## Placeholders still to fill

- ABN number is not published; the site says "ABN Registered".
