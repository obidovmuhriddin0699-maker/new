"""ADUZ · 8-qism (v2) — mijoz yuborgan Gemini/Veo roligi dizaynida.

Mijozning 3D kliplari (Rustam aka divan ortida, asoschi gologramma bilan, Rustam akaning yaqin kadrlari,
asoschi telefon menyusini ko'rsatadi) sekinlashtirilib ishlatiladi. AI noto'g'ri yozgan matnli qismlar
(uchib keluvchi so'zlar, 5 qadam, menyu) shu uslubda to'g'ri o'zbekcha matn bilan qayta chiziladi.

Ishga tushirish:
    python3 make_day8_v2.py <manba_video.mp4> <chiqish.mp4>
    python3 make_day8_v2.py <manba_video.mp4> --qa
"""
import glob
import math
import os
import subprocess
import sys
import tempfile
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import voice
from make_day2 import WHITE, YELLOW, FPS, H, W, add, clamp, draw_text_c, ease, ease_out_back, font, noise, prog, \
    tone, wrap

SR = voice.SR
DUR = 41.5
CYAN = (90, 220, 255)
NAVY = (8, 22, 70)
TG = (42, 158, 230)
CACHE = os.path.join(tempfile.gettempdir(), "aduz_day8_ref")

LINES = [
    (0.25, "rus8", "[shout]Nima bo'ldi?!", "", 1.0),
    (3.0, "narr", "[excited]Shoshmang, aka![p=150][happy]Reklamaning osonroq yo'lini ko'rsataman!",
     "Shoshmang, aka! Reklamaning osonroq yo‘lini ko‘rsataman!", 1.04),
    (6.6, "narr", "[neutral]Kanal qidirish, narx so'rash, kelishish, kuzatish...[p=200][angry]hammasi qo'lda!",
     "Kanal qidirish, narx so‘rash, kelishish, kuzatish... hammasi qo‘lda!", 1.06),
    (13.2, "narr", "[excited]Aduz reklama beruvchi va kanal egasini[p=100]bitta platformada uchrashtiradi!",
     "ADUZ reklama beruvchi va kanal egasini bitta platformada uchrashtiradi!", 0.94),
    (19.6, "narr", "[happy]Kanal toping.", "Kanal toping.", 0.95),
    (21.2, "narr", "[happy]Solishtiring.", "Solishtiring.", 0.95),
    (22.8, "narr", "[happy]Buyurtma bering.", "Buyurtma bering.", 0.95),
    (24.4, "narr", "[happy]Kuzating.", "Kuzating.", 0.95),
    (25.8, "narr", "[excited]Natijani ko'ring!", "Natijani ko‘ring!", 0.85),
    (27.6, "rus8", "[excited]Hammasi bir joyda?!", "Hammasi bir joyda?!"),
    (30.4, "narr", "[happy]Ha! Hammasi bir joyda.[p=150][excited]Telegramda, bot orqali!",
     "Ha! Hammasi bir joyda. Telegramda, bot orqali!", 1.04),
    (35.0, "narr", "[excited]Sizga birinchi qaysi imkoniyat kerak?[p=150][happy]Izohda yozing!",
     "Sizga birinchi qaysi imkoniyat kerak? Izohda yozing!", 0.94),
]

# reference clips: name -> (start, end) in the source video (seconds)
CLIPS = {"peek": (0.0, 1.45), "holo": (1.45, 2.95), "logo": (4.2, 5.4), "close": (8.0, 9.2), "point": (9.25, 10.0)}
STEPS = [("Kanal toping", "hudud va mavzu bo‘yicha"), ("Solishtiring", "narx va haqiqiy ko‘rishlar"),
         ("Buyurtma bering", "sana, soat, format"), ("Kuzating", "holati bir joyda"),
         ("Natijani ko‘ring", "qaysi kanal ishladi")]


