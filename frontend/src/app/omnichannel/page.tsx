"use client"

import { useState } from "react"
import { ConversationList } from "@/components/omnichannel/conversation-list"
import { ConversationChat } from "@/components/omnichannel/conversation-chat"
import { AgentStatusBadge } from "@/components/omnichannel/agent-status-badge"
import { useConversation } from "@/hooks/use-conversations"

export default function OmnichannelPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const { conversation } = useConversation(selectedId)

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-background">
        <div>
          <h1 className="text-xl font-bold">Atendimento Omnichannel</h1>
          <p className="text-sm text-muted-foreground">
            Gerencie conversas de todos os canais em um só lugar.
          </p>
        </div>
        <AgentStatusBadge />
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        <div className="w-80 border-r">
          <ConversationList
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>
        <div className="flex-1">
          {conversation ? (
            <ConversationChat conversation={conversation} />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              Selecione uma conversa para iniciar o atendimento.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}