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
- Field `name`/`data-field` attributes match the LSP (Local Service Pro CRM) contact fields: `full_name`, `email`, `phone`, `property_address`, `postal_code`, `property_size`, `service_needed`, `job_notes`. A hidden `source_page` carries the page URL and `qf_extra` is a honeypot (named so browser autofill ignores it; a filled honeypot goes straight to the thank-you page without passing the submission on).
- The CRM tracking script (`external-tracking.js`, tracking id `tk_6f4c…`) is loaded deferred in every page's `<head>` and captures the native `submit` event; the page then redirects to `/thank-you` (noindex). There is no form endpoint.
- **Service needed is multi-select.** Checkboxes write one comma-separated value (for example `Lawn Mowing, Hedge Trimming`) into the single `service_needed` field, so the CRM still receives one value. At least one service is required. In LSP, `contact.service_needed` should be a text field (or a multi-option field), because a single-option dropdown cannot hold the combined value.
- **Returning or new customer.** The form opens with a required "Have you used Down the Rabbit Hole AUST before?" question (`returning_customer` = `Yes` / `No`).
  - **Yes:** the form is sent and the visitor goes to `/thank-you`, which says "Thanks for coming back, <first name>!".
  - **No:** the form is sent first, so the lead is captured even if they stop, then the visitor goes to `/quote-details` (noindex, not in the sitemap). There, seven qualifying questions are sent as a second submission that carries the same `full_name`, `email` and `phone`, so the CRM matches it to the same contact. Then `/thank-you` shows the new-customer message.
  - The first name and contact details pass between pages in `sessionStorage` (this tab only), never in the URL. Opening `/quote-details` directly shows the contact fields instead.
  - The qualifying field keys need matching custom fields in LSP: `returning_customer`, `service_frequency`, `start_timeframe`, `property_type`, `customer_role`, `yard_condition`, `dva_card_holder`, `lead_source` and `form_step`. Questions and options live in `QUALIFY_QUESTIONS` in `tools/build.py`.
- Both forms use native validation (required fields, email, 4-digit postcode, phone pattern) with an inline error message.

## ServiceM8 integration

Every quote form submission also creates a ServiceM8 job, through the Vercel serverless function `api/quote.js`. The API key stays on the server and never reaches the browser.

**Step 1, the quote form (inline or pop-up):**
- The function looks up an existing active client contact by email (`companycontact.json?$filter=email eq '…' and active eq 1`). If there is no match, it creates a client and client contact.
- It creates a job with status Quote: `job_address` is the property address and postcode, and `job_description` is a short summary.
- It adds a job contact (`type: JOB`). Phone numbers starting 04 are saved as mobile.
- It adds a job note with every form detail, the page the form was sent from and the time received.
- Each photo is attached to the Job Diary as "Website photo N.jpg", using one multipart POST to `attachment.json` (the method in ServiceM8's "Attaching files to a Job Diary" guide).

**Step 2, new customers' quick questions:** the answers are added as a second note on the same job. The browser keeps the job UUID with an HMAC token for this tab only, and the function checks the token before writing to the job.

**Photos:** visitors can add up to 5. The browser shrinks each one to a maximum of 1600px as JPEG, typically 100–300KB, so uploads stay under Vercel's 4.5MB request limit. Photos are not sent to LSP.

**Setup**
1. In ServiceM8, go to Settings > API Keys and create a key. ServiceM8's docs say a private-app key is sent in the `X-API-Key` header, which is what the function does. These are the matching permissions, if ServiceM8 asks: `create_jobs`, `manage_customers`, `read_customer_contacts`, `manage_customer_contacts`, `manage_job_contacts`, `publish_job_notes`, `manage_attachments`.
2. In Vercel, go to Project > Settings > Environment Variables and add `SERVICEM8_API_KEY` for Production, and for Preview if you want to test there. Redeploy.
3. Send a test quote with a photo and check the job, note and attachment in ServiceM8.

**Behaviour if something fails**
- The form always finishes on the thank-you page, and LSP still captures the lead.
- If the key is missing, the function returns 503. If ServiceM8 rejects a request, it returns 502. The details go to the Vercel function logs only.
- The function accepts POST requests only, from this site's own domains. It ignores honeypot submissions, and it needs a name plus an email or phone.
- `vercel.json` gives the function 30 seconds (`functions.api/quote.js.maxDuration`) so photo uploads can finish.
- Only Vercel runs the function. `_redirects` and `.htaccess` hosts serve the static site without it.

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

The owner is Michael Robinson. The business is owner-operated, so copy never refers to a team, crew or staff. Copy only states: fully insured, ABN registered, 60+ Canberra lawns maintained, residential and commercial, locally operated, est. 2021, upfront quotes, green waste removal *available* with mowing, garden maintenance and clean-ups, and no need to be home with clear access. It is a registered DVA provider (confirmed by the client), but copy never says DVA will approve or fund a job; eligibility is DVA's call. It does not state prices or price ranges (copy points to a free quote instead), reply times, travel-charge policies or statistics without a source.

## Reviews widget

The homepage (after the before-and-after gallery) and the About page show the review widget from the CRM's reputation module (`REVIEW_WIDGET_JS` / `REVIEW_WIDGET_SRC` in `tools/build.py`). `site.js` loads the widget script and iframe only when the section is about 600px from the viewport, so it does not slow the first paint.

## Placeholders still to fill

- ABN number is not published; the site says "ABN Registered".
