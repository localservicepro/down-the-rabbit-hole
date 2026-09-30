#!/usr/bin/env python3
"""Static site generator for downtherabbitholeaust.com.
Run: python3 tools/build.py  → writes *.html, sitemap.xml, _redirects, .htaccess into the repo root."""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPY = os.environ.get("COPY_DIR", os.path.join(ROOT, "content"))
SITE = "https://downtherabbitholeaust.com"
BIZ_ID = SITE + "/#business"
NAME = "Down the Rabbit Hole AUST"
LEGAL = "Down the Rabbit Hole (Aust) Pty Ltd"
PHONE = "0423 720 317"
TEL = "tel:+61423720317"
SMS = "sms:+61423720317"
EMAIL = "info@downtherabbitholeaust.com"
FB = "https://www.facebook.com/p/Down-the-Rabbit-Hole-AUST-61552753624844/"
IG = "https://www.instagram.com/downtherabbitholeaust"
GBP = "https://www.google.com/maps/search/?api=1&query=Google&query_place_id=ChIJuzQLsqNMFmsRcFlpp27qAAQ"
MAP_EMBED = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d416436.695680462!2d149.1297825!3d-35.37024405!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0xaf8e434d15506cf1%3A0x24c31c1abe5ee30a!2sDown%20the%20Rabbit%20Hole%20Aust!5e0!3m2!1sen!2sph!4v1790757761736!5m2!1sen!2sph"
HOURS = "___HOURS___"
TRACKING_ID = "tk_6f4c1089fe214ae6baa8c2dc37522e82"
THANK_YOU = "/thank-you"
CSS = open(os.path.join(ROOT, "assets", "site.css"), encoding="utf-8").read()
try:
    IMG = json.load(open(os.path.join(ROOT, "images", "manifest.json")))
except FileNotFoundError:
    IMG = {}

HERO_IMAGE = os.environ.get("HERO_IMAGE", "garden-clean-up-1-after")

SERVICES = [
    # slug, name, nav descriptor, icon, home-card blurb
    ("lawn-mowing", "Lawn Mowing", "Weston Creek, Woden & Tuggeranong", "mower", "Lawn mowing Canberra wide: scheduled or one-off visits with clean edges and clippings taken away."),
    ("lawn-care", "Lawn Care", "Fertilising & weed control, Canberra wide", "sprout", "Fertilising, weed control and seasonal programs for tired or patchy lawns."),
    ("gardening-services", "Gardening Services", "A local gardener for Woden & Inner South", "trowel", "A reliable local gardener for weeding, planting, mulching and regular visits."),
    ("garden-maintenance", "Garden Maintenance", "Homes, rentals & strata across the ACT", "shears", "Weeding, pruning and ongoing garden care on a schedule that suits you."),
    ("hedge-trimming", "Hedge Trimming", "Established gardens in Woden & Weston Creek", "hedge", "Shaping, height reduction and every clipping removed from site."),
    ("yard-clean-ups", "Yard Clean-Ups", "Pre-sale & end of lease, Tuggeranong to Belconnen", "broom", "Overgrown yards, pre-sale tidies and end-of-lease clean-ups done in a day."),
    ("green-waste-removal", "Green Waste Removal", "Clippings, branches & leaves, Canberra wide", "leaf", "Clippings, branches, leaves and garden debris loaded and gone."),
    ("rubbish-removal", "Rubbish Removal", "Garden, yard & household junk, ACT & Queanbeyan", "bin", "Garden, yard and household junk collected without a trip to the tip."),
    ("dva-lawn-care", "DVA Lawn Care", "Veterans in Tuggeranong, Belconnen & Queanbeyan", "medal", "Lawn and garden care for veterans and DVA card holders across Canberra."),
    ("weed-spraying", "Weed Spraying", "Bindi & broadleaf control, Belconnen & Weston Creek", "spray", "Bindi, broadleaf and garden bed weed control timed for Canberra seasons."),
]
SERVICE_NAMES = {s[0]: s[1] for s in SERVICES}
SERVICE_TYPES = {
    "lawn-mowing": "Lawn mowing", "lawn-care": "Lawn care", "gardening-services": "Gardening services",
    "garden-maintenance": "Garden maintenance", "hedge-trimming": "Hedge trimming", "yard-clean-ups": "Yard clean-up",
    "green-waste-removal": "Green waste removal", "rubbish-removal": "Rubbish removal", "dva-lawn-care": "DVA lawn care and gardening",
    "weed-spraying": "Weed spraying",
}

DISTRICTS = [
    ("Weston Creek", "/lawn-mowing-weston-creek", ["Fisher", "Waramanga", "Chapman", "Weston", "Rivett", "Stirling", "Holder", "Duffy", "Coombs", "Denman Prospect", "Wright"]),
    ("Woden Valley", "/lawn-mowing-woden-valley", ["Phillip", "Chifley", "O'Malley", "Mawson", "Pearce", "Torrens", "Farrer", "Isaacs", "Curtin", "Hughes", "Lyons"]),
    ("Tuggeranong", "/lawn-mowing-tuggeranong", ["Kambah", "Wanniassa", "Greenway", "Fadden", "Monash", "Gowrie", "Isabella Plains", "Richardson", "Chisholm", "Macarthur", "Gilmore", "Bonython"]),
    ("Belconnen", "/lawn-mowing-belconnen", ["Charnwood", "Macgregor", "Melba", "Latham", "Spence", "Evatt", "Holt", "Higgins", "Scullin", "Hawker", "Weetangera", "Macquarie", "Cook", "Aranda", "Giralang", "Kaleen", "Lawson", "Bruce"]),
    ("Inner North", "/lawn-mowing-inner-north", ["Lyneham", "O'Connor", "Dickson", "Downer", "Ainslie", "Braddon", "Acton", "Watson", "Hackett", "Reid", "Campbell"]),
    ("Inner South", "/lawn-mowing-inner-south", ["Yarralumla", "Deakin", "Red Hill", "Narrabundah"]),
    ("Queanbeyan & NSW", "/lawn-mowing-queanbeyan", ["Queanbeyan", "Jerrabomberra", "Googong", "Karabar", "Crestwood", "Beard"]),
]
DISTRICT_LINKS = {d[0]: d[1] for d in DISTRICTS}
BUILT_SUBURB_PAGES = {"/lawn-mowing-kambah", "/lawn-mowing-woden-valley"}

POSTS = {
    "/post/spring-lawn-mowing-canberra-guide": ("Spring Lawn Mowing Canberra: Your Post-Winter Guide", "2026-09-02", "When to give your lawn its first cut after winter, and how to do it without setting it back."),
    "/post/bindi-spraying-canberra-lawn-weeds": ("Stop Bindi & Broadleaf Weeds Before Canberra Summer", "2026-09-08", "How to identify, prevent and control bindi and broadleaf weeds in ACT lawns."),
    "/post/garden-mulching-canberra-guide": ("Garden Mulching Canberra: A Guide to a Thriving Garden", "2026-09-15", "What mulch to use, when to apply it and how it protects Canberra garden beds."),
    "/post/hedge-trimming-canberra": ("Hedge Trimming Canberra: Get Ready for Spring & Summer", "2026-08-25", ""),
    "/post/spring-garden-checklist-canberra": ("Your Essential Spring Garden Checklist for Canberra", "2026-08-18", ""),
    "/post/canberra-lawn-frost-damage-spring-care": ("Revive Your Canberra Lawn: Early Spring Care After Frost", "2026-08-11", ""),
    "/post/winter-lawn-care-tips-canberra": ("Canberra Winter Lawn Care Guide for Homeowners", "", ""),
    "/post/prepare-lawn-for-spring-canberra": ("Prepare Your Lawn for Spring in Canberra: A Pro Guide", "", ""),
    "/post/green-waste-canberra-disposal-guide": ("Green Waste Canberra: Your Complete Disposal Guide", "", ""),
    "/post/yard-clean-up-canberra-guide": ("Your Guide to Yard Clean Up in Canberra", "", ""),
    "/post/garden-service-canberra-guide": ("Garden Service Canberra: Your Ultimate Guide to a Perfect Yard", "", ""),
    "/post/garden-maintenance-canberra-guide": ("Garden Maintenance in Canberra: What Homeowners Should Know", "", ""),
    "/post/grass-mowing-canberra-guide": ("Grass Mowing Canberra: Your Ultimate Lawn Care Guide", "", ""),
    "/post/canberra-lawn-mowing-services-guide": ("Canberra Lawn Mowing Services: The Ultimate Guide", "", ""),
    "/post/dva-lawn-care-services-canberra-5929": ("DVA Lawn Care Services Canberra: A Veteran's Guide", "", ""),
    "/post/best-lawn-mowing-services-canberra": ("Best Lawn Mowing Services in Canberra", "", ""),
    "/post/top-rated-canberra-lawn-maintenance-providers": ("Top-Rated Canberra Lawn Maintenance Providers: A Homeowner's Guide", "", ""),
    "/post/the-ultimate-guide-to-commercial-yard-maintenance-in-Australia": ("The Ultimate Guide to Commercial Yard Maintenance in Australia", "", ""),
    "/post/case-study--transforming-a-neglected-garden-into-a-vibrant-outdoor-space": ("Case Study: Transforming a Neglected Garden into a Vibrant Outdoor Space", "", ""),
}
LATEST_POSTS = ["/post/garden-mulching-canberra-guide", "/post/bindi-spraying-canberra-lawn-weeds", "/post/spring-lawn-mowing-canberra-guide"]

