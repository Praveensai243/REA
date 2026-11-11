"""Animated icons (SVG + GSAP) in the Sipp Smart colours. Drawn here, so they're free.

icon_for(scene, kind) picks an icon from the scene's words.
render_icon(name, prefix, dur) returns (svg_html, tweens); a tween is
(selector, from_vars or None, to_vars, at) — the same format make_video.py uses.
"""

AMBER = "#F5A623"
CREAM = "#FFF7EC"
WINE = "#B3123F"
MINT = "#3DDC84"
SKY = "#6EC6FF"
LINE = f'stroke="{CREAM}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round" fill="none"'

# (keywords, icon) — first match wins; checked against kicker + text + voice
RULES = [
    (["Christmas", "క్రిస్మస్"], "tree"),
    (["coffee", "Coffee", "కాఫీ", "Espresso", "Caffeine", "కెఫీన్"], "coffee"),
    (["Energy", "ఎనర్జీ"], "bolt"),
    (["drive", "Drive", "డ్రైవ్", "Cab", "క్యాబ్", "Breathalyzer"], "car"),
    (["Law", "Ban", "బ్యాన్", "limit", "లిమిట్", "నిషేధం", "GIFT"], "gavel"),
    (["tablet", "Paracetamol", "టాబ్లెట్", "మందు వేసుకు", "Doctor"], "pill"),
    (["నిద్ర", "sleep", "REM"], "moon"),
    (["గుండె", "heart", "Health కోసం"], "heart"),
    (["చలి", "వెచ్చ", "body heat", "సూప్"], "thermo"),
    (["కల్లు", "Toddy", "తాటి"], "palm"),
    (["టైమ్", "Liver కి"], "clock"),
    (["Washroom", "Kidneys", "నీళ్లు", "నీటి", "glass నీళ్లు", "water"], "water"),
    (["Mojito", "Cuba Libre", "Tonic", "Lemonade", "Mule", "Fizz", "G&T", "Soda"], "highball"),
    (["Margarita", "Negroni", "Daiquiri", "Martini", "Sour", "Cocktail", "cocktail"], "cocktail"),
    (["Beer", "బీర్", "Lager", "Ale", "beer"], "beer"),
    (["Wine", "వైన్", "wine"], "wine"),
    (["Whisky", "విస్కీ", "Single Malt", "Bourbon", "Old Fashioned", "Malt", "whisk", "Whiskies"], "whisky"),
    (["Vodka", "Tequila", "Rum", "Old Monk", "Gin", "Feni", "bottle", "Bottle", "Label", "Agave", "Proof"], "bottle"),
    (["shake", "Ice", "ice"], "shaker"),
]


def icon_for(scene, kind=None, fallback=True):
    """Icon that fits the scene's words. With fallback=False, returns None when
    nothing fits (so the scene shows no icon rather than a random one)."""
    text = " ".join(str(scene.get(k, "")) for k in ("k", "m", "s", "v"))
    if scene.get("icon"):
        return scene["icon"]
    for words, name in RULES:
        if any(w in text for w in words):
            return name
    if not fallback:
        return None
    return "cocktail" if kind == "cocktail" else "question"


def plan_icons(scenes, kind):
    """One icon per scene (or None): always on the hook; elsewhere only when the
    words clearly fit and it isn't the same icon as the scene before."""
    out, prev = [], None
    day_icon = next((i for i in (icon_for(s, kind, False) for s in scenes) if i), None)
    for n, sc in enumerate(scenes):
        if sc.get("stamp") or sc.get("list"):
            out.append(None)
            continue
        ic = icon_for(sc, kind, False)
        if n == 0:
            ic = ic or day_icon or ("cocktail" if kind == "cocktail" else "question")
        elif ic == prev:
            ic = None
        out.append(ic)
        prev = ic or prev
    return out


def _reps(dur, period):
    return max(1, int(dur / period))


def render_icon(name, p, dur):  # noqa: D401
    """p = unique id prefix for this scene."""
    fn = ICONS.get(name, ICONS["question"])
    svg, tweens = fn(p, dur)
    html = (f'<svg id="{p}" class="icon" viewBox="0 0 200 200" width="230" height="230" '
            f'xmlns="http://www.w3.org/2000/svg" style="overflow:visible">{svg}</svg>')
    # every icon pops in
    tweens = [(f"#{p}", "{opacity:0,scale:0.6,y:20}", "{opacity:1,scale:1,y:0,duration:0.45,ease:'back.out(1.7)'}", 0.05)] + tweens
    return html, tweens


