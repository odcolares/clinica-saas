import { render, screen } from "@testing-library/react"
import { describe, it, expect, vi } from "vitest"
import React from "react"
import { ToasterProvider } from "@/components/providers/toaster-provider"

// Mock sonner's Toaster to verify props are passed correctly
const mockProps: Record<string, unknown> = {}
vi.mock("sonner", () => ({
  Toaster: function MockToaster(props: Record<string, unknown>) {
    Object.assign(mockProps, props)
    return (
      <div data-testid="mock-toaster" data-props={JSON.stringify(props)}>
        Toaster
      </div>
    )
  },
}))

describe("ToasterProvider", () => {
  it("renders Toaster component without crashing", () => {
    render(<ToasterProvider />)

    expect(screen.getByTestId("mock-toaster")).toBeInTheDocument()
  })

  it("applies Toaster props correctly", () => {
    render(<ToasterProvider />)

    const toaster = screen.getByTestId("mock-toaster")
    const props = JSON.parse(toaster.getAttribute("data-props") || "{}")

    expect(props.position).toBe("bottom-right")
    expect(props.theme).toBe("system")
    expect(props.richColors).toBe(true)
    expect(props.closeButton).toBe(true)
    expect(props.duration).toBe(4000)
  })
})
