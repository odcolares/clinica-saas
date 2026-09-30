"use client"

import { useState } from "react"
import { Search, MessageSquare, User, Clock } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useConversations } from "@/hooks/use-conversations"
import type { ConversationFilters, ConversationChannel, ConversationStatus } from "@/types/api"

const STATUS_LABELS: Record<string, string> = {
  open: "Aberta",
  assigned: "Atribuída",
  closed: "Fechada",
}

const STATUS_VARIANTS: Record<string, "default" | "secondary" | "outline"> = {
  open: "default",
  assigned: "secondary",
  closed: "outline",
}

const CHANNEL_LABELS: Record<string, string> = {
  telegram: "Telegram",
  whatsapp: "WhatsApp",
}

export function ConversationList({
  selectedId,
  onSelect,
}: {
  selectedId?: string | null
  onSelect?: (id: string) => void
}) {
  const [filters, setFilters] = useState<ConversationFilters>({})
  const { conversations, isLoading, isError, error } = useConversations(filters)

  const unreadCount = conversations.filter((c) => c.status === "open").length

  if (isError) {
    return (
      <Card>
        <CardContent className="pt-6 text-center text-destructive">
          Erro ao carregar conversas: {error?.message}
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      <div className="p-4 space-y-3 border-b">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Conversas</h2>
          {unreadCount > 0 && (
            <Badge variant="default">{unreadCount} aberta{unreadCount !== 1 ? "s" : ""}</Badge>
          )}
        </div>

        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar conversas..."
            className="pl-8"
            onChange={(e) =>
              setFilters((f) => ({ ...f, search: e.target.value || undefined }))
            }
          />
        </div>

        <div className="grid grid-cols-2 gap-2">
          <Select
            value={filters.status || "all"}
            onValueChange={(v) =>
              setFilters((f) => ({
                ...f,
                status: v === "all" ? undefined : (v as ConversationStatus),
              }))
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="open">Aberta</SelectItem>
              <SelectItem value="assigned">Atribuída</SelectItem>
              <SelectItem value="closed">Fechada</SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={filters.channel || "all"}
            onValueChange={(v) =>
              setFilters((f) => ({
                ...f,
                channel: v === "all" ? undefined : (v as ConversationChannel),
              }))
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Canal" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="telegram">Telegram</SelectItem>
              <SelectItem value="whatsapp">WhatsApp</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Carregando conversas...
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Nenhuma conversa encontrada.
            </div>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.id}
                className={`w-full text-left p-3 rounded-lg border transition-colors hover:bg-accent ${
                  selectedId === conv.id ? "bg-accent border-accent" : ""
                }`}
                onClick={() => onSelect?.(conv.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium text-sm">
                      {conv.metadata.display_name || conv.external_chat_id}
                    </span>
                  </div>
                  <Badge variant={STATUS_VARIANTS[conv.status]} className="text-xs">
                    {STATUS_LABELS[conv.status]}
                  </Badge>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-muted-foreground">
                    {CHANNEL_LABELS[conv.channel] || conv.channel}
                  </span>
                  {conv.assigned_to && (
                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                      <User className="h-3 w-3" />
                      {conv.assigned_to}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {new Date(conv.updated_at).toLocaleString("pt-BR", {
                    day: "2-digit",
                    month: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </button>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  )
}