# ------------------------------------------------------------------ icons
def whisky(p, dur):
    svg = f'''
    <defs><clipPath id="{p}-c"><path d="M48 70 L58 170 Q60 178 70 178 L130 178 Q140 178 142 170 L152 70 Z"/></clipPath></defs>
    <g clip-path="url(#{p}-c)">
      <rect id="{p}-liq" x="40" y="105" width="120" height="80" fill="{AMBER}" opacity="0.95"/>
      <rect id="{p}-i1" x="66" y="92" width="32" height="32" rx="6" fill="{CREAM}" opacity="0.75"/>
      <rect id="{p}-i2" x="104" y="98" width="30" height="30" rx="6" fill="{CREAM}" opacity="0.6"/>
    </g>
    <path d="M48 70 L58 170 Q60 178 70 178 L130 178 Q140 178 142 170 L152 70" {LINE}/>
    <path d="M60 80 L66 160" stroke="{CREAM}" stroke-width="4" opacity="0.35" stroke-linecap="round"/>'''
    t = [(f"#{p}-liq", "{scaleY:0,transformOrigin:'50% 100%'}", "{scaleY:1,duration:0.9,ease:'power2.out'}", 0.2),
         (f"#{p}-i1", "{y:-70,rotation:-20}", "{y:0,rotation:8,duration:0.7,ease:'bounce.out'}", 0.5),
         (f"#{p}-i2", "{y:-90,rotation:25}", "{y:0,rotation:-6,duration:0.8,ease:'bounce.out'}", 0.65),
         (f"#{p}-i1", None, f"{{y:-5,duration:0.9,yoyo:true,repeat:{_reps(dur, 0.9)},ease:'sine.inOut'}}", 1.3)]
    return svg, t


def beer(p, dur):
    bubbles = "".join(f'<circle class="{p}-b" cx="{70 + (i * 17) % 60}" cy="165" r="{3 + i % 3}" fill="{CREAM}" opacity="0.7"/>' for i in range(7))
    svg = f'''
    <defs><clipPath id="{p}-c"><rect x="50" y="62" width="88" height="118" rx="8"/></clipPath></defs>
    <g clip-path="url(#{p}-c)">
      <rect id="{p}-liq" x="50" y="80" width="88" height="100" fill="{AMBER}"/>
      {bubbles}
    </g>
    <g id="{p}-foam" fill="{CREAM}">
      <circle cx="62" cy="68" r="15"/><circle cx="84" cy="60" r="18"/><circle cx="108" cy="62" r="17"/><circle cx="128" cy="69" r="14"/>
    </g>
    <rect x="50" y="62" width="88" height="118" rx="8" {LINE}/>
    <path d="M138 88 Q170 88 170 118 Q170 148 138 148" {LINE}/>'''
    t = [(f"#{p}-liq", "{scaleY:0,transformOrigin:'50% 100%'}", "{scaleY:1,duration:0.8,ease:'power2.out'}", 0.15),
         (f"#{p}-foam", "{scale:0,transformOrigin:'50% 100%'}", "{scale:1,duration:0.5,ease:'back.out(2)'}", 0.8),
         (f".{p}-b", "{y:0,opacity:0.8}", f"{{y:-95,opacity:0,duration:1.2,stagger:0.17,repeat:{_reps(dur, 1.3)},ease:'none'}}", 0.6)]
    return svg, t


