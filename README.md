# MUXRIDDIN AI INSTAGRAM MANAGER

Instagram Professional (Business) akkauntini AI agent yordamida boshqaruvchi tizim.
AI kontentni rejalashtiradi va yaratadi. **Instagram'ga nashr qilish faqat sizning
tasdig‘ingizdan keyin** amalga oshadi va faqat rasmiy Meta API orqali bo‘ladi.

> **Joriy holat: PHASE 2 — Database, repositories & content state machine.**
> Real Instagram OAuth va real publishing hali **yo‘q** (PHASE 7–8).
> Meta credentials kerak emas va so‘ralmaydi.

- Arxitektura: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Kontent hayot sikli, versiyalash va approval xavfsizligi: [`docs/CONTENT_LIFECYCLE.md`](docs/CONTENT_LIFECYCLE.md)
- API hujjatlari (backend ishlayotganda): http://localhost:8000/docs

---

## 1. Project overview

| Qism | Texnologiya | Papka |
|---|---|---|
| Backend API | Python 3.12, FastAPI, SQLAlchemy 2, Alembic | `backend/` |
| Background jobs | Celery + Redis | `backend/app/workers/` |
| Database | PostgreSQL 16 (SQLite fallback — dev) | — |
| Admin panel | Next.js 15, TypeScript, Tailwind CSS 4 | `frontend/` |
| AI | `AIProvider` interface, `OllamaProvider` (default `qwen2.5:3b`) | `backend/app/providers/ai/` |
| Meta | interface + mock (PHASE 1) | `backend/app/integrations/meta/` |
| Docker | Docker Compose (dev) | `docker-compose.yml`, `docker/` |

PHASE 1 da tayyor bo‘lganlar:

- `GET /health` va `GET /api/v1/health`: database va Redis holati.
- `/api/v1/...` API versioning.
- Global error handling: barcha xatolar bir xil JSON formatda, ichida `request_id` bor.
- Structured JSON logging. Parol va token kabi maydonlar logga chiqmaydi (redaction).
- Login (`POST /api/v1/auth/login`, JWT) va `GET /api/v1/auth/me`. Parollar Argon2 bilan hash qilinadi.
- `GET /api/v1/system/ai-status`: Ollama holati. Ollama o‘chiq bo‘lsa ham backend ishlashda davom etadi.
- 13 ta entity uchun SQLAlchemy modellari va boshlang‘ich Alembic migration.
- OAuth tokenlarni shifrlash uchun `TokenCipher` (Fernet, kalit rotatsiyasi bilan).
- AI agent permission'lari. `PUBLISH_TO_INSTAGRAM` umuman mavjud emas va hech qachon berilmaydi.
- Celery worker foundation (`system.ping` task).

PHASE 2 da qo'shilganlar:

- Repository qatlami (14 ta repository) va service qatlami. Oqim: Router → Service → Repository → DB.
- Kontent state machine. Ruxsat etilmagan o'tishlar HTTP 409 qaytaradi.
- Kontent versiyalash (`content_versions`): har bir o'zgarish yangi o'zgarmas versiya yaratadi.
- Approval aniq versiya va SHA-256 hash'ga bog'lanadi. Kontent tahrirlansa, eski approval bekor qilinadi.
- Approve faqat tasdiqlangan inson (OWNER/ADMIN) tomonidan qilinadi. AI va tizim jarayonlari approve qila olmaydi.
- Audit log: kim, nima, qachon, qaysi kontent va qaysi versiya. Sir ma'lumotlar yashiriladi.
- Idempotency: approve, schedule va kelajakdagi publish bir xil key bilan takrorlansa dublikat yaratilmaydi.
- `python -m app.cli seed`: xavfsiz development ma'lumotlari.
- Content API: `/api/v1/contents` (list, create, get, patch, submit-review, request-edit, approve, reject, history).
- **Publish endpoint yo'q.** U PHASE 8 da qo'shiladi.

## 2. Requirements (Windows 11)

