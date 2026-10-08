/* ==========================================================================
   rsvp.js — RSVP form: inline validation, accessible errors, delivery.

   Delivery, in order of preference (configure in data/wedding.json → rsvp):
     1. "endpoint": any HTTPS URL that accepts a JSON POST (your backend,
        Google Apps Script, Formspree, …) — the answer is sent there.
     2. "whatsapp": the couple's number in international format (e.g. 998901234567)
        — a pre-filled WhatsApp message opens for the guest to send.
     3. neither set — the answer is kept on this device only (localStorage),
        and a warning is logged so the site owner knows to configure 1 or 2.
   ========================================================================== */

const STORE = "modern-love:rsvp";

export function initRsvp(config = {}, names = "") {
  const form = document.getElementById("rsvp-form");
  const success = document.getElementById("rsvp-success");
  const status = document.getElementById("rsvp-status");
  const submit = document.getElementById("rsvp-submit");
  if (!form) return;

  const max = Math.max(1, +config.maxGuests || 5);
  const guests = form.elements.guests;
  guests.max = String(max);
  const guestsField = guests.closest(".field");

  /* ---- helpers ---- */
  const fieldOf = (name) => form.querySelector(`[name="${name}"]`)?.closest(".field");
  const setError = (name, msg) => {
    const f = fieldOf(name);
    if (!f) return;
    f.classList.toggle("is-invalid", !!msg);
    const err = f.querySelector(".field__error");
    if (err) err.textContent = msg || "";
    form.querySelectorAll(`[name="${name}"]`).forEach((el) => el.setAttribute("aria-invalid", msg ? "true" : "false"));
  };
  const attending = () => form.elements.attendance.value === "yes";

  const rules = {
    name: (v) => (v.trim().length < 2 ? "Iltimos, ismingizni kiriting." : ""),
    phone: (v) => {
      const digits = v.replace(/\D/g, "");
      if (!digits) return "Iltimos, telefon raqamingizni kiriting.";
      return digits.length < 9 || digits.length > 15 ? "Telefon raqami noto‘g‘ri. Masalan: +998 90 123 45 67" : "";
    },
    attendance: (v) => (!v ? "Iltimos, kela olishingizni belgilang." : ""),
    guests: (v) => {
      if (!attending()) return "";
      const n = Number(v);
      return Number.isInteger(n) && n >= 1 && n <= max ? "" : `Mehmonlar soni 1 dan ${max} gacha bo‘lishi kerak.`;
    }
  };
  const validate = (name) => {
    const el = form.elements[name];
    const msg = rules[name](el.value ?? "");
    setError(name, msg);
    return !msg;
  };

  /* ---- interactions ---- */
  form.addEventListener("input", (e) => {
    const name = e.target.name;
    if (rules[name] && fieldOf(name)?.classList.contains("is-invalid")) validate(name);
  });
  form.addEventListener("focusout", (e) => {
    const name = e.target.name;
    if (rules[name] && e.target.value) validate(name);
  });
  form.addEventListener("change", (e) => {
    if (e.target.name === "attendance") {
      validate("attendance");
      guestsField.classList.toggle("is-hidden", !attending());
    }
  });
  form.querySelectorAll("[data-step]").forEach((b) => b.addEventListener("click", () => {
    guests.value = String(Math.min(max, Math.max(1, (Number(guests.value) || 1) + Number(b.dataset.step))));
    validate("guests");
  }));

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const ok = ["name", "phone", "attendance", "guests"].map(validate).every(Boolean);
    if (!ok) {
      const firstBad = form.querySelector(".is-invalid input, .is-invalid textarea");
      firstBad?.focus();
      status.textContent = "Iltimos, belgilangan maydonlarni tekshiring.";
      return;
    }
    const payload = {
      name: form.elements.name.value.trim(),
      phone: form.elements.phone.value.trim(),
      attendance: form.elements.attendance.value,
      guests: attending() ? Number(guests.value) : 0,
      message: form.elements.message.value.trim(),
      submittedAt: new Date().toISOString()
    };

    submit.disabled = true;
    status.textContent = "Yuborilmoqda…";
    try {
      await deliver(payload, config, names);
      form.hidden = true;
      success.hidden = false;
      success.focus({ preventScroll: true });
      status.textContent = "";
    } catch (err) {
      console.error("[rsvp]", err);
      status.textContent = "Javobingizni yuborib bo‘lmadi. Internetni tekshirib, qayta urinib ko‘ring.";
    } finally {
      submit.disabled = false;
    }
  });
}

async function deliver(payload, config, names) {
  if (config.endpoint) {
    const res = await fetch(config.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return;
  }
  if (config.whatsapp) {
    const text =
      `Taklifga javob — ${names}\n` +
      `${payload.attendance === "yes" ? "✓ Albatta boraman" : "✗ Afsuski, kela olmayman"}\n` +
      `Ism: ${payload.name}\nTelefon: ${payload.phone}\n` +
      (payload.attendance === "yes" ? `Mehmonlar: ${payload.guests}\n` : "") +
      (payload.message ? `Tilak: ${payload.message}` : "");
    const url = `https://wa.me/${config.whatsapp.replace(/\D/g, "")}?text=${encodeURIComponent(text)}`;
    window.open(url, "_blank", "noopener");
    return;
  }
  // No delivery channel configured: keep the answer on this device and tell the developer.
  const list = JSON.parse(localStorage.getItem(STORE) || "[]");
  list.push(payload);
  localStorage.setItem(STORE, JSON.stringify(list));
  console.warn("[rsvp] No rsvp.endpoint or rsvp.whatsapp configured in data/wedding.json — reply stored locally only.");
}
