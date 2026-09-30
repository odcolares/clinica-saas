import { render, screen, fireEvent } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import type { Conversation } from "@/types/api"
import { ConversationList } from "@/components/omnichannel/conversation-list"

const conversations: Conversation[] = [
  {
    id: "conv-1",
    channel: "telegram",
    external_chat_id: "tg-1",
    status: "open",
    assigned_to: null,
    customer: null,
    lead: null,
    metadata: { display_name: "João Silva", phone: "11999999999", telegram_user_id: "tg-1" },
    created_at: "2026-09-30T10:00:00Z",
    updated_at: "2026-09-30T12:00:00Z",
  },
  {
    id: "conv-2",
    channel: "whatsapp",
    external_chat_id: "wa-2",
    status: "assigned",
    assigned_to: "agent-1",
    customer: null,
    lead: null,
    metadata: { display_name: "Maria Souza", phone: "11988888888", telegram_user_id: null },
    created_at: "2026-09-30T09:00:00Z",
    updated_at: "2026-09-30T11:30:00Z",
  },
  {
    id: "conv-3",
    channel: "telegram",
    external_chat_id: "tg-3",
    status: "closed",
    assigned_to: "agent-2",
    customer: null,
    lead: null,
    metadata: { display_name: "Pedro Lima", phone: null, telegram_user_id: "tg-3" },
    created_at: "2026-09-29T08:00:00Z",
    updated_at: "2026-09-30T10:00:00Z",
  },
]

const mockSet = { current: conversations }

vi.mock("@/hooks/use-conversations", () => ({
  useConversations: () => ({
    conversations: mockSet.current,
    count: mockSet.current.length,
    hasNext: false,
    hasPrevious: false,
    isLoading: false,
    isValidating: false,
    isError: false,
    error: null,
  }),
}))

describe("ConversationList", () => {
  beforeEach(() => {
    mockSet.current = [...conversations]
  })

  it("renders conversations", async () => {
    render(<ConversationList selectedId={null} onSelect={vi.fn()} />)
    expect(await screen.findByText("João Silva")).toBeInTheDocument()
    expect(await screen.findByText("Maria Souza")).toBeInTheDocument()
    expect(await screen.findByText("Pedro Lima")).toBeInTheDocument()
  })

  it("shows open count badge", async () => {
    render(<ConversationList selectedId={null} onSelect={vi.fn()} />)
    expect(await screen.findByText("1 aberta")).toBeInTheDocument()
  })

  it("shows status badges with correct labels", async () => {
    render(<ConversationList selectedId={null} onSelect={vi.fn()} />)
    expect(await screen.findByText("Aberta")).toBeInTheDocument()
    expect(screen.getByText("Atribuída")).toBeInTheDocument()
    expect(screen.getByText("Fechada")).toBeInTheDocument()
  })

  it("calls onSelect with conversation id when clicking a conversation", async () => {
    const onSelect = vi.fn()
    render(<ConversationList selectedId={null} onSelect={onSelect} />)
    const item = await screen.findByText("João Silva")
    fireEvent.click(item.closest("button")!)
    expect(onSelect).toHaveBeenCalledWith("conv-1")
  })
})