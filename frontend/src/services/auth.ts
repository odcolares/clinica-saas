import apiClient from "./api"
import type { LoginRequest, LoginResponse, RefreshRequest } from "@/types/api"

export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>("/auth/login", data)
    return response.data
  },

  async logout(): Promise<void> {
    await apiClient.post("/auth/logout")
  },

  async refreshToken(data: RefreshRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>("/auth/refresh", data)
    return response.data
  },

  async passwordReset(email: string): Promise<void> {
    await apiClient.post("/auth/password-reset", { email })
  },

  async emailVerification(token: string): Promise<void> {
    await apiClient.post("/auth/email-verification", { token })
  },
}
