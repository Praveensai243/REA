"""Real-footage style: every line plays a full-screen stock clip (Pixabay), cut on
each sentence, with a slow push-in, a warm grade, dark edges for readable text,
and bold captions. Motion graphics sit on top: a title, MYTH ✗ / FACT ✓ / TIP !
stamps, a glass recipe list that ticks off, and a comment prompt at the end.

Same builder API as style.py / paper.py: every builder returns (html, tweens).
"""
import style
from icons import render_icon
from style import FONTS, esc, _vlen, three_glasses  # noqa: F401

W, H = 1080, 1920
GOLD = "#FFC94A"
ACCENT = {"edu": GOLD, "cocktail": GOLD}
STAMP = {"MYTH": ("#E5372B", "✗ MYTH"), "FACT": ("#2FA84F", "✓ FACT"), "TIP": ("#F0A21B", "! TIP")}
MEDIA_SIZE = (1080, 1920)     # make_video asks photos.get_media for portrait footage

CSS = """
#root .rfoot{position:absolute;inset:0;overflow:hidden;background:#111;}
#root .rfoot video,#root .rfoot img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
  filter:contrast(1.08) saturate(1.12) sepia(0.12) brightness(0.92);}
#root .rshade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0.62) 0%,rgba(0,0,0,0.0) 30%,
  rgba(0,0,0,0.0) 48%,rgba(0,0,0,0.72) 78%,rgba(0,0,0,0.80) 100%);}
#root .rtitle{position:absolute;left:70px;right:70px;top:250px;color:#FFF;font-weight:800;line-height:1.12;
  text-shadow:0 4px 22px rgba(0,0,0,0.6);}
#root .rtitle .rhl{color:%(gold)s;}
#root .rkick{display:inline-block;margin-bottom:18px;padding:8px 22px;border-radius:40px;background:rgba(255,255,255,0.16);
  border:2px solid rgba(255,255,255,0.35);font-size:34px;font-weight:800;color:#FFF;letter-spacing:0.02em;}
#root .rstamp{position:absolute;left:50%%;top:640px;transform:translateX(-50%%) rotate(-7deg);padding:14px 40px;border:8px solid;
  border-radius:18px;font-weight:800;font-size:92px;letter-spacing:0.05em;color:#FFF;white-space:nowrap;box-shadow:0 10px 40px rgba(0,0,0,0.5);}
#root .rglass{position:absolute;left:70px;right:70px;top:560px;padding:34px 40px;border-radius:34px;background:rgba(14,12,10,0.55);
  border:2px solid rgba(255,255,255,0.22);backdrop-filter:blur(10px);display:flex;flex-direction:column;gap:20px;}
#root .rrow{display:flex;align-items:center;gap:24px;color:#FFF;font-weight:800;line-height:1.15;}
#root .rcb{flex:none;width:54px;height:54px;border-radius:50%%;border:4px solid rgba(255,255,255,0.8);display:flex;align-items:center;
  justify-content:center;font-size:34px;color:#111;}
#root .rpill{position:absolute;left:50%%;top:820px;transform:translateX(-50%%);display:flex;align-items:center;gap:20px;padding:24px 46px;
  border-radius:60px;background:#FFF;color:#111;font-weight:800;font-size:50px;white-space:nowrap;box-shadow:0 12px 40px rgba(0,0,0,0.4);}
#root .cap{top:1150px !important;z-index:5;}
#root .phrase{font-size:74px !important;color:#FFF;text-shadow:0 3px 0 rgba(0,0,0,0.55),0 6px 26px rgba(0,0,0,0.65) !important;}
#root .acc-te,#root .acc-la{color:%(gold)s !important;}
#root .rflash{position:absolute;inset:0;background:#FFF;opacity:0;pointer-events:none;}
""".replace("%(gold)s", GOLD).replace("%%", "%")


def scene_doc(sid, dur, body, tweens):
    doc = style.scene_doc(sid, dur, body, tweens)
    return doc.replace("</style>", CSS + "</style>", 1)


def caption(sid, text, v_start, v_len, accent_color=GOLD, first=False):
    return style.caption(sid, text, v_start, v_len, accent_color, first=first)


def _title_html(sid, text, kicker=None):
    lines = [ln for ln in text.split("\n") if ln.strip()]
    words = [w for ln in lines for w in ln.split()]
    key = max(words, key=_vlen) if words else ""
    units = max((_vlen(x) for x in lines), default=10)
    size = int(max(54, min(88, 900 / (units * 0.52 + 1), 270 / (max(1, len(lines)) * 1.12))))
    done, out = False, []
    for ln in lines:
        ws = []
        for w in ln.split():
            if w == key and not done:
                ws.append(f'<span class="rhl">{esc(w)}</span>'); done = True
            else:
                ws.append(esc(w))
        out.append(" ".join(ws))
    kick = f'<div id="{sid}-k" class="rkick">{esc(kicker)}</div><br>' if kicker else ""
    return f'<div id="{sid}-t" class="rtitle" style="font-size:{size}px">{kick}{"<br>".join(out)}</div>'


