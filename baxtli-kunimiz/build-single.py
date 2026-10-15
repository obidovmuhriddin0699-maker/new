#!/usr/bin/env python3
"""
build-single.py — packs the invitation into ONE self-contained file: dist/index.html
(open it by double-click, send it on Telegram, upload anywhere).

  python3 build-single.py

Needs Node.js (esbuild is fetched once with npx). Inlines CSS (fonts, artwork),
bundles the JS, embeds data/wedding.json and every image, video (MP4), the music
(MP3) and the sound effects as data: URIs.
"""
import base64, json, mimetypes, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
CSS = ["css/fonts.css", "css/base.css", "css/intro.css", "css/sections.css", "css/motion.css"]
SOUNDS = ["seal-crack", "envelope-open", "card-slide", "shimmer", "click", "pop", "whoosh", "success", "page", "heartbeat"]

for ext, mime in ((".woff2", "font/woff2"), (".webp", "image/webp"), (".svg", "image/svg+xml"), (".mp4", "video/mp4"), (".mp3", "audio/mpeg")):
    mimetypes.add_type(mime, ext)


def data_uri(rel):
    p = ROOT / rel
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def bundle_js():
    out = subprocess.run(["npx", "--yes", "esbuild@0.24.0", "js/app.js", "--bundle", "--format=iife", "--minify",
                          "--target=es2017,safari12,chrome61", "--legal-comments=none"], cwd=ROOT, capture_output=True, text=True)
    if out.returncode:
        sys.exit("esbuild failed:\n" + out.stderr)
    return out.stdout


def inline_css():
    parts = []
    for rel in CSS:
        css = (ROOT / rel).read_text(encoding="utf-8")
        base = (ROOT / rel).parent
        css = re.sub(r'url\(["\']?(\.\./assets/[^"\')]+)["\']?\)',
                     lambda m: f'url("{data_uri((base / m.group(1)).resolve().relative_to(ROOT).as_posix())}")', css)
        parts.append(css)
    return "\n".join(parts)


def js_assets(data):
    paths = set()
    for item in data.get("gallery", []):
        paths.add(f"assets/images/{item['id']}-{max(item.get('widths', [960]))}.webp")
    for key, img in data.get("images", {}).items():
        paths.add(f"assets/images/{key}-{max(img.get('widths', [960]))}.webp")
    # the hero video and poster are written straight into the markup; the finale is set from JS
    paths.update([f"{data['finale']['video']}.mp4", data["finale"]["poster"]])
    paths.add(data["music"])
    paths.update(f"assets/sfx/{s}.mp3" for s in SOUNDS)
    return {p: data_uri(p) for p in sorted(paths) if (ROOT / p).exists()}


def main():
    data = json.loads((ROOT / "data/wedding.json").read_text(encoding="utf-8"))
    if data.get("musicFallback"):                    # MP3 plays in every browser
        data["music"] = data.pop("musicFallback")
    assets = js_assets(data)

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    html = re.sub(r'\s*<link rel="(stylesheet|preload|manifest)"[^>]*>', "", html)
    html = re.sub(r'\s*<script (type="module"|defer) src="js/[^"]+"></script>', "", html)
    html = re.sub(r'\s*<source src="assets/[^"]+\.webm"[^>]*>', "", html)
    # every remaining local file referenced by the markup (icons, poster, hero video, rose, paper pattern)
    html = re.sub(r'(src|href)="(assets/[^"]+)"', lambda m: f'{m.group(1)}="{data_uri(m.group(2))}"', html)
    html = html.replace("</head>", f"<style>\n{inline_css()}\n</style>\n</head>", 1)
    payload = ('<script id="wedding-data" type="application/json">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
               + "<script>window.__BUNDLE=true;window.__ASSETS=" + json.dumps(assets) + ";</script>\n"
               + "<script>" + bundle_js().replace("</script", "<\\/script") + "</script>\n</body>")
    html = html.replace("</body>", payload, 1)
    DIST.mkdir(exist_ok=True)
    out = DIST / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1e6:.1f} MB  ({len(assets)} embedded files)")


if __name__ == "__main__":
    main()
