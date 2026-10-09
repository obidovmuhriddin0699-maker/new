# MUXRIDDIN AI INSTAGRAM MANAGER

Instagram Professional (Business) akkauntini AI agent yordamida boshqaruvchi tizim.
AI kontentni rejalashtiradi va yaratadi. **Instagram'ga nashr qilish faqat sizning
tasdig‘ingizdan keyin** amalga oshadi va faqat rasmiy Meta API orqali bo‘ladi.

> **Joriy holat: PHASE 7 — Meta OAuth (Instagram Login).**
> Instagram akkauntni rasmiy Meta OAuth orqali ulash, tokenni shifrlab saqlash va avtomatik yangilash tayyor.
> Real publishing hali **yo‘q** (PHASE 8). `META_DRY_RUN=true` default.

- Arxitektura: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Kontent hayot sikli, versiyalash va approval xavfsizligi: [`docs/CONTENT_LIFECYCLE.md`](docs/CONTENT_LIFECYCLE.md)
- AI pipeline (agentlar, schemalar, sifat, joblar, xatolar): [`docs/AI_PIPELINE.md`](docs/AI_PIPELINE.md)
- Admin panel (sahifalar, xavfsizlik, approval UI): [`docs/ADMIN_PANEL.md`](docs/ADMIN_PANEL.md)
- Telegram bot (buyruqlar, xavfsizlik, sozlash): [`docs/TELEGRAM_BOT.md`](docs/TELEGRAM_BOT.md)
- Meta OAuth (oqim, xavfsizlik, token hayoti, callback'lar): [`docs/META_OAUTH.md`](docs/META_OAUTH.md)
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

PHASE 3 da qo'shilganlar:

- AI pipeline. U to'rt qismdan iborat:
  - **Strategist**: strategiya va kontent yo'nalishlari.
  - **Planner**: g'oyalar va haftalik/oylik reja.
  - **Creator**: post, karusel, Reels ssenariysi, Story va hashtag'lar.
  - **Quality Evaluator**: qoidalarga asoslangan sifat tekshiruvi.
- AI chiqishi Pydantic schemalari bilan tekshiriladi. Noto'g'ri JSON kelsa, bitta tuzatish urinishi qilinadi. Bu ham muvaffaqiyatsiz bo'lsa, job FAILED bo'ladi va hech narsa uydirilmaydi.
- AI yaratgan kontent faqat `DRAFT` holatida saqlanadi. Siz so'rasangiz va sifat tekshiruvidan o'tsa, `READY_FOR_REVIEW` ga o'tadi. **Hech qachon avtomatik `APPROVED` bo'lmaydi.**
- `AIJob` ishlash rejimlari: `sync` (default) yoki `celery` (HTTP 202 javob, keyin holatni so'rash kerak).
- Rasm va video provider'lari `not_configured` holatida. Ular soxta media yaratmaydi.
- `/api/v1/ai/*` endpoint'lari (to'liq ro'yxat [`docs/AI_PIPELINE.md`](docs/AI_PIPELINE.md) da).

PHASE 4 da qo'shilganlar (admin panel):

- Sahifalar:
  - Umumiy ko'rinish (Overview);
  - Kontent navbati va approval UI;
  - AI Studio;
  - Kalendar: kun, hafta va oy ko'rinishi;
  - Media kutubxona, Instagram, Analitika, AI sozlamalari, Brend sozlamalari, Telegram, Tizim loglari, Sozlamalar.
- Approval UI tugmalari: **Tahrirlash, Qayta yaratish, Rad etish, Tasdiqlash**.
  - "Tasdiqlash va nashr qilish" tugmasi PHASE 8 gacha o'chirilgan.
  - Tasdiq kontentning aniq versiyasiga bog'lanadi.
- Xavfsiz sessiya:
  - JWT faqat httpOnly cookie'da saqlanadi, brauzer JavaScript'i uni o'qiy olmaydi.
  - Next.js proxy (BFF) so'rovlarni backend'ga yuboradi va CSRF himoyasini bajaradi.
- Mobil qurilmadan foydalanish mumkin. Telefondan faqat frontend portini ochish kifoya.

PHASE 5 da qo'shilganlar (Telegram bot):

- Buyruqlar: `/start`, `/content`, `/plan`, `/reels`, `/story`, `/status`, `/approve`, `/reject`, `/analytics`, `/settings`.
- Kontent preview'si inline tugmalar bilan keladi: **TASDIQLASH / TAHRIR / RAD ETISH**.
  - Tasdiqlash va rad etish ikki bosqichli.
  - Tugmalar bir martalik, kontentning aniq versiyasiga va aniq Telegram foydalanuvchisiga bog'langan.
- Botdan foydalanish uchun ikki shart bor:
  - Telegram ID `TELEGRAM_ALLOWED_USER_IDS` ro'yxatida bo'lishi;
  - hisob panel orqali bir martalik kod bilan bog'langan bo'lishi.
- Yangi kontent ko'rib chiqishga tushganda tasdiqlovchilarga avtomatik xabar yuboriladi.

PHASE 6 da qo'shilganlar (approval tizimi):

- **Nashrga tayyorlik tekshiruvi (preflight).** Status, tasdiq (sababi bilan), sifat, format, media, Instagram akkaunt va publisher holati tekshiriladi. PHASE 8 da publish servisi aynan shu tekshiruvdan foydalanadi.
- **Versiyalar farqi (diff).** Tasdiqlovchi oxirgi tasdiqlangan versiyaga nisbatan nima o'zgarganini satrma-satr ko'radi.
- **Tasdiqni bekor qilish (revoke).**
- **"Tahrir → AI qayta ishlaydi → yana navbatga" sikli.** Panelda ham, Telegram'da ham ishlaydi (🤖 tugmasi).
- **Ixtiyoriy siyosatlar:** "to'rt ko'z" qoidasi va tasdiq muddati.
- **"Tasdiqlar" sahifasi:** kutayotganlar navbati (eng uzoq kutayotgani birinchi) va qarorlar tarixi (kanal va qaror bo'yicha filtr bilan).
- **Telegram eslatmalari:** uzoq kutib qolgan kontent haqida.

PHASE 7 da qo'shilganlar (Meta OAuth, Instagram Login):

- **Rasmiy OAuth oqimi:** panel → Instagram'ning rasmiy ruxsat oynasi → `/instagram/callback`. Login/parol so'ralmaydi.
- **Token:** qisqa muddatli token uzoq muddatliga (60 kun) almashtiriladi va **faqat shifrlangan** holda saqlanadi.
- **Avtomatik yangilash:** Celery beat har 6 soatda tekshiradi. Qo'lda yangilash uchun tugma va CLI bor.
- **Xavfsizlik:** bir martalik `state` (foydalanuvchiga bog'langan, 10 daqiqa amal qiladi). Majburiy ruxsatlar tekshiriladi. Ulanish, yangilash, uzish va xatolar audit'ga yoziladi.
- **Meta callback'lari:** deauthorize va data deletion (`signed_request` HMAC bilan tekshiriladi) hamda deletion status sahifasi.
- **Xatolar:** Meta xato kodlari tasniflanadi (token muddati, ruxsat, limit, tarmoq) va o'zbekcha tushunarli xabar sifatida ko'rsatiladi.
- **Instagram sahifasi:** holat, ruxsatlar, token muddati, ogohlantirishlar, "qayta ulash kerak" belgisi.

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
| `AI_PROVIDER` | `ollama` (real) yoki `mock` (faqat test/demo; production'da taqiqlangan) |
| `OLLAMA_BASE_URL`, `AI_MODEL` | AI provider (default `qwen2.5:3b`) |
| `AI_TIMEOUT_SECONDS`, `AI_MAX_OUTPUT_TOKENS`, `AI_STRUCTURED_MAX_ATTEMPTS` | Generatsiya chegaralari |
| `AI_JOBS_MODE` | `sync` (so'rov ichida) yoki `celery` (fonda, worker kerak) |
| `AI_MAX_ACTIVE_JOBS_PER_USER` | Bir vaqtda ishlayotgan AI job'lar soni chegarasi |
| `IMAGE_PROVIDER`, `VIDEO_PROVIDER` | `none` (default, `not_configured`) yoki `mock` (faqat placeholder) |
| `META_APP_ID`, `META_APP_SECRET` | Meta App Dashboard'dagi **Instagram app ID / secret** (§9). Secret faqat serverda |
| `META_REDIRECT_URI` | OAuth qaytish manzili: `https://<panel>/instagram/callback` (dashboard'dagi bilan aynan bir xil) |
| `META_SCOPES`, `META_REQUIRED_SCOPES` | So‘raladigan va majburiy ruxsatlar (§12) |
| `META_TOKEN_REFRESH_WINDOW_DAYS` | Token tugashiga shuncha kun qolganda avtomatik yangilanadi (default 15) |
| `PANEL_PUBLIC_URL` | Panelning tashqi manzili (bot havolalari va Meta data-deletion status URL) |
| `META_LOGIN_MODE` | `instagram` (default, amalga oshirilgan) yoki `facebook` (hali yo‘q) |
| `META_GRAPH_API_VERSION` | Graph API versiyasi (rasmiy changelog bilan tekshiring) |
| `META_DRY_RUN` | `true` bo‘lsa real akkauntga hech narsa yuborilmaydi |
| `BACKEND_URL` | Next.js server tomoni backend'ga shu manzil orqali ulanadi (brauzerga yuborilmaydi) |
| `APPROVAL_MAX_AGE_HOURS` | Tasdiq amal qilish muddati (0 = cheksiz) |
| `APPROVAL_REQUIRE_DIFFERENT_APPROVER` | "To'rt ko'z": versiyani yozgan odam uni o'zi tasdiqlay olmaydi |
| `APPROVAL_REMINDER_HOURS` | Shuncha soatdan ko'p kutgan kontent haqida Telegram eslatmasi (0 = o'chiq) |
| `SESSION_COOKIE_SECURE` | `auto` (HTTPS bo'lsa Secure), `true` yoki `false` |

Production'da `APP_ENV=production` bo‘lsa, backend quyidagi holatlarda **ishga tushmaydi**:
dev JWT kaliti ishlatilgan bo‘lsa, Fernet kaliti yo‘q bo‘lsa, `DATABASE_URL` PostgreSQL bo‘lmasa,
CORS'da `*` bo‘lsa, `DEBUG=true` bo‘lsa, `META_APP_ID` bor-u `META_APP_SECRET` yo‘q bo‘lsa yoki
`META_REDIRECT_URI` https bo‘lmasa.

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
Copy-Item .env.example .env.local      # bir marta (BACKEND_URL=http://localhost:8000)
npm run dev
```

**Telefondan kirish (bir Wi-Fi tarmog'ida).** Telefon faqat frontend'ga ulanadi, backend kompyuterda localhost'da qoladi:

```powershell
cd frontend
npm run dev -- -H 0.0.0.0
ipconfig                                # "IPv4 Address" ni toping, masalan 192.168.1.20
# Administrator PowerShell'da (bir marta) 3000-portni faqat Private tarmoq uchun oching:
New-NetFirewallRule -DisplayName "Muxriddin panel" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow -Profile Private
```

Telefon brauzerida `http://192.168.1.20:3000` manzilini oching. HTTP orqali ishlaganda cookie `Secure` belgisiz bo'ladi (`SESSION_COOKIE_SECURE=auto`). Internetga chiqarishdan oldin HTTPS majburiy (PHASE 12).

**Terminal 3 — Celery worker (ixtiyoriy, Redis kerak)**

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker -l info --pool=solo
```

> Windows'da Celery uchun `--pool=solo` majburiy.

Instagram tokenlarini avtomatik yangilash uchun **Celery beat** ham kerak (alohida terminalda):

```powershell
celery -A app.workers.celery_app beat -l info --schedule $env:TEMP\celerybeat-schedule
```

Docker Compose'da beat `worker` konteyneri ichida (`-B`) ishlaydi.

Development ma'lumotlarini yuklash (admin, "Muxriddin Design" brendi, namuna draft):

```powershell
$env:SEED_ADMIN_PASSWORD = "kamida-12-belgili-parol"   # ixtiyoriy; bo'lmasa parol generatsiya qilinib bir marta ko'rsatiladi
python -m app.cli seed
Remove-Item Env:SEED_ADMIN_PASSWORD
```

Default admin email: `admin@example.com` (`SEED_ADMIN_EMAIL` yoki `--admin-email` bilan o'zgartiriladi).

Manzillar:

- Admin panel: http://localhost:3000. `seed` yoki `create-admin` bilan yaratilgan email va parol orqali kiring.
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

To'liq pipeline holati (provider, job rejimi, media provider'lar):

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/ai/status -Headers @{ Authorization = "Bearer $token" }
```

Birinchi generatsiya (natija `DRAFT` bo'lib saqlanadi):

```powershell
$req = @{ topic = "Minimalist yotoqxona"; slides = 5 } | ConvertTo-Json
Invoke-RestMethod -Method Post http://localhost:8000/api/v1/ai/generate-carousel -Headers @{ Authorization = "Bearer $token" } -ContentType "application/json" -Body $req
```

> CPU'da `qwen2.5:3b` bitta javob uchun 30–120 soniya ishlashi mumkin. Agar so'rov uzoq kutib qolsa, `.env` da `AI_JOBS_MODE=celery` qiling va Celery worker'ni ishga tushiring (5-bo'lim).
> Ollama'siz sinab ko'rish uchun `.env` ga `AI_PROVIDER=mock` yozing. Bu deterministik test matni qaytaradi va metadata'da `provider: mock` deb belgilanadi.

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

1. Telegram'da **@BotFather** → `/newbot` buyrug'ini yuboring va berilgan tokenni nusxalang.
2. O'z Telegram ID raqamingizni bilish uchun **@userinfobot** → `/start`.
3. `.env` ga yozing (token — maxfiy, git'ga tushmaydi):

```
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_BOT_USERNAME=sizning_botingiz
TELEGRAM_ALLOWED_USER_IDS=123456789
PANEL_PUBLIC_URL=http://localhost:3000
```

4. Botni ishga tushiring (alohida terminalda):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.integrations.telegram
```

Docker orqali: `docker compose --profile telegram up -d`.

5. Panel → **Telegram** → "Bog'lash kodini olish" tugmasini bosing va botga `/start XXXX-XXXX` yuboring.

Batafsil: [`docs/TELEGRAM_BOT.md`](docs/TELEGRAM_BOT.md).

## 9. Meta Developer setup

Default va yagona amalga oshirilgan usul: **Instagram API with Instagram Login**
(Facebook Page shart emas). Batafsil oqim va manbalar: [`docs/META_OAUTH.md`](docs/META_OAUTH.md).

> Meta Dashboard'dagi menyu nomlari vaqti-vaqti bilan o‘zgaradi. Quyidagi qadamlar
> 2026-yil oktyabr holatiga ko‘ra. Farq bo‘lsa, rasmiy hujjat ustun:
> https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/get-started

1. https://developers.facebook.com → **My Apps** → **Create App**. Use case: **Manage messaging & content on Instagram** (yoki "Other" → **Business** turi).
2. App ichida **Instagram** mahsuloti → **API setup with Instagram login**.
3. **Business login settings** bo‘limida:
   * **OAuth redirect URIs**: `https://<panel-manzili>/instagram/callback`
   * **Deauthorize callback URL**: `https://<panel-manzili>/api/meta/deauthorize`
   * **Data deletion request URL**: `https://<panel-manzili>/api/meta/data-deletion`
4. Shu sahifadagi **Instagram app ID** va **Instagram app secret** ni oling.
   Facebook App ID **emas**, Instagram app ID kerak.
5. **App roles → Roles** (yoki Instagram testers) bo‘limida o‘z Instagram akkauntingizni qo‘shing va Instagram ilovasida taklifni qabul qiling
   (Settings → Website permissions / Apps and websites → Tester invites).

`.env` (backend), PowerShell'da:

```powershell
# Fernet kalit — tokenlar faqat shifrlangan saqlanadi (bir marta yarating, yo'qotmang!)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

```dotenv
TOKEN_ENCRYPTION_KEYS=<yuqoridagi kalit>
META_APP_ID=<Instagram app ID>
META_APP_SECRET=<Instagram app secret>
META_REDIRECT_URI=https://<panel-manzili>/instagram/callback
PANEL_PUBLIC_URL=https://<panel-manzili>
```

`.env` git'ga tushmaydi. App secret brauzerga hech qachon yuborilmaydi.

## 10. Instagram Business connection

1. Instagram ilovasida akkauntni **professional** qiling: Settings → Account type and tools →
   **Switch to professional account** → **Business** (tavsiya) yoki **Creator**.
   Shaxsiy akkaunt bu API bilan ishlamaydi.
2. Panel → **Instagram** → **Instagram’ni ulash**. Siz Instagram'ning **rasmiy** oynasiga o‘tasiz
   (login/parol faqat o‘sha yerda, bizning tizimga kiritilmaydi va saqlanmaydi).
3. Ruxsatlarni tasdiqlang. Panel `/instagram/callback` sahifasiga qaytadi va natijani ko‘rsatadi.
4. Instagram sahifasida: username, akkaunt turi, berilgan ruxsatlar, token muddati (60 kun).
   Token tugashiga 15 kun qolganda Celery beat uni avtomatik yangilaydi (har 6 soatda tekshiradi).
   Qo‘lda yangilash: **Tokenni yangilash** yoki:

```powershell
cd backend; .\.venv\Scripts\Activate.ps1
python -m app.cli refresh-instagram-tokens
```

**Uzish** tokenlarni bekor qiladi va akkauntni o‘chiradi (soft delete). Instagram tomonida
ham ruxsatni olib tashlash: Instagram → Settings → Website permissions → Apps and websites.

Creator akkauntlar uchun ogohlantirish chiqadi: Stories'ni API orqali nashr qilish faqat Business akkauntlarda ishlaydi.

## 11. OAuth configuration (local dev va production)

Meta redirect URI uchun **https** talab qiladi. Lokal kompyuterda tunnel ishlating
(masalan, Cloudflare Tunnel, bepul, hisob shart emas):

```powershell
winget install --id Cloudflare.cloudflared
cloudflared tunnel --url http://localhost:3000
# chiqqan manzil: https://<random>.trycloudflare.com
```

1. Shu manzilni `META_REDIRECT_URI=https://<random>.trycloudflare.com/instagram/callback`
   va `PANEL_PUBLIC_URL=https://<random>.trycloudflare.com` ga yozing, dashboard'dagi
   **OAuth redirect URIs** ga ham qo‘shing (aynan bir xil bo‘lishi shart).
2. Backend'ni qayta ishga tushiring.
3. Panelni **tunnel manzili orqali** oching (sessiya cookie'si shu domen uchun yaratiladi).
   `trycloudflare.com` manzili har ishga tushganda o‘zgaradi. Doimiy manzil uchun nomlangan tunnel yoki o‘z domeningizni ishlating.

Xavfsizlik:
* `state` bir martalik, foydalanuvchiga bog‘langan va 10 daqiqada eskiradi (faqat SHA-256 saqlanadi).
* Code faqat backend'da tokenga almashtiriladi. Token brauzerga, logga yoki audit'ga tushmaydi.
* Callback sahifasi code'ni manzil satridan darhol o‘chiradi. `Referrer-Policy: no-referrer`.
* `TOKEN_ENCRYPTION_KEYS` bo‘lmasa, ulanish **boshlanmaydi** (aks holda code behuda sarflanardi).

## 12. Permissions

| Ruxsat (scope) | Nima uchun | Endpoint(lar) | Development / Standard Access | App Review / Advanced Access | Production |
|---|---|---|---|---|---|
| `instagram_business_basic` | Profil: ID, username, akkaunt turi. **Majburiy** | `GET /me` | Ruxsat berilgan rolli (o‘z) akkauntlar bilan ishlaydi | Boshqa odamlarning akkauntlari uchun kerak | Majburiy |
| `instagram_business_content_publish` | Post/Reels/Carousel nashr qilish (PHASE 8). **Majburiy** | `POST /{ig-user-id}/media`, `POST /{ig-user-id}/media_publish` | Rolli akkauntlar bilan | Boshqa akkauntlar uchun kerak | Majburiy |
| `instagram_business_manage_insights` | Statistika (PHASE 9) | `GET /{ig-media-id}/insights`, `GET /{ig-user-id}/insights` | Rolli akkauntlar bilan | Boshqa akkauntlar uchun kerak | Default so‘raladi, ixtiyoriy |
| `instagram_business_manage_comments` | Izohlar | `/{ig-media-id}/comments` | — | — | **So‘ralmaydi** (funksiya yo‘q) |
| `instagram_business_manage_messages` | Direct xabarlar | Messaging API | — | — | **So‘ralmaydi** (funksiya yo‘q) |

* Eski `business_basic`, `business_content_publish` kabi nomlar 2025-yil yanvarda bekor qilingan. Faqat `instagram_business_*` ishlating.
* Majburiy ruxsat berilmasa, ulanish rad etiladi (`instagram_permission_missing`) va hech narsa saqlanmaydi.
  Ixtiyoriy ruxsat berilmasa, ulanish bo‘ladi, lekin ogohlantirish chiqadi.
* Ro‘yxatni `.env` dagi `META_SCOPES` / `META_REQUIRED_SCOPES` orqali o‘zgartirish mumkin.

## 13. App Review requirements

**O‘z akkauntingiz uchun** (MUXRIDDIN DESIGN akkaunti app'da rolga ega bo‘lsa) **Standard Access**
yetarli. Meta hujjatlariga ko‘ra bu holatda App Review shart emas. Buni o‘z dashboard'ingizda tekshiring.

**Boshqa (sizga tegishli bo‘lmagan) akkauntlarni** ulash uchun **Advanced Access** kerak:

1. **Business verification** (Meta Business Portfolio orqali kompaniya hujjatlari).
2. **App Review**: har bir ruxsat uchun foydalanish tavsifi va **screencast**: ulanish → kontent tasdiqlash → nashr.
3. Ochiq **Privacy Policy URL** va **Terms of Service URL** (App settings → Basic).
4. **Deauthorize** va **Data deletion** callback URL'lari (§9). Ular tayyor va `signed_request`
   imzosini app secret bilan tekshiradi. Deletion so‘rovi `{url, confirmation_code}` qaytaradi,
   holatni `https://<panel>/api/meta/data-deletion-status?code=…` da ko‘rish mumkin.
5. App'ni **Live** rejimga o‘tkazish.

Real publishing (PHASE 8) default `META_DRY_RUN=true` bilan o‘chiq bo‘ladi.

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

AI testlari faqat deterministik `MockAIProvider` va `respx` mock'lari bilan ishlaydi. Ollama, pullik API kalitlari yoki internet kerak emas.

Testlar hech qachon real Meta, real Ollama yoki real Redis'ga murojaat qilmaydi
(`respx` mock, `META_DRY_RUN=true`).

**Frontend** (`frontend` papkasida):

```powershell
npm run lint
npm run typecheck
npm run build
```

**E2E (Playwright)** alohida stack ishga tushiradi: backend 8100-portda (yangi SQLite baza, mock AI, migration + seed), frontend 3100-portda, soxta Meta server (`backend/tests/fake_meta.py`) 8200-portda. Sizning dev bazangiz va real AI/Meta ishlatilmaydi. Testlar desktop va mobil (Pixel 7) rejimlarida bajariladi.

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

- Instagram login/paroli **hech qachon** so‘ralmaydi va saqlanmaydi. Ulanish faqat rasmiy Meta OAuth orqali. `state` bir martalik va foydalanuvchiga bog‘langan. Meta callback'lari (`signed_request`) HMAC bilan tekshiriladi.
- httpx/httpcore loglari WARNING darajasida cheklangan, chunki ular to‘liq URL'ni (ichida `access_token`) yozadi.
- OAuth tokenlar faqat Fernet bilan shifrlangan holda saqlanadi (`oauth_tokens.token_ciphertext`). Kalit faqat `.env` dan olinadi.
- `.env` va `.env.*` `.gitignore` da (`.env.example` bundan mustasno). Buni test ham tekshiradi.
- Brauzer backend'ga to'g'ridan-to'g'ri murojaat qilmaydi. Sessiya tokeni httpOnly + SameSite=Strict cookie'da saqlanadi va Next.js proxy uni server tomonida qo'shadi. Boshqa saytdan kelgan so'rovlar (CSRF) rad etiladi. Frontendga hech qanday secret berilmaydi.
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
| AI so'rovi `503 ai_provider_unavailable` | `ollama serve`; Docker'da Ollama host'da ishlayotganini tekshiring |
| AI so'rovi `503 ai_model_not_found` | `ollama pull qwen2.5:3b` (yoki `AI_MODEL` dagi model) |
| AI so'rovi `504 ai_timeout` | `AI_TIMEOUT_SECONDS` ni oshiring yoki `AI_JOBS_MODE=celery` |
| AI so'rovi `502 ai_invalid_output` | Model JSON'ni noto'g'ri qaytardi. Qayta urinib ko'ring, `AI_STRUCTURED_MAX_ATTEMPTS=3` qiling yoki kattaroq model ishlating |
| Bot javob bermaydi | Bot jarayoni ishlayaptimi (`python -m app.integrations.telegram`)? `TELEGRAM_ENABLED=true` va token to'g'rimi? |
| Bot "ruxsat berilmagan" deydi | Telegram ID'ingizni `TELEGRAM_ALLOWED_USER_IDS` ga qo'shing va botni qayta ishga tushiring |
| Bot "hisob bog'lanmagan" deydi | Panel → Telegram → kod oling, botga `/start KOD` yuboring (kod 10 daqiqa amal qiladi) |
| "Bu tugma allaqachon ishlatilgan / muddati tugagan" | `/content` buyrug'i bilan yangi tugmalar oling |
| `403 four_eyes_required` | "To'rt ko'z" siyosati yoqilgan: bu versiyani boshqa admin tasdiqlashi kerak |
| `409 approval_required` (reasons: `approval_expired`) | Tasdiq muddati o'tgan, kontentni qayta tasdiqlang |
| `429 too_many_requests` | Oldingi AI job'lar tugashini kuting (`GET /api/v1/ai/jobs`) |
| `400 language_not_supported` | Bu til brend profilida yoqilmagan (`languages`) |
| `503 meta_not_configured` | `.env` da `META_APP_ID`, `META_APP_SECRET`, `META_REDIRECT_URI` ni to‘ldiring (§9) |
| `503 token_encryption_not_configured` | `TOKEN_ENCRYPTION_KEYS` ni yarating (§9) va backend'ni qayta ishga tushiring |
| Instagram oynasida "Invalid redirect_uri" | `META_REDIRECT_URI` dashboard'dagi **OAuth redirect URIs** bilan harfma-harf bir xil emas (https, oxiridagi `/`) |
| "Ulanish so‘rovi yaroqsiz yoki muddati o‘tgan" | `state` 10 daqiqada eskiradi va bir martalik. "Instagram’ni ulash" ni qayta bosing |
| `instagram_permission_missing` | Ruxsatlar oynasida majburiy ruxsatni o‘chirib qo‘ygansiz. Qayta ulang va hammasini belgilang |
| `instagram_refresh_too_early` | Meta 24 soatdan yangi tokenni yangilamaydi. Keyinroq urinib ko‘ring |
| "Qayta ulash kerak" | Token muddati o‘tgan yoki bekor qilingan. "Instagram’ni ulash" ni qayta bosing |
| Callback'dan keyin login sahifasi chiqadi | Panelni redirect URI'dagi domen orqali oching (tunnel manzili), login qiling, oqim davom etadi |
| Migration `91ed60cfe649 requires 'approvals' to be empty` | Eski versiyasiz approval qatorlari bor; ularni xavfsiz ko'chirib bo'lmaydi |

## Development phases

| Phase | Holat |
|---|---|
| 0 — Architecture | ✅ |
| 1 — Project foundation | ✅ |
| 2 — Database (repositories, seed, state machine) | ✅ |
| 3 — AI Content Creator | ✅ |
| 4 — Admin Panel | ✅ |
| 5 — Telegram Bot | ✅ |
| 6 — Approval System | ✅ |
| 7 — Meta OAuth | ✅ |
| 8 — Instagram Publishing | ⏳ |
| 9 — Analytics | ⏳ |
| 10 — Security hardening | ⏳ |
| 11 — Docker (production images) | ⏳ |
| 12 — Production deployment | ⏳ |
