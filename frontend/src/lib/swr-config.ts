import { SWRConfiguration } from "swr"

export const swrConfig: SWRConfiguration = {
  dedupingInterval: 2 * 60 * 1000, // 2 minutes
  revalidateOnFocus: true,
  revalidateOnReconnect: true,
  shouldRetryOnError: true,
  errorRetryCount: 3,
  errorRetryInterval: 1000,
}

export const fetcher = (url: string) =>
  fetch(url).then((res) => {
    if (!res.ok) {
      throw new Error(`Erro ao carregar dados: ${res.status}`)
    }
    return res.json()
  })
