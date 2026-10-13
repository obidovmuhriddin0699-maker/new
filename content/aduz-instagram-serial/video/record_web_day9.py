"""9-qism veb-sahifasini (web/kun-09-hudud.html) ovozli video rolikka aylantirish.

Brauzerda sahifa ochiladi va ovoz bilan sinxron "ssenariy" bajariladi: aylantirish, qidiruvga yozish,
tugma/tab bosish. Kadrlar CDP screencast orqali yoziladi, so'ng 30 fps ga yig'ilib, ustiga yumshoq kamera
harakati (qotishsiz), subtitr, ovoz, musiqa va klik effektlari qo'shiladi.

Ishga tushirish:  python3 record_web_day9.py <chiqish.mp4>
Kerak: playwright (python), Chromium, ffmpeg, RHVoice (voice.py).
"""
import asyncio
import base64
import glob
import math
import os
import subprocess
import sys
import tempfile
import time

import numpy as np
from PIL import Image, ImageDraw

import voice
from make_day2 import FPS, add, font, noise, tone, wrap

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "..", "web", "kun-09-hudud.html")
W, H = 1080, 1920
SR = voice.SR

# (speaker, text with emotions, subtitle, rate_mul)
VOICE = {
    "r0": ("rus8", "[sad]Farg'onadagi do'konim uchun[p=100]Toshkent kanaliga reklama berdim...",
           "Farg‘onadagi do‘konim uchun Toshkent kanaliga reklama berdim...", 1.1),
    "r1": ("rus8", "[ironic]Toshkentdan divan olgani kim keladi?!", "Toshkentdan divan olgani kim keladi?!", 1.05),
    "n2": ("narr", "[happy]Aduzda kanalni hudud va mavzu bo'yicha qidirasiz.",
           "ADUZ'da kanalni hudud va mavzu bo‘yicha qidirasiz.", 0.97),
    "n3": ("narr", "[warm]Hududni tanlang —[p=100]ro'yxat darhol yangilanadi.",
           "Hududni tanlang — ro‘yxat darhol yangilanadi.", 0.97),
    "n4": ("narr", "[neutral]Viloyatlar bo'yicha kanallar alohida ko'rinadi.",
           "Viloyatlar bo‘yicha kanallar alohida ko‘rinadi.", 0.97),
    "n5": ("narr", "[neutral]Har bir kanal auditoriyasi qayerda ekani oldindan ko'rinadi.",
           "Har bir kanal auditoriyasi qayerda ekani oldindan ko‘rinadi.", 0.97),
    "r6": ("rus8", "[ironic]Toshkent bozori?[p=150]Yo'q, rahmat!", "Toshkent bozori? Yo‘q, rahmat!", 1.0),
    "r7": ("rus8", "[excited]Mana, Farg'ona kanali —[p=100]menga shu kerak!", "Mana, Farg‘ona kanali — menga shu kerak!", 1.0),
    "n8": ("narr", "[happy]Mahalliy biznes egasi do'stingizga yuboring!", "Mahalliy biznes egasi do‘stingizga yuboring!", 0.97),
    "n9": ("narr", "[excited]Bot: Target reklama bot.[p=150]Ertaga narxlarni solishtiramiz!",
           "Bot: @Targetreklammabot. Ertaga narxlarni solishtiramiz!", 0.97),
}

# ---------------------------------------------------------------- browser helpers
SCROLL_JS = """
async ([sel, dur, off]) => {
  const el = sel === 'top' ? null : document.querySelector(sel);
  const y0 = window.scrollY;
  const y1 = el ? el.getBoundingClientRect().top + window.scrollY - off : 0;
  const t0 = performance.now();
  await new Promise(res => {
    const step = now => {
      const k = Math.min(1, (now - t0) / dur);
      const e = k < .5 ? 4*k*k*k : 1 - Math.pow(-2*k + 2, 3) / 2;
      window.scrollTo(0, y0 + (y1 - y0) * e);
      k < 1 ? requestAnimationFrame(step) : res();
    };
    requestAnimationFrame(step);
  });
}
"""
DRIFT_JS = """
async ([px, dur]) => {
  const y0 = window.scrollY, t0 = performance.now();
  await new Promise(res => {
    const step = now => {
      const k = Math.min(1, (now - t0) / dur);
      window.scrollTo(0, y0 + px * Math.sin(k * Math.PI));
      k < 1 ? requestAnimationFrame(step) : res();
    };
    requestAnimationFrame(step);
  });
}
"""


