import { render, screen, waitFor } from "@testing-library/react"
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { NewAppointmentForm } from "@/components/appointments/new-appointment-form"

const API_BASE = "/api/v1"

const server = setupServer(
  http.post(`${API_BASE}/appointments`, async () => {
    return HttpResponse.json(
      {
        id: "apt-999",
        customer: "cust-001",
        professional: "prof-001",
        service: "svc-001",
        start_time: "2025-09-19T10:00:00Z",
        end_time: "2025-09-19T11:00:00Z",
        status: "agendado",
        notes: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
      { status: 201 }
    )
  })
)

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe("NewAppointmentForm", () => {
  it("renders form fields", () => {
    render(<NewAppointmentForm />)
    expect(screen.getByText("Novo Agendamento")).toBeInTheDocument()
    expect(screen.getByText("Preencha os dados do agendamento")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /criar agendamento/i })).toBeInTheDocument()
  })

  it("renders select triggers for cliente, profissional, service", () => {
    render(<NewAppointmentForm />)
    expect(screen.getByText("Selecione um cliente")).toBeInTheDocument()
    expect(screen.getByText("Selecione um profissional")).toBeInTheDocument()
    expect(screen.getByText("Selecione um serviço")).toBeInTheDocument()
  })

  it("renders datetime-local input for start_time", () => {
    render(<NewAppointmentForm />)
    const timeInput = document.querySelector('input[type="datetime-local"]')
    expect(timeInput).toBeInTheDocument()
  })

  it("renders notes textarea", () => {
    render(<NewAppointmentForm />)
    expect(screen.getByPlaceholderText("Observações sobre o agendamento...")).toBeInTheDocument()
  })
})
