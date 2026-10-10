import { NextResponse, type NextRequest } from "next/server";

const SESSION_COOKIE = "mx_session";
// Meta redirects here cross-site, so the SameSite=Strict session cookie is not sent on
// this navigation. The page itself finishes the flow with a same-origin request (which
// does carry the cookie) and sends the user to /login if that request is unauthenticated.
const PUBLIC_PATHS = new Set(["/instagram/callback", "/privacy", "/terms"]);
// /media/<random-name>: uploaded post media that Meta's servers download (no session).

// Cheap presence check only; the backend validates the token on every API call
// and the proxy clears the cookie when the backend answers 401.
export function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const hasSession = Boolean(request.cookies.get(SESSION_COOKIE)?.value);

  if (pathname === "/login") {
    if (hasSession) return NextResponse.redirect(new URL("/overview", request.url));
    return NextResponse.next();
  }
  if (PUBLIC_PATHS.has(pathname) || pathname.startsWith("/media/")) return NextResponse.next();
  if (!hasSession) {
    const url = new URL("/login", request.url);
    if (pathname !== "/") url.searchParams.set("next", pathname + search);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api/|_next/|favicon.ico|robots.txt).*)"],
};
