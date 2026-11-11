"""Make one @sipp_smart Short from content/calendar.yaml.

    python scripts/make_video.py --date 2026-11-11            # with Telugu voice (needs internet)
    python scripts/make_video.py --date 2026-11-11 --no-voice # music + effects only

Writes out/<date>.mp4 and out/<date>.json (Instagram caption, YouTube title/description).
"""
import argparse
import asyncio
import datetime as dt
import html
import json
import re
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from audio import Soundtrack  # noqa: E402
from icons import plan_icons, render_icon  # noqa: E402
from photos import get_photos  # noqa: E402
import style  # noqa: E402
import mascot  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
VOICE = os.environ.get("SIPP_VOICE", "te-IN-MohanNeural")   # or te-IN-ShrutiNeural
VOICE_RATE = os.environ.get("SIPP_VOICE_RATE", "+10%")
HF = ["npx", "--yes", "hyperframes@0.9.31"]
LOGO_HEIGHT = int(os.environ.get("SIPP_LOGO_HEIGHT", "64"))

FOOTER_TAGS = "#sippsmart #telugu #telugureels #alcoholfacts #drinkresponsibly #hyderabad #vizag #telugupeople"
FOOTER = ("ℹ️ Legal drinking age పైబడినవారికి మాత్రమే. మితంగా, బాధ్యతగా తాగండి. తాగితే drive చేయొద్దు.\n"
          "Follow @sipp_smart for more 🥂")

STAMP = {"MYTH": "#FF4D4D", "FACT": "#3DDC84", "TIP": "#F5A623"}
BGS = {
    "edu": ["radial-gradient(circle at 50% 40%, #3A1730 0%, #140A16 70%)", "#140A16",
            "linear-gradient(180deg,#0E1A2B 0%,#140A16 100%)", "#140A16",
            "linear-gradient(180deg,#0F2418 0%,#140A16 100%)", "#140A16"],
    "cocktail": ["radial-gradient(circle at 50% 40%, #1C4A4E 0%, #0A1A1C 72%)", "#0A1A1C",
                 "linear-gradient(180deg,#2A2110 0%,#0A1A1C 100%)", "#0A1A1C",
                 "linear-gradient(180deg,#3A1730 0%,#0A1A1C 100%)", "#0A1A1C"],
}

OVERLAY = {
    "edu": "linear-gradient(180deg, rgba(20,10,22,0.66) 0%, rgba(20,10,22,0.5) 45%, rgba(20,10,22,0.85) 100%)",
    "cocktail": "linear-gradient(180deg, rgba(8,24,26,0.64) 0%, rgba(8,24,26,0.48) 45%, rgba(8,24,26,0.84) 100%)",
}

FONTS = """
@font-face{font-family:'Anek';font-weight:500;src:url('assets/fonts/anek-telugu-telugu-500-normal.woff2') format('woff2');unicode-range:U+0951-0952,U+0964-0965,U+0C00-0C7F,U+1CDA,U+1CF2,U+200C-200D,U+25CC;}
@font-face{font-family:'Anek';font-weight:800;src:url('assets/fonts/anek-telugu-telugu-800-normal.woff2') format('woff2');unicode-range:U+0951-0952,U+0964-0965,U+0C00-0C7F,U+1CDA,U+1CF2,U+200C-200D,U+25CC;}
@font-face{font-family:'Anek';font-weight:500;src:url('assets/fonts/anek-telugu-latin-500-normal.woff2') format('woff2');unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2212;}
@font-face{font-family:'Anek';font-weight:800;src:url('assets/fonts/anek-telugu-latin-800-normal.woff2') format('woff2');unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2212;}
"""

