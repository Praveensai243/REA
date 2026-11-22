"""Pixel-art host: a cartoon of Sai, drawn with code (no photos).

The outfit changes by date (8 outfits, rotating). Poses are separate PNG frames
swapped on the timeline: chin (thinking), point (at the card), cheers (raises a
glass at the end), plus blink frames. A small mouth overlay flaps while the
voice talks.
"""
import copy
import datetime as dt

from PIL import Image

GW, GH = 40, 80            # pixel grid
SCALE = 7                  # each pixel -> 7x7 on screen (280 x 560)
LEFT, TOP = 750, 990       # where the character stands on the 1080x1920 frame

BASE = dict(H=(38, 31, 28), h=(70, 58, 50), g=(120, 114, 108), S=(168, 107, 69), s=(138, 84, 52),
            L=(190, 128, 88), B=(36, 28, 25), b=(112, 104, 98), M=(92, 46, 34), X=(245, 243, 238),
            E=(30, 22, 20), K=(17, 17, 17), A=(230, 150, 40), a=(250, 214, 120), Q=(214, 236, 244))

OUTFITS = [
    dict(T=(20, 20, 20), t=(48, 48, 48), J=(52, 96, 160), j=(38, 74, 128), l=(84, 126, 186), Wh=(242, 242, 240), w=(200, 200, 198), R=(150, 150, 148)),
    dict(T=(236, 234, 228), t=(205, 202, 195), J=(40, 40, 44), j=(26, 26, 30), l=(70, 70, 76), Wh=(242, 242, 240), w=(200, 200, 198), R=(150, 150, 148)),
    dict(T=(88, 98, 58), t=(70, 79, 45), J=(196, 170, 124), j=(170, 144, 100), l=(214, 192, 150), Wh=(242, 242, 240), w=(200, 200, 198), R=(150, 150, 148)),
    dict(T=(122, 32, 44), t=(98, 24, 34), J=(112, 116, 124), j=(88, 92, 100), l=(140, 144, 152), Wh=(30, 30, 30), w=(60, 60, 60), R=(230, 230, 230)),
    dict(T=(30, 44, 84), t=(22, 33, 64), J=(122, 160, 206), j=(96, 134, 182), l=(150, 186, 226), Wh=(242, 242, 240), w=(200, 200, 198), R=(150, 150, 148)),
    dict(T=(214, 164, 48), t=(186, 138, 32), J=(40, 40, 44), j=(26, 26, 30), l=(70, 70, 76), Wh=(242, 242, 240), w=(200, 200, 198), R=(150, 150, 148)),
    dict(T=(28, 122, 122), t=(20, 98, 98), J=(34, 58, 98), j=(24, 44, 78), l=(56, 84, 128), Wh=(206, 48, 48), w=(170, 34, 34), R=(240, 240, 240)),
    dict(T=(244, 242, 236), t=(214, 210, 202), J=(214, 196, 166), j=(190, 170, 140), l=(230, 216, 190), Wh=(110, 72, 46), w=(86, 56, 36), R=(60, 40, 26)),
]
POSES = ("chin", "point", "cheers")


def outfit_for(day):
    return OUTFITS[dt.date.fromisoformat(str(day)).toordinal() % len(OUTFITS)]


