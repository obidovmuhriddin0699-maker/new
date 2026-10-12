"""ADUZ · "Reklama degani shumi?!" · 2-qism — animatsion rolik generatori.

Ishga tushirish:  python3 make_day2.py <chiqish.mp4>
Kerak: Python 3, Pillow, numpy, ffmpeg.

Video 1080x1920, 30 fps, 40 s: 5 ta kadr x 8 s (Google Flow ssenariysi bo'yicha).
Qahramonlar va fonlar oddiy vektor shakllardan chiziladi; ovoz — musiqa va effektlar
(dialog subtitr ko'rinishida). Bot ekrani — illyustratsiya, haqiqiy ekran yozuvi bilan
almashtirish tavsiya etiladi.
"""
import math
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 40.0
FONT_DIR = "/usr/share/fonts/opentype/inter/"


@lru_cache(None)
def font(size, weight="ExtraBold"):
    return ImageFont.truetype(FONT_DIR + f"Inter-{weight}.otf", size)


# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x):
    x = clamp(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def prog(t, a, b):
    return clamp((t - a) / (b - a))


def talking(t, speaking):
    """Mouth open/closed toggle while speaking."""
    return speaking and (int(t * 9) % 2 == 0)


def text_size(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0], b[3] - b[1]


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if text_size(d, test, f)[0] <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_text_c(d, cx, y, s, f, fill, stroke=0, stroke_fill=(0, 0, 0)):
    tw, th = text_size(d, s, f)
    d.text((cx - tw / 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return th


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def thick_line(d, p1, p2, w_, fill):
    d.line([p1, p2], fill=fill, width=w_)
    r = w_ / 2
    for p in (p1, p2):
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)


def paste_scaled(base, img, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.LANCZOS)
    if alpha < 1.0:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img = img.copy()
        img.putalpha(a)
    base.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


# ---------------------------------------------------------------- palette
NAVY = (31, 45, 92)
BRAND = (15, 61, 145)
YELLOW = (255, 200, 61)
RED = (229, 72, 77)
WHITE = (255, 255, 255)
INK = (24, 24, 30)

# ---------------------------------------------------------------- characters
SS = 2  # supersampling for sprites


@lru_cache(None)
def rustam(pose="none", brows=0, tilt=0, eye=1.0, look=0, mouth="closed"):
    """Half-body sprite of Rustam aka. Coordinates in 1x units (800x1000)."""
    s = SS
    im = Image.new("RGBA", (800 * s, 1000 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    S = lambda *v: tuple(int(x * s) for x in v)
    skin, skin_d = (224, 172, 130), (196, 140, 102)
    cx, cy = 400, 330

    # body
    d.rounded_rectangle(S(150, 520, 650, 1060), radius=150 * s, fill=NAVY)
    d.polygon([S(330, 520)[0:2], S(470, 520)[0:2], S(400, 690)[0:2]], fill=(245, 245, 245))
    d.polygon([S(330, 520)[0:2], S(400, 690)[0:2], S(300, 640)[0:2]], fill=(24, 35, 74))
    d.polygon([S(470, 520)[0:2], S(400, 690)[0:2], S(500, 640)[0:2]], fill=(24, 35, 74))
    d.rectangle(S(355, 460, 445, 540), fill=skin_d)
    # ears
    for ex in (cx - 142, cx + 142):
        d.ellipse(S(ex - 26, cy - 10, ex + 26, cy + 60), fill=skin_d)
    # hair + grey temples
    d.ellipse(S(cx - 150, cy - 190, cx + 150, cy + 40), fill=(28, 28, 32))
    for gx in (cx - 140, cx + 140):
        d.ellipse(S(gx - 18, cy - 40, gx + 18, cy + 20), fill=(150, 150, 156))
    # face
    d.ellipse(S(cx - 135, cy - 120, cx + 135, cy + 170), fill=skin)
    d.chord(S(cx - 135, cy - 150, cx + 135, cy - 30), 180, 360, fill=(28, 28, 32))
    # eyes
    for sx in (-1, 1):
        ex, ey = cx + sx * 55, cy + 15
        h = 22 * eye
        d.ellipse(S(ex - 26, ey - h, ex + 26, ey + h), fill=WHITE)
        pr = min(13, 13 * eye + 2)
        d.ellipse(S(ex + look - pr, ey - pr, ex + look + pr, ey + pr), fill=(40, 28, 20))
        # brows (tilt>0: angry inner-down, tilt<0: worried inner-up)
        inner = (cx + sx * 22, cy - 40 - brows + tilt)
        outer = (cx + sx * 92, cy - 46 - brows - tilt * 0.4)
        d.line([S(*inner)[0:2], S(*outer)[0:2]], fill=(22, 20, 20), width=16 * s)
    # nose
    d.ellipse(S(cx - 20, cy + 35, cx + 20, cy + 80), fill=skin_d)
    # mouth (under mustache)
    my = cy + 118
    if mouth == "open":
        d.ellipse(S(cx - 34, my - 14, cx + 34, my + 26), fill=(110, 30, 30))
    elif mouth == "O":
        d.ellipse(S(cx - 22, my - 16, cx + 22, my + 34), fill=(110, 30, 30))
    elif mouth == "grin":
        d.chord(S(cx - 60, my - 30, cx + 60, my + 30), 0, 180, fill=WHITE, outline=(110, 30, 30), width=5 * s)
    elif mouth == "frown":
        d.arc(S(cx - 40, my, cx + 40, my + 40), 200, 340, fill=(110, 30, 30), width=7 * s)
    else:
        d.line([S(cx - 30, my + 6)[0:2], S(cx + 30, my + 6)[0:2]], fill=(110, 30, 30), width=7 * s)
    # mustache
    d.rounded_rectangle(S(cx - 80, cy + 78, cx + 80, cy + 112), radius=18 * s, fill=(20, 18, 18))

    # arms / props
    hand = lambda x, y, r=32: d.ellipse(S(x - r, y - r, x + r, y + r), fill=skin)
    if pose == "show":  # phone toward camera
        thick_line(d, S(230, 620)[0:2], S(300, 790)[0:2], 80 * s, NAVY)
        thick_line(d, S(570, 620)[0:2], S(470, 800)[0:2], 80 * s, NAVY)
        d.rounded_rectangle(S(270, 600, 530, 960), radius=34 * s, fill=(20, 20, 26))
        d.rounded_rectangle(S(284, 618, 516, 942), radius=24 * s, fill=(236, 240, 247))
        for i, c in enumerate([(120, 170, 240), (200, 200, 210), (120, 170, 240)]):
            y0 = 650 + i * 92
            d.rounded_rectangle(S(300 if i % 2 == 0 else 340, y0, 460 if i % 2 == 0 else 500, y0 + 64),
                                radius=20 * s, fill=c)
        hand(290, 820)
        hand(510, 820)
    elif pose == "read":  # phone in front of chest, back to camera
        thick_line(d, S(220, 640)[0:2], S(350, 790)[0:2], 80 * s, NAVY)
        thick_line(d, S(580, 640)[0:2], S(450, 790)[0:2], 80 * s, NAVY)
        d.rounded_rectangle(S(330, 640, 470, 860), radius=26 * s, fill=(40, 42, 52))
        d.ellipse(S(350, 660, 372, 682), fill=(15, 15, 18))
        hand(345, 800)
        hand(455, 800)
    elif pose == "mouth":  # recording voice message
        thick_line(d, S(590, 640)[0:2], S(590, 560)[0:2], 80 * s, NAVY)
        d.rounded_rectangle(S(530, 400, 640, 580), radius=22 * s, fill=(40, 42, 52))
        hand(585, 580)
        thick_line(d, S(220, 640)[0:2], S(150, 520)[0:2], 76 * s, NAVY)
        hand(140, 500, 36)
    elif pose == "despair":
        thick_line(d, S(220, 640)[0:2], S(120, 470)[0:2], 76 * s, NAVY)
        thick_line(d, S(580, 640)[0:2], S(680, 470)[0:2], 76 * s, NAVY)
        hand(112, 452, 36)
        hand(688, 452, 36)
    return im.resize((800, 1000), Image.LANCZOS)


@lru_cache(None)
def dilnoza(eye=1.0, look=0, mouth="closed", brows=0):
    s = SS
    im = Image.new("RGBA", (800 * s, 1000 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    S = lambda *v: tuple(int(x * s) for x in v)
    skin, skin_d = (233, 188, 152), (210, 160, 126)
    hair = (26, 22, 26)
    cx, cy = 400, 340
    # bun behind
    d.ellipse(S(cx + 70, cy + 40, cx + 190, cy + 160), fill=hair)
    # body: beige sweater
    d.rounded_rectangle(S(160, 520, 640, 1060), radius=160 * s, fill=(222, 200, 170))
    for i in range(6):
        x = 200 + i * 80
        d.line([S(x, 600)[0:2], S(x, 1000)[0:2]], fill=(208, 186, 156), width=6 * s)
    d.rounded_rectangle(S(320, 500, 480, 560), radius=26 * s, fill=(208, 186, 156))
    d.rectangle(S(360, 450, 440, 520), fill=skin_d)
    # headphones around neck
    d.arc(S(290, 470, 510, 640), 0, 180, fill=(245, 245, 245), width=20 * s)
    d.ellipse(S(268, 520, 330, 600), fill=(245, 245, 245))
    d.ellipse(S(470, 520, 532, 600), fill=(245, 245, 245))
    # hair back
    d.ellipse(S(cx - 150, cy - 185, cx + 150, cy + 120), fill=hair)
    # face
    d.ellipse(S(cx - 125, cy - 125, cx + 125, cy + 160), fill=skin)
    # fringe / parting
    d.chord(S(cx - 140, cy - 175, cx + 20, cy - 10), 180, 360, fill=hair)
    d.chord(S(cx - 20, cy - 175, cx + 140, cy - 20), 180, 360, fill=hair)
    for ex in (cx - 125, cx + 125):
        d.ellipse(S(ex - 18, cy + 5, ex + 18, cy + 60), fill=skin_d)
    # eyes
    for sx in (-1, 1):
        ex, ey = cx + sx * 50, cy + 20
        h = 18 * eye
        d.ellipse(S(ex - 22, ey - h, ex + 22, ey + h), fill=WHITE)
        pr = min(11, 11 * eye + 2)
        d.ellipse(S(ex + look - pr, ey - pr, ex + look + pr, ey + pr), fill=(35, 24, 18))
        # lashes when half-closed
        if eye < 0.7:
            d.line([S(ex - 24, ey - h)[0:2], S(ex + 24, ey - h)[0:2]], fill=(30, 20, 20), width=5 * s)
        d.line([S(cx + sx * 25, cy - 34 - brows)[0:2], S(cx + sx * 80, cy - 26 - brows)[0:2]],
               fill=(30, 24, 24), width=9 * s)
        # glasses
        d.rounded_rectangle(S(ex - 46, ey - 34, ex + 46, ey + 34), radius=16 * s, outline=(15, 15, 18), width=7 * s)
    d.line([S(cx - 4, cy + 16)[0:2], S(cx + 4, cy + 16)[0:2]], fill=(15, 15, 18), width=7 * s)
    d.line([S(cx - 96, cy + 10)[0:2], S(cx - 125, cy + 5)[0:2]], fill=(15, 15, 18), width=6 * s)
    d.line([S(cx + 96, cy + 10)[0:2], S(cx + 125, cy + 5)[0:2]], fill=(15, 15, 18), width=6 * s)
    # nose, mouth
    d.arc(S(cx - 14, cy + 50, cx + 14, cy + 80), 20, 160, fill=skin_d, width=6 * s)
    my = cy + 110
    lip = (178, 80, 84)
    if mouth == "open":
        d.ellipse(S(cx - 24, my - 10, cx + 24, my + 20), fill=(120, 40, 44))
    elif mouth == "smirk":
        d.arc(S(cx - 30, my - 20, cx + 40, my + 14), 20, 150, fill=lip, width=7 * s)
    else:
        d.line([S(cx - 24, my + 2)[0:2], S(cx + 24, my + 2)[0:2]], fill=lip, width=7 * s)
    # arms + phone (looking at it)
    beige = (222, 200, 170)
    thick_line(d, S(230, 650)[0:2], S(340, 820)[0:2], 76 * s, beige)
    thick_line(d, S(570, 650)[0:2], S(460, 820)[0:2], 76 * s, beige)
    d.rounded_rectangle(S(335, 660, 465, 870), radius=24 * s, fill=(40, 42, 52))
    for x in (345, 455):
        d.ellipse(S(x - 30, 800, x + 30, 860), fill=skin)
    return im.resize((800, 1000), Image.LANCZOS)


# ---------------------------------------------------------------- backgrounds
@lru_cache(None)
def bg_shop():
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):  # warm wall gradient
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(250 - 30 * k), int(232 - 40 * k), int(205 - 50 * k)))
    d.rectangle((0, 1350, W, H), fill=(196, 160, 120))
    for x in range(0, W, 135):
        d.line([(x, 1350), (x - 200, H)], fill=(180, 145, 108), width=4)
    # window
    rrect(d, (640, 260, 1020, 900), 20, fill=(200, 228, 245), outline=(150, 120, 90), width=14)
    d.line([(830, 260), (830, 900)], fill=(150, 120, 90), width=10)
    # sign
    rrect(d, (60, 640, 340, 770), 14, fill=RED)
    draw_text_c(d, 200, 676, "CHEGIRMA", font(46), WHITE)
    # sofas
    for (x0, y0, c) in [(-60, 1080, (150, 152, 160)), (640, 1120, (205, 190, 165))]:
        rrect(d, (x0, y0, x0 + 520, y0 + 260), 50, fill=c)
        rrect(d, (x0 + 30, y0 - 120, x0 + 490, y0 + 60), 50, fill=tuple(int(v * 0.9) for v in c))
        rrect(d, (x0 + 380, y0 + 20, x0 + 470, y0 + 70), 10, fill=WHITE)
    return im


@lru_cache(None)
def bg_room():
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(214 - 30 * k), int(226 - 30 * k), int(236 - 25 * k)))
    rrect(d, (60, 220, 460, 820), 18, fill=(225, 238, 248), outline=(240, 244, 248), width=16)
    d.line([(260, 220), (260, 820)], fill=(240, 244, 248), width=10)
    colors = [(255, 220, 90), (255, 160, 170), (140, 210, 160), (150, 190, 255), (255, 190, 120)]
    for i in range(12):
        x = 560 + (i % 4) * 115
        y = 260 + (i // 4) * 120
        d.rectangle((x, y, x + 90, y + 90), fill=colors[i % 5])
    # desk
    d.rectangle((0, 1380, W, H), fill=(160, 112, 72))
    d.rectangle((0, 1380, W, 1410), fill=(130, 88, 54))
    # plant
    rrect(d, (870, 1230, 990, 1385), 14, fill=(200, 110, 80))
    for a in range(-60, 61, 30):
        ang = math.radians(a - 90)
        d.ellipse((930 + 120 * math.cos(ang) - 45, 1200 + 120 * math.sin(ang) - 25,
                   930 + 120 * math.cos(ang) + 45, 1200 + 120 * math.sin(ang) + 25), fill=(70, 150, 90))
    return im


def counter(img):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1560, W, H), fill=(150, 98, 58))
    d.rectangle((0, 1540, W, 1580), fill=(120, 76, 44))
    for x in range(0, W, 180):
        d.line([(x, 1600), (x, H)], fill=(136, 88, 52), width=6)


