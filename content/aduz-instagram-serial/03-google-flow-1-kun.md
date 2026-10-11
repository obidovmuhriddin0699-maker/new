# Google Flow uchun: 1-KUN — "3 kun, 0 kanal"

**Umumiy davomiylik:** ~39 s = 4 ta Flow klipi (Veo, har biri 8 s gacha) + 2 ta montaj bloki (bot ekran yozuvi va CTA)
**Format:** 9:16 vertikal. Flow'da 9:16 bo‘lmasa, 16:9 da yaratib, markazni 9:16 ga kesing (kompozitsiya markazda bo‘lsin).
**Model:** Veo 3 (sinov uchun Fast rejimi, yakuniy variant uchun Quality). Har promptga 2–4 variant so‘rang va eng yaxshisini tanlang.

---

## 1-QADAM. "Ingredients" (reference rasmlar)

Bu rasmlarni Flow ichida (yoki istalgan rasm generatorida) yaratib, **Ingredients** sifatida saqlang. Keyin har klipda shularni tanlaysiz va qahramon hamma klipda bir xil chiqadi.

**Ingredient 1 — RUSTAM**
```
Photorealistic full-body portrait of an Uzbek man, 42 years old, medium height, slightly heavy build, short black hair with grey temples, thick black mustache, clean-shaven chin, warm brown eyes, friendly expressive face. Wearing a navy blue classic jacket over a white open-collar shirt without tie, silver wristwatch on left wrist, dark grey trousers, black leather shoes. Standing, neutral pose, plain light grey studio background, soft even lighting, 9:16.
```

**Ingredient 2 — DO‘KON (lokatsiya)**
```
Photorealistic interior of a small furniture showroom in Fergana, Uzbekistan. Grey and beige fabric sofas in rows, small paper price tags with no readable text, a wooden cashier desk with an old wooden abacus on it, glass storefront with daylight, warm ceiling lights, tiled floor, a plain red paper sign on the wall with no letters. No people. Vertical 9:16.
```

**Ingredient 3 — XARIDOR**
```
Photorealistic portrait of a young Uzbek man, 25 years old, short dark hair, casual dark green jacket, jeans, friendly ordinary face. Plain light grey background, 9:16.
```

---

## 2-QADAM. Klip promptlari (Ingredients to Video)

> **Dialog bo‘yicha muhim:** Veo ovozni ham yaratadi, lekin o‘zbek tilidagi talaffuz sifati kafolatlanmagan. Ikki yo‘l bor:
> - **A (tavsiya):** promptdagi o‘zbekcha replikani qoldiring. Lab harakati chiqadi. Talaffuz yomon bo‘lsa, montajda ovozni haqiqiy ovoz aktyori yozuviga almashtiring (replikalar qisqa, lab harakatiga taxminan mos tushadi).
> - **B:** dialog qatorini olib tashlab, `No speech, only ambient sound` yozing. Ovozni to‘liq montajda qo‘shasiz.

### KLIP 1 · 0–8 s · HOOK
Ingredients: Rustam + Do‘kon
```
Vertical 9:16, photorealistic, cinematic. Top-down medium shot: the man from the reference lies exhausted on a grey sofa in the furniture showroom from the reference, a smartphone resting on his face. He slowly lifts the phone off his face, stares at the ceiling with a tired, comically defeated expression, and says in Uzbek, in a tired voice: "Telegramda reklama berish oson deyishdi..." Then he lets out a long sigh. Warm late-afternoon interior light. Static camera.
Audio: quiet ticking clock, his long sigh.
Avoid: readable text, logos, subtitles, distorted hands, change of clothing.
```

### KLIP 2 · 8–16 s · FLASHBACK VA ADMINLAR
Ingredients: Rustam + Do‘kon
```
Vertical 9:16, photorealistic. Same man and same showroom, bright morning daylight, slightly warmer and more saturated colors. He stands energetically, rubs his hands together, picks up his smartphone and says confidently in Uzbek: "Bir soatda topaman! Telegram-ku bu!" Quick cut feel: he types fast on the phone at the wooden cashier desk, reads the screen, his face drops, and he lightly slaps his own forehead, saying in Uzbek: "Men lichkadaman-ku!" Phone screen is blurred and unreadable. Handheld camera, slow push-in.
Audio: upbeat light music, keyboard tapping, a soft message notification sound.
Avoid: readable text on screen, logos, extra people.
```

