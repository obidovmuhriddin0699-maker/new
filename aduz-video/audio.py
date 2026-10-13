"""Synthesises the music + SFX track for an episode (32 s, 44.1 kHz stereo WAV).

Usage: python3 audio.py <episode number> build/episodeN.wav
Episodes 1-3 use the simple bed below; from 4 on, the v2 engine (needs scipy) with reverb,
sidechain and a full drum/bass/chord arrangement.
Every episode shares the same music bed (Muammo 0-11 s, Yechim 11-22 s, Natija 22-32 s);
the SFX cues follow that episode's animation timeline in episodeN.html.
"""
import sys
import wave

import numpy as np

SR, DUR = 44100, 32.0
N = int(SR * DUR)
t = np.arange(N) / SR
mix = np.zeros((N, 2))
rng = np.random.default_rng(1)


def env(n, a=0.005, r=0.2):
    x = np.arange(n) / SR
    return np.minimum(1, x / a) * np.exp(-x / r)


def add(start, sig, gain=1.0, pan=0.0):
    i = int(start * SR)
    sig = sig[: max(0, N - i)]
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    mix[i : i + len(sig), 0] += sig * gain * l
    mix[i : i + len(sig), 1] += sig * gain * r


def tone(freq, dur, kind="sine", a=0.005, r=0.3):
    n = int(dur * SR)
    x = np.arange(n) / SR
    ph = 2 * np.pi * freq * x
    if kind == "sine":
        s = np.sin(ph)
    elif kind == "square":
        s = np.sign(np.sin(ph)) * 0.6
    elif kind == "saw":
        s = 2 * ((freq * x) % 1) - 1
    else:  # soft pluck
        s = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    return s * env(n, a, r)


def noise(dur, r=0.1, lp=0.0):
    n = int(dur * SR)
    s = rng.standard_normal(n)
    if lp:
        k = int(lp)
        s = np.convolve(s, np.ones(k) / k, mode="same")
    return s * env(n, 0.002, r)


def section(a, b, fade=0.4):
    m = ((t >= a) & (t < b)).astype(float)
    m *= np.clip((t - a) / fade, 0, 1) * np.clip((b - t) / fade, 0, 1)
    return m


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def chime(at):
    add(at, tone(midi(88), 0.8, "sine", 0.003, 0.3), 0.18)
    add(at + 0.15, tone(midi(95), 1.0, "sine", 0.003, 0.4), 0.16)


def tap(at):
    add(at, noise(0.02, 0.004), 0.25)
    add(at, tone(2200, 0.05, "sine", 0.001, 0.01), 0.25)


def pop(at, freq, gain=0.12, pan=0.0):
    add(at, tone(freq, 0.12, "sine", 0.002, 0.04) + 0.5 * tone(freq * 1.5, 0.12, "sine", 0.002, 0.03), gain, pan)


def buzzer(at, pan):
    add(at, tone(140, 0.28, "square", 0.004, 0.12) + 0.6 * tone(147, 0.28, "square", 0.004, 0.12), 0.16, pan)


def cha_ching(at):
    add(at, noise(0.08, 0.03, 2), 0.2)
    for f, d in [(2093, 0.0), (2637, 0.0), (3136, 0.12), (4186, 0.12)]:
        add(at + 0.05 + d, tone(f, 0.9, "sine", 0.001, 0.25), 0.09)


