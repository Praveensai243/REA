"""Photos for the centre card.

Where photos come from, in this order:
  1. Your own photos: content/photos/<YYYY-MM-DD>/*.jpg|png (used first, in name order).
  2. Free stock photos searched with the day's `broll:` words:
       Pixabay (PIXABAY_API_KEY secret) — Pixabay Content License, free, no credit required
       Pexels  (PEXELS_API_KEY secret)  — used if there's no Pixabay key
  3. None — the card shows an animated icon instead.

Every photo is cropped square to 1080x1080 for the card.
"""
import hashlib
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / ".cache" / "photos"
PEXELS = "https://api.pexels.com/v1/search"


def _square(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf",
                    "scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080", "-q:v", "3", str(dst)],
                   check=True)


def _own(day):
    folder = REPO / "content" / "photos" / day
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))


def _pexels(day, queries, want):
    key = os.environ.get("PEXELS_API_KEY")
    if not key or not queries:
        return []
    import requests

    CACHE.mkdir(parents=True, exist_ok=True)
    out, seen = [], set()
    per_query = max(1, -(-want // len(queries)))
    for q in queries:
        try:
            r = requests.get(PEXELS, headers={"Authorization": key}, timeout=30,
                             params={"query": q, "orientation": "square", "per_page": 20})
            photos = r.json().get("photos", []) if r.ok else []
        except Exception as e:
            print(f"  pexels photo search failed for '{q}': {e}")
            continue
        start = int(hashlib.md5(f"{day}{q}".encode()).hexdigest(), 16) % max(1, min(len(photos), 8))
        for ph in (photos[start:] + photos[:start]):
            if len([o for o in out if o["q"] == q]) >= per_query or len(out) >= want:
                break
            if ph["id"] in seen:
                continue
            seen.add(ph["id"])
            dst = CACHE / f"pexels_{ph['id']}.jpg"
            if not dst.exists():
                try:
                    data = requests.get(ph["src"].get("large2x") or ph["src"]["large"], timeout=60).content
                    dst.write_bytes(data)
                except Exception as e:
                    print(f"  download failed: {e}")
                    continue
            out.append({"path": dst, "q": q, "credit": f"Photo by {ph.get('photographer', '?')} on Pexels"})
    return out


PIXABAY = "https://pixabay.com/api/"


def _pixabay(day, queries, want):
    key = os.environ.get("PIXABAY_API_KEY")
    if not key or not queries:
        return []
    import requests

    CACHE.mkdir(parents=True, exist_ok=True)
    out, seen = [], set()
    per_query = max(1, -(-want // len(queries)))
    for q in queries:
        try:
            r = requests.get(PIXABAY, timeout=30, params={
                "key": key, "q": q, "image_type": "photo", "safesearch": "true",
                "min_width": 1080, "min_height": 1080, "per_page": 30, "order": "popular"})
            hits = r.json().get("hits", []) if r.ok else []
        except Exception as e:
            print(f"  pixabay search failed for '{q}': {e}")
            continue
        start = int(hashlib.md5(f"{day}{q}".encode()).hexdigest(), 16) % max(1, min(len(hits), 8))
        taken = 0
        for h in (hits[start:] + hits[:start]):
            if taken >= per_query or len(out) >= want:
                break
            if h["id"] in seen:
                continue
            seen.add(h["id"])
            dst = CACHE / f"pixabay_{h['id']}.jpg"
            if not dst.exists():
                try:
                    dst.write_bytes(requests.get(h.get("largeImageURL") or h["webformatURL"], timeout=60).content)
                except Exception as e:
                    print(f"  download failed: {e}")
                    continue
            out.append({"path": dst, "q": q, "credit": f"Image by {h.get('user', '?')} from Pixabay"})
            taken += 1
    return out


def get_photos(entry, work, want):
    """Returns up to `want` card-ready photos as project-relative paths."""
    day = str(entry["date"])
    raw = [{"path": p, "credit": "own photo"} for p in _own(day)][:want]
    if len(raw) < want:
        raw += _pixabay(day, entry.get("broll") or [], want - len(raw))
    if len(raw) < want:
        raw += _pexels(day, entry.get("broll") or [], want - len(raw))
    out = []
    for n, item in enumerate(raw):
        dst = work / "assets" / f"photo_{n}.jpg"
        try:
            _square(item["path"], dst)
            out.append(f"assets/photo_{n}.jpg")
        except subprocess.CalledProcessError as e:
            print(f"  could not use {item['path']}: {e}")
    return out