def piala(d, x, y, sc=1.0):
    d.chord((x - 70 * sc, y - 70 * sc, x + 70 * sc, y + 70 * sc), 0, 180, fill=WHITE, outline=(40, 80, 170), width=6)
    for i in range(-2, 3):
        d.ellipse((x + i * 24 * sc - 8 * sc, y + 20 * sc, x + i * 24 * sc + 8 * sc, y + 36 * sc), fill=(40, 80, 170))
    d.ellipse((x - 70 * sc, y - 10 * sc, x + 70 * sc, y + 10 * sc), fill=(150, 170, 80))


# ---------------------------------------------------------------- overlays
def hud(d, part="2-qism"):
    d.text((60, 240), f"Reklama degani shumi?! · {part}", font=font(34, "SemiBold"),
           fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
    rrect(d, (880, 226, 1020, 290), 16, fill=BRAND)
    draw_text_c(d, 950, 236, "ADUZ", font(38, "Black"), WHITE)


def subtitle(d, s):
    f = font(62)
    lines = wrap(d, s, f, 940)
    y = 1440 - len(lines) * 78
    for ln in lines:
        draw_text_c(d, W / 2, y, ln, f, WHITE, stroke=7)
        y += 78


def subtitle2(d, s):
    f = font(54)
    y = 1440
    for ln in wrap(d, s, f, 960):
        draw_text_c(d, W / 2, y, ln, f, WHITE, stroke=6)
        y += 68


def headline(d, s, y=430, size=92, color=YELLOW, pop=1.0):
    f = font(max(8, int(size * pop)), "Black")
    draw_text_c(d, W / 2, y, s, f, color, stroke=8)


def chat_card(base, y, who, msg, k, accent):
    """Slide-in chat card; k=animation progress 0..1."""
    if k <= 0:
        return
    card = Image.new("RGBA", (960, 230), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    rrect(d, (0, 0, 959, 229), 34, fill=(255, 255, 255, 245))
    d.ellipse((24, 30, 104, 110), fill=accent)
    draw_text_c(d, 64, 46, who[0], font(44, "Black"), WHITE)
    d.text((126, 26), who, font=font(36, "Bold"), fill=(90, 90, 100))
    lines = wrap(d, msg, font(42, "Bold"), 800)
    for i, ln in enumerate(lines[:2]):
        d.text((126, 80 + i * 54), ln, font=font(42, "Bold"), fill=INK)
    rrect(d, (720, 22, 940, 62), 12, fill=(225, 225, 230))
    draw_text_c(d, 830, 27, "Shartli misol", font(24, "SemiBold"), (90, 90, 100))
    x = int(60 + (1 - ease_out_back(k)) * 1100)
    base.alpha_composite(card, (x, int(y)))


def shake(t, a, b, amp=14):
    if a <= t <= b:
        return int(amp * math.sin(t * 90)), int(amp * math.cos(t * 77))
    return 0, 0


# ---------------------------------------------------------------- abacus
def abacus_scene(t):
    im = Image.new("RGBA", (W, H), (110, 70, 40, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y + 30)], fill=(100, 63, 36), width=6)
    rrect(d, (60, 300, 1020, 1300), 30, outline=(70, 40, 20), width=44)
    rows = 7
    for r in range(rows):
        y = 420 + r * 125
        d.line([(100, y), (980, y)], fill=(200, 180, 140), width=10)
        n = 10
        m = 3 + r % 3
        e = ease(prog(t, r * 0.35, r * 0.35 + 0.5))
        for i in range(n):
            bx = 940 - (n - 1 - i) * 62 - (200 * e if i < m else 0)
            col = (176, 52, 40) if i % 2 == 0 else (220, 170, 60)
            d.ellipse((bx - 30, y - 38, bx + 30, y + 38), fill=col, outline=(80, 30, 20), width=3)
    return im


# ---------------------------------------------------------------- phone mock (K4)
@lru_cache(None)
def phone_mock():
    pw, ph = 760, 1240
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, pw - 1, ph - 1), 80, fill=(18, 18, 24))
    rrect(d, (22, 22, pw - 23, ph - 23), 62, fill=(244, 246, 251))
    rrect(d, (pw / 2 - 90, 40, pw / 2 + 90, 70), 15, fill=(18, 18, 24))
    rrect(d, (22, 100, pw - 23, 240), 0, fill=BRAND)
    d.text((60, 120), "ADUZ", font=font(54, "Black"), fill=WHITE)
    d.text((60, 186), "@Targetreklammabot", font=font(30, "SemiBold"), fill=(200, 215, 245))
    d.text((60, 270), "Kanallarni solishtirish", font=font(38, "Bold"), fill=INK)
    cols = ["Narx", "Muddat", "Format", "Ko‘rish"]
    xs = [60, 240, 410, 560]
    for x, c in zip(xs, cols):
        d.text((x, 340), c, font=font(28, "Bold"), fill=(110, 110, 125))
    rows = [("1-kanal", "300 ming", "1 soat", "post", "4 ming"),
            ("2-kanal", "150 ming", "24 soat", "1 rasm", "2 ming"),
            ("3-kanal", "250 ming", "24 soat", "post", "7 ming")]
    for i, (name, *vals) in enumerate(rows):
        y = 400 + i * 230
        rrect(d, (44, y, pw - 45, y + 200), 28, fill=WHITE, outline=(225, 228, 238), width=3)
        d.text((70, y + 22), name, font=font(36, "Black"), fill=BRAND)
        for x, v in zip(xs, vals):
            d.text((x, y + 100), v, font=font(30, "Bold"), fill=INK)
    rrect(d, (44, 1110, pw - 45, 1190), 28, fill=(225, 228, 238))
    draw_text_c(d, pw / 2, 1128, "Shartli misol", font(30, "SemiBold"), (100, 100, 115))
    return im


