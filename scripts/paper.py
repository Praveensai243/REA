"""Paper" style (modelled on the pixel-host explainer reels):

  * light paper background, big black headline with one word on a yellow marker,
    a smaller grey line under it
  * a white card with a thick black border and a hard shadow: a dark "screen" with
    the video clip / photo / animated icon, and a strip below that ticks ✓ (FACT),
    crosses ✗ (MYTH) or shows ! (TIP); recipes become a checklist that ticks off
  * a black button that a cursor glides to and clicks
  * bold black word-by-word captions, left of the pixel host

Same builder API as style.py: every builder returns (html, tweens).
"""
import re

from icons import render_icon
from style import FONTS, esc, _vlen, phrases, three_glasses, scene_doc as _scene_doc  # noqa: F401

W, H = 1080, 1920
PAPER = "#EFECE5"
INK = "#141414"
MARK = "#F6D65A"                     # yellow marker
ACCENT = {"edu": MARK, "cocktail": MARK}   # make_video passes ACCENT[kind] to caption()
STRIP = {"MYTH": ("#FBE3E1", "#D93A2F", "✗", "MYTH"), "FACT": ("#E4F2E6", "#3E9A52", "✓", "FACT"),
         "TIP": ("#FFF1D6", "#B86E00", "!", "TIP"), None: ("#E4F2E6", "#3E9A52", "✓", None)}

HEAD = dict(left=70, right=70, top=300)
CARD = dict(left=70, top=590, width=880, height=330, shot=222)
BTN_TOP = 1000
CAP = dict(left=60, width=650, top=1160, height=330)

CSS = """
#root{position:absolute;inset:0;font-family:'Anek',sans-serif;color:%(ink)s;}
#root .head{position:absolute;left:%(hl)dpx;right:%(hr)dpx;top:%(ht)dpx;}
#root .h1{font-weight:800;font-size:76px;line-height:1.12;letter-spacing:-0.01em;}
#root .mk{background:linear-gradient(180deg,transparent 8%%,%(mark)s 8%%,%(mark)s 92%%,transparent 92%%);padding:0 0.12em;}
#root .h2{margin-top:14px;font-weight:800;font-size:44px;color:#77736B;}
#root .card{position:absolute;left:%(cl)dpx;top:%(ct)dpx;width:%(cw)dpx;height:%(ch)dpx;background:#FFFFFF;
  border:6px solid %(ink)s;box-shadow:16px 16px 0 %(ink)s;overflow:hidden;}
#root .shot{position:absolute;left:0;right:0;top:0;height:%(cs)dpx;background:#1C1916;overflow:hidden;border-bottom:6px solid %(ink)s;}
#root .photo{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;}
#root .bigicon{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;}
#root .strip{position:absolute;left:0;right:0;bottom:0;display:flex;align-items:center;gap:26px;padding:0 30px;}
#root .dot{flex:none;width:62px;height:62px;border-radius:50%%;display:flex;align-items:center;justify-content:center;color:#FFF;font-size:40px;font-weight:800;}
#root .stxt{flex:1;font-weight:800;font-size:46px;line-height:1.35;padding:8px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
#root .tag{flex:none;font-weight:800;font-size:34px;color:#77736B;}
#root .box{flex:none;width:150px;height:84px;border:6px solid %(ink)s;display:flex;align-items:center;justify-content:center;color:#FFF;font-size:52px;font-weight:800;}
#root .rows{position:absolute;left:34px;right:34px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;gap:18px;}
#root .row{display:flex;align-items:center;gap:22px;font-weight:800;line-height:1.1;}
#root .cb{flex:none;width:52px;height:52px;border:5px solid %(ink)s;background:#FFF;display:flex;align-items:center;justify-content:center;font-size:36px;color:#FFF;}
#root .btn{position:absolute;left:%(cl)dpx;top:%(bt)dpx;display:flex;align-items:center;gap:20px;padding:22px 40px;background:%(ink)s;color:#FFF;
  font-weight:800;font-size:46px;white-space:nowrap;}
#root .cursor{position:absolute;width:64px;height:64px;}
#root .cap{position:absolute;left:%(pl)dpx;width:%(pw)dpx;top:%(pt)dpx;height:%(ph)dpx;}
#root .phrase{position:absolute;left:0;right:0;top:0;text-align:center;font-weight:800;font-size:70px;line-height:1.14;text-wrap:balance;}
#root .w{display:inline-block;margin:0 0.12em;}
#root .acc-te,#root .acc-la{background:%(mark)s;padding:0 0.1em;}
#root .acc-la{font-family:'Accent',serif;font-style:italic;font-weight:700;}
""" % dict(ink=INK, mark=MARK, hl=HEAD["left"], hr=HEAD["right"], ht=HEAD["top"], cl=CARD["left"], ct=CARD["top"],
           cw=CARD["width"], ch=CARD["height"], cs=CARD["shot"], bt=BTN_TOP, pl=CAP["left"], pw=CAP["width"],
           pt=CAP["top"], ph=CAP["height"])

