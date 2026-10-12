"""ADUZ · "Reklama degani shumi?!" · 3-qism — "30 ming obunachi, 0 buyurtma".

Dilnozaning ovozli monologi bilan animatsion rolik.
Ishga tushirish:  python3 make_day3.py <chiqish.mp4>
Kerak: Python 3, Pillow, numpy, ffmpeg, espeak-ng (o'zbek ovozi: uz).
"""
import math
import os
import subprocess
import sys
import tempfile
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from make_day2 import (BRAND, INK, RED, WHITE, YELLOW, FPS, H, W, SR, add, bg_room, chat_card, clamp,
                       dilnoza, draw_text_c, ease, ease_out_back, font, headline, hud, noise, paste_scaled,
                       piala, prog, push, rrect, subtitle, subtitle2, tone)

DUR = 40.0
PART = "3-qism"

# (start_s, speaker, text_for_tts, subtitle, espeak_speed)
LINES = [
    (0.3, "dil", "O'ttiz ming obunachi. Bugun ham birorta reklama yo'q.",
     "30 ming obunachi. Bugun ham birorta reklama yo‘q.", 145),
    (4.9, "dil", "Telefon jim. Men ham jim.", "Telefon jim. Men ham jim.", 145),
    (8.4, "dil", "Ertalab yangilik joyladim. Tushda telefonni yangiladim.",
     "Ertalab yangilik joyladim. Tushda telefonni yangiladim.", 145),
    (13.6, "dil", "Sen ham kutyapsanmi?", "Sen ham kutyapsanmi?", 145),
    (16.1, "dil", "Ana! Reklama!", "Ana! Reklama!", 145),
    (18.6, "dil", "Kerak emas!", "Kerak emas!", 150),
    (19.9, "dil", "Tanishlarga aytsangiz, ular ham bepul so'raydi-da.",
     "Tanishlarga aytsangiz, ular ham bepul so‘raydi-da.", 160),
    (24.4, "dik", "Reklama beruvchilar sizni qanday topadi? ADUZda kanalingizni qo'shasiz, ular sizni ko'radi.",
     "Reklama beruvchilar sizni qanday topadi? ADUZ'da kanalingizni qo‘shasiz — ular sizni ko‘radi.", 165),
    (33.0, "dil", "Bir minut... yana kimdir narx deb yozdi.", "Bir minut... yana kimdir «narx?» deb yozdi.", 145),
    (37.0, "dil", "Yana o'sha aka!", "Yana o‘sha aka!", 150),
]
VOICES = {"dil": ["-v", "uz+f3", "-p", "58"], "dik": ["-v", "uz+m3", "-p", "38"]}


# ---------------------------------------------------------------- speech
def synth(tmp):
    """Return mixed speech track, Dilnoza envelope per frame and line timings."""
    track = np.zeros(int(SR * DUR) + SR)
    dil = np.zeros_like(track)
    timings = []
    for i, (start, who, tts, sub, speed) in enumerate(LINES):
        raw = os.path.join(tmp, f"l{i}.wav")
        out = os.path.join(tmp, f"l{i}_44.wav")
        subprocess.run(["espeak-ng", *VOICES[who], "-s", str(speed), "-w", raw, tts], check=True)
        # soften the robotic edge: band-limit, light room, resample
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                        "highpass=f=120,lowpass=f=6500,aecho=0.8:0.6:40:0.15,volume=1.6",
                        "-ar", str(SR), "-ac", "1", out], check=True)
        with wave.open(out) as w:
            sig = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
        add(track, sig, start)
        if who == "dil":
            add(dil, sig, start)
        timings.append((start, start + len(sig) / SR, who, sub))
    n = int(DUR * FPS)
    env = np.zeros(n)
    hop = SR // FPS
    for f in range(n):
        seg = dil[f * hop:(f + 1) * hop]
        env[f] = math.sqrt(float(np.mean(seg ** 2))) if len(seg) else 0
    env = env / max(1e-9, env.max())
    return track[: int(SR * DUR)], env, timings


# ---------------------------------------------------------------- visuals
def clock_badge(d, s, x=W - 260, y=330):
    rrect(d, (x, y, x + 200, y + 80), 24, fill=(0, 0, 0, 170))
    draw_text_c(d, x + 100, y + 14, s, font(46, "Black"), WHITE)


