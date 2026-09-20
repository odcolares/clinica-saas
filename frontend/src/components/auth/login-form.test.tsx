import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { LoginForm } from "@/components/auth/login-form"

const API_BASE = "/api/v1"

const server = setupServer(
  http.post(`${API_BASE}/auth/login`, async ({ request }) => {
    const body = await request.json()
    if ((body as { email: string }).email === "admin@clinica.com" && (body as { password: string }).password === "admin123") {
      return HttpResponse.json({
        access: "mock-access-token",
        refresh: "mock-refresh-token",
        user: {
          id: "user-1",
          email: "admin@clinica.com",
          name: "Admin User",
          role: "admin",
          tenant: "tenant-1",
        },
      })
    }
    return HttpResponse.json({ detail: "Credenciais inválidas" }, { status: 401 })
  })
)

const mockPush = vi.fn()

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}))

beforeAll(() => server.listen())
afterEach(() => {
  server.resetHandlers()
  mockPush.mockClear()
})
afterAll(() => server.close())

describe("LoginForm", () => {
  it("renders login form with email and password fields", () => {
    render(<LoginForm />)
    expect(screen.getByLabelText("E-mail")).toBeInTheDocument()
    expect(screen.getByLabelText("Senha")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /entrar/i })).toBeInTheDocument()
  })

  it("renders with pre-filled test credentials", () => {
    render(<LoginForm />)
    expect(screen.getByDisplayValue("admin@clinica.com")).toBeInTheDocument()
    expect(screen.getByDisplayValue("admin123")).toBeInTheDocument()
  })

  it("submits and redirects on successful login", async () => {
    render(<LoginForm />)

    fireEvent.click(screen.getByRole("button", { name: /entrar/i }))

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/dashboard")
    })
  })

  it("shows error on failed login", async () => {
    server.use(
      http.post(`${API_BASE}/auth/login`, () => {
        return HttpResponse.json({ detail: "Credenciais inválidas" }, { status: 401 })
      })
    )

    render(<LoginForm />)

    const emailInput = screen.getByLabelText("E-mail")
    const passwordInput = screen.getByLabelText("Senha")

    // Clear the pre-filled values
    fireEvent.change(emailInput, { target: { value: "wrong@email.com" } })
    fireEvent.change(passwordInput, { target: { value: "wrong" } })

    fireEvent.click(screen.getByRole("button", { name: /entrar/i }))

    await waitFor(() => {
      expect(screen.getByText("Credenciais inválidas")).toBeInTheDocument()
    })
    expect(mockPush).not.toHaveBeenCalled()
  })

  it("shows loading state during submission", async () => {
    render(<LoginForm />)

    const submitButton = screen.getByRole("button", { name: /entrar/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(submitButton).toBeDisabled()
    })
  })
})