CSS = """
#root{position:absolute;inset:0;font-family:'Anek',sans-serif;color:#FFF7EC;}
#root .bg{position:absolute;inset:0;}
#root .stack{position:absolute;left:90px;right:90px;top:250px;bottom:610px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px;text-align:center;}
#root .iconwrap{display:flex;justify-content:center;margin-bottom:-10px;}
#root .kicker,#root .main,#root .list,#root .sub{text-shadow:0 4px 22px rgba(0,0,0,0.55);}
#root .kicker{font-size:48px;font-weight:500;letter-spacing:0.03em;color:#F5A623;}
#root .main{font-weight:800;line-height:1.16;}
#root .list{font-weight:800;line-height:1.38;text-align:left;}
#root .sub{font-size:46px;font-weight:500;line-height:1.3;color:#E9DCCB;}
#root .stamp{display:inline-block;border:9px solid currentColor;border-radius:22px;padding:4px 40px;font-size:118px;font-weight:800;}
#root .pill{display:inline-block;padding:18px 44px;border-radius:999px;font-size:60px;font-weight:800;background:#F5A623;color:#2A1606;}
"""


def visual_len(s):
    """Width in 'Latin letter' units. A Telugu letter (with its vowel signs) is about
    about 1.6x as wide as a Latin letter in this font; vowel signs/virama add no width."""
    w = 0.0
    for c in s:
        o = ord(c)
        if 0x0C3E <= o <= 0x0C56 or o in (0x0C01, 0x0C03, 0x0C4D):
            continue
        w += 1.85 if 0x0C00 <= o <= 0x0C7F else 1.0
    return w


def main_size(text, is_list, height=760):
    longest = max(visual_len(line) for line in text.split("\n"))
    lines = text.count("\n") + 1
    if is_list:
        size = min(76, int(900 / (longest * 0.56)), int((height + 60) / (lines * 1.38)))
        return max(40, size)
    size = min(124, int(900 / (longest * 0.56)), int(height / (lines * 1.16)))
    return max(52, size)


def best_wrap(text, max_lines=3, height=760):
    """Re-wrap a headline into 1–3 lines so it can be shown as BIG as possible."""
    import itertools
    raw = text.replace("\n", " ").split()
    glue = {"కి", "కు", "లో", "తో", "ని", "నా", "నా?", "ఆ?", "గా", "లోనే", "ను", "నుంచి", "?", "!"}
    def latin(w):
        return bool(re.fullmatch(r"[A-Za-z&'\"]+", w))

    words = []
    for w in raw:
        bare = w.strip(",.!?:")
        if words and (w in glue or bare in glue):          # Telugu postpositions stick to the word before
            words[-1] += " " + w
        elif words and latin(words[-1].split()[-1]) and re.match(r"[A-Za-z]", w):
            words[-1] += " " + w                           # keep English phrases together ("Red wine")
        else:
            words.append(w)
    if len(words) <= 1 or main_size(text, False, height) >= 100:
        return text   # the written line breaks already give big text
    cands = []
    for n in range(1, min(max_lines, len(words)) + 1):
        for cuts in itertools.combinations(range(1, len(words)), n - 1):
            idx = (0,) + cuts + (len(words),)
            cand = "\n".join(" ".join(words[x:y]) for x, y in zip(idx, idx[1:]))
            lonely = sum(1 for ln in cand.split("\n") if " " not in ln and visual_len(ln) < 7)
            cands.append((main_size(cand, False, height), n, cand, lonely))
    top = max(c[0] for c in cands)
    best = min((c for c in cands if c[0] >= top - 10), key=lambda c: (c[3], c[1], -c[0]))
    return best[2]


def esc(s):
    return html.escape(s).replace("\n", "<br>")


