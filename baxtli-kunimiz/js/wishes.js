/* ==========================================================================
   wishes.js — "Tilaklar daftari" (guest book).

   A shared wall needs a small backend: set wishes.endpoint in
   data/wedding.json to a URL that returns a JSON array on GET
   ([{ "name": "…", "text": "…" }]) and accepts a JSON POST — the book then
   shows everyone's wishes. Without it, each wish is sent to the couple the
   same way as RSVP answers (rsvp.endpoint / rsvp.whatsapp) and is listed
   on the guest's own device.
   ========================================================================== */
import { t, onLang } from "./i18n.js";
import { play } from "./sfx.js";
import { deliver } from "./rsvp.js";

const STORE = "baxtli-kunimiz:my-wishes";

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function initWishes(config = {}, rsvpConfig = {}) {
  const form = document.getElementById("wish-form");
  const list = document.getElementById("wish-list");
  const status = document.getElementById("wish-status");
  if (!form || !list) return;

  let wishes = [];
  try { wishes = JSON.parse(localStorage.getItem(STORE) || "[]"); } catch (_) { wishes = []; }

  function render(newest = -1) {
    if (!wishes.length) { list.innerHTML = `<li class="wishes__empty">${esc(t("w_empty"))}</li>`; return; }
    list.innerHTML = wishes.slice().reverse().map((w, i) =>
      `<li class="wish${i === newest ? " wish--new" : ""}"><p>${esc(w.text)}</p><cite>— ${esc(w.name)}</cite></li>`).join("");
  }

  if (config.endpoint) {
    fetch(config.endpoint, { headers: { Accept: "application/json" } })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((rows) => { if (Array.isArray(rows)) { wishes = rows.filter((w) => w && w.name && w.text).slice(-100); render(); } })
      .catch((err) => console.warn("[wishes] could not load the shared book:", err));
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = form.elements.name.value.trim();
    const text = form.elements.text.value.trim();
    if (name.length < 2 || text.length < 2) { status.textContent = t("w_need"); return; }
    const wish = { type: "wish", name, text, submittedAt: new Date().toISOString() };
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    play("pop");
    try {
      await deliver(wish, config.endpoint ? { endpoint: config.endpoint } : rsvpConfig);
      wishes.push({ name, text });
      if (!config.endpoint) localStorage.setItem(STORE, JSON.stringify(wishes.slice(-50)));
      render(0);
      form.reset();
      status.textContent = t("w_thanks");
      play("shimmer", { volume: 0.5, delay: 0.15 });
    } catch (err) {
      console.error("[wishes]", err);
      status.textContent = t("f_failed");
    } finally {
      btn.disabled = false;
    }
  });

  render();
  onLang(() => render());
}
