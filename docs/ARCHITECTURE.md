# MUXRIDDIN AI INSTAGRAM MANAGER — Architecture (PHASE 0)

> Status: PHASE 0 — architecture. Kod hali yozilmagan.
> Asosiy prinsip: **AI = Assistant, USER = FINAL AUTHORITY.**

---

## 1. Project architecture

```
                    ┌───────────────────────────────┐
                    │        USER (yagona egasi)     │
                    └──────┬─────────────────┬──────┘
                           │                 │
                 Web Admin Panel        Telegram Bot
                 (Next.js, mobil)       (aiogram)
                           │ HTTPS/JWT       │ HTTPS (internal API key)
                           ▼                 ▼
                ┌──────────────────────────────────────┐
                │            FastAPI Backend            │
                │  api/ → services/ → repositories/     │
                │                                       │
                │  ┌─────────────┐   ┌───────────────┐  │
                │  │ Agent layer │   │ ApprovalService│ │  ◄── yagona "publish gate"
                │  │ (no publish)│   └──────┬────────┘  │
                │  └─────┬───────┘          │ approved  │
                │        │ providers        ▼           │
                │  AIProvider / ImageProvider / PublishService
                │  VideoProvider             │          │
                └────────┼───────────────────┼──────────┘
                         │                   │
          Ollama / OpenAI-compat /     Meta Graph API (official)
          Claude-compat                      │
                                       Instagram Business
                ┌───────────────┐
                │ Workers       │  Celery + Redis (prod) / APScheduler (dev)
                │ - AI jobs     │
                │ - scheduled   │
                │   publish     │
                │ - insights    │
                │   sync        │
                └───────────────┘
                PostgreSQL (prod) / SQLite (dev)
```

### Agent pipeline

```
Strategist → Content Planner → Content Creator → Visual/Media Generator
   → Quality Checker → Approval Queue → USER APPROVE → PublishService → Meta API
   → Instagram → Analytics sync → AI Analyst → (next week strategy)
```

Har bir agent — `agents/` ichidagi alohida klass, umumiy `BaseAgent` dan meros oladi
va **faqat ruxsat berilgan tool'larni** chaqira oladi (§4.2).

---

## 2. Folder structure

```
backend/
  app/
    main.py                 # FastAPI app factory
    api/v1/                 # routers: auth, content, approvals, calendar, media,
                            #          instagram, analytics, settings, logs, telegram
    core/                   # config (pydantic-settings), security, crypto, logging, errors
    models/                 # SQLAlchemy 2.0 ORM
    schemas/                # Pydantic v2 DTO
    repositories/           # DB access layer
    services/               # content, approval, publish, schedule, analytics, audit
    agents/                 # strategist, planner, creator, visual, quality, analyst
      permissions.py        # AgentTool enum + policy
    providers/
      ai/                   # base.py (AIProvider), ollama.py, openai_compat.py, anthropic_compat.py, mock.py
      image/                # base.py (ImageProvider), mock.py
      video/                # base.py (VideoProvider), mock.py
    integrations/
      meta/                 # oauth.py, client.py, publishing.py, insights.py, errors.py, capabilities.py
      telegram/             # bot.py, handlers/, keyboards.py
    workers/                # celery_app.py, tasks/
  alembic/                  # migrations
  pyproject.toml
frontend/                   # Next.js (App Router) + TypeScript + Tailwind
  app/(dashboard)/...       # overview, queue, calendar, media, instagram, analytics, ...
  lib/api.ts
  e2e/                      # Playwright
backend/tests/              # pytest (PHASE 1: backend testlari backend/ ichida)
docker/                     # Dockerfile.backend, Dockerfile.frontend, nginx/
docs/                       # ARCHITECTURE.md, META_API.md, SECURITY.md
scripts/                    # dev setup, seed, backup
README.md
.env.example
docker-compose.yml
```

---

## 3. Technology decisions

