# Kamron & Farangiz — Crystal Ballroom wedding invitation

A cinematic, mobile-first wedding invitation website in a modern Art Deco "crystal ballroom" style (noir, champagne gold, crystal sparkle) with living film backgrounds. Pure HTML, CSS and vanilla
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

> **Media:** every film and photo comes from the four videos and three images supplied for
> this invitation. The films are cut into six short scenes (`assets/video/`), and the
> gallery uses the three images plus stills from the films. The alt texts describe each
> scene without naming anyone. The street-embrace video is the same clip that was supplied
> for the previous version.

## Single-file version: `dist/index.html`

`dist/index.html` is the **finished invitation in one file** (about 10.5 MB, films included). All styles,
scripts, fonts, photos, films and the music are embedded, so it opens by double-click,
can be sent on Telegram, and can be uploaded to any host on its own. Settings are in the
`config.js` block inside the file. After editing the multi-file sources, rebuild it with:

```bash
npm run build        # python3 tools/build_single.py
```

The multi-file folder loads faster on phones (responsive image sizes, lazy loading,
music downloaded only on click), so prefer it for hosting when possible.

## Video version: `dist/taklifnoma-video.mp4`

A 73-second vertical video (1080×1920, 30 fps, H.264/AAC, about 17 MB) of the real site.
It shows the Art Deco doors, the tap on "Taklifnomani ochish", the doors opening with sparklers, and every section
through to the final scene, with "Asadov — Silencio" starting at the tap. It's ready for
Telegram, Instagram Stories and WhatsApp.

```bash
npm run video                                   # node tools/render-video.cjs (Playwright + ffmpeg)
VIDEO_NOW=2026-11-06T10:00 npm run video        # moment the countdown is shown from
```

A video is frozen in time, so the countdown in it is rendered as seen at `VIDEO_NOW`
(default `2026-09-06T10:00`, i.e. 30 days before the configured date). **Re-render after
the date is confirmed**, and pick a `VIDEO_NOW` shortly before you send it.

## Motion-design video: `dist/taklifnoma-motion.mp4`

A 48-second cinematic motion-graphics invitation (1080×1920, 30 fps, with "Asadov —
Silencio"). It's a composed piece in its own right, built in `motion/` and not a recording
of the website:

| Time | Scene |
|---|---|
| 0–5 s | The Art Deco emblem draws itself in gold; crystal glints; "To‘yga taklifnoma" |
| 5–12 s | Deco doors swing open with a flash and sparklers; names letter by letter over the ballroom film |
| 12–18 s | Glass invitation card over the chandelier photo; words appear one by one |
| 18–30 s | Four story films open like an iris inside gold arches, with chapter titles |
| 30–36 s | The date in large gold numerals with a turning sunburst |
| 36–41 s | A gold map pin draws itself; the city name appears |
| 41–48 s | Sparkler finale: emblem, names, message, date; fade to black |

Names, date and city are read from `config.js`.

```bash
npm run motion            # renders dist/taklifnoma-motion.mp4 (Playwright + ffmpeg)
npm run motion:preview    # a few stills in dist/.motion-preview/ for quick checks
```

Opening `motion/index.html` through the local server (`npm start` → `/motion/`) plays the
composition live in the browser, without music.

## 3. Structure

```
wedding/
├── index.html            semantic page skeleton (sections A–I)
├── config.js             ← all content and settings
├── css/
│   ├── fonts.css         self-hosted Instrument Serif + Manrope (OFL), latin + latin-ext
│   ├── base.css          tokens, reset, typography, buttons
│   ├── opening.css       video scenes, Art Deco door gate, emblem, sunburst, hero
│   ├── sections.css      invitation, story, details, countdown, gallery, location, finale
│   ├── components.css    top bar, menu, music toggle, lightbox, RSVP form
│   └── motion.css        intro reveal, scroll reveals, reduced-motion rules
├── js/                   classic scripts (work from file:// too), loaded with defer
│   ├── core.js           config → view model, time-zone maths, <picture> builder
│   ├── render.js         fills the page from config (scenes, story films, marquee)
│   ├── video.js          films: load near the screen, play while visible, poster fallback
│   ├── dust.js           sparkle engine: gold dust, crystal glints, sparkler fountains
│   ├── opening.js        the "Taklifnomani ochish" door gate
│   ├── audio.js          music (user-initiated only), toggle, missing-file handling
│   ├── motion.js         IntersectionObserver reveals, parallax, top bar
│   ├── nav.js            section menu
│   ├── countdown.js      live countdown + .ics calendar file
│   ├── gallery.js        lightbox (keyboard, swipe, focus management)
│   ├── rsvp.js           validation + submission
│   └── main.js           boot (each feature isolated)
├── assets/
│   ├── images/           WebP photos, two widths each
│   ├── video/            six silent film loops (MP4 + WebM) and their posters
│   ├── audio/            Asadov Silencio.m4a
│   ├── fonts/  icons/  textures/
├── docs/RSVP.md          connecting the form to Google Sheets / Formspree
├── tests/e2e.cjs         Playwright end-to-end suite
├── motion/               the motion-design composition (index.html, motion.css, motion.js)
└── tools/                static server, preview-image, single-file, video and motion renderers
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

- **Style:** modern Art Deco "crystal ballroom". Deep noir film scenes alternate with calm
  ivory sections; champagne gold is the accent, with crystal-white sparkle.
- **Logo:** an Art Deco arch emblem (stepped shoulders, sunburst fan, diamond apex) with the
  couple's monogram. It draws itself line by line on the gate and returns in the finale; the
  favicon, home-screen icon and link preview use it too.
- **Gate:** two Art Deco doors with a gold arch pattern swing open in 3D. Light pours through
  the gap and sparkler fountains burst up from the bottom corners.
- **Hero:** names in gold foil revealed letter by letter, with a bright glint sweeping across
  them every few seconds and a slowly turning deco sunburst behind.
- **Sparkle engine (`js/dust.js`):** rising gold dust, crystal star glints that flare like
  light on a chandelier, and sparkler fountains (a burst at the opening, continuous in the
  finale). Each particle is a pure function of time.
- **Ornaments:** stepped deco corners on cards, fan-and-diamond dividers, gold-rimmed arches
  around films and photos, a gold marquee band, glass cards over films, warm light leaks.
- **Countdown:** each digit rolls in when it changes.
- **Films as backgrounds (`config.scenes`):** full-bleed on phones; on wide screens the
  portrait film sits in a tall gold arch over a blurred copy of itself. Photos can be scenes
  too, with a slow cinematic drift.
- **Accessibility:** `prefers-reduced-motion`, Save-Data and iOS Low Power Mode switch the
  films to posters and turn off the doors, sparkles, glints and rays.

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
`npm run build` rebuilds `dist/index.html`; `npm run video` re-renders the video.
