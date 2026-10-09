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

/**
 * Reads a request body as a stream, counting bytes, and gives up as soon as it exceeds
 * `limit` (returns null) — an oversized body is never buffered in full. A declared
 * Content-Length above the limit is refused before reading anything.
 */
export async function readBodyLimited(request: Request, limit: number): Promise<Uint8Array<ArrayBuffer> | null> {
  const declared = Number(request.headers.get("content-length") ?? "0");
  if (Number.isFinite(declared) && declared > limit) return null;
  if (!request.body) return new Uint8Array(0);
  const reader = request.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > limit) {
      await reader.cancel().catch(() => undefined);
      return null;
    }
    chunks.push(value);
  }
  const out = new Uint8Array(size);
  let offset = 0;
  for (const c of chunks) {
    out.set(c, offset);
    offset += c.byteLength;
  }
  return out;
}
