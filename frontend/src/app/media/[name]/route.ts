import { backendUrl, forwardedFor } from "@/lib/server/session";

const NAME = /^[A-Za-z0-9_-]{20,64}\.(jpg|mp4|mov)$/;

// Public media for Meta's servers: {PANEL_PUBLIC_URL}/media/<name> -> backend file route.
// Streams the body; supports Range for video players.
export async function GET(request: Request, ctx: { params: Promise<{ name: string }> }): Promise<Response> {
  const { name } = await ctx.params;
  if (!NAME.test(name)) return new Response("Not found", { status: 404 });
  // Own rate-limit bucket per client, not one shared by every visitor of this server.
  const headers: Record<string, string> = { ...forwardedFor(request) };
  const range = request.headers.get("range");
  if (range) headers.Range = range;
  let upstream: Response;
  try {
    upstream = await fetch(`${backendUrl()}/api/v1/media/${name}`, { headers, cache: "no-store" });
  } catch {
    return new Response("Backend unreachable", { status: 503 });
  }
  if (!upstream.ok && upstream.status !== 206) return new Response("Not found", { status: 404 });
  const out = new Headers();
  for (const h of ["content-type", "content-length", "content-range", "accept-ranges", "etag", "last-modified"]) {
    const v = upstream.headers.get(h);
    if (v) out.set(h, v);
  }
  out.set("Cache-Control", "public, max-age=86400");
  out.set("X-Content-Type-Options", "nosniff");
  return new Response(upstream.body, { status: upstream.status, headers: out });
}
