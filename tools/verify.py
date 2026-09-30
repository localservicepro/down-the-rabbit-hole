#!/usr/bin/env python3
"""SEO / structure verification for the built site. Run after tools/build.py."""
import glob, json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYWORDS = {
    "index": "lawn mowing canberra", "lawn-mowing": "grass mowing canberra", "lawn-care": "lawn care canberra",
    "gardening-services": "gardener canberra", "garden-maintenance": "garden maintenance canberra",
    "hedge-trimming": "hedge trimming canberra", "yard-clean-ups": "yard clean up canberra",
    "green-waste-removal": "green waste removal canberra", "rubbish-removal": "rubbish removal canberra",
    "dva-lawn-care": "dva gardening services", "weed-spraying": "weed spraying canberra", "services": "lawn and garden services",
    "lawn-mowing-kambah": "lawn mowing kambah", "lawn-mowing-woden-valley": "lawn mowing woden valley",
    "lawn-mowing-weston-creek": "lawn mowing weston creek", "lawn-mowing-tuggeranong": "lawn mowing tuggeranong", "lawn-mowing-belconnen": "lawn mowing belconnen",
    "lawn-mowing-inner-north": "lawn mowing inner north", "lawn-mowing-inner-south": "lawn mowing inner south", "lawn-mowing-queanbeyan": "lawn mowing queanbeyan",
}
PLACEHOLDER_ROUTES = set()  # only /post/... (blog posts migrated separately) is exempt


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0; self.main = []; self.in_main = 0; self.h1 = []; self._h1 = False
        self.links = []; self.imgs = []; self.title = ""; self._title = False; self.desc = None; self.canon = None; self.ld = []; self._ld = False; self.kw_meta = False
    def handle_starttag(self, t, a):
        a = dict(a)
        if t in ("script", "style", "noscript"):
            self.skip += 1
            if t == "script" and a.get("type") == "application/ld+json": self._ld = True
        if t == "main": self.in_main += 1
        if t == "h1": self._h1 = True; self.h1.append("")
        if t == "title": self._title = True
        if t == "meta" and a.get("name") == "description": self.desc = a.get("content")
        if t == "meta" and a.get("name") == "keywords": self.kw_meta = True
        if t == "link" and a.get("rel") == "canonical": self.canon = a.get("href")
        if t == "a" and a.get("href"): self.links.append(a["href"])
        if t == "img": self.imgs.append(a)
        if t == "iframe": self.imgs.append(dict(a, iframe=True))
    def handle_endtag(self, t):
        if t in ("script", "style", "noscript"): self.skip -= 1; self._ld = False
        if t == "main": self.in_main -= 1
        if t == "h1": self._h1 = False
        if t == "title": self._title = False
    def handle_data(self, d):
        if self._ld: self.ld.append(d)
        if self._title: self.title += d
        if self.skip: return
        if self._h1: self.h1[-1] += d
        self.parts.append(d)
        if self.in_main: self.main.append(d)


def words(s):
    return re.findall(r"[A-Za-z0-9'’\-]+", s)


def density(text, kw):
    t = re.sub(r"\s+", " ", text.lower()).replace("-", " ").replace("’", "'")
    k = kw.replace("-", " ")
    occ = len(re.findall(re.escape(k), t))
    n = len(words(t))
    return occ, n, (occ / n * 100 if n else 0)


