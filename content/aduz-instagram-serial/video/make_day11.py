"""ADUZ · 11-qism — "Buyurtma holatini kuzatish" (motion uslubi A, MOTION_QOLLANMA.md).

 01 Beshinchi qo'ng'iroq  — qo'ng'iroqlar jurnali ketma-ket tushadi (stagger), hisoblagich 5
 02 Buyurtma → oyna        — Card → workspace: kichik "Buyurtma #12" kartasi to'liq buyurtma oynasiga o'sadi
 03 Holat bosqichlari      — Kutilmoqda → Tasdiqlandi → Joylandi (progress chizig'i, har qadam ovoz bilan)
 04 Bot xabar beradi       — telefon ekraniga bildirishnomalar prujina bilan tushadi (Spring stack)
 05 Izohda yozing          — "Necha marta qo'ng'iroq qilgansiz?" variantlari, kursor tanlaydi

Ishga tushirish:  python3 make_day11.py <chiqish.mp4>   |   python3 make_day11.py --qa
"""
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

import voice
from make_day2 import FPS, H, W, add, clamp, dilnoza, ease, font, noise, prog, rustam, tone
from make_day7 import founder
from motion_a import (GREEN, INK, MUTED, NAVY, ORANGE, PAGE, RED, SKY, WIN, avatar_circle, card, chip, cursor,
                      dashed_rect, page, sp, spring, subtitle)

SR = voice.SR
DUR = 40.0
X0, Y0, X1, Y1 = WIN
CX = (X0 + X1) / 2

LINES = [
    (0.3, "rus8", "[angry]Beshinchi marta qo'ng'iroq qilyapman...[p=150][shout]Chiqdimi?!",
     "Beshinchi marta qo‘ng‘iroq qilyapman... Chiqdimi?!", 1.05),
    (4.8, "dil", "[ironic]Aka,[p=100]kechqurun chiqadi!", "(Dilnoza) Aka, kechqurun chiqadi!"),
    (8.4, "narr", "[happy]Aduzda buyurtma bergach,[p=100]uning holatini o'zingiz ko'rasiz.",
     "ADUZ'da buyurtma bergach, uning holatini o‘zingiz ko‘rasiz.", 0.97),
    (16.7, "narr", "[neutral]Kutilmoqda.", "Kutilmoqda.", 0.95),
    (18.5, "narr", "[happy]Tasdiqlandi.", "Tasdiqlandi.", 0.95),
    (20.3, "narr", "[excited]Joylandi!", "Joylandi!", 0.95),
    (21.6, "narr", "[warm]Har bir qadam ko'rinib turadi.", "Har bir qadam ko‘rinib turadi.", 0.97),
    (24.4, "narr", "[warm]Qo'ng'iroq qilish shart emas —[p=100]bot o'zi xabar beradi.",
     "Qo‘ng‘iroq qilish shart emas — bot o‘zi xabar beradi.", 0.97),
    (29.0, "rus8", "[happy]Endi telefonim ham dam oladi!", "Endi telefonim ham dam oladi!"),
    (32.6, "narr", "[happy]Siz adminga necha marta qo'ng'iroq qilgansiz?[p=150]Izohda yozing!",
     "Siz adminga necha marta qo‘ng‘iroq qilgansiz? Izohda yozing!", 0.97),
]
STEP_T = [16.7 - 16, 18.5 - 16, 20.3 - 16]   # local times in block 3 (synced after QA in main)

BLOCKS = [
    ("01", "Beshinchi qo‘ng‘iroq", "“Chiqdimi?” — “Kechqurun.” — “Qaysi kechqurun?”", "reklama beruvchilar."),
    ("02", "Buyurtma → oyna", "Kichik karta to‘liq buyurtmaga ochiladi.", "buyurtmani bir joyda ko‘rish."),
    ("03", "Holat bosqichlari", "Kutilmoqda → Tasdiqlandi → Joylandi.", "vaqtni tejash."),
    ("04", "Bot xabar beradi", "Har o‘zgarishda — bildirishnoma.", "qo‘ng‘iroqsiz kuzatish."),
    ("05", "Izohda yozing", "Siz necha marta qo‘ng‘iroq qilgansiz?", "hamma reklama beruvchilar."),
]


