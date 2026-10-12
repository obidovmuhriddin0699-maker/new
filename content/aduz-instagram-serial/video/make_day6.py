"""ADUZ · "Reklama degani shumi?!" · 6-qism — "200 ming obunachi... va 900 ta ko'rish".

Rustam aka va Shokir (alohida tembrdagi ovozlar), diktor — iliq ayol ovozi.
Ishga tushirish:  python3 make_day6.py <chiqish.mp4>
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
from make_day2 import (BRAND, INK, RED, WHITE, YELLOW, FPS, H, W, add, bg_shop, clamp, draw_text_c, ease,
                       ease_out_back, font, headline, hud, noise, paste_scaled, prog, push, rrect, rustam,
                       subtitle, subtitle2, tone)
from make_day5 import counter, person

SR = voice.SR
DUR = 43.5
PART = "6-qism"
GREEN = (46, 160, 90)

# (start_s, speaker, text_with_emotions, subtitle[, rate_mul])
LINES = [
    (0.3, "sho", "[shout]Toga![p=120][excited]Ikki yuz ming obunachi! Ikki yuz ming!",
     "Toga! 200 ming obunachi! 200 ming!"),
    (3.3, "rus", "[excited]Voy-bo'!", "Voy-bo‘!"),
    (4.4, "sho", "[happy]Obunachisi ko'p bo'lsa, bo'ldi-da![p=100]Hamma ko'radi!",
     "Obunachisi ko‘p bo‘lsa, bo‘ldi-da! Hamma ko‘radi!", 1.08),
    (10.2, "rus", "[neutral]Qani, ko'raylik-chi...[p=350][worried]Shokir... bu ko'zcha nima?",
     "Qani, ko‘raylik-chi... Shokir, bu ko‘zcha nima?"),
    (14.2, "sho", "[ironic]Bu...[p=250]dizayn, toga.", "Bu... dizayn, toga."),
    (16.4, "rus", "[neutral]Dilnozaning kanalida o'ttiz ming obunachi,[p=100]yetti ming ko'rish.",
     "Dilnozaning kanalida 30 ming obunachi — 7 ming ko‘rish.", 1.12),
    (20.0, "rus", "[angry]Bunda ikki yuz ming...[p=200][shout]to'qqiz yuz ko'rish?!",
     "Bunda 200 ming... 900 ko‘rish?!"),
    (24.4, "dik", "[warm]Obunachi soni hali hammasi emas.[p=200]Ko'rishlarga qarang."
                  "[p=200]Aduzda kanallarni yonma-yon solishtirasiz.",
     "Obunachi soni hali hammasi emas. Ko‘rishlarga qarang. ADUZ'da kanallarni yonma-yon solishtirasiz.", 1.12),
    (32.3, "rus", "[happy]Yaxshiyamki, hali pul to'lamadik.", "Yaxshiyamki, hali pul to‘lamadik.", 1.1),
    (34.6, "sho", "[sad]Toga...[p=250]men allaqachon to'lab qo'ydim.", "Toga... men allaqachon to‘lab qo‘ydim.",
     1.08),
    (38.7, "rus", "[shout]Bu reklama-ku, yo lotereya?!", "Bu reklama-ku, yo lotereya?!", 1.12),
]
CTA_AT = 41.1


# ---------------------------------------------------------------- props
def eye_icon(d, x, y, s=1.0, col=(110, 110, 125)):
    d.ellipse((x - 22 * s, y - 13 * s, x + 22 * s, y + 13 * s), outline=col, width=int(4 * s))
    d.ellipse((x - 7 * s, y - 7 * s, x + 7 * s, y + 7 * s), fill=col)


@lru_cache(None)
def posts_card():
    cw, ch = 900, 560
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, cw - 1, ch - 1), 40, fill=(255, 255, 255, 248))
    d.ellipse((30, 30, 110, 110), fill=(150, 150, 160))
    draw_text_c(d, 70, 48, "K", font(42, "Black"), WHITE)
    d.text((130, 34), "Katta kanal", font=font(40, "Black"), fill=INK)
    d.text((130, 82), "200 000 obunachi", font=font(30, "SemiBold"), fill=(110, 110, 125))
    rrect(d, (640, 34, 870, 74), 12, fill=(230, 230, 235))
    draw_text_c(d, 755, 40, "Shartli misol", font(24, "SemiBold"), (90, 90, 100))
    for i, v in enumerate(["900", "1,1 ming", "850"]):
        y = 150 + i * 130
        rrect(d, (30, y, cw - 30, y + 110), 24, fill=(244, 246, 251))
        d.rectangle((60, y + 28, 420, y + 44), fill=(200, 205, 215))
        d.rectangle((60, y + 60, 300, y + 76), fill=(215, 220, 228))
        eye_icon(d, 700, y + 55, 1.2, RED)
        d.text((740, y + 34), v, font=font(40, "Black"), fill=RED)
    return im


def compare_bars(d, t):
    """Two channels: subscribers vs real views (conditional example)."""
    rows = [("Katta kanal", 200_000, 900, RED), ("Dilnozaning kanali", 30_000, 7_000, GREEN)]
    for i, (name, subs, views, col) in enumerate(rows):
        y = 470 + i * 330
        k = ease(prog(t, 0.3 + i * 0.9, 1.3 + i * 0.9))
        rrect(d, (50, y, 1030, y + 290), 36, fill=(255, 255, 255, 240))
        d.text((90, y + 24), name, font=font(42, "Black"), fill=INK)
        d.text((90, y + 90), "Obunachi", font=font(30, "SemiBold"), fill=(110, 110, 125))
        d.text((90, y + 180), "Ko‘rish", font=font(30, "SemiBold"), fill=(110, 110, 125))
        wmax = 500
        ws = wmax * subs / 200_000 * k
        wv = wmax * views / 200_000 * k * 8  # views scaled x8 so the bar is visible
        rrect(d, (260, y + 92, 260 + max(20, ws), y + 132), 18, fill=(150, 160, 185))
        rrect(d, (260, y + 182, 260 + max(20, min(wmax, wv)), y + 222), 18, fill=col)
        d.text((260 + max(20, ws) + 16, y + 92), f"{int(subs * k):,}".replace(",", " "), font=font(32, "Black"),
               fill=INK)
        d.text((260 + max(20, min(wmax, wv)) + 16, y + 182), f"{int(views * k):,}".replace(",", " "),
               font=font(32, "Black"), fill=col)
    rrect(d, (360, 1130, 720, 1175), 14, fill=(230, 230, 235))
    draw_text_c(d, W / 2, 1137, "Shartli misol", font(28, "SemiBold"), (90, 90, 100))


@lru_cache(None)
def channels_mock():
    pw, ph = 760, 1240
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rrect(d, (0, 0, pw - 1, ph - 1), 80, fill=(18, 18, 24))
    rrect(d, (22, 22, pw - 23, ph - 23), 62, fill=(244, 246, 251))
    rrect(d, (pw / 2 - 90, 40, pw / 2 + 90, 70), 15, fill=(18, 18, 24))
    d.rectangle((22, 100, pw - 23, 240), fill=BRAND)
    d.text((60, 120), "ADUZ", font=font(54, "Black"), fill=WHITE)
    d.text((60, 186), "@Targetreklammabot", font=font(30, "SemiBold"), fill=(200, 215, 245))
    d.text((60, 270), "Kanallarni solishtirish", font=font(38, "Black"), fill=INK)
    xs = [60, 250, 450]
    for x, c in zip(xs, ["Obunachi", "O‘rt. ko‘rish", "Hudud"]):
        d.text((x, 340), c, font=font(28, "Bold"), fill=(110, 110, 125))
    rows = [("Katta kanal", "200 000", "900", "Toshkent"), ("Farg‘ona Bugun", "30 000", "7 000", "Farg‘ona"),
            ("Vodiy e’lonlari", "18 000", "5 500", "Farg‘ona")]
    for i, (name, a, b, c) in enumerate(rows):
        y = 400 + i * 230
        rrect(d, (44, y, pw - 45, y + 200), 28, fill=WHITE, outline=(225, 228, 238), width=3)
        d.text((70, y + 22), name, font=font(36, "Black"), fill=BRAND)
        for x, v in zip(xs, (a, b, c)):
            d.text((x, y + 100), v, font=font(32, "Bold"), fill=RED if (i == 0 and v == "900") else INK)
    rrect(d, (44, 1110, pw - 45, 1190), 28, fill=(225, 228, 238))
    draw_text_c(d, pw / 2, 1128, "Shartli misol", font(30, "SemiBold"), (100, 100, 115))
    return im


# ---------------------------------------------------------------- scenes
def two_shot(t, envs, tt, r_kw, s_kw, rx=300, sx=800, s_scale=0.86, sho_y=1130):
    img = bg_shop().copy()
    sho = person("sho", mouth=voice.mouth(envs, "sho", tt, s_kw.pop("quiet", "closed")), **s_kw)
    paste_scaled(img, sho, sx, sho_y, s_scale)
    spr = rustam(r_kw.pop("pose", "none"), mouth=voice.mouth(envs, "rus", tt, r_kw.pop("quiet", "closed")), **r_kw)
    paste_scaled(img, spr, rx, 1120, 0.92)
    counter(img)
    return img


def scene1(t, envs):
    tt = t
    excited = tt < 4.3
    img = two_shot(t, envs, tt,
                   dict(brows=30 if tt > 3.2 else 10, tilt=-10 if tt > 3.2 else 0, eye=1.25 if tt > 3.2 else 1.0,
                        look=12, quiet="O" if 3.2 < tt < 4.4 else "grin"),
                   dict(eye=1.15, brows=14, arms="phones_up", quiet="grin"),
                   sx=820 + (1 - ease_out_back(prog(t, 0, 0.5))) * 400)
    d = ImageDraw.Draw(img)
    k = ease_out_back(prog(t, 0.3, 0.8))
    headline(d, "200 000 OBUNACHI", y=420, size=96, pop=max(0.2, k))
    rrect(d, (380, 540, 700, 590), 14, fill=(0, 0, 0, 150))
    draw_text_c(d, W / 2, 548, "shartli misol", font(30, "SemiBold"), WHITE)
    if excited and int(t * 8) % 2 == 0:
        for (x, y) in ((120, 700), (960, 660), (900, 980)):
            d.polygon([(x, y - 30), (x + 9, y), (x, y + 30), (x - 9, y)], fill=YELLOW)
    return push(img, t / 8, 1.0, 1.04)


def scene2(t, envs):
    tt = t + 8
    if t < 2.0:  # daydream: a queue in front of the shop
        img = Image.new("RGBA", (W, H), (255, 214, 120, 255))
        d = ImageDraw.Draw(img)
        for y in range(H):
            d.line([(0, y), (W, y)], fill=(255, int(214 + 30 * y / H), int(120 + 60 * y / H)))
        for i in range(14):
            x = 80 + (i % 7) * 150 + (i // 7) * 70
            y = 900 + (i // 7) * 260 + 10 * math.sin(t * 6 + i)
            d.ellipse((x - 50, y - 50, x + 50, y + 50), fill=(225, 175, 135))
            d.ellipse((x - 54, y - 64, x + 54, y - 4), fill=(40, 30, 30))
            d.rounded_rectangle((x - 70, y + 50, x + 70, y + 230), radius=50,
                                fill=[(63, 120, 220), (200, 90, 150), (46, 160, 90), (230, 150, 50)][i % 4])
        headline(d, "...xayolda", y=420, size=80, color=WHITE)
        return img
    img = bg_shop().copy()
    sus = tt > 12.0
    spr = rustam("read", brows=-6 if sus else 12, tilt=12 if sus else 0, eye=0.7 if sus else 1.0,
                 mouth=voice.mouth(envs, "rus", tt, "frown" if sus else "closed"))
    paste_scaled(img, spr, 330, 1120, 0.92)
    sho = person("sho", eye=0.9, brows=4 if tt < 14 else -2, look=-10,
                 mouth=voice.mouth(envs, "sho", tt, "closed"))
    paste_scaled(img, sho, 830, 1140, 0.84)
    counter(img)
    k = ease_out_back(prog(t, 2.2, 2.8))
    paste_scaled(img, posts_card(), W / 2, 760 + (1 - k) * 900, 0.95)
    d = ImageDraw.Draw(img)
    if tt > 12.6:  # circle the eye icons
        x, y0 = W / 2 + (700 - 450) * 0.95, 760 + (150 + 55 - 280) * 0.95
        for i in range(3):
            y = y0 + i * 130 * 0.95
            r = 44 + 4 * math.sin(t * 10)
            d.ellipse((x - r, y - r, x + r, y + r), outline=YELLOW, width=7)
    return img


def scene3(t, envs):
    tt = t + 16
    img = bg_shop().copy()
    img.alpha_composite(Image.new("RGBA", (W, H), (20, 30, 60, 110)))
    angry = tt > 20.2
    spr = rustam("despair" if angry else "read", brows=-8 if angry else 20, tilt=16 if angry else -8,
                 eye=0.85 if angry else 1.1, mouth=voice.mouth(envs, "rus", tt, "frown"))
    paste_scaled(img, spr, 330, 1300, 0.8)
    shrink = 1 - 0.12 * ease(prog(t, 4.3, 5.5))
    sho = person("sho", eye=0.7, brows=-6, look=-12, mouth="frown")
    paste_scaled(img, sho, 830, 1320 + (1 - shrink) * 300, 0.74 * shrink)
    counter(img, 1640)
    d = ImageDraw.Draw(img)
    compare_bars(d, t)
    return img


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
        d.ellipse((cx - r, 400 + i * 260 - r, cx + r, 400 + i * 260 + r), outline=(70, 110, 190), width=3)
    k = ease_out_back(prog(t, 0.1, 0.9))
    paste_scaled(img, channels_mock(), W / 2, 900 + (1 - k) * 1400, PS)
    d = ImageDraw.Draw(img)
    headline(d, "Ko‘rishga qarang", y=300, size=80, color=WHITE)
    if t > 2.0:  # highlight the honest local channels
        row = 1 + int((t - 2.0) / 1.4) % 2
        top = 900 - 1240 * PS / 2
        y = top + (400 + row * 230) * PS
        x0 = W / 2 - 760 * PS / 2 + 44 * PS
        d.rounded_rectangle((x0, y, x0 + (760 - 89) * PS, y + 200 * PS), radius=24, outline=YELLOW, width=8)
    return img


def scene5(t, envs):
    tt = t + 32
    ft = min(tt, CTA_AT)
    guilty = ft > 34.8
    despair = ft > 38.6
    img = two_shot(t, envs, ft,
                   dict(pose="despair" if despair else "none", brows=36 if despair else (16 if not guilty else 4),
                        tilt=-14 if despair else 0, eye=1.25 if despair else 1.0, look=0 if despair else 12,
                        quiet="O" if despair else ("grin" if not guilty else "closed")),
                   dict(eye=0.7 if guilty else 1.0, brows=-8 if guilty else 6, look=-12 if guilty else -6,
                        quiet="frown" if guilty else "closed"))
    d = ImageDraw.Draw(img)
    if 37.9 < ft < 38.6:  # awkward silence
        draw_text_c(d, W / 2, 520, ". . .", font(120, "Black"), WHITE, stroke=8)
    if despair:
        k = ease_out_back(prog(ft, 38.6, 39.0))
        headline(d, "BU REKLAMA-KU,", y=380, size=86, color=WHITE, pop=max(0.2, k))
        headline(d, "YO LOTEREYA?!", y=480, size=100, color=YELLOW, pop=max(0.2, k))
    if tt >= CTA_AT:
        a = clamp((tt - CTA_AT) / 0.3)
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(150 * a))))
        d = ImageDraw.Draw(img)
        kk = ease_out_back(prog(tt, CTA_AT, CTA_AT + 0.4))
        rrect(d, (60, 740, 1020, 1110), 40, fill=(255, 255, 255, 250))
        f = font(max(8, int(46 * max(0.3, kk))), "Black")
        draw_text_c(d, W / 2, 780, "Siz nimaga qaraysiz:", f, INK)
        draw_text_c(d, W / 2, 846, "obunachigami, ko‘rishgami?", f, INK)
        rrect(d, (280, 975, 800, 1070), 30, fill=BRAND)
        draw_text_c(d, W / 2, 993, "IZOHDA YOZING", font(48, "Black"), WHITE)
    return img


def frame(t, envs, timings):
    scenes = [scene1, scene2, scene3, scene4, scene5]
    k = min(4, int(t // 8))
    img = scenes[k](t - 8 * k, envs)
    d = ImageDraw.Draw(img)
    hud(d, PART)
    for (a, b, who, sub) in timings:
        if a - 0.05 <= t <= b + 0.3 and t < CTA_AT and not (who == "rus" and b > 39 and t > 38.6):
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
    prog_ = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]
    t = 0.0
    while t < 37.9:
        if 16 <= t < 24:
            chord = [(57, 60, 64), (52, 55, 59)][int(t / 2.4) % 2]  # minor while comparing
        else:
            chord = prog_[int(t / 2.4) % 4]
        step = int(round(t / 0.3)) % 8
        m = chord[[0, 1, 2, 1, 0, 2, 1, 2][step]] + 12
        add(buf, tone(note(m), 0.35, decay=9, harmonics=(1, 0.35, 0.1), vol=0.12), t)
        if step == 0:
            add(buf, tone(note(chord[0] - 12), 1.4, decay=2.2, harmonics=(1, 0.25), vol=0.16), t)
        t += 0.3
    add(buf, tone(523, 0.6, decay=3, harmonics=(1, 0.5, 0.3), vol=0.3), 0.25)   # fanfare
    add(buf, tone(659, 0.6, decay=3, harmonics=(1, 0.5, 0.3), vol=0.3), 0.4)
    add(buf, tone(784, 0.9, decay=2.5, harmonics=(1, 0.5, 0.3), vol=0.3), 0.55)
    for at in (7.85, 9.85, 15.85, 23.85, 31.85):
        add(buf, noise(0.45, 0.3, 30) * np.sin(np.linspace(0, np.pi, int(0.45 * SR))), at)
    nn = int(1.0 * SR)  # crickets in the awkward silence
    tt = np.arange(nn) / SR
    add(buf, 0.06 * np.sin(2 * np.pi * 4200 * tt) * (np.sin(2 * np.pi * 9 * tt) > 0.3), 37.85)
    add(buf, tone(70, 0.6, decay=6, harmonics=(1, 0.5), vol=0.9), 38.6)          # comic hit
    add(buf, tone(2093, 1.2, decay=2.5, harmonics=(1, 0.2), vol=0.15), CTA_AT)
    return buf[: int(SR * DUR)]


def main(out, preview=None):
    tmp = tempfile.mkdtemp()
    speech, envs, timings = voice.build_speech(LINES, DUR, FPS, tmp)
    for (a, b, who, sub) in timings:
        print(f"{a:5.1f}-{b:5.1f} {who}: {sub}")
    if preview:
        for ts in preview:
            frame(float(ts), envs, timings).convert("RGB").save(f"preview6_{ts}.png")
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
        main(sys.argv[1] if len(sys.argv) > 1 else "aduz_6-kun.mp4")