def bed():
    """Music shared by every episode, including the scene transitions."""
    # Scene 1 (0-11 s): tension
    s1 = section(0, 11.0)
    stress = np.clip((t - 5.5) / 4.5, 0, 1)
    drone = np.sin(2 * np.pi * 55 * t) + 0.7 * np.sin(2 * np.pi * 58.3 * t) + 0.3 * np.sin(2 * np.pi * 110.5 * t)
    drone *= 0.6 + 0.4 * np.sin(2 * np.pi * (0.8 + 1.2 * stress) * t) ** 2
    mix[:] += (drone * s1 * (0.10 + 0.08 * stress))[:, None]
    for k in np.arange(0.5, 10.6, 0.75):  # heartbeat
        hb = tone(60, 0.25, "sine", 0.002, 0.08) + 0.5 * tone(48, 0.25, "sine", 0.002, 0.1)
        add(k, hb, 0.35 + 0.25 * min(1, max(0, (k - 5.5) / 4.5)))
        add(k + 0.22, hb, 0.2)
    riser_n = int(1.9 * SR)
    rx = np.arange(riser_n) / SR
    riser = rng.standard_normal(riser_n) * (rx / 1.9) ** 2
    riser = np.convolve(riser, np.ones(6) / 6, mode="same") + 0.5 * np.sin(2 * np.pi * (200 * rx + 300 * rx**2)) * (rx / 1.9) ** 2
    add(8.8, riser, 0.22)
    add(10.7, noise(0.7, 0.18, 12), 0.35)  # whoosh into solution

    # Scene 2 (11-22 s): clean, modern
    s2 = section(11.0, 22.2)
    pad = sum(np.sin(2 * np.pi * midi(n) * t) for n in (60, 64, 67, 71)) / 4
    mix[:] += (pad * s2 * 0.09)[:, None]
    beat = 60 / 112
    arp = [72, 76, 79, 83, 79, 76]
    for k, at in enumerate(np.arange(11.3, 21.9, beat / 2)):
        add(at, tone(midi(arp[k % len(arp)]), 0.3, "pluck", 0.003, 0.12), 0.07, 0.3 * np.sin(k))
    for at in np.arange(11.3, 21.9, beat):  # soft kick
        n = int(0.2 * SR)
        x = np.arange(n) / SR
        add(at, np.sin(2 * np.pi * (50 + 60 * np.exp(-x * 30)) * x) * env(n, 0.002, 0.08), 0.25)
    add(21.9, noise(0.5, 0.14, 8), 0.3)  # whoosh into result

    # Scene 3 (22-32 s): triumphant, C G Am F
    chords = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]
    bar = 4 * 60 / 120
    for ci, at in enumerate(np.arange(22.0, 32.0, bar)):
        ch = chords[ci % 4]
        n = int(bar * SR)
        x = np.arange(n) / SR
        sig = sum(np.sin(2 * np.pi * midi(m) * x) + 0.3 * np.sin(4 * np.pi * midi(m) * x) for m in ch) / 3
        add(at, sig * np.minimum(1, x / 0.05) * np.exp(-x / 2.5), 0.12)
        add(at, tone(midi(ch[0] - 24), bar, "sine", 0.01, 1.2), 0.25)
        for j in range(8):
            add(at + j * bar / 8, tone(midi(ch[j % 3] + 12 + 12 * (j // 3 % 2)), 0.25, "pluck", 0.002, 0.1), 0.07, 0.4 * np.sin(j))
    for at in np.arange(22.0, 31.5, 0.5):
        n = int(0.25 * SR)
        x = np.arange(n) / SR
        add(at, np.sin(2 * np.pi * (45 + 80 * np.exp(-x * 35)) * x) * env(n, 0.002, 0.1), 0.4)
        add(at + 0.25, noise(0.05, 0.02), 0.04)
    add(28.3, tone(1760, 2.0, "sine", 0.001, 0.8) + 0.4 * tone(3520, 2.0, "sine", 0.001, 0.5), 0.16)  # end-card ting


def cues_1():
    """1-qism: Reklama bozoridagi xaos."""
    for at, kind in [(0.9, "out"), (1.9, "in"), (2.9, "out"), (4.0, "in"), (5.0, "out")]:  # chat messages
        pop(at, 1100 if kind == "out" else 760, 0.18, 0.3 if kind == "out" else -0.3)
    add(6.2, tone(220, 0.4, "saw", 0.01, 0.15), 0.06)
    for at, pan in zip([6.6, 7.1, 7.6, 8.1], [-0.5, 0.5, -0.4, 0.4]):
        buzzer(at, pan)
    for at in np.arange(12.1, 13.3, 0.075):  # typing
        add(at, noise(0.03, 0.006), 0.05, rng.uniform(-0.3, 0.3))
    for i in range(3):  # chip pops + card swooshes
        add(13.3 + i * 0.15, tone(1300 + 200 * i, 0.08, "sine", 0.002, 0.03), 0.12)
        add(13.9 + i * 0.3, noise(0.35, 0.09, 20), 0.18, 0.6)
    tap(16.15)
    tap(17.65)
    chime(18.6)
    for i in range(3):
        add(19.3 + i * 0.35, tone(midi(84 + 3 * i), 0.2, "sine", 0.002, 0.06), 0.08)
    cha_ching(25.0)
    for i in range(3):  # badge pops
        add(24.4 + i * 0.35, tone(midi(79 + 4 * i), 0.3, "sine", 0.002, 0.12), 0.12)


def cues_2():
    """2-qism: Auditoriyani topish muammosi."""
    add(0.6, noise(0.3, 0.07, 16), 0.15)  # post slides in
    for i, at in enumerate(np.arange(1.6, 9.6, 0.38)):  # viewers landing off-target
        pop(at, 520 + 40 * (i % 3), 0.06, np.sin(i * 1.7) * 0.6)
    for at in (3.3, 4.1, 4.9):  # comments from the wrong audience
        pop(at, 900, 0.16, -0.3)
    add(5.7, noise(0.4, 0.1, 18), 0.2)  # stats sheet
    for k in range(6):  # bars filling
        add(6.1 + k * 0.2, tone(330 - 20 * k, 0.25, "saw", 0.01, 0.1), 0.035)
    for at, pan in zip([6.6, 7.1, 7.6, 8.1], [-0.5, 0.5, -0.5, 0.5]):
        buzzer(at, pan)
    for at in (11.9, 12.3, 12.7, 13.1, 14.55, 14.95, 15.3):  # filter taps, channel count drops
        tap(at)
        add(at + 0.05, tone(1400, 0.08, "sine", 0.002, 0.03), 0.1)
    drag = int(0.7 * SR)
    dx = np.arange(drag) / SR
    add(13.5, np.sin(2 * np.pi * (900 * dx - 300 * dx**2)) * np.exp(-dx * 1.5) * 0.4, 0.08)  # slider drag
    add(15.4, noise(0.45, 0.11, 20), 0.2, 0.5)  # slide to results
    gauge = int(1.1 * SR)
    gx = np.arange(gauge) / SR
    add(15.7, np.sin(2 * np.pi * (500 * gx + 400 * gx**2)) * np.minimum(1, gx / 0.05) * np.exp(-gx * 1.2), 0.07)
    for i in range(2):
        add(16.2 + i * 0.25, noise(0.3, 0.08, 20), 0.14, 0.6)
    tap(17.6)
    chime(18.6)
    for i in range(3):
        add(19.3 + i * 0.35, tone(midi(84 + 3 * i), 0.2, "sine", 0.002, 0.06), 0.08)
    for i in range(36):  # viewers hitting the bullseye
        if i % 3 == 0:
            add(23.15 + i * 0.05, tone(midi(84 + (i // 3) % 5 * 2), 0.12, "sine", 0.002, 0.05), 0.07, np.sin(i) * 0.5)
    cha_ching(25.0)


def cues_3():
    """3-qism: Soxta obunachilar va ishonchsizlik."""
    add(0.6, noise(0.3, 0.07, 16), 0.15)  # post slides in
    for i, at in enumerate(1.2 + 3.0 * (np.arange(14) / 14) ** 2):  # view ticks slowing to a stop
        add(at, tone(1500, 0.04, "sine", 0.001, 0.015), 0.07, 0.2)
    add(3.6, tone(98, 0.9, "saw", 0.02, 0.4) + 0.6 * tone(92.5, 0.9, "saw", 0.02, 0.4), 0.07)  # disappointment
    add(4.8, noise(0.4, 0.1, 18), 0.2)  # audit sheet
    sweep = int(1.6 * SR)
    sx = np.arange(sweep) / SR
    add(5.3, np.sin(2 * np.pi * (300 * sx + 120 * sx**2)) * np.minimum(1, sx / 0.1) * np.minimum(1, (1.6 - sx) / 0.2), 0.05)  # scan line
    for i in range(6):  # BOT tags
        pop(5.6 + i * 0.22, 420, 0.1, (-1) ** i * 0.3)
    jump = int(0.5 * SR)
    jx = np.arange(jump) / SR
    add(7.4, np.sin(2 * np.pi * (200 * jx + 900 * jx**2)) * np.exp(-jx * 4), 0.1)  # bought spike
    for at, pan in zip([6.6, 7.1, 7.6, 8.1], [-0.5, 0.5, -0.5, 0.5]):
        buzzer(at, pan)
    fall = int(1.0 * SR)
    fx = np.arange(fall) / SR
    add(9.0, np.sin(2 * np.pi * (700 * fx - 300 * fx**2)) * np.minimum(1, fx / 0.05) * np.exp(-fx * 1.5), 0.1)  # deflate
    for at in np.arange(12.0, 12.7, 0.06):  # typing
        add(at, noise(0.03, 0.006), 0.05, rng.uniform(-0.3, 0.3))
    tap(12.9)
    for i in range(4):  # audit rows: scanning ticks, then a red result
        a = 13.05 + i * 0.5
        for k in range(4):
            add(a + k * 0.1, tone(1800, 0.03, "sine", 0.001, 0.01), 0.04)
        add(a + 0.4, tone(220, 0.18, "square", 0.004, 0.06), 0.08, 0.3)
    add(15.0, tone(110, 0.6, "saw", 0.01, 0.25), 0.07)  # low trust score
    add(15.35, noise(0.15, 0.04, 30), 0.5)  # stamp thud
    add(15.35, tone(70, 0.3, "sine", 0.002, 0.12), 0.5)
    add(16.0, noise(0.45, 0.11, 20), 0.2, 0.5)  # slide to verified channels
    for i in range(3):
        add(16.35 + i * 0.25, noise(0.3, 0.08, 20), 0.14, 0.6)
    tap(17.6)
    chime(18.6)
    for i in range(3):
        add(19.3 + i * 0.35, tone(midi(84 + 3 * i), 0.2, "sine", 0.002, 0.06), 0.08)
    for i in range(0, 50, 2):  # bots flipping into real people
        add(22.9 + i * 0.036, tone(midi(79 + (i // 2) % 6 * 2), 0.1, "sine", 0.002, 0.04), 0.06, np.sin(i) * 0.5)
    for i in range(3):  # stat tiles
        add(23.4 + i * 0.15, tone(midi(76 + 4 * i), 0.2, "sine", 0.002, 0.08), 0.1)
    cha_ching(25.0)


# =====================================================================================
# v2 engine (4-qismdan boshlab): separate buses, filters, reverb, sidechain, soft clip.
# =====================================================================================
from scipy.signal import butter, fftconvolve, sosfilt  # noqa: E402


def filt(sig, kind, fc, order=2):
    sos = butter(order, fc, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, sig, axis=0)


def sweep_filter(sig, f0, f1, kind="bandpass", width=0.6, chunks=24):
    """Filter whose centre moves from f0 to f1 (log), done in short chunks."""
    out = np.zeros_like(sig)
    edges = np.linspace(0, len(sig), chunks + 1).astype(int)
    for k in range(chunks):
        fc = f0 * (f1 / f0) ** (k / max(1, chunks - 1))
        band = [fc * (1 - width / 2), min(fc * (1 + width / 2), SR / 2 - 100)] if kind == "bandpass" else fc
        a, b = edges[k], edges[k + 1]
        pad = min(a, 2048)
        out[a:b] = filt(sig[a - pad : b], kind, band)[pad:]
    return out


class Mixer:
    def __init__(self):
        self.music = np.zeros((N, 2))
        self.drums = np.zeros((N, 2))
        self.sfx = np.zeros((N, 2))
        self.send = np.zeros((N, 2))
        self.kicks = []

    def put(self, bus, start, sig, gain=1.0, pan=0.0, verb=0.0):
        i = int(start * SR)
        if i >= N:
            return
        if sig.ndim == 1:
            l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
            sig = np.stack([sig * l, sig * r], axis=1)
        sig = sig[: N - i] * gain
        getattr(self, bus)[i : i + len(sig)] += sig
        if verb:
            self.send[i : i + len(sig)] += sig * verb

    def render(self, duck_depth=0.55):
        duck = np.ones(N)
        for k in self.kicks:
            i = int(k * SR)
            n = min(int(0.35 * SR), N - i)
            x = np.arange(n) / SR
            duck[i : i + n] = np.minimum(duck[i : i + n], 1 - duck_depth * np.exp(-x / 0.11))
        r = rnd_ir()
        verb = np.stack([fftconvolve(self.send[:, c], r[:, c])[:N] for c in range(2)], axis=1)
        out = self.music * duck[:, None] + self.drums + self.sfx + verb * 0.55
        out = filt(out, "highpass", 28)
        out = np.tanh(out * 1.4) / 1.4  # gentle saturation / soft clip
        return out


def rnd_ir(length=2.4, decay=0.55):
    n = int(length * SR)
    x = np.arange(n) / SR
    g = np.random.default_rng(77)
    ir = g.standard_normal((n, 2)) * np.exp(-x / decay)[:, None]
    ir = filt(filt(ir, "lowpass", 7000), "highpass", 250)
    ir[: int(0.02 * SR)] = 0  # pre-delay
    return ir / np.sqrt(np.sum(ir**2, axis=0, keepdims=True)) * 0.9


def seconds(d):
    return np.arange(int(d * SR)) / SR


def kick(punch=1.0):
    x = seconds(0.45)
    f = 45 + 110 * np.exp(-x * 35)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.16)
    click = filt(rng.standard_normal(len(x)), "highpass", 2500) * np.exp(-x / 0.004) * 0.3
    return np.tanh((body + click) * 1.6 * punch)


def clap():
    x = seconds(0.4)
    n = rng.standard_normal(len(x))
    env = sum(np.exp(-np.clip(x - d, 0, None) / (0.012 if d < 0.02 else 0.13)) * (x >= d) for d in (0, 0.011, 0.022))
    return filt(n, "bandpass", [900, 3200]) * env * 0.8


def hat(open_=False):
    x = seconds(0.3 if open_ else 0.06)
    return filt(rng.standard_normal(len(x)), "highpass", 7500) * np.exp(-x / (0.12 if open_ else 0.018)) * 0.5


def crash():
    x = seconds(2.5)
    n = filt(filt(rng.standard_normal((len(x), 2)), "highpass", 3500), "lowpass", 11000)
    return n * np.exp(-x / 0.65)[:, None] * 0.26


def boom(depth=1.0):
    x = seconds(2.0)
    f = 30 + 60 * np.exp(-x * 6)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.7)
    thump = filt(rng.standard_normal(len(x)), "lowpass", 300) * np.exp(-x / 0.08) * 0.8
    return np.tanh((sub + thump) * 1.3 * depth)


def saw(f, x):
    return 2 * ((f * x) % 1.0) - 1


def supersaw(freqs, dur, cutoff=2400, attack=0.02, release=0.3):
    x = seconds(dur)
    out = np.zeros((len(x), 2))
    for f in freqs:
        for c, cents in enumerate(((-11, 4), (-4, 12))):
            v = sum(saw(f * 2 ** (ct / 1200), x + 0.13 * k) for k, ct in enumerate(cents))
            out[:, c] += v
    out /= 2 * len(freqs)
    env = np.minimum(1, x / attack) * np.minimum(1, np.clip(dur - x, 0, None) / release)
    return filt(out, "lowpass", cutoff) * env[:, None]


def pad(freqs, dur, cutoff=1400, attack=0.6, release=0.8):
    x = seconds(dur)
    v = sum(np.sin(2 * np.pi * f * x) + 0.4 * (2 * np.abs(saw(f, x)) - 1) for f in freqs) / len(freqs)
    env = np.minimum(1, x / attack) * np.minimum(1, np.clip(dur - x, 0, None) / release)
    s = filt(v * env, "lowpass", cutoff)
    return np.stack([s, np.roll(s, int(0.012 * SR))], axis=1)


def bell(f, dur=1.2, index=2.2, decay=0.45):
    x = seconds(dur)
    mod = index * np.exp(-x / 0.18) * np.sin(2 * np.pi * f * 3.5 * x)
    return np.sin(2 * np.pi * f * x + mod) * np.exp(-x / decay) * np.minimum(1, x / 0.002)


def sub(f, dur):
    x = seconds(dur)
    s = np.sin(2 * np.pi * f * x) + 0.25 * np.sin(4 * np.pi * f * x)
    return s * np.minimum(1, x / 0.005) * np.minimum(1, np.clip(dur - x, 0, None) / 0.03)


def tick(high=True):
    x = seconds(0.06)
    f = 2600 if high else 1700
    body = np.sin(2 * np.pi * f * x) * np.exp(-x / 0.008)
    n = filt(rng.standard_normal(len(x)), "bandpass", [f * 0.7, f * 1.4]) * np.exp(-x / 0.004)
    return body * 0.6 + n * 0.5


def whoosh(dur, f0, f1):
    n = rng.standard_normal(int(dur * SR))
    s = sweep_filter(n, f0, f1)
    x = seconds(dur)
    return s * np.sin(np.pi * x / dur) ** 1.5


def riser(dur):
    x = seconds(dur)
    n = sweep_filter(rng.standard_normal(len(x)), 400, 6000, width=0.9)
    tone_ = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2 * x / dur)) / SR) * 0.3
    return (n + tone_) * (x / dur) ** 2.5


def ui_click():
    x = seconds(0.05)
    return np.sin(2 * np.pi * 1500 * x) * np.exp(-x / 0.01) + filt(rng.standard_normal(len(x)), "highpass", 3000) * np.exp(-x / 0.003) * 0.4


def ding(f=880.0):
    return np.concatenate([bell(f, 0.12, 1.2, 0.08), bell(f * 1.5, 0.8, 1.0, 0.25)])


def glitch_hit():
    x = seconds(0.5)
    low = np.sin(2 * np.pi * np.cumsum(90 + 120 * np.exp(-x * 25)) / SR) * np.exp(-x / 0.14)
    grit = np.sign(np.sin(2 * np.pi * 220 * x)) * np.exp(-x / 0.05) * 0.25
    return np.tanh((low + grit + filt(rng.standard_normal(len(x)), "lowpass", 1500) * np.exp(-x / 0.03) * 0.6) * 1.5)


def m(note):
    return midi(note)


def render_4():
    """4-qism: Vaqtni o'g'irlaydigan jarayonlar. 120 BPM, cuts on the beat grid."""
    M = Mixer()
    # ---------- Scene 1 (0-10.55): ticking clock, dark minor pulse ----------
    ticks = list(np.arange(0.5, 5.5, 0.5)) + list(np.arange(5.5, 8.5, 0.25)) + list(np.arange(8.5, 10.6, 0.125))
    for k, at in enumerate(ticks):  # same schedule as tickTimes() in episode4.html
        M.put("sfx", at, tick(k % 2 == 0), 0.32, -0.25 if k % 2 else 0.25, verb=0.15)
    M.put("music", 0.0, pad([m(45), m(48), m(52)], 10.6, cutoff=700, attack=1.5), 0.32, verb=0.3)
    for i, at in enumerate(np.arange(2.0, 8.5, 0.25)):  # filtered saw bass, opening with stress
        x = seconds(0.22)
        cut = 250 + 1500 * ((at - 2) / 6.5) ** 1.5
        note = m(33) if i % 8 not in (6, 7) else m(36)
        M.put("music", at, filt(saw(note, x) * np.exp(-x / 0.12), "lowpass", cut), 0.22)
    for at in np.arange(5.5, 8.5, 0.5):
        M.put("drums", at, kick(0.8), 0.5)
        M.kicks.append(at)
        M.put("drums", at + 0.25, hat(), 0.12, 0.3)
    for at in (1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0):  # new chat messages
        M.put("sfx", at, ding(988), 0.08, 0.2, verb=0.2)
    M.put("sfx", 4.55, whoosh(0.5, 600, 3000), 0.18, 0.4)
    for at, kind in [(5.2, "out"), (5.75, "in"), (6.3, "out"), (6.9, "in"), (7.45, "out"), (8.05, "in")]:
        M.put("sfx", at, bell(1320 if kind == "out" else 990, 0.25, 0.8, 0.06), 0.12, 0.3 if kind == "out" else -0.3)
        if kind == "in":
            for k in range(5):
                M.put("sfx", at - 0.45 + k * 0.08, filt(rng.standard_normal(1200), "bandpass", [2000, 6000]) * np.exp(-seconds(1200 / SR) / 0.004), 0.05)
    for at, pan in ((5.6, -0.4), (6.6, 0.4), (7.6, -0.4)):  # red slams
        M.put("sfx", at, glitch_hit(), 0.42, pan, verb=0.25)
    # "3 KUN": big hit, then the beat drops out under a riser
    M.put("sfx", 8.5, boom(1.0), 0.75, verb=0.4)
    M.put("sfx", 8.5, clap(), 0.4, verb=0.5)
    M.put("sfx", 8.5, crash(), 0.35)
    M.put("sfx", 8.6, riser(1.95), 0.32)
    M.put("sfx", 10.55, whoosh(0.5, 300, 5000), 0.32, 0.0, verb=0.3)

    # ---------- Scene 2 (11-21.75): clean four-on-the-floor, Cmaj7 Am7 Fmaj7 G ----------
    M.put("sfx", 11.0, boom(0.8), 0.55, verb=0.35)
    M.put("sfx", 11.0, crash(), 0.3)
    prog2 = [(11, [60, 64, 67, 71], 48), (13, [57, 60, 64, 67], 45), (15, [53, 57, 60, 64], 41), (17, [55, 59, 62, 67], 43), (19, [60, 64, 67, 71], 48), (21, [57, 60, 64, 67], 45)]
    for start, notes, root in prog2:
        dur = min(2.0, 21.75 - start)
        M.put("music", start, supersaw([m(n) for n in notes], dur, cutoff=2600), 0.3, verb=0.25)
        M.put("music", start, pad([m(n + 12) for n in notes[:3]], dur, cutoff=3000, attack=0.2), 0.12, verb=0.3)
        for b in np.arange(0, dur - 0.01, 0.25):
            M.put("music", start + b, sub(m(root) * (2 if int(b * 4) % 2 else 1), 0.2), 0.28)
        for j, b in enumerate(np.arange(0, dur - 0.01, 0.25)):  # bell arpeggio
            M.put("music", start + b, bell(m(notes[j % 4] + 12), 0.4, 1.4, 0.18), 0.06, 0.35 * np.sin(j * 1.3), verb=0.3)
    for at in np.arange(11.0, 21.75, 0.5):
        M.put("drums", at, kick(), 0.55)
        M.kicks.append(at)
        M.put("drums", at + 0.25, hat(at % 2 > 1.4), 0.14, 0.3)
        if int(round(at * 2)) % 2 == 1:
            M.put("drums", at, clap(), 0.28, verb=0.2)
    for at in np.arange(12.0, 18.0, 0.25):  # stopwatch
        M.put("sfx", at, tick(True), 0.06, 0.5)
    M.put("sfx", 12.4, ui_click(), 0.3)
    for i in range(6):  # checkbox cascade, pentatonic up
        M.put("sfx", 12.52 + i * 0.09, bell(m([72, 74, 76, 79, 81, 84][i]), 0.35, 1.5, 0.12), 0.14, -0.3 + i * 0.12, verb=0.25)
    M.put("sfx", 13.5, whoosh(0.45, 2000, 600), 0.16, 0.6)  # banner
    M.put("sfx", 14.2, bell(m(79), 0.3, 1.0, 0.1), 0.12)
    M.put("sfx", 15.0, ui_click(), 0.4)
    plane = whoosh(0.85, 500, 7000)
    M.put("sfx", 15.05, np.stack([plane * np.linspace(1, 0.3, len(plane)), plane * np.linspace(0.3, 1, len(plane))], axis=1), 0.45, verb=0.3)
    for i in range(6):
        M.put("sfx", 15.5 + i * 0.12, ui_click(), 0.12, -0.4 + i * 0.16)
        M.put("sfx", 16.3 + i * 0.22, bell(m([76, 79, 81, 84, 86, 88][i]), 0.6, 1.2, 0.22), 0.16, -0.3 + i * 0.12, verb=0.35)
    M.put("sfx", 18.5, boom(0.9), 0.65, verb=0.4)  # "47 SONIYA"
    M.put("sfx", 18.5, crash(), 0.32)
    for k, f in enumerate((m(84), m(88), m(91), m(96))):
        M.put("sfx", 18.5 + k * 0.03, bell(f, 1.6, 2.5, 0.5), 0.07, -0.3 + k * 0.2, verb=0.5)
    for k, f in enumerate((m(72), m(76), m(79), m(84))):  # success sheet chime
        M.put("sfx", 19.9 + k * 0.07, bell(f, 1.4, 1.2, 0.45), 0.1, -0.2 + k * 0.13, verb=0.5)
    M.put("sfx", 21.0, riser(1.0), 0.28)

    # ---------- Scene 3 (22-32): uplifting C G Am F, drums drop at the end card ----------
    M.put("sfx", 21.75, whoosh(0.5, 500, 8000), 0.3, verb=0.3)
    M.put("sfx", 22.0, boom(0.9), 0.6, verb=0.45)
    M.put("sfx", 22.0, crash(), 0.38)
    prog3 = [(22, [60, 64, 67], 48), (24, [55, 59, 62], 43), (26, [57, 60, 64], 45), (28, [53, 57, 60], 41), (30, [60, 64, 67, 72], 48)]
    for start, notes, root in prog3:
        dur = 2.0 if start < 30 else 2.0
        M.put("music", start, supersaw([m(n) for n in notes] + [m(notes[0] + 12)], dur, cutoff=3200 if start < 27 else 1800), 0.3 if start < 27 else 0.22, verb=0.3)
        M.put("music", start, pad([m(n + 12) for n in notes], dur + (0.6 if start == 30 else 0), cutoff=2600, attack=0.3), 0.16, verb=0.4)
        for b in np.arange(0, dur - 0.01, 0.5 if start >= 27 else 0.25):
            M.put("music", start + b, sub(m(root), 0.22 if start < 27 else 0.45), 0.3)
    melody = [(22, 76), (22.5, 79), (23, 84), (23.5, 79), (24, 74), (24.5, 79), (25, 83), (25.5, 79),
              (26, 72), (26.5, 76), (27, 81), (28, 69), (28.5, 72), (29, 77), (29.5, 81), (30, 76)]
    for at, n in melody:
        M.put("music", at, bell(m(n + 12), 1.0, 1.8, 0.35), 0.12, 0.15, verb=0.45)
    for at in np.arange(22.0, 26.75, 0.5):
        M.put("drums", at, kick(1.1), 0.6)
        M.kicks.append(at)
        M.put("drums", at + 0.25, hat(True), 0.13, 0.35)
        if int(round(at * 2)) % 2 == 1:
            M.put("drums", at, clap(), 0.32, verb=0.25)
    M.put("sfx", 22.8, whoosh(0.7, 3000, 500), 0.14, -0.5)  # red bar
    M.put("sfx", 23.6, bell(m(84), 0.4, 1.4, 0.12), 0.16, 0.4)  # tiny green bar
    rise = seconds(1.1)
    M.put("sfx", 23.9, np.sin(2 * np.pi * np.cumsum(400 * 2 ** (2.5 * rise / 1.1)) / SR) * (rise / 1.1) * 0.5, 0.1)
    M.put("sfx", 25.0, boom(0.6), 0.45, verb=0.4)
    g = np.random.default_rng(5)
    for k in range(18):  # sparkle
        M.put("sfx", 25.0 + g.uniform(0, 0.8), bell(m(int(g.choice([84, 88, 91, 96, 100]))), 0.8, 1.5, 0.25), 0.05, g.uniform(-0.8, 0.8), verb=0.5)
    for i in range(3):
        M.put("sfx", 25.2 + i * 0.25, bell(m(79 + 5 * i), 0.5, 1.2, 0.2), 0.14, -0.4 + 0.4 * i, verb=0.3)
    M.put("sfx", 27.0, whoosh(0.6, 3000, 800), 0.18, verb=0.4)  # end card
    M.put("sfx", 28.3, bell(1760, 3.0, 1.0, 0.9) + 0.0, 0.2, verb=0.6)
    M.put("sfx", 28.3, bell(2637, 3.0, 0.8, 0.7), 0.08, 0.3, verb=0.6)

    out = M.render()
    out *= np.clip((DUR - t) / 1.2, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- v3 additions (5-qismdan): sound-director pass ----------
from scipy.signal import lfilter  # noqa: E402


class MixerPro(Mixer):
    """Adds a tempo-synced ping-pong delay, a vocal-space EQ dip on music,
    a bus compressor and a gentle master EQ (warmth + air) on top of Mixer."""

    def __init__(self, bpm=120):
        super().__init__()
        self.delay = np.zeros((N, 2))
        self.beat = 60 / bpm

    def put(self, bus, start, sig, gain=1.0, pan=0.0, verb=0.0, echo=0.0):
        super().put(bus, start, sig, gain, pan, verb)
        if echo:
            i = int(start * SR)
            if i < N:
                s = sig if sig.ndim == 2 else np.stack([sig, sig], axis=1) * np.sqrt(0.5)
                s = s[: N - i] * gain * echo
                self.delay[i : i + len(s)] += s

    def render(self, duck_depth=0.5):
        duck = np.ones(N)
        for k in self.kicks:
            i = int(k * SR)
            n = min(int(0.32 * SR), N - i)
            x = np.arange(n) / SR
            duck[i : i + n] = np.minimum(duck[i : i + n], 1 - duck_depth * np.exp(-x / 0.1))
        # ping-pong delay: dotted eighth, filtered repeats
        d = int(self.beat * 0.75 * SR)
        src = filt(filt(self.delay.mean(axis=1), "highpass", 400), "lowpass", 4500)
        echo = np.zeros((N, 2))
        for k in range(1, 7):
            if k * d >= N:
                break
            echo[k * d :, k % 2] += src[: N - k * d] * 0.55**k
        verb = np.stack([fftconvolve(self.send[:, c], rnd_ir(2.8, 0.7)[:, c])[:N] for c in range(2)], axis=1)
        music = self.music * duck[:, None]
        music -= filt(music, "bandpass", [2200, 4200]) * 0.35  # leave room for a voice-over
        # widen: Haas-delay the right channel of everything above 300 Hz, keep the low end mono
        hi = filt(music, "highpass", 300)
        lo = music - hi
        lag = int(0.009 * SR)
        hi_w = hi.copy()
        hi_w[lag:, 1] = hi[:-lag, 1]
        mid, side = (hi_w[:, 0] + hi_w[:, 1]) / 2, (hi_w[:, 0] - hi_w[:, 1]) / 2 * 1.3
        music = lo.mean(axis=1, keepdims=True) + np.stack([mid + side, mid - side], axis=1)
        drums = self.drums.copy()
        drums -= filt(drums, "highpass", 13000) * 0.6  # tame hat fizz
        out = music + drums + self.sfx + verb * 0.5 + echo * 0.6
        out = filt(out, "highpass", 30)
        out -= filt(out, "bandpass", [180, 320]) * 0.15  # clear low-mid mud
        out += filt(out, "lowpass", 110) * 0.06 + filt(out, "highpass", 10000) * 0.05  # warmth + air
        # bus compressor: 2:1 above -14 dBFS RMS, 10 ms attack / 150 ms release
        lvl = np.sqrt(np.convolve(np.mean(out**2, axis=1), np.ones(441) / 441, mode="same") + 1e-12)
        over = np.maximum(0, 20 * np.log10(lvl) + 14)
        gr = over * 0.5
        a = np.exp(-1 / (0.15 * SR))
        gr = lfilter([1 - a], [1, -a], gr)
        out *= (10 ** (-gr / 20))[:, None]
        return np.tanh(out * 1.25) / 1.25


def epiano(f, dur, vel=1.0):
    """Rhodes-like FM electric piano: soft bell attack, warm body, slow tremolo."""
    x = seconds(dur)
    idx = 1.6 * vel * np.exp(-x / 0.35) + 0.25
    tone_ = np.sin(2 * np.pi * f * x + idx * np.sin(2 * np.pi * f * x))
    tine = 0.25 * vel * np.sin(2 * np.pi * f * 14 * x) * np.exp(-x / 0.03)
    env = np.minimum(1, x / 0.004) * np.exp(-x / 1.6) * np.minimum(1, np.clip(dur - x, 0, None) / 0.15)
    s = (tone_ + tine) * env
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * x)
    return np.stack([s * trem, s * (2 - trem)], axis=1) * 0.5


def chord_ep(notes, dur, vel=0.8, strum=0.012):
    out = np.zeros((int((dur + strum * len(notes)) * SR), 2))
    for k, n in enumerate(notes):
        s = epiano(m(n), dur, vel)
        i = int(k * strum * SR)
        out[i : i + len(s)] += s
    return out / np.sqrt(len(notes))


def soft_kick():
    x = seconds(0.5)
    f = 48 + 90 * np.exp(-x * 28)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.2)
    return np.tanh(body * 1.8) * 0.9


def snare():
    x = seconds(0.35)
    body = np.sin(2 * np.pi * 190 * x) * np.exp(-x / 0.05)
    n = filt(rng.standard_normal(len(x)), "bandpass", [1500, 7000]) * np.exp(-x / 0.09)
    return np.tanh((body * 0.6 + n * 0.8 + clap()[: len(x)] * 0.5) * 1.2)


def shaker():
    x = seconds(0.09)
    return filt(rng.standard_normal(len(x)), "bandpass", [5000, 11000]) * np.sin(np.pi * x / 0.09) ** 2 * 0.5


def coin():
    g = rng.uniform(0.95, 1.08)
    return bell(m(96) * g, 0.6, 3.0, 0.12) * 0.6 + bell(m(103) * g, 0.6, 2.0, 0.08) * 0.4


def reverse_swell(notes, dur=0.6):
    """Reversed reverb-like swell of a chord, ending exactly on the hit."""
    x = seconds(dur)
    s = sum(np.sin(2 * np.pi * m(n) * x) for n in notes) / len(notes)
    n = filt(rng.standard_normal(len(x)), "bandpass", [1500, 9000]) * 0.4
    return (s + n) * (x / dur) ** 3


def flutter():
    """Paper bill flapping past."""
    x = seconds(0.35)
    am = (np.sin(2 * np.pi * 38 * x) > 0) * 0.7 + 0.3
    return filt(rng.standard_normal(len(x)), "bandpass", [800, 3500]) * am * np.sin(np.pi * x / 0.35) * 0.5


def data_blip(n):
    return bell(m(n), 0.12, 0.6, 0.04)


def render_5():
    """5-qism: Hisobotlarning yo'qligi. 120 BPM; A minor (muammo) -> C major (yechim) -> F lift (natija)."""
    M = MixerPro(120)
    g = np.random.default_rng(55)
    # ---------- Scene 1 (0-10.55): mysterious, half-time, money sucked into the void ----------
    M.put("music", 0.0, pad([m(45), m(52), m(57), m(60)], 10.6, cutoff=650, attack=2.0), 0.36, verb=0.35)
    for at, notes in ((0.5, [57, 60, 64]), (2.5, [53, 57, 60]), (4.5, [57, 60, 64]), (6.5, [52, 56, 59])):
        M.put("music", at, chord_ep([n - 12 for n in notes] + [notes[0]], 1.9, 0.5), 0.35, verb=0.4, echo=0.25)
    for k, at in enumerate(np.arange(1.0, 8.5, 0.5)):
        n = [69, 72, 76, 72][k % 4]
        M.put("music", at, filt(epiano(m(n), 0.4, 0.4), "lowpass", 1800), 0.16, -0.3 + 0.2 * (k % 4), echo=0.35)
    for at in np.arange(2.0, 8.5, 1.0):  # half-time heartbeat kick + rim
        M.put("drums", at, soft_kick(), 0.5)
        M.kicks.append(at)
        M.put("drums", at + 0.5, filt(snare(), "highpass", 900), 0.16, 0.1, verb=0.3)
    for at in np.arange(5.5, 8.5, 0.25):
        M.put("drums", at + (0.03 if int(at * 4) % 2 else 0), shaker(), 0.18 * g.uniform(0.6, 1), 0.4)
    for b in np.arange(0.8, 10.0, 0.36):  # bills fluttering into the black hole
        M.put("sfx", b + g.uniform(0, 0.1), flutter(), 0.08 * g.uniform(0.6, 1), g.uniform(-0.9, 0.9))
    swirl = whoosh(9.5, 300, 900)
    pan = np.sin(np.linspace(0, 9, len(swirl)))
    M.put("sfx", 0.6, np.stack([swirl * (1 - pan) / 2, swirl * (1 + pan) / 2], axis=1), 0.12)
    for i in range(5):  # expense rows + red "?"
        M.put("sfx", 0.9 + i * 0.4, ui_click(), 0.12, 0.2)
        M.put("sfx", 1.0 + i * 0.4, data_blip([57, 60, 64, 67, 69][i] + 12), 0.1, -0.2, verb=0.3)
    M.put("sfx", 3.1, glitch_hit(), 0.3, verb=0.3)  # total ???
    M.put("sfx", 4.55, whoosh(0.5, 600, 3000), 0.16, 0.4)
    for at, kind in [(5.2, "out"), (5.9, "in"), (6.6, "out"), (7.25, "in"), (7.9, "out")]:
        M.put("sfx", at, bell(1320 if kind == "out" else 990, 0.25, 0.8, 0.06), 0.11, 0.3 if kind == "out" else -0.3, verb=0.2)
    for at, p in ((5.6, -0.4), (6.6, 0.4), (7.6, -0.4)):
        M.put("sfx", at, glitch_hit(), 0.38, p, verb=0.25)
    M.put("sfx", 7.9, reverse_swell([57, 60, 64, 69], 0.6), 0.3)
    M.put("sfx", 8.5, boom(1.0), 0.75, verb=0.45)
    M.put("sfx", 8.5, snare(), 0.35, verb=0.6)
    M.put("sfx", 8.5, crash(), 0.3)
    M.put("sfx", 8.6, riser(1.95), 0.28)
    # pixel dissolve: quantised digital sparkle in C major pentatonic
    for k, at in enumerate(np.arange(10.55, 11.0, 1 / 32)):
        M.put("sfx", at, data_blip(int(g.choice([72, 74, 76, 79, 81, 84, 86, 88]))), 0.07, g.uniform(-0.9, 0.9), verb=0.2)
    M.put("sfx", 10.5, reverse_swell([60, 64, 67, 72], 0.5), 0.35)

    # ---------- Scene 2 (11-21.75): warm modern groove, C Am F G with 9ths ----------
    M.put("sfx", 11.0, boom(0.8), 0.55, verb=0.35)
    M.put("sfx", 11.0, crash(), 0.24)
    prog2 = [(11, [48, 55, 64, 67, 74], 36), (13, [45, 55, 60, 64, 71], 33), (15, [41, 55, 60, 64, 69], 29), (17, [43, 55, 59, 62, 69], 31),
             (19, [48, 55, 64, 67, 74], 36), (21, [45, 55, 60, 64, 71], 33)]
    for start, notes, root in prog2:
        dur = min(2.0, 21.75 - start)
        for b in (0.0, 0.75, 1.5):  # syncopated e-piano comping
            if b < dur:
                M.put("music", start + b, chord_ep(notes[1:], min(0.7, dur - b), 0.7), 0.42, verb=0.25)
        M.put("music", start, pad([m(n + 12) for n in notes[2:]], dur, cutoff=2400, attack=0.25), 0.1, verb=0.35)
        for b in np.arange(0, dur - 0.01, 0.5):
            M.put("music", start + b, sub(m(root + 12) / 2 if b % 1 else m(root + 12), 0.4), 0.24)
    arp = [76, 79, 84, 79, 74, 79, 83, 79]
    for k, at in enumerate(np.arange(11.0, 21.75, 0.25)):
        if k % 2 == 0:
            M.put("music", at, bell(m(arp[(k // 2) % 8] + 12), 0.3, 1.0, 0.12), 0.05, 0.3 * np.sin(k), echo=0.5)
    for at in np.arange(11.0, 21.75, 0.5):
        M.put("drums", at, soft_kick(), 0.62)
        M.kicks.append(at)
        if int(round(at * 2)) % 2 == 1:
            M.put("drums", at, snare(), 0.3, verb=0.2)
    for k, at in enumerate(np.arange(11.0, 21.75, 0.125)):  # swung 16th hats with velocity
        sw = 0.02 if k % 2 else 0.0
        M.put("drums", at + sw, hat(k % 8 == 4), (0.09 if k % 2 == 0 else 0.045) * g.uniform(0.75, 1.0), 0.35)
    for i in range(4):  # KPI tiles pop in, then count up
        M.put("sfx", T5_KPI + i * 0.12, data_blip([72, 76, 79, 84][i]), 0.16, -0.3 + 0.2 * i, verb=0.2)
    for k, at in enumerate(np.arange(11.8, 14.0, 0.0625)):
        M.put("sfx", at, tick(True), 0.03 * (1 - k / 36), 0.3)
    data = seconds(1.4)
    M.put("sfx", 12.3, np.sin(2 * np.pi * np.cumsum(500 * 2 ** (data / 1.4)) / SR) * np.sin(np.pi * data / 1.4) * 0.3, 0.12, echo=0.3)
    for i in range(5):
        M.put("sfx", 14.2 + i * 0.1, whoosh(0.25, 1500, 4000), 0.07, 0.5)
    M.put("sfx", 15.4, whoosh(0.6, 800, 2500), 0.16)  # re-sort
    M.put("sfx", 16.2, chord_ep([72, 76, 79, 84], 1.2, 1.0), 0.3, verb=0.4, echo=0.3)  # crown
    M.put("sfx", 16.8, bell(m(58), 0.4, 2.0, 0.1), 0.2, verb=0.2)  # flagged
    M.put("sfx", 17.5, ui_click(), 0.4)
    M.put("sfx", 17.52, sub(m(43), 0.12), 0.25)  # toggle thunk
    for k in range(7):
        M.put("sfx", 17.7 + k * 0.06 + 0.45, coin(), 0.18, -0.4 + 0.12 * k, verb=0.2)
    M.put("sfx", 18.0, reverse_swell([67, 72, 76, 79], 0.5), 0.35)
    M.put("sfx", 18.5, boom(0.9), 0.62, verb=0.4)
    M.put("sfx", 18.5, crash(), 0.26)
    M.put("sfx", 18.5, chord_ep([60, 67, 72, 76, 79], 1.6, 1.0), 0.32, verb=0.5)
    for k, f in enumerate((72, 76, 79, 84)):  # report-ready chime
        M.put("sfx", 19.9 + k * 0.07, bell(m(f), 1.4, 1.2, 0.45), 0.09, -0.2 + k * 0.13, verb=0.5, echo=0.3)
    M.put("sfx", 21.0, riser(1.0), 0.26)

    # ---------- Scene 3 (22-32): lift to F, plagal ending F -> C ----------
    M.put("sfx", 21.75, whoosh(0.5, 500, 8000), 0.28, verb=0.3)
    M.put("sfx", 22.0, boom(0.9), 0.6, verb=0.45)
    M.put("sfx", 22.0, crash(), 0.3)
    prog3 = [(22, [41, 57, 60, 64, 69], 29), (24, [43, 55, 59, 62, 67], 31), (26, [40, 55, 59, 64, 67], 28), (28, [45, 57, 60, 64, 72], 33),
             (29, [41, 57, 60, 65, 69], 29), (30, [36, 55, 60, 64, 67, 72], 24)]
    for start, notes, root in prog3:
        dur = 1.0 if start in (28, 29) else 2.0
        M.put("music", start, chord_ep(notes[1:], dur + (1.6 if start == 30 else 0), 0.85), 0.45, verb=0.4, echo=0.2)
        M.put("music", start, pad([m(n + 12) for n in notes[1:4]], dur + (1.2 if start == 30 else 0), cutoff=2600, attack=0.3), 0.14, verb=0.4)
        M.put("music", start, supersaw([m(n) for n in notes[1:4]], dur, cutoff=2800 if start < 27 else 1500), 0.14 if start < 27 else 0.08, verb=0.3)
        for b in np.arange(0, dur - 0.01, 0.5):
            M.put("music", start + b, sub(m(root + 12), 0.45), 0.3 if start < 27 else 0.2)
    melody = [(22, 81), (22.5, 79), (23, 77), (23.5, 76), (24, 74), (24.75, 76), (25.5, 79),
              (26, 76), (26.5, 74), (27, 72), (28, 72), (28.5, 74), (29, 76), (29.5, 77), (30, 79)]
    for at, n in melody:
        M.put("music", at, epiano(m(n), 0.9, 0.9), 0.3, 0.15, verb=0.45, echo=0.35)
        M.put("music", at, bell(m(n + 12), 0.8, 1.2, 0.3), 0.05, -0.15, verb=0.4)
    for at in np.arange(22.0, 26.75, 0.5):
        M.put("drums", at, soft_kick(), 0.66)
        M.kicks.append(at)
        if int(round(at * 2)) % 2 == 1:
            M.put("drums", at, snare(), 0.32, verb=0.25)
    for k, at in enumerate(np.arange(22.0, 26.75, 0.125)):
        M.put("drums", at + (0.02 if k % 2 else 0), hat(k % 4 == 2), (0.09 if k % 2 == 0 else 0.05) * g.uniform(0.75, 1.0), 0.35)
    donut = seconds(1.4)
    M.put("sfx", 22.6, np.sin(2 * np.pi * np.cumsum(300 * 2 ** (1.5 * donut / 1.4)) / SR) * np.sin(np.pi * donut / 1.4), 0.08, echo=0.3)
    for k, n in enumerate([65, 69, 72, 77, 81]):  # donut segments
        M.put("sfx", 22.6 + k * 0.28, data_blip(n + 12), 0.1, -0.4 + 0.2 * k, verb=0.3)
    for i in range(2):
        M.put("sfx", 23.6 + i * 0.2, bell(m([77, 81][i]), 0.5, 1.2, 0.18), 0.14, -0.3 + 0.6 * i, verb=0.3)
    M.put("sfx", 24.5, reverse_swell([65, 69, 72, 77], 0.5), 0.3)
    M.put("sfx", 25.0, boom(0.6), 0.42, verb=0.4)
    for k in range(16):
        M.put("sfx", 25.0 + g.uniform(0, 0.9), coin() if k % 3 == 0 else bell(m(int(g.choice([84, 89, 93, 96, 101]))), 0.8, 1.5, 0.25), 0.05, g.uniform(-0.8, 0.8), verb=0.5)
    M.put("sfx", 27.0, whoosh(0.6, 3000, 800), 0.16, verb=0.4)
    M.put("sfx", 28.3, bell(1760, 3.0, 1.0, 0.9), 0.18, verb=0.6, echo=0.4)
    M.put("sfx", 28.3, bell(2637, 3.0, 0.8, 0.7), 0.07, 0.3, verb=0.6)

    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


T5_KPI = 11.5


def keystroke():
    x = seconds(0.04)
    return filt(rng.standard_normal(len(x)), "bandpass", [1800, 6000]) * np.exp(-x / 0.006) + np.sin(2 * np.pi * 900 * x) * np.exp(-x / 0.004) * 0.3


def rewind(dur=0.45):
    x = seconds(dur)
    f = 1800 * 2 ** (-4 * x / dur)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + sweep_filter(rng.standard_normal(len(x)), 4000, 400) * 0.6) * np.sin(np.pi * x / dur)


def choir(notes, dur):
    """Airy 'aah' swell: detuned sines with slow vibrato."""
    x = seconds(dur)
    v = sum(np.sin(2 * np.pi * m(n) * x + 0.004 * m(n) * np.sin(2 * np.pi * 5 * x) / 5) + 0.5 * np.sin(2 * np.pi * m(n) * 1.004 * x) for n in notes)
    s = v / len(notes) * (x / dur) ** 1.5
    return np.stack([s, np.roll(s, int(0.015 * SR))], axis=1)


def render_6():
    """6-qism: ADUZ kashfiyoti. 4-qism uslubi (v2 Mixer), 120 BPM. D minor -> G major -> C major."""
    M = Mixer()
    # ---------- Scene 1 (0-10.55): tedious form, typing is the rhythm ----------
    M.put("music", 0.0, pad([m(38), m(41), m(45), m(50)], 10.6, cutoff=700, attack=1.5), 0.32, verb=0.3)
    for i, at in enumerate(np.arange(2.0, 8.5, 0.25)):
        x = seconds(0.22)
        cut = 250 + 1500 * ((at - 2) / 6.5) ** 1.5
        note = m(26) if i % 8 not in (6, 7) else m(29)
        M.put("music", at, filt(saw(note, x) * np.exp(-x / 0.12), "lowpass", cut), 0.22)
    for at in np.arange(5.5, 8.5, 0.5):
        M.put("drums", at, kick(0.8), 0.5)
        M.kicks.append(at)
        M.put("drums", at + 0.25, hat(), 0.12, 0.3)
    g = np.random.default_rng(6)
    for f0, dur in [(1.0, .5), (1.7, .5), (2.4, .7), (3.95, .5), (4.4, .5), (5.0, .5), (6.8, .7), (7.6, .7)]:  # typing per field
        for k in np.arange(f0, f0 + dur, 0.0625):
            M.put("sfx", k + g.uniform(0, 0.012), keystroke(), 0.12 * g.uniform(0.6, 1), g.uniform(-0.3, 0.3))
    for at in (1.0, 1.7, 2.4, 3.95, 4.4, 5.0):
        M.put("sfx", at, ui_click(), 0.1, 0.2)
    M.put("sfx", 3.1, glitch_hit(), 0.3, -0.2, verb=0.2)  # wrong format
    M.put("sfx", 3.1, tone(330, 0.15, "sine", 0.002, 0.06), 0.12)
    M.put("sfx", 3.25, tone(262, 0.25, "sine", 0.002, 0.1), 0.12)
    M.put("sfx", 5.7, tone(220, 0.3, "square", 0.005, 0.12), 0.07)  # session expired
    M.put("sfx", 5.95, tone(175, 0.45, "square", 0.005, 0.2), 0.07)
    M.put("sfx", 6.2, ui_click(), 0.25)
    M.put("sfx", 6.3, rewind(0.45), 0.3, verb=0.2)  # form resets
    for at, p in ((5.6, -0.4), (6.6, 0.4), (7.6, -0.4)):
        M.put("sfx", at, glitch_hit(), 0.42, p, verb=0.25)
    M.put("sfx", 8.5, boom(1.0), 0.75, verb=0.4)
    M.put("sfx", 8.5, clap(), 0.4, verb=0.5)
    M.put("sfx", 8.5, crash(), 0.33)
    M.put("sfx", 8.6, riser(1.95), 0.32)
    # doors open: heavy slide spreading out + light "aah"
    slide = whoosh(0.5, 200, 1500)
    M.put("sfx", 10.55, np.stack([slide * np.linspace(.6, 1, len(slide)), slide * np.linspace(.6, 1, len(slide))[::-1]], axis=1), 0.4, verb=0.3)
    M.put("sfx", 10.2, choir([67, 71, 74, 79], 0.85), 0.22, verb=0.6)

    # ---------- Scene 2 (11-21.75): bright four-on-the-floor, G Em C D ----------
    M.put("sfx", 11.0, boom(0.8), 0.55, verb=0.35)
    M.put("sfx", 11.0, crash(), 0.28)
    prog2 = [(11, [55, 59, 62, 66], 43), (13, [52, 55, 59, 62], 40), (15, [48, 52, 55, 59], 36), (17, [50, 54, 57, 62], 38), (19, [55, 59, 62, 66], 43), (21, [52, 55, 59, 62], 40)]
    for start, notes, root in prog2:
        dur = min(2.0, 21.75 - start)
        M.put("music", start, supersaw([m(n) for n in notes], dur, cutoff=2600), 0.3, verb=0.25)
        M.put("music", start, pad([m(n + 12) for n in notes[:3]], dur, cutoff=3000, attack=0.2), 0.12, verb=0.3)
        for b in np.arange(0, dur - 0.01, 0.25):
            M.put("music", start + b, sub(m(root) * (2 if int(b * 4) % 2 else 1), 0.2), 0.28)
        for j, b in enumerate(np.arange(0, dur - 0.01, 0.25)):
            M.put("music", start + b, bell(m(notes[j % 4] + 12), 0.4, 1.4, 0.18), 0.06, 0.35 * np.sin(j * 1.3), verb=0.3)
    for at in np.arange(11.0, 21.75, 0.5):
        M.put("drums", at, kick(), 0.55)
        M.kicks.append(at)
        M.put("drums", at + 0.25, hat(at % 2 > 1.4), 0.14, 0.3)
        if int(round(at * 2)) % 2 == 1:
            M.put("drums", at, clap(), 0.28, verb=0.2)
    for at in np.arange(11.9, 13.5, 0.16):  # stopwatch
        M.put("sfx", at, tick(True), 0.06, 0.5)
    M.put("sfx", 12.0, ui_click(), 0.4)  # START
    M.put("sfx", 12.15, bell(1320, 0.25, 0.8, 0.06), 0.14, 0.3)  # /start
    for k, n in enumerate((67, 71, 74, 79)):  # bot welcome card
        M.put("sfx", 12.6 + k * 0.05, bell(m(n + 12), 0.6, 1.2, 0.2), 0.08, -0.3 + 0.2 * k, verb=0.3)
    M.put("sfx", 13.2, ui_click(), 0.4)  # login
    M.put("sfx", 13.35, ding(m(83)), 0.18, verb=0.3)
    M.put("sfx", 13.5, bell(m(91), 0.8, 1.5, 0.3), 0.1, verb=0.4)  # stopwatch stops at 10 s
    M.put("sfx", 13.7, whoosh(0.5, 600, 3000), 0.2, 0.4)
    for i in range(6):  # tiles cascade, G pentatonic
        M.put("sfx", 14.2 + i * 0.15, bell(m([67, 69, 71, 74, 76, 79][i] + 12), 0.4, 1.5, 0.14), 0.13, -0.4 + i * 0.16, verb=0.25)
    for i in range(6):  # guided tour pings
        M.put("sfx", 15.3 + i * 0.45, bell(m([79, 83, 86, 88, 91, 95][i]), 0.5, 1.0, 0.18), 0.08, -0.5 + 0.2 * i, verb=0.35)
        M.put("sfx", 15.3 + i * 0.45, whoosh(0.18, 2000, 5000), 0.04, -0.5 + 0.2 * i)
    M.put("sfx", 17.2, bell(m(79), 0.3, 1.0, 0.1), 0.12)
    M.put("sfx", 18.5, boom(0.9), 0.65, verb=0.4)  # "1 BOSISH"
    M.put("sfx", 18.5, crash(), 0.3)
    for k, f in enumerate((m(79), m(83), m(86), m(91))):
        M.put("sfx", 18.5 + k * 0.03, bell(f, 1.6, 2.5, 0.5), 0.07, -0.3 + k * 0.2, verb=0.5)
    for k, f in enumerate((m(74), m(79), m(83), m(86))):  # welcome sheet chime
        M.put("sfx", 19.9 + k * 0.07, bell(f, 1.4, 1.2, 0.45), 0.1, -0.2 + k * 0.13, verb=0.5)
    M.put("sfx", 21.0, riser(1.0), 0.28)

    # ---------- Scene 3 (22-32): uplifting C G Am F, journey milestones ----------
    M.put("sfx", 21.75, whoosh(0.5, 500, 8000), 0.3, verb=0.3)
    M.put("sfx", 22.0, boom(0.9), 0.6, verb=0.45)
    M.put("sfx", 22.0, crash(), 0.36)
    prog3 = [(22, [60, 64, 67], 48), (24, [55, 59, 62], 43), (26, [57, 60, 64], 45), (28, [53, 57, 60], 41), (30, [60, 64, 67, 72], 48)]
    for start, notes, root in prog3:
        M.put("music", start, supersaw([m(n) for n in notes] + [m(notes[0] + 12)], 2.0, cutoff=3200 if start < 27 else 1800), 0.3 if start < 27 else 0.22, verb=0.3)
        M.put("music", start, pad([m(n + 12) for n in notes], 2.0 + (0.6 if start == 30 else 0), cutoff=2600, attack=0.3), 0.16, verb=0.4)
        for b in np.arange(0, 1.99, 0.5 if start >= 27 else 0.25):
            M.put("music", start + b, sub(m(root), 0.22 if start < 27 else 0.45), 0.3)
    melody = [(22, 79), (22.5, 76), (23, 79), (23.5, 84), (24, 83), (24.5, 79), (25, 74), (25.5, 79),
              (26, 81), (26.5, 79), (27, 76), (28, 77), (28.5, 76), (29, 72), (29.5, 74), (30, 76)]
    for at, n in melody:
        M.put("music", at, bell(m(n + 12), 1.0, 1.8, 0.35), 0.12, 0.15, verb=0.45)
    for at in np.arange(22.0, 26.75, 0.5):
        M.put("drums", at, kick(1.1), 0.6)
        M.kicks.append(at)
        M.put("drums", at + 0.25, hat(True), 0.13, 0.35)
        if int(round(at * 2)) % 2 == 1:
            M.put("drums", at, clap(), 0.32, verb=0.25)
    path = seconds(2.35)
    M.put("sfx", 22.6, np.sin(2 * np.pi * np.cumsum(350 * 2 ** (2 * path / 2.35)) / SR) * np.sin(np.pi * path / 2.35) * 0.4, 0.08, verb=0.3)
    for k, (at, n) in enumerate(((22.8, 72), (23.5, 76), (24.2, 79), (24.95, 84))):  # milestones
        M.put("sfx", at, bell(m(n + 12), 0.9, 1.6, 0.3), 0.16, -0.3 + 0.2 * k, verb=0.4)
    M.put("sfx", 25.0, boom(0.6), 0.45, verb=0.4)
    for k in range(18):
        M.put("sfx", 25.0 + g.uniform(0, 0.8), bell(m(int(g.choice([84, 88, 91, 96, 100]))), 0.8, 1.5, 0.25), 0.05, g.uniform(-0.8, 0.8), verb=0.5)
    for i in range(3):
        M.put("sfx", 25.2 + i * 0.25, bell(m(79 + 5 * i), 0.5, 1.2, 0.2), 0.14, -0.4 + 0.4 * i, verb=0.3)
    M.put("sfx", 27.0, whoosh(0.6, 3000, 800), 0.18, verb=0.4)
    M.put("sfx", 28.3, bell(1760, 3.0, 1.0, 0.9), 0.2, verb=0.6)
    M.put("sfx", 28.3, bell(2637, 3.0, 0.8, 0.7), 0.08, 0.3, verb=0.6)

    out = M.render()
    out *= np.clip((DUR - t) / 1.2, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


V2 = {4: render_4, 5: render_5, 6: render_6}


CUES = {1: cues_1, 2: cues_2, 3: cues_3}

if __name__ == "__main__":
    episode, out = int(sys.argv[1]), sys.argv[2]
    if episode in V2:
        mix[:] = V2[episode]()
    else:
        bed()
        CUES[episode]()
        mix *= np.clip((DUR - t) / 0.6, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    mix /= np.max(np.abs(mix)) / 0.89
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", out)
