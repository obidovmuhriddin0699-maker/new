from app.agents.base import BaseAgent
from app.agents.schemas import (
    CarouselOutput,
    HashtagOutput,
    PostOutput,
    ReelsScriptOutput,
    StoryOutput,
)
from app.agents.structured import GenerationMeta
from app.models import BrandProfile


class ContentCreator(BaseAgent):
    name = "content_creator"

    async def post(
        self, brand: BrandProfile, *, language: str, topic: str, user_request: str | None = None
    ) -> tuple[PostOutput, GenerationMeta]:
        return await self._run(
            task="post",
            brand=brand,
            language=language,
            schema=PostOutput,
            instructions=(
                "Write a single-image Instagram post: hook, caption (short paragraphs), one "
                "CTA, relevant hashtags, image alt text and an image-generation visual prompt "
                "in English."
            ),
            topic=topic,
            user_request=user_request,
        )

    async def carousel(
        self,
        brand: BrandProfile,
        *,
        language: str,
        topic: str,
        slides: int,
        user_request: str | None = None,
    ) -> tuple[CarouselOutput, GenerationMeta]:
        return await self._run(
            task="carousel",
            brand=brand,
            language=language,
            schema=CarouselOutput,
            instructions=(
                f"Write an Instagram carousel with exactly {slides} slides in order. Each slide "
                "has a concise heading (max ~8 words) and short body copy. Add a caption, one "
                "CTA and hashtags."
            ),
            topic=topic,
            user_request=user_request,
        )

    async def reels(
        self,
        brand: BrandProfile,
        *,
        language: str,
        topic: str,
        target_seconds: int,
        user_request: str | None = None,
    ) -> tuple[ReelsScriptOutput, GenerationMeta]:
        return await self._run(
            task="reels",
            brand=brand,
            language=language,
            schema=ReelsScriptOutput,
            instructions=(
                f"Write a Reels script of about {target_seconds} seconds: a hook for the first "
                "seconds, an ordered scene list (duration, visual, on-screen text, narration), "
                "a CTA, a caption and hashtags."
            ),
            topic=topic,
            user_request=user_request,
        )

    async def story(
        self, brand: BrandProfile, *, language: str, topic: str, user_request: str | None = None
    ) -> tuple[StoryOutput, GenerationMeta]:
        return await self._run(
            task="story",
            brand=brand,
            language=language,
            schema=StoryOutput,
            instructions=(
                "Write an Instagram Story concept: 1-5 frames with visual description, short "
                "text and an optional interactive element idea (poll/question/quiz/slider)."
            ),
            topic=topic,
            user_request=user_request,
        )

    async def hashtags(
        self, brand: BrandProfile, *, language: str, topic: str, count: int
    ) -> tuple[HashtagOutput, GenerationMeta]:
        result, meta = await self._run(
            task="hashtags",
            brand=brand,
            language=language,
            schema=HashtagOutput,
            instructions=f"Suggest {count} relevant, non-spammy hashtags.",
            topic=topic,
        )
        result.hashtags = result.hashtags[:count]
        return result, meta