# ---------------------------------------------------------------- scenes
def frame(t):
    if t < 8:
        img = scene1(t)
    elif t < 16:
        img = scene2(t - 8)
    elif t < 24:
        img = scene3(t - 16)
    elif t < 32:
        img = scene4(t - 24)
    else:
        img = scene5(t - 32)
    # white flash on cuts
    for c in (8, 16, 24, 32):
        if c - 0.05 <= t < c + 0.18:
            a = 1 - abs(t - c) / 0.18
            img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), clamp(a) * 0.8)
    return img


def push(img, t, z0=1.0, z1=1.06, dx=0, dy=0):
    z = z0 + (z1 - z0) * t
    if abs(z - 1) < 1e-3 and not dx and not dy:
        return img
    nw, nh = int(W * z), int(H * z)
    big = img.resize((nw, nh), Image.BILINEAR)
    x0 = (nw - W) // 2 + dx
    y0 = (nh - H) // 2 + dy
    return big.crop((x0, y0, x0 + W, y0 + H))


def scene1(t):
    img = bg_shop().copy()
    speaking = t < 3
    if t < 3:
        spr = rustam("show", brows=28, tilt=-6, eye=1.15, mouth="open" if talking(t, True) else "O")
    elif t < 4.6:
        spr = rustam("read", brows=34, eye=1.2, mouth="O")
    elif t < 6.2:
        spr = rustam("read", brows=-4, eye=0.45, mouth="flat")
    else:
        spr = rustam("read", brows=-10, tilt=14, eye=0.75, look=-8, mouth="frown")
    paste_scaled(img, spr, W / 2, 1080, 1.15)
    counter(img)
    d = ImageDraw.Draw(img)
    hud(d)
    pop = ease_out_back(prog(t, 0, 0.5))
    if t < 3:
        headline(d, "QAYSI BIRI TO‘G‘RI?!", y=420, pop=max(0.2, pop))
        subtitle(d, "Bir xil post. Uch xil admin. Uch xil narx!")
    else:
        chat_card(img, 330, "1-admin", "300 ming. Bir soat tepada, keyin lentada.", prog(t, 3.0, 3.5), (63, 120, 220))
        chat_card(img, 580, "2-admin", "150 ming. 24 soat, lekin bitta rasm.", prog(t, 4.6, 5.1), (80, 170, 110))
        chat_card(img, 830, "3-admin", "Avval postni yuboring, keyin narx aytaman.", prog(t, 6.2, 6.7), (200, 90, 150))
    return push(img, t / 8, 1.0, 1.05)


