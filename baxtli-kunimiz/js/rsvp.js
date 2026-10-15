/* ==========================================================================
   rsvp.js — "Ishtirokni tasdiqlang". The RSVP wax seal opens the form;
   answers are validated and delivered (data/wedding.json → rsvp):
     1. "endpoint": HTTPS URL accepting a JSON POST (Apps Script, Formspree…)
     2. "whatsapp": couple's number, e.g. 998901234567 — a prefilled message opens
     3. neither   — kept on this device only (localStorage) + a console warning
   ========================================================================== */
import { t, onLang } from "./i18n.js";
import { crackSeal } from "./seal.js";
import { play } from "./sfx.js";

const STORE = "baxtli-kunimiz:rsvp";

export function initRsvp(config = {}) {
  const sealBtn = document.getElementById("rsvp-seal");
  const panel = document.getElementById("rsvp-panel");
  const form = document.getElementById("rsvp-form");
  const thanks = document.getElementById("rsvp-thanks");
  const thanksText = document.getElementById("rsvp-thanks-text");
  const status = document.getElementById("rsvp-status");
  const submit = document.getElementById("rsvp-submit");
  if (!form) return;

  /* ---- the seal ---- */
  sealBtn?.addEventListener("click", () => {
    crackSeal(sealBtn);
    play("seal-crack");
    play("page", { delay: 0.35, volume: 0.8 });
    sealBtn.setAttribute("aria-expanded", "true");
    setTimeout(() => {
      sealBtn.closest(".rsvp-seal")?.classList.add("is-used");
      panel.classList.add("is-open");
      setTimeout(() => form.elements.name.focus({ preventScroll: true }), 700);
    }, 650);
  });

  /* ---- validation ---- */
  const max = Math.max(1, +config.maxGuests || 5);
  const guests = form.elements.guests;
  guests.max = String(max);
  const guestsField = guests.closest(".field");
  const attending = () => form.elements.attendance.value === "yes";
  const rules = {
    name: (v) => (v.trim().length < 2 ? t("e_name") : ""),
    phone: (v) => { const n = v.replace(/\D/g, "").length; return n < 9 || n > 15 ? t("e_phone") : ""; },
    attendance: (v) => (!v ? t("e_attend") : ""),
    guests: (v) => (!attending() ? "" : (Number.isInteger(+v) && +v >= 1 && +v <= max ? "" : t("e_guests")))
  };
  const errEl = (name) => document.getElementById(`rsvp-${name}-err`);
  function validate(name) {
    const msg = rules[name](form.elements[name].value || "");
    const err = errEl(name);
    if (err) err.textContent = msg;
    form.querySelectorAll(`[name="${name}"]`).forEach((el) => el.setAttribute("aria-invalid", msg ? "true" : "false"));
    const el = form.elements[name];
    (el instanceof RadioNodeList ? el[0] : el)?.closest(".field")?.classList.toggle("is-invalid", !!msg);
    return !msg;
  }
  form.addEventListener("input", (e) => {
    if (rules[e.target.name] && errEl(e.target.name)?.textContent) validate(e.target.name);
  });
  form.addEventListener("change", (e) => {
    if (e.target.name === "attendance") {
      play("click", { volume: 0.7 });
      validate("attendance");
      guestsField.classList.toggle("is-hidden", !attending());
    }
  });
  form.querySelectorAll("[data-step]").forEach((b) => b.addEventListener("click", () => {
    guests.value = String(Math.min(max, Math.max(1, (+guests.value || 1) + +b.dataset.step)));
    play("click", { volume: 0.6, rate: b.dataset.step > 0 ? 1.15 : 0.9 });
    validate("guests");
  }));
  onLang(() => ["name", "phone", "attendance", "guests"].forEach((n) => { if (errEl(n)?.textContent) validate(n); }));

  /* ---- submit ---- */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const ok = ["name", "phone", "attendance", "guests"].map(validate).every(Boolean);
    if (!ok) {
      status.textContent = t("f_check");
      form.querySelector('[aria-invalid="true"]')?.focus();
      return;
    }
    const payload = {
      type: "rsvp",
      name: form.elements.name.value.trim(),
      phone: form.elements.phone.value.trim(),
      attendance: form.elements.attendance.value,
      guests: attending() ? +guests.value : 0,
      message: form.elements.message.value.trim(),
      submittedAt: new Date().toISOString()
    };
    submit.disabled = true;
    status.textContent = t("f_sending");
    play("pop");
    try {
      await deliver(payload, config);
      form.hidden = true;
      thanksText.textContent = t(payload.attendance === "yes" ? "thanks_yes" : "thanks_no");
      thanks.hidden = false;
      thanks.focus({ preventScroll: true });
      thanks.scrollIntoView({ behavior: "smooth", block: "center" });
      play("success");
      status.textContent = "";
    } catch (err) {
      console.error("[rsvp]", err);
      status.textContent = t("f_failed");
    } finally {
      submit.disabled = false;
    }
  });
}

/** Shared by the RSVP form and the wishes book. */
export async function deliver(payload, config = {}) {
  if (config.endpoint) {
    const res = await fetch(config.endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return "endpoint";
  }
  if (config.whatsapp) {
    const lines = payload.type === "wish"
      ? [`💌 ${t("wishes_title")}`, `${payload.name}: ${payload.text}`]
      : [`💌 ${t("rsvp_title")}`, payload.attendance === "yes" ? `✓ ${t("f_yes")}` : `✗ ${t("f_no")}`,
         `${t("f_name")}: ${payload.name}`, `${t("f_phone")}: ${payload.phone}`,
         payload.attendance === "yes" ? `${t("f_guests")}: ${payload.guests}` : "", payload.message ? `${t("f_message")}: ${payload.message}` : ""];
    window.open(`https://wa.me/${config.whatsapp.replace(/\D/g, "")}?text=${encodeURIComponent(lines.filter(Boolean).join("\n"))}`, "_blank", "noopener");
    return "whatsapp";
  }
  const key = payload.type === "wish" ? "baxtli-kunimiz:wishes-sent" : STORE;
  const list = JSON.parse(localStorage.getItem(key) || "[]");
  list.push(payload);
  localStorage.setItem(key, JSON.stringify(list));
  console.warn("[rsvp] No rsvp.endpoint or rsvp.whatsapp in data/wedding.json — the answer is stored on this device only.");
  return "local";
}
