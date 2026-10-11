"""Bundle the whole site into one self-contained file: dist/index.html.

Every stylesheet, script, font, photo, cloud layer, icon and the music track is
inlined (data URIs), so the file opens by double-click, from Telegram, a USB
stick or any host — no other files needed. config.js stays readable near the
top of the file, so texts and settings can still be edited in place.

    python3 tools/build_single.py

Photos are embedded once, at their largest size (the multi-file site keeps the
smaller responsive sizes for faster mobile loading).
"""

import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "index.html"

MIME = {
    ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml",
    ".woff2": "font/woff2", ".m4a": "audio/mp4",
}


def data_uri(path: Path) -> str:
    return f"data:{MIME[path.suffix]};base64,{base64.b64encode(path.read_bytes()).decode()}"


def inline_css(href: str) -> str:
    css_path = ROOT / href
    css = css_path.read_text(encoding="utf-8")

    def repl(m):
        target = (css_path.parent / m.group(2)).resolve()
        return f'url("{data_uri(target)}")'

    css = re.sub(r"url\((['\"]?)(\.\./[^'\")]+)\1\)", repl, css)
    return f"<style>/* {href} */\n{css}</style>"


def inline_js(src: str) -> str:
    js = (ROOT / src).read_text(encoding="utf-8")
    assert "</script" not in js.lower(), f"{src} contains </script>"
    return f"<script>/* {src} */\n{js}</script>"


def asset_map() -> dict:
    """Largest width of every photo + the music track, keyed by the path the JS asks for."""
    assets = {}
    best = {}
    for f in (ROOT / "assets" / "images").glob("*.webp"):
        m = re.match(r"(.+)-(\d+)$", f.stem)
        if m and int(m.group(2)) > best.get(m.group(1), (0, None))[0]:
            best[m.group(1)] = (int(m.group(2)), f)
    for _, f in best.values():
        assets[f"assets/images/{f.name}"] = data_uri(f)
    for f in (ROOT / "assets" / "audio").glob("*.m4a"):
        assets[f"assets/audio/{f.name}"] = data_uri(f)
    return assets


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    # Preloads and the relative og:image make no sense inside a single file.
    html = re.sub(r'\s*<link rel="preload"[^>]*>', "", html)
    html = re.sub(r'\s*<meta property="og:image[^>]*>', "", html)
    html = html.replace('href="assets/icons/favicon.svg"', f'href="{data_uri(ROOT / "assets/icons/favicon.svg")}"')
    html = html.replace('href="assets/icons/apple-touch-icon.png"',
                        f'href="{data_uri(ROOT / "assets/icons/apple-touch-icon.png")}"')

    html = re.sub(r'<link rel="stylesheet" href="([^"]+)">', lambda m: inline_css(m.group(1)), html)

    assets = asset_map()
    asset_script = "<script>window.__ASSETS=" + json.dumps(assets, separators=(",", ":")) + ";</script>"
    first = True

    def repl_script(m):
        nonlocal first
        out = inline_js(m.group(1))
        if first:  # assets before config.js, so everything can resolve them
            out = asset_script + "\n" + out
            first = False
        return out

    html = re.sub(r'<script src="([^"]+)" defer></script>', repl_script, html)
    assert 'src="js/' not in html and 'href="css/' not in html, "something was not inlined"

    html = html.replace("<head>", "<head>\n  <!-- Single-file build of the Love in the Clouds invitation "
                        "(tools/build_single.py). Edit settings in the config.js block below. -->", 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size / 1_048_576:.1f} MB, {len(assets)} embedded assets")


if __name__ == "__main__":
    main()