def scene2(t):
    if t < 3:
        img = abacus_scene(t)
        d = ImageDraw.Draw(img)
        hud(d)
        subtitle(d, "Bir soat tepada... yigirma to‘rt soat...")
        return push(img, t / 3, 1.08, 1.0)
    img = bg_shop().copy()
    if t < 6:
        spr = rustam("none", brows=12, tilt=-10, eye=0.9, look=int(14 * math.sin(t * 4)),
                     mouth="open" if talking(t, True) else "closed")
    else:
        spr = rustam("despair", brows=36, tilt=-14, eye=1.2, mouth="open" if talking(t, True) else "O")
    sx, sy = shake(t, 6, 6.6)
    paste_scaled(img, spr, W / 2 + sx, 1060 + sy, 1.25)
    counter(img)
    d = ImageDraw.Draw(img)
    hud(d)
    for i, (s, x, y) in enumerate([("1 soat?", 200, 520), ("24 soat?", 860, 600), ("1 rasm?", 850, 800)]):
        k = prog(t, 3 + i * 0.6, 3.4 + i * 0.6)
        if k > 0:
            f = font(max(8, int(56 * ease_out_back(k))), "Black")
            draw_text_c(d, x, y + 8 * math.sin(t * 3 + i), s, f, YELLOW, stroke=6)
    if t < 6:
        subtitle(d, "...bitta rasm...")
    else:
        headline(d, "?!", y=380, size=180, pop=ease_out_back(prog(t, 6, 6.4)))
        subtitle(d, "Bu matematikami yo fizika?!")
    return push(img, (t - 3) / 5, 1.0, 1.06)


