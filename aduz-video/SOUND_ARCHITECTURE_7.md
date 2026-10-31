# ADUZ 7-qism — ovoz arxitekturasi va cue-sheet

Bu hujjat `audio.py` dan avtomatik yaratiladi (`python3 audio.py 7 --cuesheet SOUND_ARCHITECTURE_7.md`).

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

## Musiqa (score)

| Vaqt | Bo'lim | Aranjirovka |
|---|---|---|
| 0:00–0:09.5 | Muammo · E-minor, tashvishli minimal | Qorong'i pad; offbeat bo'g'iq elektro-pianino; 2 s dan filtrlangan bas pulsi; 3 s dan yumshoq 16-lik hat; 5.5 s dan kick. 9.5 s da hammasi keskin to'xtaydi. |
| 0:09.5–0:10.15 | Ovoz vakuumi | Montaj kesimi: musiqa, reverb va dumlar −30 dB ga keskin o'chiriladi (gate). Faqat xona shovqini, ilova yopilishi va yurak urishi qoladi. Keyin J-cut swell yechim tonalligida. |
| 0:11–0:21.75 | Yechim · D-major, ataylab siyrak | Faqat 4 qatlam: half-time kick + snap, marimba-uslub qo'ng'iroqcha, iliq Rhodes (D–Bm–G–A), sub. 'Sodda' xabarini aranjirovka ham aytadi. |
| 0:22–0:27 | Natija · D-major, to'liq | D–A–Bm–G: to'liq baraban, supersaw, Rhodes + qo'ng'iroqcha melodiyasi. |
| 0:27–0:32 | Yakun · brend | Baraban o'chadi; ADUZ sonic logo (A–D–F#) logotip bilan bir kadrda; D akkord bilan so'nadi. |

## Cue-sheet

