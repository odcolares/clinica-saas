import useSWR, { mutate } from "swr"
import { swrConfig, fetcher } from "@/lib/swr-config"
import type { TenantSettings, TenantSettingsUpdateRequest } from "@/types/api"

const TENANT_SETTINGS_KEY = "/api/v1/settings/tenant"

export function useTenantSettings() {
  const { data, error, isLoading, isValidating } = useSWR<TenantSettings>(
    TENANT_SETTINGS_KEY,
    fetcher,
    swrConfig
  )

  return {
    settings: data,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export async function updateTenantSettings(
  payload: TenantSettingsUpdateRequest
): Promise<TenantSettings> {
  const res = await fetch(TENANT_SETTINGS_KEY, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao atualizar configurações")
  }

  const settings = (await res.json()) as TenantSettings
  mutate(TENANT_SETTINGS_KEY)
  return settings
}