def wine(p, dur):
    svg = f'''
    <defs><clipPath id="{p}-c"><path d="M58 40 Q58 120 100 124 Q142 120 142 40 Z"/></clipPath></defs>
    <g id="{p}-g">
      <g clip-path="url(#{p}-c)"><path id="{p}-liq" d="M40 80 Q100 70 160 80 L160 140 L40 140 Z" fill="{WINE}"/></g>
      <path d="M58 40 Q58 120 100 124 Q142 120 142 40" {LINE}/>
      <path d="M100 124 L100 172 M72 176 L128 176" {LINE}/>
    </g>'''
    t = [(f"#{p}-liq", "{y:50}", "{y:0,duration:0.8,ease:'power2.out'}", 0.2),
         (f"#{p}-g", "{rotation:0,transformOrigin:'50% 95%'}", f"{{rotation:7,duration:0.8,yoyo:true,repeat:{_reps(dur, 0.8)},ease:'sine.inOut'}}", 0.9),
         (f"#{p}-liq", None, f"{{rotation:-10,transformOrigin:'50% 50%',duration:0.8,yoyo:true,repeat:{_reps(dur, 0.8)},ease:'sine.inOut'}}", 0.9)]
    return svg, t


def cocktail(p, dur):
    svg = f'''
    <defs><clipPath id="{p}-c"><path d="M40 52 L160 52 L100 118 Z"/></clipPath></defs>
    <g clip-path="url(#{p}-c)"><rect id="{p}-liq" x="40" y="62" width="120" height="60" fill="#FF6F61"/></g>
    <path d="M40 52 L160 52 L100 118 Z" {LINE}/>
    <path d="M100 118 L100 170 M72 174 L128 174" {LINE}/>
    <g id="{p}-lime" transform="translate(150 50)">
      <circle r="22" fill="{MINT}"/><circle r="16" fill="#C8F7A6"/>
      <path d="M0 -16 L0 16 M-16 0 L16 0 M-11 -11 L11 11 M-11 11 L11 -11" stroke="{MINT}" stroke-width="2.5"/>
    </g>'''
    t = [(f"#{p}-liq", "{scaleY:0,transformOrigin:'50% 100%'}", "{scaleY:1,duration:0.8,ease:'power2.out'}", 0.2),
         (f"#{p}-lime", "{scale:0,rotation:-90,svgOrigin:'150 50'}", "{scale:1,rotation:0,duration:0.6,ease:'back.out(2)'}", 0.7),
         (f"#{p}-lime", None, f"{{rotation:360,svgOrigin:'150 50',duration:{max(dur - 1.3, 1):.2f},ease:'none'}}", 1.3)]
    return svg, t


def highball(p, dur):
    bubbles = "".join(f'<circle class="{p}-b" cx="{78 + (i * 13) % 44}" cy="170" r="{2.5 + i % 3}" fill="{CREAM}" opacity="0.8"/>' for i in range(8))
    svg = f'''
    <defs><clipPath id="{p}-c"><rect x="64" y="40" width="72" height="140" rx="6"/></clipPath></defs>
    <g clip-path="url(#{p}-c)">
      <rect id="{p}-liq" x="64" y="62" width="72" height="118" fill="#9BE7C4" opacity="0.85"/>
      <ellipse cx="88" cy="90" rx="10" ry="6" fill="{MINT}" transform="rotate(-30 88 90)"/>
      <ellipse cx="112" cy="112" rx="10" ry="6" fill="{MINT}" transform="rotate(25 112 112)"/>
      {bubbles}
    </g>
    <rect x="64" y="40" width="72" height="140" rx="6" {LINE}/>
    <path id="{p}-straw" d="M118 20 L106 150" stroke="{AMBER}" stroke-width="8" stroke-linecap="round"/>'''
    t = [(f"#{p}-liq", "{scaleY:0,transformOrigin:'50% 100%'}", "{scaleY:1,duration:0.8,ease:'power2.out'}", 0.2),
         (f"#{p}-straw", "{y:-60,opacity:0}", "{y:0,opacity:1,duration:0.5,ease:'power2.out'}", 0.7),
         (f".{p}-b", "{y:0,opacity:0.9}", f"{{y:-110,opacity:0,duration:1.1,stagger:0.14,repeat:{_reps(dur, 1.2)},ease:'none'}}", 0.6)]
    return svg, t


