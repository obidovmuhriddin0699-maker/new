import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { SESSION_COOKIE, backendUrl, forwardedFor, isSameOrigin, jsonError, readBodyLimited } from "@/lib/server/session";

// Backend-for-frontend proxy: /api/backend/<path> -> BACKEND_URL/api/v1/<path>
// The JWT stays in an httpOnly cookie and is attached here, server-side.
const SEGMENT = /^[A-Za-z0-9_.-]+$/;
// auth/login|logout* must go through /api/auth/* (keeps the token server-side, clears the cookie).
const BLOCKED = new Set(["auth/login", "auth/logout", "auth/logout-all"]);
// Backend routes that work without a session (everything else is refused here, before the
// body is read, so anonymous clients cannot make this server buffer large uploads).
const PUBLIC = new Set(["health"]);
const MAX_BODY = 1_000_000;
// Raw media uploads (JPEG / MP4 / MOV); the backend validates bytes and size again.
const UPLOAD_PATH = /^contents\/\d+\/assets\/upload$/;
const MAX_UPLOAD = 110 * 1024 * 1024;

type Ctx = { params: Promise<{ path: string[] }> };

async function proxy(request: Request, ctx: Ctx): Promise<Response> {
  const { path } = await ctx.params;
  if (!path.length || path.some((s) => !SEGMENT.test(s) || s === "." || s === "..")) {
    return jsonError(400, "invalid_path", "Invalid API path");
  }
  const joined = path.join("/");
  if (BLOCKED.has(joined)) return jsonError(404, "not_found", "Not found");

  const method = request.method.toUpperCase();
  const mutating = !["GET", "HEAD"].includes(method);
  if (mutating && !isSameOrigin(request)) {
    return jsonError(403, "csrf_rejected", "Cross-site request rejected");
  }

  const token = (await cookies()).get(SESSION_COOKIE)?.value;
  if (!token && !PUBLIC.has(joined)) return jsonError(401, "unauthenticated", "Sessiya tugagan, qayta kiring");
  const headers: Record<string, string> = { Accept: "application/json", ...forwardedFor(request) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const requestId = request.headers.get("x-request-id");
  if (requestId) headers["X-Request-ID"] = requestId.slice(0, 64);

  // Bytes are counted while streaming; the read stops as soon as the limit is passed.
  let body: Uint8Array<ArrayBuffer> | undefined;
  if (mutating && method === "POST" && UPLOAD_PATH.test(joined)) {
    const read = await readBodyLimited(request, MAX_UPLOAD);
    if (!read) return jsonError(413, "body_too_large", "Fayl juda katta");
    body = read;
    headers["Content-Type"] = "application/octet-stream";
  } else if (mutating) {
    const read = await readBodyLimited(request, MAX_BODY);
    if (!read) return jsonError(413, "body_too_large", "Request body too large");
    body = read;
    headers["Content-Type"] = "application/json";
  }

  const search = new URL(request.url).search;
  let upstream: Response;
  try {
    upstream = await fetch(`${backendUrl()}/api/v1/${joined}${search}`, {
      method,
      headers,
      body,
      cache: "no-store",
    });
  } catch {
    return jsonError(503, "backend_unreachable", "Backend bilan aloqa yo‘q");
  }

  const outHeaders = new Headers();
  for (const h of ["content-type", "x-request-id", "retry-after"]) {
    const v = upstream.headers.get(h);
    if (v) outHeaders.set(h, v);
  }
  outHeaders.set("Cache-Control", "no-store");
  const payload = upstream.status === 204 ? null : await upstream.arrayBuffer();
  const response = new NextResponse(payload, { status: upstream.status, headers: outHeaders });
  if (upstream.status === 401) response.cookies.delete(SESSION_COOKIE); // expired / invalid session
  return response;
}

export { proxy as GET, proxy as POST, proxy as PATCH, proxy as PUT, proxy as DELETE };
