"""ADUZ · "Reklama degani shumi?!" · 5-qism — "Bugun divan emas, chat sotdim".

Rustam akaning ovozli monologi (RHVoice "Islom"), Shokir, xaridor va xotinining ovozi bilan.
Ishga tushirish:  python3 make_day5.py <chiqish.mp4>
Kerak: Python 3, Pillow, numpy, ffmpeg, RHVoice + o'zbek ovozlari (voice.py ga qarang).
"""
import math
import os
import subprocess
import sys
import tempfile
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import voice
from make_day2 import (BRAND, INK, NAVY, RED, SS, WHITE, YELLOW, FPS, H, W, add, bg_shop, chat_card, clamp,
                       draw_text_c, ease, ease_out_back, font, headline, hud, noise, paste_scaled, prog, push,
                       rrect, rustam, subtitle, subtitle2, thick_line, tone)

SR = voice.SR
DUR = 40.0
PART = "5-qism"

# (start_s, speaker, text_for_tts, subtitle)
LINES = [
    (0.6, "rus", "Bugun divan sotmadim. Bugun... yozishdim.", "Bugun divan sotmadim. Bugun... yozishdim."),
    (4.4, "rus", "Ishonmaysizmi? Mana, eshiting.", "Ishonmaysizmi? Mana, eshiting."),
    (8.4, "rus", "Ertalab mijoz keldi. Men unga: bir minut, dedim.",
     "Ertalab mijoz keldi. Men unga: «Bir minut», dedim."),
    (12.4, "rus", "Bir minutim... yarim soat bo'ldi.", "Bir minutim... yarim soat bo‘ldi."),
    (16.3, "xot", "Dadasi, ovqat sovib qoldi!", "(Xotini) Dadasi, ovqat sovib qoldi!"),
    (18.7, "rus", "Hozir! Admin yozyapti!", "Hozir! Admin yozyapti!"),
    (20.6, "rus", "Chekni yubordim, ko'rdingizmi? Yana yuboraymi?", "Chekni yubordim, ko‘rdingizmi? Yana yuboraymi?"),
    (24.4, "dik", "Qo'lda qilinsa, reklama o'nlab mayda ishga bo'linib ketadi. "
                  "Aduzda kanal tanlash, buyurtma va kuzatish bir joyda.",
     "Qo‘lda qilinsa, reklama o‘nlab mayda ishga bo‘linadi. ADUZ'da tanlash, buyurtma va kuzatish — bir joyda.",
     1.08),
    (32.5, "sho", "Toga! Muammo hal! Ikki yuz ming obunachisi bor kanal topdim!",
     "Toga! Muammo hal! 200 ming obunachisi bor kanal topdim!"),
    (36.6, "rus", "Ikki yuz ming?!", "200 ming?!"),
]