async def record(frames_dir, durations):
    from playwright.async_api import async_playwright
    exe = (glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome") + [None])[0]
    log = []          # (time, kind, key)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=exe, args=["--force-color-profile=srgb"])
        ctx = await browser.new_context(viewport={"width": 540, "height": 960}, device_scale_factor=2,
                                        color_scheme="light", permissions=["clipboard-read", "clipboard-write"])
        page = await ctx.new_page()
        await page.goto("file://" + os.path.abspath(PAGE))
        await page.wait_for_load_state("networkidle")
        await page.evaluate("document.fonts.ready")
        await page.add_style_tag(content="html{scrollbar-width:none} ::-webkit-scrollbar{display:none}")
        cdp = await ctx.new_cdp_session(page)
        frames = []
        t_start = [None]

        def on_frame(ev):
            ts = ev["metadata"]["timestamp"]
            if t_start[0] is None:
                t_start[0] = ts
            path = os.path.join(frames_dir, f"{len(frames):05d}.jpg")
            with open(path, "wb") as f:
                f.write(base64.b64decode(ev["data"]))
            frames.append((ts - t_start[0], path))
            asyncio.ensure_future(cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]}))

        cdp.on("Page.screencastFrame", on_frame)
        await cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": W, "maxHeight": H,
                                                "everyNthFrame": 1})
        wall0 = time.monotonic()
        now = lambda: time.monotonic() - wall0

        async def say(key, extra=0.25):
            log.append((now(), "say", key))
            return durations[key] + extra

        async def hold(sec, drift=26):
            await page.evaluate(DRIFT_JS, [drift, int(sec * 1000)])

        async def scroll(sel, dur=1.0, off=40):
            log.append((now(), "whoosh", sel))
            await page.evaluate(SCROLL_JS, [sel, int(dur * 1000), off])

        async def click(sel):
            log.append((now(), "click", sel))
            await page.click(sel)

        async def type_text(sel, text):
            await page.click(sel)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            for ch in text:
                log.append((now(), "key", ch))
                await page.keyboard.insert_text(ch)
                await asyncio.sleep(0.085)

        # ---------- scenario
        await hold(0.6)
        d = await say("r0"); await hold(d)
        await scroll("#hudud", 1.1)
        d = await say("r1"); await hold(max(d, 2.2))
        await scroll("#qidiruv", 1.1, 20)
        d = await say("n2")
        t0 = now()
        await type_text("#q", "Farg‘ona mebel")
        await hold(max(0.6, d - (now() - t0)) + 0.6)
        d = await say("n3")
        t0 = now()
        await type_text("#q", "mebel")
        await asyncio.sleep(0.3)
        await click("#regionChips .chip:nth-child(3)")   # Andijon
        await hold(1.0)
        await click("#regionChips .chip:nth-child(2)")   # Farg'ona
        await hold(max(0.8, d - (now() - t0)) + 0.4)
        await scroll("#viloyat", 1.1, 20)
        d = await say("n4")
        t0 = now()
        for i in (2, 3, 1):
            await hold(0.25, 0)
            await click(f".tabs button:nth-of-type({i})")
            await hold(1.0, 10)
        await hold(max(0.4, d - (now() - t0)))
        await scroll("#kanal", 1.1, 20)
        d = await say("n5"); await hold(d + 0.2)
        await click('#pick .chip[data-n="Toshkent bozori"]')
        await hold(0.5)
        d = await say("r6"); await hold(d + 0.3)
        await click('#pick .chip[data-n="Farg‘ona Bugun"]')
        await hold(0.4)
        d = await say("r7"); await hold(d + 0.4)
        await scroll("#yuboring", 1.2, 20)
        d = await say("n8")
        await hold(1.2)
        await click("#copyMsg")
        await hold(max(0.6, d - 1.2))
        d = await say("n9"); await hold(d + 1.4)
        total = now()
        await cdp.send("Page.stopScreencast")
        await browser.close()
    return frames, log, total


# ---------------------------------------------------------------- compose
def subtitle(img, s, who):
    if not s:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(46, "ExtraBold")
    lines = wrap(d, s, f, 900)[:3]
    lh = 60
    box_h = len(lines) * lh + 44
    y0 = 1430 - box_h
    d.rounded_rectangle((60, y0, W - 60, y0 + box_h), radius=36, fill=(23, 24, 31, 228))
    col = (255, 255, 255) if who == "narr" else (255, 196, 160)
    y = y0 + 22
    for ln in lines:
        tw = d.textbbox((0, 0), ln, font=f)[2]
        d.text(((W - tw) / 2, y), ln, font=f, fill=col)
        y += lh
    img.alpha_composite(layer)


