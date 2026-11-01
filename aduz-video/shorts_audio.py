#!/usr/bin/env python3
"""Music bed + SFX for the 18 s "qisqa" Reels (shorts.js); the narrator is added later by voice_gemini.py.

  python3 -I shorts_audio.py build/short.wav
"""
import os
import sys
import wave

import numpy as np

SR, DUR = 44100, 18.0
HERE = os.path.dirname(os.path.abspath(__file__))
out = np.zeros((int(SR * DUR), 2))


def add(at, sig, gain=1.0):
    i = int(at * SR)
    n = min(len(sig), len(out) - i)
    if n > 0:
        out[i:i + n] += (sig[:n, None] if sig.ndim == 1 else sig[:n]) * gain


def sfx(name):
    with wave.open(os.path.join(HERE, "sfx", name + ".wav")) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768.0


def env(n, a=0.005, r=0.2):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (50 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 9)


def hat():
    n = int(0.06 * SR)
    return np.random.default_rng(1).normal(0, 1, n) * np.exp(-np.arange(n) / SR * 70) * 0.3


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t + 0.5) for f in freqs)
    return s / len(freqs) * env(n, 0.4, 0.6)


# Groove from 2.2 s (bot section) to 18 s, 100 BPM; quieter under the hook so the first words land.
beat = 60 / 100
t = 2.2
i = 0
while t < DUR - 0.2:
    if i % 2 == 0:
        add(t, kick(), 0.5)
    add(t + beat / 2, hat(), 0.35)
    t += beat
    i += 1
chords = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7], [164.8, 207.7, 246.9]]
for k, at in enumerate(np.arange(0.0, DUR, 2.4)):
    add(at, pad(chords[k % 4], 2.6), 0.07 if at < 2.2 else 0.1)

add(0.0, sfx("bass_drop"), 0.8)
add(2.0, sfx("whoosh_sweep"), 0.5)
add(14.0, sfx("whoosh_sweep"), 0.5)
add(14.3, sfx("sparkle_hit"), 0.6)
add(15.3, sfx("pop_swish"), 0.6)

out *= 0.9 / max(1e-9, np.abs(out).max())
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