HOME_FAQS = [
    ("How much does lawn mowing cost in Canberra?", "Lawn mowing costs in Canberra depend on lawn size, frequency, and condition. We provide clear, upfront quotes before starting so you know exactly what to expect."),
    ("Do you offer one-off lawn mowing services?", "Yes. We offer one-off lawn mowing for properties that need a quick tidy-up, as well as regular scheduled mowing for ongoing maintenance."),
    ("How often should lawns be mowed in Canberra?", "Most Canberra lawns are best mowed every 1-2 weeks during the growing season and every 2-4 weeks in the cooler months. We can recommend the right schedule based on your lawn type and time of year."),
    ("Do you provide lawn care as well as mowing?", "Yes. Our services include complete lawn care in Canberra, including general maintenance, seasonal upkeep, and lawn tidy-ups alongside mowing."),
    ("Do you offer yard clean-ups for overgrown properties?", "Yes. We provide full yard clean-ups for overgrown or neglected properties, including debris removal and garden bed tidy-ups."),
    ("Is green waste removal included?", "Green waste removal is available with all lawn mowing, garden maintenance, and yard clean-up services. We remove clippings, branches, and garden debris."),
    ("Do you service residential and commercial properties?", "Yes. We provide lawn mowing and garden maintenance services for both residential homes and commercial properties across Canberra."),
    ("Do I need to be home during the service?", "No. As long as we have clear access to the property, you don’t need to be home while we complete the work."),
    ("Which areas of Canberra do you service?", "We service lawns and gardens across Canberra and surrounding areas, including Kambah, Fisher, Woden, Tuggeranong, Weston Creek, and nearby regions."),
]

PAIRS = [
    ("yard-tidy-1", "Yard tidy", "an overgrown back yard before the tidy-up", "the same back yard mowed, edged and cleared"),
    ("yard-tidy-2", "Yard tidy", "a neglected yard with long grass before work started", "the yard mowed, edged and tidied"),
    ("overgrown-clean-up", "Overgrown clean-up", "an overgrown garden before the clean-up", "the garden cleared and tidy after the clean-up"),
    ("garden-clean-up-1", "Garden clean-up", "garden beds and lawn before the clean-up", "garden beds weeded and lawn tidied after the clean-up"),
    ("garden-clean-up-2", "Garden clean-up", "a second view of the garden before the clean-up", "the garden after weeding, pruning and green waste removal"),
    ("garden-tidy", "Garden tidy", "a garden before the tidy-up", "the garden after the tidy-up"),
    ("garden-bed-restore", "Garden bed restore", "overgrown garden beds before restoration", "garden beds weeded, edged and restored"),
    ("defence-property", "Defence property tidy", "a Defence housing property before the clean-up", "the Defence housing property after mowing and tidying"),
]

ICONS = {
    "grid": '<svg viewBox="0 0 24 24"><rect x="3.5" y="3.5" width="7" height="7" rx="2"/><rect x="13.5" y="3.5" width="7" height="7" rx="2"/><rect x="3.5" y="13.5" width="7" height="7" rx="2"/><rect x="13.5" y="13.5" width="7" height="7" rx="2"/></svg>',
    "mower": '<svg viewBox="0 0 24 24"><path d="M3 15h9l2-7h4"/><circle cx="6" cy="17" r="2.5"/><circle cx="17" cy="17" r="2.5"/><path d="M8.5 17h6M12 15l1.5-5"/><path d="M4 12V9h5"/></svg>',
    "sprout": '<svg viewBox="0 0 24 24"><path d="M12 21v-8"/><path d="M12 13c0-4 3-6 7-6 0 4-3 6-7 6z"/><path d="M12 15c0-3.5-2.5-5.5-6-5.5 0 3.5 2.5 5.5 6 5.5z"/><path d="M5 21h14"/></svg>',
    "trowel": '<svg viewBox="0 0 24 24"><path d="M4 20l6-6"/><path d="M10 14l-2-2 6-6 4 4-6 6-2-2z"/><path d="M14 6l3-3 4 4-3 3"/></svg>',
    "shears": '<svg viewBox="0 0 24 24"><circle cx="6.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/><path d="M8.5 16 15 4M15.5 16 9 4"/></svg>',
    "hedge": '<svg viewBox="0 0 24 24"><path d="M4 12a8 8 0 0 1 16 0v3H4z"/><path d="M8 15v5M16 15v5M12 15v5"/><path d="M3 20h18"/></svg>',
    "broom": '<svg viewBox="0 0 24 24"><path d="M14 3l7 7"/><path d="M10.5 6.5 17.5 13.5"/><path d="M4 21c1-5 3-8 6.5-9.5L15 16c-1.5 3.5-5 5-11 5z"/><path d="M7 21l1-4M10 21l2-3"/></svg>',
    "leaf": '<svg viewBox="0 0 24 24"><path d="M5 19C5 9 11 4 20 4c0 9-5 15-15 15z"/><path d="M5 19c3-5 6-8 10-10"/></svg>',
    "bin": '<svg viewBox="0 0 24 24"><path d="M4 7h16"/><path d="M6 7l1 13h10l1-13"/><path d="M9 7V4h6v3"/><path d="M10 11v6M14 11v6"/></svg>',
    "medal": '<svg viewBox="0 0 24 24"><circle cx="12" cy="14" r="5.5"/><path d="M12 11.5l.9 1.8 2 .3-1.45 1.4.35 2-1.8-.95-1.8.95.35-2L9.1 13.6l2-.3z"/><path d="M8 9 5 3h5l2 4 2-4h5l-3 6"/></svg>',
    "spray": '<svg viewBox="0 0 24 24"><path d="M8 9h6l1 12H7z"/><path d="M10 9V6h2v3"/><path d="M10 6h5"/><path d="M18 4l1-1M19 7h1.5M18 10l1 1"/></svg>',
    "phone": '<svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>',
    "sms": '<svg viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8M8 13h5"/></svg>',
    "mail": '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "pin": '<svg viewBox="0 0 24 24"><path d="M12 21s7-6.5 7-12a7 7 0 0 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>',
    "clock": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
    "check": '<svg viewBox="0 0 24 24"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
    "shield": '<svg viewBox="0 0 24 24"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="m9 12 2 2 4-4"/></svg>',
    "badge": '<svg viewBox="0 0 24 24"><path d="M12 3l2.2 2 3-.4 1 2.9 2.7 1.4-.8 2.9 1.5 2.6-2.3 2-.2 3-3 .3L14 22l-2-2.2L10 22l-2.1-2.3-3-.3-.2-3-2.3-2 1.5-2.6-.8-2.9L5.8 7.5l1-2.9 3 .4z"/><path d="m9 12 2 2 4-4"/></svg>',
    "home": '<svg viewBox="0 0 24 24"><path d="M3 11 12 4l9 7"/><path d="M5 10v10h5v-6h4v6h5V10"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "plus": '<svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>',
    "star": '<svg viewBox="0 0 24 24"><path d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6L2.5 9.4l6.6-.8z"/></svg>',
    "fb": '<svg viewBox="0 0 24 24"><path d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.8c0-.9.3-1.6 1.6-1.6h1.7V4.4c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.3H7.4V14h2.8v8z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24"><path d="M12 7.3A4.7 4.7 0 1 0 12 16.7 4.7 4.7 0 0 0 12 7.3zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm5.9-7.9a1.1 1.1 0 1 1-2.2 0 1.1 1.1 0 0 1 2.2 0zM12 3.9c2.6 0 2.9 0 4 .1 2.7.1 3.9 1.4 4 4 .1 1 .1 1.3.1 4s0 3-.1 4c-.1 2.6-1.4 3.9-4 4-1 .1-1.3.1-4 .1s-3 0-4-.1c-2.6-.1-3.9-1.4-4-4-.1-1-.1-1.3-.1-4s0-3 .1-4c.1-2.6 1.4-3.9 4-4 1-.1 1.3-.1 4-.1zM12 2.2c-2.7 0-3 0-4.1.1-3.6.2-5.5 2.1-5.7 5.7C2.2 9 2.2 9.3 2.2 12s0 3 .1 4.1c.2 3.6 2.1 5.5 5.7 5.7 1.1.1 1.4.1 4.1.1s3 0 4.1-.1c3.6-.2 5.5-2.1 5.7-5.7.1-1.1.1-1.4.1-4.1s0-3-.1-4.1c-.2-3.6-2.1-5.5-5.7-5.7-1.1-.1-1.4-.1-4.1-.1z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "close": '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18"/></svg>',
}
CARET = '<svg class="caret" viewBox="0 0 12 8" aria-hidden="true"><path d="M1 1.5 6 6.5l5-5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'


