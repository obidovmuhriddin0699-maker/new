#!/usr/bin/env python3
"""Build a single-file invitation: every photo, video and the music track are
embedded as data URIs, so dist/index.html opens correctly on its own
(phone, Telegram file, file://) without the assets/ folder.

Usage:  python3 tools/build_standalone.py        → dist/index.html
Requires: ffmpeg (re-encodes media to lighter, widely compatible formats).
"""
import base64
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
OUT = ROOT / "dist" / "index.html"
TMP = Path(tempfile.mkdtemp(prefix="cp-standalone-"))


def b64(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


_cache = {}


def image_uri(src: str) -> str:
    """JPG → WebP (≈50% smaller); WebP is supported by every current mobile browser."""
    if src in _cache:
        return _cache[src]
    webp = ROOT / re.sub(r"\.(jpe?g|png)$", ".webp", src, flags=re.I)
    uri = b64(webp, "image/webp") if webp.exists() else b64(ROOT / src, "image/jpeg")
    _cache[src] = uri
    return uri


def video_uri(src: str) -> str:
    if src in _cache:
        return _cache[src]
    out = TMP / (Path(src).stem + ".mp4")
    ffmpeg("-i", str(ROOT / src), "-an", "-vf", "scale=540:-2", "-c:v", "libx264",
           "-preset", "slow", "-crf", "29", "-profile:v", "main", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(out))
    _cache[src] = b64(out, "video/mp4")
    return _cache[src]


def audio_uri(src: str) -> str:
    out = TMP / "music.mp3"
    ffmpeg("-i", str(ROOT / src), "-map", "0:a", "-map_metadata", "-1",
           "-c:a", "libmp3lame", "-b:a", "96k", str(out))
    return b64(out, "audio/mpeg")


def embed_images(node):
    if isinstance(node, dict):
        if isinstance(node.get("src"), str) and re.search(r"\.(jpe?g|png)$", node["src"], re.I):
            node["src"] = image_uri(node["src"])
            node["variants"] = []
        for v in node.values():
            embed_images(v)
    elif isinstance(node, list):
        for v in node:
            embed_images(v)


def main():
    html = SRC.read_text(encoding="utf-8")
    m = re.search(r'(<script type="application/json" id="wedding-data">)(.*?)(</script>)', html, re.S)
    data = json.loads(m.group(2))

    data["hero"]["video"] = video_uri(data["hero"]["video"])
    for clip in data.get("film", []):
        clip["src"] = video_uri(clip["src"])
        clip["poster"] = image_uri(clip["poster"])
    embed_images(data)
    if data.get("music"):
        data["music"] = audio_uri(data["music"])

    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = html[:m.start(2)] + payload + html[m.end(2):]

    # head: drop links that need the folder structure, inline the favicon
    html = re.sub(r'\s*<link rel="preload" as="image"[^>]*>', "", html)
    html = re.sub(r'\s*<link rel="manifest"[^>]*>', "", html)
    html = re.sub(r'\s*<link rel="apple-touch-icon"[^>]*>', "", html)
    html = html.replace('href="assets/icons/favicon.svg"',
                        f'href="{b64(ROOT / "assets/icons/favicon.svg", "image/svg+xml")}"')
    # standalone file never fetches data/wedding.json — embedded data is authoritative
    html = html.replace("localData: 'data/wedding.json',", "localData: '',")
    html = html.replace("if (!/^https?:$/.test(location.protocol)) return inline;",
                        "if (!/^https?:$/.test(location.protocol) || (!CONFIG.apiBase && !CONFIG.localData)) return inline;")
    html = html.replace("if ('serviceWorker' in navigator && /^https?:$/.test(location.protocol))",
                        "if (false)")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}  {OUT.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
