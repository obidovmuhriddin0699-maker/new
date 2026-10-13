# ADUZ 10-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 10 --cuesheet SOUND_ARCHITECTURE_10.md`).

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
| `fx.crumple` | L5 | Qoralama g'ijimlanadi: qog'oz chirsillashi |
| `fx.thud` | L5 | Qog'oz to'p yerga tushadi |
| `fx.fill` | L3 | Avtomatik to'ldirish 'domino'si: har sozlama o'z notasida |
| `fx.peg` | L3 | Omad g'ildiragi qozig'i ko'rsatkichdan o'tishi |
| `fx.clack` | L5 | G'ildirak to'xtadi: oxirgi 'tak' + thud |
| `fx.scan` | L3 | Matching skaneri: ko'tariluvchi tremolo ton |
| `fx.score` | L3 | Kanal bahosi: yuqori moslik — yuqori nota, past moslik — past nota |
| `fx.radar` | L3 | Radar diagramma ochilishi: sonar 'ping' |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:09.5 | Muammo · D-minor, tashvishli minimal | 7-qism aranjirovkasi 2 yarim ton pastda. Ustida omad g'ildiragi qoziqlari: boshida tez 'trrr' (soniyasiga ~30), keyin fizika bo'yicha sekinlashadi — har bir 'chiq' qoziq ko'rsatkichdan o'tgan kadrga tushadi. |
| 0:09.5–0:10.15 | Ovoz vakuumi | G'ildirak to'xtashi bilan musiqa kesiladi (gate). Sukunatda oxirgi 'tak' va yurak urishi: 'Moslik: 12%'. Keyin J-cut swell C-major'da. |
| 0:11–0:21.75 | Yechim · C-major, siyrak | Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Skaner har bir kanalni baholaganda baho notasi: yuqori moslik — baland nota, past moslik — past nota (C-pentatonik). Radar diagramma sonar 'ping'i bilan ochiladi. |
| 0:22–0:27 | Natija · C-major, to'liq | To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. |
| 0:27–0:32 | Yakun · brend | ADUZ sonic logo (C tonikada), so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -21 dB | C | 0% | Xona — sahna 'havosi' |
| 0:00.05 | L4 | `tr.whoosh` | -16 dB | R30 | 20% | Telefon kadrga kiradi |
| 0:00.60 | L3 | `ui.popup` | -23 dB | R20 | 15% | Katalog qatori #1 — 'moslik: ?' |
| 0:00.72 | L3 | `ui.popup` | -23 dB | R20 | 15% | Katalog qatori #2 — 'moslik: ?' |
| 0:00.84 | L3 | `ui.popup` | -23 dB | R20 | 15% | Katalog qatori #3 — 'moslik: ?' |
| 0:00.96 | L3 | `ui.popup` | -23 dB | R20 | 15% | Katalog qatori #4 — 'moslik: ?' |
| 0:01.08 | L3 | `ui.popup` | -23 dB | R20 | 15% | Katalog qatori #5 — 'moslik: ?' |
| 0:01.20 | L3 | `ui.popup` | -23 dB | R20 | 15% | Katalog qatori #6 — 'moslik: ?' |
| 0:01.32 | L3 | `ui.popup` | -23 dB | R20 | 15% | Katalog qatori #7 — 'moslik: ?' |
| 0:01.44 | L3 | `ui.popup` | -23 dB | R20 | 15% | Katalog qatori #8 — 'moslik: ?' |
| 0:01.70 | L3 | `ui.tap` | -26 dB | R30 | 0% | Ikkilanayotgan kursor |
| 0:02.10 | L3 | `ui.tap` | -26 dB | R30 | 0% | Ikkilanayotgan kursor |
| 0:02.50 | L3 | `ui.tap` | -26 dB | R30 | 0% | Ikkilanayotgan kursor |
| 0:02.90 | L3 | `ui.tap` | -26 dB | R30 | 0% | Ikkilanayotgan kursor |
| 0:03.30 | L3 | `ui.tap` | -26 dB | R30 | 0% | Ikkilanayotgan kursor |
| 0:03.40 | L3 | `ui.popup` | -16 dB | C | 20% | 'Tasodifiy tanlash' tugmasi |
| 0:04.30 | L3 | `ui.tap` | -9 dB | R20 | 0% | Tasodifiy tanlash bosildi |
| 0:04.50 | L4 | `tr.whoosh` | -13 dB | C | 30% | Omad g'ildiragi chiqadi |
| 0:05.03 | L3 | `fx.peg` | -16 dB | R10 | 10% | Qoziq #1 |
| 0:05.07 | L3 | `fx.peg` | -16 dB | R10 | 10% | Qoziq |
| 0:05.10 | L3 | `fx.peg` | -16 dB | R10 | 10% | Qoziq |
| 0:05.13 | L3 | `fx.peg` | -16 dB | R10 | 10% | Qoziq |
| 0:05.17 | L3 | `fx.peg` | -16 dB | R10 | 10% | Qoziq |
| 0:05.20 | L3 | `fx.peg` | -16 dB | R10 | 10% | Qoziq |
| 0:05.24 | L3 | `fx.peg` | -16 dB | R10 | 10% | Qoziq |
| 0:05.27 | L3 | `fx.peg` | -16 dB | R10 | 10% | Qoziq |
| 0:05.31 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.34 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.38 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq #11 |
| 0:05.41 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.45 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.49 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.52 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.56 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.60 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.60 | L5 | `imp.glitch` | -9 dB | L40 | 25% | Slam: TAXMIN? |
| 0:05.64 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.67 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.71 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.75 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq #21 |
| 0:05.79 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.83 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.87 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.91 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:05.96 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:06.00 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:06.04 | L3 | `fx.peg` | -15 dB | R10 | 10% | Qoziq |
| 0:06.08 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.13 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.17 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq #31 |
| 0:06.22 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.26 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.31 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.35 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.40 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.45 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.50 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.55 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.60 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.60 | L5 | `imp.glitch` | -9 dB | R40 | 25% | Slam: OMAD? |
| 0:06.65 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq #41 |
| 0:06.70 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.75 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.81 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.86 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.92 | L3 | `fx.peg` | -14 dB | R10 | 10% | Qoziq |
| 0:06.98 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.04 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.10 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.16 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.23 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq #51 |
| 0:07.29 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.36 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.43 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.50 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.58 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.60 | L5 | `imp.glitch` | -9 dB | L40 | 25% | Slam: TAVAKKAL! |
| 0:07.66 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.74 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.82 | L3 | `fx.peg` | -13 dB | R10 | 10% | Qoziq |
| 0:07.91 | L3 | `fx.peg` | -12 dB | R10 | 10% | Qoziq |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.01 | L3 | `fx.peg` | -12 dB | R10 | 10% | Qoziq #61 |
| 0:08.11 | L3 | `fx.peg` | -12 dB | R10 | 10% | Qoziq |
| 0:08.22 | L3 | `fx.peg` | -12 dB | R10 | 10% | Qoziq |
| 0:08.35 | L3 | `fx.peg` | -12 dB | R10 | 10% | Qoziq |
| 0:08.48 | L3 | `fx.peg` | -12 dB | R10 | 10% | Qoziq |
| 0:08.50 | L5 | `imp.boom` | -3 dB | C | 40% | 50 / 50 — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -9 dB | C | 50% | Zarba qatlami |
| 0:08.50 | L5 | `imp.crash` | -11 dB | C | 0% | Zarba qatlami |
| 0:08.64 | L3 | `fx.peg` | -12 dB | R10 | 10% | Qoziq |
| 0:08.83 | L3 | `fx.peg` | -12 dB | R10 | 10% | Qoziq |
| 0:09.12 | L3 | `fx.peg` | -11 dB | R10 | 10% | Qoziq |
| 0:09.50 | L5 | `fx.clack` | -6 dB | R10 | 0% | OVOZ VAKUUMI: g'ildirak to'xtadi — Toshkent Memlar |
| 0:09.75 | L5 | `fx.heartbeat` | -8 dB | C | 0% | Hukm: Moslik 12% |
| 0:10.15 | L4 | `tr.swell` | -8 dB | C | 30% | J-cut: yechim akkordi (C-major) |
| 0:10.55 | L3 | `ui.slider` | -24 dB | R60 | 20% | Piksel-dissolve uchqunlari |
| 0:10.58 | L3 | `ui.slider` | -24 dB | L60 | 20% | Piksel-dissolve |
| 0:10.61 | L3 | `ui.slider` | -24 dB | R60 | 20% | Piksel-dissolve |
| 0:10.64 | L3 | `ui.slider` | -24 dB | L60 | 20% | Piksel-dissolve |
| 0:10.68 | L3 | `ui.slider` | -24 dB | R60 | 20% | Piksel-dissolve |
| 0:10.71 | L3 | `ui.slider` | -24 dB | L60 | 20% | Piksel-dissolve |
| 0:10.74 | L3 | `ui.slider` | -24 dB | R60 | 20% | Piksel-dissolve |
| 0:10.77 | L3 | `ui.slider` | -24 dB | L60 | 20% | Piksel-dissolve |
| 0:10.80 | L3 | `ui.slider` | -24 dB | R60 | 20% | Piksel-dissolve |
| 0:10.83 | L3 | `ui.slider` | -24 dB | L60 | 20% | Piksel-dissolve |
| 0:10.86 | L3 | `ui.slider` | -24 dB | R60 | 20% | Piksel-dissolve |
| 0:10.89 | L3 | `ui.slider` | -24 dB | L60 | 20% | Piksel-dissolve |
| 0:10.93 | L3 | `ui.slider` | -24 dB | R60 | 20% | Piksel-dissolve |
| 0:10.96 | L3 | `ui.slider` | -24 dB | L60 | 20% | Piksel-dissolve |
| 0:11.00 | L5 | `imp.boom` | -6 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `tr.whoosh` | -15 dB | L30 | 20% | Telefon kiradi |
| 0:11.70 | L3 | `fx.snap` | -23 dB | L30 | 10% | Kanal qatori |
| 0:11.76 | L3 | `fx.snap` | -23 dB | L22 | 10% | Kanal qatori |
| 0:11.82 | L3 | `fx.snap` | -23 dB | L14 | 10% | Kanal qatori |
| 0:11.88 | L3 | `fx.snap` | -23 dB | L6 | 10% | Kanal qatori |
| 0:11.94 | L3 | `fx.snap` | -23 dB | C | 10% | Kanal qatori |
| 0:12.00 | L3 | `fx.snap` | -23 dB | R10 | 10% | Kanal qatori |
| 0:12.06 | L3 | `fx.snap` | -23 dB | R18 | 10% | Kanal qatori |
| 0:12.12 | L3 | `fx.snap` | -23 dB | R26 | 10% | Kanal qatori |
| 0:12.20 | L3 | `fx.scan` | -16 dB | C | 30% | Matching skaneri ro'yxatni kezadi |
| 0:12.30 | L3 | `fx.score` | -16 dB | L40 | 30% | Baho: 12% |
| 0:12.50 | L3 | `fx.score` | -13 dB | L30 | 30% | Baho: 94% |
| 0:12.70 | L3 | `fx.score` | -16 dB | L20 | 30% | Baho: 23% |
| 0:12.90 | L3 | `fx.score` | -13 dB | L10 | 30% | Baho: 91% |
| 0:13.10 | L3 | `fx.score` | -16 dB | C | 30% | Baho: 31% |
| 0:13.30 | L3 | `fx.score` | -13 dB | R10 | 30% | Baho: 88% |
| 0:13.50 | L3 | `fx.score` | -16 dB | R20 | 30% | Baho: 18% |
| 0:13.70 | L3 | `fx.score` | -13 dB | R30 | 30% | Baho: 76% |
| 0:14.10 | L4 | `tr.slide` | -15 dB | C | 15% | Ro'yxat moslik bo'yicha qayta tartiblanadi |
| 0:14.70 | L3 | `fx.snap` | -14 dB | C | 20% | Tartib joyiga tushdi |
| 0:14.80 | L3 | `ui.select` | -16 dB | L30 | 30% | Medal #1 |
| 0:14.92 | L3 | `ui.select` | -16 dB | C | 30% | Medal #2 |
| 0:15.04 | L3 | `ui.select` | -16 dB | R30 | 30% | Medal #3 |
| 0:15.60 | L3 | `ui.tap` | -10 dB | C | 0% | Eng mos kanal bosildi |
| 0:15.80 | L4 | `tr.slide` | -16 dB | C | 15% | 'Nega mos?' oynasi |
| 0:16.00 | L3 | `fx.radar` | -13 dB | C | 40% | Radar diagramma 'ping'i |
| 0:16.05 | L3 | `ui.launch` | -18 dB | C | 30% | Diagramma o'sadi |
| 0:17.60 | L3 | `ui.tap` | -9 dB | R10 | 0% | Tanlash bosildi |
| 0:17.85 | L3 | `ui.next` | -13 dB | C | 30% | Tanlandi |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: 94% MOSLIK oldidan |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | 94% MOSLIK — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Oltin uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | Eng mos kanallar tanlandi oynasi |
| 0:21.20 | L4 | `tr.riser` | -12 dB | C | 0% | J-cut: whip oldidan |
| 0:21.75 | L4 | `tr.whip` | -8 dB | C | 25% | Whip-pan o'tishi |
| 0:22.00 | L5 | `imp.boom` | -5 dB | C | 45% | Natija boshlanishi |
| 0:22.00 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:22.80 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Taxmin' qatori #1 chizildi |
| 0:23.00 | L3 | `ui.select` | -16 dB | R40 | 30% | Matching qatori #1 |
| 0:23.15 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Taxmin' qatori #2 chizildi |
| 0:23.35 | L3 | `ui.select` | -16 dB | R40 | 30% | Matching qatori #2 |
| 0:23.50 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Taxmin' qatori #3 chizildi |
| 0:23.70 | L3 | `ui.select` | -16 dB | R40 | 30% | Matching qatori #3 |
| 0:23.85 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Taxmin' qatori #4 chizildi |
| 0:24.05 | L3 | `ui.select` | -16 dB | R40 | 30% | Matching qatori #4 |
| 0:24.50 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: nishonlar oldidan |
| 0:25.00 | L5 | `imp.boom` | -8 dB | C | 40% | Urg'u |
| 0:25.00 | L5 | `imp.sparkle` | -7 dB | C | 50% | Uchqunlar |
| 0:25.20 | L3 | `ui.select` | -17 dB | L40 | 30% | Nishon #1 |
| 0:25.45 | L3 | `ui.select` | -17 dB | C | 30% | Nishon #2 |
| 0:25.70 | L3 | `ui.select` | -17 dB | R40 | 30% | Nishon #3 |
| 0:26.85 | L4 | `tr.whoosh` | -16 dB | C | 40% | Yakuniy kadrga |
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (C tonikada) |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
