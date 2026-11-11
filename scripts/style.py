"""Visual style (modelled on the reference reel):

  * word-by-word captions at the top, synced to the voice; each word blurs in,
    one key word per phrase gets a coloured serif accent
  * one floating card in the middle: a photo with slow zoom/pan (or an animated
    icon when there's no photo), MYTH/FACT chips, recipe checklists, the ending question
  * a continuous dark glow background with drifting particles (lives in the root)

Every builder returns (html, tweens). A tween is (selector, from_vars|None, to_vars, at).
"""
import html as _html
import re

from icons import render_icon

W, H = 1080, 1920
CAPTION_TOP = 200          # below Instagram's top bar
CARD = dict(left=150, top=610, size=780)   # bottom edge 1390, above Instagram's caption area

ACCENT = {"edu": "#FF7A6B", "cocktail": "#5EEAD4"}
GLOW = {"edu": ("#3B2A6B", "#120B1E"), "cocktail": ("#134E4A", "#071A1C")}
STAMP = {"MYTH": "#FF4D4D", "FACT": "#3DDC84", "TIP": "#F5A623"}

FONTS = """
@font-face{font-family:'Anek';font-weight:500;src:url('assets/fonts/anek-telugu-telugu-500-normal.woff2') format('woff2');unicode-range:U+0951-0952,U+0964-0965,U+0C00-0C7F,U+1CDA,U+1CF2,U+200C-200D,U+25CC;}
@font-face{font-family:'Anek';font-weight:800;src:url('assets/fonts/anek-telugu-telugu-800-normal.woff2') format('woff2');unicode-range:U+0951-0952,U+0964-0965,U+0C00-0C7F,U+1CDA,U+1CF2,U+200C-200D,U+25CC;}
@font-face{font-family:'Anek';font-weight:500;src:url('assets/fonts/anek-telugu-latin-500-normal.woff2') format('woff2');unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2212;}
@font-face{font-family:'Anek';font-weight:800;src:url('assets/fonts/anek-telugu-latin-800-normal.woff2') format('woff2');unicode-range:U+0000-00FF,U+2000-206F,U+2190-21FF,U+2212;}
@font-face{font-family:'Accent';font-weight:700;font-style:italic;src:url('assets/fonts/playfair-display-latin-700-italic.woff2') format('woff2');unicode-range:U+0000-00FF,U+2000-206F;}
"""

CSS = """
#root{position:absolute;inset:0;font-family:'Anek',sans-serif;color:#FFF7EC;}
#root .cap{position:absolute;left:60px;right:60px;top:%dpx;height:330px;display:flex;align-items:flex-start;justify-content:center;}
#root .phrase{position:absolute;left:0;right:0;top:0;text-align:center;font-weight:800;font-size:96px;line-height:1.14;text-wrap:balance;text-shadow:0 6px 28px rgba(0,0,0,0.45);}
#root .w{display:inline-block;margin:0 0.13em;}
#root .acc-te{transform:skewX(-9deg);}
#root .acc-la{font-family:'Accent',serif;font-style:italic;font-weight:700;}
#root .card{position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;border-radius:46px;overflow:hidden;
  background:linear-gradient(160deg,#2B1D40 0%%,#140C20 100%%);border:2px solid rgba(255,247,236,0.10);
  box-shadow:0 40px 120px rgba(0,0,0,0.55),0 0 0 1px rgba(0,0,0,0.3);}
#root .photo{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover;}
#root .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,6,14,0) 45%%,rgba(10,6,14,0.55) 100%%);}
#root .bigicon{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;}
#root .chip{position:absolute;display:inline-block;padding:10px 28px;border-radius:999px;font-weight:800;font-size:42px;white-space:nowrap;
  background:rgba(20,12,30,0.78);border:2px solid rgba(255,247,236,0.18);color:#FFF7EC;}
#root .stamp{position:absolute;left:44px;top:40px;border:8px solid currentColor;border-radius:20px;padding:2px 30px;
  font-size:96px;font-weight:800;background:rgba(10,6,14,0.55);}
#root .rows{position:absolute;left:56px;right:56px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;gap:26px;}
#root .row{display:flex;align-items:center;gap:22px;font-weight:800;line-height:1.15;}
#root .tick{flex:none;width:46px;height:46px;border-radius:50%%;display:flex;align-items:center;justify-content:center;font-size:30px;color:#140C20;}
#root .ask{position:absolute;left:50px;right:50px;top:200px;text-align:center;font-weight:800;line-height:1.15;}
#root .pill{position:absolute;left:50%%;transform:translateX(-50%%);bottom:150px;padding:18px 44px;border-radius:999px;font-size:52px;font-weight:800;background:#F5A623;color:#2A1606;white-space:nowrap;}
#root .sub{position:absolute;left:40px;right:40px;bottom:62px;text-align:center;font-size:36px;font-weight:500;color:#E9DCCB;}
""" % (CAPTION_TOP, CARD["left"], CARD["top"], CARD["size"], CARD["size"])


