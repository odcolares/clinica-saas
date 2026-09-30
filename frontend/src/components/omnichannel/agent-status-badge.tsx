"use client"

import { Badge } from "@/components/ui/badge"
import { useAuth } from "@/hooks/use-auth"

const STATUS_CONFIG: Record<
  "online" | "away" | "busy",
  { label: string; variant: "default" | "secondary" | "destructive" }
> = {
  online: { label: "Online", variant: "default" },
  away: { label: "Ausente", variant: "secondary" },
  busy: { label: "Ocupado", variant: "destructive" },
}

/**
 * Badge de status do agente.
 *
 * Limitação: sem Device API backend, o status é inferido a partir do
 * token de autenticação (online enquanto logado). Em logout → offline.
 */
export function AgentStatusBadge() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading || !isAuthenticated) {
    return <Badge variant="secondary">Offline</Badge>
  }

  // Sem Device API: assume online enquanto houver token válido.
  const status: "online" | "away" | "busy" = "online"
  const config = STATUS_CONFIG[status]

  return (
    <Badge variant={config.variant} className="gap-1.5">
      <span className="size-1.5 rounded-full bg-current" />
      {config.label}
    </Badge>
  )
}