def esc(s):
    return html.escape(str(s), quote=True)


def icon(name):
    return ICONS[name].replace("<svg", '<svg aria-hidden="true" focusable="false"', 1)


def img_dims(name, small=False):
    d = IMG.get(name)
    if not d:
        return (800, 600) if small else (1600, 1200)
    return (d["w800"], d["h800"]) if small else (d["w"], d["h"])


def picture(name, alt, cls="", lazy=True, sizes="(max-width: 900px) 100vw, 50vw", priority=False):
    w, h = img_dims(name)
    sw, sh = img_dims(name, True)
    attrs = f'src="/images/{name}.webp" srcset="/images/{name}-800.webp {sw}w, /images/{name}.webp {w}w" sizes="{sizes}" width="{w}" height="{h}" alt="{esc(alt)}"'
    if cls:
        attrs += f' class="{cls}"'
    attrs += ' fetchpriority="high" decoding="async"' if priority else ' loading="lazy" decoding="async"'
    return f"<img {attrs}>"


# ---------- shared components ----------

def header(active="", over_hero=False):
    items = [
        f'<a class="dd-item dd-all" role="menuitem" href="/services"><span class="dd-icon">{icon("grid")}</span><span class="dd-text"><strong>All Services</strong><em>Lawn, garden, clean-up and removal services in Canberra</em></span></a>'
    ]
    for slug, name, desc, ic, _ in SERVICES:
        items.append(f'<a class="dd-item" role="menuitem" href="/{slug}"><span class="dd-icon">{icon(ic)}</span><span class="dd-text"><strong>{esc(name)}</strong><em>{esc(desc)}</em></span></a>')
    dd = "\n".join(items)
    contact_href = "#contact" if active != "404" else "/#contact"
    areas_href = "#areas" if active == "home" else "/#areas"
    about_href = "/about"
    def cls(k):
        return "nav-link is-active" if k == active else "nav-link"
    mobile_items = "\n".join(
        f'<a class="dd-item" href="/{slug}"><span class="dd-icon">{icon(ic)}</span><span class="dd-text"><strong>{esc(name)}</strong><em>{esc(desc)}</em></span></a>'
        for slug, name, desc, ic, _ in SERVICES)
    return f'''<header class="site-header{" over-hero" if over_hero else " solid"}" id="top">
  <div class="nav-inner">
    <a href="/" class="brand" aria-label="{NAME} home"><img src="/images/dtrh-logo-104.webp" width="52" height="52" alt="{NAME} badge logo: rabbit with a wheelbarrow, taking the headaches away"><span class="brand-name">Down the Rabbit Hole<small>Lawn &amp; garden care · Canberra</small></span></a>
    <nav class="nav-main" aria-label="Main navigation">
      <a href="/" class="{cls("home")}">Home</a>
      <div class="nav-dropdown">
        <button class="{cls("services")} nav-trigger" aria-expanded="false" aria-controls="services-menu" aria-haspopup="true">Services {CARET}</button>
        <div class="dropdown-panel" id="services-menu" role="menu" aria-label="Services">
{dd}
        </div>
      </div>
      <a href="{about_href}" class="{cls("about")}">About</a>
      <a href="{areas_href}" class="nav-link">Areas</a>
      <a href="{contact_href}" class="nav-link">Contact</a>
    </nav>
    <div class="nav-actions">
      <a href="{TEL}" class="nav-phone">{icon("phone")}{PHONE}</a>
      <a href="{contact_href}" class="btn btn-primary" data-open-quote>Get a Free Quote</a>
      <button class="nav-burger" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-backdrop" aria-hidden="true"></div>
<nav class="mobile-panel" id="mobile-menu" aria-label="Mobile navigation">
  <div class="mp-head"><img src="/images/dtrh-logo-104.webp" width="52" height="52" alt="" style="border-radius:50%"><button class="mp-close" aria-label="Close menu">{icon("close")}</button></div>
  <a class="mp-link" href="/">Home</a>
  <button class="mp-link mp-acc" aria-expanded="false" aria-controls="mp-services">Services {CARET}</button>
  <div class="mp-sub" id="mp-services">
    <a class="dd-item" href="/services"><span class="dd-icon">{icon("grid")}</span><span class="dd-text"><strong>All Services</strong><em>Everything we do, in one place</em></span></a>
{mobile_items}
  </div>
  <a class="mp-link" href="{about_href}">About</a>
  <a class="mp-link" href="{areas_href}">Areas</a>
  <a class="mp-link" href="{contact_href}">Contact</a>
  <div class="mp-cta"><a class="btn btn-primary" href="{contact_href}" data-open-quote>Get a Free Quote</a><a class="btn btn-outline" href="{TEL}">{icon("phone")}Call {PHONE}</a></div>
  <div class="mp-social social"><a href="{FB}" aria-label="Facebook" rel="noopener" target="_blank">{icon("fb")}</a><a href="{IG}" aria-label="Instagram" rel="noopener" target="_blank">{icon("ig")}</a></div>
</nav>
<div class="call-bar"><a href="{TEL}">{icon("phone")}Call {PHONE}</a><a class="cb-quote" href="{contact_href}" data-open-quote>Get a Free Quote</a></div>'''


def footer():
    services = "\n".join(f'<li><a href="/{s}">{esc(n)}</a></li>' for s, n, *_ in SERVICES)
    districts = "\n".join(f'<li><a href="{u}">{esc(n)}</a></li>' for n, u, _ in DISTRICTS)
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="/images/dtrh-logo-512.webp" width="120" height="120" alt="{NAME} badge logo, est. 2021" loading="lazy" decoding="async">
        <p><strong style="color:#fff">{NAME}</strong><br>Lawn mowing Canberra homeowners and businesses rely on, with garden maintenance, hedges, clean-ups and waste removal. Taking the headaches away since 2021.</p>
        <div class="footer-nap">
          <a href="{TEL}">{icon("phone")}{PHONE}</a>
          <a href="{SMS}">{icon("sms")}Text {PHONE}</a>
          <a href="mailto:{EMAIL}">{icon("mail")}{EMAIL}</a>
          <span>{icon("pin")}Canberra, ACT, Australia (service-area business)</span>
          <span>{icon("clock")}Hours: {HOURS}</span>
        </div>
        <div class="social"><a href="{FB}" aria-label="Down the Rabbit Hole AUST on Facebook" rel="noopener" target="_blank">{icon("fb")}</a><a href="{IG}" aria-label="Down the Rabbit Hole AUST on Instagram" rel="noopener" target="_blank">{icon("ig")}</a></div>
      </div>
      <div><h3 class="fh">Services</h3><ul>
        <li><a href="/services">All services</a></li>
{services}
      </ul></div>
      <div><h3 class="fh">Areas</h3><ul>
{districts}
      </ul></div>
      <div><h3 class="fh">Company</h3><ul>
        <li><a href="/about">About us</a></li>
        <li><a href="/blog">Lawn care guides</a></li>
        <li><a href="/#contact">Get a free quote</a></li>
        <li><a href="{GBP}" rel="noopener" target="_blank">Find us on Google</a></li>
        <li><a href="/lawn-mowing-kambah">Lawn mowing Kambah</a></li>
        <li><a href="/lawn-mowing-woden-valley">Lawn mowing Woden Valley</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <span>ABN Registered | Fully Insured | Est. 2021</span>
      <span>&copy; 2026 {LEGAL}</span>
    </div>
  </div>
