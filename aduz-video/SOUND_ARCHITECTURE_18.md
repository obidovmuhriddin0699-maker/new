# ADUZ 18-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 18 --cuesheet SOUND_ARCHITECTURE_18.md`).

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
| `fx.shutter` | L3 | Skrinshot: kamera zatvori 'chiq-chiq' |
| `fx.xray` | L3 | Lupa fosh qiladi: shisha shimmer + pastga tushuvchi 'vuuu' |
| `fx.crack` | L5 | Shisha yoriladi: keskin 'chars' + mayda jaranglar |
| `fx.creak` | L3 | Yoriq shisha zo'riqishi: ingichka g'ichirlash |
| `fx.shatter` | L5 | Shisha sinadi: portlash + 70 ta parcha jarangi |
| `fx.stamp` | L3 | 'Tasdiqlangan' muhri |
| `fx.zap` | L3 | Elektr uchquni: chirsillash |
| `fx.short` | L5 | Qisqa tutashuv: portlash + pasayib boruvchi g'uvullash |
| `fx.fizz` | L3 | Kuygan simlar vishillashi |
| `fx.twang` | L4 | Simlar tortiladi: yuqoriga ketuvchi 'tang' |
| `fx.plug` | L3 | Vilka rozetkaga: klak + uchqun + yoqilish toni |
| `fx.chain` | L5 | Zanjir: metall halqalar shaldirashi + zarba |
| `fx.padlock` | L5 | Qulf: og'ir 'klak' + metall jarang |
| `fx.chain_snap` | L5 | Zanjir uziladi: keskin 'chars' + jarang + halqalar sochilishi |
| `fx.sms` | L3 | SMS: ikki notali signal |
| `fx.flip` | L3 | Tanga tashlandi: 'ting' + havoda aylanish |
| `fx.wobble` | L5 | Tanga aylanib to'xtaydi: tezlashuvchi metall chiqillash, keskin jimlik |
| `fx.drain` | L3 | Byudjet oqib ketmoqda: pasayuvchi hushtak |
| `fx.zip` | L4 | A|B chizig'i tortiladi: ko'tariluvchi 'zzzip' |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:09.5 | Muammo · B-minor, tashvishli minimal | 7-qism aranjirovkasi 5 yarim ton pastda: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Ustida: ikki dizayn ustida ikkilanish, tanga tashlash ('ting' + aylanish + tushish), 'Ishga tushirish', byudjet oqib ketishi — pasayuvchi hushtaklar. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: tanga qorong'ilikka tushib, aylanib to'xtaydi — tezlashuvchi metall chiqillash va keskin jimlik; yurak urishi. Keyin J-cut swell A-major'da. |
| 0:10.3–0:11 | A|B chizig'i | Markazdan pastga yorug' chiziq tortiladi ('zzzip'), kadr ikki tomonga whoosh bilan ochiladi. |
| 0:11–0:21.75 | Yechim · A-major, siyrak | Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: test byudjeti, 'boshlash', A (chapda, past) va B (o'ngda, baland) navbatma-navbat 'blip' — poyga, g'olib B, tavsiya 'ding', byudjet tangalari B ga. |
| 0:22–0:27 | Natija · A-major, to'liq | To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. CTR ustuni o'sadi, ×6.7 da kassa ovozi (ssenariydagi 'kassa ovozi'). |
| 0:27–0:32 | Yakun · brend | ADUZ sonic logo (A tonikada), so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -21 dB | C | 0% | Xona — sahna 'havosi' |
| 0:00.05 | L4 | `tr.whoosh` | -16 dB | R30 | 20% | Telefon kadrga kiradi |
| 0:01.40 | L3 | `ui.popup` | -20 dB | L30 | 20% | Kursor A ustida — '?' |
| 0:01.90 | L3 | `ui.popup` | -20 dB | R30 | 20% | Kursor B ustida — '?' |
| 0:02.40 | L3 | `fx.flip` | -10 dB | C | 25% | TANGA TASHLANDI |
| 0:03.40 | L3 | `fx.coin` | -10 dB | C | 20% | Tanga tushdi: A |
| 0:03.70 | L3 | `ui.tap` | -11 dB | L30 | 0% | A tanlandi |
| 0:04.20 | L3 | `ui.tap` | -10 dB | R20 | 0% | Ishga tushirish — 100% → A |
| 0:04.25 | L3 | `ui.launch` | -15 dB | C | 30% | Butun byudjet ketdi |
| 0:04.60 | L3 | `fx.drain` | -17 dB | R20 | 20% | Byudjet oqmoqda #1 |
| 0:04.60 | L3 | `fx.tick` | -30 dB | R30 | 10% | Siyrak bosishlar |
| 0:05.10 | L3 | `fx.tick` | -30 dB | R30 | 10% | Siyrak bosishlar |
| 0:05.60 | L3 | `fx.tick` | -30 dB | R30 | 10% | Siyrak bosishlar |
| 0:05.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: TAXMIN |
| 0:06.00 | L3 | `fx.drain` | -17 dB | R20 | 20% | Byudjet oqmoqda #2 |
| 0:06.10 | L3 | `fx.tick` | -30 dB | R30 | 10% | Siyrak bosishlar |
| 0:06.60 | L3 | `fx.tick` | -30 dB | R30 | 10% | Siyrak bosishlar |
| 0:06.60 | L5 | `imp.glitch` | -8 dB | R40 | 25% | Slam: TAVAKKAL |
| 0:07.10 | L3 | `fx.tick` | -30 dB | R30 | 10% | Siyrak bosishlar |
| 0:07.40 | L3 | `fx.drain` | -17 dB | R20 | 20% | Byudjet oqmoqda #3 |
| 0:07.60 | L3 | `fx.tick` | -30 dB | R30 | 10% | Siyrak bosishlar |
| 0:07.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: BYUDJET KETDI |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.10 | L3 | `fx.tick` | -30 dB | R30 | 10% | Siyrak bosishlar |
| 0:08.50 | L5 | `imp.boom` | -3 dB | C | 40% | LOTEREYA — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -8 dB | C | 50% | Zarba qatlami |
| 0:08.50 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:08.60 | L3 | `fx.tick` | -30 dB | R30 | 10% | Siyrak bosishlar |
| 0:08.60 | L4 | `tr.riser` | -10 dB | C | 0% | Riser — 9.5 s da keskin kesiladi |
| 0:09.62 | L5 | `fx.wobble` | -8 dB | C | 0% | OVOZ VAKUUMI: tanga aylanib to'xtaydi |
| 0:09.90 | L5 | `fx.heartbeat` | -12 dB | C | 0% | Yurak urishi |
| 0:10.15 | L4 | `tr.swell` | -8 dB | C | 30% | J-cut: yechim akkordi (A-major) |
| 0:10.30 | L4 | `fx.zip` | -10 dB | C | 20% | A|B chizig'i tortiladi |
| 0:10.58 | L4 | `tr.whoosh` | -10 dB | C | 30% | Kadr ikki tomonga ochiladi |
| 0:11.00 | L5 | `imp.boom` | -6 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `tr.whoosh` | -15 dB | L30 | 20% | Telefon kiradi |
| 0:11.90 | L3 | `ui.popup` | -17 dB | C | 20% | Test byudjeti: 10% |
| 0:12.60 | L3 | `ui.tap` | -9 dB | R20 | 0% | 'A/B testni boshlash' |
| 0:12.65 | L3 | `ui.launch` | -14 dB | C | 30% | Test boshlandi |
| 0:13.00 | L3 | `fx.blip` | -24 dB | L40 | 20% | Poyga: A |
| 0:13.20 | L3 | `fx.blip` | -24 dB | R40 | 20% | Poyga: B |
| 0:13.40 | L3 | `fx.blip` | -24 dB | L40 | 20% | Poyga: A |
| 0:13.60 | L3 | `fx.blip` | -24 dB | R40 | 20% | Poyga: B |
| 0:13.80 | L3 | `fx.blip` | -24 dB | L40 | 20% | Poyga: A |
| 0:14.00 | L3 | `fx.blip` | -24 dB | R40 | 20% | Poyga: B |
| 0:14.20 | L3 | `fx.blip` | -24 dB | L40 | 20% | Poyga: A |
| 0:14.40 | L3 | `fx.blip` | -24 dB | R40 | 20% | Poyga: B |
| 0:14.60 | L3 | `fx.blip` | -24 dB | L40 | 20% | Poyga: A |
| 0:14.80 | L3 | `fx.blip` | -24 dB | R40 | 20% | Poyga: B |
| 0:15.00 | L3 | `fx.blip` | -24 dB | L40 | 20% | Poyga: A |
| 0:15.20 | L3 | `fx.blip` | -24 dB | R40 | 20% | Poyga: B |
| 0:15.60 | L3 | `ui.success` | -11 dB | R30 | 40% | G'OLIB: B |
| 0:15.60 | L5 | `imp.sparkle` | -13 dB | R30 | 40% | G'olib toji |
| 0:16.20 | L3 | `fx.ding` | -14 dB | C | 30% | Tavsiya: qolgan byudjet B ga |
| 0:16.80 | L3 | `ui.tap` | -10 dB | R30 | 0% | 'Ha, B ga' |
| 0:17.35 | L3 | `fx.coin` | -24 dB | L30 | 20% | Byudjet tangasi #1 → B |
| 0:17.43 | L3 | `fx.coin` | -24 dB | L22 | 20% | Byudjet tangasi #2 → B |
| 0:17.51 | L3 | `fx.coin` | -24 dB | L14 | 20% | Byudjet tangasi #3 → B |
| 0:17.59 | L3 | `fx.coin` | -24 dB | L6 | 20% | Byudjet tangasi #4 → B |
| 0:17.67 | L3 | `fx.coin` | -24 dB | C | 20% | Byudjet tangasi #5 → B |
| 0:17.75 | L3 | `fx.coin` | -24 dB | R10 | 20% | Byudjet tangasi #6 → B |
| 0:17.75 | L3 | `ui.select` | -14 dB | R30 | 30% | Byudjet g'olibda ✓ |
| 0:17.83 | L3 | `fx.coin` | -24 dB | R18 | 20% | Byudjet tangasi #7 → B |
| 0:17.91 | L3 | `fx.coin` | -24 dB | R26 | 20% | Byudjet tangasi #8 → B |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: G'OLIB — B oldidan |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | G'OLIB — B — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Oltin uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | Byudjet g'olibda oynasi |
| 0:21.20 | L4 | `tr.riser` | -12 dB | C | 0% | J-cut: whip oldidan |
| 0:21.75 | L4 | `tr.whip` | -8 dB | C | 25% | Whip-pan o'tishi |
| 0:22.00 | L5 | `imp.boom` | -5 dB | C | 45% | Natija boshlanishi |
| 0:22.00 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:22.40 | L4 | `tr.riser` | -16 dB | R30 | 20% | CTR ustuni o'sadi |
| 0:23.20 | L5 | `fx.kassa` | -8 dB | C | 30% | KASSA — ×6.7 |
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
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (A tonikada) |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
