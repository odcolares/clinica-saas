import { notFound } from "next/navigation"
import { ConversationChat } from "@/components/omnichannel/conversation-chat"
import { AgentStatusBadge } from "@/components/omnichannel/agent-status-badge"

interface ConversationDetailPageProps {
  params: Promise<{ id: string }>
}

export default async function ConversationDetailPage({ params }: ConversationDetailPageProps) {
  const { id } = await params
  return <ConversationDetailContent id={id} />
}

async function ConversationDetailContent({ id }: { id: string }) {
  // Server component: fetch initial data
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}${id ? `/conversations/${id}` : ""}`, {
    headers: { "Content-Type": "application/json" },
  })

  if (!res.ok) {
    notFound()
  }

  const conversation = await res.json()

  return (
    <div className="h-screen flex flex-col">
      <div className="flex items-center justify-between p-4 border-b bg-background">
        <div>
          <h1 className="text-xl font-bold">Conversa #{conversation.id}</h1>
        </div>
        <AgentStatusBadge />
      </div>
      <div className="flex-1">
        <ConversationChat conversation={conversation} />
      </div>
    </div>
  )
}