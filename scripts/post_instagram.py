"""Post out/<date>.mp4 to Instagram as a Reel through Instagram's official API.

Needs two secrets (set in GitHub → Settings → Secrets → Actions):
  IG_USER_ID       your Instagram professional account ID
  IG_ACCESS_TOKEN  a long-lived Instagram User access token (lasts 60 days)

    python scripts/post_instagram.py --date 2026-11-11 [--dry-run]

Instagram fetches the video from a public link (--video-url, comma-separated
backups allowed), because Instagram Login does not accept direct file uploads.
Skips the post if posted/<date>.json already exists, so a re-run never double-posts.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
API_VERSION = os.environ.get("IG_API_VERSION", "v26.0")
GRAPH = f"https://graph.instagram.com/{API_VERSION}"


def fail(msg, resp=None):
    detail = ""
    if resp is not None:
        try:
            detail = json.dumps(resp.json())
        except ValueError:
            detail = resp.text[:500]
    print(f"❌ {msg} {detail}")
    sys.exit(1)


def post(day, video_urls, dry_run=False):
    video = REPO / "out" / f"{day}.mp4"
    meta = json.loads((REPO / "out" / f"{day}.json").read_text(encoding="utf-8"))
    log = REPO / "posted" / f"{day}.json"
    if log.exists():
        print(f"Already posted for {day}: {log.read_text()}")
        return
    if not video.exists():
        fail(f"Video not found: {video}")
    caption = meta["instagram_caption"]
    if dry_run:
        print(f"[dry run] would post {video.name} ({video.stat().st_size // 1024} KB)\n---\n{caption}\n---")
        return

    user_id = os.environ.get("IG_USER_ID")
    token = os.environ.get("IG_ACCESS_TOKEN")
    if not user_id or not token:
        fail("IG_USER_ID / IG_ACCESS_TOKEN secrets are missing.")
    if not any(video_urls):
        fail("No public video link given (--video-url).")

    container = None
    for url in [u for u in video_urls if u]:
        print(f"trying video link: {url}")
        r = requests.post(f"{GRAPH}/{user_id}/media", data={
            "media_type": "REELS", "video_url": url, "caption": caption,
            "share_to_feed": "true", "access_token": token}, timeout=60)
        if r.status_code != 200:
            fail("Could not create the Reel container.", r)
        cid = r.json()["id"]
        status = None
        for _ in range(30):  # up to ~10 minutes
            time.sleep(20)
            r = requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code,status", "access_token": token}, timeout=60)
            status = r.json().get("status_code")
            print(f"  status: {status}")
            if status in ("FINISHED", "ERROR", "EXPIRED"):
                break
        if status == "FINISHED":
            container = cid
            break
        print(f"  Instagram could not use this link ({r.text[:300]}); trying the next one")
    if not container:
        fail("Instagram could not process the video from any link.")

    # 4) publish
    r = requests.post(f"{GRAPH}/{user_id}/media_publish",
                      data={"creation_id": container, "access_token": token}, timeout=60)
    if r.status_code != 200:
        fail("Publish failed.", r)
    media_id = r.json()["id"]
    link = None
    try:
        link = requests.get(f"{GRAPH}/{media_id}", params={"fields": "permalink", "access_token": token},
                            timeout=60).json().get("permalink")
    except Exception:
        pass
    log.parent.mkdir(exist_ok=True)
    log.write_text(json.dumps({"date": day, "media_id": media_id, "permalink": link,
                               "posted_at_utc": dt.datetime.utcnow().isoformat(timespec="seconds")}, indent=2))
    print(f"✅ Posted to Instagram: {link or media_id}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD (default: today in India)")
    ap.add_argument("--video-url", default="", help="public link(s) to the mp4, comma-separated")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    day = a.date or (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date().isoformat()
    post(day, a.video_url.split(","), a.dry_run)
