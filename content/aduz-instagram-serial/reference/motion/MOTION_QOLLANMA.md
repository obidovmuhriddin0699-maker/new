# ADUZ · Motion video qo‘llanmasi (yo‘riqnoma)

> **Qachon ishlatiladi:** mijoz "motion video", "motion animatsiya" yoki "motion uslubida" rolik so‘raganda,
> **avval shu faylni o‘qing** va shu papkadagi namuna videolarga tayaning. Bu yo‘riqnoma mijozning
> o‘zi bergan namunalar asosida tuzilgan (2026-10-13).

Papka: `content/aduz-instagram-serial/reference/motion/`

---

## 1. Namuna videolar ro‘yxati

| Fayl | Uzunlik · o‘lcham | Nima ko‘rsatadi | Asosiy g‘oya |
|---|---|---|---|
| `ref00_gemini_generated_video_f86c1b90.mp4` | 10 s · 720×1280 · ovozli | ADUZ 8-qism, 3D (Gemini/Veo) | 3D qahramonlar, ko‘k to‘rli fon, uchuvchi so‘zlar, ADUZ hub, 5 ta neon kartochka, telefon menyusi |
| `ref01_VID_20261013_095212_187.mp4` | 26 s · 720×1280 · ovozli | Muharrirdagi tutorial: "Paper Flip Animation" | Qog‘oz varag‘i bukilishi (page curl), keyframe/progress bilan animatsiya, oxirida **Follow** tugmasi + yulduzcha portlash ("Goal 10k followers") |
| `ref02_VID_20261013_094951_481.mp4` | 8 s · 720×900 · ovozsiz | "Opus 5.5 Motion Graphics" — 16 ta naqsh umumiy ko‘rinishi | Barcha naqshlar bitta to‘rda; har biri o‘z kichik oynasida jonli |
| `ref03_..._442.mp4` | 8 s · 720×900 | **Card → workspace** | Kichik kartochka kattalashib to‘liq ishchi oynaga aylanadi (shared-element morph), keyin qaytadi |
| `ref04_..._947.mp4` | 8 s · 720×900 | **Magnetic dock** | Kursor o‘tganda ikonkalar kattalashadi (macOS dock), ustida yorliq ("Notes", "Assets"...), egri chiziq ko‘rsatkichi |
| `ref05_..._414.mp4` | 8 s · 720×900 | **Tabs → panels** | Tanlangan tab sirpanadi (Reels → Posts), panel kontenti almashadi, raqam badge |
| `ref06_..._446.mp4` | 8 s · 720×900 | **Chart morph** | Ustunli grafik chiziqli grafikka aylanadi (nuqtalar ustun tepasidan o‘tadi), yuqorida qiymat badge "92" |
| `ref07_..._735.mp4` | 8 s · 720×900 | **Button → player** | "Preview" tugmasi o‘sib video pleerga aylanadi, progress chizig‘i yuradi, play/pause |
| `ref08_..._958.mp4` | 8 s · 720×900 | **Masked type** | "OPUS" kontur harflar; chiziq o‘tgach rasm harflarni pastdan to‘ldiradi; "in motion" chiqadi |
| `ref09_..._854.mp4` | 8 s · 720×900 | **Search → results** | Qidiruv maydoniga matn yoziladi, natijalar ketma-ket (stagger) pastga tushadi |
| `ref10_..._739.mp4` | 8 s · 720×900 | **Dashboard zoom** | Dashboard'dagi bitta plitka ajralib kattalashadi (burchak qavslari bilan), KPI "12,480 +18%" |
| `ref11_..._468.mp4` | 8 s · 720×900 | **Spring stack** | Kartochkalar to‘plami prujina harakati bilan yoyiladi va joyiga o‘tiradi; burchakda easing egri chizig‘i |
| `ref12_gemini_generated_video_e6324fc0.mp4` | 10 s · 720×1280 · ovozli | ADUZ 2-qism, 3D (Gemini/Veo) | 3D qahramon ofisda, "QAYSI BIRI TO‘G‘RI?!" sarlavha, admin bildirishnomalari, cho‘t, telefonda ADUZ solishtirish ekrani |

`ref02` umumiy ko‘rinishidagi qolgan naqshlar (alohida video yo‘q, lekin shu uslubda qilinadi):
**Elastic type** (STRETCH so‘zi cho‘ziladi), **Text → layout**, **Image reveal**, **Perspective shift**,
**Glass focus**, **Flowing paths**, **Particle logo**.