def scene_html(sid, sc, dur, bg, first=False, icon=None, video=None):
    show_icon = bool(icon)
    parts, tweens, t = [], [], 0.0
    if show_icon:
        icon_svg, icon_tweens = render_icon(icon, f"{sid}-ic", dur)
        parts.append(f'<div id="{sid}-icw" class="clip iconwrap" data-start="0" data-duration="{dur:g}">{icon_svg}</div>')
        tweens.extend(icon_tweens)
    if sc.get("k"):
        parts.append(f'<div id="{sid}-k" class="clip kicker" data-start="0" data-duration="{dur:g}">{esc(sc["k"])}</div>')
        tweens.append((f"#{sid}-k", "{opacity:%s,y:%s}" % ((1, 0) if first else (0, 30)), "{opacity:1,y:0,duration:0.35,ease:'power3.out'}", 0))
        t = 0.2
    if sc.get("stamp"):
        col = STAMP.get(sc["stamp"], "#FFF7EC")
        parts.append(f'<div id="{sid}-st" class="clip" data-start="0" data-duration="{dur:g}">'
                     f'<span id="{sid}-stw" class="stamp" style="color:{col}">{esc(sc["stamp"])}</span></div>')
        tweens.append((f"#{sid}-stw", "{scale:2.2,opacity:0,rotation:-14}",
                       "{scale:1,opacity:1,rotation:-6,duration:0.35,ease:'power4.out'}", 0.05))
        t = 0.75
    is_list = bool(sc.get("list"))
    text = sc["m"] if is_list else best_wrap(sc["m"], height=520 if show_icon else 760)
    size = main_size(text, is_list, 520 if show_icon else 760)
    cls = "list" if is_list else "main"
    parts.append(f'<div id="{sid}-m" class="clip {cls}" data-start="0" data-duration="{dur:g}" '
                 f'style="font-size:{size}px">{esc(text)}</div>')
    if first:
        tweens.append((f"#{sid}-m", "{opacity:1,scale:1.08}", "{opacity:1,scale:1,duration:0.5,ease:'power3.out'}", 0))
    else:
        tweens.append((f"#{sid}-m", "{opacity:0,y:40,scale:0.96}", "{opacity:1,y:0,scale:1,duration:0.45,ease:'power3.out'}", t))
    end_in = (0.5 if first else t + 0.45)
    if dur - end_in > 0.6:
        tweens.append((f"#{sid}-m", None, f"{{scale:1.045,duration:{dur - end_in - 0.05:.2f},ease:'none'}}", round(end_in, 2)))
    if sc.get("pill"):
        parts.append(f'<div id="{sid}-p" class="clip pill" data-start="0" data-duration="{dur:g}">{esc(sc["pill"])}</div>')
        tweens.append((f"#{sid}-p", "{opacity:0,scale:0.8}", "{opacity:1,scale:1,duration:0.4,ease:'back.out(1.8)'}", t + 0.5))
    if sc.get("s"):
        parts.append(f'<div id="{sid}-s" class="clip sub" data-start="0" data-duration="{dur:g}">{esc(sc["s"])}</div>')
        tweens.append((f"#{sid}-s", "{opacity:0}", "{opacity:1,duration:0.4}", t + 0.8))
    if not first:  # punch-in on every scene change
        tweens.append((f"#{sid}-stack", "{scale:1.07}", "{scale:1,duration:0.35,ease:'power2.out'}", 0))
    if sc.get("stamp"):  # shake + flash on the reveal, in sync with the impact sound
        tweens.append((f"#{sid}-flash", "{opacity:0.32}", "{opacity:0,duration:0.28,ease:'power2.out',immediateRender:false}", 0.38))
        tweens.append((f"#{sid}-stack", None, "{keyframes:[{x:-16,duration:0.05},{x:13,duration:0.05},{x:-9,duration:0.05},{x:6,duration:0.05},{x:0,duration:0.06}]}", 0.38))
    video_html = ""
    if video:
        rate = f' data-playback-rate="{video["rate"]}"' if video["rate"] != 1 else ""
        video_html = (f'<video id="{sid}-v" class="clip" src="{video["src"]}" muted playsinline data-start="0" '
                      f'data-duration="{dur:g}" data-media-start="{video["start"]:g}"{rate} '
                      f'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(0.85) brightness(0.9)"></video>\n    ')
    tl = "\n".join(f"    tl.fromTo('{a}', {b}, {c}, {d});" if b else f"    tl.to('{a}', {c}, {d});" for a, b, c, d in tweens)
    body = "\n    ".join(parts)
    return f"""<template>
  <style>{FONTS}{CSS}</style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
    {video_html}<div id="{sid}-bg" class="bg" style="background:{bg}"></div>
    <div id="{sid}-stack" class="stack">
    {body}
    </div>
    <div id="{sid}-flash" style="position:absolute;inset:0;background:#FFF7EC;opacity:0;pointer-events:none"></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{tl}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


def cta_scene(entry):
    """Last screen: the day's comment question + Follow button."""
    ask = entry.get("ask") or {}
    share = any(w in ask.get("m", "") for w in ("tag", "పంపండి", "share"))
    sub = ("Save చేసి try చేయండి" if entry["kind"] == "cocktail"
           else "మితంగా తాగండి, తెలివిగా Sip చేయండి")
    return {"k": "Share చేయండి" if share else "Comment చేయండి",
            "m": ask.get("m", "మితంగా తాగండి,\nతెలివిగా Sip చేయండి"),
            "pill": "Follow @sipp_smart", "s": sub,
            "v": (ask.get("v", "") + " సిప్ స్మార్ట్‌ని ఫాలో అవ్వండి.").strip()}


