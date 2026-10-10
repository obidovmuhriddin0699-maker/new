import type { ContentStatus, ContentType } from "./types";

export const TZ = "Asia/Tashkent";

export const STATUS_LABEL: Record<ContentStatus, string> = {
  DRAFT: "Qoralama",
  GENERATING: "Yaratilmoqda",
  READY_FOR_REVIEW: "Ko‘rib chiqish",
  EDIT_REQUESTED: "Tahrir so‘ralgan",
  APPROVED: "Tasdiqlangan",
  SCHEDULED: "Rejalashtirilgan",
  PUBLISHING: "Nashr qilinmoqda",
  PUBLISHED: "Nashr qilingan",
  FAILED: "Xato",
  REJECTED: "Rad etilgan",
};

export const STATUS_STYLE: Record<ContentStatus, string> = {
  DRAFT: "bg-stone-100 text-stone-700 ring-stone-300 dark:bg-stone-800 dark:text-stone-200 dark:ring-stone-600",
  GENERATING: "bg-violet-50 text-violet-700 ring-violet-200 dark:bg-violet-950 dark:text-violet-200 dark:ring-violet-800",
  READY_FOR_REVIEW: "bg-amber-50 text-amber-800 ring-amber-200 dark:bg-amber-950 dark:text-amber-200 dark:ring-amber-800",
  EDIT_REQUESTED: "bg-orange-50 text-orange-800 ring-orange-200 dark:bg-orange-950 dark:text-orange-200 dark:ring-orange-800",
  APPROVED: "bg-emerald-50 text-emerald-800 ring-emerald-200 dark:bg-emerald-950 dark:text-emerald-200 dark:ring-emerald-800",
  SCHEDULED: "bg-sky-50 text-sky-800 ring-sky-200 dark:bg-sky-950 dark:text-sky-200 dark:ring-sky-800",
  PUBLISHING: "bg-blue-50 text-blue-800 ring-blue-200 dark:bg-blue-950 dark:text-blue-200 dark:ring-blue-800",
  PUBLISHED: "bg-teal-50 text-teal-800 ring-teal-200 dark:bg-teal-950 dark:text-teal-200 dark:ring-teal-800",
  FAILED: "bg-red-50 text-red-700 ring-red-200 dark:bg-red-950 dark:text-red-200 dark:ring-red-800",
  REJECTED: "bg-zinc-100 text-zinc-600 ring-zinc-300 dark:bg-zinc-800 dark:text-zinc-300 dark:ring-zinc-600",
};

export const TYPE_LABEL: Record<ContentType, string> = {
  POST: "Post",
  CAROUSEL: "Karusel",
  REELS: "Reels",
  STORY: "Story",
};

// Instagram formats per type — the backend's ALLOWED_ASPECT_RATIOS (providers/media.py);
// readiness refuses anything else. The first entry is the default (DEFAULT_ASPECT_RATIO).
export const ASPECT_RATIOS: Record<ContentType, string[]> = {
  POST: ["4:5", "1:1", "16:9"],
  CAROUSEL: ["4:5", "1:1"],
  REELS: ["9:16"],
  STORY: ["9:16"],
};

export const ASPECT_LABEL: Record<string, string> = {
  "4:5": "4:5 (vertikal)",
  "1:1": "1:1 (kvadrat)",
  "16:9": "16:9 (gorizontal)",
  "9:16": "9:16 (to‘liq ekran)",
};

/** The ratio if allowed for the type, else the type's default. */
export function validRatio(type: ContentType, ratio: string | null | undefined): string {
  return ratio && ASPECT_RATIOS[type].includes(ratio) ? ratio : ASPECT_RATIOS[type][0];
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("uz-UZ", {
    timeZone: TZ,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const d = value.length === 10 ? new Date(`${value}T00:00:00`) : new Date(value);
  return new Intl.DateTimeFormat("uz-UZ", { year: "numeric", month: "2-digit", day: "2-digit" }).format(d);
}

/** YYYY-MM-DD in local time. */
export function isoDate(d: Date): string {
  const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

// Asia/Tashkent is UTC+5 all year (no DST), so a fixed offset is exact.
const TZ_OFFSET = "+05:00";
const TZ_OFFSET_MS = 5 * 3600 * 1000;

/** Instant -> "YYYY-MM-DDTHH:mm" wall-clock time in Tashkent (for datetime-local inputs). */
export function tashkentInputValue(d: Date): string {
  return new Date(d.getTime() + TZ_OFFSET_MS).toISOString().slice(0, 16);
}

/** datetime-local value read as Tashkent wall-clock time -> UTC ISO string. */
export function tashkentToIso(value: string): string {
  const withSeconds = value.length === 16 ? `${value}:00` : value;
  const d = new Date(`${withSeconds}${TZ_OFFSET}`);
  if (Number.isNaN(d.getTime())) throw new Error("Vaqt noto‘g‘ri kiritilgan");
  return d.toISOString();
}

/** Instant -> calendar day "YYYY-MM-DD" in Tashkent. */
export function tashkentDay(value: string): string {
  return new Date(new Date(value).getTime() + TZ_OFFSET_MS).toISOString().slice(0, 10);
}

export function truncate(text: string | null | undefined, n = 120): string {
  if (!text) return "";
  return text.length > n ? `${text.slice(0, n - 1)}…` : text;
}

export function parseHashtags(text: string): string[] {
  return text
    .split(/[\s,]+/)
    .map((t) => t.trim())
    .filter(Boolean);
}
