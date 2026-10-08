import json

import pytest
from sqlalchemy import select

from app.agents.permissions import PIPELINE_AGENT_TOOLS, AgentTool
from app.core.actors import AgentActor, SystemActor
from app.core.errors import (
    AppError,
    ApprovalForbiddenError,
    InvalidStateTransitionError,
    NotFoundError,
    PermissionDeniedError,
    TooManyRequestsError,
)
from app.models import AIJob, AuditLog, Content, ContentVersion
from app.models.enums import ActorType, AIJobStatus, ContentStatus
from app.providers.ai.base import AIProviderTimeoutError, AIProviderUnavailableError
from app.services import ApprovalService, ContentService
from app.services.ai_content import AIContentService, JobType
from tests.conftest import mock_factory

BAD_CAPTION = json.dumps(
    {
        "hook": "h",
        "caption": "Natija 100% kafolatlanadi.",
        "cta": "Yozing",
        "hashtags": ["#a"],
    }
)


def run(db, human, job_type, params, factory=None):
    service = AIContentService(db, provider_factory=factory or mock_factory())
    job = service.request(job_type, params, human)
    return service.execute(job.id)


def test_caption_generation_saves_ai_draft(db, human, brand):
    outcome = run(db, human, JobType.POST, {"topic": "Minimalist xona", "language": "uz"})
    job, content = outcome.job, outcome.content
    assert job.status == AIJobStatus.SUCCEEDED
    assert job.started_at and job.finished_at and job.duration_ms is not None
    assert job.content_id == content.id and job.created_by_user_id == human.user_id
    assert content.status == ContentStatus.DRAFT
    assert content.created_by == ActorType.AGENT
    assert content.brand_profile_id == brand.id and content.cta
    v1 = db.scalars(select(ContentVersion).where(ContentVersion.content_id == content.id)).one()
    assert v1.source == ActorType.AGENT
    assert v1.ai_metadata["provider"] == "mock" and v1.ai_metadata["ai_job_id"] == job.id
    assert v1.ai_metadata["requested_by_user_id"] == human.user_id
    assert outcome.quality.passed
    assert not ContentService(db).is_publish_authorized(content)


def test_carousel_reels_story_structures_are_saved(db, human, brand):
    carousel = run(db, human, JobType.CAROUSEL, {"topic": "Yotoqxona", "slides": 3}).content
    assert carousel.structure["kind"] == "carousel"
    assert [s["index"] for s in carousel.structure["slides"]] == [1, 2, 3]
    reels = run(db, human, JobType.REELS, {"topic": "Kichik xona"}).content
    assert reels.structure["approx_duration_seconds"] == 15
    assert reels.script.startswith("1. [3s]") and reels.aspect_ratio == "9:16"
    story = run(db, human, JobType.STORY, {"topic": "Uslub"}).content
    assert story.structure["frames"][1]["interactive_element"] == "poll"


def test_structure_is_part_of_the_approved_version(db, human, brand):
    content = run(
        db, human, JobType.CAROUSEL, {"topic": "Yotoqxona", "submit_for_review": True}
    ).content
    ApprovalService(db).approve(content.id, human, expected_version=1)
    slides = [dict(s) for s in content.structure["slides"]]
    slides[0]["heading"] = "Changed"
    ContentService(db).update(
        content.id,
        human,
        expected_version=1,
        changes={"structure": {**content.structure, "slides": slides}},
    )
    assert content.version == 2 and content.status == ContentStatus.READY_FOR_REVIEW
    assert not ContentService(db).is_publish_authorized(content)


def test_submit_for_review_only_when_quality_passes(db, human, brand):
    ok = run(db, human, JobType.POST, {"topic": "Minimalizm", "submit_for_review": True})
    assert ok.content.status == ContentStatus.READY_FOR_REVIEW
    bad = run(
        db,
        human,
        JobType.POST,
        {"topic": "Minimalizm", "submit_for_review": True},
        factory=mock_factory(BAD_CAPTION),
    )
    assert not bad.quality.passed
    assert bad.content.status == ContentStatus.DRAFT  # stays draft, still saved for the human
    assert "guarantee_claim" in {f.code for f in bad.quality.findings}


