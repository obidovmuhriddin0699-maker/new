"""ADUZ · "Reklama degani shumi?!" · 8-qism — "ADUZ nima?" (motion grafika uslubi).

Muxriddin Obidov (asoschi) ADUZ'ni tanishtiradi: kinetik matn, ikonkalar, markaziy "hub", 5 bosqich.
Ishga tushirish:  python3 make_day8.py <chiqish.mp4>      (ovoz tekshiruvi: python3 make_day8.py --qa)
"""
import math
import os
import subprocess
import sys
import tempfile
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import voice
from make_day2 import (BRAND, INK, RED, WHITE, YELLOW, FPS, H, W, add, clamp, dilnoza, draw_text_c, ease,
                       ease_out_back, font, noise, prog, rrect, rustam, subtitle2, tone, wrap)
from make_day7 import founder

SR = voice.SR
PART = "8-qism"
DUR = 42.5
GREEN = (46, 190, 110)
CYAN = (80, 200, 255)
BG1, BG2 = (8, 18, 48), (14, 52, 128)

LINES = [
    (0.3, "rus", "[shout]Divanimning orqasida nima qilyapsiz?!", "Divanimning orqasida nima qilyapsiz?!", 1.05),
    (2.9, "asos", "[warm]Sizga reklamaning osonroq yo'lini ko'rsatgani keldim.",
     "Sizga reklamaning osonroq yo‘lini ko‘rsatgani keldim.", 1.04),
    (7.1, "asos", "[neutral]Kanal qidirish, narx so'rash, kelishish, kuzatish...[p=250][sad]"
                  "hammasi alohida, hammasi qo'lda.",
     "Kanal qidirish, narx so‘rash, kelishish, kuzatish... hammasi alohida, hammasi qo‘lda.", 1.06),
    (14.0, "asos", "[warm]Aduz reklama beruvchi va kanal egasini[p=100]bitta platformada uchrashtiradi.",
     "ADUZ reklama beruvchi va kanal egasini bitta platformada uchrashtiradi.", 1.04),
    (20.0, "asos", "[neutral]Hudud bo'yicha kanal toping.[p=200]Narx va ko'rishlarni solishtiring.[p=200]"
                   "Buyurtma bering, holatini kuzating.[p=200][happy]Natijani ko'ring.",
     "Hudud bo‘yicha kanal toping. Narx va ko‘rishlarni solishtiring. Buyurtma bering, holatini kuzating. "
     "Natijani ko‘ring.", 1.06),
    (29.0, "rus", "[excited]Hammasi bir joyda?!", "Hammasi bir joyda?!"),
    (30.6, "asos", "[happy]Hammasi bir joyda.[p=250][warm]Telegramda, bot orqali.",
     "Hammasi bir joyda. Telegramda, bot orqali."),
    (35.0, "asos", "[warm]Sizga birinchi qaysi imkoniyat kerak?[p=150]Izohda yozing.",
     "Sizga birinchi qaysi imkoniyat kerak? Izohda yozing.", 1.04),
]

FEATURES = [("search", "Kanal toping", "hudud va mavzu bo‘yicha"),
            ("scale", "Solishtiring", "narx va haqiqiy ko‘rishlar"),
            ("calendar", "Buyurtma bering", "sana, soat, format"),
            ("status", "Kuzating", "kutilmoqda → joylandi"),
            ("chart", "Natijani ko‘ring", "qaysi kanal ishladi")]


# ---------------------------------------------------------------- background
@lru_cache(None)
def bg_base():
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BG1[i] + (BG2[i] - BG1[i]) * k) for i in range(3)))
    return im