---

## 2. Ikki vizual yo‘nalish

### A. "Clean UI motion" (ref02–ref11) — asosiy motion uslub
- **Fon:** iliq och kulrang `#EBE9E5` (sahifa), ichki maydon `#EEECEA`.
- **Kartochkalar:** oq `#FCFCFC` / `#F9F8F7`, burchak radiusi katta (≈ 24–32 px @720), juda yumshoq soya.
- **Qorong‘i panellar:** `#17181F` / `#11131A` (dock, pleer foni).
- **Urg‘u ranglar:** to‘q sariq-terrakota `#E07E57`, yumshoq havorang `#72AFD4`, to‘q ko‘k `#234B9F`.
- **Matn:** sarlavha — qalin grotesk (Inter Bold/Black), qora `#17181F`; izoh — kichik kulrang;
  texnik yorliqlar — monospace ("shape morph", "ISSUE 05").
- **Sahifa tuzilishi (har bir naqsh):** chap yuqorida kichik to‘q sariq raqam (`01`, `02`...) + sarlavha
  ("Card → workspace"), ostida bir qatorli izoh; o‘rtada animatsiya oynasi; pastda to‘q sariq
  **"Use it for:"** qatori; eng pastda muallif satri.
- **Kursor:** oq strelka kursor ko‘pincha harakatni "boshqaradi" (dock, tugma bosish).
- **Ishora elementlari:** shtrix (dashed) chegaralar, burchak qavslari, egri chiziq (easing grafigi).

### B. "ADUZ 3D promo" (ref00, ref12) — Gemini/Veo 3D uslubi
- 3D (Pixar-ga o‘xshash) qahramonlar: Rustam aka (mo‘ylovli), Muxriddin Obidov (oq ko‘ylak).
- To‘q ko‘k to‘rli fon `#0A2060 → #1847A8`, mayda uchqunlar, havorang neon `#5ADCFF` chegara va yorug‘lik.
- Kinetik tipografiya: so‘zlar harakat izi (motion blur) bilan uchib keladi, keyin markazga yig‘iladi.
- Neon "pill" kartochkalar (to‘q ko‘k ichki qism, havorang yonuvchi chegara), 3D ikonkalar.
- Sariq urg‘u `#FFC83D` (ADUZ logotipi, muhim so‘zlar).
- Taglavha: oq qalin matn, qora kontur.

**Qaysi birini tanlash:** mijoz aniq aytmasa — mahsulot imkoniyatini ko‘rsatish (UI, natija, grafik) uchun
**A**, hikoya/qahramonli epizod uchun **B**. Ikkalasini aralashtirish mumkin: B dagi hikoya + A dagi
UI-naqsh bloklari (masalan, 3D sahnadan keyin "Search → results" bloki).

---

## 3. Harakat qoidalari (namunalardan o‘lchangan)

1. **8 soniyalik halqa (loop):** har bir naqsh ≈8 s. Tuzilma:
   `0–0.8 s` boshlang‘ich holat → `0.8–1.3 s` asosiy o‘zgarish (morph/ochilish) →
   `1.3–6.9 s` natija holati, **lekin jonli** (progress yuradi, kursor yuradi, raqamlar o‘zgaradi) →
   `6.9–7.6 s` teskari harakat → boshlang‘ich holatga silliq qaytish (choksiz loop).
2. **Prujina (spring) easing:** biroz oshib ketib (overshoot ≈ 5–10%) joyiga o‘tiradi. Chiziqli harakat yo‘q.
3. **Shared-element morph:** element yo‘qolib, boshqasi paydo bo‘lmaydi — **o‘zi** o‘sib boshqa
   shaklga aylanadi (tugma → pleer, kartochka → oyna, plitka → KPI kartochkasi).
