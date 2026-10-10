# Love in the Clouds — Muxriddin & Umida

A cinematic, mobile-first wedding invitation website. Pure HTML, CSS and vanilla
JavaScript: no framework, no build step, no runtime dependencies.

> **⚠️ Before sharing:** the configured date, **6 October 2026, 16:00**, has already
> passed. As a result the countdown shows its "after the wedding" message and the RSVP
> form is closed. Confirm the real date and update `eventDate` / `eventTime` in
> [`config.js`](config.js), then run `npm run previews` so the link-preview image shows
> the new date. The date was **not** changed automatically.

---

## 1. Quick start

```bash
cd wedding
node tools/static-server.cjs 8080      # or: npm start
# open http://127.0.0.1:8080
```

Any static server works (`python3 -m http.server`, VS Code Live Server, …).
Double-clicking `index.html` also works. Chrome blocks web fonts on `file://`, so in that
case the page falls back to Georgia and the system sans-serif.

**Preview a different "now"** without touching the event date:
`http://127.0.0.1:8080/?now=2026-09-20T12:00` (venue time). A small badge marks this test
mode. Use it to see the live countdown, the "today" state (`?now=2026-10-06T17:00`) or an
open RSVP form.

## 2. Configuration: everything lives in `config.js`

| Key | What it controls |
|---|---|
| `coupleNames`, `groom`, `bride` | Names everywhere (title, monogram, details, finale) |
| `eventDate` (`YYYY-MM-DD`), `eventTime` (`HH:MM`) | Countdown, details, calendar file, RSVP closing |
| `timeZone` | IANA zone of the venue (`Asia/Tashkent`). The countdown is correct in any visitor time zone |
| `eventDurationHours` | Length of the celebration (calendar file, "today" message) |
| `venueName`, `venueCity`, `venueAddress` | Location section. An empty address is simply not shown |
| `mapUrl` | Exact Google / Yandex Maps link. **Empty →** the button opens a map *search* for venue + city, not a verified pin |
| `locationImage` | Photo next to the venue (`""` hides it) |
| `opening` | Eyebrow, subtitle, button label and arch photo of the opening scene |
| `invitationText` | Greeting, lead, body paragraphs, signature |
| `storyContent` | Timeline chapters `{ label, title, text, image }`. The texts are gentle placeholders; replace them with your story |
| `galleryImages` | Ordered list of image ids for the gallery |
| `finalScene` | Closing photo and message |
| `images` | Every photo: `id → { widths, ratio, alt }`. Files are `assets/images/{id}-{width}.webp` |
| `backgroundMusic`, `musicTitle`, `musicVolume` | Background music (see §4) |
| `rsvp` | `rsvpEndpoint`, `format`, `deadline`, `maxGuests`, `contactNote` (see §5) |
| `colors` | Palette tokens, applied as CSS custom properties |

**Static tags in `index.html`:** link previews (Telegram, WhatsApp) read the `<title>`,
`description` and `og:*` tags without running JavaScript, so those live in `index.html`.
Update them together with `config.js`. After deploying, change `og:image` to an absolute URL
(`https://your-domain/…/assets/icons/og-image.jpg`), which some apps require.

### Adding or replacing photos
1. Export a WebP at two widths, e.g. `assets/images/our-photo-480.webp` and `-960.webp`.
2. Add `"our-photo": { widths: [480, 960], ratio: "4/5", alt: "…" }` to `images`.
3. Use the id in `storyContent`, `galleryImages`, `opening.image`, `finalScene.image` or `locationImage`.

`ratio` is width/height and reserves space before the image loads (no layout shift). In the
gallery, images wider than 1.2:1 automatically span two columns.

> **About the current photos:** they are the photos supplied with the earlier version of
> this site (the `gh-pages` branch). Where they came from isn't recorded, so the alt
> texts describe each scene without claiming it shows the couple. If any of them isn't
> Muxriddin and Umida's own photograph, replace it before publishing.

## 3. Structure

