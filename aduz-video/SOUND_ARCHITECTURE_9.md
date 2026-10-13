# ADUZ 9-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 9 --cuesheet SOUND_ARCHITECTURE_9.md`).

## Qatlamlar

| Qatlam | Nomi | Vazifasi |
|---|---|---|
| L1 | Musiqa (score) | Pad, klavishlar, bas, baraban, melodiya. Kick'dan sidechain; 2,2–4,2 kHz diktor uchun bo'shatilgan. |
| L2 | Muhit (ambience) | Sahna 'xonasi': ofis shovqini, havo. Juda past, sezilmas — lekin sukunatni 'jonli' qiladi. |
| L3 | UI / foley | Bosish, tanlash, slider, popup, xato. Musiqa tonalligiga sozlangan. |
| L4 | O'tishlar | Whoosh, swell, riser, squeegee, whip. J-cut: tovush kesimdan oldin boshlanadi. |
| L5 | Zarbalar / urg'u | Boom, crash, glitch, uchqunlar. Kinetik so'zlar bilan bir kadrda. |
| L6 | Brend (sonic logo) | ADUZ ovozli logotipi: 5–1–3 motiv (qo'ng'iroq + elektro-pianino + sub). |
| L7 | Diktor joyi | Hozircha bo'sh. Diktor qo'shilsa: musiqa −6 dB ducking, SFX −3 dB. |

## Tovushlar kutubxonasi