| Dastur | Versiya | Majburiymi |
|---|---|---|
| Python | 3.12 (3.11+) | ha |
| Node.js | 22 LTS | ha |
| Git | oxirgi | ha |
| Ollama | oxirgi | AI uchun (backend usiz ham ishlaydi) |
| PostgreSQL | 16 | yo‘q — SQLite fallback bor yoki Docker |
| Redis | 7 | yo‘q — dev'da ixtiyoriy yoki Docker |
| Docker Desktop | oxirgi (WSL2) | Docker Compose uchun |

RAM: 16 GB yetarli (`qwen2.5:3b` modeli ~2 GB).

## 3. Installation (Windows PowerShell)

> Eslatma: Windows PowerShell 5.1 `&&` operatorini qo‘llamaydi. Shuning uchun
> quyidagi har bir buyruqni alohida qatorda bajaring.

### 3.1 Dasturlarni o‘rnatish (winget)

```powershell
winget install -e --id Python.Python.3.12
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Git.Git
winget install -e --id Ollama.Ollama
# ixtiyoriy:
winget install -e --id Docker.DockerDesktop
```

O‘rnatgandan keyin PowerShell'ni **yopib, qayta oching** (PATH yangilanadi) va tekshiring:

```powershell
python --version
node --version
npm --version
git --version
ollama --version
```

### 3.2 Repository va avtomatik sozlash

```powershell
git clone https://github.com/obidovmuhriddin0699-maker/new.git muxriddin-ai
cd muxriddin-ai
powershell -ExecutionPolicy Bypass -File .\scripts\dev-setup.ps1
```

`dev-setup.ps1` quyidagilarni bajaradi:

1. `backend\.venv` yaratadi va backend kutubxonalarini o‘rnatadi.
2. `.env.example` dan `.env` faylini yaratadi.
3. `JWT_SECRET_KEY` va `TOKEN_ENCRYPTION_KEYS` uchun **lokal** tasodifiy kalitlar generatsiya qiladi.
4. `alembic upgrade head` ni ishga tushiradi (default: SQLite, `backend\data\muxriddin.db`).
5. `npm install` qiladi va `frontend\.env.local` faylini yaratadi.

### 3.3 Qo‘lda sozlash (skriptsiz)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
cd ..
Copy-Item .env.example .env
```

Kalitlarni generatsiya qiling va `.env` ichiga qo‘ying:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"                                  # JWT_SECRET_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"     # TOKEN_ENCRYPTION_KEYS
```

> Agar `Activate.ps1` "running scripts is disabled" xatosini bersa:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## 4. Environment variables

To‘liq ro‘yxat va izohlar: [`.env.example`](.env.example). Muhimlari:

| O‘zgaruvchi | Vazifasi |
|---|---|
| `APP_ENV` | `development` / `test` / `production` |
| `DATABASE_URL` | bo‘sh bo‘lsa SQLite; PostgreSQL: `postgresql+psycopg://user:pass@host:5432/db` |
| `REDIS_URL` | Redis/Celery broker |
| `JWT_SECRET_KEY` | JWT imzolash kaliti (prod'da ≥32 belgi, majburiy) |
| `TOKEN_ENCRYPTION_KEYS` | Fernet kalit(lar)i; birinchisi bilan shifrlanadi, qolganlari faqat o‘qish (rotation) uchun |
| `CORS_ORIGINS` | ruxsat etilgan frontend manzillari, vergul bilan |
| `OLLAMA_BASE_URL`, `AI_MODEL` | AI provider (default `qwen2.5:3b`) |
| `META_LOGIN_MODE` | `instagram` (default) yoki `facebook` |
| `META_GRAPH_API_VERSION` | Graph API versiyasi (rasmiy changelog bilan tekshiring) |
| `META_DRY_RUN` | `true` bo‘lsa real akkauntga hech narsa yuborilmaydi |
| `NEXT_PUBLIC_API_URL` | frontend → backend manzili (**brauzerga ochiq**, secret qo‘ymang) |

Production'da `APP_ENV=production` bo‘lsa, backend quyidagi holatlarda **ishga tushmaydi**:
dev JWT kaliti ishlatilgan bo‘lsa, Fernet kaliti yo‘q bo‘lsa, `DATABASE_URL` PostgreSQL bo‘lmasa,
CORS'da `*` bo‘lsa yoki `DEBUG=true` bo‘lsa.

## 5. Local development

Uchta terminal oching (repository ildizidan):

**Terminal 1 — backend**

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.cli create-admin --email siz@example.com      # bir marta; parol so‘raladi (min 12)
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend**

```powershell
cd frontend
npm run dev
```

**Terminal 3 — Celery worker (ixtiyoriy, Redis kerak)**

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker -l info --pool=solo
```

> Windows'da Celery uchun `--pool=solo` majburiy.

Development ma'lumotlarini yuklash (admin, "Muxriddin Design" brendi, namuna draft):

```powershell
$env:SEED_ADMIN_PASSWORD = "kamida-12-belgili-parol"   # ixtiyoriy; bo'lmasa parol generatsiya qilinib bir marta ko'rsatiladi
python -m app.cli seed
Remove-Item Env:SEED_ADMIN_PASSWORD
```

Default admin email: `admin@example.com` (`SEED_ADMIN_EMAIL` yoki `--admin-email` bilan o'zgartiriladi).

Manzillar:

- Admin panel: http://localhost:3000. Bosh sahifada backend `/health` holati ko‘rinadi.
- API docs (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/health

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## 6. Ollama setup

```powershell
ollama pull qwen2.5:3b
ollama list
Invoke-RestMethod http://localhost:11434/api/tags
```

Ollama odatda Windows'da fon xizmati sifatida avtomatik ishga tushadi. Agar ishlamasa: `ollama serve`.

Modelni almashtirish uchun `.env` ga `AI_MODEL=boshqa-model` yozing (avval `ollama pull boshqa-model`).

Holatni tekshirish (login token bilan):

```powershell
$body = @{ email = "siz@example.com"; password = "PAROLINGIZ" } | ConvertTo-Json
$token = (Invoke-RestMethod -Method Post http://localhost:8000/api/v1/auth/login -ContentType "application/json" -Body $body).access_token
Invoke-RestMethod http://localhost:8000/api/v1/system/ai-status -Headers @{ Authorization = "Bearer $token" }
```

Ollama o‘chiq bo‘lsa, javob `available: false` va `error_code: "ai_provider_unavailable"` bo‘ladi. Backend crash bo‘lmaydi.

## 7. Database setup

**Variant A — SQLite (default, hech narsa o‘rnatish shart emas).** `DATABASE_URL` bo‘sh qoldiriladi.

**Variant B — PostgreSQL Docker orqali (tavsiya):**

```powershell
docker compose up -d postgres redis
```

`.env` ga yozing:

```
DATABASE_URL=postgresql+psycopg://muxriddin:muxriddin_dev@localhost:5432/muxriddin
```

**Variant C — PostgreSQL'ni Windows'ga o‘rnatish:**

```powershell
winget install -e --id PostgreSQL.PostgreSQL.16
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE USER muxriddin WITH PASSWORD 'muxriddin_dev';"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE DATABASE muxriddin OWNER muxriddin;"
```

**Migration buyruqlari** (`backend` papkasida, venv aktiv):

```powershell
alembic upgrade head          # eng oxirgi sxemaga o‘tkazish
alembic current               # joriy revision
alembic downgrade -1          # bir qadam orqaga
alembic revision --autogenerate -m "izoh"   # model o‘zgarganda yangi migration
alembic check                 # modellar va migrationlar mosligini tekshirish
```

**Redis (Windows):** Redis rasmiy ravishda Windows'ni qo‘llamaydi. Docker
(`docker compose up -d redis`) yoki WSL2 ishlating. Development'da Redis bo‘lmasa,
backend ishlaydi va `/health` da `redis.ok=false` ko‘rinadi.

## 8. Telegram setup

PHASE 5 da qo‘shiladi.

## 9–13. Meta Developer setup, Instagram Business connection, OAuth, permissions, App Review

PHASE 7–8 da rasmiy Meta hujjatlari asosida yoziladi. Hozirgi reja
[`docs/ARCHITECTURE.md` §5](docs/ARCHITECTURE.md) da. Default autentifikatsiya strategiyasi:
**Instagram API with Instagram Login**.

PHASE 1 da Meta App ID, App Secret yoki access token **kerak emas** va ularni
repository'ga yozmang.

## 14. Testing

**Backend** (`backend` papkasida, venv aktiv):

```powershell
python -m pytest -q
ruff check .
ruff format --check .
```

PostgreSQL migration testini ham ishga tushirish uchun bo‘sh test bazasi kerak:

```powershell
$env:TEST_POSTGRES_URL = "postgresql+psycopg://muxriddin:muxriddin_dev@localhost:5432/muxriddin_test"
python -m pytest -q
Remove-Item Env:TEST_POSTGRES_URL
```

Butun test to'plamini PostgreSQL'da ishga tushirish uchun (parallel approve testi ham faqat PostgreSQL'da ishlaydi):

```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg://muxriddin:muxriddin_dev@localhost:5432/muxriddin_suite"
python -m pytest -q
Remove-Item Env:TEST_DATABASE_URL
```

> `muxriddin_test` va `muxriddin_suite` bazalari **bo'sh** bo'lishi kerak: testlar ulardagi jadvallarni o'chirib, qayta yaratadi.

Testlar hech qachon real Meta, real Ollama yoki real Redis'ga murojaat qilmaydi
(`respx` mock, `META_DRY_RUN=true`).

**Frontend** (`frontend` papkasida):

```powershell
npm run lint
npm run typecheck
npm run build
```

**E2E (Playwright)**: backend va frontendni o‘zi ishga tushiradi va panel `/health` ni ko‘ra olishini tekshiradi:

```powershell
npx playwright install chromium        # bir marta
npm run build
$env:BACKEND_PYTHON = "..\backend\.venv\Scripts\python.exe"
npm run test:e2e
```

## 15. Docker Compose (local development)

```powershell
Copy-Item .env.example .env        # agar hali yo‘q bo‘lsa
docker compose up -d --build
docker compose ps
docker compose logs -f backend
```

| Servis | Manzil |
|---|---|
| frontend | http://localhost:3000 |
| backend | http://localhost:8000 (ishga tushishda `alembic upgrade head` avtomatik bajariladi) |
| worker | Celery worker |
| postgres | localhost:5432 |
| redis | localhost:6379 |

Portlar faqat `127.0.0.1` ga ochiladi.

**Ollama Docker ichida emas.** Ollama Windows host'da ishlaydi va backend container unga
`http://host.docker.internal:11434` orqali ulanadi. Boshqa manzil kerak bo‘lsa, `.env` da
`DOCKER_OLLAMA_BASE_URL` ni o‘zgartiring.

Admin yaratish:

```powershell
docker compose exec backend python -m app.cli create-admin --email siz@example.com
# yoki namuna ma'lumotlar bilan:
docker compose exec -e SEED_ADMIN_PASSWORD=kamida-12-belgili-parol backend python -m app.cli seed
```

To‘xtatish: `docker compose down` (ma'lumotlar bilan birga o‘chirish: `docker compose down -v`).

## 16. Security

- Instagram login/paroli **hech qachon** so‘ralmaydi va saqlanmaydi. Ulanish faqat OAuth orqali (PHASE 7).
- OAuth tokenlar faqat Fernet bilan shifrlangan holda saqlanadi (`oauth_tokens.token_ciphertext`). Kalit faqat `.env` dan olinadi.
- `.env` va `.env.*` `.gitignore` da (`.env.example` bundan mustasno). Buni test ham tekshiradi.
- Frontendga faqat `NEXT_PUBLIC_API_URL` beriladi. Secret'lar brauzerga chiqmaydi.
- CORS faqat `CORS_ORIGINS` ro‘yxatidagi manzillarga ochiq. Production'da `*` taqiqlangan.
- 500 xatolarda ichki tafsilotlar foydalanuvchiga ko‘rsatilmaydi, ular faqat logga yoziladi.
- AI agentlar uchun `PUBLISH_TO_INSTAGRAM` / `APPROVE_CONTENT` ruxsatlarini berib bo‘lmaydi (`ForbiddenAgentPermissionError`).
- Publish endpoint **yo'q**. Approve endpoint faqat inson sessiyasi (JWT `actor=human`) uchun ochiq, OWNER/ADMIN rolini talab qiladi va publish qilmaydi.
- Approval kontentning aniq versiyasi va hash'iga bog'langan. Approve'dan keyin kontent o'zgarsa, approval kuchini yo'qotadi. Batafsil: [`docs/CONTENT_LIFECYCLE.md`](docs/CONTENT_LIFECYCLE.md).
- Audit log faqat qo'shiladi, o'zgartirilmaydi. Unda parol, token va kalitlar saqlanmaydi.

## 17. Troubleshooting

| Muammo | Yechim |
|---|---|
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `python` topilmadi / Microsoft Store ochiladi | Settings → Apps → Advanced app settings → App execution aliases → `python.exe` ni o‘chiring, Python'ni qayta o‘rnating |
| `ai-status` → `ai_provider_unavailable` | `ollama serve` ni ishga tushiring; Docker'da — Ollama host'da ishlayotganini tekshiring |
| `ai_model_not_found` | `ollama pull qwen2.5:3b` |
| `/health` → `redis.ok=false` | Redis ishga tushmagan; dev uchun muammo emas (`docker compose up -d redis`) |
| `/health` → 503 `degraded` | Database'ga ulanib bo‘lmadi — `DATABASE_URL` va PostgreSQL holatini tekshiring |
| Frontend "Backend bilan aloqa yo‘q" | Backend 8000-portda ishlayaptimi? `CORS_ORIGINS` da `http://localhost:3000` bormi? |
| Port band (5432/6379/8000/3000) | lokal PostgreSQL/Redis xizmatini to‘xtating yoki `docker-compose.yml` dagi portni o‘zgartiring |
| Celery Windows'da osilib qoladi | `--pool=solo` bilan ishga tushiring |
| `Invalid production configuration` | §4 dagi production talablarini bajaring |
| `409 version_mismatch` | Kontent siz ko'rgandan keyin o'zgargan. Qayta yuklang va `expected_version` ni yangilang |
| `409 invalid_state_transition` | Bu holatdan bu amalga o'tib bo'lmaydi (jadval: `docs/CONTENT_LIFECYCLE.md`) |
| `403 approval_forbidden` | Approve uchun OWNER/ADMIN roli kerak. AI yoki tizim approve qila olmaydi |
| Migration `91ed60cfe649 requires 'approvals' to be empty` | Eski versiyasiz approval qatorlari bor; ularni xavfsiz ko'chirib bo'lmaydi |

## Development phases

| Phase | Holat |
|---|---|
| 0 — Architecture | ✅ |
| 1 — Project foundation | ✅ |
| 2 — Database (repositories, seed, state machine) | ✅ |
| 3 — AI Content Creator | ⏳ |
| 4 — Admin Panel | ⏳ |
| 5 — Telegram Bot | ⏳ |
| 6 — Approval System | ⏳ |
| 7 — Meta OAuth | ⏳ |
| 8 — Instagram Publishing | ⏳ |
| 9 — Analytics | ⏳ |
| 10 — Security hardening | ⏳ |
| 11 — Docker (production images) | ⏳ |
| 12 — Production deployment | ⏳ |
