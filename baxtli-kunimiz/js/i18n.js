/* ==========================================================================
   i18n.js — Uzbek / Russian. Texts live in data/wedding.json → text.{uz,ru}.
   Markup hooks:
     data-t="key"        → textContent
     data-t-ph="key"     → placeholder
     data-t-aria="key"   → aria-label
     data-list="key"     → one <span> per array item
     data-bind="name"    → values computed from the wedding data (names, date…)
   The choice is remembered on this device; ?lang=ru opens Russian directly.
   ========================================================================== */
import { dateParts, pad } from "./data.js";

const STORE = "baxtli-kunimiz:lang";
let data = null;
let lang = "uz";
const listeners = new Set();

const fill = (s, vars) => String(s).replace(/\{(\w+)\}/g, (m, k) => (vars[k] !== undefined ? vars[k] : m));
const local = (v) => (v && typeof v === "object" && !Array.isArray(v) ? (v[lang] ?? v.uz ?? "") : v);

export const getLang = () => lang;
export const L = local;

/** Translated text; `vars` fill {placeholders}. Unknown keys fall back to Uzbek. */
export function t(key, vars = {}) {
  const dict = data.text[lang] || {};
  const value = dict[key] !== undefined ? dict[key] : data.text.uz[key];
  if (value === undefined) return key;
  return Array.isArray(value) ? value : fill(value, { ...baseVars(), ...vars });
}

function baseVars() {
  return {
    groom: local(data.groom),
    bride: local(data.bride),
    date: data.date,
    venue: local(data.venue.name),
    deadline: data.rsvp?.deadline || "",
    max: data.rsvp?.maxGuests || 5,
    title: data.musicTitle || ""
  };
}

export function bindings() {
  const { d, m, y } = dateParts(data);
  return {
    groom: local(data.groom),
    bride: local(data.bride),
    monogram: data.monogram,
    dateSpaced: `${pad(d)} · ${pad(m)} · ${y}`,
    dateDots: data.date,
    time: data.time,
    venueName: local(data.venue.name),
    venueCity: local(data.venue.city),
    monthYear: `${t("months")[m - 1]} ${y}`,
    musicCredit: data.musicTitle ? `♪ ${data.musicTitle}` : ""
  };
}

export function onLang(fn) { listeners.add(fn); }

export function setLang(next, { silent = false } = {}) {
  if (!data.text[next]) next = "uz";
  lang = next;
  try { localStorage.setItem(STORE, next); } catch (_) { /* private mode */ }
  apply();
  if (!silent) listeners.forEach((fn) => fn(lang));
}

function apply() {
  const root = document.documentElement;
  root.lang = lang;
  document.querySelectorAll("[data-t]").forEach((el) => { el.textContent = t(el.dataset.t); });
  document.querySelectorAll("[data-t-ph]").forEach((el) => { el.placeholder = t(el.dataset.tPh); });
  document.querySelectorAll("[data-t-aria]").forEach((el) => el.setAttribute("aria-label", t(el.dataset.tAria)));
  document.querySelectorAll("[data-list]").forEach((el) => {
    const items = t(el.dataset.list);
    if (Array.isArray(items)) el.innerHTML = items.map((x) => `<span>${x}</span>`).join("");
  });
  const b = bindings();
  document.querySelectorAll("[data-bind]").forEach((el) => {
    const v = b[el.dataset.bind];
    if (v !== undefined) el.textContent = v;
  });
  document.querySelectorAll(".lang [data-lang]").forEach((btn) => btn.setAttribute("aria-pressed", String(btn.dataset.lang === lang)));
}

export function initI18n(d) {
  data = d;
  let start = d.defaultLang || "uz";
  try { start = localStorage.getItem(STORE) || start; } catch (_) { /* ignore */ }
  const q = new URLSearchParams(location.search).get("lang");
  if (q) start = q;
  setLang(start, { silent: true });
}