def watermark_html(work, total):
    """Logo in the top-right corner on every frame. Uses template/assets/logo.png
    (or logo.svg / logo.jpg) if present, otherwise a text badge."""
    style = ("position:absolute;top:1414px;left:0;right:0;z-index:60;opacity:0.9;"
             "display:flex;align-items:center;justify-content:center")
    for name in ("logo.png", "logo.svg", "logo.webp", "logo.jpg"):
        if (work / "assets" / name).exists():
            return (f'      <div id="watermark" class="clip" data-start="0" data-duration="{total:g}" data-track-index="17" '
                    f'data-layout-ignore style="{style}"><img src="assets/{name}" alt="Sipp Smart" '
                    f'style="height:{LOGO_HEIGHT}px;width:auto;display:block"></div>')
    return (f'      <div id="watermark" class="clip" data-start="0" data-duration="{total:g}" data-track-index="17" '
            f'data-layout-ignore style="{style};font-family:Anek,sans-serif;font-weight:800;font-size:34px;'
            f'letter-spacing:0.04em;color:rgba(255,247,236,0.75);">@sipp_smart</div>')


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


async def tts_all(texts, folder):
    import edge_tts
    paths = []
    for i, text in enumerate(texts):
        p = folder / f"voice_{i}.mp3"
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text, VOICE, rate=VOICE_RATE).save(str(p))
                if p.stat().st_size > 1000:
                    break
            except Exception as e:  # network hiccup: retry
                print(f"  tts retry {attempt + 1}: {e}")
                await asyncio.sleep(3 * (attempt + 1))
        else:
            raise RuntimeError(f"Telugu voice failed for scene {i}")
        paths.append(p)
    return paths


def metadata(entry):
    base = entry.get("yt_title") or entry["caption"]
    yt_title = base if len(base) <= 90 else entry["scenes"][0]["m"].replace("\n", " ")
    yt_title = f"{yt_title[:90]} #shorts"
    ask = entry.get("ask", {}).get("m", "").replace("\n", " ")
    ask_line = f"\n\n👇 {ask}" if ask else ""
    caption = f"{entry['caption']}{ask_line}\n\n{FOOTER}\n\n{FOOTER_TAGS}"
    yt_desc = f"{entry['caption']}{ask_line}\n\n{FOOTER}\n\n#shorts {FOOTER_TAGS}"
    return {"date": str(entry["date"]), "kind": entry["kind"], "instagram_caption": caption,
            "youtube_title": yt_title, "youtube_description": yt_desc}


