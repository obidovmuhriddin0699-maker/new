"""YouTube AI Agent for generating optimized video metadata, scripts, and content plans."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.agents.base import BaseAgent
from app.agents.structured import GenerationMeta
from app.models import BrandProfile


class YouTubeMetadataOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    titles: list[Annotated[str, Field(max_length=100)]] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Yuqori CTR beruvchi 3-5 ta muqobil sarlavha",
    )
    description: Annotated[str, Field(max_length=4500)] = Field(
        ...,
        description="YouTube tavsifi: kirish, mazmun, timestamps, CTA va havolalar",
    )
    tags: list[Annotated[str, Field(max_length=50)]] = Field(
        default_factory=list,
        max_length=30,
        description="SEO qidiruv teglari (kalit so'zlar)",
    )
    hashtags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Tavsif uchun asosiy hashtaglar (#shorts, #mavzu)",
    )
    thumbnail_concept: Annotated[str, Field(max_length=1000)] = Field(
        ...,
        description="Thumbnail vizual g'oyasi: matn, yuz ifodasi, ranglar",
    )
    pinned_comment: Annotated[str, Field(max_length=500)] = Field(
        ...,
        description="Birinchi qadaladigan izoh (auditoriyani jalb qilish uchun)",
    )


class YouTubeShortsScriptOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    title: Annotated[str, Field(max_length=100)] = Field(..., description="Shorts video sarlavhasi")
    hook: Annotated[str, Field(max_length=200)] = Field(
        ..., description="Dastlabki 3 soniyalik qiziqtiruvchi hook"
    )
    script_segments: list[str] = Field(
        ...,
        min_length=2,
        max_length=8,
        description="Ssenariy bo'limlari (ketma-ketlikda, dinamik va qisqa)",
    )
    cta: Annotated[str, Field(max_length=150)] = Field(
        ..., description="Yakuniy Call to Action"
    )
    visual_and_audio_cues: list[str] = Field(
        default_factory=list,
        description="B-roll, ekrandagi matnlar va ovoz ko'rsatmalari",
    )
    tags: list[str] = Field(default_factory=list, description="Shorts uchun teglar")


class YouTubeAgent(BaseAgent):
    """AI Agent specialized in YouTube content creation and optimization."""

    name = "youtube_agent"

    async def generate_metadata(
        self,
        brand: BrandProfile,
        *,
        language: str,
        topic: str,
        video_summary: str | None = None,
        target_audience: str | None = None,
    ) -> tuple[YouTubeMetadataOutput, GenerationMeta]:
        """Generate high-performing YouTube video metadata (titles, description, tags)."""
        instructions = (
            "YouTube videosi uchun yuqori natija beruvchi (yuqori CTR va SEO reyting) "
            "metadata tayyorlang. Sarlavhalar qisqa, intriga uyg'otuvchi va qidiruvbop bo'lsin. "
            "Tavsif dastlabki 2 qatorda asosiy qiziqishni bering, keyin mazmun, "
            "vaqt belgilari uchun joy qoldiring va harakatga chaqiruv (CTA) qo'shing. "
            "Teglar mavzuga oid aniq kalit so'zlardan iborat bo'lsin. "
            "Thumbnail kontseptsiyasida katta matn va diqqat tortuvchi elementlarni ko'rsating."
        )

        return await self._run(
            task="youtube_metadata",
            brand=brand,
            language=language,
            schema=YouTubeMetadataOutput,
            instructions=instructions,
            topic=topic,
            video_summary=video_summary,
            target_audience=target_audience,
        )

    async def generate_shorts_script(
        self,
        brand: BrandProfile,
        *,
        language: str,
        topic: str,
        target_seconds: int = 45,
    ) -> tuple[YouTubeShortsScriptOutput, GenerationMeta]:
        """Generate dynamic YouTube Shorts script (30-60s) with hook and visual cues."""
        instructions = (
            f"YouTube Shorts uchun {target_seconds} soniyalik tezkor ssenariy yozing. "
            "Eng muhim qism: birinchi 3 soniyadagi HOOK tomoshabinni darhol ushlasin. "
            "Har bir segment qisqa, aniq va ortiqcha so'zlarsiz bo'lsin. "
            "Vizual va audio tavsiyalarda qanday B-roll yoki matn chiqishini ko'rsating."
        )

        return await self._run(
            task="youtube_shorts_script",
            brand=brand,
            language=language,
            schema=YouTubeShortsScriptOutput,
            instructions=instructions,
            topic=topic,
            target_seconds=target_seconds,
        )
