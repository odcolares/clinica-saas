import { render, screen, waitFor, cleanup, fireEvent } from "@testing-library/react"
import { describe, it, expect, beforeAll, beforeEach, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { SWRConfig, mutate } from "swr"
import { ProfessionalForm } from "@/components/professionals/professional-form"
import { professionals } from "@/mocks/data"

const API_BASE = "/api/v1"
const PROFESSIONALS_KEY = `${API_BASE}/professionals`

// Mock ResizeObserver for components that use it (Select, etc.)
beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver
})

const server = setupServer(
  http.get(`${API_BASE}/professionals`, () => {
    return HttpResponse.json(professionals)
  }),
  http.post(`${API_BASE}/professionals`, async ({ request }) => {
    const body = await request.json()
    const newProf = {
      id: "prof-new",
      ...body,
      commission_type: body.commission_type ?? "none",
      commission_percent: body.commission_percent ?? 0,
      commission_fixed: body.commission_fixed ?? 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    return HttpResponse.json(newProf, { status: 201 })
  }),
  http.patch(`${API_BASE}/professionals/:id`, async ({ params, request }) => {
    const existing = professionals.find((p) => p.id === params.id)
    if (!existing) return HttpResponse.json({ detail: "Not found" }, { status: 404 })
    const body = await request.json()
    return HttpResponse.json({ ...existing, ...body })
  }),
)

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

beforeAll(() => server.listen())
beforeEach(() => {
  mutate(PROFESSIONALS_KEY, undefined, { populateCache: false })
})
afterEach(() => {
  server.resetHandlers()
  cleanup()
  mutate(PROFESSIONALS_KEY, undefined, { populateCache: false })
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

describe("ProfessionalForm", () => {
  it("renders form for new professional", () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <ProfessionalForm />
      </SWRConfig>
    )
    expect(screen.getByText("Novo Profissional")).toBeInTheDocument()
    expect(screen.getByPlaceholderText("Nome completo")).toBeInTheDocument()
  })

  it("renders form for editing existing professional", () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <ProfessionalForm professional={professionals[0]} />
      </SWRConfig>
    )
    expect(screen.getByText("Editar Profissional")).toBeInTheDocument()
    expect(screen.getByDisplayValue(professionals[0].name)).toBeInTheDocument()
  })

  it("renders commission type options", () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <ProfessionalForm />
      </SWRConfig>
    )

    expect(screen.getByText("Tipo de Comissão")).toBeInTheDocument()
  })

  it("shows commission fields when percent type is selected", async () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <ProfessionalForm />
      </SWRConfig>
    )

    const commissionSelect = screen.getByRole("combobox")
    fireEvent.mouseDown(commissionSelect)

    await waitFor(() => {
      expect(screen.getByText("Percentual (%)")).toBeInTheDocument()
    })
  })
})
