"""aiogram handlers. Thin: parse the update, call TelegramService, render the reply."""

import logging
from datetime import date, timedelta

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.core.config import get_settings
from app.core.errors import AppError
from app.integrations.telegram.runtime import keyboard, with_service
from app.models.enums import ContentStatus
from app.services.ai_content import AIContentService, JobType
from app.services.telegram import (
    CALLBACK_PREFIX,
    ERROR_TEXT,
    Button,
    Reply,
    TelegramAccessError,
    TelegramService,
    esc,
)

logger = logging.getLogger(__name__)
router = Router(name="muxriddin")

HELP = (
    "<b>MUXRIDDIN AI INSTAGRAM MANAGER</b>\n\n"
    "/content — tasdiq kutayotgan kontent\n"
    "/content mavzu — yangi post yaratish\n"
    "/reels mavzu — Reels ssenariysi\n"
    "/story mavzu — Story konsepti\n"
    "/plan — keyingi hafta uchun reja\n"
    "/approve ID — kontentni ko‘rib chiqish va tasdiqlash\n"
    "/reject ID — kontentni rad etish\n"
    "/status — umumiy holat\n"
    "/analytics — analitika\n"
    "/settings — hisob sozlamalari\n\n"
    "AI faqat qoralama tayyorlaydi. Tasdiqlash har doim sizda."
)
MAX_TOPIC = 300


class EditComment(StatesGroup):
    waiting = State()


async def send(message: Message, reply: Reply) -> None:
    await message.answer(reply.text, reply_markup=keyboard(reply.buttons))


async def guarded(message: Message, fn) -> Reply | None:  # type: ignore[no-untyped-def]
    """Run fn(service) for a linked user; turn access errors into a friendly reply."""
    try:
        return await with_service(fn)
    except TelegramAccessError as exc:
        await message.answer(exc.reason)
    except AppError as exc:
        await message.answer(ERROR_TEXT.get(exc.code, exc.message))
    return None


# ---------------------------------------------------------------- basics
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject) -> None:
    tg = message.from_user.id  # type: ignore[union-attr]
    if command.args:
        try:
            user = await with_service(lambda s: s.link(tg, command.args or ""))
        except TelegramAccessError as exc:
            await message.answer(exc.reason)
            return
        await message.answer(
            f"✅ Hisob bog‘landi: {esc(user.email)}\n"
            "Tasdiq kutayotgan kontent haqida xabar olasiz.\n\n" + HELP
        )
        return
    try:
        await with_service(lambda s: s.resolve_user(tg))
    except TelegramAccessError as exc:
        await message.answer(f"Assalomu alaykum!\n{exc.reason}")
        return
    await message.answer(HELP)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP)


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    tg = message.from_user.id  # type: ignore[union-attr]
    reply = await guarded(message, lambda s: (s.resolve_user(tg), Reply(s.status_text()))[1])
    if reply:
        await send(message, reply)


@router.message(Command("analytics"))
async def cmd_analytics(message: Message) -> None:
    tg = message.from_user.id  # type: ignore[union-attr]
    reply = await guarded(message, lambda s: (s.resolve_user(tg), Reply(s.analytics_text()))[1])
    if reply:
        await send(message, reply)


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    tg = message.from_user.id  # type: ignore[union-attr]
    reply = await guarded(message, lambda s: Reply(s.settings_text(tg)))
    if reply:
        await send(message, reply)


# ---------------------------------------------------------------- review
def _pending(s: TelegramService, tg: int) -> list[Reply]:
    s.resolve_user(tg)
    items = s.pending_reviews(limit=5)
    if not items:
        return [Reply("Tasdiq kutayotgan kontent yo‘q.")]
    return [Reply(s.preview(c), buttons=s.review_buttons(tg, c)) for c in items]