def draw(pose="chin", blink=False, outfit=None):
    C = copy.deepcopy(BASE)
    C.update(outfit or OUTFITS[0])
    g = [[None] * GW for _ in range(GH)]

    def p(x, y, c):
        if 0 <= x < GW and 0 <= y < GH:
            g[y][x] = c

    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                p(x, y, c)

    def circ(cx, cy, r, c, ry=None):
        ry = ry or r
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                if ((x - cx) / r) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    p(x, y, c)

    def limb(pts, c="S", shade="s"):
        for x, y in pts:
            rect(x - 1, y - 1, x + 1, y + 1, c)
            p(x + 1, y, shade)

    # jeans
    rect(11, 52, 29, 73, "J")
    for y in range(58, 74):
        for x in (19, 20, 21):
            p(x, y, None)
    rect(11, 52, 29, 53, "j"); rect(18, 52, 18, 57, "j")
    rect(13, 55, 13, 69, "l"); rect(26, 55, 26, 69, "l")
    rect(11, 70, 18, 73, "j"); rect(22, 70, 29, 73, "j")
    # shoes
    rect(9, 74, 18, 77, "Wh"); rect(22, 74, 31, 77, "Wh"); rect(9, 78, 18, 78, "R"); rect(22, 78, 31, 78, "R")
    rect(11, 75, 13, 75, "w"); rect(27, 75, 29, 75, "w")
    # t-shirt
    rect(11, 33, 29, 52, "T"); circ(11, 35, 3, "T"); circ(29, 35, 3, "T")
    rect(7, 34, 11, 41, "T"); rect(29, 34, 33, 41, "T")
    rect(28, 37, 29, 51, "t")
    # left arm (viewer's left)
    if pose == "point":   # raised, pointing up-left at the card
        limb([(8, 40), (7, 38), (6, 36), (5, 34), (4, 32), (3, 30)])
        rect(1, 26, 4, 29, "S"); rect(0, 25, 1, 26, "S"); p(4, 29, "s")
        rect(6, 34, 10, 38, "T")
    else:
        rect(8, 42, 10, 55, "S"); rect(8, 42, 8, 55, "s"); rect(7, 55, 11, 58, "S"); rect(7, 58, 11, 58, "s")
    # neck
    rect(17, 29, 23, 33, "s"); rect(16, 33, 24, 33, "t")
    # hair
    circ(20, 11, 9, "H", 7)
    for cx, cy, r in [(14, 6, 3), (18, 4, 3), (23, 4, 3), (27, 6, 3), (12, 9, 2), (29, 10, 2)]:
        circ(cx, cy, r, "H")
    for x0, y0 in [(14, 5), (19, 3), (24, 4), (16, 8), (22, 7), (26, 8), (12, 10)]:
        p(x0, y0, "h"); p(x0 + 1, y0 - 1, "h"); p(x0 + 2, y0 - 1, "h")
    for x, y in [(12, 13), (28, 13), (12, 14)]:
        p(x, y, "g")
    # face
    rect(13, 12, 27, 27, "S"); rect(12, 14, 28, 22, "S")
    rect(11, 16, 11, 20, "s"); rect(29, 16, 29, 20, "s")
    rect(12, 12, 12, 17, "H"); rect(28, 12, 28, 17, "H")
    rect(13, 11, 27, 12, "H"); p(13, 13, "H"); p(27, 13, "H")
    rect(14, 16, 18, 16, "H"); rect(22, 16, 26, 16, "H")          # eyebrows
    if blink:
        rect(15, 18, 17, 18, "s"); rect(23, 18, 25, 18, "s")
    else:
        rect(15, 18, 17, 18, "X"); rect(23, 18, 25, 18, "X"); p(16, 18, "E"); p(24, 18, "E")
    rect(20, 19, 20, 22, "s"); p(19, 22, "s"); p(21, 22, "s")
    # beard
    for y in range(21, 31):
        half = {21: 8, 22: 8, 23: 8, 24: 8, 25: 8, 26: 7, 27: 7, 28: 6, 29: 5, 30: 3}[y]
        for x in range(20 - half, 20 + half + 1):
            if y < 23 and 15 <= x <= 25:
                continue
            p(x, y, "B")
    rect(16, 23, 24, 23, "B"); rect(18, 25, 22, 25, "M"); rect(18, 24, 22, 24, "L")
    for x, y in [(17, 28), (22, 27), (14, 23), (26, 23)]:
        p(x, y, "b")
    # right arm (viewer's right)
    if pose == "chin":
        limb([(32, 42), (31, 40), (30, 38), (29, 36), (28, 34), (27, 32)])
        rect(30, 34, 34, 38, "T")
        rect(23, 28, 27, 31, "S"); rect(23, 31, 27, 31, "s"); p(24, 28, "L"); p(26, 28, "L")
    elif pose == "cheers":   # glass raised high
        limb([(33, 40), (34, 38), (35, 36), (35, 34), (35, 32), (35, 30), (35, 28)])
        rect(30, 34, 34, 38, "T")
        rect(33, 24, 37, 27, "S")
        rect(33, 15, 38, 23, "Q"); rect(34, 18, 37, 23, "A"); rect(34, 18, 37, 18, "a")   # whisky glass
    else:
        rect(30, 42, 32, 55, "S"); rect(32, 42, 32, 55, "s"); rect(29, 55, 33, 58, "S"); rect(29, 58, 33, 58, "s")
    # outline
    out = [r[:] for r in g]
    for y in range(GH):
        for x in range(GW):
            if g[y][x] is None and any(0 <= x + dx < GW and 0 <= y + dy < GH and g[y + dy][x + dx]
                                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = "K"
    im = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
    for y in range(GH):
        for x in range(GW):
            if out[y][x]:
                im.putpixel((x, y), C[out[y][x]] + (255,))
    return im.resize((GW * SCALE, GH * SCALE), Image.NEAREST)


def write_frames(day, assets):
    """Writes assets/me_<pose>[_blink].png for this date's outfit."""
    o = outfit_for(day)
    for pose in POSES:
        for blink in (False, True):
            draw(pose, blink, o).save(assets / f"me_{pose}{'_blink' if blink else ''}.png")


def me_doc(pose_events, talk_spans, total, scene_doc):
    """pose_events: [(time, pose)] (pose holds until the next one).
    talk_spans: [(start, length)] when the voice is speaking."""
    imgs, tw = [], []
    frames = [f"{p}{b}" for p in POSES for b in ("", "_blink")]
    for f in frames:
        imgs.append(f'<img id="me-{f}" src="assets/me_{f}.png" style="position:absolute;left:0;top:0;'
                    f'width:{GW * SCALE}px;height:{GH * SCALE}px;opacity:0" alt="">')
    # one image visible at a time: build a list of (time, frame) switches
    pose_events = sorted([(0.0, "chin")] + [(round(t, 2), p) for t, p in pose_events if p in POSES])
    switches = []
    for i, (t, p) in enumerate(pose_events):
        end = pose_events[i + 1][0] if i + 1 < len(pose_events) else total
        switches.append((t, p))
        b = t + 1.3
        while b < end - 0.3:            # blink while holding this pose
            switches.append((round(b, 2), p + "_blink"))
            switches.append((round(b + 0.12, 2), p))
            b += 2.7
    switches.sort()
    for f in frames:
        tw.append((f"#me-{f}", "{opacity:0}", "{opacity:0,duration:0.01}", 0))
    shown = None
    for t, f in switches:
        if shown:
            tw.append((f"#me-{shown}", None, "{opacity:0,duration:0.01}", t))
        tw.append((f"#me-{f}", None, "{opacity:1,duration:0.01}", t))
        shown = f
    # talking mouth: a dark pixel block that opens and closes
    mx, my = 18 * SCALE, 24 * SCALE
    imgs.append(f'<div id="me-mouth" style="position:absolute;left:{mx}px;top:{my}px;width:{5 * SCALE}px;'
                f'height:{2 * SCALE}px;background:#5C2E22;border-top:{SCALE}px solid #3A1A12;opacity:0"></div>')
    tw.append(("#me-mouth", "{opacity:0}", "{opacity:0,duration:0.01}", 0))
    for start, length in talk_spans:
        n = max(1, int(length / 0.26))
        tw.append(("#me-mouth", None, f"{{opacity:1,duration:0.06,yoyo:true,repeat:{2 * n - 1},repeatDelay:0.07,ease:'none'}}",
                   round(start, 2)))
    # whole body: pops in, then breathes gently
    tw.append(("#me", "{y:40,opacity:0}", "{y:0,opacity:1,duration:0.4,ease:'back.out(1.6)'}", 0.1))
    tw.append(("#me", None, f"{{y:-6,duration:0.9,yoyo:true,repeat:{max(1, int(total / 0.9) - 1)},ease:'sine.inOut'}}", 0.5))
    body = (f'<div id="me" style="position:absolute;left:{LEFT}px;top:{TOP}px;width:{GW * SCALE}px;height:{GH * SCALE}px">'
            f'<div style="position:absolute;left:30px;right:30px;bottom:-14px;height:22px;border-radius:50%;'
            f'background:rgba(0,0,0,0.10)"></div>{"".join(imgs)}</div>')
    return scene_doc("me", total, body, tw)


def pose_for(scene, index, is_last):
    if is_last:
        return "cheers"
    if scene.get("stamp") or scene.get("list"):
        return "point"
    return "chin"