def test_generated_content_is_never_approved_or_publishable(db, human, brand):
    for jt, params in [
        (JobType.POST, {"topic": "a b c", "submit_for_review": True}),
        (JobType.CAROUSEL, {"topic": "a b c", "submit_for_review": True}),
        (JobType.REELS, {"topic": "a b c", "submit_for_review": True}),
    ]:
        content = run(db, human, jt, params).content
        assert content.status in (ContentStatus.DRAFT, ContentStatus.READY_FOR_REVIEW)
    assert db.scalars(select(Content).where(Content.status == ContentStatus.APPROVED)).all() == []
    from app.models import Approval

    assert db.scalars(select(Approval)).all() == []


def test_pipeline_agent_cannot_approve_schedule_or_publish(db, human, brand):
    content = run(db, human, JobType.POST, {"topic": "abc", "submit_for_review": True}).content
    agent = AgentActor(name="content_creator", tools=PIPELINE_AGENT_TOOLS)
    with pytest.raises(ApprovalForbiddenError):
        ApprovalService(db).approve(content.id, agent, expected_version=1)
    with pytest.raises(PermissionDeniedError):
        ContentService(db).start_publishing(content.id, agent)
    from datetime import timedelta

    from app.models.base import utcnow
    from app.services import ScheduleService

    with pytest.raises(ApprovalForbiddenError):
        ScheduleService(db).schedule(content.id, agent, scheduled_at=utcnow() + timedelta(1))
    assert AgentTool.CREATE_SCHEDULE not in PIPELINE_AGENT_TOOLS
    db.refresh(content)
    assert content.status == ContentStatus.READY_FOR_REVIEW


@pytest.mark.parametrize(
    ("error", "category"),
    [
        (AIProviderUnavailableError("Ollama is not reachable"), "provider_unavailable"),
        (AIProviderTimeoutError("Ollama did not respond in time."), "timeout"),
    ],
)
def test_provider_failure_fails_job_and_saves_nothing(db, human, brand, error, category):
    outcome = run(db, human, JobType.POST, {"topic": "abc"}, factory=mock_factory(error))
    assert outcome.job.status == AIJobStatus.FAILED
    assert outcome.job.error_category == category and outcome.job.error == error.message
    assert outcome.content is None and outcome.job.output is None
    assert db.scalars(select(Content)).all() == []


def test_invalid_output_fails_job_without_fabrication(db, human, brand):
    outcome = run(
        db,
        human,
        JobType.CAROUSEL,
        {"topic": "abc"},
        factory=mock_factory("garbage", '{"title": "x"}'),
    )
    assert outcome.job.status == AIJobStatus.FAILED
    assert outcome.job.error_category == "invalid_output"
    assert db.scalars(select(Content)).all() == []


def test_unexpected_crash_is_safe(db, human, brand):
    def boom():
        raise RuntimeError("secret internal detail")

    outcome = run(db, human, JobType.POST, {"topic": "abc"}, factory=boom)
    assert outcome.job.status == AIJobStatus.FAILED
    assert outcome.job.error == "Internal error during generation"
    assert "secret" not in (outcome.job.error or "")


def test_execute_is_idempotent(db, human, brand):
    service = AIContentService(db, provider_factory=mock_factory())
    job = service.request(JobType.POST, {"topic": "abc"}, human)
    first = service.execute(job.id)
    second = service.execute(job.id)
    assert first.content.id == second.content.id
    assert len(db.scalars(select(Content)).all()) == 1


def test_ideas_and_plan_can_save_drafts(db, human, brand):
    ideas = run(db, human, JobType.IDEAS, {"count": 2, "save_as_drafts": True})
    assert len(ideas.result["ideas"]) == 2
    plan = run(
        db,
        human,
        JobType.CONTENT_PLAN,
        {"start_date": "2026-10-12", "period": "week", "save_as_drafts": True},
    )
    items = plan.result["items"]
    assert all(i["status"] == "DRAFT_CREATED" and i["content_id"] for i in items)
    drafts = db.scalars(select(Content)).all()
    assert len(drafts) == 2 + len(items)
    assert {c.status for c in drafts} == {ContentStatus.DRAFT}


def test_strategy_uses_real_performance_only(db, human, brand):
    calls = []

    def responder(prompt, system):
        calls.append(prompt)
        from app.providers.ai.mock import builtin_response

        return builtin_response(prompt)

    run(db, human, JobType.STRATEGY, {}, factory=mock_factory(responder=responder))
    assert "No performance data is available" in calls[0]


