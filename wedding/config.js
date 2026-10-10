/* ==========================================================================
   LOVE IN THE CLOUDS — central configuration
   --------------------------------------------------------------------------
   Every name, date, text, image, audio file, colour and link on the site
   comes from this file. Edit the values below; no other file needs to change.

   Paths are relative to index.html. Keep the quotes and commas intact.
   ========================================================================== */
window.WEDDING_CONFIG = {
  coupleNames: "Muxriddin & Umida",
  groom: "Muxriddin",
  bride: "Umida",

  // ⚠️ 6-oktabr 2026 sanasi o‘tib ketgan. Taklifnomani tarqatishdan oldin sanani
  //    tasdiqlang yoki yangilang. Countdown shu qiymatlardan hisoblanadi.
  eventDate: "2026-10-06", // YYYY-MM-DD
  eventTime: "16:00",      // HH:MM, 24-hour, venue local time
  timeZone: "Asia/Tashkent",
  // How long the celebration lasts; used for the calendar file and "to‘y bugun" state.
  eventDurationHours: 6,

  venueName: "Versal to‘yxonasi",
  venueCity: "Farg‘ona shahri",
  // Leave empty until the exact address is confirmed — nothing is shown when empty.
  venueAddress: "",
  // Paste the exact Google Maps / Yandex Maps link here. When empty, the button
  // opens a map search for venueName + venueCity (not a verified pin).
  mapUrl: "",
  locationImage: "staircase", // photo next to the venue details ("" to hide)

  opening: {
    eyebrow: "To‘yga taklifnoma",
    subtitle: "Hayotimizning eng go‘zal kunida sizni yonimizda ko‘rishdan mamnun bo‘lamiz.",
    button: "Taklifnomani ochish",
    image: "window", // id from `images` below; set to "" for a sky-only opening
  },

  invitationText: {
    eyebrow: "Taklifnoma",
    greeting: "Qadrli mehmonimiz!",
    lead: "Ikki qalbni bir umrga bog‘laydigan kunimizni siz bilan birga nishonlashni istaymiz.",
    body: [
      "Sizni nikoh to‘yimizga lutfan taklif etamiz. Hayotimizning bu yangi sahifasini eng yaqin insonlarimiz davrasida boshlash biz uchun katta baxt.",
      "Tashrifingiz va samimiy duolaringiz biz uchun eng qimmatli sovg‘a bo‘ladi.",
    ],
    signature: "Hurmat bilan, Muxriddin va Umida",
  },

  // "Bizning hikoyamiz". `label` is free text (a year, a season, a chapter).
  // The texts below are gentle placeholders — replace them with your own story.
  storyContent: [
    { label: "I bob", title: "Ilk uchrashuv", text: "Bir qarash, bir tabassum — va ikkimiz ham hali nomini bilmagan iliq tuyg‘u.", image: "touch" },
    { label: "II bob", title: "Bir-birimizni kashf etib", text: "Uzun suhbatlar, umumiy orzular va har kuni sekin-asta qurilgan ishonch.", image: "evening-hands" },
    { label: "III bob", title: "Va’da", text: "Ota-onalarimizning duosi bilan uzuk taqildi. Javob esa faqat bitta edi.", image: "rings-blossom" },
    { label: "IV bob", title: "Bir umrga", text: "Endi bu baxtni barcha yaqinlarimiz bilan baham ko‘rishga tayyormiz.", image: "first-dance" },
  ],

  // Photo gallery (ids from `images`). Order = display order.
  galleryImages: ["pink-embrace", "roses", "ring-on", "staircase", "bouquet-hands", "moon", "rose-sunset"],

  finalScene: {
    image: "beach",
    message: "Sevgimizning eng go‘zal lahzasida yonimizda bo‘lishingizni chin dildan kutib qolamiz.",
  },

  // Every photo on the site. Files live in assets/images/{id}-{width}.webp.
  // `widths` lists the sizes on disk; `ratio` is width/height (prevents layout shift).
  // These are the photos supplied with the earlier version of the site. If any of
  // them is not your own photograph, replace it before publishing.
  images: {
    "window":        { widths: [480, 720], ratio: "4/5",     alt: "Baland ravoqli deraza oldida kelin va kuyov siluetlari" },
    "touch":         { widths: [480, 720], ratio: "4/5",     alt: "Bir-biriga intilgan ikki qo‘l" },
    "evening-hands": { widths: [480, 720], ratio: "3/4",     alt: "Kechki chiroqlar fonida nikoh uzugi taqilgan qo‘llar" },
    "rings-blossom": { widths: [480, 720], ratio: "4/5",     alt: "Pushti gullar orasida turgan nikoh uzugi" },
    "first-dance":   { widths: [480, 960], ratio: "3/4",     alt: "Kelin va kuyovning ilk raqsi" },
    "pink-embrace":  { widths: [480, 720], ratio: "3/4",     alt: "Pushti libos fonida bir-birini quchgan qo‘llar" },
    "roses":         { widths: [480, 720], ratio: "4/5",     alt: "Qizil atirgullar guldastasi yonida qo‘l ushlashib turgan juftlik" },
    "ring-on":       { widths: [480, 720], ratio: "720/427", alt: "Kuyov kelinning barmog‘iga uzuk taqmoqda" },
    "staircase":     { widths: [480, 720], ratio: "3/4",     alt: "Keng zinapoyada kelin va kuyov" },
    "bouquet-hands": { widths: [480, 720], ratio: "4/5",     alt: "Oq libos va pushti guldasta ustida qo‘llar" },
    "moon":          { widths: [480, 720], ratio: "9/16",    alt: "To‘lin oy fonida qo‘l ushlashgan juftlik siluetlari" },
    "rose-sunset":   { widths: [480, 736], ratio: "4/5",     alt: "Quyosh botishida ochilgan qizil atirgul" },
    "beach":         { widths: [480, 720], ratio: "9/16",    alt: "Quyosh botayotgan dengiz bo‘yida qo‘l ushlashgan juftlik siluetlari" },
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