# ---------------------------------------------------------------- reference assets
def extract(src):
    os.makedirs(CACHE, exist_ok=True)
    for name, (a, b) in CLIPS.items():
        d = os.path.join(CACHE, name)
        if os.path.isdir(d) and glob.glob(d + "/*.png"):
            continue
        os.makedirs(d, exist_ok=True)
        # 2.5x slow motion with motion interpolation, upscaled to 1080x1920
        vf = ("setpts=2.5*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
              "scale=1080:1920:flags=lanczos")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", src, "-vf", vf,
                        os.path.join(d, "%04d.png")], check=True)
    still = os.path.join(CACHE, "steps.png")
    if not os.path.exists(still):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "7.2", "-i", src, "-frames:v", "1", still], check=True)


@lru_cache(None)
def clip_frames(name):
    return sorted(glob.glob(os.path.join(CACHE, name, "*.png")))


@lru_cache(maxsize=8)
def load_frame(path):
    return Image.open(path).convert("RGBA")


def clip_at(name, t, dur, zoom=None):
    """Frame of a slowed clip at local time t. If the scene is longer than the clip, it plays
    back and forth (boomerang) instead of freezing on the last frame."""
    fr = clip_frames(name)
    n = len(fr)
    i = int(t * FPS)
    if n > 1:
        period = 2 * (n - 1)
        i %= period
        if i >= n:
            i = period - i
    return load_frame(fr[i]).copy()


@lru_cache(None)
def step_icon(i):
    """3D icons cropped from the reference 'steps' frame (720x1280 source)."""
    im = Image.open(os.path.join(CACHE, "steps.png")).convert("RGBA")
    cy = [180, 415, 645, 875, 1105][i]
    crop = im.crop((200 - 96, cy - 96, 200 + 96, cy + 96)).resize((230, 230), Image.LANCZOS)
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).ellipse((4, 4, 226, 226), fill=255)
    out = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    out.paste(crop, (0, 0), mask.filter(ImageFilter.GaussianBlur(2)))
    return out


# ---------------------------------------------------------------- style helpers
@lru_cache(None)
def grid_bg():
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(10 + 14 * k), int(32 + 40 * k), int(98 + 70 * k)))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for x in range(0, W, 54):
        gd.line([(x, 0), (x, H)], fill=(120, 170, 255, 26), width=1)
    for y in range(0, H, 54):
        gd.line([(0, y), (W, y)], fill=(120, 170, 255, 26), width=1)
    im.alpha_composite(g)
    vign = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vign).ellipse((-300, -200, W + 300, H + 200), fill=255)
    dark = Image.new("RGBA", (W, H), (2, 8, 30, 170))
    dark.putalpha(Image.eval(vign.filter(ImageFilter.GaussianBlur(220)), lambda v: 170 - int(v * 170 / 255)))
    im.alpha_composite(dark)
    return im


def background(t):
    img = grid_bg().copy()
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    for i in range(60):  # floating sparks
        x = (rng.uniform(0, W) + t * rng.uniform(-20, 20)) % W
        y = (rng.uniform(0, H) - t * rng.uniform(10, 60)) % H
        r = rng.uniform(1.5, 4)
        a = int(120 + 120 * math.sin(t * 2 + i))
        col = YELLOW if i % 7 == 0 else (200, 225, 255)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (max(0, a),))
    return img


