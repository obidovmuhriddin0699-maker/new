"""Telegram bot business logic (framework-independent, synchronous, testable).

Security model
--------------
* A Telegram account must be (1) listed in ``TELEGRAM_ALLOWED_USER_IDS`` and
  (2) linked to an active panel user via a one-time code generated in the
  panel. Every update re-checks both.
* Decisions run through ``ApprovalService`` as ``HumanActor(channel=TELEGRAM)``,
  so the same role, version and hash rules apply as in the web panel.
* Inline buttons carry only a random one-time token. The action, content id,
  content version and the Telegram user it was issued to are stored
  server-side (hashed token). Buttons cannot be forged, replayed, or used by
  another account, and a button for version N cannot act on version N+1.
* Approve and reject need a second confirmation tap.
"""

import hashlib
import html
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.actors import Actor, HumanActor, SystemActor
from app.core.config import get_settings
from app.core.errors import AppError, NotFoundError, PermissionDeniedError
from app.core.transaction import atomic
from app.models import AuditLog, Content, TelegramActionToken, TelegramLinkCode, User
from app.models.base import utcnow
from app.models.enums import ApprovalChannel, AuditAction, ContentStatus
from app.repositories import ContentRepository, SystemSettingRepository, UserRepository
from app.services.approval import ApprovalService
from app.services.audit import AuditLogService
from app.services.guards import APPROVER_ROLES, require_active_human

CALLBACK_PREFIX = "mx:"
NOTIFY_CURSOR_KEY = "telegram.notify_cursor"
REMINDER_KEY = "telegram.last_reminder_at"
CONFIRM_TTL = timedelta(minutes=10)
EDIT_TTL = timedelta(minutes=30)
MAX_MESSAGE = 3900

STATUS_LABEL = {
    "DRAFT": "Qoralama",
    "GENERATING": "Yaratilmoqda",
    "READY_FOR_REVIEW": "Ko‘rib chiqish",
    "EDIT_REQUESTED": "Tahrir so‘ralgan",
    "APPROVED": "Tasdiqlangan",
    "SCHEDULED": "Rejalashtirilgan",
    "PUBLISHING": "Nashr qilinmoqda",
    "PUBLISHED": "Nashr qilingan",
    "FAILED": "Xato",
    "REJECTED": "Rad etilgan",
}
TYPE_LABEL = {"POST": "Post", "CAROUSEL": "Karusel", "REELS": "Reels", "STORY": "Story"}

ERROR_TEXT = {
    "version_mismatch": (
        "Kontent bu xabar yuborilgandan keyin o‘zgargan. Yangi versiyani ko‘rib chiqing."
    ),
    "invalid_state_transition": "Kontent holati bu amalga ruxsat bermaydi.",
    "approval_forbidden": "Tasdiqlash uchun OWNER yoki ADMIN roli kerak.",
    "permission_denied": "Bu amal uchun ruxsatingiz yo‘q.",
    "not_found": "Kontent topilmadi.",
    "content_integrity_error": "Kontent yaxlitligi tekshiruvidan o‘tmadi; panelda tekshiring.",
}


class TelegramAccessError(Exception):
    """User may not use the bot. ``reason`` is safe to show."""

    def __init__(self, reason: str, code: str) -> None:
        super().__init__(reason)
        self.reason = reason
        self.code = code


class TelegramTokenError(Exception):
    pass


@dataclass(slots=True)
class Button:
    text: str
    callback_data: str | None = None
    url: str | None = None


