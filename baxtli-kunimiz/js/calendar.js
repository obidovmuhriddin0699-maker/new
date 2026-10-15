/* ==========================================================================
   calendar.js — the wedding month with the day circled in gold,
   plus "Add to calendar" (.ics file for iPhone/Android/Outlook) and a
   Google Calendar link.
   ========================================================================== */
import { dateParts, pad } from "./data.js";
import { t, L, onLang } from "./i18n.js";
import { play } from "./sfx.js";

const utcStamp = (d) => d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");

export function initCalendar(data) {
  const grid = document.getElementById("calendar-grid");
  const { d, m, y, at } = dateParts(data);
  const end = new Date(at.getTime() + (data.durationHours || 5) * 3600e3);

  function render() {
    if (!grid) return;
    const first = new Date(Date.UTC(y, m - 1, 1)).getUTCDay();      // 0 = Sunday
    const lead = (first + 6) % 7;                                    // Monday first
    const days = new Date(Date.UTC(y, m, 0)).getUTCDate();
    let html = t("weekdays").map((w) => `<span class="calendar__wd" role="columnheader">${w}</span>`).join("");
    for (let i = 0; i < lead; i++) html += '<span class="calendar__day" aria-hidden="true"></span>';
    for (let day = 1; day <= days; day++) {
      const wedding = day === d;
      html += `<span class="calendar__day${wedding ? " is-wedding" : ""}" role="gridcell"${wedding ? ` aria-label="${pad(d)}.${pad(m)}.${y} — ${t("date_title")}"` : ""}><span>${day}</span></span>`;
    }
    grid.innerHTML = html;
    grid.setAttribute("aria-label", `${t("months")[m - 1]} ${y}`);
  }

  function details() {
    const title = t("calendar_event");
    const where = `${L(data.venue.name)}, ${L(data.venue.city)}`;
    return { title, where, text: t("invite_text") };
  }

  function updateGoogle() {
    const a = document.getElementById("google-calendar");
    if (!a) return;
    const { title, where, text } = details();
    a.href = "https://calendar.google.com/calendar/render?action=TEMPLATE" +
      `&text=${encodeURIComponent(title)}&dates=${utcStamp(at)}/${utcStamp(end)}` +
      `&location=${encodeURIComponent(where)}&details=${encodeURIComponent(text)}`;
  }

  function downloadIcs() {
    const { title, where, text } = details();
    const esc = (s) => String(s).replace(/([,;\\])/g, "\\$1").replace(/\n/g, "\\n");
    const ics = [
      "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Baxtli kunimiz//Taklifnoma//UZ", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
      "BEGIN:VEVENT",
      `UID:${y}${pad(m)}${pad(d)}-${data.monogram.replace(/\W/g, "")}@taklifnoma`,
      `DTSTAMP:${utcStamp(new Date())}`,
      `DTSTART:${utcStamp(at)}`,
      `DTEND:${utcStamp(end)}`,
      `SUMMARY:${esc(title)}`,
      `LOCATION:${esc(where)}`,
      `DESCRIPTION:${esc(text)}`,
      "BEGIN:VALARM", "TRIGGER:-P1D", "ACTION:DISPLAY", `DESCRIPTION:${esc(title)}`, "END:VALARM",
      "END:VEVENT", "END:VCALENDAR"
    ].join("\r\n");
    const blob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${data.monogram.replace(/\W/g, "")}-${y}${pad(m)}${pad(d)}.ics`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
    play("pop");
  }

  document.getElementById("add-calendar")?.addEventListener("click", downloadIcs);
  render();
  updateGoogle();
  onLang(() => { render(); updateGoogle(); });
  return { at };
}
