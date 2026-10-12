"""Tabiiyroq o'zbekcha ovoz: RHVoice (Dilnavoz, Islom) + yumshoq ishlov va musiqa "ducking".

O'rnatish (Ubuntu):
    apt-get install -y rhvoice
    git clone --depth 1 https://github.com/RHVoice/Uzbek-bin.git  /usr/share/RHVoice/languages/Uzbek
    git clone --depth 1 https://github.com/RHVoice/dilnavoz-uzb.git /usr/share/RHVoice/voices/dilnavoz
    git clone --depth 1 https://github.com/RHVoice/islom-uzb.git    /usr/share/RHVoice/voices/islom
"""
import math
import os
import re
import subprocess
import wave

import numpy as np

SR = 44100

# speaker -> (RHVoice voice, rate %, pitch %)
SPEAKERS = {
    "rus": ("islom", 100, 92),      # Rustam aka: past, xotirjam
    "sho": ("islom", 112, 122),     # Shokir: yosh, tez, baland
    "dil": ("dilnavoz", 100, 100),  # Dilnoza
    "xot": ("dilnavoz", 96, 108),   # Rustam akaning xotini (kadr ortidan)
    "dik": ("islom", 96, 104),      # Diktor
    "xar": ("islom", 104, 112),     # Xaridor
}

# gentle voice chain: clean lows, soften harsh highs, even out level, tiny room
VOICE_CHAIN = ("highpass=f=75,"
               "afftdn=nr=10:nf=-45,"                     # vocoder hiss out
               "agate=threshold=0.008:ratio=3:attack=5:release=120,"
               "equalizer=f=140:t=q:w=1:g=2.5,"            # warmth / body
               "equalizer=f=320:t=q:w=1.4:g=-3,"           # less boxy
               "equalizer=f=2800:t=q:w=1.6:g=2.5,"         # clarity
               "equalizer=f=5500:t=q:w=2:g=-4,"            # soften buzz
               "lowpass=f=8800,"
               "deesser=i=0.4,"
               "acompressor=threshold=-22dB:ratio=2.5:attack=10:release=150:makeup=3:knee=6,"
               "aecho=0.88:0.4:18|33:0.07|0.04")           # small warm room
PHONE_CHAIN = "highpass=f=280,lowpass=f=3600,acompressor=threshold=-20dB:ratio=3:makeup=4"


# emotion -> (rate %, pitch shift %, volume %)
EMOTIONS = {
    "neutral": (100, 0, 100),
    "warm": (94, 2, 100),       # diktor: xotirjam, iliq
    "tired": (86, -8, 90),      # charchagan
    "sad": (82, -12, 86),       # xafa, cho'zib
    "ironic": (92, -4, 98),     # kinoya
    "happy": (106, 8, 106),
    "excited": (114, 14, 115),  # hayajon
    "shout": (110, 18, 125),    # qichqiriq
    "angry": (110, 6, 118),     # asabiy
    "worried": (104, 6, 102),   # xavotir
    "realize": (78, -6, 84),    # sekin anglash
}
_TAG = re.compile(r"\[(\w+)(?:=(\d+))?\]")


def to_ssml(text):
    """'[tired]Eh...[p=400][sad]Bugun' -> SSML with prosody per segment and breaks."""
    out, emo, pos = [], "neutral", 0

    def flush(chunk):
        chunk = chunk.strip()
        if chunk:
            r, pch, vol = EMOTIONS[emo]
            chunk = chunk.replace("&", "va").replace("<", "").replace(">", "")
            out.append(f'<prosody rate="{r}%" pitch="{100 + pch}%" volume="{vol}%">{chunk}</prosody>')

    for m in _TAG.finditer(text):
        flush(text[pos:m.start()])
        if m.group(1) == "p":
            out.append(f'<break time="{int(m.group(2) or 300)}ms"/>')
        else:
            emo = m.group(1)
        pos = m.end()
    flush(text[pos:])
    return "<speak>" + " ".join(out) + "</speak>"


def tts(text, speaker, path, rate_mul=1.0):
    voice, rate, pitch = SPEAKERS[speaker]
    ssml = to_ssml(text) if "[" in text else None
    cmd = ["RHVoice-test", "-p", voice, "-q", "max", "-r", str(int(rate * rate_mul)), "-t", str(pitch), "-o", path]
    if ssml:
        cmd.insert(1, "-s")
    subprocess.run(cmd, input=(ssml or text).encode(), check=True, stderr=subprocess.DEVNULL)


