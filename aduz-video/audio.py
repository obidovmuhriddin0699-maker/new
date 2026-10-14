"""Synthesises the music + SFX track for an episode (32 s, 44.1 kHz stereo WAV).

Usage: python3 audio.py <episode number> build/episodeN.wav
Episodes 1-3 use the simple bed below; from 4 on, the v2 engine (needs scipy) with reverb,
sidechain and a full drum/bass/chord arrangement.
Every episode shares the same music bed (Muammo 0-11 s, Yechim 11-22 s, Natija 22-32 s);
the SFX cues follow that episode's animation timeline in episodeN.html.
"""
import os
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


KEY_SHIFT = 0  # semitones; lets an episode reuse another episode's score in a new key


def m(note):
    return midi(note + KEY_SHIFT)


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
        self.front = np.zeros((N, 2))  # bypasses gates (e.g. sounds inside a "sound vacuum")
        self.gates = []  # [(start, end, gain)] — editorial cuts applied to everything but `front`
        self.width = None  # optional [(time, side_gain)] keyframes; default constant 1.3
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
        wk = self.width or [(0, 1.3)]
        width = np.interp(t, [k[0] for k in wk], [k[1] for k in wk])
        mid, side = (hi_w[:, 0] + hi_w[:, 1]) / 2, (hi_w[:, 0] - hi_w[:, 1]) / 2 * width
        music = lo.mean(axis=1, keepdims=True) + np.stack([mid + side, mid - side], axis=1)
        drums = self.drums.copy()
        drums -= filt(drums, "highpass", 13000) * 0.6  # tame hat fizz
        out = music + drums + self.sfx + verb * 0.5 + echo * 0.6
        if self.gates:
            g = np.ones(N)
            for a, b, gain in self.gates:
                i, j, r = int(a * SR), int(b * SR), int(0.03 * SR)
                g[i:j] = np.minimum(g[i:j], gain)
                g[max(0, i - r) : i] = np.minimum(g[max(0, i - r) : i], np.linspace(1, gain, i - max(0, i - r)))
                g[j : j + r] = np.minimum(g[j : j + r], np.linspace(gain, 1, len(g[j : j + r])))
            out *= g[:, None]
        out += self.front
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


# =====================================================================================
# Ovoz arxitekturasi (7-qismdan): qatlamlar, nomlangan tovushlar kutubxonasi va cue-sheet.
# Har bir qism = score (musiqa) + cue-sheet (taymkodli tovushlar ro'yxati). Cue-sheet hujjatga
# ham eksport qilinadi:  python3 audio.py 7 --cuesheet SOUND_ARCHITECTURE_7.md
# =====================================================================================
LAYERS = {
    "L1": ("Musiqa (score)", "Pad, klavishlar, bas, baraban, melodiya. Kick'dan sidechain; 2,2–4,2 kHz diktor uchun bo'shatilgan."),
    "L2": ("Muhit (ambience)", "Sahna 'xonasi': ofis shovqini, havo. Juda past, sezilmas — lekin sukunatni 'jonli' qiladi."),
    "L3": ("UI / foley", "Bosish, tanlash, slider, popup, xato. Musiqa tonalligiga sozlangan."),
    "L4": ("O'tishlar", "Whoosh, swell, riser, squeegee, whip. J-cut: tovush kesimdan oldin boshlanadi."),
    "L5": ("Zarbalar / urg'u", "Boom, crash, glitch, uchqunlar. Kinetik so'zlar bilan bir kadrda."),
    "L6": ("Brend (sonic logo)", "ADUZ ovozli logotipi: 5–1–3 motiv (qo'ng'iroq + elektro-pianino + sub)."),
    "L7": ("Diktor joyi", "Hozircha bo'sh. Diktor qo'shilsa: musiqa −6 dB ducking, SFX −3 dB."),
}


def amb_office(dur=10.3):
    x = seconds(dur)
    br = np.cumsum(rng.standard_normal((len(x), 2)), axis=0)
    br = filt(br - filt(br, "lowpass", 20), "lowpass", 380)
    br /= np.max(np.abs(br)) + 1e-9
    hvac = filt(rng.standard_normal((len(x), 2)), "bandpass", [600, 1400]) * 0.12
    hum = (np.sin(2 * np.pi * 50 * x) + 0.4 * np.sin(2 * np.pi * 100 * x))[:, None] * 0.05
    env = np.minimum(1, x / 0.6) * np.minimum(1, (dur - x) / 0.25)
    return (br * 0.6 + hvac + hum) * env[:, None]


def amb_air(dur=10.7):
    x = seconds(dur)
    n = filt(rng.standard_normal((len(x), 2)), "bandpass", [2500, 7000]) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * x))[:, None]
    return n * 0.25 * (np.minimum(1, x / 1.0) * np.minimum(1, (dur - x) / 0.6))[:, None]


def heartbeat():
    hb = tone(60, 0.3, "sine", 0.002, 0.09) + 0.5 * tone(45, 0.3, "sine", 0.002, 0.12)
    out = np.zeros(int(0.6 * SR))
    out[: len(hb)] += hb
    out[int(0.22 * SR) : int(0.22 * SR) + len(hb)] += hb * 0.6
    return out


def fragment(note=76):
    x = seconds(0.09)
    s = np.sign(np.sin(2 * np.pi * m(note) * x)) * 0.4 + np.sin(2 * np.pi * m(note) * 2 * x) * 0.3
    s = np.round(s * 6) / 6  # bit-crushed
    return filt(s, "bandpass", [500, 6000]) * np.exp(-x / 0.03)


def ui_popup(note=72):
    x = seconds(0.12)
    f = m(note) * (1 + 0.5 * x / 0.12)
    out = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.04) * 0.8
    c = ui_click()
    out[: len(c)] += c * 0.3
    return out


def ui_dropdown():
    out = np.zeros(int(0.3 * SR))
    for k in range(5):
        c = tick(k % 2 == 0)
        i = int(k * 0.045 * SR)
        out[i : i + len(c)] += c * (1 - k * 0.12)
    return out


def ui_error():
    a, b = tone(m(64), 0.15, "sine", 0.002, 0.06), tone(m(60), 0.28, "sine", 0.002, 0.11)
    out = np.zeros(int(0.45 * SR))
    out[: len(a)] += a
    out[int(0.13 * SR) : int(0.13 * SR) + len(b)] += b
    gl = glitch_hit()[: len(out)]
    out[: len(gl)] += gl * 0.3
    return out


def ui_select(note=74):
    s = bell(m(note), 0.45, 1.3, 0.14)
    c = ui_click()
    s[: len(c)] += c * 0.5
    return s


def layer(*sigs):
    """Sum 1-D signals of different lengths (zero-padded)."""
    out = np.zeros(max(len(x) for x in sigs))
    for x in sigs:
        out[: len(x)] += x
    return out


def ui_slider(note=74):
    return layer(bell(m(note), 0.08, 0.5, 0.025), tick(True) * 0.4)


def ui_next():
    return np.concatenate([bell(m(74), 0.09, 0.8, 0.05), bell(m(81), 0.4, 1.0, 0.15)])


def ui_launch(dur=1.35):
    x = seconds(dur)
    f = m(62) * 2 ** (2 * x / dur)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (x / dur) ** 1.5 * 0.5
    return s + sweep_filter(rng.standard_normal(len(x)), 800, 9000) * (x / dur) ** 2 * 0.4


def ui_success():
    out = np.zeros(int(1.6 * SR))
    for k, n in enumerate((74, 78, 81, 86)):
        b = bell(m(n), 1.3, 1.2, 0.45)
        i = int(k * 0.06 * SR)
        out[i : i + len(b)] += b * 0.5
    return out


def fx_collapse():
    x = seconds(0.6)
    f = 1400 * 2 ** (-6 * x / 0.6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - x / 0.6) * 0.6 + sweep_filter(rng.standard_normal(len(x)), 6000, 300) * (1 - x / 0.6) * 0.5
    th = tone(55, 0.6, "sine", 0.002, 0.12)
    s[int(0.42 * SR) :] += th[: len(s) - int(0.42 * SR)] * 0.9
    return s


def fx_strike():
    return sweep_filter(rng.standard_normal(int(0.25 * SR)), 4000, 900) * np.exp(-seconds(0.25) / 0.08) * 0.8


def sparkle(seed=1):
    gg = np.random.default_rng(seed)
    out = np.zeros((int(1.8 * SR), 2))
    for _ in range(16):
        b = bell(m(int(gg.choice([86, 88, 90, 93, 95, 98]))), 0.8, 1.5, 0.25)
        i, p = int(gg.uniform(0, 0.9) * SR), gg.uniform(-0.8, 0.8)
        out[i : i + len(b), 0] += b * np.sqrt(0.5 * (1 - p)) * 0.3
        out[i : i + len(b), 1] += b * np.sqrt(0.5 * (1 + p)) * 0.3
    return out


def squeegee_fx():
    x = seconds(0.45)
    swish = sweep_filter(rng.standard_normal(len(x)), 1500, 9000) * np.sin(np.pi * x / 0.45) ** 1.2
    squeak = np.sin(2 * np.pi * np.cumsum(1800 + 700 * x / 0.45) / SR) * np.exp(-((x - 0.3) / 0.05) ** 2) * 0.15
    return swish + squeak


def whip():
    w = whoosh(0.4, 300, 7000)
    return np.stack([w * np.linspace(1, 0.15, len(w)), w * np.linspace(0.15, 1, len(w))], axis=1)


def brand_logo(tonic=62):
    """ADUZ sonic logo: 5-1-3 motif over the tonic (tonic-relative so it fits every key)."""
    out = np.zeros((int(3.0 * SR), 2))
    for k, iv in enumerate((7, 12, 16)):
        n = tonic + 12 + iv
        b = bell(m(n + 12), 2.2, 1.6, 0.6) * 0.45
        e = epiano(m(n), 2.2, 0.9)
        i = int(k * 0.25 * SR)
        out[i : i + len(b), 0] += b * (0.8 - 0.2 * k) + e[: len(b), 0] * 0.6
        out[i : i + len(b), 1] += b * (0.4 + 0.2 * k) + e[: len(b), 1] * 0.6
    s = sub(m(tonic - 24), 2.5) * np.exp(-seconds(2.5) / 0.9)
    out[: len(s)] += s[:, None] * 0.35
    return out


# name -> (layer, generator(arg), description)
SOUNDS = {
    "amb.office": ("L2", lambda a=None: amb_office(a or 10.3), "Ofis fon shovqini: past 'xona tovushi', ventilyatsiya, 50 Hz g'uvullash"),
    "amb.air": ("L2", lambda a=None: amb_air(a or 10.7), "Yorug', ochiq havo — yechim sahnasi muhiti"),
    "ui.popup": ("L3", lambda a=None: ui_popup(a or 72), "Yumshoq 'pop' — popup paydo bo'lishi (balandligi sozlanadi)"),
    "ui.dropdown": ("L3", lambda a=None: ui_dropdown(), "Ochiluvchi ro'yxat 'shitirlashi' (5 ta tez tik)"),
    "ui.error": ("L3", lambda a=None: ui_error(), "Xato: pastga tushuvchi ikki nota + glitch"),
    "ui.tap": ("L3", lambda a=None: ui_click(), "Barmoq bosishi"),
    "ui.select": ("L3", lambda a=None: ui_select(a or 74), "Tanlash: klik + tonallikdagi qo'ng'iroqcha"),
    "ui.slider": ("L3", lambda a=None: ui_slider(a or 74), "Slider qadami: ko'tariluvchi mayda tik"),
    "ui.next": ("L3", lambda a=None: ui_next(), "'Keyingi': ikki nota yuqoriga"),
    "ui.launch": ("L3", lambda a=None: ui_launch(), "Ishga tushirish: ko'tariluvchi ton + shovqin"),
    "ui.success": ("L3", lambda a=None: ui_success(), "Muvaffaqiyat: D-major arpedjio akkordi"),
    "fx.fragment": ("L3", lambda a=None: fragment(a or 76), "Suzuvchi jargon bo'lagi: bit-crush 'blip'"),
    "fx.strike": ("L3", lambda a=None: fx_strike(), "Matn ustidan chizish: tushuvchi 'chirt'"),
    "fx.collapse": ("L5", lambda a=None: fx_collapse(), "Ilova yopilishi: pastga 'so'rilish' + zarba"),
    "fx.heartbeat": ("L5", lambda a=None: heartbeat(), "Yurak urishi — ovoz vakuumi ichida"),
    "tr.whoosh": ("L4", lambda a=None: whoosh(0.4, 600, 3000), "Yumshoq whoosh: telefon/ekran kirishi"),
    "tr.slide": ("L4", lambda a=None: whoosh(0.35, 900, 4000), "Ekranlar orasida sirpanish"),
    "tr.swell": ("L4", lambda a=None: reverse_swell(a or [62, 66, 69, 74], 0.45), "Teskari swell (J-cut): keyingi kadrga 'nafas'"),
    "tr.riser": ("L4", lambda a=None: riser(a or 0.9), "Riser — keskin kesiladi (montaj usuli)"),
    "tr.squeegee": ("L4", lambda a=None: squeegee_fx(), "Squeegee o'tishi: yuqori chastotali 'shirr' + rezina g'ichirlashi"),
    "tr.whip": ("L4", lambda a=None: whip(), "Whip-pan: chapdan o'ngga tez o'tuvchi whoosh"),
    "imp.glitch": ("L5", lambda a=None: glitch_hit(), "Qizil kinetik so'z zarbasi"),
    "imp.boom": ("L5", lambda a=None: boom(a or 1.0), "Katta zarba: sub + thump"),
    "imp.clap": ("L5", lambda a=None: clap(), "Zarba ustidagi clap qatlami"),
    "imp.crash": ("L5", lambda a=None: crash(), "Crash tarelka (yumshatilgan)"),
    "imp.sparkle": ("L5", lambda a=None: sparkle(a or 1), "Uchqunlar: D-pentatonik qo'ng'iroqchalar to'dasi"),
    "brand.logo": ("L6", lambda a=None: brand_logo(a or 62), "ADUZ sonic logo (5–1–3 motiv)"),
}

