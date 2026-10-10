/* ==========================================================================
   core.js — shared helpers and the derived view of config.js.
   Classic script (no modules) so the site also works when opened from disk.
   ========================================================================== */
(function () {
  "use strict";

  var MONTHS = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul",
    "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];
  var WEEKDAYS = ["Yakshanba", "Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"];

  var reducedMotionQuery = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;

  function $(selector, root) { return (root || document).querySelector(selector); }
  function $$(selector, root) { return Array.prototype.slice.call((root || document).querySelectorAll(selector)); }
  function pad(n) { return String(n).padStart(2, "0"); }
  function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /** Offset in minutes of an IANA time zone at a UTC instant (Asia/Tashkent → 300). */
  function zoneOffset(timeZone, utcMs) {
    var parts = new Intl.DateTimeFormat("en-US", {
      timeZone: timeZone, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit"
    }).formatToParts(new Date(utcMs));
    var v = {};
    parts.forEach(function (p) { v[p.type] = Number(p.value); });
    var hour = v.hour === 24 ? 0 : v.hour;
    return (Date.UTC(v.year, v.month - 1, v.day, hour, v.minute, v.second) - utcMs) / 60000;
  }

  /** Wall-clock time in a time zone → absolute epoch milliseconds (DST-safe). */
  function zonedTime(y, m, d, hh, mm, timeZone) {
    var guess = Date.UTC(y, m - 1, d, hh, mm);
    try {
      var first = guess - zoneOffset(timeZone, guess) * 60000;
      // Second pass corrects the rare case where the offset differs at the result.
      return guess - zoneOffset(timeZone, first) * 60000;
    } catch (err) {
      console.warn("[taklifnoma] Unknown timeZone \"" + timeZone + "\" — using UTC+5 (Asia/Tashkent).", err);
      return guess - 300 * 60000;
    }
  }

  function parseDate(value) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value || "").trim());
    return m ? { y: +m[1], m: +m[2], d: +m[3] } : null;
  }
  function parseTime(value) {
    var m = /^(\d{1,2}):(\d{2})$/.exec(String(value || "").trim());
    return m ? { hh: +m[1], mm: +m[2] } : null;
  }

  /**
   * Testing aid: ?now=2026-09-20T12:00 pretends the current time is that moment
   * (venue time zone). It never changes the configured event date.
   */
  function readPreviewNow(timeZone) {
    var raw;
    try { raw = new URLSearchParams(window.location.search).get("now"); } catch (e) { raw = null; }
    if (!raw) return null;
    var m = /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{1,2}):(\d{2})(?::(\d{2}))?)?$/.exec(raw.trim());
    if (!m) {
      console.warn("[taklifnoma] Ignoring ?now=" + raw + " (use YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS).");
      return null;
    }
    var at = zonedTime(+m[1], +m[2], +m[3], m[4] ? +m[4] : 12, m[5] ? +m[5] : 0, timeZone) + (m[6] ? +m[6] * 1000 : 0);
    return { offset: at - Date.now(), label: raw.trim() };
  }

  function buildView(cfg) {
    var timeZone = cfg.timeZone || "Asia/Tashkent";
    var date = parseDate(cfg.eventDate);
    var time = parseTime(cfg.eventTime) || { hh: 0, mm: 0 };
    var problems = [];
    if (!date) problems.push("eventDate must look like YYYY-MM-DD (got \"" + cfg.eventDate + "\").");
    if (!parseTime(cfg.eventTime)) problems.push("eventTime must look like HH:MM (got \"" + cfg.eventTime + "\").");

    var startMs = date ? zonedTime(date.y, date.m, date.d, time.hh, time.mm, timeZone) : NaN;
    var durationMs = (Number(cfg.eventDurationHours) || 6) * 3600000;

    var rsvp = cfg.rsvp || {};
    var deadline = parseDate(rsvp.deadline);
    // Replies close at the end of the deadline day (venue time), or when the event starts.
    var rsvpClosesMs = deadline ? zonedTime(deadline.y, deadline.m, deadline.d, 23, 59, timeZone) + 59999 : startMs;

    var groom = cfg.groom || (cfg.coupleNames || "").split("&")[0].trim();
    var bride = cfg.bride || (cfg.coupleNames || "").split("&")[1] || "";
    bride = bride.trim();

    var weekday = date ? WEEKDAYS[new Date(Date.UTC(date.y, date.m - 1, date.d)).getUTCDay()] : "";
    var mapUrl = cfg.mapUrl ||
      "https://www.google.com/maps/search/?api=1&query=" +
      encodeURIComponent([cfg.venueName, cfg.venueAddress, cfg.venueCity].filter(Boolean).join(", "));

    var preview = readPreviewNow(timeZone);

    return {
      cfg: cfg,
      problems: problems,
      timeZone: timeZone,
      startMs: startMs,
      endMs: startMs + durationMs,
      rsvpClosesMs: rsvpClosesMs,
      mapUrl: mapUrl,
      mapIsSearch: !cfg.mapUrl,
      preview: preview,
      groom: groom,
      bride: bride,
      date: date,
      time: time,
      text: {
        groomUpper: groom.toLocaleUpperCase("uz"),
        brideUpper: bride.toLocaleUpperCase("uz"),
        monogram: groom.charAt(0) + "&" + bride.charAt(0),
        namesInline: groom + " & " + bride,
        namesInlineHtml: escapeHtml(groom) + " <em>&amp;</em> " + escapeHtml(bride),
        dateDots: date ? pad(date.d) + " · " + pad(date.m) + " · " + date.y : "",
        dateLong: date ? date.d + "-" + MONTHS[date.m - 1] + ", " + date.y + "-yil" : "",
        day: date ? pad(date.d) : "",
        monthName: date ? capitalize(MONTHS[date.m - 1]) : "",
        year: date ? String(date.y) : "",
        weekday: weekday,
        time: pad(time.hh) + ":" + pad(time.mm),
        dateTimeShort: date ? date.d + "-" + MONTHS[date.m - 1] + " · soat " + pad(time.hh) + ":" + pad(time.mm) : "",
        deadlineLong: deadline ? deadline.d + "-" + MONTHS[deadline.m - 1] : ""
      }
    };
  }

  window.LITC = {
    $: $,
    $$: $$,
    pad: pad,
    escapeHtml: escapeHtml,
    zonedTime: zonedTime,
    reducedMotion: function () { return !!(reducedMotionQuery && reducedMotionQuery.matches); },
    view: null,

    /** Current time, shifted when ?now= preview is active. */
    now: function () {
      var v = window.LITC.view;
      return Date.now() + (v && v.preview ? v.preview.offset : 0);
    },

    init: function () {
      var cfg = window.WEDDING_CONFIG;
      if (!cfg) throw new Error("config.js did not load (window.WEDDING_CONFIG is missing).");
      window.LITC.view = buildView(cfg);
      window.LITC.view.problems.forEach(function (p) { console.error("[taklifnoma] config: " + p); });
      return window.LITC.view;
    },

    /** Responsive <picture> markup for an image id from config.images. */
    picture: function (id, opts) {
      opts = opts || {};
      var cfg = window.LITC.view.cfg;
      var item = (cfg.images || {})[id];
      if (!item) {
        console.warn("[taklifnoma] Image id \"" + id + "\" is not defined in config.images.");
        return "";
      }
      var widths = (item.widths || [720]).slice().sort(function (a, b) { return a - b; });
      var max = widths[widths.length - 1];
      var ratio = String(item.ratio || "4/5").split("/").map(Number);
      var height = Math.round(max * ratio[1] / ratio[0]);
      var src = function (w) { return encodeURI("assets/images/" + id + "-" + w + ".webp"); };
      var srcset = widths.map(function (w) { return src(w) + " " + w + "w"; }).join(", ");
      var alt = escapeHtml(opts.alt != null ? opts.alt : item.alt || "");
      var loading = opts.eager ? 'fetchpriority="high"' : 'loading="lazy"';
      return '<img src="' + src(max) + '" srcset="' + srcset + '" sizes="' + (opts.sizes || "100vw") + '"' +
        ' width="' + max + '" height="' + height + '" alt="' + alt + '" ' + loading + ' decoding="async"' +
        ' data-image-id="' + escapeHtml(id) + '">';
    },

    /** Largest file for an image id (used by the lightbox). */
    largest: function (id) {
      var item = (window.LITC.view.cfg.images || {})[id] || {};
      var widths = item.widths || [720];
      return encodeURI("assets/images/" + id + "-" + Math.max.apply(null, widths) + ".webp");
    },

    /** Lock / unlock page scrolling (menu, lightbox). Nested calls are counted. */
    lockScroll: (function () {
      var count = 0;
      return function (on) {
        count = Math.max(0, count + (on ? 1 : -1));
        document.documentElement.classList.toggle("is-scroll-locked", count > 0);
      };
    })(),

    /** Keep Tab focus inside `container` while it is open. Returns a release function. */
    trapFocus: function (container) {
      function onKey(e) {
        if (e.key !== "Tab") return;
        var items = $$('a[href], button:not([disabled]), input:not([disabled]):not([tabindex="-1"]), select, textarea, [tabindex]:not([tabindex="-1"])', container)
          .filter(function (el) { return el.offsetParent !== null || el === document.activeElement; });
        if (!items.length) return;
        var first = items[0], last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
      document.addEventListener("keydown", onKey);
      return function () { document.removeEventListener("keydown", onKey); };
    }
  };
})();
