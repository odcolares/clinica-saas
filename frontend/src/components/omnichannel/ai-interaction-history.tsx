"use client"

import { useState, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import type { ConversationMessage } from "@/types/api"

export function AIIntractionHistory({ conversationId }: { conversationId: string }) {
  const [interactions, setInteractions] = useState<Array<{
    id: string
    role: "user" | "assistant" | "system"
    content: string
    created_at: string
    tokens_used?: number
    latency_ms?: number
  }>>([])]
  const [isLoading, setIsLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [lastId, setLastId] = useState<string | null>(null)

  useEffect(() => {
    fetchInteractions()
  }, [])

  const fetchInteractions = async (skipLastId = false) => {
    setIsLoading(true)
    try {
      const url = skipLastId && lastId
        ? `/api/v1/ai/interactions?after=${lastId}`
        : `/api/v1/ai/interactions?conversation_id=${conversationId}`

      const res = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        toast.error(err.detail || "Falha ao carregar histórico")
        return
      }

      const data = await res.json()
      const newInteractions = data.interactions || []

      if (newInteractions.length > 0) {
        setLastId(newInteractions[newInteractions.length - 1].id)
        setInteractions(prev => {
          // Avoid duplicates
          const existingIds = new Set(prev.map(i => i.id))
          return [...new Set([...prev, ...newInteractions])].filter(
            (item) => !existingIds.has(item.id)
          )
        })
        setHasMore(newInteractions.length > 0)
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao carregar histórico")
    } finally {
      setIsLoading(false)
    }
  }

  const loadMore = () => {
    if (!isLoading && hasMore) {
      fetchInteractions(true)
    }
  }

  if (isLoading && interactions.length === 0) {
    return (
      <ScrollArea className="h-[calc(100vh-12rem)] p-8 text-center">
        <div>
          <span className="animate-spin h-12 w-12 mx-auto border-b-2 border-current border-t-2 rounded-full"></span>
          <p className="mt-4 text-muted-foreground">Carregando histórico de IA...</p>
        </div>
      </ScrollArea>
    )
  }

  return (
    <ScrollArea className="h-[calc(100vh-12rem)] p-4">
      <h2 className="mb-4 text-lg font-semibold border-b pb-2">
        Histórico de Interações da IA
      </h2>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {interactions.map((interaction) => (
          <div
            key={interaction.id}
            className="p-3 rounded-lg border border-border bg-card"
          >
            <div className="flex items-start gap-3">
              <Badge
                variant={interaction.role === "assistant" ? "default" : "outline"}
                className="flex-shrink-0 text-sm"
              >
                {interaction.role === "assistant" ? "IA" : interaction.role}
              </Badge>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{interaction.role === "assistant" ? "Assistente IA" : "Usuário"}</p>
                <p className="text-xs text-muted-foreground line-clamp-3">
                  {interaction.content}
                </p>
              </div>
              <div className="text-right text-xs text-muted-foreground">
                {new Date(interaction.created_at).toLocaleTimeString("pt-BR")} • 
                {interaction.tokens_used !== undefined 
                  ? `${interaction.tokens_used} tokens` 
                  : ""}
                {interaction.latency_ms !== undefined
                  ? ` (${interaction.latency_ms}ms)`
                  : ""}
              </div>
            </div>
          </div>
        ))}
      </div>

      {interactions.length > 0 && (
        <Button
          onClick={loadMore}
          disabled={!hasMore || isLoading}
          className="mt-3 w-full justify-end"
        >
          {hasMore && !isLoading ? "Carregar mais" : "Nenhum mais histórico"}
        </Button>
      )}
    </ScrollArea>
  )
}