import { render, screen, waitFor, cleanup } from "@testing-library/react"
import { describe, it, expect, beforeAll, beforeEach, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { SWRConfig, mutate } from "swr"
import { ProfessionalDirectory } from "@/components/professionals/professional-directory"
import { professionals } from "@/mocks/data"

const API_BASE = "/api/v1"
const SWEET_PROFESSIONALS_KEY = `${API_BASE}/professionals`

const server = setupServer(
  http.get(`${API_BASE}/professionals`, () => {
    return HttpResponse.json(professionals)
  })
)

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

beforeAll(() => server.listen())
beforeEach(() => {
  mutate(SWEET_PROFESSIONALS_KEY, undefined, { populateCache: false })
})
afterEach(() => {
  server.resetHandlers()
  cleanup()
  mutate(SWEET_PROFESSIONALS_KEY, undefined, { populateCache: false })
})
afterAll(() => server.close())

const swrTestConfig = {
  dedupingInterval: 0,
  revalidateOnMount: true,
  revalidateOnFocus: false,
  revalidateOnReconnect: false,
  shouldRetryOnError: false,
  errorRetryCount: 0,
}

describe("ProfessionalDirectory", () => {
  it("renders directory title", async () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <ProfessionalDirectory />
      </SWRConfig>
    )
    await waitFor(() => {
      expect(screen.getByText("Profissionais")).toBeInTheDocument()
    })
  })

  it("renders search input", async () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <ProfessionalDirectory />
      </SWRConfig>
    )
    expect(screen.getByPlaceholderText("Buscar profissionais...")).toBeInTheDocument()
  })

  it("renders professionals", async () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <ProfessionalDirectory />
      </SWRConfig>
    )

    await waitFor(() => {
      expect(screen.getAllByText(professionals[0].name).length).toBeGreaterThan(0)
    })
  })

  it("shows error state on API failure", async () => {
    server.use(
      http.get(`${API_BASE}/professionals`, () => {
        return HttpResponse.json({ detail: "Server Error" }, { status: 500 })
      })
    )

    render(
      <SWRConfig value={swrTestConfig}>
        <ProfessionalDirectory />
      </SWRConfig>
    )

    await waitFor(
      () => {
        expect(screen.getAllByText("Erro ao carregar profissionais").length).toBe(1)
      },
      { timeout: 10000 }
    )
  }, 15000)
})
