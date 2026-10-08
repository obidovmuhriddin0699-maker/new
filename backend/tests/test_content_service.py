import pytest

from app.agents.permissions import AgentTool
from app.core.actors import AgentActor, SystemActor
from app.core.errors import (
    AppError,
    ConflictError,
    InvalidStateTransitionError,
    NotFoundError,
    PermissionDeniedError,
    VersionMismatchError,
)
from app.models.enums import (
    ActorType,
    AssetKind,
    AuditAction,
    ContentStatus,
    ContentType,
)
from app.repositories import AuditLogRepository, ContentVersionRepository
from app.services import AssetInput, ContentService
from tests.conftest import make_approved, make_content, make_ready


def _actions(db, content_id):
    return [e.action for e in AuditLogRepository(db).list_for_content(content_id)]


def test_create_makes_draft_v1_with_snapshot_and_audit(db, human):
    content = make_content(db, human, cta="Saqlang")
    assert content.status == ContentStatus.DRAFT
    assert content.version == 1
    assert content.created_by == ActorType.HUMAN
    v1 = ContentVersionRepository(db).get_version(content.id, 1)
    assert v1.caption == content.caption and v1.cta == "Saqlang"
    assert v1.source == ActorType.HUMAN and v1.created_by_user_id == human.user_id
    assert len(v1.content_hash) == 64
    assert _actions(db, content.id) == ["CONTENT_CREATED", "CONTENT_VERSION_CREATED"]


def test_update_creates_new_immutable_version(db, human):
    content = make_content(db, human)
    service = ContentService(db)
    service.update(content.id, human, expected_version=1, changes={"caption": "Yangi matn"})
    assert content.version == 2
    versions = ContentVersionRepository(db).list_for_content(content.id)
    assert [v.version for v in versions] == [1, 2]
    assert versions[0].caption == "Minimalizm haqida post"  # v1 preserved
    assert versions[1].caption == "Yangi matn"
    assert versions[0].content_hash != versions[1].content_hash
    assert "CONTENT_UPDATED" in _actions(db, content.id)


def test_noop_update_does_not_bump_version(db, human):
    content = make_content(db, human)
    ContentService(db).update(
        content.id, human, expected_version=1, changes={"caption": content.caption}
    )
    assert content.version == 1


def test_update_with_stale_version_rejected(db, human):
    content = make_content(db, human)
    service = ContentService(db)
    service.update(content.id, human, expected_version=1, changes={"caption": "a"})
    with pytest.raises(VersionMismatchError):
        service.update(content.id, human, expected_version=1, changes={"caption": "b"})
    assert content.caption == "a"


def test_unknown_fields_rejected(db, human):
    content = make_content(db, human)
    with pytest.raises(AppError):
        ContentService(db).update(
            content.id, human, expected_version=1, changes={"status": "PUBLISHED"}
        )
    with pytest.raises(AppError):
        ContentService(db).update(content.id, human, expected_version=1, changes={"version": 9})


def test_viewer_cannot_create_or_edit(db, human, viewer):
    with pytest.raises(PermissionDeniedError):
        make_content(db, viewer)
    content = make_content(db, human)
    with pytest.raises(PermissionDeniedError):
        ContentService(db).update(content.id, viewer, expected_version=1, changes={"topic": "x"})


def test_agent_needs_tools(db):
    no_tools = AgentActor(name="weak", tools=frozenset())
    with pytest.raises(PermissionDeniedError):
        make_content(db, no_tools)
    creator = AgentActor(name="creator", tools=frozenset({AgentTool.CREATE_CONTENT}))
    content = make_content(db, creator)
    assert content.created_by == ActorType.AGENT
    with pytest.raises(PermissionDeniedError):
        ContentService(db).update(content.id, creator, expected_version=1, changes={"topic": "x"})


def test_system_actor_is_not_a_content_writer(db):
    with pytest.raises(PermissionDeniedError):
        make_content(db, SystemActor("scheduler"))


