# ADUZ 12-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 12 --cuesheet SOUND_ARCHITECTURE_12.md`).

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
| `fx.transfer` | L3 | Pul o'tkazmasi: whoosh + tanga |
| `fx.coin` | L3 | Tanga jiringlashi |
| `fx.blocked` | L5 | 'Sizni blokladi': og'ir eshik yopilishi |
| `fx.fail` | L3 | Xabar yetib bormadi: qizil '!' |
| `fx.vault_lock` | L5 | Seyf qulflanishi: og'ir thunk + uch zinali latch + metall jarang |
| `fx.freeze` | L3 | Muzlatish: kristallanayotgan muz — zichlashib boruvchi shisha uchqunlar |
| `fx.melt` | L3 | Muz eriydi: tomchilar |
| `fx.tick` | L3 | Soat tiqillashi |
| `fx.dart_throw` | L3 | Dart uchishi: qisqa, yuqori chastotali 'fiyyu' |
| `fx.dart_hit` | L3 | Dart tegishi: yog'och 'tuk' + dumning titrashi |
| `fx.thunder` | L5 | Chaqmoq: keskin 'chars' + past gumburlash |
| `fx.breaker` | L5 | Elektr shiti yoqiladi: og'ir 'klak' |
| `fx.flicker` | L3 | Lyuminessent lampa: g'uvullab miltillash |
| `fx.blip` | L3 | Issiqlik xaritasi katagi: tonallikdagi 'blip' |
| `fx.bar` | L3 | Shahar ustuni o'sadi: ko'tariluvchi ton |
| `fx.ding` | L3 | Tavsiya lampochkasi: 'ding' |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:09.5 | Muammo · C-minor, tashvishli minimal | 7-qism aranjirovkasi 4 yarim ton pastda: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida 8 ta dart — har biri uchish 'fiyyu' + yog'och 'tuk', panorama dart tushgan joyga mos. 8.5 s da chaqmoq strob bilan bir kadrda. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: musiqa o'chadi; qorong'ida yana bitta dart uchadi va tegadi — ko'rinmaydi, faqat eshitiladi ('tegdimi, yo'qmi — noma'lum'). Yurak urishi. Keyin J-cut swell Bb-major'da. |
| 0:10.55–0:11 | Chiroq yonishi | Elektr shiti 'KLAK' → lyuminessent lampa ikki marta miltillab yonadi; ovoz tasvirdagi miltillash kadrlari bilan sinxron (10.58 / 10.68 / 10.77 s). |
| 0:11–0:21.75 | Yechim · Bb-major, siyrak | Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: jonli hisoblagich tiqillashi, issiqlik xaritasi diagonallari Bb-pentatonik zinapoyada, shahar ustunlari ko'tariluvchi tonlar, tavsiya 'ding', 'Qo'llash' → ko'rishlar o'sishi (yuqoriga yuruvchi blip). |
| 0:22–0:27 | Natija · Bb-major, to'liq | To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. To'rtta dart nishon markaziga — har tegishda tonallikdagi tasdiq ohangi. |
| 0:27–0:32 | Yakun · brend | ADUZ sonic logo (Bb tonikada), so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -22 dB | C | 0% | Qorong'i xona — sahna 'havosi' |
| 0:00.20 | L3 | `fx.switch` | -16 dB | L20 | 20% | Fonar yoqiladi |
| 0:00.80 | L3 | `ui.popup` | -18 dB | C | 20% | Reklama posti: 'Statistika mavjud emas' |
| 0:01.05 | L3 | `fx.dart_throw` | -17 dB | L14 | 15% | Dart #1 otildi |
| 0:01.40 | L3 | `fx.dart_hit` | -10 dB | L27 | 30% | Dart #1 — qorong'ida tegdi |
| 0:01.95 | L3 | `fx.dart_throw` | -17 dB | R16 | 15% | Dart #2 otildi |
| 0:02.30 | L3 | `fx.dart_hit` | -10 dB | R33 | 30% | Dart #2 — qorong'ida tegdi |
| 0:02.85 | L3 | `fx.dart_throw` | -17 dB | C | 15% | Dart #3 otildi |
| 0:03.20 | L3 | `fx.dart_hit` | -10 dB | L8 | 30% | Dart #3 — qorong'ida tegdi |
| 0:03.75 | L3 | `fx.dart_throw` | -17 dB | R12 | 15% | Dart #4 otildi |
| 0:04.10 | L3 | `fx.dart_hit` | -10 dB | R24 | 30% | Dart #4 — qorong'ida tegdi |
| 0:04.65 | L3 | `fx.dart_throw` | -17 dB | L17 | 15% | Dart #5 otildi |
| 0:05.00 | L3 | `fx.dart_hit` | -10 dB | L34 | 30% | Dart #5 — qorong'ida tegdi |
| 0:05.55 | L3 | `fx.dart_throw` | -17 dB | R6 | 15% | Dart #6 otildi |
| 0:05.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: NATIJA? |
| 0:05.90 | L3 | `fx.dart_hit` | -10 dB | R11 | 30% | Dart #6 — qorong'ida tegdi |
| 0:06.45 | L3 | `fx.dart_throw` | -17 dB | R20 | 15% | Dart #7 otildi |
| 0:06.60 | L5 | `imp.glitch` | -8 dB | R40 | 25% | Slam: KIM KO'RDI? |
| 0:06.80 | L3 | `fx.dart_hit` | -10 dB | R40 | 30% | Dart #7 — qorong'ida tegdi |
| 0:07.35 | L3 | `fx.dart_throw` | -17 dB | L9 | 15% | Dart #8 otildi |
| 0:07.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: QACHON? |
| 0:07.70 | L3 | `fx.dart_hit` | -10 dB | L18 | 30% | Dart #8 — qorong'ida tegdi |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: chaqmoq oldidan |
| 0:08.50 | L5 | `fx.thunder` | -5 dB | C | 30% | CHAQMOQ — strob bilan bir kadrda |
| 0:08.50 | L5 | `imp.boom` | -4 dB | C | 40% | QORONG'IDA — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -10 dB | C | 50% | Zarba qatlami |
| 0:08.60 | L4 | `tr.riser` | -11 dB | C | 0% | Riser — 9.5 s da keskin kesiladi |
| 0:09.60 | L3 | `fx.dart_throw` | -16 dB | R30 | 0% | OVOZ VAKUUMI: yana bitta o'q... |
| 0:09.95 | L3 | `fx.dart_hit` | -10 dB | R50 | 0% | ...tegdimi, yo'qmi — noma'lum |
| 0:09.95 | L5 | `fx.heartbeat` | -9 dB | C | 0% | Yurak urishi |
| 0:10.15 | L4 | `tr.swell` | -8 dB | C | 30% | J-cut: yechim akkordi (Bb-major) |
| 0:10.55 | L5 | `fx.breaker` | -6 dB | C | 0% | Chiroq kaliti: 'KLAK' |
| 0:10.58 | L3 | `fx.flicker` | -10 dB | L20 | 0% | Lampa miltillashi #1 |
| 0:10.68 | L3 | `fx.flicker` | -10 dB | R20 | 0% | Lampa miltillashi #2 |
| 0:10.77 | L3 | `fx.flicker` | -12 dB | C | 0% | Lampa yonib qoladi |
| 0:11.00 | L5 | `imp.boom` | -6 dB | C | 35% | Yechim boshlanishi — CHIROQ YONDI |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `tr.whoosh` | -15 dB | L30 | 20% | Telefon kiradi |
| 0:11.50 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:12.00 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:12.00 | L3 | `fx.blip` | -23 dB | L50 | 20% | Issiqlik katagi diagonali 1/18 |
| 0:12.09 | L3 | `fx.blip` | -23 dB | L44 | 20% | Issiqlik katagi diagonali 2/18 |
| 0:12.18 | L3 | `fx.blip` | -23 dB | L38 | 20% | Issiqlik katagi diagonali 3/18 |
| 0:12.27 | L3 | `fx.blip` | -23 dB | L32 | 20% | Issiqlik katagi diagonali 4/18 |
| 0:12.36 | L3 | `fx.blip` | -23 dB | L26 | 20% | Issiqlik katagi diagonali 5/18 |
| 0:12.44 | L3 | `fx.blip` | -23 dB | L21 | 20% | Issiqlik katagi diagonali 6/18 |
| 0:12.50 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:12.53 | L3 | `fx.blip` | -23 dB | L15 | 20% | Issiqlik katagi diagonali 7/18 |
| 0:12.62 | L3 | `fx.blip` | -23 dB | L9 | 20% | Issiqlik katagi diagonali 8/18 |
| 0:12.71 | L3 | `fx.blip` | -23 dB | C | 20% | Issiqlik katagi diagonali 9/18 |
| 0:12.80 | L3 | `fx.blip` | -23 dB | C | 20% | Issiqlik katagi diagonali 10/18 |
| 0:12.89 | L3 | `fx.blip` | -23 dB | R9 | 20% | Issiqlik katagi diagonali 11/18 |
| 0:12.98 | L3 | `fx.blip` | -23 dB | R15 | 20% | Issiqlik katagi diagonali 12/18 |
| 0:13.00 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:13.07 | L3 | `fx.blip` | -23 dB | R21 | 20% | Issiqlik katagi diagonali 13/18 |
| 0:13.16 | L3 | `fx.blip` | -23 dB | R26 | 20% | Issiqlik katagi diagonali 14/18 |
| 0:13.24 | L3 | `fx.blip` | -23 dB | R32 | 20% | Issiqlik katagi diagonali 15/18 |
| 0:13.33 | L3 | `fx.blip` | -23 dB | R38 | 20% | Issiqlik katagi diagonali 16/18 |
| 0:13.42 | L3 | `fx.blip` | -23 dB | R44 | 20% | Issiqlik katagi diagonali 17/18 |
| 0:13.50 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:13.51 | L3 | `fx.blip` | -23 dB | R50 | 20% | Issiqlik katagi diagonali 18/18 |
| 0:13.70 | L5 | `imp.glitch` | -20 dB | R30 | 20% | Qaynoq katak #1 |
| 0:13.80 | L3 | `fx.bar` | -17 dB | L20 | 20% | Shahar ustuni #1 |
| 0:13.82 | L5 | `imp.glitch` | -20 dB | R30 | 20% | Qaynoq katak #2 |
| 0:13.94 | L5 | `imp.glitch` | -20 dB | R30 | 20% | Qaynoq katak #3 |
| 0:13.94 | L3 | `fx.bar` | -17 dB | L20 | 20% | Shahar ustuni #2 |
| 0:14.00 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:14.08 | L3 | `fx.bar` | -17 dB | L20 | 20% | Shahar ustuni #3 |
| 0:14.22 | L3 | `fx.bar` | -17 dB | L20 | 20% | Shahar ustuni #4 |
| 0:14.36 | L3 | `fx.bar` | -17 dB | L20 | 20% | Shahar ustuni #5 |
| 0:14.50 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:15.00 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:15.20 | L3 | `fx.ding` | -12 dB | R10 | 35% | Tavsiya: 20:00 ga ko'chiring |
| 0:15.50 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:16.00 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:16.00 | L3 | `ui.tap` | -9 dB | R30 | 0% | 'Qo'llash' bosildi |
| 0:16.20 | L3 | `ui.select` | -13 dB | R30 | 30% | Qo'llandi ✓ |
| 0:16.50 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:16.50 | L3 | `fx.blip` | -20 dB | R40 | 25% | +ko'rish #1 |
| 0:16.65 | L3 | `fx.blip` | -20 dB | R32 | 25% | +ko'rish #2 |
| 0:16.80 | L3 | `fx.blip` | -20 dB | R24 | 25% | +ko'rish #3 |
| 0:16.95 | L3 | `fx.blip` | -20 dB | R16 | 25% | +ko'rish #4 |
| 0:17.00 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:17.10 | L3 | `fx.blip` | -20 dB | R8 | 25% | +ko'rish #5 |
| 0:17.25 | L3 | `fx.blip` | -20 dB | C | 25% | +ko'rish #6 |
| 0:17.50 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:18.00 | L3 | `fx.tick` | -26 dB | R35 | 0% | Jonli hisoblagich |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: CHIROQ YONDI oldidan |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | CHIROQ YONDI — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Oltin uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | Hammasi ko'z oldingizda oynasi |
| 0:21.20 | L4 | `tr.riser` | -12 dB | C | 0% | J-cut: whip oldidan |
| 0:21.75 | L4 | `tr.whip` | -8 dB | C | 25% | Whip-pan o'tishi |
| 0:22.00 | L5 | `imp.boom` | -5 dB | C | 45% | Natija boshlanishi |
| 0:22.00 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:22.25 | L3 | `fx.dart_throw` | -18 dB | C | 15% | Nishonga dart #1 |
| 0:22.50 | L3 | `fx.dart_hit` | -12 dB | C | 30% | Markazga tegdi #1 |
| 0:22.52 | L3 | `ui.select` | -20 dB | R20 | 30% | Tegdi — tasdiq #1 |
| 0:22.55 | L3 | `fx.dart_throw` | -18 dB | C | 15% | Nishonga dart #2 |
| 0:22.80 | L3 | `fx.dart_hit` | -12 dB | C | 30% | Markazga tegdi #2 |
| 0:22.82 | L3 | `ui.select` | -20 dB | R20 | 30% | Tegdi — tasdiq #2 |
| 0:22.85 | L3 | `fx.dart_throw` | -18 dB | C | 15% | Nishonga dart #3 |
| 0:23.10 | L3 | `fx.dart_hit` | -12 dB | C | 30% | Markazga tegdi #3 |
| 0:23.12 | L3 | `ui.select` | -20 dB | R20 | 30% | Tegdi — tasdiq #3 |
| 0:23.15 | L3 | `fx.dart_throw` | -18 dB | C | 15% | Nishonga dart #4 |
| 0:23.40 | L3 | `fx.dart_hit` | -12 dB | C | 30% | Markazga tegdi #4 |
| 0:23.42 | L3 | `ui.select` | -20 dB | R20 | 30% | Tegdi — tasdiq #4 |
| 0:23.50 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #1 chizildi |
| 0:23.70 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #1 |
| 0:23.85 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #2 chizildi |
| 0:24.05 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #2 |
| 0:24.20 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #3 chizildi |
| 0:24.40 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #3 |
| 0:24.50 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: nishonlar oldidan |
| 0:25.00 | L5 | `imp.boom` | -8 dB | C | 40% | Urg'u |
| 0:25.00 | L5 | `imp.sparkle` | -7 dB | C | 50% | Uchqunlar |
| 0:25.20 | L3 | `ui.select` | -17 dB | L40 | 30% | Nishon #1 |
| 0:25.45 | L3 | `ui.select` | -17 dB | C | 30% | Nishon #2 |
| 0:25.70 | L3 | `ui.select` | -17 dB | R40 | 30% | Nishon #3 |
| 0:26.85 | L4 | `tr.whoosh` | -16 dB | C | 40% | Yakuniy kadrga |
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (Bb tonikada) |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