# (time, sound, gain, pan, reverb, echo, izoh, arg)
CUES_7 = [
    (0.0, "amb.office", 0.10, 0, 0, 0, "Ofis xonasi — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.16, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    *[(0.8 + i * 0.55, "fx.fragment", 0.07, (-1) ** i * 0.6, 0.15, 0.3, f"Jargon bo'lagi #{i + 1}", [64, 67, 71, 74, 76, 79][i % 6]) for i in range(12)],
    (1.2, "ui.popup", 0.18, 0.1, 0.2, 0, "Popup: 'Bid strategiyasi'", 76),
    (2.2, "ui.dropdown", 0.2, 0.2, 0.1, 0, "Ochiluvchi ro'yxat", None),
    (3.2, "ui.popup", 0.18, -0.1, 0.2, 0, "Popup: piksel kodi", 71),
    (4.2, "ui.error", 0.22, 0, 0.2, 0, "To'lov usuli tasdiqlanmagan", None),
    (5.0, "ui.popup", 0.18, 0.2, 0.2, 0, "Qo'llanma.pdf — 128 sahifa", 67),
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: CPM? CTR?", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: QAYERDAN BOSHLASH?", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: QO'LLANMA: 128 SAHIFA", None),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "CHALKASH — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.6, "fx.collapse", 0.5, 0, 0.35, 0, "Ilova nuqtaga 'so'riladi'", None),
    (9.75, "fx.heartbeat", 0.45, 0, 0.2, 0, "OVOZ VAKUUMI: faqat yurak", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi kesimdan oldin", [62, 66, 69, 74]),
    (10.55, "tr.squeegee", 0.45, 0, 0.25, 0, "Squeegee o'tishi", None),
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    *[(11.6 + i * 0.15, "ui.select", 0.12, -0.3 + 0.3 * i, 0.25, 0.2, f"Katta tugma #{i + 1}", [74, 78, 81][i]) for i in range(3)],
    (13.0, "ui.select", 0.24, 0.2, 0.2, 0, "Tanlandi: Reklama berish", 81),
    (13.2, "tr.slide", 0.14, 0.5, 0.1, 0, "1-qadam ekrani", None),
    *[(13.4 + i * 0.12, "ui.popup", 0.1, -0.3 + 0.3 * i, 0.2, 0, f"Variant #{i + 1}", [74, 76, 78][i]) for i in range(3)],
    (13.7, "ui.select", 0.1, 0.3, 0.3, 0.3, "Maslahat pufagi", 86),
    (14.0, "ui.select", 0.24, -0.2, 0.2, 0, "Tanlandi: Do'kon", 78),
    (14.3, "tr.slide", 0.14, 0.5, 0.1, 0, "2-qadam ekrani", None),
    *[(14.7 + i * 0.08, "ui.slider", 0.08, -0.4 + 0.08 * i, 0.1, 0, f"Slider qadami {i + 1}/10", [62, 64, 66, 67, 69, 71, 73, 74, 76, 78][i]) for i in range(10)],
    (15.75, "ui.next", 0.22, 0.2, 0.25, 0.2, "Keyingi", None),
    (16.0, "tr.slide", 0.14, 0.5, 0.1, 0, "3-qadam ekrani", None),
    (16.8, "ui.tap", 0.35, 0.1, 0, 0, "Ishga tushirish bosildi", None),
    (16.85, "ui.launch", 0.25, 0, 0.3, 0.2, "Ishga tushmoqda...", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: 3 QADAM oldidan", [66, 69, 74, 78]),
    (18.2, "ui.success", 0.3, 0, 0.4, 0.3, "Ishga tushdi!", None),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "3 QADAM — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 3),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Kampaniya ishga tushdi oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    *[(22.8 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(4)],
    *[(23.0 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [74, 78, 81, 86][i]) for i in range(4)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [69, 74, 78, 81]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 5),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [81, 86, 90][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO — logotip bilan bir kadrda", 62),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 93),
]

SCORE_7 = [
    ("0:00–0:09.5", "Muammo · E-minor, tashvishli minimal", "Qorong'i pad; offbeat bo'g'iq elektro-pianino; 2 s dan filtrlangan bas pulsi; 3 s dan yumshoq 16-lik hat; 5.5 s dan kick. 9.5 s da hammasi keskin to'xtaydi."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Montaj kesimi: musiqa, reverb va dumlar −30 dB ga keskin o'chiriladi (gate). Faqat xona shovqini, ilova yopilishi va yurak urishi qoladi. Keyin J-cut swell yechim tonalligida."),
    ("0:11–0:21.75", "Yechim · D-major, ataylab siyrak", "Faqat 4 qatlam: half-time kick + snap, marimba-uslub qo'ng'iroqcha, iliq Rhodes (D–Bm–G–A), sub. 'Sodda' xabarini aranjirovka ham aytadi."),
    ("0:22–0:27", "Natija · D-major, to'liq", "D–A–Bm–G: to'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi."),
    ("0:27–0:32", "Yakun · brend", "Baraban o'chadi; ADUZ sonic logo (A–D–F#) logotip bilan bir kadrda; D akkord bilan so'nadi."),
]


def score_7(M):
    # Scene 1: E minor, anxious; cut dead at 9.5 for the sound vacuum
    M.put("music", 0.0, pad([m(40), m(43), m(47), m(50)], 9.5, cutoff=700, attack=1.5, release=0.05), 0.3, verb=0.3)
    for at in np.arange(1.25, 9.4, 0.5):
        M.put("music", at, filt(chord_ep([64, 67, 71], 0.3, 0.5), "lowpass", 1500), 0.22, 0.2, echo=0.2)
    for i, at in enumerate(np.arange(2.0, 9.5, 0.25)):
        x = seconds(0.22)
        cut = 250 + 1500 * ((at - 2) / 7.5) ** 1.5
        M.put("music", at, filt(saw(m(28) if i % 8 not in (6, 7) else m(31), x) * np.exp(-x / 0.12), "lowpass", cut), 0.2)
    for k, at in enumerate(np.arange(3.0, 9.5, 0.125)):
        M.put("drums", at, hat(), 0.05 if k % 2 else 0.08, 0.3)
    for at in np.arange(5.5, 9.5, 0.5):
        M.put("drums", at, soft_kick(), 0.5)
        M.kicks.append(at)
    # Scene 2: D major, deliberately sparse
    prog2 = [(11, [62, 66, 69, 73], 38), (13, [59, 62, 66, 69], 35), (15, [55, 59, 62, 66], 31), (17, [57, 61, 64, 69], 33), (19, [62, 66, 69, 73], 38), (21, [59, 62, 66, 69], 35)]
    for start, notes, root in prog2:
        dur = min(2.0, 21.75 - start)
        M.put("music", start, chord_ep(notes, dur, 0.6), 0.38, verb=0.3)
        for b in np.arange(0, dur - 0.01, 1.0):
            M.put("music", start + b, sub(m(root + 12), 0.6), 0.26)
        for j, b in enumerate(np.arange(0, dur - 0.01, 0.5)):
            M.put("music", start + b + 0.25, bell(m(notes[(j * 2) % 4] + 12), 0.35, 0.5, 0.15), 0.07, 0.3 * (-1) ** j, verb=0.2, echo=0.35)
    for at in np.arange(11.0, 21.75, 1.0):
        M.put("drums", at, soft_kick(), 0.55)
        M.kicks.append(at)
        M.put("drums", at + 0.5, filt(clap(), "highpass", 1200), 0.2, 0.1, verb=0.25)
    for k, at in enumerate(np.arange(11.0, 21.75, 0.25)):
        M.put("drums", at + (0.02 if k % 2 else 0), shaker(), 0.07, 0.4)
    # Scene 3: D major, full
    prog3 = [(22, [62, 66, 69], 38), (24, [57, 61, 64], 33), (26, [59, 62, 66], 35), (28, [55, 59, 62], 31), (30, [62, 66, 69, 74], 38)]
    for start, notes, root in prog3:
        full = start < 27
        M.put("music", start, chord_ep(notes + [notes[0] + 12], 2.0 + (1.5 if start == 30 else 0), 0.85), 0.42, verb=0.4, echo=0.2)
        M.put("music", start, supersaw([m(n) for n in notes], 2.0, cutoff=3000 if full else 1500), 0.16 if full else 0.08, verb=0.3)
        for b in np.arange(0, 1.99, 0.5):
            M.put("music", start + b, sub(m(root + 12), 0.45), 0.3 if full else 0.18)
    melody = [(22, 78), (22.5, 81), (23, 86), (23.5, 85), (24, 81), (24.5, 76), (25, 81), (25.5, 85), (26, 83), (26.5, 81), (28, 79), (29, 78), (29.5, 76), (30, 74)]
    for at, n in melody:
        M.put("music", at, epiano(m(n), 0.9, 0.9), 0.28, 0.15, verb=0.45, echo=0.35)
        M.put("music", at, bell(m(n + 12), 0.8, 1.2, 0.3), 0.05, -0.15, verb=0.4)
    for at in np.arange(22.0, 26.75, 0.5):
        M.put("drums", at, soft_kick(), 0.65)
        M.kicks.append(at)
        if int(round(at * 2)) % 2 == 1:
            M.put("drums", at, snare(), 0.3, verb=0.25)
    for k, at in enumerate(np.arange(22.0, 26.75, 0.125)):
        M.put("drums", at + (0.02 if k % 2 else 0), hat(k % 4 == 2), 0.08 if k % 2 == 0 else 0.045, 0.35)


FRONT = {"amb.office", "fx.collapse", "fx.heartbeat"}  # stay audible through the vacuum gate


def render_cues(M, cues):
    for at, name, gain, pan, verb, echo, _note, arg in cues:
        layer, gen, _ = SOUNDS[name]
        sig = gen(arg) if arg is not None else gen()
        if name in FRONT:
            M.put("front", at, sig, gain, pan)
        else:
            M.put("sfx", at, sig, gain, pan, verb=verb, echo=echo)


def render_7():
    """7-qism: Platforma interfeysi bilan tanishuv. Score + cue-sheet (CUES_7)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # sound vacuum: hard editorial cut, only `front` survives
    score_7(M)
    render_cues(M, CUES_7)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


def cuesheet_md(ep, cues, score):
    db = lambda g: f"{20 * np.log10(g):+.0f} dB"
    tc = lambda s: f"{int(s // 60)}:{s % 60:05.2f}"
    lines = [f"# ADUZ {ep}-qism — ovoz arxitekturasi va cue-sheet", "",
             f"Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py {ep} --cuesheet SOUND_ARCHITECTURE_{ep}.md`).", "",
             "## Qatlamlar", "", "| Qatlam | Nomi | Vazifasi |", "|---|---|---|"]
    lines += [f"| {k} | {n} | {d} |" for k, (n, d) in LAYERS.items()]
    lines += ["", "## Tovushlar kutubxonasi", "", "| Nomi | Qatlam | Tavsif |", "|---|---|---|"]
    lines += [f"| `{k}` | {v[0]} | {v[2]} |" for k, v in SOUNDS.items()]
    lines += ["", "## Musiqa (score)", "", "| Vaqt | Bo'lim | Aranjirovka |", "|---|---|---|"]
    lines += [f"| {a} | {b} | {c} |" for a, b, c in score]
    lines += ["", "## Cue-sheet", "", "| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |", "|---|---|---|---|---|---|---|"]
    for at, name, gain, pan, verb, echo, note, arg in sorted(cues, key=lambda c: c[0]):
        p = "C" if abs(pan) < 0.05 else (f"L{abs(pan) * 100:.0f}" if pan < 0 else f"R{pan * 100:.0f}")
        lines.append(f"| {tc(at)} | {SOUNDS[name][0]} | `{name}` | {db(gain)} | {p} | {verb:.0%} | {note} |")
    lines += ["", "## Master zanjir", "",
              "Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → "
              "hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → "
              "iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.", ""]
    return "\n".join(lines)


# ---------- 8-qism uchun yangi tovushlar ----------
def fx_window(note=67):
    x = seconds(0.18)
    f = m(note) * (0.7 + 0.6 * x / 0.18)
    return layer(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.06) * 0.7, ui_click() * 0.3)


def fx_paper():
    x = seconds(0.4)
    am = 0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 9 * x + np.sin(2 * np.pi * 3 * x)))
    return filt(rng.standard_normal(len(x)), "bandpass", [1200, 7000]) * am * np.sin(np.pi * x / 0.4) * 0.6


def fx_sticky():
    x = seconds(0.12)
    return layer(filt(rng.standard_normal(len(x)), "lowpass", 1800) * np.exp(-x / 0.02), tone(140, 0.12, "sine", 0.001, 0.03) * 0.8)


def fx_tab():
    return layer(tick(True) * 0.7, bell(m(88), 0.06, 0.4, 0.015) * 0.4)


def fx_magnet(dur=1.3):
    x = seconds(dur)
    f = 55 * 2 ** (x / dur)
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * (4 + 14 * x / dur) * x)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR + 2.5 * np.sin(2 * np.pi * f * 2 * x)) * trem * (x / dur) ** 0.7
    return np.tanh(s * 1.5) * np.minimum(1, (dur - x) / 0.05) * 0.6


def fx_absorb(note=74):
    x = seconds(0.2)
    f = m(note) * 2 ** (-x / 0.2)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.07) * 0.6 + tone(70, 0.2, "sine", 0.001, 0.05) * 0.5


def fx_snap():
    return layer(ui_click(), tone(90, 0.15, "sine", 0.001, 0.04) * 0.9, filt(rng.standard_normal(1500), "highpass", 5000) * np.exp(-seconds(1500 / SR) / 0.003) * 0.4)


def ui_cart(note=79):
    return layer(ui_popup(note), bell(m(note + 12), 0.5, 2.2, 0.15) * 0.5)


def ui_pay():
    return layer(ui_click(), np.concatenate([np.zeros(int(0.12 * SR)), ui_success()]))


def fx_pulse(note=86):
    return bell(m(note), 0.3, 0.6, 0.08) * 0.8


SOUNDS.update({
    "fx.window": ("L3", lambda a=None: fx_window(a or 67), "Oyna ochilishi: yumshoq 'bloop' (balandligi sozlanadi)"),
    "fx.paper": ("L3", lambda a=None: fx_paper(), "Qog'oz shitirlashi (daftar, chek)"),
    "fx.sticky": ("L3", lambda a=None: fx_sticky(), "Stiker 'shap' etib yopishishi"),
    "fx.tab": ("L3", lambda a=None: fx_tab(), "Brauzer tabi ochilishi"),
    "fx.magnet": ("L4", lambda a=None: fx_magnet(a or 1.3), "Magnit maydoni: ko'tariluvchi tremolo g'uvullash"),
    "fx.absorb": ("L5", lambda a=None: fx_absorb(a or 74), "Bo'lak magnitga 'yutilishi': pastga tushuvchi ton + thump"),
    "fx.snap": ("L3", lambda a=None: fx_snap(), "Karta joyiga 'chiq' etib tushishi"),
    "ui.cart": ("L3", lambda a=None: ui_cart(a or 79), "Savatchaga qo'shish: pop + qo'ng'iroqcha"),
    "ui.pay": ("L3", lambda a=None: ui_pay(), "To'lov: klik + muvaffaqiyat akkordi"),
    "fx.pulse": ("L3", lambda a=None: fx_pulse(a or 86), "Hub impulsi: ma'lumot oqimi"),
    "tr.implode": ("L4", lambda a=None: layer(reverse_swell([59, 62, 66, 71], 0.55) * 0.8, whoosh(0.55, 6000, 300) * 0.6), "Implosion: hamma narsa markazga so'riladi"),
    "tr.flip": ("L4", lambda a=None: layer(whoosh(0.18, 2000, 6000), np.concatenate([np.zeros(int(0.2 * SR)), whoosh(0.2, 6000, 1500)])), "Karta aylanishi: ikki marta 'fvip'"),
})

# Scattered pan positions for scene 1: each desk piece sounds from where it is on screen.
_P8 = [(0.5, "fx.window", -0.6, 62), (0.9, "fx.window", 0.7, 66), (1.3, "fx.window", 0.4, 69), (2.0, "fx.paper", -0.6, None), (2.4, "fx.sticky", 0.3, None),
       (2.6, "fx.sticky", 0.8, None), (3.0, "fx.tab", 0.3, None), (3.7, "fx.window", -0.5, 64), (4.4, "fx.paper", 0.5, None), (4.8, "fx.sticky", -0.2, None)]
CUES_8 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Ish stoli xonasi", 10.4),
    *[(at, name, 0.2 if name != "fx.paper" else 0.16, pan, 0.25, 0.25, f"Stolda yangi bo'lak ({name.split('.')[1]}) — ekrandagi joyidan eshitiladi", arg) for at, name, pan, arg in _P8],
    *[(3.05 + k * 0.07, "fx.tab", 0.07, 0.3 + 0.03 * k, 0.1, 0, f"Brauzer tabi #{k + 2}", None) for k in range(6)],
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: QAYSI EXCEL?", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: QAYSI CHAT?", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: CHEK QAYERDA?", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: kamera uzoqlashishi oldidan", [59, 62, 66, 71]),
    (8.25, "tr.whoosh", 0.25, 0, 0.3, 0, "Kamera orqaga tortiladi — butun stol", None),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "TARQOQ — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.28, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser", 1.9),
    (10.45, "tr.implode", 0.5, 0, 0.35, 0, "Implosion o'tishi (J-cut)", None),
    (11.0, "imp.boom", 0.55, 0, 0.4, 0, "Yechim: magnit yoqiladi", 0.8),
    (11.0, "fx.magnet", 0.42, 0, 0.3, 0, "Magnit maydoni kuchayadi", 1.3),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit", 10.7),
    *[(11.25 + i * 0.11, "fx.absorb", 0.24, (-1) ** i * (0.8 - i * 0.1), 0.25, 0.15, f"Bo'lak #{i + 1} yutildi — chetdan markazga", [74, 76, 78, 81, 83, 86, 88, 90][i]) for i in range(8)],
    (12.25, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: telefon paydo bo'lishi", [62, 66, 69, 74]),
    (12.3, "fx.snap", 0.35, 0, 0.2, 0, "Logo telefonga aylanadi", None),
    (12.5, "ui.select", 0.12, 0, 0.3, 0.3, "ADUZ logotipi", 86),
    (12.8, "tr.slide", 0.16, 0.6, 0.1, 0, "Kategoriyalar kirib keladi", None),
    (13.6, "ui.select", 0.24, -0.2, 0.2, 0, "Tanlandi: Moda", 78),
    *[(13.8 + i * 0.1, "fx.snap", 0.12, -0.3 if i % 2 == 0 else 0.3, 0.15, 0, f"Kanal kartasi #{i + 1} joyiga tushdi", None) for i in range(6)],
    *[(a, "ui.tap", 0.3, -0.2 if i % 2 == 0 else 0.3, 0, 0, f"'+' bosildi #{i + 1}", None) for i, a in enumerate([14.6, 15.0, 15.4, 15.8, 16.2])],
    *[(a + 0.45, "ui.cart", 0.2, 0.6, 0.2, 0.2, f"Savatchaga tushdi — {i + 1}", [74, 76, 78, 81, 83][i]) for i, a in enumerate([14.6, 15.0, 15.4, 15.8, 16.2])],
    (16.6, "tr.slide", 0.18, 0, 0.15, 0, "Savatcha ochiladi", None),
    (17.6, "ui.pay", 0.32, 0, 0.35, 0.3, "Bitta to'lov", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: BITTA JOY oldidan", [66, 69, 74, 78]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "BITTA JOY — zarba", 0.9),
    (18.5, "imp.crash", 0.25, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 7),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Buyurtma qabul qilindi", None),
    (21.2, "tr.riser", 0.24, 0, 0, 0, "J-cut: aylanish oldidan", 0.55),
    (21.75, "tr.flip", 0.4, 0, 0.2, 0, "Karta aylanishi o'tishi", None),
    (22.0, "imp.boom", 0.5, 0, 0.45, 0, "Natija boshlanishi", 0.8),
    (22.3, "fx.snap", 0.3, 0, 0.3, 0, "ADUZ hub markazi", None),
    *[(22.6 + i * 0.15, "ui.select", 0.12, [0, 0.7, 0.7, 0, -0.7, -0.7][i], 0.3, 0.2, f"Kategoriya: {['Yangiliklar', 'Moda', 'Biznes', 'Taʼlim', 'Sport', 'Oziq-ovqat'][i]}", [79, 83, 86, 88, 91, 95][i]) for i in range(6)],
    *[(23.4 + k * 0.4, "fx.pulse", 0.05, (-1) ** k * 0.6, 0.3, 0.4, "Hub bo'ylab impuls", [91, 95, 98, 95][k % 4]) for k in range(8)],
    (24.1, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: pillar oldidan", [67, 71, 74, 79]),
    *[(24.6 + i * 0.2, "ui.cart", 0.16, -0.5 + 0.5 * i, 0.3, 0.2, f"Pill: 1 {['ilova', 'to‘lov', 'hisobot'][i]}", [79, 83, 86][i]) for i in range(3)],
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.42, 0, 0.5, 0, "Uchqunlar", 9),
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (G tonallikda)", 55),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 91),
]

SCORE_8 = [
    ("0:00–0:10.5", "Muammo · B-minor, 'tarqoq'", "Pad + filtrlangan bas. Plucklar har xil vaqtda, stereo maydonning turli nuqtalarida (poliritm 3:4, sidechain'siz — beat'ga bo'ysunmaydi) — tovush ham tarqoq. 5.5 s dan kick, 8.5 s dan riser."),
    ("0:10.5–0:12.3", "Magnit · o'tish", "Implosion: hamma tovush markazga so'riladi; magnit g'uvullashi; bo'laklar chetdan markazga 'yutiladi'. Stereo kenglik 1,7 → 0,35 ga qisqaradi — tovush tom ma'noda markazga yig'iladi."),
    ("0:12.3–0:21.75", "Yechim · D-major, 'yig'ilgan'", "Hamma narsa to'rga tushadi: to'g'ri 4/4 kick, clap, 8-lik hat, Rhodes D–Bm–G–A, sub. Plucklar markazda, beat'ga qulflangan."),
    ("0:22–0:27", "Natija · G-major, to'liq", "G–D–Em–C: supersaw, Rhodes + qo'ng'iroqcha melodiyasi, to'liq baraban."),
    ("0:27–0:32", "Yakun · brend", "Baraban o'chadi, ADUZ sonic logo (G tonikada: D–G–B), G akkord bilan so'nadi."),
]


def score_8(M):
    g = np.random.default_rng(88)
    # Scene 1: B minor; scattered polyrhythmic plucks, each from a random place in the stereo field
    M.put("music", 0.0, pad([m(47), m(50), m(54), m(59)], 10.5, cutoff=750, attack=1.2), 0.24, verb=0.35)
    for k, at in enumerate(np.arange(0.6, 10.3, 1 / 3)):  # 3-against-4 pluck line
        M.put("sfx", at, bell(m([71, 74, 78, 81, 78, 74][k % 6]), 0.25, 0.6, 0.09), 0.11, g.uniform(-0.95, 0.95), verb=0.25, echo=0.25)
    for i, at in enumerate(np.arange(2.0, 8.5, 0.25)):
        x = seconds(0.22)
        cut = 250 + 1500 * ((at - 2) / 6.5) ** 1.5
        M.put("music", at, filt(saw(m(35) if i % 8 not in (6, 7) else m(38), x) * np.exp(-x / 0.12), "lowpass", cut), 0.2)
    for at in np.arange(5.5, 8.5, 0.5):
        M.put("drums", at, soft_kick(), 0.5)
        M.kicks.append(at)
        M.put("drums", at + 0.25, hat(), 0.07, g.uniform(-0.6, 0.6))
    # Scene 2 (from 12.3, after the magnet): D major, everything on the grid and centred
    M.put("music", 11.0, pad([m(50), m(57), m(62), m(66)], 1.4, cutoff=1200, attack=0.8), 0.2, verb=0.4)
    prog2 = [(12.3, [62, 66, 69, 73], 38), (13.3, [59, 62, 66, 69], 35), (15.3, [55, 59, 62, 66], 31), (17.3, [57, 61, 64, 69], 33), (19.3, [62, 66, 69, 73], 38), (21.3, [59, 62, 66, 69], 35)]
    for start, notes, root in prog2:
        dur = min(2.0 if start > 12.5 else 1.0, 21.75 - start)
        for b in (0.0, 0.75, 1.5):
            if b < dur:
                M.put("music", start + b, chord_ep(notes, min(0.7, dur - b), 0.7), 0.38, verb=0.25)
        for b in np.arange(0, dur - 0.01, 0.5):
            M.put("music", start + b, sub(m(root + 12), 0.4), 0.26)
        for j, b in enumerate(np.arange(0, dur - 0.01, 0.25)):
            M.put("music", start + b, bell(m(notes[j % 4] + 12), 0.25, 0.7, 0.1), 0.045, 0.0, echo=0.3)
    for at in np.arange(12.5, 21.75, 0.5):
        M.put("drums", at, soft_kick(), 0.6)
        M.kicks.append(at)
        if int(round(at * 2)) % 2 == 1:
            M.put("drums", at, snare(), 0.26, verb=0.2)
        M.put("drums", at + 0.25, hat(), 0.07, 0.25)
    # Scene 3: G major, full
    prog3 = [(22, [55, 59, 62], 43), (24, [50, 54, 57], 38), (26, [52, 55, 59], 40), (28, [48, 52, 55], 36), (30, [55, 59, 62, 67], 43)]
    for start, notes, root in prog3:
        full = start < 27
        M.put("music", start, chord_ep(notes + [notes[0] + 12], 2.0 + (1.5 if start == 30 else 0), 0.85), 0.42, verb=0.4, echo=0.2)
        M.put("music", start, supersaw([m(n) for n in notes], 2.0, cutoff=3000 if full else 1500), 0.15 if full else 0.08, verb=0.3)
        for b in np.arange(0, 1.99, 0.5):
            M.put("music", start + b, sub(m(root), 0.45), 0.3 if full else 0.18)
    melody = [(22, 74), (22.5, 79), (23, 83), (23.5, 81), (24, 78), (24.5, 74), (25, 78), (25.5, 81), (26, 79), (26.5, 76), (28, 76), (29, 74), (29.5, 72), (30, 71)]
    for at, n in melody:
        M.put("music", at, epiano(m(n), 0.9, 0.9), 0.28, 0.15, verb=0.45, echo=0.35)
        M.put("music", at, bell(m(n + 12), 0.8, 1.2, 0.3), 0.05, -0.15, verb=0.4)
    for at in np.arange(22.0, 26.75, 0.5):
        M.put("drums", at, soft_kick(), 0.65)
        M.kicks.append(at)
        if int(round(at * 2)) % 2 == 1:
            M.put("drums", at, snare(), 0.3, verb=0.25)
    for k, at in enumerate(np.arange(22.0, 26.75, 0.125)):
        M.put("drums", at + (0.02 if k % 2 else 0), hat(k % 4 == 2), 0.08 if k % 2 == 0 else 0.045, 0.35)


def render_8():
    """8-qism: Yagona Marketplace yechimi. Score + cue-sheet (CUES_8)."""
    M = MixerPro(120)
    # stereo width follows the story: scattered (wide) -> pulled into the centre (narrow) -> balanced
    M.width = [(0, 1.7), (10.4, 1.7), (11.6, 0.35), (21.6, 0.5), (22.0, 1.0), (32, 1.0)]
    score_8(M)
    render_cues(M, CUES_8)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 9-qism uchun yangi tovushlar ----------
def fx_detent(note=60):
    x = seconds(0.03)
    return layer(filt(rng.standard_normal(len(x)), "bandpass", [2500, 8000]) * np.exp(-x / 0.003) * 0.7, np.sin(2 * np.pi * m(note) * 4 * x) * np.exp(-x / 0.006) * 0.4)


def fx_knob(dur=0.55):
    out = np.zeros(int(dur * SR))
    k, at = 0, 0.0
    while at < dur - 0.03:
        c = fx_detent(60 + (k % 3))
        i = int(at * SR)
        out[i : i + len(c)] += c[: len(out) - i] * (0.7 + 0.3 * np.sin(k))
        at += 0.025 + 0.02 * abs(np.sin(k * 0.7))
        k += 1
    return out


def fx_switch():
    x = seconds(0.18)
    return layer(filt(rng.standard_normal(len(x)), "bandpass", [1500, 6000]) * np.exp(-x / 0.004), tone(110, 0.18, "sine", 0.001, 0.04) * 0.9, np.concatenate([np.zeros(int(0.012 * SR)), fx_detent(72) * 0.8]))


def fx_slider(dur=0.6):
    x = seconds(dur)
    fr = filt(rng.standard_normal(len(x)), "bandpass", [600, 2400]) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 7 * x)))
    return fr * np.sin(np.pi * x / dur) * 0.6


def fx_lcd():
    return layer(tone(1975, 0.08, "square", 0.002, 0.03) * 0.3, filt(rng.standard_normal(int(0.25 * SR)), "bandpass", [80, 400]) * np.exp(-seconds(0.25) / 0.1) * 0.6)


def fx_alarm(note=79, n=3):
    out = np.zeros(int((0.16 * n + 0.1) * SR))
    for k in range(n):
        b = tone(m(note), 0.09, "square", 0.002, 0.03) * 0.5
        i = int(k * 0.16 * SR)
        out[i : i + len(b)] += filt(b, "lowpass", 3000)
    return out


def fx_relay():
    x = seconds(0.02)
    return filt(rng.standard_normal(len(x)), "bandpass", [3000, 9000]) * np.exp(-x / 0.002)


def crt_off():
    x = seconds(0.6)
    whine = np.sin(2 * np.pi * 7800 * x) * np.exp(-x / 0.12) * 0.25
    thoomp = np.sin(2 * np.pi * np.cumsum(90 * 2 ** (-3 * x)) / SR) * np.exp(-x / 0.15) * 0.9
    crackle = filt(rng.standard_normal(len(x)), "highpass", 3000) * (rng.random(len(x)) < 0.02) * np.exp(-x / 0.2) * 1.0
    return whine + thoomp + crackle


def boot(tonic=63):
    out = np.zeros(int(1.0 * SR))
    for k, iv in enumerate((0, 7, 12, 16, 19)):
        b = bell(m(tonic + iv + 12), 0.6, 1.0, 0.18)
        i = int(k * 0.045 * SR)
        out[i : i + len(b)] += b[: len(out) - i] * 0.5
    return out


def fx_token(note=75):
    x = seconds(0.9)
    glass = sum(np.sin(2 * np.pi * m(note) * r * x) * np.exp(-x / (0.5 / r)) / r for r in (1, 2.76, 5.4))
    return glass * np.minimum(1, x / 0.003) * 0.6


def fx_think(dur=1.6):
    out = np.zeros(int(dur * SR))
    gg = np.random.default_rng(17)
    for _ in range(int(dur * 22)):
        b = bell(m(int(gg.choice([87, 89, 91, 94, 96, 99]))), 0.12, 0.5, 0.03) * gg.uniform(0.2, 0.6)
        i = int(gg.uniform(0, dur - 0.13) * SR)
        out[i : i + len(b)] += b
    return out * np.sin(np.pi * seconds(dur) / dur)


def fx_type():
    x = seconds(0.035)
    return filt(rng.standard_normal(len(x)), "bandpass", [1500, 5000]) * np.exp(-x / 0.005) * 0.8


def tr_glitch():
    out = np.zeros(int(0.42 * SR))
    gg = np.random.default_rng(23)
    for k in range(10):
        f = gg.choice([220, 440, 880, 1760, 3520])
        seg = np.sign(np.sin(2 * np.pi * f * seconds(0.03))) * 0.4 + filt(rng.standard_normal(int(0.03 * SR)), "highpass", 2000) * 0.5
        i = int(k * 0.04 * SR)
        out[i : i + len(seg)] += seg * (1 - k / 12)
    return out


def fx_nope():
    return layer(tone(m(48), 0.12, "sine", 0.002, 0.05) * 0.8, np.concatenate([np.zeros(int(0.08 * SR)), tone(m(46), 0.2, "sine", 0.002, 0.08) * 0.8]), fx_detent(48) * 0.5)


SOUNDS.update({
    "fx.knob": ("L3", lambda a=None: fx_knob(a or 0.55), "Murvat aylantirish: zinali 'chiq-chiq' (ratchet)"),
    "fx.detent": ("L3", lambda a=None: fx_detent(a or 60), "Bitta murvat qadami — pult elementi paydo bo'lishi"),
    "fx.switch": ("L3", lambda a=None: fx_switch(), "Tumbler: metall 'chiq' + past thunk"),
    "fx.slider": ("L3", lambda a=None: fx_slider(a or 0.6), "Slayder ishqalanishi"),
    "fx.lcd": ("L3", lambda a=None: fx_lcd(), "LCD yonishi: qisqa beep + elektr g'uvullash"),
    "fx.alarm": ("L5", lambda a=None: fx_alarm(*(a or (79, 3))), "Ogohlantirish signali (C-minor tonallikda)"),
    "fx.relay": ("L1", lambda a=None: fx_relay(), "Rele chiqillashi — muammo sahnasining 'hi-hat'i"),
    "tr.crt_off": ("L4", lambda a=None: crt_off(), "Eski televizor o'chishi: chiyillash + thoomp + chirsillash"),
    "tr.boot": ("L4", lambda a=None: boot(a or 63), "ADUZ yonishi: Eb-major arpedjio"),
    "fx.token": ("L3", lambda a=None: fx_token(a or 75), "AI so'zni ajratdi: shisha shimmer (balandligi sozlanadi)"),
    "fx.think": ("L3", lambda a=None: fx_think(a or 1.6), "AI 'o'ylayapti': mayda qo'ng'iroqcha uchqunlari"),
    "fx.type": ("L3", lambda a=None: fx_type(), "Yumshoq klaviatura bosishi"),
    "tr.glitch": ("L4", lambda a=None: tr_glitch(), "Digital glitch o'tishi: bit-stutter"),
    "fx.nope": ("L3", lambda a=None: fx_nope(), "'Oldin' qatori: past ikki nota (rad)"),
})
FRONT.add("tr.crt_off")


# ---------- 9-qism (2-variant, 7-qism uslubida) ----------
def fx_crumple():
    x = seconds(0.45)
    bursts = (rng.random(len(x)) < 0.012).astype(float)
    bursts = np.convolve(bursts, np.exp(-seconds(0.004) / 0.001), mode="same")
    crackle = filt(rng.standard_normal(len(x)) * bursts, "bandpass", [1000, 9000]) * 3
    s = (crackle + filt(rng.standard_normal(len(x)), "bandpass", [400, 2500]) * 0.15) * np.sin(np.pi * x / 0.45) ** 0.5
    return np.tanh(s * 2) / 2  # tame the sharpest crackles so they don't become the mix peak


def fx_thud():
    return layer(tone(65, 0.25, "sine", 0.001, 0.07), filt(rng.standard_normal(int(0.12 * SR)), "lowpass", 900) * np.exp(-seconds(0.12) / 0.02) * 0.6)


def fx_fill(note=72):
    return layer(bell(m(note), 0.28, 0.9, 0.09) * 0.8, ui_click() * 0.35)


SOUNDS.update({
    "fx.crumple": ("L5", lambda a=None: fx_crumple(), "Qoralama g'ijimlanadi: qog'oz chirsillashi"),
    "fx.thud": ("L5", lambda a=None: fx_thud(), "Qog'oz to'p yerga tushadi"),
    "fx.fill": ("L3", lambda a=None: fx_fill(a or 72), "Avtomatik to'ldirish 'domino'si: har sozlama o'z notasida"),
})
FRONT.update({"fx.crumple", "fx.thud"})
_PENTA = [65, 67, 69, 72, 74, 77, 79, 81, 84, 86, 89, 91, 93, 96, 98, 101, 103, 105, 108, 110]  # F-major pentatonic, 4 octaves up

CUES_9 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.16, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    *[(0.4 + i * 0.45, "fx.detent", 0.08, (-1) ** i * 0.7, 0.2, 0.2, f"Tishli g'ildirak #{i + 1}", 55 + i) for i in range(14)],
    (1.0, "tr.slide", 0.08, 0, 0.1, 0, "Ro'yxat pastga suriladi", None),
    (2.0, "ui.tap", 0.3, 0.2, 0, 0, "Narx strategiyasi bosildi", None),
    (2.05, "ui.dropdown", 0.2, 0.2, 0.1, 0, "Jargonli ro'yxat ochiladi", None),
    (3.0, "ui.tap", 0.2, 0.2, 0, 0, "Yopildi — tanlanmadi", None),
    (3.2, "tr.slide", 0.08, 0, 0.1, 0, "Yana pastga", None),
    (5.0, "ui.error", 0.24, 0, 0.2, 0, "12 ta majburiy maydon to'ldirilmagan", None),
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: MAJBURIY *", None),
    (5.8, "tr.slide", 0.08, 0, 0.1, 0, "Yana pastga", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: QAYSI STRATEGIYA?", None),
    (7.6, "ui.tap", 0.3, 0.4, 0, 0, "Saqlash bosildi", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: YANA XATO!", None),
    (7.8, "ui.error", 0.26, 0, 0.25, 0, "Saqlanmadi", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [55, 58, 62, 67]),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "20 TA SOZLAMA — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.55, "fx.crumple", 0.26, 0, 0, 0, "OVOZ VAKUUMI: qoralama g'ijimlanadi", None),
    (9.95, "fx.thud", 0.4, 0.15, 0, 0, "Qog'oz to'p tushadi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi kesimdan oldin", [65, 69, 72, 77]),
    (10.55, "tr.squeegee", 0.45, 0, 0.25, 0, "Squeegee o'tishi", None),
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    *[(11.6 + i * 0.15, "ui.select", 0.12, -0.3 + 0.3 * i, 0.25, 0.2, f"Maqsad kartasi #{i + 1}", [77, 81, 84][i]) for i in range(3)],
    (13.0, "ui.select", 0.24, 0.2, 0.2, 0, "Tanlandi: Do'konga mijoz", 84),
    (13.2, "tr.slide", 0.14, 0.5, 0.1, 0, "Aqlli sozlash ekrani", None),
    *[(13.55 + k * 0.105, "fx.fill", 0.17, -0.5 + k * 0.05, 0.25, 0.15, f"Avto-to'ldirish {k + 1}/20 — domino", _PENTA[k]) for k in range(20)],
    (15.8, "ui.next", 0.22, 0, 0.3, 0.2, "20/20 — hammasi to'ldirildi", None),
    (15.95, "tr.slide", 0.16, 0, 0.15, 0, "Tavsiya etilgan reja", None),
    (16.8, "ui.tap", 0.35, 0.1, 0, 0, "Ishga tushirish bosildi", None),
    (16.85, "ui.launch", 0.25, 0, 0.3, 0.2, "Ishga tushmoqda...", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: 1 TANLOV oldidan", [69, 72, 77, 81]),
    (18.2, "ui.success", 0.3, 0, 0.4, 0.3, "Ishga tushdi!", None),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "1 TANLOV — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 15),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Kampaniya ishga tushdi oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    *[(22.8 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(4)],
    *[(23.0 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [77, 81, 84, 89][i]) for i in range(4)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [72, 77, 81, 84]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 17),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [84, 89, 93][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (F tonikada)", 53),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 96),
]

SCORE_9 = [
    ("0:00–0:09.5", "Muammo · G-minor, tashvishli minimal", "7-qism aranjirovkasi 3 yarim ton yuqorida: qorong'i pad, offbeat bo'g'iq Rhodes, filtrlangan bas pulsi, yumshoq hat, 5.5 s dan kick. 9.5 s da hammasi keskin to'xtaydi."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: musiqa va dumlar −30 dB. Faqat qoralama g'ijimlanishi va qog'oz to'pning tushishi eshitiladi. Keyin J-cut swell F-major'da."),
    ("0:11–0:21.75", "Yechim · F-major, siyrak", "Half-time kick + snap, iliq Rhodes, sub, qo'ng'iroqcha. Ustida 20 notali 'domino' — avtomatik to'ldirish F-pentatonik bo'yicha 4 oktavaga ko'tariladi."),
    ("0:22–0:27", "Natija · F-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (F tonikada), so'nish."),
]


def score_9(M):
    """7-qism partiturasi, 3 yarim ton yuqorida (seriya 'qardosh' eshitilishi uchun)."""
    global KEY_SHIFT
    KEY_SHIFT = 3
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_9():
    """9-qism (2-variant): Aqlli kampaniya yaratish. Score + cue-sheet (CUES_9)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # crumpled draft: sound vacuum
    M.width = [(0, 0.9), (32, 0.9)]  # a little narrower than 7-qism for mono-safe phone speakers
    score_9(M)
    render_cues(M, CUES_9)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 10-qism: Matching algoritmi ishda ----------
def fx_peg():
    return layer(fx_detent(64) * 0.9, filt(rng.standard_normal(int(0.03 * SR)), "bandpass", [600, 2500]) * np.exp(-seconds(0.03) / 0.005) * 0.5)


def fx_clack():
    return layer(fx_peg() * 1.2, tone(80, 0.3, "sine", 0.001, 0.08) * 0.9, np.concatenate([np.zeros(int(0.06 * SR)), fx_peg() * 0.5]))


def fx_scan(dur=1.6):
    x = seconds(dur)
    f = 900 * 2 ** (x / dur)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 12 * x))
    return (s * 0.35 + sweep_filter(rng.standard_normal(len(x)), 2000, 7000) * 0.2) * np.sin(np.pi * x / dur)


def fx_score(note=72):
    return layer(bell(m(note), 0.4, 1.0, 0.14) * 0.8, tick(True) * 0.3)


def fx_radar():
    x = seconds(1.2)
    return np.sin(2 * np.pi * 1180 * x) * np.exp(-x / 0.25) * np.minimum(1, x / 0.004) * 0.6


SOUNDS.update({
    "fx.peg": ("L3", lambda a=None: fx_peg(), "Omad g'ildiragi qozig'i ko'rsatkichdan o'tishi"),
    "fx.clack": ("L5", lambda a=None: fx_clack(), "G'ildirak to'xtadi: oxirgi 'tak' + thud"),
    "fx.scan": ("L3", lambda a=None: fx_scan(a or 1.6), "Matching skaneri: ko'tariluvchi tremolo ton"),
    "fx.score": ("L3", lambda a=None: fx_score(a or 72), "Kanal bahosi: yuqori moslik — yuqori nota, past moslik — past nota"),
    "fx.radar": ("L3", lambda a=None: fx_radar(), "Radar diagramma ochilishi: sonar 'ping'"),
})
FRONT.update({"fx.clack"})

# Fortune wheel — same physics as episode10.html (linear deceleration from WHEEL_T0 over WHEEL_T seconds).
WHEEL_T0, WHEEL_T, WHEEL_LAND = 5.0, 4.5, 0
WHEEL_FINAL = -np.pi / 2 - (WHEEL_LAND + 0.5) * np.pi / 6 + 2 * np.pi * 6
WHEEL_TICKS = [WHEEL_T0 + WHEEL_T * (1 - np.sqrt(1 - k * (np.pi / 6) / WHEEL_FINAL)) for k in range(1, int(WHEEL_FINAL / (np.pi / 6)) + 1)]
_SCORES10 = [12, 94, 23, 91, 31, 88, 18, 76]
_SCAN10 = [12.2 + (k + 0.5) / 8 * 1.6 for k in range(8)]
_C_PENTA = [48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84]
_note10 = lambda sc: _C_PENTA[min(len(_C_PENTA) - 1, int(sc / 100 * len(_C_PENTA)))] + 12

CUES_10 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.16, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    *[(0.6 + k * 0.12, "ui.popup", 0.07, 0.2, 0.15, 0, f"Katalog qatori #{k + 1} — 'moslik: ?'", [60, 62, 64, 67, 69, 72, 74, 76][k]) for k in range(8)],
    *[(at, "ui.tap", 0.05, 0.3, 0, 0, "Ikkilanayotgan kursor", None) for at in (1.7, 2.1, 2.5, 2.9, 3.3)],
    (3.4, "ui.popup", 0.16, 0, 0.2, 0, "'Tasodifiy tanlash' tugmasi", 64),
    (4.3, "ui.tap", 0.35, 0.2, 0, 0, "Tasodifiy tanlash bosildi", None),
    (4.5, "tr.whoosh", 0.22, 0, 0.3, 0, "Omad g'ildiragi chiqadi", None),
    *[(at, "fx.peg", 0.16 + 0.12 * (at - WHEEL_T0) / WHEEL_T, 0.1, 0.1, 0, f"Qoziq #{k + 1}" if k % 10 == 0 else "Qoziq", None) for k, at in enumerate(WHEEL_TICKS)],
    (5.6, "imp.glitch", 0.36, -0.4, 0.25, 0, "Slam: TAXMIN?", None),
    (6.6, "imp.glitch", 0.36, 0.4, 0.25, 0, "Slam: OMAD?", None),
    (7.6, "imp.glitch", 0.36, -0.4, 0.25, 0, "Slam: TAVAKKAL!", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [50, 53, 57, 62]),
    (8.5, "imp.boom", 0.7, 0, 0.4, 0, "50 / 50 — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.36, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.28, 0, 0, 0, "Zarba qatlami", None),
    (WHEEL_T0 + WHEEL_T, "fx.clack", 0.5, 0.1, 0, 0, "OVOZ VAKUUMI: g'ildirak to'xtadi — Toshkent Memlar", None),
    (9.75, "fx.heartbeat", 0.4, 0, 0, 0, "Hukm: Moslik 12%", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (C-major)", [60, 64, 67, 72]),
    *[(10.55 + k / 32, "ui.slider", 0.06, (-1) ** k * 0.6, 0.2, 0, "Piksel-dissolve uchqunlari" if k == 0 else "Piksel-dissolve", [72, 74, 76, 79, 81, 84, 86, 88][k % 8]) for k in range(14)],
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    *[(11.7 + k * 0.06, "fx.snap", 0.07, -0.3 + 0.08 * k, 0.1, 0, "Kanal qatori", None) for k in range(8)],
    (12.2, "fx.scan", 0.16, 0, 0.3, 0.2, "Matching skaneri ro'yxatni kezadi", 1.6),
    *[(at, "fx.score", 0.15 + 0.08 * (sc > 70), -0.4 + 0.1 * k, 0.3, 0.2, f"Baho: {sc}%", _note10(sc)) for k, (at, sc) in enumerate(zip(_SCAN10, _SCORES10))],
    (14.1, "tr.slide", 0.18, 0, 0.15, 0, "Ro'yxat moslik bo'yicha qayta tartiblanadi", None),
    (14.7, "fx.snap", 0.2, 0, 0.2, 0, "Tartib joyiga tushdi", None),
    *[(14.8 + i * 0.12, "ui.select", 0.16, -0.3 + 0.3 * i, 0.3, 0.2, f"Medal #{i + 1}", [84, 79, 76][i]) for i in range(3)],
    (15.6, "ui.tap", 0.3, 0, 0, 0, "Eng mos kanal bosildi", None),
    (15.8, "tr.slide", 0.16, 0, 0.15, 0, "'Nega mos?' oynasi", None),
    (16.0, "fx.radar", 0.22, 0, 0.4, 0.45, "Radar diagramma 'ping'i", None),
    (16.05, "ui.launch", 0.12, 0, 0.3, 0, "Diagramma o'sadi", None),
    (17.6, "ui.tap", 0.35, 0.1, 0, 0, "Tanlash bosildi", None),
    (17.85, "ui.next", 0.22, 0, 0.3, 0.2, "Tanlandi", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: 94% MOSLIK oldidan", [64, 67, 72, 76]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "94% MOSLIK — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 19),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Eng mos kanallar tanlandi oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    *[(22.8 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Taxmin' qatori #{i + 1} chizildi", None) for i in range(4)],
    *[(23.0 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"Matching qatori #{i + 1}", [72, 76, 79, 84][i]) for i in range(4)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [67, 72, 76, 79]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 21),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [79, 84, 88][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (C tonikada)", 60),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 91),
]

SCORE_10 = [
    ("0:00–0:09.5", "Muammo · D-minor, tashvishli minimal", "7-qism aranjirovkasi 2 yarim ton pastda. Ustida omad g'ildiragi qoziqlari: boshida tez 'trrr' (soniyasiga ~30), keyin fizika bo'yicha sekinlashadi — har bir 'chiq' qoziq ko'rsatkichdan o'tgan kadrga tushadi."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "G'ildirak to'xtashi bilan musiqa kesiladi (gate). Sukunatda oxirgi 'tak' va yurak urishi: 'Moslik: 12%'. Keyin J-cut swell C-major'da."),
    ("0:11–0:21.75", "Yechim · C-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Skaner har bir kanalni baholaganda baho notasi: yuqori moslik — baland nota, past moslik — past nota (C-pentatonik). Radar diagramma sonar 'ping'i bilan ochiladi."),
    ("0:22–0:27", "Natija · C-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (C tonikada), so'nish."),
]


def score_10(M):
    """7-qism partiturasi, 2 yarim ton pastda."""
    global KEY_SHIFT
    KEY_SHIFT = -2
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_10():
    """10-qism: Matching algoritmi ishda. Score + cue-sheet (CUES_10)."""
    M = MixerPro(120)
    M.gates.append((WHEEL_T0 + WHEEL_T, 10.15, 0.03))  # the wheel stops: sound vacuum
    M.width = [(0, 0.9), (32, 0.9)]
    score_10(M)
    render_cues(M, CUES_10)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 11-qism: Kafolatlangan xavfsizlik (Escrow) ----------
def fx_transfer():
    return layer(whoosh(0.45, 800, 6000) * 0.7, np.concatenate([np.zeros(int(0.3 * SR)), coin() * 0.8]))


def fx_blocked():
    x = seconds(0.9)
    slam_ = np.sin(2 * np.pi * np.cumsum(70 * 2 ** (-x * 2)) / SR) * np.exp(-x / 0.18)
    door = filt(rng.standard_normal(len(x)), "lowpass", 600) * np.exp(-x / 0.05) * 0.8
    return np.tanh((slam_ + door) * 1.4) * 0.9


def fx_fail():
    return layer(tone(m(57), 0.12, "sine", 0.002, 0.04) * 0.7, np.concatenate([np.zeros(int(0.07 * SR)), tone(m(52), 0.16, "sine", 0.002, 0.06) * 0.7]))


def fx_vault_lock():
    x = seconds(1.6)
    ring = sum(np.sin(2 * np.pi * f * x) * np.exp(-x / d) for f, d in ((410, 0.6), (1083, 0.35), (1731, 0.22), (2950, 0.12))) * 0.25
    thunk = tone(58, 0.4, "sine", 0.001, 0.12) * 1.2
    latch = np.zeros(len(x))
    for k, at in enumerate((0.0, 0.07, 0.16)):
        c = fx_detent(55 + 4 * k) * 1.4
        i = int(at * SR)
        latch[i : i + len(c)] += c
    return np.tanh(layer(ring, thunk, latch) * 1.2)


def fx_freeze(dur=0.7):
    out = np.zeros(int(dur * SR))
    gg = np.random.default_rng(31)
    for k in range(60):
        at = dur * (k / 60) ** 0.6
        b = bell(gg.uniform(3500, 9000), 0.05, 0.4, 0.012) * gg.uniform(0.2, 0.6)
        i = int(at * SR)
        out[i : i + len(b)] += b[: len(out) - i]
    x = seconds(dur)
    out += np.sin(2 * np.pi * np.cumsum(2000 * 2 ** (1.5 * x / dur)) / SR) * (x / dur) * 0.15
    return out


def fx_melt(dur=0.6):
    out = np.zeros(int(dur * SR))
    for k, at in enumerate((0.0, 0.12, 0.22, 0.36, 0.45)):
        x = seconds(0.12)
        drip = np.sin(2 * np.pi * np.cumsum(1600 * 2 ** (-3 * x / 0.12) + 300) / SR) * np.exp(-x / 0.04)
        i = int(at * SR)
        out[i : i + len(drip)] += drip[: len(out) - i] * (0.7 - 0.08 * k)
    return out


SOUNDS.update({
    "fx.transfer": ("L3", lambda a=None: fx_transfer(), "Pul o'tkazmasi: whoosh + tanga"),
    "fx.coin": ("L3", lambda a=None: coin(), "Tanga jiringlashi"),
    "fx.blocked": ("L5", lambda a=None: fx_blocked(), "'Sizni blokladi': og'ir eshik yopilishi"),
    "fx.fail": ("L3", lambda a=None: fx_fail(), "Xabar yetib bormadi: qizil '!'"),
    "fx.vault_lock": ("L5", lambda a=None: fx_vault_lock(), "Seyf qulflanishi: og'ir thunk + uch zinali latch + metall jarang"),
    "fx.freeze": ("L3", lambda a=None: fx_freeze(), "Muzlatish: kristallanayotgan muz — zichlashib boruvchi shisha uchqunlar"),
    "fx.melt": ("L3", lambda a=None: fx_melt(), "Muz eriydi: tomchilar"),
})
FRONT.update({"fx.blocked", "fx.fail"})

CUES_11 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.16, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    *[(at, "ui.select", 0.1, -0.3, 0.2, 0, f"Admin: xabar", 66) for at in (0.9, 2.2, 3.6)],
    *[(at, "ui.select", 0.1, 0.3, 0.2, 0, "Siz: xabar", 71) for at in (1.6, 4.7, 5.5, 6.3)],
    (2.9, "fx.transfer", 0.3, 0.3, 0.2, 0, "500 000 so'm o'tkazildi", None),
    (4.3, "tr.slide", 0.1, 0, 0.2, 0, "'Ertasi kuni'", None),
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: OLDINDAN TO'LOV", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: POST YO'Q", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: JAVOB YO'Q", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [57, 60, 64, 69]),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "500 000 → 0 — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.55, "fx.blocked", 0.5, 0, 0, 0, "OVOZ VAKUUMI: admin blokladi", None),
    *[(9.7 + k * 0.08, "fx.fail", 0.22, 0.4, 0, 0, f"Xabar yetmadi #{k + 1}", None) for k in range(3)],
    (9.95, "fx.heartbeat", 0.4, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (G-major)", [67, 71, 74, 79]),
    (10.55, "tr.whoosh", 0.3, 0, 0.3, 0, "Oltin doira o'tishi", None),
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    (11.6, "ui.popup", 0.14, 0, 0.2, 0, "Buyurtma kartasi", 79),
    (12.6, "ui.tap", 0.35, 0.2, 0, 0, "Kafolat bilan to'lash", None),
    (12.8, "tr.slide", 0.14, 0.5, 0.1, 0, "Kafolat hisobi ekrani", None),
    (12.8, "fx.knob", 0.18, 0, 0.2, 0, "Seyf disk-qulfi aylanadi", 0.8),
    (13.0, "fx.transfer", 0.24, -0.4, 0.2, 0, "Tanga seyfga uchadi", None),
    (13.6, "fx.vault_lock", 0.5, 0, 0.35, 0, "SEYF QULFLANDI", None),
    (13.7, "fx.freeze", 0.3, 0, 0.4, 0.2, "MUZLATILDI", None),
    (13.8, "ui.select", 0.16, -0.2, 0.3, 0, "1. Pul muzlatildi", 79),
    *[(14.3 + 0.7 * (1 - (1 - k / 12) ** 1.6), "fx.tick", 0.08, 0.3, 0, 0, "Vaqt tez o'tadi (18:52 → 19:00)", None) for k in range(12)],
    (15.0, "ui.next", 0.2, 0, 0.3, 0.2, "2. Post chiqdi — bot tekshirdi", None),
    (15.8, "ui.select", 0.16, 0, 0.3, 0, "3. 24 soat turdi", 83),
    (16.0, "fx.melt", 0.3, 0, 0.3, 0.2, "Muz eriydi", None),
    (16.2, "fx.transfer", 0.24, 0.4, 0.2, 0, "Tanga adminga o'tadi", None),
    (16.7, "ui.select", 0.18, 0.4, 0.3, 0.2, "4. Pul adminga o'tdi", 86),
    (16.95, "ui.popup", 0.14, 0, 0.2, 0, "Post chiqmasa — pul qaytadi", 74),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: PUL HIMOYADA oldidan", [71, 74, 79, 83]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "PUL HIMOYADA — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 23),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Pulingiz himoyada oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    *[(22.8 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(4)],
    *[(23.0 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [79, 83, 86, 91][i]) for i in range(4)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [74, 79, 83, 86]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 25),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [86, 91, 95][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (G tonikada)", 55),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 98),
]
SOUNDS.setdefault("fx.tick", ("L3", lambda a=None: tick(True), "Soat tiqillashi"))

SCORE_11 = [
    ("0:00–0:09.5", "Muammo · A-minor, tashvishli minimal", "7-qism aranjirovkasi 5 yarim ton yuqorida: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Chat xabarlari tonallikdagi qo'ng'iroqchalar; 2.9 s da pul o'tkazmasi."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: admin 'blokladi' — og'ir eshik yopilishi, uchta yetib bormagan xabar ('!'), yurak urishi. Keyin J-cut swell G-major'da."),
    ("0:11–0:21.75", "Yechim · G-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida seyf hikoyasi: disk-qulf aylanadi → tanga kiradi → og'ir qulflanish → muz kristallanadi → vaqt tezlashadi → bot tasdig'i → muz eriydi → tanga adminga."),
    ("0:22–0:27", "Natija · G-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (G tonikada), so'nish."),
]


def score_11(M):
    """7-qism partiturasi, 5 yarim ton yuqorida."""
    global KEY_SHIFT
    KEY_SHIFT = 5
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_11():
    """11-qism: Kafolatlangan xavfsizlik (Escrow). Score + cue-sheet (CUES_11)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # blocked: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_11(M)
    render_cues(M, CUES_11)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out



# ---------- 12-qism: Shaffof statistika va jonli tahlil ----------
def fx_dart_throw():
    return whoosh(0.32, 1500, 7000) * 0.8


def fx_dart_hit():
    x = seconds(0.6)
    thunk = np.sin(2 * np.pi * np.cumsum(260 * 2 ** (-x * 6) + 90) / SR) * np.exp(-x / 0.04)
    click = filt(rng.standard_normal(len(x)), "bandpass", [1800, 6000]) * np.exp(-x / 0.003) * 0.6
    quiver = np.sin(2 * np.pi * 340 * x) * (0.5 + 0.5 * np.sin(2 * np.pi * 34 * x)) * np.exp(-x / 0.14) * 0.22
    return np.tanh((thunk + click + quiver) * 1.3) * 0.9


def fx_thunder():
    x = seconds(2.2)
    crack = filt(rng.standard_normal(len(x)), "highpass", 1800) * np.exp(-x / 0.03) * 0.8
    roll = filt(rng.standard_normal(len(x)), "lowpass", 260) * np.exp(-x / 0.7) * (0.6 + 0.4 * np.sin(2 * np.pi * 3.1 * x) * np.sin(2 * np.pi * 1.3 * x)) * 2.2
    return np.tanh((crack + roll) * 1.1) * 0.85


def fx_breaker():
    x = seconds(0.35)
    return np.tanh(layer(tone(70, 0.35, "sine", 0.001, 0.08) * 1.2, filt(rng.standard_normal(len(x)), "lowpass", 900) * np.exp(-x / 0.02), fx_switch() * 0.8) * 1.2)


def fx_flicker(dur=0.06):
    x = seconds(dur + 0.03)
    buzz = filt(2 * ((120 * x) % 1) - 1, "bandpass", [200, 2400]) + np.sin(2 * np.pi * 60 * x) * 0.5
    ping = filt(rng.standard_normal(len(x)), "highpass", 4000) * np.exp(-x / 0.006) * 0.6
    return (buzz * np.clip(x / 0.004, 0, 1) * np.clip((dur + 0.03 - x) / 0.03, 0, 1) + ping) * 0.6


def fx_blip(note=82):
    return layer(tone(m(note), 0.09, "pluck", 0.002, 0.06) * 0.6, bell(m(note + 12), 0.15, 0.8, 0.05) * 0.25)


def fx_bar(note=70):
    x = seconds(0.4)
    return np.sin(2 * np.pi * np.cumsum(m(note) * 2 ** (x / 0.4)) / SR) * np.exp(-x / 0.12) * np.clip(x / 0.01, 0, 1) * 0.5


SOUNDS.update({
    "fx.dart_throw": ("L3", lambda a=None: fx_dart_throw(), "Dart uchishi: qisqa, yuqori chastotali 'fiyyu'"),
    "fx.dart_hit": ("L3", lambda a=None: fx_dart_hit(), "Dart tegishi: yog'och 'tuk' + dumning titrashi"),
    "fx.thunder": ("L5", lambda a=None: fx_thunder(), "Chaqmoq: keskin 'chars' + past gumburlash"),
    "fx.breaker": ("L5", lambda a=None: fx_breaker(), "Elektr shiti yoqiladi: og'ir 'klak'"),
    "fx.flicker": ("L3", lambda a=None: fx_flicker(a or 0.06), "Lyuminessent lampa: g'uvullab miltillash"),
    "fx.blip": ("L3", lambda a=None: fx_blip(a or 82), "Issiqlik xaritasi katagi: tonallikdagi 'blip'"),
    "fx.bar": ("L3", lambda a=None: fx_bar(a or 70), "Shahar ustuni o'sadi: ko'tariluvchi ton"),
    "fx.ding": ("L3", lambda a=None: ding(a or 932.3), "Tavsiya lampochkasi: 'ding'"),
})
FRONT.update({"fx.dart_hit", "fx.breaker", "fx.flicker"})

BB_PENT = [70, 72, 74, 77, 79, 82, 84, 86, 89, 91, 94]
_dpan = lambda x: round((x - 540) / 540 * 0.6, 2)
_DARTS_12 = [(1.4, 300), (2.3, 840), (3.2, 470), (4.1, 760), (5.0, 230), (5.9, 640), (6.8, 900), (7.7, 380)]

CUES_12 = [
    (0.0, "amb.office", 0.08, 0, 0, 0, "Qorong'i xona — sahna 'havosi'", 9.6),
    (0.2, "fx.switch", 0.16, -0.2, 0.2, 0, "Fonar yoqiladi", None),
    (0.8, "ui.popup", 0.12, 0, 0.2, 0, "Reklama posti: 'Statistika mavjud emas'", 62),
    *[(at - 0.35, "fx.dart_throw", 0.14, _dpan(x) * 0.5, 0.15, 0, f"Dart #{i + 1} otildi", None) for i, (at, x) in enumerate(_DARTS_12)],
    *[(at, "fx.dart_hit", 0.3, _dpan(x), 0.3, 0.15, f"Dart #{i + 1} — qorong'ida tegdi", None) for i, (at, x) in enumerate(_DARTS_12)],
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: NATIJA?", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: KIM KO'RDI?", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: QACHON?", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: chaqmoq oldidan", [56, 60, 63, 68]),
    (8.5, "fx.thunder", 0.55, 0, 0.3, 0, "CHAQMOQ — strob bilan bir kadrda", None),
    (8.5, "imp.boom", 0.65, 0, 0.4, 0, "QORONG'IDA — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.3, 0, 0.5, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.28, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.6, "fx.dart_throw", 0.16, 0.3, 0, 0, "OVOZ VAKUUMI: yana bitta o'q...", None),
    (9.95, "fx.dart_hit", 0.32, 0.5, 0, 0, "...tegdimi, yo'qmi — noma'lum", None),
    (9.95, "fx.heartbeat", 0.36, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (Bb-major)", [58, 62, 65, 70]),
    (10.55, "fx.breaker", 0.5, 0, 0, 0, "Chiroq kaliti: 'KLAK'", None),
    (10.58, "fx.flicker", 0.3, -0.2, 0, 0, "Lampa miltillashi #1", 0.036),
    (10.676, "fx.flicker", 0.3, 0.2, 0, 0, "Lampa miltillashi #2", 0.036),
    (10.772, "fx.flicker", 0.24, 0, 0, 0, "Lampa yonib qoladi", 0.3),
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi — CHIROQ YONDI", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    *[(at, "fx.tick", 0.05, 0.35, 0, 0, "Jonli hisoblagich", None) for at in np.arange(11.5, 18.25, 0.5)],
    *[(12.0 + k * 1.6 / 18, "fx.blip", 0.07, -0.5 + k / 17, 0.2, 0.2, f"Issiqlik katagi diagonali {k + 1}/18", BB_PENT[k % 11]) for k in range(18)],
    *[(13.7 + i * 0.12, "imp.glitch", 0.1, 0.3, 0.2, 0, f"Qaynoq katak #{i + 1}", None) for i in range(3)],
    *[(13.8 + i * 0.14, "fx.bar", 0.14, -0.2, 0.2, 0.15, f"Shahar ustuni #{i + 1}", [70, 74, 77, 79, 82][i]) for i in range(5)],
    (15.2, "fx.ding", 0.24, 0.1, 0.35, 0.3, "Tavsiya: 20:00 ga ko'chiring", None),
    (16.0, "ui.tap", 0.35, 0.3, 0, 0, "'Qo'llash' bosildi", None),
    (16.2, "ui.select", 0.22, 0.3, 0.3, 0.2, "Qo'llandi ✓", 82),
    *[(16.5 + k * 0.15, "fx.blip", 0.1, 0.4 - 0.08 * k, 0.25, 0.25, f"+ko'rish #{k + 1}", [82, 84, 86, 89, 91, 94][k]) for k in range(6)],
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: CHIROQ YONDI oldidan", [62, 65, 70, 74]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "CHIROQ YONDI — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 29),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Hammasi ko'z oldingizda oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    *[(at - 0.25, "fx.dart_throw", 0.12, 0, 0.15, 0, f"Nishonga dart #{i + 1}", None) for i, at in enumerate((22.5, 22.8, 23.1, 23.4))],
    *[(at, "fx.dart_hit", 0.26, 0, 0.3, 0.15, f"Markazga tegdi #{i + 1}", None) for i, at in enumerate((22.5, 22.8, 23.1, 23.4))],
    *[(at + 0.02, "ui.select", 0.1, 0.2, 0.3, 0.2, f"Tegdi — tasdiq #{i + 1}", [77, 82, 86, 89][i]) for i, at in enumerate((22.5, 22.8, 23.1, 23.4))],
    *[(23.5 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[(23.7 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [74, 77, 82][i]) for i in range(3)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [65, 70, 74, 77]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 31),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [82, 86, 89][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (Bb tonikada)", 58),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 89),
]

SCORE_12 = [
    ("0:00–0:09.5", "Muammo · C-minor, tashvishli minimal", "7-qism aranjirovkasi 4 yarim ton pastda: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida 8 ta dart — har biri uchish 'fiyyu' + yog'och 'tuk', panorama dart tushgan joyga mos. 8.5 s da chaqmoq strob bilan bir kadrda."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: musiqa o'chadi; qorong'ida yana bitta dart uchadi va tegadi — ko'rinmaydi, faqat eshitiladi ('tegdimi, yo'qmi — noma'lum'). Yurak urishi. Keyin J-cut swell Bb-major'da."),
    ("0:10.55–0:11", "Chiroq yonishi", "Elektr shiti 'KLAK' → lyuminessent lampa ikki marta miltillab yonadi; ovoz tasvirdagi miltillash kadrlari bilan sinxron (10.58 / 10.68 / 10.77 s)."),
    ("0:11–0:21.75", "Yechim · Bb-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: jonli hisoblagich tiqillashi, issiqlik xaritasi diagonallari Bb-pentatonik zinapoyada, shahar ustunlari ko'tariluvchi tonlar, tavsiya 'ding', 'Qo'llash' → ko'rishlar o'sishi (yuqoriga yuruvchi blip)."),
    ("0:22–0:27", "Natija · Bb-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. To'rtta dart nishon markaziga — har tegishda tonallikdagi tasdiq ohangi."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (Bb tonikada), so'nish."),
]


def score_12(M):
    """7-qism partiturasi, 4 yarim ton pastda."""
    global KEY_SHIFT
    KEY_SHIFT = -4
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_12():
    """12-qism: Shaffof statistika va jonli tahlil. Score + cue-sheet (CUES_12)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # dart in the dark: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_12(M)
    render_cues(M, CUES_12)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 13-qism: Ommaviy qamrov ----------
def fx_flick():
    x = seconds(0.07)
    return filt(rng.standard_normal(len(x)), "bandpass", [1200, 5000]) * np.exp(-x / 0.012) * 0.8 + np.sin(2 * np.pi * 520 * x) * np.exp(-x / 0.01) * 0.3


def fx_power_down():
    x = seconds(0.9)
    sweep = np.sin(2 * np.pi * np.cumsum(880 * 2 ** (-x * 4)) / SR) * np.exp(-x / 0.35) * 0.5
    return layer(sweep, ui_click() * 0.6)


def fx_low_battery():
    return layer(tone(m(76), 0.11, "sine", 0.002, 0.04) * 0.6, np.concatenate([np.zeros(int(0.13 * SR)), tone(m(69), 0.2, "sine", 0.002, 0.08) * 0.6]))


def fx_send():
    return whoosh(0.22, 2500, 9000) * 0.7


def fx_kassa():
    x = seconds(0.25)
    drawer = filt(rng.standard_normal(len(x)), "bandpass", [300, 2500]) * np.exp(-x / 0.06) * 0.6
    return layer(fx_detent(70) * 1.2, np.concatenate([np.zeros(int(0.05 * SR)), drawer]), np.concatenate([np.zeros(int(0.12 * SR)), ding(1318.5) * 0.7]), np.concatenate([np.zeros(int(0.2 * SR)), coin() * 0.7]))


SOUNDS.update({
    "fx.flick": ("L4", lambda a=None: fx_flick(), "Plitka ag'dariladi: qog'oz 'shirt'"),
    "fx.power_down": ("L5", lambda a=None: fx_power_down(), "Telefon o'chadi: pastga tushuvchi ton + klik"),
    "fx.low_battery": ("L3", lambda a=None: fx_low_battery(), "Batareya 1%: ikki notali ogohlantirish"),
    "fx.send": ("L3", lambda a=None: fx_send(), "Post yuborildi: qisqa 'fiyt'"),
    "fx.kassa": ("L5", lambda a=None: fx_kassa(), "Kassa: tugma + quti + 'ding' + tanga"),
})
FRONT.update({"fx.power_down", "fx.low_battery"})

E_PENT = [64, 66, 68, 71, 73, 76, 78, 80, 83, 85, 88, 90]
_RIT_13 = [(1.0, 0, False), (2.3, 1, True), (3.6, 2, False)]
_MONT_13 = [(4.8 + k * 0.32 + (k % 3) * 0.04, 3 + k, k in (2, 6, 9)) for k in range(11)]
_tpan = lambda i: round(((i % 5) - 2) * 0.22, 2)

CUES_13 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.16, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    *[x for at, i, err in _RIT_13 for x in [
        (at - 0.15, "ui.tap", 0.24, _tpan(i), 0, 0, f"Chat #{i + 1} ochildi", None),
        (at, "tr.slide", 0.1, 0, 0.1, 0, "Chat kartasi chiqadi", None),
        (at + 0.3, "ui.tap", 0.2, -0.3, 0, 0, "Nusxa olish", None),
        (at + 0.52, "ui.tap", 0.2, 0, 0, 0, "Joylash", None),
        (at + 0.74, "ui.tap", 0.2, 0.3, 0, 0, "Yuborish", None),
        (at + 0.76, "fx.send", 0.14, 0.4, 0.15, 0, "Post ketdi", None),
        (at + 1.0, "fx.fail" if err else "ui.select", 0.18 if err else 0.1, 0, 0.2, 0, "Admin: «Narx boshqacha»" if err else "Yuborildi", None if err else 59),
    ]],
    *[(at - 0.12, "ui.tap", 0.14, _tpan(i), 0, 0, f"Chat #{i + 1}", None) for at, i, err in _MONT_13],
    *[(at, "fx.fail" if err else "ui.select", 0.14 if err else 0.07, _tpan(i), 0.15, 0, f"Chat #{i + 1}: " + ("xato" if err else "yuborildi"), None if err else 59) for at, i, err in _MONT_13],
    *[(at, "fx.tick", 0.04 + 0.04 * (at - 4.5) / 5, 0.35, 0, 0, "Soat yuguradi", None) for at in np.arange(4.5, 9.45, 0.25)],
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: 50 TA CHAT", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: 50 MARTA NUSXA", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: YANA 36 TA...", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [54, 57, 61, 66]),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "14 / 50 — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.55, "fx.power_down", 0.45, 0, 0, 0, "OVOZ VAKUUMI: telefon o'chdi", None),
    (9.6, "fx.low_battery", 0.26, 0, 0, 0, "Batareya 1%", None),
    (9.95, "fx.heartbeat", 0.36, 0, 0, 0, "Yurak urishi", None),
    (10.1, "fx.low_battery", 0.18, 0, 0, 0, "Batareya 1% (so'nggi)", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (E-major)", [64, 68, 71, 76]),
    *[(10.35 + 0.65 * (d / 14 * 0.55 + 0.225), "fx.flick", 0.16, round(-0.5 + d / 14, 2), 0.15, 0, f"Plitkalar ag'dariladi — diagonal {d + 1}/15", None) for d in range(15)],
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    (12.1, "ui.select", 0.2, -0.3, 0.2, 0, "Filtr: Kiyim-kechak", 76),
    (12.6, "ui.select", 0.2, 0.1, 0.2, 0, "Filtr: Farg'ona vodiysi", 80),
    *[(12.9 + k / 18, "fx.blip", 0.07, round(-0.5 + (k % 6) / 5, 2), 0.2, 0.2, f"Kanallar belgilanmoqda {3 * (k + 1)}/54", E_PENT[k % 12]) for k in range(18)],
    (13.95, "ui.success", 0.18, 0, 0.4, 0.2, "54 kanal tanlandi", None),
    *[(14.0 + k * 0.11, "ui.slider", 0.06, 0.2, 0.1, 0, f"Qamrov hisoblanmoqda {k + 1}/8", [64, 66, 68, 71, 73, 76, 78, 80][k]) for k in range(8)],
    (15.2, "ui.tap", 0.38, 0.2, 0, 0, "'54 kanalga yuborish' bosildi", None),
    (15.25, "ui.launch", 0.22, 0, 0.3, 0.2, "Yuborish boshlandi", None),
    *[(15.4 + k * 0.07, "fx.send", 0.1, round((k / 13 - 0.5) * 1.4, 2), 0.2, 0.15, f"Post #{k + 1} uchib ketdi", None) for k in range(14)],
    *[(15.4 + k * 0.08, "fx.blip", 0.06, round(-0.5 + k / 12, 2), 0.25, 0.25, f"Kanal to'lqini {k + 1}/13", E_PENT[k % 12]) for k in range(13)],
    (16.6, "ui.success", 0.3, 0, 0.5, 0.3, "54 / 54 yuborildi", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: BITTA TUGMA oldidan", [68, 71, 76, 80]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "BITTA TUGMA — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 37),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "54 kanalga yuborildi oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    *[(22.45 + k * 0.17, "ui.slider", 0.07, -0.3, 0.1, 0, f"Qamrov o'smoqda {k + 1}/9", [64, 66, 68, 71, 73, 76, 78, 80, 83][k]) for k in range(9)],
    (24.0, "fx.kassa", 0.4, 0, 0.3, 0.2, "KASSA — 186 000 qamrov", None),
    *[(23.5 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[(23.7 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [76, 80, 83][i]) for i in range(3)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [71, 76, 80, 83]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 41),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [83, 88, 92][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (E tonikada)", 64),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 95),
]

SCORE_13 = [
    ("0:00–0:09.5", "Muammo · F#-minor, tashvishli minimal", "7-qism aranjirovkasi 2 yarim ton yuqorida: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida 'nusxa → joylash → yuborish' marosimi: bir xil uch bosish qayta-qayta (zerikarli takror — ataylab). 4.5 s dan soat tiqillashi tobora balandlashadi."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: telefon o'chadi (pastga tushuvchi ton), 'batareya 1%' ogohlantirishi, yurak urishi. Keyin J-cut swell E-major'da."),
    ("0:10.35–0:11", "Plitkalar ag'darilishi", "15 ta qog'oz 'shirt' — har biri plitkalar devorining bitta diagonali bilan sinxron; panorama chapdan o'ngga yuradi."),
    ("0:11–0:21.75", "Yechim · E-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: ikki filtr tanlovi, 54 kanal belgilanishi (E-pentatonik zinapoya), qamrov hisoblagichi, 'yuborish' bosilishi va 14 ta post stereo maydon bo'ylab uchib ketadi."),
    ("0:22–0:27", "Natija · E-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Qamrov hisoblagichi ko'tariluvchi qadamlar bilan 186 000 ga yetadi — kassa ovozi (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (E tonikada), so'nish."),
]


def score_13(M):
    """7-qism partiturasi, 2 yarim ton yuqorida."""
    global KEY_SHIFT
    KEY_SHIFT = 2
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_13():
    """13-qism: Ommaviy qamrov. Score + cue-sheet (CUES_13)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # phone dies: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_13(M)
    render_cues(M, CUES_13)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 14-qism: Vaqt mashinasi (Rejalashtirish) ----------
def fx_ringtone(dur=1.0):
    out = np.zeros(int(dur * SR))
    pat = [83, 78, 83, 86, 83, 78, 75, 78]
    for k, at in enumerate(np.arange(0, dur - 0.1, 0.13)):
        n = layer(tone(m(pat[k % 8]), 0.16, "pluck", 0.002, 0.1) * 0.5, bell(m(pat[k % 8] + 12), 0.12, 0.6, 0.04) * 0.15)
        i = int(at * SR)
        out[i : i + len(n)] += n[: len(out) - i]
    return filt(out, "highpass", 300)


def fx_vibrate(dur=1.0):
    x = seconds(dur)
    gate = (np.sin(2 * np.pi * 2.2 * x) > -0.3).astype(float)
    gate = np.convolve(gate, np.ones(400) / 400, mode="same")
    return filt(np.sign(np.sin(2 * np.pi * 170 * x)) * 0.5, "lowpass", 900) * gate * 0.7


def fx_breath(dur=1.4):
    x = seconds(dur)
    env_ = np.sin(np.pi * x / dur) ** 2
    return filt(rng.standard_normal(len(x)), "bandpass", [250, 1400]) * env_ * 0.45


def fx_birds(n=4, seed=3):
    gg = np.random.default_rng(seed)
    out = np.zeros(int((0.18 * n + 0.3) * SR))
    for k in range(n):
        d = gg.uniform(0.05, 0.1)
        x = seconds(d)
        f0 = gg.uniform(2600, 4200)
        ch = np.sin(2 * np.pi * np.cumsum(f0 + 1400 * np.sin(np.pi * x / d) + 300 * np.sin(2 * np.pi * 40 * x)) / SR) * np.sin(np.pi * x / d) ** 2
        i = int((k * 0.18 + gg.uniform(0, 0.05)) * SR)
        out[i : i + len(ch)] += ch * gg.uniform(0.4, 0.8)
    return out


def fx_blink():
    return whoosh(0.18, 300, 1200) * 0.5


SOUNDS.update({
    "fx.ringtone": ("L3", lambda a=None: fx_ringtone(a or 1.0), "Budilnik: tonallikdagi marimba-arpedjio"),
    "fx.vibrate": ("L3", lambda a=None: fx_vibrate(a or 1.0), "Telefon vibratsiyasi: past g'uvullash, pulsatsiya"),
    "fx.breath": ("L2", lambda a=None: fx_breath(a or 1.4), "Uyqudagi chuqur nafas"),
    "fx.birds": ("L2", lambda a=None: fx_birds(*(a or (4, 3))), "Ertalabki qushlar chug'urlashi"),
    "fx.blink": ("L4", lambda a=None: fx_blink(), "Ko'z qovog'i 'shirt' etib yumiladi"),
})
FRONT.update({"fx.breath"})

B_PENT = [71, 73, 75, 78, 80, 83, 85, 87, 90]

CUES_14 = [
    (0.0, "amb.office", 0.07, 0, 0, 0, "Tungi xona — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.14, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    *[(at, "fx.tick", 0.035, -0.4, 0.1, 0, "Devor soati", None) for at in np.arange(0.5, 9.45, 1.0)],
    *[x for a, k, b in [(2.0, 0, 3.05), (6.6, 1, 7.35), (7.6, 2, 8.35)] for x in [
        (a, "fx.ringtone", 0.2, 0.1, 0.2, 0, f"Budilnik {['23:00', '01:00', '06:30'][k]}", round(b - a, 2)),
        (a, "fx.vibrate", 0.16, 0, 0, 0, "Vibratsiya", round(b - a, 2)),
    ]],
    (3.0, "ui.tap", 0.3, -0.2, 0, 0, "'Kechiktirish' bosildi", None),
    (3.3, "fx.breath", 0.2, 0, 0.2, 0, "Ko'z yumilmoqda...", 1.3),
    (4.6, "fx.ding", 0.2, 0.2, 0.3, 0.2, "Admin xabari: post bekor", 739.99),
    (4.62, "ui.error", 0.18, 0.2, 0.2, 0, "Kechikdi", None),
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: TUNGI 23:00", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: 01:00 — YANA", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: 06:30 — YANA", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [49, 52, 56, 61]),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "UYQUSIZ TUN — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.3, "fx.blink", 0.25, 0, 0, 0, "Ko'zlar yumiladi", None),
    (9.5, "fx.breath", 0.38, 0, 0, 0, "OVOZ VAKUUMI: og'ir nafas", 1.0),
    (9.8, "fx.heartbeat", 0.3, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (B-major)", [59, 63, 66, 71]),
    (10.34, "fx.birds", 0.12, -0.5, 0.3, 0.2, "Ertalab: qushlar (chap)", (3, 5)),
    (10.53, "fx.blink", 0.2, 0, 0.1, 0, "Ko'z pirpiradi", None),
    (10.7, "fx.birds", 0.1, 0.5, 0.3, 0.2, "Qushlar (o'ng)", (3, 7)),
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi — uyg'onish", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    (11.9, "ui.select", 0.2, -0.2, 0.2, 0, "Kun: Seshanba", 78),
    (12.2, "fx.knob", 0.16, 0.2, 0.15, 0, "Soat barabani aylanadi 19 → 23", 0.8),
    *[(12.2 + 0.8 * (1 - np.cos(np.pi * (k + 0.5) / 4)) / 2, "ui.slider", 0.08, 0.2, 0.1, 0, f"Soat qadami {20 + k}:00", [71, 75, 78, 83][k]) for k in range(4)],
    (13.15, "ui.popup", 0.14, -0.2, 0.2, 0, "Navbat: 23:00", 78),
    (13.55, "ui.tap", 0.24, 0.3, 0, 0, "+ Qo'shish", None),
    (13.57, "ui.popup", 0.14, 0, 0.2, 0, "Navbat: 01:00", 82),
    (13.95, "ui.tap", 0.24, 0.3, 0, 0, "+ Qo'shish", None),
    (13.97, "ui.popup", 0.14, 0.2, 0.2, 0, "Navbat: 06:30", 85),
    (14.6, "ui.tap", 0.36, 0.2, 0, 0, "'Rejalashtirish' bosildi", None),
    (14.65, "ui.success", 0.24, 0, 0.4, 0.2, "3 ta post rejada", None),
    (15.0, "tr.riser", 0.18, 0, 0.2, 0, "Vaqt mashinasi ishga tushadi", 0.7),
    *[(at, "fx.tick", 0.05, round(0.4 * np.sin(at * 7), 2), 0.1, 0, "Soat tez yuguradi", None) for at in 15.2 + 2.5 * (np.arange(26) / 26) ** 0.8],
    *[(at, "fx.send", 0.14, (-0.3, 0, 0.3)[i], 0.2, 0, f"Avtomatik chiqdi: {['23:00', '01:00', '06:30'][i]}", None) for i, at in enumerate((15.8, 16.5, 17.3))],
    *[(at + 0.05, "ui.select", 0.2, (-0.3, 0, 0.3)[i], 0.3, 0.2, f"Chiqdi ✓ #{i + 1}", [78, 82, 85][i]) for i, at in enumerate((15.8, 16.5, 17.3))],
    (17.4, "fx.birds", 0.08, 0.4, 0.3, 0.2, "Tong — qushlar", (4, 11)),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: AVTOMATIK oldidan", [63, 66, 71, 75]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "AVTOMATIK — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 43),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Hammasi o'z vaqtida chiqdi oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (22.3, "fx.knob", 0.12, 0, 0.15, 0, "Soat millari aylanadi", 1.1),
    *[(at, "ui.select", 0.18, (-0.3, 0.3, 0)[i], 0.3, 0.2, f"Soat belgisi ✓ {['23:00', '01:00', '06:30'][i]}", [78, 82, 85][i]) for i, at in enumerate((22.5, 22.85, 23.2))],
    (23.2, "fx.kassa", 0.36, 0, 0.3, 0.2, "KASSA — uchala post o'z vaqtida", None),
    *[(23.5 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[(23.7 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [75, 78, 83][i]) for i in range(3)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [66, 71, 75, 78]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 47),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [83, 87, 90][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (B tonikada)", 59),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 90),
]

SCORE_14 = [
    ("0:00–0:09.5", "Muammo · C#-minor, tashvishli minimal", "7-qism aranjirovkasi 3 yarim ton pastda: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida tungi xona: devor soati, uch marta budilnik (tonallikdagi marimba + vibratsiya), 'Kechiktirish', uyquli nafas, adminning 'post bekor' xabari."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: ko'zlar yumiladi — og'ir nafas va yurak urishi. Keyin J-cut swell B-major'da."),
    ("0:10.2–0:11", "Uyg'onish", "Ko'z ochiladi, bir pirpiraydi ('shirt'), chap va o'ngdan ertalabki qushlar — tun tugadi."),
    ("0:11–0:21.75", "Yechim · B-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: kun tanlovi, soat barabani (detent + ko'tariluvchi qadamlar), navbatga uchta post, 'Rejalashtirish'. 15.2 s dan 'vaqt mashinasi': tezlashuvchi soat tiqillashi, har post o'z vaqtida 'fiyt' + tasdiq, tongda qushlar."),
    ("0:22–0:27", "Natija · B-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Soat millari aylanadi, uchta belgi, kassa ovozi (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (B tonikada), so'nish."),
]


def score_14(M):
    """7-qism partiturasi, 3 yarim ton pastda."""
    global KEY_SHIFT
    KEY_SHIFT = -3
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_14():
    """14-qism: Vaqt mashinasi (Rejalashtirish). Score + cue-sheet (CUES_14)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # eyes close: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_14(M)
    render_cues(M, CUES_14)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 15-qism: Ochiq haqiqat (Reyting tizimi) ----------
def fx_shutter():
    x = seconds(0.12)
    a = filt(rng.standard_normal(len(x)), "bandpass", [1500, 7000]) * np.exp(-x / 0.008)
    b = np.concatenate([np.zeros(int(0.06 * SR)), filt(rng.standard_normal(int(0.06 * SR)), "bandpass", [1000, 5000]) * np.exp(-seconds(0.06) / 0.01)])
    return layer(a, b * 0.7) * 0.8


def fx_xray():
    x = seconds(0.6)
    shimmer = sum(np.sin(2 * np.pi * f * x + 3 * np.sin(2 * np.pi * 6 * x)) for f in (1800, 2410, 3150)) / 3 * np.exp(-x / 0.25) * 0.35
    wob = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (-x * 1.5) * (1 + 0.04 * np.sin(2 * np.pi * 9 * x))) / SR) * np.exp(-x / 0.3) * 0.5
    return shimmer + wob


def _tinkles(dur, n, seed, f0=2500, f1=9000):
    gg = np.random.default_rng(seed)
    out = np.zeros(int((dur + 0.4) * SR))
    for k in range(n):
        at = dur * (k / n) ** 1.6
        b = bell(gg.uniform(f0, f1), 0.25, 0.5, gg.uniform(0.02, 0.08)) * gg.uniform(0.2, 0.7)
        i = int(at * SR)
        out[i : i + len(b)] += b[: len(out) - i]
    return out


def fx_crack():
    x = seconds(0.5)
    snap = filt(rng.standard_normal(len(x)), "highpass", 2500) * np.exp(-x / 0.012)
    body = np.sin(2 * np.pi * 140 * x) * np.exp(-x / 0.05) * 0.6
    return np.tanh(layer(snap + body, _tinkles(0.25, 10, 41) * 0.5) * 1.3) * 0.85


def fx_creak(dur=0.5):
    x = seconds(dur)
    f = 900 + 500 * x / dur
    return np.sin(2 * np.pi * np.cumsum(f + 40 * rng.standard_normal(len(x))) / SR) * np.sin(np.pi * x / dur) * 0.25


def fx_shatter():
    x = seconds(0.9)
    burst = filt(rng.standard_normal(len(x)), "highpass", 1200) * np.exp(-x / 0.08) * 0.9
    low = np.sin(2 * np.pi * 90 * x) * np.exp(-x / 0.12) * 0.7
    return np.tanh(layer(burst + low, _tinkles(0.8, 70, 43) * 0.8) * 1.1) * 0.85


def fx_stamp():
    x = seconds(0.25)
    return np.tanh((np.sin(2 * np.pi * np.cumsum(160 * 2 ** (-x * 8) + 60) / SR) * np.exp(-x / 0.05) + filt(rng.standard_normal(len(x)), "bandpass", [600, 3000]) * np.exp(-x / 0.01) * 0.6) * 1.4) * 0.8


SOUNDS.update({
    "fx.shutter": ("L3", lambda a=None: fx_shutter(), "Skrinshot: kamera zatvori 'chiq-chiq'"),
    "fx.xray": ("L3", lambda a=None: fx_xray(), "Lupa fosh qiladi: shisha shimmer + pastga tushuvchi 'vuuu'"),
    "fx.crack": ("L5", lambda a=None: fx_crack(), "Shisha yoriladi: keskin 'chars' + mayda jaranglar"),
    "fx.creak": ("L3", lambda a=None: fx_creak(a or 0.5), "Yoriq shisha zo'riqishi: ingichka g'ichirlash"),
    "fx.shatter": ("L5", lambda a=None: fx_shatter(), "Shisha sinadi: portlash + 70 ta parcha jarangi"),
    "fx.stamp": ("L3", lambda a=None: fx_stamp(), "'Tasdiqlangan' muhri"),
})
FRONT.update({"fx.crack", "fx.creak"})

EB_PENT = [63, 65, 67, 70, 72, 75, 77, 79, 82, 84, 87]

CUES_15 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.16, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    (0.8, "ui.select", 0.1, -0.3, 0.2, 0, "Admin: 'Mana isbot'", 68),
    (1.3, "fx.shutter", 0.22, -0.2, 0.15, 0, "Skrinshot #1: 50 000 ko'rish", None),
    (1.35, "ui.popup", 0.12, -0.2, 0.2, 0, "Skrinshot ochiladi", 75),
    (2.5, "fx.shutter", 0.22, 0.2, 0.15, 0, "Skrinshot #2: 340 buyurtma, 5 yulduz", None),
    (2.55, "ui.popup", 0.12, 0.2, 0.2, 0, "Skrinshot ochiladi", 79),
    (3.6, "ui.select", 0.1, -0.3, 0.2, 0, "Admin: 'Narxi 800 000'", 68),
    (4.3, "tr.whoosh", 0.18, 0.5, 0.25, 0, "Lupa kadrga kiradi", None),
    (5.0, "fx.xray", 0.26, -0.2, 0.3, 0.2, "Fosh: 50 000 → 4 200", None),
    (6.6, "fx.xray", 0.26, 0, 0.3, 0.2, "Fosh: 340 → 3", None),
    (7.6, "fx.xray", 0.26, 0.1, 0.3, 0.2, "Fosh: bot akkaunt", None),
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: SOXTA SKRIN", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: KO'PAYTIRILGAN", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: BOT SHARH", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [53, 56, 60, 65]),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "SOXTA ISBOT — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.5, "fx.crack", 0.55, 0, 0, 0, "OVOZ VAKUUMI: shisha yoriladi", None),
    (9.85, "fx.creak", 0.3, 0.2, 0, 0, "Yoriq zo'riqadi...", 0.45),
    (9.95, "fx.heartbeat", 0.3, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (Eb-major)", [63, 67, 70, 75]),
    (10.3, "fx.shatter", 0.55, 0, 0.35, 0.15, "SHISHA SINADI — o'tish", None),
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    *[(12.0 + k * 0.1, "ui.slider", 0.07, -0.3, 0.1, 0, f"Reyting hisoblanmoqda {k + 1}/8", EB_PENT[k]) for k in range(8)],
    *[(12.4 + i * 0.12, "fx.bar", 0.12, 0.3, 0.2, 0.15, f"Yulduz taqsimoti {5 - i}★", [82, 79, 75, 72, 70][i]) for i in range(5)],
    (13.6, "ui.popup", 0.16, 0, 0.2, 0, "Qoida: baho faqat buyurtmadan", 75),
    *[x for i, at in enumerate((14.2, 14.8, 15.4)) for x in [
        (at, "ui.popup", 0.13, (-0.3, 0, 0.3)[i], 0.2, 0, f"Sharh #{i + 1}", [77, 79, 82][i]),
        (at + 0.45, "fx.stamp", 0.24, (-0.3, 0, 0.3)[i], 0.15, 0, f"Tasdiqlangan buyurtma #{i + 1}", None),
    ]],
    (17.0, "ui.tap", 0.36, 0.2, 0, 0, "'Buyurtma berish' bosildi", None),
    (17.05, "ui.success", 0.24, 0, 0.4, 0.2, "Ishonch bilan buyurtma", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: OCHIQ HAQIQAT oldidan", [67, 70, 75, 79]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "OCHIQ HAQIQAT — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 53),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Ishonch bilan tanlang oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    *[(22.5 + k * 0.17, "ui.select", 0.16, round(-0.5 + k * 0.25, 2), 0.3, 0.2, f"Yulduz #{k + 1}", [75, 77, 79, 82, 84][k]) for k in range(5)],
    (23.2, "fx.kassa", 0.36, 0, 0.3, 0.2, "KASSA — 4.6 reyting", None),
    *[(23.5 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[(23.7 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [79, 82, 87][i]) for i in range(3)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [70, 75, 79, 82]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 59),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [87, 91, 94][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (Eb tonikada)", 63),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 94),
]

SCORE_15 = [
    ("0:00–0:09.5", "Muammo · F-minor, tashvishli minimal", "7-qism aranjirovkasi 1 yarim ton yuqorida: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida: skrinshotlar 'chiq-chiq' (kamera zatvori), lupa kiradi va har fosh — shisha shimmer + pastga tushuvchi 'vuuu' (slamlar bilan bir kadrda)."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: kadr shishadek yoriladi — keskin 'chars', mayda jaranglar, yoriqning ingichka g'ichirlashi, yurak urishi. Keyin J-cut swell Eb-major'da."),
    ("0:10.3–0:11", "Shisha sinadi", "Portlash + 70 ta parcha jarangi; ishonch 'sinadi', parchalar ortidan yechim ochiladi."),
    ("0:11–0:21.75", "Yechim · Eb-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: reyting hisoblagichi (Eb-pentatonik qadamlar), yulduz taqsimoti ustunlari, qoida, uchta sharh va har biriga 'Tasdiqlangan' muhri."),
    ("0:22–0:27", "Natija · Eb-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Beshta yulduz ko'tariluvchi qo'ng'iroqchalar bilan yonadi, kassa ovozi (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (Eb tonikada), so'nish."),
]


def score_15(M):
    """7-qism partiturasi, 1 yarim ton yuqorida."""
    global KEY_SHIFT
    KEY_SHIFT = 1
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_15():
    """15-qism: Ochiq haqiqat (Reyting tizimi). Score + cue-sheet (CUES_15)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # glass cracks: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_15(M)
    render_cues(M, CUES_15)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 16-qism: Bot va mutaxassis hamkorligi ----------
def fx_zap(dur=0.35):
    x = seconds(dur)
    crackle = filt(filt(rng.standard_normal(len(x)), "highpass", 2000) * (rng.random(len(x)) > 0.92), "lowpass", 7000) * 2.5
    buzz = np.sign(np.sin(2 * np.pi * 100 * x)) * 0.25 * np.exp(-x / 0.08)
    return np.tanh((crackle + buzz) * np.exp(-x / (dur * 0.4)) * 1.5) * 0.7


def fx_short():
    x = seconds(1.0)
    bang = np.tanh(filt(rng.standard_normal(len(x)), "lowpass", 3000) * np.exp(-x / 0.04) * 3) * 0.8
    hum = np.sin(2 * np.pi * np.cumsum(120 * 2 ** (-x * 2.5)) / SR) * np.exp(-x / 0.35) * 0.5
    return layer(bang, hum, fx_zap(0.6) * 0.6)


def fx_fizz(dur=0.6):
    x = seconds(dur)
    return filt(rng.standard_normal(len(x)), "bandpass", [3000, 9000]) * (rng.random(len(x)) > 0.8) * np.exp(-x / (dur * 0.5)) * 0.8


def fx_twang():
    x = seconds(0.7)
    f = 70 * 2 ** (2.5 * np.clip(x / 0.35, 0, 1))
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.3) * 1.5) * 0.6


def fx_plug():
    return layer(fx_switch() * 1.1, np.concatenate([np.zeros(int(0.03 * SR)), fx_zap(0.2) * 0.4]), np.concatenate([np.zeros(int(0.06 * SR)), tone(m(61), 0.5, "sine", 0.05, 0.3) * 0.3]))


SOUNDS.update({
    "fx.zap": ("L3", lambda a=None: fx_zap(a or 0.35), "Elektr uchquni: chirsillash"),
    "fx.short": ("L5", lambda a=None: fx_short(), "Qisqa tutashuv: portlash + pasayib boruvchi g'uvullash"),
    "fx.fizz": ("L3", lambda a=None: fx_fizz(a or 0.6), "Kuygan simlar vishillashi"),
    "fx.twang": ("L4", lambda a=None: fx_twang(), "Simlar tortiladi: yuqoriga ketuvchi 'tang'"),
    "fx.plug": ("L3", lambda a=None: fx_plug(), "Vilka rozetkaga: klak + uchqun + yoqilish toni"),
})
FRONT.update({"fx.short", "fx.fizz"})

DB_PENT = [61, 63, 65, 68, 70, 73, 75, 77, 80, 82, 85]
_W16 = [0.6 + i * 0.45 for i in range(8)] + [5.4, 6.4]

CUES_16 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.16, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    *[(at, "tr.whoosh", 0.06, round((-1) ** i * 0.6, 2), 0.1, 0, f"Sim #{i + 1} chiqadi", None) for i, at in enumerate(_W16)],
    *[(at + k * 0.03, "fx.type", 0.05, -0.1, 0, 0, "Kod yozilmoqda", None) for at, n in ((0.8, 29), (1.4, 30), (2.0, 30), (2.6, 18), (3.1, 27)) for k in range(0, n, 3)],
    *[x for at in (2.4, 3.6, 4.6, 6.0) for x in [
        (at, "fx.zap", 0.22, (-0.5, 0.5, -0.5, 0.5)[[2.4, 3.6, 4.6, 6.0].index(at)], 0.15, 0, f"Uchqun ({at} s)", None),
        (at + 0.02, "ui.error", 0.16, 0, 0.2, 0, "Konsol: xato", None),
    ]],
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: API TOKEN?", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: WEBHOOK?", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: 401 XATO", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [51, 54, 58, 63]),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "CHIGAL — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.5, "fx.short", 0.5, 0, 0, 0, "OVOZ VAKUUMI: qisqa tutashuv", None),
    (9.62, "fx.fizz", 0.3, -0.3, 0, 0, "Simlar vishillaydi", 0.5),
    (9.95, "fx.heartbeat", 0.3, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (Db-major)", [61, 65, 68, 73]),
    (10.3, "fx.twang", 0.4, 0, 0.2, 0.15, "Simlar bitta chiziqqa tortiladi", None),
    (10.58, "tr.whoosh", 0.3, 0, 0.3, 0, "Chiziqdan kadr ochiladi", None),
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    (12.1, "ui.tap", 0.3, 0.2, 0, 0, "+ Admin qo'shish", None),
    *[(12.4 + k * 0.066, "fx.type", 0.08, 0.1, 0, 0, f"'@aduz_bot' — {k + 1}/9", None) for k in range(9)],
    (13.05, "ui.popup", 0.14, 0, 0.2, 0, "ADUZ Bot topildi", 73),
    (13.3, "ui.select", 0.22, 0.2, 0.2, 0, "ADUZ Bot tanlandi", 77),
    *[(13.7 + i * 0.15, "fx.switch", 0.16, 0.4, 0.1, 0, f"Huquq #{i + 1} yoqildi", None) for i in range(3)],
    (14.4, "ui.tap", 0.34, 0.2, 0, 0, "'Saqlash' bosildi", None),
    (14.7, "tr.slide", 0.14, 0.5, 0.1, 0, "ADUZ ekraniga", None),
    (15.0, "tr.whoosh", 0.12, 0.3, 0.1, 0, "Vilka siljiydi", None),
    (15.6, "fx.plug", 0.42, -0.3, 0.2, 0, "VILKA ULANDI", None),
    (15.7, "ui.success", 0.26, 0, 0.4, 0.2, "Kanal ulandi", None),
    *[(at, "ui.select", 0.14, 0, 0.3, 0.2, f"Ro'yxat #{i + 1}", [73, 77, 80][i]) for i, at in enumerate((16.0, 16.3, 16.6))],
    (17.0, "ui.popup", 0.16, 0, 0.2, 0, "Mutaxassis Dilshod", 82),
    *[(17.3 + k * 0.1, "fx.type", 0.05, 0.1, 0, 0, "Mutaxassis yozmoqda", None) for k in range(10)],
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: BOT + MUTAXASSIS oldidan", [65, 68, 73, 77]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "BOT + MUTAXASSIS — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 61),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Kanal ulandi oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (22.5, "tr.riser", 0.16, 0, 0.2, 0, "Yashil kabel cho'ziladi", 0.7),
    (23.2, "fx.plug", 0.3, 0, 0.2, 0, "Ulandi ✓", None),
    (23.2, "fx.kassa", 0.34, 0, 0.3, 0.2, "KASSA — ulanish", None),
    *[(23.5 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[(23.7 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [77, 80, 85][i]) for i in range(3)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [68, 73, 77, 80]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 67),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [85, 89, 92][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (Db tonikada)", 61),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 92),
]

SCORE_16 = [
    ("0:00–0:09.5", "Muammo · Eb-minor, tashvishli minimal", "7-qism aranjirovkasi 1 yarim ton pastda: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida: kod yozish (klaviatura), simlar chiqishi (mayda whoosh), har xato — elektr uchquni + konsol xatosi."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: qisqa tutashuv — portlash, pasayib boruvchi g'uvullash, kuygan simlar vishillashi, yurak urishi. Keyin J-cut swell Db-major'da."),
    ("0:10.3–0:11", "Bitta chiziq", "Simlar tortiladi (yuqoriga ketuvchi 'tang') va bitta yashil chiziqqa aylanadi; undan kadr whoosh bilan ochiladi."),
    ("0:11–0:21.75", "Yechim · Db-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: 'Admin qo'shish', '@aduz_bot' yozilishi, uchta tumbler, 'Saqlash', vilka rozetkaga (klak + uchqun + yoqilish toni), mutaxassis xabari."),
    ("0:22–0:27", "Natija · Db-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Yashil kabel ulanadi — kassa ovozi (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (Db tonikada), so'nish."),
]


def score_16(M):
    """7-qism partiturasi, 1 yarim ton pastda."""
    global KEY_SHIFT
    KEY_SHIFT = -1
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_16():
    """16-qism: Bot va mutaxassis hamkorligi. Score + cue-sheet (CUES_16)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # short circuit: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_16(M)
    render_cues(M, CUES_16)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 17-qism: Topilgan daromadning erkinligi ----------
def fx_chain(dur=0.7):
    out = np.zeros(int(dur * SR))
    gg = np.random.default_rng(17)
    for k in range(26):
        at = dur * 0.8 * (k / 26) ** 0.7
        b = layer(bell(gg.uniform(1800, 4200), 0.12, 2.5, gg.uniform(0.02, 0.05)), fx_detent(int(gg.integers(70, 84))) * 0.8) * gg.uniform(0.3, 0.8)
        i = int(at * SR)
        out[i : i + len(b)] += b[: len(out) - i]
    x = seconds(dur)
    return np.tanh((out + np.sin(2 * np.pi * 70 * x) * np.exp(-x / 0.08) * 0.8) * 1.2) * 0.8


def fx_snap():
    x = seconds(0.9)
    crack = filt(rng.standard_normal(len(x)), "highpass", 1500) * np.exp(-x / 0.015)
    ring = sum(np.sin(2 * np.pi * f * x) * np.exp(-x / d) for f, d in ((620, 0.4), (1570, 0.25), (2890, 0.15))) * 0.3
    return np.tanh(layer(crack + ring, np.concatenate([np.zeros(int(0.08 * SR)), fx_chain(0.6) * 0.6])) * 1.2) * 0.85


def fx_sms():
    return layer(tone(m(85), 0.09, "sine", 0.002, 0.04) * 0.5, np.concatenate([np.zeros(int(0.12 * SR)), tone(m(90), 0.14, "sine", 0.002, 0.07) * 0.5]))


SOUNDS.update({
    "fx.chain": ("L5", lambda a=None: fx_chain(a or 0.7), "Zanjir: metall halqalar shaldirashi + zarba"),
    "fx.padlock": ("L5", lambda a=None: fx_vault_lock(), "Qulf: og'ir 'klak' + metall jarang"),
    "fx.chain_snap": ("L5", lambda a=None: fx_snap(), "Zanjir uziladi: keskin 'chars' + jarang + halqalar sochilishi"),
    "fx.sms": ("L3", lambda a=None: fx_sms(), "SMS: ikki notali signal"),
})
FRONT.update({"fx.chain", "fx.padlock"})

FS_PENT = [66, 68, 70, 73, 75, 78, 80, 82, 85, 87, 90]

CUES_17 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.16, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    *[x for i, at in enumerate((1.2, 2.6, 4.0, 5.4, 6.6, 7.6)) for x in [
        (at, "ui.tap", 0.26, 0.2, 0, 0, f"'Pulni yechish' #{i + 1}", None),
        (at + 0.2, "fx.sticky", 0.2, round(-0.3 + 0.12 * i, 2), 0.15, 0, f"Bahona kartasi #{i + 1}", None),
        (at + 0.22, "ui.error", 0.12, round(-0.3 + 0.12 * i, 2), 0.2, 0, "Rad etildi", None),
    ]],
    (1.45, "fx.detent", 0.2, 0.4, 0.1, 0, "Balansga qulf belgisi", 60),
    *[(at, "fx.tick", 0.035, -0.4, 0.1, 0, "Kutish kunlari o'tmoqda", None) for at in np.arange(1.0, 9.0, 0.5)],
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: BAHONA", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: YANA BAHONA", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: 14 KUN KUTING", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [56, 59, 63, 68]),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "QULFDA — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.5, "fx.chain", 0.45, 0, 0, 0, "OVOZ VAKUUMI: zanjirlar kadrni o'raydi", 0.6),
    (9.62, "fx.padlock", 0.45, 0, 0, 0, "Qulf yopildi", None),
    (9.95, "fx.heartbeat", 0.3, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (F#-major)", [66, 70, 73, 78]),
    (10.3, "fx.chain_snap", 0.5, 0, 0.35, 0.15, "ZANJIR UZILADI", None),
    (10.5, "tr.whoosh", 0.3, 0, 0.3, 0, "Oltin doira ochiladi", None),
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    (12.4, "ui.tap", 0.3, 0.2, 0, 0, "'Kartaga yechish'", None),
    (12.5, "tr.slide", 0.14, 0, 0.1, 0, "Yechish oynasi chiqadi", None),
    (12.9, "ui.select", 0.2, 0.2, 0.2, 0, "Uzcard tanlandi", 78),
    (13.3, "ui.select", 0.22, 0.3, 0.2, 0, "'Hammasi' — 2 450 000", 82),
    (14.0, "ui.tap", 0.36, 0.2, 0, 0, "'Tasdiqlash' bosildi", None),
    (14.1, "tr.whoosh", 0.16, 0, 0.2, 0, "Bank kartasi kadrga kiradi", None),
    (14.3, "tr.riser", 0.16, 0, 0.2, 0, "Tangalar oqimi", 1.1),
    *[(14.3 + k * 0.06 + 0.5, "fx.coin", 0.06, round((k % 5 - 2) * 0.2, 2), 0.2, 0, f"Tanga #{k + 1} kartaga", None) for k in range(16)],
    (15.4, "ui.success", 0.28, 0, 0.4, 0.2, "O'tkazildi ✓", None),
    (15.6, "fx.sms", 0.24, 0.3, 0.2, 0.15, "SMS: +2 450 000 so'm", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: PUL — SIZNIKI oldidan", [70, 73, 78, 82]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "PUL — SIZNIKI — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 71),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Pul kartangizda oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    *[(22.85 + k * 0.05, "fx.coin", 0.05, round(((k * 7) % 11 - 5) * 0.1, 2), 0.2, 0, f"Tanga yomg'iri #{k + 1}", None) for k in range(10)],
    (23.2, "fx.kassa", 0.38, 0, 0.3, 0.2, "KASSA — 2 450 000 kartada", None),
    *[(23.5 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[(23.7 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [78, 82, 87][i]) for i in range(3)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [70, 75, 78, 82]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 73),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [87, 90, 94][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (F# tonikada)", 66),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 94),
]

SCORE_17 = [
    ("0:00–0:09.5", "Muammo · G#-minor, tashvishli minimal", "7-qism aranjirovkasi 4 yarim ton yuqorida: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida: har 'Pulni yechish' bosilishiga bahona kartasi 'shap' etib yopishadi + rad signali; kutish kunlari tiqillaydi."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: zanjirlar kadrni o'raydi (metall shaldirash), og'ir qulf 'klak', yurak urishi. Keyin J-cut swell F#-major'da."),
    ("0:10.3–0:11", "Zanjir uziladi", "Keskin 'chars' + metall jarang + halqalar sochilishi; oltin doira whoosh bilan ochiladi."),
    ("0:11–0:21.75", "Yechim · F#-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: 'Kartaga yechish', karta va 'Hammasi' tanlovi, 'Tasdiqlash' → riser + 16 ta tanga kartaga tushadi → 'O'tkazildi' → SMS signali."),
    ("0:22–0:27", "Natija · F#-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Tanga yomg'iri kartaga, kassa ovozi (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (F# tonikada), so'nish."),
]


def score_17(M):
    """7-qism partiturasi, 4 yarim ton yuqorida."""
    global KEY_SHIFT
    KEY_SHIFT = 4
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_17():
    """17-qism: Topilgan daromadning erkinligi. Score + cue-sheet (CUES_17)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # chained and locked: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_17(M)
    render_cues(M, CUES_17)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 18-qism: Mukammallik formulasi (A/B test) ----------
def fx_flip(dur=1.0):
    x = seconds(dur)
    ping = bell(2600, 0.5, 1.5, 0.12)[: len(x)] * 0.6
    whirr = np.sin(2 * np.pi * 3100 * x) * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * x)) * np.sin(np.pi * x / dur) * 0.12
    out = whirr.copy()
    out[: len(ping)] += ping
    return out


def fx_wobble(dur=0.75):
    # spinning-disk wobble: metallic clicks accelerating, then sudden stop
    out = np.zeros(int((dur + 0.15) * SR))
    at, k = 0.0, 0
    while at < dur:
        rate = 7 * (60 / 7) ** (at / dur)
        c = layer(fx_detent(84) * 0.7, bell(3200 + 300 * (k % 3), 0.06, 1.2, 0.02) * 0.25)
        i = int(at * SR)
        out[i : i + len(c)] += c[: len(out) - i] * (0.5 + 0.5 * at / dur)
        at += 1 / rate
        k += 1
    return out


def fx_drain(dur=1.4):
    x = seconds(dur)
    return np.sin(2 * np.pi * np.cumsum(m(69) * 2 ** (-1.2 * x / dur)) / SR) * np.sin(np.pi * x / dur) * 0.3


def fx_zip(dur=0.28):
    x = seconds(dur)
    tone_ = np.sin(2 * np.pi * np.cumsum(400 * 2 ** (4 * x / dur)) / SR) * 0.35
    n = filt(rng.standard_normal(len(x)), "bandpass", [2000, 7000]) * 0.3
    return (tone_ + n) * np.clip(x / 0.02, 0, 1) * np.clip((dur - x) / 0.03, 0, 1)


SOUNDS.update({
    "fx.flip": ("L3", lambda a=None: fx_flip(a or 1.0), "Tanga tashlandi: 'ting' + havoda aylanish"),
    "fx.wobble": ("L5", lambda a=None: fx_wobble(a or 0.75), "Tanga aylanib to'xtaydi: tezlashuvchi metall chiqillash, keskin jimlik"),
    "fx.drain": ("L3", lambda a=None: fx_drain(a or 1.4), "Byudjet oqib ketmoqda: pasayuvchi hushtak"),
    "fx.zip": ("L4", lambda a=None: fx_zip(a or 0.28), "A|B chizig'i tortiladi: ko'tariluvchi 'zzzip'"),
})
FRONT.update({"fx.wobble"})

A_PENT = [69, 71, 73, 76, 78, 81, 83, 85, 88, 90]

CUES_18 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "tr.whoosh", 0.16, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    (1.4, "ui.popup", 0.1, -0.3, 0.2, 0, "Kursor A ustida — '?'", 64),
    (1.9, "ui.popup", 0.1, 0.3, 0.2, 0, "Kursor B ustida — '?'", 62),
    (2.4, "fx.flip", 0.3, 0, 0.25, 0.15, "TANGA TASHLANDI", 1.0),
    (3.4, "fx.coin", 0.3, 0, 0.2, 0, "Tanga tushdi: A", None),
    (3.7, "ui.tap", 0.28, -0.3, 0, 0, "A tanlandi", None),
    (4.2, "ui.tap", 0.3, 0.2, 0, 0, "Ishga tushirish — 100% → A", None),
    (4.25, "ui.launch", 0.18, 0, 0.3, 0.2, "Butun byudjet ketdi", None),
    *[(at, "fx.drain", 0.14, 0.2, 0.2, 0.2, f"Byudjet oqmoqda #{i + 1}", 1.3) for i, at in enumerate((4.6, 6.0, 7.4))],
    *[(4.6 + k * 0.5, "fx.tick", 0.03, 0.3, 0.1, 0, "Siyrak bosishlar", None) for k in range(9)],
    (5.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: TAXMIN", None),
    (6.6, "imp.glitch", 0.4, 0.4, 0.25, 0, "Slam: TAVAKKAL", None),
    (7.6, "imp.glitch", 0.4, -0.4, 0.25, 0, "Slam: BYUDJET KETDI", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [54, 57, 61, 66]),
    (8.5, "imp.boom", 0.72, 0, 0.4, 0, "LOTEREYA — asosiy zarba", 1.0),
    (8.5, "imp.clap", 0.38, 0, 0.5, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (8.6, "tr.riser", 0.3, 0, 0, 0, "Riser — 9.5 s da keskin kesiladi", 0.9),
    (9.62, "fx.wobble", 0.42, 0, 0, 0, "OVOZ VAKUUMI: tanga aylanib to'xtaydi", 0.7),
    (9.9, "fx.heartbeat", 0.26, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (A-major)", [57, 61, 64, 69]),
    (10.3, "fx.zip", 0.3, 0, 0.2, 0.15, "A|B chizig'i tortiladi", 0.28),
    (10.58, "tr.whoosh", 0.3, 0, 0.3, 0, "Kadr ikki tomonga ochiladi", None),
    (11.0, "imp.boom", 0.5, 0, 0.35, 0, "Yechim boshlanishi", 0.8),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "tr.whoosh", 0.18, -0.3, 0.2, 0, "Telefon kiradi", None),
    (11.9, "ui.popup", 0.14, 0, 0.2, 0, "Test byudjeti: 10%", 76),
    (12.6, "ui.tap", 0.34, 0.2, 0, 0, "'A/B testni boshlash'", None),
    (12.65, "ui.launch", 0.2, 0, 0.3, 0.2, "Test boshlandi", None),
    *[(13.0 + k * 0.2, "fx.blip", 0.06, -0.4 if k % 2 == 0 else 0.4, 0.2, 0.15, f"Poyga: {'A' if k % 2 == 0 else 'B'}", (A_PENT[min(k // 2, 3)] if k % 2 == 0 else A_PENT[min(k // 2 + 2, 9)])) for k in range(12)],
    (15.6, "ui.success", 0.28, 0.3, 0.4, 0.2, "G'OLIB: B", None),
    (15.6, "imp.sparkle", 0.22, 0.3, 0.4, 0, "G'olib toji", 79),
    (16.2, "fx.ding", 0.2, 0, 0.3, 0.2, "Tavsiya: qolgan byudjet B ga", 880.0),
    (16.8, "ui.tap", 0.3, 0.3, 0, 0, "'Ha, B ga'", None),
    *[(16.95 + k * 0.08 + 0.4, "fx.coin", 0.06, round(-0.3 + 0.08 * k, 2), 0.2, 0, f"Byudjet tangasi #{k + 1} → B", None) for k in range(8)],
    (17.75, "ui.select", 0.2, 0.3, 0.3, 0.2, "Byudjet g'olibda ✓", 81),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: G'OLIB — B oldidan", [61, 64, 69, 73]),
    (18.5, "imp.boom", 0.6, 0, 0.4, 0, "G'OLIB — B — zarba", 0.9),
    (18.5, "imp.crash", 0.26, 0, 0, 0, "Zarba qatlami", None),
    (18.5, "imp.sparkle", 0.4, 0, 0.5, 0, "Oltin uchqunlar", 83),
    (19.9, "ui.success", 0.28, 0, 0.5, 0.3, "Byudjet g'olibda oynasi", None),
    (21.2, "tr.riser", 0.26, 0, 0, 0, "J-cut: whip oldidan", 0.55),
    (21.75, "tr.whip", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (22.0, "imp.boom", 0.55, 0, 0.45, 0, "Natija boshlanishi", 0.9),
    (22.0, "imp.crash", 0.3, 0, 0, 0, "Zarba qatlami", None),
    (22.4, "tr.riser", 0.16, 0.3, 0.2, 0, "CTR ustuni o'sadi", 0.8),
    (23.2, "fx.kassa", 0.38, 0, 0.3, 0.2, "KASSA — ×6.7", None),
    *[(23.5 + i * 0.35, "fx.strike", 0.16, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[(23.7 + i * 0.35, "ui.select", 0.16, 0.4, 0.3, 0.2, f"ADUZ qatori #{i + 1}", [76, 81, 85][i]) for i in range(3)],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [69, 73, 76, 81]),
    (25.0, "imp.boom", 0.42, 0, 0.4, 0, "Urg'u", 0.6),
    (25.0, "imp.sparkle", 0.45, 0, 0.5, 0, "Uchqunlar", 89),
    *[(25.2 + i * 0.25, "ui.select", 0.14, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [85, 88, 93][i]) for i in range(3)],
    (26.85, "tr.whoosh", 0.16, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (A tonikada)", 57),
    (28.3, "ui.select", 0.08, 0.2, 0.5, 0.4, "CTA tugmasi", 93),
]

SCORE_18 = [
    ("0:00–0:09.5", "Muammo · B-minor, tashvishli minimal", "7-qism aranjirovkasi 5 yarim ton pastda: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida: ikki dizayn ustida ikkilanish, tanga tashlash ('ting' + aylanish + tushish), 'Ishga tushirish', byudjet oqib ketishi — pasayuvchi hushtaklar."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: tanga qorong'ilikka tushib, aylanib to'xtaydi — tezlashuvchi metall chiqillash va keskin jimlik; yurak urishi. Keyin J-cut swell A-major'da."),
    ("0:10.3–0:11", "A|B chizig'i", "Markazdan pastga yorug' chiziq tortiladi ('zzzip'), kadr ikki tomonga whoosh bilan ochiladi."),
    ("0:11–0:21.75", "Yechim · A-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: test byudjeti, 'boshlash', A (chapda, past) va B (o'ngda, baland) navbatma-navbat 'blip' — poyga, g'olib B, tavsiya 'ding', byudjet tangalari B ga."),
    ("0:22–0:27", "Natija · A-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. CTR ustuni o'sadi, ×6.7 da kassa ovozi (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (A tonikada), so'nish."),
]


def score_18(M):
    """7-qism partiturasi, 5 yarim ton pastda."""
    global KEY_SHIFT
    KEY_SHIFT = -5
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_18():
    """18-qism: Mukammallik formulasi (A/B test). Score + cue-sheet (CUES_18)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # the coin wobbles to rest: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_18(M)
    render_cues(M, CUES_18)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- Foydalanuvchi SFX kutubxonasi: sfx/*.wav (19-qismdan boshlab) ----------
# Foydalanuvchi yuborgan ikki namunaviy videodan (SFX to'plami reklamasi) kesib olingan haqiqiy yozuvlar:
# mono, 44.1 kHz, boshidagi jimlik kesilgan, cho'qqi −1 dBFS. Cue'larda "sfx.<nom>" sifatida ishlatiladi.
SFX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")
_SMP = {}


def smp(name, semis=0):
    """Kutubxona namunasi; semis ≠ 0 bo'lsa — yarim tonlarga siljitilgan (tezlik bilan birga, 'varispeed')."""
    if name not in _SMP:
        with wave.open(os.path.join(SFX_DIR, name + ".wav")) as w:
            assert w.getframerate() == SR and w.getnchannels() == 1
            _SMP[name] = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    x = _SMP[name]
    if not semis:
        return x.copy()
    r = 2 ** (semis / 12)
    return np.interp(np.arange(0, len(x) - 1, r), np.arange(len(x)), x)


SFX_LIB = {
    "click_1": ("L3", "Toza UI klik (1.7 kHz), 40 ms"), "click_2": ("L3", "UI klik, 2-variant"), "click_3": ("L3", "UI klik, 3-variant"),
    "click_4": ("L3", "UI klik, 4-variant"), "click_5": ("L3", "UI klik, 5-variant"),
    "click_double_1": ("L3", "Qo'sh klik (tasdiqlash)"), "click_double_2": ("L3", "Qo'sh klik, 2-variant"),
    "pop_swish": ("L3", "Qisqa 'pop' + shuvullash: element paydo bo'lishi"), "swipe": ("L4", "Swipe: ekran/kartaning sirpanishi"),
    "glitch_seq": ("L5", "Raqamli glitch ketma-ketligi (6 zarb)"), "notify_pop": ("L3", "Bildirishnoma: ikki 'pop' + dum"),
    "notify_ring": ("L3", "Bildirishnoma: jarangli 'ding'"), "hit_low": ("L5", "Past tonal zarba (≈260 Hz) + dum"),
    "hit_chime": ("L5", "Tonal zarba, qo'ng'iroqsimon (≈390 Hz)"), "hit_tone": ("L5", "Tonal zarba, 3-variant"),
    "whoosh_soft": ("L4", "Yumshoq whoosh (1.3 s)"), "whoosh_sweep": ("L4", "Whoosh, tonallik siljishi bilan"),
    "ratchet_roll": ("L3", "Tishli chiqillash, sekinlashuvchi (1.2 s)"), "riser_click": ("L4", "Riser: chiqillashlar bilan kuchayib boradi"),
    "glitch_long": ("L5", "Uzun zich glitch / ma'lumot oqimi (1.8 s)"), "glitch_noise": ("L5", "Shovqinli glitch (1.4 s)"),
    "stutter": ("L5", "Stutter: 10 ta tez zarb"), "glitch_short": ("L5", "Qisqa yuqori glitch (0.4 s)"),
    "tick": ("L3", "Mayda tik"), "tick_roll": ("L3", "8 ta bir tekis tik (hisoblagich/yozish)"), "boom_sub": ("L5", "Sub-boom (≈58 Hz) + dum"),
}
SOUNDS.update({f"sfx.{n}": (lay, (lambda a=None, n=n: smp(n, a or 0)), d) for n, (lay, d) in SFX_LIB.items()})
CLICKS = ["click_1", "click_2", "click_3", "click_4", "click_5"]


def sfx_riser(at, end):
    """riser_click shunday joylashtiriladi-ki, uning cho'qqisi `end` ga to'g'ri keladi."""
    return end - 1.12


# ---------- 19-qism: Mikro-kanallar kuchi (birinchi bo'lib sfx/ kutubxonasi bilan) ----------
SOUNDS.update({
    "sfx.deflate": ("L5", lambda a=None: smp("whoosh_sweep", -7), "Gigant pufak havosi chiqadi: whoosh_sweep −7 yarim ton"),
})
FRONT.update({"sfx.deflate"})
_RISE = [0, 2, 4, 7, 9, 12, 9, 12, 14, 16, 19, 21]   # D-pentatonik bo'yicha yarim tonlar (pop_swish uchun)
_ck = lambda i: f"sfx.{CLICKS[i % 5]}"

CUES_19 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "sfx.whoosh_soft", 0.2, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    (0.6, "sfx.tick_roll", 0.14, -0.3, 0.2, 0, "Katalog: kichik kanallar xira paydo bo'ladi", None),
    (1.6, _ck(0), 0.7, 0.1, 0, 0, "Gigant tanlandi", None),
    (1.62, "sfx.pop_swish", 0.25, 0.1, 0.2, 0, "Gigant kattalashadi", None),
    (2.6, "sfx.click_double_1", 0.7, 0.2, 0, 0, "'Butun byudjetni berish'", None),
    (2.7, "sfx.notify_ring", 0.3, 0.2, 0.25, 0, "To'landi", None),
    (3.0, "sfx.ratchet_roll", 0.22, -0.2, 0.1, 0, "Ko'rishlar sanalmoqda", None),
    *[(3.6 + k * 0.62, "sfx.tick", 0.18, round(((k * 5) % 9 - 4) * 0.15, 2), 0.3, 0.3, f"Kichik kanal faolligi lipillaydi #{k + 1}", 12) for k in range(8)],
    (6.0, "sfx.notify_pop", 0.32, 0, 0.2, 0, "1 reaksiya ≈ 21 000 so'm", -3),
    *[x for at, pan, nm in ((5.6, -0.4, "FAQAT GIGANT"), (6.6, 0.4, "QIMMAT"), (7.6, -0.4, "FAOLLIK 0.6%")) for x in [
        (at, "sfx.stutter", 0.42, pan, 0.2, 0, f"Slam: {nm}", None),
        (at, "sfx.glitch_short", 0.5, pan, 0.2, 0, "Slam qatlami", None),
    ]],
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [52, 55, 59, 64]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da, gate kesadi", None),
    (8.5, "sfx.boom_sub", 0.9, 0, 0.35, 0, "BITTA GIGANT — asosiy zarba", None),
    (8.5, "sfx.hit_low", 0.6, 0, 0.4, 0, "Zarba qatlami: tonal", None),
    (8.5, "sfx.glitch_seq", 0.28, 0, 0.2, 0, "Zarba qatlami: glitch", None),
    (9.55, "sfx.deflate", 0.6, 0, 0, 0, "OVOZ VAKUUMI: gigantning havosi chiqadi", None),
    (9.95, "fx.heartbeat", 0.28, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (D-major)", [62, 66, 69, 74]),
    *[(10.15 + k * 0.033, "sfx.pop_swish", 0.16, round(-0.6 + k * 0.11, 2), 0.3, 0.2, f"Mikro-kanal yonadi #{k + 1}", _RISE[k]) for k in range(12)],
    (10.55, "sfx.glitch_seq", 0.26, 0, 0.2, 0, "Piksel eriydi — tarmoq ochiladi", None),
    (11.0, "sfx.boom_sub", 0.5, 0, 0.35, 0, "Yechim boshlanishi", None),
    (11.0, "sfx.hit_chime", 0.32, 0, 0.4, 0.2, "Yechim: tonal urg'u", None),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "sfx.whoosh_soft", 0.2, -0.3, 0.2, 0, "Telefon kiradi", None),
    (11.3, "sfx.tick_roll", 0.22, 0, 0.2, 0.15, "Tarmoq tugunlari paydo bo'ladi", None),
    *[x for i, at in enumerate((11.9, 12.4)) for x in [
        (at, _ck(i + 1), 0.7, -0.3 + 0.5 * i, 0, 0, f"Filtr #{i + 1}", None),
        (at + 0.02, "ui.select", 0.14, -0.3 + 0.5 * i, 0.25, 0.2, "Filtr tasdig'i (tonallikda)", [74, 78][i]),
        (at + 0.1, "sfx.swipe", 0.28, 0.2, 0.15, 0, "Mos kelmaganlar so'nadi", None),
    ]],
    (12.8, "sfx.pop_swish", 0.3, 0, 0.2, 0, "Xulosa: 25 kanal", 4),
    (12.85, "sfx.ratchet_roll", 0.18, 0.2, 0.1, 0, "Obunachilar sanalmoqda", None),
    (14.0, "sfx.click_double_2", 0.7, 0.2, 0, 0, "'Tarmoqqa joylash'", None),
    (14.05, "sfx.whoosh_soft", 0.18, 0, 0.25, 0, "Post tarmoqqa ketdi", None),
    *[(14.2 + k * 0.1, "sfx.pop_swish", 0.17, round(-0.6 + k * 0.11, 2), 0.3, 0.25, f"Yorug'lik to'lqini: tugun #{k + 1}", _RISE[k]) for k in range(12)],
    (14.4, "sfx.ratchet_roll", 0.2, -0.2, 0.1, 0, "Reaksiyalar o'smoqda", None),
    (15.6, "sfx.ratchet_roll", 0.16, 0.2, 0.1, 0, "Reaksiyalar o'smoqda", None),
    (16.6, "sfx.notify_ring", 0.36, 0.3, 0.25, 0.2, "×100 reaksiya", None),
    (16.62, "ui.success", 0.2, 0.3, 0.4, 0.2, "Musiqiy tasdiq", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: MIKRO-KUCH oldidan", [66, 69, 74, 78]),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "MIKRO-KUCH — zarba", None),
    (18.5, "sfx.hit_chime", 0.5, 0, 0.4, 0.2, "Zarba qatlami: tonal", None),
    (18.5, "imp.sparkle", 0.35, 0, 0.5, 0, "Oltin uchqunlar", 239),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Oyna ko'tariladi", None),
    (19.9, "ui.success", 0.26, 0, 0.5, 0.3, "Mikro-tarmoq ishda", None),
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — cho'qqisi whip'da (21.75 s)", None),
    (21.75, "sfx.whoosh_sweep", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (21.75, "sfx.swipe", 0.3, 0, 0.2, 0, "Whip qatlami", None),
    (22.0, "sfx.boom_sub", 0.6, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.0, "sfx.hit_low", 0.4, 0, 0.4, 0, "Zarba qatlami", None),
    (22.2, "sfx.pop_swish", 0.3, -0.4, 0.2, 0, "1 gigant", -5),
    (22.4, "sfx.tick_roll", 0.28, 0.4, 0.2, 0.2, "25 mikro-kanal to'planadi", None),
    *[(22.45 + k * 0.1, "sfx.pop_swish", 0.14, 0.4, 0.3, 0.2, f"Mikro #{k + 1}", _RISE[k + 2]) for k in range(6)],
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA — 10.7% faollik", None),
    (23.22, "sfx.notify_ring", 0.24, 0.2, 0.25, 0.2, "Kassa qatlami", None),
    *[(23.5 + i * 0.35, "sfx.swipe", 0.34, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, _ck(i + 2), 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [74, 78, 81][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [66, 71, 74, 78]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "imp.sparkle", 0.4, 0, 0.5, 0, "Uchqunlar", 241),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_swish", 0.3, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [7, 12, 16][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Tonallikdagi qo'ng'iroqcha", [81, 86, 90][i]),
    ]],
    (26.85, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (D tonikada)", 62),
    (28.3, _ck(0), 0.35, 0.2, 0.3, 0.3, "CTA tugmasi", None),
    (28.32, "ui.select", 0.07, 0.2, 0.5, 0.4, "CTA qo'ng'iroqchasi", 90),
]

SCORE_19 = [
    ("Ovoz manbai", "Foydalanuvchi SFX kutubxonasi (sfx/)", "Birinchi qism: barcha UI, o'tish va zarba ovozlari foydalanuvchi yuborgan namunalardan (sfx.*): kliklar, qo'sh klik, pop_swish, swipe, whoosh, riser_click, stutter/glitch, notify, hit_low/hit_chime, boom_sub, tik va ratchet. Sintez faqat musiqiy qismlarda: partitura, J-cut swell, tonallikdagi qo'ng'iroqchalar (ui.select), success, uchqunlar, sonic logo, kassa."),
    ("0:00–0:09.5", "Muammo · E-minor, tashvishli minimal", "7-qism aranjirovkasi asl tonallikda. Ustida: gigant tanlash (klik + pop), 'butun byudjet' (qo'sh klik + ding), hisoblagich (ratchet), kichik kanallar faolligi yuqori tik bilan lipillaydi, slamlar — stutter + qisqa glitch."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: gigant pufakning havosi chiqadi (whoosh_sweep 7 yarim ton pastda), yurak urishi. Keyin J-cut swell D-major'da."),
    ("0:10.15–0:11", "Tarmoq yonadi", "12 ta pop_swish D-pentatonik zinapoyada chapdan o'ngga — kichik kanallar birin-ketin yonadi; piksel erishida glitch ketma-ketligi."),
    ("0:11–0:21.75", "Yechim · D-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: filtrlar (klik + tonallik qo'ng'irog'i + swipe), 'Tarmoqqa joylash' (qo'sh klik), yorug'lik to'lqini — 12 ta ko'tariluvchi pop, reaksiya hisoblagichi (ratchet), ×100 — notify_ring."),
    ("0:22–0:27", "Natija · D-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Gigant — past pop, mikro-kanallar — tik + ko'tariluvchi poplar, kassa + ding; taqqoslash — swipe + klik."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (D tonikada), so'nish."),
]


def render_19():
    """19-qism: Mikro-kanallar kuchi. Score (7-qism, asl tonallik) + cue-sheet (CUES_19), SFX — sfx/ kutubxonasi."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # the giant deflates: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_7(M)
    render_cues(M, CUES_19)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 20-qism: Qonuniy va oq savdo (B2B) — sfx/ kutubxonasi bilan ----------
SOUNDS.update({
    "sfx.stamp_big": ("L5", lambda a=None: layer(smp("boom_sub") * 0.9, smp("hit_low", -5) * 0.7, smp("click_double_1", -12) * 0.6), "Katta muhr 'RAD ETILDI': boom_sub + hit_low −5 + qo'sh klik −12"),
})
FRONT.update({"sfx.stamp_big"})
AB_PENT = [68, 70, 72, 75, 77, 80, 82, 84, 87, 89]

CUES_20 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Ofis — sahna 'havosi'", 9.6),
    (0.05, "sfx.whoosh_soft", 0.2, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    (0.8, "sfx.notify_pop", 0.3, -0.3, 0.2, 0, "Buxgalter: 'Hujjatlar qani?'", None),
    (1.6, "sfx.pop_swish", 0.28, 0.3, 0.2, 0, "Siz: 'Kartadan o'tkazganman...'", None),
    (2.4, "sfx.notify_pop", 0.3, -0.3, 0.2, 0, "Buxgalter: 'Shartnoma? Faktura? Dalolatnoma?'", 2),
    *[(2.4 + k * 0.3, "fx.paper", 0.1, round(((k * 3) % 7 - 3) * 0.2, 2), 0.25, 0, f"Cheklar uchib tushadi #{k + 1}", None) for k in range(0, 20, 3)],
    (3.1, "sfx.swipe", 0.26, 0, 0.15, 0, "Hujjatlar ro'yxati ochiladi", None),
    *[(at, "sfx.glitch_short", 0.3, -0.2 + 0.2 * i, 0.15, 0, f"✕ yo'q #{i + 1}", -3 - 2 * i) for i, at in enumerate((3.3, 3.6, 3.9))],
    (4.6, "sfx.notify_pop", 0.3, -0.3, 0.2, 0, "Buxgalter: 'Hisobdan chiqarib bo'lmaydi'", -2),
    (5.4, "sfx.notify_ring", 0.34, 0.2, 0.25, 0, "Soliq xizmati xabari", -5),
    (7.0, "sfx.pop_swish", 0.24, 0.3, 0.2, 0, "Siz: '???'", -3),
    *[x for at, pan, nm in ((5.6, -0.4, "SHARTNOMA YO'Q"), (6.6, 0.4, "FAKTURA YO'Q"), (7.6, -0.4, "NAQD · KARTA")) for x in [
        (at, "sfx.stutter", 0.42, pan, 0.2, 0, f"Slam: {nm}", None),
        (at, "sfx.glitch_short", 0.5, pan, 0.2, 0, "Slam qatlami", None),
    ]],
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [58, 61, 65, 70]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da, gate kesadi", None),
    (8.5, "sfx.boom_sub", 0.9, 0, 0.35, 0, "QORA XARAJAT — asosiy zarba", None),
    (8.5, "sfx.hit_low", 0.6, 0, 0.4, 0, "Zarba qatlami: tonal", None),
    (8.5, "sfx.glitch_seq", 0.28, 0, 0.2, 0, "Zarba qatlami: glitch", None),
    (9.62, "sfx.stamp_big", 0.45, 0, 0, 0, "OVOZ VAKUUMI: 'RAD ETILDI' muhri", None),
    (9.95, "fx.heartbeat", 0.28, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (Ab-major)", [68, 72, 75, 80]),
    (10.4, "sfx.swipe", 0.4, -0.3, 0.2, 0, "Varaq ag'dariladi (1-yarmi)", -4),
    (10.7, "sfx.swipe", 0.4, 0.3, 0.2, 0, "Varaq ag'dariladi (2-yarmi)", 3),
    (11.0, "sfx.boom_sub", 0.5, 0, 0.35, 0, "Yechim boshlanishi", None),
    (11.0, "sfx.hit_chime", 0.32, 0, 0.4, 0.2, "Yechim: tonal urg'u", 6),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "sfx.whoosh_soft", 0.2, -0.3, 0.2, 0, "Telefon kiradi", None),
    (12.0, "sfx.click_1", 0.7, 0.3, 0, 0, "'Yuridik shaxs sifatida to'lash' tumbleri", None),
    (12.05, "ui.select", 0.15, 0.3, 0.25, 0.2, "Tumbler yoqildi (tonallikda)", 80),
    *[x for i, at in enumerate((12.6, 13.0, 13.4)) for x in [
        (at - 0.3, "sfx.pop_swish", 0.2, -0.2 + 0.2 * i, 0.2, 0, f"Hujjat #{i + 1} yaratilmoqda", 2 * i),
        (at, f"sfx.{CLICKS[i + 1]}", 0.55, 0.3, 0.1, 0, f"Hujjat #{i + 1} ✓", None),
        (at + 0.02, "ui.select", 0.14, 0.3, 0.25, 0.2, "Tonallikdagi tasdiq", [75, 80, 84][i]),
    ]],
    (13.9, "fx.stamp", 0.3, 0.2, 0.2, 0, "E-IMZO muhri", None),
    (13.9, "sfx.hit_chime", 0.26, 0.2, 0.3, 0.2, "E-imzo — tonal urg'u", 11),
    (14.3, "sfx.pop_swish", 0.2, 0.2, 0.2, 0, "Dalolatnoma yaratilmoqda", 6),
    (14.6, "sfx.click_5", 0.55, 0.3, 0.1, 0, "Dalolatnoma ✓", None),
    (14.62, "ui.select", 0.14, 0.3, 0.25, 0.2, "Tonallikdagi tasdiq", 87),
    (15.2, "sfx.click_double_2", 0.7, 0.2, 0, 0, "'Buxgalteriyaga eksport'", None),
    *[(15.35 + k * 0.12, "sfx.whoosh_sweep", 0.12, 0.5, 0.2, 0, f"Hujjat #{k + 1} buxgalterga uchadi", 5 + k * 2) for k in range(4)],
    (15.25, "sfx.pop_swish", 0.25, 0.6, 0.2, 0, "Buxgalter avatari", -2),
    (16.4, "sfx.notify_ring", 0.36, 0.1, 0.25, 0.2, "Buxgalter: 'Rahmat! Hammasi joyida'", 3),
    (16.42, "ui.success", 0.2, 0.1, 0.4, 0.2, "Musiqiy tasdiq", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: OQ SAVDO oldidan", [72, 75, 80, 84]),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "OQ SAVDO — zarba", None),
    (18.5, "sfx.hit_chime", 0.5, 0, 0.4, 0.2, "Zarba qatlami: tonal", 6),
    (18.5, "imp.sparkle", 0.35, 0, 0.5, 0, "Oltin uchqunlar", 263),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Oyna ko'tariladi", None),
    (19.9, "ui.success", 0.26, 0, 0.5, 0.3, "Hujjatlar tayyor", None),
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — cho'qqisi whip'da (21.75 s)", None),
    (21.75, "sfx.whoosh_sweep", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (21.75, "sfx.swipe", 0.3, 0, 0.2, 0, "Whip qatlami", None),
    (22.0, "sfx.boom_sub", 0.6, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.0, "sfx.hit_low", 0.4, 0, 0.4, 0, "Zarba qatlami", 6),
    *[(22.35 + i * 0.18, "sfx.pop_swish", 0.22, round(-0.45 + 0.3 * i, 2), 0.25, 0.15, f"Hujjat kartasi #{i + 1}", [0, 2, 4, 7][i]) for i in range(4)],
    (23.15, "fx.stamp", 0.4, 0, 0.2, 0, "TASDIQLANDI muhri", None),
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA — hujjatlar tasdiqlandi", None),
    (23.22, "sfx.notify_ring", 0.22, 0.2, 0.25, 0.2, "Kassa qatlami", 6),
    *[(23.5 + i * 0.35, "sfx.swipe", 0.34, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, f"sfx.{CLICKS[(i + 2) % 5]}", 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [80, 84, 87][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [72, 77, 80, 84]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "imp.sparkle", 0.4, 0, 0.5, 0, "Uchqunlar", 269),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_swish", 0.3, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [7, 12, 16][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Tonallikdagi qo'ng'iroqcha", [87, 92, 96][i]),
    ]],
    (26.85, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (Ab tonikada)", 68),
    (28.3, "sfx.click_1", 0.35, 0.2, 0.3, 0.3, "CTA tugmasi", None),
    (28.32, "ui.select", 0.07, 0.2, 0.5, 0.4, "CTA qo'ng'iroqchasi", 96),
]

SOUNDS.update({
    "sfx.splat": ("L5", lambda a=None: layer(smp("pop_swish", -12), smp("glitch_short", -12) * 0.4), "Siyoh sachrashi: pop_swish −12 + glitch_short −12"),
})
FRONT.update({"sfx.splat"})
CUES_20 += [  # FX v2: effektlar uchun qo'shimcha ovozlar
    *[(at + 0.12, "sfx.tick", 0.2, 0.3, 0.3, 0.25, "Yaltiroq nur (glint)", 12) for at in (12.0, 12.6, 13.0, 13.9, 14.6, 15.2, 16.5)],
    (5.4, "sfx.stutter", 0.2, 0.2, 0.15, 0, "Soliq xabari — RGB glitch", 5),
    (9.66, "sfx.splat", 0.4, 0, 0, 0, "Muhr ostidan siyoh sachraydi", None),
    (10.7, "sfx.hit_chime", 0.18, 0, 0.4, 0.2, "Varaq o'rtasida yorug'lik chizig'i", 12),
    (13.9, "sfx.pop_swish", 0.22, 0.3, 0.2, 0, "E-imzo siyohi sachraydi", -7),
    (16.0, "sfx.pop_swish", 0.2, 0.6, 0.3, 0.2, "Hujjatlar buxgalterga yetdi — uchqun", 9),
    (18.45, "sfx.whoosh_soft", 0.12, 0, 0.4, 0, "Oltin nurlar ochiladi", 7),
    (22.3, "sfx.whoosh_soft", 0.12, 0, 0.4, 0, "Hujjatlar ortida nurlar", 7),
    (23.2, "sfx.pop_swish", 0.22, 0, 0.3, 0, "Yashil siyoh sachraydi", -9),
    (25.0, "sfx.hit_chime", 0.15, 0, 0.4, 0.2, "Nishonlar ustida flare", 12),
]
CUES_20.sort(key=lambda c: c[0])

SCORE_20 = [
    ("Ovoz manbai", "Foydalanuvchi SFX kutubxonasi (sfx/) + FX v2", "FX v2: har yaltiroq nur — yuqori tik (glint), siyoh sachrashlari — past pop_swish, nurlar — yumshoq whoosh, flare — hit_chime +12. UI, o'tish va zarba ovozlari — sfx.* namunalari (kliklar, qo'sh klik, pop_swish, swipe, whoosh, riser_click, stutter/glitch, notify, hit_low/hit_chime, boom_sub). Sintez: partitura, J-cut swell, tonallikdagi qo'ng'iroqchalar, success, uchqunlar, kassa, qog'oz shitirlashi, kichik muhr (fx.stamp), sonic logo."),
    ("0:00–0:09.5", "Muammo · Bb-minor, tashvishli minimal", "7-qism aranjirovkasi 6 yarim ton yuqorida. Ustida: buxgalter xabarlari (notify_pop), sizning javoblaringiz (pop_swish), cheklar shitirlashi, hujjatlar ro'yxati (swipe) va uchta '✕' — pastga tushib boruvchi qisqa glitchlar, soliq xabari (notify_ring pastroq), slamlar — stutter + glitch."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: 'RAD ETILDI' muhri kadrga uriladi — boom_sub + hit_low (−5) + qo'sh klik (−12) bitta og'ir zarbaga yig'ilgan; yurak urishi. Keyin J-cut swell Ab-major'da."),
    ("0:10.4–0:11", "Varaq ag'dariladi", "Ikki swipe (pastroq va balandroq) — varaqning ikki yarmi."),
    ("0:11–0:21.75", "Yechim · Ab-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: tumbler (klik + qo'ng'iroqcha), har hujjat — pop (yaratilmoqda) → klik + tonallikdagi tasdiq, E-imzo muhri + hit_chime, eksport (qo'sh klik + 4 ta ko'tariluvchi whoosh), buxgalter javobi (notify_ring)."),
    ("0:22–0:27", "Natija · Ab-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. To'rt hujjat kartasi (ko'tariluvchi pop), TASDIQLANDI muhri + kassa (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (Ab tonikada), so'nish."),
]


def score_20(M):
    """7-qism partiturasi, 6 yarim ton yuqorida."""
    global KEY_SHIFT
    KEY_SHIFT = 6
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_20():
    """20-qism: Qonuniy va oq savdo (B2B). Score + cue-sheet (CUES_20), SFX — sfx/ kutubxonasi."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # "RAD ETILDI" stamp: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_20(M)
    render_cues(M, CUES_20)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 21-qism: Raqamli adolat (Arbitraj) — sfx/ + FX v2 ----------
SOUNDS.update({
    "sfx.dust": ("L5", lambda a=None: smp("glitch_noise", 5) * np.linspace(0.3, 1, len(smp("glitch_noise", 5))) ** 0.5, "Kulga aylanish: glitch_noise +5, sekin kuchayib"),
    "sfx.gavel": ("L5", lambda a=None: layer(smp("boom_sub") * 0.8, smp("hit_low", 5) * 0.8, smp("click_double_2", -10) * 0.9), "Sudya bolg'asi: boom_sub + hit_low +5 + qo'sh klik −10"),
})
FRONT.update({"sfx.dust"})
F_PENT = [65, 67, 69, 72, 74, 77, 79, 81, 84, 86]

CUES_21 = [
    (0.0, "amb.office", 0.09, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "sfx.whoosh_soft", 0.2, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    (0.5, "sfx.pop_swish", 0.28, 0, 0.2, 0, "Reklama posti chiqdi (18:00)", None),
    (0.55, "sfx.tick", 0.2, 0, 0.3, 0.25, "Post yaltiraydi (glint)", 12),
    *[(1.4 + k * 0.17, "sfx.tick", 0.08 + 0.01 * k, 0.4, 0.1, 0, "Vaqt tez o'tadi 18:00 → 20:07", 3) for k in range(13)],
    (3.7, "sfx.glitch_seq", 0.4, 0, 0.2, 0, "POST O'CHIRILDI — RGB glitch", None),
    (3.7, "sfx.hit_low", 0.4, 0, 0.3, 0, "O'chirish zarbasi", -5),
    (4.4, "sfx.pop_swish", 0.26, 0.3, 0.2, 0, "Boshqa reklama tepaga qadaldi", 4),
    (4.4, "sfx.stutter", 0.16, 0.3, 0.1, 0, "Kichik glitch", 7),
    (5.0, "sfx.pop_swish", 0.24, 0.3, 0.2, 0, "Siz: 'Post qayerda?'", -2),
    (6.0, "sfx.notify_pop", 0.3, -0.3, 0.2, 0, "Admin: 'Kanal qoidasi'", None),
    (7.0, "sfx.notify_ring", 0.3, 0, 0.25, 0, "Admin sizni blokladi", -6),
    *[x for at, pan, nm in ((5.6, -0.4, "POST O'CHIRILDI"), (6.6, 0.4, "2 SOAT"), (7.6, -0.4, "PUL KETDI")) for x in [
        (at, "sfx.stutter", 0.42, pan, 0.2, 0, f"Slam: {nm}", None),
        (at, "sfx.glitch_short", 0.5, pan, 0.2, 0, "Slam qatlami", None),
    ]],
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [55, 58, 62, 67]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da, gate kesadi", None),
    (8.5, "sfx.boom_sub", 0.9, 0, 0.35, 0, "VA'DA BUZILDI — asosiy zarba", None),
    (8.5, "sfx.hit_low", 0.6, 0, 0.4, 0, "Zarba qatlami: tonal", None),
    (8.5, "sfx.glitch_seq", 0.28, 0, 0.2, 0, "Zarba qatlami: glitch", None),
    (9.6, "sfx.dust", 0.45, 0.2, 0, 0, "OVOZ VAKUUMI: va'da kulga aylanib sochiladi", None),
    (9.95, "fx.heartbeat", 0.28, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.4, 0, 0.3, 0, "J-cut: yechim akkordi (F-major)", [65, 69, 72, 77]),
    (10.22, "sfx.whoosh_sweep", 0.3, 0.3, 0.2, 0, "Bolg'a ko'tarilib tushadi", -3),
    (10.5, "sfx.gavel", 0.85, 0, 0.45, 0.15, "SUDYA BOLG'ASI — o'tish", None),
    (10.52, "sfx.hit_chime", 0.22, 0, 0.4, 0.2, "Flare jarangi", 12),
    (11.0, "sfx.boom_sub", 0.45, 0, 0.35, 0, "Yechim boshlanishi", None),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "sfx.whoosh_soft", 0.2, -0.3, 0.2, 0, "Telefon kiradi", None),
    *[(12.0 + k * 0.28, "sfx.tick", 0.16, round(-0.3 + 0.12 * (k % 6), 2), 0.2, 0.2, f"Bot tekshiruvi #{k + 1} — post joyida", 7) for k in range(5)],
    *[(12.0 + k * 0.28 + 0.02, "ui.select", 0.06, 0.2, 0.3, 0.2, "Tekshiruv — tonallikdagi tasdiq", 81) for k in range(5)],
    (13.4, "sfx.glitch_short", 0.5, 0, 0.2, 0, "BUZILISH ANIQLANDI", -3),
    (13.4, "sfx.notify_ring", 0.36, 0, 0.25, 0.2, "Ogohlantirish", -4),
    (13.45, "fx.shutter", 0.3, 0.2, 0.15, 0, "Dalil: skrinshot", None),
    (13.62, "sfx.tick", 0.18, 0.3, 0.3, 0.25, "Dalil kartasi yaltiraydi", 12),
    (14.2, "sfx.pop_swish", 0.24, 0, 0.2, 0, "Arbitraj ko'rib chiqmoqda", 2),
    (14.25, "sfx.ratchet_roll", 0.16, -0.2, 0.15, 0, "Tarozi tebranadi", None),
    (15.0, "sfx.gavel", 0.4, 0, 0.35, 0, "Qaror: buyurtmachi foydasiga", None),
    (15.02, "ui.success", 0.22, 0, 0.4, 0.2, "Musiqiy tasdiq", None),
    (15.1, "sfx.tick", 0.18, 0.3, 0.3, 0.25, "Qaror kartasi yaltiraydi", 12),
    *[(15.6 + k * 0.1 + 0.5, "fx.coin", 0.07, round(-0.4 + 0.15 * k, 2), 0.2, 0, f"Tanga qaytdi #{k + 1}", None) for k in range(6)],
    (15.6, "sfx.whoosh_soft", 0.16, 0.4, 0.2, 0, "Pul qaytmoqda", 5),
    (16.3, "sfx.notify_ring", 0.34, -0.2, 0.25, 0.2, "1 200 000 so'm qaytarildi", 3),
    (16.4, "sfx.tick", 0.18, -0.2, 0.3, 0.25, "Qaytarildi kartasi yaltiraydi", 12),
    (16.6, "sfx.pop_swish", 0.22, 0.2, 0.2, 0, "Admin reytingi pasayadi", -7),
    (17.0, "sfx.glitch_short", 0.2, 0.2, 0.2, 0, "4.6 → 3.9", -7),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: ADOLAT oldidan", [69, 72, 77, 81]),
    (18.45, "sfx.whoosh_soft", 0.12, 0, 0.4, 0, "Oltin nurlar ochiladi", 7),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "ADOLAT — zarba", None),
    (18.5, "sfx.hit_chime", 0.5, 0, 0.4, 0.2, "Zarba qatlami: tonal", 3),
    (18.5, "imp.sparkle", 0.35, 0, 0.5, 0, "Oltin uchqunlar", 301),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Oyna ko'tariladi", None),
    (19.9, "ui.success", 0.26, 0, 0.5, 0.3, "Pul qaytarildi", None),
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — cho'qqisi whip'da (21.75 s)", None),
    (21.75, "sfx.whoosh_sweep", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (21.75, "sfx.swipe", 0.3, 0, 0.2, 0, "Whip qatlami", None),
    (22.0, "sfx.boom_sub", 0.5, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.3, "sfx.whoosh_soft", 0.14, 0.3, 0.3, 0, "Bolg'a ko'tariladi; nurlar", 4),
    (22.75, "sfx.gavel", 0.75, 0, 0.45, 0.15, "BOLG'A — adolat", None),
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA — 1 200 000 qaytdi", None),
    (23.22, "sfx.notify_ring", 0.22, 0.2, 0.25, 0.2, "Kassa qatlami", 3),
    *[(23.5 + i * 0.35, "sfx.swipe", 0.34, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, f"sfx.{CLICKS[(i + 1) % 5]}", 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [77, 81, 84][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [69, 74, 77, 81]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "sfx.hit_chime", 0.15, 0, 0.4, 0.2, "Flare jarangi", 12),
    (25.0, "imp.sparkle", 0.4, 0, 0.5, 0, "Uchqunlar", 303),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_swish", 0.3, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [7, 12, 16][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Tonallikdagi qo'ng'iroqcha", [84, 89, 93][i]),
    ]],
    (26.85, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (F tonikada)", 65),
    (28.3, "sfx.click_1", 0.35, 0.2, 0.3, 0.3, "CTA tugmasi", None),
    (28.32, "ui.select", 0.07, 0.2, 0.5, 0.4, "CTA qo'ng'iroqchasi", 93),
]

SCORE_21 = [
    ("Ovoz manbai", "Foydalanuvchi SFX kutubxonasi (sfx/) + FX v2", "UI, o'tish va zarba ovozlari — sfx.* namunalari. Yangi yig'malar: sfx.gavel (boom_sub + hit_low +5 + qo'sh klik −10) va sfx.dust (glitch_noise +5, sekin kuchayib). Sintez: partitura, swell, tonallikdagi qo'ng'iroqchalar, success, uchqunlar, kassa, skrinshot zatvori, sonic logo."),
    ("0:00–0:09.5", "Muammo · G-minor, tashvishli minimal", "7-qism aranjirovkasi 3 yarim ton yuqorida. Ustida: post chiqadi (pop + glint), vaqt tez o'tadi (tobora balandlashuvchi tiklar), 3.7 s — post o'chiriladi (glitch_seq + past hit), boshqa reklama, chat, blok; slamlar — stutter + glitch."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: 'Bu xabar o'chirildi' kartasi kulga aylanib sochiladi — sfx.dust; yurak urishi va qizil pulsatsiya. Keyin J-cut swell F-major'da."),
    ("0:10.2–0:11", "Sudya bolg'asi", "Bolg'a ko'tarilib tushadi (whoosh_sweep) va 10.5 s da uriladi — sfx.gavel + flare jarangi; oltin doira ochiladi."),
    ("0:11–0:21.75", "Yechim · F-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: bot tekshiruvlari (tik + tonallik), buzilish aniqlandi (glitch + notify_ring), skrinshot-dalil, arbitraj (ratchet — tarozi tebranadi), qaror (kichik bolg'a), tangalar qaytadi, reyting pasayadi."),
    ("0:22–0:27", "Natija · F-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Bolg'a zarbasi, kassa (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (F tonikada), so'nish."),
]


def score_21(M):
    """7-qism partiturasi, 3 yarim ton yuqorida."""
    global KEY_SHIFT
    KEY_SHIFT = 3
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_21():
    """21-qism: Raqamli adolat (Arbitraj). Score + cue-sheet (CUES_21), SFX — sfx/ kutubxonasi."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # the promise turns to dust: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_21(M)
    render_cues(M, CUES_21)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- Musiqa uslubi (foydalanuvchi referenslari v2: "Heavenly-meme", "Dexter-meme") — ORIGINAL sintez ----------
# Referens treklarning o'zi ishlatilmaydi (mualliflik huquqi); faqat kayfiyati: xor "aaah" (vahiy lahzasi) va
# o'ynoqi-sirli pizzicato (muammo sahnasi). Ikkalasi ham shu yerda noldan sintez qilinadi.
def karplus(freq, dur, bright=0.5, seed=0):
    n, p = int(dur * SR), max(2, int(SR / freq))
    g = np.random.default_rng(seed)
    buf = g.uniform(-1, 1, p) * 0.8
    out = np.empty(n)
    a = 0.5 + 0.49 * bright
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = a * buf[i % p] + (1 - a) * buf[(i + 1) % p]
        buf[i % p] *= 0.996
    return out * np.exp(-seconds(dur) / (dur * 0.35))


def choir(notes, dur, vowel="a", vib=5.2):
    x = seconds(dur)
    F = {"a": [(750, 1.0), (1150, 0.6), (2600, 0.15)], "o": [(500, 1.0), (850, 0.5), (2500, 0.1)]}[vowel]
    out = np.zeros(len(x))
    for k, nt in enumerate(notes):
        f0 = m(nt)
        src = np.zeros(len(x))
        for dt in (-7, -2, 3, 8):
            ph = 2 * np.pi * np.cumsum(f0 * 2 ** (dt / 1200) * (1 + 0.004 * np.sin(2 * np.pi * vib * x + k + dt))) / SR
            src += 2 * ((ph / (2 * np.pi)) % 1) - 1
        voice = sum(filt(src, "bandpass", [fc * 0.85, fc * 1.15]) * w for fc, w in F)
        out += voice
    air = filt(rng.standard_normal(len(x)), "bandpass", [3000, 8000]) * 0.03
    envl = np.clip(x / 0.7, 0, 1) * np.clip((dur - x) / 1.0, 0, 1)
    return (out / max(1, len(notes)) * 0.5 + air) * envl


def quirky_pizz(M, start, end, root=64, gain=0.16):
    """O'ynoqi-sirli pizzicato motiv (original): 8-lik notalar, xromatik pasayish va tritonga ishora."""
    motif = [0, 7, 3, 6, 0, 7, 10, 6, 0, 7, 3, 2, -1, 3, 6, 5]
    for k, at in enumerate(np.arange(start, end - 0.05, 0.25)):
        nt = root + motif[k % len(motif)] + (12 if (k // 16) % 2 else 0)
        acc = 1.0 if k % 4 == 0 else 0.7
        M.put("music", at, karplus(m(nt), 0.4, 0.55, seed=k), gain * acc, -0.35 if k % 2 else 0.35, verb=0.25, echo=0.15)


SOUNDS.update({
    "mus.choir_d": ("L1", lambda a=None: choir([62, 66, 69, 74], a or 2.5), "Xor 'aaah' D-major (heavenly uslub, original sintez)"),
    "mus.choir_g": ("L1", lambda a=None: choir([55, 62, 67, 71], a or 2.5), "Xor 'aaah' G-major"),
    "mus.choir_hi": ("L1", lambda a=None: choir([74, 78, 81], a or 1.8, "o"), "Baland xor 'ooo' — uchqunlar ustida"),
})


# ---------- 22-qism: Jalb qiluvchi kontent — sfx/ + FX v2 + kinetik matn + yangi musiqa uslubi ----------
SFX_LIB.update({
    "bass_drop": ("L5", "Past bass-zarba (matn chiqishi)"), "tick_hi": ("L3", "Yuqori matn tiki (6.5 kHz)"),
    "shimmer": ("L3", "Yaltiroq shimmer (8.7 kHz tonal)"), "type_burst": ("L3", "Yozish shitirlashi (typewriter)"),
    "blip_up": ("L3", "Ko'tariluvchi bliplar"), "sparkle_hit": ("L5", "Sparkle-zarba"), "swoosh_text": ("L4", "Matn whoosh'i"),
    "whoosh_low": ("L4", "Past whoosh / swell"), "thump": ("L5", "Qisqa thump"), "pluck_tone": ("L3", "Tonal pluck (0.75 s)"),
    "pop_short": ("L3", "Qisqa pop"), "click_soft": ("L3", "Yumshoq klik"), "chime_swell": ("L3", "Chime-swell"),
})
SOUNDS.update({f"sfx.{n}": (lay, (lambda a=None, n=n: smp(n, a or 0)), d) for n, (lay, d) in SFX_LIB.items()})
SOUNDS.update({
    "sfx.letters_fall": ("L3", lambda a=None: layer(*[np.concatenate([np.zeros(int(k * 0.035 * SR)), smp("tick_hi", (k * 5) % 12 - 6) * (0.4 + 0.6 * ((k * 7) % 5) / 4)]) for k in range(20)]), "Harflar birin-ketin tushadi: 20 ta tick_hi turli balandlikda"),
})
FRONT.update({"sfx.letters_fall"})

CUES_22 = [
    (0.0, "amb.office", 0.08, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "sfx.whoosh_soft", 0.2, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    (0.15, "sfx.tick_hi", 0.25, 0, 0.2, 0.2, "'22-QISM' harflari tushadi", None),
    (0.3, "sfx.swoosh_text", 0.3, 0, 0.2, 0, "Sarlavha blur-fade-up", None),
    *[x for i, (a, b) in enumerate([(1.3, 2.8), (4.3, 4.9), (6.4, 6.75)]) for x in [
        (a - 0.7, "sfx.whoosh_soft", 0.12, 0.2, 0.15, 0, f"Lenta aylanadi #{i + 1}", 5),
        (a, "sfx.click_soft", 0.3, 0, 0.1, 0, f"Ko'z to'xtadi — {b - a:.1f} s", None),
        (b, "sfx.swipe", 0.5, 0.3, 0.15, 0, f"O'TIB KETILDI #{i + 1} (flick)", 4),
        (b + 0.15, "sfx.glitch_short", 0.22, 0.3, 0.1, 0, "RGB glitch", 4),
    ]],
    *[x for at, pan, nm in ((5.6, -0.4, "ZERIKARLI"), (6.6, 0.4, "UZUN MATN"), (7.6, -0.4, "O'TIB KETILDI")) for x in [
        (at, "sfx.stutter", 0.42, pan, 0.2, 0, f"Slam: {nm}", None),
        (at, "sfx.glitch_short", 0.5, pan, 0.2, 0, "Slam qatlami", None),
    ]],
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [52, 55, 59, 64]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da", None),
    (8.5, "sfx.boom_sub", 0.9, 0, 0.35, 0, "KO'RINMAS — asosiy zarba", None),
    (8.5, "sfx.bass_drop", 0.6, 0, 0.3, 0, "Zarba qatlami: bass drop", None),
    (8.5, "sfx.glitch_seq", 0.26, 0, 0.2, 0, "Zarba qatlami: glitch", None),
    (9.6, "sfx.letters_fall", 0.45, 0, 0, 0, "OVOZ VAKUUMI: harflar birin-ketin tushadi", None),
    (9.95, "fx.heartbeat", 0.26, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: yechim akkordi (D-major)", [62, 66, 69, 74]),
    (10.2, "mus.choir_d", 1.2, 0, 0.6, 0.2, "HEAVENLY XOR 'aaah' — vahiy lahzasi", 2.8),
    (10.45, "sfx.whoosh_low", 0.4, 0, 0.3, 0, "Zoom-through o'tishi", None),
    (10.75, "sfx.shimmer", 0.3, 0, 0.4, 0.2, "Flare yaltirog'i", None),
    (11.0, "sfx.boom_sub", 0.45, 0, 0.35, 0, "Yechim boshlanishi", None),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "sfx.whoosh_soft", 0.2, -0.3, 0.2, 0, "Telefon kiradi", None),
    *[(11.4 + i * 0.1, "sfx.pop_short", 0.3, round(-0.4 + 0.27 * i, 2), 0.2, 0, f"Shablon #{i + 1} paydo bo'ladi", [0, 3, 7, 12][i]) for i in range(4)],
    *[(11.8 + i * 0.12, "sfx.shimmer", 0.12, round(-0.4 + 0.27 * i, 2), 0.3, 0.2, f"Shablon #{i + 1} yaltiraydi", None) for i in range(4)],
    (12.1, "sfx.click_1", 0.7, -0.3, 0, 0, "'−30%' shabloni tanlandi", None),
    (12.25, "sfx.swipe", 0.3, 0.3, 0.15, 0, "Konstruktorga o'tish", None),
    (12.7, "sfx.bass_drop", 0.4, 0, 0.3, 0, "'−30%' BOUNCE", 5),
    (12.72, "sfx.sparkle_hit", 0.3, 0, 0.3, 0.2, "Bounce yaltirog'i", None),
    (13.0, "sfx.blip_up", 0.35, 0, 0.25, 0.2, "'YANGI KOLLEKSIYA' letter-up", None),
    (13.3, "sfx.type_burst", 0.4, 0.2, 0.15, 0, "'Faqat 3 kun!' typewriter", None),
    (13.6, "sfx.pop_short", 0.35, 0, 0.2, 0, "'Buyurtma berish' tugmasi", 5),
    (14.0, "sfx.click_2", 0.7, 0.1, 0, 0, "Animatsiya: Flicker", None),
    (14.05, "sfx.shimmer", 0.35, 0, 0.3, 0.2, "FLICKER — sarlavha qayta jonlanadi", None),
    (14.05, "sfx.glitch_short", 0.18, 0, 0.2, 0, "Flicker glitch", 7),
    (14.5, "sfx.click_3", 0.7, -0.2, 0, 0, "Brend rangi tanlandi", None),
    (14.52, "sfx.chime_swell", 0.3, 0, 0.3, 0.2, "Rang almashadi", None),
    (15.2, "sfx.click_double_2", 0.7, 0.2, 0, 0, "'Kanallarga yuborish'", None),
    (15.32, "sfx.tick", 0.2, 0.3, 0.3, 0.25, "Tugma yaltiraydi (glint)", 12),
    (15.45, "sfx.swoosh_text", 0.35, 0.3, 0.2, 0, "Lentaga o'tish", None),
    (15.6, "sfx.whoosh_soft", 0.14, 0, 0.2, 0, "Lenta aylanadi...", 5),
    (16.6, "sfx.thump", 0.5, 0, 0.25, 0, "...va TO'XTAYDI — sizning reklamangizda", None),
    (16.62, "sfx.sparkle_hit", 0.35, 0, 0.3, 0.2, "Ko'z to'xtadi", None),
    (16.65, "mus.choir_hi", 0.6, 0, 0.6, 0.2, "Xor 'ooo' — ko'z to'xtadi", 1.6),
    (16.9, "sfx.ratchet_roll", 0.2, -0.2, 0.15, 0, "Statistika o'smoqda", None),
    (17.3, "sfx.tick", 0.2, 0.2, 0.3, 0.25, "Statistika kartasi yaltiraydi", 12),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: KO'Z TO'XTAYDI oldidan", [66, 69, 74, 78]),
    (18.45, "sfx.whoosh_soft", 0.12, 0, 0.4, 0, "Oltin nurlar ochiladi", 7),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "KO'Z TO'XTAYDI — zarba", None),
    (18.5, "sfx.bass_drop", 0.5, 0, 0.3, 0, "Color-bounce zarbasi", None),
    (18.5, "mus.choir_d", 0.8, 0, 0.6, 0.2, "Xor 'aaah' zarba ostida", 1.8),
    (18.5, "imp.sparkle", 0.3, 0, 0.5, 0, "Oltin uchqunlar", 331),
    (18.75, "sfx.swoosh_text", 0.3, 0, 0.2, 0, "Taglavha blur-fade-up", None),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Oyna ko'tariladi", None),
    (19.9, "ui.success", 0.24, 0, 0.5, 0.3, "Reklama tayyor", None),
    (20.3, "sfx.blip_up", 0.3, 0, 0.25, 0.2, "'Reklama tayyor!' letter-up", 5),
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — cho'qqisi whip'da (21.75 s)", None),
    (21.75, "sfx.whoosh_sweep", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (21.75, "sfx.swipe", 0.3, 0, 0.2, 0, "Whip qatlami", None),
    (22.0, "sfx.boom_sub", 0.5, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.2, "sfx.tick_hi", 0.25, 0, 0.2, 0.2, "'NATIJA' harflari", None),
    (22.3, "sfx.swoosh_text", 0.3, 0.2, 0.2, 0, "Sarlavha word-right", None),
    (22.35, "sfx.pop_short", 0.3, -0.4, 0.2, 0, "Oldingi post", -5),
    (22.6, "sfx.bass_drop", 0.45, 0.4, 0.3, 0, "Yangi karta — bounce", 5),
    (22.62, "sfx.sparkle_hit", 0.3, 0.4, 0.3, 0.2, "Karta yaltiraydi", None),
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA — CTR 3.8%", None),
    (23.22, "sfx.notify_ring", 0.22, 0.2, 0.25, 0.2, "Kassa qatlami", None),
    *[(23.5 + i * 0.35, "sfx.swipe", 0.34, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, f"sfx.{CLICKS[(i + 3) % 5]}", 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [74, 78, 81][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [66, 71, 74, 78]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "sfx.shimmer", 0.25, 0, 0.4, 0.2, "Flare yaltirog'i", None),
    (25.0, "imp.sparkle", 0.35, 0, 0.5, 0, "Uchqunlar", 337),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_short", 0.32, -0.4 + 0.4 * i, 0.3, 0, f"Nishon #{i + 1}", [7, 12, 16][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Tonallikdagi qo'ng'iroqcha", [81, 86, 90][i]),
    ]],
    (26.85, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (D tonikada)", 62),
    (27.0, "mus.choir_d", 0.5, 0, 0.6, 0.2, "Xor logotip ostida", 3.5),
    (28.3, "sfx.click_1", 0.35, 0.2, 0.3, 0.3, "CTA tugmasi", None),
    (28.32, "ui.select", 0.07, 0.2, 0.5, 0.4, "CTA qo'ng'iroqchasi", 90),
]

SCORE_22 = [
    ("Ovoz manbai", "sfx/ kutubxonasi (39 ta) + FX v2 + yangi musiqa uslubi", "Matn animatsiyalari uchun yangi namunalar: tick_hi (harflar), swoosh_text (blur/word), type_burst (typewriter), blip_up (letter-up), bass_drop + sparkle_hit (bounce), shimmer (flicker), pop_short, click_soft, thump, chime_swell, whoosh_low. Musiqa: 7-qism partiturasi + ORIGINAL 'heavenly' xor (formant 'aaah') va o'ynoqi-sirli pizzicato (Karplus-Strong) — foydalanuvchi referenslari kayfiyatida, lekin ularning o'zi emas."),
    ("0:00–0:09.5", "Muammo · E-minor + pizzicato", "7-qism aranjirovkasi asl tonallikda + o'ynoqi-sirli pizzicato motivi (8-lik notalar, xromatik pasayish, tritonga ishora; chap-o'ng navbatma-navbat). Lenta aylanishi (yumshoq whoosh), har to'xtash — yumshoq klik, har flick — swipe + glitch; slamlar — stutter + glitch."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: zerikarli postning harflari birin-ketin tushadi — 20 ta tick_hi turli balandlikda; yurak urishi."),
    ("0:10.15–0:11", "Vahiy lahzasi", "HEAVENLY XOR 'aaah' D-major'da (original sintez) + past whoosh (zoom-through) + shimmer."),
    ("0:11–0:21.75", "Yechim · D-major, siyrak", "Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Har kinetik matn presetining o'z ovozi: bounce — bass_drop + sparkle, letter-up — blip_up, typewriter — type_burst, flicker — shimmer + glitch. Lenta to'xtaganda — thump + sparkle + baland xor 'ooo'."),
    ("0:22–0:27", "Natija · D-major, to'liq", "To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Kassa (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (D tonikada) ostida yumshoq xor, so'nish."),
]


def render_22():
    """22-qism: Jalb qiluvchi kontent. Score (7-qism) + pizzicato + xor + cue-sheet (CUES_22)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # the letters fall off: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_7(M)
    quirky_pizz(M, 1.0, 9.45, root=64, gain=0.4)
    render_cues(M, CUES_22)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 23-qism: Iliq mijozlarni qaytarish — birinchi NEON qism (neon.js), sfx/ + xor + pizzicato ----------
SOUNDS.update({
    "mus.choir_c": ("L1", lambda a=None: choir([60, 64, 67, 72], a or 2.5), "Xor 'aaah' C-major (heavenly uslub, original sintez)"),
    "mus.choir_c_hi": ("L1", lambda a=None: choir([72, 76, 79], a or 1.8, "o"), "Baland xor 'ooo' C-major"),
    "sfx.cool_down": ("L5", lambda a=None: smp("whoosh_sweep", -9) * np.linspace(1, 0.4, len(smp("whoosh_sweep", -9))), "Iliq mijoz 'soviydi': whoosh_sweep −9, so'nib"),
})
FRONT.update({"sfx.cool_down"})


def _lcg(seed):
    s = seed
    def r():
        nonlocal s
        s = (s * 16807) % 2147483647
        return s / 2147483647
    return r


def _ease_inv(pp):
    """eInOut(p) = pp → p (lib.js eInOut, kubik)."""
    return (pp / 4) ** (1 / 3) if pp < 0.5 else 1 - ((2 - 2 * pp) ** (1 / 3)) / 2


_r23 = _lcg(423)
_BLIPS23 = []
for _i in range(14):
    _a = (_i + 0.3 + _r23() * 0.4) / 14 * np.pi * 2 * 1.7
    _r23()
    _BLIPS23.append(15.0 + _a / 3.4)
_BLIPS23 = [b for b in _BLIPS23 if b < 16.75]                       # episode23.html: foundAt(b) before T23.back
_PINGS23 = [10.4 + 0.6 * _ease_inv(pp) for pp in (0.18, 0.42, 0.63, 0.86)]   # lib.js RADAR_PINGS
_LEAVE23 = [(4.35, 0.4), (4.47, -0.4), (5.35, -0.4), (5.47, 0.4), (6.35, 0.4), (7.35, -0.4)]

CUES_23 = [
    (0.0, "amb.office", 0.08, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.05, "sfx.whoosh_soft", 0.2, 0.3, 0.2, 0, "Telefon kadrga kiradi", None),
    (0.15, "sfx.tick_hi", 0.25, 0, 0.2, 0.2, "'23-QISM' harflari tushadi", None),
    (0.3, "sfx.swoosh_text", 0.3, 0, 0.2, 0, "Sarlavha blur-fade-up", None),
    *[(0.8 + i * 0.18, "sfx.pop_short", 0.22, round(-0.5 + 0.2 * i, 2), 0.2, 0, f"Iliq mijoz #{i + 1} keldi", [0, 2, 4, 7, 9, 12][i]) for i in range(6)],
    *[(a, f"sfx.{CLICKS[i]}", 0.5, 0.2, 0.1, 0, f"'Savatga' #{i + 1}", None) for i, a in enumerate((2.4, 3.0, 3.5))],
    *[(a + 0.05, "sfx.blip_up", 0.18, 0.2, 0.2, 0.1, "Savat nishoni", 3 * i) for i, a in enumerate((2.4, 3.0, 3.5))],
    *[x for i, a in enumerate((4.0, 5.0, 6.0, 7.0)) for x in [
        (a, "sfx.notify_pop", 0.42, 0.15, 0.15, 0, f"Bildirishnoma #{i + 1}", [0, 1, -1, 2][i]),
        (a + 0.35, "sfx.glitch_short", 0.2, 0.3, 0.1, 0, "RGB glitch", 4),
    ]],
    *[(a, "sfx.whoosh_sweep", 0.22, pan, 0.2, 0, f"Mijoz chalg'idi — uchib ketdi #{i + 1}", 5) for i, (a, pan) in enumerate(_LEAVE23)],
    *[x for at, pan, nm in ((5.6, -0.4, "CHALG'IDI"), (6.6, 0.4, "SAVAT TASHLANDI"), (7.6, -0.4, "QAYTMADI")) for x in [
        (at, "sfx.stutter", 0.42, pan, 0.2, 0, f"Slam: {nm}", None),
        (at, "sfx.glitch_short", 0.5, pan, 0.2, 0, "Slam qatlami", None),
    ]],
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [50, 53, 57, 62]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da", None),
    (8.5, "sfx.boom_sub", 0.9, 0, 0.35, 0, "YO'QOTILDI — asosiy zarba", None),
    (8.5, "sfx.bass_drop", 0.6, 0, 0.3, 0, "Zarba qatlami: bass drop", None),
    (8.5, "sfx.glitch_seq", 0.26, 0, 0.2, 0, "Zarba qatlami: glitch", None),
    (8.7, "sfx.swoosh_text", 0.25, 0, 0.2, 0, "Taglavha blur-fade-up", None),
    (9.6, "sfx.cool_down", 0.4, 0, 0.2, 0, "OVOZ VAKUUMI: oxirgi iliq mijoz soviydi", None),
    (9.85, "sfx.dust", 0.4, 0.2, 0, 0, "...va kulga aylanadi", None),
    (9.95, "fx.heartbeat", 0.26, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: yechim akkordi (C-major)", [60, 64, 67, 72]),
    (10.2, "mus.choir_c", 1.2, 0, 0.6, 0.2, "HEAVENLY XOR 'aaah' — vahiy lahzasi", 2.8),
    (10.4, "sfx.whoosh_low", 0.4, 0, 0.3, 0, "Radar o'tishi — nur aylanadi", None),
    *[(a, "sfx.tick_hi", 0.3, round(-0.4 + 0.27 * i, 2), 0.4, 0.3, f"Radar 'ping' #{i + 1}", [0, 5, 7, 12][i]) for i, a in enumerate(_PINGS23)],
    (11.0, "sfx.boom_sub", 0.45, 0, 0.35, 0, "Yechim boshlanishi", None),
    (11.0, "sfx.shimmer", 0.3, 0, 0.4, 0.2, "Flare yaltirog'i", None),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit (deyarli sezilmas)", 10.7),
    (11.1, "sfx.whoosh_soft", 0.2, -0.3, 0.2, 0, "Telefon kiradi", None),
    *[(11.5 + i * 0.12, "sfx.pop_short", 0.28, round(-0.3 + 0.3 * i, 2), 0.2, 0, f"Segment #{i + 1}", [0, 4, 7][i]) for i in range(3)],
    (12.4, "sfx.click_1", 0.7, -0.2, 0, 0, "'Savatga qo'shdi' segmenti tanlandi", None),
    (12.42, "sfx.ratchet_roll", 0.2, 0, 0.15, 0, "1 222 → 486", None),
    (13.15, "sfx.pop_swish", 0.3, 0, 0.2, 0, "Eslatma shabloni paydo bo'ladi", None),
    (13.4, "sfx.click_2", 0.7, 0, 0, 0, "Shablon tanlandi", None),
    (13.42, "sfx.blip_up", 0.32, 0, 0.25, 0.2, "'SAVATINGIZ KUTMOQDA' letter-up", None),
    (13.75, "sfx.bass_drop", 0.35, 0, 0.3, 0, "'−10%' bounce", 5),
    (13.77, "sfx.sparkle_hit", 0.25, 0, 0.3, 0.2, "Bounce yaltirog'i", None),
    (14.4, "sfx.click_double_2", 0.7, 0.2, 0, 0, "'Mijozlarni qaytarish'", None),
    (14.42, "sfx.glitch_short", 0.18, 0, 0.2, 0, "Tugma glitch'i", 7),
    (14.65, "sfx.swipe", 0.3, 0.3, 0.15, 0, "Radar ekraniga o'tish", None),
    (15.0, "sfx.whoosh_low", 0.25, 0, 0.3, 0, "Radar aylana boshlaydi", 5),
    *[(b, "sfx.tick_hi", 0.24, round(-0.5 + i / max(1, len(_BLIPS23) - 1), 2), 0.3, 0.25, f"Topildi #{i + 1}", [0, 4, 7, 12, 16, 19, 24, 12][i % 8]) for i, b in enumerate(_BLIPS23)],
    *[(b + 0.02, "sfx.pop_short", 0.16, 0, 0.2, 0, "Avatar paydo bo'ladi", 7) for b in _BLIPS23],
    (16.75, "sfx.whoosh_sweep", 0.3, 0, 0.25, 0, "Mijozlar do'konga qaytadi", 7),
    (17.25, "sfx.thump", 0.45, 0, 0.25, 0, "...QAYTDI", None),
    (17.27, "sfx.sparkle_hit", 0.35, 0, 0.3, 0.2, "Qaytish uchqunlari", None),
    (17.27, "mus.choir_c_hi", 0.6, 0, 0.6, 0.2, "Xor 'ooo' — mijoz qaytdi", 1.4),
    (17.0, "sfx.ratchet_roll", 0.2, -0.2, 0.15, 0, "Statistika o'smoqda", None),
    (17.45, "sfx.tick", 0.2, 0.2, 0.3, 0.25, "Statistika kartasi yaltiraydi", 12),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: QAYTIB KELDI oldidan", [64, 67, 72, 76]),
    (18.45, "sfx.whoosh_soft", 0.12, 0, 0.4, 0, "Nurlar ochiladi", 7),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "QAYTIB KELDI — zarba", None),
    (18.5, "sfx.bass_drop", 0.5, 0, 0.3, 0, "Color-bounce zarbasi", None),
    (18.5, "mus.choir_c", 0.8, 0, 0.6, 0.2, "Xor 'aaah' zarba ostida", 1.8),
    (18.5, "imp.sparkle", 0.3, 0, 0.5, 0, "Uchqunlar", 331),
    (18.7, "sfx.swoosh_text", 0.3, 0, 0.2, 0, "Taglavha blur-fade-up", None),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Oyna ko'tariladi", None),
    (19.9, "ui.success", 0.24, 0, 0.5, 0.3, "Retargeting yoqildi", None),
    (20.3, "sfx.blip_up", 0.3, 0, 0.25, 0.2, "'RETARGETING YOQILDI' letter-up", 5),
    *[(20.6 + i * 0.25, "sfx.tick", 0.18, 0, 0.2, 0.2, f"Belgi #{i + 1}", [0, 4, 7][i]) for i in range(3)],
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — cho'qqisi whip'da (21.75 s)", None),
    (21.75, "sfx.whoosh_sweep", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (21.75, "sfx.swipe", 0.3, 0, 0.2, 0, "Whip qatlami", None),
    (22.0, "sfx.boom_sub", 0.5, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.2, "sfx.tick_hi", 0.25, 0, 0.2, 0.2, "'NATIJA' harflari", None),
    (22.3, "sfx.swoosh_text", 0.3, 0.2, 0.2, 0, "Sarlavha word-right", None),
    (22.35, "sfx.whoosh_soft", 0.18, 0.3, 0.2, 0, "Post-taymlayn kiradi", None),
    *[(22.35 + (k * 324 + 200) / 1700 * 4.4 - 0.15, "sfx.tick", 0.16, 0, 0.2, 0.2, f"Pleyhed: kanal #{k + 1}", [0, 4, 7, 12, 7][k]) for k in range(5)],
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA — konversiya 8.6%", None),
    (23.22, "sfx.notify_ring", 0.22, 0.2, 0.25, 0.2, "Kassa qatlami", None),
    *[(23.5 + i * 0.35, "sfx.swipe", 0.34, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, f"sfx.{CLICKS[(i + 3) % 5]}", 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [72, 76, 79][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [64, 69, 72, 76]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "sfx.shimmer", 0.25, 0, 0.4, 0.2, "Flare yaltirog'i", None),
    (25.0, "imp.sparkle", 0.35, 0, 0.5, 0, "Uchqunlar", 337),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_short", 0.32, -0.4 + 0.4 * i, 0.3, 0, f"Neon nishon #{i + 1}", [5, 10, 14][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Tonallikdagi qo'ng'iroqcha", [79, 84, 88][i]),
    ]],
    (26.85, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (C tonikada)", 60),
    (27.0, "mus.choir_c", 0.5, 0, 0.6, 0.2, "Xor logotip ostida", 3.5),
    (27.5, "sfx.blip_up", 0.22, 0, 0.25, 0.2, "'BIZNESINGIZ' letter-up", None),
    (27.7, "sfx.bass_drop", 0.3, 0, 0.3, 0, "'HIMOYACHISI!' bounce", 5),
    (28.3, "sfx.pop_short", 0.3, 0.2, 0.3, 0.2, "IZOHGA “ADUZ” CTA", 7),
    (28.32, "ui.select", 0.07, 0.2, 0.5, 0.4, "CTA qo'ng'iroqchasi", 88),
]

SCORE_23 = [
    ("Ovoz manbai", "sfx/ kutubxonasi + FX v2 + neon dizayn (neon.js)", "Birinchi neon qism: vizual — telegram_reklama777 dizayn tizimi; ovoz — o'sha sfx/ kutubxonasi, original xor ('aaah'/'ooo') va pizzicato. Yangi: sfx.cool_down (whoosh_sweep −9, so'nib) — iliq mijoz soviydi; radar 'ping'lari tick_hi bilan, topilgan har mijoz — pentatonik bo'yicha ko'tariluvchi tick."),
    ("0:00–0:09.5", "Muammo · D-minor + pizzicato", "7-qism aranjirovkasi 2 yarim ton pastda + o'ynoqi-sirli pizzicato (D). Iliq mijozlar kelishi — ko'tariluvchi pop'lar, 'Savatga' — kliklar; har bildirishnoma — notify_pop + glitch, chalg'igan mijoz uchib ketadi — whoosh_sweep. Slamlar — stutter + glitch."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: oxirgi iliq mijoz soviydi (cool_down) va kulga aylanadi (dust); yurak urishi."),
    ("0:10.15–0:11", "Vahiy lahzasi · radar", "HEAVENLY XOR C-major'da + past whoosh; radar nuri aylanadi, 4 ta 'ping' (tick_hi, 0/5/7/12)."),
    ("0:11–0:21.75", "Yechim · C-major, siyrak", "Segment tanlash (klik + ratchet: 1 222 → 486), eslatma shabloni (letter-up — blip_up, '−10%' — bass_drop + sparkle), ishga tushirish (qo'sh klik). Radar: har topilgan mijoz — tick + pop. Qaytish — thump + sparkle + xor 'ooo'."),
    ("0:22–0:27", "Natija · C-major, to'liq", "To'liq baraban, supersaw, Rhodes. Post-taymlayn pleyhedi ostida har kanal — tick. Kassa (ssenariydagi 'kassa ovozi')."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (C tonikada) ostida xor; 'BIZNESINGIZ HIMOYACHISI!' kinetik matni va izoh-CTA ovozlari, so'nish."),
]


def score_23(M):
    """7-qism partiturasi, 2 yarim ton pastda (D-minor → C-major)."""
    global KEY_SHIFT
    KEY_SHIFT = -2
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_23():
    """23-qism: Iliq mijozlarni qaytarish. Score (−2) + pizzicato + xor + cue-sheet (CUES_23)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # the last warm customer cools down: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_23(M)
    quirky_pizz(M, 1.0, 9.45, root=62, gain=0.4)
    render_cues(M, CUES_23)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 24-qism: Doimiy hamroh (24/7) — birinchi "MOTION REEL" qism (reel.js), sfx/ + xor + pizzicato ----------
SOUNDS.update({
    "mus.choir_b": ("L1", lambda a=None: choir([59, 63, 66, 71], a or 2.5), "Xor 'aaah' B-major (heavenly uslub, original sintez)"),
    "mus.choir_b_hi": ("L1", lambda a=None: choir([71, 75, 78], a or 1.8, "o"), "Baland xor 'ooo' B-major"),
})
_KEYS24 = sorted({20.2 + 1.2 * _ease_inv(k) for k in (0, .08, .16, .3, .38, .46, .54, .66, .74, .82)})   # episode24.html: violet card playhead
_MSG24 = [1.0, 2.2, 3.6, 4.8, 6.0, 7.0]

CUES_24 = [
    (0.0, "amb.office", 0.07, 0, 0, 0, "Tungi xona — sahna 'havosi'", 9.6),
    (0.1, "sfx.type_burst", 0.3, 0, 0.15, 0, "'24-QISM' dekodlanadi (scramble)", None),
    (0.12, "sfx.swoosh_text", 0.25, 0, 0.2, 0, "To'q sariq chiziq + shkala chiziladi", None),
    (0.45, "sfx.bass_drop", 0.45, 0, 0.3, 0, "'DOIMIY HAMROH' — og'ir grotesk slam", 3),
    (0.05, "sfx.whoosh_soft", 0.18, 0.3, 0.2, 0, "Chat kartasi kiradi", None),
    *[x for i, a in enumerate(_MSG24) for x in [
        (a - 0.45, "sfx.type_burst", 0.18, 0.35, 0.1, 0, f"Mijoz yozmoqda #{i + 1}", None),
        (a, "sfx.pop_swish", 0.32, 0.35, 0.15, 0, f"Xabar #{i + 1} yuborildi — javobsiz", [0, -1, -2, -3, -4, -5][i]),
    ]],
    (1.2, "sfx.tick_roll", 0.12, -0.3, 0.1, 0, "Kutish taymeri yuguradi", None),
    (4.4, "sfx.tick_roll", 0.14, -0.3, 0.1, 0, "Taymer tezlashadi", 3),
    (7.8, "sfx.ratchet_roll", 0.2, -0.3, 0.1, 0, "Soatlar o'tib ketadi", None),
    *[x for at, pan, nm in ((5.6, -0.4, "JAVOB YO'Q"), (6.6, 0.4, "OFFLINE"), (7.6, -0.2, "SOVUQ MUNOSABAT")) for x in [
        (at, "sfx.stutter", 0.42, pan, 0.2, 0, f"Slab-karta: {nm}", None),
        (at, "sfx.glitch_short", 0.5, pan, 0.2, 0, "Slam qatlami", None),
    ]],
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [49, 52, 56, 61]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da", None),
    (8.45, "sfx.whoosh_low", 0.35, 0, 0.2, 0, "To'q sariq karta butun kadrga ochiladi", None),
    (8.5, "sfx.boom_sub", 0.9, 0, 0.35, 0, "SOVUQ. — asosiy zarba", None),
    (8.5, "sfx.bass_drop", 0.6, 0, 0.3, 0, "Zarba qatlami: bass drop", None),
    (8.5, "sfx.glitch_seq", 0.26, 0, 0.2, 0, "Zarba qatlami: glitch", None),
    (8.62, "sfx.pop_short", 0.3, 0.4, 0.2, 0, "Qora disk (nuqtali panjara)", -5),
    (9.6, "sfx.letters_fall", 0.4, 0, 0, 0, "OVOZ VAKUUMI: 'Allo?' shovqinga aylanadi", None),
    (9.85, "sfx.dust", 0.35, 0.2, 0, 0, "...va sochiladi", None),
    (9.95, "fx.heartbeat", 0.26, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: yechim akkordi (B-major)", [59, 63, 66, 71]),
    (10.2, "mus.choir_b", 1.2, 0, 0.6, 0.2, "HEAVENLY XOR 'aaah' — 'Yordam.'", 2.8),
    *[(10.35 + i * 0.05, "sfx.pop_short", 0.16, round(-0.5 + 0.2 * i, 2), 0.2, 0, f"Panjara to'lqini kiradi #{i + 1}", [0, 2, 4, 7, 9, 12][i]) for i in range(6)],
    (10.55, "sfx.shimmer", 0.3, 0, 0.4, 0.2, "'Yordam.' serif so'zi", None),
    *[(10.7 + i * 0.05, "sfx.pop_short", 0.14, round(0.5 - 0.2 * i, 2), 0.2, 0, f"Panjara to'lqini chiqadi #{i + 1}", [12, 9, 7, 4, 2, 0][i]) for i in range(6)],
    (11.0, "sfx.boom_sub", 0.45, 0, 0.35, 0, "Yechim boshlanishi", None),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit", 10.7),
    *[(11.25 + i * 0.12, "sfx.swoosh_text", 0.16, round(-0.4 + 0.2 * i, 2), 0.15, 0, f"UI-karta #{i + 1} uchib kiradi", None) for i in range(5)],
    (12.3, "sfx.click_1", 0.7, 0.3, 0, 0, "'Jonli menejer' toggle — YONDI", None),
    (12.33, "sfx.blip_up", 0.32, 0.3, 0.25, 0.2, "Toggle laym rangga o'tadi", None),
    (12.7, "sfx.pop_swish", 0.32, 0.3, 0.15, 0, "Mijoz xabari", None),
    (13.15, "sfx.type_burst", 0.28, -0.3, 0.15, 0, "Menejer yozmoqda...", None),
    (13.65, "sfx.notify_ring", 0.34, -0.3, 0.25, 0.2, "Menejer javob berdi (40 soniyada)", None),
    (14.4, "sfx.notify_pop", 0.34, -0.3, 0.2, 0.1, "To'lov o'tdi", None),
    (15.0, "sfx.pop_short", 0.3, 0.3, 0.2, 0, "'Rahmat, tez ekan!'", 7),
    (15.02, "mus.choir_b_hi", 0.5, 0, 0.6, 0.2, "Xor 'ooo' — mijoz xotirjam", 1.4),
    (15.4, "sfx.ratchet_roll", 0.2, -0.3, 0.15, 0, "Javob vaqti: 3 soat → 47 s", None),
    (16.0, "sfx.whoosh_sweep", 0.18, 0.3, 0.2, 0, "Donut 98% gacha to'ladi", 7),
    (16.6, "sfx.tick_roll", 0.18, 0, 0.2, 0.1, "24 soatlik ustunlar o'sadi", 5),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: JAVOB BOR oldidan", [63, 66, 71, 75]),
    (18.45, "sfx.whoosh_low", 0.3, 0, 0.3, 0, "Laym karta butun kadrga ochiladi", None),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "JAVOB — zarba", None),
    (18.5, "sfx.bass_drop", 0.5, 0, 0.3, 0, "Og'ir grotesk slam", None),
    (18.6, "sfx.thump", 0.45, 0, 0.25, 0, "BOR. — ikkinchi zarba", None),
    (18.5, "mus.choir_b", 0.8, 0, 0.6, 0.2, "Xor 'aaah' zarba ostida", 1.8),
    (18.5, "imp.sparkle", 0.3, 0, 0.5, 0, "Uchqunlar", 331),
    (18.8, "sfx.swoosh_text", 0.3, 0, 0.2, 0, "'47 soniyada — kechasi ham'", None),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Binafsha karta ko'tariladi", None),
    (20.0, "sfx.shimmer", 0.22, 0, 0.3, 0.2, "'Siz yolg'iz emassiz.'", None),
    *[(k, "sfx.tick_hi", 0.2, round(-0.4 + 0.8 * i / max(1, len(_KEYS24) - 1), 2), 0.25, 0.2, f"Keyframe #{i + 1} yondi", [0, 2, 4, 7, 9, 12, 14, 16, 19, 21][i % 10]) for i, k in enumerate(_KEYS24)],
    (21.35, "ui.success", 0.24, 0, 0.5, 0.3, "HAL QILINDI", None),
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — cho'qqisi whip'da (21.75 s)", None),
    (21.75, "sfx.whoosh_sweep", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (21.75, "sfx.swipe", 0.3, 0, 0.2, 0, "Whip qatlami", None),
    (22.0, "sfx.boom_sub", 0.5, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.1, "sfx.bass_drop", 0.45, 0, 0.3, 0, "'24/7' chiziqli fonda", 5),
    (22.1, "sfx.whoosh_low", 0.2, 0, 0.2, 0, "Chiziqlar oqadi", 3),
    (22.95, "sfx.type_burst", 0.25, 0, 0.15, 0, "'NATIJA' dekodlanadi", None),
    (23.0, "sfx.bass_drop", 0.3, 0, 0.3, 0, "'HAR DOIM YONINGIZDA'", 7),
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA", None),
    (23.22, "sfx.notify_ring", 0.22, 0.2, 0.25, 0.2, "Kassa qatlami", None),
    *[(23.5 + i * 0.35, "sfx.swipe", 0.34, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, f"sfx.{CLICKS[(i + 1) % 5]}", 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [71, 75, 78][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [63, 68, 71, 75]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "imp.sparkle", 0.35, 0, 0.5, 0, "Uchqunlar", 337),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_short", 0.32, -0.4 + 0.4 * i, 0.3, 0, f"Rangli nishon #{i + 1}", [4, 9, 13][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Tonallikdagi qo'ng'iroqcha", [78, 83, 87][i]),
    ]],
    (25.6, "sfx.shimmer", 0.25, 0, 0.4, 0.2, "Zarrachalar sferaga yig'iladi", None),
    (26.85, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (B tonikada)", 59),
    (27.0, "mus.choir_b", 0.5, 0, 0.6, 0.2, "Xor logotip ostida", 3.5),
    *[(27.45 + i * 0.1, "sfx.thump", 0.28, round(-0.45 + 0.3 * i, 2), 0.2, 0, f"'{'ADUZ'[i]}' harfi joyiga tushadi", None) for i in range(4)],
    (27.7, "sfx.whoosh_soft", 0.16, 0, 0.3, 0, "Orbita chiziladi", 7),
    (27.8, "sfx.swoosh_text", 0.22, 0, 0.2, 0, "To'q sariq tagchiziq", None),
    (28.0, "sfx.type_burst", 0.22, 0, 0.15, 0, "'BIZNESINGIZ HIMOYACHISI' dekodlanadi", None),
    (28.6, "sfx.pop_short", 0.3, 0.2, 0.3, 0.2, "CTA tugmasi", 7),
    (28.62, "ui.select", 0.07, 0.2, 0.5, 0.4, "CTA qo'ng'iroqchasi", 87),
]

SCORE_24 = [
    ("Ovoz manbai", "sfx/ kutubxonasi + FX v2 + 'motion reel' dizayn (reel.js)", "Birinchi reel qism: vizual — foydalanuvchi yuborgan showreel uslubi; ovoz — sfx/ kutubxonasi, original xor ('aaah'/'ooo') va pizzicato. Har grafik qurilmaning o'z ovozi: scramble — type_burst, og'ir grotesk slam — bass_drop, panjara to'lqini — pop_short kaskadi, keyframe'lar — tick_hi, harflar tushishi — thump."),
    ("0:00–0:09.5", "Muammo · C#-minor + pizzicato", "7-qism aranjirovkasi 3 yarim ton pastda + pizzicato. Har yuborilgan xabar — type_burst + pop_swish (har safar yarim ton pastroq: umid so'nadi), kutish taymeri — tick_roll / ratchet. Slab-kartalar — stutter + glitch; 8.5 s to'q sariq kadr — whoosh_low + boom."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: 'Allo?' shovqinga aylanadi (letters_fall) va sochiladi (dust); yurak urishi."),
    ("0:10.15–0:11", "Vahiy · panjara to'lqini", "HEAVENLY XOR B-major'da; plitkalar kirishi/chiqishi — pentatonik pop_short kaskadi (yuqoriga / pastga), 'Yordam.' — shimmer."),
    ("0:11–0:21.75", "Yechim · B-major, siyrak", "UI-kartalar uchib kiradi (swoosh_text), toggle — klik + blip_up, menejer yozmoqda — type_burst, javob — notify_ring, rahmat — xor 'ooo'. 18.5 s: JAVOB / BOR. — ikki zarba. Binafsha kartada pleyhed har keyframe'ni yoqadi — ko'tariluvchi tick_hi."),
    ("0:22–0:27", "Natija · B-major, to'liq", "'24/7' chiziqli fonda — bass_drop; to'liq baraban, supersaw, Rhodes; kassa."),
    ("0:27–0:32", "Yakun · brend", "ADUZ sonic logo (B tonikada) + xor; harflar tushishi — to'rtta thump, orbita, tagchiziq, scramble; so'nish."),
]


def score_24(M):
    """7-qism partiturasi, 3 yarim ton pastda (C#-minor → B-major)."""
    global KEY_SHIFT
    KEY_SHIFT = -3
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_24():
    """24-qism: Doimiy hamroh (24/7). Score (−3) + pizzicato + xor + cue-sheet (CUES_24)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # "Allo?" decodes into noise: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_24(M)
    quirky_pizz(M, 1.0, 9.45, root=61, gain=0.4)
    render_cues(M, CUES_24)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 25-qism: Mutlaq erkinlik (mobil boshqaruv) — UCHALA dizayn va BUTUN ovoz kutubxonasi bitta qismda ----------
SOUNDS.update({
    "mus.choir_g_hi": ("L1", lambda a=None: choir([74, 79, 83], a or 1.8, "o"), "Baland xor 'ooo' G-major"),
})
_NOTIF25 = [1.4, 2.3, 3.1, 3.9, 4.6, 5.3, 6.0, 6.7, 7.3, 7.9]

CUES_25 = [
    # --- 1. Muammo (klassik dunyo): ofis, kompyuter, kabel ---
    (0.0, "amb.office", 0.1, 0, 0, 0, "Ofis — ventilyatsiya, 50 Hz g'uvullash", 9.6),
    (0.05, "tr.whoosh", 0.2, 0.3, 0.2, 0, "Monitor va xarita kiradi", None),
    (0.15, "sfx.tick_hi", 0.22, 0, 0.2, 0.2, "'25-QISM' harflari", None),
    (0.3, "sfx.swoosh_text", 0.28, 0, 0.2, 0, "'Mutlaq erkinlik' blur-up", None),
    *[(a, "sfx.notify_pop", 0.3, round(-0.3 + 0.06 * i, 2), 0.15, 0, f"Monitorda yangi buyurtma #{i + 1}", [0, 2, 3, 5, 7, 8, 10, 12, 13, 15][i]) for i, a in enumerate(_NOTIF25)],
    *[(1.0 + k * 0.5, "fx.tick", 0.07, -0.4, 0, 0, "Devor soati", None) for k in range(8)],
    (1.0, "sfx.whoosh_soft", 0.12, 0.4, 0.2, 0, "Egasi ofisdan chiqib ketadi", 3),
    (4.0, "fx.twang", 0.3, 0.3, 0.2, 0, "Kabel taranglashdi", None),
    (4.05, "fx.chain", 0.25, 0.3, 0.2, 0, "Kabel — zanjirday", 0.4),
    *[(a + 0.08, "fx.twang", 0.22, 0.4, 0.15, 0, "Kabel egasini orqaga tortadi", None) for a in (5.6, 6.6, 7.6)],
    *[x for at, pan, nm in ((5.6, -0.4, "OFISGA BOG'LIQ"), (6.6, 0.4, "BUYURTMA KUTMOQDA"), (7.6, -0.4, "KECH QOLDINGIZ")) for x in [
        (at, "sfx.stutter", 0.4, pan, 0.2, 0, f"Slam: {nm}", None),
        (at, "imp.glitch", 0.35, pan, 0.2, 0, "Klassik slam qatlami", None),
    ]],
    (7.0, "fx.alarm", 0.16, 0, 0.2, 0, "Javobsiz buyurtmalar — ogohlantirish", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [57, 60, 64, 69]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da", None),
    (8.5, "sfx.boom_sub", 0.85, 0, 0.35, 0, "QARAMLIK — asosiy zarba", None),
    (8.5, "imp.boom", 0.4, 0, 0.3, 0, "Klassik boom qatlami", None),
    (8.5, "fx.chain", 0.5, 0, 0.3, 0, "Zanjirlar monitorni o'raydi", 0.6),
    (8.7, "sfx.swoosh_text", 0.25, 0, 0.2, 0, "Taglavha blur-up", None),
    # --- vakuum ---
    (9.6, "fx.padlock", 0.32, 0, 0, 0, "OVOZ VAKUUMI: qulf yopildi", None),
    (9.8, "tr.crt_off", 0.26, 0, 0.1, 0, "Monitor eski televizorday o'chadi", None),
    (9.95, "fx.heartbeat", 0.26, 0, 0, 0, "Yurak urishi", None),
    # --- pocketZoom: ofis cho'ntakka sig'adi ---
    (10.15, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: yechim akkordi (G-major)", [55, 59, 62, 67]),
    (10.2, "mus.choir_g", 1.2, 0, 0.6, 0.2, "HEAVENLY XOR 'aaah' — ofis cho'ntakka sig'adi", 2.8),
    (10.3, "tr.implode", 0.35, 0, 0.2, 0, "Butun ofis telefon ekraniga so'riladi", None),
    (10.85, "tr.boot", 0.3, 0, 0.3, 0.2, "Telefon yonadi", 67),
    (10.95, "sfx.shimmer", 0.3, 0, 0.4, 0.2, "Flare", None),
    (11.0, "sfx.boom_sub", 0.45, 0, 0.35, 0, "Yechim boshlanishi", None),
    # --- dunyo 1: bozor (klassik) ---
    (11.0, "amb.air", 0.03, 0, 0, 0, "Ochiq havo", 10.7),
    (11.05, "fx.birds", 0.12, -0.5, 0.3, 0.2, "Bozor ertalabi: qushlar", (3, 5)),
    (11.5, "ui.popup", 0.25, 0, 0.2, 0, "Buyurtma kartasi", 72),
    (11.9, "fx.vibrate", 0.18, 0, 0, 0, "Telefon titraydi", 0.5),
    (11.92, "sfx.notify_ring", 0.32, 0.2, 0.25, 0.2, "Yangi buyurtma!", None),
    (12.6, "sfx.click_1", 0.7, 0.2, 0, 0, "'Tasdiqlash'", None),
    (12.62, "fx.stamp", 0.3, 0, 0.2, 0, "Tasdiqlandi — muhr", None),
    (12.75, "ui.success", 0.2, 0, 0.5, 0.3, "Yashil tasdiq", None),
    (12.8, "sfx.sparkle_hit", 0.25, 0, 0.3, 0.2, "Uchqunlar", None),
    # --- dunyo 2: tungi yo'l (neon) ---
    (14.3, "sfx.whoosh_sweep", 0.35, 0, 0.25, 0, "Neon halqa — dunyo almashadi", 3),
    (14.45, "sfx.glitch_short", 0.25, 0, 0.2, 0, "RGB glitch", None),
    *[(14.6 + k * 0.75, "sfx.whoosh_low", 0.12, (-0.6, 0.6)[k % 2], 0.3, 0, f"O'tib ketayotgan mashina #{k + 1}", 2 * (k % 3)) for k in range(4)],
    (14.6, "fx.flicker", 0.12, 0.4, 0.2, 0, "Neon vivesqa g'uvullashi", 0.05),
    (15.3, "sfx.notify_pop", 0.3, -0.2, 0.2, 0.1, "Andijon Savdo: ko'rish 2x", 2),
    (15.9, "sfx.click_2", 0.7, 0.2, 0, 0, "'Byudjet +50 000'", None),
    (15.95, "fx.transfer", 0.28, 0.2, 0.2, 0, "Byudjet o'tkazildi", None),
    (16.0, "sfx.ratchet_roll", 0.18, 0, 0.15, 0, "Byudjet chizig'i o'sadi", None),
    (16.6, "fx.switch", 0.35, 0.3, 0.1, 0, "Avto-optimallash yoqildi", None),
    (16.62, "sfx.blip_up", 0.28, 0.3, 0.25, 0.2, "Toggle firuza", None),
    # --- dunyo 3: choyxona (reel) ---
    (17.6, "sfx.pop_short", 0.2, -0.4, 0.2, 0, "Plitkalar to'lqini #1", 0),
    (17.68, "sfx.pop_short", 0.2, 0.0, 0.2, 0, "Plitkalar to'lqini #2", 4),
    (17.76, "sfx.pop_short", 0.2, 0.4, 0.2, 0, "Plitkalar to'lqini #3", 7),
    (17.75, "sfx.type_burst", 0.28, 0, 0.15, 0, "'CHOYXONA 13:05' dekodlanadi", None),
    (17.9, "sfx.tick_roll", 0.16, 0, 0.2, 0.1, "+18 buyurtma sanaladi", 5),
    (18.15, "sfx.click_3", 0.7, 0.2, 0, 0, "'Avto-javob' toggle", None),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: ISTALGAN JOYDAN oldidan", [59, 62, 67, 71]),
    (18.45, "sfx.whoosh_low", 0.3, 0, 0.3, 0, "Laym karta butun kadrga", None),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "ISTALGAN — zarba", None),
    (18.5, "sfx.bass_drop", 0.5, 0, 0.3, 0, "Og'ir grotesk", None),
    (18.5, "imp.crash", 0.25, 0, 0.4, 0, "Klassik crash", None),
    (18.6, "sfx.thump", 0.45, 0, 0.25, 0, "JOYDAN. — ikkinchi zarba", None),
    (18.5, "mus.choir_g", 0.8, 0, 0.6, 0.2, "Xor 'aaah' zarba ostida", 1.8),
    (18.5, "imp.sparkle", 0.3, 0, 0.5, 0, "Uchqunlar", 331),
    (18.8, "sfx.swoosh_text", 0.3, 0, 0.2, 0, "'bir telefon — butun biznes'", None),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Binafsha karta", None),
    (20.0, "sfx.shimmer", 0.22, 0, 0.3, 0.2, "'Ofis — endi cho'ntagingizda.'", None),
    *[(20.2 + 1.2 * _ease_inv(k), "sfx.tick_hi", 0.2, round(-0.4 + 0.1 * i, 2), 0.25, 0.2, f"Kun keyframe #{i + 1}", [0, 4, 7, 9, 12, 16, 19, 21][i]) for i, k in enumerate((.04, .12, .36, .44, .52, .7, .78, .86))],
    (21.35, "ui.success", 0.24, 0, 0.5, 0.3, "HAMMASI NAZORATDA", None),
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — whip'ga", None),
    (21.75, "tr.whip", 0.4, 0, 0.25, 0, "Whip-pan (klassik)", None),
    (21.75, "sfx.whoosh_sweep", 0.3, 0, 0.25, 0, "Whip qatlami", None),
    # --- 3. Natija: uchala dunyo ---
    (22.0, "sfx.boom_sub", 0.5, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.2, "sfx.tick_hi", 0.25, 0, 0.2, 0.2, "'NATIJA'", None),
    (22.3, "sfx.swoosh_text", 0.3, 0.2, 0.2, 0, "Sarlavha word-right", None),
    (22.15, "fx.snap", 0.3, -0.5, 0.2, 0, "Panel: BOZOR (klassik)", None),
    (22.3, "fx.lcd", 0.25, 0, 0.2, 0, "Panel: YO'L (neon)", None),
    (22.45, "sfx.bass_drop", 0.3, 0.5, 0.25, 0, "Panel: CHOYXONA (reel)", 7),
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA", None),
    (23.22, "fx.coin", 0.12, 0.3, 0.2, 0, "Tanga", None),
    *[(23.5 + i * 0.35, "fx.strike", 0.3, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, f"sfx.{CLICKS[(i + 2) % 5]}", 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [79, 83, 86][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [59, 64, 67, 71]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "imp.sparkle", 0.35, 0, 0.5, 0, "Oltin uchqunlar", 337),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_short", 0.32, -0.4 + 0.4 * i, 0.3, 0, f"Oltin nishon #{i + 1}", [5, 9, 12][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Qo'ng'iroqcha", [83, 86, 91][i]),
    ]],
    (26.6, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakunga", None),
    # --- yakun: uch logotip "stutter" + reel identity ---
    *[(27.0 + i * 0.15, s, 0.32, (-0.4, 0.4, 0)[i], 0.2, 0, f"Logotip #{i + 1} ({nm})", None) for i, (s, nm) in enumerate((("sfx.hit_chime", "klassik"), ("sfx.hit_tone", "neon"), ("sfx.hit_low", "reel")))],
    (27.45, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (G tonikada)", 67),
    (27.45, "mus.choir_g", 0.5, 0, 0.6, 0.2, "Xor logotip ostida", 3.5),
    *[(27.9 + i * 0.1, "sfx.thump", 0.26, round(-0.45 + 0.3 * i, 2), 0.2, 0, f"'{'ADUZ'[i]}' harfi tushadi", None) for i in range(4)],
    (28.15, "sfx.whoosh_soft", 0.16, 0, 0.3, 0, "Orbita", 7),
    (28.25, "sfx.swoosh_text", 0.22, 0, 0.2, 0, "Tagchiziq", None),
    (28.45, "sfx.type_burst", 0.22, 0, 0.15, 0, "'BIZNESINGIZ HIMOYACHISI'", None),
    (29.05, "sfx.pop_short", 0.3, 0.2, 0.3, 0.2, "CTA", 7),
    (29.07, "ui.select", 0.07, 0.2, 0.5, 0.4, "CTA qo'ng'iroqchasi", 91),
]

SCORE_25 = [
    ("Ovoz manbai", "BUTUN kutubxona: sfx/ + 1–21-qism sintez ovozlari + xor + pizzicato", "Foydalanuvchi: 'barcha dizayn va ovozlardan foydalan'. Har dunyo o'z ovoz palitrasida: ofis — amb.office, soat, notify_pop, kabel (fx.twang + fx.chain), klassik imp.glitch/imp.boom; vakuum — fx.padlock + tr.crt_off; o'tish — tr.implode + tr.boot; bozor — qushlar, vibratsiya, fx.stamp; tungi yo'l — o'tayotgan mashinalar (whoosh_low), neon g'uvullashi, fx.transfer, fx.switch; choyxona — reel ovozlari (pop kaskadi, type_burst, tick_hi keyframe'lar)."),
    ("0:00–0:09.5", "Muammo · A-minor + pizzicato", "7-qism aranjirovkasi 5 yarim ton yuqorida + pizzicato (A). Har yangi buyurtma — notify_pop (pentatonik ko'tariladi: bosim o'sadi), devor soati, 4.0 s dan kabel taranglashadi (twang + chain); slamlar — stutter + klassik imp.glitch; 7.0 s ogohlantirish."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: qulf yopiladi (fx.padlock), monitor eski televizorday o'chadi (tr.crt_off), yurak urishi."),
    ("0:10.15–0:11", "Vahiy · pocketZoom", "HEAVENLY XOR G-major'da; ofis telefonga so'riladi (tr.implode), telefon yonadi (tr.boot, G)."),
    ("0:11–0:21.75", "Yechim · G-major, uch dunyo", "Bozor (qushlar, buyurtma — vibratsiya + ring, tasdiq — klik + muhr + success) → neon halqa (whoosh_sweep + glitch) → tungi yo'l (mashinalar, byudjet — transfer, toggle — switch) → plitkalar to'lqini → choyxona (scramble, +18, avto-javob). 18.5 s: ISTALGAN / JOYDAN. — ikki zarba + crash + xor. Kun keyframe'lari — tick_hi."),
    ("0:22–0:27", "Natija · G-major, to'liq", "Uch panel — har biri o'z dunyosi ovozida (snap / lcd / bass_drop), kassa + tanga, 'Oldin' qatorlari — fx.strike."),
    ("0:27–0:32", "Yakun · brend", "Uch logotip stutter (hit_chime / hit_tone / hit_low), sonic logo (G) + xor, harflar tushishi, CTA."),
]


def score_25(M):
    """7-qism partiturasi, 5 yarim ton yuqorida (A-minor → G-major)."""
    global KEY_SHIFT
    KEY_SHIFT = 5
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_25():
    """25-qism: Mutlaq erkinlik. Score (+5) + pizzicato + xor + cue-sheet (CUES_25)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # padlock + CRT off: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_25(M)
    quirky_pizz(M, 1.0, 9.45, root=69, gain=0.36)
    render_cues(M, CUES_25)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 26-qism: Ulashing va daromad ko'ring — "motion reel" uslubi (24-qism dizayni) ----------
SOUNDS.update({
    "mus.choir_e": ("L1", lambda a=None: choir([64, 68, 71, 76], a or 2.5), "Xor 'aaah' E-major (heavenly uslub, original sintez)"),
    "mus.choir_e_hi": ("L1", lambda a=None: choir([76, 80, 83], a or 1.8, "o"), "Baland xor 'ooo' E-major"),
})
SOUNDS["fx.chain_snap_v"] = ("L5", SOUNDS["fx.chain_snap"][1], "Zanjir uziladi (vakuum ichida eshitiladigan nusxa)")
FRONT.update({"fx.chain_snap_v"})
_SEND26 = [1.0 + i * 0.55 for i in range(8)]
_JOIN26 = [13.6, 14.2, 14.8, 15.4]
_KEYS26 = sorted({20.2 + 1.2 * _ease_inv(k) for k in (0, .06, .24, .3, .36, .5, .56, .62, .74, .8, .86, .92)})

CUES_26 = [
    (0.0, "amb.office", 0.07, 0, 0, 0, "Xona — sahna 'havosi'", 9.6),
    (0.1, "sfx.type_burst", 0.3, 0, 0.15, 0, "'26-QISM' dekodlanadi", None),
    (0.12, "sfx.swoosh_text", 0.25, 0, 0.2, 0, "To'q sariq chiziq + shkala", None),
    (0.45, "sfx.bass_drop", 0.45, 0, 0.3, 0, "'ULASHING' — og'ir grotesk slam", 3),
    *[(0.5 + i * 0.06, "sfx.pop_short", 0.14, round(-0.6 + 0.17 * i, 2), 0.2, 0, f"Do'st tuguni #{i + 1}", [0, 2, 4, 7, 9, 12, 14, 16][i]) for i in range(8)],
    *[x for i, a in enumerate(_SEND26) for x in [
        (a, "fx.send", 0.16, round(-0.6 + 0.17 * i, 2), 0.15, 0, f"Tavsiya yuborildi #{i + 1}", None),
        (a + 0.55, "sfx.blip_up", 0.16, round(-0.6 + 0.17 * i, 2), 0.2, 0.1, f"Do'st ro'yxatdan o'tdi #{i + 1}", i),
        (a + 0.6, "sfx.click_soft", 0.25, 0.5, 0.1, 0, "Hamyon: hamon 0 so'm", None),
    ]],
    *[x for at, pan, nm in ((5.6, -0.4, "BEPUL REKLAMA"), (6.6, 0.4, "RAHMAT HAM YO'Q"), (7.6, -0.4, "0 SO'M")) for x in [
        (at, "sfx.stutter", 0.42, pan, 0.2, 0, f"Slab-karta: {nm}", None),
        (at, "sfx.glitch_short", 0.5, pan, 0.2, 0, "Slam qatlami", None),
    ]],
    (7.6, "fx.nope", 0.25, -0.4, 0.15, 0, "0 so'm — rad", None),
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [54, 57, 61, 66]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da", None),
    (8.45, "sfx.whoosh_low", 0.35, 0, 0.2, 0, "To'q sariq karta butun kadrga", None),
    (8.5, "sfx.boom_sub", 0.9, 0, 0.35, 0, "BEHUDA. — asosiy zarba", None),
    (8.5, "sfx.bass_drop", 0.6, 0, 0.3, 0, "Zarba qatlami: bass drop", None),
    (8.5, "sfx.glitch_seq", 0.26, 0, 0.2, 0, "Zarba qatlami: glitch", None),
    (8.62, "fx.coin", 0.2, 0.4, 0.2, 0, "Chizib tashlangan tanga", None),
    (9.6, "fx.chain_snap_v", 0.3, 0, 0, 0, "OVOZ VAKUUMI: aloqalar uziladi", None),
    (9.8, "sfx.letters_fall", 0.35, 0, 0, 0, "'0 SO'M' shovqinga aylanadi", None),
    (10.0, "sfx.dust", 0.3, 0.2, 0, 0, "...va sochiladi", None),
    (9.95, "fx.heartbeat", 0.26, 0, 0, 0, "Yurak urishi", None),
    (10.15, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: yechim akkordi (E-major)", [64, 68, 71, 76]),
    (10.2, "mus.choir_e", 1.2, 0, 0.6, 0.2, "HEAVENLY XOR 'aaah' — 'Ulashing.'", 2.8),
    (10.3, "sfx.whoosh_sweep", 0.35, 0, 0.25, 0, "Chiziqlar kadrni yopadi", 3),
    (10.62, "sfx.shimmer", 0.3, 0, 0.4, 0.2, "'Ulashing.' serif so'zi", None),
    (10.7, "sfx.whoosh_sweep", 0.25, 0, 0.25, 0, "Chiziqlar ochiladi", 7),
    (11.0, "sfx.boom_sub", 0.45, 0, 0.35, 0, "Yechim boshlanishi", None),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit", 10.7),
    *[(11.25 + i * 0.12, "sfx.swoosh_text", 0.16, round(-0.4 + 0.2 * i, 2), 0.15, 0, f"UI-karta #{i + 1}", None) for i in range(5)],
    (12.3, "sfx.click_1", 0.7, 0.3, 0, 0, "'NUSXA' — havola nusxalandi", None),
    (12.32, "sfx.tick_hi", 0.25, 0.3, 0.25, 0.2, "Nusxalandi", 12),
    (12.95, "sfx.click_double_2", 0.6, 0.3, 0, 0, "'ULASHISH'", None),
    *[(13.0 + i * 0.06, "fx.send", 0.12, round(-0.5 + 0.2 * i, 2), 0.15, 0, f"Havola do'stga #{i + 1}", None) for i in range(5)],
    *[x for i, a in enumerate(_JOIN26) for x in [
        (a, "sfx.pop_swish", 0.28, 0.3, 0.15, 0, f"Ro'yxatdan o'tdi #{i + 1}", [0, 2, 4, 7][i]),
        (a + 0.12, "fx.coin", 0.22, 0.4, 0.2, 0, "+15 000 so'm", None),
    ]],
    (15.6, "sfx.ratchet_roll", 0.2, -0.3, 0.15, 0, "Daromad sanaladi → 1 240 000", None),
    (15.62, "fx.transfer", 0.22, -0.3, 0.2, 0, "Hisobga tushmoqda", None),
    (16.1, "sfx.whoosh_sweep", 0.15, 0.3, 0.2, 0, "Donut 10%", 9),
    (16.6, "sfx.tick_roll", 0.18, 0, 0.2, 0.1, "Oylik ustunlar o'sadi", 5),
    (17.0, "mus.choir_e_hi", 0.45, 0, 0.6, 0.2, "Xor 'ooo' — 'havola ishlaydi'", 1.4),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: PASSIV DAROMAD oldidan", [68, 71, 76, 80]),
    (18.45, "sfx.whoosh_low", 0.3, 0, 0.3, 0, "Laym karta butun kadrga", None),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "PASSIV — zarba", None),
    (18.5, "sfx.bass_drop", 0.5, 0, 0.3, 0, "Og'ir grotesk", None),
    (18.6, "sfx.thump", 0.45, 0, 0.25, 0, "DAROMAD. — ikkinchi zarba", None),
    (18.5, "mus.choir_e", 0.8, 0, 0.6, 0.2, "Xor 'aaah' zarba ostida", 1.8),
    (18.5, "imp.sparkle", 0.3, 0, 0.5, 0, "Uchqunlar", 331),
    (18.8, "sfx.swoosh_text", 0.3, 0, 0.2, 0, "'bir havola — doimiy foyda'", None),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Binafsha karta", None),
    (20.0, "sfx.shimmer", 0.22, 0, 0.3, 0.2, "'Ulashing — daromad ko'ring.'", None),
    *[(k, "sfx.tick_hi", 0.18, round(-0.45 + 0.9 * i / max(1, len(_KEYS26) - 1), 2), 0.25, 0.2, f"Keyframe #{i + 1}", [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26][i % 12]) for i, k in enumerate(_KEYS26)],
    (21.35, "fx.kassa", 0.2, 0, 0.3, 0.2, "HISOBGA TUSHDI", None),
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — whip'ga", None),
    (21.75, "sfx.whoosh_sweep", 0.42, 0, 0.25, 0, "Whip-pan o'tishi", None),
    (21.75, "sfx.swipe", 0.3, 0, 0.2, 0, "Whip qatlami", None),
    (22.0, "sfx.boom_sub", 0.5, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.1, "sfx.bass_drop", 0.45, 0, 0.3, 0, "'10%' halftone fonda", 5),
    (22.1, "sfx.shimmer", 0.18, 0, 0.3, 0.2, "Halftone to'lqinlari", None),
    (22.95, "sfx.type_burst", 0.25, 0, 0.15, 0, "'NATIJA' dekodlanadi", None),
    (23.0, "sfx.bass_drop", 0.3, 0, 0.3, 0, "'TAVSIYA = DAROMAD'", 7),
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA", None),
    (23.22, "sfx.notify_ring", 0.22, 0.2, 0.25, 0.2, "Kassa qatlami", None),
    *[(23.5 + i * 0.35, "sfx.swipe", 0.34, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, f"sfx.{CLICKS[(i + 4) % 5]}", 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [76, 80, 83][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [68, 73, 76, 80]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "imp.sparkle", 0.35, 0, 0.5, 0, "Uchqunlar", 337),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_short", 0.32, -0.4 + 0.4 * i, 0.3, 0, f"Rangli nishon #{i + 1}", [4, 9, 13][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Qo'ng'iroqcha", [80, 85, 88][i]),
    ]],
    (25.6, "sfx.shimmer", 0.25, 0, 0.4, 0.2, "Zarrachalar sferaga yig'iladi", None),
    (26.85, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakuniy kadrga", None),
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (E tonikada)", 64),
    (27.0, "mus.choir_e", 0.5, 0, 0.6, 0.2, "Xor logotip ostida", 3.5),
    *[(27.45 + i * 0.1, "sfx.thump", 0.28, round(-0.45 + 0.3 * i, 2), 0.2, 0, f"'{'ADUZ'[i]}' harfi tushadi", None) for i in range(4)],
    (27.7, "sfx.whoosh_soft", 0.16, 0, 0.3, 0, "Orbita", 7),
    (27.8, "sfx.swoosh_text", 0.22, 0, 0.2, 0, "Tagchiziq", None),
    (28.0, "sfx.type_burst", 0.22, 0, 0.15, 0, "'BIZNESINGIZ HIMOYACHISI'", None),
    (28.6, "sfx.pop_short", 0.3, 0.2, 0.3, 0.2, "CTA", 7),
    (28.62, "ui.select", 0.07, 0.2, 0.5, 0.4, "CTA qo'ng'iroqchasi", 88),
]

SCORE_26 = [
    ("Ovoz manbai", "sfx/ kutubxonasi + reel uslubi (24-qism dizayni)", "Reel grafik qurilmalarining ovozlari 24-qismdagidek (scramble — type_burst, og'ir grotesk — bass_drop, keyframe — tick_hi, harflar — thump); mavzuga xos: tavsiya yuborish — fx.send, do'st qo'shilishi — blip_up (har safar yuqoriroq), hamyon — 'bo'sh' click_soft; yechimda har ro'yxat — pop_swish + fx.coin, daromad — ratchet + fx.transfer."),
    ("0:00–0:09.5", "Muammo · F#-minor + pizzicato", "7-qism aranjirovkasi 2 yarim ton yuqorida + pizzicato. Sakkiz tavsiya, sakkiz 'qo'shildi' — har biriga hamyondan bo'sh klik javob beradi. Slab-kartalar — stutter + glitch, '0 SO'M' — fx.nope; 8.5 s to'q sariq kadr."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: aloqalar uziladi (fx.chain_snap), '0 SO'M' shovqinga aylanib sochiladi; yurak urishi."),
    ("0:10.15–0:11", "Vahiy · stripeWipe", "HEAVENLY XOR E-major'da; chiziqlar kadrni yopadi/ochadi (whoosh_sweep ×2), 'Ulashing.' — shimmer."),
    ("0:11–0:21.75", "Yechim · E-major, siyrak", "Nusxa — klik + tick, ulashish — qo'sh klik + beshta fx.send, har ro'yxat — pop_swish + tanga, daromad hisoblagichi — ratchet + transfer, xor 'ooo'. 18.5 s: PASSIV / DAROMAD. — ikki zarba. Keyframe'lar — ko'tariluvchi tick_hi, 'HISOBGA TUSHDI' — kassa."),
    ("0:22–0:27", "Natija · E-major, to'liq", "'10%' halftone fonda — bass_drop + shimmer; to'liq baraban; kassa."),
    ("0:27–0:32", "Yakun · brend", "Sonic logo (E tonikada) + xor; harflar tushishi, orbita, scramble, CTA."),
]


def score_26(M):
    """7-qism partiturasi, 2 yarim ton yuqorida (F#-minor → E-major)."""
    global KEY_SHIFT
    KEY_SHIFT = 2
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_26():
    """26-qism: Ulashing va daromad ko'ring. Score (+2) + pizzicato + xor + cue-sheet (CUES_26)."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # the links snap: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_26(M)
    quirky_pizz(M, 1.0, 9.45, root=66, gain=0.38)
    render_cues(M, CUES_26)
    out = M.render()
    out *= np.clip((DUR - t) / 1.4, 0, 1)[:, None] * np.clip(t / 0.3, 0, 1)[:, None]
    return out


# ---------- 27-qism: Aqlli byudjet taqsimoti — INSTAGRAM REELS (hook 0-kadrda, loop, xavfsiz zona) ----------
SOUNDS.update({
    "mus.choir_eb": ("L1", lambda a=None: choir([63, 67, 70, 75], a or 2.5), "Xor 'aaah' Eb-major (heavenly uslub, original sintez)"),
    "mus.choir_eb_hi": ("L1", lambda a=None: choir([75, 79, 82], a or 1.8, "o"), "Baland xor 'ooo' Eb-major"),
    "fx.coin_v": ("L3", SOUNDS["fx.coin"][1], "Tanga (vakuum ichida eshitiladigan nusxa)"),
})
FRONT.update({"fx.coin_v"})
_DROPS27 = [(2.0 + k * 0.38, k % 6) for k in range(18)]
_LIVE27 = {1, 4}
_KEYS27 = sorted({20.2 + 1.2 * _ease_inv(k) for k in (0, .06, .12, .28, .34, .5, .56, .62, .78, .84, .9)})

CUES_27 = [
    # --- HOOK (0-kadr = loop nuqtasi) ---
    (0.0, "sfx.boom_sub", 0.95, 0, 0.3, 0, "HOOK: '62%' — kadr 0 dan zarba", None),
    (0.0, "sfx.bass_drop", 0.7, 0, 0.3, 0, "'62%' og'ir grotesk", None),
    (0.12, "sfx.bass_drop", 0.5, 0, 0.3, 0, "'KUYYAPTI'", 5),
    (0.05, "fx.fizz", 0.14, 0.3, 0.2, 0, "Kuyayotgan pul shitirlashi", None),
    (0.3, "sfx.swoosh_text", 0.2, 0, 0.2, 0, "Serif izoh", None),
    (1.45, "sfx.glitch_short", 0.4, 0, 0.15, 0, "Keskin kesim → muammo", None),
    (1.5, "sfx.swipe", 0.3, 0, 0.15, 0, "Kesim qatlami", None),
    # --- 1. Muammo ---
    (1.6, "amb.office", 0.06, 0, 0, 0, "Xona — sahna 'havosi'", 8.0),
    (1.6, "sfx.type_burst", 0.26, 0, 0.15, 0, "'27-QISM' dekodlanadi", None),
    (1.75, "sfx.bass_drop", 0.4, 0, 0.3, 0, "'BYUDJET'", 3),
    *[(1.75 + i * 0.06, "sfx.pop_short", 0.14, round(-0.5 + 0.2 * i, 2), 0.2, 0, f"Kanal kartasi #{i + 1}", [0, 2, 4, 7, 9, 12][i]) for i in range(6)],
    *[x for k, (a, ch) in enumerate(_DROPS27) for x in [
        (a, "fx.coin", 0.07, round(-0.4 + 0.16 * ch, 2), 0.15, 0, f"Tanga → kanal #{ch + 1}", None),
        ((a + 0.45, "sfx.tick_hi", 0.12, round(-0.4 + 0.16 * ch, 2), 0.2, 0.1, "Jonli kanal: foydali", 12) if ch in _LIVE27 else
         (a + 0.45, "fx.zap", 0.1, round(-0.4 + 0.16 * ch, 2), 0.15, 0, "O'lik kanal: tanga yonib ketdi", None)),
    ]],
    *[x for at, pan, nm in ((5.6, -0.4, "O'LIK KANAL"), (6.6, 0.4, "BOTLAR KO'RADI"), (7.6, -0.4, "PUL KUYDI")) for x in [
        (at, "sfx.stutter", 0.42, pan, 0.2, 0, f"Slab-karta: {nm}", None),
        (at, "sfx.glitch_short", 0.5, pan, 0.2, 0, "Slam qatlami", None),
    ]],
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [53, 56, 60, 65]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da", None),
    (8.45, "sfx.whoosh_low", 0.35, 0, 0.2, 0, "To'q sariq kadr", None),
    (8.5, "sfx.boom_sub", 0.9, 0, 0.35, 0, "KUL. — asosiy zarba", None),
    (8.5, "sfx.bass_drop", 0.6, 0, 0.3, 0, "Zarba qatlami", None),
    (8.5, "sfx.glitch_seq", 0.26, 0, 0.2, 0, "Zarba qatlami: glitch", None),
    (8.55, "fx.fizz", 0.2, 0, 0.2, 0, "Kul uchqunlari", None),
    # --- vakuum ---
    (9.6, "fx.coin_v", 0.3, 0, 0.2, 0, "OVOZ VAKUUMI: oxirgi tanga tushadi", None),
    (9.85, "fx.fizz", 0.3, 0, 0.1, 0, "...yonib ketadi", None),
    (10.0, "sfx.dust", 0.3, 0.2, 0, 0, "...kulga aylanadi", None),
    (9.95, "fx.heartbeat", 0.26, 0, 0, 0, "Yurak urishi", None),
    # --- o'tish: barsWipe ---
    (10.15, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: yechim akkordi (Eb-major)", [63, 67, 70, 75]),
    (10.2, "mus.choir_eb", 1.2, 0, 0.6, 0.2, "HEAVENLY XOR — 'Optimallash.'", 2.8),
    *[(10.3 + i * 0.03, "sfx.pop_short", 0.12, round(-0.5 + 0.09 * i, 2), 0.15, 0, f"Ekvalayzer ustuni #{i + 1}", [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26][i]) for i in range(12)],
    (10.55, "sfx.shimmer", 0.3, 0, 0.4, 0.2, "'Optimallash.'", None),
    (10.7, "sfx.whoosh_sweep", 0.25, 0, 0.25, 0, "Ustunlar tushadi", 7),
    # --- 2. Yechim ---
    (11.0, "sfx.boom_sub", 0.45, 0, 0.35, 0, "Yechim boshlanishi", None),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit", 10.7),
    *[(11.25 + i * 0.12, "sfx.swoosh_text", 0.16, round(-0.4 + 0.27 * i, 2), 0.15, 0, f"UI-karta #{i + 1}", None) for i in range(4)],
    (12.2, "sfx.click_1", 0.7, 0.3, 0, 0, "Jonli optimizatsiya — YONDI", None),
    (12.22, "sfx.blip_up", 0.3, 0.3, 0.25, 0.2, "Toggle laym", None),
    (12.55, "fx.scan", 0.22, 0, 0.2, 0, "Skaner kanallar bo'ylab", None),
    *[((12.55 + 0.85 * (i + 0.5) / 6, "ui.select", 0.12, 0.3, 0.3, 0.2, f"Kanal #{i + 1}: FOYDALI", 75) if i in _LIVE27 else
       (12.55 + 0.85 * (i + 0.5) / 6, "fx.nope", 0.16, -0.3, 0.15, 0, f"Kanal #{i + 1}: STOP", None)) for i in range(6)],
    (13.7, "sfx.click_double_2", 0.7, 0.2, 0, 0, "'Qayta taqsimlash'", None),
    (13.72, "fx.transfer", 0.3, 0, 0.2, 0, "Pul jonli kanallarga oqadi", None),
    (13.75, "sfx.whoosh_sweep", 0.2, 0, 0.2, 0, "Budjet chiziqlari ko'chadi", 5),
    (14.6, "sfx.ratchet_roll", 0.2, -0.3, 0.15, 0, "Tejaldi: 1 860 000", None),
    *[(14.65 + k * 0.08, "fx.coin", 0.06, round(-0.4 + 0.1 * k, 2), 0.2, 0, f"Tanga #{k + 1}", None) for k in range(8)],
    (15.4, "sfx.whoosh_sweep", 0.15, 0.3, 0.2, 0, "Donut 100%", 9),
    (16.0, "mus.choir_eb_hi", 0.45, 0, 0.6, 0.2, "Xor 'ooo' — har so'm ishlaydi", 1.4),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: HAR SO'M ISHLAYDI oldidan", [67, 70, 75, 79]),
    (18.45, "sfx.whoosh_low", 0.3, 0, 0.3, 0, "Laym kadr", None),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "HAR SO'M — zarba", None),
    (18.5, "sfx.bass_drop", 0.5, 0, 0.3, 0, "Og'ir grotesk", None),
    (18.6, "sfx.thump", 0.45, 0, 0.25, 0, "ISHLAYDI. — ikkinchi zarba", None),
    (18.5, "mus.choir_eb", 0.8, 0, 0.6, 0.2, "Xor zarba ostida", 1.8),
    (18.5, "imp.sparkle", 0.3, 0, 0.5, 0, "Uchqunlar", 331),
    (18.8, "sfx.swoosh_text", 0.3, 0, 0.2, 0, "Serif izoh", None),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Binafsha karta", None),
    (20.0, "sfx.shimmer", 0.22, 0, 0.3, 0.2, "'Byudjet — aqlli taqsimotda.'", None),
    *[(k, "sfx.tick_hi", 0.18, round(-0.45 + 0.9 * i / max(1, len(_KEYS27) - 1), 2), 0.25, 0.2, f"Keyframe #{i + 1}", [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24][i % 11]) for i, k in enumerate(_KEYS27)],
    (21.35, "ui.success", 0.24, 0, 0.5, 0.3, "BYUDJET ISHLAYAPTI", None),
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — whip'ga", None),
    (21.75, "sfx.whoosh_sweep", 0.42, 0, 0.25, 0, "Whip-pan", None),
    (21.75, "sfx.swipe", 0.3, 0, 0.2, 0, "Whip qatlami", None),
    # --- 3. Natija ---
    (22.0, "sfx.boom_sub", 0.5, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.1, "sfx.bass_drop", 0.45, 0, 0.3, 0, "'×3' chiziqli fonda", 5),
    (22.1, "sfx.whoosh_low", 0.2, 0, 0.2, 0, "Chiziqlar oqadi", 3),
    (22.95, "sfx.type_burst", 0.25, 0, 0.15, 0, "'NATIJA'", None),
    (23.0, "sfx.bass_drop", 0.3, 0, 0.3, 0, "'O'SHA PUL — ×3'", 7),
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA", None),
    (23.22, "sfx.notify_ring", 0.22, 0.2, 0.25, 0.2, "Kassa qatlami", None),
    *[(23.5 + i * 0.35, "sfx.swipe", 0.34, -0.4, 0.15, 0, f"'Oldin' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, f"sfx.{CLICKS[i % 5]}", 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [75, 79, 82][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [67, 72, 75, 79]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "imp.sparkle", 0.35, 0, 0.5, 0, "Uchqunlar", 337),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_short", 0.32, -0.4 + 0.4 * i, 0.3, 0, f"Rangli nishon #{i + 1}", [3, 8, 12][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Qo'ng'iroqcha", [79, 84, 87][i]),
    ]],
    (26.85, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakuniy kadrga", None),
    # --- yakun + loop ko'prigi ---
    (27.0, "brand.logo", 0.55, 0, 0.5, 0.35, "ADUZ SONIC LOGO (Eb tonikada)", 63),
    (27.0, "mus.choir_eb", 0.5, 0, 0.6, 0.2, "Xor logotip ostida", 3.5),
    *[(27.45 + i * 0.1, "sfx.thump", 0.28, round(-0.45 + 0.3 * i, 2), 0.2, 0, f"'{'ADUZ'[i]}' harfi tushadi", None) for i in range(4)],
    (27.7, "sfx.whoosh_soft", 0.16, 0, 0.3, 0, "Orbita", 7),
    (27.8, "sfx.swoosh_text", 0.22, 0, 0.2, 0, "Tagchiziq", None),
    (28.0, "sfx.type_burst", 0.22, 0, 0.15, 0, "'BIZNESINGIZ HIMOYACHISI'", None),
    (28.5, "sfx.bass_drop", 0.3, 0, 0.3, 0, "IZOHGA 'BYUDJET' — CTA", 7),
    (28.52, "ui.select", 0.08, 0, 0.5, 0.4, "CTA qo'ng'iroqchasi", 87),
    (28.9, "sfx.swoosh_text", 0.2, 0, 0.2, 0, "'saqlab qo'ying'", None),
    (30.8, "sfx.riser_click", 0.3, 0, 0, 0, "LOOP: riser — cho'qqisi kadr 0 zarbasiga ulanadi", None),
    (31.4, "sfx.whoosh_low", 0.3, 0, 0.2, 0, "LOOP: to'q sariq kadr qayta ochiladi", None),
    (31.4, "sfx.glitch_short", 0.25, 0, 0.15, 0, "LOOP: glitch", None),
]

SCORE_27 = [
    ("Format", "Instagram Reels uchun", "Hook kadr 0 da (fade-in yo'q), har 1–2 s da yangi voqea, matn xavfsiz zonada, katta subtitrlar (ovozsiz ko'rish), izoh-CTA va loop: oxirgi 0.6 s boshidagi kadrni qayta quradi, ovozda riser kadr 0 dagi zarbaga ulanadi. Audio — boshida/oxirida so'nish yo'q (20 ms anti-klik)."),
    ("0:00–0:01.6", "HOOK", "Kadr 0 dan sub-boom + bass_drop ('62% KUYYAPTI'), kuyayotgan pul shitirlashi; 1.45 s keskin kesim (glitch + swipe)."),
    ("0:01.6–0:09.5", "Muammo · D-minor + pizzicato", "7-qism aranjirovkasi 1 yarim ton yuqorida + pizzicato. 18 ta tanga oltita kanalga: jonli kanalda — tick_hi, o'lik kanalda — fx.zap (yonib ketadi). Slab-kartalar — stutter + glitch; 8.5 s KUL. — boom + fizz."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: oxirgi tanga tushadi (fx.coin_v), yonadi (fizz), kulga aylanadi (dust); yurak urishi."),
    ("0:10.15–0:11", "Vahiy · barsWipe", "HEAVENLY XOR Eb-major'da; ekvalayzer ustunlari — 12 pog'onali pentatonik pop kaskadi, 'Optimallash.' — shimmer."),
    ("0:11–0:21.75", "Yechim · Eb-major, siyrak", "Toggle — klik + blip; skaner — fx.scan, har kanal: STOP — fx.nope, FOYDALI — ui.select; qayta taqsimlash — qo'sh klik + fx.transfer; tejaldi — ratchet + tangalar. 18.5 s: HAR SO'M / ISHLAYDI. — ikki zarba + xor; keyframe'lar — tick_hi."),
    ("0:22–0:27", "Natija · Eb-major, to'liq", "'×3' chiziqli fonda, kassa, nishonlar."),
    ("0:27–0:32", "Yakun + loop", "Sonic logo (Eb) + xor, harflar, izoh-CTA 'BYUDJET'; 30.8 s riser + 31.4 s whoosh — loop orqali kadr 0 zarbasiga ulanadi."),
]


def score_27(M):
    """7-qism partiturasi, 1 yarim ton yuqorida (F-minor → Eb-major)."""
    global KEY_SHIFT
    KEY_SHIFT = 1
    try:
        score_7(M)
    finally:
        KEY_SHIFT = 0


def render_27():
    """27-qism (Instagram Reels): Score (+1) + pizzicato + xor + cue-sheet (CUES_27). Loop: so'nishsiz, 20 ms anti-klik."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # the last coin burns: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_27(M)
    quirky_pizz(M, 1.6, 9.45, root=65, gain=0.36)
    render_cues(M, CUES_27)
    out = M.render()
    out *= np.clip((DUR - t) / 0.02, 0, 1)[:, None] * np.clip(t / 0.005, 0, 1)[:, None]
    return out


# ---------- 28-qism (XOTIMA): Yangi bozor standarti — INSTAGRAM REELS, asl tonallikka (D) qaytish ----------
SOUNDS.update({
    "fx.sticky_v": ("L3", SOUNDS["fx.sticky"][1], "Stiker (vakuum ichida eshitiladigan nusxa)"),
})
FRONT.update({"fx.sticky_v"})
_STK28 = [1.7 + i * 0.55 for i in range(12)]
_MOD28 = [11.5 + i * 0.3 for i in range(8)]

CUES_28 = [
    # --- HOOK ---
    (0.0, "sfx.boom_sub", 0.95, 0, 0.3, 0, "HOOK: 'ESKI DAVR' — kadr 0 dan zarba", None),
    (0.0, "sfx.bass_drop", 0.7, 0, 0.3, 0, "'ESKI'", None),
    (0.1, "sfx.bass_drop", 0.5, 0, 0.3, 0, "'DAVR'", 3),
    (0.0, "fx.strike", 0.35, 0, 0.2, 0, "To'q sariq chiziq bilan o'chiriladi", None),
    (0.2, "sfx.swoosh_text", 0.22, 0, 0.2, 0, "'tugadi.'", None),
    (1.45, "sfx.glitch_short", 0.4, 0, 0.15, 0, "Keskin kesim → muammo", None),
    (1.5, "sfx.swipe", 0.3, 0, 0.15, 0, "Kesim qatlami", None),
    # --- 1. Eski davr: tartibsizlik doskasi ---
    (1.6, "amb.office", 0.06, 0, 0, 0, "Xona — sahna 'havosi'", 8.0),
    (1.6, "sfx.type_burst", 0.26, 0, 0.15, 0, "'28-QISM / XOTIMA' dekodlanadi", None),
    (1.75, "sfx.bass_drop", 0.4, 0, 0.3, 0, "'ESKI DAVR'", 3),
    *[x for i, a in enumerate(_STK28) for x in [
        (a, "fx.sticky", 0.3, round(-0.45 + 0.45 * (i % 3), 2), 0.15, 0, f"Og'riq stikeri #{i + 1} yopishdi", None),
        (a + 0.1, "fx.twang", 0.07, round(-0.3 + 0.3 * (i % 3), 2), 0.2, 0, "Qizil ip tortiladi", None),
    ]],
    *[x for at, pan, nm in ((5.6, -0.4, "TARTIBSIZLIK"), (6.6, 0.4, "ISHONCHSIZLIK"), (7.6, -0.2, "VAQT YO'QOTISH")) for x in [
        (at, "sfx.stutter", 0.42, pan, 0.2, 0, f"Slab-karta: {nm}", None),
        (at, "sfx.glitch_short", 0.5, pan, 0.2, 0, "Slam qatlami", None),
    ]],
    (8.0, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: asosiy zarba oldidan", [52, 55, 59, 64]),
    (8.38, "sfx.riser_click", 0.3, 0, 0, 0, "Riser — cho'qqisi 9.5 s da", None),
    (8.45, "sfx.whoosh_low", 0.35, 0, 0.2, 0, "To'q sariq kadr", None),
    (8.5, "sfx.boom_sub", 0.9, 0, 0.35, 0, "YETAR. — asosiy zarba", None),
    (8.5, "sfx.bass_drop", 0.6, 0, 0.3, 0, "Zarba qatlami", None),
    (8.5, "imp.crash", 0.25, 0, 0.4, 0, "Klassik crash", None),
    # --- vakuum: stikerlar to'kiladi ---
    *[(9.6 + k * 0.05, "fx.sticky_v", 0.18, round(-0.4 + 0.07 * k, 2), 0.1, 0, f"OVOZ VAKUUMI: stiker #{k + 1} tushadi", None) for k in range(12)],
    (9.95, "fx.heartbeat", 0.26, 0, 0, 0, "Yurak urishi", None),
    # --- o'tish: snapInto ---
    (10.15, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: yechim akkordi (D-major — seriyaning asl tonalligi)", [62, 66, 69, 74]),
    (10.2, "mus.choir_d", 1.3, 0, 0.6, 0.2, "HEAVENLY XOR D-major — uyga qaytish", 3.0),
    *[(10.3 + i * 0.04, "fx.snap", 0.12, round(-0.5 + 0.09 * i, 2), 0.15, 0, f"Stiker panjaraga tushadi #{i + 1}", None) for i in range(12)],
    (10.75, "tr.boot", 0.25, 0, 0.3, 0.2, "ADUZ markazi yonadi", 62),
    # --- 2. Ekotizim ---
    (11.0, "sfx.boom_sub", 0.45, 0, 0.35, 0, "Yechim boshlanishi", None),
    (11.0, "amb.air", 0.025, 0, 0, 0, "Yorug' muhit", 10.7),
    (11.1, "sfx.type_burst", 0.24, 0, 0.15, 0, "'ADUZ EKOTIZIMI'", None),
    *[x for i, a in enumerate(_MOD28) for x in [
        (a, "sfx.tick_hi", 0.18, round(-0.6 + 0.17 * i, 2), 0.25, 0.2, f"Modul #{i + 1} ulanadi", [0, 2, 4, 7, 9, 12, 14, 16][i]),
        (a + 0.2, "sfx.pop_short", 0.22, round(-0.6 + 0.17 * i, 2), 0.2, 0, "Modul kartasi", [0, 2, 4, 7, 9, 12, 14, 16][i]),
    ]],
    (14.3, "sfx.click_1", 0.7, 0.3, 0, 0, "'Hisobotni ochish'", None),
    (14.6, "fx.paper", 0.3, 0, 0.2, 0, "Shaffof hisobot chiqadi", None),
    *[(14.9 + i * 0.3, "fx.coin", 0.12, (-0.3, 0.2, 0.4)[i], 0.2, 0, f"Hisobot qatori #{i + 1}", None) for i in range(3)],
    (16.1, "sfx.sparkle_hit", 0.3, 0, 0.3, 0.2, "HAMMASI KO'RINIB TURADI", None),
    (16.12, "mus.choir_hi", 0.5, 0, 0.6, 0.2, "Xor 'ooo' — shaffoflik", 1.4),
    (18.0, "tr.swell", 0.35, 0, 0.3, 0, "J-cut: YANGI STANDART oldidan", [66, 69, 74, 78]),
    (18.45, "sfx.whoosh_low", 0.3, 0, 0.3, 0, "Laym kadr", None),
    (18.5, "sfx.boom_sub", 0.8, 0, 0.35, 0, "YANGI — zarba", None),
    (18.5, "sfx.bass_drop", 0.5, 0, 0.3, 0, "Og'ir grotesk", None),
    (18.6, "sfx.thump", 0.45, 0, 0.25, 0, "STANDART. — ikkinchi zarba", None),
    (18.5, "mus.choir_d", 0.8, 0, 0.6, 0.2, "Xor zarba ostida", 1.8),
    (18.5, "imp.sparkle", 0.3, 0, 0.5, 0, "Uchqunlar", 331),
    (18.8, "sfx.swoosh_text", 0.3, 0, 0.2, 0, "Serif izoh", None),
    (19.7, "sfx.swipe", 0.3, 0, 0.2, 0, "Binafsha karta", None),
    (20.0, "sfx.shimmer", 0.22, 0, 0.3, 0.2, "'Bozorning yangi standarti.'", None),
    *[(20.4 + i * 0.25, "ui.select", 0.14, round(-0.3 + 0.2 * i, 2), 0.3, 0.2, f"Standart #{i + 1} ✓", [74, 78, 81, 86][i]) for i in range(4)],
    (21.5, "fx.stamp", 0.25, 0, 0.2, 0, "STANDART: ADUZ", None),
    (20.63, "sfx.riser_click", 0.32, 0, 0, 0, "Riser — whip'ga", None),
    (21.75, "sfx.whoosh_sweep", 0.42, 0, 0.25, 0, "Whip-pan", None),
    (21.75, "sfx.swipe", 0.3, 0, 0.2, 0, "Whip qatlami", None),
    # --- 3. Natija ---
    (22.0, "sfx.boom_sub", 0.5, 0, 0.4, 0, "Natija boshlanishi", None),
    (22.1, "sfx.bass_drop", 0.45, 0, 0.3, 0, "'28/28' nuqtali panjarada", 5),
    (22.1, "sfx.shimmer", 0.18, 0, 0.3, 0.2, "Panjara to'lqini", None),
    (22.95, "sfx.type_burst", 0.25, 0, 0.15, 0, "'NATIJA'", None),
    (23.0, "sfx.bass_drop", 0.3, 0, 0.3, 0, "'ESKI DAVR → ADUZ'", 7),
    (23.2, "fx.kassa", 0.32, 0, 0.3, 0.2, "KASSA", None),
    (23.22, "sfx.notify_ring", 0.22, 0.2, 0.25, 0.2, "Kassa qatlami", None),
    *[(23.5 + i * 0.35, "fx.strike", 0.3, -0.4, 0.15, 0, f"'Eski davr' qatori #{i + 1} chizildi", None) for i in range(3)],
    *[x for i in range(3) for x in [
        (23.7 + i * 0.35, f"sfx.{CLICKS[(i + 2) % 5]}", 0.4, 0.4, 0, 0, f"ADUZ qatori #{i + 1}", None),
        (23.72 + i * 0.35, "ui.select", 0.13, 0.4, 0.3, 0.2, "Tonallikdagi tasdiq", [74, 78, 81][i]),
    ]],
    (24.5, "tr.swell", 0.3, 0, 0.3, 0, "J-cut: nishonlar oldidan", [66, 71, 74, 78]),
    (25.0, "sfx.boom_sub", 0.45, 0, 0.4, 0, "Urg'u", None),
    (25.0, "imp.sparkle", 0.35, 0, 0.5, 0, "Uchqunlar", 337),
    *[x for i in range(3) for x in [
        (25.2 + i * 0.25, "sfx.pop_short", 0.32, -0.4 + 0.4 * i, 0.3, 0, f"Rangli nishon #{i + 1}", [5, 9, 12][i]),
        (25.22 + i * 0.25, "ui.select", 0.1, -0.4 + 0.4 * i, 0.3, 0, "Qo'ng'iroqcha", [81, 86, 90][i]),
    ]],
    (26.85, "sfx.whoosh_soft", 0.2, 0, 0.4, 0, "Yakuniy kadrga", None),
    # --- yakun + loop ---
    (27.0, "brand.logo", 0.6, 0, 0.5, 0.35, "ADUZ SONIC LOGO (D tonikada — seriya boshidagidek)", 62),
    (27.0, "mus.choir_d", 0.6, 0, 0.6, 0.2, "Xor logotip ostida", 3.5),
    *[(27.45 + i * 0.1, "sfx.thump", 0.28, round(-0.45 + 0.3 * i, 2), 0.2, 0, f"'{'ADUZ'[i]}' harfi tushadi", None) for i in range(4)],
    (27.7, "sfx.whoosh_soft", 0.16, 0, 0.3, 0, "Orbita", 7),
    (27.8, "sfx.swoosh_text", 0.22, 0, 0.2, 0, "Tagchiziq", None),
    (28.0, "sfx.type_burst", 0.22, 0, 0.15, 0, "'BIZNESINGIZ HIMOYACHISI'", None),
    (28.5, "sfx.bass_drop", 0.3, 0, 0.3, 0, "IZOHGA 'ADUZ' — CTA", 7),
    (28.52, "ui.select", 0.08, 0, 0.5, 0.4, "CTA qo'ng'iroqchasi", 86),
    (28.9, "sfx.swoosh_text", 0.2, 0, 0.2, 0, "'saqlab qo'ying'", None),
    (30.8, "sfx.riser_click", 0.3, 0, 0, 0, "LOOP: riser — kadr 0 zarbasiga", None),
    (31.4, "sfx.whoosh_low", 0.3, 0, 0.2, 0, "LOOP: hook kadri qayta ochiladi", None),
    (31.4, "sfx.glitch_short", 0.25, 0, 0.15, 0, "LOOP: glitch", None),
]

SCORE_28 = [
    ("Format", "Instagram Reels (27-qism qoidalari) + seriya xotimasi", "Hook kadr 0 da, xavfsiz zona, katta subtitrlar, izoh-CTA 'ADUZ', loop. Musiqa seriyaning asl tonalligiga qaytadi: 7-qism partiturasi KEY_SHIFT = 0 (E-minor → D-major), xor D-major, sonic logo D tonikada — 1-qismdagidek."),
    ("0:00–0:01.6", "HOOK", "Kadr 0 dan sub-boom + ikki bass_drop ('ESKI / DAVR'), fx.strike — o'chiriladi; 1.45 s keskin kesim."),
    ("0:01.6–0:09.5", "Eski davr · E-minor + pizzicato", "O'n ikki og'riq stikeri doskaga yopishadi (fx.sticky), har biri qizil ip bilan bog'lanadi (fx.twang); slab-kartalar — stutter + glitch; 8.5 s YETAR. — boom + crash."),
    ("0:09.5–0:10.15", "Ovoz vakuumi", "Gate: stikerlar birin-ketin tushadi (fx.sticky_v ×12), yurak urishi."),
    ("0:10.15–0:11", "Uyga qaytish · snapInto", "HEAVENLY XOR D-major; stikerlar panjaraga 'chiq' etib tushadi (fx.snap ×12), ADUZ markazi yonadi (tr.boot D)."),
    ("0:11–0:21.75", "Ekotizim · D-major", "Sakkiz modul ulanadi — pentatonik tick_hi + pop; shaffof hisobot — qog'oz + tangalar, 'hammasi ko'rinib turadi' — sparkle + xor 'ooo'. 18.5 s: YANGI / STANDART. — ikki zarba; standartlar ro'yxati — ko'tariluvchi ui.select, muhr."),
    ("0:22–0:27", "Natija · D-major, to'liq", "'28/28' — bass_drop + shimmer, kassa, 'eski davr' qatorlari — fx.strike."),
    ("0:27–0:32", "Xotima + loop", "Sonic logo D tonikada + xor, harflar, izoh-CTA 'ADUZ'; riser + whoosh kadr 0 zarbasiga ulanadi."),
]


def render_28():
    """28-qism (Xotima, Instagram Reels): asl tonallikdagi score + pizzicato + xor + cue-sheet (CUES_28). Loop: so'nishsiz."""
    M = MixerPro(120)
    M.gates.append((9.5, 10.15, 0.03))  # the stickers drop off the board: sound vacuum
    M.width = [(0, 0.75), (32, 0.75)]
    score_7(M)
    quirky_pizz(M, 1.6, 9.45, root=64, gain=0.36)
    render_cues(M, CUES_28)
    out = M.render()
    out *= np.clip((DUR - t) / 0.02, 0, 1)[:, None] * np.clip(t / 0.005, 0, 1)[:, None]
    return out

V2 = {4: render_4, 5: render_5, 6: render_6, 7: render_7, 8: render_8, 9: render_9, 10: render_10, 11: render_11, 12: render_12, 13: render_13, 14: render_14, 15: render_15, 16: render_16, 17: render_17, 18: render_18, 19: render_19, 20: render_20, 21: render_21, 22: render_22, 23: render_23, 24: render_24, 25: render_25, 26: render_26, 27: render_27, 28: render_28}


CUES = {1: cues_1, 2: cues_2, 3: cues_3}

if __name__ == "__main__":
    episode, out = int(sys.argv[1]), sys.argv[-1]
    if "--cuesheet" in sys.argv:
        sheets = {7: (CUES_7, SCORE_7), 8: (CUES_8, SCORE_8), 9: (CUES_9, SCORE_9), 10: (CUES_10, SCORE_10), 11: (CUES_11, SCORE_11), 12: (CUES_12, SCORE_12), 13: (CUES_13, SCORE_13), 14: (CUES_14, SCORE_14), 15: (CUES_15, SCORE_15), 16: (CUES_16, SCORE_16), 17: (CUES_17, SCORE_17), 18: (CUES_18, SCORE_18), 19: (CUES_19, SCORE_19), 20: (CUES_20, SCORE_20), 21: (CUES_21, SCORE_21), 22: (CUES_22, SCORE_22), 23: (CUES_23, SCORE_23), 24: (CUES_24, SCORE_24), 25: (CUES_25, SCORE_25), 26: (CUES_26, SCORE_26), 27: (CUES_27, SCORE_27), 28: (CUES_28, SCORE_28)}
        with open(out, "w") as fh:
            fh.write(cuesheet_md(episode, *sheets[episode]))
        print("wrote", out)
        sys.exit(0)
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