def phone_icon(d, x, y, s, col):
    d.rounded_rectangle((x - 12 * s, y - 20 * s, x + 12 * s, y + 20 * s), radius=int(6 * s), outline=col, width=int(4 * s))
    d.line([(x - 4 * s, y + 13 * s), (x + 4 * s, y + 13 * s)], fill=col, width=int(3 * s))


# ---------------------------------------------------------------- block 1: call log
CALLS = ["10:02", "11:15", "12:30", "14:05", "16:40"]


def block1(img, t, envs):
    card(img, (X0 + 40, Y0 + 50, X1 - 40, Y0 + 770), r=36)
    d = ImageDraw.Draw(img)
    d.text((X0 + 80, Y0 + 86), "Qo‘ng‘iroqlar: Dilnoza (admin)", font=font(36, "Black"), fill=INK)
    for i, tm in enumerate(CALLS):
        k = sp(t, 0.3 + i * 0.55, 0.4)
        if k <= 0:
            continue
        y = Y0 + 160 + i * 115 + (1 - clamp(k)) * 40
        d.rounded_rectangle((X0 + 70, y, X1 - 70, y + 96), radius=24, fill=(246, 242, 238))
        phone_icon(d, X0 + 120, y + 48, 1.0, RED if i < 4 else ORANGE)
        d.text((X0 + 160, y + 24), "Chiqdimi?" if i % 2 == 0 else "Reklama qachon?", font=font(32, "Bold"), fill=INK)
        tw = d.textbbox((0, 0), tm, font=font(30, "Bold"))[2]
        d.text((X1 - 100 - tw, y + 28), tm, font=font(30, "Bold"), fill=MUTED)
    n = sum(1 for i in range(5) if t > 0.3 + i * 0.55)
    if n:
        k = sp(t, 0.3 + (n - 1) * 0.55, 0.3)
        chip(img, int(X1 - 170), int(Y0 + 80), f"× {n}", fill=RED, color=(255, 255, 255), size=int(32 * max(0.5, k)))
    # Rustam on the phone + Dilnoza's answer bubble
    spr = rustam("mouth", brows=-8, tilt=14, eye=0.85, mouth=voice.mouth(envs, "rus8", t, "frown"))
    avatar_circle(img, spr, X0 + 130, Y0 + 880, 150, ORANGE if voice.speaking(envs, "rus8", t) else (200, 195, 190),
                  sp(t, 0.1))
    ka = sp(t, 4.6, 0.4)
    if ka > 0:
        sd = dilnoza(eye=0.6, mouth=voice.mouth(envs, "dil", t, "smirk"))
        avatar_circle(img, sd, X1 - 130, Y0 + 880, 150, SKY if voice.speaking(envs, "dil", t) else (200, 195, 190), ka)


# ---------------------------------------------------------------- block 2: card -> workspace
def order_panel(d, img, x0, y0, x1, y1, k):
    d.text((x0 + 40, y0 + 34), "Buyurtma #12", font=font(44, "Black"), fill=INK)
    chip(img, int(x1 - 250), int(y0 + 36), "Kutilmoqda", fill=(252, 236, 210), color=(170, 110, 20), size=28)
    d = ImageDraw.Draw(img)
    rows = [("Kanal", "Farg‘ona Bugun"), ("Sana", "15-oktabr"), ("Soat", "20:00"), ("Format", "matn + 3 rasm"),
            ("Tepada turish", "1 soat"), ("To‘lov", "250 000 so‘m")]
    for i, (a, b) in enumerate(rows):
        kk = clamp((k - 0.6 - i * 0.05) / 0.3)
        if kk <= 0:
            continue
        y = y0 + 130 + i * 92
        d.text((x0 + 40, y), a, font=font(30, "SemiBold"), fill=MUTED)
        tw = d.textbbox((0, 0), b, font=font(34, "Bold"))[2]
        d.text((x1 - 40 - tw, y - 2), b, font=font(34, "Bold"), fill=INK)
        d.line([(x0 + 40, y + 58), (x1 - 40, y + 58)], fill=(236, 232, 227), width=2)
    return d


