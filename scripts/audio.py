"""Soundtrack engine v2 — everything is synthesized here, so it's royalty-free.

Two styles:
  edu      — punchy hip-hop/pop beat (Mon–Thu)
  cocktail — deep-house lounge groove (Fri–Sun)

On top of the beat:
  * a 5-note "Sipp Smart" pluck tune at the start and the end (sonic logo)
  * a riser + a short silence ("drop") before every MYTH/FACT/TIP reveal,
    then an impact; MYTH gets a "wrong answer" buzz, FACT/TIP a "correct" chime
  * whooshes on scene changes, a pop on the ending card
  * the Telugu voice: cleaned up (EQ + compression), with the music ducked under it
  * mastered to about -14 LUFS (Instagram/YouTube loudness), peaks below -1 dB
"""
import subprocess
import wave

import numpy as np
from scipy import signal

SR = 44100


# ---------------------------------------------------------------- helpers
def t_(sec):
    return np.arange(int(SR * sec)) / SR


def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def lp(x, f, order=2):
    b, a = signal.butter(order, min(f, SR / 2 - 100) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def saw(f, t):
    return 2 * ((f * t) % 1.0) - 1


def env_adsr(n, a=0.005, d=0.1, s=0.6, r=0.1):
    total = n / SR
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-4), np.where(t < a + d, 1 - (1 - s) * (t - a) / max(d, 1e-4), s))
    rel_start = max(total - r, a + d)
    e = np.where(t > rel_start, e * np.clip(1 - (t - rel_start) / max(r, 1e-4), 0, 1), e)
    return e


class Bus:
    """Stereo buffer."""

    def __init__(self, n):
        self.x = np.zeros((n, 2))

    def add(self, sig, at, gain=1.0, pan=0.0):
        i = int(round(at * SR))
        if i >= len(self.x) or i + len(sig) <= 0:
            return
        if i < 0:
            sig, i = sig[-i:], 0
        j = min(len(self.x), i + len(sig))
        s = sig[: j - i] * gain
        if s.ndim == 1:
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            self.x[i:j, 0] += s * l * 1.414
            self.x[i:j, 1] += s * r * 1.414
        else:
            self.x[i:j] += s


# ---------------------------------------------------------------- instruments
class Kit:
    def __init__(self, rng):
        self.rng = rng
        self.kick = self._kick()
        self.kick_house = self._kick(tight=True)
        self.clap = self._clap()
        self.hat_c = self._hat(0.035)
        self.hat_o = self._hat(0.22)
        self.shaker = self._hat(0.05, lo=9000) * 0.5
        self.rim = self._rim()

    def noise(self, sec):
        return self.rng.standard_normal(int(SR * sec))

    def _kick(self, tight=False):
        t = t_(0.5)
        f = 62 + 130 * np.exp(-t * (38 if tight else 28))
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (9 if tight else 7))
        knock = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 45) * 0.45
        click = hp(self.noise(0.5), 3500) * np.exp(-t * 250) * 0.5
        return np.tanh((body * 0.8 + knock + click) * 1.6) * 0.9

    def _clap(self):
        n = self.noise(0.35)
        t = t_(0.35)
        e = np.zeros_like(t)
        for k, d in enumerate((0.0, 0.011, 0.022)):
            e += np.where(t >= d, np.exp(-(t - d) * (180 if k < 2 else 18)), 0)
        return bp(n, 900, 5000) * e * 0.9

    def _hat(self, dec, lo=7000):
        n = hp(self.noise(dec * 6), lo, 3)
        return n * np.exp(-t_(dec * 6) / dec) * 0.6

    def _rim(self):
        t = t_(0.12)
        return (np.sin(2 * np.pi * 1700 * t) * 0.6 + bp(self.noise(0.12), 1500, 4000)) * np.exp(-t * 60) * 0.5


def pluck(freq, sec=0.9, bright=0.6, rng=None):
    """Karplus-Strong plucked string (sitar/guitar-like)."""
    n = int(SR * sec)
    L = max(2, int(SR / freq))
    rng = rng or np.random.default_rng(0)
    exc = np.zeros(n)
    burst = lp(rng.uniform(-1, 1, L), 1500 + 6000 * bright)
    exc[:L] = burst
    g = 0.996
    a = np.zeros(L + 2)
    a[0] = 1
    a[L] = -g / 2
    a[L + 1] = -g / 2
    y = signal.lfilter([1.0], a, exc)
    return y / (np.max(np.abs(y)) + 1e-9) * np.exp(-t_(sec) * 1.2)


