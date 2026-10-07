import useSWR, { mutate } from "swr"
import { swrConfig, fetcher } from "@/lib/swr-config"
import type {
  IntegrationConfig,
  IntegrationConfigCreateRequest,
  WebhookEndpoint,
  WebhookEndpointCreateRequest,
  ApiKey,
  ApiKeyCreateResponse,
} from "@/types/api"

const INTEGRATIONS_KEY = "/api/v1/settings/integrations"
const WEBHOOKS_KEY = "/api/v1/settings/webhooks"
const API_KEYS_KEY = "/api/v1/settings/api-keys"

export function useIntegrations() {
  const { data, error, isLoading, isValidating } = useSWR<IntegrationConfig[]>(
    INTEGRATIONS_KEY,
    fetcher,
    swrConfig
  )

  return {
    integrations: data ?? [],
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export async function createIntegration(
  payload: IntegrationConfigCreateRequest
): Promise<IntegrationConfig> {
  const res = await fetch(INTEGRATIONS_KEY, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao criar integração")
  }

  const integration = (await res.json()) as IntegrationConfig
  mutate(INTEGRATIONS_KEY)
  return integration
}

export async function updateIntegration(
  id: string,
  payload: Partial<IntegrationConfig>
): Promise<IntegrationConfig> {
  const res = await fetch(`${INTEGRATIONS_KEY}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao atualizar integração")
  }

  const integration = (await res.json()) as IntegrationConfig
  mutate(`${INTEGRATIONS_KEY}/${id}`)
  mutate(INTEGRATIONS_KEY)
  return integration
}

export async function deleteIntegration(id: string): Promise<void> {
  const res = await fetch(`${INTEGRATIONS_KEY}/${id}`, {
    method: "DELETE",
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao excluir integração")
  }

  mutate(INTEGRATIONS_KEY)
}

export function useWebhooks() {
  const { data, error, isLoading, isValidating } = useSWR<WebhookEndpoint[]>(
    WEBHOOKS_KEY,
    fetcher,
    swrConfig
  )

  return {
    webhooks: data ?? [],
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export async function createWebhook(
  payload: WebhookEndpointCreateRequest
): Promise<WebhookEndpoint> {
  const res = await fetch(WEBHOOKS_KEY, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao criar webhook")
  }

  const webhook = (await res.json()) as WebhookEndpoint
  mutate(WEBHOOKS_KEY)
  return webhook
}

export async function updateWebhook(
  id: string,
  payload: Partial<WebhookEndpoint>
): Promise<WebhookEndpoint> {
  const res = await fetch(`${WEBHOOKS_KEY}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao atualizar webhook")
  }

  const webhook = (await res.json()) as WebhookEndpoint
  mutate(`${WEBHOOKS_KEY}/${id}`)
  mutate(WEBHOOKS_KEY)
  return webhook
}

export async function deleteWebhook(id: string): Promise<void> {
  const res = await fetch(`${WEBHOOKS_KEY}/${id}`, {
    method: "DELETE",
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao excluir webhook")
  }

  mutate(WEBHOOKS_KEY)
}

export function useApiKeys() {
  const { data, error, isLoading, isValidating } = useSWR<ApiKey[]>(
    API_KEYS_KEY,
    fetcher,
    swrConfig
  )

  return {
    apiKeys: data ?? [],
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export async function createApiKey(name: string): Promise<ApiKeyCreateResponse> {
  const res = await fetch(API_KEYS_KEY, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao criar API key")
  }

  const apiKey = (await res.json()) as ApiKeyCreateResponse
  mutate(API_KEYS_KEY)
  return apiKey
}

export async function deleteApiKey(id: string): Promise<void> {
  const res = await fetch(`${API_KEYS_KEY}/${id}`, {
    method: "DELETE",
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao excluir API key")
  }

  mutate(API_KEYS_KEY)
}

export async function toggleApiKey(id: string, active: boolean): Promise<ApiKey> {
  const res = await fetch(`${API_KEYS_KEY}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ active }),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao atualizar API key")
  }

  const apiKey = (await res.json()) as ApiKey
  mutate(`${API_KEYS_KEY}/${id}`)
  mutate(API_KEYS_KEY)
  return apiKey
}
