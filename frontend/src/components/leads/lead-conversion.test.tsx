import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { LeadConversion } from "@/components/leads/lead-conversion"
import { leads } from "@/mocks/data"

const API_BASE = "/api/v1"

const server = setupServer(
  http.post(`${API_BASE}/leads/:id/convert`, ({ params }) => {
    const lead = leads.find((l) => l.id === params.id)
    if (!lead) return new HttpResponse(null, { status: 404 })
    return HttpResponse.json({
      id: "cust-999",
      lead_id: lead.id,
      name: lead.name,
      email: lead.email,
      phone: lead.phone,
      document: null,
      birth_date: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })
  })
)

const mockPush = vi.fn()
const mockOnConverted = vi.fn()

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}))

beforeAll(() => server.listen())
afterEach(() => {
  server.resetHandlers()
  mockPush.mockClear()
  mockOnConverted.mockClear()
})
afterAll(() => server.close())

const testLead = leads.find((l) => l.id === "lead-001")!

describe("LeadConversion", () => {
  it("renders trigger button", () => {
    render(<LeadConversion lead={testLead} />)
    expect(screen.getByText("Converter para Cliente")).toBeInTheDocument()
  })

  it("opens dialog when trigger clicked", async () => {
    render(<LeadConversion lead={testLead} />)
    fireEvent.click(screen.getByText("Converter para Cliente"))

    await waitFor(() => {
      expect(screen.getByText("Converter Lead para Cliente")).toBeInTheDocument()
    })
  })

  it("shows lead details in dialog", async () => {
    render(<LeadConversion lead={testLead} />)
    fireEvent.click(screen.getByText("Converter para Cliente"))

    await waitFor(() => {
      expect(screen.getByText(testLead.name)).toBeInTheDocument()
    })
  })

  it("converts lead and redirects to customer page", async () => {
    render(<LeadConversion lead={testLead} onConverted={mockOnConverted} />)
    fireEvent.click(screen.getByText("Converter para Cliente"))

    await waitFor(() => {
      expect(screen.getByText("Confirmar Conversão")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Confirmar Conversão"))

    await waitFor(() => {
      expect(screen.getByText(/Cliente criado com sucesso/)).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(mockOnConverted).toHaveBeenCalled()
    })

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith("/customers/cust-999")
    })
  })

  it("shows error message on conversion failure", async () => {
    server.use(
      http.post(`${API_BASE}/leads/:id/convert`, () => {
        return new HttpResponse(null, { status: 500 })
      })
    )

    render(<LeadConversion lead={testLead} />)
    fireEvent.click(screen.getByText("Converter para Cliente"))

    await waitFor(() => {
      expect(screen.getByText("Confirmar Conversão")).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText("Confirmar Conversão"))

    await waitFor(() => {
      expect(screen.getByText(/Não foi possível converter/)).toBeInTheDocument()
    })
  })
})
