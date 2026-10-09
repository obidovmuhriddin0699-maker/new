import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { SESSION_COOKIE, backendUrl, isSameOrigin, jsonError } from "@/lib/server/session";

// Backend-for-frontend proxy: /api/backend/<path> -> BACKEND_URL/api/v1/<path>
// The JWT stays in an httpOnly cookie and is attached here, server-side.
const SEGMENT = /^[A-Za-z0-9_.-]+$/;
const BLOCKED = new Set(["auth/login"]); // must go through /api/auth/login (keeps token server-side)
const MAX_BODY = 1_000_000;

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
  const headers: Record<string, string> = { Accept: "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const requestId = request.headers.get("x-request-id");
  if (requestId) headers["X-Request-ID"] = requestId.slice(0, 64);

  let body: string | undefined;
  if (mutating) {
    body = await request.text();
    if (body.length > MAX_BODY) return jsonError(413, "body_too_large", "Request body too large");
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
  for (const h of ["content-type", "x-request-id"]) {
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
