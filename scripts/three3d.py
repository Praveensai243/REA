"""3D explainer scenes (Three.js, bundled in template/assets/lib/three.min.js).

Everything is drawn from the scene's local time, so HyperFrames can seek any frame:
a GSAP tween on a hidden clock element calls window.R3_<sid>(t) on every update.

Scenes
  hero  : one glass/bottle (whisky, beer, wine, cocktail, highball, bottle, water)
          drops in, a pour stream fills it, camera orbits slowly
  three : 30ml whisky / 250ml beer / 100ml wine side by side, filling one by one,
          with labels and a "≈ 10g alcohol" chip under each
"""
import json

HERO = {"whisky", "beer", "wine", "cocktail", "highball", "bottle", "water", "shaker"}
CANVAS_TOP, CANVAS_H = 470, 720

JS = r"""
(function(){
const C = __CFG__;
const W = 1080, H = __CH__;
const cv = document.getElementById(C.id + '-cv');
const R = new THREE.WebGLRenderer({canvas: cv, antialias: true, alpha: true, preserveDrawingBuffer: true});
R.setPixelRatio(1); R.setSize(W, H, false); R.localClippingEnabled = true;
R.outputColorSpace = THREE.SRGBColorSpace; R.toneMapping = THREE.ACESFilmicToneMapping; R.toneMappingExposure = 1.15;
const S = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 100);
S.add(new THREE.HemisphereLight(0xfff1dc, 0x1a120c, 1.1));
const key = new THREE.DirectionalLight(0xffffff, 2.6); key.position.set(3, 6, 5); S.add(key);
const rim = new THREE.PointLight(0xffa640, 40, 30); rim.position.set(-4, 3, -3); S.add(rim);
const rim2 = new THREE.PointLight(0x9fd0ff, 18, 30); rim2.position.set(4, 2, -4); S.add(rim2);

function radialTex(inner, outer){
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const g = c.getContext('2d'); const gr = g.createRadialGradient(128,128,0,128,128,128);
  gr.addColorStop(0, inner); gr.addColorStop(1, outer); g.fillStyle = gr; g.fillRect(0,0,256,256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
// floor: warm wooden-ish disc fading out
const floor = new THREE.Mesh(new THREE.CircleGeometry(6, 64),
  new THREE.MeshBasicMaterial({map: radialTex('rgba(110,68,34,0.8)', 'rgba(20,12,8,0)'), transparent: true}));
floor.rotation.x = -Math.PI / 2; S.add(floor);
const shadowTex = radialTex('rgba(0,0,0,0.55)', 'rgba(0,0,0,0)');

const P = {   // outer profiles [radius, height]; liquid starts at base, ends at top
  whisky:  {pts: [[0,0],[1.05,0],[1.1,0.06],[1.12,1.55]], base: 0.32, top: 1.5, liq: 0xd7801e, fill: 0.55},
  beer:    {pts: [[0,0],[0.78,0],[0.82,0.12],[1.0,2.5],[1.04,2.75]], base: 0.22, top: 2.7, liq: 0xf2b21b, fill: 0.86, foam: true},
  wine:    {pts: [[0,0],[0.72,0],[0.72,0.05],[0.1,0.12],[0.08,1.25],[0.35,1.38],[0.82,1.85],[0.86,2.35],[0.72,2.85]], base: 1.36, top: 2.8, liq: 0x8c1730, fill: 0.5},
  highball:{pts: [[0,0],[0.74,0],[0.76,0.1],[0.8,2.7]], base: 0.2, top: 2.65, liq: 0x6a2c12, fill: 0.85, straw: true, lime: true, ice: 3},
  cocktail:{pts: [[0,0],[0.74,0],[0.76,0.1],[0.8,2.7]], base: 0.2, top: 2.65, liq: 0xe46a2e, fill: 0.85, straw: true, lime: true, ice: 3},
  water:   {pts: [[0,0],[0.85,0],[0.88,0.08],[0.95,2.2]], base: 0.18, top: 2.15, liq: 0x9fd8ff, fill: 0.8},
  bottle:  {pts: [[0,0],[0.62,0],[0.66,0.05],[0.66,1.9],[0.58,2.15],[0.22,2.55],[0.2,3.05],[0.24,3.12],[0.24,3.3]], base: 0.08, top: 2.0, liq: 0xb8661c, fill: 0.9, amber: true},
};
P.shaker = P.highball;

function interpR(pts, y){
  for (let i = 1; i < pts.length; i++){
    const [r0,y0] = pts[i-1], [r1,y1] = pts[i];
    if (y >= y0 && y <= y1) return r0 + (r1 - r0) * ((y - y0) / Math.max(1e-6, y1 - y0));
  }
  return pts[pts.length-1][0];
}
const glassMat = new THREE.MeshPhysicalMaterial({color: 0xffffff, transparent: true, opacity: 0.2, roughness: 0.04,
  metalness: 0.0, clearcoat: 1, clearcoatRoughness: 0.03, side: THREE.DoubleSide, depthWrite: false});
const amberMat = new THREE.MeshPhysicalMaterial({color: 0x7a3d0c, transparent: true, opacity: 0.55, roughness: 0.08,
  clearcoat: 1, side: THREE.DoubleSide, depthWrite: false});

function makeVessel(kind){
  const p = P[kind] || P.whisky, g = new THREE.Group();
  const outer = p.pts.map(([r,y]) => new THREE.Vector2(r, y));
  const glass = new THREE.Mesh(new THREE.LatheGeometry(outer, 64), p.amber ? amberMat : glassMat);
  glass.renderOrder = 3; g.add(glass);
  // liquid: the inside of the glass, clipped at the fill level
  const inner = [];
  const ys = p.pts.map(q => q[1]).filter(y => y >= p.base);
  [p.base].concat(ys).forEach(y => inner.push(new THREE.Vector2(Math.max(0.001, interpR(p.pts, y) * 0.9), y)));
  inner.unshift(new THREE.Vector2(0, p.base));
  const plane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);
  const lm = new THREE.MeshPhysicalMaterial({color: p.liq, transparent: true, opacity: 0.88, roughness: 0.15,
    clearcoat: 1, clippingPlanes: [plane], side: THREE.DoubleSide});
  const liquid = new THREE.Mesh(new THREE.LatheGeometry(inner, 64), lm); liquid.renderOrder = 1; g.add(liquid);
  const surf = new THREE.Mesh(new THREE.CircleGeometry(1, 48), new THREE.MeshPhysicalMaterial({color: p.liq,
    roughness: 0.1, clearcoat: 1, transparent: true, opacity: 0.95}));
  surf.rotation.x = -Math.PI / 2; surf.renderOrder = 2; g.add(surf);
  let foam = null;
  if (p.foam){ foam = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 0.22, 48),
      new THREE.MeshStandardMaterial({color: 0xfffaf0, roughness: 0.9})); g.add(foam); }
  const ices = [];
  for (let i = 0; i < (p.ice || (kind === 'whisky' ? 2 : 0)); i++){
    const s = kind === 'whisky' ? 0.62 : 0.5;
    const m = new THREE.Mesh(new THREE.BoxGeometry(s, s, s), new THREE.MeshPhysicalMaterial({color: 0xeaf6ff,
      transparent: true, opacity: 0.55, roughness: 0.08, clearcoat: 1}));
    m.userData.ph = i * 1.9; ices.push(m); g.add(m);
  }
  if (p.straw){
    const st = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 3.2, 12), new THREE.MeshStandardMaterial({color: 0xf4f4f4}));
    st.position.set(0.3, 1.9, 0.1); st.rotation.z = -0.22; g.add(st);
  }
  if (p.lime){
    const lime = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 0.12, 32), new THREE.MeshStandardMaterial({color: 0x7ec23a, roughness: 0.6}));
    lime.position.set(-0.75, p.top + 0.05, 0); lime.rotation.z = Math.PI / 2.4; g.add(lime);
  }
  if (p.amber){
    const lab = new THREE.Mesh(new THREE.CylinderGeometry(0.67, 0.67, 0.8, 48, 1, true),
      new THREE.MeshStandardMaterial({color: 0xf3e3c3, roughness: 0.7, side: THREE.DoubleSide}));
    lab.position.y = 1.0; g.add(lab);
  }
  const sh = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 3.4), new THREE.MeshBasicMaterial({map: shadowTex, transparent: true, depthWrite: false}));
  sh.rotation.x = -Math.PI / 2; sh.position.y = 0.01; g.add(sh);
  const stream = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.05, 1, 12), new THREE.MeshPhysicalMaterial({color: p.liq,
    transparent: true, opacity: 0.85, roughness: 0.1}));
  g.add(stream);
  const bubbles = [];
  if (kind === 'beer' || kind === 'cocktail' || kind === 'highball'){
    for (let i = 0; i < 14; i++){
      const b = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 8), new THREE.MeshBasicMaterial({color: 0xffffff, transparent: true, opacity: 0.7}));
      b.userData = {a: i * 2.39996, r: 0.15 + (i * 37 % 10) / 20, sp: 0.5 + (i * 13 % 7) / 10, off: (i * 0.31) % 1}; bubbles.push(b); g.add(b);
    }
  }
  return {g, p, plane, liquid, surf, foam, ices, stream, bubbles};
}
const ease = x => x < 0 ? 0 : x > 1 ? 1 : x * x * (3 - 2 * x);
const back = x => { x = Math.min(1, Math.max(0, x)); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };

function setFill(v, frac, t){   // frac 0..1 of the planned fill
  const p = v.p, lvl = p.base + (p.top - p.base) * p.fill * frac;
  const wy = v.g.position.y;
  v.plane.constant = wy + lvl;
  v.surf.visible = frac > 0.01;
  const r = interpR(p.pts, lvl) * 0.9;
  v.surf.position.y = lvl; v.surf.scale.set(r, r, 1);
  if (v.foam){ v.foam.visible = frac > 0.5; v.foam.position.y = lvl + 0.1; v.foam.scale.set(r, Math.min(1, (frac - 0.5) * 2), r); }
  v.ices.forEach((m, i) => { m.visible = frac > 0.15; const bob = Math.sin(t * 2.2 + m.userData.ph) * 0.04;
    m.position.set((i - 0.5) * 0.45, Math.max(p.base + 0.3, lvl - 0.18) + bob + (i % 2) * 0.12, (i % 2 ? 0.2 : -0.2));
    m.rotation.set(0.3 + i, t * 0.4 + i, 0.2); });
  v.bubbles.forEach(b => { const u = b.userData, k = ((t * u.sp + u.off) % 1);
    b.visible = frac > 0.2; const y = p.base + k * (lvl - p.base);
    b.position.set(Math.cos(u.a) * u.r, y, Math.sin(u.a) * u.r); });
}
function setStream(v, on, frac){
  const p = v.p, lvl = p.base + (p.top - p.base) * p.fill * frac, top = p.top + 2.2;
  v.stream.visible = on; const len = top - lvl;
  v.stream.scale.set(1, Math.max(0.01, len), 1); v.stream.position.set(0, lvl + len / 2, 0);
}

const items = [], labels = [];
if (C.mode === 'three'){
  ['whisky', 'beer', 'wine'].forEach((k, i) => { const v = makeVessel(k); v.g.position.x = (i - 1) * 3.4; S.add(v.g); items.push(v); });
} else {
  const v = makeVessel(C.kind); v.g.scale.setScalar(1.0); S.add(v.g); items.push(v);
}
(C.labels || []).forEach((txt, i) => labels.push([document.getElementById(C.id + '-lb' + i), i]));

window['R3_' + C.id] = function(t){
  const d = C.dur;
  // camera: slow orbit + gentle push in
  const a = C.mode === 'three' ? -0.28 + 0.56 * (t / d) : -0.42 + 0.84 * (t / d);
  const rad = (C.mode === 'three' ? 15.5 : 11) - 1.2 * ease(t / d);
  const cy = C.mode === 'three' ? 3.2 : 3.0;
  cam.position.set(Math.sin(a) * rad, cy + 1.6, Math.cos(a) * rad);
  cam.lookAt(0, C.mode === 'three' ? 1.0 : 1.5, 0);
  items.forEach((v, i) => {
    const t0 = 0.1 + i * 0.18, e = back((t - t0) / 0.55);
    const s = (C.mode === 'three' ? 1 : 1.0) * (0.55 + 0.45 * e);
    v.g.scale.setScalar(Math.max(0.001, s)); v.g.position.y = (1 - ease((t - t0) / 0.5)) * 2.2;
    if (C.mode !== 'three') v.g.rotation.y = t * 0.35;
    const f0 = C.fills[i], f1 = f0 + C.fillDur;
    const frac = ease((t - f0) / (f1 - f0));
    setFill(v, frac, t);
    setStream(v, t > f0 - 0.05 && t < f1 + 0.05, frac);
  });
  R.render(S, cam);
  labels.forEach(([el, i]) => {
    if (!el) return;
    const v = items[i]; const pos = new THREE.Vector3(v.g.position.x, -0.35, 0).project(cam);
    el.style.left = ((pos.x + 1) / 2 * W) + 'px'; el.style.top = ((1 - pos.y) / 2 * H) + 'px';
    el.style.opacity = t > C.fills[i] + 0.2 ? 1 : 0;
  });
};
window['R3_' + C.id](0);
})();
"""


