import { type NextRequest, NextResponse } from "next/server"

// Routes that are accessible without authentication
const PUBLIC_ROUTES = ["/login", "/api/v1/auth/login", "/api/v1/auth/refresh"]

// Routes that should redirect to login if already authenticated (optional: skip for now)
const AUTH_ROUTES = ["/login"]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Allow public routes
  if (PUBLIC_ROUTES.some((route) => pathname.startsWith(route))) {
    return NextResponse.next()
  }

  // Check for access token in cookies
  const accessToken = request.cookies.get("access_token")?.value

  if (!accessToken) {
    // Redirect to login page if no token
    const url = request.nextUrl.clone()
    url.pathname = "/login"
    url.searchParams.set("callbackUrl", pathname)
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
}