def tint(img, color, a):
    if a <= 0:
        return img
    ov = Image.new("RGBA", (W, H), color + (int(255 * clamp(a)),))
    img.alpha_composite(ov)
    return img


def desk_front(img, phone_on_desk=False, glow=False):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1560, W, H), fill=(160, 112, 72))
    d.rectangle((0, 1560, W, 1590), fill=(130, 88, 54))
    piala(d, 220, 1560, 1.0)
    if phone_on_desk:
        rrect(d, (500, 1505, 720, 1562), 14, fill=(40, 42, 52))
        if glow:
            rrect(d, (510, 1512, 710, 1555), 10, fill=(150, 200, 255))


def dil_sprite(t, env, look=0, base_eye=1.0, brows=0, quiet_mouth="closed"):
    fi = min(len(env) - 1, int(t * FPS))
    speaking = env[fi] > 0.18
    blink = (t % 3.7) < 0.12
    eye = 0.1 if blink else base_eye
    return dilnoza(eye=eye, look=look, mouth="open" if speaking and int(t * 10) % 2 == 0 else
                   ("closed" if speaking else quiet_mouth), brows=brows)


@lru_cache(None)
def add_channel_mock():
    pw, ph = 760, 1240
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, pw - 1, ph - 1), 80, fill=(18, 18, 24))
    rrect(d, (22, 22, pw - 23, ph - 23), 62, fill=(244, 246, 251))
    rrect(d, (pw / 2 - 90, 40, pw / 2 + 90, 70), 15, fill=(18, 18, 24))
    d.rectangle((22, 100, pw - 23, 240), fill=BRAND)
    d.text((60, 120), "ADUZ", font=font(54, "Black"), fill=WHITE)
    d.text((60, 186), "@Targetreklammabot", font=font(30, "SemiBold"), fill=(200, 215, 245))
    d.text((60, 270), "Kanal qo‘shish", font=font(42, "Black"), fill=INK)
    fields = [("Kanal nomi", "Farg‘ona Bugun"), ("Hudud", "Farg‘ona"), ("Mavzu", "Yangiliklar"),
              ("Reklama narxi", "200 000 so‘m")]
    for i, (k, v) in enumerate(fields):
        y = 350 + i * 150
        d.text((60, y), k, font=font(28, "SemiBold"), fill=(110, 110, 125))
        rrect(d, (50, y + 40, pw - 50, y + 120), 20, fill=WHITE, outline=(215, 220, 232), width=3)
        d.text((80, y + 60), v, font=font(36, "Bold"), fill=INK)
    d.text((60, 955), "Bo‘sh vaqtlar", font=font(28, "SemiBold"), fill=(110, 110, 125))
    for j, s in enumerate(["10:00", "14:00", "20:00"]):
        x = 60 + j * 200
        rrect(d, (x, 995, x + 180, 1055), 30, fill=(220, 232, 252))
        draw_text_c(d, x + 90, 1006, s, font(32, "Bold"), BRAND)
    rrect(d, (50, 1090, pw - 50, 1180), 30, fill=BRAND)
    draw_text_c(d, pw / 2, 1112, "Kanalni qo‘shish", font(40, "Black"), WHITE)
    return im


def scene1(t, env):
    img = bg_room().copy()
    rise = ease(prog(t, 0.0, 0.6))
    spr = dil_sprite(t, env, base_eye=0.85, brows=-4)
    paste_scaled(img, spr, W / 2, 1130 + (1 - rise) * 120, 1.15)
    desk_front(img)
    d = ImageDraw.Draw(img)
    hud(d, PART)
    headline(d, "KANAL EGASINING BIR KUNI", y=420, size=70, pop=max(0.2, ease_out_back(prog(t, 0, 0.5))))
    rrect(d, (220, 540, 860, 620), 30, fill=(0, 0, 0, 160))
    draw_text_c(d, W / 2, 553, "30 000 obunachi · shartli misol", font(38, "Bold"), WHITE)
    return push(img, t / 8, 1.0, 1.05)