def _footage(sid, photo, dur, icon, first):
    """Full-screen clip/photo with a slow push-in; dark gradient + icon if no footage."""
    tw = []
    if isinstance(photo, dict) and photo.get("kind") == "video":
        rate = f' data-playback-rate="{max(0.5, photo["dur"] / dur - 0.01):.3f}"' if photo["dur"] < dur else ""
        inner = (f'<video id="{sid}-v" class="clip" src="{photo["src"]}" muted playsinline data-start="0" '
                 f'data-duration="{dur:g}" data-media-start="0"{rate}></video>')
    elif photo:
        src = photo["src"] if isinstance(photo, dict) else photo
        inner = f'<img id="{sid}-v" src="{src}" alt="">'
    else:
        ic_html, ic_tw = render_icon(icon or "question", f"{sid}-ic", dur)
        ic_html = ic_html.replace('width="230" height="230"', 'width="380" height="380"')
        inner = (f'<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 42%,#3A2A1A,#0E0B09 70%)"></div>'
                 f'<div style="position:absolute;left:0;right:0;top:560px;display:flex;justify-content:center">{ic_html}</div>')
        tw += ic_tw
    html = f'<div id="{sid}-f" class="rfoot">{inner}</div><div class="rshade"></div>'
    if photo:
        tw.append((f"#{sid}-v", "{scale:1.14}", f"{{scale:1.0,duration:{dur:.2f},ease:'power1.out'}}", 0))
    if not first:   # quick punch-in + white flash on each cut
        tw.append((f"#{sid}-f", "{scale:1.08}", "{scale:1,duration:0.35,ease:'power3.out'}", 0))
        tw.append((f"#{sid}-fl", "{opacity:0.55}", "{opacity:0,duration:0.25,ease:'power2.out'}", 0))
    return html + f'<div id="{sid}-fl" class="rflash"></div>', tw


def card(sid, sc, dur, kind, photo=None, icon=None, v_start=0.3, v_len=2.0, first=False):
    f_html, tw = _footage(sid, photo, dur, icon, first)
    html = f_html
    if sc.get("list"):
        html += _title_html(sid, sc.get("k") or "", None)
        rows = sc["m"].split("\n")
        longest = max(_vlen(r) for r in rows)
        size = max(38, int(min(56, 700 / (longest * 0.56))))
        times = [round(v_start + v_len * i / max(len(rows), 1), 2) for i in range(len(rows))]
        rh = []
        for i, r in enumerate(rows):
            rh.append(f'<div id="{sid}-r{i}" class="rrow" style="font-size:{size}px"><span id="{sid}-c{i}" class="rcb">'
                      f'<span id="{sid}-x{i}" style="opacity:0">✓</span></span><span>{esc(r)}</span></div>')
            tw += [(f"#{sid}-r{i}", "{opacity:0,x:-40}", "{opacity:1,x:0,duration:0.3,ease:'power2.out'}", max(0.2, times[i] - 0.2)),
                   (f"#{sid}-c{i}", None, f"{{backgroundColor:'{GOLD}',borderColor:'{GOLD}',duration:0.15}}", times[i] + 0.15),
                   (f"#{sid}-x{i}", "{opacity:0,scale:0.3}", "{opacity:1,scale:1,duration:0.2,ease:'back.out(3)'}", times[i] + 0.15)]
        html += f'<div id="{sid}-g" class="rglass">{"".join(rh)}</div>'
        tw.append((f"#{sid}-g", "{opacity:0,y:40}", "{opacity:1,y:0,duration:0.4,ease:'power3.out'}", 0.1))
    else:
        html += _title_html(sid, sc["m"], sc.get("k"))
        if sc.get("anim") == "three_glasses":
            g_html, g_tw = three_glasses(sid, v_start, v_len)
            html += (f'<div style="position:absolute;left:0;top:430px;width:1080px;height:700px;color:#FFF7EC;'
                     f'transform:scale(0.95);transform-origin:50% 0">{g_html}</div>')
            tw += g_tw
        if sc.get("stamp") in STAMP:
            col, label = STAMP[sc["stamp"]]
            at = round(v_start + min(v_len * 0.55, 1.5), 2)
            html += f'<div id="{sid}-st" class="rstamp" style="background:{col};border-color:#FFF">{label}</div>'
            tw.append((f"#{sid}-st", "{opacity:0,scale:2.4}", "{opacity:1,scale:1,duration:0.28,ease:'back.out(2.2)'}", at))
            tw.append((f"#{sid}-f", None, "{x:-12,duration:0.05,yoyo:true,repeat:3}", round(at + 0.25, 2)))
    if first:
        tw.append((f"#{sid}-t", "{opacity:1,y:0}", "{opacity:1,y:0,duration:0.01}", 0))
    else:
        tw.append((f"#{sid}-t", "{opacity:0,y:-30}", "{opacity:1,y:0,duration:0.4,ease:'power3.out'}", 0.12))
    return html, tw


def cta_card(sid, sc, dur, kind, photo=None):
    f_html, tw = _footage(sid, photo, dur, "cocktail" if kind == "cocktail" else "question", False)
    bubble = ('<svg viewBox="0 0 24 24" width="44" height="44"><path d="M4 4 H20 V16 H10 L5 20 V16 H4 Z" fill="none" '
              'stroke="#111" stroke-width="2.6" stroke-linejoin="round"/></svg>')
    html = (f_html + _title_html(sid, sc["m"], sc.get("s"))
            + f'<div id="{sid}-p" class="rpill">{bubble}{esc(sc.get("k") or "Comment")}</div>')
    tw += [(f"#{sid}-t", "{opacity:0,y:-30}", "{opacity:1,y:0,duration:0.4,ease:'power3.out'}", 0.12),
           (f"#{sid}-p", "{opacity:0,scale:0.6}", "{opacity:1,scale:1,duration:0.4,ease:'back.out(2)'}", 0.8),
           (f"#{sid}-p", None, "{scale:1.06,duration:0.5,yoyo:true,repeat:3,ease:'sine.inOut'}", 1.4)]
    return html, tw


def background_doc(kind, total):
    return scene_doc("bg", total, '<div style="position:absolute;inset:0;background:#0B0907"></div>', [])