def _review_one(s: TelegramService, tg: int, content_id: int) -> Reply:
    s.resolve_user(tg)
    content = s.get_content(content_id)
    if content.status != ContentStatus.READY_FOR_REVIEW:
        return Reply(
            s.preview(content) + "\n\nBu kontent hozir ko‘rib chiqish holatida emas.",
            buttons=[[Button("Panelda ochish", url=s.panel_link(content))]],
        )
    reply = Reply(s.preview(content), buttons=s.review_buttons(tg, content))
    s.session.commit()
    return reply


def _parse_id(command: CommandObject) -> int | None:
    arg = (command.args or "").strip().lstrip("#")
    return int(arg) if arg.isdigit() else None


@router.message(Command("approve", "reject"))
async def cmd_review(message: Message, command: CommandObject) -> None:
    tg = message.from_user.id  # type: ignore[union-attr]
    content_id = _parse_id(command)
    if content_id is None:
        await message.answer(f"Foydalanish: /{command.command} ID (masalan /{command.command} 12)")
        return
    # Text commands never decide directly: they show the content with buttons,
    # and the decision still needs the two-step button confirmation.
    reply = await guarded(message, lambda s: _review_one(s, tg, content_id))
    if reply:
        await send(message, reply)


# ---------------------------------------------------------------- generation
def _generate(s: TelegramService, tg: int, job_type: str, topic: str) -> Reply:
    actor = s.require_linked_writer(tg)
    service = AIContentService(s.session)
    job = service.request(
        job_type, {"topic": topic, "language": "uz", "submit_for_review": True}, actor
    )
    if get_settings().ai_jobs_mode == "celery":
        from app.workers.tasks.ai import run_ai_job

        run_ai_job.delay(job.id)
        return Reply(
            f"⏳ AI vazifasi #{job.id} navbatga qo‘yildi. Tayyor bo‘lgach, tasdiq uchun "
            "xabar keladi."
        )
    outcome = service.execute(job.id)
    if outcome.job.status.value == "FAILED":
        return Reply(
            f"⚠️ Generatsiya muvaffaqiyatsiz: {esc(outcome.job.error or '')}\nHech narsa saqlanmadi."
        )
    content = outcome.content
    if content is None:
        return Reply("Natija saqlanmadi.")
    if content.status == ContentStatus.READY_FOR_REVIEW:
        return Reply(
            f"✅ #{content.id} tayyor va ko‘rib chiqishga yuborildi. Tasdiqlash tugmalari "
            "bilan xabar keladi (yoki /content)."
        )
    findings = ", ".join(
        f.code
        for f in (outcome.quality.findings if outcome.quality else [])
        if f.severity.value == "ERROR"
    )
    return Reply(
        f"📝 #{content.id} qoralama sifatida saqlandi — sifat tekshiruvidan o‘tmadi"
        + (f" ({esc(findings)})" if findings else "")
        + ". Panelda tahrirlang.",
        buttons=[[Button("Panelda ochish", url=s.panel_link(content))]],
    )


async def _generate_cmd(message: Message, command: CommandObject, job_type: str) -> None:
    tg = message.from_user.id  # type: ignore[union-attr]
    topic = (command.args or "").strip()[:MAX_TOPIC]
    if len(topic) < 3:
        await message.answer(f"Mavzuni yozing: /{command.command} Minimalist yotoqxona")
        return
    await message.answer("⏳ AI ishlamoqda… (lokal modelda 30–120 soniya)")
    reply = await guarded(message, lambda s: _generate(s, tg, job_type, topic))
    if reply:
        await send(message, reply)


@router.message(Command("content"))
async def cmd_content(message: Message, command: CommandObject) -> None:
    if command.args and command.args.strip():
        await _generate_cmd(message, command, JobType.POST)
        return
    tg = message.from_user.id  # type: ignore[union-attr]

    def pending(s: TelegramService) -> list[Reply]:
        replies = _pending(s, tg)
        s.session.commit()
        return replies

    replies = await guarded(message, pending)
    for reply in replies or []:
        await send(message, reply)