| Taymkod | Qatlam | Tovush | Daraja | Pan | Reverb | Izoh |
|---|---|---|---|---|---|---|
| 0:00.00 | L2 | `amb.office` | -20 dB | C | 0% | Ofis xonasi — sahna 'havosi' |
| 0:00.05 | L4 | `tr.whoosh` | -16 dB | R30 | 20% | Telefon kadrga kiradi |
| 0:00.80 | L3 | `fx.fragment` | -23 dB | R60 | 15% | Jargon bo'lagi #1 |
| 0:01.20 | L3 | `ui.popup` | -15 dB | R10 | 20% | Popup: 'Bid strategiyasi' |
| 0:01.35 | L3 | `fx.fragment` | -23 dB | L60 | 15% | Jargon bo'lagi #2 |
| 0:01.90 | L3 | `fx.fragment` | -23 dB | R60 | 15% | Jargon bo'lagi #3 |
| 0:02.20 | L3 | `ui.dropdown` | -14 dB | R20 | 10% | Ochiluvchi ro'yxat |
| 0:02.45 | L3 | `fx.fragment` | -23 dB | L60 | 15% | Jargon bo'lagi #4 |
| 0:03.00 | L3 | `fx.fragment` | -23 dB | R60 | 15% | Jargon bo'lagi #5 |
| 0:03.20 | L3 | `ui.popup` | -15 dB | L10 | 20% | Popup: piksel kodi |
| 0:03.55 | L3 | `fx.fragment` | -23 dB | L60 | 15% | Jargon bo'lagi #6 |
| 0:04.10 | L3 | `fx.fragment` | -23 dB | R60 | 15% | Jargon bo'lagi #7 |
| 0:04.20 | L3 | `ui.error` | -13 dB | C | 20% | To'lov usuli tasdiqlanmagan |
| 0:04.65 | L3 | `fx.fragment` | -23 dB | L60 | 15% | Jargon bo'lagi #8 |
| 0:05.00 | L3 | `ui.popup` | -15 dB | R20 | 20% | Qo'llanma.pdf — 128 sahifa |
| 0:05.20 | L3 | `fx.fragment` | -23 dB | R60 | 15% | Jargon bo'lagi #9 |
| 0:05.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: CPM? CTR? |
| 0:05.75 | L3 | `fx.fragment` | -23 dB | L60 | 15% | Jargon bo'lagi #10 |
| 0:06.30 | L3 | `fx.fragment` | -23 dB | R60 | 15% | Jargon bo'lagi #11 |
| 0:06.60 | L5 | `imp.glitch` | -8 dB | R40 | 25% | Slam: QAYERDAN BOSHLASH? |
| 0:06.85 | L3 | `fx.fragment` | -23 dB | L60 | 15% | Jargon bo'lagi #12 |
| 0:07.60 | L5 | `imp.glitch` | -8 dB | L40 | 25% | Slam: QO'LLANMA: 128 SAHIFA |
| 0:08.50 | L5 | `imp.boom` | -3 dB | C | 40% | CHALKASH — asosiy zarba |
| 0:08.50 | L5 | `imp.clap` | -8 dB | C | 50% | Zarba qatlami |
| 0:08.50 | L5 | `imp.crash` | -10 dB | C | 0% | Zarba qatlami |
| 0:08.60 | L4 | `tr.riser` | -10 dB | C | 0% | Riser — 9.5 s da keskin kesiladi |
| 0:09.60 | L5 | `fx.collapse` | -6 dB | C | 35% | Ilova nuqtaga 'so'riladi' |
| 0:09.75 | L5 | `fx.heartbeat` | -7 dB | C | 20% | OVOZ VAKUUMI: faqat yurak |
| 0:10.15 | L4 | `tr.swell` | -8 dB | C | 30% | J-cut: yechim akkordi kesimdan oldin |
| 0:10.55 | L4 | `tr.squeegee` | -7 dB | C | 25% | Squeegee o'tishi |
| 0:11.00 | L5 | `imp.boom` | -6 dB | C | 35% | Yechim boshlanishi |
| 0:11.00 | L2 | `amb.air` | -32 dB | C | 0% | Yorug' muhit (deyarli sezilmas) |
| 0:11.10 | L4 | `tr.whoosh` | -15 dB | L30 | 20% | Telefon kiradi |
| 0:11.60 | L3 | `ui.select` | -18 dB | L30 | 25% | Katta tugma #1 |
| 0:11.75 | L3 | `ui.select` | -18 dB | C | 25% | Katta tugma #2 |
| 0:11.90 | L3 | `ui.select` | -18 dB | R30 | 25% | Katta tugma #3 |
| 0:13.00 | L3 | `ui.select` | -12 dB | R20 | 20% | Tanlandi: Reklama berish |
| 0:13.20 | L4 | `tr.slide` | -17 dB | R50 | 10% | 1-qadam ekrani |
| 0:13.40 | L3 | `ui.popup` | -20 dB | L30 | 20% | Variant #1 |
| 0:13.52 | L3 | `ui.popup` | -20 dB | C | 20% | Variant #2 |
| 0:13.64 | L3 | `ui.popup` | -20 dB | R30 | 20% | Variant #3 |
| 0:13.70 | L3 | `ui.select` | -20 dB | R30 | 30% | Maslahat pufagi |
| 0:14.00 | L3 | `ui.select` | -12 dB | L20 | 20% | Tanlandi: Do'kon |
| 0:14.30 | L4 | `tr.slide` | -17 dB | R50 | 10% | 2-qadam ekrani |
| 0:14.70 | L3 | `ui.slider` | -22 dB | L40 | 10% | Slider qadami 1/10 |
| 0:14.78 | L3 | `ui.slider` | -22 dB | L32 | 10% | Slider qadami 2/10 |
| 0:14.86 | L3 | `ui.slider` | -22 dB | L24 | 10% | Slider qadami 3/10 |
| 0:14.94 | L3 | `ui.slider` | -22 dB | L16 | 10% | Slider qadami 4/10 |
| 0:15.02 | L3 | `ui.slider` | -22 dB | L8 | 10% | Slider qadami 5/10 |
| 0:15.10 | L3 | `ui.slider` | -22 dB | C | 10% | Slider qadami 6/10 |
| 0:15.18 | L3 | `ui.slider` | -22 dB | R8 | 10% | Slider qadami 7/10 |
| 0:15.26 | L3 | `ui.slider` | -22 dB | R16 | 10% | Slider qadami 8/10 |
| 0:15.34 | L3 | `ui.slider` | -22 dB | R24 | 10% | Slider qadami 9/10 |
| 0:15.42 | L3 | `ui.slider` | -22 dB | R32 | 10% | Slider qadami 10/10 |
| 0:15.75 | L3 | `ui.next` | -13 dB | R20 | 25% | Keyingi |
| 0:16.00 | L4 | `tr.slide` | -17 dB | R50 | 10% | 3-qadam ekrani |
| 0:16.80 | L3 | `ui.tap` | -9 dB | R10 | 0% | Ishga tushirish bosildi |
| 0:16.85 | L3 | `ui.launch` | -12 dB | C | 30% | Ishga tushmoqda... |
| 0:18.00 | L4 | `tr.swell` | -9 dB | C | 30% | J-cut: 3 QADAM oldidan |
| 0:18.20 | L3 | `ui.success` | -10 dB | C | 40% | Ishga tushdi! |
| 0:18.50 | L5 | `imp.boom` | -4 dB | C | 40% | 3 QADAM — zarba |
| 0:18.50 | L5 | `imp.crash` | -12 dB | C | 0% | Zarba qatlami |
| 0:18.50 | L5 | `imp.sparkle` | -8 dB | C | 50% | Oltin uchqunlar |
| 0:19.90 | L3 | `ui.success` | -11 dB | C | 50% | Kampaniya ishga tushdi oynasi |
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
| 0:27.00 | L6 | `brand.logo` | -5 dB | C | 50% | ADUZ SONIC LOGO — logotip bilan bir kadrda |
| 0:28.30 | L3 | `ui.select` | -22 dB | R20 | 50% | CTA tugmasi |

## Master zanjir

Sidechain (kick) → diktor uchun 2,2–4,2 kHz chuqurcha → 300 Hz dan yuqori stereo kengaytirish (bas mono) → hi-hat 'shivillashi' yumshatilgan → ping-pong delay (nuqtali 8-lik) → reverb (2,8 s) → bus-kompressor 2:1 → iliqlik/havo EQ → soft-clip → ffmpeg `loudnorm` −14 LUFS + `alimiter` −1,5 dBFS.
