import "server-only";

import { backendUrl, jsonError } from "@/lib/server/session";

const MAX_BODY = 8_000;

/**
 * Meta's servers POST `signed_request` (form-encoded) here. There is no session and no
 * CSRF check: authenticity is the HMAC signature, which the backend verifies with the
 * app secret. Only the `signed_request` field is forwarded.
 */
export async function forwardSignedRequest(request: Request, path: string): Promise<Response> {
  const raw = await request.text();
  if (raw.length > MAX_BODY) return jsonError(413, "body_too_large", "Request body too large");
  const signed = new URLSearchParams(raw).get("signed_request");
  if (!signed) return jsonError(400, "invalid_signed_request", "signed_request is required");
  try {
    const upstream = await fetch(`${backendUrl()}/api/v1/instagram/meta/${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
      body: new URLSearchParams({ signed_request: signed }).toString(),
      cache: "no-store",
    });
    return new Response(await upstream.text(), {
      status: upstream.status,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
    });
  } catch {
    return jsonError(503, "backend_unreachable", "Backend unreachable");
  }
}