```
wedding/
├── index.html            semantic page skeleton (sections A–I)
├── config.js             ← all content and settings
├── css/
│   ├── fonts.css         self-hosted Instrument Serif + Manrope (OFL), latin + latin-ext
│   ├── base.css          tokens, reset, typography, buttons
│   ├── opening.css       sky, cloud layers, opening scene, cloud-pass transition
│   ├── sections.css      invitation, story, details, countdown, gallery, location, finale
│   ├── components.css    top bar, menu, music toggle, lightbox, RSVP form
│   └── motion.css        intro reveal, scroll reveals, reduced-motion rules
├── js/                   classic scripts (work from file:// too), loaded with defer
│   ├── core.js           config → view model, time-zone maths, <picture> builder
│   ├── render.js         fills the page from config
│   ├── opening.js        the "Taklifnomani ochish" gate
│   ├── audio.js          music (user-initiated only), toggle, missing-file handling
│   ├── motion.js         IntersectionObserver reveals, parallax, top bar
│   ├── nav.js            section menu
│   ├── countdown.js      live countdown + .ics calendar file
│   ├── gallery.js        lightbox (keyboard, swipe, focus management)
│   ├── rsvp.js           validation + submission
│   └── main.js           boot (each feature isolated)
├── assets/
│   ├── images/           WebP photos, two widths each
│   ├── clouds/           generated, seamlessly tiling cloud layers (tools/generate_clouds.py)
│   ├── audio/            Asadov Silencio.m4a
│   ├── fonts/  icons/  textures/
├── docs/RSVP.md          connecting the form to Google Sheets / Formspree
├── tests/e2e.cjs         Playwright end-to-end suite
└── tools/                static server, cloud generator, preview-image renderer
```

## 4. Music

`assets/audio/Asadov Silencio.m4a` is the supplied track, unchanged. It is:

- **never started automatically.** It begins only inside the guest's click on
  "Taklifnomani ochish". It isn't even downloaded before then (`preload="none"`);
- faded in gently, looped, paused while the tab is hidden, and resumed on return;
- controlled by the persistent "Musiqa" button (bottom right, 48px touch target);
- **honest when unavailable.** If the file is missing, or the browser can't decode AAC,
  the button shows "Musiqa yo‘q" and nothing pretends to play. All current Chrome,
  Safari (macOS/iOS), Firefox, Edge and Android browsers decode AAC. Some Linux builds of
  Chromium don't.

## 5. RSVP

The form validates name, attendance and guest count, and offers an optional wish. It shows
accessible inline errors, a loading state, and success or failure feedback. Duplicate
submissions are blocked: one request at a time, and a stable `submissionId` per reply for
server-side de-duplication. A sent reply is remembered on the guest's device.

**Until `rsvp.rsvpEndpoint` is set, no reply is collected.** The form says so plainly
("Javobingiz yuborilmadi: onlayn javob qabul qilish hali sozlanmagan") and never shows a
success message. → See **[docs/RSVP.md](docs/RSVP.md)** for a free Google Sheets backend
(10 minutes) or Formspree.

Replies close at the end of `rsvp.deadline` (venue time) or, if no deadline is set, when
the event starts.

## 6. Deploying

Upload the `wedding/` folder as-is to any static host: Netlify (drag and drop), Vercel,
Cloudflare Pages or GitHub Pages. Nothing needs building. Serve over HTTPS.

The repository's current `gh-pages` branch still serves the earlier version of the
invitation. This version hasn't been published there; that's a deliberate step for you to
take once the date is confirmed.

## 7. Design system (summary)

- **Palette:** warm ivory `#FBF7F1`, cream `#F4ECE0`, champagne `#EADCC6`, beige `#DCCBB3`,
  taupe `#665748` (text), ink `#2F2822`, brushed gold `#A88A5C` (lines and large accents
  only) and `#7E6440` (small gold text, WCAG AA on ivory/cream).
- **Type:** Instrument Serif for names and headings (tracked capitals on the opening,
  italics for accents); Manrope for body text and controls; fluid `clamp()` scale; small
  uppercase eyebrows with optical centring.
- **Layout:** mobile-first single column, editorial two-column compositions from 820px,
  arches echoing the opening photograph, generous whitespace, 72rem content width.
- **Motion:** three drifting cloud layers with depth parallax, a slow camera push on
  arrival, a staged title reveal, a cloud pass when the invitation opens, and
  IntersectionObserver reveals with soft image zoom. Only `transform`, `opacity` and
  `clip-path` are animated. Everything is disabled under `prefers-reduced-motion`.

## 8. Testing

```bash
npm install          # once: installs Playwright
npm run test:setup   # once: downloads Chromium for Playwright
npm test             # 29 end-to-end checks
```

The suite covers no horizontal overflow or clipped elements, with every image loading,
at 360, 375, 390, 430, 768, 1024 and 1440px. It also checks the opening gate and focus
order; that music plays only after the click and downloads nothing early; missing or
unsupported audio; countdown maths in Tashkent time from any visitor time zone, plus the
"today" and "after" states; the calendar file; the lightbox (keys, wrap-around, focus
trap, focus return, swipe); the map link; the menu; RSVP validation, the no-endpoint
honesty, single submission on double submit, server errors and retry, and the closed
state; reduced motion; semantic structure; colour contrast; and `file://` loading.

Other tools: `npm run previews` re-renders the link-preview image and icon;
`npm run clouds` regenerates the cloud layers (needs Python with Pillow and NumPy).
