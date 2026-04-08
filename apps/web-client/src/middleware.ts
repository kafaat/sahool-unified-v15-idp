import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const { pathname } = req.nextUrl;
  const isAuthed = !!req.auth;

  // Public routes
  if (pathname.startsWith("/login") || pathname.startsWith("/register")) {
    if (isAuthed) return NextResponse.redirect(new URL("/fields", req.url));
    return NextResponse.next();
  }

  // Everything else requires auth
  if (!isAuthed) {
    return NextResponse.redirect(new URL(`/login?callbackUrl=${encodeURIComponent(pathname)}`, req.url));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