def build(entry, voice=True, render=True, check=False, broll=True):
    day = str(entry["date"])
    work = REPO / "build" / day
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(REPO / "template", work)
    (work / "compositions").mkdir()
    out = REPO / "out"
    out.mkdir(exist_ok=True)

    scenes = list(entry["scenes"]) + [cta_scene(entry)]
    voices = []
    if voice:
        texts = [s["v"] for s in scenes]
        import voice_clone
        if voice_clone.available():
            try:
                voices = voice_clone.synth_all(texts, work)
                print("  voice: your cloned voice (IndicF5)")
            except Exception as e:  # never miss a post because of the clone
                print(f"  ⚠️ cloned voice failed ({e}); using the Microsoft Telugu voice instead")
        if not voices:
            voices = asyncio.run(tts_all(texts, work))
            print(f"  voice: {VOICE}")

    durs = []
    for i, sc in enumerate(scenes):
        if voices:
            d = probe_duration(voices[i]) + 0.7 + (0.45 if sc.get("stamp") else 0)
        else:
            d = 1.2 + 0.075 * len(sc["v"])
        floor = 3.8 if i == len(scenes) - 1 else 2.4
        durs.append(round(max(floor, d), 2))
    durs[-1] = round(durs[-1] + 1.6, 2)  # hold the ending so the last line can be read
    total = round(sum(durs), 2)

    # soundtrack
    st = Soundtrack(total, seed=int(day.replace("-", "")), style=entry["kind"])
    st.compose()
    t = 0.0
    for i, (sc, d) in enumerate(zip(scenes, durs)):
        if i:
            st.whoosh(t)
        if sc.get("stamp"):
            st.reveal(t + 0.38, sc["stamp"])  # when the stamp lands
        if sc.get("pill"):
            st.pop(t + 0.5)
        if voices:
            st.add_voice(voices[i], t + (0.75 if sc.get("stamp") else 0.3))
        t += d
    st.write(work / "assets" / "soundtrack.wav")

    # scenes + root (style modelled on the reference reel)
    kind = entry["kind"]
    icon_plan = plan_icons(scenes[:-1], kind) + [None]
    day_icon = icon_plan[0]
    card_icons = [ic or day_icon for ic in icon_plan]
    # your own photos (content/photos/host/) open and close every video, rotating day by day
    host_dir = REPO / "content" / "photos" / "host"
    host_pool = sorted(host_dir.glob("*.jpg")) if host_dir.is_dir() else []
    host_hook = host_end = None
    if host_pool:
        n = int(day.replace("-", "")) % len(host_pool)
        for tag, src in (("hook", host_pool[n]), ("end", host_pool[(n + 1) % len(host_pool)])):
            shutil.copy(src, work / "assets" / f"host_{tag}.jpg")
        host_hook, host_end = "assets/host_hook.jpg", "assets/host_end.jpg"
    n_cards = sum(1 for sc in scenes[1:-1] if not sc.get("list") and not sc.get("anim")) or 1
    photo_list = get_photos(entry, work, n_cards) if broll else []
    print(f"  photos: {len(photo_list)} topic + {2 if host_pool else 0} of you" + ("" if photo_list else " (other cards show animated icons)"))
    hosts, t, pi = [], 0.0, 0
    mascot_events = []
    for i, (sc, d) in enumerate(zip(scenes, durs)):
        sid = f"s{i + 1}"
        v_start = 0.75 if sc.get("stamp") else 0.3
        v_len = probe_duration(voices[i]) if voices else max(0.8, 0.45 + 0.075 * len(sc["v"]))  # estimate
        cap_html, cap_tw = style.caption(sid, sc["v"], v_start, v_len, style.ACCENT[kind], first=(i == 0))
        pose = mascot.pose_for(sc, i, i == len(scenes) - 1)
        if pose:
            mascot_events.append((t + (0.4 if sc.get("stamp") else 0.35), pose))
        if i == len(scenes) - 1:
            card_html, card_tw = style.cta_card(sid, sc, d, kind, photo=host_end)
        else:
            photo = None
            if i == 0 and host_hook:
                photo = host_hook
            elif photo_list and not sc.get("list") and not sc.get("anim"):
                photo = photo_list[pi % len(photo_list)]
                pi += 1
            card_html, card_tw = style.card(sid, sc, d, kind, photo=photo, icon=card_icons[i] if not photo else icon_plan[i],
                                            v_start=v_start, v_len=v_len, first=(i == 0))
        doc = style.scene_doc(sid, d, cap_html + card_html, card_tw + cap_tw)
        (work / "compositions" / f"{sid}.html").write_text(doc, encoding="utf-8")
        hosts.append(f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                     f'data-start="{t:g}" data-duration="{d:g}" data-track-index="{i + 2}" data-track-kind="graphics" '
                     f'data-width="{W}" data-height="{H}"></div>')
        t += d
    (work / "compositions" / "bg.html").write_text(style.background_doc(kind, total), encoding="utf-8")
    (work / "compositions" / "mascot.html").write_text(mascot.mascot_doc(mascot_events, total, style.scene_doc), encoding="utf-8")
    hosts.append(f'      <div id="mascot" data-composition-id="mascot" data-composition-src="compositions/mascot.html" '
                 f'data-start="0" data-duration="{total:g}" data-track-index="20" data-width="{W}" data-height="{H}"></div>')
    bg_html = (f'<div id="bg" data-composition-id="bg" data-composition-src="compositions/bg.html" data-start="0" '
               f'data-duration="{total:g}" data-track-index="1" data-width="{W}" data-height="{H}"></div>')
    (work / "index.html").write_text(f"""<!doctype html>
<html lang="te">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #07040B; }}
      #root {{ width: 100%; height: 100%; position: relative; }}
      {style.FONTS}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:g}" data-width="{W}" data-height="{H}">
      {bg_html}
{chr(10).join(hosts)}
{watermark_html(work, total)}
      <audio id="soundtrack" class="clip" src="assets/soundtrack.wav" data-start="0" data-duration="{total:g}" data-track-index="30" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""", encoding="utf-8")
    (work / "meta.json").write_text(json.dumps({"id": f"sipp-{day}", "name": f"sipp-{day}"}))

    meta = metadata(entry)
    meta["duration_seconds"] = total
    meta["voice"] = VOICE if voices else None
    (out / f"{day}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    if check:
        subprocess.run(HF + ["check"], cwd=work, check=False)
    if render:
        subprocess.run(HF + ["render", "--output", str(out / f"{day}.mp4")], cwd=work, check=True)
        print(f"✅ {out / f'{day}.mp4'}  ({total}s)")
    return work


def load_calendar():
    return yaml.safe_load((REPO / "content" / "calendar.yaml").read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD (default: today in India)")
    ap.add_argument("--all", action="store_true", help="make every video in the calendar")
    ap.add_argument("--from-date", help="with --all: start from this date")
    ap.add_argument("--to-date", help="with --all: stop after this date")
    ap.add_argument("--no-voice", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--no-broll", action="store_true", help="skip photos (cards show icons)")
    a = ap.parse_args()

    cal = load_calendar()
    if a.all:
        todo = [e for e in cal if (not a.from_date or str(e["date"]) >= a.from_date)
                and (not a.to_date or str(e["date"]) <= a.to_date)]
    else:
        day = a.date or (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date().isoformat()
        todo = [e for e in cal if str(e["date"]) == day]
        if not todo:
            print(f"No video planned for {day}.")
            sys.exit(0)
    for e in todo:
        print(f"▶ {e['date']} ({e['kind']})")
        build(e, voice=not a.no_voice, render=not a.no_render, check=a.check, broll=not a.no_broll)


if __name__ == "__main__":
    main()
