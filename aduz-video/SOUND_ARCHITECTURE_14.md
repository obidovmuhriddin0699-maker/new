# ADUZ 14-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 14 --cuesheet SOUND_ARCHITECTURE_14.md`).

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
| `fx.flick` | L4 | Plitka ag'dariladi: qog'oz 'shirt' |
| `fx.power_down` | L5 | Telefon o'chadi: pastga tushuvchi ton + klik |
| `fx.low_battery` | L3 | Batareya 1%: ikki notali ogohlantirish |
| `fx.send` | L3 | Post yuborildi: qisqa 'fiyt' |
| `fx.kassa` | L5 | Kassa: tugma + quti + 'ding' + tanga |
| `fx.ringtone` | L3 | Budilnik: tonallikdagi marimba-arpedjio |
| `fx.vibrate` | L3 | Telefon vibratsiyasi: past g'uvullash, pulsatsiya |
| `fx.breath` | L2 | Uyqudagi chuqur nafas |
| `fx.birds` | L2 | Ertalabki qushlar chug'urlashi |
| `fx.blink` | L4 | Ko'z qovog'i 'shirt' etib yumiladi |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:09.5 | Muammo · C#-minor, tashvishli minimal | 7-qism aranjirovkasi 3 yarim ton pastda: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida tungi xona: devor soati, uch marta budilnik (tonallikdagi marimba + vibratsiya), 'Kechiktirish', uyquli nafas, adminning 'post bekor' xabari. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: ko'zlar yumiladi — og'ir nafas va yurak urishi. Keyin J-cut swell B-major'da. |
| 0:10.2–0:11 | Uyg'onish | Ko'z ochiladi, bir pirpiraydi ('shirt'), chap va o'ngdan ertalabki qushlar — tun tugadi. |
| 0:11–0:21.75 | Yechim · B-major, siyrak | Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: kun tanlovi, soat barabani (detent + ko'tariluvchi qadamlar), navbatga uchta post, 'Rejalashtirish'. 15.2 s dan 'vaqt mashinasi': tezlashuvchi soat tiqillashi, har post o'z vaqtida 'fiyt' + tasdiq, tongda qushlar. |
| 0:22–0:27 | Natija · B-major, to'liq | To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Soat millari aylanadi, uchta belgi, kassa ovozi (ssenariydagi 'kassa ovozi'). |
| 0:27–0:32 | Yakun · brend | ADUZ sonic logo (B tonikada), so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -23 dB | C | 0% | Tungi xona — sahna 'havosi' |
| 0:00.05 | L4 | `tr.whoosh` | -17 dB | R30 | 20% | Telefon kadrga kiradi |
| 0:00.50 | L3 | `fx.tick` | -29 dB | L40 | 10% | Devor soati |
| 0:01.50 | L3 | `fx.tick` | -29 dB | L40 | 10% | Devor soati |
| 0:02.00 | L3 | `fx.ringtone` | -14 dB | R10 | 20% | Budilnik 23:00 |
| 0:02.00 | L3 | `fx.vibrate` | -16 dB | C | 0% | Vibratsiya |
| 0:02.50 | L3 | `fx.tick` | -29 dB | L40 | 10% | Devor soati |
| 0:03.00 | L3 | `ui.tap` | -10 dB | L20 | 0% | 'Kechiktirish' bosildi |
| 0:03.30 | L2 | `fx.breath` | -14 dB | C | 20% | Ko'z yumilmoqda... |
| 0:03.50 | L3 | `fx.tick` | -29 dB | L40 | 10% | Devor soati |
| 0:04.50 | L3 | `fx.tick` | -29 dB | L40 | 10% | Devor soati |
| 0:04.60 | L3 | `fx.ding` | -14 dB | R20 | 30% | Admin xabari: post bekor |
| 0:04.62 | L3 | `ui.error` | -15 dB | R20 | 20% | Kechikdi |
| 0:05.50 | L3 | `fx.tick` | -29 dB | L40 | 10% | Devor soati |
| 0:05.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: TUNGI 23:00 |
| 0:06.50 | L3 | `fx.tick` | -29 dB | L40 | 10% | Devor soati |
| 0:06.60 | L3 | `fx.ringtone` | -14 dB | R10 | 20% | Budilnik 01:00 |
| 0:06.60 | L3 | `fx.vibrate` | -16 dB | C | 0% | Vibratsiya |
| 0:06.60 | L5 | `imp.glitch` | -8 dB | R40 | 25% | Slam: 01:00 — YANA |
| 0:07.50 | L3 | `fx.tick` | -29 dB | L40 | 10% | Devor soati |
| 0:07.60 | L3 | `fx.ringtone` | -14 dB | R10 | 20% | Budilnik 06:30 |
| 0:07.60 | L3 | `fx.vibrate` | -16 dB | C | 0% | Vibratsiya |
| 0:07.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: 06:30 — YANA |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.50 | L3 | `fx.tick` | -29 dB | L40 | 10% | Devor soati |
| 0:08.50 | L5 | `imp.boom` | -3 dB | C | 40% | UYQUSIZ TUN — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -8 dB | C | 50% | Zarba qatlami |
| 0:08.50 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:08.60 | L4 | `tr.riser` | -10 dB | C | 0% | Riser — 9.5 s da keskin kesiladi |
| 0:09.30 | L4 | `fx.blink` | -12 dB | C | 0% | Ko'zlar yumiladi |
| 0:09.50 | L2 | `fx.breath` | -8 dB | C | 0% | OVOZ VAKUUMI: og'ir nafas |
| 0:09.80 | L5 | `fx.heartbeat` | -10 dB | C | 0% | Yurak urishi |
| 0:10.15 | L4 | `tr.swell` | -8 dB | C | 30% | J-cut: yechim akkordi (B-major) |
| 0:10.34 | L2 | `fx.birds` | -18 dB | L50 | 30% | Ertalab: qushlar (chap) |
| 0:10.53 | L4 | `fx.blink` | -14 dB | C | 10% | Ko'z pirpiradi |
| 0:10.70 | L2 | `fx.birds` | -20 dB | R50 | 30% | Qushlar (o'ng) |
| 0:11.00 | L5 | `imp.boom` | -6 dB | C | 35% | Yechim boshlanishi — uyg'onish |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `tr.whoosh` | -15 dB | L30 | 20% | Telefon kiradi |
| 0:11.90 | L3 | `ui.select` | -14 dB | L20 | 20% | Kun: Seshanba |
| 0:12.20 | L3 | `fx.knob` | -16 dB | R20 | 15% | Soat barabani aylanadi 19 → 23 |
| 0:12.23 | L3 | `ui.slider` | -22 dB | R20 | 10% | Soat qadami 20:00 |
| 0:12.45 | L3 | `ui.slider` | -22 dB | R20 | 10% | Soat qadami 21:00 |
| 0:12.75 | L3 | `ui.slider` | -22 dB | R20 | 10% | Soat qadami 22:00 |
| 0:12.97 | L3 | `ui.slider` | -22 dB | R20 | 10% | Soat qadami 23:00 |
| 0:13.15 | L3 | `ui.popup` | -17 dB | L20 | 20% | Navbat: 23:00 |
| 0:13.55 | L3 | `ui.tap` | -12 dB | R30 | 0% | + Qo'shish |
| 0:13.57 | L3 | `ui.popup` | -17 dB | C | 20% | Navbat: 01:00 |
| 0:13.95 | L3 | `ui.tap` | -12 dB | R30 | 0% | + Qo'shish |
| 0:13.97 | L3 | `ui.popup` | -17 dB | R20 | 20% | Navbat: 06:30 |
| 0:14.60 | L3 | `ui.tap` | -9 dB | R20 | 0% | 'Rejalashtirish' bosildi |
| 0:14.65 | L3 | `ui.success` | -12 dB | C | 40% | 3 ta post rejada |
| 0:15.00 | L4 | `tr.riser` | -15 dB | C | 20% | Vaqt mashinasi ishga tushadi |
| 0:15.20 | L3 | `fx.tick` | -26 dB | L16 | 10% | Soat tez yuguradi |
| 0:15.38 | L3 | `fx.tick` | -26 dB | R31 | 10% | Soat tez yuguradi |
| 0:15.52 | L3 | `fx.tick` | -26 dB | R39 | 10% | Soat tez yuguradi |
| 0:15.64 | L3 | `fx.tick` | -26 dB | R17 | 10% | Soat tez yuguradi |
| 0:15.76 | L3 | `fx.tick` | -26 dB | L14 | 10% | Soat tez yuguradi |
| 0:15.80 | L3 | `fx.send` | -17 dB | L30 | 20% | Avtomatik chiqdi: 23:00 |
| 0:15.85 | L3 | `ui.select` | -14 dB | L30 | 30% | Chiqdi ✓ #1 |
| 0:15.87 | L3 | `fx.tick` | -26 dB | L36 | 10% | Soat tez yuguradi |
| 0:15.97 | L3 | `fx.tick` | -26 dB | L38 | 10% | Soat tez yuguradi |
| 0:16.08 | L3 | `fx.tick` | -26 dB | L22 | 10% | Soat tez yuguradi |
| 0:16.17 | L3 | `fx.tick` | -26 dB | R5 | 10% | Soat tez yuguradi |
| 0:16.27 | L3 | `fx.tick` | -26 dB | R28 | 10% | Soat tez yuguradi |
| 0:16.36 | L3 | `fx.tick` | -26 dB | R40 | 10% | Soat tez yuguradi |
| 0:16.46 | L3 | `fx.tick` | -26 dB | R35 | 10% | Soat tez yuguradi |
| 0:16.50 | L3 | `fx.send` | -17 dB | C | 20% | Avtomatik chiqdi: 01:00 |
| 0:16.55 | L3 | `fx.tick` | -26 dB | R16 | 10% | Soat tez yuguradi |
| 0:16.55 | L3 | `ui.select` | -14 dB | C | 30% | Chiqdi ✓ #2 |
| 0:16.64 | L3 | `fx.tick` | -26 dB | L8 | 10% | Soat tez yuguradi |
| 0:16.72 | L3 | `fx.tick` | -26 dB | L29 | 10% | Soat tez yuguradi |
| 0:16.81 | L3 | `fx.tick` | -26 dB | L40 | 10% | Soat tez yuguradi |
| 0:16.90 | L3 | `fx.tick` | -26 dB | L36 | 10% | Soat tez yuguradi |
| 0:16.98 | L3 | `fx.tick` | -26 dB | L20 | 10% | Soat tez yuguradi |
| 0:17.06 | L3 | `fx.tick` | -26 dB | C | 10% | Soat tez yuguradi |
| 0:17.15 | L3 | `fx.tick` | -26 dB | R24 | 10% | Soat tez yuguradi |
| 0:17.23 | L3 | `fx.tick` | -26 dB | R37 | 10% | Soat tez yuguradi |
| 0:17.30 | L3 | `fx.send` | -17 dB | R30 | 20% | Avtomatik chiqdi: 06:30 |
| 0:17.31 | L3 | `fx.tick` | -26 dB | R39 | 10% | Soat tez yuguradi |
| 0:17.35 | L3 | `ui.select` | -14 dB | R30 | 30% | Chiqdi ✓ #3 |
| 0:17.39 | L3 | `fx.tick` | -26 dB | R29 | 10% | Soat tez yuguradi |
| 0:17.40 | L2 | `fx.birds` | -22 dB | R40 | 30% | Tong — qushlar |
| 0:17.47 | L3 | `fx.tick` | -26 dB | R10 | 10% | Soat tez yuguradi |
| 0:17.54 | L3 | `fx.tick` | -26 dB | L12 | 10% | Soat tez yuguradi |
| 0:17.62 | L3 | `fx.tick` | -26 dB | L30 | 10% | Soat tez yuguradi |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: AVTOMATIK oldidan |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | AVTOMATIK — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Oltin uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | Hammasi o'z vaqtida chiqdi oynasi |
| 0:21.20 | L4 | `tr.riser` | -12 dB | C | 0% | J-cut: whip oldidan |
| 0:21.75 | L4 | `tr.whip` | -8 dB | C | 25% | Whip-pan o'tishi |
| 0:22.00 | L5 | `imp.boom` | -5 dB | C | 45% | Natija boshlanishi |
| 0:22.00 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:22.30 | L3 | `fx.knob` | -18 dB | C | 15% | Soat millari aylanadi |
| 0:22.50 | L3 | `ui.select` | -15 dB | L30 | 30% | Soat belgisi ✓ 23:00 |
| 0:22.85 | L3 | `ui.select` | -15 dB | R30 | 30% | Soat belgisi ✓ 01:00 |
| 0:23.20 | L3 | `ui.select` | -15 dB | C | 30% | Soat belgisi ✓ 06:30 |
| 0:23.20 | L5 | `fx.kassa` | -9 dB | C | 30% | KASSA — uchala post o'z vaqtida |
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
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (B tonikada) |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
