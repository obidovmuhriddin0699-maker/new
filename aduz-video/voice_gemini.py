#!/usr/bin/env python3
"""Instagram Reels'ga Gemini TTS diktor ovozini qo'shish.

  GEMINI_API_KEY=... python3 -I voice_gemini.py 7 8 9      # tanlangan qismlar
  GEMINI_API_KEY=... python3 -I voice_gemini.py all        # diktor.json dagi hammasi
  python3 -I voice_gemini.py --test 7                       # kalitsiz: ovoz o'rniga signal, faqat mikshni tekshirish

Matn: instagram/diktor.json ([boshlanish_s, maksimal_s, matn] bo'laklari).
Natija: instagram/ovozli/ADUZ_N-qism_reels.mp4 (video o'zgarmaydi, musiqa diktor ostida pasayadi).
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
IG = os.path.join(HERE, "instagram")
OUT = os.path.join(IG, "ovozli")
MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
VOICE = os.environ.get("GEMINI_TTS_VOICE", "Charon")
STYLE = (
    "O'zbek tilida, reklama diktori ovozida gapir: ishonchli, jonli, biroz tez, "
    "har jumla aniq. Matnni o'zgartirmasdan o'qi:\n"
)
RATE = 24000  # Gemini TTS: 24 kHz, 16-bit, mono PCM


def tts(text, path):
    key = os.environ["GEMINI_API_KEY"]
    body = {
        "contents": [{"parts": [{"text": STYLE + text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}},
        },
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm)


def test_tone(text, path):
    # Kalitsiz sinov: matn uzunligiga mos signal (~14 belgi/soniya).
    dur = max(1.0, len(text) / 14)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    f"sine=frequency=220:duration={dur:.2f}:sample_rate={RATE}", "-ac", "1", path], check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def fit(src, dst, max_s):
    """Bo'lak sig'masa 1.25x gacha tezlashtiradi; baribir sig'masa ogohlantiradi."""
    d = duration(src)
    tempo = 1.0
    if d > max_s:
        tempo = min(d / max_s, 1.25)
        if d / tempo > max_s + 0.05:
            print(f"  ! {os.path.basename(src)}: {d:.1f}s, {max_s}s ga sig'maydi — matnni qisqartiring")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                    f"atempo={tempo:.3f},aresample=48000", "-ac", "2", dst], check=True)
    return d / tempo


def build(n, segments, test):
    src = os.path.join(IG, f"ADUZ_{n}-qism_reels.mp4")
    dst = os.path.join(OUT, f"ADUZ_{n}-qism_reels.mp4")
    with tempfile.TemporaryDirectory() as tmp:
        inputs, delays = [], []
        for i, (start, max_s, text) in enumerate(segments):
            raw, fitted = os.path.join(tmp, f"r{i}.wav"), os.path.join(tmp, f"f{i}.wav")
            (test_tone if test else tts)(text, raw)
            d = fit(raw, fitted, max_s)
            print(f"  {n}-qism [{start:>5.1f}s] {d:4.1f}s  {text}")
            inputs += ["-i", fitted]
            delays.append(int(start * 1000))
        k = len(segments)
        parts = "".join(f"[{i + 1}:a]adelay={ms}|{ms}[v{i}];" for i, ms in enumerate(delays))
        mix = "".join(f"[v{i}]" for i in range(k))
        graph = (
            parts
            + f"{mix}amix=inputs={k}:normalize=0,volume=1.6,asplit=2[voice][key];"
            # Diktor gapirganda musiqa ~10 dB pasayadi.
            + "[0:a][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[bed];"
            + "[bed][voice]amix=inputs=2:normalize=0,"
            + "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.8:level=false[a]"
        )
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, *inputs, "-filter_complex", graph,
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                        "-ar", "48000", "-movflags", "+faststart", "-t", "32", dst], check=True)
    print(f"  -> {os.path.relpath(dst, HERE)}")


def main():
    args = sys.argv[1:]
    test = "--test" in args
    args = [a for a in args if a != "--test"]
    script = json.load(open(os.path.join(IG, "diktor.json"), encoding="utf-8"))
    eps = [k for k in script if not k.startswith("_")] if args == ["all"] else args
    if not eps:
        sys.exit(__doc__)
    if not test and not os.environ.get("GEMINI_API_KEY"):
        sys.exit("GEMINI_API_KEY topilmadi (muhit sozlamalarida qo'shing yoki --test bilan sinang).")
    os.makedirs(OUT, exist_ok=True)
    for n in eps:
        build(n, script[n], test)


if __name__ == "__main__":
    main()