def coffee(p, dur):
    steam = "".join(f'<path class="{p}-s" d="M{80 + i * 20} 70 q-10 -12 0 -24 q10 -12 0 -24" {LINE} opacity="0.8"/>' for i in range(3))
    svg = f'''
    {steam}
    <path d="M50 80 L150 80 L140 150 Q136 166 120 166 L80 166 Q64 166 60 150 Z" fill="{AMBER}" opacity="0.25"/>
    <path d="M50 80 L150 80 L140 150 Q136 166 120 166 L80 166 Q64 166 60 150 Z" {LINE}/>
    <path d="M148 92 Q176 92 172 116 Q168 136 142 134" {LINE}/>
    <path d="M36 178 L164 178" {LINE}/>'''
    t = [(f".{p}-s", "{y:10,opacity:0}", f"{{y:-18,opacity:0.9,duration:1,stagger:0.25,yoyo:true,repeat:{_reps(dur, 1.0)},ease:'sine.inOut'}}", 0.3)]
    return svg, t


def bottle(p, dur):
    """Bottle tips over and pours into a glass that fills up."""
    svg = f'''
    <defs><clipPath id="{p}-gc"><path d="M108 120 L114 186 Q115 192 121 192 L163 192 Q169 192 170 186 L176 120 Z"/></clipPath></defs>
    <g clip-path="url(#{p}-gc)"><rect id="{p}-liq" x="100" y="120" width="80" height="80" fill="{AMBER}"/></g>
    <path d="M108 120 L114 186 Q115 192 121 192 L163 192 Q169 192 170 186 L176 120" {LINE}/>
    <rect id="{p}-stream" x="134" y="64" width="8" height="70" rx="4" fill="{AMBER}"/>
    <g id="{p}-g">
      <path d="M40 30 L58 30 L58 52 Q74 60 74 78 L74 150 Q74 158 66 158 L32 158 Q24 158 24 150 L24 78 Q24 60 40 52 Z" fill="{AMBER}" opacity="0.25"/>
      <path d="M40 30 L58 30 L58 52 Q74 60 74 78 L74 150 Q74 158 66 158 L32 158 Q24 158 24 150 L24 78 Q24 60 40 52 Z" {LINE}/>
      <rect x="28" y="96" width="42" height="30" rx="5" fill="{AMBER}"/>
    </g>'''
    t = [(f"#{p}-g", "{rotation:0,svgOrigin:'49 158'}", "{rotation:118,x:40,y:-60,svgOrigin:'49 158',duration:0.7,ease:'power2.inOut'}", 0.3),
         (f"#{p}-stream", "{scaleY:0,transformOrigin:'50% 0%',opacity:1}", "{scaleY:1,duration:0.25,ease:'none'}", 0.95),
         (f"#{p}-liq", "{y:72}", f"{{y:0,duration:{max(1.2, min(2.4, dur - 1.6)):.2f},ease:'power1.out'}}", 1.05),
         (f"#{p}-stream", None, "{opacity:0,duration:0.2}", round(1.05 + max(1.2, min(2.4, dur - 1.6)), 2))]
    return svg, t


def shaker(p, dur):
    svg = f'''
    <g id="{p}-g">
      <path d="M70 70 L130 70 L122 178 L78 178 Z" fill="{CREAM}" opacity="0.15"/>
      <path d="M70 70 L130 70 L122 178 L78 178 Z" {LINE}/>
      <path d="M76 70 Q76 44 100 40 Q124 44 124 70" {LINE}/>
      <rect x="90" y="24" width="20" height="16" rx="4" {LINE}/>
      <path d="M78 110 L122 110" stroke="{AMBER}" stroke-width="6"/>
    </g>
    <circle class="{p}-d" cx="150" cy="60" r="5" fill="{SKY}"/><circle class="{p}-d" cx="48" cy="80" r="4" fill="{SKY}"/>
    <circle class="{p}-d" cx="160" cy="110" r="3" fill="{SKY}"/>'''
    t = [(f"#{p}-g", "{rotation:-14,transformOrigin:'50% 60%'}", f"{{rotation:14,duration:0.14,yoyo:true,repeat:{_reps(dur, 0.14)},ease:'sine.inOut'}}", 0.4),
         (f".{p}-d", "{scale:0,opacity:1}", f"{{scale:1.6,opacity:0,duration:0.5,stagger:0.12,repeat:{_reps(dur, 0.6)},ease:'power1.out'}}", 0.5)]
    return svg, t