### KLIP 3 · 16–21 s · OVOZLI XABAR
Ingredients: Rustam + Do‘kon
```
Vertical 9:16, photorealistic. Side medium shot: the same man sits on the grey sofa holding the smartphone to his ear, listening to a very long voice message. His eyelids grow heavy, his head slowly tilts, and he falls asleep sitting up, the phone still at his ear. Comic timing. Warm interior light. Static camera.
Audio: a muffled monotone voice from the phone, then soft snoring. No other speech.
Avoid: readable text, distorted face, change of clothing.
```

### MONTAJ BLOKI · 21–28 s · YECHIM (Flow'da yaratilmaydi)
- Botning (@Targetreklammabot) haqiqiy ekran yozuvi: kanallar ro‘yxati, telefon ramkasi ichida.
- **Diktor:** "Kanal qidirish uch kun emas, bir necha daqiqa olishi mumkin. ADUZ'da Telegram kanallari bir joyda jamlangan."
- **Ekranda:** "Kanallar — bir joyda. ADUZ"

### KLIP 4 · 28–36 s · YAKUNIY BURILISH
Ingredients: Rustam + Do‘kon + Xaridor
```
Vertical 9:16, photorealistic. Wide shot from the showroom entrance. The young customer from the reference walks in through the glass door and asks politely in Uzbek: "Aka, divan bormi?" The man from the reference, sitting at the wooden cashier desk staring at his phone, waves him off without looking up and says in Uzbek: "Hozir emas, uka, mijoz qidiryapman!" The customer shrugs and walks out. The man freezes for a second, slowly realizes his mistake, and looks directly into the camera with comic regret. Natural daylight. Static camera, slight push-in at the end.
Audio: door bell chime, footsteps.
Avoid: readable text, logos, angry expressions, extra people.
```
> **Agar klip juda tiqilinch chiqsa,** uni ikkiga bo‘ling: 4a (xaridor kiradi, savol beradi, javob oladi) va 4b (xaridor chiqadi, Rustam kameraga qaraydi). 4b uchun Flow'dagi **Extend** funksiyasidan yoki 4a ning oxirgi kadrini **Frames to Video** boshlang‘ich kadri qilib foydalaning.

### MONTAJ BLOKI · 36–39 s · CTA
- Ekranda: **"Siz reklama uchun kanalni qanday topasiz? Izohda yozing 👇"**
- Pastda: *"Ertaga: 3 ta kanal topildi... endi narx so‘raymiz."*

---

## 3-QADAM. Montajda qo‘shiladiganlar
| Vaqt | Element |
|---|---|
| 0–3 s | Hook matni: **"3-KUN. HALI HAM KANAL QIDIRYAPMAN."** |
| 8 s | Flashback belgisi: **"1-KUN, 09:00"** + rewind ovozi |
| 10–16 s | Chat pufakchalari: "Narx lichkada.", "Admin hozir band." |
| 16–21 s | **"▶ 3:40"** va hisoblagich: **"Yozilgan adminlar: 12 · Javob: 2"** |
| Butun video | Subtitrlar, "Reklama degani shumi?! · 1-qism", ADUZ logotipi |
| Yakunda | CTA ekrani |

**Subtitrlar:**
```
00:00 «Telegramda reklama berish oson» deyishdi...
00:08 Bir soatda topaman! Telegram-ku bu!
00:12 «Narx lichkada.»
00:13 Men lichkadaman-ku!
00:21 Kanal qidirish uch kun emas,
00:24 bir necha daqiqa olishi mumkin.
00:26 ADUZ'da Telegram kanallari bir joyda jamlangan.
00:29 Aka, divan bormi?
00:31 Hozir emas, uka, mijoz qidiryapman!
```

## Flow bo‘yicha amaliy maslahatlar
1. Avval **Fast** rejimida sinab ko‘ring. Yaxshi chiqqan promptni **Quality** rejimida qayta yarating.
2. Qahramon har klipda bir xil chiqishi uchun **har doim bir xil Ingredient rasmlarini** tanlang.
3. Kliplarni Flow'ning **Scenebuilder** bo‘limida ketma-ket joylab, umumiy ritmni tekshiring. Yakuniy montajni (matn, ovoz, logotip) CapCut yoki Premiere'da qiling.
4. Telefon ekrani ko‘pincha bo‘sh yoki xira chiqadi. Bu yaxshi: ekrandagi chat va matnlarni montajda qo‘yasiz.
5. Instagramga joylaganda **"AI info"** belgisini yoqing.