@lru_cache(None)
def blob(r, color):
    im = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((r, r, 3 * r, 3 * r), fill=color)
    return im.filter(ImageFilter.GaussianBlur(r // 2))


def background(t, accent=(40, 110, 255)):
    img = bg_base().copy()
    for i, (r, c) in enumerate([(260, accent + (90,)), (220, (255, 200, 61, 55)), (300, (80, 200, 255, 60))]):
        x = W / 2 + 380 * math.sin(t * 0.35 + i * 2.1)
        y = H / 2 + 620 * math.cos(t * 0.27 + i * 1.7)
        b = blob(r, c)
        img.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))
    d = ImageDraw.Draw(img)
    # drifting dot grid
    off = (t * 24) % 90
    for y in range(-90, H + 90, 90):
        for x in range(0, W + 90, 90):
            d.ellipse((x - 2, y + off - 2, x + 2, y + off + 2), fill=(120, 160, 255, 70))
    return img


def hud8(d):
    d.text((60, 240), f"Reklama degani shumi?! · {PART}", font=font(34, "SemiBold"), fill=(220, 230, 255))
    rrect(d, (880, 226, 1020, 290), 16, fill=YELLOW)
    draw_text_c(d, 950, 236, "ADUZ", font(38, "Black"), INK)


# ---------------------------------------------------------------- avatars & icons
@lru_cache(None)
def avatar_img(who, mouth, size=300):
    if who == "rus":
        spr = rustam("none", brows=24, tilt=-10, eye=1.15, mouth=mouth)
    elif who == "asos":
        spr = founder(eye=1.0, mouth=mouth, smile=(mouth == "closed"))
    else:
        spr = dilnoza(eye=0.95, mouth=mouth)
    head = spr.crop((120, 60, 680, 620)).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size + 20, size + 20), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, size + 19, size + 19), fill=YELLOW if who == "asos" else WHITE)
    disc = Image.new("RGBA", (size, size), (235, 242, 255, 255))
    disc.alpha_composite(head)
    out.paste(disc, (10, 10), mask)
    return out


def avatar(img, envs, who, t, cx, cy, k=1.0, size=300):
    if k <= 0.01:
        return
    m = voice.mouth(envs, who, t, "closed")
    a = avatar_img(who, m, size)
    s = max(0.05, k)
    a = a.resize((max(1, int(a.width * s)), max(1, int(a.height * s))), Image.LANCZOS)
    if voice.speaking(envs, who, t):  # speaking ring pulse
        d = ImageDraw.Draw(img)
        r = a.width / 2 + 14 + 8 * abs(math.sin(t * 9))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=YELLOW, width=6)
    img.alpha_composite(a, (int(cx - a.width / 2), int(cy - a.height / 2)))


@lru_cache(None)
def icon(kind, size=120, col=WHITE):
    s = 4
    n = size * s
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = int(n * 0.07)
    if kind == "search":
        d.ellipse((n * .12, n * .12, n * .62, n * .62), outline=col, width=w)
        d.line([(n * .55, n * .55), (n * .86, n * .86)], fill=col, width=int(w * 1.4))
    elif kind == "scale":
        d.line([(n * .5, n * .15), (n * .5, n * .85)], fill=col, width=w)
        d.line([(n * .15, n * .3), (n * .85, n * .3)], fill=col, width=w)
        for x in (.22, .78):
            d.chord((n * (x - .15), n * .38, n * (x + .15), n * .62), 0, 180, fill=col)
        d.rectangle((n * .3, n * .82, n * .7, n * .88), fill=col)
    elif kind == "calendar":
        d.rounded_rectangle((n * .12, n * .2, n * .88, n * .86), radius=n * .08, outline=col, width=w)
        d.rectangle((n * .12, n * .2, n * .88, n * .36), fill=col)
        for i in range(3):
            for j in range(2):
                d.rectangle((n * (.24 + i * .2), n * (.47 + j * .17), n * (.34 + i * .2), n * (.56 + j * .17)), fill=col)
    elif kind == "status":
        d.ellipse((n * .12, n * .12, n * .88, n * .88), outline=col, width=w)
        d.line([(n * .3, n * .52), (n * .45, n * .67), (n * .72, n * .36)], fill=col, width=int(w * 1.3))
    elif kind == "chart":
        for i, h in enumerate((.35, .55, .8)):
            d.rectangle((n * (.16 + i * .25), n * (.88 - h), n * (.32 + i * .25), n * .88), fill=col)
    elif kind == "plane":
        d.polygon([(n * .1, n * .48), (n * .9, n * .15), (n * .62, n * .88), (n * .48, n * .6)], fill=col)
        d.polygon([(n * .48, n * .6), (n * .9, n * .15), (n * .42, n * .78)], fill=(200, 210, 230))
    elif kind == "user":
        d.ellipse((n * .32, n * .12, n * .68, n * .48), fill=col)
        d.chord((n * .14, n * .52, n * .86, n * 1.2), 180, 360, fill=col)
    elif kind == "channel":
        d.polygon([(n * .15, n * .38), (n * .52, n * .38), (n * .85, n * .15), (n * .85, n * .85),
                   (n * .52, n * .62), (n * .15, n * .62)], fill=col)
    return im.resize((size, size), Image.LANCZOS)


