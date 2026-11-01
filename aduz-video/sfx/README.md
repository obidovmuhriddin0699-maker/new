# ADUZ — SFX kutubxonasi

Foydalanuvchi yuborgan namunaviy videolardan kesib olingan 39 ta haqiqiy ovoz: 26 tasi — ikki SFX to'plami reklamasidan,
13 tasi — ikki "Text Animation Presets" videosidan (matn animatsiyalari ovozlari, 22-qismdan). 19-qismdan boshlab barcha motion roliklarda shu ovozlar ishlatiladi (`audio.py` → `sfx.<nom>`).

- Format: mono WAV, 44.1 kHz, 16-bit; boshidagi jimlik kesilgan, oxirida 30 ms fade, cho'qqi −1 dBFS.
- Har bir ovozni eshitib ko'rish: [`PREVIEW.mp4`](PREVIEW.mp4) — ekranda nomi va tavsifi bilan ketma-ket.
- Tavsiflar spektr va to'lqin shakli bo'yicha berilgan (taxminiy). Biror nom noto'g'ri bo'lsa, faylni qayta nomlash kifoya.
- Asl to'plam fayllari (yuqori sifatli WAV) qo'lga kirsa, xuddi shu nomlar bilan almashtiring — kod o'zgarmaydi.

| Fayl | Rol | Tavsif |
|---|---|---|
| `click_1` … `click_5` | L3 UI | Toza UI klik (≈1.7 kHz), 40 ms — tugma bosish, tanlash |
| `click_double_1/2` | L3 UI | Qo'sh klik — tasdiqlash |
| `pop_swish` | L3 UI | Qisqa "pop" + shuvullash — element paydo bo'lishi |
| `swipe` | L4 o'tish | Ekran/kartaning sirpanishi |
| `glitch_seq` | L5 zarba | Raqamli glitch ketma-ketligi (6 zarb, 1.1 s) |
| `notify_pop` | L3 UI | Bildirishnoma: ikki "pop" + dum |
| `notify_ring` | L3 UI | Bildirishnoma: jarangli "ding" |
| `hit_low` | L5 zarba | Past tonal zarba (≈260 Hz) + dum |
| `hit_chime` | L5 zarba | Tonal zarba, qo'ng'iroqsimon (≈390 Hz) |
| `hit_tone` | L5 zarba | Tonal zarba, 3-variant |
| `whoosh_soft` | L4 o'tish | Yumshoq whoosh (1.3 s) |
| `whoosh_sweep` | L4 o'tish | Whoosh, tonallik siljishi bilan |
| `ratchet_roll` | L3 UI | Tishli chiqillash, sekinlashuvchi (1.2 s) |
| `riser_click` | L4 o'tish | Riser: chiqillashlar bilan kuchayib, oxirida cho'qqi (≈1.12 s da) |
| `glitch_long` | L5 zarba | Uzun zich glitch / ma'lumot oqimi (1.8 s) |
| `glitch_noise` | L5 zarba | Shovqinli glitch (1.4 s) |
| `stutter` | L5 zarba | Stutter: 10 ta tez zarb |
| `glitch_short` | L5 zarba | Qisqa yuqori glitch (0.4 s) |
| `tick` | L3 UI | Mayda tik |
| `tick_roll` | L3 UI | 8 ta bir tekis tik — hisoblagich/yozish |
| `boom_sub` | L5 zarba | Sub-boom (≈58 Hz) + dum |
| `bass_drop` | L5 zarba | Past bass-zarba — matn chiqishi (bounce) |
| `tick_hi` | L3 UI | Yuqori matn tiki (≈6.5 kHz) — harflar |
| `shimmer` | L3 UI | Yaltiroq shimmer (≈8.7 kHz tonal) — flicker, flare |
| `type_burst` | L3 UI | Yozish shitirlashi — typewriter |
| `blip_up` | L3 UI | Ko'tariluvchi bliplar — letter-up |
| `sparkle_hit` | L5 zarba | Sparkle-zarba |
| `swoosh_text` | L4 o'tish | Matn whoosh'i — blur-fade, word-right |
| `whoosh_low` | L4 o'tish | Past whoosh / swell |
| `thump` | L5 zarba | Qisqa thump |
| `pluck_tone` | L3 UI | Tonal pluck (0.75 s) |
| `pop_short` | L3 UI | Qisqa pop |
| `click_soft` | L3 UI | Yumshoq klik |
| `chime_swell` | L3 UI | Chime-swell |

**Litsenziya:** bu ovozlar boshqa muallifning SFX to'plami reklamasidan olingan. Tijoriy reklamada ishlatishdan oldin
to'plamning litsenziyasini (yoki muallif ruxsatini) tekshiring.
