"""ADUZ · "Reklama degani shumi?!" · 4-qism — "Qaysi ertaga?!".

Rustam aka va Dilnozaning ovozli dialogi (bo'lingan ekran) bilan animatsion rolik.
Ishga tushirish:  python3 make_day4.py <chiqish.mp4>
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
from PIL import Image, ImageDraw, ImageFilter

from make_day2 import (BRAND, INK, RED, WHITE, YELLOW, FPS, H, W, SR, add, bg_room, bg_shop, clamp, dilnoza,
                       draw_text_c, ease, ease_out_back, font, headline, hud, noise, paste_scaled, piala, prog,
                       push, rrect, rustam, subtitle2, tone, wrap)

DUR = 40.0
PART = "4-qism"
HALF = H // 2

# (start_s, speaker, text_for_tts, subtitle, espeak_speed)
LINES = [
    (0.3, "rus", "Ertaga chiqaramiz, dedi. Bugun ertami, yo yo'q?!",
     "«Ertaga chiqaramiz» dedi. Bugun ertami, yo yo‘q?!", 145),
    (8.2, "rus", "Qani reklama?", "Qani reklama?", 145),
    (9.8, "dil", "Kechqurun chiqadi.", "Kechqurun chiqadi.", 145),
    (11.7, "rus", "Kechqurun do'kon yopiq-ku!", "Kechqurun do‘kon yopiq-ku!", 150),
    (14.1, "dil", "Post matni qani, aka?", "Post matni qani, aka?", 150),
    (16.5, "rus", "Beshta rasm yubordim-ku!", "Beshta rasm, ikkita ovozli xabar yubordim-ku!", 150),
    (18.8, "dil", "Bir soat tepada, keyin lentada.", "Bir soat tepada, keyin lentada.", 155),
    (21.75, "rus", "Lentaga?! Atlasmi?!", "Lentaga?! Qanaqa lenta? Atlasmi?", 145),
    (24.3, "dik", "Sana, soat, format, muddat va to'lov oldindan aniq bo'lsin. ADUZda bular buyurtmada belgilanadi.",
     "Sana, soat, format, muddat va to‘lov oldindan aniq bo‘lsin. ADUZ'da bular buyurtmada belgilanadi.", 165),
    (32.2, "dil", "Bo'ldi. Ertaga, soat yigirmada.", "Bo‘ldi. Ertaga, soat 20:00 da.", 165),
    (35.3, "rus", "Qaysi ertaga?", "Qaysi ertaga?", 140),
    (37.0, "dil", "Aka!", "...Aka!!!", 140),
]
VOICES = {"rus": ["-v", "uz+m1", "-p", "30"], "dil": ["-v", "uz+f3", "-p", "58"],
          "dik": ["-v", "uz+m3", "-p", "42"]}


# ---------------------------------------------------------------- speech
def synth(tmp):
    track = np.zeros(int(SR * DUR) + SR)
    per = {k: np.zeros_like(track) for k in VOICES}
    timings = []
    for i, (start, who, tts, sub, speed) in enumerate(LINES):
        raw = os.path.join(tmp, f"l{i}.wav")
        out = os.path.join(tmp, f"l{i}_44.wav")
        subprocess.run(["espeak-ng", *VOICES[who], "-s", str(speed), "-w", raw, tts], check=True)
        af = "highpass=f=110,lowpass=f=6500,aecho=0.8:0.6:40:0.15,volume=1.6"
        if who in ("rus", "dil"):  # phone-call colour during the split-screen call
            if 8 <= start < 24 or start >= 32:
                af = "highpass=f=300,lowpass=f=3400,volume=2.2"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af,
                        "-ar", str(SR), "-ac", "1", out], check=True)
        with wave.open(out) as w:
            sig = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
        add(track, sig, start)
        add(per[who], sig, start)
        timings.append((start, start + len(sig) / SR, who, sub))
    n = int(DUR * FPS)
    hop = SR // FPS
    envs = {}
    for k, sig in per.items():
        e = np.array([math.sqrt(float(np.mean(sig[f * hop:(f + 1) * hop] ** 2))) for f in range(n)])
        envs[k] = e / max(1e-9, e.max())
    return track[: int(SR * DUR)], envs, timings


def speaking(envs, who, t):
    e = envs[who]
    return e[min(len(e) - 1, int(t * FPS))] > 0.15


def mouth_of(envs, who, t, quiet="closed"):
    if speaking(envs, who, t):
        return "open" if int(t * 10) % 2 == 0 else "closed"
    return quiet


# ---------------------------------------------------------------- halves
@lru_cache(None)
def half_bg(which):
    src = bg_shop() if which == "shop" else bg_room()
    img = src.crop((0, 470, W, 470 + HALF)).copy()
    if which == "shop":  # hide the sale sign so the top bar stays readable
        d = ImageDraw.Draw(img)
        d.rectangle((50, 160, 350, 310), fill=img.getpixel((500, 235)))
    return img


def counter_half(img):
    d = ImageDraw.Draw(img)
    d.rectangle((0, HALF - 120, W, HALF), fill=(150, 98, 58))
    d.rectangle((0, HALF - 130, W, HALF - 110), fill=(120, 76, 44))


def desk_half(img):
    d = ImageDraw.Draw(img)
    d.rectangle((0, HALF - 120, W, HALF), fill=(160, 112, 72))
    d.rectangle((0, HALF - 130, W, HALF - 110), fill=(130, 88, 54))
    piala(d, 190, HALF - 125, 0.8)


def thought(d, cx, cy, s, color=WHITE):
    for (dx, dy, r) in [(-115, 0, 56), (-45, -24, 72), (45, -24, 72), (115, 0, 56), (0, 24, 64)]:
        d.ellipse((cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r), fill=color)
    d.ellipse((cx - 170, cy + 70, cx - 146, cy + 94), fill=color)
    d.ellipse((cx - 196, cy + 104, cx - 182, cy + 118), fill=color)
    draw_text_c(d, cx, cy - 20, s, font(36, "Black"), INK)


def rustam_half(t, envs, pose="mouth", expr="normal", morning=False):
    img = half_bg("shop").copy()
    talk = mouth_of(envs, "rus", t, quiet="grin" if expr == "happy" else "closed")
    params = {"normal": dict(brows=6, eye=1.0), "happy": dict(brows=14, eye=0.9),
              "angry": dict(brows=-8, tilt=14, eye=0.8), "confused": dict(brows=30, tilt=-10, eye=1.2, look=-6),
              "innocent": dict(brows=22, tilt=-12, eye=1.15)}[expr]
    if expr == "confused" and not speaking(envs, "rus", t):
        talk = "O"
    spr = rustam(pose, mouth=talk, **params)
    paste_scaled(img, spr, W / 2, 600, 0.85)
    counter_half(img)
    if morning:
        img.alpha_composite(Image.new("RGBA", img.size, (150, 190, 255, 40)))
    return img


def dil_half(t, envs, expr="normal"):
    img = half_bg("room").copy()
    params = {"normal": dict(eye=0.95), "happy": dict(eye=0.85, brows=6), "patient": dict(eye=0.55, brows=-4),
              "shock": dict(eye=1.25, brows=14), "done": dict(eye=0.3, brows=-8)}[expr]
    blink = (t % 3.3) < 0.1
    if blink:
        params = dict(params, eye=0.1)
    quiet = "smirk" if expr == "happy" else ("open" if expr == "shock" else "closed")
    spr = dilnoza(mouth=mouth_of(envs, "dil", t, quiet=quiet), **params)
    paste_scaled(img, spr, W / 2, 590, 0.85)
    desk_half(img)
    return img


def split(top, bot, t, envs, call=True):
    img = Image.new("RGBA", (W, H))
    # dim the half that is not speaking during a call
    if call:
        r, dl = speaking(envs, "rus", t), speaking(envs, "dil", t)
        if dl and not r:
            top.alpha_composite(Image.new("RGBA", top.size, (0, 0, 0, 70)))
        if r and not dl:
            bot.alpha_composite(Image.new("RGBA", bot.size, (0, 0, 0, 70)))
    img.alpha_composite(top, (0, 0))
    img.alpha_composite(bot, (0, HALF))
    d = ImageDraw.Draw(img)
    d.rectangle((0, HALF - 6, W, HALF + 6), fill=WHITE)
    if call:
        rrect(d, (W / 2 - 150, HALF - 34, W / 2 + 150, HALF + 34), 34, fill=(46, 160, 90))
        sec = int(t)
        draw_text_c(d, W / 2, HALF - 22, f"Qo‘ng‘iroq 0:{sec % 60:02d}", font(34, "Bold"), WHITE)
    return img


def sub_at(d, who, s):
    """Subtitle near the speaker: Rustam in the upper half, Dilnoza in the lower half."""
    f = font(56)
    lines = wrap(d, s, f, 960)
    y = (HALF - 250 if who == "rus" else 1440) - (len(lines) - 1) * 70
    for ln in lines:
        draw_text_c(d, W / 2, y, ln, f, WHITE, stroke=7)
        y += 70


# ---------------------------------------------------------------- scenes
def scene1(t, envs):
    if t < 5:
        img = bg_shop().copy()
        img.alpha_composite(Image.new("RGBA", (W, H), (150, 190, 255, 40)))
        spr = rustam("read", brows=20, tilt=-8, eye=1.1, mouth=mouth_of(envs, "rus", t, "frown"))
        paste_scaled(img, spr, W / 2, 1080, 1.15)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 1560, W, H), fill=(150, 98, 58))
        d.rectangle((0, 1540, W, 1580), fill=(120, 76, 44))
        headline(d, "QAYSI ERTAGA?!", y=420, size=104, pop=max(0.2, ease_out_back(prog(t, 0, 0.5))))
        rrect(d, (W - 260, 560, W - 60, 640), 24, fill=(0, 0, 0, 170))
        draw_text_c(d, W - 160, 574, "09:00", font(46, "Black"), WHITE)
        return push(img, t / 5, 1.0, 1.04)
    # flashback: yesterday's chat, both smiling with different ideas
    top = rustam_half(t, envs, pose="read", expr="happy")
    bot = dil_half(t, envs, expr="happy")
    img = split(top, bot, t, envs, call=False)
    img.alpha_composite(Image.new("RGBA", (W, H), (255, 230, 180, 35)))
    d = ImageDraw.Draw(img)
    rrect(d, (40, HALF - 60, 300, HALF + 0), 20, fill=(0, 0, 0, 170))
    draw_text_c(d, 170, HALF - 50, "KECHA", font(38, "Black"), YELLOW)
    k1 = ease_out_back(prog(t, 5.5, 5.9))
    k2 = ease_out_back(prog(t, 6.5, 6.9))
    if k1 > 0:
        thought(d, 880, 400 + (1 - k1) * 60, "ertalab 08:00")
    if k2 > 0:
        thought(d, 880, HALF + 330 + (1 - k2) * 60, "kechqurun 20:00")
    # chat recap
    rrect(d, (60, 660, 600, 740), 30, fill=(255, 255, 255, 235))
    d.text((90, 676), "«Ertaga chiqaring.»", font=font(38, "Bold"), fill=INK)
    rrect(d, (60, HALF + 640, 600, HALF + 720), 30, fill=(220, 240, 255, 235))
    d.text((90, HALF + 656), "«Xo‘p, ertaga.»", font=font(38, "Bold"), fill=INK)
    return img


def scene2(t, envs):
    tt = t + 8
    expr_r = "angry" if tt > 11.6 else "normal"
    expr_d = "patient" if tt > 11.6 else "normal"
    return split(rustam_half(tt, envs, expr=expr_r), dil_half(tt, envs, expr=expr_d), tt, envs)


def scene3(t, envs):
    tt = t + 16
    expr_r = "confused" if tt > 21.75 else "normal"
    expr_d = "shock" if tt > 22.7 else "patient"
    img = split(rustam_half(tt, envs, expr=expr_r), dil_half(tt, envs, expr=expr_d), tt, envs)
    d = ImageDraw.Draw(img)
    if 16.5 < tt < 18.8:  # attachments he sent
        for i in range(5):
            x = 40 + (i % 2) * 90
            y = 330 + (i // 2) * 90
            rrect(d, (x, y, x + 80, y + 80), 12, fill=(200, 210, 230), outline=WHITE, width=4)
        for i in range(2):
            rrect(d, (760, 340 + i * 70, 1040, 395 + i * 70), 28, fill=(63, 120, 220))
            draw_text_c(d, 900, 350 + i * 70, "0:47", font(32, "Bold"), WHITE)
    if tt > 21.75:
        k = ease_out_back(prog(tt, 21.75, 22.15))
        f = font(max(8, int(96 * k)), "Black")
        draw_text_c(d, 860, 360, "LENTA?!", f, YELLOW, stroke=9)
    return img


@lru_cache(None)
def order_mock():
    pw, ph = 760, 1240
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, pw - 1, ph - 1), 80, fill=(18, 18, 24))
    rrect(d, (22, 22, pw - 23, ph - 23), 62, fill=(244, 246, 251))
    rrect(d, (pw / 2 - 90, 40, pw / 2 + 90, 70), 15, fill=(18, 18, 24))
    d.rectangle((22, 100, pw - 23, 240), fill=BRAND)
    d.text((60, 120), "ADUZ", font=font(54, "Black"), fill=WHITE)
    d.text((60, 186), "@Targetreklammabot", font=font(30, "SemiBold"), fill=(200, 215, 245))
    d.text((60, 270), "Reklama buyurtmasi", font=font(42, "Black"), fill=INK)
    fields = [("Sana", "15-oktabr"), ("Soat", "20:00"), ("Format", "Matn + 3 ta rasm"),
              ("Tepada turish", "1 soat"), ("To‘lov", "200 000 so‘m")]
    for i, (k, v) in enumerate(fields):
        y = 350 + i * 140
        d.text((60, y), k, font=font(28, "SemiBold"), fill=(110, 110, 125))
        rrect(d, (50, y + 38, pw - 50, y + 112), 20, fill=WHITE, outline=(215, 220, 232), width=3)
        d.text((80, y + 55), v, font=font(34, "Bold"), fill=INK)
    rrect(d, (50, 1090, pw - 50, 1180), 30, fill=BRAND)
    draw_text_c(d, pw / 2, 1112, "Buyurtma berish", font(40, "Black"), WHITE)
    return im


PS = 0.72


def scene4(t, envs):
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
    paste_scaled(img, order_mock(), W / 2, 900 + (1 - k) * 1400, PS)
    d = ImageDraw.Draw(img)
    hud(d, PART)
    headline(d, "5 narsa aniq bo‘lsin", y=300, size=74, color=WHITE)
    # tick each field as it is mentioned
    top = 900 - 1240 * PS / 2
    for i in range(5):
        if t > 0.9 + i * 0.55:
            y = top + (350 + i * 140 + 75) * PS
            x = W / 2 + 760 * PS / 2 - 80
            kk = ease_out_back(prog(t, 0.9 + i * 0.55, 1.2 + i * 0.55))
            r = 26 * kk
            d.ellipse((x - r, y - r, x + r, y + r), fill=(46, 160, 90))
            if kk > 0.6:
                d.line([(x - 12, y), (x - 3, y + 10), (x + 14, y - 10)], fill=WHITE, width=6)
    return img


def scene5(t, envs):
    tt = t + 32
    expr_d = "done" if tt > 36.95 else "patient"
    expr_r = "innocent" if tt > 35.2 else "normal"
    freeze_t = min(tt, 38.1)
    img = split(rustam_half(freeze_t, envs, expr=expr_r), dil_half(freeze_t, envs, expr=expr_d), freeze_t, envs)
    if tt >= 38.1:
        a = clamp((tt - 38.1) / 0.4)
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * a))))
        d = ImageDraw.Draw(img)
        kk = ease_out_back(prog(tt, 38.1, 38.5))
        rrect(d, (60, 760, 1020, 1110), 40, fill=(255, 255, 255, 250))
        f = font(max(8, int(48 * max(0.3, kk))), "Black")
        draw_text_c(d, W / 2, 800, "Sizda ham shunday", f, INK)
        draw_text_c(d, W / 2, 866, "tushunmovchilik bo‘lganmi?", f, INK)
        rrect(d, (280, 975, 800, 1070), 30, fill=BRAND)
        draw_text_c(d, W / 2, 993, "IZOHDA YOZING", font(48, "Black"), WHITE)
        draw_text_c(d, W / 2, 1180, "Ertaga: bu Rustam akaga qanchaga tushdi?", font(42, "Bold"), YELLOW, stroke=5)
    return img


def frame(t, envs, timings):
    scenes = [scene1, scene2, scene3, scene4, scene5]
    k = min(4, int(t // 8))
    img = scenes[k](t - 8 * k, envs)
    d = ImageDraw.Draw(img)
    hud(d, PART)
    for (a, b, who, sub) in timings:
        if a - 0.05 <= t <= b + 0.25 and t < 38.1:
            if who == "dik":
                subtitle2(d, sub)
            elif t < 5:
                sub_at(d, "dil", sub)  # full-frame hook: subtitle low
            else:
                sub_at(d, who, sub)
    for c in (8, 16, 24, 32):
        if c - 0.05 <= t < c + 0.18:
            a = 1 - abs(t - c) / 0.18
            img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), clamp(a) * 0.8)
    return img


# ---------------------------------------------------------------- audio
def music_and_sfx():
    buf = np.zeros(int(SR * DUR) + SR)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    prog_ = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)]
    t = 0.0
    while t < 38.1:
        chord = prog_[int(t / 2.4) % 4]
        step = int(round(t / 0.3)) % 8
        m = chord[[0, 1, 2, 1, 0, 2, 1, 2][step]] + 12
        add(buf, tone(note(m), 0.35, decay=9, vol=0.035), t)
        if step == 0:
            add(buf, tone(note(chord[0] - 12), 1.2, decay=2.5, harmonics=(1, 0.3), vol=0.045), t)
        t += 0.3
    # rooster far away in the hook
    tt = np.arange(int(0.9 * SR)) / SR
    f0 = 700 + 500 * np.sin(np.pi * tt / 0.9)
    add(buf, 0.08 * np.sin(2 * np.pi * np.cumsum(f0) / SR) * np.sin(np.pi * tt / 0.9), 3.0)
    # phone ringing before the call
    for at in (7.4, 7.9):
        add(buf, tone(880, 0.3, decay=3, harmonics=(1, 0.5), vol=0.08), at)
    for at in (4.95, 23.85, 31.85):
        add(buf, noise(0.45, 0.2, 30) * np.sin(np.linspace(0, np.pi, int(0.45 * SR))), at)
    add(buf, tone(330, 0.3, decay=4, harmonics=(1,), vol=0.15), 22.0)  # "boing" under LENTA
    add(buf, tone(220, 0.3, decay=4, harmonics=(1,), vol=0.12), 22.15)
    add(buf, tone(70, 0.6, decay=6, harmonics=(1, 0.5), vol=0.35), 38.1)
    add(buf, tone(2093, 1.5, decay=2.5, harmonics=(1, 0.2), vol=0.05), 38.6)
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
    speech, envs, timings = synth(tmp)
    for (a, b, who, sub) in timings:
        print(f"{a:5.1f}-{b:5.1f} {who}: {sub}")
    if preview:
        for ts in preview:
            frame(float(ts), envs, timings).convert("RGB").save(f"preview4_{ts}.png")
        return
    wav = os.path.join(tmp, "mix.wav")
    write_wav(wav, music_and_sfx() + speech)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(i / FPS, envs, timings).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print("done", out)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        main(None, sys.argv[2:])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_4-kun.mp4")
