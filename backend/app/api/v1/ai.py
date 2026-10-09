"""AI pipeline endpoints. All require an authenticated human; none can approve,
schedule or publish. Generation is synchronous by default (AI_JOBS_MODE=sync)
or queued to Celery (AI_JOBS_MODE=celery, HTTP 202 + poll /ai/jobs/{id})."""

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response, status

from app.agents.permissions import PIPELINE_AGENT_TOOLS
from app.agents.quality import EvaluationInput
from app.agents.schemas import QualityReport
from app.api.deps import DbSession, HumanActorDep
from app.core.config import get_settings
from app.core.errors import AppError, NotFoundError
from app.models.enums import AIJobStatus
from app.providers.ai.base import AIProvider
from app.providers.ai.factory import create_ai_provider
from app.providers.media import create_image_provider, create_video_provider
from app.repositories import ContentRepository
from app.schemas.ai import (
    AIJobRead,
    AIStatusResponse,
    CaptionRequest,
    CarouselRequest,
    ContentPlanRequest,
    EvaluateRequest,
    GenerationResponse,
    HashtagRequest,
    IdeasRequest,
    ImageRequest,
    MediaProviderStatus,
    MediaResult,
    PipelineStatusResponse,
    ReelsRequest,
    StoryRequest,
    StrategyRequest,
)
from app.schemas.errors import error_responses
from app.schemas.panel import RegenerateRequest
from app.services.ai_content import AGENT_FOR_JOB, AIContentService, JobOutcome, JobType
from app.services.media import MediaGenerationService

router = APIRouter(prefix="/ai", tags=["ai"])


def get_provider_factory() -> Callable[[], AIProvider]:
    """Dependency so tests can inject a deterministic provider."""
    return create_ai_provider


ProviderFactoryDep = Annotated[Callable[[], AIProvider], Depends(get_provider_factory)]

# Provider/model failures -> HTTP status for synchronous requests.
_FAILURE_STATUS = {
    "provider_unavailable": 503,
    "model_not_found": 503,
    "timeout": 504,
    "invalid_response": 502,
    "invalid_output": 502,
}
GEN_ERRORS = error_responses(401, 403, 404, 409, 422) | {
    429: {"description": "Too many AI jobs in progress for this user"},
    502: {"description": "The AI model returned invalid output (job FAILED, nothing saved)"},
    503: {"description": "AI provider unavailable or model not installed"},
    504: {"description": "AI provider timed out"},
}


class GenerationFailedError(AppError):
    def __init__(self, outcome: JobOutcome) -> None:
        job = outcome.job
        super().__init__(
            job.error or "AI generation failed",
            code=f"ai_{job.error_category or 'failed'}",
            details={"job_id": job.id, "category": job.error_category},
        )
        self.status_code = _FAILURE_STATUS.get(job.error_category or "", 500)


def _response(outcome: JobOutcome) -> GenerationResponse:
    return GenerationResponse(
        job=AIJobRead.model_validate(outcome.job),
        result=outcome.result,
        quality=outcome.quality,
        content_id=outcome.content.id if outcome.content else None,
        content_status=outcome.content.status.value if outcome.content else None,
    )


def _run(
    job_type: str,
    body: Any,
    db: DbSession,
    actor: HumanActorDep,
    factory: Callable[[], AIProvider],
    response: Response,
) -> GenerationResponse:
    service = AIContentService(db, provider_factory=factory)
    job = service.request(job_type, body.model_dump(mode="json"), actor)
    if get_settings().ai_jobs_mode == "celery":
        from app.workers.tasks.ai import run_ai_job

        run_ai_job.delay(job.id)
        response.status_code = status.HTTP_202_ACCEPTED
        db.refresh(job)
        return _response(service.outcome(job))
    outcome = service.execute(job.id)
    if outcome.job.status == AIJobStatus.FAILED:
        raise GenerationFailedError(outcome)
    return _response(outcome)


def _route(path: str, job_type: str, model: type, summary: str, description: str) -> None:
    def endpoint(
        body: model,
        db: DbSession,
        actor: HumanActorDep,  # type: ignore[valid-type]
        factory: ProviderFactoryDep,
        response: Response,
    ) -> GenerationResponse:
        return _run(job_type, body, db, actor, factory, response)

    endpoint.__name__ = f"ai_{job_type}"
    router.add_api_route(
        path,
        endpoint,
        methods=["POST"],
        response_model=GenerationResponse,
        summary=summary,
        description=description,
        responses=GEN_ERRORS,
    )


