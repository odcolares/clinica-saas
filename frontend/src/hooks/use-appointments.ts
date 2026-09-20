import useSWR, { mutate } from "swr"
import { swrConfig, fetcher } from "@/lib/swr-config"
import type {
  Appointment,
  AppointmentCreateRequest,
  AppointmentUpdateRequest,
  AppointmentFilters,
  AppointmentStatus,
  Professional,
  Service,
  PaginatedResponse,
  ProfessionalAvailability,
  AvailabilityFilters,
} from "@/types/api"

const APPOINTMENTS_KEY = "/api/v1/appointments"

export function useAppointments(filters?: AppointmentFilters) {
  const queryString = filters
    ? "?" + new URLSearchParams(filters as Record<string, string>).toString()
    : ""

  const { data, error, isLoading, isValidating } = useSWR<PaginatedResponse<Appointment>>(
    `${APPOINTMENTS_KEY}${queryString}`,
    fetcher,
    swrConfig
  )

  return {
    appointments: data?.results ?? [],
    count: data?.count ?? 0,
    hasNext: data?.next !== null,
    hasPrevious: data?.previous !== null,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export function useAppointment(id: string | null) {
  const { data, error, isLoading, isValidating } = useSWR<Appointment>(
    id ? `/api/v1/appointments/${id}` : null,
    fetcher,
    swrConfig
  )

  return {
    appointment: data,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export function useProfessionals() {
  const { data, error, isLoading } = useSWR<Professional[]>(
    "/api/v1/professionals",
    fetcher,
    swrConfig
  )

  return {
    professionals: data ?? [],
    isLoading,
    isError: !!error,
    error,
  }
}

export function useServices() {
  const { data, error, isLoading } = useSWR<Service[]>(
    "/api/v1/services",
    fetcher,
    swrConfig
  )

  return {
    services: data ?? [],
    isLoading,
    isError: !!error,
    error,
  }
}

export async function createAppointment(payload: AppointmentCreateRequest): Promise<Appointment> {
  const res = await fetch("/api/v1/appointments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao criar agendamento")
  }

  const appointment = await res.json() as Appointment
  mutate(APPOINTMENTS_KEY)
  return appointment
}

export async function updateAppointment(
  id: string,
  payload: AppointmentUpdateRequest
): Promise<Appointment> {
  const res = await fetch(`/api/v1/appointments/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao atualizar agendamento")
  }

  const appointment = await res.json() as Appointment
  mutate(`/api/v1/appointments/${id}`)
  mutate(APPOINTMENTS_KEY)
  return appointment
}

export async function cancelAppointment(id: string): Promise<Appointment> {
  const res = await fetch(`/api/v1/appointments/${id}/cancel`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao cancelar agendamento")
  }

  const appointment = await res.json() as Appointment
  mutate(`/api/v1/appointments/${id}`)
  mutate(APPOINTMENTS_KEY)
  return appointment
}

export async function confirmAppointment(id: string): Promise<Appointment> {
  const res = await fetch(`/api/v1/appointments/${id}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao confirmar agendamento")
  }

  const appointment = await res.json() as Appointment
  mutate(`/api/v1/appointments/${id}`)
  mutate(APPOINTMENTS_KEY)
  return appointment
}

export function useProfessionalAvailability(filters: AvailabilityFilters) {
  const queryString = filters
    ? "?" + new URLSearchParams(filters as unknown as Record<string, string>).toString()
    : ""

  const { data, error, isLoading, isValidating } = useSWR<ProfessionalAvailability[]>(
    filters.date ? `/api/v1/availability${queryString}` : null,
    fetcher,
    swrConfig
  )

  return {
    availability: data ?? [],
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export function useProfessionalAvailabilityByDate(professionalId: string, date: string) {
  const { data, error, isLoading, isValidating } = useSWR<ProfessionalAvailability>(
    professionalId && date ? `/api/v1/availability/${professionalId}?date=${date}` : null,
    fetcher,
    swrConfig
  )

  return {
    availability: data,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}