def block2(img, t, envs):
    grow = ease(prog(t, 1.0, 1.8)) if t < 6.6 else 1 - ease(prog(t, 6.6, 7.4))
    sx0, sy0, sx1, sy1 = X0 + 60, Y0 + 700, X0 + 420, Y0 + 880       # small card
    bx0, by0, bx1, by1 = X0 + 40, Y0 + 60, X1 - 40, Y0 + 760          # workspace
    d = ImageDraw.Draw(img)
    if grow > 0.02:
        dashed_rect(d, (sx0, sy0, sx1, sy1), r=26)
    x0 = sx0 + (bx0 - sx0) * grow
    y0 = sy0 + (by0 - sy0) * grow
    x1 = sx1 + (bx1 - sx1) * grow
    y1 = sy1 + (by1 - sy1) * grow
    card(img, (x0, y0, x1, y1), r=30)
    d = ImageDraw.Draw(img)
    if grow < 0.3:
        d.text((x0 + 30, y0 + 30), "Buyurtma #12", font=font(36, "Black"), fill=INK)
        d.rounded_rectangle((x0 + 30, y0 + 90, x0 + 230, y0 + 106), radius=8, fill=(225, 220, 214))
        d.rounded_rectangle((x0 + 30, y0 + 122, x0 + 170, y0 + 138), radius=8, fill=(232, 228, 223))
    else:
        order_panel(d, img, x0, y0, x1, y1, grow)
    # cursor clicks the small card to open it
    m = ease(prog(t, 0.0, 0.9))
    cx_ = X1 - 120 - (X1 - 120 - (sx0 + 300)) * m
    cy_ = Y0 + 960 - (Y0 + 960 - (sy0 + 120)) * m
    if grow > 0.95:
        cx_ += 30 * math.sin(t * 1.4)
        cy_ = Y0 + 860 + 10 * math.cos(t * 1.2)
    cursor(img, cx_, cy_, clamp(1 - abs(t - 0.95) / 0.2))


# ---------------------------------------------------------------- block 3: status stepper
STEPS = [("Kutilmoqda", "buyurtma kanal egasiga yuborildi", (230, 160, 40)),
         ("Tasdiqlandi", "kanal egasi qabul qildi · 15:20", NAVY),
         ("Joylandi", "post kanalda · 20:00", GREEN)]


def block3(img, t, envs):
    card(img, (X0 + 40, Y0 + 50, X1 - 40, Y0 + 820), r=36)
    d = ImageDraw.Draw(img)
    d.text((X0 + 80, Y0 + 86), "Buyurtma #12 · Farg‘ona Bugun", font=font(36, "Black"), fill=INK)
    rail_x = X0 + 130
    top, gap = Y0 + 220, 200
    # rail grows to the current step
    done = sum(1 for st in STEP_T if t >= st)
    target = (done - 1) if done else 0
    prog_rail = 0
    for i in range(1, 3):
        prog_rail += ease(prog(t, STEP_T[i] - 0.4, STEP_T[i]))
    d.line([(rail_x, top), (rail_x, top + 2 * gap)], fill=(230, 226, 221), width=10)
    d.line([(rail_x, top), (rail_x, top + gap * prog_rail)], fill=GREEN if done == 3 else NAVY, width=10)
    for i, (name, sub_, col) in enumerate(STEPS):
        y = top + i * gap
        on = t >= STEP_T[i]
        k = sp(t, STEP_T[i], 0.4) if on else 0
        r = 34 + 6 * k
        d.ellipse((rail_x - r, y - r, rail_x + r, y + r), fill=col if on else (238, 234, 229))
        if on:
            d.line([(rail_x - 14, y), (rail_x - 3, y + 12), (rail_x + 16, y - 12)], fill=(255, 255, 255), width=7)
        d.text((rail_x + 70, y - 40), name, font=font(44, "Black"), fill=INK if on else (190, 185, 180))
        d.text((rail_x + 70, y + 14), sub_, font=font(30, "SemiBold"), fill=MUTED if on else (205, 200, 195))
        if on and i == done - 1:  # pulse on the current step
            pr = r + 10 + 14 * ((t * 1.2) % 1)
            col2 = tuple(int(c * (1 - (t * 1.2) % 1) + p * ((t * 1.2) % 1)) for c, p in zip(col, (252, 252, 252)))
            d.ellipse((rail_x - pr, y - pr, rail_x + pr, y + pr), outline=col2, width=4)
    # toast when published
    if t >= STEP_T[2]:
        k = sp(t, STEP_T[2] + 0.2, 0.5)
        y = Y0 + 860 + (1 - clamp(k)) * 60
        card(img, (X0 + 80, y, X1 - 80, y + 110), r=55, fill=INK, alpha=int(255 * clamp(k)))
        d = ImageDraw.Draw(img)
        d.text((X0 + 130, y + 30), "Reklamangiz joylandi — 20:00", font=font(36, "Bold"), fill=(255, 255, 255))