def load(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768


def save(path, sig):
    sig = np.clip(sig, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())


def render_line(text, speaker, tmp, idx, phone=False, rate_mul=1.0):
    raw = os.path.join(tmp, f"v{idx}_raw.wav")
    out = os.path.join(tmp, f"v{idx}.wav")
    tts(text, speaker, raw, rate_mul)
    chain = (PHONE_CHAIN if phone else VOICE_CHAIN) + ",afade=t=in:d=0.02,areverse,afade=t=in:d=0.06,areverse"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", chain, "-ar", str(SR), "-ac", "1", out],
                   check=True)
    sig = load(out)
    # trim leading/trailing silence so timings are exact
    nz = np.where(np.abs(sig) > 0.01)[0]
    if len(nz):
        sig = sig[max(0, nz[0] - int(0.03 * SR)): nz[-1] + int(0.08 * SR)]
    # soft breath before longer phrases (sounds more human)
    if len(sig) > 1.6 * SR and not phone:
        nb = int(0.22 * SR)
        rng = np.random.default_rng(idx)
        br = np.convolve(rng.standard_normal(nb), np.ones(40) / 40, mode="same")
        br *= np.sin(np.linspace(0, np.pi, nb)) ** 2 * 0.012
        sig = np.concatenate([br, np.zeros(int(0.04 * SR)), sig])
    # per-line loudness match (RMS of voiced part)
    rms = math.sqrt(float(np.mean(sig[np.abs(sig) > 0.02] ** 2))) if np.any(np.abs(sig) > 0.02) else 0.1
    return sig * (0.18 / max(rms, 1e-4))


def build_speech(lines, dur, fps, tmp, phone_fn=None):
    """lines: (start, speaker, tts_text, subtitle[, rate_mul]).

    Returns speech track, per-speaker mouth envelopes and (start, end, speaker, subtitle) timings.
    Lines that would overlap the previous one are pushed later automatically.
    """
    n = int(dur * SR) + SR
    track = np.zeros(n)
    per = {}
    timings = []
    last_end = 0.0
    for i, line in enumerate(lines):
        start, who, text, sub = line[:4]
        rate_mul = line[4] if len(line) > 4 else 1.0
        phone = bool(phone_fn and phone_fn(start, who))
        sig = render_line(text, who, tmp, i, phone, rate_mul)
        start = max(start, last_end + 0.12)
        a = int(start * SR)
        b = min(n, a + len(sig))
        track[a:b] += sig[: b - a]
        per.setdefault(who, np.zeros(n))[a:b] += sig[: b - a]
        last_end = start + len(sig) / SR
        timings.append((start, last_end, who, sub))
    frames = int(dur * fps)
    hop = SR // fps
    envs = {}
    for k, sig in per.items():
        e = np.array([math.sqrt(float(np.mean(sig[f * hop:(f + 1) * hop] ** 2))) for f in range(frames)])
        envs[k] = e / max(1e-9, e.max())
    return track[: int(dur * SR)], envs, timings


def mix(speech, music_sfx, out_wav, tmp):
    """Duck music under the voice, then loudness-normalise the whole mix (-14 LUFS, Instagram-friendly)."""
    sp = os.path.join(tmp, "speech.wav")
    mu = os.path.join(tmp, "music.wav")
    save(sp, speech * 0.9)
    save(mu, music_sfx / max(1e-9, np.abs(music_sfx).max()) * 0.5)
    fc = ("[0:a]asplit=2[v][sc];"
          "[1:a][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=350[md];"
          "[v][md]amix=inputs=2:weights='1 0.55':normalize=0,"
          "loudnorm=I=-14:TP=-1.5:LRA=9[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", sp, "-i", mu, "-filter_complex", fc,
                    "-map", "[out]", "-ar", str(SR), "-ac", "1", out_wav], check=True)


def speaking(envs, who, t, fps=30):
    e = envs.get(who)
    if e is None:
        return False
    return e[min(len(e) - 1, int(t * fps))] > 0.12


def mouth(envs, who, t, quiet="closed", fps=30):
    """Open/closed mouth following the voice energy (smoother than a fixed toggle)."""
    e = envs.get(who)
    if e is None:
        return quiet
    v = e[min(len(e) - 1, int(t * fps))]
    if v > 0.45:
        return "open"
    if v > 0.12:
        return "open" if int(t * 12) % 2 == 0 else "closed"
    return quiet
