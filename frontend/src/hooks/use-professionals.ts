import useSWR, { mutate } from "swr"
import { swrConfig, fetcher } from "@/lib/swr-config"
import type { Professional } from "@/types/api"

const PROFESSIONALS_KEY = "/api/v1/professionals"

export function useProfessionals() {
  const { data, error, isLoading, isValidating } = useSWR<Professional[]>(
    PROFESSIONALS_KEY,
    fetcher,
    swrConfig
  )

  return {
    professionals: data ?? [],
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export async function createProfessional(payload: Partial<Professional>): Promise<Professional> {
  const res = await fetch(PROFESSIONALS_KEY, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao criar profissional")
  }

  const professional = (await res.json()) as Professional
  mutate(PROFESSIONALS_KEY)
  return professional
}

export async function updateProfessional(
  id: string,
  payload: Partial<Professional>
): Promise<Professional> {
  const res = await fetch(`${PROFESSIONALS_KEY}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao atualizar profissional")
  }

  const professional = (await res.json()) as Professional
  mutate(`${PROFESSIONALS_KEY}/${id}`)
  mutate(PROFESSIONALS_KEY)
  return professional
}

export async function deleteProfessional(id: string): Promise<void> {
  const res = await fetch(`${PROFESSIONALS_KEY}/${id}`, {
    method: "DELETE",
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao excluir profissional")
  }

  mutate(PROFESSIONALS_KEY)
}