PLAY = '<svg viewBox="0 0 20 20" width="34" height="34"><path d="M5 3 L17 10 L5 17 Z" fill="#FFF"/></svg>'
BUBBLE = ('<svg viewBox="0 0 24 24" width="38" height="38"><path d="M4 4 H20 V16 H10 L5 20 V16 H4 Z" fill="none" '
          'stroke="#FFF" stroke-width="2.6" stroke-linejoin="round"/></svg>')
CURSOR_SVG = ('<svg viewBox="0 0 32 32" width="64" height="64"><path d="M4 2 L4 26 L10 20 L14 30 L19 28 L15 18 L24 18 Z" '
              'fill="#FFFFFF" stroke="#141414" stroke-width="2.4" stroke-linejoin="round"/></svg>')


def scene_doc(sid, dur, body, tweens):
    doc = _scene_doc(sid, dur, body, tweens)
    a = doc.index("<style>")
    b = doc.index("</style>", a) + len("</style>")
    return doc[:a] + "<style>" + FONTS + CSS + "</style>" + doc[b:]


# ------------------------------------------------------------------ headline
def _marked(text):
    """Headline html: the longest word sits on a yellow marker."""
    lines = [ln for ln in text.split("\n") if ln.strip()]
    words = [w for ln in lines for w in ln.split()]
    if not words:
        return ""
    key = max(words, key=_vlen)
    out, done = [], False
    for ln in lines:
        ws = []
        for w in ln.split():
            if w == key and not done:
                ws.append(f'<span class="mk">{esc(w)}</span>')
                done = True
            else:
                ws.append(esc(w))
        out.append(" ".join(ws))
    return "<br>".join(out)


def headline(sid, title, sub=None, first=False):
    units = max((_vlen(x) for x in title.split("\n")), default=10)
    lines = max(1, len([x for x in title.split("\n") if x.strip()]))
    room = 270 - (62 if sub else 0)          # keep clear of the card below
    size = int(max(50, min(84, 900 / (units * 0.52 + 1), room / (lines * 1.12))))
    html = (f'<div class="head"><div id="{sid}-h1" class="h1" style="font-size:{size}px">{_marked(title)}</div>'
            + (f'<div id="{sid}-h2" class="h2">{esc(sub)}</div>' if sub else "") + "</div>")
    if first:
        tw = [(f"#{sid}-h1", "{opacity:1,x:0}", "{opacity:1,x:0,duration:0.01}", 0)]
    else:
        tw = [(f"#{sid}-h1", "{opacity:0,x:-60}", "{opacity:1,x:0,duration:0.4,ease:'power3.out'}", 0.05)]
    if sub:
        tw.append((f"#{sid}-h2", "{opacity:%d,y:%d}" % ((1, 0) if first else (0, 16)), "{opacity:1,y:0,duration:0.35,ease:'power2.out'}", 0.2))
    return html, tw


# ------------------------------------------------------------------ captions
def caption(sid, text, v_start, v_len, accent_color=MARK, first=False):
    import style
    html, tw = style.caption(sid, text, v_start, v_len, accent_color, first=False)
    html = html.replace(' style="font-size:80px"', ' style="font-size:58px"')
    html = re.sub(r'(class="w acc-(?:te|la)") style="color:[^"]*"', r"\1", html)
    # plain pop-in (no blur) suits the flat look
    tw = [(a, b.replace(",filter:'blur(14px)'", ""), c.replace(",filter:'blur(0px)'", ""), d) if b else
          (a, b, c.replace(",filter:'blur(16px)'", ""), d) for a, b, c, d in tw]
    return html, tw


# ------------------------------------------------------------------ card
def _card_in(sid, dur, first):
    if first:
        t = [(f"#{sid}-card", "{opacity:1,y:0}", "{opacity:1,y:0,duration:0.01}", 0.0)]
    else:
        t = [(f"#{sid}-card", "{opacity:0,y:70,rotation:-2}", "{opacity:1,y:0,rotation:0,duration:0.45,ease:'back.out(1.6)'}", 0.1)]
    t.append((f"#{sid}-card", None, "{opacity:0,y:-30,duration:0.2,ease:'power2.in'}", round(max(dur - 0.22, 0.6), 2)))
    return t


