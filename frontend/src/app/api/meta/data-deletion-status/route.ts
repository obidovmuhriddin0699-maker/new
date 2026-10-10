import { backendUrl, forwardedFor, jsonError } from "@/lib/server/session";

const CODE = /^[A-Za-z0-9_-]{6,64}$/;

// Public status page for a data deletion request (the `url` returned to Meta).
export async function GET(request: Request): Promise<Response> {
  const code = new URL(request.url).searchParams.get("code") ?? "";
  if (!CODE.test(code)) return jsonError(400, "invalid_code", "Invalid confirmation code");
  try {
    const upstream = await fetch(`${backendUrl()}/api/v1/instagram/meta/data-deletion/${code}`, {
      headers: { Accept: "application/json", ...forwardedFor(request) },
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
