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

  function renderStory(cfg) {
    var list = L.$('[data-slot="story"]');
    var items = cfg.storyContent || [];
    if (!items.length) {
      L.$("#hikoya").hidden = true;
      return;
    }
    var html = items.map(function (item) {
      var media = item.image
        ? '<div class="chapter__media reveal reveal--image">' +
          L.picture(item.image, { sizes: "(min-width: 820px) 26rem, 85vw" }) + "</div>"
        : "";
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
      venueName: cfg.venueName || "",
      venueCity: cfg.venueCity || "",
      venueAddress: cfg.venueAddress || "",
      finalMessage: finalScene.message || "",
      musicCredit: cfg.backgroundMusic && cfg.musicTitle ? "Musiqa: " + cfg.musicTitle : "",
      countdownNote: v.text.dateLong ? v.text.dateLong + " · " + v.text.weekday + " · " + v.text.time : "",
      rsvpLead: v.text.deadlineLong
        ? "Iltimos, " + v.text.deadlineLong + "gacha javobingizni bildiring — bu bizga tayyorgarlikni to‘g‘ri rejalashtirishga yordam beradi."
        : "Iltimos, ishtirokingizni oldindan bildiring — bu bizga tayyorgarlikni to‘g‘ri rejalashtirishga yordam beradi.",
      rsvpContact: rsvp.contactNote || ""
    }));

    renderInvitation(cfg);
    renderStory(cfg);
    renderGallery(cfg);

    renderPhoto("[data-opening-photo]", opening.image, { eager: true, sizes: "(min-width: 900px) 20rem, 60vw" });
    var locationImage = cfg.locationImage === undefined ? "staircase" : cfg.locationImage;
    renderPhoto('[data-slot="locationPhoto"]', locationImage, { sizes: "(min-width: 820px) 24rem, 90vw" });
    renderPhoto('[data-slot="finalePhoto"]', finalScene.image, { sizes: "(min-width: 900px) 26rem, 100vw" });

    var map = L.$("[data-map-link]");
    map.href = v.mapUrl;
    if (v.mapIsSearch) map.setAttribute("data-map-search", "");

    if (v.date) document.title = v.text.namesInline + " — to‘yga taklifnoma";
  };
})();