@dataclass(slots=True)
class Reply:
    text: str
    buttons: list[list[Button]] = field(default_factory=list)
    # When set, the bot waits for the user's next text message as an edit comment.
    await_comment_token: str | None = None
    # When True, the bot replaces the original message's keyboard instead of sending a new one.
    edit_original: bool = False


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _parse_ts(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def esc(value: object) -> str:
    return html.escape(str(value), quote=False)


def _cut(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


class TelegramService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.audit = AuditLogService(session)
        self.settings = get_settings()

    # ------------------------------------------------------------------ access
    def is_allowed(self, telegram_id: int) -> bool:
        return telegram_id in self.settings.telegram_allowed_user_ids

    def resolve_user(self, telegram_id: int) -> User:
        if not self.is_allowed(telegram_id):
            raise TelegramAccessError(
                "Sizga bu botdan foydalanishga ruxsat berilmagan.", "not_allowed"
            )
        user = UserRepository(self.session).get_by_telegram_id(telegram_id)
        if user is None:
            raise TelegramAccessError(
                "Telegram hisobingiz panelga bog‘lanmagan. Panel → Telegram sahifasida kod oling "
                "va botga /start KOD yuboring.",
                "not_linked",
            )
        if not user.is_active:
            raise TelegramAccessError("Panel hisobingiz faol emas.", "inactive")
        return user

    def actor(self, telegram_id: int) -> HumanActor:
        return HumanActor(
            user_id=self.resolve_user(telegram_id).id, channel=ApprovalChannel.TELEGRAM
        )

    def record_denied(self, telegram_id: int, reason: str) -> None:
        with atomic(self.session):
            self.audit.record(
                AuditAction.TELEGRAM_ACCESS_DENIED,
                SystemActor("telegram_bot"),
                status="DENIED",
                error=reason,
                details={"telegram_user_id": telegram_id},
            )

    # ------------------------------------------------------------------ linking
    def create_link_code(self, actor: Actor) -> tuple[str, Any]:
        user = require_active_human(self.session, actor)
        raw = secrets.token_hex(4).upper()  # 8 hex chars, e.g. 7F3A9C1E
        code = f"{raw[:4]}-{raw[4:]}"
        expires = utcnow() + timedelta(minutes=self.settings.telegram_link_code_ttl_minutes)
        with atomic(self.session):
            for old in self.session.scalars(
                select(TelegramLinkCode).where(
                    TelegramLinkCode.user_id == user.id, TelegramLinkCode.used_at.is_(None)
                )
            ):
                old.used_at = utcnow()  # only the newest code is valid
            self.session.add(
                TelegramLinkCode(user_id=user.id, code_hash=_hash(code), expires_at=expires)
            )
            self.audit.record(
                AuditAction.TELEGRAM_LINK_CODE_CREATED,
                actor,
                details={"expires_at": expires.isoformat()},
            )
        return code, expires

    def link(self, telegram_id: int, code: str) -> User:
        if not self.is_allowed(telegram_id):
            self.record_denied(telegram_id, "link attempt from non-allowed Telegram id")
            raise TelegramAccessError(
                "Sizga bu botdan foydalanishga ruxsat berilmagan.", "not_allowed"
            )
        from app.core.ratelimit import TELEGRAM_LINK_ATTEMPT, get_limiter

        limiter, key = get_limiter(), f"tg:{telegram_id}"
        allowed, _ = limiter.peek(TELEGRAM_LINK_ATTEMPT, key)
        if not allowed:
            self.record_denied(telegram_id, "too many wrong link codes")
            raise TelegramAccessError(TELEGRAM_LINK_ATTEMPT.message, "rate_limited")
        normalized = code.strip().upper()
        if len(normalized) == 8 and "-" not in normalized:
            normalized = f"{normalized[:4]}-{normalized[4:]}"
        with atomic(self.session):
            row = self.session.scalar(
                select(TelegramLinkCode).where(TelegramLinkCode.code_hash == _hash(normalized))
            )
            if row is None or row.used_at is not None or row.expires_at <= utcnow():
                limiter.hit(TELEGRAM_LINK_ATTEMPT, key)
                raise TelegramAccessError(
                    "Kod noto‘g‘ri yoki muddati o‘tgan. Panelda yangi kod oling.", "invalid_code"
                )
            users = UserRepository(self.session)
            user = users.get_active(row.user_id)
            if user is None:
                raise TelegramAccessError("Panel hisobingiz faol emas.", "inactive")
            other = users.get_by_telegram_id(telegram_id)
            if other is not None and other.id != user.id:
                other.telegram_user_id = None  # one Telegram account -> one panel user
                self.session.flush()  # release the unique value before re-assigning it
            user.telegram_user_id = telegram_id
            row.used_at = utcnow()
            row.used_by_telegram_id = telegram_id
            self.audit.record(
                AuditAction.TELEGRAM_ACCOUNT_LINKED,
                HumanActor(user_id=user.id, channel=ApprovalChannel.TELEGRAM),
                details={"telegram_user_id": telegram_id},
            )
            return user

    def unlink(self, actor: Actor) -> None:
        user = require_active_human(self.session, actor)
        with atomic(self.session):
            previous = user.telegram_user_id
            user.telegram_user_id = None
            self.audit.record(
                AuditAction.TELEGRAM_ACCOUNT_UNLINKED,
                actor,
                details={"telegram_user_id": previous},
            )

    # ------------------------------------------------------------------ tokens
    def issue_token(
        self, telegram_id: int, action: str, content: Content, ttl: timedelta | None = None
    ) -> str:
        token = secrets.token_urlsafe(16)
        ttl = ttl or timedelta(hours=self.settings.telegram_action_ttl_hours)
        self.session.add(
            TelegramActionToken(
                token_hash=_hash(token),
                telegram_user_id=telegram_id,
                action=action,
                content_id=content.id,
                content_version=content.version,
                expires_at=utcnow() + ttl,
            )
        )
        self.session.flush()
        return token

    def consume_token(self, telegram_id: int, token: str, allowed: set[str]) -> TelegramActionToken:
        row = self.session.scalar(
            select(TelegramActionToken)
            .where(TelegramActionToken.token_hash == _hash(token))
            .with_for_update()
        )
        if row is None or row.telegram_user_id != telegram_id or row.action not in allowed:
            raise TelegramTokenError("Bu tugma yaroqsiz.")
        if row.used_at is not None:
            raise TelegramTokenError("Bu tugma allaqachon ishlatilgan.")
        if row.expires_at <= utcnow():
            raise TelegramTokenError(
                "Bu tugmaning muddati tugagan. Panelda yoki /content orqali qayta oching."
            )
        row.used_at = utcnow()
        self.session.flush()
        return row

    def review_buttons(self, telegram_id: int, content: Content) -> list[list[Button]]:
        cb = lambda action: CALLBACK_PREFIX + self.issue_token(telegram_id, action, content)  # noqa: E731
        return [
            [Button("✅ TASDIQLASH", cb("approve"))],
            [Button("✏️ TAHRIR", cb("edit")), Button("❌ RAD ETISH", cb("reject"))],
            [Button("Panelda ochish", url=self.panel_link(content))],
        ]

    def panel_link(self, content: Content) -> str:
        return f"{self.settings.panel_public_url.rstrip('/')}/content/{content.id}"

    # ------------------------------------------------------------------ callbacks
    def handle_callback(self, telegram_id: int, data: str) -> Reply:
        actor = self.actor(telegram_id)
        if not data.startswith(CALLBACK_PREFIX):
            return Reply("Noma’lum tugma.")
        token = data[len(CALLBACK_PREFIX) :]
        decision: tuple[str, int, int] | None = None
        try:
            # 1) Validate and burn the token in its own transaction.
            with atomic(self.session):
                row = self.consume_token(
                    telegram_id,
                    token,
                    {
                        "approve",
                        "reject",
                        "edit",
                        "approve_confirm",
                        "reject_confirm",
                        "cancel",
                        "rework",
                    },
                )
                content = ContentRepository(self.session).get(row.content_id)
                if content is None:
                    return Reply("Kontent topilmadi yoki o‘chirilgan.")
                if content.version != row.content_version:
                    return Reply(
                        f"Bu tugma v{row.content_version} uchun edi, hozirgi versiya "
                        f"v{content.version}. Yangi versiyani ko‘rib chiqing.",
                        buttons=self._fresh_buttons(telegram_id, content),
                    )
                action = row.action
                if action in ("approve", "reject"):
                    return self._confirm_prompt(telegram_id, content, action)
                if action == "cancel":
                    return Reply(
                        "Bekor qilindi.",
                        buttons=self._fresh_buttons(telegram_id, content),
                        edit_original=True,
                    )
                if action == "edit":
                    edit_token = self.issue_token(telegram_id, "edit_submit", content, EDIT_TTL)
                    return Reply(
                        f"#{content.id} (v{content.version}) uchun nimani o‘zgartirish kerak? "
                        "Izohni bitta xabarda yozing. Izohsiz yuborish uchun /skip.",
                        await_comment_token=edit_token,
                    )
                decision = (action, content.id, row.content_version)
        except TelegramTokenError as exc:
            return Reply(str(exc))

        # 2) The decision runs in ApprovalService's own transaction, so denied
        #    attempts are audited even though the decision itself fails.
        action, content_id, version = decision
        if action == "rework":
            return self._rework(actor, content_id, version)
        approvals = ApprovalService(self.session, self.audit)
        try:
            if action == "approve_confirm":
                approvals.approve(content_id, actor, expected_version=version)
                return Reply(
                    f"✅ #{content_id} v{version} tasdiqlandi.\n"
                    "Nashr qilinmadi — avtomatik nashr PHASE 8 da qo‘shiladi.",
                    edit_original=True,
                )
            approvals.reject(
                content_id, actor, expected_version=version, comment="Telegram orqali rad etildi"
            )
            return Reply(f"❌ #{content_id} v{version} rad etildi.", edit_original=True)
        except AppError as exc:
            return Reply(ERROR_TEXT.get(exc.code, exc.message))

    def _confirm_prompt(self, telegram_id: int, content: Content, action: str) -> Reply:
        approve = action == "approve"
        question = "tasdiqlaysizmi" if approve else "rad etasizmi"
        yes = CALLBACK_PREFIX + self.issue_token(
            telegram_id, f"{action}_confirm", content, CONFIRM_TTL
        )
        no = CALLBACK_PREFIX + self.issue_token(telegram_id, "cancel", content, CONFIRM_TTL)
        return Reply(
            f"#{content.id} kontentning <b>v{content.version}</b> versiyasini {question}?"
            + ("\nBu amal nashr qilmaydi." if approve else ""),
            buttons=[
                [
                    Button("Ha, tasdiqlayman" if approve else "Ha, rad etaman", yes),
                    Button("Bekor qilish", no),
                ]
            ],
            edit_original=True,
        )

    def submit_edit_comment(self, telegram_id: int, token: str, comment: str | None) -> Reply:
        actor = self.actor(telegram_id)
        try:
            with atomic(self.session):
                row = self.consume_token(telegram_id, token, {"edit_submit"})
                ApprovalService(self.session, self.audit).request_edit(
                    row.content_id,
                    actor,
                    expected_version=row.content_version,
                    comment=(comment or "").strip()[:1000] or None,
                )
        except TelegramTokenError as exc:
            return Reply(str(exc))
        except AppError as exc:
            return Reply(ERROR_TEXT.get(exc.code, exc.message))
        content = ContentRepository(self.session).get(row.content_id)
        buttons: list[list[Button]] = []
        if content is not None:
            with atomic(self.session):
                rework = self.issue_token(telegram_id, "rework", content)
            buttons = [
                [Button("🤖 AI qayta ishlasin", CALLBACK_PREFIX + rework)],
                [Button("Panelda tahrirlash", url=self.panel_link(content))],
            ]
        return Reply(
            f"✏️ #{row.content_id} uchun tahrir so‘raldi. AI izohingiz asosida qayta ishlashi "
            "mumkin yoki panelda o‘zingiz tahrirlang.",
            buttons=buttons,
        )

    def _rework(self, actor: HumanActor, content_id: int, version: int) -> Reply:
        """Edit -> AI rework -> back to the approval queue (approvers get notified)."""
        from app.services.ai_content import AIContentService, JobType

        service = AIContentService(self.session)
        try:
            job = service.request(
                JobType.REGENERATE,
                {"content_id": content_id, "expected_version": version},
                actor,
            )
        except AppError as exc:
            return Reply(ERROR_TEXT.get(exc.code, exc.message))
        if self.settings.ai_jobs_mode == "celery":
            from app.workers.tasks.ai import run_ai_job

            run_ai_job.delay(job.id)
            return Reply(
                f"⏳ AI #{content_id} ni qayta ishlamoqda (vazifa #{job.id}). Tayyor bo‘lgach, "
                "tasdiqlash uchun xabar keladi."
            )
        outcome = service.execute(job.id)
        if outcome.job.status.value == "FAILED":
            return Reply(
                f"⚠️ AI qayta ishlay olmadi: {esc(outcome.job.error or '')}\n"
                "Panelda tahrirlang yoki keyinroq urinib ko‘ring."
            )
        new_version = outcome.content.version if outcome.content else "?"
        return Reply(
            f"🤖 #{content_id} qayta ishlandi (v{new_version}) va ko‘rib chiqish navbatiga "
            "qaytdi. Tasdiqlash uchun xabar keladi."
        )

    def _fresh_buttons(self, telegram_id: int, content: Content) -> list[list[Button]]:
        if content.status == ContentStatus.READY_FOR_REVIEW:
            return self.review_buttons(telegram_id, content)
        return [[Button("Panelda ochish", url=self.panel_link(content))]]

    # ------------------------------------------------------------------ views
    def preview(self, content: Content, *, title: str = "INSTAGRAM KONTENT") -> str:
        line = "━━━━━━━━━━━━━━━━"
        ctype = content.content_type.value
        parts = [
            line,
            f"<b>{esc(title)}</b>  #{content.id} · v{content.version}",
            line,
            f"<b>Turi:</b> {TYPE_LABEL.get(ctype, ctype)}",
            f"<b>Holat:</b> {STATUS_LABEL.get(content.status.value, content.status.value)}",
        ]
        if content.topic:
            parts.append(f"<b>Mavzu:</b> {esc(_cut(content.topic, 200))}")
        if content.hook:
            parts.append(f"<b>Hook:</b> {esc(_cut(content.hook, 300))}")
        structure = content.structure or {}
        if structure.get("slides"):
            parts.append("<b>Slaydlar:</b>")
            for i, s in enumerate(structure["slides"][:10], 1):
                parts.append(f"{i}. {esc(_cut(str(s.get('heading', '')), 80))}")
        if structure.get("scenes"):
            parts.append(
                f"<b>Sahnalar:</b> {len(structure['scenes'])} ta, "
                f"~{structure.get('approx_duration_seconds', '?')} s"
            )
        if structure.get("frames"):
            parts.append(f"<b>Kadrlar:</b> {len(structure['frames'])} ta")
        if content.caption:
            parts.append(f"<b>Caption:</b>\n{esc(_cut(content.caption, 1500))}")
        elif content.script:
            parts.append(f"<b>Ssenariy:</b>\n{esc(_cut(content.script, 1200))}")
        if content.cta:
            parts.append(f"<b>CTA:</b> {esc(_cut(content.cta, 300))}")
        if content.hashtags:
            parts.append(f"<b>Hashtaglar:</b> {esc(_cut(' '.join(content.hashtags), 500))}")
        parts += [line, f"Muallif: {'AI' if content.created_by.value == 'AGENT' else 'Inson'}"]
        return _cut("\n".join(parts), MAX_MESSAGE)

    def pending_reviews(self, limit: int = 5) -> list[Content]:
        rows, _ = ContentRepository(self.session).search(
            status=ContentStatus.READY_FOR_REVIEW, limit=limit
        )
        return list(rows)

    def get_content(self, content_id: int) -> Content:
        content = ContentRepository(self.session).get(content_id)
        if content is None:
            raise NotFoundError("Content not found")
        return content

    def status_text(self) -> str:
        from app.services.dashboard import DashboardService

        s = DashboardService(self.session).summary()
        return "\n".join(
            [
                "<b>Holat</b>",
                f"Jami kontent: {s.total}",
                f"Tasdiq kutmoqda: {s.pending_approval}",
                f"Qoralama: {s.drafts}",
                f"Rejalashtirilgan: {s.scheduled}",
                f"Nashr qilingan: {s.published}",
                f"Xato: {s.failed}",
            ]
        )

    def analytics_text(self) -> str:
        from app.services.analytics_report import AnalyticsReportService
        from app.services.dashboard import DashboardService

        s = DashboardService(self.session).summary()
        report = AnalyticsReportService(self.session).latest()
        if not s.analytics_available and report is None:
            return (
                "<b>Analitika</b>\nMa’lumot yo‘q: Instagram statistikasi hali sinxronlanmagan. "
                "Ko‘rsatkichlar taxmin qilinmaydi."
            )
        lines = ["<b>Analitika</b>"]
        if s.reach is not None:
            lines.append(f"Qamrov (reach, 7 kun): {s.reach}")
        if s.engagement_rate is not None:
            lines.append(f"O‘rtacha engagement: {s.engagement_rate * 100:.2f}%")
        if report is not None:
            lines.append("")
            lines.append(self._report_text(report))
        return "\n".join(lines)

    @staticmethod
    def _report_text(report: Any) -> str:
        head = (
            f"<b>Haftalik hisobot</b> ({report.period_start.isoformat()} – "
            f"{report.period_end.isoformat()}, {'AI' if report.source == 'ai' else 'qoidalar'})"
        )
        body = [head, esc(_cut(report.summary, 1200))]
        if report.recommendations:
            body.append("<b>Tavsiyalar:</b>")
            body += [f"• {esc(_cut(r, 300))}" for r in report.recommendations[:5]]
        return "\n".join(body)

    def settings_text(self, telegram_id: int) -> str:
        user = self.resolve_user(telegram_id)
        return "\n".join(
            [
                "<b>Sozlamalar</b>",
                f"Panel hisobi: {esc(user.email)}",
                f"Rol: {user.role.value}",
                f"Tasdiqlash huquqi: {'ha' if user.role in APPROVER_ROLES else 'yo‘q'}",
                f"Panel: {esc(self.settings.panel_public_url)}",
                "Bog‘lanishni bekor qilish: Panel → Telegram.",
            ]
        )

    # ------------------------------------------------------------------ notifications
    def init_notify_cursor(self) -> int:
        repo = SystemSettingRepository(self.session)
        cursor = repo.get_value(NOTIFY_CURSOR_KEY)
        if cursor is None:
            # Start from "now": never flood users with historical events.
            cursor = self.session.scalar(select(func.max(AuditLog.id))) or 0
            with atomic(self.session):
                repo.set_value(NOTIFY_CURSOR_KEY, cursor, "Last audit id processed by the bot")
        return int(cursor)

    def recipients(self) -> list[User]:
        allowed = set(self.settings.telegram_allowed_user_ids)
        users = self.session.scalars(
            select(User).where(
                User.telegram_user_id.is_not(None),
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        ).all()
        return [u for u in users if u.telegram_user_id in allowed and u.role in APPROVER_ROLES]

    def collect_review_notifications(self, limit: int = 20) -> tuple[list[tuple[int, Reply]], int]:
        """New READY_FOR_REVIEW and publish-outcome events since the cursor ->
        (telegram_id, message) pairs."""
        cursor = self.init_notify_cursor()
        events = self.session.scalars(
            select(AuditLog).where(AuditLog.id > cursor).order_by(AuditLog.id).limit(200)
        ).all()
        out: list[tuple[int, Reply]] = []
        last = cursor
        seen: set[int] = set()
        recipients = self.recipients()
        with atomic(self.session):
            for event in events:
                last = event.id
                outcome = self._publish_outcome(event)
                if outcome is not None:
                    out += [(int(u.telegram_user_id or 0), outcome) for u in recipients]
                    continue
                if (
                    event.action != AuditAction.CONTENT_SUBMITTED_FOR_REVIEW.value
                    or event.content_id is None
                    or event.content_id in seen
                ):
                    continue
                content = ContentRepository(self.session).get(event.content_id)
                if content is None or content.status != ContentStatus.READY_FOR_REVIEW:
                    continue
                seen.add(content.id)
                for user in recipients:
                    tg = int(user.telegram_user_id)  # type: ignore[arg-type]
                    out.append(
                        (
                            tg,
                            Reply(
                                self.preview(content, title="YANGI KONTENT — TASDIQ KUTMOQDA"),
                                buttons=self.review_buttons(tg, content),
                            ),
                        )
                    )
                if len(seen) >= limit:
                    break
        return out, last

    def _publish_outcome(self, event: AuditLog) -> Reply | None:
        """Publish success / final failure → one short message (no buttons)."""
        details = event.details or {}
        if event.action == AuditAction.CONTENT_PUBLISH_SUCCEEDED.value:
            link = details.get("permalink")
            text = f"✅ <b>Instagram’da nashr qilindi</b> — kontent #{event.content_id}"
            if link:
                text += f"\n{esc(link)}"
            return Reply(text)
        if event.action == AuditAction.ANALYTICS_REPORT_CREATED.value:
            from app.models import AnalyticsReport

            report = self.session.get(AnalyticsReport, details.get("report_id") or 0)
            return Reply(self._report_text(report)) if report is not None else None
        if event.action == AuditAction.CONTENT_PUBLISH_FAILED.value and event.status == "FAILED":
            error = _cut(event.error or "noma’lum xato", 300)
            return Reply(
                f"❌ <b>Nashr muvaffaqiyatsiz</b> — kontent #{event.content_id}\n{esc(error)}\n"
                "Panelda ko‘ring va qayta urinib ko‘ring."
            )
        return None

    def collect_reminders(self) -> list[tuple[int, Reply]]:
        """Digest of content waiting longer than APPROVAL_REMINDER_HOURS (once per period)."""
        hours = self.settings.approval_reminder_hours
        if hours <= 0:
            return []
        repo = SystemSettingRepository(self.session)
        now = utcnow()
        last = repo.get_value(REMINDER_KEY)
        if last and (now - _parse_ts(last)) < timedelta(hours=hours):
            return []
        threshold = now - timedelta(hours=hours)
        waiting = [c for c in self.pending_reviews(limit=50) if c.updated_at <= threshold]
        with atomic(self.session):
            repo.set_value(REMINDER_KEY, now.isoformat(), "Last approval reminder digest")
        if not waiting:
            return []
        lines = [f"⏰ <b>{len(waiting)} ta kontent {hours} soatdan ko‘proq tasdiq kutmoqda</b>"]
        for c in waiting[:10]:
            lines.append(f"• #{c.id} {esc(_cut(c.topic or c.content_type.value, 60))}")
        lines.append("Ko‘rish: /content")
        text = "\n".join(lines)
        return [(int(u.telegram_user_id or 0), Reply(text)) for u in self.recipients()]

    def advance_cursor(self, last_id: int) -> None:
        with atomic(self.session):
            SystemSettingRepository(self.session).set_value(NOTIFY_CURSOR_KEY, last_id)

    def require_linked_writer(self, telegram_id: int) -> HumanActor:
        actor = self.actor(telegram_id)
        user = UserRepository(self.session).get(actor.user_id)
        if user is None or user.role not in APPROVER_ROLES:
            raise PermissionDeniedError("Your role cannot create content")
        return actor
