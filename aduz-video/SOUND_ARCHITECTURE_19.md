# ADUZ 19-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 19 --cuesheet SOUND_ARCHITECTURE_19.md`).

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
| `sfx.click_1` | L3 | Toza UI klik (1.7 kHz), 40 ms |
| `sfx.click_2` | L3 | UI klik, 2-variant |
| `sfx.click_3` | L3 | UI klik, 3-variant |
| `sfx.click_4` | L3 | UI klik, 4-variant |
| `sfx.click_5` | L3 | UI klik, 5-variant |
| `sfx.click_double_1` | L3 | Qo'sh klik (tasdiqlash) |
| `sfx.click_double_2` | L3 | Qo'sh klik, 2-variant |
| `sfx.pop_swish` | L3 | Qisqa 'pop' + shuvullash: element paydo bo'lishi |
| `sfx.swipe` | L4 | Swipe: ekran/kartaning sirpanishi |
| `sfx.glitch_seq` | L5 | Raqamli glitch ketma-ketligi (6 zarb) |
| `sfx.notify_pop` | L3 | Bildirishnoma: ikki 'pop' + dum |
| `sfx.notify_ring` | L3 | Bildirishnoma: jarangli 'ding' |
| `sfx.hit_low` | L5 | Past tonal zarba (≈260 Hz) + dum |
| `sfx.hit_chime` | L5 | Tonal zarba, qo'ng'iroqsimon (≈390 Hz) |
| `sfx.hit_tone` | L5 | Tonal zarba, 3-variant |
| `sfx.whoosh_soft` | L4 | Yumshoq whoosh (1.3 s) |
| `sfx.whoosh_sweep` | L4 | Whoosh, tonallik siljishi bilan |
| `sfx.ratchet_roll` | L3 | Tishli chiqillash, sekinlashuvchi (1.2 s) |
| `sfx.riser_click` | L4 | Riser: chiqillashlar bilan kuchayib boradi |
| `sfx.glitch_long` | L5 | Uzun zich glitch / ma'lumot oqimi (1.8 s) |
| `sfx.glitch_noise` | L5 | Shovqinli glitch (1.4 s) |
| `sfx.stutter` | L5 | Stutter: 10 ta tez zarb |
| `sfx.glitch_short` | L5 | Qisqa yuqori glitch (0.4 s) |
| `sfx.tick` | L3 | Mayda tik |
| `sfx.tick_roll` | L3 | 8 ta bir tekis tik (hisoblagich/yozish) |
| `sfx.boom_sub` | L5 | Sub-boom (≈58 Hz) + dum |
| `sfx.deflate` | L5 | Gigant pufak havosi chiqadi: whoosh_sweep −7 yarim ton |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| Ovoz manbai | Foydalanuvchi SFX kutubxonasi (sfx/) | Birinchi qism: barcha UI, o'tish va zarba ovozlari foydalanuvchi yuborgan namunalardan (sfx.*): kliklar, qo'sh klik, pop_swish, swipe, whoosh, riser_click, stutter/glitch, notify, hit_low/hit_chime, boom_sub, tik va ratchet. Sintez faqat musiqiy qismlarda: partitura, J-cut swell, tonallikdagi qo'ng'iroqchalar (ui.select), success, uchqunlar, sonic logo, kassa. |
| 0:00–0:09.5 | Muammo · E-minor, tashvishli minimal | 7-qism aranjirovkasi asl tonallikda. Ustida: gigant tanlash (klik + pop), 'butun byudjet' (qo'sh klik + ding), hisoblagich (ratchet), kichik kanallar faolligi yuqori tik bilan lipillaydi, slamlar — stutter + qisqa glitch. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: gigant pufakning havosi chiqadi (whoosh_sweep 7 yarim ton pastda), yurak urishi. Keyin J-cut swell D-major'da. |
| 0:10.15–0:11 | Tarmoq yonadi | 12 ta pop_swish D-pentatonik zinapoyada chapdan o'ngga — kichik kanallar birin-ketin yonadi; piksel erishida glitch ketma-ketligi. |
| 0:11–0:21.75 | Yechim · D-major, siyrak | Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida: filtrlar (klik + tonallik qo'ng'irog'i + swipe), 'Tarmoqqa joylash' (qo'sh klik), yorug'lik to'lqini — 12 ta ko'tariluvchi pop, reaksiya hisoblagichi (ratchet), ×100 — notify_ring. |
| 0:22–0:27 | Natija · D-major, to'liq | To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Gigant — past pop, mikro-kanallar — tik + ko'tariluvchi poplar, kassa + ding; taqqoslash — swipe + klik. |
| 0:27–0:32 | Yakun · brend | ADUZ sonic logo (D tonikada), so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -21 dB | C | 0% | Xona — sahna 'havosi' |
| 0:00.05 | L4 | `sfx.whoosh_soft` | -14 dB | R30 | 20% | Telefon kadrga kiradi |
| 0:00.60 | L3 | `sfx.tick_roll` | -17 dB | L30 | 20% | Katalog: kichik kanallar xira paydo bo'ladi |
| 0:01.60 | L3 | `sfx.click_1` | -3 dB | R10 | 0% | Gigant tanlandi |
| 0:01.62 | L3 | `sfx.pop_swish` | -12 dB | R10 | 20% | Gigant kattalashadi |
| 0:02.60 | L3 | `sfx.click_double_1` | -3 dB | R20 | 0% | 'Butun byudjetni berish' |
| 0:02.70 | L3 | `sfx.notify_ring` | -10 dB | R20 | 25% | To'landi |
| 0:03.00 | L3 | `sfx.ratchet_roll` | -13 dB | L20 | 10% | Ko'rishlar sanalmoqda |
| 0:03.60 | L3 | `sfx.tick` | -15 dB | L60 | 30% | Kichik kanal faolligi lipillaydi #1 |
| 0:04.22 | L3 | `sfx.tick` | -15 dB | R15 | 30% | Kichik kanal faolligi lipillaydi #2 |
| 0:04.84 | L3 | `sfx.tick` | -15 dB | L45 | 30% | Kichik kanal faolligi lipillaydi #3 |
| 0:05.46 | L3 | `sfx.tick` | -15 dB | R30 | 30% | Kichik kanal faolligi lipillaydi #4 |
| 0:05.60 | L5 | `sfx.stutter` | -8 dB | L40 | 20% | Slam: FAQAT GIGANT |
| 0:05.60 | L5 | `sfx.glitch_short` | -6 dB | L40 | 20% | Slam qatlami |
| 0:06.00 | L3 | `sfx.notify_pop` | -10 dB | C | 20% | 1 reaksiya ≈ 21 000 so'm |
| 0:06.08 | L3 | `sfx.tick` | -15 dB | L30 | 30% | Kichik kanal faolligi lipillaydi #5 |
| 0:06.60 | L5 | `sfx.stutter` | -8 dB | R40 | 20% | Slam: QIMMAT |
| 0:06.60 | L5 | `sfx.glitch_short` | -6 dB | R40 | 20% | Slam qatlami |
| 0:06.70 | L3 | `sfx.tick` | -15 dB | R45 | 30% | Kichik kanal faolligi lipillaydi #6 |
| 0:07.32 | L3 | `sfx.tick` | -15 dB | L15 | 30% | Kichik kanal faolligi lipillaydi #7 |
| 0:07.60 | L5 | `sfx.stutter` | -8 dB | L40 | 20% | Slam: FAOLLIK 0.6% |
| 0:07.60 | L5 | `sfx.glitch_short` | -6 dB | L40 | 20% | Slam qatlami |
| 0:07.94 | L3 | `sfx.tick` | -15 dB | R60 | 30% | Kichik kanal faolligi lipillaydi #8 |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.38 | L4 | `sfx.riser_click` | -10 dB | C | 0% | Riser — cho'qqisi 9.5 s da, gate kesadi |
| 0:08.50 | L5 | `sfx.boom_sub` | -1 dB | C | 35% | BITTA GIGANT — asosiy zarba |
| 0:08.50 | L5 | `sfx.hit_low` | -4 dB | C | 40% | Zarba qatlami: tonal |
| 0:08.50 | L5 | `sfx.glitch_seq` | -11 dB | C | 20% | Zarba qatlami: glitch |
| 0:09.55 | L5 | `sfx.deflate` | -4 dB | C | 0% | OVOZ VAKUUMI: gigantning havosi chiqadi |
| 0:09.95 | L5 | `fx.heartbeat` | -11 dB | C | 0% | Yurak urishi |
| 0:10.15 | L4 | `tr.swell` | -8 dB | C | 30% | J-cut: yechim akkordi (D-major) |
| 0:10.15 | L3 | `sfx.pop_swish` | -16 dB | L60 | 30% | Mikro-kanal yonadi #1 |
| 0:10.18 | L3 | `sfx.pop_swish` | -16 dB | L49 | 30% | Mikro-kanal yonadi #2 |
| 0:10.22 | L3 | `sfx.pop_swish` | -16 dB | L38 | 30% | Mikro-kanal yonadi #3 |
| 0:10.25 | L3 | `sfx.pop_swish` | -16 dB | L27 | 30% | Mikro-kanal yonadi #4 |
| 0:10.28 | L3 | `sfx.pop_swish` | -16 dB | L16 | 30% | Mikro-kanal yonadi #5 |
| 0:10.31 | L3 | `sfx.pop_swish` | -16 dB | L5 | 30% | Mikro-kanal yonadi #6 |
| 0:10.35 | L3 | `sfx.pop_swish` | -16 dB | R6 | 30% | Mikro-kanal yonadi #7 |
| 0:10.38 | L3 | `sfx.pop_swish` | -16 dB | R17 | 30% | Mikro-kanal yonadi #8 |
| 0:10.41 | L3 | `sfx.pop_swish` | -16 dB | R28 | 30% | Mikro-kanal yonadi #9 |
| 0:10.45 | L3 | `sfx.pop_swish` | -16 dB | R39 | 30% | Mikro-kanal yonadi #10 |
| 0:10.48 | L3 | `sfx.pop_swish` | -16 dB | R50 | 30% | Mikro-kanal yonadi #11 |
| 0:10.51 | L3 | `sfx.pop_swish` | -16 dB | R61 | 30% | Mikro-kanal yonadi #12 |
| 0:10.55 | L5 | `sfx.glitch_seq` | -12 dB | C | 20% | Piksel eriydi — tarmoq ochiladi |
| 0:11.00 | L5 | `sfx.boom_sub` | -6 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L5 | `sfx.hit_chime` | -10 dB | C | 40% | Yechim: tonal urg'u |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `sfx.whoosh_soft` | -14 dB | L30 | 20% | Telefon kiradi |
| 0:11.30 | L3 | `sfx.tick_roll` | -13 dB | C | 20% | Tarmoq tugunlari paydo bo'ladi |
| 0:11.90 | L3 | `sfx.click_2` | -3 dB | L30 | 0% | Filtr #1 |
| 0:11.92 | L3 | `ui.select` | -17 dB | L30 | 25% | Filtr tasdig'i (tonallikda) |
| 0:12.00 | L4 | `sfx.swipe` | -11 dB | R20 | 15% | Mos kelmaganlar so'nadi |
| 0:12.40 | L3 | `sfx.click_3` | -3 dB | R20 | 0% | Filtr #2 |
| 0:12.42 | L3 | `ui.select` | -17 dB | R20 | 25% | Filtr tasdig'i (tonallikda) |
| 0:12.50 | L4 | `sfx.swipe` | -11 dB | R20 | 15% | Mos kelmaganlar so'nadi |
| 0:12.80 | L3 | `sfx.pop_swish` | -10 dB | C | 20% | Xulosa: 25 kanal |
| 0:12.85 | L3 | `sfx.ratchet_roll` | -15 dB | R20 | 10% | Obunachilar sanalmoqda |
| 0:14.00 | L3 | `sfx.click_double_2` | -3 dB | R20 | 0% | 'Tarmoqqa joylash' |
| 0:14.05 | L4 | `sfx.whoosh_soft` | -15 dB | C | 25% | Post tarmoqqa ketdi |
| 0:14.20 | L3 | `sfx.pop_swish` | -15 dB | L60 | 30% | Yorug'lik to'lqini: tugun #1 |
| 0:14.30 | L3 | `sfx.pop_swish` | -15 dB | L49 | 30% | Yorug'lik to'lqini: tugun #2 |
| 0:14.40 | L3 | `sfx.pop_swish` | -15 dB | L38 | 30% | Yorug'lik to'lqini: tugun #3 |
| 0:14.40 | L3 | `sfx.ratchet_roll` | -14 dB | L20 | 10% | Reaksiyalar o'smoqda |
| 0:14.50 | L3 | `sfx.pop_swish` | -15 dB | L27 | 30% | Yorug'lik to'lqini: tugun #4 |
| 0:14.60 | L3 | `sfx.pop_swish` | -15 dB | L16 | 30% | Yorug'lik to'lqini: tugun #5 |
| 0:14.70 | L3 | `sfx.pop_swish` | -15 dB | L5 | 30% | Yorug'lik to'lqini: tugun #6 |
| 0:14.80 | L3 | `sfx.pop_swish` | -15 dB | R6 | 30% | Yorug'lik to'lqini: tugun #7 |
| 0:14.90 | L3 | `sfx.pop_swish` | -15 dB | R17 | 30% | Yorug'lik to'lqini: tugun #8 |
| 0:15.00 | L3 | `sfx.pop_swish` | -15 dB | R28 | 30% | Yorug'lik to'lqini: tugun #9 |
| 0:15.10 | L3 | `sfx.pop_swish` | -15 dB | R39 | 30% | Yorug'lik to'lqini: tugun #10 |
| 0:15.20 | L3 | `sfx.pop_swish` | -15 dB | R50 | 30% | Yorug'lik to'lqini: tugun #11 |
| 0:15.30 | L3 | `sfx.pop_swish` | -15 dB | R61 | 30% | Yorug'lik to'lqini: tugun #12 |
| 0:15.60 | L3 | `sfx.ratchet_roll` | -16 dB | R20 | 10% | Reaksiyalar o'smoqda |
| 0:16.60 | L3 | `sfx.notify_ring` | -9 dB | R30 | 25% | ×100 reaksiya |
| 0:16.62 | L3 | `ui.success` | -14 dB | R30 | 40% | Musiqiy tasdiq |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: MIKRO-KUCH oldidan |
| 0:18.50 | L5 | `sfx.boom_sub` | -2 dB | C | 35% | MIKRO-KUCH — zarba |
| 0:18.50 | L5 | `sfx.hit_chime` | -6 dB | C | 40% | Zarba qatlami: tonal |
| 0:18.50 | L5 | `imp.sparkle` | -9 dB | C | 50% | Oltin uchqunlar |
| 0:19.70 | L4 | `sfx.swipe` | -10 dB | C | 20% | Oyna ko'tariladi |
| 0:19.90 | L3 | `ui.success` | -12 dB | C | 50% | Mikro-tarmoq ishda |
| 0:20.63 | L4 | `sfx.riser_click` | -10 dB | C | 0% | Riser — cho'qqisi whip'da (21.75 s) |
| 0:21.75 | L4 | `sfx.whoosh_sweep` | -8 dB | C | 25% | Whip-pan o'tishi |
| 0:21.75 | L4 | `sfx.swipe` | -10 dB | C | 20% | Whip qatlami |
| 0:22.00 | L5 | `sfx.boom_sub` | -4 dB | C | 40% | Natija boshlanishi |
| 0:22.00 | L5 | `sfx.hit_low` | -8 dB | C | 40% | Zarba qatlami |
| 0:22.20 | L3 | `sfx.pop_swish` | -10 dB | L40 | 20% | 1 gigant |
| 0:22.40 | L3 | `sfx.tick_roll` | -11 dB | R40 | 20% | 25 mikro-kanal to'planadi |
| 0:22.45 | L3 | `sfx.pop_swish` | -17 dB | R40 | 30% | Mikro #1 |
| 0:22.55 | L3 | `sfx.pop_swish` | -17 dB | R40 | 30% | Mikro #2 |
| 0:22.65 | L3 | `sfx.pop_swish` | -17 dB | R40 | 30% | Mikro #3 |
| 0:22.75 | L3 | `sfx.pop_swish` | -17 dB | R40 | 30% | Mikro #4 |
| 0:22.85 | L3 | `sfx.pop_swish` | -17 dB | R40 | 30% | Mikro #5 |
| 0:22.95 | L3 | `sfx.pop_swish` | -17 dB | R40 | 30% | Mikro #6 |
| 0:23.20 | L5 | `fx.kassa` | -10 dB | C | 30% | KASSA — 10.7% faollik |
| 0:23.22 | L3 | `sfx.notify_ring` | -12 dB | R20 | 25% | Kassa qatlami |
| 0:23.50 | L4 | `sfx.swipe` | -9 dB | L40 | 15% | 'Oldin' qatori #1 chizildi |
| 0:23.70 | L3 | `sfx.click_3` | -8 dB | R40 | 0% | ADUZ qatori #1 |
| 0:23.72 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:23.85 | L4 | `sfx.swipe` | -9 dB | L40 | 15% | 'Oldin' qatori #2 chizildi |
| 0:24.05 | L3 | `sfx.click_4` | -8 dB | R40 | 0% | ADUZ qatori #2 |
| 0:24.07 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:24.20 | L4 | `sfx.swipe` | -9 dB | L40 | 15% | 'Oldin' qatori #3 chizildi |
| 0:24.40 | L3 | `sfx.click_5` | -8 dB | R40 | 0% | ADUZ qatori #3 |
| 0:24.42 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:24.50 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: nishonlar oldidan |
| 0:25.00 | L5 | `sfx.boom_sub` | -7 dB | C | 40% | Urg'u |
| 0:25.00 | L5 | `imp.sparkle` | -8 dB | C | 50% | Uchqunlar |
| 0:25.20 | L3 | `sfx.pop_swish` | -10 dB | L40 | 30% | Nishon #1 |
| 0:25.22 | L3 | `ui.select` | -20 dB | L40 | 30% | Tonallikdagi qo'ng'iroqcha |
| 0:25.45 | L3 | `sfx.pop_swish` | -10 dB | C | 30% | Nishon #2 |
| 0:25.47 | L3 | `ui.select` | -20 dB | C | 30% | Tonallikdagi qo'ng'iroqcha |
| 0:25.70 | L3 | `sfx.pop_swish` | -10 dB | R40 | 30% | Nishon #3 |
| 0:25.72 | L3 | `ui.select` | -20 dB | R40 | 30% | Tonallikdagi qo'ng'iroqcha |
| 0:26.85 | L4 | `sfx.whoosh_soft` | -14 dB | C | 40% | Yakuniy kadrga |
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (D tonikada) |
| 0:28.30 | L3 | `sfx.click_1` | -9 dB | R20 | 30% | CTA tugmasi |
| 0:28.32 | L3 | `ui.select` | -23 dB | R20 | 50% | CTA qo'ng'iroqchasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
