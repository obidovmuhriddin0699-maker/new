import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { SESSION_COOKIE, backendUrl, isSameOrigin, jsonError } from "@/lib/server/session";

// Revokes the token server-side (so a copied cookie stops working), then clears the cookie.
// ?all=1 signs out every session of the user (all devices).
export async function POST(request: Request) {
  if (!isSameOrigin(request)) return jsonError(403, "csrf_rejected", "Cross-site request rejected");
  const token = (await cookies()).get(SESSION_COOKIE)?.value;
  const all = new URL(request.url).searchParams.get("all") === "1";
  if (token) {
    try {
      await fetch(`${backendUrl()}/api/v1/auth/${all ? "logout-all" : "logout"}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
    } catch {
      // Backend unreachable: still clear the cookie locally; the token expires on its own.
    }
  }
  const response = NextResponse.json({ ok: true });
  response.cookies.delete(SESSION_COOKIE);
  return response;
}
