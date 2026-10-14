# ADUZ 13-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 13 --cuesheet SOUND_ARCHITECTURE_13.md`).

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

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:09.5 | Muammo · F#-minor, tashvishli minimal | 7-qism aranjirovkasi 2 yarim ton yuqorida: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida 'nusxa → joylash → yuborish' marosimi: bir xil uch bosish qayta-qayta (zerikarli takror — ataylab). 4.5 s dan soat tiqillashi tobora balandlashadi. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: telefon o'chadi (pastga tushuvchi ton), 'batareya 1%' ogohlantirishi, yurak urishi. Keyin J-cut swell E-major'da. |
| 0:10.35–0:11 | Plitkalar ag'darilishi | 15 ta qog'oz 'shirt' — har biri plitkalar devorining bitta diagonali bilan sinxron; panorama chapdan o'ngga yuradi. |
| 0:11–0:21.75 | Yechim · E-major, siyrak | Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: ikki filtr tanlovi, 54 kanal belgilanishi (E-pentatonik zinapoya), qamrov hisoblagichi, 'yuborish' bosilishi va 14 ta post stereo maydon bo'ylab uchib ketadi. |
| 0:22–0:27 | Natija · E-major, to'liq | To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Qamrov hisoblagichi ko'tariluvchi qadamlar bilan 186 000 ga yetadi — kassa ovozi (ssenariydagi 'kassa ovozi'). |
| 0:27–0:32 | Yakun · brend | ADUZ sonic logo (E tonikada), so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -21 dB | C | 0% | Xona — sahna 'havosi' |
| 0:00.05 | L4 | `tr.whoosh` | -16 dB | R30 | 20% | Telefon kadrga kiradi |
| 0:00.85 | L3 | `ui.tap` | -12 dB | L44 | 0% | Chat #1 ochildi |
| 0:01.00 | L4 | `tr.slide` | -20 dB | C | 10% | Chat kartasi chiqadi |
| 0:01.30 | L3 | `ui.tap` | -14 dB | L30 | 0% | Nusxa olish |
| 0:01.52 | L3 | `ui.tap` | -14 dB | C | 0% | Joylash |
| 0:01.74 | L3 | `ui.tap` | -14 dB | R30 | 0% | Yuborish |
| 0:01.76 | L3 | `fx.send` | -17 dB | R40 | 15% | Post ketdi |
| 0:02.00 | L3 | `ui.select` | -20 dB | C | 20% | Yuborildi |
| 0:02.15 | L3 | `ui.tap` | -12 dB | L22 | 0% | Chat #2 ochildi |
| 0:02.30 | L4 | `tr.slide` | -20 dB | C | 10% | Chat kartasi chiqadi |
| 0:02.60 | L3 | `ui.tap` | -14 dB | L30 | 0% | Nusxa olish |
| 0:02.82 | L3 | `ui.tap` | -14 dB | C | 0% | Joylash |
| 0:03.04 | L3 | `ui.tap` | -14 dB | R30 | 0% | Yuborish |
| 0:03.06 | L3 | `fx.send` | -17 dB | R40 | 15% | Post ketdi |
| 0:03.30 | L3 | `fx.fail` | -15 dB | C | 20% | Admin: «Narx boshqacha» |
| 0:03.45 | L3 | `ui.tap` | -12 dB | C | 0% | Chat #3 ochildi |
| 0:03.60 | L4 | `tr.slide` | -20 dB | C | 10% | Chat kartasi chiqadi |
| 0:03.90 | L3 | `ui.tap` | -14 dB | L30 | 0% | Nusxa olish |
| 0:04.12 | L3 | `ui.tap` | -14 dB | C | 0% | Joylash |
| 0:04.34 | L3 | `ui.tap` | -14 dB | R30 | 0% | Yuborish |
| 0:04.36 | L3 | `fx.send` | -17 dB | R40 | 15% | Post ketdi |
| 0:04.50 | L3 | `fx.tick` | -28 dB | R35 | 0% | Soat yuguradi |
| 0:04.60 | L3 | `ui.select` | -20 dB | C | 20% | Yuborildi |
| 0:04.68 | L3 | `ui.tap` | -17 dB | R22 | 0% | Chat #4 |
| 0:04.75 | L3 | `fx.tick` | -28 dB | R35 | 0% | Soat yuguradi |
| 0:04.80 | L3 | `ui.select` | -23 dB | R22 | 15% | Chat #4: yuborildi |
| 0:05.00 | L3 | `fx.tick` | -27 dB | R35 | 0% | Soat yuguradi |
| 0:05.04 | L3 | `ui.tap` | -17 dB | R44 | 0% | Chat #5 |
| 0:05.16 | L3 | `ui.select` | -23 dB | R44 | 15% | Chat #5: yuborildi |
| 0:05.25 | L3 | `fx.tick` | -27 dB | R35 | 0% | Soat yuguradi |
| 0:05.40 | L3 | `ui.tap` | -17 dB | L44 | 0% | Chat #6 |
| 0:05.50 | L3 | `fx.tick` | -26 dB | R35 | 0% | Soat yuguradi |
| 0:05.52 | L3 | `fx.fail` | -17 dB | L44 | 15% | Chat #6: xato |
| 0:05.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: 50 TA CHAT |
| 0:05.64 | L3 | `ui.tap` | -17 dB | L22 | 0% | Chat #7 |
| 0:05.75 | L3 | `fx.tick` | -26 dB | R35 | 0% | Soat yuguradi |
| 0:05.76 | L3 | `ui.select` | -23 dB | L22 | 15% | Chat #7: yuborildi |
| 0:06.00 | L3 | `ui.tap` | -17 dB | C | 0% | Chat #8 |
| 0:06.00 | L3 | `fx.tick` | -26 dB | R35 | 0% | Soat yuguradi |
| 0:06.12 | L3 | `ui.select` | -23 dB | C | 15% | Chat #8: yuborildi |
| 0:06.25 | L3 | `fx.tick` | -25 dB | R35 | 0% | Soat yuguradi |
| 0:06.36 | L3 | `ui.tap` | -17 dB | R22 | 0% | Chat #9 |
| 0:06.48 | L3 | `ui.select` | -23 dB | R22 | 15% | Chat #9: yuborildi |
| 0:06.50 | L3 | `fx.tick` | -25 dB | R35 | 0% | Soat yuguradi |
| 0:06.60 | L3 | `ui.tap` | -17 dB | R44 | 0% | Chat #10 |
| 0:06.60 | L5 | `imp.glitch` | -8 dB | R40 | 25% | Slam: 50 MARTA NUSXA |
| 0:06.72 | L3 | `fx.fail` | -17 dB | R44 | 15% | Chat #10: xato |
| 0:06.75 | L3 | `fx.tick` | -25 dB | R35 | 0% | Soat yuguradi |
| 0:06.96 | L3 | `ui.tap` | -17 dB | L44 | 0% | Chat #11 |
| 0:07.00 | L3 | `fx.tick` | -24 dB | R35 | 0% | Soat yuguradi |
| 0:07.08 | L3 | `ui.select` | -23 dB | L44 | 15% | Chat #11: yuborildi |
| 0:07.25 | L3 | `fx.tick` | -24 dB | R35 | 0% | Soat yuguradi |
| 0:07.32 | L3 | `ui.tap` | -17 dB | L22 | 0% | Chat #12 |
| 0:07.44 | L3 | `ui.select` | -23 dB | L22 | 15% | Chat #12: yuborildi |
| 0:07.50 | L3 | `fx.tick` | -24 dB | R35 | 0% | Soat yuguradi |
| 0:07.56 | L3 | `ui.tap` | -17 dB | C | 0% | Chat #13 |
| 0:07.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: YANA 36 TA... |
| 0:07.68 | L3 | `fx.fail` | -17 dB | C | 15% | Chat #13: xato |
| 0:07.75 | L3 | `fx.tick` | -24 dB | R35 | 0% | Soat yuguradi |
| 0:07.92 | L3 | `ui.tap` | -17 dB | R22 | 0% | Chat #14 |
| 0:08.00 | L3 | `fx.tick` | -23 dB | R35 | 0% | Soat yuguradi |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.04 | L3 | `ui.select` | -23 dB | R22 | 15% | Chat #14: yuborildi |
| 0:08.25 | L3 | `fx.tick` | -23 dB | R35 | 0% | Soat yuguradi |
| 0:08.50 | L3 | `fx.tick` | -23 dB | R35 | 0% | Soat yuguradi |
| 0:08.50 | L5 | `imp.boom` | -3 dB | C | 40% | 14 / 50 — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -8 dB | C | 50% | Zarba qatlami |
| 0:08.50 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:08.60 | L4 | `tr.riser` | -10 dB | C | 0% | Riser — 9.5 s da keskin kesiladi |
| 0:08.75 | L3 | `fx.tick` | -23 dB | R35 | 0% | Soat yuguradi |
| 0:09.00 | L3 | `fx.tick` | -22 dB | R35 | 0% | Soat yuguradi |
| 0:09.25 | L3 | `fx.tick` | -22 dB | R35 | 0% | Soat yuguradi |
| 0:09.55 | L5 | `fx.power_down` | -7 dB | C | 0% | OVOZ VAKUUMI: telefon o'chdi |
| 0:09.60 | L3 | `fx.low_battery` | -12 dB | C | 0% | Batareya 1% |
| 0:09.95 | L5 | `fx.heartbeat` | -9 dB | C | 0% | Yurak urishi |
| 0:10.10 | L3 | `fx.low_battery` | -15 dB | C | 0% | Batareya 1% (so'nggi) |
| 0:10.15 | L4 | `tr.swell` | -8 dB | C | 30% | J-cut: yechim akkordi (E-major) |
| 0:10.50 | L4 | `fx.flick` | -16 dB | L50 | 15% | Plitkalar ag'dariladi — diagonal 1/15 |
| 0:10.52 | L4 | `fx.flick` | -16 dB | L43 | 15% | Plitkalar ag'dariladi — diagonal 2/15 |
| 0:10.55 | L4 | `fx.flick` | -16 dB | L36 | 15% | Plitkalar ag'dariladi — diagonal 3/15 |
| 0:10.57 | L4 | `fx.flick` | -16 dB | L29 | 15% | Plitkalar ag'dariladi — diagonal 4/15 |
| 0:10.60 | L4 | `fx.flick` | -16 dB | L21 | 15% | Plitkalar ag'dariladi — diagonal 5/15 |
| 0:10.62 | L4 | `fx.flick` | -16 dB | L14 | 15% | Plitkalar ag'dariladi — diagonal 6/15 |
| 0:10.65 | L4 | `fx.flick` | -16 dB | L7 | 15% | Plitkalar ag'dariladi — diagonal 7/15 |
| 0:10.67 | L4 | `fx.flick` | -16 dB | C | 15% | Plitkalar ag'dariladi — diagonal 8/15 |
| 0:10.70 | L4 | `fx.flick` | -16 dB | R7 | 15% | Plitkalar ag'dariladi — diagonal 9/15 |
| 0:10.73 | L4 | `fx.flick` | -16 dB | R14 | 15% | Plitkalar ag'dariladi — diagonal 10/15 |
| 0:10.75 | L4 | `fx.flick` | -16 dB | R21 | 15% | Plitkalar ag'dariladi — diagonal 11/15 |
| 0:10.78 | L4 | `fx.flick` | -16 dB | R29 | 15% | Plitkalar ag'dariladi — diagonal 12/15 |
| 0:10.80 | L4 | `fx.flick` | -16 dB | R36 | 15% | Plitkalar ag'dariladi — diagonal 13/15 |
| 0:10.83 | L4 | `fx.flick` | -16 dB | R43 | 15% | Plitkalar ag'dariladi — diagonal 14/15 |
| 0:10.85 | L4 | `fx.flick` | -16 dB | R50 | 15% | Plitkalar ag'dariladi — diagonal 15/15 |
| 0:11.00 | L5 | `imp.boom` | -6 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `tr.whoosh` | -15 dB | L30 | 20% | Telefon kiradi |
| 0:12.10 | L3 | `ui.select` | -14 dB | L30 | 20% | Filtr: Kiyim-kechak |
| 0:12.60 | L3 | `ui.select` | -14 dB | R10 | 20% | Filtr: Farg'ona vodiysi |
| 0:12.90 | L3 | `fx.blip` | -23 dB | L50 | 20% | Kanallar belgilanmoqda 3/54 |
| 0:12.96 | L3 | `fx.blip` | -23 dB | L30 | 20% | Kanallar belgilanmoqda 6/54 |
| 0:13.01 | L3 | `fx.blip` | -23 dB | L10 | 20% | Kanallar belgilanmoqda 9/54 |
| 0:13.07 | L3 | `fx.blip` | -23 dB | R10 | 20% | Kanallar belgilanmoqda 12/54 |
| 0:13.12 | L3 | `fx.blip` | -23 dB | R30 | 20% | Kanallar belgilanmoqda 15/54 |
| 0:13.18 | L3 | `fx.blip` | -23 dB | R50 | 20% | Kanallar belgilanmoqda 18/54 |
| 0:13.23 | L3 | `fx.blip` | -23 dB | L50 | 20% | Kanallar belgilanmoqda 21/54 |
| 0:13.29 | L3 | `fx.blip` | -23 dB | L30 | 20% | Kanallar belgilanmoqda 24/54 |
| 0:13.34 | L3 | `fx.blip` | -23 dB | L10 | 20% | Kanallar belgilanmoqda 27/54 |
| 0:13.40 | L3 | `fx.blip` | -23 dB | R10 | 20% | Kanallar belgilanmoqda 30/54 |
| 0:13.46 | L3 | `fx.blip` | -23 dB | R30 | 20% | Kanallar belgilanmoqda 33/54 |
| 0:13.51 | L3 | `fx.blip` | -23 dB | R50 | 20% | Kanallar belgilanmoqda 36/54 |
| 0:13.57 | L3 | `fx.blip` | -23 dB | L50 | 20% | Kanallar belgilanmoqda 39/54 |
| 0:13.62 | L3 | `fx.blip` | -23 dB | L30 | 20% | Kanallar belgilanmoqda 42/54 |
| 0:13.68 | L3 | `fx.blip` | -23 dB | L10 | 20% | Kanallar belgilanmoqda 45/54 |
| 0:13.73 | L3 | `fx.blip` | -23 dB | R10 | 20% | Kanallar belgilanmoqda 48/54 |
| 0:13.79 | L3 | `fx.blip` | -23 dB | R30 | 20% | Kanallar belgilanmoqda 51/54 |
| 0:13.84 | L3 | `fx.blip` | -23 dB | R50 | 20% | Kanallar belgilanmoqda 54/54 |
| 0:13.95 | L3 | `ui.success` | -15 dB | C | 40% | 54 kanal tanlandi |
| 0:14.00 | L3 | `ui.slider` | -24 dB | R20 | 10% | Qamrov hisoblanmoqda 1/8 |
| 0:14.11 | L3 | `ui.slider` | -24 dB | R20 | 10% | Qamrov hisoblanmoqda 2/8 |
| 0:14.22 | L3 | `ui.slider` | -24 dB | R20 | 10% | Qamrov hisoblanmoqda 3/8 |
| 0:14.33 | L3 | `ui.slider` | -24 dB | R20 | 10% | Qamrov hisoblanmoqda 4/8 |
| 0:14.44 | L3 | `ui.slider` | -24 dB | R20 | 10% | Qamrov hisoblanmoqda 5/8 |
| 0:14.55 | L3 | `ui.slider` | -24 dB | R20 | 10% | Qamrov hisoblanmoqda 6/8 |
| 0:14.66 | L3 | `ui.slider` | -24 dB | R20 | 10% | Qamrov hisoblanmoqda 7/8 |
| 0:14.77 | L3 | `ui.slider` | -24 dB | R20 | 10% | Qamrov hisoblanmoqda 8/8 |
| 0:15.20 | L3 | `ui.tap` | -8 dB | R20 | 0% | '54 kanalga yuborish' bosildi |
| 0:15.25 | L3 | `ui.launch` | -13 dB | C | 30% | Yuborish boshlandi |
| 0:15.40 | L3 | `fx.send` | -20 dB | L70 | 20% | Post #1 uchib ketdi |
| 0:15.40 | L3 | `fx.blip` | -24 dB | L50 | 25% | Kanal to'lqini 1/13 |
| 0:15.47 | L3 | `fx.send` | -20 dB | L59 | 20% | Post #2 uchib ketdi |
| 0:15.48 | L3 | `fx.blip` | -24 dB | L42 | 25% | Kanal to'lqini 2/13 |
| 0:15.54 | L3 | `fx.send` | -20 dB | L48 | 20% | Post #3 uchib ketdi |
| 0:15.56 | L3 | `fx.blip` | -24 dB | L33 | 25% | Kanal to'lqini 3/13 |
| 0:15.61 | L3 | `fx.send` | -20 dB | L38 | 20% | Post #4 uchib ketdi |
| 0:15.64 | L3 | `fx.blip` | -24 dB | L25 | 25% | Kanal to'lqini 4/13 |
| 0:15.68 | L3 | `fx.send` | -20 dB | L27 | 20% | Post #5 uchib ketdi |
| 0:15.72 | L3 | `fx.blip` | -24 dB | L17 | 25% | Kanal to'lqini 5/13 |
| 0:15.75 | L3 | `fx.send` | -20 dB | L16 | 20% | Post #6 uchib ketdi |
| 0:15.80 | L3 | `fx.blip` | -24 dB | L8 | 25% | Kanal to'lqini 6/13 |
| 0:15.82 | L3 | `fx.send` | -20 dB | L5 | 20% | Post #7 uchib ketdi |
| 0:15.88 | L3 | `fx.blip` | -24 dB | C | 25% | Kanal to'lqini 7/13 |
| 0:15.89 | L3 | `fx.send` | -20 dB | R5 | 20% | Post #8 uchib ketdi |
| 0:15.96 | L3 | `fx.send` | -20 dB | R16 | 20% | Post #9 uchib ketdi |
| 0:15.96 | L3 | `fx.blip` | -24 dB | R8 | 25% | Kanal to'lqini 8/13 |
| 0:16.03 | L3 | `fx.send` | -20 dB | R27 | 20% | Post #10 uchib ketdi |
| 0:16.04 | L3 | `fx.blip` | -24 dB | R17 | 25% | Kanal to'lqini 9/13 |
| 0:16.10 | L3 | `fx.send` | -20 dB | R38 | 20% | Post #11 uchib ketdi |
| 0:16.12 | L3 | `fx.blip` | -24 dB | R25 | 25% | Kanal to'lqini 10/13 |
| 0:16.17 | L3 | `fx.send` | -20 dB | R48 | 20% | Post #12 uchib ketdi |
| 0:16.20 | L3 | `fx.blip` | -24 dB | R33 | 25% | Kanal to'lqini 11/13 |
| 0:16.24 | L3 | `fx.send` | -20 dB | R59 | 20% | Post #13 uchib ketdi |
| 0:16.28 | L3 | `fx.blip` | -24 dB | R42 | 25% | Kanal to'lqini 12/13 |
| 0:16.31 | L3 | `fx.send` | -20 dB | R70 | 20% | Post #14 uchib ketdi |
| 0:16.36 | L3 | `fx.blip` | -24 dB | R50 | 25% | Kanal to'lqini 13/13 |
| 0:16.60 | L3 | `ui.success` | -10 dB | C | 50% | 54 / 54 yuborildi |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: BITTA TUGMA oldidan |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | BITTA TUGMA — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Oltin uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | 54 kanalga yuborildi oynasi |
| 0:21.20 | L4 | `tr.riser` | -12 dB | C | 0% | J-cut: whip oldidan |
| 0:21.75 | L4 | `tr.whip` | -8 dB | C | 25% | Whip-pan o'tishi |
| 0:22.00 | L5 | `imp.boom` | -5 dB | C | 45% | Natija boshlanishi |
| 0:22.00 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:22.45 | L3 | `ui.slider` | -23 dB | L30 | 10% | Qamrov o'smoqda 1/9 |
| 0:22.62 | L3 | `ui.slider` | -23 dB | L30 | 10% | Qamrov o'smoqda 2/9 |
| 0:22.79 | L3 | `ui.slider` | -23 dB | L30 | 10% | Qamrov o'smoqda 3/9 |
| 0:22.96 | L3 | `ui.slider` | -23 dB | L30 | 10% | Qamrov o'smoqda 4/9 |
| 0:23.13 | L3 | `ui.slider` | -23 dB | L30 | 10% | Qamrov o'smoqda 5/9 |
| 0:23.30 | L3 | `ui.slider` | -23 dB | L30 | 10% | Qamrov o'smoqda 6/9 |
| 0:23.47 | L3 | `ui.slider` | -23 dB | L30 | 10% | Qamrov o'smoqda 7/9 |
| 0:23.50 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #1 chizildi |
| 0:23.64 | L3 | `ui.slider` | -23 dB | L30 | 10% | Qamrov o'smoqda 8/9 |
| 0:23.70 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #1 |
| 0:23.81 | L3 | `ui.slider` | -23 dB | L30 | 10% | Qamrov o'smoqda 9/9 |
| 0:23.85 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #2 chizildi |
| 0:24.00 | L5 | `fx.kassa` | -8 dB | C | 30% | KASSA — 186 000 qamrov |
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
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (E tonikada) |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
