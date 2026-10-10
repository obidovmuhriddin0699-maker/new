# Railway'ga joylash

Bu qo'llanma loyihani [Railway](https://railway.com) platformasiga GitHub'dan joylashni tushuntiradi.
Railway HTTPS manzil (`https://<nom>.up.railway.app`), PostgreSQL va Redis'ni o'zi beradi,
shuning uchun Caddy, zaxira servisi va `deploy.sh` bu yerda **kerak emas**.

```
 Internet ──HTTPS──► frontend (Next.js panel, ochiq domen)
                         │  private network (*.railway.internal)
                         ▼
                      backend (API, ochiq emas) ── volume: media
                         │
        worker (+beat) ──┼── Postgres (Railway)
        telegram (ixt.)  └── Redis (Railway)
        ollama (ixt., AI)
```

> **Narx.** Railway'ning doimiy bepul tarifi yo'q: sinov krediti tugagach Hobby rejasi kerak
> (oyiga $5, shu jumladan $5 foydalanish). Bu stack (backend, worker, frontend, Postgres, Redis)
> taxminan 1–1,5 GB RAM ishlatadi. Ollama qo'shilsa, yana 3–4 GB kerak bo'ladi va bu
> oylik hisobni sezilarli oshiradi. Aniq narxni Railway'ning narxlar sahifasida tekshiring.

> **Muhim (2026):** Railway `railway.json` (Config as Code) formatini eskirgan deb e'lon qilgan.
> Yangi servislar uni ishlatolmaydi. Shuning uchun quyidagi sozlamalar **dashboard'da**
> beriladi. Backend image'i esa servis vazifasini `APP_ROLE` o'zgaruvchisidan biladi.

## 1. Loyiha va ma'lumotlar bazasi

1. railway.com → **New Project** → **Deploy from GitHub repo** → `obidovmuhriddin0699-maker/new`.
   Birinchi servis yaratiladi; uning nomini **backend** qiling (Settings → Name).
2. Servis **Settings → Source → Branch**: ish `main` ga birlashtirilmaguncha
   `claude/nima-boldi-9nzp1a` ni tanlang.
3. Loyiha ichida **+ New → Database → PostgreSQL** va **+ New → Database → Redis**.
   Ularning nomlari `Postgres` va `Redis` bo'lib qolsin (quyidagi havolalar shu nomlarga tayanadi).

## 2. Umumiy (shared) o'zgaruvchilar

Project **Settings → Shared Variables** ga qo'shing. Kalitlarni o'zingiz yarating:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"                               # JWT_SECRET_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # TOKEN_ENCRYPTION_KEYS
```

```
APP_ENV=production
JWT_SECRET_KEY=<tasodifiy, kamida 32 belgi>
TOKEN_ENCRYPTION_KEYS=<Fernet kalit>
META_DRY_RUN=true
AI_PROVIDER=ollama
AI_MODEL=qwen2.5:3b
OLLAMA_BASE_URL=http://ollama.railway.internal:11434
BACKUP_MONITORING=false
```

> `TOKEN_ENCRYPTION_KEYS` ni xavfsiz joyda saqlang. Usiz saqlangan Instagram tokenlarini
> ochib bo'lmaydi.

## 3. Servislar

Har bir servisni **+ New → GitHub Repo → shu repo** bilan qo'shing (bir xil repo, bir xil branch).
Keyin **Variables → Raw Editor** ga mos blokni joylang.

### 3.1 backend (API)

```
RAILWAY_DOCKERFILE_PATH=docker/backend.prod.Dockerfile
APP_ROLE=web
RUN_MIGRATIONS=true
PORT=8000
RAILWAY_RUN_UID=0
APP_ENV=${{shared.APP_ENV}}
JWT_SECRET_KEY=${{shared.JWT_SECRET_KEY}}
TOKEN_ENCRYPTION_KEYS=${{shared.TOKEN_ENCRYPTION_KEYS}}
META_DRY_RUN=${{shared.META_DRY_RUN}}
AI_PROVIDER=${{shared.AI_PROVIDER}}
AI_MODEL=${{shared.AI_MODEL}}
OLLAMA_BASE_URL=${{shared.OLLAMA_BASE_URL}}
BACKUP_MONITORING=${{shared.BACKUP_MONITORING}}
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
PANEL_PUBLIC_URL=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
CORS_ORIGINS=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
MEDIA_PUBLIC_BASE_URL=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
META_REDIRECT_URI=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}/instagram/callback
ALLOWED_HOSTS=${{RAILWAY_PRIVATE_DOMAIN}},healthcheck.railway.app,${{frontend.RAILWAY_PUBLIC_DOMAIN}}
TRUSTED_PROXIES=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,fc00::/7
BOOTSTRAP_ADMIN_EMAIL=siz@example.com
BOOTSTRAP_ADMIN_PASSWORD=<kamida 12 belgili parol>
```

Qo'shimcha sozlamalar:

* **Volume:** servis ustida o'ng tugma → **Attach Volume** → mount path
  `/var/lib/muxriddin/media` (yuklangan rasm/videolar shu yerda saqlanadi).
* **Settings → Deploy → Healthcheck Path:** `/health`.
* **Ochiq domen bermang:** backend faqat ichki tarmoqda ishlaydi.

Nima uchun:
* `RAILWAY_RUN_UID=0`: Railway volume'ni root egaligida ulaydi. Start skripti volume'ni
  `app` foydalanuvchisiga beradi va ilovani **root'siz** ishga tushiradi.
* `TRUSTED_PROXIES`: Railway ichki tarmog'i manzillari (panel shu yerdan murojaat qiladi).
  Backend'ning ochiq domeni yo'q, shuning uchun bu manzillardan faqat sizning servislaringiz keladi.
* `BOOTSTRAP_ADMIN_*`: birinchi ishga tushishda egasi (OWNER) yaratiladi. Kirganingizdan
  keyin **ikkala o'zgaruvchini o'chiring** (parol o'zgaruvchilarda qolmasin).
* `postgresql://` manzil avtomatik `postgresql+psycopg://` ga aylantiriladi.