def camera(img, t, total):
    z = 1.03 + 0.012 * math.sin(t * 0.5)
    dx = 12 * math.sin(t * 0.7)
    dy = 9 * math.cos(t * 0.55)
    nw, nh = int(W * z), int(H * z)
    big = img.resize((nw, nh), Image.BICUBIC)
    x0 = int((nw - W) / 2 + dx)
    y0 = int((nh - H) / 2 + dy)
    return big.crop((x0, y0, x0 + W, y0 + H))


def music_and_sfx(log, dur):
    buf = np.zeros(int(SR * dur) + SR)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 96
    prog_ = [(60, 64, 67, 71), (57, 60, 64, 67), (53, 57, 60, 64), (55, 59, 62, 65)]
    t, n = 0.0, 0
    while t < dur - 0.5:
        chord = prog_[int(n / 4) % 4]
        if n % 4 == 0:
            for m in chord:
                add(buf, tone(note(m), beat * 4, decay=0.5, harmonics=(1, 0.15), vol=0.045), t)
            add(buf, tone(note(chord[0] - 24), beat * 3, decay=1.0, harmonics=(1, 0.4), vol=0.16), t)
        if n % 2 == 0:
            add(buf, tone(60, 0.25, decay=18, harmonics=(1, 0.3), vol=0.3), t)
        add(buf, noise(0.04, 0.1, 1) * np.exp(-80 * np.arange(int(0.04 * SR)) / SR), t + beat / 2)
        add(buf, tone(note(chord[(n * 2) % 4] + 12), 0.3, decay=9, harmonics=(1, 0.2), vol=0.04), t + beat / 2)
        t += beat
        n += 1
    for (tt, kind, key) in log:
        if kind == "whoosh":
            add(buf, noise(0.4, 0.22, 40) * np.sin(np.linspace(0, np.pi, int(0.4 * SR))), tt)
        elif kind == "click":
            add(buf, tone(1500, 0.06, decay=60, harmonics=(1,), vol=0.3), tt)
        elif kind == "key":
            add(buf, noise(0.03, 0.16, 1) * np.exp(-90 * np.arange(int(0.03 * SR)) / SR), tt)
    return buf[: int(SR * dur)]


def main(out):
    tmp = tempfile.mkdtemp()
    # 1) voices first: we need their lengths to pace the browser scenario
    durations, rendered = {}, {}
    for i, (k, (who, txt, sub, rm)) in enumerate(VOICE.items()):
        sig = voice.render_line(txt, who, tmp, i, rate_mul=rm)
        rendered[k] = sig
        durations[k] = len(sig) / SR
    # 2) record the page
    frames_dir = os.path.join(tmp, "frames")
    os.makedirs(frames_dir)
    frames, log, total = asyncio.run(record(frames_dir, durations))
    dur = total
    print(f"captured {len(frames)} frames over {dur:.1f}s")
    # align: browser wall-clock (log) vs screencast timestamps start almost together; use screencast t=0 as origin
    # 3) speech track at logged times
    lines = []
    for (tt, kind, key) in log:
        if kind == "say":
            who, txt, sub, rm = VOICE[key]
            lines.append((tt, who, txt, sub, rm))
    speech, envs, timings = voice.build_speech(lines, dur, FPS, tmp)
    voice.qa(lines, timings, speech)
    wav = os.path.join(tmp, "mix.wav")
    voice.mix(speech, music_and_sfx(log, dur), wav, tmp)
    # 4) compose frames at 30 fps (latest captured frame <= t), camera + subtitles
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    times = [f[0] for f in frames]
    j = 0
    cache = (None, None)
    for i in range(int(dur * FPS)):
        t = i / FPS
        while j + 1 < len(times) and times[j + 1] <= t:
            j += 1
        path = frames[j][1]
        if cache[0] != path:
            base = Image.open(path).convert("RGBA")
            if base.size != (W, H):
                base = base.resize((W, H), Image.LANCZOS)
            cache = (path, base)
        img = camera(cache[1], t, dur)
        for (a, b, who, sub) in timings:
            if a - 0.05 <= t <= b + 0.3:
                subtitle(img, sub, who)
        proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()
    print("done", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "aduz_9-kun_web.mp4")
