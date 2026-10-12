"""ADUZ · "Reklama degani shumi?!" · 7-qism — "Mijoz qaysi kanaldan keldi?" (1-hafta finali).

Rustam aka, Shokir, uchta xaridor va ADUZ asoschisi Muxriddin Obidov (multfilm obrazi).
Ishga tushirish:  python3 make_day7.py <chiqish.mp4>      (ovoz tekshiruvi: python3 make_day7.py --qa)
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
from make_day2 import (BRAND, INK, RED, SS, WHITE, YELLOW, FPS, H, W, add, bg_shop, clamp, draw_text_c, ease,
                       ease_out_back, font, headline, hud, noise, paste_scaled, prog, push, rrect, rustam,
                       subtitle, subtitle2, thick_line, tone)
from make_day5 import counter, person

SR = voice.SR
PART = "7-qism"
GREEN = (46, 160, 90)

# (start_s, speaker, text_with_emotions, subtitle[, rate_mul])
LINES = [
    (0.4, "rus", "[worried]Reklama chiqdi.[p=150]Pul ketdi.[p=300][worried]Endi... mijoz qaysi kanaldan keldi?",
     "Reklama chiqdi. Pul ketdi. Endi... mijoz qaysi kanaldan keldi?", 1.06),
    (8.1, "rus", "[neutral]Bizni qayerdan topdingiz?", "Bizni qayerdan topdingiz?", 1.15),
    (10.0, "ayol", "[happy]Instagramdan.", "Instagramdan."),
    (11.0, "rus", "[shout]Bizda Instagram yo'q-ku!", "Bizda Instagram yo‘q-ku!", 1.12),
    (12.7, "ota", "[neutral]Qo'shnim aytdi.", "Qo‘shnim aytdi."),
    (13.95, "yig", "[ironic]Shunchaki o'tib ketayotgandim.", "Shunchaki o‘tib ketayotgandim.", 1.1),
    (16.3, "sho", "[excited]Demak, qo'shni kanalni ko'rgan,[p=100]keyin Instagramga kirgan...",
     "Demak, qo‘shni kanalni ko‘rgan, keyin Instagramga kirgan...", 1.05),
    (20.3, "rus", "[angry]Qaysi biri ishladi?[p=200][worried]Keyingi safar qayerga pul beraman?",
     "Qaysi biri ishladi? Keyingi safar qayerga pul beraman?", 1.06),
    (24.4, "dik", "[warm]Har bir kanalga alohida promo-kod bering.[p=200]Shunda qaysi biri ishlaganini bilasiz."
                  "[p=200]Aduzda buyurtma va natijalar bir joyda.",
     "Har bir kanalga alohida promo-kod bering — qaysi biri ishlaganini bilasiz. "
     "ADUZ'da buyurtma va natijalar bir joyda.", 1.17),
    (32.6, "rus", "[tired]Eh...[p=250]kimdir buning osonroq yo'lini topsa edi...",
     "Eh... kimdir buning osonroq yo‘lini topsa edi..."),
    (36.6, "asos", "[warm]Shoshmang.[p=300]Osonroq yo'li bor.", "Shoshmang. Osonroq yo‘li bor.", 1.07),
    (39.3, "rus", "[shout]Siz kimsiz?!", "Siz kimsiz?!"),
]
DUR = 44.5
END_AT = 41.6   # name title -> "Davomi bor" card


# ---------------------------------------------------------------- founder (cartoon of Muxriddin Obidov)
@lru_cache(None)
def founder(eye=1.0, look=0, mouth="closed", smile=False):
    """White shirt, rimless rectangular glasses with thin dark temples, neat side-parted black hair."""
    s = SS
    im = Image.new("RGBA", (800 * s, 1000 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    S = lambda *v: tuple(int(x * s) for x in v)
    skin, skin_d = (228, 186, 150), (205, 160, 124)
    cx, cy = 400, 340
    # white shirt, open collar
    d.rounded_rectangle(S(165, 520, 635, 1060), radius=150 * s, fill=(248, 248, 250))
    d.polygon([S(330, 505)[0:2], S(400, 600)[0:2], S(360, 640)[0:2], S(300, 560)[0:2]], fill=(232, 232, 238))
    d.polygon([S(470, 505)[0:2], S(400, 600)[0:2], S(440, 640)[0:2], S(500, 560)[0:2]], fill=(232, 232, 238))
    d.polygon([S(360, 520)[0:2], S(440, 520)[0:2], S(400, 600)[0:2]], fill=skin_d)
    for y in (700, 800, 900):
        d.ellipse(S(394, y, 406, y + 12), fill=(210, 210, 218))
    d.rectangle(S(362, 455, 438, 525), fill=skin_d)
    for ex in (cx - 128, cx + 128):
        d.ellipse(S(ex - 22, cy, ex + 22, cy + 56), fill=skin_d)
    # hair: neat, side-parted
    d.ellipse(S(cx - 138, cy - 190, cx + 138, cy + 10), fill=(22, 20, 22))
    d.ellipse(S(cx - 125, cy - 120, cx + 125, cy + 165), fill=skin)
    d.chord(S(cx - 132, cy - 175, cx + 132, cy - 40), 180, 360, fill=(22, 20, 22))
    d.pieslice(S(cx - 150, cy - 175, cx + 40, cy - 30), 180, 260, fill=(22, 20, 22))
    d.line([S(cx - 60, cy - 160)[0:2], S(cx - 40, cy - 92)[0:2]], fill=(60, 56, 60), width=4 * s)  # parting
    # eyes
    for sx in (-1, 1):
        ex, ey = cx + sx * 50, cy + 18
        h = 17 * eye
        d.ellipse(S(ex - 22, ey - h, ex + 22, ey + h), fill=WHITE)
        pr = min(11, 11 * eye + 2)
        d.ellipse(S(ex + look - pr, ey - pr, ex + look + pr, ey + pr), fill=(35, 26, 20))
        d.line([S(cx + sx * 22, cy - 28)[0:2], S(cx + sx * 84, cy - 32)[0:2]], fill=(25, 22, 22), width=11 * s)
        # rimless lenses: faint outline + light glare
        d.rounded_rectangle(S(ex - 46, ey - 30, ex + 46, ey + 30), radius=10 * s, outline=(170, 180, 190),
                            width=3 * s)
        d.line([S(ex + 18, ey - 22)[0:2], S(ex + 32, ey - 8)[0:2]], fill=(235, 242, 250), width=4 * s)
    d.line([S(cx - 4, cy + 12)[0:2], S(cx + 4, cy + 12)[0:2]], fill=(40, 40, 46), width=6 * s)        # bridge
    d.line([S(cx - 96, cy + 4)[0:2], S(cx - 128, cy + 2)[0:2]], fill=(30, 30, 36), width=6 * s)        # temples
    d.line([S(cx + 96, cy + 4)[0:2], S(cx + 128, cy + 2)[0:2]], fill=(30, 30, 36), width=6 * s)
    d.ellipse(S(cx - 15, cy + 45, cx + 15, cy + 80), fill=skin_d)
    my = cy + 112
    if mouth == "open":
        d.ellipse(S(cx - 26, my - 10, cx + 26, my + 20), fill=(120, 40, 40))
    elif smile:
        d.arc(S(cx - 40, my - 26, cx + 40, my + 14), 20, 160, fill=(150, 60, 60), width=7 * s)
    else:
        d.line([S(cx - 24, my + 2)[0:2], S(cx + 24, my + 2)[0:2]], fill=(150, 60, 60), width=7 * s)
    # holds a phone at chest height
    thick_line(d, S(560, 640)[0:2], S(470, 780)[0:2], 74 * s, (248, 248, 250))
    d.rounded_rectangle(S(430, 700, 520, 850), radius=16 * s, fill=(40, 42, 52))
    d.ellipse(S(440, 760, 500, 820), fill=skin)
    return im.resize((800, 1000), Image.LANCZOS)


# ---------------------------------------------------------------- props
def notepad(d, x, y, n):
    rrect(d, (x, y, x + 190, y + 240), 12, fill=(255, 250, 220), outline=(200, 180, 120), width=4)
    for i in range(n):
        d.line([(x + 20, y + 40 + i * 50), (x + 120 + 40 * (i % 2), y + 40 + i * 50)], fill=(60, 60, 90), width=5)
        draw_text_c(d, x + 160, y + 18 + i * 50, "?", font(38, "Black"), RED)


def whiteboard(d, t):
    rrect(d, (90, 420, 990, 980), 24, fill=(250, 250, 252), outline=(160, 160, 170), width=10)
    labels = [("Kanal 1", 220, 540), ("Kanal 2", 760, 540), ("Instagram", 490, 700), ("Qo‘shni", 220, 860),
              ("Mijoz", 760, 870)]
    k = prog(t, 0.2, 3.5)
    shown = int(k * len(labels)) + 1
    for i, (s, x, y) in enumerate(labels[:shown]):
        rrect(d, (x - 110, y - 36, x + 110, y + 36), 18, outline=(63, 120, 220), width=5)
        draw_text_c(d, x, y - 22, s, font(32, "Bold"), INK)
    arrows = [((330, 540), (490, 660)), ((650, 540), (490, 660)), ((490, 740), (330, 830)), ((330, 860), (650, 870)),
              ((760, 580), (760, 830)), ((490, 740), (760, 830)), ((220, 580), (220, 820))]
    for i, (a, b) in enumerate(arrows[: int(prog(t, 0.6, 4.5) * len(arrows))]):
        jitter = 6 * math.sin(i * 3.1)
        d.line([a, (b[0] + jitter, b[1])], fill=RED, width=6)
        d.ellipse((b[0] - 9 + jitter, b[1] - 9, b[0] + 9 + jitter, b[1] + 9), fill=RED)
    if t > 3.8:
        draw_text_c(d, 870, 440, "???", font(60, "Black"), RED)


@lru_cache(None)
def results_mock():
    pw, ph = 760, 1240
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, pw - 1, ph - 1), 80, fill=(18, 18, 24))
    rrect(d, (22, 22, pw - 23, ph - 23), 62, fill=(244, 246, 251))
    rrect(d, (pw / 2 - 90, 40, pw / 2 + 90, 70), 15, fill=(18, 18, 24))
    d.rectangle((22, 100, pw - 23, 240), fill=BRAND)
    d.text((60, 120), "ADUZ", font=font(54, "Black"), fill=WHITE)
    d.text((60, 186), "@Targetreklammabot", font=font(30, "SemiBold"), fill=(200, 215, 245))
    d.text((60, 270), "Reklama natijalari", font=font(40, "Black"), fill=INK)
    rows = [("1-kanal", "FARGONA10", 18, GREEN), ("2-kanal", "DIVAN10", 3, RED)]
    for i, (name, code, n, col) in enumerate(rows):
        y = 360 + i * 300
        rrect(d, (44, y, pw - 45, y + 260), 28, fill=WHITE, outline=(225, 228, 238), width=3)
        d.text((74, y + 26), name, font=font(38, "Black"), fill=BRAND)
        rrect(d, (74, y + 90, 360, y + 145), 16, fill=(235, 240, 250))
        d.text((92, y + 98), code, font=font(32, "Black"), fill=BRAND)
        d.text((74, y + 175), f"Promo-kod bilan: {n} ta mijoz", font=font(32, "Bold"), fill=col)
    rrect(d, (44, 1110, pw - 45, 1190), 28, fill=(225, 228, 238))
    draw_text_c(d, pw / 2, 1128, "Shartli misol", font(30, "SemiBold"), (100, 100, 115))
    return im


# ---------------------------------------------------------------- scenes
def scene1(t, envs):
    img = bg_shop().copy()
    spr = rustam("read", brows=18, tilt=-8, eye=1.05, look=int(14 * math.sin(t * 2.2)),
                 mouth=voice.mouth(envs, "rus", t, "frown"))
    paste_scaled(img, spr, W / 2, 1100, 1.1)
    counter(img)
    d = ImageDraw.Draw(img)
    # second phone in the other hand
    rrect(d, (160, 1260, 260, 1440), 18, fill=(40, 42, 52))
    headline(d, "1-HAFTA FINALI", y=420, size=96, pop=max(0.2, ease_out_back(prog(t, 0.2, 0.7))))
    for i, (x, y, s) in enumerate([(170, 900, "Kanal 1"), (910, 940, "Kanal 2")]):
        k = ease_out_back(prog(t, 1.5 + i * 0.6, 1.9 + i * 0.6))
        if k > 0:
            rrect(d, (x - 120, y - 40, x + 120, y + 40), 30, fill=(255, 255, 255, 235))
            draw_text_c(d, x, y - 24, s, font(max(8, int(36 * k)), "Black"), BRAND)
    if t > 4.6:
        draw_text_c(d, W / 2, 610, "?", font(int(140 + 20 * math.sin(t * 6)), "Black"), YELLOW, stroke=8)
    return push(img, t / 8, 1.0, 1.05)


def scene2(t, envs):
    tt = t + 8
    img = bg_shop().copy()
    # which customer is at the desk
    who = "ayol" if tt < 12.4 else ("ota" if tt < 13.9 else "yig")
    sw = ease(prog(t, 4.3, 4.6)) if who == "ota" else (ease(prog(t, 5.8, 6.1)) if who == "yig" else 1)
    if who == "ayol":
        cust = ("ayol", None)
    if who == "ayol":
        img = draw_customer_woman(img, envs, tt)
    elif who == "ota":
        img = draw_customer(img, envs, tt, "ota", sw)
    else:
        img = draw_customer(img, envs, tt, "yig", sw)
    shout = 10.9 < tt < 12.4
    spr = rustam("read", brows=34 if shout else 10, tilt=-14 if shout else 0, eye=1.25 if shout else 1.0,
                 look=-14, mouth=voice.mouth(envs, "rus", tt, "O" if shout else "closed"))
    paste_scaled(img, spr, 720, 1120, 0.95)
    counter(img)
    d = ImageDraw.Draw(img)
    notepad(d, 830, 1300, 1 + (tt > 10.6) + (tt > 13.4) + (tt > 15.3))
    rrect(d, (60, 330, 520, 410), 30, fill=(0, 0, 0, 170))
    draw_text_c(d, 290, 344, "Detektiv Rustam aka", font(38, "Black"), YELLOW)
    return img


def draw_customer(img, envs, tt, who, sw):
    if who == "ota":
        p = person("xar", eye=0.75, brows=4, mouth=voice.mouth(envs, "ota", tt, "closed"))
        paste_scaled(img, p, 290, 1150 + (1 - sw) * 80, 0.85, alpha=sw)
        d = ImageDraw.Draw(img)
        # doppi + grey beard to make him an elderly man
        x, y = 290, 1150 + (1 - sw) * 80 - (500 - 340) * 0.85
        d.chord((x - 105, y - 165, x + 105, y - 40), 180, 360, fill=(30, 30, 30))
        for i in range(4):
            d.line([(x - 70 + i * 45, y - 130), (x - 50 + i * 45, y - 100)], fill=WHITE, width=5)
        d.chord((x - 85, y + 40, x + 85, y + 140), 0, 180, fill=(200, 200, 205))
    else:
        p = person("xar", eye=0.9, brows=0, look=-8, mouth=voice.mouth(envs, "yig", tt, "grin"))
        paste_scaled(img, p, 290, 1150 + (1 - sw) * 80, 0.85, alpha=sw)
    return img


def draw_customer_woman(img, envs, tt):
    from make_day2 import dilnoza
    p = dilnoza(eye=0.95, look=10, mouth=voice.mouth(envs, "ayol", tt, "smirk"), brows=4)
    # tint her sweater differently so she is not Dilnoza
    p = p.copy()
    px = np.array(p)
    mask = (abs(px[..., 0].astype(int) - 222) < 18) & (abs(px[..., 1].astype(int) - 200) < 18) & \
           (abs(px[..., 2].astype(int) - 170) < 18)
    px[mask, 0:3] = (200, 90, 150)
    p = Image.fromarray(px)
    paste_scaled(img, p, 290, 1150, 0.85)
    return img


def scene3(t, envs):
    tt = t + 16
    img = bg_shop().copy()
    d = ImageDraw.Draw(img)
    whiteboard(d, t)
    sho = person("sho", eye=1.05 if tt < 20 else 0.8, brows=10 if tt < 20 else -4, look=-14,
                 mouth=voice.mouth(envs, "sho", tt, "grin" if tt < 20 else "frown"))
    paste_scaled(img, sho, 820, 1250, 0.8)
    angry = tt > 20.2
    spr = rustam("despair" if angry else "none", brows=-6 if angry else 6, tilt=14 if angry else 0,
                 eye=0.85, look=12, mouth=voice.mouth(envs, "rus", tt, "frown"))
    paste_scaled(img, spr, 290, 1250, 0.85)
    counter(img, 1660)
    d = ImageDraw.Draw(img)
    if tt > 20.2:
        rrect(d, (220, 320, 860, 400), 30, fill=(0, 0, 0, 180))
        draw_text_c(d, W / 2, 334, "Kelgan mijozlar: 3 · Qaysi kanaldan: ???", font(32, "Bold"), YELLOW)
    return img


PS = 0.68


def scene4(t, envs):
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(15 + 20 * k), int(61 + 30 * k), int(145 + 40 * k)))
    # two promo-code tickets first, then the results screen
    if t < 2.8:
        for i, (code, ang) in enumerate([("FARGONA10", -6), ("DIVAN10", 5)]):
            k = ease_out_back(prog(t, 0.1 + i * 0.4, 0.6 + i * 0.4))
            card = Image.new("RGBA", (620, 260), (0, 0, 0, 0))
            cd = ImageDraw.Draw(card)
            rrect(cd, (0, 0, 619, 259), 30, fill=(255, 255, 255, 250))
            cd.text((40, 30), f"{i + 1}-kanal uchun", font=font(36, "Bold"), fill=(110, 110, 125))
            cd.text((40, 100), code, font=font(84, "Black"), fill=BRAND)
            card = card.rotate(ang, expand=True, resample=Image.BICUBIC)
            paste_scaled(img, card, W / 2 + (1 - k) * 900 * (1 if i else -1), 760 + i * 360, 1.0)
        headline(d, "Har kanalga — o‘z promo-kodi", y=330, size=64, color=WHITE)
    else:
        k = ease_out_back(prog(t, 2.8, 3.5))
        paste_scaled(img, results_mock(), W / 2, 880 + (1 - k) * 1400, PS)
        headline(d, "Qaysi kanal ishladi — aniq", y=300, size=66, color=WHITE)
    return img


def scene5(t, envs):
    tt = t + 32
    ft = min(tt, END_AT)
    img = bg_shop().copy()
    img.alpha_composite(Image.new("RGBA", (W, H), (70, 40, 20, 50)))  # warm evening
    rise = ease(prog(ft, 36.1, 37.0))
    jump = ft > 39.2
    # founder rises from behind the sofa
    f = founder(eye=1.0, look=-10 if ft < 39.2 else -4, mouth=voice.mouth(envs, "asos", ft, "closed"),
                smile=ft > 38.5)
    paste_scaled(img, f, 700, 1460 - rise * 470, 0.92)
    d = ImageDraw.Draw(img)
    # soft rim light behind founder
    if rise > 0.5:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse((470, 560, 930, 1020), outline=(255, 240, 200, 90), width=16)
        img.alpha_composite(glow)
    # sofa back in front of the founder
    d = ImageDraw.Draw(img)
    rrect(d, (60, 1130, 1020, 1460), 70, fill=(150, 152, 160))
    rrect(d, (20, 1380, 1060, 1700), 60, fill=(165, 167, 176))
    rrect(d, (0, 1650, W, H), 0, fill=(150, 98, 58))
    # Rustam on the sofa; jumps up at the end
    rj = ease_out_back(prog(ft, 39.2, 39.6))
    spr = rustam("despair" if jump else "none", brows=38 if jump else -2, tilt=-16 if jump else 10,
                 eye=1.3 if jump else 0.6, look=12 if jump else 0,
                 mouth=voice.mouth(envs, "rus", ft, "O" if jump else "frown"))
    paste_scaled(img, spr, 330 - rj * 40, 1330 - rj * 140, 0.9)
    d = ImageDraw.Draw(img)
    if ft > 39.8:
        k = ease_out_back(prog(ft, 39.8, 40.3))
        rrect(d, (380, 520, 1040, 640), 30, fill=(255, 255, 255, 245))
        d.text((410, 534), "Muxriddin Obidov", font=font(max(8, int(44 * k)), "Black"), fill=INK)
        d.text((410, 590), "ADUZ asoschisi", font=font(max(8, int(32 * k)), "Bold"), fill=BRAND)
    if tt >= END_AT:
        a = clamp((tt - END_AT) / 0.5)
        img = Image.blend(img, Image.new("RGBA", (W, H), (10, 10, 16, 255)), a * 0.85)
        d = ImageDraw.Draw(img)
        k = ease_out_back(prog(tt, END_AT + 0.2, END_AT + 0.7))
        draw_text_c(d, W / 2, 760, "DAVOMI BOR...", font(max(8, int(104 * k)), "Black"), YELLOW, stroke=6)
        draw_text_c(d, W / 2, 920, "Keyingi qismni o‘tkazib yubormang", font(46, "Bold"), WHITE)
        rrect(d, (290, 1010, 790, 1105), 30, fill=BRAND)
        draw_text_c(d, W / 2, 1028, "KUZATING", font(52, "Black"), WHITE)
    return img


def frame(t, envs, timings):
    scenes = [scene1, scene2, scene3, scene4, scene5]
    k = min(4, int(t // 8))
    img = scenes[k](t - 8 * k, envs)
    d = ImageDraw.Draw(img)
    hud(d, PART)
    for (a, b, who, sub) in timings:
        if a - 0.05 <= t <= b + 0.3 and t < END_AT:
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
    t = 0.0
    while t < 32:
        if 8 <= t < 16:  # playful "detective" walk
            seq = [57, 60, 64, 63, 62, 60, 57, 55]
            m = seq[int(round(t / 0.3)) % 8] + 12
            add(buf, tone(note(m), 0.25, decay=12, harmonics=(1, 0.5, 0.25), vol=0.11), t)
            if int(round(t / 0.3)) % 2 == 0:
                add(buf, tone(note(45), 0.3, decay=8, harmonics=(1, 0.3), vol=0.15), t)
        else:
            chord = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)][int(t / 2.4) % 4]
            step = int(round(t / 0.3)) % 8
            add(buf, tone(note(chord[[0, 1, 2, 1, 0, 2, 1, 2][step]] + 12), 0.35, decay=9,
                          harmonics=(1, 0.35, 0.1), vol=0.11), t)
            if step == 0:
                add(buf, tone(note(chord[0] - 12), 1.4, decay=2.2, harmonics=(1, 0.25), vol=0.15), t)
        t += 0.3
    for m, at in [(57, 32.0), (53, 34.4)]:  # quiet, tired pad
        for mm in (m, m + 3, m + 7):
            add(buf, tone(note(mm), 2.6, decay=0.8, harmonics=(1, 0.2), vol=0.06), at)
    for i, m in enumerate((60, 64, 67, 72)):  # reveal chord when the founder rises
        add(buf, tone(note(m), 3.5, decay=0.7, harmonics=(1, 0.3, 0.1), vol=0.09), 36.1 + i * 0.08)
    for at in (7.85, 15.85, 23.85, 31.85):
        add(buf, noise(0.45, 0.3, 30) * np.sin(np.linspace(0, np.pi, int(0.45 * SR))), at)
    nw = int(0.6 * SR)
    add(buf, noise(0.6, 0.35, 40) * np.sin(np.linspace(0, np.pi, nw)) ** 2, 36.0)  # whoosh (rise)
    add(buf, tone(70, 0.5, decay=7, harmonics=(1, 0.5), vol=0.8), 39.25)              # jump hit
    for i, m in enumerate((55, 60, 64, 67)):                                          # "davomi bor" sting
        add(buf, tone(note(m), 2.5, decay=1.2, harmonics=(1, 0.4, 0.2), vol=0.14), END_AT + 0.2 + i * 0.12)
    for at in (8.0, 9.6, 10.8, 12.5, 13.9):  # pen scratches
        add(buf, noise(0.25, 0.08, 1) * np.exp(-6 * np.arange(int(0.25 * SR)) / SR), at)
    return buf[: int(SR * DUR)]


def main(out, preview=None, qa_only=False):
    tmp = tempfile.mkdtemp()
    speech, envs, timings = voice.build_speech(LINES, DUR, FPS, tmp)
    problems = voice.qa(LINES, timings, speech)
    if qa_only:
        sys.exit(1 if problems else 0)
    if preview:
        for ts in preview:
            frame(float(ts), envs, timings).convert("RGB").save(f"preview7_{ts}.png")
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
    if len(sys.argv) > 1 and sys.argv[1] == "--qa":
        main(None, qa_only=True)
    elif len(sys.argv) > 2 and sys.argv[1] == "--preview":
        main(None, sys.argv[2:])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_7-kun.mp4")
