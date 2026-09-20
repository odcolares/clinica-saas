import { render, screen, fireEvent } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { CalendarPageContent } from "@/components/calendar/calendar-view"

describe("Calendar", () => {
  it("renders calendar page title", () => {
    render(<CalendarPageContent />)
    expect(screen.getByText("Calendário")).toBeInTheDocument()
  })

  it("renders agenda appointments heading", () => {
    render(<CalendarPageContent />)
    expect(screen.getByText("Agendamentos")).toBeInTheDocument()
  })

  it("renders day headers", () => {
    render(<CalendarPageContent />)
    expect(screen.getByText("Dom")).toBeInTheDocument()
    expect(screen.getByText("Seg")).toBeInTheDocument()
    expect(screen.getByText("Ter")).toBeInTheDocument()
    expect(screen.getByText("Qua")).toBeInTheDocument()
    expect(screen.getByText("Qui")).toBeInTheDocument()
    expect(screen.getByText("Sex")).toBeInTheDocument()
    expect(screen.getByText("Sáb")).toBeInTheDocument()
  })

  it("renders today button", () => {
    render(<CalendarPageContent />)
    expect(screen.getByLabelText("Hoje")).toBeInTheDocument()
  })

  it("renders previous and next month buttons", () => {
    render(<CalendarPageContent />)
    expect(screen.getByLabelText("Mês anterior")).toBeInTheDocument()
    expect(screen.getByLabelText("Próximo mês")).toBeInTheDocument()
  })

  it("renders current month", () => {
    render(<CalendarPageContent />)
    expect(screen.getByText("setembro 2025")).toBeInTheDocument()
  })
})