# ---------------------------------------------------------------- extra characters
@lru_cache(None)
def person(kind, eye=1.0, look=0, mouth="closed", brows=0, arms="down"):
    """Simple half-body sprite for the customer ('xar') and Shokir ('sho')."""
    s = SS
    im = Image.new("RGBA", (800 * s, 1000 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    S = lambda *v: tuple(int(x * s) for x in v)
    skin, skin_d = (226, 178, 140), (200, 150, 112)
    cx, cy = 400, 340
    if kind == "sho":
        body, body2 = (32, 44, 96), WHITE
    else:
        body, body2 = (60, 110, 80), (50, 92, 66)
    d.rounded_rectangle(S(170, 520, 630, 1060), radius=150 * s, fill=body)
    if kind == "sho":  # tracksuit stripes + zip
        for x in (230, 250, 550, 570):
            d.line([S(x, 600)[0:2], S(x, 1000)[0:2]], fill=body2, width=8 * s)
        d.line([S(400, 540)[0:2], S(400, 1000)[0:2]], fill=(200, 200, 210), width=5 * s)
    else:
        d.polygon([S(340, 520)[0:2], S(460, 520)[0:2], S(400, 640)[0:2]], fill=(235, 235, 235))
    d.rectangle(S(360, 460, 440, 530), fill=skin_d)
    for ex in (cx - 128, cx + 128):
        d.ellipse(S(ex - 22, cy, ex + 22, cy + 55), fill=skin_d)
    d.ellipse(S(cx - 140, cy - 170, cx + 140, cy + 30), fill=(24, 22, 24))
    d.ellipse(S(cx - 125, cy - 115, cx + 125, cy + 160), fill=skin)
    if kind == "sho":  # backwards cap
        d.chord(S(cx - 140, cy - 185, cx + 140, cy - 10), 180, 360, fill=(20, 20, 24))
        d.rounded_rectangle(S(cx - 40, cy - 120, cx + 40, cy - 92), radius=10 * s, fill=(20, 20, 24))
    else:
        d.chord(S(cx - 125, cy - 150, cx + 125, cy - 40), 180, 360, fill=(24, 22, 24))
    for sx in (-1, 1):
        ex, ey = cx + sx * 50, cy + 15
        h = 20 * eye
        d.ellipse(S(ex - 24, ey - h, ex + 24, ey + h), fill=WHITE)
        pr = min(12, 12 * eye + 2)
        d.ellipse(S(ex + look - pr, ey - pr, ex + look + pr, ey + pr), fill=(40, 28, 20))
        d.line([S(cx + sx * 22, cy - 32 - brows)[0:2], S(cx + sx * 82, cy - 38 - brows)[0:2]],
               fill=(22, 20, 20), width=12 * s)
    d.ellipse(S(cx - 16, cy + 40, cx + 16, cy + 78), fill=skin_d)
    my = cy + 112
    if mouth == "open":
        d.ellipse(S(cx - 30, my - 14, cx + 30, my + 24), fill=(110, 30, 30))
    elif mouth == "grin":
        d.chord(S(cx - 55, my - 28, cx + 55, my + 28), 0, 180, fill=WHITE, outline=(110, 30, 30), width=5 * s)
    elif mouth == "frown":
        d.arc(S(cx - 36, my, cx + 36, my + 36), 200, 340, fill=(110, 30, 30), width=7 * s)
    else:
        d.line([S(cx - 26, my + 4)[0:2], S(cx + 26, my + 4)[0:2]], fill=(110, 30, 30), width=7 * s)
    hand = lambda x, y, r=30: d.ellipse(S(x - r, y - r, x + r, y + r), fill=skin)
    if arms == "phones_up":  # Shokir: two phones in the air
        for (sx, hx) in ((230, 130), (570, 670)):
            thick_line(d, S(sx, 620)[0:2], S(hx, 420)[0:2], 74 * s, body)
            d.rounded_rectangle(S(hx - 40, 300, hx + 40, 430), radius=16 * s, fill=(40, 42, 52))
            hand(hx, 430)
    elif arms == "watch":  # customer checks his watch
        thick_line(d, S(230, 640)[0:2], S(380, 720)[0:2], 74 * s, body)
        d.rounded_rectangle(S(370, 690, 430, 740), radius=10 * s, fill=(60, 60, 70))
        hand(420, 730)
    return im.resize((800, 1000), Image.LANCZOS)


# ---------------------------------------------------------------- backgrounds
@lru_cache(None)
def bg_street():
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / 1100
        d.line([(0, y), (W, y)], fill=(int(60 + 170 * min(1, k)), int(50 + 90 * min(1, k)), int(110 + 30 * min(1, k))))
    # building facade
    d.rectangle((0, 380, W, 1500), fill=(196, 170, 140))
    d.rectangle((0, 380, W, 460), fill=(150, 120, 90))
    rrect(d, (120, 400, 960, 450), 10, fill=(40, 40, 60))
    draw_text_c(d, W / 2, 404, "RUSTAM MEBEL", font(40, "Black"), YELLOW)
    # shop window (behind shutter)
    d.rectangle((120, 520, 960, 1360), fill=(255, 220, 160))
    # pavement
    d.rectangle((0, 1500, W, H), fill=(110, 110, 118))
    for x in range(-200, W, 220):
        d.line([(x, 1500), (x + 300, H)], fill=(96, 96, 104), width=6)
    # street lamp
    d.rectangle((1010, 640, 1028, 1500), fill=(50, 50, 60))
    d.ellipse((970, 600, 1070, 670), fill=(255, 230, 150))
    return im


def shutter(img, k):
    """Metal shutter coming down over the shop window, k=0..1."""
    d = ImageDraw.Draw(img)
    bottom = 520 + (1360 - 520) * k
    d.rectangle((120, 520, 960, bottom), fill=(150, 155, 165))
    y = 520
    while y < bottom:
        d.line([(120, y), (960, y)], fill=(120, 125, 135), width=4)
        y += 34


def counter(img, y0=1560):
    d = ImageDraw.Draw(img)
    d.rectangle((0, y0, W, H), fill=(150, 98, 58))
    d.rectangle((0, y0 - 20, W, y0 + 20), fill=(120, 76, 44))
    for x in range(0, W, 180):
        d.line([(x, y0 + 40), (x, H)], fill=(136, 88, 52), width=6)


def clock_badge(d, s, x=W - 260, y=330):
    rrect(d, (x, y, x + 200, y + 80), 24, fill=(0, 0, 0, 170))
    draw_text_c(d, x + 100, y + 14, s, font(46, "Black"), WHITE)


def tally(d, t0, t, y=560):
    items = [("Xabarlar", 47), ("Ovozli", 9), ("Qo‘ng‘iroq", 6), ("Chek", 2), ("Sotilgan divan", 0)]
    rrect(d, (60, y, 520, y + 70 + 58 * len(items)), 30, fill=(0, 0, 0, 175))
    for i, (k, v) in enumerate(items):
        cur = int(v * ease(prog(t, t0 + i * 0.25, t0 + 1.6 + i * 0.25)))
        col = RED if k.startswith("Sotilgan") else YELLOW
        d.text((90, y + 30 + i * 58), k, font=font(36, "Bold"), fill=WHITE)
        tw = d.textbbox((0, 0), str(cur), font=font(42, "Black"))[2]
        d.text((490 - tw, y + 26 + i * 58), str(cur), font=font(42, "Black"), fill=col)


# ---------------------------------------------------------------- scenes
def scene1(t, envs):
    img = bg_street().copy()
    shutter(img, ease(prog(t, 0.0, 2.2)))
    spr = rustam("none", brows=4, eye=0.8, mouth=voice.mouth(envs, "rus", t, "frown"))
    paste_scaled(img, spr, W / 2, 1180, 1.12)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1640, W, H), fill=(110, 110, 118))
    headline(d, "REKLAMA UCHUN BIR KUN", y=520, size=72, pop=max(0.2, ease_out_back(prog(t, 0.3, 0.8))))
    clock_badge(d, "20:00")
    return push(img, t / 8, 1.0, 1.05)


