"""ADUZ · 10-qism — "Narx va ma'lumotlarni solishtirish" (motion uslubi A, MOTION_QOLLANMA.md).

 01 Uch narx              — 2-qismga qaytish: uchta admin javobi (chat kartochkalar)
 02 Kartochka → jadval    — Spring stack: kartochkalar yoyilib, bitta solishtirish jadvaliga tushadi
 03 Saralash              — Tabs → panels: Narx · Ko'rish · 1000 ko'rish narxi bo'yicha qatorlar o'rin almashadi
 04 Ustun → chiziq        — Chart morph: narx ustunlari "1000 ko'rish narxi" chizig'iga aylanadi + Dashboard zoom
 05 Saqlab qo'ying        — kursor "Saqlash" ni bosadi, belgi portlaydi; ertangi qismga ko'prik

Ishga tushirish:  python3 make_day10.py <chiqish.mp4>   |   python3 make_day10.py --qa
"""
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

import voice
from make_day2 import FPS, H, W, add, clamp, ease, font, noise, prog, rustam, tone
from make_day7 import founder
from motion_a import (GREEN, INK, MUTED, NAVY, ORANGE, PAGE, RED, SKY, WIN, avatar_circle, card, chip, cursor,
                      page, sp, spring, subtitle)

SR = voice.SR
DUR = 40.0
X0, Y0, X1, Y1 = WIN
CX = (X0 + X1) / 2

# shartli misol (conditional example)
CHANNELS = [
    {"n": "1-kanal", "price": 300, "dur": "1 soat", "fmt": "matn+rasm", "views": 4000, "col": ORANGE},
    {"n": "2-kanal", "price": 150, "dur": "24 soat", "fmt": "1 rasm", "views": 2000, "col": SKY},
    {"n": "3-kanal", "price": 250, "dur": "24 soat", "fmt": "matn+rasm", "views": 7000, "col": NAVY},
]
for c in CHANNELS:
    c["cpm"] = c["price"] * 1000 / c["views"]   # ming so'm / 1000 ko'rish

LINES = [
    (0.3, "rus8", "[ironic]Esingizdami?[p=150]Bir post —[p=100]uch xil narx.", "Esingizdami? Bir post — uch xil narx.", 1.05),
    (4.2, "rus8", "[sad]Qaysi biri to'g'ri,[p=100]hali ham bilmayman...", "Qaysi biri to‘g‘ri, hali ham bilmayman...", 1.05),
    (8.4, "narr", "[happy]Aduzda narx, muddat, format va ko'rishlar[p=100]bitta jadvalda.",
     "ADUZ'da narx, muddat, format va ko‘rishlar — bitta jadvalda.", 0.97),
    (16.4, "narr", "[warm]Eng arzonini emas —[p=150]eng foydalisini tanlang.",
     "Eng arzonini emas — eng foydalisini tanlang.", 0.97),
    (20.4, "narr", "[neutral]Ko'rishlar bo'yicha saralang,[p=100]keyin har ming ko'rish narxiga qarang.",
     "Ko‘rishlar bo‘yicha saralang, keyin har 1000 ko‘rish narxiga qarang.", 1.0),
    (24.4, "narr", "[excited]Qimmatroq kanal[p=100]aslida foydaliroq chiqishi mumkin!",
     "Qimmatroq kanal aslida foydaliroq chiqishi mumkin!", 0.97),
    (29.0, "rus8", "[excited]Endi cho't kerak emas!", "Endi cho‘t kerak emas!"),
    (32.6, "narr", "[happy]Saqlab qo'ying![p=150]Ertaga buyurtma holatini kuzatamiz.",
     "Saqlab qo‘ying! Ertaga buyurtma holatini kuzatamiz.", 0.97),
]

BLOCKS = [
    ("01", "Uch narx", "Bir xil post — uch xil javob.", "kanal tanlayotgan biznes egalari."),
    ("02", "Kartochka → jadval", "Uchta javob bitta jadvalga tushadi.", "narxlarni bir qarashda solishtirish."),
    ("03", "Saralash", "Tab almashadi — qatorlar o‘rin almashadi.", "eng foydali kanalni topish."),
    ("04", "Ustun → chiziq", "Narx emas, 1000 ko‘rish narxi muhim.", "byudjetni to‘g‘ri sarflash."),
    ("05", "Saqlab qo‘ying", "Keyingi reklamadan oldin qayta ko‘ring.", "reklama beruvchilar va SMM mutaxassislar."),
]


