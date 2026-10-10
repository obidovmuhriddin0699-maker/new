/* ==========================================================================
   countdown.js — live countdown to config.eventDate + eventTime in
   config.timeZone, plus the "Kalendarga qo‘shish" (.ics) download.
   Nothing is hardcoded: every value is computed from the configured instant.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;

  // Uzbek doesn't inflect these nouns after numbers, so one form serves all counts.
  var LIVE_UNITS = { days: "kun", hours: "soat", minutes: "daqiqa" };

  function split(ms) {
    var s = Math.max(0, Math.floor(ms / 1000));
    return {
      days: Math.floor(s / 86400),
      hours: Math.floor((s % 86400) / 3600),
      minutes: Math.floor((s % 3600) / 60),
      seconds: s % 60
    };
  }

  function icsDate(ms) {
    return new Date(ms).toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
  }
  function icsText(s) {
    return String(s || "").replace(/\\/g, "\\\\").replace(/\n/g, "\\n").replace(/([,;])/g, "\\$1");
  }

  function downloadCalendar() {
    var v = L.view;
    var cfg = v.cfg;
    var location = [cfg.venueName, cfg.venueAddress, cfg.venueCity].filter(Boolean).join(", ");
    var lines = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//Love in the Clouds//Taklifnoma//UZ",
      "CALSCALE:GREGORIAN",
      "METHOD:PUBLISH",
      "BEGIN:VEVENT",
      "UID:" + icsDate(v.startMs) + "-" + encodeURIComponent(v.text.namesInline).replace(/%/g, "") + "@taklifnoma",
      "DTSTAMP:" + icsDate(Date.now()),
      "DTSTART:" + icsDate(v.startMs),
      "DTEND:" + icsDate(v.endMs),
      "SUMMARY:" + icsText(v.text.namesInline + " — nikoh to‘yi"),
      "LOCATION:" + icsText(location),
      "DESCRIPTION:" + icsText("Xarita: " + v.mapUrl),
      "BEGIN:VALARM",
      "TRIGGER:-P1D",
      "ACTION:DISPLAY",
      "DESCRIPTION:" + icsText("Ertaga " + v.text.namesInline + " to‘yi"),
      "END:VALARM",
      "END:VEVENT",
      "END:VCALENDAR"
    ];
    var blob = new Blob([lines.join("\r\n") + "\r\n"], { type: "text/calendar;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = (v.groom + "-" + v.bride + "-toy.ics").toLowerCase().replace(/[^a-z0-9.-]+/g, "-");
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  window.LITC.countdown = {
    init: function () {
      var v = L.view;
      var timer = L.$("[data-countdown]");
      var message = L.$("[data-countdown-message]");
      var title = L.$("[data-countdown-title]");
      var live = L.$("[data-countdown-live]");
      var cells = {};
      ["days", "hours", "minutes", "seconds"].forEach(function (unit) {
        cells[unit] = L.$('[data-unit="' + unit + '"]', timer);
      });
      var lastLive = "";
      var lastPhase = "";
      var handle = 0;

      var calendarBtn = L.$("[data-add-calendar]");
      if (isNaN(v.startMs)) {
        calendarBtn.hidden = true;
        timer.hidden = true;
        message.hidden = false;
        message.textContent = "To‘y sanasi hali belgilanmagan.";
        return;
      }
      calendarBtn.addEventListener("click", downloadCalendar);

      function setPhase(phase) {
        if (phase === lastPhase) return;
        lastPhase = phase;
        var counting = phase === "before";
        timer.hidden = !counting;
        message.hidden = counting;
        if (phase === "during") {
          title.textContent = "Bugun — o‘sha kun!";
          message.textContent = "Baxtli kunimiz keldi! Sizni to‘yxonada intiqlik bilan kutmoqdamiz.";
        } else if (phase === "after") {
          title.textContent = "Bu kun ortda qoldi";
          message.textContent = "Baxtli kunimiz o‘tdi. Duolaringiz va yonimizda bo‘lganingiz uchun chin dildan minnatdormiz.";
          calendarBtn.hidden = true;
        } else {
          title.textContent = "Baxtli kungacha";
        }
      }

      function tick() {
        var now = L.now();
        if (now >= v.endMs) { setPhase("after"); return stop(); }
        if (now >= v.startMs) { setPhase("during"); schedule(); return; }
        setPhase("before");
        var parts = split(v.startMs - now);
        cells.days.textContent = String(parts.days);
        cells.hours.textContent = L.pad(parts.hours);
        cells.minutes.textContent = L.pad(parts.minutes);
        cells.seconds.textContent = L.pad(parts.seconds);
        // Screen readers hear a calm summary once a minute, not every second.
        var summary = "To‘ygacha " + parts.days + " " + LIVE_UNITS.days + ", " + parts.hours + " " +
          LIVE_UNITS.hours + " va " + parts.minutes + " " + LIVE_UNITS.minutes + " qoldi.";
        if (summary !== lastLive) { live.textContent = summary; lastLive = summary; }
        schedule();
      }

      function schedule() {
        // Align ticks to the next whole second of (possibly shifted) time.
        handle = window.setTimeout(tick, 1000 - (L.now() % 1000) + 10);
      }
      function stop() { window.clearTimeout(handle); }

      timer.setAttribute("aria-hidden", "true"); // the live summary speaks for it
      tick();
      // Timers are throttled in background tabs; resync when the guest returns.
      document.addEventListener("visibilitychange", function () {
        if (!document.hidden && lastPhase !== "after") { stop(); tick(); }
      });
    },
    split: split
  };
})();
