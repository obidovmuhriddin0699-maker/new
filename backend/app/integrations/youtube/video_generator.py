"""Automated YouTube Shorts video generator using Edge TTS, Pillow, and FFmpeg.

Creates high-definition (1080x1920) vertical YouTube Shorts with:
- Natural Neural Text-to-Speech (Uzbek, Russian, English)
- Aesthetic dark-mode kinetic visual cards and typography
- Clean subtitles and branding badges
- Fast and reliable FFmpeg rendering (via imageio-ffmpeg)
"""

import logging
import os
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("app.integrations.youtube.video_generator")

DEFAULT_VOICES = {
    "uz": "uz-UZ-SardorNeural",
    "ru": "ru-RU-DmitryNeural",
    "en": "en-US-ChristopherNeural",
}

FEMALE_VOICES = {
    "uz": "uz-UZ-MadinaNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "en": "en-US-JennyNeural",
}

WIDTH = 1080
HEIGHT = 1920


def get_ffmpeg_path() -> str:
    """Return static ffmpeg executable path."""
    return imageio_ffmpeg.get_ffmpeg_exe()


def _get_font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    """Load default truetype font or fallback to system font."""
    font_candidates = [
        "arial.ttf",
        "segoeui.ttf",
        "calibri.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
    ]
    for candidate in font_candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:  # noqa: S112
            continue
    return ImageFont.load_default()


def create_slide_image(
    *,
    badge_text: str,
    main_text: str,
    step_indicator: str,
    channel_name: str = "@MuxriddinAI",
    theme_color: tuple[int, int, int] = (99, 102, 241),
    output_png_path: str,
) -> None:
    """Draw a 1080x1920 vertical visual card."""
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Gradient glow in the background
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(15 + ratio * 20)
        g = int(23 + ratio * 15)
        b = int(42 + ratio * 50)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Top Accent Line
    draw.rectangle([(0, 0), (WIDTH, 12)], fill=theme_color)

    font_badge = _get_font(34)
    font_step = _get_font(42)
    font_main = _get_font(60)
    font_footer = _get_font(34)
    font_sub_footer = _get_font(28)

    # Step Badge (e.g. "DIQQAT" or "MASLAHAT 1")
    pill_box = [(WIDTH // 2 - 260, 260), (WIDTH // 2 + 260, 340)]
    draw.rounded_rectangle(pill_box, radius=40, fill=(30, 41, 59), outline=theme_color, width=3)
    draw.text((WIDTH // 2, 300), step_indicator, fill=(255, 255, 255), font=font_badge, anchor="mm")

    # Topic badge below step
    draw.text(
        (WIDTH // 2, 420),
        badge_text.upper(),
        fill=(148, 163, 184),
        font=font_step,
        anchor="mm",
    )

    # Main Content Card
    card_margin = 80
    card_top = 540
    card_bottom = 1460
    card_box = [(card_margin, card_top), (WIDTH - card_margin, card_bottom)]

    draw.rounded_rectangle(card_box, radius=48, fill=(24, 33, 56), outline=(51, 65, 85), width=3)

    quote_font = _get_font(120)
    draw.text(
        (card_margin + 50, card_top + 60),
        "“",
        fill=theme_color,
        font=quote_font,
        anchor="lt",
    )

    # Wrap main text
    wrapped_lines = textwrap.wrap(main_text, width=22)
    line_spacing = 95
    total_text_height = len(wrapped_lines) * line_spacing
    text_start_y = card_top + ((card_bottom - card_top) - total_text_height) // 2 + 10

    for idx, line in enumerate(wrapped_lines):
        line_y = text_start_y + (idx * line_spacing)
        draw.text((WIDTH // 2 + 3, line_y + 3), line, fill=(0, 0, 0), font=font_main, anchor="mm")
        draw.text((WIDTH // 2, line_y), line, fill=(248, 250, 252), font=font_main, anchor="mm")

    # Footer Branding
    footer_y = 1680
    draw.text(
        (WIDTH // 2, footer_y),
        channel_name,
        fill=(203, 213, 225),
        font=font_footer,
        anchor="mm",
    )
    draw.text(
        (WIDTH // 2, footer_y + 60),
        "Obuna bo'ling va layk bosing",
        fill=(148, 163, 184),
        font=font_sub_footer,
        anchor="mm",
    )

    img.save(output_png_path, "PNG")


async def render_audio_segment(text: str, voice: str, output_mp3_path: str) -> None:
    """Generate neural TTS voiceover for a given text segment."""
    comm = edge_tts.Communicate(text, voice)
    await comm.save(output_mp3_path)


def create_video_clip_ffmpeg(
    ffmpeg_exe: str,
    image_path: str,
    audio_path: str,
    output_clip_path: str,
) -> None:
    """Render a single still slide + audio into a high quality MP4 clip."""
    cmd = [
        ffmpeg_exe,
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-movflags", "+faststart",
        output_clip_path,
    ]
    subprocess.run(  # noqa: S603
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        check=True,
    )


def concat_video_clips(ffmpeg_exe: str, clip_paths: list[str], output_video_path: str) -> None:
    """Concatenate multiple video clips into one final video."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        list_file = f.name
        for p in clip_paths:
            clean_path = p.replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    try:
        cmd = [
            ffmpeg_exe,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            "-movflags", "+faststart",
            output_video_path,
        ]
        subprocess.run(  # noqa: S603
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True,
        )
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)


async def generate_shorts_video(
    *,
    topic: str,
    hook: str,
    segments: list[str],
    cta: str,
    language: str = "uz",
    voice: str | None = None,
    output_path: str | Path,
    channel_name: str = "@MuxriddinAI",
) -> str:
    """Generate a complete vertical YouTube Shorts video (.mp4) with voiceover and slides."""
    ffmpeg_exe = get_ffmpeg_path()
    output_file = Path(output_path).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    eff_voice = voice or DEFAULT_VOICES.get(language, DEFAULT_VOICES["uz"])
    work_dir = Path(tempfile.mkdtemp(prefix="shorts_gen_"))

    slides_data = [
        {
            "step": "DIQQAT (HOOK)",
            "text": hook,
            "badge": topic[:30],
            "theme": (239, 68, 68),
        }
    ]

    for i, seg in enumerate(segments, 1):
        slides_data.append(
            {
                "step": f"MASLAHAT #{i}",
                "text": seg,
                "badge": topic[:30],
                "theme": (99, 102, 241),
            }
        )

    slides_data.append(
        {
            "step": "XULOSA (CTA)",
            "text": cta,
            "badge": "KANALGA OBUNA BO'LING",
            "theme": (16, 185, 129),
        }
    )

    clip_paths = []

    try:
        logger.info("Shorts video generatsiyasi boshlandi: %s ta slayd", len(slides_data))

        for idx, item in enumerate(slides_data):
            img_path = str(work_dir / f"slide_{idx}.png")
            audio_path = str(work_dir / f"audio_{idx}.mp3")
            clip_path = str(work_dir / f"clip_{idx}.mp4")

            create_slide_image(
                badge_text=item["badge"],
                main_text=item["text"],
                step_indicator=item["step"],
                channel_name=channel_name,
                theme_color=item["theme"],
                output_png_path=img_path,
            )

            await render_audio_segment(item["text"], eff_voice, audio_path)
            create_video_clip_ffmpeg(ffmpeg_exe, img_path, audio_path, clip_path)
            clip_paths.append(clip_path)

        concat_video_clips(ffmpeg_exe, clip_paths, str(output_file))
        logger.info("Video muvaffaqiyatli tayyorlandi: %s", output_file)
        return str(output_file)

    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