def fmt_k(v):
    return f"{int(round(v))} ming"


# ---------------------------------------------------------------- block 1: three chat answers
def chat_card(img, x, y, w, name, lines, col, k, tilt=0.0):
    if k <= 0:
        return
    h = 210
    layer = Image.new("RGBA", (int(w) + 80, h + 80), (0, 0, 0, 0))
    tmp = Image.new("RGBA", (int(w) + 80, h + 80), (0, 0, 0, 0))
    card(tmp, (40, 40, 40 + w, 40 + h), r=32)
    d = ImageDraw.Draw(tmp)
    d.ellipse((70, 70, 140, 140), fill=col)
    d.text((97, 82), name[0], font=font(40, "Black"), fill=(255, 255, 255))
    d.text((165, 66), name, font=font(32, "Bold"), fill=MUTED)
    for i, ln in enumerate(lines):
        d.text((165, 110 + i * 48), ln, font=font(40 if i == 0 else 32, "Black" if i == 0 else "SemiBold"),
               fill=INK if i == 0 else MUTED)
    chip(tmp, int(40 + w - 210), 66, "shartli misol", fill=(240, 236, 232), color=MUTED, size=22)
    if tilt:
        tmp = tmp.rotate(tilt, resample=Image.BICUBIC, expand=False)
    layer.alpha_composite(tmp)
    s = 0.6 + 0.4 * k
    if s != 1:
        layer = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.LANCZOS)
    img.alpha_composite(layer, (int(x - 40 * s + (1 - s) * w / 2), int(y - 40 * s)))


def block1(img, t, envs):
    texts = [["300 ming", "1 soat tepada, keyin lentada"], ["150 ming", "24 soat, faqat 1 rasm"],
             ["250 ming", "24 soat, matn + rasm"]]
    for i, c in enumerate(CHANNELS):
        k = sp(t, 0.4 + i * 0.9, 0.5)
        y = Y0 + 80 + i * 250 + 6 * math.sin(t * 2 + i)
        chat_card(img, X0 + 40 + (1 - clamp(k)) * 300, y, X1 - X0 - 80, f"{i + 1}-admin", texts[i], c["col"], k)
    d = ImageDraw.Draw(img)
    if t > 3.4:
        k = sp(t, 3.4)
        f = font(max(8, int(86 * k)), "Black")
        s = "?!"
        tw = d.textbbox((0, 0), s, font=f)[2]
        d.text((X1 - 60 - tw, Y0 + 830), s, font=f, fill=ORANGE)
    spr = rustam("read", brows=24, tilt=-10, eye=1.15, mouth=voice.mouth(envs, "rus8", t, "frown"))
    avatar_circle(img, spr, X0 + 130, Y0 + 900, 150, ORANGE if voice.speaking(envs, "rus8", t) else (200, 195, 190),
                  sp(t, 0.1))


# ---------------------------------------------------------------- block 2: spring stack -> table
COLS = [("Kanal", 0), ("Narx", 245), ("Muddat", 420), ("Format", 565), ("Ko‘rish", 725)]


def table(img, t, order, row_t0=0.0, highlight=None, y_top=None):
    """Comparison table; rows animate to their slot in `order` (list of channel indexes)."""
    yt = y_top or (Y0 + 70)
    card(img, (X0 + 40, yt, X1 - 40, yt + 640), r=36)
    d = ImageDraw.Draw(img)
    for name, x in COLS:
        d.text((X0 + 80 + x, yt + 34), name, font=font(28, "Bold"), fill=MUTED)
    d.line([(X0 + 70, yt + 90), (X1 - 70, yt + 90)], fill=(228, 224, 219), width=3)
    for idx, c in enumerate(CHANNELS):
        slot = order.index(idx)
        y = yt + 120 + slot * 165
        if highlight == idx:
            d.rounded_rectangle((X0 + 60, y - 14, X1 - 60, y + 130), radius=26, fill=(250, 232, 222))
        d.rounded_rectangle((X0 + 80, y + 12, X0 + 150, y + 82), radius=18, fill=c["col"])
        d.text((X0 + 80 + 90, y + 24), c["n"], font=font(34, "Black"), fill=INK)
        vals = [fmt_k(c["price"]), c["dur"], c["fmt"], f"{c['views']:,}".replace(",", " ")]
        for (name, x), v in zip(COLS[1:], vals):
            d.text((X0 + 80 + x, y + 26), v, font=font(30 if name != "Format" else 26, "Bold"), fill=INK)


