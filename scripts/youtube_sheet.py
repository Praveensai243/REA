"""Writes out/youtube_schedule.csv: one row per video with the file name, the date and
time to schedule it in YouTube Studio, the title and the description."""
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "out"
POST_TIME = "7:00 PM IST"

rows = []
for meta_file in sorted(OUT.glob("20*.json")):
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    video = OUT / f"{meta['date']}.mp4"
    if video.exists():
        rows.append({"schedule_date": meta["date"], "schedule_time": POST_TIME, "file": video.name,
                     "title": meta["youtube_title"], "description": meta["youtube_description"]})

with open(OUT / "youtube_schedule.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["schedule_date", "schedule_time", "file", "title", "description"])
    w.writeheader()
    w.writerows(rows)
print(f"youtube_schedule.csv: {len(rows)} videos")