# ---------------------------------------------------------------- block 4: notifications on a phone
NOTIFS = [("ADUZ bot", "Buyurtma #12 tasdiqlandi", "15:20"), ("ADUZ bot", "Reklama kanalda joylandi", "20:00"),
          ("ADUZ bot", "Post 1 soat tepada turdi", "21:00")]


def block4(img, t, envs):
    # phone frame
    px0, py0, px1, py1 = CX - 270, Y0 + 30, CX + 270, Y0 + 960
    card(img, (px0, py0, px1, py1), r=70, fill=(23, 24, 31))
    d = ImageDraw.Draw(img)
    sw, sh = int(px1 - px0 - 36), int(py1 - py0 - 36)
    scr = Image.new("RGB", (sw, sh), (52, 70, 110))
    ds = ImageDraw.Draw(scr)
    for i in range(-300, sh, 60):  # soft wallpaper stripes, clipped to the screen
        ds.line([(0, i), (sw, i + 200)], fill=(58, 78, 120), width=24)
    m = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, sw - 1, sh - 1), radius=56, fill=255)
    img.paste(scr, (int(px0 + 18), int(py0 + 18)), m)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((CX - 70, py0 + 34, CX + 70, py0 + 62), radius=14, fill=(23, 24, 31))
    clock = "21:00" if t > 5 else "20:00"
    f = font(110, "Bold")
    tw = d.textbbox((0, 0), clock, font=f)[2]
    d.text((CX - tw / 2, py0 + 110), clock, font=f, fill=(255, 255, 255))
    for i, (app, msg, tm) in enumerate(NOTIFS):
        k = sp(t, 0.6 + i * 1.5, 0.5)
        if k <= 0:
            continue
        y = py0 + 300 + i * 150 + (1 - clamp(k)) * -80 + 4 * math.sin(t * 2 + i)
        card(img, (px0 + 40, y, px1 - 40, y + 130), r=30, fill=(250, 250, 250), alpha=int(245 * clamp(k)))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((px0 + 64, y + 26, px0 + 120, y + 82), radius=14, fill=NAVY)
        d.text((px0 + 80, y + 34), "A", font=font(30, "Black"), fill=(255, 255, 255))
        d.text((px0 + 140, y + 20), app, font=font(24, "Bold"), fill=MUTED)
        d.text((px1 - 120, y + 20), tm, font=font(24, "Bold"), fill=MUTED)
        d.text((px0 + 140, y + 58), msg, font=font(28, "Bold"), fill=INK)
    # crossed phone-call icon: no more calls
    if t > 5.0:
        k = sp(t, 5.0)
        x, y = X1 - 110, Y0 + 120
        d.ellipse((x - 60 * k, y - 60 * k, x + 60 * k, y + 60 * k), fill=(255, 255, 255))
        if k > 0.6:
            phone_icon(d, x, y, 1.4, INK)
            d.line([(x - 40, y - 40), (x + 40, y + 40)], fill=RED, width=10)


# ---------------------------------------------------------------- block 5: comment poll
OPTS = ["1 marta", "3 marta", "5 marta", "10+ marta"]