def block2(img, t, envs):
    # 0–2.2s: spring stack of three cards fanning out; 2.2–3.2s: they fly into table rows
    fly = ease(prog(t, 2.2, 3.2))
    if fly < 1:
        for i, c in enumerate(CHANNELS):
            fan = spring(prog(t, 0.2 + i * 0.12, 0.8 + i * 0.12))
            ang = (-8 + i * 8) * fan
            x = CX - 280 + (i - 1) * 60 * fan
            y = Y0 + 300 + (i - 1) * 30 * fan
            tx, ty = X0 + 40, Y0 + 190 + i * 165
            x = x + (tx - x) * fly
            y = y + (ty - y) * fly
            chat_card(img, x, y, 560, c["n"], [fmt_k(c["price"]), f"{c['dur']} · {c['fmt']}"], c["col"],
                      1 - fly * 0.6, tilt=ang * (1 - fly))
        d = ImageDraw.Draw(img)
        # easing curve chip (as in ref11)
        card(img, (X1 - 230, Y0 + 50, X1 - 50, Y0 + 170), r=22)
        d = ImageDraw.Draw(img)
        pts = [(X1 - 210 + u * 140, Y0 + 145 - 80 * spring(u)) for u in [i / 20 for i in range(21)]]
        d.line(pts, fill=ORANGE, width=5)
        u = clamp(t / 2.2)
        d.ellipse((pts[int(u * 20)][0] - 8, pts[int(u * 20)][1] - 8, pts[int(u * 20)][0] + 8, pts[int(u * 20)][1] + 8),
                  fill=INK)
    if fly > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        table(layer, t, [0, 1, 2])
        a = layer.getchannel("A").point(lambda v: int(v * fly))
        layer.putalpha(a)
        img.alpha_composite(layer)
    if t > 4.0:
        k = sp(t, 4.0)
        chip(img, int(X0 + 40), int(Y0 + 760), "Hammasi bitta ekranda", fill=ORANGE, color=(255, 255, 255),
             size=int(32 * max(0.3, k)) + 1)


# ---------------------------------------------------------------- block 3: tabs sort the rows
TABS3 = [("Narx", lambda c: c["price"]), ("Ko‘rish", lambda c: -c["views"]), ("1000 ko‘rish", lambda c: c["cpm"])]


def block3(img, t, envs):
    switches = [0.0, 2.6, 5.2]
    a = max(i for i, s in enumerate(switches) if t >= s)
    prev = max(0, a - 1)
    k = spring(prog(t, switches[a], switches[a] + 0.5))
    # tabs
    card(img, (X0 + 40, Y0 + 40, X1 - 40, Y0 + 150), r=55, fill=(246, 243, 240))
    tw = (X1 - X0 - 100) / 3
    tx = lambda i: X0 + 50 + i * tw
    sx = tx(prev) + (tx(a) - tx(prev)) * k
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((sx, Y0 + 50, sx + tw, Y0 + 140), radius=45, fill=INK)
    for i, (name, _) in enumerate(TABS3):
        f = font(34, "Bold")
        w_ = d.textbbox((0, 0), name, font=f)[2]
        on = abs(tx(i) - sx) < tw / 2
        d.text((tx(i) + (tw - w_) / 2, Y0 + 75), name, font=f, fill=(255, 255, 255) if on else MUTED)
    # rows sorted by the active tab, animating from previous order
    order_prev = sorted(range(3), key=lambda i: TABS3[prev][1](CHANNELS[i]))
    order_now = sorted(range(3), key=lambda i: TABS3[a][1](CHANNELS[i]))
    card(img, (X0 + 40, Y0 + 190, X1 - 40, Y0 + 860), r=36)
    d = ImageDraw.Draw(img)
    for idx, c in enumerate(CHANNELS):
        y_prev = Y0 + 230 + order_prev.index(idx) * 200
        y_now = Y0 + 230 + order_now.index(idx) * 200
        y = y_prev + (y_now - y_prev) * k + 4 * math.sin(t * 2 + idx)
        best = order_now.index(idx) == 0
        if best:
            d.rounded_rectangle((X0 + 60, y - 10, X1 - 60, y + 160), radius=26, fill=(250, 232, 222))
        d.rounded_rectangle((X0 + 90, y + 30, X0 + 180, y + 120), radius=22, fill=c["col"])
        d.text((X0 + 210, y + 26), c["n"], font=font(40, "Black"), fill=INK)
        metric = [fmt_k(c["price"]), f"{c['views']:,} ko‘rish".replace(",", " "),
                  f"{c['cpm']:.0f} ming / 1000"][a]
        d.text((X0 + 210, y + 82), metric, font=font(34, "Bold"), fill=ORANGE if best else MUTED)
        if best:
            chip(img, int(X1 - 260), int(y + 52), "eng yaxshi", fill=GREEN, color=(255, 255, 255), size=28)
            d = ImageDraw.Draw(img)
    # cursor drives the tab switches
    nxt = next((s for s in switches if s > t), None)
    if nxt is not None:
        i_n = switches.index(nxt)
        m = ease(prog(t, nxt - 1.1, nxt - 0.15))
        cx_ = tx(a) + tw / 2 + (tx(i_n) - tx(a)) * m
        cursor(img, cx_, Y0 + 115 + 10 * math.sin(t * 1.5), clamp(1 - abs(t - nxt + 0.05) / 0.2))
    else:
        cursor(img, tx(a) + tw / 2 + 20 * math.sin(t), Y0 + 125, 0)


