import { render, screen } from "@testing-library/react"
import { describe, it, expect } from "vitest"
import { DashboardContent } from "@/components/dashboard/dashboard-content"

describe("DashboardContent", () => {
  it("renders dashboard title", () => {
    render(<DashboardContent />)
    expect(screen.getByText("Painel de Controle")).toBeInTheDocument()
  })

  it("renders KPI card for Receita Total", () => {
    render(<DashboardContent />)
    expect(screen.getByText("Receita Total")).toBeInTheDocument()
  })

  it("renders KPI card for Clientes Ativos", () => {
    render(<DashboardContent />)
    expect(screen.getByText("Clientes Ativos")).toBeInTheDocument()
  })

  it("renders KPI card for Leads Ativos", () => {
    render(<DashboardContent />)
    expect(screen.getByText("Leads Ativos")).toBeInTheDocument()
  })

  it("renders KPI card for Agendamentos Hoje", () => {
    render(<DashboardContent />)
    expect(screen.getByText("Agendamentos Hoje")).toBeInTheDocument()
  })

  it("renders bar chart section", () => {
    render(<DashboardContent />)
    expect(screen.getByText("Receita Mensal")).toBeInTheDocument()
  })
})