def test_request_authorization(db, human, viewer, brand):
    service = AIContentService(db, provider_factory=mock_factory())
    with pytest.raises(PermissionDeniedError):
        service.request(JobType.POST, {"topic": "abc"}, viewer)
    with pytest.raises(PermissionDeniedError):
        service.request(JobType.POST, {"topic": "abc"}, AgentActor(name="x"))
    with pytest.raises(PermissionDeniedError):
        service.request(JobType.POST, {"topic": "abc"}, SystemActor("x"))


def test_request_validation(db, human, brand):
    service = AIContentService(db, provider_factory=mock_factory())
    with pytest.raises(AppError, match="not enabled"):
        service.request(JobType.POST, {"topic": "abc", "language": "ru"}, human)
    with pytest.raises(NotFoundError):
        service.request(JobType.POST, {"topic": "abc", "brand_profile_id": 999}, human)
    with pytest.raises(AppError):
        service.request("publish", {}, human)


def test_no_brand_profile(db, human):
    with pytest.raises(NotFoundError, match="No default brand profile"):
        AIContentService(db).request(JobType.POST, {"topic": "abc"}, human)


def test_active_job_limit(db, human, brand, monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "ai_max_active_jobs_per_user", 2)
    service = AIContentService(db, provider_factory=mock_factory())
    service.request(JobType.POST, {"topic": "abc"}, human)
    service.request(JobType.POST, {"topic": "abc"}, human)
    with pytest.raises(TooManyRequestsError):
        service.request(JobType.POST, {"topic": "abc"}, human)


def test_audit_trail_without_prompt_text(db, human, brand):
    outcome = run(db, human, JobType.POST, {"topic": "abc", "instructions": "MAXFIY-SO'ROV"})
    actions = [a.action for a in db.scalars(select(AuditLog).order_by(AuditLog.id))]
    for expected in (
        "AI_JOB_REQUESTED",
        "AI_JOB_STARTED",
        "CONTENT_CREATED",
        "CONTENT_VERSION_CREATED",
        "AI_JOB_SUCCEEDED",
    ):
        assert expected in actions
    requested = db.scalars(select(AuditLog).where(AuditLog.action == "AI_JOB_REQUESTED")).one()
    assert requested.actor_user_id == human.user_id
    created = db.scalars(select(AuditLog).where(AuditLog.action == "CONTENT_CREATED")).one()
    assert created.actor_type == ActorType.AGENT and created.actor_name == "agent:content_creator"
    for row in db.scalars(select(AuditLog)):
        assert "MAXFIY" not in str(row.details)
    job = db.get(AIJob, outcome.job.id)
    assert "MAXFIY" not in json.dumps(job.output)


def test_job_input_redacts_secret_like_keys(db, human, brand):
    service = AIContentService(db, provider_factory=mock_factory())
    job = service.request(JobType.POST, {"topic": "abc", "api_key": "sk-123"}, human)
    assert job.input["api_key"] == "***REDACTED***"


def test_pipeline_agent_cannot_edit_after_human_approval(db, human, brand):
    content = run(db, human, JobType.POST, {"topic": "abc", "submit_for_review": True}).content
    ApprovalService(db).approve(content.id, human, expected_version=1)
    agent = AgentActor(name="content_creator", tools=PIPELINE_AGENT_TOOLS)
    with pytest.raises(PermissionDeniedError):
        ContentService(db).update(content.id, agent, expected_version=1, changes={"cta": "x"})
    with pytest.raises(InvalidStateTransitionError):
        ContentService(db).submit_for_review(content.id, agent)


def test_celery_mode_executes_via_task(db, human, brand, monkeypatch):
    import app.services.ai_content as module
    from app.workers.celery_app import celery_app
    from app.workers.tasks.ai import run_ai_job

    monkeypatch.setattr(module, "create_ai_provider", mock_factory())
    celery_app.conf.task_always_eager = True
    job = AIContentService(db).request(JobType.HASHTAGS, {"topic": "minimalism"}, human)
    assert run_ai_job.delay(job.id).get(timeout=5) == "SUCCEEDED"
    db.expire_all()
    assert db.get(AIJob, job.id).status == AIJobStatus.SUCCEEDED
    assert run_ai_job.delay(job.id).get(timeout=5) == "SUCCEEDED"  # idempotent re-delivery
