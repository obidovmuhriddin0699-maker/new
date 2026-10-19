"""YouTube Agent CLI & Channel Manager.

YouTube Data API v3 orqali videolarni avtomatik yuklash, rejalashtirish,
statistikalarni kuzatish hamda AI yordamida SEO metadata va Shorts ssenariylarini yaratish.

Foydalanish:
  python youtube_agent.py auth               # Google OAuth orqali YouTube hisobini ulash
  python youtube_agent.py channel            # Kanal statistikasi (obunachilar, ko'rishlar)
  python youtube_agent.py videos             # So'nggi videolarning statistikasi
  python youtube_agent.py upload <fayl>      # Video yuklash va rejalashtirish
  python youtube_agent.py ai-meta <mavzu>    # AI yordamida sarlavha, tavsif, teglar yaratish
  python youtube_agent.py ai-shorts <mavzu>  # AI yordamida Shorts ssenariysi yaratish
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to sys.path so we can import app modules directly
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import get_settings
from app.integrations.youtube.client import YouTubeClient
from app.integrations.youtube.errors import YouTubeApiError
from app.integrations.youtube.schemas import (
    YouTubeCategory,
    YouTubePrivacyStatus,
    YouTubeVideoUploadRequest,
)

TOKENS_FILE = ROOT_DIR / ".youtube_tokens.json"


def load_tokens() -> dict:
    if TOKENS_FILE.exists():
        try:
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_tokens(tokens: dict) -> None:
    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2, ensure_ascii=False)
    print(f"Tokenlar saqlandi: {TOKENS_FILE}")


def get_client() -> YouTubeClient:
    settings = get_settings()
    client_id = settings.youtube_client_id or os.getenv("YOUTUBE_CLIENT_ID", "")
    client_secret = (
        settings.youtube_client_secret.get_secret_value()
        if settings.youtube_client_secret
        else os.getenv("YOUTUBE_CLIENT_SECRET", "")
    )
    tokens = load_tokens()

    if not client_id:
        print("[OGOHLANTIRISH] YOUTUBE_CLIENT_ID topilmadi.")
        print(".env faylida YOUTUBE_CLIENT_ID va YOUTUBE_CLIENT_SECRET ni sozlang.")

    return YouTubeClient(
        client_id=client_id,
        client_secret=client_secret,
        access_token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token"),
        api_key=settings.youtube_api_key or os.getenv("YOUTUBE_API_KEY", ""),
    )


async def cmd_auth(args):
    client = get_client()
    settings = get_settings()
    redirect_uri = args.redirect_uri or settings.youtube_redirect_uri or "urn:ietf:wg:oauth:2.0:oob"

    print("=" * 60)
    print("YOUTUBE OAUTH 2.0 AVTORIZATSIYA")
    print("=" * 60)
    url = client.get_authorization_url(redirect_uri=redirect_uri)
    print("\n1. Quyidagi havolani brauzerda oching va Google hisobingizga ruxsat bering:")
    print(f"\n{url}\n")
    print("2. Google taqdim etgan avtorizatsiya kodi (code) ni bu yerga kiriting:")

    code = input("Kodni kiriting: ").strip()
    if not code:
        print("Kod kiritilmadi. Bekor qilindi.")
        await client.aclose()
        return

    try:
        tokens = await client.exchange_code(code, redirect_uri=redirect_uri)
        data = {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": tokens.expires_in,
            "updated_at": datetime.now().isoformat(),
        }
        save_tokens(data)
        print("\n Tabriklaymiz! YouTube kanalingiz muvaffaqiyatli ulandi.")
    except YouTubeApiError as exc:
        print(f"\n[XATOLIK] Token olishda muammo yuz berdi: {exc.message}")
    finally:
        await client.aclose()


async def cmd_channel(args):
    client = get_client()
    try:
        stats = await client.get_my_channel_stats()
        print("=" * 50)
        print(f"YouTube Kanal: {stats.title}")
        print("=" * 50)
        print(f"Kanal ID:         {stats.channel_id}")
        if stats.custom_url:
            print(f"Maxsus havola:    https://youtube.com/{stats.custom_url}")
        print(f"Obunachilar:      {stats.subscriber_count:,}")
        print(f"Videolar soni:    {stats.video_count:,}")
        print(f"Umumiy ko'rishlar:{stats.view_count:,}")
        print("-" * 50)
    except YouTubeApiError as exc:
        print(f"[XATOLIK] Kanal ma'lumotlarini olishda xato: {exc.message}")
        print("Iltimos, avval 'python youtube_agent.py auth' buyrug'i orqali hisobni ulang.")
    finally:
        await client.aclose()


async def cmd_videos(args):
    client = get_client()
    try:
        videos = await client.list_channel_videos(max_results=args.limit)
        if not videos:
            print("Kanalda videolar topilmadi yoki ruxsat yetarli emas.")
            return

        print(f"\nSo'nggi {len(videos)} ta video statistikasi:\n")
        print(f"{'№':<3} {'ID':<12} {'Ko\'rish':<10} {'Layk':<8} {'Izoh':<8} {'Sarlavha'}")
        print("-" * 80)
        for idx, v in enumerate(videos, start=1):
            print(
                f"{idx:<3} {v.video_id:<12} {v.view_count:<10,}"
                f" {v.like_count:<8,} {v.comment_count:<8,} {v.title[:35]}"
            )
    except YouTubeApiError as exc:
        print(f"[XATOLIK] Videolarni olishda xato: {exc.message}")
    finally:
        await client.aclose()


async def cmd_upload(args):
    client = get_client()
    file_path = Path(args.file)
    if not file_path.is_file():
        print(f"[XATOLIK] Fayl topilmadi: {file_path}")
        await client.aclose()
        return

    # Scheduling
    publish_dt = None
    if args.schedule:
        try:
            publish_dt = datetime.fromisoformat(args.schedule.replace(" ", "T"))
            print(f"Rejalashtirilgan vaqt: {publish_dt.isoformat()}")
        except ValueError:
            print("[XATOLIK] Reja vaqti noto'g'ri formatda. Namuna: '2026-10-25 18:00' yoki '2026-10-25T18:00:00'")
            await client.aclose()
            return

    tags_list = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    privacy = YouTubePrivacyStatus(args.privacy)
    if publish_dt:
        privacy = YouTubePrivacyStatus.PRIVATE

    req = YouTubeVideoUploadRequest(
        title=args.title or file_path.stem.replace("_", " ").title(),
        description=args.description or "",
        tags=tags_list,
        category_id=args.category,
        privacy_status=privacy,
        publish_at=publish_dt,
        made_for_kids=args.for_kids,
    )

    print("=" * 60)
    print(f"Video yuklanmoqda: {file_path.name}")
    print(f"Sarlavha: {req.title}")
    print(f"Maxfiylik: {req.privacy_status.value}")
    if publish_dt:
        print(f"Avtomatik nashr vaqti: {publish_dt}")
    print("=" * 60)

    try:
        resp = await client.upload_video(file_path, req)
        print("\n Video muvaffaqiyatli yuklandi!")
        print(f"Video ID:   {resp.video_id}")
        print(f"Havola:     {resp.url}")
        print(f"Holati:     {resp.privacy_status}")
    except YouTubeApiError as exc:
        print(f"\n[XATOLIK] Video yuklashda xato yuz berdi: {exc.message}")
    finally:
        await client.aclose()


async def cmd_ai_meta(args):
    from app.agents.youtube import YouTubeAgent
    from app.models import BrandProfile
    from app.providers.ai.factory import create_ai_provider

    print("AI YouTube Metadata generatsiya qilinmoqda...")
    ai = create_ai_provider()
    agent = YouTubeAgent(ai)

    brand = BrandProfile(
        name="YouTube Channel",
        niche="Content Creation",
        voice=["Samimiy", "Ekspert", "Qiziqarli"],
        topics=["Texnologiya", "Dasturlash"],
        languages=[args.lang],
        target_audience="Tomoshabinlar",
        preferred_ctas=["Kanalga obuna bo'ling!"],
    )

    meta, info = await agent.generate_metadata(
        brand,
        language=args.lang,
        topic=args.topic,
        video_summary=args.summary,
    )

    print("\n" + "=" * 60)
    print("YOUTUBE AI METADATA NATIJALARI")
    print("=" * 60)
    print("\n TOP SARLAVHALAR (Tavsiya etilgan):")
    for i, t in enumerate(meta.titles, 1):
        print(f"  {i}. {t}")

    print("\n TAVSIF (Description):")
    print("-" * 40)
    print(meta.description)
    print("-" * 40)

    print("\n TEGLAR (SEO Tags):")
    print(", ".join(meta.tags))

    print("\n HASHTAGLAR:")
    print(" ".join(meta.hashtags))

    print("\n THUMBNAIL (Muqova) G'OYASI:")
    print(meta.thumbnail_concept)

    print("\n MAHKAMLANGAN IZOH (Pinned Comment):")
    print(meta.pinned_comment)
    print("=" * 60)


async def cmd_ai_shorts(args):
    from app.agents.youtube import YouTubeAgent
    from app.models import BrandProfile
    from app.providers.ai.factory import create_ai_provider

    print(f"AI YouTube Shorts ({args.seconds}s) ssenariysi tayyorlanmoqda...")
    ai = create_ai_provider()
    agent = YouTubeAgent(ai)

    brand = BrandProfile(
        name="YouTube Shorts",
        niche="Short Content",
        voice=["Dinamik", "Qiziqarli", "Tezkor"],
        topics=["Shorts"],
        languages=[args.lang],
        target_audience="Shorts tomoshabinlari",
        preferred_ctas=["Layk bosing va obuna bo'ling!"],
    )

    shorts, info = await agent.generate_shorts_script(
        brand,
        language=args.lang,
        topic=args.topic,
        target_seconds=args.seconds,
    )

    print("\n" + "=" * 60)
    print(f"YOUTUBE SHORTS SSENARIYSI: {shorts.title}")
    print("=" * 60)
    print(f"\n HOOK (Dastlabki 3 soniya):\n  \"{shorts.hook}\"\n")
    print(" SSENARIY QADAMLARI:")
    for idx, seg in enumerate(shorts.script_segments, 1):
        print(f"  [{idx}] {seg}")

    print(f"\n CTA (Call to action):\n  \"{shorts.cta}\"")

    if shorts.visual_and_audio_cues:
        print("\n VIZUAL VA AUDIO TAVSIYALAR:")
        for cue in shorts.visual_and_audio_cues:
            print(f"  • {cue}")

    if shorts.tags:
        print(f"\n TEGLAR:\n  {', '.join(shorts.tags)}")
    print("=" * 60)


async def cmd_generate_video(args):
    from app.agents.youtube import YouTubeAgent
    from app.integrations.youtube.video_generator import generate_shorts_video
    from app.models import BrandProfile
    from app.providers.ai.factory import create_ai_provider

    print("=" * 60)
    print("AVTOMATIK YOUTUBE SHORTS GENERATSIYASI")
    print("=" * 60)
    print(f"Mavzu: {args.topic}")
    print("1. AI yordamida ssenariy va ovoz matnlari tuzilmoqda...")

    ai = create_ai_provider()
    agent = YouTubeAgent(ai)

    brand = BrandProfile(
        name="YouTube Shorts",
        niche="Short Content",
        voice=["Dinamik", "Qiziqarli", "Tezkor"],
        topics=["Shorts"],
        languages=[args.lang],
        target_audience="Shorts tomoshabinlari",
        preferred_ctas=["Layk bosing va obuna bo'ling!"],
    )

    shorts, _ = await agent.generate_shorts_script(
        brand,
        language=args.lang,
        topic=args.topic,
        target_seconds=args.seconds,
    )

    print(f" Ssenariy tayyor: \"{shorts.title}\"")
    print(f"   Hook: \"{shorts.hook}\"")

    out_file = args.output
    if not out_file:
        safe_topic = "".join(c if c.isalnum() else "_" for c in args.topic)[:25]
        out_file = f"shorts_{safe_topic}.mp4"

    print("\n2. Ovoz (Neural TTS), vizual slaydlar va FFmpeg montaj qilinmoqda...")
    video_path = await generate_shorts_video(
        topic=args.topic,
        hook=shorts.hook,
        segments=shorts.script_segments,
        cta=shorts.cta,
        language=args.lang,
        voice=args.voice,
        output_path=out_file,
    )

    print(f"\n Video muvaffaqiyatli yaratildi: {video_path}")

    # Agar foydalanuvchi to'g'ridan-to'g'ri YouTube'ga yuklashni so'ragan bo'lsa
    if args.upload:
        print("\n3. Video YouTube'ga yuklanmoqda...")
        client = get_client()

        publish_dt = None
        if args.schedule:
            try:
                publish_dt = datetime.fromisoformat(args.schedule.replace(" ", "T"))
            except ValueError:
                print("[XATOLIK] Rejalashtirilgan vaqt noto'g'ri formatda.")

        privacy = YouTubePrivacyStatus(args.privacy)
        if publish_dt:
            privacy = YouTubePrivacyStatus.PRIVATE

        upload_req = YouTubeVideoUploadRequest(
            title=shorts.title[:100],
            description=f"{shorts.hook}\n\n#shorts #{args.topic.replace(' ', '')}",
            tags=shorts.tags,
            category_id=args.category,
            privacy_status=privacy,
            publish_at=publish_dt,
        )

        try:
            resp = await client.upload_video(video_path, upload_req)
            print("\n Video YouTube'ga muvaffaqiyatli yuklandi!")
            print(f"   Video ID: {resp.video_id}")
            print(f"   Havola:   {resp.url}")
            print(f"   Holat:    {resp.privacy_status}")
        except YouTubeApiError as exc:
            print(f"\n[XATOLIK] YouTube'ga yuklashda xatolik: {exc.message}")
        finally:
            await client.aclose()


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Agent & Channel Manager CLI (Muxriddin AI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Buyruqlar")

    # auth
    p_auth = subparsers.add_parser("auth", help="Google OAuth orqali YouTube hisobini ulash")
    p_auth.add_argument("--redirect-uri", help="OAuth Redirect URI")

    # channel
    subparsers.add_parser("channel", help="Kanal statistikasi")

    # videos
    p_vids = subparsers.add_parser("videos", help="So'nggi videolar statistikasi")
    p_vids.add_argument("--limit", type=int, default=10, help="Videolar soni (default: 10)")

    # upload
    p_up = subparsers.add_parser("upload", help="Video yuklash va rejalashtirish")
    p_up.add_argument("file", help="Video fayl yo'li (masalan, video.mp4)")
    p_up.add_argument("--title", help="Video sarlavhasi")
    p_up.add_argument("--description", help="Video tavsifi")
    p_up.add_argument("--tags", help="Vergul bilan ajratilgan teglar")
    p_up.add_argument("--category", default=YouTubeCategory.PEOPLE_BLOGS, help="Kategoriya ID-si (default: 22)")
    p_up.add_argument(
        "--privacy",
        choices=["public", "private", "unlisted"],
        default="private",
        help="Maxfiylik darajasi (default: private)",
    )
    p_up.add_argument(
        "--schedule",
        help="Avtomatik nashr qilish sanasi va vaqti: '2026-10-25 18:00' (ISO 8601)",
    )
    p_up.add_argument("--for-kids", action="store_true", help="Bolalar uchun mo'ljallangan")

    # generate-video (Full automatic video creation)
    p_gen = subparsers.add_parser("generate-video", help="To'liq avtomatik YouTube Shorts video (.mp4) yaratish")
    p_gen.add_argument("topic", help="Video mavzusi (masalan: 'Sun\'iy intellekt kelajagi')")
    p_gen.add_argument("--output", help="Chiquvchi video fayl nomi (masalan: shorts.mp4)")
    p_gen.add_argument("--lang", default="uz", choices=["uz", "ru", "en"], help="Til (default: uz)")
    p_gen.add_argument("--voice", help="Maxsus TTS ovoz (masalan: uz-UZ-MadinaNeural)")
    p_gen.add_argument("--seconds", type=int, default=45, help="Taxminiy davomiylik (default: 45)")
    p_gen.add_argument("--upload", action="store_true", help="Tayyor bo'lgach to'g'ridan-to'g'ri YouTube'ga yuklash")
    p_gen.add_argument("--privacy", choices=["public", "private", "unlisted"], default="private")
    p_gen.add_argument("--schedule", help="Avtomatik nashr sanasi: '2026-10-25 18:00'")
    p_gen.add_argument("--category", default=YouTubeCategory.PEOPLE_BLOGS)

    # ai-meta
    p_meta = subparsers.add_parser("ai-meta", help="AI bilan SEO sarlavha, tavsif va teglar yaratish")
    p_meta.add_argument("topic", help="Video mavzusi")
    p_meta.add_argument("--summary", help="Video mazmuni haqida qisqacha ma'lumot")
    p_meta.add_argument("--lang", default="uz", choices=["uz", "ru", "en"], help="Til")

    # ai-shorts
    p_sh = subparsers.add_parser("ai-shorts", help="AI bilan YouTube Shorts ssenariysi yaratish")
    p_sh.add_argument("topic", help="Shorts mavzusi")
    p_sh.add_argument("--seconds", type=int, default=45, help="Davomiyligi (15-60 soniya)")
    p_sh.add_argument("--lang", default="uz", choices=["uz", "ru", "en"], help="Til")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    handlers = {
        "auth": cmd_auth,
        "channel": cmd_channel,
        "videos": cmd_videos,
        "upload": cmd_upload,
        "generate-video": cmd_generate_video,
        "ai-meta": cmd_ai_meta,
        "ai-shorts": cmd_ai_shorts,
    }

    asyncio.run(handlers[args.command](args))


if __name__ == "__main__":
    main()