def scene2(t, envs):
    tt = t + 8
    img = bg_shop().copy()
    # customer in the background on the left, leaves at the end
    leave = ease(prog(t, 6.0, 7.6))
    cust = person("xar", eye=0.9, look=-6 if t < 3 else 8, mouth="frown" if t > 4 else "closed",
                  arms="watch" if 3.0 < t < 5.5 else "down")
    paste_scaled(img, cust, 230 - leave * 500, 1130 + 12 * math.sin(t * 6) * (1 if 3 < t < 6 else 0), 0.8,
                 alpha=1 - leave * 0.6)
    spr = rustam("read", brows=10, eye=0.9, look=-6, mouth=voice.mouth(envs, "rus", tt))
    paste_scaled(img, spr, 660, 1100, 1.05)
    counter(img)
    d = ImageDraw.Draw(img)
    clock_badge(d, "11:00" if t < 4 else "11:30")
    if 1.6 < t < 4:
        rrect(d, (520, 560, 980, 650), 40, fill=WHITE)
        draw_text_c(d, 750, 575, "«Bir minut...»", font(44, "Black"), INK)
    return push(img, t / 8, 1.0, 1.04)


def scene3(t, envs):
    tt = t + 16
    img = bg_shop().copy()
    img.alpha_composite(Image.new("RGBA", (W, H), (60, 30, 90, 60)))  # evening
    pose = "mouth" if tt > 20.4 else "read"
    spr = rustam(pose, brows=-4 if tt < 18.6 else 16, tilt=10 if tt < 18.6 else -8, eye=0.85,
                 mouth=voice.mouth(envs, "rus", tt, "frown"))
    paste_scaled(img, spr, 640, 1090, 1.08)
    counter(img)
    d = ImageDraw.Draw(img)
    # plate of plov on the counter, steam fading
    d.ellipse((140, 1500, 420, 1590), fill=WHITE, outline=(40, 80, 170), width=6)
    d.ellipse((180, 1490, 380, 1560), fill=(214, 160, 70))
    for i in range(3):
        a = int(200 * (1 - prog(t, 0, 6)))
        if a > 10:
            x = 220 + i * 60
            y = 1440 - 30 * math.sin(t * 2 + i)
            d.arc((x - 20, y - 60, x + 20, y), 270, 90, fill=(255, 255, 255, a), width=6)
    clock_badge(d, "19:00")
    tally(d, 0.4, t)
    return img