def supersaw(freqs, sec, cutoff=1600, detune=0.006):
    t = t_(sec)
    left = np.zeros_like(t)
    right = np.zeros_like(t)
    for f in freqs:
        for k, d in enumerate((-detune, 0.0, detune)):
            ph = (k * 0.37) % 1
            s = 2 * ((f * (1 + d) * t + ph) % 1.0) - 1
            if k == 0:
                left += s
            elif k == 2:
                right += s
            else:
                left += 0.7 * s
                right += 0.7 * s
    st = np.stack([lp(left, cutoff), lp(right, cutoff)], axis=1)
    return st / (len(freqs) * 2.5)


def reverb_ir(sec=1.6, rng=None):
    rng = rng or np.random.default_rng(1)
    t = t_(sec)
    ir = rng.standard_normal((len(t), 2)) * np.exp(-t * 4.2)[:, None]
    ir[:, 0] = lp(ir[:, 0], 6000)
    ir[:, 1] = lp(ir[:, 1], 6000)
    return ir / np.sqrt(np.sum(ir ** 2, axis=0, keepdims=True))


# chord progressions (MIDI notes, minor-key, feel-good)
PROG_EDU = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]]      # Am7 Fmaj7 Cmaj7 G7
PROG_HOUSE = [[57, 60, 64, 67, 71], [50, 53, 57, 60, 64], [55, 59, 62, 65, 69], [52, 55, 59, 62, 66]]  # Am9 Dm9 G9 Em7(add9)
MOTIF = [76, 79, 81, 84, 81]        # E G A C A — the "Sipp Smart" tune
MOTIF_RHYTHM = [0, 0.5, 1.0, 1.5, 2.25]


