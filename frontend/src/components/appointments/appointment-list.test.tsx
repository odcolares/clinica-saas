import { render, screen, waitFor } from "@testing-library/react"
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { mutate } from "swr"
import { AppointmentList } from "@/components/appointments/appointment-list"
import { appointments, professionals, services } from "@/mocks/data"

const API_BASE = "/api/v1"

vi.mock("@/lib/swr-config", () => ({
  swrConfig: {
    dedupingInterval: 0,
    revalidateOnMount: true,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    shouldRetryOnError: false,
    errorRetryCount: 0,
  },
  fetcher: (url: string) => fetch(url).then((res) => {
    if (!res.ok) {
      throw new Error(`Erro ao carregar dados: ${res.status}`)
    }
    return res.json()
  }),
}))

const server = setupServer(
  http.get(`${API_BASE}/appointments`, () => {
    return HttpResponse.json({
      count: appointments.length,
      next: null,
      previous: null,
      results: appointments,
    })
  }),
  http.get(`${API_BASE}/professionals`, () => {
    return HttpResponse.json(professionals)
  }),
  http.get(`${API_BASE}/services`, () => {
    return HttpResponse.json(services)
  })
)

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

beforeAll(() => server.listen())
afterEach(() => {
  server.resetHandlers()
  mutate(`${API_BASE}/appointments`, undefined, { populateCache: false })
  mutate(`${API_BASE}/professionals`, undefined, { populateCache: false })
  mutate(`${API_BASE}/services`, undefined, { populateCache: false })
})
afterAll(() => server.close())

describe("AppointmentList", () => {
  it("renders loading state initially", async () => {
    render(<AppointmentList />)
    expect(screen.getByText("Carregando agendamentos...")).toBeInTheDocument()
  })

  it("renders appointment service names after data is loaded", async () => {
    render(<AppointmentList />)

    await waitFor(() => {
      expect(screen.getAllByText("Consulta Inicial").length).toBeGreaterThan(0)
    })
  })

  it("renders professional names for appointments", async () => {
    render(<AppointmentList />)

    await waitFor(() => {
      expect(screen.getAllByText(/Dra\. Mariana Costa/).length).toBeGreaterThan(0)
    })
  })

  it("renders empty state when no appointments", async () => {
    server.use(
      http.get(`${API_BASE}/appointments`, () => {
        return HttpResponse.json({
          count: 0,
          next: null,
          previous: null,
          results: [],
        })
      })
    )

    render(<AppointmentList />)

    await waitFor(() => {
      expect(screen.getByText("Nenhum agendamento encontrado.")).toBeInTheDocument()
    })
  })

  it("shows error state on API failure", async () => {
    server.use(
      http.get(`${API_BASE}/appointments`, () => {
        return HttpResponse.json({ detail: "Server Error" }, { status: 500 })
      })
    )

    render(<AppointmentList />)

    await waitFor(
      () => {
        expect(screen.getByText(/Erro ao carregar agendamentos/)).toBeInTheDocument()
      },
      { timeout: 5000 }
    )
  })
})
