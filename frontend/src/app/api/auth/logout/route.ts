import { NextResponse } from "next/server";

import { SESSION_COOKIE, isSameOrigin, jsonError } from "@/lib/server/session";

export async function POST(request: Request) {
  if (!isSameOrigin(request)) return jsonError(403, "csrf_rejected", "Cross-site request rejected");
  const response = NextResponse.json({ ok: true });
  response.cookies.delete(SESSION_COOKIE);
  return response;
}
