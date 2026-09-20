import useSWR, { mutate } from "swr"
import { swrConfig, fetcher } from "@/lib/swr-config"
import { useRouter } from "next/navigation"
import type { LoginRequest, LoginResponse, User, RefreshRequest } from "@/types/api"

export function useAuth() {
  const router = useRouter()

  const { data, error, isLoading, isValidating } = useSWR<{
    user: User
    access: string
    refresh: string
  }>(
    "/api/v1/auth/me",
    (url: string) =>
      fetch(url).then((res) => {
        if (!res.ok) throw new Error("Não autenticado")
        return res.json()
      }),
    {
      ...swrConfig,
      revalidateOnMount: true,
      shouldRetryOnError: false,
    }
  )

  const isAuthenticated = !!data && !error
  const isLoadingAuth = isLoading || isValidating

  async function login(values: LoginRequest): Promise<void> {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.detail || "Credenciais inválidas")
    }

    const response = await res.json() as LoginResponse

    document.cookie = `access_token=${response.access}; path=/; max-age=604800; SameSite=Lax`
    document.cookie = `refresh_token=${response.refresh}; path=/; max-age=2592000; SameSite=Lax`

    mutate("/api/v1/auth/me")
    router.push("/dashboard")
  }

  async function logout(): Promise<void> {
    await fetch("/api/v1/auth/logout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })

    document.cookie = "access_token=; path=/; max-age=0"
    document.cookie = "refresh_token=; path=/; max-age=0"

    mutate("/api/v1/auth/me")
    router.push("/login")
  }

  async function refreshAccessToken(refreshToken: string): Promise<LoginResponse> {
    const res = await fetch("/api/v1/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken } as RefreshRequest),
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.detail || "Token inválido")
    }

    return await res.json() as LoginResponse
  }

  return {
    user: data?.user,
    isAuthenticated,
    isLoading: isLoadingAuth,
    isError: !!error,
    error,
    login,
    logout,
    refreshAccessToken,
    refetch: () => mutate("/api/v1/auth/me"),
  }
}
