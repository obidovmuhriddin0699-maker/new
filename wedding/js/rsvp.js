/* ==========================================================================
   rsvp.js — attendance form.
   • Validates in the browser with accessible, inline error messages.
   • Sends to config.rsvp.rsvpEndpoint only. With no endpoint configured it
     says so plainly — it never shows "saved" unless the server answered OK.
   • Duplicate protection: one request at a time (button locked), a stable
     submissionId per reply so the backend can de-duplicate retries, and the
     sent reply remembered on this device.
   ========================================================================== */
(function () {
  "use strict";
  var L = window.LITC;
  var TIMEOUT_MS = 15000;

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "id-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
  }

  function storageKey() { return "litc-rsvp:" + L.view.cfg.eventDate; }
  function readSaved() {
    try { return JSON.parse(localStorage.getItem(storageKey()) || "null"); } catch (e) { return null; }
  }
  function writeSaved(data) {
    try { localStorage.setItem(storageKey(), JSON.stringify(data)); } catch (e) { /* private mode */ }
  }

  window.LITC.rsvp = {
    init: function () {
      var v = L.view;
      var rsvp = v.cfg.rsvp || {};
      var form = L.$("[data-rsvp-form]");
      var done = L.$("[data-rsvp-done]");
      var closed = L.$("[data-rsvp-closed]");
      var submit = L.$("[data-rsvp-submit]");
      var submitLabel = L.$("[data-rsvp-submit-label]");
      var status = L.$("[data-rsvp-status]");
      var guestsField = L.$("[data-guests-field]");
      var guests = form.elements.guests;
      var message = form.elements.message;
      var counter = L.$("[data-message-count]");
      var maxGuests = Math.max(1, Math.min(20, Number(rsvp.maxGuests) || 6));
      var submitting = false;
      var submissionId = uuid();

      // Guest-count options.
      for (var i = 1; i <= maxGuests; i++) {
        var opt = document.createElement("option");
        opt.value = String(i);
        opt.textContent = i === 1 ? "Faqat o‘zim" : i + " kishi";
        guests.appendChild(opt);
      }

      function showPanel(panel) {
        form.hidden = panel !== form;
        done.hidden = panel !== done;
        closed.hidden = panel !== closed;
      }

      // Replies closed (deadline passed or the event has started)?
      if (!isNaN(v.rsvpClosesMs) && L.now() > v.rsvpClosesMs) {
        L.$("[data-rsvp-closed-text]").textContent = L.now() >= v.startMs
          ? "Javoblarni qabul qilish yakunlandi. E’tiboringiz uchun rahmat!"
          : "Javob berish muddati tugadi. Savollaringiz bo‘lsa, bizga to‘g‘ridan-to‘g‘ri murojaat qiling.";
        showPanel(closed);
        var lead = L.$('[data-bind="rsvpLead"]');
        if (lead) lead.hidden = true;
        return;
      }

      function showDone(data, earlier) {
        var yes = data.attendance === "yes";
        L.$("[data-rsvp-done-title]").textContent = yes ? "Rahmat, " + data.name + "!" : "Javobingiz uchun rahmat";
        L.$("[data-rsvp-done-text]").textContent = (earlier ? "Javobingiz avval yuborilgan. " : "") + (yes
          ? "Sizni " + (data.guests > 1 ? data.guests + " kishi bo‘lib " : "") + "to‘yimizda ko‘rishni intiqlik bilan kutamiz."
          : "Afsuski kela olmasligingizni tushunamiz. Samimiy tilaklaringiz biz uchun qadrli.");
        showPanel(done);
      }

      var saved = readSaved();
      if (saved && saved.name) showDone(saved, true);

      L.$("[data-rsvp-again]").addEventListener("click", function () {
        submissionId = uuid(); // a changed reply is a new submission
        status.textContent = "";
        status.className = "rsvp__status";
        showPanel(form);
        form.elements.name.focus();
      });

      // ---------- Validation ----------
      function setError(name, text) {
        var holder = L.$('[data-error-for="' + name + '"]', form);
        holder.textContent = text || "";
        if (name === "attendance") {
          holder.parentElement.classList.toggle("is-invalid", !!text);
          L.$$('input[name="attendance"]', form).forEach(function (r) {
            if (text) r.setAttribute("aria-invalid", "true"); else r.removeAttribute("aria-invalid");
          });
        } else {
          var input = form.elements[name];
          if (text) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
        }
      }

      function attendance() {
        var checked = L.$('input[name="attendance"]:checked', form);
        return checked ? checked.value : "";
      }

      function validate() {
        var errors = {};
        var name = form.elements.name.value.trim().replace(/\s+/g, " ");
        if (!name) errors.name = "Iltimos, ismingizni kiriting.";
        else if (name.length < 2) errors.name = "Ism kamida 2 ta harfdan iborat bo‘lsin.";
        else if (!/\p{L}/u.test(name)) errors.name = "Ismni harflar bilan yozing.";
        if (!attendance()) errors.attendance = "Iltimos, ishtirok etish-etmasligingizni tanlang.";
        if (attendance() === "yes") {
          var n = Number(guests.value);
          if (!(n >= 1 && n <= maxGuests)) errors.guests = "Mehmonlar sonini tanlang (1–" + maxGuests + ").";
        }
        ["name", "attendance", "guests"].forEach(function (key) { setError(key, errors[key]); });
        return { ok: !Object.keys(errors).length, errors: errors, name: name };
      }

      L.$$('input[name="attendance"]', form).forEach(function (radio) {
        radio.addEventListener("change", function () {
          guestsField.hidden = attendance() !== "yes";
          setError("attendance", "");
          if (attendance() !== "yes") setError("guests", "");
        });
      });
      form.elements.name.addEventListener("input", function () {
        if (form.elements.name.getAttribute("aria-invalid")) setError("name", "");
      });
      message.addEventListener("input", function () {
        counter.textContent = message.value.length + " / 500";
      });

      function setLoading(on) {
        submitting = on;
        submit.disabled = on;
        submit.classList.toggle("is-loading", on);
        submit.setAttribute("aria-busy", on ? "true" : "false");
        submitLabel.textContent = on ? "Yuborilmoqda…" : "Javobni yuborish";
      }

      function setStatus(kind, text) {
        status.className = "rsvp__status" + (kind ? " is-" + kind : "");
        status.textContent = text;
      }

      // ---------- Submit ----------
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (submitting) return; // ignore double clicks / repeated Enter

        var result = validate();
        if (!result.ok) {
          setStatus("error", "Iltimos, belgilangan maydonlarni to‘g‘rilang.");
          var first = result.errors.name ? form.elements.name
            : result.errors.attendance ? L.$('input[name="attendance"]', form) : guests;
          first.focus();
          return;
        }
        // Bots fill the hidden field; quietly drop the submission.
        if (form.elements.website.value) return;

        var yes = attendance() === "yes";
        var payload = {
          submissionId: submissionId,
          name: result.name,
          attendance: attendance(),
          guests: yes ? Number(guests.value) : 0,
          message: message.value.trim(),
          event: v.text.namesInline + " · " + v.cfg.eventDate,
          submittedAt: new Date().toISOString(),
          page: window.location.href.split("#")[0]
        };

        var endpoint = (rsvp.rsvpEndpoint || "").trim();
        if (!endpoint) {
          console.warn("[taklifnoma] RSVP not sent: config.rsvp.rsvpEndpoint is empty. See docs/RSVP.md.");
          setStatus("warning", "Javobingiz yuborilmadi: onlayn javob qabul qilish hali sozlanmagan. " +
            (rsvp.contactNote ? rsvp.contactNote : "Iltimos, kelin-kuyovga to‘g‘ridan-to‘g‘ri xabar bering."));
          return;
        }

        setLoading(true);
        setStatus("", "Javobingiz yuborilmoqda…");

        var controller = "AbortController" in window ? new AbortController() : null;
        var timer = window.setTimeout(function () { if (controller) controller.abort(); }, TIMEOUT_MS);
        var asText = rsvp.format === "text";

        fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": asText ? "text/plain;charset=utf-8" : "application/json", "Accept": "application/json" },
          body: JSON.stringify(payload),
          signal: controller ? controller.signal : undefined,
          redirect: "follow"
        }).then(function (res) {
          return res.text().then(function (body) {
            var json = null;
            try { json = body ? JSON.parse(body) : null; } catch (err) { /* non-JSON is fine if status is OK */ }
            var rejected = json && (json.ok === false || json.result === "error" || json.success === false);
            if (!res.ok || rejected) {
              var err = new Error("HTTP " + res.status + (json && json.error ? " — " + json.error : ""));
              err.status = res.status;
              throw err;
            }
          });
        }).then(function () {
          var record = { name: payload.name, attendance: payload.attendance, guests: payload.guests, at: payload.submittedAt };
          writeSaved(record);
          setStatus("", "");
          showDone(record, false);
          done.focus();
        }).catch(function (err) {
          console.error("[taklifnoma] RSVP failed:", err);
          var text = err && err.name === "AbortError"
            ? "Server javob bermadi. Internet aloqasini tekshirib, qayta urinib ko‘ring."
            : err && err.status >= 500
              ? "Serverda vaqtinchalik nosozlik. Birozdan so‘ng qayta urinib ko‘ring."
              : err && err.status
                ? "Javobni qabul qilib bo‘lmadi (xato " + err.status + "). Iltimos, qayta urinib ko‘ring."
                : "Javobni yuborib bo‘lmadi. Internet aloqasini tekshirib, qayta urinib ko‘ring.";
          setStatus("error", text);
        }).then(function () {
          window.clearTimeout(timer);
          setLoading(false);
        });
      });
    }
  };
})();
