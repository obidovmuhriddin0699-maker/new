# YouTube Agent & Channel Manager

Ushbu modul **YouTube Data API v3** va **AI Agent** orqali YouTube kanalini to'liq avtomatlashtirish, videolarni rejalashtirib yuklash hamda statistikani kuzatish imkoniyatini taqdim etadi.

---

## Asosiy imkoniyatlar

1. **Avtomatik va Rejalashtirilgan Yuklash (Resumable Upload & Scheduling)**:
   - YouTube'ning 2 bosqichli ishonchli (resumable) yuklash protokoli orqali katta hajmdagi videolarni ham uzilishlarsiz yuklash.
   - `--schedule "YYYY-MM-DD HH:MM"` yoki `publish_at` parametri orqali videolarni kelajakdagi vaqtga rejalashtirish. YouTube bu vaqt kelganda videoni avtomatik tarzda `public` holatiga o'tkazadi.
   - Maxfiylik boshqaruvi: `public`, `private`, `unlisted`.

2. **Kanal va Video Analitikasi (Analytics & Tracking)**:
   - Kanalning umumiy statistikasi: jami obunachilar, umumiy ko'rishlar, videolar soni.
   - So'nggi videolarning aniq metrikalari: har bir videoning ko'rishlar soni, layklar, izohlar soni.

3. **YouTube AI Content Agent**:
   - **SEO Metadata**: Yuqori CTR beruvchi sarlavhalar (3-5 ta variant), qidiruvga mos tavsif (description), kalit teglar va tomoshabinni jalb qiluvchi birinchi qadalgan izoh (pinned comment).
   - **Thumbnail g'oyalari**: Diqqatni tortuvchi vizual elementlar, kontrast ranglar va matn takliflari.
   - **Shorts Ssenariylari**: Dastlabki 3 soniyada tomoshabinni to'xtatuvchi kuchli HOOK, dinamik qadamlar, ovoz/vizual ko'rsatmalar va Call To Action (CTA).

4. **Avtomatik Video Generator (.MP4 yaratish)**:
   - **Neural TTS (Ovozlashtirish)**: Edge-TTS orqali o'zbek (`uz-UZ-SardorNeural`, `uz-UZ-MadinaNeural`), rus va ingliz tillarida tabiiy inson ovozi.
   - **Vizual kartalar**: Pillow orqali 1080x1920 o'lchamdagi vertikal estetik kartalar, badge va markazlashtirilgan matnlar.
   - **FFmpeg montaji**: Ovoz va slaydlarni birlashtirib, YouTube Shorts uchun tayyor `.mp4` video hosil qiladi.

---

## Modul tuzilishi

- [`backend/app/integrations/youtube/client.py`](../backend/app/integrations/youtube/client.py) — YouTube Data API v3 async httpx mijozi.
- [`backend/app/integrations/youtube/schemas.py`](../backend/app/integrations/youtube/schemas.py) — Video, kanal va yuklash modellari.
- [`backend/app/integrations/youtube/errors.py`](../backend/app/integrations/youtube/errors.py) — Xatoliklar boshqaruvi (kvota, tarmoq, autentifikatsiya).
- [`backend/app/integrations/youtube/video_generator.py`](../backend/app/integrations/youtube/video_generator.py) — Avtomatik video generator (TTS + Pillow + FFmpeg).
- [`backend/app/agents/youtube.py`](../backend/app/agents/youtube.py) — AI YouTube Agent (sarlavhalar, ssenariy, tavsif).
- [`backend/app/api/v1/youtube.py`](../backend/app/api/v1/youtube.py) — FastAPI REST endpointlari.
- [`youtube_agent.py`](../youtube_agent.py) — Qulay terminal (CLI) boshqaruv paneli.
