import { render, screen, fireEvent } from "@testing-library/react"
import { describe, it, expect, beforeAll, afterEach, afterAll, vi } from "vitest"
import React from "react"
import { ErrorBoundary } from "@/components/ui/error-boundary"

// Helper: a component that throws when triggered
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error("Test error")
  }
  return <div>Normal content</div>
}

describe("ErrorBoundary", () => {
  const originalConsoleError = console.error
  const originalLocation = window.location

  beforeAll(() => {
    console.error = vi.fn()
    // jsdom doesn't allow direct assignment to window.location.reload — use Object.defineProperty
    Object.defineProperty(window, "location", {
      configurable: true,
      value: {
        ...originalLocation,
        reload: vi.fn(),
      },
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  afterAll(() => {
    console.error = originalConsoleError
    Object.defineProperty(window, "location", {
      configurable: true,
      value: originalLocation,
    })
  })

  it("renders children when no error", () => {
    render(
      <ErrorBoundary>
        <div>Children content</div>
      </ErrorBoundary>
    )

    expect(screen.getByText("Children content")).toBeInTheDocument()
  })

  it("renders fallback when error is thrown", () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText("Algo deu errado")).toBeInTheDocument()
    expect(
      screen.getByText("Ocorreu um erro inesperado. Tente recarregar a página.")
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Tentar novamente" })).toBeInTheDocument()
  })

  it("calls onError callback when error occurs", () => {
    const onError = vi.fn()

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(onError).toHaveBeenCalledTimes(1)
    expect(onError.mock.calls[0][0]).toBeInstanceOf(Error)
    expect(onError.mock.calls[0][0].message).toBe("Test error")
  })

  it("renders custom fallback when provided", () => {
    render(
      <ErrorBoundary fallback={<div>Custom fallback</div>}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText("Custom fallback")).toBeInTheDocument()
  })

  it("calls window.location.reload when retry button is clicked", () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    const retryButton = screen.getByRole("button", { name: "Tentar novamente" })
    fireEvent.click(retryButton)

    expect(window.location.reload).toHaveBeenCalledTimes(1)
  })
})
