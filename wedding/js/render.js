/* ==========================================================================
   render.js — fills the page from config.js.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  var COLOR_VARS = {
    ivory: "--ivory", cream: "--cream", champagne: "--champagne", beige: "--beige",
    taupe: "--taupe", ink: "--ink", gold: "--gold", goldDeep: "--gold-deep"
  };

  function applyColors(colors) {
    var root = document.documentElement.style;
    Object.keys(colors || {}).forEach(function (key) {
      if (COLOR_VARS[key] && colors[key]) root.setProperty(COLOR_VARS[key], colors[key]);
    });
  }

  function bindText(values) {
    L.$$("[data-bind]").forEach(function (el) {
      var key = el.getAttribute("data-bind");
      if (!(key in values)) return;
      var value = values[key] == null ? "" : values[key];
      if (/Html$/.test(key)) el.innerHTML = value;
      else el.textContent = value;
    });
  }

  function renderInvitation(cfg) {
    var slot = L.$('[data-slot="invitationBody"]');
    var body = (cfg.invitationText && cfg.invitationText.body) || [];
    slot.innerHTML = body.map(function (p) {
      return '<p class="reveal">' + L.escapeHtml(p) + "</p>";
    }).join("");
  }

  /** Silent looping film; js/video.js loads and plays it only while it's on screen. */
  function film(id, cls) {
    var cfg = L.view.cfg;
    var meta = (cfg.videos || {})[id];
    if (!meta) {
      console.warn("[taklifnoma] Video id \"" + id + "\" is not defined in config.videos.");
      return "";
    }
    return '<video class="' + cls + '" muted loop playsinline preload="none" disablepictureinpicture' +
      ' poster="' + L.asset("assets/video/" + id + ".webp") + '"' +
      ' data-video="' + L.asset("assets/video/" + id + ".mp4") + '"' +
      ' data-video-webm="' + L.asset("assets/video/" + id + ".webm") + '"' +
      ' aria-label="' + L.escapeHtml(meta.alt || "") + '"></video>';
  }

  /** A scene's background: a film from config.videos, or a photo from config.images
      (photos get the same slow cinematic drift, so every scene feels alive). */
  function renderScenes(cfg) {
    var scenes = cfg.scenes || {};
    L.$$("[data-scene]").forEach(function (slot) {
      var id = scenes[slot.getAttribute("data-scene")];
      var isFilm = id && (cfg.videos || {})[id];
      var isPhoto = id && !isFilm && (cfg.images || {})[id];
      var poster = isFilm ? L.asset("assets/video/" + id + ".webp") : isPhoto ? L.largest(id) : "";
      var media = isFilm ? film(id, "scene__film")
        : isPhoto ? L.picture(id, { sizes: "(min-width: 900px) 30rem, 100vw", eager: slot.getAttribute("data-scene") === "opening" })
          .replace("<img ", '<img class="scene__film scene__still" ') : "";
      if (id && !media) console.warn("[taklifnoma] Scene \"" + id + "\" is neither in config.videos nor config.images.");
      slot.innerHTML = (poster ? '<div class="scene__backdrop" style="background-image:url(\'' + poster + '\')"></div>' : "") +
        media + '<div class="scene__scrim"></div>';
    });
  }

  function renderMarquee(v) {
    var item = '<span class="marquee__item"><span class="gold-text">' + L.escapeHtml(v.text.namesInline) +
      '</span><i></i><span class="gold-text">' + L.escapeHtml(v.text.dateDots.replace(/ · /g, ".")) + "</span><i></i></span>";
    var half = new Array(7).join(item); // 6 copies; the track holds two halves for a seamless loop
    L.$$("[data-marquee]").forEach(function (track) { track.innerHTML = half + half; });
  }

  /** Wrap each letter in a span so the names can be revealed letter by letter. */
  function splitLetters() {
    L.$$("[data-split]").forEach(function (el) {
      var text = el.textContent;
      el.setAttribute("aria-label", text);
      el.innerHTML = Array.prototype.map.call(text, function (ch, i) {
        // Outer span animates; inner span carries the foil (clip-text can't sit on an animated layer).
        return '<span class="ch" aria-hidden="true" style="--i:' + i + '"><span class="ch__g">' +
          (ch === " " ? "&nbsp;" : L.escapeHtml(ch)) + "</span></span>";
      }).join("");
    });
  }

  /** Month grid (Monday first) with the wedding day sealed in gold. */
  function renderCalendar(v) {
    var grid = L.$("[data-calendar]");
    if (!grid || !v.date) return;
    var heads = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"];
    var first = new Date(Date.UTC(v.date.y, v.date.m - 1, 1)).getUTCDay(); // 0 = Sunday
    var lead = (first + 6) % 7;
    var days = new Date(Date.UTC(v.date.y, v.date.m, 0)).getUTCDate();
    var html = heads.map(function (h) { return '<span class="calendar__head" role="columnheader">' + h + "</span>"; }).join("");
    for (var i = 0; i < lead; i++) html += '<span class="calendar__day calendar__day--empty"></span>';
    for (var d = 1; d <= days; d++) {
      var on = d === v.date.d;
      html += '<span class="calendar__day' + (on ? " calendar__day--on" : "") + '" role="gridcell"' +
        (on ? ' aria-current="date" aria-label="' + L.escapeHtml(v.text.dateLong) + ' — to‘y kuni"' : "") + ">" + d + "</span>";
    }
    grid.innerHTML = html;
  }

  function renderStory(cfg) {
    var list = L.$('[data-slot="story"]');
    var items = cfg.storyContent || [];
    if (!items.length) {
      L.$("#hikoya").hidden = true;
      return;
    }
    var html = items.map(function (item) {
      var inner = item.video && (cfg.videos || {})[item.video] ? film(item.video, "chapter__film")
        : item.image ? L.picture(item.image, { sizes: "(min-width: 820px) 26rem, 85vw" }) : "";
      var media = inner ? '<div class="chapter__media reveal reveal--image">' + inner + "</div>" : "";
      return '<li class="chapter">' + media +
        '<div class="chapter__body">' +
        (item.label ? '<p class="chapter__label reveal">' + L.escapeHtml(item.label) + "</p>" : "") +
        '<h3 class="chapter__title reveal">' + L.escapeHtml(item.title) + "</h3>" +
        '<p class="chapter__text reveal">' + L.escapeHtml(item.text) + "</p>" +
        "</div></li>";
    }).join("");
    list.innerHTML = html;
  }

  function renderGallery(cfg) {
    var grid = L.$('[data-slot="gallery"]');
    var ids = (cfg.galleryImages || []).filter(function (id) { return cfg.images && cfg.images[id]; });
    if (!ids.length) {
      L.$("#galereya").hidden = true;
      return;
    }
    grid.innerHTML = ids.map(function (id, i) {
      var item = cfg.images[id];
      var r = String(item.ratio || "4/5").split("/").map(Number);
      var wide = r[0] / r[1] > 1.2;
      return '<li class="gallery__item' + (wide ? " gallery__item--wide" : "") + ' reveal reveal--image" style="--delay:' + (i % 4) * 0.08 + 's">' +
        '<button class="gallery__btn" type="button" data-gallery-index="' + i + '" aria-label="Suratni kattalashtirish: ' + L.escapeHtml(item.alt || "") + '">' +
        L.picture(id, { sizes: wide ? "(min-width: 1024px) 40rem, 92vw" : "(min-width: 1024px) 20rem, 46vw", alt: "" }) +
        "</button></li>";
    }).join("");
    grid.setAttribute("data-ids", JSON.stringify(ids));
  }

  function renderPhoto(selector, id, opts) {
    var slot = L.$(selector);
    if (!slot) return;
    if (!id) { slot.hidden = true; return; }
    slot.innerHTML = L.picture(id, opts);
  }

  window.LITC.render = function () {
    var v = L.view;
    var cfg = v.cfg;
    applyColors(cfg.colors);

    var opening = cfg.opening || {};
    var inv = cfg.invitationText || {};
    var rsvp = cfg.rsvp || {};
    var finalScene = cfg.finalScene || {};

    bindText(Object.assign({}, v.text, {
      openingEyebrow: opening.eyebrow || "To‘yga taklifnoma",
      openingSubtitle: opening.subtitle || "",
      openingButton: opening.button || "Taklifnomani ochish",
      invitationEyebrow: inv.eyebrow || "Taklifnoma",
      invitationGreeting: inv.greeting || "",
      invitationLead: inv.lead || "",
      invitationSignature: inv.signature || "",
      // No venue name yet → the city takes its place (and isn't repeated below it).
      venueName: cfg.venueName || cfg.venueCity || "",
      venueCity: cfg.venueName ? cfg.venueCity || "" : "",
      venueAddress: cfg.venueAddress || "",
      finalMessage: finalScene.message || "",
      musicCredit: cfg.backgroundMusic && cfg.musicTitle ? "Musiqa: " + cfg.musicTitle : "",
      countdownNote: v.text.dateLong ? v.text.dateLong + " · " + v.text.weekday + " · " + v.text.time : "",
      rsvpLead: v.text.deadlineLong
        ? "Iltimos, " + v.text.deadlineLong + "gacha javobingizni bildiring — bu bizga tayyorgarlikni to‘g‘ri rejalashtirishga yordam beradi."
        : "Iltimos, ishtirokingizni oldindan bildiring — bu bizga tayyorgarlikni to‘g‘ri rejalashtirishga yordam beradi.",
      rsvpContact: rsvp.contactNote || "",
      initialGroom: v.groom.charAt(0),
      initialBride: v.bride.charAt(0),
      groom: v.groom,
      bride: v.bride,
      timeLabel: "Soat " + v.text.time,
      monthYear: v.text.monthName + " " + v.text.year
    }));
    renderCalendar(v);
    splitLetters();
    renderScenes(cfg);
    renderMarquee(v);

    renderInvitation(cfg);
    renderStory(cfg);
    renderGallery(cfg);

    var locationImage = cfg.locationImage === undefined ? "staircase" : cfg.locationImage;
    renderPhoto('[data-slot="locationPhoto"]', locationImage, { sizes: "(min-width: 820px) 24rem, 90vw" });

    var map = L.$("[data-map-link]");
    map.href = v.mapUrl;
    if (v.mapIsSearch) map.setAttribute("data-map-search", "");
    // Turn-by-turn directions from wherever the guest is.
    var dir = L.$("[data-directions-link]");
    if (dir) {
      dir.href = "https://www.google.com/maps/dir/?api=1&destination=" +
        encodeURIComponent([cfg.venueName, cfg.venueAddress, cfg.venueCity].filter(Boolean).join(", "));
    }

    if (v.date) document.title = v.text.namesInline + " — to‘yga taklifnoma";
  };
})();
