# Telegram bot (PHASE 5)

aiogram 3, long polling (works on a laptop behind NAT; webhook can come with PHASE 12).

```
Telegram ──► aiogram (AccessMiddleware → handlers) ──► TelegramService ──► ApprovalService / AIContentService
                     ▲                                        │
                     └──── notifier loop (every 15 s) ◄───────┘  reads CONTENT_SUBMITTED_FOR_REVIEW
                                                               from the audit log (cursor in system_settings)
```

## Commands

| Command | What it does |
|---|---|
| `/start` / `/start KOD` | Welcome; with a code from the panel it links your Telegram account |
| `/content` | Up to 5 items waiting for review, each with buttons |
| `/content mavzu` | Generate a single-image post draft |
| `/reels mavzu`, `/story mavzu` | Generate a Reels script / Story concept |
| `/plan` | Weekly plan from next Monday (shown only; save drafts in AI Studio) |
| `/approve ID`, `/reject ID` | Show that item with buttons — text commands never decide by themselves |
| `/status`, `/analytics`, `/settings`, `/help` | Counters, real analytics only, account info, help |

Buttons on a preview: **✅ TASDIQLASH**, **✏️ TAHRIR**, **❌ RAD ETISH**, **Panelda ochish**.

* Approve / reject ask for a second confirmation ("Ha, tasdiqlayman").
* Edit asks for a comment (next message, or `/skip`) and records an edit request.
* Generated content is sent for review only if the quality check passed; approvers are
  then notified by the notifier, so nobody gets duplicates.

## Security

1. **Two gates for every update.** The Telegram ID must be in `TELEGRAM_ALLOWED_USER_IDS`,
   and the account must be linked to an active panel user. Group chats are ignored.
   Strangers get a short refusal; the attempt is audited at most once per 10 minutes per ID.
2. **Linking.** The panel issues a one-time code (`XXXX-XXXX`, 10 min, stored hashed, the
   newest code invalidates older ones). One Telegram account maps to one panel user.
3. **Buttons.** `callback_data` is `mx:<random token>`. The token is stored hashed and bound
   to the action, the content id, the **content version** and the Telegram user it was issued
   to. It works once and expires (72 h; confirmation buttons 10 min). A button for v1 can
   never approve v2, and another person cannot press your button.
4. **Same rules as the panel.** Decisions call `ApprovalService` as
   `HumanActor(channel=TELEGRAM)`: active OWNER/ADMIN only, exact version and hash, audited
   (denied attempts too). Approval never publishes.
5. **Output safety.** All content is HTML-escaped and length-limited before sending.
6. **Secrets.** The bot token is a `SecretStr`; aiogram logging is limited to WARNING so the
   token (part of API URLs) is not logged. The bot refuses to start without an allowlist.

## Setup (Windows PowerShell)

1. Create a bot: in Telegram open **@BotFather** → `/newbot` → copy the token.
2. Find your numeric Telegram ID: open **@userinfobot** → `/start`.
3. In `.env`:

   ```
   TELEGRAM_ENABLED=true
   TELEGRAM_BOT_TOKEN=123456:ABC...        # keep secret
   TELEGRAM_BOT_USERNAME=your_bot_name
   TELEGRAM_ALLOWED_USER_IDS=123456789
   PANEL_PUBLIC_URL=http://localhost:3000
   ```

4. Start the bot:

   ```powershell
   cd backend
   .\.venv\Scripts\Activate.ps1
   python -m app.integrations.telegram
   ```

   or with Docker: `docker compose --profile telegram up -d`.
5. Panel → **Telegram** → "Bog‘lash kodini olish" → send `/start XXXX-XXXX` to the bot.

## Tests

`tests/test_telegram_service.py` (linking, tokens, two-step decisions, version binding,
roles, denials audited, HTML escaping, notifications), `tests/test_telegram_bot.py`
(aiogram handlers with real aiogram types and mocked Telegram API, middleware, FSM edit
flow, generation commands, notifier, startup guards), `tests/test_telegram_api.py`.
No test talks to Telegram.

## Limitations

* Not yet tested against the real Telegram API (unreachable from the build environment).
* FSM state (waiting for an edit comment) is in memory: a bot restart drops it; the user
  simply presses ✏️ again.
* Long polling only; one bot process per token.
* In `AI_JOBS_MODE=sync` a generation command blocks that handler for the model's runtime
  (other users are still served — work runs in a thread).
