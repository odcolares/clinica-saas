import useSWR, { mutate } from "swr"
import { swrConfig, fetcher } from "@/lib/swr-config"
import type {
  Conversation,
  ConversationFilters,
  ConversationMessage,
  PaginatedResponse,
  AssignConversationRequest,
  OutboundMessageRequest,
  Template,
} from "@/types/api"
import {
  fetchTemplates,
  createTemplate,
  updateTemplate,
  deleteTemplate,
} from "@/lib/omnichannel-api"

const API_PREFIX = "/api/v1"
const CONVERSATIONS_KEY = `${API_PREFIX}/conversations`
const CONVERSATION_KEY = (id: string) => `${CONVERSATIONS_KEY}/${id}`
const MESSAGES_KEY = (id: string) => `${CONVERSATIONS_KEY}/${id}/messages`
const TEMPLATES_KEY = "/omnichannel/templates"

// ─── Conversations ─────────────────────────────────────────

export function useConversations(filters?: ConversationFilters) {
  const queryString = filters
    ? "?" + new URLSearchParams(filters as Record<string, string>).toString()
    : ""

  const { data, error, isLoading, isValidating } = useSWR<
    PaginatedResponse<Conversation>
  >(`${CONVERSATIONS_KEY}${queryString}`, fetcher, swrConfig)

  return {
    conversations: data?.results ?? [],
    count: data?.count ?? 0,
    hasNext: data?.next !== null,
    hasPrevious: data?.previous !== null,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export function useConversation(id: string | null) {
  const { data, error, isLoading, isValidating } = useSWR<Conversation>(
    id ? CONVERSATION_KEY(id) : null,
    fetcher,
    swrConfig,
  )

  return {
    conversation: data,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export function useConversationMessages(
  id: string | null,
  opts?: { refreshInterval?: number },
) {
  const refreshInterval = opts?.refreshInterval ?? 8000
  const key = id ? MESSAGES_KEY(id) : null

  const { data, error, isLoading, isValidating } = useSWR<
    PaginatedResponse<ConversationMessage>
  >(key, fetcher, {
    ...swrConfig,
    refreshInterval,
    revalidateOnFocus: true,
    revalidateOnReconnect: true,
  })

  return {
    messages: data?.results ?? [],
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export async function assignConversation(
  id: string,
  payload: AssignConversationRequest,
): Promise<Conversation> {
  const res = await fetch(CONVERSATION_KEY(id), {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail || "Falha ao atribuir conversa")
  }
  const result = (await res.json()) as Conversation
  mutate(CONVERSATION_KEY(id))
  mutate(CONVERSATIONS_KEY)
  return result
}

export async function replyConversation(
  id: string,
  payload: OutboundMessageRequest,
): Promise<ConversationMessage> {
  const res = await fetch(`${CONVERSATION_KEY(id)}/reply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail || "Falha ao enviar mensagem")
  }
  const result = (await res.json()) as ConversationMessage
  mutate(MESSAGES_KEY(id))
  mutate(CONVERSATION_KEY(id))
  return result
}

// ─── Templates ─────────────────────────────────────────────

export function useTemplates() {
  const { data, error, isLoading } = useSWR<Template[]>(
    TEMPLATES_KEY,
    () => fetchTemplates(),
    swrConfig,
  )

  return {
    templates: data ?? [],
    isLoading,
    isError: !!error,
    error,
  }
}

export async function createTemplateItem(
  payload: Omit<Template, "id" | "created_at">,
): Promise<Template> {
  const result = createTemplate(payload)
  mutate(TEMPLATES_KEY, [...(fetchTemplates() || []), result])
  return result
}

export async function updateTemplateItem(
  id: string,
  payload: Partial<Omit<Template, "id" | "created_at">>,
): Promise<Template> {
  const result = updateTemplate(id, payload)
  mutate(TEMPLATES_KEY, fetchTemplates())
  return result
}

export async function deleteTemplateItem(id: string): Promise<void> {
  deleteTemplate(id)
  mutate(TEMPLATES_KEY, fetchTemplates())
}