def glow_text(img, s, cx, y, size, color=WHITE, glow=CYAN, weight="Black", alpha=1.0, blur_x=0):
    f = font(size, weight)
    d0 = ImageDraw.Draw(img)
    bb = d0.textbbox((0, 0), s, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 60
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.text((pad - bb[0], pad - bb[1]), s, font=f, fill=glow + (int(200 * alpha),))
    g = layer.filter(ImageFilter.GaussianBlur(14))
    ld2 = ImageDraw.Draw(g)
    ld2.text((pad - bb[0], pad - bb[1]), s, font=f, fill=color + (int(255 * alpha),))
    if blur_x > 1:  # horizontal motion blur via running sum
        k = int(blur_x)
        arr = np.asarray(g).astype(np.float32)
        cs = np.cumsum(np.pad(arr, ((0, 0), (k, 0), (0, 0))), axis=1)
        arr = (cs[:, k:] - cs[:, :-k]) / k
        g = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    img.alpha_composite(g, (int(cx - tw / 2 - pad), int(y - pad)))


def neon_pill(img, box, active=False, k=1.0):
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((40, 40, 40 + w, 40 + h), radius=h // 2, outline=CYAN + (int(255 * k),), width=8)
    glow = layer.filter(ImageFilter.GaussianBlur(10 if active else 6))
    d2 = ImageDraw.Draw(glow)
    d2.rounded_rectangle((40, 40, 40 + w, 40 + h), radius=h // 2, fill=(14, 40, 110, int(215 * k)),
                         outline=(170, 235, 255, int(255 * k)), width=4)
    img.alpha_composite(glow, (x0 - 40, y0 - 40))


def sub(img, s):
    if not s:
        return
    d = ImageDraw.Draw(img)
    f = font(50, "ExtraBold")
    y = 1450
    for ln in wrap(d, s, f, 940):
        draw_text_c(d, W / 2, y, ln, f, WHITE, stroke=6, stroke_fill=(5, 15, 50))
        y += 64


# ---------------------------------------------------------------- scenes
def sc_peek(t, dur):
    return clip_at("peek", t, dur, (1.0, 1.04))


def sc_holo(t, dur):
    img = clip_at("holo", t, dur, (1.0, 1.06))
    k = ease_out_back(prog(t, 0.8, 1.3))
    if k > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        x0, y0 = 300, 1210
        d.rounded_rectangle((x0, y0, x0 + 700 * k, y0 + 150), radius=40, fill=(10, 25, 70, 220),
                            outline=CYAN + (230,), width=4)
        img.alpha_composite(layer)
        if k > 0.7:
            d = ImageDraw.Draw(img)
            d.text((x0 + 36, y0 + 22), "Muxriddin Obidov", font=font(52, "Black"), fill=WHITE)
            d.text((x0 + 36, y0 + 88), "ADUZ asoschisi", font=font(36, "Bold"), fill=CYAN)
    return img


def sc_words(t, dur):
    img = background(t)
    words = [("Kanal qidirish", -1, 520, WHITE), ("Narx so‘rash", 1, 660, YELLOW), ("Kelishish", -1, 800, WHITE),
             ("Kuzatish", 1, 940, YELLOW)]
    implode = ease(prog(t, dur - 1.9, dur - 1.2))
    for i, (s, side, y, col) in enumerate(words):
        t0 = 0.3 + i * 0.95
        k = prog(t, t0, t0 + 0.45)
        if k <= 0:
            continue
        e = ease_out_back(k)
        x = W / 2 + side * (1 - e) * 1100
        jitter = 6 * math.sin(t * 13 + i) if t > t0 + 0.45 else 0
        y = y + 10 * math.sin(t * 2.2 + i * 1.3)
        ty = y + (840 - y) * implode
        tx = x + (W / 2 - x) * implode + jitter
        size = int(96 * (1 - 0.6 * implode))
        glow_text(img, s, tx, ty, size, col, CYAN, alpha=1 - 0.7 * implode,
                  blur_x=int(40 * (1 - k)) if k < 1 else 0)
        # speed streaks
        if k < 1:
            d = ImageDraw.Draw(img)
            for j in range(4):
                yy = y + 20 + j * 18
                d.line([(tx - side * 420, yy), (tx - side * 120, yy)], fill=(255, 255, 255, 90), width=3)
    if t > dur - 1.3:  # burst + "HAMMASI QO'LDA!"
        kb = prog(t, dur - 1.3, dur - 0.9)
        d = ImageDraw.Draw(img)
        for a in range(0, 360, 20):
            r0, r1 = 120 + 300 * kb, 200 + 420 * kb
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            d.line([(W / 2 + ca * r0, 860 + sa * r0), (W / 2 + ca * r1, 860 + sa * r1)],
                   fill=(255, 255, 255, int(220 * (1 - kb))), width=6)
        glow_text(img, "HAMMASI QO‘LDA!", W / 2, 800, int(104 * ease_out_back(kb)) + 8, YELLOW, (255, 90, 60))
    return img


def sc_logo(t, dur):
    img = clip_at("logo", t, dur, (1.0, 1.05))
    z = 1.0 + 0.05 * clamp(t / max(dur, 0.1))
    # cover English labels (source y≈906-942 -> 1080p ≈1359-1413) with Uzbek labels in the same spots
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    k = ease(prog(t, 1.0, 1.5))
    for cx, s in ((215, "Reklama beruvchi"), (830, "Kanal egasi")):
        x = W / 2 + (cx - W / 2) * z
        y = H / 2 + (1386 - H / 2) * z
        d.rounded_rectangle((x - 200, y - 42, x + 200, y + 42), radius=42, fill=(10, 30, 90, 255))
    img.alpha_composite(layer)
    for cx, s in ((215, "Reklama beruvchi"), (830, "Kanal egasi")):
        x = W / 2 + (cx - W / 2) * z
        y = H / 2 + (1386 - H / 2) * z
        glow_text(img, s, x, y - 24, 36, WHITE, CYAN, weight="Bold", alpha=max(0.01, k))
    if t > 2.2:
        glow_text(img, "Bitta platformada", W / 2, 360, int(84 * ease_out_back(prog(t, 2.2, 2.7))) + 8, YELLOW,
                  (255, 160, 40))
    return img


def sc_steps(t, dur):
    img = background(t)
    starts = STEP_STARTS
    for i, ((title, subt), st) in enumerate(zip(STEPS, starts)):
        k = prog(t, st, st + 0.45)
        if k <= 0:
            continue
        e = ease_out_back(k)
        y = 330 + i * 250 + 7 * math.sin(t * 2.0 + i * 0.9)
        active = st <= t < (starts[i + 1] if i + 1 < len(starts) else 99)
        x0 = 250 + (1 - e) * 800 + 5 * math.cos(t * 1.6 + i)
        neon_pill(img, (x0, y + 40, x0 + 720, y + 200), active, min(1, k * 1.5))
        d = ImageDraw.Draw(img)
        d.text((x0 + 150, y + 62), title, font=font(52, "Black"), fill=WHITE)
        d.text((x0 + 150, y + 130), subt, font=font(34, "SemiBold"), fill=(180, 225, 255))
        ic = step_icon(i)
        s = 0.8 + 0.12 * (math.sin(t * 6) if active else 0)
        ic2 = ic.resize((int(ic.width * s * e), int(ic.height * s * e)), Image.LANCZOS) if e > 0.05 else None
        if ic2:
            img.alpha_composite(ic2, (int(x0 + 20 - ic2.width / 2), int(y + 120 - ic2.height / 2)))
        glow_text(img, f"{i + 1}.", 120, y + 80, 70, (150, 210, 255), CYAN)
    return img


def sc_close(t, dur):
    img = clip_at("close", t, dur, (1.0, 1.1))
    if t > 0.9:
        k = ease_out_back(prog(t, 0.9, 1.3))
        glow_text(img, "HAMMASI BIR JOYDA?!", W / 2, 1180, int(68 * k) + 8, YELLOW, (255, 140, 40))
    return img


@lru_cache(None)
def bot_panel():
    """Correct-text replacement for the phone menu (source x>=300 -> 1080p x>=450)."""
    pw, ph = W - 450, H
    im = Image.new("RGBA", (pw, ph), (13, 22, 48, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 70, 140, 170), radius=26, fill=TG)
    d.polygon([(62, 122), (122, 92), (104, 152), (92, 130)], fill=WHITE)
    d.text((165, 85), "ADUZ", font=font(64, "Black"), fill=WHITE)
    for i, s in enumerate(["Kanal qidirish...", "@Targetreklammabot"]):
        y = 200 + i * 90
        d.rounded_rectangle((30, y, pw - 30, y + 70), radius=35, fill=(245, 247, 252))
        d.ellipse((58, y + 18, 90, y + 50), outline=(120, 130, 150), width=5)
        d.text((112, y + 14), s, font=font(32, "SemiBold"), fill=(110, 115, 130))
    items = ["Kanal topish", "Solishtirish", "Buyurtma berish", "Kuzatish", "Natijalar", "Bildirishnomalar"]
    for i, s in enumerate(items):
        y = 395 + i * 132
        hl = (i == 4)
        d.rounded_rectangle((30, y, pw - 30, y + 112), radius=24,
                            fill=(28, 60, 130) if hl else (24, 34, 66),
                            outline=CYAN if hl else None, width=4 if hl else 1)
        d.ellipse((50, y + 26, 110, y + 86), fill=TG)
        d.text((135, y + 34), s, font=font(36, "Bold"), fill=WHITE)
        d.text((pw - 75, y + 26), "›", font=font(52, "Bold"), fill=(170, 190, 220))
    return im


def sc_point(t, dur):
    img = clip_at("point", t, dur, (1.0, 1.0))  # no zoom: the menu overlay must stay aligned
    img.alpha_composite(bot_panel(), (450, 0))
    # our own "Izohda yozing" button over the reference one (source 174-546 x 1062-1158)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    d.rounded_rectangle((250, 1585, 830, 1745), radius=80, fill=(10, 20, 50, 235),
                        outline=(120 + int(100 * pulse), 220, 255, 255), width=8)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1)))
    glow_text(img, "Izohda yozing", 540, 1622, 64, WHITE, (170, 110, 255))
    return img