# ---------------------------------------------------------------- block 4: chart morph + zoom
def block4(img, t, envs):
    card(img, (X0 + 40, Y0 + 50, X1 - 40, Y0 + 720), r=36)
    d = ImageDraw.Draw(img)
    morph = ease(prog(t, 1.4, 2.6))
    title = "Narx (ming so‘m)" if morph < 0.5 else "1000 ko‘rish narxi"
    d.text((X0 + 80, Y0 + 90), title, font=font(40, "Black"), fill=INK)
    chip(img, int(X1 - 270), int(Y0 + 88), "shartli misol", fill=(240, 236, 232), color=MUTED, size=24)
    d = ImageDraw.Draw(img)
    base = Y0 + 620
    maxh = 380
    xs = [X0 + 200 + i * 250 for i in range(3)]
    pts = []
    for i, c in enumerate(CHANNELS):
        hp = maxh * c["price"] / 300 * sp(t, 0.2 + i * 0.12, 0.5)
        hc = maxh * c["cpm"] / 80
        h = hp + (hc - hp) * morph
        bw = 120 * (1 - morph) + 8 * morph
        col = c["col"]
        d.rounded_rectangle((xs[i] - bw / 2, base - max(2, h), xs[i] + bw / 2, base), radius=int(min(20, bw / 2)),
                            fill=col if morph < 0.95 else (230, 226, 222))
        pts.append((xs[i], base - h))
        lab = fmt_k(c["price"]) if morph < 0.5 else f"{c['cpm']:.0f} ming"
        f = font(32, "Black")
        tw = d.textbbox((0, 0), lab, font=f)[2]
        lx = xs[i] - tw / 2 + (60 * morph if i == 2 else 0)
        d.text((lx, base - h - 54 - (10 * morph if i == 2 else 0)), lab, font=f, fill=INK)
        tw = d.textbbox((0, 0), c["n"], font=font(28, "Bold"))[2]
        d.text((xs[i] - tw / 2, base + 18), c["n"], font=font(28, "Bold"), fill=MUTED)
    if morph > 0.05:
        d.line(pts, fill=INK, width=int(6 * morph) + 1)
        for (x, y) in pts:
            r = 12 * morph
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255), outline=INK, width=5)
    # dashboard zoom: the best point gets brackets, then a KPI card rises
    if t > 3.2:
        kb = sp(t, 3.2, 0.4)
        x, y = pts[2]
        for sxx, syy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            L = 28 * kb
            bx, by = x + sxx * 46, y + syy * 46
            d.line([(bx, by), (bx - sxx * L, by)], fill=ORANGE, width=6)
            d.line([(bx, by), (bx, by - syy * L)], fill=ORANGE, width=6)
    kz = sp(t, 4.0, 0.6)
    if kz > 0:
        y0 = Y0 + 760 + (1 - clamp(kz)) * 80
        card(img, (X0 + 40, y0, X1 - 40, y0 + 200), r=34, alpha=int(255 * clamp(kz)))
        d = ImageDraw.Draw(img)
        d.text((X0 + 80, y0 + 30), "3-kanal — eng foydali", font=font(40, "Black"), fill=INK)
        d.text((X0 + 80, y0 + 96), "250 ming, lekin 1000 ko‘rish ≈ 36 ming so‘m", font=font(32, "Bold"), fill=GREEN)
        chip(img, int(X1 - 250), int(y0 + 34), "−52%", fill=GREEN, color=(255, 255, 255), size=34)


