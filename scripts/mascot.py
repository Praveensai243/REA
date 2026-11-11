"""Sippy — the Sipp Smart mascot (an original character: a little amber glass).

Lives in its own sub-composition for the whole video (bottom-left corner, next to the
card) and reacts to what's happening:
  think  (hook / questions)  — leans, eyes up, "?" bubble
  myth                        — head shake, frown, red ✗ bubble
  fact                        — nod, thumbs up, green ✓ bubble
  tip                         — points at the card, "!" bubble
  stir   (recipe lists)       — happy bounce, arms wave
  cheers (ending)             — raises a tiny glass, sparkles
"""

LEFT, TOP, W, H = 22, 1150, 250, 300

SVG = """
<svg id="mz" viewBox="0 0 200 240" width="250" height="300" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">
  <ellipse cx="100" cy="232" rx="58" ry="7" fill="#000" opacity="0.35"/>
  <g id="mz-body">
    <!-- legs -->
    <path d="M78 206 L74 226 M122 206 L126 226" stroke="#FFF7EC" stroke-width="7" stroke-linecap="round"/>
    <ellipse cx="70" cy="228" rx="12" ry="6" fill="#FFF7EC"/><ellipse cx="130" cy="228" rx="12" ry="6" fill="#FFF7EC"/>
    <!-- arms (behind the glass) -->
    <g id="mz-armL"><path d="M50 140 Q28 150 26 176" stroke="#FFF7EC" stroke-width="7" fill="none" stroke-linecap="round"/>
      <circle cx="26" cy="178" r="8" fill="#FFF7EC"/></g>
    <g id="mz-armR"><path d="M150 140 Q172 150 174 176" stroke="#FFF7EC" stroke-width="7" fill="none" stroke-linecap="round"/>
      <circle cx="174" cy="178" r="8" fill="#FFF7EC"/>
      <g id="mz-thumb" opacity="0"><rect x="170" y="160" width="8" height="16" rx="4" fill="#FFF7EC"/></g>
      <g id="mz-mini" opacity="0">
        <path d="M162 150 L186 150 L183 176 L165 176 Z" fill="#F5A623" stroke="#FFF7EC" stroke-width="3"/>
      </g></g>
    <!-- glass body -->
    <defs><clipPath id="mz-c"><path d="M44 62 L56 196 Q58 208 70 208 L130 208 Q142 208 144 196 L156 62 Z"/></clipPath></defs>
    <g clip-path="url(#mz-c)">
      <rect x="30" y="60" width="140" height="160" fill="#FFF7EC" opacity="0.12"/>
      <path id="mz-liq" d="M30 112 Q65 104 100 112 T170 112 L170 220 L30 220 Z" fill="#F5A623"/>
      <rect x="60" y="76" width="10" height="110" rx="5" fill="#FFF7EC" opacity="0.28"/>
    </g>
    <path d="M44 62 L56 196 Q58 208 70 208 L130 208 Q142 208 144 196 L156 62" stroke="#FFF7EC" stroke-width="6" fill="none" stroke-linejoin="round"/>
    <!-- face -->
    <g id="mz-eyes">
      <ellipse cx="82" cy="142" rx="15" ry="17" fill="#FFF7EC"/><ellipse cx="120" cy="142" rx="15" ry="17" fill="#FFF7EC"/>
      <g id="mz-pupils"><circle cx="84" cy="145" r="8" fill="#1A0F1F"/><circle cx="122" cy="145" r="8" fill="#1A0F1F"/>
        <circle cx="87" cy="141" r="2.6" fill="#FFF7EC"/><circle cx="125" cy="141" r="2.6" fill="#FFF7EC"/></g>
      <rect id="mz-lid" x="64" y="120" width="74" height="0" fill="#F5A623"/>
    </g>
    <circle cx="68" cy="168" r="6" fill="#FF7A6B" opacity="0.6"/><circle cx="134" cy="168" r="6" fill="#FF7A6B" opacity="0.6"/>
    <path id="mz-smile" d="M88 170 Q101 182 114 170" stroke="#1A0F1F" stroke-width="5" fill="none" stroke-linecap="round"/>
    <path id="mz-frown" d="M88 178 Q101 168 114 178" stroke="#1A0F1F" stroke-width="5" fill="none" stroke-linecap="round" opacity="0"/>
    <!-- lime wheel hat + straw -->
    <path d="M128 70 L150 18" stroke="#FF7A6B" stroke-width="7" stroke-linecap="round"/>
    <g id="mz-lime"><circle cx="60" cy="60" r="20" fill="#3DDC84"/><circle cx="60" cy="60" r="14" fill="#C8F7A6"/>
      <path d="M60 46 L60 74 M46 60 L74 60 M50 50 L70 70 M50 70 L70 50" stroke="#3DDC84" stroke-width="2.5"/></g>
  </g>
  <!-- bubbles -->
  <g id="mz-bq" opacity="0"><circle cx="168" cy="38" r="26" fill="#FFF7EC"/>
    <path d="M159 30 Q160 20 169 20 Q178 20 178 29 Q178 36 169 39 L169 46" stroke="#1A0F1F" stroke-width="5" fill="none" stroke-linecap="round"/>
    <circle cx="169" cy="54" r="3.2" fill="#1A0F1F"/></g>
  <g id="mz-bx" opacity="0"><circle cx="168" cy="38" r="26" fill="#FF4D4D"/>
    <path d="M157 27 L179 49 M179 27 L157 49" stroke="#FFF7EC" stroke-width="6" stroke-linecap="round"/></g>
  <g id="mz-bc" opacity="0"><circle cx="168" cy="38" r="26" fill="#3DDC84"/>
    <path d="M155 39 L165 49 L182 28" stroke="#FFF7EC" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>
  <g id="mz-be" opacity="0"><circle cx="168" cy="38" r="26" fill="#F5A623"/>
    <path d="M168 24 L168 42" stroke="#1A0F1F" stroke-width="6" stroke-linecap="round"/><circle cx="168" cy="52" r="3.6" fill="#1A0F1F"/></g>
  <g id="mz-sp" opacity="0" fill="#F5A623">
    <path d="M190 120 l4 10 l10 4 l-10 4 l-4 10 l-4 -10 l-10 -4 l10 -4 Z"/>
    <path d="M160 100 l3 7 l7 3 l-7 3 l-3 7 l-3 -7 l-7 -3 l7 -3 Z"/></g>
</svg>
"""


