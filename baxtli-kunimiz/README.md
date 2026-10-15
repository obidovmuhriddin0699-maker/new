# Baxtli kunimiz — Muxriddin & Umida

Konvert va mum muhr bilan ochiladigan, oltin ravoqli, ikki tilli (o‘zbek / rus) to‘y taklifnomasi sayti. Saytning o‘z ovoz effektlari bor. Faqat HTML, CSS va vanilla JavaScript ishlatilgan.

**Sana:** 06.11.2026, 16:00 (Asia/Tashkent) · **Joy:** Versal to‘yxonasi, Farg‘ona shahri

## Bo‘limlar
1. **Konvert:** barglar fonida mum muhrli konvert. Muhr bosilganda muhr sinadi, qopqoq ochiladi, karta chiqadi, yorug‘lik taraladi va musiqa boshlanadi.
2. **Bosh sahifa:** oltin ravoq ichida video, kelin-kuyov ismlari, sana va soat, yog‘ilayotgan oltin zarralar va gulbarglar.
3. **Taklif:** Bismillah, “Ikki qalb · Bitta taqdir · Abadiy muhabbat”, “Aziz mehmonimiz — Sizni kutamiz”.
4. **Sana va vaqt:** oy kalendari (to‘y kuni oltin doirada), countdown, “Kalendarga qo‘shish” (.ics fayl va Google Kalendar).
5. **Kechaning tartibi:** aylantirganda chiziq bo‘ylab sirpanib tushadigan atirgulli dastur.
6. **Manzil:** ravoqli surat, Yandex xarita va Google orqali yo‘l chizish tugmalari.
7. **Xotiralarimiz:** suratlar galereyasi; to‘liq ekranda ochiladi, surib o‘tkaziladi va kattalashtiriladi.
8. **Kiyim uslubi** va **Sovg‘a haqida**.
9. **Ishtirokni tasdiqlang:** RSVP muhri bosilganda forma ochiladi.
10. **Tilaklar daftari:** mehmonlarning tilaklari.
11. **Yakun:** oy ostidagi video medalyon ichida.

## Ovoz effektlari (`assets/sfx/`)
Hammasi shu sayt uchun noldan sintez qilingan (begona yozuvlar ishlatilmagan):

| Fayl | Qayerda eshitiladi |
|---|---|
| `seal-crack` | muhr sinishi (konvert va RSVP) |
| `envelope-open` | konvert qopqog‘i ochilishi |
| `card-slide` | karta konvertdan chiqishi |
| `shimmer` | sehrli qo‘ng‘iroqchalar (taklifnoma ochilganda, tilak yuborilganda) |
| `whoosh` | sarlavhalar paydo bo‘lishi, suratni ochish |
| `heartbeat` | kalendarda to‘y kuni ko‘ringanda |
| `page` | til almashtirish, suratlarni varaqlash |
| `click`, `pop` | tugmalar, forma yuborish |
| `success` | RSVP javobi qabul qilinganda |

Pastki o‘ng burchakdagi tugma musiqani ham, effektlarni ham o‘chiradi yoki yoqadi. Effektlar baland bo‘lmasligi uchun `sfxVolume`, musiqa uchun `musicVolume` qiymatini o‘zgartiring.

## Ishga tushirish
`data/wedding.json` faylini `fetch` orqali o‘qigani uchun saytni **lokal server** orqali oching:
- VS Code → `index.html` → **Open with Live Server**, yoki
- `python3 -m http.server 8080` → http://localhost:8080

Faylni ikki marta bosib ochish kerak bo‘lsa, `dist/index.html` dan foydalaning (pastda).

## Ma’lumotlarni o‘zgartirish — `data/wedding.json`

| Maydon | Ma’nosi |
|---|---|
| `groom`, `bride` | Ismlar: `uz` va `ru` variantlari |
| `date`, `time`, `timezone` | Sana `KK.OO.YYYY`, vaqt, vaqt zonasi. Kalendar, countdown va .ics fayl shundan yasaladi |
| `venue` | Nomi, shahri, xarita qidiruvi (`query`). Aniq havolalar uchun `yandexUrl` / `googleUrl` |
| `program` | Dastur: vaqt + `uz` / `ru` nomi |
| `gallery` | Suratlar (`assets/images/{id}-{kenglik}.webp`) |
| `dressColors` | Kiyim uslubi ranglari |
| `rsvp` | `endpoint` yoki `whatsapp`, `deadline`, `maxGuests` |
| `wishes.endpoint` | Tilaklar daftari umumiy bo‘lishi uchun (pastga qarang) |
| `text.uz`, `text.ru` | Saytdagi barcha matnlar |
| `music`, `musicFallback` | Musiqa. *Asadov — Silencio* ham papkada bor |

**Javoblar qayerga boradi**
1. **`rsvp.endpoint`:** JSON `POST` qabul qiladigan manzil (Google Apps Script, Formspree va h.k.).
2. **`rsvp.whatsapp`:** raqam (`998901234567`); mehmon uchun tayyor matnli WhatsApp xabari ochiladi.
3. Ikkalasi ham bo‘sh bo‘lsa, javob faqat mehmon qurilmasida saqlanadi. **Tarqatishdan oldin 1 yoki 2-ni sozlang.**

**Tilaklar daftari.** Hamma mehmonlarning tilaklari bitta joyda ko‘rinishi uchun `wishes.endpoint` kerak: GET so‘rovida `[{ "name": "…", "text": "…" }]` qaytaradigan va POST qabul qiladigan manzil. U bo‘lmasa, tilak kelin-kuyovga RSVP kanali orqali yuboriladi va mehmonning o‘z qurilmasida ko‘rinadi.

**Til:** `defaultLang` (`uz` yoki `ru`). `?lang=ru` havolasi saytni darhol ruscha ochadi.

## JavaScript o‘zgarsa
`js/*.js` modullari eski brauzerlar uchun bitta `js/app.bundle.js` fayliga yig‘ilgan. Ularni o‘zgartirgandan keyin qayta yig‘ing:
```bash
npx esbuild@0.24.0 js/app.js --bundle --format=iife --minify --target=es2017,safari12,chrome61 --outfile=js/app.bundle.js
```

## Bitta fayl
```bash
python3 build-single.py      # → dist/index.html (~10 MB, serversiz ishlaydi)
```