def scene(sid, mode, dur, kind="whisky", fills=None, fill_dur=1.4, labels=None, chips=None):
    """Returns (html, tweens). html = canvas + labels + the setup script."""
    labels = labels or []
    cfg = {"id": sid, "mode": mode, "kind": kind, "dur": dur, "fills": fills or [0.8], "fillDur": fill_dur,
           "labels": labels}
    lab_html = "".join(
        f'<div id="{sid}-lb{i}" style="position:absolute;transform:translate(-50%,0);text-align:center;opacity:0;'
        f'color:#FFF;font-weight:800;font-size:30px;white-space:nowrap;text-shadow:0 3px 14px rgba(0,0,0,0.7)">{txt}'
        + (f'<br><div style="margin-top:8px;display:inline-block;padding:4px 14px;border-radius:30px;background:#2FA84F;'
           f'font-size:24px">{chips[i]}</div>' if chips else "") + '</div>'
        for i, txt in enumerate(labels))
    html = (f'<div style="position:absolute;left:0;top:{CANVAS_TOP}px;width:1080px;height:{CANVAS_H}px;'
            f'-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 8%,#000 82%,transparent 100%);'
            f'mask-image:linear-gradient(180deg,transparent 0,#000 8%,#000 82%,transparent 100%)">'
            f'<canvas id="{sid}-cv" width="1080" height="{CANVAS_H}" style="width:1080px;height:{CANVAS_H}px"></canvas>'
            f'{lab_html}</div><div id="{sid}-clk" style="position:absolute;width:1px;height:1px;opacity:0"></div>'
            f'<script>{JS.replace("__CFG__", json.dumps(cfg)).replace("__CH__", str(CANVAS_H))}</script>')
    tw = [(f"#{sid}-clk", "{x:0}",
           f"{{x:1,duration:{dur:.2f},ease:'none',onUpdate:function(){{window.R3_{sid}&&window.R3_{sid}(this.time())}}}}", 0)]
    return html, tw