def sc_cta(t, dur):
    img = sc_point(t + 2.0, dur)
    layer = Image.new("RGBA", (W, H), (4, 10, 35, int(205 * ease(prog(t, 0, 0.4)))))
    img.alpha_composite(layer)
    k = ease_out_back(prog(t, 0.2, 0.7))
    glow_text(img, "Sizga birinchi qaysi", W / 2, 330, int(64 * k) + 8, WHITE)
    glow_text(img, "imkoniyat kerak?", W / 2, 410, int(64 * k) + 8, YELLOW, (255, 150, 40))
    for i, (title, _) in enumerate(STEPS):
        kk = prog(t, 0.6 + i * 0.2, 1.0 + i * 0.2)
        if kk <= 0:
            continue
        y = 540 + i * 150 + 6 * math.sin(t * 2.4 + i)
        x0 = 170 + (1 - ease_out_back(kk)) * 800
        neon_pill(img, (x0, y, x0 + 740, y + 116), False, kk)
        d = ImageDraw.Draw(img)
        d.text((x0 + 40, y + 28), f"{i + 1}", font=font(52, "Black"), fill=YELLOW)
        d.text((x0 + 110, y + 30), title, font=font(48, "Bold"), fill=WHITE)
    return img


SCENES = [sc_peek, sc_holo, sc_words, sc_logo, sc_steps, sc_close, sc_point, sc_cta]


