"""Video clips and photos for the centre card.

Where they come from, in this order:
  1. Your own clips/photos: content/photos/<YYYY-MM-DD>/*.mp4|mov|jpg|png (used first, in name order).
  2. Free Pixabay VIDEO clips (PIXABAY_API_KEY secret), searched with the day's `broll:` words.
  3. Free stock photos to fill any gaps: Pixabay, or Pexels if you have a PEXELS_API_KEY.
  4. None — the card shows an animated icon instead.
Pixabay Content License: free, even commercially, no credit required.

Everything is cropped square to 1080x1080 for the card; clips are trimmed and muted.
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


VIDEO_EXT = (".mp4", ".mov", ".m4v", ".webm")


def _square_video(src, dst, max_len=12):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-t", str(max_len), "-an",
                    "-vf", "scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,setsar=1,fps=30",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(dst)], check=True)
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dst)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def _own(day):
    folder = REPO / "content" / "photos" / day
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") + VIDEO_EXT)


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


PIXABAY_VIDEOS = "https://pixabay.com/api/videos/"


def _pixabay_videos(day, queries, want):
    key = os.environ.get("PIXABAY_API_KEY")
    if not key or not queries:
        return []
    import requests

    CACHE.mkdir(parents=True, exist_ok=True)
    out, seen = [], set()
    per_query = max(1, -(-want // len(queries)))
    for q in queries:
        try:
            r = requests.get(PIXABAY_VIDEOS, timeout=30, params={
                "key": key, "q": q, "video_type": "film", "safesearch": "true", "per_page": 30, "order": "popular"})
            hits = r.json().get("hits", []) if r.ok else []
        except Exception as e:
            print(f"  pixabay video search failed for '{q}': {e}")
            continue
        hits = [h for h in hits if h.get("duration", 0) >= 5]
        start = int(hashlib.md5(f"v{day}{q}".encode()).hexdigest(), 16) % max(1, min(len(hits), 8))
        taken = 0
        for h in (hits[start:] + hits[:start]):
            if taken >= per_query or len(out) >= want:
                break
            if h["id"] in seen:
                continue
            seen.add(h["id"])
            files = h.get("videos", {})
            pick = next((files[k] for k in ("medium", "large", "small") if files.get(k, {}).get("url")
                         and min(files[k].get("width", 0), files[k].get("height", 0)) >= 720), None)
            if not pick:
                continue
            dst = CACHE / f"pixabay_v{h['id']}.mp4"
            if not dst.exists():
                try:
                    dst.write_bytes(requests.get(pick["url"], timeout=120).content)
                except Exception as e:
                    print(f"  video download failed: {e}")
                    continue
            out.append({"path": dst, "q": q, "credit": f"Video by {h.get('user', '?')} from Pixabay"})
            taken += 1
    return out


def get_media(entry, work, want):
    """Up to `want` card-ready items: {"src": project path, "kind": "video"|"photo", "dur": seconds}."""
    day = str(entry["date"])
    queries = entry.get("broll") or []
    raw = [{"path": p, "credit": "own"} for p in _own(day)][:want]
    if len(raw) < want:
        raw += _pixabay_videos(day, queries, want - len(raw))
    if len(raw) < want:
        raw += _pixabay(day, queries, want - len(raw))
    if len(raw) < want:
        raw += _pexels(day, queries, want - len(raw))
    out = []
    for n, item in enumerate(raw):
        src = Path(item["path"])
        try:
            if src.suffix.lower() in VIDEO_EXT:
                dst = work / "assets" / f"clip_{n}.mp4"
                d = _square_video(src, dst)
                if d >= 2:
                    out.append({"src": f"assets/clip_{n}.mp4", "kind": "video", "dur": d})
            else:
                dst = work / "assets" / f"photo_{n}.jpg"
                _square(src, dst)
                out.append({"src": f"assets/photo_{n}.jpg", "kind": "photo", "dur": 0})
        except subprocess.CalledProcessError as e:
            print(f"  could not use {src}: {e}")
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
