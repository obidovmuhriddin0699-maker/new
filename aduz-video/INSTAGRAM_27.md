# 27-qism — Instagram Reels uchun tayyor paket

| Fayl | Nima |
|---|---|
| `ADUZ_27-qism.mp4` | Reels videosi: 1080×1920, 9:16, 30 fps, H.264 High 4.1, AAC 48 kHz 256k, 32 s, −14 LUFS (integral ≈ −12.8), cho'qqi −1.9 dBFS, `faststart` |
| `ADUZ_27-qism_cover.jpg` | Muqova (1080×1920). Asosiy matn ("62% KUYYAPTI") profil to'ridagi 3:4 kesimga ham sig'adi |
| `SOUND_ARCHITECTURE_27.md` | Ovoz cue-sheet |

## Videoda nima Reels uchun moslangan

- **Hook kadr 0 da.** Qorong'idan ochilish yo'q: birinchi kadrdayoq to'q sariq fonda "62% KUYYAPTI" va zarba ovozi. Lentada aylantirayotgan odam birinchi soniyada to'xtashi kerak.
- **Tez ritm.** Har 1–2 soniyada yangi voqea: tanga uchishi, kanal yonishi, slab-karta, kesim.
- **Xavfsiz zona.** Barcha matn va asosiy grafika Instagram tugmalari ostida qolmaydi:
  - yuqoridagi ~250 px bo'sh;
  - pastdagi ~460 px bo'sh (izoh, ism, musiqa yozuvi shu yerda);
  - o'ng ustunda (like / izoh / ulashish) y ≈ 1060 dan pastda matn yo'q.
  - Tekshirish: `node render.mjs episode27.html --stills=… --safe` zonalarni qizil bilan ko'rsatadi.
- **Katta subtitrlar.** Ko'pchilik ovozsiz ko'radi, shuning uchun matn ekranga "yopishtirilgan".
- **Izoh-CTA.** Yakunda "IZOHGA YOZING: BYUDJET" chiqadi — izohlar videoning tarqalishiga yordam beradi. Yonida "saqlab qo'ying" chaqirig'i ham bor.
- **Cheksiz loop.** Oxirgi 0.6 s boshidagi kadrni qayta quradi. Video qayta boshlanganda chok sezilmaydi, ovozdagi riser ham kadr 0 dagi zarbaga ulanadi. Qayta ko'rishlar soni oshadi.
- **Ovoz.** Original musiqa va SFX (meme treklari yo'q), shuning uchun mualliflik huquqi sababli ovoz o'chirilmaydi.

## Post matni (nusxa oling)

```
Reklama pulingizning 62% i oʻlik kanallarda kuyyaptimi?

Byudjet hamma kanalga teng boʻlinsa — botlar koʻradi, pul havoga ketadi.
ADUZ jonli optimizatsiyasi oʻlik kanallarni toʻxtatadi va pulni faqat foyda keltirayotgan kanallarga yoʻnaltiradi.

Izohga BYUDJET deb yozing — kanalni tekshirish roʻyxatini yuboramiz.
Saqlab qoʻying, keyingi kampaniyada kerak boʻladi.

#telegramreklama #reklama #biznes #fargona #aduz
```

**Alt matn** (Instagram → Kengaytirilgan sozlamalar → Alt matn):
> ADUZ promo animatsiyasi: reklama byudjetining 62% i oʻlik Telegram kanallarida kuyishi, so'ng ADUZ jonli optimizatsiyasi pulni jonli kanallarga qayta taqsimlashi.

## Joylashda (tavsiya)

1. **Faylni yuklash.** `ADUZ_27-qism.mp4` faylini telefonga asl sifatda o'tkazing (Telegram'da "fayl" sifatida yuboring, siqilmaydi). Instagram ilovasida Sozlamalar → Ma'lumotlardan foydalanish → **"Yuqori sifatda yuklash"**ni yoqing.
2. **Muqova.** "Muqovani tahrirlash" → "Kamera roliklaridan qo'shish" → `ADUZ_27-qism_cover.jpg`.
3. **Musiqa qo'shmang.** Video o'z ovozi bilan chiqsin (original audio). Ustiga trend musiqa qo'yilsa SFX va zarbalar yo'qoladi.
4. **"Izohga BYUDJET" va'dasi.** CTA ishlashi uchun izoh yozganlarga haqiqatan nimadir yuborish kerak. Ro'yxat matnini oldindan tayyorlab qo'ying (yoki avto-javob sozlang).
5. **Birinchi soat.** Izohlarga tez javob bering — bu tarqalish uchun eng muhim signal.
6. **Joylash vaqti.** Auditoriyangiz faol bo'lgan vaqtni Instagram statistikasidan (Professional panel → Auditoriya) qarang.

**Namuna — tekshiring:** 62%, 3 000 000 so'm, 1 860 000 so'm tejaldi, "×3 mijoz", kanal nomlari va ERR qiymatlari, "jonli optimizatsiya" funksiyasining o'zi — ADUZ'ning haqiqiy ko'rsatkichlari bilan almashtiring. `#aduz` heshtegi va akkaunt nomini o'zingiznikiga moslang.
