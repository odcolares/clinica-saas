import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { describe, it, expect, vi, beforeEach } from "vitest"
import { ConversationChat } from "@/components/omnichannel/conversation-chat"

const mockMessages = [
  {
    id: "msg-1",
    conversation: "conv-1",
    direction: "inbound" as const,
    sender_kind: "customer" as const,
    body: "Olá, tudo bem?",
    normalized_body: "olá, tudo bem?",
    telegram_message_id: null,
    payload: {},
    created_at: "2026-09-30T12:00:00Z",
  },
  {
    id: "msg-2",
    conversation: "conv-1",
    direction: "outbound" as const,
    sender_kind: "agent" as const,
    body: "Tudo bem, como posso ajudar?",
    normalized_body: "tudo bem, como posso ajudar?",
    telegram_message_id: null,
    payload: {},
    created_at: "2026-09-30T12:01:00Z",
  },
]

const conversation = {
  id: "conv-1",
  channel: "telegram" as const,
  external_chat_id: "tg-1",
  status: "open" as const,
  assigned_to: null,
  customer: null,
  lead: null,
  metadata: { display_name: "João Silva", phone: "11999999999", telegram_user_id: "tg-1" },
  created_at: "2026-09-30T10:00:00Z",
  updated_at: "2026-09-30T12:00:00Z",
}

const mockMessagesState = { current: mockMessages }

vi.mock("@/hooks/use-conversations", () => ({
  useConversationMessages: () => ({
    messages: mockMessagesState.current,
    isLoading: false,
    isValidating: false,
    isError: false,
    error: null,
  }),
  replyConversation: vi.fn(async (_id: string, payload: { body: string }) => {
    const newMsg = {
      id: `msg-${mockMessagesState.current.length + 1}`,
      conversation: "conv-1",
      direction: "outbound" as const,
      sender_kind: "agent" as const,
      body: payload.body,
      normalized_body: payload.body,
      telegram_message_id: null,
      payload: {},
      created_at: new Date().toISOString(),
    }
    mockMessagesState.current = [...mockMessagesState.current, newMsg]
    return newMsg
  }),
  assignConversation: vi.fn(),
}))

describe("ConversationChat", () => {
  beforeEach(() => {
    mockMessagesState.current = [...mockMessages]
  })

  it("renders messages", async () => {
    render(<ConversationChat conversation={conversation} />)
    expect(await screen.findByText("Olá, tudo bem?")).toBeInTheDocument()
    expect(await screen.findByText("Tudo bem, como posso ajudar?")).toBeInTheDocument()
  })

  it("renders header with display name", async () => {
    render(<ConversationChat conversation={conversation} />)
    expect(await screen.findByText("João Silva")).toBeInTheDocument()
  })

  it("sends a message", async () => {
    render(<ConversationChat conversation={conversation} />)
    const input = await screen.findByPlaceholderText("Digite uma mensagem...")
    fireEvent.change(input, { target: { value: "Teste de mensagem" } })
    const buttons = screen.getAllByRole("button")
    const sendBtn = buttons[buttons.length - 1]
    fireEvent.click(sendBtn)
    await waitFor(() => {
      expect(screen.getByText("Teste de mensagem")).toBeInTheDocument()
    })
  })

  it("shows assign button", async () => {
    render(<ConversationChat conversation={conversation} />)
    expect(await screen.findByText("Atribuir")).toBeInTheDocument()
  })
})