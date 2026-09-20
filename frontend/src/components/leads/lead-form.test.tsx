import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import { LeadForm } from "./lead-form"
import { LeadCreateRequest } from "@/types/api"

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

describe("LeadForm", () => {
  it("renders the form with all fields", () => {
    render(<LeadForm onSubmit={vi.fn()} />)
    expect(screen.getByLabelText("Nome *")).toBeInTheDocument()
    expect(screen.getByLabelText("E-mail")).toBeInTheDocument()
    expect(screen.getByLabelText("Telefone")).toBeInTheDocument()
    expect(screen.getByLabelText("Origem *")).toBeInTheDocument()
    expect(screen.getByLabelText("Detalhes da origem")).toBeInTheDocument()
    expect(screen.getByText("Salvar")).toBeInTheDocument()
  })

  it("shows validation error when name is empty", async () => {
    render(<LeadForm onSubmit={vi.fn()} />)
    fireEvent.click(screen.getByText("Salvar"))
    await waitFor(() => {
      expect(screen.getByText("Nome é obrigatório")).toBeInTheDocument()
    })
  })

  it("calls onSubmit with correct data when form is valid", async () => {
    const mockSubmit = vi.fn()
    render(<LeadForm onSubmit={mockSubmit} />)

    fireEvent.change(screen.getByLabelText("Nome *"), {
      target: { value: "Test Lead" },
    })
    fireEvent.change(screen.getByLabelText("E-mail"), {
      target: { value: "test@example.com" },
    })
    fireEvent.change(screen.getByLabelText("Telefone"), {
      target: { value: "11999999999" },
    })
    fireEvent.change(screen.getByLabelText("Detalhes da origem"), {
      target: { value: "From Google Ads" },
    })

    fireEvent.click(screen.getByText("Salvar"))

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        name: "Test Lead",
        email: "test@example.com",
        phone: "11999999999",
        origin: "site",
        source_detail: "From Google Ads",
      } as LeadCreateRequest)
    })
  })

  it("shows loading state when isSubmitting is true", () => {
    render(<LeadForm onSubmit={vi.fn()} isLoading={true} />)
    expect(screen.getByText("Salvando...")).toBeInTheDocument()
  })
})