### 3.2 worker (fon vazifalari + rejalashtiruvchi)

```
RAILWAY_DOCKERFILE_PATH=docker/backend.prod.Dockerfile
APP_ROLE=worker
CELERY_BEAT=true
APP_ENV=${{shared.APP_ENV}}
JWT_SECRET_KEY=${{shared.JWT_SECRET_KEY}}
TOKEN_ENCRYPTION_KEYS=${{shared.TOKEN_ENCRYPTION_KEYS}}
META_DRY_RUN=${{shared.META_DRY_RUN}}
AI_PROVIDER=${{shared.AI_PROVIDER}}
AI_MODEL=${{shared.AI_MODEL}}
OLLAMA_BASE_URL=${{shared.OLLAMA_BASE_URL}}
BACKUP_MONITORING=${{shared.BACKUP_MONITORING}}
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
PANEL_PUBLIC_URL=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
CORS_ORIGINS=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
MEDIA_PUBLIC_BASE_URL=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}
META_REDIRECT_URI=https://${{frontend.RAILWAY_PUBLIC_DOMAIN}}/instagram/callback
ALLOWED_HOSTS=${{frontend.RAILWAY_PUBLIC_DOMAIN}}
```

* **Replicas = 1** qoldiring: `CELERY_BEAT=true` bo'lgan worker faqat bitta bo'lishi kerak,
  aks holda rejalashtirilgan vazifalar ikki marta ishga tushadi.
* Domen va volume kerak emas.

### 3.3 frontend (panel)

```
RAILWAY_DOCKERFILE_PATH=docker/frontend.prod.Dockerfile
PORT=3000
BACKEND_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:8000
TRUST_PROXY_HEADERS=true
PANEL_PUBLIC_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
SESSION_COOKIE_SECURE=true
LEGAL_OPERATOR_NAME=MUXRIDDIN DESIGN
LEGAL_CONTACT_EMAIL=siz@example.com
```

* **Settings → Networking → Generate Domain** (port 3000). Shu domen panel manzili bo'ladi.
* Healthcheck Path: `/login`.

### 3.4 ollama (ixtiyoriy, AI uchun)

**+ New → Docker Image** → `ollama/ollama:0.40.2`.

```
OLLAMA_HOST=[::]:11434
```

* Volume: `/root/.ollama` (model qayta yuklanmasligi uchun).
* Modelni bir marta yuklang: Railway CLI'ning `railway ssh` buyrug'i bilan ollama servisiga
  ulaning va `ollama pull qwen2.5:3b` ni bajaring.
* `OLLAMA_HOST=[::]:11434` ichki tarmoqda IPv4 va IPv6 orqali eshitish uchun. Agar Ollama
  bu qiymat bilan ishga tushmasa, `0.0.0.0:11434` qo'ying.

Ollama'siz ham panel ishlaydi. AI tugmalari "AI ishlamayapti" deb ko'rsatadi, qo'lda kontent
yaratish va nashr qilish ishlayveradi.

### 3.5 telegram (ixtiyoriy)

Backend bilan bir xil o'zgaruvchilar, faqat: `APP_ROLE=telegram`, `PORT` ni olib tashlang,
qo'shing: `TELEGRAM_ENABLED=true`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_IDS`.
Replicas = 1.

## 4. Birinchi ishga tushirish

