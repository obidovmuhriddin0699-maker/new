# ADUZ 11-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 11 --cuesheet SOUND_ARCHITECTURE_11.md`).

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

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:09.5 | Muammo · A-minor, tashvishli minimal | 7-qism aranjirovkasi 5 yarim ton yuqorida: qorong'i pad, offbeat Rhodes, filtrlangan bas, 5.5 s dan kick. Chat xabarlari tonallikdagi qo'ng'iroqchalar; 2.9 s da pul o'tkazmasi. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Gate: admin 'blokladi' — og'ir eshik yopilishi, uchta yetib bormagan xabar ('!'), yurak urishi. Keyin J-cut swell G-major'da. |
| 0:11–0:21.75 | Yechim · G-major, siyrak | Half-time kick + snap, Rhodes, sub, qo'ng'iroqcha. Ustida seyf hikoyasi: disk-qulf aylanadi → tanga kiradi → og'ir qulflanish → muz kristallanadi → vaqt tezlashadi → bot tasdig'i → muz eriydi → tanga adminga. |
| 0:22–0:27 | Natija · G-major, to'liq | To'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. |
| 0:27–0:32 | Yakun · brend | ADUZ sonic logo (G tonikada), so'nish. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -21 dB | C | 0% | Xona — sahna 'havosi' |
| 0:00.05 | L4 | `tr.whoosh` | -16 dB | R30 | 20% | Telefon kadrga kiradi |
| 0:00.90 | L3 | `ui.select` | -20 dB | L30 | 20% | Admin: xabar |
| 0:01.60 | L3 | `ui.select` | -20 dB | R30 | 20% | Siz: xabar |
| 0:02.20 | L3 | `ui.select` | -20 dB | L30 | 20% | Admin: xabar |
| 0:02.90 | L3 | `fx.transfer` | -10 dB | R30 | 20% | 500 000 so'm o'tkazildi |
| 0:03.60 | L3 | `ui.select` | -20 dB | L30 | 20% | Admin: xabar |
| 0:04.30 | L4 | `tr.slide` | -20 dB | C | 20% | 'Ertasi kuni' |
| 0:04.70 | L3 | `ui.select` | -20 dB | R30 | 20% | Siz: xabar |
| 0:05.50 | L3 | `ui.select` | -20 dB | R30 | 20% | Siz: xabar |
| 0:05.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: OLDINDAN TO'LOV |
| 0:06.30 | L3 | `ui.select` | -20 dB | R30 | 20% | Siz: xabar |
| 0:06.60 | L5 | `imp.glitch` | -8 dB | R40 | 25% | Slam: POST YO'Q |
| 0:07.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: JAVOB YO'Q |
| 0:08.00 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: asosiy zarba oldidan |
| 0:08.50 | L5 | `imp.boom` | -3 dB | C | 40% | 500 000 → 0 — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -8 dB | C | 50% | Zarba qatlami |
| 0:08.50 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:08.60 | L4 | `tr.riser` | -10 dB | C | 0% | Riser — 9.5 s da keskin kesiladi |
| 0:09.55 | L5 | `fx.blocked` | -6 dB | C | 0% | OVOZ VAKUUMI: admin blokladi |
| 0:09.70 | L3 | `fx.fail` | -13 dB | R40 | 0% | Xabar yetmadi #1 |
| 0:09.78 | L3 | `fx.fail` | -13 dB | R40 | 0% | Xabar yetmadi #2 |
| 0:09.86 | L3 | `fx.fail` | -13 dB | R40 | 0% | Xabar yetmadi #3 |
| 0:09.95 | L5 | `fx.heartbeat` | -8 dB | C | 0% | Yurak urishi |
| 0:10.15 | L4 | `tr.swell` | -8 dB | C | 30% | J-cut: yechim akkordi (G-major) |
| 0:10.55 | L4 | `tr.whoosh` | -10 dB | C | 30% | Oltin doira o'tishi |
| 0:11.00 | L5 | `imp.boom` | -6 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `tr.whoosh` | -15 dB | L30 | 20% | Telefon kiradi |
| 0:11.60 | L3 | `ui.popup` | -17 dB | C | 20% | Buyurtma kartasi |
| 0:12.60 | L3 | `ui.tap` | -9 dB | R20 | 0% | Kafolat bilan to'lash |
| 0:12.80 | L4 | `tr.slide` | -17 dB | R50 | 10% | Kafolat hisobi ekrani |
| 0:12.80 | L3 | `fx.knob` | -15 dB | C | 20% | Seyf disk-qulfi aylanadi |
| 0:13.00 | L3 | `fx.transfer` | -12 dB | L40 | 20% | Tanga seyfga uchadi |
| 0:13.60 | L5 | `fx.vault_lock` | -6 dB | C | 35% | SEYF QULFLANDI |
| 0:13.70 | L3 | `fx.freeze` | -10 dB | C | 40% | MUZLATILDI |
| 0:13.80 | L3 | `ui.select` | -16 dB | L20 | 30% | 1. Pul muzlatildi |
| 0:14.30 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.39 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.48 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.56 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.63 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.70 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.77 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.83 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.88 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.92 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.96 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:14.99 | L3 | `fx.tick` | -22 dB | R30 | 0% | Vaqt tez o'tadi (18:52 → 19:00) |
| 0:15.00 | L3 | `ui.next` | -14 dB | C | 30% | 2. Post chiqdi — bot tekshirdi |
| 0:15.80 | L3 | `ui.select` | -16 dB | C | 30% | 3. 24 soat turdi |
| 0:16.00 | L3 | `fx.melt` | -10 dB | C | 30% | Muz eriydi |
| 0:16.20 | L3 | `fx.transfer` | -12 dB | R40 | 20% | Tanga adminga o'tadi |
| 0:16.70 | L3 | `ui.select` | -15 dB | R40 | 30% | 4. Pul adminga o'tdi |
| 0:16.95 | L3 | `ui.popup` | -17 dB | C | 20% | Post chiqmasa — pul qaytadi |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: PUL HIMOYADA oldidan |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | PUL HIMOYADA — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Oltin uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | Pulingiz himoyada oynasi |
| 0:21.20 | L4 | `tr.riser` | -12 dB | C | 0% | J-cut: whip oldidan |
| 0:21.75 | L4 | `tr.whip` | -8 dB | C | 25% | Whip-pan o'tishi |
| 0:22.00 | L5 | `imp.boom` | -5 dB | C | 45% | Natija boshlanishi |
| 0:22.00 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:22.80 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #1 chizildi |
| 0:23.00 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #1 |
| 0:23.15 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #2 chizildi |
| 0:23.35 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #2 |
| 0:23.50 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #3 chizildi |
| 0:23.70 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #3 |
| 0:23.85 | L3 | `fx.strike` | -16 dB | L40 | 15% | 'Oldin' qatori #4 chizildi |
| 0:24.05 | L3 | `ui.select` | -16 dB | R40 | 30% | ADUZ qatori #4 |
| 0:24.50 | L4 | `tr.swell` | -10 dB | C | 30% | J-cut: nishonlar oldidan |
| 0:25.00 | L5 | `imp.boom` | -8 dB | C | 40% | Urg'u |
| 0:25.00 | L5 | `imp.sparkle` | -7 dB | C | 50% | Uchqunlar |
| 0:25.20 | L3 | `ui.select` | -17 dB | L40 | 30% | Nishon #1 |
| 0:25.45 | L3 | `ui.select` | -17 dB | C | 30% | Nishon #2 |
| 0:25.70 | L3 | `ui.select` | -17 dB | R40 | 30% | Nishon #3 |
| 0:26.85 | L4 | `tr.whoosh` | -16 dB | C | 40% | Yakuniy kadrga |
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO (G tonikada) |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