def test_submit_for_review_rules(db, human):
    content = make_content(db, human, caption=None)
    service = ContentService(db)
    with pytest.raises(ConflictError):
        service.submit_for_review(content.id, human)  # incomplete
    service.update(content.id, human, expected_version=1, changes={"caption": "ok"})
    service.submit_for_review(content.id, human)
    assert content.status == ContentStatus.READY_FOR_REVIEW
    with pytest.raises(InvalidStateTransitionError):
        service.submit_for_review(content.id, human)


@pytest.mark.parametrize(
    "status",
    [
        ContentStatus.PUBLISHED,
        ContentStatus.REJECTED,
        ContentStatus.PUBLISHING,
        ContentStatus.GENERATING,
    ],
)
def test_non_editable_states(db, human, status):
    content = make_content(db, human)
    content.status = status
    db.commit()
    with pytest.raises(InvalidStateTransitionError):
        ContentService(db).update(content.id, human, expected_version=1, changes={"topic": "x"})


def test_assets_are_part_of_the_version(db, human):
    content = make_content(db, human)
    service = ContentService(db)
    asset = service.add_asset(
        content.id,
        human,
        expected_version=1,
        asset=AssetInput(
            kind=AssetKind.IMAGE, public_url="https://cdn.example/1.jpg", checksum_sha256="a" * 64
        ),
    )
    assert content.version == 2
    v2 = ContentVersionRepository(db).get_version(content.id, 2)
    assert v2.media[0]["asset_id"] == asset.id
    assert v2.media[0]["checksum_sha256"] == "a" * 64
    service.remove_asset(content.id, asset.id, human, expected_version=2)
    assert content.version == 3
    assert ContentVersionRepository(db).get_version(content.id, 3).media == []
    with pytest.raises(NotFoundError):
        service.remove_asset(content.id, 9999, human, expected_version=3)


def test_ai_generation_flow(db, human, agent):
    content = make_content(db, human, caption=None)
    service = ContentService(db)
    service.start_generation(content.id, agent)
    assert content.status == ContentStatus.GENERATING
    service.complete_generation(
        content.id,
        agent,
        fields={"caption": "AI matni", "content_type": ContentType.REELS, "script": "1. Hook"},
        ai_metadata={"provider": "ollama", "model": "qwen2.5:3b", "ai_job_id": 7},
    )
    assert content.status == ContentStatus.READY_FOR_REVIEW  # never further than review
    v2 = ContentVersionRepository(db).get_version(content.id, 2)
    assert v2.source == ActorType.AGENT and v2.created_by_name == "agent:content_creator"
    assert v2.ai_metadata["model"] == "qwen2.5:3b"


def test_generation_only_by_agents(db, human):
    content = make_content(db, human)
    with pytest.raises(PermissionDeniedError):
        ContentService(db).start_generation(content.id, human)


def test_generation_failure(db, human, agent):
    content = make_content(db, human)
    service = ContentService(db)
    service.start_generation(content.id, agent)
    service.fail_generation(content.id, agent, error="Ollama unavailable")
    assert content.status == ContentStatus.FAILED
    assert "CONTENT_GENERATION_FAILED" in _actions(db, content.id)


def test_agent_cannot_edit_approved_content(db, human, agent):
    content = make_approved(db, human)
    with pytest.raises(PermissionDeniedError):
        ContentService(db).update(
            content.id, agent, expected_version=content.version, changes={"caption": "hack"}
        )


def test_soft_delete_invalidates_approval(db, human):
    content = make_approved(db, human)
    service = ContentService(db)
    service.soft_delete(content.id, human)
    with pytest.raises(NotFoundError):
        service.get(content.id)
    assert "CONTENT_DELETED" in _actions(db, content.id)
    assert "CONTENT_APPROVAL_INVALIDATED" in _actions(db, content.id)


def test_history(db, human):
    content = make_ready(db, human)
    h = ContentService(db).history(content.id)
    assert [v.version for v in h.versions] == [1]
    assert h.events[-1].action == AuditAction.CONTENT_SUBMITTED_FOR_REVIEW.value