@lru_cache(None)
def orders_mock():
    pw, ph = 760, 1240
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, pw - 1, ph - 1), 80, fill=(18, 18, 24))
    rrect(d, (22, 22, pw - 23, ph - 23), 62, fill=(244, 246, 251))
    rrect(d, (pw / 2 - 90, 40, pw / 2 + 90, 70), 15, fill=(18, 18, 24))
    d.rectangle((22, 100, pw - 23, 240), fill=BRAND)
    d.text((60, 120), "ADUZ", font=font(54, "Black"), fill=WHITE)
    d.text((60, 186), "@Targetreklammabot", font=font(30, "SemiBold"), fill=(200, 215, 245))
    d.text((60, 270), "Buyurtmalarim", font=font(42, "Black"), fill=INK)
    rows = [("1-kanal", "Joylandi", (46, 160, 90)), ("2-kanal", "Tasdiqlandi", (63, 120, 220)),
            ("3-kanal", "Kutilmoqda", (230, 160, 40))]
    for i, (name, st, col) in enumerate(rows):
        y = 360 + i * 240
        rrect(d, (44, y, pw - 45, y + 210), 28, fill=WHITE, outline=(225, 228, 238), width=3)
        d.text((74, y + 26), name, font=font(38, "Black"), fill=BRAND)
        d.text((74, y + 90), "15-oktabr · 20:00 · matn+rasm", font=font(28, "SemiBold"), fill=(100, 100, 115))
        rrect(d, (74, y + 140, 74 + 260, y + 190), 25, fill=col)
        draw_text_c(d, 74 + 130, y + 148, st, font(30, "Bold"), WHITE)
    rrect(d, (44, 1110, pw - 45, 1190), 28, fill=(225, 228, 238))
    draw_text_c(d, pw / 2, 1128, "Hammasi bir joyda", font(32, "Bold"), (90, 90, 110))
    return im


PS = 0.72


def scene4(t, envs):
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(15 + 20 * k), int(61 + 30 * k), int(145 + 40 * k)))
    k = ease_out_back(prog(t, 0.8, 1.6))
    paste_scaled(img, orders_mock(), W / 2, 900 + (1 - k) * 1400, PS)
    d = ImageDraw.Draw(img)
    # many little chat bubbles fly into the phone
    rng = np.random.default_rng(5)
    for i in range(26):
        sx, sy = rng.uniform(60, 1020), rng.uniform(280, 1500)
        p = ease(prog(t, 0.0 + i * 0.03, 1.4 + i * 0.03))
        x = sx + (W / 2 - sx) * p
        y = sy + (900 - sy) * p
        if p < 0.98:
            r = 34 * (1 - p) + 6
            d.rounded_rectangle((x - r * 1.6, y - r, x + r * 1.6, y + r), radius=int(r),
                                fill=(255, 255, 255, int(230 * (1 - p))))
    headline(d, "Hammasi bir joyda", y=300, size=74, color=WHITE)
    return img


