#!/usr/bin/env python3
"""
build-single.py — packs the whole site into ONE self-contained file:
dist/index.html (open it by double-click, send it on Telegram, upload anywhere).

  python3 build-single.py

Requires Node.js (esbuild is fetched once with npx). What it does:
  * bundles js/app.js and its modules into one script (esbuild, IIFE, minified)
  * inlines all CSS, with the fonts as data: URIs
  * embeds data/wedding.json as <script id="wedding-data">
  * embeds media as data: URIs in window.__ASSETS — the largest WebP of each
    photo, the MP4 videos and the MP3 music (plays in every browser)
The multi-file site stays the recommended way to host: it loads lazily and
serves AVIF + WebP at the right size. The single file trades that for portability.
"""
import base64
import json
import mimetypes
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
CSS = ["css/fonts.css", "css/base.css", "css/components.css", "css/clouds.css", "css/animations.css", "css/responsive.css"]

mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/avif", ".avif")
mimetypes.add_type("audio/mp4", ".m4a")
mimetypes.add_type("video/mp4", ".mp4")


def data_uri(rel):
    path = ROOT / rel
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def bundle_js():
    out = subprocess.run(
        ["npx", "--yes", "esbuild@0.24.0", "js/app.js", "--bundle", "--format=iife",
         "--minify", "--target=es2020", "--legal-comments=none"],
        cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("esbuild failed:\n" + out.stderr)
    return out.stdout


def inline_css():
    parts = []
    for rel in CSS:
        css = (ROOT / rel).read_text(encoding="utf-8")
        base = (ROOT / rel).parent
        def repl(m):
            target = (base / m.group(1)).resolve().relative_to(ROOT).as_posix()
            return f'url("{data_uri(target)}")'
        parts.append(re.sub(r'url\(["\']?(\.\./assets/[^"\')]+)["\']?\)', repl, css))
    return "\n".join(parts)


def collect_assets(data):
    """Only what the page actually uses."""
    paths = set()
    for item in [*data.get("gallery", []), *({"id": k, **v} for k, v in data.get("images", {}).items())]:
        paths.add(f"assets/images/{item['id']}-{max(item.get('widths', [960]))}.webp")
    for film in data.get("films", {}).values():
        if film.get("video"):
            paths.add(f"{film['video']}.mp4")
        if film.get("poster"):
            paths.add(film["poster"])
    if data.get("music"):
        paths.add(data["music"])
    return {p: data_uri(p) for p in sorted(paths) if (ROOT / p).exists()}


def main():
    data = json.loads((ROOT / "data/wedding.json").read_text(encoding="utf-8"))
    # MP3 plays everywhere (Firefox on Linux may lack AAC), so the single file carries only it.
    if data.get("musicFallback"):
        data["music"] = data.pop("musicFallback")
    assets = collect_assets(data)

    html = (ROOT / "index.html").read_text(encoding="utf-8")
    # drop external CSS/JS, manifest and preloads — everything is inline now
    html = re.sub(r'\s*<link rel="(stylesheet|preload|manifest)"[^>]*>', "", html)
    html = re.sub(r'\s*<script (type="module"|defer) src="js/[^"]+"></script>', "", html)
    html = html.replace('href="assets/icons/favicon.svg"', f'href="{data_uri("assets/icons/favicon.svg")}"')
    html = html.replace('href="assets/icons/apple-touch-icon.png"', f'href="{data_uri("assets/icons/apple-touch-icon.png")}"')
    # hero media is written straight into the markup so nothing relative is requested
    html = re.sub(r'\s*<source src="assets/video/[^"]+\.webm"[^>]*>', "", html)
    html = re.sub(r'(src|href)="(assets/video/[^"]+\.(?:mp4|webp))"', lambda m: f'{m.group(1)}="{data_uri(m.group(2))}"', html)
    html = html.replace("</head>", f"<style>\n{inline_css()}\n</style>\n</head>", 1)

    payload = (
        '<script id="wedding-data" type="application/json">'
        + json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        + "</script>\n"
        + "<script>window.__BUNDLE=true;window.__ASSETS="
        + json.dumps(assets)
        + ";</script>\n<script>"
        + bundle_js().replace("</script", "<\\/script")
        + "</script>\n</body>"
    )
    html = html.replace("</body>", payload, 1)

    DIST.mkdir(exist_ok=True)
    out = DIST / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size / 1e6:.1f} MB  ({len(assets)} embedded files)")


if __name__ == "__main__":
    main()
