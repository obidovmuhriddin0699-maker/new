"""ADUZ · 9-qism — "Hudud bo'yicha kanal tanlash" (motion uslubi A, MOTION_QOLLANMA.md).

5 ta 8 soniyalik blok (har biri o'z sarlavhasi bilan, ref02–ref11 dagi kabi):
 01 Noto'g'ri hudud      — Flowing paths: Toshkent kanali ↔ Farg'onadagi do'kon
 02 Search → results     — "Farg'ona · mebel" qidiruvi, natijalar ketma-ket tushadi
 03 Tabs → panels        — viloyat tablari, panel almashadi
 04 Dashboard zoom       — kanal kartochkasidagi "Hudud" plitkasi kattalashadi
 05 Follow → CTA         — kursor "Yuborish" ni bosadi, yulduzcha portlash (ref01)

Ishga tushirish:  python3 make_day9.py <chiqish.mp4>   |   python3 make_day9.py --qa
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
from motion_a import (CARD, GREEN, INK, INNER, MUTED, NAVY, ORANGE, RED, SKY, WIN, avatar_circle, card, chip,
                      cursor, dashed_rect, page, pin, sp, spring, subtitle)

SR = voice.SR
DUR = 40.0

LINES = [
    (0.3, "rus8", "[sad]Farg'onadagi do'konim uchun[p=100]Toshkent kanaliga reklama berdim...",
     "Farg‘onadagi do‘konim uchun Toshkent kanaliga reklama berdim...", 1.12),
    (5.0, "rus8", "[ironic]Toshkentdan divan olgani kim keladi?!", "Toshkentdan divan olgani kim keladi?!", 1.06),
    (8.4, "narr", "[happy]Aduzda kanallarni hudud va mavzu bo'yicha qidirasiz.",
     "ADUZ'da kanallarni hudud va mavzu bo‘yicha qidirasiz.", 0.96),
    (12.4, "narr", "[excited]Farg'ona, mebel —[p=100]mos kanallar darhol chiqadi!",
     "Farg‘ona, mebel — mos kanallar darhol chiqadi!", 0.96),
    (16.4, "narr", "[warm]Mijozingiz qayerda bo'lsa,[p=100]reklamangiz ham o'sha yerda bo'lsin.",
     "Mijozingiz qayerda bo‘lsa, reklamangiz ham o‘sha yerda bo‘lsin.", 0.96),
    (24.4, "narr", "[neutral]Har bir kanal qaysi hududga mo'ljallangani oldindan ko'rinadi.",
     "Har bir kanal qaysi hududga mo‘ljallangani oldindan ko‘rinadi.", 0.96),
    (28.9, "rus8", "[excited]Endi Farg'ona kanallarini topdim![p=150][worried]Narxlari-chi?",
     "Endi Farg‘ona kanallarini topdim! Narxlari-chi?", 1.06),
    (33.4, "narr", "[happy]Mahalliy biznes egasi do'stingizga yuboring![p=150]Ertaga narxlarni solishtiramiz.",
     "Mahalliy biznes egasi do‘stingizga yuboring! Ertaga narxlarni solishtiramiz.", 0.97),
]

BLOCKS = [
    ("01", "Noto‘g‘ri hudud", "Reklama bor — mijoz yo‘q.", "do‘kon, kafe, xizmat egalari."),
    ("02", "Qidiruv → natijalar", "Hudud va mavzu yozing — kanallar tushadi.", "mos kanalni tez topish."),
    ("03", "Viloyat → kanallar", "Tab almashadi, ro‘yxat yangilanadi.", "bir nechta viloyatda ishlaydiganlar."),
    ("04", "Kanal → hudud", "Kanal kimga mo‘ljallangani ko‘rinadi.", "byudjetni to‘g‘ri sarflash."),
    ("05", "Yuboring", "Mahalliy biznes egasi do‘stingizga.", "mahalliy tadbirkorlar."),
]

X0, Y0, X1, Y1 = WIN
CX = (X0 + X1) / 2


# ---------------------------------------------------------------- block 1: wrong region (flowing path)
def block1(img, t, envs):
    d = ImageDraw.Draw(img)
    # two location cards
    k1, k2 = sp(t, 0.2), sp(t, 0.6)
    tx, ty = 290, 640          # Toshkent
    fx, fy = 790, 980          # Farg'ona
    if k1 > 0:
        card(img, (tx - 190, ty - 120, tx + 190, ty + 120 * k1), r=30)
        d = ImageDraw.Draw(img)
        if k1 > 0.6:
            pin(d, tx - 110, ty + 20, NAVY, "", 0.8)
            d.text((tx - 50, ty - 70), "Toshkent", font=font(40, "Black"), fill=INK)
            d.text((tx - 50, ty - 18), "kanal · 120 ming", font=font(28, "SemiBold"), fill=MUTED)
            d.text((tx - 50, ty + 26), "auditoriya: Toshkent", font=font(28, "SemiBold"), fill=NAVY)
    if k2 > 0:
        card(img, (fx - 190, fy - 120, fx + 190, fy + 120 * k2), r=30)
        d = ImageDraw.Draw(img)
        if k2 > 0.6:
            pin(d, fx - 110, fy + 20, ORANGE, "", 0.8)
            d.text((fx - 50, fy - 70), "Farg‘ona", font=font(40, "Black"), fill=INK)
            d.text((fx - 50, fy - 18), "Rustam Mebel", font=font(28, "SemiBold"), fill=MUTED)
            d.text((fx - 50, fy + 26), "do‘kon shu yerda", font=font(28, "SemiBold"), fill=ORANGE)
    # flowing dashed path between them (dashes keep moving -> never static)
    pk = ease(prog(t, 1.0, 2.2))
    if pk > 0:
        n = 40
        pts = []
        for i in range(n + 1):
            u = i / n * pk
            sx_, sy_, ex_, ey_ = tx + 195, ty - 20, fx + 40, fy - 130
            x = sx_ + (ex_ - sx_) * u
            y = sy_ + (ey_ - sy_) * u - 150 * math.sin(math.pi * u)
            pts.append((x, y))
        off = int(t * 12) % 2
        for i in range(off, len(pts) - 1, 2):
            d.line([pts[i], pts[i + 1]], fill=(150, 140, 130), width=6)
        if pk > 0.95:
            mx, my = pts[n // 2]
            chip(img, int(mx - 40), int(my - 100), "≈ 300 km", fill=(255, 255, 255), color=INK, size=30)
    # people of the channel audience gather around Tashkent, not around the shop
    for i in range(6):
        k = sp(t, 2.4 + i * 0.12, 0.35)
        if k <= 0:
            continue
        px = tx - 150 + i * 62 + 6 * math.sin(t * 3 + i)
        py = ty + 230 + 10 * math.cos(t * 2.5 + i)
        r = 22 * k
        d.ellipse((px - r, py - r - 26, px + r, py + r - 26), fill=SKY)
        d.chord((px - 1.5 * r, py - 4, px + 1.5 * r, py + 2.6 * r), 180, 360, fill=SKY)
    # big red cross over the path once Rustam realises
    if t > 5.1:
        k = sp(t, 5.1, 0.35)
        cx_, cy_ = (tx + 195 + fx + 40) / 2, (ty - 20 + fy - 130) / 2 - 150
        s = 70 * k
        d.line([(cx_ - s, cy_ - s), (cx_ + s, cy_ + s)], fill=RED, width=18)
        d.line([(cx_ - s, cy_ + s), (cx_ + s, cy_ - s)], fill=RED, width=18)
    # Rustam avatar with "speaking" ring
    talk = voice.speaking(envs, "rus8", t)
    spr = rustam("none", brows=20 if t > 5.0 else -2, tilt=-10 if t > 5.0 else 8, eye=1.15 if t > 5.0 else 0.7,
                 mouth=voice.mouth(envs, "rus8", t, "frown"))
    avatar_circle(img, spr, 230, 1180, 170, ORANGE if talk else (200, 195, 190), sp(t, 0.1))


# ---------------------------------------------------------------- block 2: search -> results
RESULTS = [("Farg‘ona Bugun", "Farg‘ona · yangiliklar", "30 ming", ORANGE),
           ("Vodiy e’lonlari", "Farg‘ona · e’lonlar", "18 ming", SKY),
           ("Marg‘ilon uylari", "Farg‘ona · uy-ro‘zg‘or", "12 ming", INK)]


def block2(img, t, envs):
    query = "Farg‘ona · mebel"
    n = int(len(query) * clamp((t - 0.5) / 1.6))
    card(img, (X0 + 50, Y0 + 60, X1 - 50, Y0 + 170), r=55)
    d = ImageDraw.Draw(img)
    d.ellipse((X0 + 90, Y0 + 92, X0 + 132, Y0 + 134), outline=INK, width=6)
    d.line([(X0 + 126, Y0 + 128), (X0 + 146, Y0 + 148)], fill=INK, width=7)
    shown = query[:n] if n else ""
    d.text((X0 + 170, Y0 + 88), shown or "Qidirish", font=font(46, "Bold"),
           fill=INK if shown else (170, 165, 160))
    if int(t * 2.4) % 2 == 0:  # blinking caret
        cw = d.textbbox((0, 0), shown, font=font(46, "Bold"))[2] if shown else 0
        d.rectangle((X0 + 172 + cw, Y0 + 90, X0 + 176 + cw, Y0 + 140), fill=ORANGE)
    for i, (name, sub_, subs, col) in enumerate(RESULTS):
        k = sp(t, 2.3 + i * 0.14, 0.5)
        if k <= 0:
            continue
        y = Y0 + 220 + i * 210 + (1 - k) * 60 + 4 * math.sin(t * 2 + i)
        card(img, (X0 + 50, y, X1 - 50, y + 180), r=34, alpha=int(255 * clamp(k)))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((X0 + 80, y + 40, X0 + 180, y + 140), radius=24, fill=col)
        d.text((X0 + 210, y + 38), name, font=font(44, "Black"), fill=INK)
        d.text((X0 + 210, y + 98), sub_, font=font(30, "SemiBold"), fill=MUTED)
        chip(img, int(X1 - 260), int(y + 62), subs, fill=(244, 240, 236), color=INK, size=30)
    if t > 3.3:  # region filter chip pulses
        k = 0.5 + 0.5 * math.sin(t * 4)
        chip(img, int(X0 + 50), int(Y0 + 880), "Hudud: Farg‘ona", fill=ORANGE, color=(255, 255, 255), size=32)
        chip(img, int(X0 + 380), int(Y0 + 880), "Mavzu: mebel, uy", fill=(255, 255, 255), color=INK, size=32)


# ---------------------------------------------------------------- block 3: tabs -> panels
TABS = ["Farg‘ona", "Andijon", "Namangan"]
PANELS = {
    0: [("Farg‘ona Bugun", "30 ming"), ("Vodiy e’lonlari", "18 ming"), ("Marg‘ilon uylari", "12 ming")],
    1: [("Andijon 24", "41 ming"), ("Asaka e’lonlari", "9 ming"), ("Andijon bozori", "15 ming")],
    2: [("Namangan tongi", "27 ming"), ("Chust yangiliklari", "8 ming"), ("Namangan uylari", "11 ming")],
}


def block3(img, t, envs):
    # active tab cycles: 0 -> 1 -> 2 -> 0, cursor drives it
    switches = [0.0, 2.2, 4.4, 6.6]
    active = max(i for i, s in enumerate(switches) if t >= s) % 3
    prev = (active - 1) % 3
    kswap = spring(prog(t, switches[max(i for i, s in enumerate(switches) if t >= s)],
                        switches[max(i for i, s in enumerate(switches) if t >= s)] + 0.45))
    card(img, (X0 + 50, Y0 + 60, X1 - 50, Y0 + 180), r=60, fill=(246, 243, 240))
    tab_w = (X1 - X0 - 120) / 3
    tx = lambda i: X0 + 60 + i * tab_w
    sel_x = tx(prev) + (tx(active) - tx(prev)) * kswap
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((sel_x, Y0 + 70, sel_x + tab_w, Y0 + 170), radius=50, fill=INK)
    for i, name in enumerate(TABS):
        f = font(40, "Bold")
        tw = d.textbbox((0, 0), name, font=f)[2]
        on = abs(tx(i) - sel_x) < tab_w / 2
        d.text((tx(i) + (tab_w - tw) / 2, Y0 + 96), name, font=f, fill=(255, 255, 255) if on else MUTED)
    rows = PANELS[active]
    card(img, (X0 + 50, Y0 + 230, X1 - 50, Y0 + 860), r=40)
    d = ImageDraw.Draw(img)
    d.text((X0 + 90, Y0 + 270), f"{TABS[active]} kanallari", font=font(44, "Black"), fill=INK)
    chip(img, int(X1 - 200), int(Y0 + 268), str(len(rows) * 4), fill=(250, 226, 214), color=ORANGE, size=30)
    for j, (name, subs) in enumerate(rows):
        k = sp(t - switches[max(i for i, s in enumerate(switches) if t >= s)], 0.1 + j * 0.1, 0.4)
        y = Y0 + 370 + j * 150 + (1 - k) * 40
        col = [ORANGE, SKY, INK][j]
        d.rounded_rectangle((X0 + 90, y, X0 + 170, y + 80), radius=18, fill=col)
        d.text((X0 + 200, y + 14), name, font=font(40, "Bold"), fill=INK)
        tw = d.textbbox((0, 0), subs, font=font(38, "Bold"))[2]
        d.text((X1 - 100 - tw, y + 16), subs, font=font(38, "Bold"), fill=MUTED)
    # cursor travels to the next tab before each switch
    nxt = (active + 1) % 3
    nxt_t = next((s for s in switches if s > t), 8.8)
    move = ease(prog(t, nxt_t - 1.2, nxt_t - 0.2))
    cx_ = tx(active) + tab_w / 2 + (tx(nxt) + tab_w / 2 - tx(active) - tab_w / 2) * move
    press = clamp(1 - abs(t - nxt_t + 0.1) / 0.25)
    cursor(img, cx_, Y0 + 130 + 20 * math.sin(t * 1.3), press)


# ---------------------------------------------------------------- block 4: dashboard zoom
def block4(img, t, envs):
    # overview card of a channel
    card(img, (X0 + 50, Y0 + 60, X1 - 50, Y0 + 560), r=40)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((X0 + 90, Y0 + 100, X0 + 200, Y0 + 210), radius=26, fill=ORANGE)
    d.text((X0 + 230, Y0 + 104), "Farg‘ona Bugun", font=font(48, "Black"), fill=INK)
    d.text((X0 + 230, Y0 + 166), "yangiliklar · e’lonlar", font=font(30, "SemiBold"), fill=MUTED)
    tiles = [("Obunachi", "30 000"), ("O‘rt. ko‘rish", "7 000"), ("Hudud", "Farg‘ona")]
    tw = (X1 - X0 - 160) / 3
    for i, (a, b) in enumerate(tiles):
        x = X0 + 70 + i * (tw + 10)
        d.rounded_rectangle((x, Y0 + 270, x + tw, Y0 + 500), radius=24, fill=(244, 241, 237))
        d.text((x + 24, Y0 + 300), a, font=font(28, "SemiBold"), fill=MUTED)
        d.text((x + 24, Y0 + 350), b, font=font(40 if i < 2 else 36, "Black"), fill=INK)
    # brackets around the "Hudud" tile, then it zooms out into a big card
    hx = X0 + 70 + 2 * (tw + 10)
    kb = sp(t, 0.6, 0.4)
    if kb > 0:
        for (bx, by, sx, sy) in ((hx - 12, Y0 + 258, 1, 1), (hx + tw + 12, Y0 + 258, -1, 1),
                                 (hx - 12, Y0 + 512, 1, -1), (hx + tw + 12, Y0 + 512, -1, -1)):
            L = 34 * kb
            d.line([(bx, by), (bx + sx * L, by)], fill=ORANGE, width=6)
            d.line([(bx, by), (bx, by + sy * L)], fill=ORANGE, width=6)
    kz = sp(t, 1.4, 0.6)
    if kz > 0:
        bx0 = hx + (X0 + 50 - hx) * kz
        by0 = Y0 + 270 + (Y0 + 470 - Y0 - 270) * kz
        bx1 = hx + tw + (X1 - 50 - hx - tw) * kz
        by1 = Y0 + 500 + (Y0 + 930 - Y0 - 500) * kz
        card(img, (bx0, by0, bx1, by1), r=36)
        d = ImageDraw.Draw(img)
        if kz > 0.7:
            d.text((bx0 + 40, by0 + 36), "Auditoriya qayerda?", font=font(40, "Black"), fill=INK)
            chip(img, int(bx1 - 250), int(by0 + 34), "shartli misol", fill=(240, 236, 232), color=MUTED, size=24)
            bars = [("Farg‘ona", 0.78, ORANGE), ("Andijon", 0.12, SKY), ("Boshqa", 0.10, (190, 185, 180))]
            for j, (name, v, col) in enumerate(bars):
                y = by0 + 120 + j * 92
                grow = ease(prog(t, 2.2 + j * 0.2, 3.2 + j * 0.2)) * (1 + 0.01 * math.sin(t * 3 + j))
                d.text((bx0 + 40, y + 6), name, font=font(32, "Bold"), fill=INK)
                wmax = (bx1 - bx0) - 380
                d.rounded_rectangle((bx0 + 230, y + 8, bx0 + 230 + max(16, wmax * v * grow), y + 48), radius=20,
                                    fill=col)
                d.text((bx0 + 250 + wmax * v * grow, y + 6), f"{int(v * 100 * min(1, grow))}%",
                       font=font(32, "Black"), fill=INK)


# ---------------------------------------------------------------- block 5: share CTA with burst
def block5(img, t, envs):
    talk_r = voice.speaking(envs, "rus8", t + 32)
    spr = rustam("none", brows=26, tilt=-10, eye=1.2, look=10,
                 mouth=voice.mouth(envs, "rus8", t + 32, "grin"))
    avatar_circle(img, spr, CX, Y0 + 230, 260, ORANGE if talk_r else (200, 195, 190), sp(t, 0.0))
    d = ImageDraw.Draw(img)
    kk = sp(t, 0.4)
    if kk > 0:
        f = font(max(8, int(54 * kk)), "Black")
        for j, s in enumerate(["Mahalliy biznes egasi", "do‘stingizga yuboring"]):
            tw = d.textbbox((0, 0), s, font=f)[2]
            d.text((CX - tw / 2, Y0 + 430 + j * 70), s, font=f, fill=INK)
    # the button grows from a pill (button -> state), cursor clicks it, burst
    kb = sp(t, 1.4, 0.5)
    bw = 520 * kb
    by = Y0 + 640
    pressed = t > 3.2
    if kb > 0:
        card(img, (CX - bw / 2, by, CX + bw / 2, by + 130), r=65, fill=NAVY if pressed else (255, 255, 255))
        d = ImageDraw.Draw(img)
        label = "Yuborildi!" if pressed else "Yuborish"
        f = font(52, "Black")
        tw = d.textbbox((0, 0), label, font=f)[2]
        if kb > 0.7:
            d.text((CX - tw / 2, by + 34), label, font=f, fill=(255, 255, 255) if pressed else INK)
    if 3.2 < t < 4.4:  # starburst (ref01 Follow)
        kb2 = prog(t, 3.2, 4.4)
        for a in range(0, 360, 24):
            r0, r1 = 150 + 160 * kb2, 190 + 230 * kb2
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            d.line([(CX + ca * r0, by + 65 + sa * r0), (CX + ca * r1, by + 65 + sa * r1)],
                   fill=tuple(int(c * (1 - kb2) + p * kb2) for c, p in zip(ORANGE, (235, 233, 229))), width=8)
    cx_ = CX + 330 - 300 * ease(prog(t, 2.0, 3.0)) + 6 * math.sin(t * 2)
    cy_ = by + 260 - 180 * ease(prog(t, 2.0, 3.0))
    cursor(img, cx_, cy_, clamp(1 - abs(t - 3.15) / 0.2))
    if t > 4.6:
        k = sp(t, 4.6)
        chip(img, int(CX - 230), int(by + 220), "Ertaga: narxlarni solishtiramiz", fill=(255, 255, 255),
             color=ORANGE, size=int(30 * max(0.3, k)) + 1)


BLOCK_FN = [block1, block2, block3, block4, block5]


def camera(img, t, a, b):
    """Continuous gentle camera (push-in per block + drift) — the picture never stands still."""
    k = clamp((t - a) / max(b - a, 0.1))
    z = 1.015 + 0.04 * ease(k) + 0.006 * math.sin(t * 1.7)
    dx = 14 * math.sin(t * 0.8)
    dy = 10 * math.cos(t * 0.65)
    nw, nh = int(W * z), int(H * z)
    big = img.resize((nw, nh), Image.BICUBIC)
    x0 = int((nw - W) / 2 + dx)
    y0 = int((nh - H) / 2 + dy)
    return big.crop((x0, y0, x0 + W, y0 + H))


def frame(t, envs, timings):
    bi = min(4, int(t // 8))
    lt = t - bi * 8
    num, title, sub, use = BLOCKS[bi]
    img = page(num, title, sub, use)
    # block transition: content slides/fades in (no hard cut, no freeze)
    BLOCK_FN[bi](img, lt, envs)
    if lt < 0.35 and bi > 0:
        a = 1 - lt / 0.35
        img.alpha_composite(Image.new("RGBA", (W, H), (235, 233, 229, int(255 * a))))
    img = camera(img, t, bi * 8, bi * 8 + 8)
    for (a, b, who, s) in timings:
        if a - 0.05 <= t <= b + 0.25:
            subtitle(img, s, INK if who == "narr" else (150, 70, 40))
    # speaker chip for the founder voice
    if voice.speaking(timings_envs[0], "narr", t):
        spr = founder(mouth=voice.mouth(timings_envs[0], "narr", t, "closed"))
        avatar_circle(img, spr, W - 110, 210, 110, NAVY, 1.0)
    return img


timings_envs = [None]


# ---------------------------------------------------------------- audio: soft clean beat (pack-like)
def music_and_sfx():
    buf = np.zeros(int(SR * DUR) + SR)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 96
    prog_ = [(60, 64, 67, 71), (57, 60, 64, 67), (53, 57, 60, 64), (55, 59, 62, 65)]
    t, n = 0.0, 0
    while t < DUR - 0.5:
        chord = prog_[int(n / 4) % 4]
        if n % 4 == 0:
            for m in chord:
                add(buf, tone(note(m), beat * 4, decay=0.5, harmonics=(1, 0.15), vol=0.045), t)
            add(buf, tone(note(chord[0] - 24), beat * 3, decay=1.0, harmonics=(1, 0.4), vol=0.16), t)
        if n % 2 == 0:
            add(buf, tone(60, 0.25, decay=18, harmonics=(1, 0.3), vol=0.35), t)
        add(buf, noise(0.04, 0.12, 1) * np.exp(-80 * np.arange(int(0.04 * SR)) / SR), t + beat / 2)
        add(buf, tone(note(chord[(n * 2) % 4] + 12), 0.3, decay=9, harmonics=(1, 0.2), vol=0.045), t + beat / 2)
        t += beat
        n += 1
    for b in (8, 16, 24, 32):  # soft swoosh between blocks
        add(buf, noise(0.4, 0.2, 40) * np.sin(np.linspace(0, np.pi, int(0.4 * SR))), b - 0.2)
    for i in range(len("Farg‘ona · mebel")):  # typing clicks
        add(buf, noise(0.03, 0.15, 1) * np.exp(-90 * np.arange(int(0.03 * SR)) / SR), 8.5 + i * 0.1)
    for i in range(3):  # results pop
        add(buf, tone(988, 0.15, decay=22, harmonics=(1, 0.3), vol=0.2), 10.3 + i * 0.14)
    for s in (18.2, 20.4, 22.6):  # tab clicks
        add(buf, tone(1400, 0.06, decay=60, harmonics=(1,), vol=0.25), s)
    add(buf, tone(70, 0.4, decay=8, harmonics=(1, 0.5), vol=0.6), 5.1)  # red cross thud
    for i, f in enumerate((1046, 1318, 1568, 2093)):  # click + burst
        add(buf, tone(f, 0.6, decay=6, harmonics=(1, 0.2), vol=0.18), 35.2 + i * 0.05)
    return buf[: int(SR * DUR)]


def main(out, qa_only=False, preview=None):
    tmp = tempfile.mkdtemp()
    speech, envs, timings = voice.build_speech(LINES, DUR, FPS, tmp)
    timings_envs[0] = envs
    problems = voice.qa(LINES, timings, speech)
    if qa_only:
        sys.exit(1 if problems else 0)
    if preview:
        for ts in preview:
            frame(float(ts), envs, timings).convert("RGB").save(f"preview9_{ts}.png")
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
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_9-kun.mp4")
