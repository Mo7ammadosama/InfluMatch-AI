import { NextRequest, NextResponse } from "next/server";
import { decodeJwt } from "jose";

const PUBLIC_PATHS = ["/", "/login", "/register"];

const ROLE_PATHS: Record<string, string[]> = {
  merchant: ["/merchant"],
  influencer: ["/influencer", "/open-campaigns"],
  admin: ["/admin"],
  creative_strategist: ["/creative-strategist"],
};

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Always allow public paths and Next.js internals
  if (PUBLIC_PATHS.includes(pathname)) return NextResponse.next();
  if (pathname.startsWith("/_next") || pathname.startsWith("/api/")) {
    return NextResponse.next();
  }

  const token = req.cookies.get("waslai_token")?.value;

  if (!token) {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  try {
    // Decode without verification — backend enforces signature on every API call
    const payload = decodeJwt(token);
    const role = payload.role as string;

    // Block cross-role routes
    for (const [r, paths] of Object.entries(ROLE_PATHS)) {
      if (r !== role && paths.some((p) => pathname.startsWith(p))) {
        return NextResponse.redirect(new URL("/dashboard", req.url));
      }
    }

    const res = NextResponse.next();
    res.headers.set("x-user-role", role);
    res.headers.set("x-user-id", String(payload.sub));
    return res;
  } catch {
    // Token malformed — clear and redirect
    const res = NextResponse.redirect(new URL("/login", req.url));
    res.cookies.delete("waslai_token");
    return res;
  }
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
