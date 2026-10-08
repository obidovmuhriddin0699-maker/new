# Sevgi bulutlari — Muxriddin & Umida

Minimal va romantik uslubdagi, to‘liq o‘zbek tilidagi to‘y taklifnomasi sayti. Har bir bo‘lim bulutlar orasidan chiqib keladi: sahifa aylantirilganda bulutlar ikki tomonga tarqaladi, tuman tarqaladi va matn tumandan ko‘tarilib chiqadi. Faqat HTML, CSS va vanilla JavaScript (ES modules) — framework yo‘q, build shart emas.

**Sana:** 06.10.2026, 16:00 (Asia/Tashkent) · **Joy:** Versal to‘yxonasi, Farg‘ona shahri

---

## 1. Ishga tushirish

Sayt `data/wedding.json` faylini `fetch()` orqali o‘qiydi va JS modullardan foydalanadi. Brauzerlar xavfsizlik sababli **`file://` manzilidan** (faylni ikki marta bosib ochganda) `fetch` va ES modullarni bloklaydi. Shuning uchun loyihani **lokal server** orqali oching:

| Usul | Qadam |
|---|---|
| **VS Code Live Server** (tavsiya) | `modern-love-uz` papkasini oching → `index.html` ustida o‘ng tugma → **Open with Live Server** |
| Python | `cd modern-love-uz && python3 -m http.server 8080` → http://localhost:8080 |
| Node | `npx http-server modern-love-uz -p 8080` |

> **Faylni bosib ochish kerak bo‘lsa** — `dist/index.html` dan foydalaning (6-bo‘lim). U bitta faylga yig‘ilgan va serversiz ishlaydi.

---

## 2. Matn va ma’lumotlarni o‘zgartirish

Hamma ma’lumot bitta faylda: **`data/wedding.json`**. Kodga tegish shart emas.

| Maydon | Nima qiladi |
|---|---|
| `groom`, `bride` | Kuyov va kelin ismlari (KATTA harfda yozing) |
| `date` | Sana `KK.OO.YYYY` formatida, masalan `"06.10.2026"` |
| `time` | Boshlanish vaqti, `"16:00"` |
| `timezone` | Countdown vaqt zonasi (`"Asia/Tashkent"`) |
| `venue.name`, `venue.city`, `venue.address` | To‘yxona nomi va manzili |
| `venue.mapsUrl` | Google Maps / Yandex havolasi. Bo‘sh bo‘lsa — nom bo‘yicha qidiruv havolasi avtomatik yasaladi |
| `story` | “Our Story” bo‘limi: yil, sarlavha, matn, rasm (`gallery` dagi `id`) |
| `program` | Kun dasturi (vaqt, sarlavha, matn) |
| `images` | Hikoya, manzil va yakuniy bo‘lim rasmlari (`id` → nisbat, o‘lchamlar, `alt`) |
| `gallery` | Galereya rasmlari: `id`, nisbat (`ratio`), o‘lchamlar (`widths`), `alt` matn |
| `rsvp` | Javoblar qayerga borishi (3-bo‘lim), `deadline`, `maxGuests` |
| `final.message` | Yakuniy so‘z |
| `seo` | Sahifa sarlavhasi va tavsifi (`{groom}`, `{bride}`, `{date}`, `{venue}` o‘rniga qiymat qo‘yiladi) |
| `siteUrl` | Sayt joylangan to‘liq manzil (masalan `https://muxriddin-umida.uz/`) — Telegram/WhatsApp ko‘rinishi va canonical uchun |

### Countdown
Sana o‘tib ketgan bo‘lsa, raqamlar o‘rniga **“O‘sha kun keldi”** chiqadi. Hozirgi standart sana (06.10.2026) o‘tgan — sanani o‘zgartirsangiz, countdown darhol sanay boshlaydi.

### Musiqa
Standart: **“Oshiq bu ko‘ngil”**. *Asadov — Silencio* ham papkada bor. Almashtirish:

```json
"music": "assets/audio/asadov-silencio.m4a",
"musicFallback": "assets/audio/asadov-silencio.mp3",
"musicTitle": "Asadov — Silencio",
```

“Reduce motion” yoqilgan qurilmalarda bulutlar, gulbarglar va harakatlar o‘chiriladi — matn darhol ko‘rinadi.

Musiqa sahifa ochilganda **o‘chiq** turadi (brauzerlar ovozni avtomatik yoqishni taqiqlaydi) va mehmon birinchi marta bosganda yumshoq yoqiladi. Pastki o‘ng burchakdagi tugma uni o‘chiradi/yoqadi.

---

## 3. RSVP — javoblarni qabul qilish

`data/wedding.json → rsvp`:

1. **`endpoint`** — JSON `POST` qabul qiladigan istalgan HTTPS manzil (o‘z backend, Google Apps Script, Formspree, Make…). Yuboriladigan ma’lumot:
   ```json
   { "name": "...", "phone": "...", "attendance": "yes|no", "guests": 2, "message": "...", "submittedAt": "ISO-sana" }
   ```