def esc(s):
    return _html.escape(s)


def _vlen(s):
    w = 0.0
    for c in s:
        o = ord(c)
        if 0x0C3E <= o <= 0x0C56 or o in (0x0C01, 0x0C03, 0x0C4D):
            continue
        w += 1.85 if 0x0C00 <= o <= 0x0C7F else 1.0
    return w


# ------------------------------------------------------------------ captions
def phrases(text, max_units=27):
    """Split the spoken line into short phrases (≤ 2 caption lines each)."""
    words = text.split()
    out, cur, units = [], [], 0.0
    for w in words:
        u = _vlen(w) + 1
        if cur and (units + u > max_units):
            out.append(cur)
            cur, units = [], 0.0
        cur.append(w)
        units += u
        if re.search(r"[.?!]$", w) and units > 8:
            out.append(cur)
            cur, units = [], 0.0
    if cur:
        if out and sum(_vlen(w) + 1 for w in cur) < 9 and sum(_vlen(w) + 1 for w in out[-1] + cur) <= max_units * 1.6:
            out[-1] += cur          # don't leave one lonely word on its own
        else:
            out.append(cur)
    return out


def caption(sid, text, v_start, v_len, accent_color, first=False):
    """Word-by-word caption. Word times are spread over the voice by word length
    (+ small pauses at commas and full stops)."""
    groups = phrases(text)
    words = [w for g in groups for w in g]
    weights = [_vlen(w) + 1.2 + (3.0 if re.search(r"[.?!]$", w) else (1.6 if w.endswith(",") else 0.0)) for w in words]
    total = sum(weights) or 1.0
    t_words, acc = [], 0.0
    for wt in weights:
        t_words.append(v_start + v_len * acc / total)
        acc += wt
    # merge a phrase into the next one if it would be on screen too briefly to read
    merged = True
    while merged and len(groups) > 1:
        merged = False
        idx = 0
        for gi in range(len(groups) - 1):
            start, nxt = t_words[idx], t_words[idx + len(groups[gi])]
            need = 0.55 + 0.3 * len(groups[gi])
            combined = sum(_vlen(w) + 1 for w in groups[gi] + groups[gi + 1])
            if nxt - start < need and combined <= 46:
                groups[gi] = groups[gi] + groups.pop(gi + 1)
                merged = True
                break
            idx += len(groups[gi])
    parts, tweens, k = [], [], 0
    starts = []
    for gi, g in enumerate(groups):
        accent_i = max(range(len(g)), key=lambda i: _vlen(g[i])) if len(g) >= 3 else -1
        spans = []
        for wi, w in enumerate(g):
            cls = "w"
            if wi == accent_i:
                cls += " acc-te" if re.search(r"[\u0C00-\u0C7F]", w) else " acc-la"
            style = f' style="color:{accent_color}"' if wi == accent_i else ""
            spans.append(f'<span id="{sid}-w{k}" class="{cls}"{style}>{esc(w)}</span>')
            if first and gi == 0:   # thumbnail: the opening line is already there on frame 0
                tweens.append((f"#{sid}-w{k}", "{opacity:1,scale:1.06}", "{opacity:1,scale:1,duration:0.4,ease:'power2.out'}", 0))
            else:
                tweens.append((f"#{sid}-w{k}", "{opacity:0,y:16,filter:'blur(14px)'}",
                               "{opacity:1,y:0,filter:'blur(0px)',duration:0.22,ease:'power2.out'}", round(t_words[k], 2)))
            k += 1
        starts.append(t_words[k - len(g)])
        units = sum(_vlen(w) + 1 for w in g)
        fs = "" if units <= 32 else ' style="font-size:80px"'   # long phrase: smaller so it stays in 2–3 lines
        parts.append(f'<div id="{sid}-p{gi}" class="phrase"{fs}>{" ".join(spans)}</div>')
    # each phrase blurs away just before the next one starts
    for gi in range(len(groups) - 1):
        tweens.append((f"#{sid}-p{gi}", None, "{opacity:0,filter:'blur(16px)',duration:0.16,ease:'power1.in'}",
                       round(max(starts[gi + 1] - 0.14, starts[gi] + 0.3), 2)))
    return f'<div class="cap">{"".join(parts)}</div>', tweens