def block5(img, t, envs):
    tt = t + 32
    spr = rustam("none", brows=20, tilt=-8, eye=1.1, look=8, mouth=voice.mouth(envs, "rus8", tt, "grin"))
    avatar_circle(img, spr, CX, Y0 + 170, 200, ORANGE if voice.speaking(envs, "rus8", tt) else (200, 195, 190),
                  sp(t, 0.0))
    d = ImageDraw.Draw(img)
    f = font(46, "Black")
    for j, s in enumerate(["Adminga necha marta", "qo‘ng‘iroq qilgansiz?"]):
        tw = d.textbbox((0, 0), s, font=f)[2]
        d.text((CX - tw / 2, Y0 + 310 + j * 60), s, font=f, fill=INK)
    pick = 2
    picked = t > 3.0
    for i, o in enumerate(OPTS):
        k = sp(t, 0.6 + i * 0.15, 0.45)
        if k <= 0:
            continue
        y = Y0 + 470 + i * 112 + 4 * math.sin(t * 2 + i)
        on = picked and i == pick
        card(img, (X0 + 120, y, X1 - 120, y + 92), r=46, fill=ORANGE if on else (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((X0 + 170, y + 22), o, font=font(40, "Bold"), fill=(255, 255, 255) if on else INK)
        if picked:
            share = [8, 27, 41, 24][i]  # shartli, illustrative
            w = (X1 - X0 - 240 - 300) * share / 41 * ease(prog(t, 3.1, 3.9))
            d.rounded_rectangle((X1 - 420, y + 34, X1 - 420 + w * 0.55, y + 58), radius=12,
                                fill=(255, 255, 255) if on else (238, 234, 229))
    m = ease(prog(t, 1.6, 2.8))
    cx_ = X1 - 140 - 200 * m + 8 * math.sin(t * 2)
    cy_ = Y0 + 980 - (Y0 + 980 - (Y0 + 470 + pick * 112 + 50)) * m
    cursor(img, cx_, cy_, clamp(1 - abs(t - 2.95) / 0.2))
    if t > 4.6:
        k = sp(t, 4.6)
        chip(img, int(CX - 250), int(Y0 + 930), "Ertaga: kanal egalari uchun", fill=(255, 255, 255), color=ORANGE,
             size=int(30 * max(0.3, k)) + 1)


BLOCK_FN = [block1, block2, block3, block4, block5]


def camera(img, t, a, b):
    """Constant-speed push + pan (a bit livelier than 9–10-qism so frames never repeat)."""
    k = clamp((t - a) / max(b - a, 0.1))
    z = 1.02 + 0.09 * k
    dx = -30 + 60 * k + 7 * math.sin(t * 1.4)
    dy = -12 + 24 * k + 6 * math.cos(t * 1.1)
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
            subtitle(img, s, INK if who == "narr" else ((40, 90, 140) if who == "dil" else (150, 70, 40)))
    return img


def music_and_sfx():
    buf = np.zeros(int(SR * DUR) + SR)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 100
    prog_ = [(60, 64, 67, 71), (55, 59, 62, 65), (57, 60, 64, 67), (53, 57, 60, 64)]
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
    for i in range(5):  # phone ring blips in the call log
        for j in range(2):
            add(buf, tone(880, 0.12, decay=10, harmonics=(1, 0.5), vol=0.14), 0.3 + i * 0.55 + j * 0.16)
    add(buf, tone(1500, 0.06, decay=60, harmonics=(1,), vol=0.28), 8.95)       # click opens the card
    add(buf, noise(0.5, 0.2, 20) * np.sin(np.linspace(0, np.pi, int(0.5 * SR))), 9.0)
    for st, f in zip(STEP_T, (660, 880, 1175)):                                # stepper chimes
        add(buf, tone(f, 0.6, decay=6, harmonics=(1, 0.3), vol=0.22), 16 + st)
    for i in range(3):                                                         # notification pings
        add(buf, tone(1568, 0.3, decay=10, harmonics=(1, 0.2), vol=0.2), 24.6 + i * 1.5)
        add(buf, tone(2093, 0.3, decay=10, harmonics=(1,), vol=0.14), 24.68 + i * 1.5)
    add(buf, tone(1500, 0.06, decay=60, harmonics=(1,), vol=0.28), 34.95)      # poll click
    return buf[: int(SR * DUR)]


def main(out, qa_only=False, preview=None):
    tmp = tempfile.mkdtemp()
    on_phone = lambda start, who: who == "dil"
    speech, envs, timings = voice.build_speech(LINES, DUR, FPS, tmp, phone_fn=on_phone)
    # sync stepper to the actual start of "Kutilmoqda / Tasdiqlandi / Joylandi"
    STEP_T[:] = [timings[i][0] - 16 for i in (3, 4, 5)]
    problems = voice.qa(LINES, timings, speech)
    if qa_only:
        sys.exit(1 if problems else 0)
    if preview:
        for ts in preview:
            frame(float(ts), envs, timings).convert("RGB").save(f"preview11_{ts}.png")
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
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_11-kun.mp4")