def scene3(t):
    img = bg_shop().copy()
    d = ImageDraw.Draw(img)
    if t < 3:
        spr = rustam("mouth", brows=16, eye=1.0, look=10, mouth="grin" if int(t * 6) % 2 else "open")
    elif t < 5:
        fade = prog(t, 3.3, 4.6)
        spr = rustam("read", brows=10 - 20 * fade, eye=1.0 - 0.3 * fade, mouth="grin" if fade < 0.4 else ("closed" if fade < 0.8 else "frown"))
    else:
        spr = rustam("despair", brows=38, tilt=-16, eye=1.25, mouth="open" if talking(t, True) else "O")
    sx, sy = shake(t, 5, 5.7, 18)
    paste_scaled(img, spr, W / 2 + sx, 1080 + sy, 1.15)
    counter(img)
    d = ImageDraw.Draw(img)
    hud(d)
    if t < 3:
        # voice-message waveform bubble
        rrect(d, (130, 430, 760, 560), 60, fill=(255, 255, 255, 240))
        d.ellipse((160, 455, 240, 535), fill=(63, 120, 220))
        d.polygon([(190, 475), (190, 515), (222, 495)], fill=WHITE)
        for i in range(18):
            hgt = 12 + 34 * abs(math.sin(t * 9 + i * 0.8))
            x = 270 + i * 26
            d.rounded_rectangle((x, 495 - hgt, x + 12, 495 + hgt), radius=6, fill=(63, 120, 220))
        subtitle(d, "Ukam, 300 mingga ikkita qilib bering, bozor-ku!")
    elif t < 5:
        chat_card(img, 400, "1-admin", "Aka, bu bozor emas, kanal.", prog(t, 3, 3.4), (63, 120, 220))
        subtitle(d, "Aka, bu bozor emas, kanal.")
    else:
        k = ease_out_back(prog(t, 5, 5.4))
        headline(d, "BU REKLAMA-KU,", y=360, size=96, color=WHITE, pop=max(0.2, k))
        headline(d, "YO LOTEREYA?!", y=470, size=110, color=YELLOW, pop=max(0.2, k))
        subtitle(d, "Bu reklama-ku, yo lotereya?!")
    return push(img, t / 8, 1.0, 1.05)