def water(p, dur):
    svg = f'''
    <defs><clipPath id="{p}-c"><path d="M56 50 L144 50 L134 178 L66 178 Z"/></clipPath></defs>
    <g clip-path="url(#{p}-c)"><path id="{p}-liq" d="M40 100 Q70 90 100 100 T160 100 L160 190 L40 190 Z" fill="{SKY}" opacity="0.8"/></g>
    <path d="M56 50 L144 50 L134 178 L66 178 Z" {LINE}/>
    <path id="{p}-drop" d="M100 0 Q112 18 100 26 Q88 18 100 0 Z" fill="{SKY}"/>'''
    t = [(f"#{p}-liq", "{y:70}", "{y:0,duration:0.8,ease:'power2.out'}", 0.2),
         (f"#{p}-liq", None, f"{{x:-20,duration:0.9,yoyo:true,repeat:{_reps(dur, 0.9)},ease:'sine.inOut'}}", 1.0),
         (f"#{p}-drop", "{y:-10,opacity:1}", f"{{y:90,opacity:0,duration:0.8,repeat:{_reps(dur, 1.0)},repeatDelay:0.2,ease:'power2.in'}}", 0.6)]
    return svg, t


def moon(p, dur):
    zs = "".join(f'<text class="{p}-z" x="{120 + i * 16}" y="{70 - i * 16}" font-family="Anek, sans-serif" font-weight="800" font-size="{34 + i * 8}" fill="{CREAM}">z</text>' for i in range(3))
    svg = f'''
    <path id="{p}-m" d="M110 40 A62 62 0 1 0 160 140 A50 50 0 1 1 110 40 Z" fill="{AMBER}"/>
    {zs}'''
    t = [(f"#{p}-m", "{rotation:-10,transformOrigin:'50% 50%'}", f"{{rotation:8,duration:1.6,yoyo:true,repeat:{_reps(dur, 1.6)},ease:'sine.inOut'}}", 0.3),
         (f".{p}-z", "{y:10,opacity:0}", f"{{y:-14,opacity:1,duration:0.9,stagger:0.3,yoyo:true,repeat:{_reps(dur, 0.9)},ease:'sine.inOut'}}", 0.4)]
    return svg, t


def car(p, dur):
    dashes = "".join(f'<rect class="{p}-r" x="{i * 50}" y="182" width="28" height="6" rx="3" fill="{CREAM}" opacity="0.6"/>' for i in range(6))
    svg = f'''
    {dashes}
    <g id="{p}-body">
      <path d="M30 140 L42 108 Q48 96 62 96 L128 96 Q142 96 150 108 L166 128 L176 132 Q182 134 182 142 L182 156 L30 156 Z" fill="{AMBER}"/>
      <path d="M62 104 L94 104 L94 126 L52 126 Z M102 104 L130 104 L146 126 L102 126 Z" fill="#2A1606" opacity="0.55"/>
    </g>
    <g id="{p}-w1"><circle cx="66" cy="158" r="17" fill="#2A1606" stroke="{CREAM}" stroke-width="5"/><path d="M66 146 L66 170 M54 158 L78 158" stroke="{CREAM}" stroke-width="3"/></g>
    <g id="{p}-w2"><circle cx="148" cy="158" r="17" fill="#2A1606" stroke="{CREAM}" stroke-width="5"/><path d="M148 146 L148 170 M136 158 L160 158" stroke="{CREAM}" stroke-width="3"/></g>'''
    t = [(f".{p}-r", "{x:0}", f"{{x:-100,duration:0.6,repeat:{_reps(dur, 0.6)},ease:'none'}}", 0.2),
         (f"#{p}-w1", "{rotation:0,svgOrigin:'66 158'}", f"{{rotation:-360,svgOrigin:'66 158',duration:0.6,repeat:{_reps(dur, 0.6)},ease:'none'}}", 0.2),
         (f"#{p}-w2", "{rotation:0,svgOrigin:'148 158'}", f"{{rotation:-360,svgOrigin:'148 158',duration:0.6,repeat:{_reps(dur, 0.6)},ease:'none'}}", 0.2),
         (f"#{p}-body", "{y:0}", f"{{y:-3,duration:0.15,yoyo:true,repeat:{_reps(dur, 0.15)},ease:'sine.inOut'}}", 0.2)]
    return svg, t


