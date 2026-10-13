"""Motion uslubi A — "Clean UI motion" (reference/motion/MOTION_QOLLANMA.md, ref02–ref11).

Qayta ishlatiladigan bloklar: sahifa ramkasi, kartochka + yumshoq soya, prujina easing, kursor, chip,
avatar, matn yordamchilari. Barcha o'lchamlar 1080x1920 uchun.
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter

from make_day2 import FPS, H, W, clamp, ease, font, prog, wrap

PAGE = (235, 233, 229)       # #EBE9E5
INNER = (238, 236, 234)      # #EEECEA
CARD = (252, 252, 252)
INK = (23, 24, 31)           # #17181F
MUTED = (120, 116, 112)
ORANGE = (224, 126, 87)      # #E07E57
SKY = (114, 175, 212)        # #72AFD4
NAVY = (35, 75, 159)         # #234B9F
GREEN = (60, 170, 110)
RED = (214, 80, 70)

WIN = (60, 330, 1020, 1330)  # animation window


def spring(x, overshoot=1.6):
    """0..1 with a small overshoot (≈6–8%), like the reference pack."""
    x = clamp(x)
    c3 = overshoot + 1
    return 1 + c3 * (x - 1) ** 3 + overshoot * (x - 1) ** 2


def sp(t, a, d=0.45):
    return spring(prog(t, a, a + d))


@lru_cache(None)
def _shadow(w, h, r, blur=26, alpha=40):
    pad = blur * 3
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((pad, pad + 10, pad + w, pad + h + 10), radius=r, fill=(60, 50, 40, alpha))
    return im.filter(ImageFilter.GaussianBlur(blur)), pad


def card(img, box, r=36, fill=CARD, shadow=True, outline=None, alpha=255):
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    if shadow and alpha > 20:
        sh, pad = _shadow(w, h, r)
        if alpha < 255:
            sh = sh.copy()
            sh.putalpha(sh.getchannel("A").point(lambda v: v * alpha // 255))
        img.alpha_composite(sh, (x0 - pad, y0 - pad))
    layer = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle((0, 0, w, h), radius=r, fill=fill + (alpha,),
                                            outline=outline, width=3 if outline else 0)
    img.alpha_composite(layer, (x0, y0))


def dashed_rect(d, box, r=30, color=(170, 160, 150), dash=14, gap=10, width=3):
    x0, y0, x1, y1 = box
    pts = []
    for x in range(int(x0 + r), int(x1 - r), dash + gap):
        pts += [((x, y0), (min(x + dash, x1 - r), y0)), ((x, y1), (min(x + dash, x1 - r), y1))]
    for y in range(int(y0 + r), int(y1 - r), dash + gap):
        pts += [((x0, y), (x0, min(y + dash, y1 - r))), ((x1, y), (x1, min(y + dash, y1 - r)))]
    for a, b in pts:
        d.line([a, b], fill=color, width=width)


def page(num, title, subtitle, use_for):
    """Static page frame (cached): number + title + subtitle, inner window, 'Kimga foydali' line, footer."""
    return _page(num, title, subtitle, use_for).copy()


@lru_cache(None)
def _page(num, title, subtitle, use_for):
    im = Image.new("RGBA", (W, H), PAGE + (255,))
    d = ImageDraw.Draw(im)
    d.text((60, 150), num, font=font(30, "Bold"), fill=ORANGE)
    d.text((120, 136), title, font=font(60, "Black"), fill=INK)
    d.text((62, 222), subtitle, font=font(32, "Medium"), fill=MUTED)
    ImageDraw.Draw(im).rounded_rectangle(WIN, radius=44, fill=INNER, outline=(226, 223, 219), width=3)
    d.text((62, 1572), "Kimga foydali:", font=font(30, "Bold"), fill=ORANGE)
    tw = d.textbbox((0, 0), "Kimga foydali: ", font=font(30, "Bold"))[2]
    d.text((62 + tw, 1572), use_for, font=font(30, "SemiBold"), fill=INK)
    d.ellipse((62, 1630, 102, 1670), fill=NAVY)
    d.text((70, 1636), "A", font=font(24, "Black"), fill=(255, 255, 255))
    d.text((116, 1637), "ADUZ  ·  @Targetreklammabot", font=font(26, "Bold"), fill=INK)
    d.text((W - 330, 1637), "Reklama degani shumi?!", font=font(24, "SemiBold"), fill=MUTED)
    return im


def cursor(img, x, y, press=0.0):
    s = 1 - 0.15 * press
    pts = [(0, 0), (0, 44), (12, 33), (21, 52), (29, 48), (20, 30), (36, 30)]
    pts = [(x + px * s, y + py * s) for px, py in pts]
    d = ImageDraw.Draw(img)
    d.polygon([(px + 3, py + 4) for px, py in pts], fill=(0, 0, 0, 70))
    d.polygon(pts, fill=(255, 255, 255), outline=INK)
    d.line(pts + [pts[0]], fill=INK, width=3)
    if press > 0.05:
        r = 30 + 30 * press
        col = tuple(int(c * press + p * (1 - press)) for c, p in zip(ORANGE, PAGE))
        d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=4)


def chip(img, x, y, text, fill=INK, color=(255, 255, 255), size=30, pad=22, h=None):
    d = ImageDraw.Draw(img)
    f = font(size, "Bold")
    tw = d.textbbox((0, 0), text, font=f)[2]
    h = h or size + 26
    d.rounded_rectangle((x, y, x + tw + pad * 2, y + h), radius=h // 2, fill=fill)
    d.text((x + pad, y + (h - size) / 2 - 4), text, font=f, fill=color)
    return tw + pad * 2


def subtitle(img, s, who_color=INK):
    """Clean caption between the window and the 'Kimga foydali' line."""
    if not s:
        return
    d = ImageDraw.Draw(img)
    f = font(44, "ExtraBold")
    lines = wrap(d, s, f, 940)[:3]
    y = 1372 if len(lines) < 3 else 1352
    for ln in lines:
        tw = d.textbbox((0, 0), ln, font=f)[2]
        d.text(((W - tw) / 2, y), ln, font=f, fill=who_color)
        y += 56


def avatar_circle(img, sprite, cx, cy, size, ring=ORANGE, k=1.0):
    if k <= 0.02:
        return
    head = sprite.crop((120, 60, 680, 620)).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    disc = Image.new("RGBA", (size, size), (243, 238, 232, 255))
    disc.alpha_composite(head)
    out = Image.new("RGBA", (size + 12, size + 12), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse((0, 0, size + 11, size + 11), fill=ring)
    out.paste(disc, (6, 6), mask)
    s = max(0.05, k)
    out = out.resize((max(1, int(out.width * s)), max(1, int(out.height * s))), Image.LANCZOS)
    img.alpha_composite(out, (int(cx - out.width / 2), int(cy - out.height / 2)))


def pin(d, x, y, color, label, size=1.0):
    r = 34 * size
    d.ellipse((x - r, y - 2.2 * r, x + r, y - 0.2 * r), fill=color)
    d.polygon([(x - r * 0.75, y - 0.8 * r), (x + r * 0.75, y - 0.8 * r), (x, y)], fill=color)
    d.ellipse((x - r * 0.38, y - 1.58 * r, x + r * 0.38, y - 0.82 * r), fill=(255, 255, 255))
    f = font(int(34 * size), "Black")
    tw = d.textbbox((0, 0), label, font=f)[2]
    d.text((x - tw / 2, y + 12), label, font=f, fill=INK)