PS = 0.72


def scene4(t):
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(15 + 20 * k), int(61 + 30 * k), int(145 + 40 * k)))
    # soft circles
    for i in range(6):
        r = 160 + i * 40
        cx = 540 + 380 * math.sin(t * 0.6 + i)
        cy = 400 + i * 260
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(70, 110, 190), width=3)
    k = ease_out_back(prog(t, 0.1, 0.9))
    ph = phone_mock()
    paste_scaled(img, ph, W / 2, 900 + (1 - k) * 1400, PS)
    d = ImageDraw.Draw(img)
    hud(d)
    # highlight sweep over rows
    if t > 1.2:
        row = int((t - 1.2) / 1.1) % 3
        y = 900 - 1240 * PS / 2 + (400 + row * 230) * PS
        x0 = W / 2 - 760 * PS / 2 + 44 * PS
        d.rounded_rectangle((x0, y, x0 + (760 - 89) * PS, y + 200 * PS), radius=24,
                            outline=YELLOW, width=8)
    headline(d, "Kanallar — bir joyda", y=300, size=74, color=WHITE)
    if t < 4:
        subtitle2(d, "Narx, muddat, format va ko‘rishlarni yonma-yon ko‘ring.")
    else:
        subtitle2(d, "ADUZ'da kanallarni shunday solishtirasiz.")
    return img