1. **Deploy** tugmasini bosing (yoki har bir servisni deploy qiling). Tartib muhim emas: backend
   migratsiyani o'zi bajaradi (`RUN_MIGRATIONS=true`, PostgreSQL advisory lock bilan,
   bir nechta nusxa bir vaqtda ishga tushsa ham xavfsiz).
2. Backend loglarida `Created owner user ...` va `Application startup complete` chiqishi kerak.
3. `https://<frontend-domeni>/login` ni oching va `BOOTSTRAP_ADMIN_*` bilan kiring.
4. Backend'dan `BOOTSTRAP_ADMIN_EMAIL` va `BOOTSTRAP_ADMIN_PASSWORD` ni o'chiring.
5. Panel → Umumiy ko'rinish → "Tizim holati": ma'lumotlar bazasi va Redis **OK** bo'lishi kerak.

## 5. Meta (Instagram) ulash

`docs/DEPLOYMENT.md` §6 dagi checklist bilan bir xil. Manzillarda `https://<frontend-domeni>` ishlating:

| Meta dashboard | Qiymat |
|---|---|
| OAuth redirect URI | `https://<frontend-domeni>/instagram/callback` |
| Deauthorize callback | `https://<frontend-domeni>/api/meta/deauthorize` |
| Data deletion request | `https://<frontend-domeni>/api/meta/data-deletion` |
| Privacy Policy / Terms | `https://<frontend-domeni>/privacy`, `/terms` |

Keyin backend va worker'ga `META_APP_ID` va `META_APP_SECRET` qo'shing. Sinovdan keyin
`META_DRY_RUN=false` qiling (shared variable).

## 6. Zaxira va monitoring

* **Ma'lumotlar bazasi:** Railway Postgres servisining **Backups** bo'limini yoqing
  (tarifingizga bog'liq). `BACKUP_MONITORING=false` shuning uchun: ops monitor compose'dagi
  zaxira servisini kutmaydi.
* **Media volume:** Railway volume backups (tarifga bog'liq), yoki vaqti-vaqti bilan nusxa oling.
* **Uptime:** tashqi monitor (UptimeRobot va h.k.) bilan `https://<frontend-domeni>/api/backend/health`.
* **Ogohlantirishlar:** Telegram servisi yoqilgan bo'lsa, ops monitor xabarlari Telegram'ga keladi.

## 7. Yangilash

GitHub'ga push qilingan har bir commit tanlangan branch'dagi servislarni avtomatik qayta yig'adi.
Ma'lumotlar bazasi migratsiyasi backend ishga tushganda bajariladi.

## 8. Muammolar

| Belgi | Sabab va yechim |
|---|---|
| Backend: `Invalid production configuration: ...` | Xabarda qaysi o'zgaruvchi yetishmasligi yozilgan (masalan `ALLOWED_HOSTS`, `PANEL_PUBLIC_URL` https bo'lishi kerak) |
| Healthcheck `400 Invalid host header` | `ALLOWED_HOSTS` da `healthcheck.railway.app` yo'q |
| Panel: "Backend bilan aloqa yo'q" | frontend `BACKEND_URL` (`http://<backend private domain>:8000`) va backend `PORT=8000` ni tekshiring |
| Yuklashda 500 / `Permission denied` | backend'da `RAILWAY_RUN_UID=0` yo'q yoki volume `/var/lib/muxriddin/media` ga ulanmagan |
| Barcha foydalanuvchilar bitta limitga tushadi | frontend'da `TRUST_PROXY_HEADERS=true`, backend'da `TRUSTED_PROXIES` ni tekshiring |
| Rejalashtirilgan post chiqmadi | worker servisi ishlayaptimi va `CELERY_BEAT=true`mi? `META_DRY_RUN=false`mi? |

## 9. Cheklovlar (halol)

* Railway ichki tarmog'i ba'zi (eski) muhitlarda faqat IPv6. Backend IPv4 va IPv6 ni bitta
  socket'da tinglaydi (`app/serve.py`). Bu IPv4 bilan sinalgan; IPv6 yo'lini bu loyihaning
  test muhitida sinab bo'lmadi (yadroda IPv6 yo'q edi).
* Mijozning haqiqiy IP'si Railway proxy'si `X-Forwarded-For` ga qo'shgan manzildan olinadi.
  Agar Railway mijoz yuborgan `X-Forwarded-For` ni o'zgartirmasdan uzatsa, IP bo'yicha limitlarni
  aylanib o'tish mumkin bo'ladi. Foydalanuvchi va akkaunt bo'yicha limitlar baribir ishlaydi.
* Railway'ning ichki manzillar diapazonlari hujjatlashtirilmagan. Shuning uchun `TRUSTED_PROXIES`
  barcha xususiy diapazonlarni o'z ichiga oladi.