| Soha | Tanlov | Sabab |
|---|---|---|
| Backend | Python 3.12 + FastAPI | async, OpenAPI/Swagger avtomatik |
| ORM / migration | SQLAlchemy 2.0 + Alembic | PostgreSQL va SQLite bir xil kod |
| DB | PostgreSQL 16 (prod), SQLite (dev fallback) | `DATABASE_URL` orqali tanlanadi |
| Background jobs | **Celery + Redis** (prod), dev'da `CELERY_TASK_ALWAYS_EAGER` yoki APScheduler | retry, ETA (scheduled publish), idempotency |
| Frontend | Next.js 15, TypeScript, Tailwind | mobil browser uchun responsive |
| Telegram | aiogram 3 | async, inline keyboard, callback data |
| Auth | JWT access (qisqa) + refresh token httpOnly cookie, Argon2 parol hash | |
| Token encryption | `cryptography` Fernet (AES-128-CBC + HMAC), key `.env` da, key rotation (MultiFernet) | |
| LLM | `AIProvider` interface; default Ollama `qwen2.5:3b` (`AI_MODEL` env) | provider-agnostic |
| HTTP client | httpx (async) | Meta/Ollama uchun, test'da `respx` mock |
| Rate limit | slowapi (Redis backend) | |
| Tests | pytest, pytest-asyncio, respx; Playwright (frontend) | |
| Container | Docker Compose: api, worker, beat, bot, frontend, postgres, redis, (ollama) | |

Windows 11 dev: Docker Desktop (WSL2) yoki to‘g‘ridan-to‘g‘ri Python venv + SQLite + lokal Ollama.
16 GB RAM uchun `qwen2.5:3b` yetarli.

---

## 4. Security model

### 4.1 Asosiy qoidalar
- Instagram login/parol **hech qachon** so‘ralmaydi va saqlanmaydi. Faqat OAuth.
- Scraping, private API, browser automation — **taqiqlangan**.
- OAuth tokenlar DB'da faqat **shifrlangan** (`OAuthToken.ciphertext`), log'ga chiqmaydi.
- `.env` `.gitignore` da. Frontend'ga hech qanday secret berilmaydi. Brauzer faqat Next.js BFF proxy bilan ishlaydi: JWT httpOnly cookie'da saqlanadi, PHASE 4 dan boshlab (`docs/ADMIN_PANEL.md`).
- CORS: prod'da faqat `FRONTEND_ORIGIN`.
- OAuth `state` parametri (CSRF) — imzolangan, bir martalik, 10 daqiqa TTL.
- Rate limiting: auth va publish endpointlarda qattiq.
- Telegram: faqat `TELEGRAM_ALLOWED_USER_IDS` ro‘yxatidagi chat ID'lar; callback data imzolangan (HMAC) va bir martalik.
- AuditLog: append-only, har bir approve/reject/publish/token action.

### 4.2 AI agent permission model

```python
class AgentTool(StrEnum):
    READ_ANALYTICS, CREATE_CONTENT, EDIT_CONTENT,
    GENERATE_MEDIA, CREATE_SCHEDULE, REQUEST_APPROVAL
    PUBLISH_TO_INSTAGRAM   # AI uchun HAR DOIM False
```