# ------------------------------------------------------------------ card
def _card_motion(sid, dur, first=False):
    if first:
        t = [(f"#{sid}-card", "{opacity:1,scale:1.04}", "{opacity:1,scale:1,duration:0.55,ease:'power2.out'}", 0.0)]
    else:
        t = [(f"#{sid}-card", "{opacity:0,y:90,scale:0.9,rotation:-3}",
              "{opacity:1,y:0,scale:1,rotation:0,duration:0.55,ease:'back.out(1.5)'}", 0.0)]
    if dur > 1.4:
        t.append((f"#{sid}-card", None, f"{{y:-14,rotation:1.2,duration:{(dur - 0.9) / 2:.2f},yoyo:true,repeat:1,ease:'sine.inOut'}}", 0.55))
    t.append((f"#{sid}-card", None, "{opacity:0,y:-50,scale:0.96,duration:0.22,ease:'power2.in'}", round(max(dur - 0.24, 0.6), 2)))
    return t


def card(sid, sc, dur, kind, photo=None, icon=None, v_start=0.3, v_len=2.0, first=False):
    inner, tw = [], []
    if isinstance(photo, dict) and photo.get("kind") == "video":
        rate = ""
        if photo["dur"] < dur:   # slow a short clip down so it covers the whole scene
            rate = f' data-playback-rate="{max(0.5, photo["dur"] / dur - 0.01):.3f}"'
        inner.append(f'<video id="{sid}-ph" class="photo clip" src="{photo["src"]}" muted playsinline '
                     f'data-start="0" data-duration="{dur:g}" data-media-start="0"{rate}></video>')
        inner.append('<div class="shade"></div>')
    elif photo:
        src = photo["src"] if isinstance(photo, dict) else photo
        inner.append(f'<img id="{sid}-ph" class="photo" src="{src}" alt="">')
        inner.append('<div class="shade"></div>')
        tw.append((f"#{sid}-ph", "{scale:1.02,xPercent:-2}", f"{{scale:1.16,xPercent:2,duration:{dur:.2f},ease:'none'}}", 0))
    if sc.get("anim") == "three_glasses":
        g_html, g_tw = three_glasses(sid, v_start, v_len)
        inner.append(g_html)
        tw += g_tw
    elif sc.get("list"):
        if photo:
            inner.append('<div style="position:absolute;inset:0;background:rgba(14,8,20,0.72)"></div>')
        rows = sc["m"].split("\n")
        longest = max(_vlen(r) for r in rows)
        size = max(36, int(min(56, 470 / (longest * 0.56), 600 / (len(rows) * 1.5))))
        html_rows = []
        times = [round(v_start + v_len * i / max(len(rows), 1), 2) for i in range(len(rows))]
        for i, r in enumerate(rows):
            html_rows.append(f'<div id="{sid}-r{i}" class="row" style="font-size:{size}px">'
                             f'<span class="tick" style="background:{ACCENT[kind]}">✓</span><span>{esc(r)}</span></div>')
            tw.append((f"#{sid}-r{i}", "{opacity:0,x:-40}", "{opacity:1,x:0,duration:0.3,ease:'power2.out'}", times[i]))
        inner.append(f'<div class="rows" style="right:250px">{"".join(html_rows)}</div>')
        # a glass on the right fills a little more with every ingredient
        inner.append(f'''<svg viewBox="0 0 200 260" width="190" height="247" style="position:absolute;right:40px;bottom:120px;overflow:visible">
          <defs><clipPath id="{sid}-gc"><path d="M40 40 L52 236 Q53 246 63 246 L137 246 Q147 246 148 236 L160 40 Z"/></clipPath></defs>
          <g clip-path="url(#{sid}-gc)"><rect id="{sid}-gl" x="30" y="40" width="140" height="220" fill="{ACCENT[kind]}" opacity="0.85"/></g>
          <path d="M40 40 L52 236 Q53 246 63 246 L137 246 Q147 246 148 236 L160 40" stroke="#FFF7EC" stroke-width="6" fill="none" stroke-linejoin="round"/>
          <circle id="{sid}-dr" cx="100" cy="-40" r="10" fill="{ACCENT[kind]}"/></svg>''')
        tw.append((f"#{sid}-gl", "{y:210}", "{y:210,duration:0.01}", 0))
        for i, tt in enumerate(times):
            level = 210 - 190 * (i + 1) / len(rows)
            tw.append((f"#{sid}-dr", "{y:0,opacity:1}", "{y:90,opacity:0,duration:0.35,ease:'power2.in',immediateRender:false}", tt))
            tw.append((f"#{sid}-gl", None, f"{{y:{level:.0f},duration:0.4,ease:'power2.out'}}", round(tt + 0.25, 2)))
    elif not photo:
        ic_html, ic_tw = render_icon(icon or ("cocktail" if kind == "cocktail" else "question"), f"{sid}-ic", dur)
        if first:   # thumbnail: no pop-in, the icon is already there
            ic_tw = [x for x in ic_tw if x[0] != f"#{sid}-ic"]
        ic_html = ic_html.replace('width="230" height="230"', 'width="440" height="440"')
        inner.append(f'<div class="bigicon">{ic_html}</div>')
        tw += ic_tw
    if sc.get("stamp"):
        col = STAMP.get(sc["stamp"], "#FFF7EC")
        inner.append(f'<div id="{sid}-st" class="stamp" style="color:{col}">{esc(sc["stamp"])}</div>')
        tw.append((f"#{sid}-st", "{scale:2.2,opacity:0,rotation:-14}",
                   "{scale:1,opacity:1,rotation:-6,duration:0.35,ease:'power4.out'}", 0.05))
    out = (f'<div id="{sid}-card" class="card">{"".join(inner)}</div>')
    tw = _card_motion(sid, dur, first) + tw
    if sc.get("k"):
        out += (f'<div id="{sid}-k" class="chip" style="left:50%;transform:translateX(-50%);top:{CARD["top"] - 78}px;'
                f'color:{ACCENT[kind]}">{esc(sc["k"])}</div>')
        tw.append((f"#{sid}-k", "{opacity:%s,y:%s}" % ((1, 0) if first else (0, 20)), "{opacity:1,y:0,duration:0.3,ease:'power2.out'}", 0.15 if not first else 0))
    if photo and icon:   # small floating sticker on the card corner
        st_html, st_tw = render_icon(icon, f"{sid}-sk", dur)
        st_html = st_html.replace('width="230" height="230"', 'width="170" height="170"')
        out += (f'<div id="{sid}-skw" style="position:absolute;left:{CARD["left"] + CARD["size"] - 120}px;'
                f'top:{CARD["top"] + CARD["size"] - 150}px;width:190px;height:190px;border-radius:50%;'
                f'background:rgba(20,12,30,0.85);border:3px solid rgba(255,247,236,0.18);display:flex;'
                f'align-items:center;justify-content:center">{st_html}</div>')
        tw += st_tw
        tw.append((f"#{sid}-skw", "{scale:0,rotation:-30}", "{scale:1,rotation:0,duration:0.45,ease:'back.out(2)'}", 0.35))
    return out, tw