def scene2(t, env):
    img = bg_room().copy()
    stage = 0 if t < 2.6 else (1 if t < 5.2 else 2)
    look = 0 if stage < 2 else 16
    spr = dil_sprite(t, env, look=look, base_eye=0.9 if stage < 2 else 0.7,
                     quiet_mouth="smirk" if stage == 2 else "closed")
    paste_scaled(img, spr, W / 2, 1130, 1.15)
    desk_front(img)
    # afternoon light
    tint(img, (255, 170, 80), 0.12 * prog(t, 2.6, 8))
    d = ImageDraw.Draw(img)
    hud(d, PART)
    clock_badge(d, ["09:00", "12:00", "15:00"][stage])
    if stage == 1:  # refresh icon spinning
        cx, cy, r = W / 2, 560, 70
        a0 = (t * 400) % 360
        d.arc((cx - r, cy - r, cx + r, cy + r), a0, a0 + 280, fill=WHITE, width=16)
    return img


def scene3(t, env):
    img = bg_room().copy()
    jump = math.sin(prog(t, 0.0, 0.5) * math.pi) * 60
    if t < 2.4:
        spr = dil_sprite(t, env, base_eye=1.2, brows=12)
    elif t < 3.8:
        spr = dil_sprite(t, env, base_eye=0.6, brows=-6)
    else:
        spr = dil_sprite(t, env, look=-4, base_eye=0.8, brows=4, quiet_mouth="smirk")
    paste_scaled(img, spr, W / 2, 1130 - jump, 1.15)
    desk_front(img)
    d = ImageDraw.Draw(img)
    hud(d, PART)
    if t < 2.4:
        headline(d, "DING!", y=420, size=110, pop=max(0.2, ease_out_back(prog(t, 0, 0.4))))
    chat_card(img, 360, "Noma'lum", "Kanalingizga 10 000 obunachi! Arzon!", prog(t, 2.0, 2.4), (150, 150, 160), tag=False)
    if t > 2.6:  # strike the spam card
        k = prog(t, 2.6, 3.0)
        d.line([(80, 470), (80 + 920 * k, 470)], fill=RED, width=14)
    chat_card(img, 640, "Mijoz", "Opa, bepul reklama qilib berasizmi? Keyin tanishlarga aytaman",
              prog(t, 3.4, 3.8), (200, 90, 150), tag=False)
    return img


PS = 0.72


def scene4(t, env):
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(15 + 20 * k), int(61 + 30 * k), int(145 + 40 * k)))
    for i in range(6):
        r = 160 + i * 40
        cx = 540 + 380 * math.sin(t * 0.6 + i)
        cy = 400 + i * 260
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(70, 110, 190), width=3)
    k = ease_out_back(prog(t, 0.1, 0.9))
    paste_scaled(img, add_channel_mock(), W / 2, 900 + (1 - k) * 1400, PS)
    d = ImageDraw.Draw(img)
    hud(d, PART)
    headline(d, "Kanalingiz — ko‘rinadigan joyda", y=300, size=62, color=WHITE)
    # tap animation on the button
    if t > 5.2:
        bx = W / 2
        by = 900 - 1240 * PS / 2 + 1135 * PS
        r = 30 + 60 * ((t - 5.2) % 1.0)
        d.ellipse((bx - r, by - r, bx + r, by + r), outline=YELLOW, width=8)
    return img


@lru_cache(None)
def night_glow():
    from PIL import ImageFilter
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((240, 700, 840, 1300), fill=(120, 170, 255, 80))
    return glow.filter(ImageFilter.GaussianBlur(90))


