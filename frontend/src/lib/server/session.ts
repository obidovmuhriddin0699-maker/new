import "server-only";

// Server-side only. The browser never sees the backend URL or the JWT.
export const SESSION_COOKIE = "mx_session";

export function backendUrl(): string {
  return (process.env.BACKEND_URL ?? "http://localhost:8000").replace(/\/$/, "");
}

/** Secure cookies on HTTPS (or when forced); plain HTTP stays usable for LAN/mobile dev. */
export function cookieSecure(request: Request): boolean {
  const mode = process.env.SESSION_COOKIE_SECURE ?? "auto";
  if (mode === "true") return true;
  if (mode === "false") return false;
  const proto = request.headers.get("x-forwarded-proto") ?? new URL(request.url).protocol;
  return proto.replace(":", "") === "https";
}

/** CSRF defence for state-changing requests: same-origin only. */
export function isSameOrigin(request: Request): boolean {
  const site = request.headers.get("sec-fetch-site");
  if (site && site !== "same-origin" && site !== "none") return false;
  const origin = request.headers.get("origin");
  if (!origin) return false;
  const host = request.headers.get("x-forwarded-host") ?? request.headers.get("host");
  try {
    return new URL(origin).host === host;
  } catch {
    return false;
  }
}

export function jsonError(status: number, code: string, message: string): Response {
  return Response.json({ error: { code, message } }, { status });
}

/**
 * Client address for the backend's rate limiter. Forwarded only when a reverse proxy in
 * front of Next.js sets X-Forwarded-For (TRUST_PROXY_HEADERS=true); otherwise a browser
 * could spoof it, so nothing is forwarded and the backend sees this server's address.
 */
export function forwardedFor(request: Request): Record<string, string> {
  if (process.env.TRUST_PROXY_HEADERS !== "true") return {};
  const xff = request.headers.get("x-forwarded-for") ?? request.headers.get("x-real-ip");
  return xff ? { "X-Forwarded-For": xff.slice(0, 200) } : {};
}