def three_glasses(sid, v_start, v_len):
    """30ml whisky = 250ml beer = 100ml wine: three glasses fill, each to the same alcohol line."""
    glasses = [  # (x, glass path, fill colour, fill top y, label)
        (40, "M20 120 L28 230 Q29 238 37 238 L103 238 Q111 238 112 230 L120 120", "#F5A623", 200, "30ml Whisky"),
        (270, "M30 30 L40 230 Q41 238 49 238 L111 238 Q119 238 120 230 L130 30", "#F7C948", 60, "250ml Beer"),
        (500, "M20 40 Q20 150 70 156 Q120 150 120 40", "#B3123F", 95, "100ml Wine"),
    ]
    html, tw = [], []
    for n, (x, path, col, top, label) in enumerate(glasses):
        extra = '<path d="M70 156 L70 226 M40 232 L100 232" stroke="#FFF7EC" stroke-width="6" stroke-linecap="round"/>' if n == 2 else ""
        html.append(f'''<div style="position:absolute;left:{x + 10}px;top:185px;width:240px;text-align:center">
          <svg viewBox="0 0 140 250" width="146" height="260" style="overflow:visible">
            <defs><clipPath id="{sid}-c{n}"><path d="{path} Z"/></clipPath></defs>
            <g clip-path="url(#{sid}-c{n})"><rect id="{sid}-f{n}" x="0" y="{top}" width="140" height="260" fill="{col}"/></g>
            <path d="{path}" stroke="#FFF7EC" stroke-width="5" fill="none" stroke-linejoin="round"/>{extra}
          </svg>
          <div style="font-weight:800;font-size:34px;margin-top:4px">{label}</div>
          <div id="{sid}-eq{n}" style="display:inline-block;margin-top:6px;padding:6px 18px;border-radius:999px;background:#3DDC84;color:#0B1F14;font-weight:800;font-size:32px">≈ 10g alcohol</div>
        </div>''')
        at = round(v_start + v_len * n / 3, 2)
        tw.append((f"#{sid}-f{n}", "{y:260}", "{y:0,duration:0.9,ease:'power2.out'}", at))
        tw.append((f"#{sid}-eq{n}", "{opacity:0,scale:0.6}", "{opacity:1,scale:1,duration:0.3,ease:'back.out(2)'}", round(at + 0.8, 2)))
    return "".join(html), tw