def scene5(t):
    img = bg_room().copy()
    d = ImageDraw.Draw(img)
    rise = ease(prog(t, 1.6, 3.4))
    if t < 4:
        spr = dilnoza(eye=1.0, mouth="closed")
    elif t < 6:
        spr = dilnoza(eye=0.55, mouth="open" if talking(t, True) else "closed", brows=-4)
    else:
        spr = dilnoza(eye=0.8, look=-12, mouth="smirk", brows=6)
    paste_scaled(img, spr, W / 2, 1130 + (1 - rise) * 900, 1.15)
    d = ImageDraw.Draw(img)
    # desk front + props
    d.rectangle((0, 1560, W, H), fill=(160, 112, 72))
    d.rectangle((0, 1560, W, 1590), fill=(130, 88, 54))
    piala(d, 220, 1560, 1.0)
    if t < 2.2:  # phone on desk
        rrect(d, (520, 1500, 700, 1560), 14, fill=(40, 42, 52))
    hud(d)
    if 4 <= t < 6:
        subtitle(d, "Postni yubormadi-yu...")
    if t >= 6:
        k = ease_out_back(prog(t, 6, 6.4))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, int(140 * clamp((t - 6) / 0.4))))
        img.alpha_composite(ov)
        d = ImageDraw.Draw(img)
        hud(d)
        rrect(d, (70, 760, 1010, 1110), 40, fill=(255, 255, 255, 250))
        f = font(int(58 * max(0.3, k)), "Black")
        draw_text_c(d, W / 2, 800, "Narx so‘rab charchagan", f, INK)
        draw_text_c(d, W / 2, 875, "do‘stingizga yuboring", f, INK)
        rrect(d, (300, 975, 780, 1070), 30, fill=BRAND)
        draw_text_c(d, W / 2, 993, "YUBORISH", font(52, "Black"), WHITE)
        draw_text_c(d, W / 2, 1180, "Ertaga: uchinchi admin kim edi?", font(48, "Bold"), YELLOW, stroke=5)
    return push(img, t / 8, 1.0, 1.04)


