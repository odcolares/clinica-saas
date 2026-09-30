import apiClient from "@/services/api"
import type {
  Conversation,
  ConversationFilters,
  ConversationMessage,
  OutboundMessageRequest,
  AssignConversationRequest,
  PaginatedResponse,
  Template,
} from "@/types/api"

const BASE = "/conversations"

export async function fetchConversations(
  filters?: ConversationFilters,
): Promise<PaginatedResponse<Conversation>> {
  const params = new URLSearchParams()
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        params.set(key, String(value))
      }
    })
  }
  const res = await apiClient.get<PaginatedResponse<Conversation>>(
    `${BASE}?${params.toString()}`,
  )
  return res.data
}

export async function fetchConversation(id: string): Promise<Conversation> {
  const res = await apiClient.get<Conversation>(`${BASE}/${id}`)
  return res.data
}

export async function fetchConversationMessages(
  id: string,
  page?: number,
): Promise<PaginatedResponse<ConversationMessage>> {
  const params = new URLSearchParams()
  if (page) params.set("page", String(page))
  const res = await apiClient.get<PaginatedResponse<ConversationMessage>>(
    `${BASE}/${id}/messages?${params.toString()}`,
  )
  return res.data
}

export async function assignConversation(
  id: string,
  payload: AssignConversationRequest,
): Promise<Conversation> {
  const res = await apiClient.post<Conversation>(
    `${BASE}/${id}/assign`,
    payload,
  )
  return res.data
}

export async function replyConversation(
  id: string,
  payload: OutboundMessageRequest,
): Promise<ConversationMessage> {
  const res = await apiClient.post<ConversationMessage>(
    `${BASE}/${id}/reply`,
    payload,
  )
  return res.data
}

// ─── Templates (offline-first via localStorage; backend endpoint
//     não está em API.md — etapa 5 ou nova pode adicionar). ───

const TEMPLATES_KEY = "omnichannel:templates"

function loadTemplates(): Template[] {
  if (typeof window === "undefined") return []
  try {
    const raw = localStorage.getItem(TEMPLATES_KEY)
    return raw ? (JSON.parse(raw) as Template[]) : []
  } catch {
    return []
  }
}

function saveTemplates(templates: Template[]): void {
  if (typeof window === "undefined") return
  try {
    localStorage.setItem(TEMPLATES_KEY, JSON.stringify(templates))
  } catch {
    // storage indisponível — templates em memória temporariamente
  }
}

export function fetchTemplates(): Template[] {
  return loadTemplates()
}

export function createTemplate(payload: Omit<Template, "id" | "created_at">): Template {
  const templates = loadTemplates()
  const newTemplate: Template = {
    ...payload,
    id: `tpl-${Date.now().toString(36)}`,
    created_at: new Date().toISOString(),
  }
  templates.push(newTemplate)
  saveTemplates(templates)
  return newTemplate
}

export function updateTemplate(
  id: string,
  payload: Partial<Omit<Template, "id" | "created_at">>,
): Template {
  const templates = loadTemplates()
  const index = templates.findIndex((t) => t.id === id)
  if (index === -1) throw new Error("Template não encontrado")
  const updated: Template = { ...templates[index], ...payload }
  templates[index] = updated
  saveTemplates(templates)
  return updated
}

export function deleteTemplate(id: string): void {
  const templates = loadTemplates().filter((t) => t.id !== id)
  saveTemplates(templates)
}