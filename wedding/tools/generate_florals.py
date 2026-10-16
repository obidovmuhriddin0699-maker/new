"""Generate the original botanical artwork (white roses, buds, sage leaves) as
SVG <symbol>s for the sage-and-ivory theme. Prints the symbols to stdout.

    python3 tools/generate_florals.py > /tmp/florals.svg
"""
import math
import random

random.seed(11)
OUT = []


def rose(cx, cy, r, rot=0):
    """A cupped white rose: outer petals, inner rings and a spiral heart."""
    g = [f'<g transform="rotate({rot:.0f} {cx:.1f} {cy:.1f})">']
    g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#petal)" stroke="#D8CDB6" stroke-width=".6"/>')
    for ring, (k, rr) in enumerate([(7, 0.95), (6, 0.74), (5, 0.52)]):
        for i in range(k):
            a = 2 * math.pi * i / k + ring * 0.4
            px = cx + math.cos(a) * r * rr * 0.55
            py = cy + math.sin(a) * r * rr * 0.55
            g.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r*rr*0.5:.1f}" ry="{r*rr*0.36:.1f}" '
                     f'transform="rotate({math.degrees(a)+90:.0f} {px:.1f} {py:.1f})" fill="url(#petal)" stroke="#D3C6AC" stroke-width=".5"/>')
    sp = " ".join(f"{'M' if i == 0 else 'L'}{cx+math.cos(t)*r*0.06*t:.1f} {cy+math.sin(t)*r*0.06*t:.1f}"
                  for i, t in enumerate([j * 0.35 for j in range(18)]))
    g.append(f'<path d="{sp}" fill="none" stroke="#C9B994" stroke-width=".7"/>')
    g.append('</g>')
    return "".join(g)


def leaf(x, y, length, angle, shade=0):
    w = length * 0.42
    a = math.radians(angle)
    tx, ty = x + math.cos(a) * length, y + math.sin(a) * length
    nx, ny = -math.sin(a) * w, math.cos(a) * w
    mx, my = (x + tx) / 2, (y + ty) / 2
    fill = "url(#leaf)" if shade == 0 else "url(#leaf2)"
    return (f'<path d="M{x:.1f} {y:.1f} Q{mx+nx:.1f} {my+ny:.1f} {tx:.1f} {ty:.1f} Q{mx-nx:.1f} {my-ny:.1f} {x:.1f} {y:.1f}Z" fill="{fill}"/>'
            f'<path d="M{x:.1f} {y:.1f} L{tx:.1f} {ty:.1f}" stroke="#6F7F64" stroke-width=".4" opacity=".6"/>')


def bud(x, y, r, angle):
    a = math.radians(angle)
    return (f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r*0.7:.1f}" ry="{r:.1f}" transform="rotate({angle+90:.0f} {x:.1f} {y:.1f})" fill="url(#petal)" stroke="#D3C6AC" stroke-width=".5"/>'
            + leaf(x - math.cos(a) * r * 0.6, y - math.sin(a) * r * 0.6, r * 1.3, angle + 150, 1)
            + leaf(x - math.cos(a) * r * 0.6, y - math.sin(a) * r * 0.6, r * 1.3, angle - 150, 1))


def corner():
    """Spray growing from the top-left corner (0,0) along two arcs."""
    parts = []
    stems = []
    for arc in (lambda t: (12 + 230 * t, 14 + 40 * math.sin(t * 2.2)),
                lambda t: (14 + 40 * math.sin(t * 2.2), 12 + 230 * t)):
        pts = [arc(i / 40) for i in range(41)]
        stems.append(pts)
        parts.append('<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + '" fill="none" stroke="#7D8C71" stroke-width="1.1"/>')
    for pts in stems:
        for i in range(4, 40, 4):
            x, y = pts[i]
            x2, y2 = pts[i + 1]
            ang = math.degrees(math.atan2(y2 - y, x2 - x))
            side = 1 if (i // 4) % 2 else -1
            parts.append(leaf(x, y, 16 + random.random() * 8 - i * 0.15, ang + side * 48, i % 3 == 0))
        for i in (18, 30, 38):
            x, y = pts[i]
            parts.append(bud(x, y, 5 + random.random() * 2, math.degrees(math.atan2(pts[i+1][1]-y, pts[i+1][0]-x)) if i < 40 else 0))
        for i in range(6, 40, 5):
            x, y = pts[i]
            for _ in range(3):
                dx, dy = random.uniform(-14, 14), random.uniform(-14, 14)
                parts.append(f'<circle cx="{x+dx:.1f}" cy="{y+dy:.1f}" r="{random.uniform(1.2, 2.2):.1f}" fill="#FFFDF8" stroke="#D9CFBC" stroke-width=".4"/>')
    parts.append(rose(46, 44, 30, 10))
    parts.append(rose(104, 30, 19, 40))
    parts.append(rose(28, 104, 18, -20))
    parts.append(leaf(70, 70, 26, 45))
    parts.append(leaf(64, 78, 22, 70, 1))
    return '<symbol id="floral-corner" viewBox="0 0 260 260">' + "".join(parts) + "</symbol>"


def spray():
    """A small horizontal spray (used under the arch and on cards)."""
    parts = ['<path d="M10 40 Q70 28 120 36 Q170 44 230 30" fill="none" stroke="#7D8C71" stroke-width="1"/>']
    for i, x in enumerate(range(24, 220, 18)):
        y = 40 - (x - 10) * 0.02 + math.sin(x / 30) * 4
        parts.append(leaf(x, y, 14, -40 if i % 2 else 220 - 180 + 140, i % 3 == 0))
    parts.append(rose(120, 34, 14, 0))
    parts.append(rose(92, 38, 9, 30))
    parts.append(rose(148, 37, 9, -30))
    parts.append(bud(60, 34, 4.5, -160))
    parts.append(bud(184, 36, 4.5, -20))
    return '<symbol id="floral-spray" viewBox="0 0 240 70">' + "".join(parts) + "</symbol>"


defs = ('<linearGradient id="petal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFEFB"/><stop offset="1" stop-color="#EFE7D6"/></linearGradient>'
        '<linearGradient id="leaf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A9B79A"/><stop offset="1" stop-color="#6F8063"/></linearGradient>'
        '<linearGradient id="leaf2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#C6D0B8"/><stop offset="1" stop-color="#8E9E80"/></linearGradient>')
print(defs)
print(corner())
print(spray())