_route(
    "/strategy",
    JobType.STRATEGY,
    StrategyRequest,
    "Content strategy recommendations",
    "Uses the brand profile and stored performance data (if any). Nothing is saved as content.",
)
_route(
    "/ideas",
    JobType.IDEAS,
    IdeasRequest,
    "Generate content ideas",
    "Optionally saves each idea as a DRAFT (`save_as_drafts`).",
)
_route(
    "/content-plan",
    JobType.CONTENT_PLAN,
    ContentPlanRequest,
    "Weekly or monthly draft content calendar",
    "Dates are computed server-side from `start_date`; no time-of-day or 'optimal time' "
    "claims unless analytics exist. Optionally saves DRAFTs.",
)
_route(
    "/generate-caption",
    JobType.POST,
    CaptionRequest,
    "Generate a single-image post",
    "Saves a DRAFT (or READY_FOR_REVIEW if requested and the quality check passed).",
)
_route(
    "/generate-carousel",
    JobType.CAROUSEL,
    CarouselRequest,
    "Generate carousel copy",
    "Ordered slides with heading + body, caption, CTA, hashtags. Saved as DRAFT.",
)
_route(
    "/generate-reels-script",
    JobType.REELS,
    ReelsRequest,
    "Generate a Reels script",
    "Hook, scenes (duration, visual, on-screen text, narration), CTA, caption. Saved as DRAFT.",
)
_route(
    "/generate-story",
    JobType.STORY,
    StoryRequest,
    "Generate a Story concept",
    "Frames with visuals, text and interactive element ideas. Saved as DRAFT.",
)
_route(
    "/regenerate",
    JobType.REGENERATE,
    RegenerateRequest,
    "Regenerate an existing content item",
    "Human-requested rewrite. READY_FOR_REVIEW content first gets an edit request recorded "
    "for the reviewer. The agent writes a new version that returns to READY_FOR_REVIEW; "
    "previous approvals never carry over.",
)
_route(
    "/hashtags",
    JobType.HASHTAGS,
    HashtagRequest,
    "Suggest hashtags",
    "Returns validated hashtag suggestions; nothing is saved as content.",
)


@router.post(
    "/evaluate-content",
    response_model=QualityReport,
    summary="Rule-based quality evaluation",
    description="Deterministic checks (completeness, structure, CTA, limits, repetition, "
    "unsupported claims, brand rules, language). Does not change content status.",
    responses=error_responses(401, 403, 404, 422),
)
def evaluate_content(body: EvaluateRequest, db: DbSession, actor: HumanActorDep) -> QualityReport:
    service = AIContentService(db)
    if body.content_id is not None:
        content = ContentRepository(db).get(body.content_id)
        if content is None:
            raise NotFoundError("Content not found")
        item = EvaluationInput.from_content(content)
        brand_id = body.brand_profile_id or content.brand_profile_id
    else:
        item = EvaluationInput(
            content_type=body.content_type,
            language=body.language,
            hook=body.hook,
            caption=body.caption,
            cta=body.cta,
            hashtags=body.hashtags,
            script=body.script,
            structure=body.structure,
        )
        brand_id = body.brand_profile_id
    return service.evaluate(actor, item, brand_profile_id=brand_id, content_id=body.content_id)


@router.post(
    "/generate-image",
    response_model=MediaResult,
    summary="Request an image for a content item",
    description="Returns `not_configured` when no image provider is set up (PHASE 3 default). "
    "No asset is created unless a real provider returns real media.",
    responses=error_responses(401, 403, 404, 422),
)
def generate_image(body: ImageRequest, db: DbSession, actor: HumanActorDep) -> MediaResult:
    result, prompt, ratio = MediaGenerationService(db).generate_image_for_content(
        body.content_id, actor
    )
    return MediaResult(
        status=result.status.value,
        provider=result.provider,
        model=result.model,
        message=result.message,
        error_code=result.error_code,
        visual_prompt=prompt,
        aspect_ratio=ratio,
        assets_created=0,
    )


@router.get(
    "/jobs/{job_id}",
    response_model=GenerationResponse,
    summary="AI job status and result",
    responses=error_responses(401, 404),
)
def get_job(job_id: int, db: DbSession, actor: HumanActorDep) -> GenerationResponse:
    return _response(AIContentService(db).get_job(job_id, actor))


@router.get(
    "/jobs",
    response_model=list[AIJobRead],
    summary="My recent AI jobs",
    responses=error_responses(401),
)
def list_jobs(db: DbSession, actor: HumanActorDep) -> list[AIJobRead]:
    jobs = AIContentService(db).jobs.list_recent(user_id=actor.user_id, limit=20)
    return [AIJobRead.model_validate(j) for j in jobs]


@router.get(
    "/status",
    response_model=PipelineStatusResponse,
    summary="AI pipeline status",
    description="Text provider health, job mode and media provider configuration. "
    "Never includes credentials or internal URLs.",
    responses=error_responses(401),
)
async def ai_status(_: HumanActorDep, factory: ProviderFactoryDep) -> PipelineStatusResponse:
    provider = factory()
    try:
        health = await provider.health()
    finally:
        await provider.aclose()
    media = []
    for kind, p in (("image", create_image_provider()), ("video", create_video_provider())):
        state = "mock" if p.name == "mock" else ("configured" if p.configured else "not_configured")
        media.append(
            MediaProviderStatus(kind=kind, provider=p.name, configured=p.configured, status=state)
        )
    return PipelineStatusResponse(
        text=AIStatusResponse(
            provider=health.provider,
            model=health.model,
            available=health.available,
            model_installed=health.model_installed,
            error_code=health.error_code,
            message=health.message,
        ),
        jobs_mode=get_settings().ai_jobs_mode,
        media=media,
        agents=sorted(set(AGENT_FOR_JOB.values()) | {"quality_evaluator"}),
        agent_permissions=sorted(t.value for t in PIPELINE_AGENT_TOOLS),
    )
