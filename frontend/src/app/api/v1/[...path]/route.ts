import { NextRequest, NextResponse } from "next/server"

const API_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
)
  .trim()
  .replace(/\/+$/, "")

const FORWARDED_HEADERS = [
  "content-type",
  "authorization",
  "x-tenant-id",
  "cookie",
]

async function proxy(req: NextRequest, path: string[]) {
  const search = req.nextUrl.search || ""
  const target = `${API_URL}/${path.join("/")}/${search}`
  const headers = new Headers()
  for (const name of FORWARDED_HEADERS) {
    const value = req.headers.get(name)
    if (value) headers.set(name, value)
  }
  const hasBody = req.method !== "GET" && req.method !== "HEAD"
  const upstream = await fetch(target, {
    method: req.method,
    headers,
    body: hasBody ? await req.arrayBuffer() : undefined,
  })
  const outHeaders = new Headers()
  const contentType = upstream.headers.get("content-type")
  if (contentType) outHeaders.set("content-type", contentType)
  return new NextResponse(await upstream.arrayBuffer(), {
    status: upstream.status,
    headers: outHeaders,
  })
}

type Ctx = { params: Promise<{ path: string[] }> }

export async function GET(req: NextRequest, ctx: Ctx) {
  return proxy(req, (await ctx.params).path)
}

export async function POST(req: NextRequest, ctx: Ctx) {
  return proxy(req, (await ctx.params).path)
}

export async function PUT(req: NextRequest, ctx: Ctx) {
  return proxy(req, (await ctx.params).path)
}

export async function PATCH(req: NextRequest, ctx: Ctx) {
  return proxy(req, (await ctx.params).path)
}

export async function DELETE(req: NextRequest, ctx: Ctx) {
  return proxy(req, (await ctx.params).path)
}