def scene5(t, envs):
    tt = t + 32
    img = bg_shop().copy()
    enter = ease_out_back(prog(t, 0.0, 0.7))
    sho = person("sho", eye=1.15, brows=14, mouth=voice.mouth(envs, "sho", tt, "grin"), arms="phones_up")
    paste_scaled(img, sho, 1310 - enter * 500, 1130 + 20 * math.sin(t * 9) * (1 - prog(t, 0, 3)), 0.86)
    hope = tt > 36.4
    spr = rustam("none", brows=30 if hope else 10, tilt=-10 if hope else 0, eye=1.25 if hope else 1.0, look=14,
                 mouth=voice.mouth(envs, "rus", tt, "grin" if hope else "O"))
    RX, RY, RS = 290, 1120, 0.92
    paste_scaled(img, spr, RX, RY, RS)
    counter(img)
    d = ImageDraw.Draw(img)
    if hope:  # sparkle in the eyes
        for ex in (345 + 14, 455 + 14):
            x, y = RX + (ex - 400) * RS, RY + (345 - 500) * RS
            r = 10 + 6 * math.sin(t * 12)
            d.polygon([(x, y - r * 2), (x + r * 0.6, y), (x, y + r * 2), (x - r * 0.6, y)], fill=WHITE)
            d.polygon([(x - r * 2, y), (x, y + r * 0.6), (x + r * 2, y), (x, y - r * 0.6)], fill=WHITE)
    if tt >= 38.3:
        a = clamp((tt - 38.3) / 0.3)
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * a))))
        d = ImageDraw.Draw(img)
        kk = ease_out_back(prog(tt, 38.3, 38.7))
        rrect(d, (60, 760, 1020, 1110), 40, fill=(255, 255, 255, 250))
        f = font(max(8, int(50 * max(0.3, kk))), "Black")
        draw_text_c(d, W / 2, 800, "Hamma ishni telefonda", f, INK)
        draw_text_c(d, W / 2, 866, "qiladigan do‘stingizga", f, INK)
        rrect(d, (300, 975, 780, 1070), 30, fill=BRAND)
        draw_text_c(d, W / 2, 993, "YUBORING", font(50, "Black"), WHITE)
        draw_text_c(d, W / 2, 1180, "Ertaga: 200 ming obunachi... lekin...", font(44, "Bold"), YELLOW, stroke=5)
    return img


def frame(t, envs, timings):
    scenes = [scene1, scene2, scene3, scene4, scene5]
    k = min(4, int(t // 8))
    img = scenes[k](t - 8 * k, envs)
    d = ImageDraw.Draw(img)
    hud(d, PART)
    for (a, b, who, sub) in timings:
        if a - 0.05 <= t <= b + 0.3 and t < 38.3:
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
    prog_ = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)]
    t = 0.0
    while t < 38.3:
        chord = prog_[int(t / 2.4) % 4]
        step = int(round(t / 0.3)) % 8
        m = chord[[0, 1, 2, 1, 0, 2, 1, 2][step]] + 12
        add(buf, tone(note(m), 0.35, decay=9, harmonics=(1, 0.35, 0.1), vol=0.12), t)
        if step == 0:
            add(buf, tone(note(chord[0] - 12), 1.4, decay=2.2, harmonics=(1, 0.25), vol=0.16), t)
        if step in (2, 6):
            add(buf, noise(0.05, 0.05, 2) * np.exp(-60 * np.arange(int(0.05 * SR)) / SR), t)
        t += 0.3
    # shutter rattle
    n = int(2.2 * SR)
    rattle = noise(2.2, 0.25, 3) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 14 * np.arange(n) / SR)))
    add(buf, rattle * np.linspace(1, 0.3, n), 0.0)
    for at in (7.85, 15.85, 23.85, 31.85):
        add(buf, noise(0.45, 0.3, 30) * np.sin(np.linspace(0, np.pi, int(0.45 * SR))), at)
    add(buf, tone(1318.5, 0.5, decay=8, harmonics=(1, 0.3), vol=0.3), 22.6)  # message sent
    add(buf, tone(70, 0.5, decay=7, harmonics=(1, 0.5), vol=0.9), 32.0)       # door bang
    add(buf, noise(0.3, 0.4, 4) * np.exp(-12 * np.arange(int(0.3 * SR)) / SR), 32.0)
    for i, f in enumerate((2093, 2637, 3136)):                               # sparkle
        add(buf, tone(f, 0.8, decay=5, harmonics=(1,), vol=0.18), 36.9 + i * 0.07)
    add(buf, tone(70, 0.6, decay=6, harmonics=(1, 0.5), vol=0.7), 38.3)
    return buf[: int(SR * DUR)]


def main(out, preview=None):
    tmp = tempfile.mkdtemp()
    speech, envs, timings = voice.build_speech(LINES, DUR, FPS, tmp)
    for (a, b, who, sub) in timings:
        print(f"{a:5.1f}-{b:5.1f} {who}: {sub}")
    if preview:
        for ts in preview:
            frame(float(ts), envs, timings).convert("RGB").save(f"preview5_{ts}.png")
        return
    wav = os.path.join(tmp, "mix.wav")
    voice.mix(speech, music_and_sfx(), wav, tmp)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
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
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_5-kun.mp4")
