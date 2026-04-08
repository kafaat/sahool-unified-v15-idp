import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const { pathname } = req.nextUrl;
  if (pathname.startsWith("/login")) {
    if (req.auth) return NextResponse.redirect(new URL("/", req.url));
    return NextResponse.next();
  }
  if (!req.auth) return NextResponse.redirect(new URL("/login", req.url));
  if (req.auth.user?.role !== "admin") {
    return NextResponse.json({ error: "Admin access required" }, { status: 403 });
  }
  return NextResponse.next();
});

export const config = { matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"] };
