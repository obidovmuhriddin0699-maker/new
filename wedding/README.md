# Kamron & Farangiz — sage & ivory envelope invitation

A cinematic, mobile-first wedding invitation website in a soft sage-and-ivory style: a lace envelope sealed with gold wax, calligraphy, floral corners and gentle gold details. Pure HTML, CSS and vanilla
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

A 27-second vertical video (1080×1920, 30 fps, H.264/AAC) of the real site, timed to the music like the reference.
It shows the envelope, the tap on the wax seal, the envelope opening into the hero, and the main cards
through to the final scene, with the invitation music. It's ready for
Telegram, Instagram Stories and WhatsApp.

```bash
npm run video                                   # node tools/render-video.cjs (Playwright + ffmpeg)
VIDEO_NOW=2026-11-06T10:00 npm run video        # moment the countdown is shown from
```

A video is frozen in time, so the countdown in it is rendered as seen at `VIDEO_NOW`
(default `2026-09-06T10:00`, i.e. 30 days before the configured date). **Re-render after
the date is confirmed**, and pick a `VIDEO_NOW` shortly before you send it.

## Motion-design video: `dist/taklifnoma-motion.mp4`

A 48-second cinematic motion-graphics invitation (1080×1920, 30 fps, with the invitation
music, looped). It uses the earlier Art Deco "Crystal Ballroom" design. It's a composed piece in its own right, built in `motion/` and not a recording
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
│   ├── opening.css       lace-envelope gate, wax seal, ornate arch hero, floral corners
│   ├── sections.css      invitation, story, details, countdown, gallery, location, finale
│   ├── components.css    top bar, menu, music toggle, lightbox, RSVP form
│   └── motion.css        intro reveal, scroll reveals, reduced-motion rules
├── js/                   classic scripts (work from file:// too), loaded with defer
│   ├── core.js           config → view model, time-zone maths, <picture> builder
│   ├── render.js         fills the page from config (scenes, story films, marquee)
│   ├── video.js          films: load near the screen, play while visible, poster fallback
│   ├── dust.js           sparkle engine: falling gold flakes (light pages), glints, fountains
│   ├── opening.js        the wax-seal envelope gate
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
│   ├── audio/            taklifnoma-musiqa.m4a
│   ├── fonts/  icons/  textures/
├── docs/RSVP.md          connecting the form to Google Sheets / Formspree
├── tests/e2e.cjs         Playwright end-to-end suite
├── motion/               the motion-design composition (index.html, motion.css, motion.js)
└── tools/                static server, preview-image, single-file, video and motion renderers
```

## 4. Music

`assets/audio/taklifnoma-musiqa.m4a` is the track taken from the reference video supplied
for this design (27 s; it loops on the site). Its title and rights holder aren't known, so
check you may use it before publishing. The music:

- **never starts automatically.** It begins only when the guest taps the wax seal, and it
  isn't downloaded before then (`preload="none"`);
- fades in gently, loops, pauses while the tab is hidden and resumes on return;
- is controlled by the persistent "Musiqa" button;
- **is honest when unavailable.** A missing file or a browser without AAC shows
  "Musiqa yo‘q" instead of pretending to play.

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

The look follows the reference video supplied for this version (a sage-and-ivory envelope
invitation). All artwork is original: the template's own illustrations are not used.

- **Palette:** sage `#A9B49E` / `#56644F`, ivory `#FBF8F2`, cream `#F3EEE4`, warm gold `#B8955A`,
  with `#7F6232` for small gold text and `#5E5C4E` for body text.
- **Type:** Great Vibes calligraphy for names and titles, Instrument Serif for dates and
  italics, Manrope for text and controls.
- **Gate:** a lace envelope on sage with white-rose corners (`tools/generate_florals.py`).
  Tapping the gold wax seal (K&F) lifts the seal, opens the flap in 3D and slides the card
  out; the view then zooms into the card.
- **Hero:** an ornate gold arch that draws itself, with the ballroom film softly fading
  inside it. The names are "written" left to right like a pen stroke, and gold flakes
  drift down.
- **Cards:** a "Sizni kutamiz" message card; a calendar card with the month grid, the
  wedding day marked by a small gold wax seal, the time, the countdown in boxes (digits
  roll in) and "Kalendarga qo‘shish"; a venue card with an arched photo and
  "Xaritada ko‘rish" / "Yo‘l ko‘rsatish" (Google Maps directions) buttons.
- **Kept and restyled:** story films in gold-rimmed arches, the gallery and lightbox,
  RSVP, the menu and the music button.
- **Accessibility:** reduced motion turns off the envelope animation, writing, flakes and
  film drift; every control is labelled; colour contrast is checked by the tests.

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
