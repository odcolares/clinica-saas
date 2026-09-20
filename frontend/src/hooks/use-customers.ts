import useSWR, { mutate } from "swr"
import { swrConfig, fetcher } from "@/lib/swr-config"
import type { Customer, PaginatedResponse, CustomerContact, CustomerAddress } from "@/types/api"

export function useCustomers() {
  const { data, error, isLoading, isValidating } = useSWR<PaginatedResponse<Customer>>(
    "/api/v1/customers",
    fetcher,
    swrConfig
  )

  return {
    customers: data?.results ?? [],
    count: data?.count ?? 0,
    hasNext: data?.next !== null,
    hasPrevious: data?.previous !== null,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export function useCustomer(id: string | null) {
  const { data, error, isLoading, isValidating } = useSWR<Customer>(
    id ? `/api/v1/customers/${id}` : null,
    fetcher,
    swrConfig
  )

  return {
    customer: data,
    isLoading,
    isValidating,
    isError: !!error,
    error,
  }
}

export async function createCustomerContact(
  customerId: string,
  contact: { type: "phone" | "email" | "whatsapp"; value: string; is_primary?: boolean }
): Promise<CustomerContact> {
  const res = await fetch(`/api/v1/customers/${customerId}/contacts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(contact),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao adicionar contato")
  }

  return await res.json() as CustomerContact
}

export async function createCustomerAddress(
  customerId: string,
  address: Omit<CustomerAddress, "id" | "created_at" | "customer">
): Promise<CustomerAddress> {
  const res = await fetch(`/api/v1/customers/${customerId}/addresses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(address),
  })

  if (!res.ok) {
    const errorData = await res.json()
    throw new Error(errorData.detail || "Falha ao adicionar endereço")
  }

  return await res.json() as CustomerAddress
}
