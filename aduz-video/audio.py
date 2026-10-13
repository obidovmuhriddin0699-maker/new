"""Synthesises the music + SFX track for an episode (32 s, 44.1 kHz stereo WAV).

Usage: python3 audio.py <episode number> build/episodeN.wav
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


CUES = {1: cues_1, 2: cues_2, 3: cues_3}

if __name__ == "__main__":
    episode, out = int(sys.argv[1]), sys.argv[2]
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