class Soundtrack:
    def __init__(self, dur, seed, style="edu"):
        self.dur = dur
        self.n = int(SR * dur)
        self.rng = np.random.default_rng(seed)
        self.style = style
        self.kit = Kit(self.rng)
        self.drums = Bus(self.n)
        self.music = Bus(self.n)      # pads, bass, stabs (get sidechained)
        self.lead = Bus(self.n)       # plucks/motif
        self.fx = Bus(self.n)
        self.verb_send = Bus(self.n)
        self.voice = np.zeros(self.n)
        self.transpose = int(self.rng.integers(-2, 3))
        self.bpm = 120 if style == "cocktail" else int(self.rng.choice([92, 96, 100]))
        self.beat = 60 / self.bpm
        self.kick_times = []
        self.drop_windows = []      # (start, end) where music is muted before a reveal

    # ---------------- arrangement
    def compose(self):
        if self.style == "cocktail":
            self._house()
        else:
            self._hiphop()
        self.motif(0.0, gain=0.55)
        self.motif(max(0.0, self.dur - 3.2), gain=0.5)

    def _hiphop(self):
        k, b, tr = self.kit, self.beat, self.transpose
        bar = 4 * b
        kick_pat = [0, 1.75, 2.5]            # in beats
        t0, i = 0.0, 0
        while t0 < self.dur:
            ch = [n + tr for n in PROG_EDU[i % 4]]
            # pad + sub bass
            self.music.add(supersaw([midi(n) for n in ch], bar + 0.05, cutoff=2200) * 0.8, t0)
            root = midi(ch[0] - 24)
            for bb in (0, 1.75, 2.5):
                ln = 0.9 * b if bb == 0 else 0.6 * b
                tt = t_(ln)
                bass = (np.tanh(np.sin(2 * np.pi * root * tt) * 2.6) * 0.6
                        + lp(saw(root * 2, tt), 900) * 0.35) * env_adsr(len(tt), 0.005, 0.1, 0.8, 0.06)
                self.music.add(bass * 0.36, t0 + bb * b)
            for kb in kick_pat:
                self.drums.add(k.kick, t0 + kb * b, 0.95)
                self.kick_times.append(t0 + kb * b)
            for cb in (1, 3):
                self.drums.add(k.clap, t0 + cb * b, 0.55)
                self.verb_send.add(k.clap, t0 + cb * b, 0.25)
            for h in range(8):
                ht = t0 + h * b / 2
                self.drums.add(k.hat_c, ht + (0.012 if h % 2 else 0), 0.42 if h % 2 else 0.3, pan=0.25)
            if i % 2 == 1:   # hat roll at bar end
                for r in range(4):
                    self.drums.add(k.hat_c, t0 + 3.5 * b + r * b / 8, 0.2, pan=0.25)
            # soft arpeggio pluck
            for a in range(4):
                note = ch[(a * 2) % len(ch)] + 12
                self.lead.add(pluck(midi(note), 0.7, 0.55, self.rng), t0 + (a + 0.5) * b, 0.3, pan=-0.3 + 0.2 * a)
            t0 += bar
            i += 1

    def _house(self):
        k, b, tr = self.kit, self.beat, self.transpose
        bar = 4 * b
        t0, i = 0.0, 0
        while t0 < self.dur:
            ch = [n + tr for n in PROG_HOUSE[i % 4]]
            self.music.add(supersaw([midi(n) for n in ch[:4]], bar + 0.05, cutoff=1800) * 0.6, t0)
            root = midi(ch[0] - 24)
            for q in range(4):
                bt = t0 + q * b
                self.drums.add(k.kick_house, bt, 0.8)
                self.kick_times.append(bt)
                self.drums.add(k.hat_o, bt + b / 2, 0.34, pan=0.2)
                if q in (1, 3):
                    self.drums.add(k.clap, bt, 0.42)
                    self.verb_send.add(k.clap, bt, 0.3)
                for s16 in range(4):
                    self.drums.add(k.shaker, bt + s16 * b / 4, 0.28 + 0.1 * (s16 == 2), pan=-0.35)
                # offbeat bass
                tt = t_(0.42 * b)
                bass = (np.tanh(np.sin(2 * np.pi * root * tt) * 2.8) * 0.6
                        + lp(saw(root * 2, tt), 1100) * 0.35) * env_adsr(len(tt), 0.004, 0.08, 0.7, 0.05)
                self.music.add(bass * 0.24, bt + b / 2)
            # chord stabs
            for sb in (0.5, 1.75, 3.0):
                stab = supersaw([midi(n + 12) for n in ch[1:4]], 0.22, cutoff=3800) * np.exp(-t_(0.22) * 9)[:, None]
                self.music.add(stab * 1.4, t0 + sb * b)
                self.verb_send.add(stab * 0.5, t0 + sb * b)
            t0 += bar
            i += 1

    def motif(self, at, gain=0.5):
        for note, r in zip(MOTIF, MOTIF_RHYTHM):
            p = pluck(midi(note + self.transpose), 1.1, 0.75, self.rng)
            self.lead.add(p, at + r * self.beat * 0.5, gain, pan=0.1)
            self.verb_send.add(p, at + r * self.beat * 0.5, gain * 0.5)

    # ---------------- effects on events
    def whoosh(self, at):
        sec = 0.45
        n = self.kit.noise(sec)
        sweep = np.zeros_like(n)
        for seg in range(9):  # stepped band sweep
            a, z = int(seg * len(n) / 9), int((seg + 1) * len(n) / 9)
            lo = 300 * 1.45 ** seg
            sweep[a:z] = bp(n, lo, min(lo * 3, 18000))[a:z]
        sweep *= np.sin(np.pi * np.arange(len(n)) / len(n)) ** 2
        self.fx.add(sweep * 0.55, at - sec * 0.6, pan=-0.2)

    def riser(self, end_at, sec=1.1):
        t = t_(sec)
        n = self.kit.noise(sec)
        out = np.zeros_like(n)
        for seg in range(12):
            a, z = int(seg * len(n) / 12), int((seg + 1) * len(n) / 12)
            lo = 400 * 1.32 ** seg
            out[a:z] = bp(n, lo, min(lo * 2.2, 18000))[a:z]
        tone = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (t * 2.2)) / SR) * 0.25
        e = (t / sec) ** 2
        self.fx.add((out * 0.7 + tone) * e * 0.6, end_at - sec)

    def impact(self, at, big=True):
        t = t_(1.4)
        f = 48 + 90 * np.exp(-t * 6)
        sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (2.5 if big else 4))
        crack = lp(self.kit.noise(1.4), 4000) * np.exp(-t * 25)
        hit = np.tanh((sub * 1.2 + crack * 0.6) * 1.5)
        self.fx.add(hit * (0.95 if big else 0.6), at)
        self.verb_send.add(crack * 0.5, at)

    def buzzer(self, at):
        t = t_(0.42)
        sq = signal.square(2 * np.pi * 98 * t) * 0.5 + signal.square(2 * np.pi * 103.5 * t) * 0.5
        s = lp(sq, 2200) * env_adsr(len(t), 0.005, 0.05, 0.9, 0.08)
        self.fx.add(s * 0.32, at + 0.05)

    def chime(self, at):
        for k, (note, d) in enumerate(((84, 0.0), (91, 0.12))):
            t = t_(1.2)
            f = midi(note)
            bell = sum(np.sin(2 * np.pi * f * m * t) * w * np.exp(-t * (3 + m)) for m, w in ((1, 1), (2.76, 0.35), (5.4, 0.15)))
            self.fx.add(bell * 0.22, at + d, pan=0.15)
            self.verb_send.add(bell * 0.2, at + d)

    def pop(self, at):
        t = t_(0.16)
        f = 400 + 1100 * np.exp(-t * 35)
        self.fx.add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22) * 0.5, at)

    def reveal(self, at, kind):
        """Riser → short silence → impact (+ buzz for MYTH, chime for FACT/TIP)."""
        self.riser(at - 0.25, 1.1)
        self.drop_windows.append((at - 0.3, at))
        self.impact(at, big=(kind == "MYTH"))
        if kind == "MYTH":
            self.buzzer(at)
        else:
            self.chime(at + 0.05)

    # ---------------- voice
    def add_voice(self, path, at, gain=1.0):
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(path), "-af",
             "highpass=f=85,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=3,"
             "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2",
             "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
            check=True, capture_output=True).stdout
        sig = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768
        i = int(at * SR)
        j = min(self.n, i + len(sig))
        if i < self.n:
            self.voice[i:j] += sig[: j - i] * gain

    # ---------------- mix + master
    def _sidechain(self):
        g = np.ones(self.n)
        rec = int(0.16 * SR)
        shape = 1 - 0.55 * np.exp(-np.arange(rec) / (0.045 * SR))
        for kt in self.kick_times:
            i = int(kt * SR)
            j = min(self.n, i + rec)
            if i < self.n:
                g[i:j] = np.minimum(g[i:j], shape[: j - i])
        return g

    def _drop_gain(self):
        g = np.ones(self.n)
        for a, z in self.drop_windows:
            i, j = max(0, int(a * SR)), min(self.n, int(z * SR))
            fade = min(400, (j - i) // 4)
            seg = np.full(j - i, 0.06)
            seg[:fade] = np.linspace(1, 0.06, fade)
            g[i:j] = np.minimum(g[i:j], seg)
        return g

    def render(self):
        sc = self._sidechain()[:, None]
        drop = self._drop_gain()[:, None]
        verb = np.stack([signal.fftconvolve(self.verb_send.x[:, c], reverb_ir(1.6, np.random.default_rng(c))[:, c])[: self.n]
                         for c in range(2)], axis=1)
        beds = (self.drums.x * 0.9 + self.music.x * sc * 0.85 + self.lead.x * 0.9 + verb * 0.28) * drop
        for c in range(2):
            beds[:, c] = hp(beds[:, c], 40)
            beds[:, c] = beds[:, c] - 0.45 * lp(beds[:, c], 90)

        has_voice = np.any(self.voice)
        if has_voice:
            env = np.abs(self.voice)
            att, rel = int(0.03 * SR), int(0.35 * SR)
            env = signal.lfilter([1.0 / att], [1, -(1 - 1.0 / att)], env)          # fast follower
            env = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], env)
            duck = 1 - 0.68 * np.clip(env * 30, 0, 1)                              # ~ -10 dB under speech
            beds = beds * duck[:, None]
            mix = beds * 0.55 + self.fx.x * 0.75 + np.repeat(self.voice[:, None], 2, axis=1) * 1.0
        else:
            mix = beds + self.fx.x * 0.8

        # fade out last 0.8 s
        f = int(0.8 * SR)
        mix[-f:] *= np.linspace(1, 0, f)[:, None]
        return self._master(mix)

    def _master(self, x):
        import pyloudnorm as pyln
        # gentle bus compression
        lvl = np.sqrt(signal.lfilter([0.002], [1, -0.998], np.mean(x ** 2, axis=1)) + 1e-12)
        thr = 0.25
        gain = np.where(lvl > thr, (thr / lvl) ** (1 - 1 / 2.5), 1.0)
        x = x * gain[:, None]
        # loudness normalize to -14 LUFS
        meter = pyln.Meter(SR)
        loud = meter.integrated_loudness(x)
        if np.isfinite(loud):
            x = x * 10 ** ((-14.0 - loud) / 20)
        # look-ahead peak limiter at -1.2 dBFS
        from scipy.ndimage import minimum_filter1d
        ceiling = 10 ** (-1.2 / 20)
        peak = np.max(np.abs(x), axis=1)
        need = np.minimum(1.0, ceiling / np.maximum(peak, 1e-9))
        win = int(0.005 * SR)
        need = minimum_filter1d(need, size=2 * win + 1, mode="nearest")   # look-ahead
        rel = int(0.08 * SR)
        smooth = signal.lfilter([1.0 / rel], [1, -(1 - 1.0 / rel)], need,
                                zi=[need[0] * (1 - 1.0 / rel)])[0]
        x = x * np.minimum(need, smooth)[:, None]
        return np.clip(x, -ceiling, ceiling)

    def write(self, path):
        x = self.render()
        pcm = (x * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
