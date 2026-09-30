"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Loader2 } from "lucide-react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { useConversationMessages, replyConversation, assignConversation } from "@/hooks/use-conversations"
import { toast } from "sonner"
import type { Conversation, ConversationMessage } from "@/types/api"

const SENDER_LABELS: Record<string, string> = {
  customer: "Cliente",
  agent: "Atendente",
  system: "Sistema",
}

const SENDER_ALIGN: Record<string, "start" | "end"> = {
  customer: "start",
  agent: "end",
  system: "start",
}

function MessageBubble({ message }: { message: ConversationMessage }) {
  const align = SENDER_ALIGN[message.sender_kind] || "start"
  const isAgent = message.sender_kind === "agent"

  return (
    <div className={`flex ${align === "end" ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-lg px-3 py-2 text-sm ${
          isAgent
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        }`}
      >
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-medium">
            {SENDER_LABELS[message.sender_kind]}
          </span>
        </div>
        <p className="whitespace-pre-wrap break-words">{message.body}</p>
        <span className="text-[10px] opacity-70 mt-1 block">
          {new Date(message.created_at).toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  )
}

export function ConversationChat({ conversation }: { conversation: Conversation }) {
  const { messages, isLoading } = useConversationMessages(conversation.id, {
    refreshInterval: 8000,
  })
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const [assignOpen, setAssignOpen] = useState(false)
  const [assignee, setAssignee] = useState<string | null>(conversation.assigned_to || "")
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  async function handleSend() {
    const text = input.trim()
    if (!text || sending) return
    setSending(true)
    try {
      await replyConversation(conversation.id, { body: text })
      setInput("")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao enviar mensagem")
    } finally {
      setSending(false)
    }
  }

  async function handleAssign() {
    if (!assignee) return
    try {
      await assignConversation(conversation.id, { assigned_to: assignee })
      toast.success("Conversa atribuída com sucesso!")
      setAssignOpen(false)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao atribuir conversa")
    }
  }

  const initials = (conversation.metadata.display_name || "??")
    .split(" ")
    .map((n: string) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
          <Avatar>
            <AvatarFallback>{initials}</AvatarFallback>
          </Avatar>
          <div>
            <h3 className="font-semibold">
              {conversation.metadata.display_name || conversation.external_chat_id}
            </h3>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="outline" className="text-xs">
                {conversation.channel}
              </Badge>
              {conversation.assigned_to && (
                <span>Atribuído a: {conversation.assigned_to}</span>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Dialog open={assignOpen} onOpenChange={setAssignOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                Atribuir
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Atribuir conversa</DialogTitle>
                <DialogDescription>
                  Selecione o atendente responsável por esta conversa.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-2 py-4">
                <Label htmlFor="assignee">Atendente</Label>
                <Input
                  id="assignee"
                  value={assignee || ""}
                  onChange={(e) => setAssignee(e.target.value)}
                  placeholder="ID do usuário"
                />
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setAssignOpen(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleAssign}>Atribuir</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1">
        <div ref={scrollRef} className="p-4 space-y-3">
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Carregando mensagens...
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Nenhagem mensagem ainda.
            </div>
          ) : (
            messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="flex gap-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite uma mensagem..."
            disabled={sending}
          />
          <Button type="submit" disabled={sending || !input.trim()}>
            {sending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  )
}