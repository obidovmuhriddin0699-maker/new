"""Generate the atmospheric cloud layers used by the site.

Clouds are painted like cumulus: clusters of overlapping soft "puffs", each
lit from above, composited back to front. Every puff is also drawn one tile
to the left and right, so each layer tiles horizontally and the CSS drift
animation loops without a seam.

    python3 tools/generate_clouds.py        # writes assets/clouds/*.webp

Requires Pillow and NumPy.
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "assets" / "clouds"

LIGHT = np.array([255, 253, 249], dtype=np.float32)   # sunlit tops (warm ivory)
SHADOW = np.array([219, 203, 186], dtype=np.float32)  # undersides (champagne)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def paint(w, h, puffs, softness):
    rgb = np.zeros((h, w, 3), np.float32)
    alpha = np.zeros((h, w), np.float32)
    for cx, cy, r, shade, op in sorted(puffs, key=lambda p: p[1] - p[2] * 0.2):
        for ox in (-w, 0, w):
            x0, x1 = int(max(cx + ox - r, 0)), int(min(cx + ox + r + 1, w))
            y0, y1 = int(max(cy - r, 0)), int(min(cy + r + 1, h))
            if x0 >= x1 or y0 >= y1:
                continue
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            dx, dy = (xx - cx - ox) / r, (yy - cy) / r
            d = np.sqrt(dx**2 + dy**2)
            a = (1 - smoothstep(1 - softness, 1.0, d)) * op
            # Lit from slightly above-left; deeper puffs (shade) are darker overall.
            lit = np.clip(0.78 - 0.55 * dy - 0.12 * dx - shade, 0, 1)
            col = SHADOW + (LIGHT - SHADOW) * lit[..., None]
            ra = alpha[y0:y1, x0:x1]
            rgb[y0:y1, x0:x1] = col * a[..., None] + rgb[y0:y1, x0:x1] * (1 - a[..., None])
            alpha[y0:y1, x0:x1] = a + ra * (1 - a)
    return rgb, alpha


def cluster(rng, cx, base_y, width, height, size, n):
    """One cumulus: a flat-bottomed dome of puffs."""
    out = []
    for _ in range(n):
        u = rng.uniform(-1, 1)
        x = cx + u * width / 2
        dome = np.sqrt(max(1 - u * u, 0.05))  # taller in the middle
        y = base_y - rng.uniform(0, 1) ** 0.7 * height * dome
        r = size * rng.uniform(0.55, 1.15) * (0.55 + 0.45 * dome)
        y = min(y, base_y - r * 0.35)          # keep the bottom flat-ish
        depth = (y - (base_y - height)) / max(height, 1)
        out.append((x, y, r, 0.18 * depth, rng.uniform(0.75, 1.0)))
    return out


def save(name, rgb, alpha, blur, opacity):
    w = alpha.shape[1]
    colour = rgb / np.maximum(alpha, 1e-4)[..., None]
    # Fully transparent pixels take the light colour, so blurring can't pull a dark fringe in.
    colour = np.where(alpha[..., None] > 0.02, colour, LIGHT)
    img = np.dstack([colour, alpha * 255 * opacity])
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8), "RGBA")
    # Blur a 3x tiled strip so the left/right edges stay continuous.
    strip = Image.new("RGBA", (w * 3, im.height))
    for i in range(3):
        strip.paste(im, (i * w, 0))
    im = strip.filter(ImageFilter.GaussianBlur(blur)).crop((w, 0, 2 * w, im.height))
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.webp"
    im.save(path, "WEBP", quality=78, method=6)
    print(f"{path.name}: {im.width}x{im.height}, {path.stat().st_size // 1024} KB")


def wisps(rng, w, h, n, y_range):
    """Far layer: long, thin, translucent streaks."""
    puffs = []
    for _ in range(n):
        cx, cy = rng.uniform(0, w), rng.uniform(*y_range) * h
        length = rng.uniform(260, 620)
        for t in np.linspace(-0.5, 0.5, int(length / 18)):
            r = rng.uniform(16, 34) * (1 - abs(t) * 1.2)
            puffs.append((cx + t * length, cy + rng.normal(0, 4) + t * 20, max(r, 6), 0.05,
                          rng.uniform(0.25, 0.5)))
    return puffs


if __name__ == "__main__":
    rng = np.random.default_rng(7)

    w, h = 2048, 520
    rgb, a = paint(w, h, wisps(rng, w, h, 16, (0.25, 0.8)), 0.9)
    save("clouds-far", rgb, a, 6, 0.75)

    w, h = 2048, 640
    puffs = []
    for cx in np.linspace(0, w, 6, endpoint=False) + rng.uniform(-60, 60, 6):
        puffs += cluster(rng, cx, h * rng.uniform(0.72, 0.9), rng.uniform(260, 420),
                         rng.uniform(140, 230), rng.uniform(48, 70), 46)
    rgb, a = paint(w, h, puffs, 0.75)
    save("clouds-mid", rgb, a, 4, 0.9)

    w, h = 2048, 560
    puffs = []
    for cx in np.linspace(0, w, 9, endpoint=False) + rng.uniform(-40, 40, 9):
        puffs += cluster(rng, cx, h + 40, rng.uniform(320, 480), rng.uniform(230, 330),
                         rng.uniform(70, 100), 60)
    rgb, a = paint(w, h, puffs, 0.65)
    save("clouds-near", rgb, a, 3, 1.0)