4. **Stagger:** ro‘yxat elementlari 80–150 ms oraliq bilan ketma-ket chiqadi (qidiruv natijalari).
5. **Hech qachon to‘liq to‘xtamaydi:** "hold" paytida ham mayda harakat bor (progress, kursor, tebranish).
   *(Mijoz fikri: qotib qolgan kadrlar qabul qilinmaydi — render'dan keyin `freezedetect` bilan tekshirish.)*
6. **Kursor-drayv:** kursor elementga yetib boradi → element javob beradi (kattalashadi, bosiladi).
7. **Qavslar va shtrixlar** — e’tiborni qaratish uchun (Dashboard zoom, Card → workspace).
8. **Tutorial uslubi (ref01):** progress/keyframe chizig‘i ko‘rinib turadi, oxirida CTA tugma
   ("Follow" / "Kuzating") yulduzcha portlash bilan.

---

## 4. ADUZ mazmuniga moslash xaritasi

| ADUZ mavzusi | Naqsh | Misol |
|---|---|---|
| Hudud bo‘yicha kanal topish | **Search → results** | "Farg‘ona mebel" yoziladi → 3 ta kanal kartochkasi (obunachi, ko‘rish, narx) |
| Narx/ko‘rishlarni solishtirish | **Tabs → panels** | Tablar: "Narx · Ko‘rish · Hudud" — panel almashadi |
| Natija / hisobot | **Chart morph** | Ustunlar (kunlik mijozlar) → chiziq, badge "+18 ta mijoz" (shartli misol) |
| KPI ajratib ko‘rsatish | **Dashboard zoom** | "Promo-kod bilan: 18 ta mijoz" plitkasi kattalashadi |
| Buyurtma kartasi → to‘liq buyurtma | **Card → workspace** | "Buyurtma #12" → sana, soat, format, holat oynasi |
| Bot funksiyalari menyusi | **Magnetic dock** | Ikonkalar: Kanal topish · Solishtirish · Buyurtma · Kuzatish · Natija |
| Demo/"qanday ishlaydi" | **Button → player** | "Ko‘rish" tugmasi → bot ekran yozuvi pleeri |
| Sarlavha / kampaniya nomi | **Masked type** | "ADUZ" kontur harflar to‘ladi → "reklama bir joyda" |
| Kanal kartochkalari / sharhlar | **Spring stack** | 3 ta kanal kartochkasi yoyiladi |
| Seriya yakuni / CTA | ref01 dagi **Follow + portlash** | "Kuzating" / "@Targetreklammabot" |

---

## 5. Texnik standart (bizning renderlar uchun)

- **Chiqish:** 1080×1920, 30 fps, H.264 yuv420p, AAC 192k. Namunalar 720×900 (4:5) — vertikal
  kadrda naqsh oynasi markazda, tepada sarlavha, pastda taglavha/CTA.
- **Har bir blok ≈8 s**, rolik 30–45 s = 4–5 blok.
- **Matn:** faqat to‘g‘ri o‘zbek lotin (o‘, g‘ — `‘` belgisi). AI generatsiya qilgan buzuq matnni
  hech qachon qoldirmang — ustidan to‘g‘ri matn bilan qayta chizing.
- **Raqamlar:** "Shartli misol" belgisi bilan; kafolat va'da qilinmaydi.
- **Brend:** ADUZ, bot `@Targetreklammabot`, asoschi **Muxriddin Obidov**.
- **Ovoz:** `video/voice.py` (RHVoice "Islom"/"Dilnavoz" + hissiyot belgilari `[excited]`, `[p=200]`),
  promo uslubi uchun `narr` / `rus8` spikerlari. Har renderdan oldin `voice.qa()` — "Muammolar: yo‘q".
- **Sifat tekshiruvi (majburiy):**
  `ffmpeg -i out.mp4 -vf "freezedetect=n=0.002:d=0.3" -f null -` → bironta freeze bo‘lmasligi kerak;
  `mpdecimate` bilan noyob kadrlar ≥ 98%; audio `ebur128` ≈ −14…−16 LUFS, peak ≤ −1 dBFS.
- **Namuna kliplardan foydalanish:** mijozning 3D kliplari sekinlashtiriladi (`minterpolate`),
  sahnadan qisqa bo‘lsa — bumerang (oldinga-orqaga), hech qachon oxirgi kadrda muzlatilmaydi.

---

## 6. Mavjud dasturlar

- `video/make_day8.py` — oddiy motion grafika (to‘q ko‘k, avatarlar).
- `video/make_day8_v2.py` — 3D Gemini uslubi (B), mijoz kliplari + to‘g‘ri matnli qayta chizilgan bloklar.
- Yangi motion roliklar uchun: A uslubdagi naqshlarni (Search → results, Chart morph, ...) alohida
  funksiyalar sifatida yozib, qayta ishlatish tavsiya etiladi.