SCENE_LINES = [0, 1, 2, 3, 4, 9, 10, 11]   # which line opens each scene
STEP_LINES = [4, 5, 6, 7, 8]
STEP_STARTS = [0.15, 1.15, 2.2, 3.35, 4.35]


def bounds(timings):
    starts = [0.0] + [timings[i][0] - (0.35 if i in (2, 3, 4) else 0.2) for i in SCENE_LINES[1:]]
    # cards pop exactly when their sentence starts
    STEP_STARTS[:] = [timings[i][0] - starts[4] for i in STEP_LINES]
    return [(starts[i], starts[i + 1] if i + 1 < len(starts) else DUR) for i in range(len(starts))]


def camera(img, t, a, b):
    """Slow push-in within each scene plus a gentle drift, so the picture is always alive."""
    k = clamp((t - a) / max(b - a, 0.1))
    z = 1.02 + 0.045 * ease(k)
    dx = 10 * math.sin(t * 0.9)
    dy = 8 * math.cos(t * 0.7)
    nw, nh = int(W * z), int(H * z)
    big = img.resize((nw, nh), Image.BICUBIC)
    x0 = int((nw - W) / 2 + dx)
    y0 = int((nh - H) / 2 + dy)
    return big.crop((x0, y0, x0 + W, y0 + H))


def frame(t, timings, bnds):
    for i, (a, b) in enumerate(bnds):
        if a <= t < b or (i == len(bnds) - 1 and t >= a):
            img = camera(SCENES[i](t - a, b - a), t, a, b)
            break
    # light flash on cuts
    for a, _ in bnds[1:]:
        if a - 0.04 <= t < a + 0.14:
            img = Image.blend(img, Image.new("RGBA", (W, H), (210, 240, 255, 255)), (1 - abs(t - a) / 0.14) * 0.55)
    for (a, b, who, s) in timings:
        if a - 0.05 <= t <= b + 0.25:
            sub(img, s)
    return img


