import { render, screen } from "@testing-library/react"
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { AgentStatusBadge } from "@/components/omnichannel/agent-status-badge"

const API_BASE = "/api/v1"

const server = setupServer(
  http.get(`${API_BASE}/auth/me`, () => {
    return HttpResponse.json({ detail: "Não autenticado" }, { status: 401 })
  }),
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

describe("AgentStatusBadge", () => {
  it("renders Offline when not authenticated", async () => {
    render(<AgentStatusBadge />)
    expect(await screen.findByText("Offline")).toBeInTheDocument()
  })

  it("renders Online when authenticated", async () => {
    server.use(
      http.get(`${API_BASE}/auth/me`, () => {
        return HttpResponse.json({
          user: { id: "u1", email: "a@b.com", name: "A", role: "admin", tenant: "t1" },
          access: "access",
          refresh: "refresh",
        })
      }),
    )
    render(<AgentStatusBadge />)
    expect(await screen.findByText("Online")).toBeInTheDocument()
  })
})