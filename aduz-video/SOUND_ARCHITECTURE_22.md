# ADUZ 22-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 22 --cuesheet SOUND_ARCHITECTURE_22.md`).

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
| `sfx.stamp_big` | L5 | Katta muhr 'RAD ETILDI': boom_sub + hit_low −5 + qo'sh klik −12 |
| `sfx.splat` | L5 | Siyoh sachrashi: pop_swish −12 + glitch_short −12 |
| `sfx.dust` | L5 | Kulga aylanish: glitch_noise +5, sekin kuchayib |
| `sfx.gavel` | L5 | Sudya bolg'asi: boom_sub + hit_low +5 + qo'sh klik −10 |
| `mus.choir_d` | L1 | Xor 'aaah' D-major (heavenly uslub, original sintez) |
| `mus.choir_g` | L1 | Xor 'aaah' G-major |
| `mus.choir_hi` | L1 | Baland xor 'ooo' — uchqunlar ustida |
| `sfx.bass_drop` | L5 | Past bass-zarba (matn chiqishi) |
| `sfx.tick_hi` | L3 | Yuqori matn tiki (6.5 kHz) |
| `sfx.shimmer` | L3 | Yaltiroq shimmer (8.7 kHz tonal) |
| `sfx.type_burst` | L3 | Yozish shitirlashi (typewriter) |
| `sfx.blip_up` | L3 | Ko'tariluvchi bliplar |
| `sfx.sparkle_hit` | L5 | Sparkle-zarba |
| `sfx.swoosh_text` | L4 | Matn whoosh'i |
| `sfx.whoosh_low` | L4 | Past whoosh / swell |
| `sfx.thump` | L5 | Qisqa thump |
| `sfx.pluck_tone` | L3 | Tonal pluck (0.75 s) |
| `sfx.pop_short` | L3 | Qisqa pop |
| `sfx.click_soft` | L3 | Yumshoq klik |
| `sfx.chime_swell` | L3 | Chime-swell |
| `sfx.letters_fall` | L3 | Harflar birin-ketin tushadi: 20 ta tick_hi turli balandlikda |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| Ovoz manbai | sfx/ kutubxonasi (39 ta) + FX v2 + yangi musiqa uslubi | Matn animatsiyalari uchun yangi namunalar: tick_hi (harflar), swoosh_text (blur/word), type_burst (typewriter), blip_up (letter-up), bass_drop + sparkle_hit (bounce), shimmer (flicker), pop_short, click_soft, thump, chime_swell, whoosh_low. Musiqa: 7-qism partiturasi + ORIGINAL 'heavenly' xor (formant 'aaah') va o'ynoqi-sirli pizzicato (Karplus-Strong) — foydalanuvchi referenslari kayfiyatida, lekin ularning o'zi emas. |
| 0:00–0:09.5 | Muammo · E-minor + pizzicato | 7-qism aranjirovkasi asl tonallikda + o'ynoqi-sirli pizzicato motivi (8-lik notalar, xromatik pasayish, tritonga ishora; chap-o'ng navbatma-navbat). Lenta aylanishi (yumshoq whoosh), har to'xtash — yumshoq klik, har flick — swipe + glitch; slamlar — stutter + glitch. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: zerikarli postning harflari birin-ketin tushadi — 20 ta tick_hi turli balandlikda; yurak urishi. |
| 0:10.15–0:11 | Vahiy lahzasi | HEAVENLY XOR 'aaah' D-major'da (original sintez) + past whoosh (zoom-through) + shimmer. |
| 0:11–0:21.75 | Yechim · D-major, siyrak | Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Har kinetik matn presetining o'z ovozi: bounce — bass_drop + sparkle, letter-up — blip_up, typewriter — type_burst, flicker — shimmer + glitch. Lenta to'xtaganda — thump + sparkle + baland xor 'ooo'. |
| 0:22–0:27 | Natija · D-major, to'liq | To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. Kassa (ssenariydagi 'kassa ovozi'). |
| 0:27–0:32 | Yakun · brend | ADUZ sonic logo (D tonikada) ostida yumshoq xor, so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -22 dB | C | 0% | Xona — sahna 'havosi' |
| 0:00.05 | L4 | `sfx.whoosh_soft` | -14 dB | R30 | 20% | Telefon kadrga kiradi |
| 0:00.15 | L3 | `sfx.tick_hi` | -12 dB | C | 20% | '22-QISM' harflari tushadi |
| 0:00.30 | L4 | `sfx.swoosh_text` | -10 dB | C | 20% | Sarlavha blur-fade-up |
| 0:00.60 | L4 | `sfx.whoosh_soft` | -18 dB | R20 | 15% | Lenta aylanadi #1 |
| 0:01.30 | L3 | `sfx.click_soft` | -10 dB | C | 10% | Ko'z to'xtadi — 1.5 s |
| 0:02.80 | L4 | `sfx.swipe` | -6 dB | R30 | 15% | O'TIB KETILDI #1 (flick) |
| 0:02.95 | L5 | `sfx.glitch_short` | -13 dB | R30 | 10% | RGB glitch |
| 0:03.60 | L4 | `sfx.whoosh_soft` | -18 dB | R20 | 15% | Lenta aylanadi #2 |
| 0:04.30 | L3 | `sfx.click_soft` | -10 dB | C | 10% | Ko'z to'xtadi — 0.6 s |
| 0:04.90 | L4 | `sfx.swipe` | -6 dB | R30 | 15% | O'TIB KETILDI #2 (flick) |
| 0:05.05 | L5 | `sfx.glitch_short` | -13 dB | R30 | 10% | RGB glitch |
| 0:05.60 | L5 | `sfx.stutter` | -8 dB | L40 | 20% | Slam: ZERIKARLI |
| 0:05.60 | L5 | `sfx.glitch_short` | -6 dB | L40 | 20% | Slam qatlami |
| 0:05.70 | L4 | `sfx.whoosh_soft` | -18 dB | R20 | 15% | Lenta aylanadi #3 |
| 0:06.40 | L3 | `sfx.click_soft` | -10 dB | C | 10% | Ko'z to'xtadi — 0.3 s |
| 0:06.60 | L5 | `sfx.stutter` | -8 dB | R40 | 20% | Slam: UZUN MATN |
| 0:06.60 | L5 | `sfx.glitch_short` | -6 dB | R40 | 20% | Slam qatlami |
| 0:06.75 | L4 | `sfx.swipe` | -6 dB | R30 | 15% | O'TIB KETILDI #3 (flick) |
| 0:06.90 | L5 | `sfx.glitch_short` | -13 dB | R30 | 10% | RGB glitch |
| 0:07.60 | L5 | `sfx.stutter` | -8 dB | L40 | 20% | Slam: O'TIB KETILDI |
| 0:07.60 | L5 | `sfx.glitch_short` | -6 dB | L40 | 20% | Slam qatlami |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.38 | L4 | `sfx.riser_click` | -10 dB | C | 0% | Riser — cho'qqisi 9.5 s da |
| 0:08.50 | L5 | `sfx.boom_sub` | -1 dB | C | 35% | KO'RINMAS — asosiy zarba |
| 0:08.50 | L5 | `sfx.bass_drop` | -4 dB | C | 30% | Zarba qatlami: bass drop |
| 0:08.50 | L5 | `sfx.glitch_seq` | -12 dB | C | 20% | Zarba qatlami: glitch |
| 0:09.60 | L3 | `sfx.letters_fall` | -7 dB | C | 0% | OVOZ VAKUUMI: harflar birin-ketin tushadi |
| 0:09.95 | L5 | `fx.heartbeat` | -12 dB | C | 0% | Yurak urishi |
| 0:10.15 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: yechim akkordi (D-major) |
| 0:10.20 | L1 | `mus.choir_d` | +2 dB | C | 60% | HEAVENLY XOR 'aaah' — vahiy lahzasi |
| 0:10.45 | L4 | `sfx.whoosh_low` | -8 dB | C | 30% | Zoom-through o'tishi |
| 0:10.75 | L3 | `sfx.shimmer` | -10 dB | C | 40% | Flare yaltirog'i |
| 0:11.00 | L5 | `sfx.boom_sub` | -7 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `sfx.whoosh_soft` | -14 dB | L30 | 20% | Telefon kiradi |
| 0:11.40 | L3 | `sfx.pop_short` | -10 dB | L40 | 20% | Shablon #1 paydo bo'ladi |
| 0:11.50 | L3 | `sfx.pop_short` | -10 dB | L13 | 20% | Shablon #2 paydo bo'ladi |
| 0:11.60 | L3 | `sfx.pop_short` | -10 dB | R14 | 20% | Shablon #3 paydo bo'ladi |
| 0:11.70 | L3 | `sfx.pop_short` | -10 dB | R41 | 20% | Shablon #4 paydo bo'ladi |
| 0:11.80 | L3 | `sfx.shimmer` | -18 dB | L40 | 30% | Shablon #1 yaltiraydi |
| 0:11.92 | L3 | `sfx.shimmer` | -18 dB | L13 | 30% | Shablon #2 yaltiraydi |
| 0:12.04 | L3 | `sfx.shimmer` | -18 dB | R14 | 30% | Shablon #3 yaltiraydi |
| 0:12.10 | L3 | `sfx.click_1` | -3 dB | L30 | 0% | '−30%' shabloni tanlandi |
| 0:12.16 | L3 | `sfx.shimmer` | -18 dB | R41 | 30% | Shablon #4 yaltiraydi |
| 0:12.25 | L4 | `sfx.swipe` | -10 dB | R30 | 15% | Konstruktorga o'tish |
| 0:12.70 | L5 | `sfx.bass_drop` | -8 dB | C | 30% | '−30%' BOUNCE |
| 0:12.72 | L5 | `sfx.sparkle_hit` | -10 dB | C | 30% | Bounce yaltirog'i |
| 0:13.00 | L3 | `sfx.blip_up` | -9 dB | C | 25% | 'YANGI KOLLEKSIYA' letter-up |
| 0:13.30 | L3 | `sfx.type_burst` | -8 dB | R20 | 15% | 'Faqat 3 kun!' typewriter |
| 0:13.60 | L3 | `sfx.pop_short` | -9 dB | C | 20% | 'Buyurtma berish' tugmasi |
| 0:14.00 | L3 | `sfx.click_2` | -3 dB | R10 | 0% | Animatsiya: Flicker |
| 0:14.05 | L3 | `sfx.shimmer` | -9 dB | C | 30% | FLICKER — sarlavha qayta jonlanadi |
| 0:14.05 | L5 | `sfx.glitch_short` | -15 dB | C | 20% | Flicker glitch |
| 0:14.50 | L3 | `sfx.click_3` | -3 dB | L20 | 0% | Brend rangi tanlandi |
| 0:14.52 | L3 | `sfx.chime_swell` | -10 dB | C | 30% | Rang almashadi |
| 0:15.20 | L3 | `sfx.click_double_2` | -3 dB | R20 | 0% | 'Kanallarga yuborish' |
| 0:15.32 | L3 | `sfx.tick` | -14 dB | R30 | 30% | Tugma yaltiraydi (glint) |
| 0:15.45 | L4 | `sfx.swoosh_text` | -9 dB | R30 | 20% | Lentaga o'tish |
| 0:15.60 | L4 | `sfx.whoosh_soft` | -17 dB | C | 20% | Lenta aylanadi... |
| 0:16.60 | L5 | `sfx.thump` | -6 dB | C | 25% | ...va TO'XTAYDI — sizning reklamangizda |
| 0:16.62 | L5 | `sfx.sparkle_hit` | -9 dB | C | 30% | Ko'z to'xtadi |
| 0:16.65 | L1 | `mus.choir_hi` | -4 dB | C | 60% | Xor 'ooo' — ko'z to'xtadi |
| 0:16.90 | L3 | `sfx.ratchet_roll` | -14 dB | L20 | 15% | Statistika o'smoqda |
| 0:17.30 | L3 | `sfx.tick` | -14 dB | R20 | 30% | Statistika kartasi yaltiraydi |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: KO'Z TO'XTAYDI oldidan |
| 0:18.45 | L4 | `sfx.whoosh_soft` | -18 dB | C | 40% | Oltin nurlar ochiladi |
| 0:18.50 | L5 | `sfx.boom_sub` | -2 dB | C | 35% | KO'Z TO'XTAYDI — zarba |
| 0:18.50 | L5 | `sfx.bass_drop` | -6 dB | C | 30% | Color-bounce zarbasi |
| 0:18.50 | L1 | `mus.choir_d` | -2 dB | C | 60% | Xor 'aaah' zarba ostida |
| 0:18.50 | L5 | `imp.sparkle` | -10 dB | C | 50% | Oltin uchqunlar |
| 0:18.75 | L4 | `sfx.swoosh_text` | -10 dB | C | 20% | Taglavha blur-fade-up |
| 0:19.70 | L4 | `sfx.swipe` | -10 dB | C | 20% | Oyna ko'tariladi |
| 0:19.90 | L3 | `ui.success` | -12 dB | C | 50% | Reklama tayyor |
| 0:20.30 | L3 | `sfx.blip_up` | -10 dB | C | 25% | 'Reklama tayyor!' letter-up |
| 0:20.63 | L4 | `sfx.riser_click` | -10 dB | C | 0% | Riser — cho'qqisi whip'da (21.75 s) |
| 0:21.75 | L4 | `sfx.whoosh_sweep` | -8 dB | C | 25% | Whip-pan o'tishi |
| 0:21.75 | L4 | `sfx.swipe` | -10 dB | C | 20% | Whip qatlami |
| 0:22.00 | L5 | `sfx.boom_sub` | -6 dB | C | 40% | Natija boshlanishi |
| 0:22.20 | L3 | `sfx.tick_hi` | -12 dB | C | 20% | 'NATIJA' harflari |
| 0:22.30 | L4 | `sfx.swoosh_text` | -10 dB | R20 | 20% | Sarlavha word-right |
| 0:22.35 | L3 | `sfx.pop_short` | -10 dB | L40 | 20% | Oldingi post |
| 0:22.60 | L5 | `sfx.bass_drop` | -7 dB | R40 | 30% | Yangi karta — bounce |
| 0:22.62 | L5 | `sfx.sparkle_hit` | -10 dB | R40 | 30% | Karta yaltiraydi |
| 0:23.20 | L5 | `fx.kassa` | -10 dB | C | 30% | KASSA — CTR 3.8% |
| 0:23.22 | L3 | `sfx.notify_ring` | -13 dB | R20 | 25% | Kassa qatlami |
| 0:23.50 | L4 | `sfx.swipe` | -9 dB | L40 | 15% | 'Oldin' qatori #1 chizildi |
| 0:23.70 | L3 | `sfx.click_4` | -8 dB | R40 | 0% | ADUZ qatori #1 |
| 0:23.72 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:23.85 | L4 | `sfx.swipe` | -9 dB | L40 | 15% | 'Oldin' qatori #2 chizildi |
| 0:24.05 | L3 | `sfx.click_5` | -8 dB | R40 | 0% | ADUZ qatori #2 |
| 0:24.07 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:24.20 | L4 | `sfx.swipe` | -9 dB | L40 | 15% | 'Oldin' qatori #3 chizildi |
| 0:24.40 | L3 | `sfx.click_1` | -8 dB | R40 | 0% | ADUZ qatori #3 |
| 0:24.42 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:24.50 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: nishonlar oldidan |
| 0:25.00 | L5 | `sfx.boom_sub` | -7 dB | C | 40% | Urg'u |
| 0:25.00 | L3 | `sfx.shimmer` | -12 dB | C | 40% | Flare yaltirog'i |
| 0:25.00 | L5 | `imp.sparkle` | -9 dB | C | 50% | Uchqunlar |
| 0:25.20 | L3 | `sfx.pop_short` | -10 dB | L40 | 30% | Nishon #1 |
| 0:25.22 | L3 | `ui.select` | -20 dB | L40 | 30% | Tonallikdagi qo'ng'iroqcha |
| 0:25.45 | L3 | `sfx.pop_short` | -10 dB | C | 30% | Nishon #2 |
| 0:25.47 | L3 | `ui.select` | -20 dB | C | 30% | Tonallikdagi qo'ng'iroqcha |
| 0:25.70 | L3 | `sfx.pop_short` | -10 dB | R40 | 30% | Nishon #3 |
| 0:25.72 | L3 | `ui.select` | -20 dB | R40 | 30% | Tonallikdagi qo'ng'iroqcha |
| 0:26.85 | L4 | `sfx.whoosh_soft` | -14 dB | C | 40% | Yakuniy kadrga |
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (D tonikada) |
| 0:27.00 | L1 | `mus.choir_d` | -6 dB | C | 60% | Xor logotip ostida |
| 0:28.30 | L3 | `sfx.click_1` | -9 dB | R20 | 30% | CTA tugmasi |
| 0:28.32 | L3 | `ui.select` | -23 dB | R20 | 50% | CTA qo'ng'iroqchasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