# ---------------------------------------------------------------- audio
SR = 44100


def tone(freq, dur, decay=4.0, harmonics=(1, 0.5, 0.25), vol=0.3):
    n = int(SR * dur)
    tt = np.arange(n) / SR
    sig = sum(a * np.sin(2 * np.pi * freq * (i + 1) * tt) for i, a in enumerate(harmonics))
    return vol * sig * np.exp(-decay * tt)


def noise(dur, vol=0.3, smooth=8):
    n = int(SR * dur)
    x = np.random.default_rng(1).standard_normal(n)
    if smooth > 1:
        x = np.convolve(x, np.ones(smooth) / smooth, mode="same")
    return vol * x


def add(buf, sig, at):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def build_audio(path):
    buf = np.zeros(int(SR * DUR) + SR)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    # playful pluck music 0-32 s (100 bpm, eighths = 0.3 s)
    prog_ = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)]
    t = 0.0
    while t < 32:
        bar = int(t / 2.4) % 4
        chord = prog_[bar]
        step = int(round(t / 0.3)) % 8
        if not (21.0 <= t < 22.2):  # silence for the punchline
            m = chord[[0, 1, 2, 1, 0, 2, 1, 2][step]] + 12
            add(buf, tone(note(m), 0.35, decay=9, vol=0.07), t)
            if step == 0:
                add(buf, tone(note(chord[0] - 12), 1.2, decay=2.5, harmonics=(1, 0.3), vol=0.09), t)
        t += 0.3
    # mysterious pad for Dilnoza 32-40 s
    for m, at in [(57, 32.0), (52, 34.4), (53, 36.8)]:
        for mm in (m, m + 3 if m != 53 else m + 4, m + 7):
            add(buf, tone(note(mm), 2.6, decay=0.8, harmonics=(1, 0.2), vol=0.05), at)
    # SFX
    ding = lambda: tone(1318.5, 0.5, decay=8, harmonics=(1, 0.3), vol=0.18) + np.pad(
        tone(1760, 0.45, decay=8, harmonics=(1,), vol=0.12), (int(0.06 * SR), 0))[: int(0.5 * SR)]
    for at in (3.0, 4.6, 6.2, 19.0):
        add(buf, ding(), at)
    rng = np.random.default_rng(3)
    for at in np.sort(rng.uniform(8.1, 10.9, 16)):
        add(buf, tone(2400 + rng.uniform(-300, 300), 0.05, decay=90, harmonics=(1, 0.4), vol=0.2), at)
    for at in (7.85, 15.85, 23.85, 31.85):
        n = noise(0.45, 0.25, 30) * np.sin(np.linspace(0, np.pi, int(0.45 * SR)))
        add(buf, n, at)
    add(buf, tone(70, 0.6, decay=6, harmonics=(1, 0.5), vol=0.5) + noise(0.6, 0.06, 2) * np.exp(-8 * np.arange(int(0.6 * SR)) / SR), 21.0)
    add(buf, tone(2093, 1.5, decay=2.5, harmonics=(1, 0.2), vol=0.07), 38.0)
    add(buf, tone(2637, 1.5, decay=2.5, harmonics=(1,), vol=0.05), 38.08)
    buf = buf[: int(SR * DUR)]
    buf = buf / max(1e-9, np.abs(buf).max()) * 0.8
    pcm = (buf * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- main
def main(out):
    wav = out + ".wav"
    build_audio(wav)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    for i in range(n):
        p.stdin.write(frame(i / FPS).convert("RGB").tobytes())
        if i % 150 == 0:
            print(f"{i}/{n}", flush=True)
    p.stdin.close()
    p.wait()
    print("done", out)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        for ts in sys.argv[2:]:
            frame(float(ts)).convert("RGB").save(f"preview_{ts}.png")
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_2-kun.mp4")
