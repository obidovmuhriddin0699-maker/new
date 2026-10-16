/* ==========================================================================
   Kamron & Farangiz — central configuration
   --------------------------------------------------------------------------
   Every name, date, text, image, audio file, colour and link on the site
   comes from this file. Edit the values below; no other file needs to change.

   Paths are relative to index.html. Keep the quotes and commas intact.
   ========================================================================== */
window.WEDDING_CONFIG = {
  coupleNames: "Kamron & Farangiz",
  groom: "Kamron",
  bride: "Farangiz",

  // ⚠️ 6-oktabr 2026 sanasi o‘tib ketgan. Taklifnomani tarqatishdan oldin sanani
  //    tasdiqlang yoki yangilang. Countdown shu qiymatlardan hisoblanadi.
  eventDate: "2026-10-06", // YYYY-MM-DD
  eventTime: "16:00",      // HH:MM, 24-hour, venue local time
  timeZone: "Asia/Tashkent",
  // How long the celebration lasts; used for the calendar file and "to‘y bugun" state.
  eventDurationHours: 6,

  // To‘yxona nomini kiriting (masalan "… to‘yxonasi"). Bo‘sh bo‘lsa, shahar nomi ko‘rsatiladi.
  venueName: "",
  venueCity: "Andijon shahri",
  // Leave empty until the exact address is confirmed — nothing is shown when empty.
  venueAddress: "",
  // Paste the exact Google Maps / Yandex Maps link here. When empty, the button
  // opens a map search for venueName + venueCity (not a verified pin).
  mapUrl: "",
  locationImage: "bouquet-bench", // photo next to the venue details ("" to hide)

  opening: {
    eyebrow: "Taklifnoma",
    subtitle: "Ikki qalb bir taqdirni tanladi — endi u bizning umumiy yo‘limiz.",
    button: "Taklifnomani ochish",
  },

  invitationText: {
    eyebrow: "Aziz mehmonimiz",
    greeting: "Sizni kutamiz",
    lead: "",
    body: [
      "Hayotimizdagi eng go‘zal kunni — nikoh to‘yimizni siz bilan birga nishonlashni istaymiz.",
      "Mehrimizga guvoh, quvonchimizga sherik bo‘ling.",
    ],
    signature: "Hurmat bilan, Kamron va Farangiz",
  },

  // Short silent films used as living backgrounds. Files: assets/video/{id}.mp4 (+ .webm)
  // and {id}.webp (poster shown while loading, on data-saver / low-power mode and with
  // reduced motion). Cut from the four videos supplied for this invitation.
  videos: {
    "ballroom-couple": { alt: "Billur qandil ostidagi bal zalida kelin va kuyov" },
    "dress-spin":      { alt: "Yuqoridan: kelinning libosi aylanib raqsga tushmoqda" },
    "hands-lace":      { alt: "To‘rli yengli kelin va kuyov qo‘l ushlashib turibdi" },
    "watch-hands":     { alt: "Kuyovning qo‘li kelinning qo‘lini ushlab turibdi" },
    "ring-hand":       { alt: "Nikoh uzugi taqilgan qo‘llar" },
    "street-embrace":  { alt: "Shahar ko‘chasida quchoqlashgan kelin va kuyov" },
  },
  // What lives behind each section: a film id (from `videos`) or a photo id (from
  // `images`, gently animated). "" = plain noir.
  scenes: {
    opening: "ballroom-couple", // plays softly inside the arch on the first screen
  },

  // "Bizning hikoyamiz". `label` is free text (a year, a season, a chapter).
  // `video` (from `videos`) plays in the chapter's gold arch; `image` is the fallback.
  // The texts below are gentle placeholders — replace them with your own story.
  storyContent: [
    { label: "I bob", title: "Ilk uchrashuv", text: "Bir qarash, bir tabassum — va ikkimiz ham hali nomini bilmagan iliq tuyg‘u.", video: "hands-lace" },
    { label: "II bob", title: "Bir-birimizni kashf etib", text: "Uzun suhbatlar, umumiy orzular va har kuni sekin-asta qurilgan ishonch.", video: "watch-hands" },
    { label: "III bob", title: "Va’da", text: "Ota-onalarimizning duosi bilan uzuk taqildi. Javob esa faqat bitta edi.", video: "ring-hand" },
    { label: "IV bob", title: "Bir umrga", text: "Endi bu baxtni barcha yaqinlarimiz bilan baham ko‘rishga tayyormiz.", video: "dress-spin" },
  ],

  // Photo gallery (ids from `images`). Order = display order.
  galleryImages: ["chandelier-embrace", "first-dance-bw", "sparklers", "ballroom-still", "street-hug", "lace-hands"],

  finalScene: {
    message: "Bizning baxtli kunimizda sizni kutib qolamiz.",
  },

  // Every photo on the site. Files live in assets/images/{id}-{width}.webp.
  // `widths` lists the sizes on disk; `ratio` is width/height (prevents layout shift).
  // The three photographs and the film stills supplied for this invitation.
  images: {
    "chandelier-embrace": { widths: [480, 564], ratio: "564/878",  alt: "Billur qandillar yonida quchoqlashgan kelin va kuyov" },
    "sparklers":          { widths: [480, 720], ratio: "736/1303", alt: "Billur qandil ostida, uchqunli favvoralar orasida kelin va kuyov" },
    "first-dance-bw":     { widths: [480, 720], ratio: "736/998",  alt: "Yuqoridan: kelin va kuyovning ilk raqsi" },
    "bouquet-bench":      { widths: [480, 720], ratio: "9/16",     alt: "Yog‘och o‘rindiqdagi oq gullar guldastasi" },
    "street-hug":         { widths: [480, 720], ratio: "9/16",     alt: "Ko‘chada guldasta bilan quchoqlashgan juftlik" },
    "ballroom-still":     { widths: [480, 720], ratio: "9/16",     alt: "Bal zalida kelin va kuyov" },
    "lace-hands":         { widths: [480, 720], ratio: "9/16",     alt: "To‘rli yengli kelin kuyovning qo‘lidan tutgan" },
  },

  // Played only after the guest taps the wax seal. The track supplied with the
  // reference video for this design (27 s, loops seamlessly on the site).
  backgroundMusic: "assets/audio/taklifnoma-musiqa.m4a",
  musicTitle: "",
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
    ivory: "#FBF8F2",
    cream: "#F3EEE4",
    champagne: "#E9E2D2",
    beige: "#D9D2C0",
    taupe: "#5E5C4E",     // body text
    ink: "#3F3E34",
    gold: "#B8955A",      // lines and accents
    goldDeep: "#7F6232",  // small gold text (meets contrast on ivory)
  },
};
