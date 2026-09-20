import useSWR, { mutate } from "swr"
import { swrConfig, fetcher } from "@/lib/swr-config"
import type { Lead, LeadCreateRequest, LeadStatus, PaginatedResponse } from "@/types/api"

const LEADS_KEY = "/api/v1/leads"

export function useLeads() {
  const { data, error, isLoading, isValidating } = useSWR<PaginatedResponse<Lead>>(
    LEADS_KEY,
    fetcher,
    swrConfig
  )

  return {
    leads: data?.results ?? [],
    count: data?.count ?? 0,
    hasNext: data?.next !== null,
    hasPrevious: data?.previous !== null,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export function useLead(id: string | null) {
  const { data, error, isLoading, isValidating } = useSWR<Lead>(
    id ? `/api/v1/leads/${id}` : null,
    fetcher,
    swrConfig
  )

  return {
    lead: data,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export async function createLead(payload: LeadCreateRequest): Promise<Lead> {
  const res = await fetch("/api/v1/leads", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao criar lead")
  }

  const lead = await res.json() as Lead
  mutate(LEADS_KEY)
  return lead
}

export async function updateLeadStatus(
  id: string,
  status: LeadStatus
): Promise<Lead> {
  const res = await fetch(`/api/v1/leads/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao atualizar status")
  }

  const lead = await res.json() as Lead
  mutate(`/api/v1/leads/${id}`)
  mutate(LEADS_KEY)
  return lead
}