def pill(p, dur):
    svg = f'''
    <g id="{p}-g">
      <rect x="40" y="76" width="120" height="48" rx="24" fill="{CREAM}"/>
      <path d="M100 76 L136 76 Q160 76 160 100 Q160 124 136 124 L100 124 Z" fill="#FF4D4D"/>
      <rect x="40" y="76" width="120" height="48" rx="24" {LINE}/>
    </g>
    <path id="{p}-x" d="M150 140 L178 168 M178 140 L150 168" stroke="#FF4D4D" stroke-width="9" stroke-linecap="round"/>'''
    t = [(f"#{p}-g", "{rotation:-25,transformOrigin:'50% 50%'}", f"{{rotation:25,duration:1.2,yoyo:true,repeat:{_reps(dur, 1.2)},ease:'sine.inOut'}}", 0.3),
         (f"#{p}-x", "{scale:0,transformOrigin:'50% 50%'}", "{scale:1,duration:0.4,ease:'back.out(3)'}", 0.9)]
    return svg, t


def gavel(p, dur):
    svg = f'''
    <rect x="22" y="158" width="86" height="18" rx="6" fill="{AMBER}"/>
    <rect x="34" y="146" width="62" height="14" rx="5" fill="{AMBER}" opacity="0.7"/>
    <g id="{p}-g">
      <rect x="64" y="104" width="104" height="14" rx="7" fill="{CREAM}"/>
      <rect x="40" y="84" width="34" height="54" rx="8" fill="{AMBER}"/>
      <rect x="36" y="92" width="42" height="8" rx="3" fill="#2A1606" opacity="0.35"/>
    </g>'''
    t = [(f"#{p}-g", "{rotation:32,svgOrigin:'166 111'}", f"{{rotation:-8,svgOrigin:'166 111',duration:0.3,yoyo:true,repeat:{_reps(dur, 0.7) * 2 - 1},repeatDelay:0.4,ease:'power3.in'}}", 0.4)]
    return svg, t


def palm(p, dur):
    leaves = "".join(f'<path d="M100 70 Q{100 + dx} {50 + dy} {100 + dx * 2} {70 + dy * 2}" stroke="{MINT}" stroke-width="12" fill="none" stroke-linecap="round"/>'
                     for dx, dy in ((-34, -20), (34, -20), (-40, 4), (40, 4), (0, -30)))
    svg = f'''
    <path d="M100 178 Q92 130 100 70" stroke="{AMBER}" stroke-width="12" fill="none" stroke-linecap="round"/>
    <g id="{p}-top">{leaves}<circle cx="94" cy="78" r="7" fill="#8B5A2B"/><circle cx="108" cy="80" r="7" fill="#8B5A2B"/></g>'''
    t = [(f"#{p}-top", "{rotation:-8,svgOrigin:'100 70'}", f"{{rotation:8,svgOrigin:'100 70',duration:1.3,yoyo:true,repeat:{_reps(dur, 1.3)},ease:'sine.inOut'}}", 0.3)]
    return svg, t


def heart(p, dur):
    svg = f'''<path id="{p}-h" d="M100 172 Q36 128 36 82 Q36 48 68 48 Q90 48 100 70 Q110 48 132 48 Q164 48 164 82 Q164 128 100 172 Z" fill="#FF4D6D"/>
    <path d="M44 110 L76 110 L86 92 L100 130 L112 104 L156 104" stroke="{CREAM}" stroke-width="6" fill="none" stroke-linejoin="round"/>'''
    t = [(f"#{p}-h", "{scale:1,transformOrigin:'50% 60%'}", f"{{scale:1.1,duration:0.28,yoyo:true,repeat:{_reps(dur, 0.42) * 2 - 1},repeatDelay:0.15,ease:'power2.out'}}", 0.4)]
    return svg, t


def thermo(p, dur):
    svg = f'''
    <rect x="86" y="24" width="28" height="126" rx="14" {LINE}/>
    <circle cx="100" cy="160" r="24" fill="#FF4D4D"/>
    <rect id="{p}-m" x="93" y="40" width="14" height="112" rx="7" fill="#FF4D4D"/>
    <path id="{p}-a" d="M150 70 L150 130 M138 118 L150 132 L162 118" stroke="{SKY}" stroke-width="7" fill="none" stroke-linecap="round"/>'''
    t = [(f"#{p}-m", "{scaleY:1,transformOrigin:'50% 100%'}", "{scaleY:0.35,duration:1.4,ease:'power2.inOut'}", 0.6),
         (f"#{p}-a", "{y:-10,opacity:0}", f"{{y:10,opacity:1,duration:0.6,yoyo:true,repeat:{_reps(dur, 0.6)},ease:'sine.inOut'}}", 0.6)]
    return svg, t


