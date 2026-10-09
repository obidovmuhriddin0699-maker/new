import { NextResponse, type NextRequest } from "next/server";

const SESSION_COOKIE = "mx_session";

// Cheap presence check only; the backend validates the token on every API call
// and the proxy clears the cookie when the backend answers 401.
export function middleware(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const hasSession = Boolean(request.cookies.get(SESSION_COOKIE)?.value);

  if (pathname === "/login") {
    if (hasSession) return NextResponse.redirect(new URL("/overview", request.url));
    return NextResponse.next();
  }
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
