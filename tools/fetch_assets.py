#!/usr/bin/env python3
"""Download generated media listed in tools/assets.json into images/ and convert:
images → <name>.webp (≤1600px, ≤150 KB), <name>-800.webp, <name>-400.webp (+ <name>-src.png kept);
videos → <name>.mp4 (h264 1280x720, silent) and <name>.webm, plus <name>-poster.webp from the first frame."""
import io, json, os, subprocess, sys, urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images")
ASSETS = json.load(open(os.path.join(ROOT, "tools", "assets.json")))
MANIFEST = os.path.join(OUT, "manifest.json")


def enc(im, longest, cap):
    w, h = im.size
    if max(w, h) > longest:
        s = longest / max(w, h); im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    for q in range(82, 29, -5):
        b = io.BytesIO(); im.save(b, "WEBP", quality=q, method=6)
        if b.tell() <= cap:
            return b.getvalue(), im.size
    return b.getvalue(), im.size


def save_image_set(name, im, meta):
    big, size = enc(im, 1600, 150 * 1024)
    small, ssize = enc(im, 800, 70 * 1024)
    thumb, tsize = enc(im, 400, 22 * 1024)
    open(os.path.join(OUT, f"{name}.webp"), "wb").write(big)
    open(os.path.join(OUT, f"{name}-800.webp"), "wb").write(small)
    open(os.path.join(OUT, f"{name}-400.webp"), "wb").write(thumb)
    meta[name] = {"w": size[0], "h": size[1], "bytes": len(big), "w800": ssize[0], "h800": ssize[1], "bytes800": len(small), "w400": tsize[0], "h400": tsize[1]}
    print(f"{name}: {size[0]}x{size[1]} {len(big)//1024} KB")


def main():
    meta = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {}
    for a in ASSETS:
        name, url, kind = a["name"], a["url"], a["type"]
        os.makedirs(os.path.join(ROOT, ".assets-tmp"), exist_ok=True)
        raw = os.path.join(ROOT, ".assets-tmp", f"{name}-src.{ 'mp4' if kind == 'video' else 'png'}")
        if not os.path.exists(raw):
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            open(raw, "wb").write(urllib.request.urlopen(req, timeout=120).read())
        if kind == "image":
            im = Image.open(raw).convert("RGB")
            save_image_set(name, im, meta)
        else:
            mp4 = os.path.join(OUT, f"{name}.mp4"); webm = os.path.join(OUT, f"{name}.webm"); frame = os.path.join(OUT, f"{name}-frame.png")
            subprocess.run(["ffmpeg", "-y", "-i", raw, "-an", "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "slow", "-crf", "27", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4], check=True, capture_output=True)
            subprocess.run(["ffmpeg", "-y", "-i", raw, "-an", "-vf", "scale=1280:-2", "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "36", "-row-mt", "1", webm], check=True, capture_output=True)
            subprocess.run(["ffmpeg", "-y", "-i", raw, "-vf", "select=eq(n\\,12),scale=1600:-2", "-frames:v", "1", frame], check=True, capture_output=True)
            im = Image.open(frame).convert("RGB")
            save_image_set(f"{name}-poster", im, meta)
            os.remove(frame)
            print(f"{name}: mp4 {os.path.getsize(mp4)//1024} KB, webm {os.path.getsize(webm)//1024} KB")
    json.dump(meta, open(MANIFEST, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
