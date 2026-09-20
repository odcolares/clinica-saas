import { cookies } from "next/headers"
import { LoginRequest, LoginResponse } from "@/types/api"
import { redirect } from "next/navigation"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || ""

export async function login(loginData: LoginRequest): Promise<{ error?: string }> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(loginData),
    })

    if (!res.ok) {
      const error = await res.json()
      return { error: error.detail || "Credenciais inválidas" }
    }

    const data: LoginResponse = await res.json()

    const cookieStore = await cookies()
    cookieStore.set("access_token", data.access, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: "/",
      sameSite: "lax",
    })
    cookieStore.set("refresh_token", data.refresh, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60 * 24 * 30, // 30 days
      path: "/",
      sameSite: "lax",
    })

    redirect("/dashboard")
  } catch (err) {
    return { error: "Falha na conexão" }
  }
}

export async function logout() {
  const cookieStore = await cookies()
  cookieStore.delete("access_token")
  cookieStore.delete("refresh_token")
  redirect("/login")
}

export async function getUser(): Promise<LoginResponse["user"] | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
      method: "GET",
      credentials: "include",
      next: { tags: ["auth"] },
    })

    if (!res.ok) return null

    const data = await res.json()
    return data.user
  } catch {
    return null
  }
}
