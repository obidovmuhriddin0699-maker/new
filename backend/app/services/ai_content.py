"""AI content creation pipeline.

    Brand profile -> strategy / ideas / plan -> caption or script generation
    -> schema validation -> quality evaluation -> save DRAFT -> human review

Boundaries enforced here:
* Only an authenticated human writer can request generation.
* Generated content is saved through ``ContentService`` by an ``AgentActor``
  whose tools never include approve/schedule/publish; content starts as DRAFT
  and can at most be submitted to READY_FOR_REVIEW (if the quality check
  passed and the human asked for it).
* Provider failures and invalid model output fail the job with a safe message
  and category; nothing is fabricated and no content is saved.
* The LLM call happens outside any DB transaction (no long-held locks).
"""

import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from datetime import date
from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.creator import ContentCreator
from app.agents.permissions import PIPELINE_AGENT_TOOLS
from app.agents.planner import ContentPlanner
from app.agents.quality import EvaluationInput, QualityEvaluator
from app.agents.schemas import (
    CarouselOutput,
    ContentPlan,
    IdeasOutput,
    PostOutput,
    QualityReport,
    ReelsScriptOutput,
    StoryOutput,
)
from app.agents.strategist import ContentStrategist
from app.agents.structured import GenerationMeta, run_sync
from app.agents.visual import build_visual_prompt
from app.core.actors import Actor, AgentActor, SystemActor
from app.core.config import get_settings
from app.core.errors import AppError, NotFoundError, TooManyRequestsError
from app.core.transaction import atomic
from app.models import AIJob, BrandProfile, Content, ContentPerformance
from app.models.enums import AIJobStatus, AuditAction, ContentLanguage, ContentType
from app.providers.ai.base import AIProvider, AIProviderError
from app.providers.ai.factory import create_ai_provider
from app.providers.media import DEFAULT_ASPECT_RATIO
from app.repositories import BrandProfileRepository, ContentRepository
from app.services.ai_job import AIJobService
from app.services.audit import AuditLogService
from app.services.content import ContentService
from app.services.guards import require_active_human, require_human_writer

logger = logging.getLogger(__name__)

ProviderFactory = Callable[[], AIProvider]
PIPELINE_ACTOR = SystemActor("ai_pipeline")


class JobType:
    STRATEGY = "strategy"
    IDEAS = "ideas"
    CONTENT_PLAN = "content_plan"
    POST = "post"
    CAROUSEL = "carousel"
    REELS = "reels"
    STORY = "story"
    HASHTAGS = "hashtags"

    ALL = (STRATEGY, IDEAS, CONTENT_PLAN, POST, CAROUSEL, REELS, STORY, HASHTAGS)
    CONTENT = {
        POST: ContentType.POST,
        CAROUSEL: ContentType.CAROUSEL,
        REELS: ContentType.REELS,
        STORY: ContentType.STORY,
    }


AGENT_FOR_JOB = {
    JobType.STRATEGY: ContentStrategist.name,
    JobType.IDEAS: ContentPlanner.name,
    JobType.CONTENT_PLAN: ContentPlanner.name,
    JobType.POST: ContentCreator.name,
    JobType.CAROUSEL: ContentCreator.name,
    JobType.REELS: ContentCreator.name,
    JobType.STORY: ContentCreator.name,
    JobType.HASHTAGS: ContentCreator.name,
}


def agent_actor(name: str) -> AgentActor:
    # No publish/approve permission exists; scheduling is excluded for pipeline agents.
    return AgentActor(name=name, tools=PIPELINE_AGENT_TOOLS)


@dataclass(slots=True)
class JobOutcome:
    job: AIJob
    result: dict[str, Any] | None = None
    quality: QualityReport | None = None
    content: Content | None = None