def scene5(t, env):
    img = bg_room().copy()
    tint(img, (10, 16, 40), 0.62)
    if t < 1.0:
        spr = dil_sprite(t, env, base_eye=0.6)
    elif t < 5.0:
        spr = dil_sprite(t, env, base_eye=0.55, brows=-6)
    else:
        spr = dil_sprite(t, env, base_eye=1.25, brows=14, quiet_mouth="open" if t < 6.6 else "smirk")
    paste_scaled(img, spr, W / 2, 1130, 1.15)
    # phone glow on face
    img.alpha_composite(night_glow())
    desk_front(img)
    d = ImageDraw.Draw(img)
    hud(d, PART)
    clock_badge(d, "23:47")
    chat_card(img, 470, "Rustam Mebel", "Assalomu alaykum, reklama necha pul?", prog(t, 0.7, 1.1), (63, 120, 220), tag=False)
    if t >= 6.4:
        a = clamp((t - 6.4) / 0.4)
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * a))))
        d = ImageDraw.Draw(img)
        hud(d, PART)
        kk = ease_out_back(prog(t, 6.4, 6.8))
        rrect(d, (60, 760, 1020, 1110), 40, fill=(255, 255, 255, 250))
        f = font(max(8, int(50 * max(0.3, kk))), "Black")
        draw_text_c(d, W / 2, 800, "Kanal egasimisiz?", f, INK)
        draw_text_c(d, W / 2, 870, "Buyurtmani qanday topasiz?", f, INK)
        rrect(d, (280, 975, 800, 1070), 30, fill=BRAND)
        draw_text_c(d, W / 2, 993, "IZOHDA YOZING", font(48, "Black"), WHITE)
        draw_text_c(d, W / 2, 1180, "Ertaga: ular nihoyat kelishadi...", font(46, "Bold"), YELLOW, stroke=5)
    return push(img, t / 8, 1.0, 1.04)


def frame(t, env, timings):
    scenes = [scene1, scene2, scene3, scene4, scene5]
    k = min(4, int(t // 8))
    img = scenes[k](t - 8 * k, env)
    d = ImageDraw.Draw(img)
    for (a, b, who, sub) in timings:
        if a - 0.05 <= t <= b + 0.25:
            (subtitle2 if who == "dik" else subtitle)(d, sub)
    for c in (8, 16, 24, 32):
        if c - 0.05 <= t < c + 0.18:
            a = 1 - abs(t - c) / 0.18
            img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), clamp(a) * 0.8)
    return img


# ---------------------------------------------------------------- audio
def music_and_sfx():
    buf = np.zeros(int(SR * DUR) + SR)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    # soft, slightly melancholic loop, low under the voice
    prog_ = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
    t = 0.0
    while t < 32:
        chord = prog_[int(t / 2.4) % 4]
        step = int(round(t / 0.3)) % 8
        m = chord[[0, 2, 1, 2, 0, 2, 1, 2][step]] + 12
        add(buf, tone(note(m), 0.35, decay=9, vol=0.04), t)
        if step == 0:
            add(buf, tone(note(chord[0] - 12), 1.2, decay=2.5, harmonics=(1, 0.3), vol=0.05), t)
        t += 0.3
    for m, at in [(57, 32.0), (52, 34.4), (53, 36.8)]:
        for mm in (m, m + 3, m + 7):
            add(buf, tone(note(mm), 2.6, decay=0.8, harmonics=(1, 0.2), vol=0.035), at)
    for i in range(10):  # clock ticks in the hook
        add(buf, tone(3000, 0.03, decay=120, harmonics=(1,), vol=0.12), 0.2 + i * 0.8)
    ding = lambda: tone(1318.5, 0.5, decay=8, harmonics=(1, 0.3), vol=0.16) + np.pad(
        tone(1760, 0.45, decay=8, harmonics=(1,), vol=0.1), (int(0.06 * SR), 0))[: int(0.5 * SR)]
    for at in (16.0, 19.4, 32.6):
        add(buf, ding(), at)
    for at in (7.85, 15.85, 23.85, 31.85):
        add(buf, noise(0.45, 0.2, 30) * np.sin(np.linspace(0, np.pi, int(0.45 * SR))), at)
    add(buf, tone(2093, 1.5, decay=2.5, harmonics=(1, 0.2), vol=0.06), 38.4)
    return buf[: int(SR * DUR)]


def write_wav(path, sig):
    sig = sig / max(1e-9, np.abs(sig).max()) * 0.85
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())


def main(out, preview=None):
    tmp = tempfile.mkdtemp()
    speech, env, timings = synth(tmp)
    if preview:
        for ts in preview:
            frame(float(ts), env, timings).convert("RGB").save(f"preview3_{ts}.png")
        return
    for (a, b, who, sub) in timings:
        print(f"{a:5.1f}-{b:5.1f} {who}: {sub}")
    wav = os.path.join(tmp, "mix.wav")
    write_wav(wav, music_and_sfx() + speech * 1.0)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for i in range(n):
        p.stdin.write(frame(i / FPS, env, timings).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print("done", out)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        main(None, sys.argv[2:])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_3-kun.mp4")
