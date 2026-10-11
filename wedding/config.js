/* ==========================================================================
   Asilbek & Maftun — central configuration
   --------------------------------------------------------------------------
   Every name, date, text, image, audio file, colour and link on the site
   comes from this file. Edit the values below; no other file needs to change.

   Paths are relative to index.html. Keep the quotes and commas intact.
   ========================================================================== */
window.WEDDING_CONFIG = {
  coupleNames: "Asilbek & Maftun",
  groom: "Asilbek",
  bride: "Maftun",

  // ⚠️ 6-oktabr 2026 sanasi o‘tib ketgan. Taklifnomani tarqatishdan oldin sanani
  //    tasdiqlang yoki yangilang. Countdown shu qiymatlardan hisoblanadi.
  eventDate: "2026-10-06", // YYYY-MM-DD
  eventTime: "16:00",      // HH:MM, 24-hour, venue local time
  timeZone: "Asia/Tashkent",
  // How long the celebration lasts; used for the calendar file and "to‘y bugun" state.
  eventDurationHours: 6,

  // To‘yxona nomini kiriting (masalan "… to‘yxonasi"). Bo‘sh bo‘lsa, shahar nomi ko‘rsatiladi.
  venueName: "",
  venueCity: "Qo‘qon shahri",
  // Leave empty until the exact address is confirmed — nothing is shown when empty.
  venueAddress: "",
  // Paste the exact Google Maps / Yandex Maps link here. When empty, the button
  // opens a map search for venueName + venueCity (not a verified pin).
  mapUrl: "",
  locationImage: "lace-arm", // photo next to the venue details ("" to hide)

  opening: {
    eyebrow: "To‘yga taklifnoma",
    subtitle: "Hayotimizning eng go‘zal kunida sizni yonimizda ko‘rishdan mamnun bo‘lamiz.",
    button: "Taklifnomani ochish",
  },

  invitationText: {
    eyebrow: "Taklifnoma",
    greeting: "Qadrli mehmonimiz!",
    lead: "Ikki qalbni bir umrga bog‘laydigan kunimizni siz bilan birga nishonlashni istaymiz.",
    body: [
      "Sizni nikoh to‘yimizga lutfan taklif etamiz. Hayotimizning bu yangi sahifasini eng yaqin insonlarimiz davrasida boshlash biz uchun katta baxt.",
      "Tashrifingiz va samimiy duolaringiz biz uchun eng qimmatli sovg‘a bo‘ladi.",
    ],
    signature: "Hurmat bilan, Asilbek va Maftun",
  },

  // Short silent films used as living backgrounds. Files: assets/video/{id}.mp4 (+ .webm)
  // and {id}.webp (poster shown while loading, on data-saver / low-power mode and with
  // reduced motion). Cut from the three videos supplied for this invitation.
  videos: {
    "window-kiss":    { alt: "Deraza yonida bir-birini quchgan juftlik" },
    "window-smile":   { alt: "Deraza oldida jilmayib turgan kelin va kuyov" },
    "window-embrace": { alt: "Deraza yonida quchoqlashgan kelin va kuyov" },
    "hands":          { alt: "Kelinning qo‘li kuyovning qo‘lida" },
    "street-spin":    { alt: "Shahar ko‘chasida kelinni ko‘tarib aylantirayotgan kuyov" },
    "street-embrace": { alt: "Shahar ko‘chasida quchoqlashgan kelin va kuyov" },
  },
  // What lives behind each section: a film id (from `videos`) or a photo id (from
  // `images`, gently animated). "" = plain noir.
  scenes: {
    opening: "window-kiss",
    invitation: "love-letter",
    countdown: "street-embrace",
    finale: "roses-moon",
  },

  // "Bizning hikoyamiz". `label` is free text (a year, a season, a chapter).
  // `video` (from `videos`) plays in the chapter's gold arch; `image` is the fallback.
  // The texts below are gentle placeholders — replace them with your own story.
  storyContent: [
    { label: "I bob", title: "Ilk uchrashuv", text: "Bir qarash, bir tabassum — va ikkimiz ham hali nomini bilmagan iliq tuyg‘u.", video: "hands" },
    { label: "II bob", title: "Bir-birimizni kashf etib", text: "Uzun suhbatlar, umumiy orzular va har kuni sekin-asta qurilgan ishonch.", video: "street-spin" },
    { label: "III bob", title: "Va’da", text: "Ota-onalarimizning duosi bilan uzuk taqildi. Javob esa faqat bitta edi.", video: "window-smile" },
    { label: "IV bob", title: "Bir umrga", text: "Endi bu baxtni barcha yaqinlarimiz bilan baham ko‘rishga tayyormiz.", video: "window-embrace" },
  ],

  // Photo gallery (ids from `images`). Order = display order.
  galleryImages: ["roses-moon", "window-kiss-still", "hands-ring", "street-lift", "love-letter", "window-hug"],

  finalScene: {
    message: "Sevgimizning eng go‘zal lahzasida yonimizda bo‘lishingizni chin dildan kutib qolamiz.",
  },

  // Every photo on the site. Files live in assets/images/{id}-{width}.webp.
  // `widths` lists the sizes on disk; `ratio` is width/height (prevents layout shift).
  // The two photographs and the film stills supplied for this invitation.
  images: {
    "roses-moon":        { widths: [480, 720], ratio: "736/1308", alt: "Oy ostidagi oq atirgullar orasida qizil atirgul va kapalak" },
    "love-letter":       { widths: [480, 720], ratio: "736/1308", alt: "Qizil atirgullar orasidagi muhabbat maktubi" },
    "hands-ring":        { widths: [480, 720], ratio: "720/1174", alt: "Uzuk taqilgan qo‘llar bir-birini ushlab turibdi" },
    "lace-arm":          { widths: [480, 720], ratio: "720/1174", alt: "To‘rli yengli kelin kuyovning qo‘lidan tutgan" },
    "street-lift":       { widths: [480, 720], ratio: "9/16",     alt: "Shahar ko‘chasida kelinni ko‘targan kuyov" },
    "street-hug":        { widths: [480, 720], ratio: "9/16",     alt: "Ko‘chada guldasta bilan quchoqlashgan juftlik" },
    "window-kiss-still": { widths: [480, 720], ratio: "9/16",     alt: "Deraza yonida bir-biriga qaragan kelin va kuyov" },
    "window-hug":        { widths: [480, 720], ratio: "9/16",     alt: "Deraza yonida quchoqlashgan kelin va kuyov" },
  },

  // Played only after the guest presses "Taklifnomani ochish".
  backgroundMusic: "assets/audio/Asadov Silencio.m4a",
  musicTitle: "Asadov — Silencio",
  musicVolume: 0.4,

  rsvp: {
    // HTTPS endpoint that accepts a POST (Google Apps Script, Formspree, your API…).
    // While empty, the form validates but tells guests that replies are not being
    // collected yet — it never pretends a reply was saved. See docs/RSVP.md.
    rsvpEndpoint: "",
    // "json" → Content-Type: application/json (Formspree, most APIs)
    // "text" → Content-Type: text/plain with a JSON body (Google Apps Script; avoids CORS preflight)
    format: "json",
    deadline: "",   // YYYY-MM-DD, last day replies are accepted (venue time). Empty = until the event starts.
    maxGuests: 6,   // including the guest themself
    contactNote: "", // e.g. "Savollar uchun: +998 90 000 00 00" — shown under the form
  },

  // Colour tokens (any CSS colour). Applied as CSS custom properties.
  colors: {
    ivory: "#FBF7F1",
    cream: "#F4ECE0",
    champagne: "#EADCC6",
    beige: "#DCCBB3",
    taupe: "#665748",
    ink: "#2F2822",
    gold: "#A88A5C",      // decorative lines and large accents
    goldDeep: "#7E6440",  // small gold text (meets contrast on ivory)
  },
};