# ---------------------------------------------------------------- block 5: save CTA
def block5(img, t, envs):
    tt = t + 32
    spr = rustam("none", brows=24, tilt=-10, eye=1.2, look=8, mouth=voice.mouth(envs, "rus8", tt, "grin"))
    avatar_circle(img, spr, CX - 230, Y0 + 210, 220, ORANGE if voice.speaking(envs, "rus8", tt) else (200, 195, 190),
                  sp(t, 0.0))
    d = ImageDraw.Draw(img)
    # crossed-out abacus (callback to 2-qism)
    ka = sp(t, 0.3)
    ax, ay = CX + 200, Y0 + 210
    if ka > 0:
        card(img, (ax - 150 * ka, ay - 110 * ka, ax + 150 * ka, ay + 110 * ka), r=28)
        d = ImageDraw.Draw(img)
        if ka > 0.7:
            for r in range(4):
                yy = ay - 60 + r * 40
                d.line([(ax - 110, yy), (ax + 110, yy)], fill=(190, 170, 140), width=5)
                for b in range(5):
                    bx = ax - 90 + b * 34 + (40 if b > 2 else 0)
                    d.ellipse((bx - 14, yy - 14, bx + 14, yy + 14), fill=[ORANGE, (220, 170, 60)][b % 2])
            kx = sp(t, 0.9, 0.35)
            s = 120 * kx
            d.line([(ax - s, ay - s * 0.8), (ax + s, ay + s * 0.8)], fill=RED, width=14)
            d.line([(ax - s, ay + s * 0.8), (ax + s, ay - s * 0.8)], fill=RED, width=14)
    # save button grows, cursor clicks, bookmark burst
    kb = sp(t, 1.4, 0.5)
    by = Y0 + 470
    saved = t > 3.0
    if kb > 0:
        bw = 560 * kb
        card(img, (CX - bw / 2, by, CX + bw / 2, by + 140), r=70, fill=NAVY if saved else (255, 255, 255))
        d = ImageDraw.Draw(img)
        if kb > 0.7:
            # bookmark icon
            bx = CX - 170
            col = (255, 255, 255) if saved else INK
            d.polygon([(bx - 22, by + 38), (bx + 22, by + 38), (bx + 22, by + 104), (bx, by + 86), (bx - 22, by + 104)],
                      fill=col if saved else None, outline=col, width=5)
            d.text((bx + 50, by + 40), "Saqlandi" if saved else "Saqlash", font=font(52, "Black"), fill=col)
    if 3.0 < t < 4.2:
        kb2 = prog(t, 3.0, 4.2)
        for a in range(0, 360, 24):
            r0, r1 = 160 + 160 * kb2, 200 + 230 * kb2
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            col = tuple(int(c * (1 - kb2) + p * kb2) for c, p in zip(ORANGE, PAGE))
            d.line([(CX + ca * r0, by + 70 + sa * r0), (CX + ca * r1, by + 70 + sa * r1)], fill=col, width=8)
    cx_ = CX + 330 - 300 * ease(prog(t, 1.8, 2.8)) + 6 * math.sin(t * 2)
    cy_ = by + 260 - 180 * ease(prog(t, 1.8, 2.8))
    cursor(img, cx_, cy_, clamp(1 - abs(t - 2.95) / 0.2))
    if t > 4.4:
        k = sp(t, 4.4)
        chip(img, int(CX - 270), int(by + 230), "Ertaga: buyurtma holatini kuzatamiz", fill=(255, 255, 255),
             color=ORANGE, size=int(30 * max(0.3, k)) + 1)


BLOCK_FN = [block1, block2, block3, block4, block5]
_envs = [None]


