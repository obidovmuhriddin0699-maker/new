"""Real concurrency checks — only meaningful on PostgreSQL (row locks)."""

import threading

import pytest

from app.core.config import get_settings
from app.core.database import get_sessionmaker
from app.repositories import ApprovalRepository
from app.services import ApprovalService
from tests.conftest import make_ready

pytestmark = pytest.mark.skipif(
    get_settings().is_sqlite, reason="needs PostgreSQL (set TEST_DATABASE_URL)"
)


def test_concurrent_approvals_create_exactly_one(db, human):
    content = make_ready(db, human)
    barrier = threading.Barrier(4)
    results: list[object] = []

    def approve() -> None:
        with get_sessionmaker()() as session:
            barrier.wait()
            try:
                results.append(
                    ApprovalService(session).approve(content.id, human, expected_version=1)
                )
            except Exception as exc:  # noqa: BLE001
                results.append(exc)

    threads = [threading.Thread(target=approve) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert all(not isinstance(r, Exception) for r in results), results
    assert sum(1 for r in results if r.created) == 1
    assert len({r.approval.id for r in results}) == 1
    assert len(ApprovalRepository(db).list_for_content(content.id)) == 1


def test_concurrent_workers_claim_a_schedule_once(db, human):
    from sqlalchemy import select

    from app.models import ContentSchedule
    from app.models.base import utcnow
    from app.services import ScheduleService
    from app.services.publish import PublishService
    from tests.conftest import make_approved

    content = make_approved(db, human)
    ScheduleService(db).schedule(content.id, human, scheduled_at=utcnow())
    schedule_id = db.scalars(select(ContentSchedule.id)).one()
    barrier = threading.Barrier(6)
    wins: list[bool] = []

    def claim() -> None:
        with get_sessionmaker()() as session:
            barrier.wait()
            wins.append(PublishService(session)._claim(schedule_id))

    threads = [threading.Thread(target=claim) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert sorted(wins) == [False] * 5 + [True]
