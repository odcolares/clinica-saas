import { render, screen, waitFor, cleanup, fireEvent } from "@testing-library/react"
import { describe, it, expect, beforeAll, beforeEach, afterEach, afterAll, vi } from "vitest"
import { http, HttpResponse } from "msw"
import { setupServer } from "msw/node"
import { SWRConfig, mutate } from "swr"
import { TenantSettingsForm } from "@/components/settings/tenant-settings-form"
import { tenantSettings } from "@/mocks/data"

const API_BASE = "/api/v1"
const TENANT_SETTINGS_KEY = `${API_BASE}/settings/tenant`

const server = setupServer(
  http.get(`${API_BASE}/settings/tenant`, () => {
    return HttpResponse.json(tenantSettings)
  }),
  http.patch(`${API_BASE}/settings/tenant`, async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ ...tenantSettings, ...body })
  }),
)

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

beforeAll(() => server.listen())
beforeEach(() => {
  mutate(TENANT_SETTINGS_KEY, undefined, { populateCache: false })
})
afterEach(() => {
  server.resetHandlers()
  cleanup()
  mutate(TENANT_SETTINGS_KEY, undefined, { populateCache: false })
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

describe("TenantSettingsForm", () => {
  it("renders form with existing settings", () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <TenantSettingsForm settings={tenantSettings} />
      </SWRConfig>
    )

    expect(screen.getByText("Configurações do Tenant")).toBeInTheDocument()
    expect(screen.getByDisplayValue(tenantSettings.brand_name)).toBeInTheDocument()
    const timezoneElements = screen.getAllByDisplayValue(tenantSettings.timezone)
    expect(timezoneElements.length).toBeGreaterThan(0)
  })

  it("renders time inputs", () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <TenantSettingsForm settings={tenantSettings} />
      </SWRConfig>
    )

    const startInput = screen.getByDisplayValue(tenantSettings.business_start)
    const endInput = screen.getByDisplayValue(tenantSettings.business_end)

    expect(startInput).toBeInTheDocument()
    expect(endInput).toBeInTheDocument()
  })

  it("renders color picker for primary color", () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <TenantSettingsForm settings={tenantSettings} />
      </SWRConfig>
    )

    const colorInput = screen.getByDisplayValue(tenantSettings.primary_color)
    expect(colorInput).toBeInTheDocument()
  })

  it("renders save button", () => {
    render(
      <SWRConfig value={swrTestConfig}>
        <TenantSettingsForm settings={tenantSettings} />
      </SWRConfig>
    )

    expect(screen.getByText("Salvar Configurações")).toBeInTheDocument()
  })
})