def camera(img, t, a, b):
    """Constant-speed push + pan — never slows to a stop (lesson from 9-qism)."""
    k = clamp((t - a) / max(b - a, 0.1))
    z = 1.02 + 0.07 * k
    dx = -20 + 40 * k + 6 * math.sin(t * 1.3)
    dy = 8 * math.cos(t * 0.9)
    nw, nh = int(W * z), int(H * z)
    big = img.resize((nw, nh), Image.BICUBIC)
    x0 = int((nw - W) / 2 + dx)
    y0 = int((nh - H) / 2 + dy)
    return big.crop((x0, y0, x0 + W, y0 + H))


def frame(t, envs, timings):
    bi = min(4, int(t // 8))
    lt = t - bi * 8
    img = page(*BLOCKS[bi])
    BLOCK_FN[bi](img, lt, envs)
    if lt < 0.35 and bi > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), PAGE + (int(255 * (1 - lt / 0.35)),)))
    if voice.speaking(envs, "narr", t):
        spr = founder(mouth=voice.mouth(envs, "narr", t, "closed"))
        avatar_circle(img, spr, W - 110, 210, 110, NAVY, 1.0)
    img = camera(img, t, bi * 8, bi * 8 + 8)
    for (a, b, who, s) in timings:
        if a - 0.05 <= t <= b + 0.25:
            subtitle(img, s, INK if who == "narr" else (150, 70, 40))
    return img


def music_and_sfx():
    buf = np.zeros(int(SR * DUR) + SR)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 98
    prog_ = [(57, 60, 64, 67), (53, 57, 60, 64), (60, 64, 67, 71), (55, 59, 62, 65)]
    t, n = 0.0, 0
    while t < DUR - 0.5:
        chord = prog_[int(n / 4) % 4]
        if n % 4 == 0:
            for m in chord:
                add(buf, tone(note(m), beat * 4, decay=0.5, harmonics=(1, 0.15), vol=0.045), t)
            add(buf, tone(note(chord[0] - 24), beat * 3, decay=1.0, harmonics=(1, 0.4), vol=0.16), t)
        if n % 2 == 0:
            add(buf, tone(60, 0.25, decay=18, harmonics=(1, 0.3), vol=0.32), t)
        add(buf, noise(0.04, 0.11, 1) * np.exp(-80 * np.arange(int(0.04 * SR)) / SR), t + beat / 2)
        add(buf, tone(note(chord[(n * 2) % 4] + 12), 0.3, decay=9, harmonics=(1, 0.2), vol=0.04), t + beat / 2)
        t += beat
        n += 1
    for b in (8, 16, 24, 32):
        add(buf, noise(0.4, 0.2, 40) * np.sin(np.linspace(0, np.pi, int(0.4 * SR))), b - 0.2)
    for i in range(3):  # chat cards ding
        add(buf, tone(1318, 0.4, decay=9, harmonics=(1, 0.3), vol=0.18), 0.4 + i * 0.9)
    for i in range(3):  # cards fly into the table
        add(buf, tone(880 + i * 120, 0.15, decay=22, harmonics=(1, 0.3), vol=0.18), 10.3 + i * 0.12)
    for s in (18.6, 21.2):  # tab clicks
        add(buf, tone(1500, 0.06, decay=60, harmonics=(1,), vol=0.28), s)
    add(buf, noise(0.8, 0.2, 10) * np.linspace(0, 1, int(0.8 * SR)), 25.2)  # morph riser
    add(buf, tone(1046, 0.5, decay=6, harmonics=(1, 0.3), vol=0.25), 28.0)    # KPI pop
    add(buf, tone(70, 0.4, decay=8, harmonics=(1, 0.5), vol=0.6), 32.9)       # abacus cross
    for i, f in enumerate((1046, 1318, 1568, 2093)):                          # save + burst
        add(buf, tone(f, 0.6, decay=6, harmonics=(1, 0.2), vol=0.18), 35.0 + i * 0.05)
    return buf[: int(SR * DUR)]


def main(out, qa_only=False, preview=None):
    tmp = tempfile.mkdtemp()
    speech, envs, timings = voice.build_speech(LINES, DUR, FPS, tmp)
    problems = voice.qa(LINES, timings, speech)
    if qa_only:
        sys.exit(1 if problems else 0)
    if preview:
        for ts in preview:
            frame(float(ts), envs, timings).convert("RGB").save(f"preview10_{ts}.png")
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
        main(None, preview=sys.argv[2:])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_10-kun.mp4")