def tree(p, dur):
    lights = "".join(f'<circle class="{p}-l" cx="{cx}" cy="{cy}" r="6" fill="{c}"/>' for cx, cy, c in
                     ((86, 92, AMBER), (116, 104, "#FF4D4D"), (78, 128, SKY), (112, 140, AMBER), (134, 150, "#FF4D4D"), (96, 154, SKY)))
    svg = f'''
    <path d="M100 30 L150 160 L50 160 Z" fill="{MINT}"/>
    <rect x="90" y="160" width="20" height="22" fill="#8B5A2B"/>
    <path id="{p}-star" d="M100 12 L106 26 L121 26 L109 35 L113 50 L100 41 L87 50 L91 35 L79 26 L94 26 Z" fill="{AMBER}"/>
    {lights}'''
    t = [(f".{p}-l", "{opacity:0.25}", f"{{opacity:1,duration:0.4,stagger:0.12,yoyo:true,repeat:{_reps(dur, 0.45)},ease:'none'}}", 0.3),
         (f"#{p}-star", "{rotation:0,svgOrigin:'100 32'}", f"{{rotation:360,svgOrigin:'100 32',duration:{max(dur - 0.5, 1):.2f},ease:'none'}}", 0.4)]
    return svg, t


def clock(p, dur):
    svg = f'''
    <circle cx="100" cy="104" r="70" {LINE}/>
    <circle cx="100" cy="104" r="6" fill="{AMBER}"/>
    <path d="M100 104 L100 70" stroke="{CREAM}" stroke-width="7" stroke-linecap="round"/>
    <path id="{p}-h" d="M100 104 L100 48" stroke="{AMBER}" stroke-width="5" stroke-linecap="round"/>
    <path d="M100 30 L100 40 M174 104 L164 104 M100 178 L100 168 M26 104 L36 104" {LINE}/>'''
    t = [(f"#{p}-h", "{rotation:0,svgOrigin:'100 104'}", f"{{rotation:360,svgOrigin:'100 104',duration:2,repeat:{_reps(dur, 2)},ease:'none'}}", 0.3)]
    return svg, t


def bolt(p, dur):
    svg = f'''<path id="{p}-b" d="M112 20 L56 112 L96 112 L84 180 L148 80 L106 80 Z" fill="{AMBER}"/>
    <path id="{p}-x" d="M30 30 L170 170" stroke="#FF4D4D" stroke-width="10" stroke-linecap="round" opacity="0.9"/>'''
    t = [(f"#{p}-b", "{opacity:1}", f"{{opacity:0.45,duration:0.12,yoyo:true,repeat:{_reps(dur, 0.6) * 2 - 1},repeatDelay:0.45,ease:'none'}}", 0.3),
         (f"#{p}-x", "{scaleX:0,transformOrigin:'0% 0%'}", "{scaleX:1,duration:0.4,ease:'power2.out'}", 1.0)]
    return svg, t


def question(p, dur):
    svg = f'''<circle cx="100" cy="100" r="78" fill="{AMBER}" opacity="0.18"/>
    <text id="{p}-q" x="100" y="138" text-anchor="middle" font-family="Anek, sans-serif" font-weight="800" font-size="120" fill="{AMBER}">?</text>'''
    t = [(f"#{p}-q", "{rotation:-10,transformOrigin:'50% 70%'}", f"{{rotation:10,duration:0.7,yoyo:true,repeat:{_reps(dur, 0.7)},ease:'sine.inOut'}}", 0.3)]
    return svg, t


ICONS = {"whisky": whisky, "beer": beer, "wine": wine, "cocktail": cocktail, "highball": highball,
         "coffee": coffee, "bottle": bottle, "shaker": shaker, "water": water, "moon": moon, "car": car,
         "pill": pill, "gavel": gavel, "palm": palm, "heart": heart, "thermo": thermo, "tree": tree,
         "clock": clock, "bolt": bolt, "question": question}
