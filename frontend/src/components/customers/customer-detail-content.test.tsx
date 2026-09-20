import { render, screen, waitFor } from "@testing-library/react"
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { CustomerDetailContent } from "@/components/customers/customer-detail-content"
import { customers, appointments } from "@/mocks/data"

const API_BASE = "/api/v1"

const server = setupServer(
  http.get(`${API_BASE}/customers/:id`, ({ params }) => {
    const customer = customers.find((c) => c.id === params.id)
    if (!customer) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json(customer)
  }),
  http.get(`${API_BASE}/customers/:id/appointments`, ({ params }) => {
    const customerAppointments = appointments.filter((a) => a.customer === params.id)
    return HttpResponse.json({
      count: customerAppointments.length,
      next: null,
      previous: null,
      results: customerAppointments,
    })
  }),
  http.get(`${API_BASE}/customers/:id/timeline`, () => {
    return HttpResponse.json({
      count: 0,
      next: null,
      previous: null,
      results: [],
    })
  })
)

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => ({ get: vi.fn(() => null), toString: vi.fn(() => "") }),
  notFound: vi.fn(),
}))

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe("CustomerDetailContent", () => {
  it("renders customer name as title", async () => {
    render(<CustomerDetailContent customerId="cust-001" />)
    await waitFor(() => {
      expect(screen.getByText("Daniela Souza")).toBeInTheDocument()
    })
  })

  it("renders customer contact info", async () => {
    render(<CustomerDetailContent customerId="cust-001" />)
    await waitFor(() => {
      expect(screen.getByText("(11) 95555-4444")).toBeInTheDocument()
    })
  })

  it("renders appointments section", async () => {
    render(<CustomerDetailContent customerId="cust-001" />)
    await waitFor(() => {
      expect(screen.getByText("Próximos Atendimentos")).toBeInTheDocument()
    })
  })

  it("renders timeline section", async () => {
    render(<CustomerDetailContent customerId="cust-001" />)
    await waitFor(() => {
      expect(screen.getByText("Histórico de Atividades")).toBeInTheDocument()
    })
  })
})