@router.message(Command("reels"))
async def cmd_reels(message: Message, command: CommandObject) -> None:
    await _generate_cmd(message, command, JobType.REELS)


@router.message(Command("story"))
async def cmd_story(message: Message, command: CommandObject) -> None:
    await _generate_cmd(message, command, JobType.STORY)


def _plan(s: TelegramService, tg: int) -> Reply:
    actor = s.require_linked_writer(tg)
    today = date.today()
    start = today + timedelta(days=(7 - today.weekday()) % 7 or 7)
    service = AIContentService(s.session)
    job = service.request(
        JobType.CONTENT_PLAN,
        {"start_date": start.isoformat(), "period": "week", "language": "uz"},
        actor,
    )
    if get_settings().ai_jobs_mode == "celery":
        from app.workers.tasks.ai import run_ai_job

        run_ai_job.delay(job.id)
        return Reply(f"⏳ Reja vazifasi #{job.id} navbatga qo‘yildi. Natija panelda: AI Studio.")
    outcome = service.execute(job.id)
    if outcome.job.status.value == "FAILED" or not outcome.result:
        return Reply(f"⚠️ Reja tuzilmadi: {esc(outcome.job.error or '')}")
    lines = [f"<b>Haftalik reja</b> ({start.isoformat()} dan)"]
    for item in outcome.result.get("items", []):
        lines.append(
            f"• {item['weekday'][:3]} {item['suggested_date']} — {item['format']}: "
            f"{esc(item['title'])}"
        )
    lines.append(f"\n<i>{esc(outcome.result.get('timing_basis', ''))}</i>")
    lines.append("Qoralama qilib saqlash: Panel → AI Studio → Kontent reja.")
    return Reply("\n".join(lines))


@router.message(Command("plan"))
async def cmd_plan(message: Message) -> None:
    tg = message.from_user.id  # type: ignore[union-attr]
    await message.answer("⏳ Reja tuzilmoqda…")
    reply = await guarded(message, lambda s: _plan(s, tg))
    if reply:
        await send(message, reply)


# ---------------------------------------------------------------- buttons
@router.callback_query(F.data.startswith(CALLBACK_PREFIX))
async def on_button(callback: CallbackQuery, state: FSMContext) -> None:
    tg = callback.from_user.id
    data = callback.data or ""
    try:
        reply = await with_service(lambda s: s.handle_callback(tg, data))
    except TelegramAccessError as exc:
        await callback.answer(exc.reason, show_alert=True)
        return
    await callback.answer()
    message = callback.message
    if reply.await_comment_token:
        await state.set_state(EditComment.waiting)
        await state.update_data(token=reply.await_comment_token)
    if message is None or not isinstance(message, Message):
        return
    if reply.edit_original:
        # Remove the buttons of the message that was tapped (its token is spent),
        # then answer with the result / confirmation and its own fresh buttons.
        try:
            await message.edit_reply_markup(reply_markup=None)
        except Exception:  # noqa: BLE001 - message may be too old to edit
            logger.debug("edit_reply_markup failed")
    await send(message, reply)


@router.message(EditComment.waiting, Command("skip"))
async def edit_skip(message: Message, state: FSMContext) -> None:
    await _submit_comment(message, state, None)


@router.message(EditComment.waiting, F.text)
async def edit_comment(message: Message, state: FSMContext) -> None:
    await _submit_comment(message, state, message.text)


async def _submit_comment(message: Message, state: FSMContext, comment: str | None) -> None:
    tg = message.from_user.id  # type: ignore[union-attr]
    token = (await state.get_data()).get("token")
    await state.clear()
    if not token:
        await message.answer("Tahrir so‘rovi topilmadi.")
        return
    reply = await guarded(message, lambda s: s.submit_edit_comment(tg, token, comment))
    if reply:
        await send(message, reply)


@router.message()
async def fallback(message: Message) -> None:
    await message.answer("Buyruqni tushunmadim. /help")