def cta_card(sid, sc, dur, kind, photo=None):
    lines = sc["m"].split("\n")
    longest = max(_vlen(x) for x in lines)
    size = int(min(96, 640 / (longest * 0.56), 400 / (len(lines) * 1.16)))
    bg = (f'<img id="{sid}-ph" class="photo" src="{photo}" alt="" style="opacity:0.38">'
          f'<div class="shade" style="background:linear-gradient(180deg,rgba(14,8,20,0.55),rgba(14,8,20,0.85))"></div>') if photo else ""
    out = (f'<div id="{sid}-card" class="card">{bg}'
           f'<div id="{sid}-ask" class="ask" style="font-size:{size}px">{esc(sc["m"]).replace(chr(10), "<br>")}</div>'
           + (f'<div id="{sid}-pill" class="pill">{esc(sc["pill"])}</div>' if sc.get("pill") else "") +
           f'<div class="sub">{esc(sc["s"])}</div></div>'
           f'<div id="{sid}-k" class="chip" style="left:50%;transform:translateX(-50%);top:{CARD["top"] - 78}px;'
           f'color:{ACCENT[kind]}">{esc(sc["k"])}</div>')
    tw = _card_motion(sid, dur + 1.0)[:2] + [
        (f"#{sid}-ask", "{opacity:0,y:30}", "{opacity:1,y:0,duration:0.4,ease:'power3.out'}", 0.3),
    ] + ([(f"#{sid}-pill", "{opacity:0,scale:0.7}", "{opacity:1,scale:1,duration:0.4,ease:'back.out(2)'}", 0.9)] if sc.get("pill") else []) + [
        (f"#{sid}-k", "{opacity:0,y:20}", "{opacity:1,y:0,duration:0.3,ease:'power2.out'}", 0.15),
    ]
    return out, tw


# ------------------------------------------------------------------ background (root)
def background_doc(kind, total):
    """The glow background + drifting particles, as its own sub-composition."""
    a, b = GLOW[kind]
    dots, tw = [], []
    for i in range(18):
        x = (i * 263) % 1040 + 20
        y = 300 + (i * 397) % 1500
        s = 6 + (i % 4) * 3
        dots.append(f'<div id="pt{i}" style="position:absolute;left:{x}px;top:{y}px;width:{s}px;height:{s}px;'
                    f'border-radius:50%;background:#FFF7EC;opacity:{0.12 + (i % 5) * 0.05:.2f}"></div>')
        tw.append((f"#pt{i}", "{y:0}", f"{{y:-{200 + (i % 6) * 60},x:{(i % 3 - 1) * 40},duration:{total:.2f},ease:'none'}}", 0))
    body = (f'<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 52%, {a} 0%, {b} 62%, #07040B 100%)"></div>'
            f'<div id="glow" style="position:absolute;left:140px;top:560px;width:800px;height:800px;border-radius:50%;'
            f'background:radial-gradient(circle,{ACCENT[kind]}33 0%,transparent 65%)"></div>{"".join(dots)}')
    tw.append(("#glow", "{scale:0.9,opacity:0.6}", f"{{scale:1.15,opacity:1,duration:{total / 4:.2f},yoyo:true,repeat:3,ease:'sine.inOut'}}", 0))
    return scene_doc("bg", total, body, tw)


def scene_doc(sid, dur, body, tweens):
    tl = "\n".join(f"    tl.fromTo('{a}', {b}, {c}, {d});" if b else f"    tl.to('{a}', {c}, {d});" for a, b, c, d in tweens)
    return f"""<template>
  <style>{FONTS}{CSS}</style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
    {body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{tl}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""
