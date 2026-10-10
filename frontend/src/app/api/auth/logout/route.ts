import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { SESSION_COOKIE, backendUrl, forwardedFor, isSameOrigin, jsonError } from "@/lib/server/session";

// Revokes the token server-side (so a copied cookie stops working), then clears the cookie.
// ?all=1 signs out every session of the user (all devices).
// The cookie is always cleared; if the revoke itself failed the response says so (502/503)
// so the UI can warn that the token may still be valid until it expires.
export async function POST(request: Request) {
  if (!isSameOrigin(request)) return jsonError(403, "csrf_rejected", "Cross-site request rejected");
  const token = (await cookies()).get(SESSION_COOKIE)?.value;
  const all = new URL(request.url).searchParams.get("all") === "1";
  let response: NextResponse = NextResponse.json({ ok: true });
  if (token) {
    try {
      const upstream = await fetch(`${backendUrl()}/api/v1/auth/${all ? "logout-all" : "logout"}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, ...forwardedFor(request) },
        cache: "no-store",
      });
      // 401: the token is already invalid (expired / revoked, e.g. after a password change).
      if (!upstream.ok && upstream.status !== 401) {
        response = NextResponse.json(
          { ok: false, error: { code: "logout_failed", message: "Sessiyani serverda bekor qilib bo‘lmadi" } },
          { status: 502 },
        );
      }
    } catch {
      // Backend unreachable: still clear the cookie locally; the token expires on its own.
      response = NextResponse.json(
        { ok: false, error: { code: "backend_unreachable", message: "Backend bilan aloqa yo‘q" } },
        { status: 503 },
      );
    }
  }
  response.cookies.delete(SESSION_COOKIE);
  return response;
}