class AIContentService:
    def __init__(
        self,
        session: Session,
        *,
        provider_factory: ProviderFactory | None = None,
        audit: AuditLogService | None = None,
    ) -> None:
        self.session = session
        self.audit = audit or AuditLogService(session)
        # Resolved at call time so tests/workers can swap the module-level factory.
        self.provider_factory = provider_factory or (lambda: create_ai_provider())
        self.jobs = AIJobService(session, self.audit)
        self.contents = ContentService(session, self.audit)
        self.brands = BrandProfileRepository(session)

    # ------------------------------------------------------------------ requests
    def request(self, job_type: str, params: dict[str, Any], actor: Actor) -> AIJob:
        """Validate the human request and create a QUEUED job (no generation yet)."""
        if job_type not in JobType.ALL:
            raise AppError(f"Unknown AI job type: {job_type}", code="invalid_job_type")
        user = require_human_writer(self.session, actor)
        brand = self.resolve_brand(params.get("brand_profile_id"))
        language = params.get("language", "uz")
        if brand.languages and language not in brand.languages:
            raise AppError(
                f"Language '{language}' is not enabled for brand '{brand.name}'",
                code="language_not_supported",
            )
        limit = get_settings().ai_max_active_jobs_per_user
        if self.jobs.count_active_for_user(user.id) >= limit:
            raise TooManyRequestsError(
                f"You already have {limit} AI jobs in progress; wait for them to finish."
            )
        settings = get_settings()
        params = {**params, "brand_profile_id": brand.id}
        with atomic(self.session):
            job = self.jobs.create(
                PIPELINE_ACTOR,
                agent=AGENT_FOR_JOB[job_type],
                job_type=job_type,
                input=params,
                provider=settings.ai_provider,
                model=settings.ai_model,
                created_by_user_id=user.id,
            )
            self.audit.record(
                AuditAction.AI_JOB_REQUESTED,
                actor,
                details={
                    "ai_job_id": job.id,
                    "job_type": job_type,
                    "brand_profile_id": brand.id,
                    "language": language,
                    "mode": settings.ai_jobs_mode,
                },
            )
        return job

    def resolve_brand(self, brand_profile_id: int | None) -> BrandProfile:
        brand = self.brands.get(brand_profile_id) if brand_profile_id else self.brands.get_default()
        if brand is None:
            raise NotFoundError(
                "Brand profile not found"
                if brand_profile_id
                else "No default brand profile configured (run the seed or create one)"
            )
        return brand

    # ------------------------------------------------------------------ execution
    def execute(self, job_id: int) -> JobOutcome:
        """Run a QUEUED job. Safe to call twice: non-QUEUED jobs are returned unchanged."""
        job = self.jobs.get(job_id)
        if job.status != AIJobStatus.QUEUED:
            return self.outcome(job)
        self.jobs.start(job.id, PIPELINE_ACTOR)
        params = dict(job.input or {})
        try:
            brand = self.resolve_brand(params.get("brand_profile_id"))
            output, meta = self._generate(job.job_type, brand, params)
        except AIProviderError as exc:
            self.jobs.fail(job.id, PIPELINE_ACTOR, error=exc.message, category=exc.category)
            return self.outcome(job)
        except AppError as exc:
            self.jobs.fail(job.id, PIPELINE_ACTOR, error=exc.message, category=exc.code)
            return self.outcome(job)
        except Exception:  # noqa: BLE001 - never leak internals; details go to the log only
            logger.exception("ai_job_crashed", extra={"ai_job_id": job.id})
            self.jobs.fail(
                job.id,
                PIPELINE_ACTOR,
                error="Internal error during generation",
                category="internal",
            )
            return self.outcome(job)

        try:
            with atomic(self.session):
                result, quality, content = self._persist(job, brand, params, output, meta)
                self.jobs.succeed(
                    job.id,
                    PIPELINE_ACTOR,
                    output={
                        "result": result,
                        "quality": quality.model_dump(mode="json") if quality else None,
                        "generation": meta.as_dict(),
                    },
                    content_id=content.id if content else None,
                )
        except AppError as exc:
            self.jobs.fail(job.id, PIPELINE_ACTOR, error=exc.message, category=exc.code)
        except Exception:  # noqa: BLE001
            logger.exception("ai_job_persist_failed", extra={"ai_job_id": job.id})
            self.jobs.fail(
                job.id,
                PIPELINE_ACTOR,
                error="Could not save generated content",
                category="internal",
            )
        return self.outcome(self.jobs.get(job.id))

    def outcome(self, job: AIJob) -> JobOutcome:
        out = job.output or {}
        quality = QualityReport.model_validate(out["quality"]) if out.get("quality") else None
        content = self.session.get(Content, job.content_id) if job.content_id else None
        return JobOutcome(job=job, result=out.get("result"), quality=quality, content=content)

    def get_job(self, job_id: int, actor: Actor) -> JobOutcome:
        user = require_active_human(self.session, actor)
        job = self.jobs.get(job_id)
        if job.created_by_user_id != user.id and user.role.value not in ("OWNER", "ADMIN"):
            raise NotFoundError("AI job not found")  # don't reveal other users' jobs
        return self.outcome(job)

    # ------------------------------------------------------------------ generation
    def _call(self, fn: Callable[[AIProvider], Coroutine[Any, Any, Any]]) -> Any:
        provider = self.provider_factory()

        async def _go() -> Any:
            try:
                return await fn(provider)
            finally:
                await provider.aclose()

        return run_sync(_go())

    def _generate(
        self, job_type: str, brand: BrandProfile, p: dict[str, Any]
    ) -> tuple[Any, GenerationMeta]:
        lang = p.get("language", "uz")
        req = p.get("instructions")
        if job_type == JobType.STRATEGY:
            perf = self._performance_summary()
            return self._call(
                lambda pr: ContentStrategist(pr).recommend(
                    brand,
                    language=lang,
                    goals=p.get("goals") or None,
                    performance=perf,
                    user_request=req,
                )
            )
        if job_type == JobType.IDEAS:
            formats = [ContentType(f) for f in p.get("formats") or []] or None
            return self._call(
                lambda pr: ContentPlanner(pr).ideas(
                    brand,
                    language=lang,
                    count=p.get("count", 5),
                    formats=formats,
                    topic=p.get("topic"),
                    user_request=req,
                )
            )
        if job_type == JobType.CONTENT_PLAN:
            return self._call(
                lambda pr: ContentPlanner(pr).plan(
                    brand,
                    language=lang,
                    start_date=date.fromisoformat(p["start_date"]),
                    period=p.get("period", "week"),
                    posts_per_week=p.get("posts_per_week", 5),
                    user_request=req,
                    has_analytics=self._has_analytics(),
                )
            )
        creator_calls = {
            JobType.POST: lambda pr: ContentCreator(pr).post(
                brand, language=lang, topic=p["topic"], user_request=req
            ),
            JobType.CAROUSEL: lambda pr: ContentCreator(pr).carousel(
                brand, language=lang, topic=p["topic"], slides=p.get("slides", 5), user_request=req
            ),
            JobType.REELS: lambda pr: ContentCreator(pr).reels(
                brand,
                language=lang,
                topic=p["topic"],
                target_seconds=p.get("target_seconds", 30),
                user_request=req,
            ),
            JobType.STORY: lambda pr: ContentCreator(pr).story(
                brand, language=lang, topic=p["topic"], user_request=req
            ),
            JobType.HASHTAGS: lambda pr: ContentCreator(pr).hashtags(
                brand, language=lang, topic=p["topic"], count=p.get("count", 15)
            ),
        }
        return self._call(creator_calls[job_type])

    def _performance_summary(self) -> dict[str, Any] | None:
        """Real stored metrics only (top items by engagement). None if there are none."""
        rows = self.session.scalars(
            select(ContentPerformance)
            .where(ContentPerformance.engagement_rate.is_not(None))
            .order_by(ContentPerformance.engagement_rate.desc())
            .limit(5)
        ).all()
        if not rows:
            return None
        items = []
        for row in rows:
            content = self.session.get(Content, row.content_id)
            items.append(
                {
                    "format": content.content_type.value if content else None,
                    "topic": content.topic if content else None,
                    "engagement_rate": row.engagement_rate,
                    "metrics": row.metrics,
                }
            )
        return {"top_content": items}

    def _has_analytics(self) -> bool:
        return (self.session.scalar(select(func.count()).select_from(ContentPerformance)) or 0) > 0

    # ------------------------------------------------------------------ persistence
    def _persist(
        self,
        job: AIJob,
        brand: BrandProfile,
        p: dict[str, Any],
        output: Any,
        meta: GenerationMeta,
    ) -> tuple[dict[str, Any], QualityReport | None, Content | None]:
        lang = ContentLanguage(p.get("language", "uz"))
        ai_meta = {
            **meta.as_dict(),
            "ai_job_id": job.id,
            "requested_by_user_id": job.created_by_user_id,
        }

        if job.job_type == JobType.IDEAS and p.get("save_as_drafts"):
            ideas = cast(IdeasOutput, output)
            for idea in ideas.ideas:
                self._create_draft(
                    brand,
                    lang,
                    idea.format,
                    ai_meta,
                    topic=idea.topic,
                    hook=idea.hook,
                    visual_prompt=build_visual_prompt(brand, idea.format, idea.title),
                )
            return ideas.model_dump(mode="json"), None, None

        if job.job_type == JobType.CONTENT_PLAN:
            plan = cast(ContentPlan, output)
            if p.get("save_as_drafts"):
                for item in plan.items:
                    draft = self._create_draft(brand, lang, item.format, ai_meta, topic=item.title)
                    item.status = "DRAFT_CREATED"
                    item.content_id = draft.id
            return plan.model_dump(mode="json"), None, None

        if job.job_type not in JobType.CONTENT:
            return output.model_dump(mode="json"), None, None

        content_type = JobType.CONTENT[job.job_type]
        fields = self._content_fields(content_type, output, brand, p["topic"])
        evaluation = EvaluationInput(
            content_type=content_type,
            language=lang.value,
            **{k: fields.get(k) for k in ("hook", "caption", "cta", "script")},
            hashtags=fields.get("hashtags", []),
            structure=fields.get("structure", {}),
        )
        quality = QualityEvaluator(brand).evaluate(evaluation, recent_texts=self._recent_texts())
        ai_meta["quality"] = {
            "passed": quality.passed,
            "score": quality.score,
            "errors": [f.code for f in quality.findings if f.severity.value == "ERROR"],
        }
        content = self._create_draft(brand, lang, content_type, ai_meta, **fields)
        if p.get("submit_for_review") and quality.passed:
            self.contents.submit_for_review(content.id, agent_actor(ContentCreator.name))
        return output.model_dump(mode="json"), quality, content

    def _create_draft(
        self,
        brand: BrandProfile,
        lang: ContentLanguage,
        content_type: ContentType,
        ai_meta: dict[str, Any],
        **fields: Any,
    ) -> Content:
        fields.setdefault("aspect_ratio", DEFAULT_ASPECT_RATIO[content_type])
        return self.contents.create(
            agent_actor(ContentCreator.name),
            content_type=content_type,
            language=lang,
            brand_profile_id=brand.id,
            ai_metadata=ai_meta,
            change_note="AI draft",
            **fields,
        )

    @staticmethod
    def _content_fields(
        content_type: ContentType, output: Any, brand: BrandProfile, topic: str
    ) -> dict[str, Any]:
        visual = build_visual_prompt(brand, content_type, topic)
        if isinstance(output, PostOutput):
            return {
                "topic": topic,
                "hook": output.hook,
                "caption": output.caption,
                "cta": output.cta,
                "hashtags": output.hashtags,
                "visual_prompt": output.visual_prompt or visual,
                "structure": {"kind": "post", "alt_text": output.alt_text},
            }
        if isinstance(output, CarouselOutput):
            slides = [{"index": i, **s.model_dump()} for i, s in enumerate(output.slides, 1)]
            return {
                "topic": topic,
                "hook": output.title,
                "caption": output.caption,
                "cta": output.cta,
                "hashtags": output.hashtags,
                "visual_prompt": visual,
                "structure": {"kind": "carousel", "title": output.title, "slides": slides},
            }
        if isinstance(output, ReelsScriptOutput):
            scenes = [{"order": i, **s.model_dump()} for i, s in enumerate(output.scenes, 1)]
            script = "\n".join(
                f"{s['order']}. [{s['duration_seconds']:g}s] {s['visual']}"
                + (f" | TEXT: {s['on_screen_text']}" if s.get("on_screen_text") else "")
                + (f" | VO: {s['narration']}" if s.get("narration") else "")
                for s in scenes
            )
            return {
                "topic": topic,
                "hook": output.hook,
                "caption": output.caption,
                "cta": output.cta,
                "hashtags": output.hashtags,
                "script": script,
                "visual_prompt": visual,
                "structure": {
                    "kind": "reels",
                    "scenes": scenes,
                    "approx_duration_seconds": output.approx_duration_seconds,
                },
            }
        if isinstance(output, StoryOutput):
            frames = [{"order": i, **f.model_dump()} for i, f in enumerate(output.frames, 1)]
            script = "\n".join(
                f"{f['order']}. {f['visual']}" + (f" | {f['text']}" if f.get("text") else "")
                for f in frames
            )
            return {
                "topic": topic,
                "hook": output.title,
                "cta": output.cta,
                "script": script,
                "visual_prompt": visual,
                "structure": {"kind": "story", "title": output.title, "frames": frames},
            }
        raise AppError("Unsupported generation output", code="internal")

    def _recent_texts(self, limit: int = 20) -> list[str]:
        rows, _ = ContentRepository(self.session).search(limit=limit)
        return [c.caption for c in rows if c.caption]

    # ------------------------------------------------------------------ evaluation
    def evaluate(
        self,
        actor: Actor,
        item: EvaluationInput,
        *,
        brand_profile_id: int | None = None,
        content_id: int | None = None,
    ) -> QualityReport:
        require_active_human(self.session, actor)
        brand = None
        try:
            brand = self.resolve_brand(brand_profile_id)
        except NotFoundError:
            if brand_profile_id:
                raise
        recent = [t for t in self._recent_texts() if t != item.caption]
        report = QualityEvaluator(brand).evaluate(item, recent_texts=recent)
        if content_id is not None:
            with atomic(self.session):
                self.audit.record(
                    AuditAction.AI_CONTENT_EVALUATED,
                    actor,
                    content_id=content_id,
                    content_version=self.session.get(Content, content_id).version,
                    details={
                        "passed": report.passed,
                        "score": report.score,
                        "finding_codes": [f.code for f in report.findings],
                    },
                )
        return report
