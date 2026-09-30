#!/usr/bin/env python3
"""Download the client's job photos from the shared Google Drive folder, resize
to max 1600px wide, convert to WebP (<=150 KB for the 1600px file, plus an 800px
variant), and write images/manifest.json with dimensions. Never hot-link Drive."""
import io, json, os, subprocess, sys, urllib.request
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images")
MANIFEST = json.load(open(os.path.join(ROOT, "tools", "image_manifest.json")))
MAX_W = 1600
CAP = 150 * 1024
os.makedirs(OUT, exist_ok=True)


def download(file_id: str) -> bytes:
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    try:
        import gdown  # handles the confirm interstitial
        buf = io.BytesIO()
        path = gdown.download(url, quiet=True, fuzzy=False)
        if path:
            data = open(path, "rb").read()
            os.remove(path)
            if data[:4] != b"<!DO" and data[:5] != b"<html":
                return data
    except Exception as e:  # fall through to curl
        print("gdown failed", file_id, e)
    data = subprocess.run(
        ["curl", "-sSL", "-A", "Mozilla/5.0", f"{url}&confirm=t"], capture_output=True
    ).stdout
    if data[:5].lower() == b"<html" or data[:4] == b"<!DO":
        raise RuntimeError(f"HTML instead of image for {file_id}")
    return data


def encode(img: Image.Image, width: int, cap: int) -> bytes:
    im = img.copy()
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    for q in (80, 75, 70, 65, 60, 55, 50, 45, 40):
        b = io.BytesIO()
        im.save(b, "WEBP", quality=q, method=6)
        if b.tell() <= cap:
            return b.getvalue()
    return b.getvalue()


def process(name: str, file_id: str, meta: dict):
    raw = download(file_id)
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (248, 248, 248))
        bg.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
        img = bg
    else:
        img = img.convert("RGB")
    big = encode(img, MAX_W, CAP)
    # keep the original for any hi-res use (video reference, branding)
    img.save(os.path.join(OUT, f"{name}-src.jpg"), "JPEG", quality=92)
    small = encode(img, 800, 60 * 1024)
    open(os.path.join(OUT, f"{name}.webp"), "wb").write(big)
    open(os.path.join(OUT, f"{name}-800.webp"), "wb").write(small)
    w = min(img.width, MAX_W)
    h = round(img.height * w / img.width)
    sw = min(img.width, 800)
    sh = round(img.height * sw / img.width)
    meta[name] = {"w": w, "h": h, "bytes": len(big), "w800": sw, "h800": sh, "bytes800": len(small)}
    print(f"{name}: {w}x{h} {len(big)//1024} KB / {sw}x{sh} {len(small)//1024} KB")


def main():
    meta = {}
    failures = []
    jobs = []
    for p in MANIFEST["pairs"]:
        jobs.append((f"{p['job']}-before", p["before"]))
        jobs.append((f"{p['job']}-after", p["after"]))
    for s in MANIFEST["singles"]:
        jobs.append((s["name"], s["id"]))
    existing = {}
    if os.path.exists(os.path.join(OUT, "manifest.json")):
        existing = json.load(open(os.path.join(OUT, "manifest.json")))
    meta.update(existing)
    for name, fid in jobs:
        if name in existing and os.path.exists(os.path.join(OUT, f"{name}.webp")):
            continue  # already fetched and (possibly) re-encoded locally; do not overwrite
        try:
            process(name, fid, meta)
        except Exception as e:
            print("FAILED", name, fid, e)
            failures.append(name)
    json.dump(meta, open(os.path.join(OUT, "manifest.json"), "w"), indent=1, sort_keys=True)
    print(f"done: {len(meta)} images, {len(failures)} failures: {failures}")
    if failures and not meta:
        sys.exit(1)


if __name__ == "__main__":
    main()