def _strip(sid, label, stamp, at):
    bg, col, sym, tag = STRIP.get(stamp, STRIP[None])
    h = CARD["height"] - CARD["shot"] - 6
    html = (f'<div class="strip" style="height:{h}px;background:{bg}">'
            f'<div class="dot" style="background:{col}">{sym}</div>'
            f'<div class="stxt">{esc(label)}</div>'
            + (f'<div class="tag">{tag}</div>' if tag and tag.lower() not in label.lower() and label != "Smart Tip" else "") +
            f'<div id="{sid}-bx" class="box" style="background:#FFF"><span id="{sid}-bs" style="opacity:0">{sym}</span></div></div>')
    tw = [(f"#{sid}-bx", "{scale:1}", "{scale:1.12,backgroundColor:'%s',duration:0.14,yoyo:true,repeat:1,ease:'power2.out'}" % col, at),
          (f"#{sid}-bx", None, "{backgroundColor:'%s',duration:0.01}" % col, round(at + 0.3, 2)),
          (f"#{sid}-bs", "{opacity:0,scale:0.3}", "{opacity:1,scale:1,duration:0.25,ease:'back.out(3)'}", round(at + 0.05, 2))]
    return html, tw


def card(sid, sc, dur, kind, photo=None, icon=None, v_start=0.3, v_len=2.0, first=False):
    """Returns headline + card for a normal scene."""
    tw = []
    if sc.get("list"):
        title, sub = sc.get("k") or "", None
    else:
        title, sub = sc["m"], (sc.get("s") or None)
    h_html, h_tw = headline(sid, title, sub, first)
    tw += h_tw
    inner = []
    if sc.get("list"):
        rows = sc["m"].split("\n")
        longest = max(_vlen(r) for r in rows)
        size = max(36, int(min(54, 640 / (longest * 0.56), 300 / (len(rows) * 1.25))))
        times = [round(v_start + v_len * i / max(len(rows), 1), 2) for i in range(len(rows))]
        rh = []
        for i, r in enumerate(rows):
            rh.append(f'<div id="{sid}-r{i}" class="row" style="font-size:{size}px"><span id="{sid}-c{i}" class="cb">'
                      f'<span id="{sid}-t{i}" style="opacity:0">✓</span></span><span>{esc(r)}</span></div>')
            tw += [(f"#{sid}-r{i}", "{opacity:0,x:-30}", "{opacity:1,x:0,duration:0.25,ease:'power2.out'}", max(0.2, times[i] - 0.2)),
                   (f"#{sid}-c{i}", None, "{backgroundColor:'#3E9A52',duration:0.12}", times[i] + 0.15),
                   (f"#{sid}-t{i}", "{opacity:0,scale:0.3}", "{opacity:1,scale:1,duration:0.2,ease:'back.out(3)'}", times[i] + 0.15)]
        inner.append(f'<div class="rows">{"".join(rh)}</div>')
        height = CARD["height"] + 40
    else:
        shot = []
        full = bool(sc.get("anim"))
        if isinstance(photo, dict) and photo.get("kind") == "video":
            rate = f' data-playback-rate="{max(0.5, photo["dur"] / dur - 0.01):.3f}"' if photo["dur"] < dur else ""
            shot.append(f'<video id="{sid}-ph" class="photo clip" src="{photo["src"]}" muted playsinline '
                        f'data-start="0" data-duration="{dur:g}" data-media-start="0"{rate}></video>')
        elif photo:
            src = photo["src"] if isinstance(photo, dict) else photo
            shot.append(f'<img id="{sid}-ph" class="photo" src="{src}" alt="">')
            tw.append((f"#{sid}-ph", "{scale:1.04}", f"{{scale:1.16,duration:{dur:.2f},ease:'none'}}", 0))
        if sc.get("anim") == "three_glasses":
            g_html, g_tw = three_glasses(sid, v_start, v_len)
            shot.append(f'<div style="position:absolute;left:0;top:-140px;width:880px;height:640px;color:#FFF7EC;'
                        f'transform:scale(0.8);transform-origin:50% 0">{g_html}</div>')
            tw += g_tw
        elif not photo:
            ic_html, ic_tw = render_icon(icon or ("cocktail" if kind == "cocktail" else "question"), f"{sid}-ic", dur)
            if first:
                ic_tw = [x for x in ic_tw if x[0] != f"#{sid}-ic"]
            inner_size = 300 if full else 220
            ic_html = ic_html.replace('width="230" height="230"', f'width="{inner_size}" height="{inner_size}"')
            shot.append(f'<div class="bigicon">{ic_html}</div>')
            tw += ic_tw
        height = CARD["height"] + (60 if full else 0)
        shot_h = height - 12 if full else CARD["shot"]
        inner.append(f'<div class="shot" style="height:{shot_h}px{";border-bottom:none" if full else ""}">{"".join(shot)}</div>')
        if not full:
            label = sc.get("k") or {"MYTH": "ఇది Myth", "FACT": "ఇది Fact", "TIP": "Smart Tip"}.get(
                sc.get("stamp"), "Weekend Cocktail" if kind == "cocktail" else "Sipp Smart")
            s_html, s_tw = _strip(sid, label, sc.get("stamp"), round(v_start + min(v_len * 0.6, 1.6), 2))
            inner.append(s_html)
            tw += s_tw
    html = h_html + f'<div id="{sid}-card" class="card" style="height:{height}px">{"".join(inner)}</div>'
    if first:   # the hook gets a button + cursor click
        b_html, b_tw = button(sid, "Recipe చూడండి" if kind == "cocktail" else "నిజం తెలుసుకోండి",
                              PLAY, round(max(0.9, v_start + v_len * 0.7), 2))
        html += b_html
        tw += b_tw
    return html, _card_in(sid, dur, first) + tw


