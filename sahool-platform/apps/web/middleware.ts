import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";

const PUBLIC_PATHS = ["/login", "/register", "/api/", "/_next/", "/favicon"];

function isPublic(pathname: string): boolean {
  return PUBLIC_PATHS.some((p) => pathname.startsWith(p));
}

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  if (isPublic(pathname)) {
    // Already-authenticated users hitting /login or /register → redirect to dashboard
    if (pathname === "/login" || pathname === "/register") {
      const token = req.cookies.get("access_token")?.value;
      if (token && process.env.JWT_SECRET_KEY) {
        try {
          await jwtVerify(
            token,
            new TextEncoder().encode(process.env.JWT_SECRET_KEY)
          );
          return NextResponse.redirect(new URL("/dashboard", req.url));
        } catch {
          // invalid token — let them through to login
        }
      }
    }
    return NextResponse.next();
  }

  // Protected route — verify access token from cookie
  const token = req.cookies.get("access_token")?.value;

  if (!token) {
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  const secret = process.env.JWT_SECRET_KEY;
  if (!secret) {
    // Misconfigured — fail open in dev, fail closed would be safer in prod
    console.error("[middleware] JWT_SECRET_KEY not set");
    return NextResponse.next();
  }

  try {
    const { payload } = await jwtVerify(token, new TextEncoder().encode(secret));

    // Admin-only routes
    if (pathname.startsWith("/admin") && payload["role"] !== "admin") {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }

    return NextResponse.next();
  } catch {
    // Token invalid or expired — redirect to login for silent refresh
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths EXCEPT:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
