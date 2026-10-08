# Content lifecycle, versioning and approval security (PHASE 2)

## 1. Layering

```
Router (app/api/v1/contents.py)      HTTP <-> schemas, auth dependency only
  -> Service (app/services/*)        business rules, permissions, transactions, audit
    -> Repository (app/repositories) SQLAlchemy queries only, never commits
      -> Database (PostgreSQL / SQLite)
```

* Transactions: every public service method runs inside `atomic(session)`
  (`app/core/transaction.py`). The outermost block commits; any exception rolls
  back everything (content, version rows, approvals, audit rows). Nested
  service calls join the outer transaction.
* Row locks: state-changing methods load content with `SELECT … FOR UPDATE`
  (PostgreSQL; no-op on SQLite).
* Repositories are synchronous on purpose: the DB driver (psycopg 3) and the
  routes are sync, FastAPI runs them in its thread pool. Moving to
  `AsyncSession` later only touches repositories + `get_db`.

## 2. Actors

| Actor | Created from | Can |
|---|---|---|
| `HumanActor(user_id, channel)` | verified JWT with `actor=human` (web), later Telegram | create/edit, submit, **approve / reject / request edit**, schedule |
| `AgentActor(name, tools)` | agent runtime (PHASE 3) | create/edit/submit only with matching `AgentTool`; never approve, schedule, publish, or touch approved content / OAuth tokens |
| `SystemActor(name)` | backend workers | `publish_service` alone may move content into PUBLISHING/PUBLISHED/FAILED |

Approval-type operations re-load the user from the database (must exist, be
active, role OWNER/ADMIN). Constructing a `HumanActor` in code with an
unknown/inactive user id is refused and audited as `APPROVAL_DENIED`.

## 3. State machine (`app/services/content_state.py`)

```
DRAFT ─────────► GENERATING ─────► READY_FOR_REVIEW ──► APPROVED ──► SCHEDULED
  │                 │   ▲               │   │   │          │  ▲          │
  │                 │   │               │   │   │          │  └─unsched──┘
  └──submit─────────┼───┼──────────────►│   │   └► REJECTED (terminal)
                    │   │               │   └► EDIT_REQUESTED ─► GENERATING / READY_FOR_REVIEW
                    ▼   │               │
                  FAILED┘◄──────────┐   │     APPROVED / SCHEDULED / FAILED ──edit──► READY_FOR_REVIEW
                                    │   │
          APPROVED / SCHEDULED / FAILED ──► PUBLISHING ──► PUBLISHED (terminal)
                                                   └────► FAILED
```

Full table:

| From | Allowed to |
|---|---|
| DRAFT | GENERATING, READY_FOR_REVIEW |
| GENERATING | READY_FOR_REVIEW, FAILED |
| READY_FOR_REVIEW | EDIT_REQUESTED, APPROVED*, REJECTED |
| EDIT_REQUESTED | GENERATING, READY_FOR_REVIEW |
| APPROVED | SCHEDULED†, PUBLISHING†, EDIT_REQUESTED, READY_FOR_REVIEW (edit) |
| SCHEDULED | PUBLISHING†, APPROVED (unschedule), EDIT_REQUESTED, READY_FOR_REVIEW (edit) |
| PUBLISHING | PUBLISHED, FAILED |
| FAILED | GENERATING, PUBLISHING†, READY_FOR_REVIEW (edit) |
| PUBLISHED, REJECTED | — (terminal) |

\* only via `ApprovalService.approve` by a verified human.
† additionally requires a **valid approval of the current version** (below).
Anything not in the table raises `InvalidStateTransitionError` (HTTP 409).

## 4. Versioning

* `contents` holds the working copy and `version` (current version number).
* `content_versions` holds an **immutable snapshot per version**: type,
  language, topic, hook, caption, hashtags, CTA, script, visual prompt, aspect
  ratio, media references (asset id, URL, checksum, size…), AI metadata
  (provider, model, job id), source (HUMAN/AGENT/SYSTEM), creator, note,
  `created_at`, and `content_hash` = SHA-256 of the canonical snapshot.
* Any effective change of a publishable field or of the asset list creates
  version N+1. No-op edits do not.
* Edits require `expected_version` (optimistic locking) — a stale editor gets
  HTTP 409 `version_mismatch` instead of silently overwriting.
* Editing APPROVED / SCHEDULED / FAILED content moves it back to
  READY_FOR_REVIEW, invalidates active approvals and cancels pending schedules.

## 5. Approval security

An approval row stores `content_id`, `content_version`, `content_hash`,
`decided_by_user_id`, `channel`, `decision`, `created_at`, and
`invalidated_at`/`invalidation_reason`.

Publishing (PHASE 8) is authorised **only** by
`ApprovalService.require_valid_approval(content)`, which requires all of:

1. an APPROVED, non-invalidated approval for `content.version`;
2. its `content_hash` equals the stored snapshot hash of that version **and**
   the hash recomputed from the live working copy (detects edits that bypassed
   versioning, e.g. direct SQL);
3. the approving user is still active with an approver role.

There is no `approved` boolean on content. A partial unique index
(`uq_approvals_active_approved`) allows at most one active approval per
content version, which also makes `approve` idempotent under concurrency.

## 6. Idempotency

| Operation | Mechanism |
|---|---|
| approve | same version → returns existing approval (`created=false`); DB partial unique index for races |
| schedule | `idempotency_key = publish:content:{id}:v{version}` (unique); repeat returns existing |
| future publish | the same key; `start_publishing` refuses a version whose schedule is DONE |

## 7. Audit events

`CONTENT_CREATED, CONTENT_UPDATED, CONTENT_VERSION_CREATED,
CONTENT_SUBMITTED_FOR_REVIEW, CONTENT_EDIT_REQUESTED, CONTENT_APPROVED,
CONTENT_APPROVAL_INVALIDATED, CONTENT_REJECTED, CONTENT_SCHEDULED,
CONTENT_SCHEDULE_CANCELLED, CONTENT_PUBLISH_STARTED, CONTENT_PUBLISH_SUCCEEDED,
CONTENT_PUBLISH_FAILED, APPROVAL_DENIED, STATE_TRANSITION_DENIED`, plus asset,
brand, AI job, Instagram account and token events.

Each row: timestamp, actor type, actor user id (only if the user really
exists), actor name, action, content id, **content version**, status
(SUCCESS / FAILED / DENIED), error, details, request id. Details are
recursively redacted (`password`, `token`, `secret`, `authorization`,
`api_key`, `encryption_key`, …). Successful events are written in the same
transaction as the change; denied attempts are written after rollback so they
are never lost.