def kinetic(img, s, x, y, t0, t, size=80, color=WHITE, center=True, weight="Black", stroke=0):
    """Word-by-word slide-up + fade."""
    d = ImageDraw.Draw(img)
    f = font(size, weight)
    words = s.split()
    widths = [d.textbbox((0, 0), w_ + " ", font=f)[2] for w_ in words]
    total = sum(widths)
    cx = x - total / 2 if center else x
    for i, (w_, ww) in enumerate(zip(words, widths)):
        k = ease(prog(t, t0 + i * 0.09, t0 + i * 0.09 + 0.35))
        if k <= 0:
            break
        layer = Image.new("RGBA", (ww + 40, size + 60), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((10, 10), w_, font=f, fill=color + (int(255 * k),), stroke_width=stroke,
                                   stroke_fill=(0, 0, 0, int(255 * k)))
        img.alpha_composite(layer, (int(cx - 10), int(y + (1 - k) * 40 - 10)))
        cx += ww


def glass(img, box, r=36, fill=(255, 255, 255, 30), outline=(255, 255, 255, 80)):
    """Translucent card: drawn on its own layer and composited (keeps real transparency)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    layer = Image.new("RGBA", (x1 - x0 + 8, y1 - y0 + 8), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle((2, 2, x1 - x0 + 2, y1 - y0 + 2), radius=r, fill=fill, outline=outline,
                                            width=3)
    img.alpha_composite(layer, (max(0, x0 - 2), max(0, y0 - 2)))


# ---------------------------------------------------------------- scenes
def s_hook(img, t, envs):
    d = ImageDraw.Draw(img)
    k1 = ease_out_back(prog(t, 0.0, 0.5))
    k2 = ease_out_back(prog(t, 2.6, 3.1))
    avatar(img, envs, "rus", t, 300, 820 + 30 * math.sin(t * 7) * (1 - prog(t, 0, 2.5)), k1, 340)
    avatar(img, envs, "asos", t, 780, 1080, k2, 340)
    kinetic(img, "?!", 300, 520, 0.4, t, 150, YELLOW)
    if t > 3.2:
        kk = ease(prog(t, 3.2, 3.7))
        glass(img, (430, 1290, 1030, 1420), 30, fill=(255, 255, 255, int(235 * kk)), outline=(255, 255, 255, 0))
        if kk > 0.5:
            d.text((460, 1305), "Muxriddin Obidov", font=font(46, "Black"), fill=INK)
            d.text((460, 1362), "ADUZ asoschisi", font=font(34, "Bold"), fill=BRAND)


def s_problem(img, t, envs):
    tt = t - 7
    d = ImageDraw.Draw(img)
    chips = ["Kanal qidirish", "Narx so‘rash", "Kelishish", "Kuzatish"]
    collapse = ease(prog(tt, 5.0, 5.8))
    for i, c in enumerate(chips):
        k = ease_out_back(prog(tt, 0.2 + i * 0.75, 0.6 + i * 0.75))
        if k <= 0:
            continue
        x0 = 120 + (i % 2) * 440
        y0 = 520 + (i // 2) * 170
        x = x0 + (W / 2 - 210 - x0) * collapse + 8 * math.sin(tt * 11 + i)
        y = y0 + (760 - y0) * collapse + 8 * math.cos(tt * 9 + i)
        glass(img, (x, y, x + 400, y + 120), 60, fill=(255, 255, 255, 40))
        draw_text_c(d, x + 200, y + 34, c, font(max(8, int(44 * k)), "Bold"), WHITE)
    stats = [("12", "admin"), ("47", "xabar"), ("3", "xil narx"), ("6", "soat")]
    for i, (n, lab) in enumerate(stats):
        k = ease_out_back(prog(tt, 1.0 + i * 0.6, 1.4 + i * 0.6)) * (1 - collapse)
        if k <= 0.02:
            continue
        x, y = 200 + i * 230, 1020
        draw_text_c(d, x, y, n, font(max(8, int(96 * k)), "Black"), RED if i < 3 else YELLOW)
        draw_text_c(d, x, y + 110, lab, font(max(8, int(32 * k)), "Bold"), (200, 210, 240))
    if tt > 5.4:
        k = ease_out_back(prog(tt, 5.4, 5.9))
        rrect(d, (170, 690, 910, 840), 40, fill=RED)
        draw_text_c(d, W / 2, 716, "HAMMASI QO‘LDA", font(max(8, int(80 * k)), "Black"), WHITE)


def s_hub(img, t, envs):
    tt = t - 14
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, 860
    k = ease_out_back(prog(tt, 0.1, 0.8))
    for i in range(3):  # pulsing rings
        r = 150 + i * 70 + 20 * math.sin(tt * 3 - i)
        d.ellipse((cx - r * k, cy - r * k, cx + r * k, cy + r * k), outline=(255, 200, 61, 90 - i * 25), width=5)
    r = 140 * k
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YELLOW)
    draw_text_c(d, cx, cy - 46 * k, "ADUZ", font(max(8, int(84 * k)), "Black"), INK)
    nodes = [("rus", "Reklama", "beruvchi", 210, 560, 0.9), ("dil", "Kanal", "egasi", 860, 1140, 1.5)]
    for who, a, b, x, y, t0 in nodes:
        kk = ease_out_back(prog(tt, t0, t0 + 0.5))
        if kk <= 0:
            continue
        # animated dashed connector
        steps = 14
        for j in range(steps):
            p0 = j / steps
            ph = (p0 + tt * 0.6) % 1.0
            px, py = x + (cx - x) * ph, y + (cy - y) * ph
            d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=(255, 255, 255, int(200 * kk)))
        avatar(img, envs, who, t, x, y, kk, 220)
        d = ImageDraw.Draw(img)
        draw_text_c(d, x, y + 140, a, font(40, "Black"), WHITE)
        draw_text_c(d, x, y + 188, b, font(40, "Black"), WHITE)
    kinetic(img, "Bitta platformada", W / 2, 330, 3.0 + 14, t, 70, YELLOW)


def s_features(img, t, envs):
    tt = t - 20
    d = ImageDraw.Draw(img)
    starts = [0.2, 1.9, 3.8, 5.2, 7.1]
    kinetic(img, "5 qadam", W / 2, 330, 20.1, t, 70, YELLOW)
    d = ImageDraw.Draw(img)
    # progress rail
    rail_k = ease(prog(tt, 0.2, 8.0))
    d.line([(150, 470), (150, 470 + 940 * rail_k)], fill=YELLOW, width=8)
    for i, ((ic, title, sub), st) in enumerate(zip(FEATURES, starts)):
        k = ease_out_back(prog(tt, st, st + 0.5))
        if k <= 0:
            continue
        y = 440 + i * 200
        x = 230 + (1 - k) * 700
        active = st <= tt < (starts[i + 1] if i + 1 < len(starts) else 99)
        glass(img, (x, y, x + 790, y + 160), 34, fill=(255, 255, 255, 70 if active else 32),
              outline=(255, 200, 61, 200) if active else (255, 255, 255, 70))
        d.ellipse((150 - 26, y + 54, 150 + 26, y + 106), fill=YELLOW if tt > st else (80, 100, 150))
        draw_text_c(d, 150, y + 60, str(i + 1), font(32, "Black"), INK)
        ic_img = icon(ic, 96, YELLOW if active else WHITE)
        img.alpha_composite(ic_img, (int(x + 30), int(y + 32)))
        d = ImageDraw.Draw(img)
        d.text((x + 150, y + 26), title, font=font(48, "Black"), fill=WHITE)
        d.text((x + 150, y + 92), sub, font=font(32, "SemiBold"), fill=(200, 215, 245))


def s_allinone(img, t, envs):
    tt = t - 29
    d = ImageDraw.Draw(img)
    avatar(img, envs, "rus", t, 260, 560, ease_out_back(prog(tt, 0.0, 0.4)), 260)
    avatar(img, envs, "asos", t, 820, 560, ease_out_back(prog(tt, 1.4, 1.8)), 260)
    kinetic(img, "HAMMASI", W / 2, 760, 30.7, t, 120, WHITE)
    kinetic(img, "BIR JOYDA", W / 2, 890, 31.0, t, 120, YELLOW)
    # telegram-bot pill
    k = ease_out_back(prog(tt, 3.4, 3.9))
    if k > 0:
        d = ImageDraw.Draw(img)
        x0, y0 = W / 2 - 430 * k, 1100
        rrect(d, (x0, y0, W / 2 + 430 * k, y0 + 150), 75, fill=(42, 158, 230))
        if k > 0.6:
            img.alpha_composite(icon("plane", 90, WHITE), (int(x0 + 40), int(y0 + 30)))
            d = ImageDraw.Draw(img)
            d.text((x0 + 150, y0 + 46), "@Targetreklammabot", font=font(48, "Black"), fill=WHITE)


def s_cta(img, t, envs):
    tt = t - 35
    d = ImageDraw.Draw(img)
    avatar(img, envs, "asos", t, W / 2, 520, ease_out_back(prog(tt, 0, 0.4)), 260)
    d = ImageDraw.Draw(img)
    kinetic(img, "Sizga birinchi qaysi", W / 2, 720, 35.2, t, 64, WHITE)
    kinetic(img, "imkoniyat kerak?", W / 2, 800, 35.5, t, 64, WHITE)
    for i, (ic, title, _) in enumerate(FEATURES):
        k = ease_out_back(prog(tt, 0.8 + i * 0.25, 1.2 + i * 0.25))
        if k <= 0:
            continue
        y = 920 + i * 92
        glass(img, (220, y, 860, y + 76), 38, fill=(255, 255, 255, 45))
        draw_text_c(d, 270, y + 14, str(i + 1), font(40, "Black"), YELLOW)
        d.text((320, y + 14), title, font=font(40, "Bold"), fill=WHITE)
    if tt > 3.6:
        k = ease_out_back(prog(tt, 3.6, 4.0))
        rrect(d, (240, 1400, 840, 1490), 45, fill=YELLOW)
        draw_text_c(d, W / 2, 1418, "IZOHDA YOZING", font(max(8, int(50 * k)), "Black"), INK)
    if tt > 5.2:
        kinetic(img, "Ertaga: Farg‘ona kanallarini topamiz", W / 2, 1520, 40.2, t, 38, (200, 215, 245),
                weight="Bold")


SCENES = [(0, 7, s_hook), (7, 14, s_problem), (14, 20, s_hub), (20, 29, s_features), (29, 35, s_allinone),
          (35, DUR + 1, s_cta)]


def frame(t, envs, timings):
    img = background(t)
    for a, b, fn in SCENES:
        if a <= t < b:
            # quick zoom-in on scene start
            fn(img, t, envs)
            break
    d = ImageDraw.Draw(img)
    hud8(d)
    for (a, b, who, sub) in timings:
        if a - 0.05 <= t <= b + 0.3 and t < 39.2:
            subtitle2(d, sub)
    for c in (7, 14, 20, 29, 35):  # flash + slight push on cuts
        if c - 0.04 <= t < c + 0.15:
            a = 1 - abs(t - c) / 0.15
            img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), clamp(a) * 0.6)
    return img


# ---------------------------------------------------------------- audio: modern light beat
def music_and_sfx():
    buf = np.zeros(int(SR * DUR) + SR)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    bpm = 104
    beat = 60 / bpm
    kick = lambda: tone(55, 0.35, decay=14, harmonics=(1, 0.3), vol=0.6) * np.linspace(1, 0.6, int(0.35 * SR))
    hat = lambda: noise(0.06, 0.25, 1) * np.exp(-60 * np.arange(int(0.06 * SR)) / SR)
    prog_ = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
    t = 0.0
    n = 0
    while t < DUR - 0.5:
        bar = int(n / 4) % 4
        chord = prog_[bar]
        quiet = 7.0 <= t < 14.0  # sparse during the "problem" part
        if n % 4 in (0, 2) and not (13.0 < t < 14.0):
            add(buf, kick() * (0.6 if quiet else 1.0), t)
        if not quiet:
            add(buf, hat(), t + beat / 2)
        if n % 4 == 0:
            for m in chord:
                add(buf, tone(note(m), beat * 4, decay=0.6, harmonics=(1, 0.25), vol=0.05), t)
            add(buf, tone(note(chord[0] - 24), beat * 2, decay=1.5, harmonics=(1, 0.5), vol=0.18), t)
        add(buf, tone(note(chord[n % 3] + 12), 0.25, decay=10, harmonics=(1, 0.3), vol=0.05), t + beat / 2)
        t += beat
        n += 1
    # riser into the hub reveal + impact
    nr = int(1.4 * SR)
    add(buf, noise(1.4, 0.25, 6) * np.linspace(0, 1, nr) ** 2, 12.6)
    add(buf, tone(45, 1.2, decay=3, harmonics=(1, 0.5), vol=0.9), 14.0)
    for c in (7, 20, 29, 35):
        add(buf, noise(0.4, 0.3, 30) * np.sin(np.linspace(0, np.pi, int(0.4 * SR))), c - 0.2)
    for st in (20.2, 21.9, 23.8, 25.2, 27.1):  # pops for each feature card
        add(buf, tone(1046, 0.18, decay=20, harmonics=(1, 0.4), vol=0.25), st)
    for i in range(4):  # chips in the problem part
        add(buf, tone(330, 0.15, decay=20, harmonics=(1, 0.5), vol=0.2), 7.2 + i * 0.75)
    add(buf, tone(110, 0.5, decay=6, harmonics=(1, 0.6, 0.3), vol=0.6), 12.4)  # "hammasi qo'lda" thud
    return buf[: int(SR * DUR)]


def main(out, preview=None, qa_only=False):
    tmp = tempfile.mkdtemp()
    speech, envs, timings = voice.build_speech(LINES, DUR, FPS, tmp)
    problems = voice.qa(LINES, timings, speech)
    if qa_only:
        sys.exit(1 if problems else 0)
    if preview:
        for ts in preview:
            frame(float(ts), envs, timings).convert("RGB").save(f"preview8_{ts}.png")
        return
    wav = os.path.join(tmp, "mix.wav")
    voice.mix(speech, music_and_sfx(), wav, tmp)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(i / FPS, envs, timings).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print("done", out)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--qa":
        main(None, qa_only=True)
    elif len(sys.argv) > 2 and sys.argv[1] == "--preview":
        main(None, sys.argv[2:])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_8-kun.mp4")
