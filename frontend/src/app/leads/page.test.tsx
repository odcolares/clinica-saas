import { render, screen, waitFor } from "@testing-library/react"
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import LeadsListPage from "./page"
import { leads } from "@/mocks/data"

const API_BASE = "/api/v1"

const server = setupServer(
  http.get(`${API_BASE}/leads`, () => {
    return HttpResponse.json({
      count: leads.length,
      next: null,
      previous: null,
      results: leads,
    })
  })
)

const mockRouterPush = vi.fn()
const mockSearchParams = {
  get: vi.fn(() => null),
  toString: vi.fn(() => ""),
}

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockRouterPush,
  }),
  useSearchParams: () => mockSearchParams,
}))

beforeAll(() => server.listen())
afterEach(() => {
  server.resetHandlers()
  mockRouterPush.mockClear()
  mockSearchParams.get.mockClear()
  mockSearchParams.toString.mockClear()
})
afterAll(() => server.close())

describe("LeadsListPage", () => {
  it("renders the page title", () => {
    render(<LeadsListPage />)
    expect(screen.getByText("Leads")).toBeInTheDocument()
  })

  it("renders leads from the API", async () => {
    render(<LeadsListPage />)
    await waitFor(() => {
      expect(screen.getAllByText("Ana Silva")[0]).toBeInTheDocument()
      expect(screen.getAllByText("Carlos Mendes")[0]).toBeInTheDocument()
    })
  })

  it("renders filter controls", () => {
    render(<LeadsListPage />)
    expect(screen.getByPlaceholderText("Buscar por nome ou e-mail...")).toBeInTheDocument()
    expect(screen.getByText("Todos os status")).toBeInTheDocument()
    expect(screen.getByText("Todas as origens")).toBeInTheDocument()
  })
})