ALL_HTML = sorted(glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "*", "*.html")) + glob.glob(os.path.join(ROOT, "*", "*", "*.html")))
built = {os.path.relpath(f, ROOT)[:-5] for f in ALL_HTML}
ok = True
ids = set()
rows = []
for f in ALL_HTML:
    name = os.path.relpath(f, ROOT)[:-5]
    if name.endswith("/index") or name.endswith(os.sep + "index"):
        continue  # directory copy of a page
    if "http-equiv=\"refresh\"" in open(f, encoding="utf-8").read(400):
        continue  # redirect stub
    p = Text(); p.feed(open(f, encoding="utf-8").read())
    issues = []
    if len(p.h1) != 1: issues.append(f"h1 count {len(p.h1)}")
    kw = KEYWORDS.get(name)
    if kw:
        h1n = p.h1[0].lower().replace("-", " ").replace("—", " ")
        if kw not in h1n:
            if all(w in h1n.split() or w.rstrip("s") in [x.rstrip("s") for x in h1n.split()] for w in kw.split() if w != "and"):
                print(f"  ~ {name}: H1 has the keyword words but not the exact phrase (spec H1 kept verbatim)")
            else:
                issues.append("keyword not in H1")
    if len(p.title) > 60: issues.append(f"title {len(p.title)}")
    if not p.desc or not 150 <= len(p.desc) <= 160: issues.append(f"description {len(p.desc or '')}")
    exp = "https://downtherabbitholeaust.com/" + ("" if name == "index" else name.replace(os.sep, "/"))
    if p.canon != exp: issues.append(f"canonical {p.canon}")
    if p.kw_meta: issues.append("meta keywords present")
    for ld in p.ld:
        try:
            d = json.loads(ld)
            for node in d.get("@graph", []):
                if node.get("@type") == "LocalBusiness": ids.add(node.get("@id"))
        except Exception as e:
            issues.append(f"invalid JSON-LD: {e}")
    for a in p.imgs:
        if a.get("iframe"):
            if not a.get("title"): issues.append("iframe without title")
        elif "alt" not in a: issues.append(f"img without alt: {a.get('src')}")
        elif not a.get("width") or not a.get("height"): issues.append(f"img without dims: {a.get('src')}")
    for href in p.links:
        if href.startswith(("http", "mailto:", "tel:", "sms:", "#")): continue
        path = href.split("#")[0].split("?")[0]
        if not path: continue
        if path == "/": continue
        if path in PLACEHOLDER_ROUTES: continue
        if path.startswith("/images/") or path.startswith("/assets/"):
            if not os.path.exists(os.path.join(ROOT, path.lstrip("/"))): issues.append(f"missing asset {path}")
            continue
        if path.strip("/") not in built and path.strip("/") + "/index" not in built: issues.append(f"dead link {href}")
    for src in [a.get("src") for a in p.imgs if not a.get("iframe")]:
        if src and src.startswith("/") and not os.path.exists(os.path.join(ROOT, src.lstrip("/"))): issues.append(f"missing image {src}")
    main_text = " ".join(p.main); all_text = " ".join(p.parts)
    occ_m, n_m, d_m = density(main_text, kw) if kw else (0, len(words(main_text)), 0)
    occ_a, n_a, d_a = density(all_text, kw) if kw else (0, len(words(all_text)), 0)
    size = os.path.getsize(f) // 1024
    rows.append((name, size, len(p.title), len(p.desc or ""), n_m, occ_m, d_m, occ_a, d_a, len(p.h1)))
    for i in issues: print(f"  ! {name}: {i}"); ok = False
print(f"business @id values across pages: {ids}")
print(f"{'page':26s} {'KB':>4} {'title':>5} {'desc':>4} {'main words':>10} {'kw main':>8} {'dens%':>6} {'kw all':>7} {'dens%':>6} h1")
for r in rows:
    print(f"{r[0]:26s} {r[1]:4d} {r[2]:5d} {r[3]:4d} {r[4]:10d} {r[5]:8d} {r[6]:6.2f} {r[7]:7d} {r[8]:6.2f} {r[9]}")
# image size caps
for f in glob.glob(os.path.join(ROOT, "images", "*.webp")):
    s = os.path.getsize(f)
    if s > 200 * 1024: print(f"  ! {os.path.basename(f)} is {s//1024} KB (>200 KB)"); ok = False
hero = os.path.join(ROOT, "images", os.environ.get("HERO_IMAGE", "garden-clean-up-1-after") + ".webp")
print(f"hero {os.path.basename(hero)}: {os.path.getsize(hero)//1024} KB")
print("OK" if ok else "ISSUES FOUND")
sys.exit(0 if ok else 1)