</footer>'''


SERVICE_OPTIONS = [n for _, n, *_ in SERVICES] + ["Something else / not sure"]
SIZE_OPTIONS = ["Courtyard or unit (under 200 m²)", "Standard block (200–600 m²)", "Large block (600–1,000 m²)", "Acreage or commercial site", "Not sure"]


def quote_form(prefix, compact=False):
    """Custom quote form. Field names match the GHL contact fields: full_name, email, phone,
    property_address, postal_code, property_size, service_needed, job_notes. The external
    tracking script captures the submission; the page then redirects to the thank-you page."""
    def f(key, label, tag="input", extra="", required=True, span=False, options=None, placeholder=""):
        i = f"{prefix}-{key}"
        req = " required" if required else ""
        if tag == "select":
            opts = '<option value="" disabled selected>Select…</option>' + "".join(f'<option value="{esc(o)}">{esc(o)}</option>' for o in options)
            ctl = f'<select id="{i}" name="{key}" data-field="{key}"{req}>{opts}</select>'
        elif tag == "textarea":
            ctl = f'<textarea id="{i}" name="{key}" data-field="{key}" rows="3" placeholder="{esc(placeholder)}"{req}></textarea>'
        else:
            ctl = f'<input id="{i}" name="{key}" data-field="{key}" placeholder="{esc(placeholder)}"{extra}{req}>'
        return f'<div class="fld{" span" if span else ""}"><label for="{i}">{esc(label)}{"" if required else " <span>(optional)</span>"}</label>{ctl}</div>'
    return f'''<form class="quote-form{" compact" if compact else ""}" id="{prefix}-form" novalidate="" data-thank-you="{THANK_YOU}" aria-label="Request a free quote">
  <div class="fgrid">
    {f("full_name", "Full name", extra=' type="text" autocomplete="name"', placeholder="Jane Citizen")}
    {f("email", "Email", extra=' type="email" autocomplete="email" inputmode="email"', placeholder="you@example.com")}
    {f("phone", "Phone", extra=' type="tel" autocomplete="tel" inputmode="tel" pattern="[0-9+ ()-]{{8,}}"', placeholder="04xx xxx xxx")}
    {f("postal_code", "Postcode", extra=' type="text" autocomplete="postal-code" inputmode="numeric" pattern="[0-9]{{4}}" maxlength="4"', placeholder="2611")}
    {f("property_address", "Property address", extra=' type="text" autocomplete="street-address"', span=True, placeholder="12 Example Street, Kambah")}
    {f("property_size", "Property size", tag="select", options=SIZE_OPTIONS)}
    {f("service_needed", "Service needed", tag="select", options=SERVICE_OPTIONS)}
    {f("job_notes", "Job notes", tag="textarea", required=False, span=True, placeholder="What needs doing, how often, access details, anything we should know.")}
  </div>
  <div class="hp" aria-hidden="true"><label for="{prefix}-qf-extra">Leave this field empty</label><input type="text" id="{prefix}-qf-extra" name="qf_extra" tabindex="-1" autocomplete="off" data-lpignore="true" data-1p-ignore="true"></div>
  <input type="hidden" name="source_page" value="">
  <button class="btn btn-primary fsubmit" type="submit">Send my quote request {icon("arrow")}</button>
  <p class="fnote">Free, no-obligation quote. We reply by phone or email, usually the same business day. Or call <a href="{TEL}">{PHONE}</a>.</p>
  <p class="ferror" role="alert" hidden>Please check the highlighted fields.</p>
</form>'''


def quote_modal():
    return f'''<div class="qm-backdrop" id="quote-modal" role="dialog" aria-modal="true" aria-labelledby="qm-title" hidden>
  <div class="qm">
    <button class="qm-close" type="button" aria-label="Close quote form">{icon("close")}</button>
    <div class="qm-head"><img src="/images/dtrh-logo-104.webp" width="48" height="48" alt="" loading="lazy" decoding="async"><div><span class="eyebrow">Free quote</span><h2 id="qm-title">Tell us about the job</h2><p>Takes about a minute. We come back with a clear, upfront quote.</p></div></div>
    {quote_form("m", compact=True)}
  </div>
</div>'''


def contact_section(heading="Get a free lawn mowing Canberra quote", line="Tell us about your lawn or garden, whether it is lawn mowing Canberra wide on a schedule or a one-off tidy, and we will come back with a clear, upfront quote. No obligation."):
    return f'''<section class="section" id="contact">
  <div class="wrap">
    <div class="contact-grid">
      <div class="rv">
        <span class="eyebrow">Contact</span>
        <h2>{esc(heading)}</h2>
        <p class="lead">{esc(line)}</p>
        <div class="nap">
          <a href="{TEL}"><span class="ico">{icon("phone")}</span><span>{PHONE}<small>Call for a quick answer</small></span></a>
          <a href="{SMS}"><span class="ico">{icon("sms")}</span><span>Text {PHONE}<small>Send a photo of the job</small></span></a>
          <a href="mailto:{EMAIL}"><span class="ico">{icon("mail")}</span><span>{EMAIL}<small>Email us any time</small></span></a>
          <div><span class="ico">{icon("pin")}</span><span>Canberra, ACT, Australia<small>Service-area business: ACT and Queanbeyan region</small></span></div>
          <div><span class="ico">{icon("clock")}</span><span>Hours: {HOURS}<small>{NAME}</small></span></div>
        </div>
      </div>
      <div class="rv rv-d1">
        <p class="fallback">Prefer to talk? Call or text <a href="{TEL}">{PHONE}</a> (<a href="{SMS}">SMS</a>) or email <a href="mailto:{EMAIL}">{EMAIL}</a></p>
        <div class="form-wrap">
{quote_form("q")}
        </div>
      </div>
    </div>
  </div>
</section>'''


def faq_section(faqs, heading="Frequently asked questions", eyebrow="FAQ", lead=None):
    items = "\n".join(
        f'<details class="rv"><summary>{esc(q)}<span class="plus">{icon("plus")}</span></summary><div class="ans"><p>{esc(a)}</p></div></details>'
        for q, a in faqs)
    lead_html = f'<p class="lead">{esc(lead)}</p>' if lead else ""
    return f'''<section class="section" id="faq">
  <div class="wrap">
    <div class="center rv"><span class="eyebrow">{esc(eyebrow)}</span><h2>{esc(heading)}</h2>{lead_html}</div>
    <div class="faq" style="margin-top:32px">
{items}
    </div>
  </div>
</section>'''


def business_schema():
    return {
        "@type": "LocalBusiness",
        "@id": BIZ_ID,
        "name": NAME,
        "legalName": LEGAL,
        "alternateName": "Down the Rabbit Hole (Aust) Pty Ltd",
        "slogan": "Taking the headaches away",
        "foundingDate": "2021",
        "telephone": "+61 423 720 317",
        "email": EMAIL,
        "url": SITE + "/",
        "image": f"{SITE}/images/{HERO_IMAGE}.webp",
        "logo": f"{SITE}/images/dtrh-logo.png",
        "priceRange": "$$",
        "address": {"@type": "PostalAddress", "addressLocality": "Canberra", "addressRegion": "ACT", "addressCountry": "AU"},
        "areaServed": [{"@type": "City", "name": "Canberra"}] + [{"@type": "Place", "name": d[0].replace(" & NSW", "")} for d in DISTRICTS],
        "sameAs": [FB, IG, GBP],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": HOURS, "closes": HOURS}],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Lawn and garden services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "url": f"{SITE}/{s}"}}
                for s, n, *_ in SERVICES[:9]
            ],
        },
    }


def jsonld(graph):
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "</script>"


def faq_schema(faqs):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def breadcrumb_schema(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def page(*, path, title, description, body, graph, active="", over_hero=False, og_image=None, robots=None, preload_image=None):
    assert len(title) <= 60, f"title too long ({len(title)}): {title}"
    assert 150 <= len(description) <= 160, f"description length {len(description)}: {path}"
    canonical = SITE + ("/" if path == "/" else path)
    og_image = og_image or f"{SITE}/images/{HERO_IMAGE}.webp"
    robots_tag = f'<meta name="robots" content="{robots}">' if robots else ""
    return f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
{robots_tag}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:locale" content="en_AU">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B2F5F">
<link rel="icon" href="/images/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
{preload_image or ""}
<link rel="preload" href="/assets/fonts/outfit-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/hanken-grotesk-var.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
{jsonld(graph)}
<script src="/assets/site.js" defer></script>
<script 
  src="https://app.downtherabbitholeaust.com/js/external-tracking.js"
  data-tracking-id="tk_6f4c1089fe214ae6baa8c2dc37522e82" defer>
</script>
</head>
<body>
{header(active, over_hero)}
<main id="main">
{body}
</main>
{footer()}
{quote_modal() if active != "thanks" else ""}
<noscript><img height="1" width="1" style="display:none" alt="" src="https://www.facebook.com/tr?id=25766325546287202&ev=PageView&noscript=1"></noscript>
</body>
</html>
'''


