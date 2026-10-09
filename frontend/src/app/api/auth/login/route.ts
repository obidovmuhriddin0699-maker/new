import { NextResponse } from "next/server";

import { SESSION_COOKIE, backendUrl, cookieSecure, forwardedFor, isSameOrigin, jsonError } from "@/lib/server/session";

export async function POST(request: Request) {
  if (!isSameOrigin(request)) return jsonError(403, "csrf_rejected", "Cross-site request rejected");
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return jsonError(400, "invalid_body", "Invalid JSON body");
  }
  let upstream: Response;
  try {
    upstream = await fetch(`${backendUrl()}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...forwardedFor(request) },
      body: JSON.stringify(body),
      cache: "no-store",
    });
  } catch {
    return jsonError(503, "backend_unreachable", "Backend bilan aloqa yo‘q");
  }
  const data = await upstream.json().catch(() => ({}));
  if (!upstream.ok) {
    const retry = upstream.headers.get("retry-after");
    return NextResponse.json(data, { status: upstream.status, headers: retry ? { "Retry-After": retry } : undefined });
  }

  const response = NextResponse.json({ ok: true, expires_in: data.expires_in });
  response.cookies.set(SESSION_COOKIE, data.access_token, {
    httpOnly: true,
    sameSite: "strict",
    secure: cookieSecure(request),
    path: "/",
    maxAge: Number(data.expires_in) || 1800,
  });
  return response;
}