Publish uchun **uch qatlamli himoya**:
1. **Agent qatlami:** agentlarga `PublishService` umuman inject qilinmaydi; `PUBLISH_TO_INSTAGRAM` policy'da `False` va config orqali ham yoqib bo‘lmaydi (hard-coded deny).
2. **Service qatlami:** `PublishService.publish(content_id)` faqat `Approval` yozuvi mavjud bo‘lsa ishlaydi:
   `approval.decision == APPROVED`, `approved_by` = haqiqiy `User` (actor_type=HUMAN),
   `approval.content_version == content.version` (approve'dan keyin kontent o‘zgarsa — approval bekor).
3. **API qatlami:** `POST /approvals/{id}/approve` faqat inson sessiyasi (JWT yoki tasdiqlangan Telegram user) orqali; agent/service token bu endpointni chaqira olmaydi.

### 4.3 Idempotency
- Har bir publish urinishi `idempotency_key = sha256(content_id + content_version)`.
- `ContentSchedule` / publish job'da unique constraint; Meta container ID va media ID saqlanadi.
- Retry: container yaratilgan, lekin publish noma'lum bo‘lsa — avval Meta'dan media mavjudligini tekshiradi, keyin qayta urinadi → duplicate post yo‘q.

---

## 5. Meta API integration plan

> PHASE 0 vaqtida `developers.facebook.com` ushbu muhitdan bloklangan, shuning uchun
> quyidagi ma'lumotlar qidiruv natijalari asosida. PHASE 7 da qayta tekshirildi;
> amaldagi oqim, endpoint'lar va manbalar: [`META_OAUTH.md`](META_OAUTH.md). Kodda versiya va scope nomlari hard-code
> qilinmaydi — `META_GRAPH_API_VERSION`, `META_SCOPES` env orqali.

### 5.1 Qaysi API?
Meta'da ikki yo‘l bor:

| | Instagram API with **Instagram Login** | Instagram API with **Facebook Login** |
|---|---|---|
| Facebook Page kerakmi | Yo‘q | Ha, IG akkaunt Page'ga bog‘langan bo‘lishi shart |
| Host | `graph.instagram.com` | `graph.facebook.com` |
| Scope'lar (joriy) | `instagram_business_basic`, `instagram_business_content_publish`, `instagram_business_manage_comments`, `instagram_business_manage_messages`, (insights — tekshiriladi) | `instagram_basic`, `instagram_content_publish`, `instagram_manage_insights`, `instagram_manage_comments`, `pages_show_list`, `pages_read_engagement`, `business_management` |

Eslatma: eski `business_*` scope qiymatlari 2025-01-27 da deprecated qilingan;
`instagram_business_*` nomlari ishlatiladi.

**Tavsiya:** default — **Instagram Login** (oddiyroq, Page shart emas).
Kod ikkala variantni `META_LOGIN_MODE=instagram|facebook` orqali qo‘llab-quvvatlaydi.

### 5.2 Graph API versiyasi
Qidiruv bo‘yicha joriy versiya **v26.0** (2026-07-29). Default `.env.example` da shu
qo‘yiladi, lekin config'dan o‘zgartiriladi.

### 5.3 OAuth flow
```
[Connect Instagram] → GET /api/v1/instagram/oauth/start   (state yaratiladi)
   → Meta authorize dialog
   → GET /api/v1/instagram/oauth/callback?code&state      (state tekshiriladi)
   → code → short-lived token → long-lived token (≈60 kun)
   → token debug/validation (scope'lar to‘liqmi)
   → Fernet bilan shifrlab OAuthToken'ga saqlash
   → /me → IG Business account discovery (id, username, account_type)
   → InstagramAccount yaratiladi
Worker: muddati tugashidan oldin long-lived token refresh; muvaffaqiyatsiz bo‘lsa — admin/Telegram ogohlantirish.
```

### 5.4 Publishing (2 bosqichli container modeli)
1. `POST /{ig-user-id}/media` — container (image_url / video_url, caption, media_type).
   - IMAGE: `image_url` (JPEG, ommaviy HTTPS URL)
   - REELS: `media_type=REELS`, `video_url`
   - CAROUSEL: har bir element `is_carousel_item=true`, so‘ng `media_type=CAROUSEL` + `children`
   - STORIES: `media_type=STORIES` — **faqat Business akkaunt** (Creator emas). PHASE 8 da tekshiriladi.
2. Video uchun `GET /{container-id}?fields=status_code` — `FINISHED` bo‘lguncha polling.
3. `POST /{ig-user-id}/media_publish` (`creation_id`).
4. Publish limiti (`content_publishing_limit`) oldindan tekshiriladi.

**Muhim:** Meta media'ni URL orqali yuklab oladi → media **ommaviy HTTPS URL'da** bo‘lishi kerak.
Lokal dev'da bu uchun tunnel (masalan cloudflared/ngrok) yoki S3-compatible storage kerak bo‘ladi — README'da yoziladi.

API qo‘llamaydigan narsalar (masalan, music/stickers, story link sticker va h.k.) **fake qilinmaydi**:
`integrations/meta/capabilities.py` da matritsa, UI'da `Not supported by current Meta API`.

### 5.5 Insights
`GET /{ig-media-id}/insights` va `GET /{ig-user-id}/insights` — faqat API qaytargan metrikalar
saqlanadi (`AnalyticsSnapshot.metrics` JSON). Qaytmagan metrika `null`, hech qachon taxmin qilinmaydi.
(Eslatma: Meta ba'zi metrikalarni, masalan `impressions`, yangi versiyalarda `views` bilan almashtirgan — PHASE 9 da tekshiriladi.)

### 5.6 Error mapping
`integrations/meta/errors.py`: Meta `error.code/subcode` → `MetaErrorKind`
(`OAUTH`, `PERMISSION_DENIED`, `TOKEN_EXPIRED`, `MEDIA_VALIDATION`, `RATE_LIMIT`, `PUBLISH_FAILED`, `UNKNOWN`)
+ o‘zbekcha user-friendly xabar.

### 5.7 Test
Barcha testlar `respx` bilan mock Meta API. `META_DRY_RUN=true` (test/dev default) — real publish yo‘q.

---

## 6. Data model (asosiy)

| Entity | Asosiy maydonlar |
|---|---|
| User | id, email, password_hash, role, telegram_user_id, is_active |
| InstagramAccount | id, user_id FK, ig_user_id (unique), username, account_type, login_mode, deleted_at |
| OAuthToken | id, instagram_account_id FK, ciphertext, scopes, expires_at, key_version |
| BrandProfile | id, name, voice, rules (JSON: taqiqlar), topics, languages, visual_style |
| Content | id, account_id FK, type (POST/CAROUSEL/REELS/STORY), status, version, topic, language, caption, hashtags, cta, hook, script, visual_prompt, deleted_at |
| ContentAsset | id, content_id FK, kind (image/video), storage_path, public_url, width, height, duration, order |
| ContentSchedule | id, content_id FK, scheduled_at, status, idempotency_key (unique), ig_container_id, ig_media_id, attempts |
| Approval | id, content_id FK, content_version, decision, decided_by (User FK), channel (web/telegram), comment |
| AnalyticsSnapshot | id, account_id/content_id, captured_at, metrics JSON |
| ContentPerformance | id, content_id FK, aggregated metrics, engagement_rate |
| AIJob | id, agent, input, output, status, provider, model, error |
| AuditLog | id, ts, actor_type (HUMAN/AGENT/SYSTEM), actor_id, action, content_id, status, error, meta |
| SystemSetting | key (PK), value JSON |

Har bir jadvalda `created_at`, `updated_at`; kerakli joylarda `deleted_at` (soft delete); status/FK/sana bo‘yicha indekslar.

### Content state machine

> PHASE 2 da yakuniy jadval: [`CONTENT_LIFECYCLE.md`](CONTENT_LIFECYCLE.md).
```
DRAFT → GENERATING → READY_FOR_REVIEW ─┬─ APPROVE ─→ APPROVED ─┬→ SCHEDULED → PUBLISHING
                                       │                       └→ PUBLISHING
                                       ├─ EDIT ───→ EDIT_REQUESTED → GENERATING → READY_FOR_REVIEW
                                       └─ REJECT ─→ REJECTED (terminal)
PUBLISHING → PUBLISHED | FAILED ;  FAILED → (retry, faqat mavjud approval bilan) PUBLISHING
```
O‘tishlar `services/content_state.py` da markaziy jadval orqali tekshiriladi; noto‘g‘ri o‘tish → 409.

---

## 7. Development phases

| Phase | Natija | Tekshiruv |
|---|---|---|
| 0 | Architecture (shu hujjat) | review |
| 1 | Repo skeleti, pyproject, Next.js init, .env.example, .gitignore, lint/test config, `/health` | pytest, ruff |
| 2 | Models + Alembic + repositories + seed | migration up/down, repo testlari |
| 3 | AIProvider (Ollama/mock), agents, brand voice guard, prompts | mock provider bilan unit testlar |
| 4 | Admin panel (auth, dashboard, queue, calendar) | Playwright smoke |
| 5 | Telegram bot (komandalar, inline approve/edit/reject) | handler unit testlar |
| 6 | Approval system + state machine + audit | CREATE→REVIEW→APPROVE→PUBLISH(mock) |
| 7 | Meta OAuth (rasmiy hujjatlardan qayta tekshirish) | OAuth mock testlar, state/CSRF |
| 8 | Instagram publishing (image, carousel, reels, story*) + idempotency + retry | mock Meta, duplicate testlari |
| 9 | Analytics sync + AI Analyst + weekly strategy | mock insights |
| 10 | Security hardening (rate limit, CORS, headers, secret scan) | security testlar |
| 11 | Docker Compose | `docker compose up` smoke |
| 12 | Production deployment (VPS, nginx, TLS, backup) | docs |

Har phase oxirida: test → fix → README yangilash → qisqa progress report.