def _bubble(bid, at, hold=1.4):
    return [(f"#{bid}", "{opacity:0,scale:0,transformOrigin:'50% 100%'}",
             "{opacity:1,scale:1,duration:0.3,ease:'back.out(2.5)'}", round(at, 2)),
            (f"#{bid}", None, "{opacity:0,scale:0.6,duration:0.2,ease:'power1.in'}", round(at + hold, 2))]


def mascot_doc(events, total, scene_doc):
    """events: list of (time, pose). Returns the sub-composition html."""
    tw = [("#mz", "{opacity:1,y:0}", "{opacity:1,y:0,duration:0.01}", 0)]
    # idle: gentle bob + liquid slosh + blinks for the whole film
    tw.append(("#mz-body", "{y:0}", f"{{y:-6,duration:0.8,yoyo:true,repeat:{max(1, int(total / 0.8))},ease:'sine.inOut'}}", 0))
    tw.append(("#mz-liq", "{x:-8}", f"{{x:8,duration:1.1,yoyo:true,repeat:{max(1, int(total / 1.1))},ease:'sine.inOut'}}", 0))
    tw.append(("#mz-lid", "{attr:{height:0}}", "{attr:{height:0},duration:0.01}", 0))   # baseline: eyes open
    t = 1.6
    while t < total - 0.3:
        tw.append(("#mz-lid", None, "{attr:{height:46},duration:0.07,yoyo:true,repeat:1,ease:'none'}", round(t, 2)))
        t += 3.1 if int(t) % 2 else 2.4
    for at, pose in events:
        at = round(at, 2)
        if pose == "think":
            tw += [("#mz-body", None, "{rotation:-7,svgOrigin:'100 220',duration:0.35,yoyo:true,repeat:1,ease:'sine.inOut'}", at),
                   ("#mz-pupils", None, "{x:4,y:-7,duration:0.25,yoyo:true,repeat:1,repeatDelay:0.9}", at)]
            tw += _bubble("mz-bq", at + 0.1)
        elif pose == "myth":
            tw += [("#mz-body", None, "{keyframes:[{rotation:-9,duration:0.1},{rotation:9,duration:0.12},{rotation:-7,duration:0.12},{rotation:6,duration:0.12},{rotation:0,duration:0.1}],svgOrigin:'100 220'}", at),
                   ("#mz-smile", None, "{opacity:0,duration:0.1,yoyo:true,repeat:1,repeatDelay:1.2}", at),
                   ("#mz-frown", None, "{opacity:1,duration:0.1,yoyo:true,repeat:1,repeatDelay:1.2}", at)]
            tw += _bubble("mz-bx", at + 0.05)
        elif pose == "fact":
            tw += [("#mz-body", None, "{keyframes:[{y:8,duration:0.12},{y:-4,duration:0.14},{y:6,duration:0.12},{y:0,duration:0.14}]}", at),
                   ("#mz-armR", None, "{rotation:-120,svgOrigin:'150 140',duration:0.25,yoyo:true,repeat:1,repeatDelay:1.1,ease:'back.out(2)'}", at),
                   ("#mz-thumb", None, "{opacity:1,duration:0.1,yoyo:true,repeat:1,repeatDelay:1.3}", at + 0.1)]
            tw += _bubble("mz-bc", at + 0.05)
        elif pose == "tip":
            tw += [("#mz-armR", None, "{rotation:-75,svgOrigin:'150 140',duration:0.25,yoyo:true,repeat:1,repeatDelay:1.2,ease:'back.out(2)'}", at),
                   ("#mz-body", None, "{rotation:4,svgOrigin:'100 220',duration:0.25,yoyo:true,repeat:1,repeatDelay:1.2}", at)]
            tw += _bubble("mz-be", at + 0.05)
        elif pose == "stir":
            tw += [("#mz-armL", None, "{rotation:35,svgOrigin:'50 140',duration:0.22,yoyo:true,repeat:5,ease:'sine.inOut'}", at),
                   ("#mz-armR", None, "{rotation:-35,svgOrigin:'150 140',duration:0.22,yoyo:true,repeat:5,ease:'sine.inOut'}", at),
                   ("#mz-lime", None, "{rotation:360,svgOrigin:'60 60',duration:1.2,ease:'power1.inOut'}", at)]
        elif pose == "cheers":
            tw += [("#mz-mini", None, "{opacity:1,duration:0.15}", at),
                   ("#mz-armR", None, "{rotation:-140,svgOrigin:'150 140',duration:0.35,ease:'back.out(1.8)'}", at),
                   ("#mz-armR", None, "{rotation:-125,svgOrigin:'150 140',duration:0.3,yoyo:true,repeat:5,ease:'sine.inOut'}", at + 0.4),
                   ("#mz-sp", None, "{opacity:1,scale:1.2,transformOrigin:'50% 50%',duration:0.3,yoyo:true,repeat:3}", at + 0.35)]
        elif pose == "wave":
            tw += [("#mz-armR", None, "{rotation:-150,svgOrigin:'150 140',duration:0.25,ease:'power2.out'}", at),
                   ("#mz-armR", None, "{rotation:-120,svgOrigin:'150 140',duration:0.18,yoyo:true,repeat:3,ease:'sine.inOut'}", at + 0.25),
                   ("#mz-armR", None, "{rotation:0,svgOrigin:'150 140',duration:0.3,ease:'power2.inOut'}", at + 1.0)]
    body = (f'<div style="position:absolute;left:{LEFT}px;top:{TOP}px;width:{W}px;height:{H}px">{SVG}</div>')
    return scene_doc("mascot", total, body, tw)


def pose_for(scene, index, is_last):
    if is_last:
        return "cheers"
    if scene.get("stamp") == "MYTH":
        return "myth"
    if scene.get("stamp") == "FACT":
        return "fact"
    if scene.get("stamp") == "TIP":
        return "tip"
    if scene.get("list"):
        return "stir"
    if index == 0 or "?" in scene.get("m", "") or "?" in scene.get("v", ""):
        return "think"
    return "wave" if index == 1 else None
