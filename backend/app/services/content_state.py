"""Content lifecycle state machine.

The table below is the single source of truth for allowed status changes.
``Content.status`` must only be changed through ``apply_transition``.
Guards that need data (a valid human approval) are enforced by the services
before calling ``apply_transition``; see ``APPROVAL_GUARDED_TARGETS``.
"""

from app.core.errors import InvalidStateTransitionError
from app.models import Content
from app.models.enums import ContentStatus as S

TRANSITIONS: dict[S, frozenset[S]] = {
    S.DRAFT: frozenset({S.GENERATING, S.READY_FOR_REVIEW}),
    S.GENERATING: frozenset({S.READY_FOR_REVIEW, S.FAILED}),
    S.READY_FOR_REVIEW: frozenset({S.EDIT_REQUESTED, S.APPROVED, S.REJECTED}),
    S.EDIT_REQUESTED: frozenset({S.GENERATING, S.READY_FOR_REVIEW}),
    # APPROVED/SCHEDULED -> READY_FOR_REVIEW happens when a human edits approved
    # content: a new version is created and needs a new approval.
    S.APPROVED: frozenset({S.SCHEDULED, S.PUBLISHING, S.EDIT_REQUESTED, S.READY_FOR_REVIEW}),
    S.SCHEDULED: frozenset({S.PUBLISHING, S.APPROVED, S.EDIT_REQUESTED, S.READY_FOR_REVIEW}),
    S.PUBLISHING: frozenset({S.PUBLISHED, S.FAILED}),
    # FAILED covers generation and publish failures. Retrying publish still
    # requires a valid approval for the current version (guard below).
    S.FAILED: frozenset({S.GENERATING, S.PUBLISHING, S.READY_FOR_REVIEW}),
    S.PUBLISHED: frozenset(),
    S.REJECTED: frozenset(),
}

TERMINAL_STATES: frozenset[S] = frozenset(s for s, targets in TRANSITIONS.items() if not targets)

# Entering these states requires an active human approval of the *current* version.
APPROVAL_GUARDED_TARGETS: frozenset[S] = frozenset({S.SCHEDULED, S.PUBLISHING})

# States in which a human may edit the content (creating a new version).
EDITABLE_STATES: frozenset[S] = frozenset(
    {S.DRAFT, S.EDIT_REQUESTED, S.READY_FOR_REVIEW, S.APPROVED, S.SCHEDULED, S.FAILED}
)

# After an edit, approved/scheduled/failed content goes back to review.
STATUS_AFTER_EDIT: dict[S, S] = {
    S.APPROVED: S.READY_FOR_REVIEW,
    S.SCHEDULED: S.READY_FOR_REVIEW,
    S.FAILED: S.READY_FOR_REVIEW,
}


def can_transition(current: S, target: S) -> bool:
    return target in TRANSITIONS.get(current, frozenset())


def assert_transition(current: S, target: S) -> None:
    if not can_transition(current, target):
        raise InvalidStateTransitionError(
            f"Transition {current.value} -> {target.value} is not allowed",
            details={"from": current.value, "to": target.value},
        )


def apply_transition(content: Content, target: S) -> S:
    """Validate and apply. Returns the previous status."""
    previous = content.status
    assert_transition(previous, target)
    content.status = target
    return previous