def write(path, content):
    fn = "index.html" if path == "/" else path.strip("/") + ".html"
    full = os.path.join(ROOT, fn)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {fn} ({len(content.encode())//1024} KB)")


# ---------- homepage ----------

def home():
    cards = "\n".join(
        f'<a class="card rv rv-d{i%3}" href="/{s}"><span class="ico">{icon(ic)}</span><h3>{esc(n)}</h3><p>{esc(blurb)}</p><span class="more">{esc(n)} Canberra {icon("arrow")}</span></a>'
        for i, (s, n, _, ic, blurb) in enumerate(SERVICES[:9]))
    districts = "\n".join(
        f'<div class="district rv"><h3><a href="{u}">{esc(n)}</a></h3><p>{esc(", ".join(subs))}</p></div>'
        for n, u, subs in DISTRICTS)
    thumbs = "\n".join(
        f'<button class="ba-thumb{" active" if i == 0 else ""}" type="button" aria-pressed="{"true" if i == 0 else "false"}" data-before="/images/{j}-before-800.webp" data-after="/images/{j}-after-800.webp" data-before-alt="Before: {esc(b)}" data-after-alt="After: {esc(a)}" data-caption="{esc(lbl)}: drag the handle to compare before and after." aria-label="Show {esc(lbl)} before and after"><img src="/images/{j}-after-400.webp" width="400" height="300" alt="" loading="lazy" decoding="async"></button>'
        for i, (j, lbl, b, a) in enumerate(PAIRS))
    j0, l0, b0, a0 = PAIRS[0]
    posts = "\n".join(
        f'<a class="post rv rv-d{i}" href="{u}"><time datetime="{POSTS[u][1]}">{POSTS[u][1][8:10]} {["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][int(POSTS[u][1][5:7])]} {POSTS[u][1][:4]}</time><h3>{esc(POSTS[u][0])}</h3><p>{esc(POSTS[u][2])}</p><span class="more" style="font-weight:700;color:var(--navy)">Read the guide →</span></a>'
        for i, u in enumerate(LATEST_POSTS))
    hw, hh = img_dims(HERO_IMAGE)
    body = f'''
<section class="hero">
  <div class="hero-media"><img src="/images/{HERO_IMAGE}.webp" srcset="/images/{HERO_IMAGE}-800.webp 800w, /images/{HERO_IMAGE}.webp {hw}w" sizes="100vw" width="{hw}" height="{hh}" alt="Lawn mowing Canberra: a mowed front lawn, clipped hedge and clean driveway under autumn trees after a visit from Down the Rabbit Hole AUST" fetchpriority="high" decoding="async"></div>
  <div class="hero-scrim" aria-hidden="true"></div>
  <div class="wrap hero-inner">
    <span class="eyebrow">Taking the headaches away · Est. 2021</span>
    <h1>Lawn Mowing Canberra — Reliable, Insured Lawn Care &amp; Garden Maintenance</h1>
    <p class="lead">Lawn mowing Canberra homeowners rely on: scheduled mowing, garden maintenance, hedge trimming and clean-ups for homes and businesses across Weston Creek, Woden, Tuggeranong and Belconnen. Upfront quotes, and the green waste leaves with us.</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="{TEL}">{icon("phone")}Call {PHONE}</a>
      <a class="btn btn-ghost" href="#contact" data-open-quote>Get a Free Quote {icon("arrow")}</a>
    </div>
    <div class="trust-strip">
      <span>{icon("check")}Fully insured</span><span>{icon("check")}ABN registered</span><span>{icon("check")}60+ Canberra lawns maintained</span><span>{icon("check")}Local Canberra team</span><span>{icon("check")}Est. 2021</span>
    </div>
  </div>
</section>

<section class="trust-bar" aria-label="Why customers choose us">
  <div class="wrap">
    <div class="trust-grid">
      <div class="trust-item rv"><span class="ico">{icon("shield")}</span><span>Fully insured<small>Public liability cover on every job</small></span></div>
      <div class="trust-item rv rv-d1"><span class="ico">{icon("badge")}</span><span>ABN registered<small>{LEGAL}</small></span></div>
      <div class="trust-item rv rv-d2"><span class="ico">{icon("mower")}</span><span>60+ Canberra lawns maintained<small>Residential and commercial lawn mowing Canberra wide</small></span></div>
      <div class="trust-item rv rv-d3"><span class="ico">{icon("pin")}</span><span>Local Canberra team<small>Locally operated, est. 2021</small></span></div>
    </div>
  </div>
</section>

<section class="section" id="services">
  <div class="wrap">
    <div class="section-head rv">
      <div><span class="eyebrow">Our services</span><h2>Lawn and garden services across Canberra</h2></div>
      <p class="lead">{NAME} is a lawn mowing Canberra service first, and most customers ask us to look after the rest of the yard too. Every service has its own page with what is included and what to expect.</p>
    </div>
    <div class="grid grid-3">
{cards}
    </div>
    <p style="margin-top:22px;color:var(--muted)">Also available: <a href="/weed-spraying">weed spraying for bindi and broadleaf weeds</a>. See the <a href="/services">full list of services</a>.</p>
  </div>
</section>

<section class="section" id="about" style="background:#fff">
  <div class="wrap">
    <div class="about-grid">
      <div class="about-media rv">
        {picture("garden-tidy-job", "Garden tidy: a brick path and garden beds at a Canberra home after weeding and edging", sizes="(max-width: 900px) 100vw, 55vw")}
        <div class="about-badge"><img src="/images/dtrh-logo-104.webp" width="56" height="56" alt="" loading="lazy" decoding="async"><span><strong>Est. 2021</strong><small>Locally operated in Canberra</small></span></div>
      </div>
      <div class="rv rv-d1">
        <span class="eyebrow">About us</span>
        <h2>A locally operated Canberra business, taking the headaches away</h2>
        <p>{NAME} is a locally operated Canberra business delivering consistent, on-time lawn mowing Canberra wide, along with garden maintenance, hedge trimming and yard clean-ups. We started in 2021, we are fully insured and ABN registered, and we currently maintain more than 60 lawns across the ACT and the Queanbeyan region for homeowners, landlords, strata groups and small businesses.</p>
        <p>Our lawn mowing Canberra customers stay with us because we turn up when we say we will, quote before we start, and take the green waste with us when we leave. Whether you want ongoing lawn care or a one-off tidy before an inspection, we keep lawn and garden maintenance simple.</p>
        <ul class="checks">
          <li>{icon("check")}Local Canberra team with professional equipment</li>
          <li>{icon("check")}Clear quotes with no surprises</li>
          <li>{icon("check")}Reliable, on-time scheduled visits</li>
          <li>{icon("check")}Respectful of your property, pets and neighbours</li>
          <li>{icon("check")}Equipped for small courtyards and large blocks</li>
        </ul>
        <div style="margin-top:24px;display:flex;gap:12px;flex-wrap:wrap"><a class="btn btn-navy" href="/about">More about us</a><a class="btn btn-outline" href="#contact">Get a Free Quote</a></div>
      </div>
    </div>
  </div>
</section>

<section class="section on-navy" id="process">
  <div class="wrap">
    <div class="center rv"><span class="eyebrow">How it works</span><h2>From first call to a tidy yard in four steps</h2><p class="lead">Booking lawn mowing Canberra wide should be simple. Here is what happens after you get in touch.</p></div>
    <div class="steps" style="margin-top:40px">
      <div class="step rv"><span class="num">1</span><h3>Quote</h3><p>Call, text or send the form. We confirm what you need and give you a clear, upfront quote.</p></div>
      <div class="step rv rv-d1"><span class="num">2</span><h3>Schedule</h3><p>Pick a one-off visit or a regular slot. We turn up on the agreed day, whether you are home or not.</p></div>
      <div class="step rv rv-d2"><span class="num">3</span><h3>Mow and maintain</h3><p>Mowing, edging, hedges, weeding and garden care done properly with professional equipment.</p></div>
      <div class="step rv rv-d3"><span class="num">4</span><h3>Tidy and remove waste</h3><p>Paths blown clean and clippings, branches and debris loaded and taken away. No green waste left behind.</p></div>
    </div>
  </div>
</section>

<section class="section" id="areas">
  <div class="wrap">
    <div class="areas-grid">
      <div>
        <div class="rv"><span class="eyebrow">Areas we service</span><h2>Lawn mowing Canberra suburbs: where we work</h2>
        <p class="lead">Our lawn mowing Canberra service covers seven districts across the ACT and the Queanbeyan region. Weston Creek is our home patch, and we run regular rounds through Woden Valley, Tuggeranong and Belconnen every week.</p></div>
        <div class="districts" style="margin-top:28px">
{districts}
        </div>
      </div>
      <div class="map-card rv rv-d1">
        <iframe src="{MAP_EMBED}" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" title="Map of the Down the Rabbit Hole AUST service area around Canberra"></iframe>
        <div class="rating">
          <span class="score">4.8</span>
          <span><span class="stars" role="img" aria-label="4.8 out of 5 stars">{icon("star")*5}</span><small>Google rating from 85 reviews</small><a href="{GBP}" rel="noopener" target="_blank">Read our Google reviews →</a></span>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section" id="proof" style="background:#fff">
  <div class="wrap">
    <div class="section-head rv"><div><span class="eyebrow">Real jobs, real results</span><h2>Before and after: recent lawn mowing Canberra jobs</h2></div><p class="lead">Every photo below is a job we completed in Canberra. Drag the handle to compare, or pick another job from the thumbnails.</p></div>
    <div class="proof-grid">
      <div class="rv">
        <div class="ba" id="ba-featured">
          <img class="ba-before" src="/images/{j0}-before-800.webp" width="800" height="600" alt="Before: {esc(b0)}" loading="lazy" decoding="async">
          <img class="ba-after" src="/images/{j0}-after-800.webp" width="800" height="600" alt="After: {esc(a0)}" loading="lazy" decoding="async">
          <span class="ba-tag before">Before</span><span class="ba-tag after">After</span>
          <div class="ba-handle" aria-hidden="true"></div>
          <input class="ba-range" type="range" min="0" max="100" value="50" aria-label="Compare before and after photos">
        </div>
        <p class="ba-caption" id="ba-caption">{esc(l0)}: drag the handle to compare before and after.</p>
        <div class="ba-thumbs">
{thumbs}
        </div>
      </div>
      <div class="rv rv-d1">
        <div class="review-card">
          <div class="g"><span class="score">4.8</span><span><span class="stars" role="img" aria-label="4.8 out of 5 stars">{icon("star")*5}</span><small style="color:var(--muted)">Google rating, 85 reviews</small></span></div>
          <h3>What lawn mowing Canberra customers say</h3>
          <!-- REVIEWS: paste 3–5 Google reviews here (reviewer first name, date, review text). Source: {GBP} -->
          <p style="color:var(--muted)">We are adding recent customer reviews here. Until then, read them straight from our Google Business Profile.</p>
          <a class="btn btn-navy" href="{GBP}" rel="noopener" target="_blank">Read reviews on Google</a>
        </div>
        <div class="aside-card" style="margin-top:18px">
          <h3>Commercial and strata grounds</h3>
          {picture("commercial-grounds-after-1", "Commercial grounds in Canberra: a mowed verge and clean car park entry after our visit", sizes="(max-width: 960px) 100vw, 30vw")}
          <p style="margin:12px 0 0;color:var(--muted)">We also keep commercial sites, strata common areas and Defence housing tidy on a regular schedule. <a href="/garden-maintenance">Garden maintenance for strata and rentals →</a></p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section" id="guides">
  <div class="wrap">
    <div class="section-head rv"><div><span class="eyebrow">Recent guides</span><h2>Lawn mowing Canberra tips from the team</h2></div><a class="btn btn-outline" href="/blog">All guides</a></div>
    <div class="grid grid-3">
{posts}
    </div>
  </div>
</section>

{faq_section(HOME_FAQS, "Lawn mowing Canberra: your questions answered", "FAQ")}

{contact_section()}
'''
    graph = [
        business_schema(),
        {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": NAME, "publisher": {"@id": BIZ_ID}},
        {"@type": "WebPage", "@id": SITE + "/#webpage", "url": SITE + "/", "name": "Lawn Mowing Canberra | Down the Rabbit Hole Lawn Care", "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": BIZ_ID}},
        faq_schema(HOME_FAQS),
    ]
    write("/", page(path="/", title="Lawn Mowing Canberra | Down the Rabbit Hole Lawn Care",
                    description="Lawn mowing Canberra homeowners rely on. Insured local team for mowing, garden maintenance, hedges & clean-ups in Weston Creek, Woden & Tuggeranong. Free quote.",
                    body=body, graph=graph, active="home", over_hero=True,
                    preload_image=f'<link rel="preload" as="image" href="/images/{HERO_IMAGE}.webp" imagesrcset="/images/{HERO_IMAGE}-800.webp 800w, /images/{HERO_IMAGE}.webp {hw}w" imagesizes="100vw" fetchpriority="high">'))


# ---------- service / suburb pages ----------

def load_copy(slug):
    return json.load(open(os.path.join(COPY, slug + ".json"), encoding="utf-8"))


def render_sections(sections):
    out = []
    for sec in sections:
        out.append(f'<h2>{esc(sec["h2"])}</h2>')
        for p in sec.get("paras", []):
            out.append(f"<p>{esc(p)}</p>")
        if sec.get("bullets"):
            out.append('<ul class="checks">' + "".join(f"<li>{icon('check')}<span>{esc(b)}</span></li>" for b in sec["bullets"]) + "</ul>")
    return "\n".join(out)


SERVICE_IMAGES = {
    "lawn-mowing": ("lawn-after-mowing", "Grass mowing Canberra: a freshly mowed and edged front lawn on a suburban corner block"),
    "lawn-care": ("garden-tidy-after", "Lawn care Canberra: a thick, green back lawn with stepping stones and trimmed hedges after seasonal care"),
    "gardening-services": ("garden-bed-restore-after", "Gardener Canberra: a garden bed weeded, mulched and edged with a stepping-stone path"),
    "garden-maintenance": ("service-garden-maintenance", "Garden maintenance Canberra: mulched raised beds and a tidy courtyard garden"),
    "hedge-trimming": ("garden-clean-up-2-after", "Hedge trimming Canberra: a neatly clipped hedge along a driveway after our visit"),
    "yard-clean-ups": ("service-yard-clean-ups", "Yard clean up Canberra: an overgrown back yard before and after being cleared and tidied"),
    "green-waste-removal": ("service-green-waste-removal", "Green waste removal Canberra: overgrown shrubs and prunings cleared from a back yard"),
    "rubbish-removal": ("service-rubbish-removal", "Rubbish removal Canberra: a trailer loaded with garden rubbish and prunings ready for the tip"),
    "dva-lawn-care": ("service-dva-lawn-care", "DVA lawn care Canberra: garden clean-up photos from a veteran's residential property"),
    "weed-spraying": ("extra-a-after", "Weed spraying Canberra: a mowed nature strip lawn beside a footpath in a new Canberra estate"),
    "services": ("commercial-grounds-result", "Lawn and garden services Canberra: a mowed back lawn and clean patio, managed and ready for business"),
    "lawn-mowing-kambah": ("overgrown-clean-up-after", "Lawn mowing Kambah: a Tuggeranong back yard and patio after mowing and a full clean-up"),
    "lawn-mowing-woden-valley": ("garden-clean-up-1-after", "Lawn mowing Woden Valley: a clipped hedge, lawn and driveway under autumn trees at a Woden home"),
}


def service_page(slug, is_suburb=False):
    c = load_copy(slug)
    img_name, img_alt = SERVICE_IMAGES[slug]
    related = "".join(
        f'<a class="card" href="/{r}"><span class="ico">{icon(next(s[3] for s in SERVICES if s[0]==r))}</span><h3>{esc(SERVICE_NAMES[r])}</h3><p>{esc(next(s[4] for s in SERVICES if s[0]==r))}</p><span class="more">See {esc(SERVICE_NAMES[r].lower())} {icon("arrow")}</span></a>'
        for r in c["related"] if r in SERVICE_NAMES)
    guides = "".join(f'<li><a href="{g}">{esc(POSTS[g][0])}</a></li>' for g in c.get("guides", []) if g in POSTS)
    faqs = [(f["q"], f["a"]) for f in c["faqs"]]
    suburb_page = c.get("suburb_page", "/lawn-mowing-kambah")
    suburb_label = {"/lawn-mowing-kambah": "Lawn mowing Kambah", "/lawn-mowing-woden-valley": "Lawn mowing Woden Valley"}.get(suburb_page, suburb_page)
    chips = "".join(f'<span class="chip">{esc(s)}</span>' for s in c.get("suburbs", []))
    crumbs = [("Home", "/")] + ([("Services", "/services")] if not is_suburb and slug != "services" else []) + ([("Areas", "/#areas")] if is_suburb else []) + [(c["h1"].split(" — ")[0].split(" for ")[0], "/" + slug)]
    crumb_html = "".join(f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{esc(n)}</li>' for i, (n, u) in enumerate(crumbs))
    service_cards = ""
    if slug == "services":
        blurbs = c.get("service_blurbs", {})
        service_cards = '<div class="grid grid-3" style="margin:40px 0 10px">' + "".join(
            f'<a class="card rv" href="/{s}"><span class="ico">{icon(ic)}</span><h3>{esc(n)}</h3><p>{esc(blurbs.get(s, blurb))}</p><span class="more">{esc(n)} {icon("arrow")}</span></a>'
            for s, n, _, ic, blurb in SERVICES) + "</div>"
    body = f'''
<section class="page-hero">
  <div class="wrap">
    <ol class="crumbs" aria-label="Breadcrumb">{crumb_html}</ol>
    <div class="page-hero-grid">
      <div>
        <span class="eyebrow">{esc(c["eyebrow"])}</span>
        <h1>{esc(c["h1"])}</h1>
        <p class="lead">{esc(c["lede"])}</p>
        <div class="hero-cta"><a class="btn btn-primary" href="{TEL}">{icon("phone")}Call {PHONE}</a><a class="btn btn-ghost" href="#contact" data-open-quote>Get a Free Quote {icon("arrow")}</a></div>
        <div class="trust-strip"><span>{icon("check")}Fully insured</span><span>{icon("check")}ABN registered</span><span>{icon("check")}60+ Canberra lawns maintained</span><span>{icon("check")}Est. 2021</span></div>
      </div>
      <div class="hero-photo">{picture(img_name, img_alt, lazy=False, priority=True)}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    {service_cards}
    <div class="article-grid">
      <article class="article">
        <div class="intro">{"".join(f"<p>{esc(p)}</p>" for p in c["intro"])}</div>
        {render_sections(c["sections"])}
        <div class="cta-band rv" style="margin-top:40px"><div><h2 style="margin-top:0">{esc(c["cta_heading"])}</h2><p>{esc(c["cta_line"])}</p></div><a class="btn btn-navy" href="#contact">Get a Free Quote</a></div>
      </article>
      <aside class="aside">
        <div class="aside-card navy">
          <h3>Free, upfront quote</h3>
          <p>Call or text {PHONE}, or send the form. We reply with a clear quote before any work starts.</p>
          <a class="btn btn-primary" href="{TEL}">{icon("phone")}Call {PHONE}</a>
          <a class="btn btn-ghost" href="#contact" data-open-quote>Request a quote</a>
        </div>
        <div class="aside-card">
          <h3>Suburbs we service</h3>
          <div class="chips">{chips}</div>
          <p style="margin:14px 0 0;font-size:.95rem"><a href="/#areas">See every Canberra suburb we cover →</a></p>
        </div>
        <div class="aside-card">
          <h3>Related services</h3>
          <ul>{"".join(f'<li><a href="/{r}">{esc(SERVICE_NAMES[r])}</a></li>' for r in c["related"] if r in SERVICE_NAMES)}<li><a href="{suburb_page}">{esc(suburb_label)}</a></li><li><a href="/services">All services</a></li></ul>
        </div>
        {f'<div class="aside-card"><h3>Related guides</h3><ul>{guides}</ul></div>' if guides else ""}
      </aside>
    </div>
  </div>
</section>

<section class="section-tight" style="background:#fff">
  <div class="wrap">
    <div class="section-head rv"><div><span class="eyebrow">Related</span><h2>Services that pair well with this one</h2></div><a class="btn btn-outline" href="/services">All services</a></div>
    <div class="grid grid-3">{related}<a class="card" href="{suburb_page}"><span class="ico">{icon("pin")}</span><h3>{esc(suburb_label)}</h3><p>Local lawn mowing and garden care with a dedicated page for the area.</p><span class="more">See the area page {icon("arrow")}</span></a></div>
  </div>
</section>

{faq_section(faqs, "Questions about " + (SERVICE_TYPES.get(slug, c["h1"].split(" — ")[0]).lower() if slug != "services" else "our services") + " in Canberra")}

{contact_section(c["cta_heading"], c["cta_line"])}
'''
    url = f"{SITE}/{slug}"
    graph = [business_schema(),
             {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": c["title"], "description": c["description"], "isPartOf": {"@id": SITE + "/#website"}, "breadcrumb": {"@id": url + "#breadcrumb"}, "primaryImageOfPage": f"{SITE}/images/{img_name}.webp"},
             dict(breadcrumb_schema(crumbs), **{"@id": url + "#breadcrumb"}),
             faq_schema(faqs)]
    if slug != "services":
        graph.insert(1, {
            "@type": "Service", "@id": url + "#service",
            "name": c["h1"].split(" — ")[0], "serviceType": SERVICE_TYPES.get(slug, "Lawn mowing"),
            "description": c["description"], "url": url, "image": f"{SITE}/images/{img_name}.webp",
            "provider": {"@id": BIZ_ID},
            "areaServed": [{"@type": "Place", "name": s} for s in c.get("suburbs", [])] + [{"@type": "City", "name": "Canberra"}],
            "offers": {"@type": "Offer", "availability": "https://schema.org/InStock", "priceCurrency": "AUD", "url": url + "#contact", "description": "Free upfront quote"},
        })
    write("/" + slug, page(path="/" + slug, title=c["title"], description=c["description"], body=body, graph=graph,
                           active="services", over_hero=True, og_image=f"{SITE}/images/{img_name}.webp"))


# ---------- about ----------

def about():
    faqs = HOME_FAQS[6:9]
    body = f'''
<section class="page-hero">
  <div class="wrap">
    <ol class="crumbs" aria-label="Breadcrumb"><li><a href="/">Home</a></li><li aria-current="page">About</li></ol>
    <div class="page-hero-grid">
      <div>
        <span class="eyebrow">About us · Est. 2021</span>
        <h1>About Down the Rabbit Hole AUST: Canberra lawn and garden care since 2021</h1>
        <p class="lead">A locally operated Canberra business that mows, maintains and tidies more than 60 lawns and gardens across the ACT and Queanbeyan.</p>
        <div class="hero-cta"><a class="btn btn-primary" href="{TEL}">{icon("phone")}Call {PHONE}</a><a class="btn btn-ghost" href="#contact" data-open-quote>Get a Free Quote {icon("arrow")}</a></div>
        <div class="trust-strip"><span>{icon("check")}Fully insured</span><span>{icon("check")}ABN registered</span><span>{icon("check")}Residential &amp; commercial</span><span>{icon("check")}Locally operated</span></div>
      </div>
      <div class="hero-photo">{picture("leaf-removal", "Leaf removal: a swept and tidy paved entry and garden at a Canberra home", lazy=False, priority=True)}</div>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="article-grid">
      <article class="article">
        <div class="intro"><p>Down the Rabbit Hole AUST is the trading name of {LEGAL}, a lawn mowing and garden maintenance business based in Canberra. We started in 2021 with a mower, a trailer and a simple idea: turn up when we say we will, quote before we start, and leave every property tidier than we found it. That idea is still the whole business.</p>
        <p>Today we look after more than 60 lawns across the ACT and the Queanbeyan region on regular rounds, plus one-off clean-ups, hedge work and rubbish and green waste removal. Our customers are homeowners, landlords and property managers, strata committees, small businesses and veterans using DVA services.</p></div>
        <h2>What we do</h2>
        <p>Our core work is scheduled lawn mowing with clean edges and clippings removed. Around that we offer lawn care, gardening and garden maintenance, hedge trimming, weed spraying, yard clean-ups for sales and end of lease, and green waste and rubbish removal. Every service has its own page, and every job finishes with the waste loaded and taken away.</p>
        <ul class="checks">{"".join(f'<li>{icon("check")}<a href="/{s}">{esc(n)}</a></li>' for s, n, *_ in SERVICES)}</ul>
        <h2>Where we work</h2>
        <p>Weston Creek is our home patch. From there we run regular rounds through Woden Valley, Tuggeranong and Belconnen, and we service the Inner North, Inner South and Queanbeyan, Jerrabomberra and Googong. <a href="/#areas">See the full suburb list.</a></p>
        <h2>How we work</h2>
        <p>Fully insured and ABN registered, we use professional equipment sized for everything from a townhouse courtyard to a large established block. We are respectful of pets, neighbours and gardens, and we keep the same crew on your property wherever we can so you see familiar faces. You do not need to be home while we work, as long as we can get in.</p>
        <h2>Guides and advice</h2>
        <p>The team writes practical, Canberra-specific guides on mowing, frost recovery, bindi control, mulching and seasonal garden care. Read them on the <a href="/blog">lawn care guides page</a>.</p>
        <div class="cta-band rv" style="margin-top:40px"><div><h2 style="margin-top:0">Want a lawn you do not have to think about?</h2><p>Call, text or send the form and we will quote your property.</p></div><a class="btn btn-navy" href="#contact">Get a Free Quote</a></div>
      </article>
      <aside class="aside">
        <div class="aside-card navy"><h3>Talk to the team</h3><p>Call or text {PHONE}, or email {EMAIL}.</p><a class="btn btn-primary" href="{TEL}">{icon("phone")}Call {PHONE}</a><a class="btn btn-ghost" href="mailto:{EMAIL}">Email us</a></div>
        <div class="aside-card"><h3>Business details</h3><ul style="display:grid;gap:8px;list-style:none;padding:0;margin:0"><li><strong>Legal name:</strong> {LEGAL}</li><li><strong>Trading as:</strong> {NAME}</li><li><strong>ABN:</strong> Registered</li><li><strong>Insurance:</strong> Fully insured</li><li><strong>Established:</strong> 2021</li><li><strong>Base:</strong> Canberra, ACT</li><li><strong>Hours:</strong> {HOURS}</li></ul></div>
        <div class="aside-card"><h3>Find us online</h3><ul><li><a href="{GBP}" rel="noopener" target="_blank">Google Business Profile</a></li><li><a href="{FB}" rel="noopener" target="_blank">Facebook</a></li><li><a href="{IG}" rel="noopener" target="_blank">Instagram</a></li></ul></div>
      </aside>
    </div>
  </div>
</section>
{faq_section(faqs, "Common questions about working with us")}
{contact_section("Get a free quote from a local Canberra team", "Tell us about your lawn or garden and we will come back with a clear, upfront quote.")}
'''
    url = SITE + "/about"
    graph = [business_schema(), {"@type": "AboutPage", "@id": url + "#webpage", "url": url, "name": "About Down the Rabbit Hole AUST", "isPartOf": {"@id": SITE + "/#website"}, "about": {"@id": BIZ_ID}}, breadcrumb_schema([("Home", "/"), ("About", "/about")]), faq_schema(faqs)]
    write("/about", page(path="/about", title="About Down the Rabbit Hole AUST | Canberra Lawn Care",
                         description="Down the Rabbit Hole AUST is a locally operated, fully insured Canberra lawn mowing and garden maintenance team, est. 2021, caring for 60+ lawns. Free quotes.",
                         body=body, graph=graph, active="about", over_hero=True, og_image=f"{SITE}/images/leaf-removal.webp"))


# ---------- 404 ----------

def notfound():
    body = f'''
<section class="notfound">
  <div class="wrap">
    <div class="big">4<span>0</span>4</div>
    <h1 style="font-size:clamp(1.6rem,3vw,2.4rem)">We could not find that page</h1>
    <p class="lead" style="margin-inline:auto">The link may be old or mistyped. Try one of these, or call {PHONE} and we will point you in the right direction.</p>
    <div class="hero-cta" style="justify-content:center"><a class="btn btn-navy" href="/">Homepage</a><a class="btn btn-primary" href="/services">Our services</a><a class="btn btn-outline" href="/#contact">Contact us</a></div>
    <p style="color:var(--muted)">Popular pages: <a href="/lawn-mowing">lawn mowing</a> · <a href="/garden-maintenance">garden maintenance</a> · <a href="/yard-clean-ups">yard clean-ups</a> · <a href="/blog">guides</a></p>
  </div>
</section>
'''
    graph = [business_schema()]
    write("/404", page(path="/404", title="Page Not Found | Down the Rabbit Hole AUST",
                       description="That page does not exist on the Down the Rabbit Hole AUST site. Head back to the homepage or our Canberra lawn and garden services, or call us on 0423 720 317.",
                       body=body, graph=graph, active="404", over_hero=False, robots="noindex, follow"))


# ---------- thank you ----------

def thankyou():
    tick = icon("check").replace("<svg", '<svg style="width:34px;height:34px;stroke:var(--orange-deep);fill:none;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round"', 1)
    body = f'''
<section class="notfound" style="min-height:60vh">
  <div class="wrap" style="max-width:720px">
    <span class="ico" style="width:72px;height:72px;border-radius:50%;background:var(--tint);display:grid;place-items:center;margin:0 auto 20px">{tick}</span>
    <h1 style="font-size:clamp(1.9rem,3.6vw,2.8rem)">Thanks, your quote request is in</h1>
    <p class="lead" style="margin-inline:auto">We have your details and will come back to you by phone or email, usually the same business day. If it is urgent, call or text {PHONE} now.</p>
    <div class="hero-cta" style="justify-content:center"><a class="btn btn-primary" href="{TEL}">{icon("phone")}Call {PHONE}</a><a class="btn btn-outline" href="/">Back to the homepage</a></div>
    <div class="steps" style="grid-template-columns:repeat(3,1fr);margin-top:36px;text-align:left">
      <div class="step" style="background:#fff;border-color:var(--line)"><span class="num">1</span><h3 style="color:var(--navy)">We read your notes</h3><p style="color:var(--muted)">Service, property size and suburb tell us what the job needs.</p></div>
      <div class="step" style="background:#fff;border-color:var(--line)"><span class="num">2</span><h3 style="color:var(--navy)">You get a clear quote</h3><p style="color:var(--muted)">Upfront pricing before any work starts. No surprises.</p></div>
      <div class="step" style="background:#fff;border-color:var(--line)"><span class="num">3</span><h3 style="color:var(--navy)">We book you in</h3><p style="color:var(--muted)">One-off visit or a regular slot, whichever suits.</p></div>
    </div>
    <p style="color:var(--muted);margin-top:28px">While you wait: <a href="/services">our services</a> · <a href="/blog">lawn care guides</a></p>
  </div>
</section>
'''
    graph = [business_schema()]
    write(THANK_YOU, page(path=THANK_YOU, title="Thanks, Your Quote Request Is In | Down the Rabbit Hole",
                          description="Thanks for requesting a quote from Down the Rabbit Hole AUST. We reply by phone or email, usually the same business day. Need it sooner? Call 0423 720 317.",
                          body=body, graph=graph, active="thanks", over_hero=False, robots="noindex, nofollow"))


# ---------- static files ----------

REDIRECTS = """# Netlify / Cloudflare Pages style redirects (status 301 unless noted)
/home                                              /                                             301
/hedge-trimming--lawn-care                         /hedge-trimming                               301
/dva-lawncare-services                             /dva-lawn-care                                301
/weed-spraying-prevention/                         /weed-spraying                                301
/weed-spraying-prevention                          /weed-spraying                                301
/blog/category/canberra-lawn-care-tips-guides      /blog                                         301
/categories/canberra-lawn-care-tips-guides         /blog                                         301
/blog/author/695b34992c0fabfb5cfaeec8              /about                                        301
/author/down-the-rabbit-hole-lawn-care-team        /about                                        301
/post/grass-mowing-canberra-guide-7692             /post/grass-mowing-canberra-guide             301
/post/ultimate-guide-to-green-waste-disposal-in-Canberra  /post/green-waste-canberra-disposal-guide  301
/blog/tag/*                                        /blog                                         301
# District pages not yet built: temporary redirect to the areas section. Remove each line when the page goes live.
/lawn-mowing-weston-creek                          /#areas                                       302
/lawn-mowing-tuggeranong                           /#areas                                       302
/lawn-mowing-belconnen                             /#areas                                       302
/lawn-mowing-inner-north                           /#areas                                       302
/lawn-mowing-inner-south                           /#areas                                       302
/lawn-mowing-queanbeyan                            /#areas                                       302
"""

HTACCESS = """# Apache equivalent of _redirects
RewriteEngine On
ErrorDocument 404 /404.html

# Serve clean URLs from .html files
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME}\\.html -f
RewriteRule ^([^.]+)$ $1.html [L]

Redirect 301 /home /
Redirect 301 /hedge-trimming--lawn-care /hedge-trimming
Redirect 301 /dva-lawncare-services /dva-lawn-care
RedirectMatch 301 ^/weed-spraying-prevention/?$ /weed-spraying
Redirect 301 /blog/category/canberra-lawn-care-tips-guides /blog
Redirect 301 /categories/canberra-lawn-care-tips-guides /blog
Redirect 301 /blog/author/695b34992c0fabfb5cfaeec8 /about
Redirect 301 /author/down-the-rabbit-hole-lawn-care-team /about
Redirect 301 /post/grass-mowing-canberra-guide-7692 /post/grass-mowing-canberra-guide
Redirect 301 /post/ultimate-guide-to-green-waste-disposal-in-Canberra /post/green-waste-canberra-disposal-guide
RedirectMatch 301 ^/blog/tag/.*$ /blog
# District pages not yet built (temporary)
RedirectMatch 302 ^/lawn-mowing-(weston-creek|tuggeranong|belconnen|inner-north|inner-south|queanbeyan)$ /#areas

<IfModule mod_headers.c>
  <FilesMatch "\\.(webp|png|woff2|css|js)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
</IfModule>
"""


def static_files(pages):
    open(os.path.join(ROOT, "_redirects"), "w").write(REDIRECTS)
    open(os.path.join(ROOT, ".htaccess"), "w").write(HTACCESS)
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /404\nDisallow: /thank-you\nSitemap: {SITE}/sitemap.xml\n")
    urls = "".join(f"  <url><loc>{SITE}{p}</loc><changefreq>monthly</changefreq><priority>{'1.0' if p=='/' else '0.8'}</priority></url>\n" for p in pages)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<!-- Blog posts (/blog and /post/...) are migrated separately; add them to this sitemap when they go live. -->\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")


def main():
    home()
    about()
    notfound()
    thankyou()
    pages = ["/", "/about", "/services"]
    for slug in ["services"] + [s[0] for s in SERVICES]:
        service_page(slug)
        if slug != "services":
            pages.append("/" + slug)
    for slug in ["lawn-mowing-kambah", "lawn-mowing-woden-valley"]:
        service_page(slug, is_suburb=True)
        pages.append("/" + slug)
    static_files(pages)


if __name__ == "__main__":
    main()
