# ADUZ 27-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 27 --cuesheet SOUND_ARCHITECTURE_27.md`).

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
| `mus.choir_e` | L1 | Xor 'aaah' E-major (heavenly uslub, original sintez) |
| `mus.choir_e_hi` | L1 | Baland xor 'ooo' E-major |
| `fx.chain_snap_v` | L5 | Zanjir uziladi (vakuum ichida eshitiladigan nusxa) |
| `mus.choir_eb` | L1 | Xor 'aaah' Eb-major (heavenly uslub, original sintez) |
| `mus.choir_eb_hi` | L1 | Baland xor 'ooo' Eb-major |
| `fx.coin_v` | L3 | Tanga (vakuum ichida eshitiladigan nusxa) |

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| Format | Instagram Reels uchun | Hook kadr 0 da (fade-in yo'q), har 1–2 s da yangi voqea, matn xavfsiz zonada, katta subtitrlar (ovozsiz ko'rish), izoh-CTA va loop: oxirgi 0.6 s boshidagi kadrni qayta quradi, ovozda riser kadr 0 dagi zarbaga ulanadi. Audio — boshida/oxirida so'nish yo'q (20 ms anti-klik). |
| 0:00–0:01.6 | HOOK | Kadr 0 dan sub-boom + bass_drop ('62% KUYYAPTI'), kuyayotgan pul shitirlashi; 1.45 s keskin kesim (glitch + swipe). |
| 0:01.6–0:09.5 | Muammo · D-minor + pizzicato | 7-qism aranjirovkasi 1 yarim ton yuqorida + pizzicato. 18 ta tanga oltita kanalga: jonli kanalda — tick_hi, o'lik kanalda — fx.zap (yonib ketadi). Slab-kartalar — stutter + glitch; 8.5 s KUL. — boom + fizz. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: oxirgi tanga tushadi (fx.coin_v), yonadi (fizz), kulga aylanadi (dust); yurak urishi. |
| 0:10.15–0:11 | Vahiy · barsWipe | HEAVENLY XOR Eb-major'da; ekvalayzer ustunlari — 12 pog'onali pentatonik pop kaskadi, 'Optimallash.' — shimmer. |
| 0:11–0:21.75 | Yechim · Eb-major, siyrak | Toggle — klik + blip; skaner — fx.scan, har kanal: STOP — fx.nope, FOYDALI — ui.select; qayta taqsimlash — qo'sh klik + fx.transfer; tejaldi — ratchet + tangalar. 18.5 s: HAR SO'M / ISHLAYDI. — ikki zarba + xor; keyframe'lar — tick_hi. |
| 0:22–0:27 | Natija · Eb-major, to'liq | '×3' chiziqli fonda, kassa, nishonlar. |
| 0:27–0:32 | Yakun + loop | Sonic logo (Eb) + xor, harflar, izoh-CTA 'BYUDJET'; 30.8 s riser + 31.4 s whoosh — loop orqali kadr 0 zarbasiga ulanadi. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L5 | `sfx.boom_sub` | -0 dB | C | 30% | HOOK: '62%' — kadr 0 dan zarba |
| 0:00.00 | L5 | `sfx.bass_drop` | -3 dB | C | 30% | '62%' og'ir grotesk |
| 0:00.05 | L3 | `fx.fizz` | -17 dB | R30 | 20% | Kuyayotgan pul shitirlashi |
| 0:00.12 | L5 | `sfx.bass_drop` | -6 dB | C | 30% | 'KUYYAPTI' |
| 0:00.30 | L4 | `sfx.swoosh_text` | -14 dB | C | 20% | Serif izoh |
| 0:01.45 | L5 | `sfx.glitch_short` | -8 dB | C | 15% | Keskin kesim → muammo |
| 0:01.50 | L4 | `sfx.swipe` | -10 dB | C | 15% | Kesim qatlami |
| 0:01.60 | L2 | `amb.office` | -24 dB | C | 0% | Xona — sahna 'havosi' |
| 0:01.60 | L3 | `sfx.type_burst` | -12 dB | C | 15% | '27-QISM' dekodlanadi |
| 0:01.75 | L5 | `sfx.bass_drop` | -8 dB | C | 30% | 'BYUDJET' |
| 0:01.75 | L3 | `sfx.pop_short` | -17 dB | L50 | 20% | Kanal kartasi #1 |
| 0:01.81 | L3 | `sfx.pop_short` | -17 dB | L30 | 20% | Kanal kartasi #2 |
| 0:01.87 | L3 | `sfx.pop_short` | -17 dB | L10 | 20% | Kanal kartasi #3 |
| 0:01.93 | L3 | `sfx.pop_short` | -17 dB | R10 | 20% | Kanal kartasi #4 |
| 0:01.99 | L3 | `sfx.pop_short` | -17 dB | R30 | 20% | Kanal kartasi #5 |
| 0:02.00 | L3 | `fx.coin` | -23 dB | L40 | 15% | Tanga → kanal #1 |
| 0:02.05 | L3 | `sfx.pop_short` | -17 dB | R50 | 20% | Kanal kartasi #6 |
| 0:02.38 | L3 | `fx.coin` | -23 dB | L24 | 15% | Tanga → kanal #2 |
| 0:02.45 | L3 | `fx.zap` | -20 dB | L40 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:02.76 | L3 | `fx.coin` | -23 dB | L8 | 15% | Tanga → kanal #3 |
| 0:02.83 | L3 | `sfx.tick_hi` | -18 dB | L24 | 20% | Jonli kanal: foydali |
| 0:03.14 | L3 | `fx.coin` | -23 dB | R8 | 15% | Tanga → kanal #4 |
| 0:03.21 | L3 | `fx.zap` | -20 dB | L8 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:03.52 | L3 | `fx.coin` | -23 dB | R24 | 15% | Tanga → kanal #5 |
| 0:03.59 | L3 | `fx.zap` | -20 dB | R8 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:03.90 | L3 | `fx.coin` | -23 dB | R40 | 15% | Tanga → kanal #6 |
| 0:03.97 | L3 | `sfx.tick_hi` | -18 dB | R24 | 20% | Jonli kanal: foydali |
| 0:04.28 | L3 | `fx.coin` | -23 dB | L40 | 15% | Tanga → kanal #1 |
| 0:04.35 | L3 | `fx.zap` | -20 dB | R40 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:04.66 | L3 | `fx.coin` | -23 dB | L24 | 15% | Tanga → kanal #2 |
| 0:04.73 | L3 | `fx.zap` | -20 dB | L40 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:05.04 | L3 | `fx.coin` | -23 dB | L8 | 15% | Tanga → kanal #3 |
| 0:05.11 | L3 | `sfx.tick_hi` | -18 dB | L24 | 20% | Jonli kanal: foydali |
| 0:05.42 | L3 | `fx.coin` | -23 dB | R8 | 15% | Tanga → kanal #4 |
| 0:05.49 | L3 | `fx.zap` | -20 dB | L8 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:05.60 | L5 | `sfx.stutter` | -8 dB | L40 | 20% | Slab-karta: O'LIK KANAL |
| 0:05.60 | L5 | `sfx.glitch_short` | -6 dB | L40 | 20% | Slam qatlami |
| 0:05.80 | L3 | `fx.coin` | -23 dB | R24 | 15% | Tanga → kanal #5 |
| 0:05.87 | L3 | `fx.zap` | -20 dB | R8 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:06.18 | L3 | `fx.coin` | -23 dB | R40 | 15% | Tanga → kanal #6 |
| 0:06.25 | L3 | `sfx.tick_hi` | -18 dB | R24 | 20% | Jonli kanal: foydali |
| 0:06.56 | L3 | `fx.coin` | -23 dB | L40 | 15% | Tanga → kanal #1 |
| 0:06.60 | L5 | `sfx.stutter` | -8 dB | R40 | 20% | Slab-karta: BOTLAR KO'RADI |
| 0:06.60 | L5 | `sfx.glitch_short` | -6 dB | R40 | 20% | Slam qatlami |
| 0:06.63 | L3 | `fx.zap` | -20 dB | R40 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:06.94 | L3 | `fx.coin` | -23 dB | L24 | 15% | Tanga → kanal #2 |
| 0:07.01 | L3 | `fx.zap` | -20 dB | L40 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:07.32 | L3 | `fx.coin` | -23 dB | L8 | 15% | Tanga → kanal #3 |
| 0:07.39 | L3 | `sfx.tick_hi` | -18 dB | L24 | 20% | Jonli kanal: foydali |
| 0:07.60 | L5 | `sfx.stutter` | -8 dB | L40 | 20% | Slab-karta: PUL KUYDI |
| 0:07.60 | L5 | `sfx.glitch_short` | -6 dB | L40 | 20% | Slam qatlami |
| 0:07.70 | L3 | `fx.coin` | -23 dB | R8 | 15% | Tanga → kanal #4 |
| 0:07.77 | L3 | `fx.zap` | -20 dB | L8 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.08 | L3 | `fx.coin` | -23 dB | R24 | 15% | Tanga → kanal #5 |
| 0:08.15 | L3 | `fx.zap` | -20 dB | R8 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:08.38 | L4 | `sfx.riser_click` | -10 dB | C | 0% | Riser — cho'qqisi 9.5 s da |
| 0:08.45 | L4 | `sfx.whoosh_low` | -9 dB | C | 20% | To'q sariq kadr |
| 0:08.46 | L3 | `fx.coin` | -23 dB | R40 | 15% | Tanga → kanal #6 |
| 0:08.50 | L5 | `sfx.boom_sub` | -1 dB | C | 35% | KUL. — asosiy zarba |
| 0:08.50 | L5 | `sfx.bass_drop` | -4 dB | C | 30% | Zarba qatlami |
| 0:08.50 | L5 | `sfx.glitch_seq` | -12 dB | C | 20% | Zarba qatlami: glitch |
| 0:08.53 | L3 | `sfx.tick_hi` | -18 dB | R24 | 20% | Jonli kanal: foydali |
| 0:08.55 | L3 | `fx.fizz` | -14 dB | C | 20% | Kul uchqunlari |
| 0:08.91 | L3 | `fx.zap` | -20 dB | R40 | 15% | O'lik kanal: tanga yonib ketdi |
| 0:09.60 | L3 | `fx.coin_v` | -10 dB | C | 20% | OVOZ VAKUUMI: oxirgi tanga tushadi |
| 0:09.85 | L3 | `fx.fizz` | -10 dB | C | 10% | ...yonib ketadi |
| 0:09.95 | L5 | `fx.heartbeat` | -12 dB | C | 0% | Yurak urishi |
| 0:10.00 | L5 | `sfx.dust` | -10 dB | R20 | 0% | ...kulga aylanadi |
| 0:10.15 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: yechim akkordi (Eb-major) |
| 0:10.20 | L1 | `mus.choir_eb` | +2 dB | C | 60% | HEAVENLY XOR — 'Optimallash.' |
| 0:10.30 | L3 | `sfx.pop_short` | -18 dB | L50 | 15% | Ekvalayzer ustuni #1 |
| 0:10.33 | L3 | `sfx.pop_short` | -18 dB | L41 | 15% | Ekvalayzer ustuni #2 |
| 0:10.36 | L3 | `sfx.pop_short` | -18 dB | L32 | 15% | Ekvalayzer ustuni #3 |
| 0:10.39 | L3 | `sfx.pop_short` | -18 dB | L23 | 15% | Ekvalayzer ustuni #4 |
| 0:10.42 | L3 | `sfx.pop_short` | -18 dB | L14 | 15% | Ekvalayzer ustuni #5 |
| 0:10.45 | L3 | `sfx.pop_short` | -18 dB | L5 | 15% | Ekvalayzer ustuni #6 |
| 0:10.48 | L3 | `sfx.pop_short` | -18 dB | C | 15% | Ekvalayzer ustuni #7 |
| 0:10.51 | L3 | `sfx.pop_short` | -18 dB | R13 | 15% | Ekvalayzer ustuni #8 |
| 0:10.54 | L3 | `sfx.pop_short` | -18 dB | R22 | 15% | Ekvalayzer ustuni #9 |
| 0:10.55 | L3 | `sfx.shimmer` | -10 dB | C | 40% | 'Optimallash.' |
| 0:10.57 | L3 | `sfx.pop_short` | -18 dB | R31 | 15% | Ekvalayzer ustuni #10 |
| 0:10.60 | L3 | `sfx.pop_short` | -18 dB | R40 | 15% | Ekvalayzer ustuni #11 |
| 0:10.63 | L3 | `sfx.pop_short` | -18 dB | R49 | 15% | Ekvalayzer ustuni #12 |
| 0:10.70 | L4 | `sfx.whoosh_sweep` | -12 dB | C | 25% | Ustunlar tushadi |
| 0:11.00 | L5 | `sfx.boom_sub` | -7 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit |
| 0:11.25 | L4 | `sfx.swoosh_text` | -16 dB | L40 | 15% | UI-karta #1 |
| 0:11.37 | L4 | `sfx.swoosh_text` | -16 dB | L13 | 15% | UI-karta #2 |
| 0:11.49 | L4 | `sfx.swoosh_text` | -16 dB | R14 | 15% | UI-karta #3 |
| 0:11.61 | L4 | `sfx.swoosh_text` | -16 dB | R41 | 15% | UI-karta #4 |
| 0:12.20 | L3 | `sfx.click_1` | -3 dB | R30 | 0% | Jonli optimizatsiya — YONDI |
| 0:12.22 | L3 | `sfx.blip_up` | -10 dB | R30 | 25% | Toggle laym |
| 0:12.55 | L3 | `fx.scan` | -13 dB | C | 20% | Skaner kanallar bo'ylab |
| 0:12.62 | L3 | `fx.nope` | -16 dB | L30 | 15% | Kanal #1: STOP |
| 0:12.76 | L3 | `ui.select` | -18 dB | R30 | 30% | Kanal #2: FOYDALI |
| 0:12.90 | L3 | `fx.nope` | -16 dB | L30 | 15% | Kanal #3: STOP |
| 0:13.05 | L3 | `fx.nope` | -16 dB | L30 | 15% | Kanal #4: STOP |
| 0:13.19 | L3 | `ui.select` | -18 dB | R30 | 30% | Kanal #5: FOYDALI |
| 0:13.33 | L3 | `fx.nope` | -16 dB | L30 | 15% | Kanal #6: STOP |
| 0:13.70 | L3 | `sfx.click_double_2` | -3 dB | R20 | 0% | 'Qayta taqsimlash' |
| 0:13.72 | L3 | `fx.transfer` | -10 dB | C | 20% | Pul jonli kanallarga oqadi |
| 0:13.75 | L4 | `sfx.whoosh_sweep` | -14 dB | C | 20% | Budjet chiziqlari ko'chadi |
| 0:14.60 | L3 | `sfx.ratchet_roll` | -14 dB | L30 | 15% | Tejaldi: 1 860 000 |
| 0:14.65 | L3 | `fx.coin` | -24 dB | L40 | 20% | Tanga #1 |
| 0:14.73 | L3 | `fx.coin` | -24 dB | L30 | 20% | Tanga #2 |
| 0:14.81 | L3 | `fx.coin` | -24 dB | L20 | 20% | Tanga #3 |
| 0:14.89 | L3 | `fx.coin` | -24 dB | L10 | 20% | Tanga #4 |
| 0:14.97 | L3 | `fx.coin` | -24 dB | C | 20% | Tanga #5 |
| 0:15.05 | L3 | `fx.coin` | -24 dB | R10 | 20% | Tanga #6 |
| 0:15.13 | L3 | `fx.coin` | -24 dB | R20 | 20% | Tanga #7 |
| 0:15.21 | L3 | `fx.coin` | -24 dB | R30 | 20% | Tanga #8 |
| 0:15.40 | L4 | `sfx.whoosh_sweep` | -16 dB | R30 | 20% | Donut 100% |
| 0:16.00 | L1 | `mus.choir_eb_hi` | -7 dB | C | 60% | Xor 'ooo' — har so'm ishlaydi |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: HAR SO'M ISHLAYDI oldidan |
| 0:18.45 | L4 | `sfx.whoosh_low` | -10 dB | C | 30% | Laym kadr |
| 0:18.50 | L5 | `sfx.boom_sub` | -2 dB | C | 35% | HAR SO'M — zarba |
| 0:18.50 | L5 | `sfx.bass_drop` | -6 dB | C | 30% | Og'ir grotesk |
| 0:18.50 | L1 | `mus.choir_eb` | -2 dB | C | 60% | Xor zarba ostida |
| 0:18.50 | L5 | `imp.sparkle` | -10 dB | C | 50% | Uchqunlar |
| 0:18.60 | L5 | `sfx.thump` | -7 dB | C | 25% | ISHLAYDI. — ikkinchi zarba |
| 0:18.80 | L4 | `sfx.swoosh_text` | -10 dB | C | 20% | Serif izoh |
| 0:19.70 | L4 | `sfx.swipe` | -10 dB | C | 20% | Binafsha karta |
| 0:20.00 | L3 | `sfx.shimmer` | -13 dB | C | 30% | 'Byudjet — aqlli taqsimotda.' |
| 0:20.20 | L3 | `sfx.tick_hi` | -15 dB | L45 | 25% | Keyframe #1 |
| 0:20.50 | L3 | `sfx.tick_hi` | -15 dB | L36 | 25% | Keyframe #2 |
| 0:20.57 | L3 | `sfx.tick_hi` | -15 dB | L27 | 25% | Keyframe #3 |
| 0:20.63 | L4 | `sfx.riser_click` | -10 dB | C | 0% | Riser — whip'ga |
| 0:20.69 | L3 | `sfx.tick_hi` | -15 dB | L18 | 25% | Keyframe #4 |
| 0:20.73 | L3 | `sfx.tick_hi` | -15 dB | L9 | 25% | Keyframe #5 |
| 0:20.80 | L3 | `sfx.tick_hi` | -15 dB | C | 25% | Keyframe #6 |
| 0:20.83 | L3 | `sfx.tick_hi` | -15 dB | R9 | 25% | Keyframe #7 |
| 0:20.85 | L3 | `sfx.tick_hi` | -15 dB | R18 | 25% | Keyframe #8 |
| 0:20.94 | L3 | `sfx.tick_hi` | -15 dB | R27 | 25% | Keyframe #9 |
| 0:20.99 | L3 | `sfx.tick_hi` | -15 dB | R36 | 25% | Keyframe #10 |
| 0:21.05 | L3 | `sfx.tick_hi` | -15 dB | R45 | 25% | Keyframe #11 |
| 0:21.35 | L3 | `ui.success` | -12 dB | C | 50% | BYUDJET ISHLAYAPTI |
| 0:21.75 | L4 | `sfx.whoosh_sweep` | -8 dB | C | 25% | Whip-pan |
| 0:21.75 | L4 | `sfx.swipe` | -10 dB | C | 20% | Whip qatlami |
| 0:22.00 | L5 | `sfx.boom_sub` | -6 dB | C | 40% | Natija boshlanishi |
| 0:22.10 | L5 | `sfx.bass_drop` | -7 dB | C | 30% | '×3' chiziqli fonda |
| 0:22.10 | L4 | `sfx.whoosh_low` | -14 dB | C | 20% | Chiziqlar oqadi |
| 0:22.95 | L3 | `sfx.type_burst` | -12 dB | C | 15% | 'NATIJA' |
| 0:23.00 | L5 | `sfx.bass_drop` | -10 dB | C | 30% | 'O'SHA PUL — ×3' |
| 0:23.20 | L5 | `fx.kassa` | -10 dB | C | 30% | KASSA |
| 0:23.22 | L3 | `sfx.notify_ring` | -13 dB | R20 | 25% | Kassa qatlami |
| 0:23.50 | L4 | `sfx.swipe` | -9 dB | L40 | 15% | 'Oldin' qatori #1 chizildi |
| 0:23.70 | L3 | `sfx.click_1` | -8 dB | R40 | 0% | ADUZ qatori #1 |
| 0:23.72 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:23.85 | L4 | `sfx.swipe` | -9 dB | L40 | 15% | 'Oldin' qatori #2 chizildi |
| 0:24.05 | L3 | `sfx.click_2` | -8 dB | R40 | 0% | ADUZ qatori #2 |
| 0:24.07 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:24.20 | L4 | `sfx.swipe` | -9 dB | L40 | 15% | 'Oldin' qatori #3 chizildi |
| 0:24.40 | L3 | `sfx.click_3` | -8 dB | R40 | 0% | ADUZ qatori #3 |
| 0:24.42 | L3 | `ui.select` | -18 dB | R40 | 30% | Tonallikdagi tasdiq |
| 0:24.50 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: nishonlar oldidan |
| 0:25.00 | L5 | `sfx.boom_sub` | -7 dB | C | 40% | Urg'u |
| 0:25.00 | L5 | `imp.sparkle` | -9 dB | C | 50% | Uchqunlar |
| 0:25.20 | L3 | `sfx.pop_short` | -10 dB | L40 | 30% | Rangli nishon #1 |
| 0:25.22 | L3 | `ui.select` | -20 dB | L40 | 30% | Qo'ng'iroqcha |
| 0:25.45 | L3 | `sfx.pop_short` | -10 dB | C | 30% | Rangli nishon #2 |
| 0:25.47 | L3 | `ui.select` | -20 dB | C | 30% | Qo'ng'iroqcha |
| 0:25.70 | L3 | `sfx.pop_short` | -10 dB | R40 | 30% | Rangli nishon #3 |
| 0:25.72 | L3 | `ui.select` | -20 dB | R40 | 30% | Qo'ng'iroqcha |
| 0:26.85 | L4 | `sfx.whoosh_soft` | -14 dB | C | 40% | Yakuniy kadrga |
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (Eb tonikada) |
| 0:27.00 | L1 | `mus.choir_eb` | -6 dB | C | 60% | Xor logotip ostida |
| 0:27.45 | L5 | `sfx.thump` | -11 dB | L45 | 20% | 'A' harfi tushadi |
| 0:27.55 | L5 | `sfx.thump` | -11 dB | L15 | 20% | 'D' harfi tushadi |
| 0:27.65 | L5 | `sfx.thump` | -11 dB | R15 | 20% | 'U' harfi tushadi |
| 0:27.70 | L4 | `sfx.whoosh_soft` | -16 dB | C | 30% | Orbita |
| 0:27.75 | L5 | `sfx.thump` | -11 dB | R45 | 20% | 'Z' harfi tushadi |
| 0:27.80 | L4 | `sfx.swoosh_text` | -13 dB | C | 20% | Tagchiziq |
| 0:28.00 | L3 | `sfx.type_burst` | -13 dB | C | 15% | 'BIZNESINGIZ HIMOYACHISI' |
| 0:28.50 | L5 | `sfx.bass_drop` | -10 dB | C | 30% | IZOHGA 'BYUDJET' — CTA |
| 0:28.52 | L3 | `ui.select` | -22 dB | C | 50% | CTA qo'ng'iroqchasi |
| 0:28.90 | L4 | `sfx.swoosh_text` | -14 dB | C | 20% | 'saqlab qo'ying' |
| 0:30.80 | L4 | `sfx.riser_click` | -10 dB | C | 0% | LOOP: riser — cho'qqisi kadr 0 zarbasiga ulanadi |
| 0:31.40 | L4 | `sfx.whoosh_low` | -10 dB | C | 20% | LOOP: to'q sariq kadr qayta ochiladi |
| 0:31.40 | L5 | `sfx.glitch_short` | -12 dB | C | 15% | LOOP: glitch |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
