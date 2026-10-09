// Browser-side API client. All calls go to the same-origin proxy (/api/backend/*);
// the session token lives in an httpOnly cookie and is never readable here.

import type { User } from "./types";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: unknown,
  ) {
    super(message);
  }
}

/** Expired / missing session: send the user to /login (and back here afterwards). */
function redirectIfUnauthenticated(res: Response): void {
  if (res.status === 401 && typeof window !== "undefined") {
    const next = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.assign(`/login?next=${next}`);
    throw new ApiError(401, "unauthenticated", "Sessiya tugagan, qayta kiring");
  }
}

type Options = { method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE"; body?: unknown };

export async function api<T>(path: string, options: Options = {}): Promise<T> {
  const res = await fetch(`/api/backend/${path.replace(/^\//, "")}`, {
    method: options.method ?? "GET",
    headers: options.body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    credentials: "same-origin",
    cache: "no-store",
  });
  redirectIfUnauthenticated(res);
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = data?.error ?? {};
    throw new ApiError(res.status, err.code ?? `http_${res.status}`, err.message ?? res.statusText, err.details);
  }
  return data as T;
}

/** Raw file upload through the same-origin proxy (bytes are validated by the backend). */
export async function uploadFile<T>(path: string, file: Blob): Promise<T> {
  const res = await fetch(`/api/backend/${path.replace(/^\//, "")}`, {
    method: "POST",
    headers: { "Content-Type": "application/octet-stream" },
    body: file,
    credentials: "same-origin",
    cache: "no-store",
  });
  redirectIfUnauthenticated(res);
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = data?.error ?? {};
    throw new ApiError(res.status, err.code ?? `http_${res.status}`, err.message ?? res.statusText, err.details);
  }
  return data as T;
}

// One auth/me request per signed-in session, shared by every component that asks (useMe).
let meCache: Promise<User | null> | null = null;

export function getMe(): Promise<User | null> {
  meCache ??= api<User>("auth/me").catch(() => {
    meCache = null; // retry next time
    return null;
  });
  return meCache;
}

/** Drop the cached user (sign-in / sign-out: the next user may have another role). */
export function forgetMe(): void {
  meCache = null;
}

/**
 * Ends the session via the Next route (revokes the token on the backend, clears the cookie).
 * Returns where to go next: /login, or /login?logout=failed when the server-side revoke
 * failed (the cookie is gone either way, but a copied token may live until it expires).
 */
export async function signOut(all = false): Promise<string> {
  forgetMe();
  try {
    const res = await fetch(`/api/auth/logout${all ? "?all=1" : ""}`, { method: "POST", credentials: "same-origin" });
    return res.ok ? "/login" : "/login?logout=failed";
  } catch {
    return "/login?logout=failed";
  }
}

export function errorText(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.code === "validation_error") return validationText(err.details);
    return ERROR_MESSAGES[err.code] ?? err.message;
  }
  if (err instanceof Error) return err.message;
  return "Noma’lum xato";
}

/** 422 from the backend: name the offending fields (details[].loc, e.g. ["body", "caption"]). */
function validationText(details: unknown): string {
  const fields = new Set<string>();
  if (Array.isArray(details)) {
    for (const d of details) {
      const loc = (d as { loc?: unknown })?.loc;
      if (!Array.isArray(loc)) continue;
      const path = loc.filter((p, i) => !(i === 0 && ["body", "query", "path"].includes(String(p)))).join(".");
      if (path) fields.add(path);
    }
  }
  const base = "Ma’lumotlar noto‘g‘ri to‘ldirilgan";
  return fields.size ? `${base}: ${[...fields].join(", ")}.` : `${base}.`;
}

// User-friendly Uzbek messages for stable backend error codes.
const ERROR_MESSAGES: Record<string, string> = {
  version_mismatch: "Kontent siz ko‘rgandan keyin o‘zgargan. Sahifani yangilang va qayta ko‘rib chiqing.",
  invalid_state_transition: "Bu holatda bu amalni bajarib bo‘lmaydi.",
  approval_required: "Avval joriy versiyani tasdiqlash kerak.",
  approval_forbidden: "Tasdiqlash uchun OWNER yoki ADMIN roli kerak.",
  permission_denied: "Bu amal uchun ruxsatingiz yo‘q.",
  ai_provider_unavailable: "AI provayder (Ollama) ishlamayapti. `ollama serve` ni ishga tushiring.",
  ai_model_not_found: "AI modeli o‘rnatilmagan. `ollama pull qwen2.5:3b` buyrug‘ini bajaring.",
  four_eyes_required: "Bu versiyani o‘zingiz yozgansiz — uni boshqa OWNER yoki ADMIN tasdiqlashi kerak (to‘rt ko‘z qoidasi).",
  ai_provider_timeout: "AI javob berishga ulgurmadi. Keyinroq urinib ko‘ring yoki Celery rejimini yoqing.",
  ai_timeout: "AI javob berishga ulgurmadi. Keyinroq urinib ko‘ring yoki Celery rejimini yoqing.",
  ai_invalid_output: "AI noto‘g‘ri formatda javob qaytardi. Hech narsa saqlanmadi — qayta urinib ko‘ring.",
  too_many_requests: "Sizda allaqachon bir nechta AI vazifa bajarilmoqda. Biroz kuting.",
  language_not_supported: "Bu til brend profilida yoqilmagan.",
  backend_unreachable: "Backend bilan aloqa yo‘q. Server ishlayotganini tekshiring.",
  csrf_rejected: "So‘rov rad etildi (xavfsizlik tekshiruvi).",
  content_incomplete: "Ko‘rib chiqishga yuborishdan oldin caption yoki ssenariy yozing.",
  already_published: "Bu versiya allaqachon nashr qilingan.",
  publish_in_progress: "Nashr jarayoni allaqachon ketmoqda. Natijani kuting — qayta bosmang.",
  media_rejected: "Fayl qabul qilinmadi: faqat JPEG rasm yoki MP4/MOV video.",
  body_too_large: "Fayl juda katta.",
  rate_limited: "Juda ko‘p so‘rov. Biroz kuting va qayta urinib ko‘ring.",
  weak_password: "Parol talablarga javob bermaydi (kamida 12 belgi, e-mail nomisiz).",
  invalid_current_password: "Joriy parol noto‘g‘ri.",
};
