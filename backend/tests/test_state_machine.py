import itertools

import pytest

from app.core.errors import InvalidStateTransitionError
from app.models import Content
from app.models.enums import ContentStatus as S
from app.models.enums import ContentType
from app.services.content_state import (
    APPROVAL_GUARDED_TARGETS,
    TERMINAL_STATES,
    TRANSITIONS,
    apply_transition,
    assert_transition,
    can_transition,
)

REQUIRED = [
    (S.DRAFT, S.GENERATING),
    (S.GENERATING, S.READY_FOR_REVIEW),
    (S.READY_FOR_REVIEW, S.EDIT_REQUESTED),
    (S.EDIT_REQUESTED, S.GENERATING),
    (S.READY_FOR_REVIEW, S.APPROVED),
    (S.APPROVED, S.SCHEDULED),
    (S.APPROVED, S.PUBLISHING),
    (S.SCHEDULED, S.PUBLISHING),
    (S.PUBLISHING, S.PUBLISHED),
    (S.PUBLISHING, S.FAILED),
    (S.READY_FOR_REVIEW, S.REJECTED),
]

FORBIDDEN = [
    (S.DRAFT, S.PUBLISHED),
    (S.DRAFT, S.PUBLISHING),
    (S.DRAFT, S.APPROVED),
    (S.READY_FOR_REVIEW, S.PUBLISHING),
    (S.READY_FOR_REVIEW, S.PUBLISHED),
    (S.READY_FOR_REVIEW, S.SCHEDULED),
    (S.GENERATING, S.APPROVED),
    (S.EDIT_REQUESTED, S.APPROVED),
    (S.REJECTED, S.PUBLISHING),
    (S.REJECTED, S.APPROVED),
    (S.REJECTED, S.READY_FOR_REVIEW),
    (S.PUBLISHED, S.PUBLISHING),
    (S.APPROVED, S.PUBLISHED),
]


def test_every_status_has_a_rule():
    assert set(TRANSITIONS) == set(S)


@pytest.mark.parametrize(("src", "dst"), REQUIRED)
def test_required_transitions_allowed(src, dst):
    assert can_transition(src, dst)


@pytest.mark.parametrize(("src", "dst"), FORBIDDEN)
def test_forbidden_transitions_raise(src, dst):
    with pytest.raises(InvalidStateTransitionError):
        assert_transition(src, dst)


def test_terminal_states():
    assert TERMINAL_STATES == {S.PUBLISHED, S.REJECTED}


def test_only_approved_scheduled_failed_can_reach_publishing():
    sources = {src for src, targets in TRANSITIONS.items() if S.PUBLISHING in targets}
    assert sources == {S.APPROVED, S.SCHEDULED, S.FAILED}
    assert {S.SCHEDULED, S.PUBLISHING} == APPROVAL_GUARDED_TARGETS


def test_approved_only_reachable_from_review():
    sources = {src for src, targets in TRANSITIONS.items() if S.APPROVED in targets}
    assert sources == {S.READY_FOR_REVIEW, S.SCHEDULED}  # SCHEDULED->APPROVED = unschedule


def test_published_only_from_publishing():
    sources = {src for src, targets in TRANSITIONS.items() if S.PUBLISHED in targets}
    assert sources == {S.PUBLISHING}


def test_matrix_is_closed():
    """Every pair not in the table is rejected (no implicit transitions)."""
    for src, dst in itertools.product(S, S):
        assert can_transition(src, dst) == (dst in TRANSITIONS[src])


def test_apply_transition_leaves_status_on_failure():
    content = Content(content_type=ContentType.POST, status=S.DRAFT)
    with pytest.raises(InvalidStateTransitionError):
        apply_transition(content, S.PUBLISHED)
    assert content.status == S.DRAFT
    assert apply_transition(content, S.GENERATING) == S.DRAFT
    assert content.status == S.GENERATING