# ---------------------------------------------------------------- audio: energetic promo beat
def music_and_sfx(bnds):
    buf = np.zeros(int(SR * DUR) + SR)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 112
    prog_ = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
    t, n = 0.0, 0
    while t < DUR - 0.6:
        chord = prog_[int(n / 4) % 4]
        if n % 2 == 0:
            add(buf, tone(52, 0.3, decay=16, harmonics=(1, 0.3), vol=0.7), t)
        if n % 4 == 2:
            add(buf, noise(0.15, 0.35, 3) * np.exp(-25 * np.arange(int(0.15 * SR)) / SR), t)  # clap
        add(buf, noise(0.05, 0.18, 1) * np.exp(-70 * np.arange(int(0.05 * SR)) / SR), t + beat / 2)
        if n % 4 == 0:
            for m in chord:
                add(buf, tone(note(m), beat * 4, decay=0.7, harmonics=(1, 0.25), vol=0.05), t)
            add(buf, tone(note(chord[0] - 24), beat * 2, decay=1.4, harmonics=(1, 0.5), vol=0.2), t)
        add(buf, tone(note(chord[n % 3] + 12), 0.22, decay=11, harmonics=(1, 0.3), vol=0.05), t + beat / 2)
        t += beat
        n += 1
    for a, _ in bnds[1:]:  # whoosh on every cut
        add(buf, noise(0.45, 0.35, 30) * np.sin(np.linspace(0, np.pi, int(0.45 * SR))), a - 0.25)
    a_holo = bnds[1][0]
    for i, m in enumerate((72, 76, 79, 84)):  # hologram shimmer
        add(buf, tone(note(m), 1.2, decay=3, harmonics=(1, 0.2), vol=0.08), a_holo + i * 0.06)
    a_words, b_words = bnds[2]
    for i in range(4):
        add(buf, noise(0.3, 0.3, 12) * np.sin(np.linspace(0, np.pi, int(0.3 * SR))), a_words + 0.3 + i * 0.95)
    add(buf, tone(45, 1.0, decay=4, harmonics=(1, 0.5), vol=0.9), b_words - 1.3)        # implode impact
    a_logo = bnds[3][0]
    add(buf, noise(1.0, 0.25, 6) * np.linspace(0, 1, int(1.0 * SR)) ** 2, a_logo - 1.0)  # riser
    for st in STEP_STARTS:
        add(buf, tone(1046, 0.18, decay=20, harmonics=(1, 0.4), vol=0.25), bnds[4][0] + st)
    a_close = bnds[5][0]
    for i, f in enumerate((2093, 2637, 3136)):  # sparkle eyes
        add(buf, tone(f, 0.8, decay=5, harmonics=(1,), vol=0.15), a_close + 0.4 + i * 0.07)
    return buf[: int(SR * DUR)]


def main(src, out, qa_only=False, preview=None):
    extract(src)
    tmp = tempfile.mkdtemp()
    speech, envs, timings = voice.build_speech(LINES, DUR, FPS, tmp)
    problems = voice.qa(LINES, timings, speech)
    bnds = bounds(timings)
    print("sahnalar:", [(round(a, 2), round(b, 2)) for a, b in bnds])
    if qa_only:
        sys.exit(1 if problems else 0)
    if preview:
        for ts in preview:
            frame(float(ts), timings, bnds).convert("RGB").save(f"preview8v2_{ts}.png")
        return
    wav = os.path.join(tmp, "mix.wav")
    voice.mix(speech, music_and_sfx(bnds), wav, tmp)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(i / FPS, timings, bnds).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print("done", out)


if __name__ == "__main__":
    src = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "--qa":
        main(src, None, qa_only=True)
    elif len(sys.argv) > 3 and sys.argv[2] == "--preview":
        main(src, None, preview=sys.argv[3:])
    else:
        main(src, sys.argv[2] if len(sys.argv) > 2 else "aduz_8-kun_v2.mp4")
