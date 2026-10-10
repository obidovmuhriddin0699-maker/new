"""Media generation service (separate from caption generation).

With no real provider configured the result is explicitly ``not_configured``
and no ContentAsset is created. Placeholder (mock) results also create no
asset: an asset row is only written for real media from a real provider.
"""

from sqlalchemy.orm import Session

from app.agents.structured import run_sync
from app.agents.visual import build_visual_prompt
from app.core.actors import Actor
from app.core.errors import NotFoundError
from app.core.transaction import atomic
from app.models.enums import AuditAction
from app.providers.image.base import ImageGenerationRequest, ImageProvider, MediaGenerationResult
from app.providers.media import DEFAULT_ASPECT_RATIO, create_image_provider
from app.repositories import BrandProfileRepository, ContentRepository
from app.services.audit import AuditLogService
from app.services.guards import require_human_writer


class MediaGenerationService:
    def __init__(
        self,
        session: Session,
        image_provider: ImageProvider | None = None,
        audit: AuditLogService | None = None,
    ) -> None:
        self.session = session
        self.audit = audit or AuditLogService(session)
        self.image_provider = image_provider or create_image_provider()

    def generate_image_for_content(
        self, content_id: int, actor: Actor
    ) -> tuple[MediaGenerationResult, str, str]:
        require_human_writer(self.session, actor)
        content = ContentRepository(self.session).get(content_id)
        if content is None:
            raise NotFoundError("Content not found")
        brand = (
            BrandProfileRepository(self.session).get(content.brand_profile_id)
            if content.brand_profile_id
            else BrandProfileRepository(self.session).get_default()
        )
        ratio = content.aspect_ratio or DEFAULT_ASPECT_RATIO[content.content_type]
        prompt = content.visual_prompt or (
            build_visual_prompt(brand, content.content_type, content.topic or "interior")
            if brand
            else content.topic or "interior"
        )
        result = run_sync(
            self.image_provider.generate_image(
                ImageGenerationRequest(prompt=prompt, aspect_ratio=ratio)
            )
        )
        with atomic(self.session):
            self.audit.record(
                AuditAction.AI_MEDIA_REQUESTED,
                actor,
                content_id=content.id,
                content_version=content.version,
                details={
                    "provider": result.provider,
                    "status": result.status.value,
                    "aspect_ratio": ratio,
                },
            )
        return result, prompt, ratio