| Nomi | Qatlam | Tavsif |
|---|---|---|
| `amb.office` | L2 | Ofis fon shovqini: past 'xona tovushi', ventilyatsiya, 50 Hz g'uvullash |
| `amb.air` | L2 | Yorug', ochiq havo — yechim sahnasi muhiti |
| `ui.popup` | L3 | Yumshoq 'pop' — popup paydo bo'lishi (balandligi sozlanadi) |
| `ui.dropdown` | L3 | Ochiluvchi ro'yxat 'shitirlashi' (5 ta tez tik) |
| `ui.error` | L3 | Xato: pastga tushuvchi ikki nota + glitch |
| `ui.tap` | L3 | Barmoq bosishi |
| `ui.select` | L3 | Tanlash: klik + tonallikdagi qo'ng'iroqcha |
| `ui.slider` | L3 | Slider qadami: ko'tariluvchi mayda tik |
| `ui.next` | L3 | 'Keyingi': ikki nota yuqoriga |
| `ui.launch` | L3 | Ishga tushirish: ko'tariluvchi ton + shovqin |
| `ui.success` | L3 | Muvaffaqiyat: D-major arpedjio akkordi |
| `fx.fragment` | L3 | Suzuvchi jargon bo'lagi: bit-crush 'blip' |
| `fx.strike` | L3 | Matn ustidan chizish: tushuvchi 'chirt' |
| `fx.collapse` | L5 | Ilova yopilishi: pastga 'so'rilish' + zarba |
| `fx.heartbeat` | L5 | Yurak urishi — ovoz vakuumi ichida |
| `tr.whoosh` | L4 | Yumshoq whoosh: telefon/ekran kirishi |
| `tr.slide` | L4 | Ekranlar orasida sirpanish |
| `tr.swell` | L4 | Teskari swell (J-cut): keyingi kadrga 'nafas' |
| `tr.riser` | L4 | Riser — keskin kesiladi (montaj usuli) |
| `tr.squeegee` | L4 | Squeegee o'tishi: yuqori chastotali 'shirr' + rezina g'ichirlashi |
| `tr.whip` | L4 | Whip-pan: chapdan o'ngga tez o'tuvchi whoosh |
| `imp.glitch` | L5 | Qizil kinetik so'z zarbasi |
| `imp.boom` | L5 | Katta zarba: sub + thump |
| `imp.clap` | L5 | Zarba ustidagi clap qatlami |
| `imp.crash` | L5 | Crash tarelka (yumshatilgan) |
| `imp.sparkle` | L5 | Uchqunlar: D-pentatonik qo'ng'iroqchalar to'dasi |
| `brand.logo` | L6 | ADUZ sonic logo (5–1–3 motiv) |
| `fx.window` | L3 | Oyna ochilishi: yumshoq 'bloop' (balandligi sozlanadi) |
| `fx.paper` | L3 | Qog'oz shitirlashi (daftar, chek) |
| `fx.sticky` | L3 | Stiker 'shap' etib yopishishi |
| `fx.tab` | L3 | Brauzer tabi ochilishi |
| `fx.magnet` | L4 | Magnit maydoni: ko'tariluvchi tremolo g'uvullash |
| `fx.absorb` | L5 | Bo'lak magnitga 'yutilishi': pastga tushuvchi ton + thump |
| `fx.snap` | L3 | Karta joyiga 'chiq' etib tushishi |
| `ui.cart` | L3 | Savatchaga qo'shish: pop + qo'ng'iroqcha |
| `ui.pay` | L3 | To'lov: klik + muvaffaqiyat akkordi |
| `fx.pulse` | L3 | Hub impulsi: ma'lumot oqimi |
| `tr.implode` | L4 | Implosion: hamma narsa markazga so'riladi |
| `tr.flip` | L4 | Karta aylanishi: ikki marta 'fvip' |
| `fx.knob` | L3 | Murvat aylantirish: zinali 'chiq-chiq' (ratchet) |
| `fx.detent` | L3 | Bitta murvat qadami — pult elementi paydo bo'lishi |
| `fx.switch` | L3 | Tumbler: metall 'chiq' + past thunk |
| `fx.slider` | L3 | Slayder ishqalanishi |
| `fx.lcd` | L3 | LCD yonishi: qisqa beep + elektr g'uvullash |
| `fx.alarm` | L5 | Ogohlantirish signali (C-minor tonallikda) |
| `fx.relay` | L1 | Rele chiqillashi — muammo sahnasining 'hi-hat'i |
| `tr.crt_off` | L4 | Eski televizor o'chishi: chiyillash + thoomp + chirsillash |
| `tr.boot` | L4 | ADUZ yonishi: Eb-major arpedjio |
| `fx.token` | L3 | AI so'zni ajratdi: shisha shimmer (balandligi sozlanadi) |
| `fx.think` | L3 | AI 'o'ylayapti': mayda qo'ng'iroqcha uchqunlari |
| `fx.type` | L3 | Yumshoq klaviatura bosishi |
| `tr.glitch` | L4 | Digital glitch o'tishi: bit-stutter |
| `fx.nope` | L3 | 'Oldin' qatori: past ikki nota (rad) |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:10.4 | Muammo · C-minor, mexanik | Hi-hat o'rnida rele chiqillashi (16-lik), filtrlangan bas pulsi, Cm pad; 5.5 s dan kick. Pult tovushlari musiqaning bir qismi bo'lib eshitiladi. |
| 0:10.4–0:10.8 | Televizor o'chishi | Gate: musiqa va dumlar keskin kesiladi, faqat TV o'chish tovushi qoladi; keyin ADUZ Eb-major arpedjio bilan 'yonadi'. |
| 0:11–0:21.75 | Yechim · Eb-major, future-garage | Siljigan (shuffle) hat'lar, sinkopali kick, reverb'li snare 2 va 4 da, Rhodes Eb–Cm–Ab–Bb, sub, delay'li pluck arpedjio. AI 'o'ylaganda' shimmer qatlami. |
| 0:22–0:27 | Natija · Ab-major, ko'tarilish | Ab–Eb–Fm–Db: to'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. |
| 0:27–0:32 | Yakun · brend | Db → Eb, ADUZ sonic logo (Eb tonikada), so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -22 dB | C | 0% | Xona: pult g'uvullashi |
| 0:00.50 | L3 | `fx.detent` | -13 dB | L75 | 15% | Murvat #1 paydo bo'ldi |
| 0:00.60 | L3 | `fx.detent` | -13 dB | L25 | 15% | Murvat #2 paydo bo'ldi |
| 0:00.70 | L3 | `fx.detent` | -13 dB | R25 | 15% | Murvat #3 paydo bo'ldi |
| 0:00.80 | L3 | `fx.detent` | -13 dB | R75 | 15% | Murvat #4 paydo bo'ldi |
| 0:00.90 | L3 | `fx.detent` | -13 dB | L75 | 15% | Murvat #5 paydo bo'ldi |
| 0:01.00 | L3 | `fx.detent` | -13 dB | L25 | 15% | Murvat #6 paydo bo'ldi |
| 0:01.10 | L3 | `fx.detent` | -13 dB | R25 | 15% | Murvat #7 paydo bo'ldi |
| 0:01.20 | L3 | `fx.detent` | -13 dB | R75 | 15% | Murvat #8 paydo bo'ldi |
| 0:01.30 | L3 | `fx.detent` | -17 dB | L80 | 10% | Slayder #1 |
| 0:01.37 | L3 | `fx.detent` | -17 dB | L62 | 10% | Slayder #2 |
| 0:01.44 | L3 | `fx.detent` | -17 dB | L44 | 10% | Slayder #3 |
| 0:01.51 | L3 | `fx.detent` | -17 dB | L26 | 10% | Slayder #4 |
| 0:01.58 | L3 | `fx.detent` | -17 dB | L8 | 10% | Slayder #5 |
| 0:01.65 | L3 | `fx.detent` | -17 dB | R10 | 10% | Slayder #6 |
| 0:01.72 | L3 | `fx.detent` | -17 dB | R28 | 10% | Slayder #7 |
| 0:01.79 | L3 | `fx.detent` | -17 dB | R46 | 10% | Slayder #8 |
| 0:01.86 | L3 | `fx.detent` | -17 dB | R64 | 10% | Slayder #9 |
| 0:01.93 | L3 | `fx.detent` | -17 dB | R82 | 10% | Slayder #10 |
| 0:02.00 | L3 | `fx.lcd` | -12 dB | L30 | 20% | LCD displey yondi |
| 0:02.10 | L3 | `fx.detent` | -18 dB | R40 | 10% | F1 tugmasi |
| 0:02.15 | L3 | `fx.detent` | -18 dB | R48 | 10% | F2 tugmasi |
| 0:02.20 | L3 | `fx.detent` | -18 dB | R56 | 10% | F3 tugmasi |
| 0:02.25 | L3 | `fx.detent` | -18 dB | R64 | 10% | F4 tugmasi |
| 0:02.30 | L3 | `fx.detent` | -18 dB | R72 | 10% | F5 tugmasi |
| 0:02.35 | L3 | `fx.detent` | -18 dB | R80 | 10% | F6 tugmasi |
| 0:02.40 | L3 | `fx.switch` | -18 dB | L75 | 10% | Tumbler #1 |
| 0:02.46 | L3 | `fx.switch` | -18 dB | L45 | 10% | Tumbler #2 |
| 0:02.52 | L3 | `fx.switch` | -18 dB | L15 | 10% | Tumbler #3 |
| 0:02.58 | L3 | `fx.switch` | -18 dB | R15 | 10% | Tumbler #4 |
| 0:02.64 | L3 | `fx.switch` | -18 dB | R45 | 10% | Tumbler #5 |
| 0:02.70 | L3 | `fx.switch` | -18 dB | R75 | 10% | Tumbler #6 |
| 0:02.76 | L3 | `fx.switch` | -18 dB | L75 | 10% | Tumbler #7 |
| 0:02.82 | L3 | `fx.switch` | -18 dB | L45 | 10% | Tumbler #8 |
| 0:02.88 | L3 | `fx.switch` | -18 dB | L15 | 10% | Tumbler #9 |
| 0:02.94 | L3 | `fx.switch` | -18 dB | R15 | 10% | Tumbler #10 |
| 0:03.00 | L3 | `fx.switch` | -18 dB | R45 | 10% | Tumbler #11 |
| 0:03.06 | L3 | `fx.switch` | -18 dB | R75 | 10% | Tumbler #12 |
| 0:03.60 | L3 | `fx.knob` | -9 dB | L30 | 15% | Qo'l CPM murvatini aylantiradi |
| 0:04.60 | L3 | `fx.switch` | -8 dB | R10 | 20% | AUTO-BID yoqildi |
| 0:04.68 | L5 | `fx.alarm` | -13 dB | L30 | 30% | LCD: XATO — sozlamalar zid |
| 0:05.20 | L3 | `fx.slider` | -10 dB | L70 | 15% | YOSH slayderi suriladi |
| 0:05.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: QAYSI BIRINI? |
| 0:06.20 | L5 | `fx.alarm` | -20 dB | R60 | 30% | Chiroqlar miltillaydi |
| 0:06.60 | L5 | `imp.glitch` | -8 dB | R40 | 25% | Slam: XATO = PUL YO'Q |
| 0:07.20 | L5 | `fx.alarm` | -18 dB | L60 | 30% | Signallar tezlashadi |
| 0:07.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: O'RGANISH — 1 HAFTA |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.50 | L5 | `imp.boom` | -3 dB | C | 40% | 36 TA TUGMA — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -8 dB | C | 50% | Zarba qatlami |
| 0:08.50 | L5 | `imp.crash` | -11 dB | C | 0% | Zarba qatlami |
| 0:08.60 | L4 | `tr.riser` | -10 dB | C | 0% | Riser — televizor o'chishi bilan uziladi |
| 0:10.40 | L4 | `tr.crt_off` | -4 dB | C | 0% | ESKI TV O'CHADI — musiqa gate bilan kesiladi |
| 0:10.70 | L4 | `tr.boot` | -9 dB | C | 40% | ADUZ yonadi (Eb-major) |
| 0:11.00 | L5 | `imp.boom` | -7 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit |
| 0:11.30 | L4 | `tr.whoosh` | -15 dB | C | 20% | Prompt kartasi |
| 0:11.80 | L3 | `fx.type` | -20 dB | C | 5% | Gap yozilmoqda |
| 0:11.86 | L3 | `fx.type` | -20 dB | R13 | 5% | Gap yozilmoqda |
| 0:11.93 | L3 | `fx.type` | -20 dB | R14 | 5% | Gap yozilmoqda |
| 0:11.99 | L3 | `fx.type` | -20 dB | C | 5% | Gap yozilmoqda |
| 0:12.05 | L3 | `fx.type` | -20 dB | L11 | 5% | Gap yozilmoqda |
| 0:12.11 | L3 | `fx.type` | -20 dB | L14 | 5% | Gap yozilmoqda |
| 0:12.18 | L3 | `fx.type` | -20 dB | C | 5% | Gap yozilmoqda |
| 0:12.24 | L3 | `fx.type` | -20 dB | R10 | 5% | Gap yozilmoqda |
| 0:12.30 | L3 | `fx.type` | -20 dB | R15 | 5% | Gap yozilmoqda |
| 0:12.36 | L3 | `fx.type` | -20 dB | R6 | 5% | Gap yozilmoqda |
| 0:12.43 | L3 | `fx.type` | -20 dB | L8 | 5% | Gap yozilmoqda |
| 0:12.49 | L3 | `fx.type` | -20 dB | L15 | 5% | Gap yozilmoqda |
| 0:12.55 | L3 | `fx.type` | -20 dB | L8 | 5% | Gap yozilmoqda |
| 0:12.61 | L3 | `fx.type` | -20 dB | R6 | 5% | Gap yozilmoqda |
| 0:12.68 | L3 | `fx.type` | -20 dB | R15 | 5% | Gap yozilmoqda |
| 0:12.74 | L3 | `fx.type` | -20 dB | R10 | 5% | Gap yozilmoqda |
| 0:12.80 | L3 | `fx.type` | -20 dB | C | 5% | Gap yozilmoqda |
| 0:12.86 | L3 | `fx.type` | -20 dB | L14 | 5% | Gap yozilmoqda |
| 0:12.93 | L3 | `fx.type` | -20 dB | L11 | 5% | Gap yozilmoqda |
| 0:12.99 | L3 | `fx.type` | -20 dB | C | 5% | Gap yozilmoqda |
| 0:13.05 | L3 | `fx.type` | -20 dB | R14 | 5% | Gap yozilmoqda |
| 0:13.11 | L3 | `fx.type` | -20 dB | R13 | 5% | Gap yozilmoqda |
| 0:13.18 | L3 | `fx.type` | -20 dB | C | 5% | Gap yozilmoqda |
| 0:13.24 | L3 | `fx.type` | -20 dB | L13 | 5% | Gap yozilmoqda |
| 0:13.40 | L3 | `fx.think` | -13 dB | C | 40% | AI tahlil qilmoqda |
| 0:13.60 | L3 | `fx.token` | -13 dB | L40 | 35% | So'z ajratildi: Hudud |
| 0:13.90 | L3 | `fx.token` | -13 dB | L10 | 35% | So'z ajratildi: Auditoriya |
| 0:14.20 | L3 | `fx.token` | -13 dB | R20 | 35% | So'z ajratildi: Soha |
| 0:14.30 | L4 | `tr.slide` | -22 dB | L40 | 10% | Chip kartaga uchadi |
| 0:14.50 | L3 | `fx.token` | -13 dB | R50 | 35% | So'z ajratildi: Byudjet |
| 0:14.50 | L4 | `tr.slide` | -22 dB | L10 | 10% | Chip kartaga uchadi |
| 0:14.70 | L4 | `tr.slide` | -22 dB | R20 | 10% | Chip kartaga uchadi |
| 0:14.75 | L3 | `fx.snap` | -15 dB | L50 | 20% | Chip rejaga joylashdi |
| 0:14.90 | L4 | `tr.slide` | -22 dB | R50 | 10% | Chip kartaga uchadi |
| 0:14.95 | L3 | `fx.snap` | -15 dB | C | 20% | Chip rejaga joylashdi |
| 0:15.15 | L3 | `fx.snap` | -15 dB | R50 | 20% | Chip rejaga joylashdi |
| 0:15.35 | L3 | `fx.snap` | -15 dB | L50 | 20% | Chip rejaga joylashdi |
| 0:15.60 | L3 | `fx.think` | -14 dB | C | 40% | AI qo'shimcha taklif qilmoqda |
| 0:15.80 | L3 | `fx.token` | -12 dB | C | 40% | AI qo'shdi: VAQT |
| 0:16.10 | L3 | `fx.token` | -12 dB | R50 | 40% | AI qo'shdi: KANALLAR |
| 0:16.40 | L3 | `fx.type` | -22 dB | C | 5% | AI matn yozmoqda |
| 0:16.46 | L3 | `fx.type` | -22 dB | R19 | 5% | AI matn yozmoqda |
| 0:16.52 | L3 | `fx.type` | -22 dB | R10 | 5% | AI matn yozmoqda |
| 0:16.58 | L3 | `fx.type` | -22 dB | L14 | 5% | AI matn yozmoqda |
| 0:16.64 | L3 | `fx.type` | -22 dB | L18 | 5% | AI matn yozmoqda |
| 0:16.70 | L3 | `fx.type` | -22 dB | C | 5% | AI matn yozmoqda |
| 0:16.76 | L3 | `fx.type` | -22 dB | R20 | 5% | AI matn yozmoqda |
| 0:16.82 | L3 | `fx.type` | -22 dB | R6 | 5% | AI matn yozmoqda |
| 0:16.88 | L3 | `fx.type` | -22 dB | L17 | 5% | AI matn yozmoqda |
| 0:16.94 | L3 | `fx.type` | -22 dB | L15 | 5% | AI matn yozmoqda |
| 0:17.00 | L3 | `fx.type` | -22 dB | R8 | 5% | AI matn yozmoqda |
| 0:17.06 | L3 | `fx.type` | -22 dB | R20 | 5% | AI matn yozmoqda |
| 0:17.12 | L3 | `fx.type` | -22 dB | C | 5% | AI matn yozmoqda |
| 0:17.18 | L3 | `fx.type` | -22 dB | L19 | 5% | AI matn yozmoqda |
| 0:17.24 | L3 | `fx.type` | -22 dB | L12 | 5% | AI matn yozmoqda |
| 0:17.30 | L3 | `fx.type` | -22 dB | R12 | 5% | AI matn yozmoqda |
| 0:17.36 | L3 | `fx.type` | -22 dB | R19 | 5% | AI matn yozmoqda |
| 0:17.42 | L3 | `fx.type` | -22 dB | C | 5% | AI matn yozmoqda |
| 0:17.50 | L3 | `ui.popup` | -14 dB | C | 20% | Ishga tushirish tugmasi |
| 0:17.90 | L3 | `ui.tap` | -9 dB | R20 | 0% | Bosildi |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: 1 GAP oldidan |
| 0:18.15 | L3 | `ui.success` | -12 dB | C | 40% | Ishga tushdi |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | 1 GAP — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | Kampaniya ishga tushdi oynasi |
| 0:21.20 | L4 | `tr.riser` | -12 dB | C | 0% | J-cut: glitch oldidan |
| 0:21.75 | L4 | `tr.glitch` | -8 dB | C | 15% | Digital glitch o'tishi |
| 0:22.00 | L5 | `imp.boom` | -6 dB | C | 45% | Natija boshlanishi |
| 0:22.60 | L3 | `fx.slider` | -12 dB | R60 | 20% | Ajratuvchi chiziq suriladi |
| 0:22.90 | L3 | `fx.nope` | -13 dB | L50 | 20% | Oldin: 36 ta tugma |
| 0:23.20 | L3 | `fx.nope` | -13 dB | L50 | 20% | Oldin: 2 soat |
| 0:23.50 | L3 | `fx.nope` | -13 dB | L50 | 20% | Oldin: xato xavfi |
| 0:23.90 | L3 | `ui.select` | -15 dB | R50 | 30% | ADUZ: 1 ta gap |
| 0:24.20 | L3 | `ui.select` | -15 dB | R50 | 30% | ADUZ: 30 soniya |
| 0:24.50 | L3 | `ui.select` | -15 dB | R50 | 30% | ADUZ: AI tekshirgan |
| 0:24.50 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: pill oldidan |
| 0:25.00 | L5 | `imp.boom` | -8 dB | C | 40% | 240 barobar tezroq |
| 0:25.00 | L5 | `imp.sparkle` | -8 dB | C | 50% | Uchqunlar |
| 0:26.85 | L4 | `tr.whoosh` | -16 dB | C | 40% | Yakuniy kadrga |
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (Eb tonallikda) |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