def button(sid, text, icon, click_at):
    """Black button; a cursor glides in from the bottom right and clicks it."""
    html = (f'<div id="{sid}-btn" class="btn">{icon}{esc(text)}</div>'
            f'<div id="{sid}-cur" class="cursor" style="left:{CARD["left"] + 300}px;top:{BTN_TOP + 50}px">{CURSOR_SVG}</div>')
    tw = [(f"#{sid}-btn", "{opacity:0,y:20}", "{opacity:1,y:0,duration:0.3,ease:'power2.out'}", round(max(0.3, click_at - 0.8), 2)),
          (f"#{sid}-cur", "{x:420,y:260,opacity:0}", "{x:0,y:0,opacity:1,duration:0.6,ease:'power3.out'}", round(max(0.4, click_at - 0.6), 2)),
          (f"#{sid}-cur", None, "{scale:0.8,duration:0.08,yoyo:true,repeat:1}", click_at),
          (f"#{sid}-btn", None, "{scale:0.94,duration:0.08,yoyo:true,repeat:1}", click_at),
          (f"#{sid}-btn", None, "{backgroundColor:'#3E9A52',duration:0.15}", round(click_at + 0.12, 2))]
    return html, tw


def cta_card(sid, sc, dur, kind, photo=None):
    h_html, tw = headline(sid, sc["m"], sc.get("s") or None)
    box = (f'<div id="{sid}-card" class="card" style="height:220px;top:{CARD["top"] + 40}px">'
           f'<div style="position:absolute;inset:0;display:flex;align-items:center;gap:26px;padding:0 34px">'
           f'<div class="dot" style="background:{INK}">{BUBBLE}</div>'
           f'<div id="{sid}-typ" style="flex:1;font-weight:800;font-size:52px;color:#77736B;white-space:nowrap;overflow:hidden">'
           f'{esc(sc.get("k") or "Comment")}…</div></div></div>')
    tw += _card_in(sid, dur + 1.0, False)[:1]
    tw.append((f"#{sid}-typ", "{clipPath:'inset(0 100% 0 0)'}", "{clipPath:'inset(0 0% 0 0)',duration:0.8,ease:'steps(12)'}", 0.6))
    b_html, b_tw = button(sid, sc.get("k") or "Comment", BUBBLE, 2.0)
    return h_html + box + b_html, tw + b_tw


# ------------------------------------------------------------------ background (root)
def background_doc(kind, total):
    """Paper background with a faint dot grid that drifts slowly."""
    dots = (f'<div id="grid" style="position:absolute;left:-60px;top:-60px;width:1200px;height:2040px;'
            f'background-image:radial-gradient(rgba(20,20,20,0.07) 2.2px, transparent 2.6px);background-size:54px 54px"></div>')
    body = f'<div style="position:absolute;inset:0;background:{PAPER}"></div>{dots}'
    tw = [("#grid", "{x:0,y:0}", f"{{x:-54,y:-54,duration:{total:.2f},ease:'none'}}", 0)]
    return scene_doc("bg", total, body, tw)
