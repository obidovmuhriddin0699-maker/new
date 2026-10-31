# ADUZ 25-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 25 --cuesheet SOUND_ARCHITECTURE_25.md`).

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
| `mus.choir_c` | L1 | Xor 'aaah' C-major (heavenly uslub, original sintez) |
| `mus.choir_c_hi` | L1 | Baland xor 'ooo' C-major |
| `sfx.cool_down` | L5 | Iliq mijoz 'soviydi': whoosh_sweep −9, so'nib |
| `mus.choir_b` | L1 | Xor 'aaah' B-major (heavenly uslub, original sintez) |
| `mus.choir_b_hi` | L1 | Baland xor 'ooo' B-major |
| `mus.choir_g_hi` | L1 | Baland xor 'ooo' G-major |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| Ovoz manbai | BUTUN kutubxona: sfx/ + 1–21-qism sintez ovozlari + xor + pizzicato | Foydalanuvchi: 'barcha dizayn va ovozlardan foydalan'. Har dunyo o'z ovoz palitrasida: ofis — amb.office, soat, notify_pop, kabel (fx.twang + fx.chain), klassik imp.glitch/imp.boom; vakuum — fx.padlock + tr.crt_off; o'tish — tr.implode + tr.boot; bozor — qushlar, vibratsiya, fx.stamp; tungi yo'l — o'tayotgan mashinalar (whoosh_low), neon g'uvullashi, fx.transfer, fx.switch; choyxona — reel ovozlari (pop kaskadi, type_burst, tick_hi keyframe'lar). |
| 0:00–0:09.5 | Muammo · A-minor + pizzicato | 7-qism aranjirovkasi 5 yarim ton yuqorida + pizzicato (A). Har yangi buyurtma — notify_pop (pentatonik ko'tariladi: bosim o'sadi), devor soati, 4.0 s dan kabel taranglashadi (twang + chain); slamlar — stutter + klassik imp.glitch; 7.0 s ogohlantirish. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: qulf yopiladi (fx.padlock), monitor eski televizorday o'chadi (tr.crt_off), yurak urishi. |
| 0:10.15–0:11 | Vahiy · pocketZoom | HEAVENLY XOR G-major'da; ofis telefonga so'riladi (tr.implode), telefon yonadi (tr.boot, G). |
| 0:11–0:21.75 | Yechim · G-major, uch dunyo | Bozor (qushlar, buyurtma — vibratsiya + ring, tasdiq — klik + muhr + success) → neon halqa (whoosh_sweep + glitch) → tungi yo'l (mashinalar, byudjet — transfer, toggle — switch) → plitkalar to'lqini → choyxona (scramble, +18, avto-javob). 18.5 s: ISTALGAN / JOYDAN. — ikki zarba + crash + xor. Kun keyframe'lari — tick_hi. |
| 0:22–0:27 | Natija · G-major, to'liq | Uch panel — har biri o'z dunyosi ovozida (snap / lcd / bass_drop), kassa + tanga, 'Oldin' qatorlari — fx.strike. |
| 0:27–0:32 | Yakun · brend | Uch logotip stutter (hit_chime / hit_tone / hit_low), sonic logo (G) + xor, harflar tushishi, CTA. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -20 dB | C | 0% | Ofis — ventilyatsiya, 50 Hz g'uvullash |
| 0:00.05 | L4 | `tr.whoosh` | -14 dB | R30 | 20% | Monitor va xarita kiradi |
| 0:00.15 | L3 | `sfx.tick_hi` | -13 dB | C | 20% | '25-QISM' harflari |
| 0:00.30 | L4 | `sfx.swoosh_text` | -11 dB | C | 20% | 'Mutlaq erkinlik' blur-up |
| 0:01.00 | L3 | `fx.tick` | -23 dB | L40 | 0% | Devor soati |
| 0:01.00 | L4 | `sfx.whoosh_soft` | -18 dB | R40 | 20% | Egasi ofisdan chiqib ketadi |
| 0:01.40 | L3 | `sfx.notify_pop` | -10 dB | L30 | 15% | Monitorda yangi buyurtma #1 |
| 0:01.50 | L3 | `fx.tick` | -23 dB | L40 | 0% | Devor soati |
| 0:02.00 | L3 | `fx.tick` | -23 dB | L40 | 0% | Devor soati |
| 0:02.30 | L3 | `sfx.notify_pop` | -10 dB | L24 | 15% | Monitorda yangi buyurtma #2 |
| 0:02.50 | L3 | `fx.tick` | -23 dB | L40 | 0% | Devor soati |
| 0:03.00 | L3 | `fx.tick` | -23 dB | L40 | 0% | Devor soati |
| 0:03.10 | L3 | `sfx.notify_pop` | -10 dB | L18 | 15% | Monitorda yangi buyurtma #3 |
| 0:03.50 | L3 | `fx.tick` | -23 dB | L40 | 0% | Devor soati |
| 0:03.90 | L3 | `sfx.notify_pop` | -10 dB | L12 | 15% | Monitorda yangi buyurtma #4 |
| 0:04.00 | L3 | `fx.tick` | -23 dB | L40 | 0% | Devor soati |
| 0:04.00 | L4 | `fx.twang` | -10 dB | R30 | 20% | Kabel taranglashdi |
| 0:04.05 | L5 | `fx.chain` | -12 dB | R30 | 20% | Kabel — zanjirday |
| 0:04.50 | L3 | `fx.tick` | -23 dB | L40 | 0% | Devor soati |
| 0:04.60 | L3 | `sfx.notify_pop` | -10 dB | L6 | 15% | Monitorda yangi buyurtma #5 |
| 0:05.30 | L3 | `sfx.notify_pop` | -10 dB | C | 15% | Monitorda yangi buyurtma #6 |
| 0:05.60 | L5 | `sfx.stutter` | -8 dB | L40 | 20% | Slam: OFISGA BOG'LIQ |
| 0:05.60 | L5 | `imp.glitch` | -9 dB | L40 | 20% | Klassik slam qatlami |
| 0:05.68 | L4 | `fx.twang` | -13 dB | R40 | 15% | Kabel egasini orqaga tortadi |
| 0:06.00 | L3 | `sfx.notify_pop` | -10 dB | R6 | 15% | Monitorda yangi buyurtma #7 |
| 0:06.60 | L5 | `sfx.stutter` | -8 dB | R40 | 20% | Slam: BUYURTMA KUTMOQDA |
| 0:06.60 | L5 | `imp.glitch` | -9 dB | R40 | 20% | Klassik slam qatlami |
| 0:06.68 | L4 | `fx.twang` | -13 dB | R40 | 15% | Kabel egasini orqaga tortadi |
| 0:06.70 | L3 | `sfx.notify_pop` | -10 dB | R12 | 15% | Monitorda yangi buyurtma #8 |
| 0:07.00 | L5 | `fx.alarm` | -16 dB | C | 20% | Javobsiz buyurtmalar — ogohlantirish |
| 0:07.30 | L3 | `sfx.notify_pop` | -10 dB | R18 | 15% | Monitorda yangi buyurtma #9 |
| 0:07.60 | L5 | `sfx.stutter` | -8 dB | L40 | 20% | Slam: KECH QOLDINGIZ |
| 0:07.60 | L5 | `imp.glitch` | -9 dB | L40 | 20% | Klassik slam qatlami |
| 0:07.68 | L4 | `fx.twang` | -13 dB | R40 | 15% | Kabel egasini orqaga tortadi |
| 0:07.90 | L3 | `sfx.notify_pop` | -10 dB | R24 | 15% | Monitorda yangi buyurtma #10 |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.38 | L4 | `sfx.riser_click` | -10 dB | C | 0% | Riser — cho'qqisi 9.5 s da |
| 0:08.50 | L5 | `sfx.boom_sub` | -1 dB | C | 35% | QARAMLIK — asosiy zarba |
| 0:08.50 | L5 | `imp.boom` | -8 dB | C | 30% | Klassik boom qatlami |
| 0:08.50 | L5 | `fx.chain` | -6 dB | C | 30% | Zanjirlar monitorni o'raydi |
| 0:08.70 | L4 | `sfx.swoosh_text` | -12 dB | C | 20% | Taglavha blur-up |
| 0:09.60 | L5 | `fx.padlock` | -10 dB | C | 0% | OVOZ VAKUUMI: qulf yopildi |
| 0:09.80 | L4 | `tr.crt_off` | -12 dB | C | 10% | Monitor eski televizorday o'chadi |
| 0:09.95 | L5 | `fx.heartbeat` | -12 dB | C | 0% | Yurak urishi |
| 0:10.15 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: yechim akkordi (G-major) |
| 0:10.20 | L1 | `mus.choir_g` | +2 dB | C | 60% | HEAVENLY XOR 'aaah' — ofis cho'ntakka sig'adi |
| 0:10.30 | L4 | `tr.implode` | -9 dB | C | 20% | Butun ofis telefon ekraniga so'riladi |
| 0:10.85 | L4 | `tr.boot` | -10 dB | C | 30% | Telefon yonadi |
| 0:10.95 | L3 | `sfx.shimmer` | -10 dB | C | 40% | Flare |
| 0:11.00 | L5 | `sfx.boom_sub` | -7 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -30 dB | C | 0% | Ochiq havo |
| 0:11.05 | L2 | `fx.birds` | -18 dB | L50 | 30% | Bozor ertalabi: qushlar |
| 0:11.50 | L3 | `ui.popup` | -12 dB | C | 20% | Buyurtma kartasi |
| 0:11.90 | L3 | `fx.vibrate` | -15 dB | C | 0% | Telefon titraydi |
| 0:11.92 | L3 | `sfx.notify_ring` | -10 dB | R20 | 25% | Yangi buyurtma! |
| 0:12.60 | L3 | `sfx.click_1` | -3 dB | R20 | 0% | 'Tasdiqlash' |
| 0:12.62 | L3 | `fx.stamp` | -10 dB | C | 20% | Tasdiqlandi — muhr |
| 0:12.75 | L3 | `ui.success` | -14 dB | C | 50% | Yashil tasdiq |
| 0:12.80 | L5 | `sfx.sparkle_hit` | -12 dB | C | 30% | Uchqunlar |
| 0:14.30 | L4 | `sfx.whoosh_sweep` | -9 dB | C | 25% | Neon halqa — dunyo almashadi |
| 0:14.45 | L5 | `sfx.glitch_short` | -12 dB | C | 20% | RGB glitch |
| 0:14.60 | L4 | `sfx.whoosh_low` | -18 dB | L60 | 30% | O'tib ketayotgan mashina #1 |
| 0:14.60 | L3 | `fx.flicker` | -18 dB | R40 | 20% | Neon vivesqa g'uvullashi |
| 0:15.30 | L3 | `sfx.notify_pop` | -10 dB | L20 | 20% | Andijon Savdo: ko'rish 2x |
| 0:15.35 | L4 | `sfx.whoosh_low` | -18 dB | R60 | 30% | O'tib ketayotgan mashina #2 |
| 0:15.90 | L3 | `sfx.click_2` | -3 dB | R20 | 0% | 'Byudjet +50 000' |
| 0:15.95 | L3 | `fx.transfer` | -11 dB | R20 | 20% | Byudjet o'tkazildi |
| 0:16.00 | L3 | `sfx.ratchet_roll` | -15 dB | C | 15% | Byudjet chizig'i o'sadi |
| 0:16.10 | L4 | `sfx.whoosh_low` | -18 dB | L60 | 30% | O'tib ketayotgan mashina #3 |
| 0:16.60 | L3 | `fx.switch` | -9 dB | R30 | 10% | Avto-optimallash yoqildi |
| 0:16.62 | L3 | `sfx.blip_up` | -11 dB | R30 | 25% | Toggle firuza |
| 0:16.85 | L4 | `sfx.whoosh_low` | -18 dB | R60 | 30% | O'tib ketayotgan mashina #4 |
| 0:17.60 | L3 | `sfx.pop_short` | -14 dB | L40 | 20% | Plitkalar to'lqini #1 |
| 0:17.68 | L3 | `sfx.pop_short` | -14 dB | C | 20% | Plitkalar to'lqini #2 |
| 0:17.75 | L3 | `sfx.type_burst` | -11 dB | C | 15% | 'CHOYXONA 13:05' dekodlanadi |
| 0:17.76 | L3 | `sfx.pop_short` | -14 dB | R40 | 20% | Plitkalar to'lqini #3 |
| 0:17.90 | L3 | `sfx.tick_roll` | -16 dB | C | 20% | +18 buyurtma sanaladi |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: ISTALGAN JOYDAN oldidan |
| 0:18.15 | L3 | `sfx.click_3` | -3 dB | R20 | 0% | 'Avto-javob' toggle |
| 0:18.45 | L4 | `sfx.whoosh_low` | -10 dB | C | 30% | Laym karta butun kadrga |
| 0:18.50 | L5 | `sfx.boom_sub` | -2 dB | C | 35% | ISTALGAN — zarba |
| 0:18.50 | L5 | `sfx.bass_drop` | -6 dB | C | 30% | Og'ir grotesk |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 40% | Klassik crash |
| 0:18.50 | L1 | `mus.choir_g` | -2 dB | C | 60% | Xor 'aaah' zarba ostida |
| 0:18.50 | L5 | `imp.sparkle` | -10 dB | C | 50% | Uchqunlar |
| 0:18.60 | L5 | `sfx.thump` | -7 dB | C | 25% | JOYDAN. — ikkinchi zarba |
| 0:18.80 | L4 | `sfx.swoosh_text` | -10 dB | C | 20% | 'bir telefon — butun biznes' |
| 0:19.70 | L4 | `sfx.swipe` | -10 dB | C | 20% | Binafsha karta |
| 0:20.00 | L3 | `sfx.shimmer` | -13 dB | C | 30% | 'Ofis — endi cho'ntagingizda.' |
| 0:20.46 | L3 | `sfx.tick_hi` | -14 dB | L40 | 25% | Kun keyframe #1 |
| 0:20.57 | L3 | `sfx.tick_hi` | -14 dB | L30 | 25% | Kun keyframe #2 |
| 0:20.63 | L4 | `sfx.riser_click` | -10 dB | C | 0% | Riser — whip'ga |
| 0:20.74 | L3 | `sfx.tick_hi` | -14 dB | L20 | 25% | Kun keyframe #3 |
| 0:20.77 | L3 | `sfx.tick_hi` | -14 dB | L10 | 25% | Kun keyframe #4 |
| 0:20.81 | L3 | `sfx.tick_hi` | -14 dB | C | 25% | Kun keyframe #5 |
| 0:20.89 | L3 | `sfx.tick_hi` | -14 dB | R10 | 25% | Kun keyframe #6 |
| 0:20.94 | L3 | `sfx.tick_hi` | -14 dB | R20 | 25% | Kun keyframe #7 |
| 0:21.01 | L3 | `sfx.tick_hi` | -14 dB | R30 | 25% | Kun keyframe #8 |
| 0:21.35 | L3 | `ui.success` | -12 dB | C | 50% | HAMMASI NAZORATDA |
| 0:21.75 | L4 | `tr.whip` | -8 dB | C | 25% | Whip-pan (klassik) |
| 0:21.75 | L4 | `sfx.whoosh_sweep` | -10 dB | C | 25% | Whip qatlami |
| 0:22.00 | L5 | `sfx.boom_sub` | -6 dB | C | 40% | Natija boshlanishi |
| 0:22.15 | L3 | `fx.snap` | -10 dB | L50 | 20% | Panel: BOZOR (klassik) |
| 0:22.20 | L3 | `sfx.tick_hi` | -12 dB | C | 20% | 'NATIJA' |
| 0:22.30 | L4 | `sfx.swoosh_text` | -10 dB | R20 | 20% | Sarlavha word-right |
| 0:22.30 | L3 | `fx.lcd` | -12 dB | C | 20% | Panel: YO'L (neon) |
| 0:22.45 | L5 | `sfx.bass_drop` | -10 dB | R50 | 25% | Panel: CHOYXONA (reel) |
| 0:23.20 | L5 | `fx.kassa` | -10 dB | C | 30% | KASSA |
| 0:23.22 | L3 | `fx.coin` | -18 dB | R30 | 20% | Tanga |
| 0:23.50 | L3 | `fx.strike` | -10 dB | L40 | 15% | 'Oldin' qatori #1 chizildi |
| 0:23.70 | L3 | `sfx.click_3` | -8 dB | R40 | 0% | ADUZ qatori #1 |
| 0:23.72 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:23.85 | L3 | `fx.strike` | -10 dB | L40 | 15% | 'Oldin' qatori #2 chizildi |
| 0:24.05 | L3 | `sfx.click_4` | -8 dB | R40 | 0% | ADUZ qatori #2 |
| 0:24.07 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:24.20 | L3 | `fx.strike` | -10 dB | L40 | 15% | 'Oldin' qatori #3 chizildi |
| 0:24.40 | L3 | `sfx.click_5` | -8 dB | R40 | 0% | ADUZ qatori #3 |
| 0:24.42 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:24.50 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: nishonlar oldidan |
| 0:25.00 | L5 | `sfx.boom_sub` | -7 dB | C | 40% | Urg'u |
| 0:25.00 | L5 | `imp.sparkle` | -9 dB | C | 50% | Oltin uchqunlar |
| 0:25.20 | L3 | `sfx.pop_short` | -10 dB | L40 | 30% | Oltin nishon #1 |
| 0:25.22 | L3 | `ui.select` | -20 dB | L40 | 30% | Qo'ng'iroqcha |
| 0:25.45 | L3 | `sfx.pop_short` | -10 dB | C | 30% | Oltin nishon #2 |
| 0:25.47 | L3 | `ui.select` | -20 dB | C | 30% | Qo'ng'iroqcha |
| 0:25.70 | L3 | `sfx.pop_short` | -10 dB | R40 | 30% | Oltin nishon #3 |
| 0:25.72 | L3 | `ui.select` | -20 dB | R40 | 30% | Qo'ng'iroqcha |
| 0:26.60 | L4 | `sfx.whoosh_soft` | -14 dB | C | 40% | Yakunga |
| 0:27.00 | L5 | `sfx.hit_chime` | -10 dB | L40 | 20% | Logotip #1 (klassik) |
| 0:27.15 | L5 | `sfx.hit_tone` | -10 dB | R40 | 20% | Logotip #2 (neon) |
| 0:27.30 | L5 | `sfx.hit_low` | -10 dB | C | 20% | Logotip #3 (reel) |
| 0:27.45 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (G tonikada) |
| 0:27.45 | L1 | `mus.choir_g` | -6 dB | C | 60% | Xor logotip ostida |
| 0:27.90 | L5 | `sfx.thump` | -12 dB | L45 | 20% | 'A' harfi tushadi |
| 0:28.00 | L5 | `sfx.thump` | -12 dB | L15 | 20% | 'D' harfi tushadi |
| 0:28.10 | L5 | `sfx.thump` | -12 dB | R15 | 20% | 'U' harfi tushadi |
| 0:28.15 | L4 | `sfx.whoosh_soft` | -16 dB | C | 30% | Orbita |
| 0:28.20 | L5 | `sfx.thump` | -12 dB | R45 | 20% | 'Z' harfi tushadi |
| 0:28.25 | L4 | `sfx.swoosh_text` | -13 dB | C | 20% | Tagchiziq |
| 0:28.45 | L3 | `sfx.type_burst` | -13 dB | C | 15% | 'BIZNESINGIZ HIMOYACHISI' |
| 0:29.05 | L3 | `sfx.pop_short` | -10 dB | R20 | 30% | CTA |
| 0:29.07 | L3 | `ui.select` | -23 dB | R20 | 50% | CTA qo'ng'iroqchasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