2. **`whatsapp`** — raqam xalqaro formatda (`"998901234567"`). Mehmon tugmani bosganda tayyor matnli WhatsApp xabari ochiladi.
3. Ikkalasi ham bo‘sh bo‘lsa — javob faqat mehmonning qurilmasida (`localStorage`) saqlanadi va konsolga ogohlantirish chiqadi. **Saytni tarqatishdan oldin 1 yoki 2-ni sozlang.**

---

## 4. Rasm va videolar

* Rasmlar: `assets/images/{id}-{kenglik}.webp` (masalan `touch-480.webp`, `touch-720.webp`). Yangi rasm qo‘shish uchun shu nomlash bilan saqlang va `gallery` ga yozing.
* Videolar: `assets/video/{nom}.mp4` + `.webm` + `{nom}-poster.webp`. Bosh sahifa videosi (dengiz bo‘yida quyosh botishi) `index.html` da, “oy” lavhasi `films` da.
* **Har bir surat va video saytda faqat bir marta ishlatilgan** — 12 ta video va atirgul suratining har biridan bittadan lavha olingan.
* Bulutlar: `assets/clouds/` (chap va o‘ng bulut massasi + pastki bulut tasmasi). Ular `css/clouds.css` va `js/clouds.js` orqali ishlaydi.
* Barcha videolar ovozsiz, faqat ekranda ko‘ringanda o‘ynaydi; “Reduce motion” yoqilgan qurilmada animatsiya va videolar to‘xtatiladi.

---

## 5. Hostingga joylash

Papkani to‘liq yuklang — build kerak emas: **Netlify** (papkani sudrab tashlash), **Vercel**, **GitHub Pages**, **Cloudflare Pages** yoki istalgan hosting. HTTPS da `sw.js` saytni oflayn ham ochiladigan qiladi; fayllarni o‘zgartirgandan keyin `sw.js` dagi `VERSION` ni oshiring.

---

## 6. Bitta fayl (`dist/index.html`)

```bash
python3 build-single.py
```

Hamma narsani (CSS, JS, shriftlar, bulutlar, rasm, video, musiqa) bitta ~12 MB faylga yig‘adi — Telegramda yuborish yoki serversiz ochish uchun. Ko‘p faylli versiya tezroq yuklanadi (rasmlar lazy, AVIF), shuning uchun hostingda asosiy papkani ishlating. Node.js kerak (esbuild `npx` orqali avtomatik olinadi).

---

## 7. JavaScript'ni o‘zgartirsangiz

Sayt eski va ilova ichidagi brauzerlarda ham ishlashi uchun `js/` dagi modullar bitta `js/app.bundle.js` fayliga yig‘ilgan. `js/*.js` fayllarini o‘zgartirgandan keyin uni qayta yig‘ing (`data/wedding.json` uchun bu shart emas):

```bash
npx esbuild@0.24.0 js/app.js --bundle --format=iife --minify --target=es2017,safari12,chrome61 --outfile=js/app.bundle.js
```

## 8. Tuzilma

```
modern-love-uz/
├── index.html
├── manifest.json · sw.js · README.md · build-single.py
├── data/wedding.json
├── css/  fonts · base · components · clouds · animations · responsive
├── js/   app · data · clouds · sparkles · navigation · scroll · animations · countdown · gallery · lightbox · audio · rsvp
└── assets/  images · video · clouds · audio · fonts · icons
```

| Modul | Vazifasi |
|---|---|
| `app.js` | Ma’lumotni yuklaydi, sahifani to‘ldiradi, barcha modullarni ishga tushiradi |
| `clouds.js` | Har bir bo‘limdagi bulut pardasi va bosh sahifadagi suzuvchi bulutlar |
| `sparkles.js` | Bosh sahifa va yakunda ko‘tarilayotgan iliq nurlar va tushayotgan atirgul gulbarglari |
| `data.js` | JSON yuklash, sana/vaqt zonasi hisoblash, responsive `<picture>` |
| `navigation.js` | To‘liq ekranli menyu, fokus tuzog‘i, Esc |
| `scroll.js` | 1px progress chizig‘i, timeline, 06 → OCTOBER → 2026 ketma-ketligi, videolarni faqat ko‘ringanda o‘ynatish |
| `animations.js` | Bosh sahifa kirish animatsiyasi, tumandan chiqish effekti, yurak urishi (“&”), desktop kursor (“Ko‘rish”) |
| `countdown.js` | Asia/Tashkent bo‘yicha countdown |
| `gallery.js` · `lightbox.js` | Masonry galereya; lightbox: ←/→/Esc, swipe, pinch-zoom, ikki marta bosib zoom |
| `audio.js` | Fon musiqasi, fade, m4a → mp3 zaxira |
| `rsvp.js` | Forma tekshiruvi va yuborish |
