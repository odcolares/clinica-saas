import { http, HttpResponse } from "msw"
import type {
  Lead,
  LeadCreateRequest,
  LeadStatusUpdate,
  Customer,
  Professional,
  Service,
  Appointment,
  AppointmentCreateRequest,
  AppointmentUpdateRequest,
  Quote,
  Payment,
  CashTransaction,
  FinancialReport,
  PaginatedResponse,
  LoginRequest,
  LoginResponse,
  RefreshRequest,
  Conversation,
  ConversationMessage,
  AssignConversationRequest,
  OutboundMessageRequest,
} from "@/types/api"
import {
  leads,
  customers,
  professionals,
  services,
  appointments,
  quotes,
  payments,
  cashTransactions,
  authTokens,
  currentUser,
  conversations,
  conversationMessages,
  generateId,
  paginate,
} from "./data"

const API_BASE = "/api/v1"

export const handlers = [
  // ─── Auth ──────────────────────────────────────────────
  http.post(`${API_BASE}/auth/login`, async ({ request }) => {
    const body = await request.json() as LoginRequest
    if (body.email === "admin@clinica.com" && body.password === "admin123") {
      return HttpResponse.json<LoginResponse>({
        access: authTokens.access,
        refresh: authTokens.refresh,
        user: currentUser,
      })
    }
    return HttpResponse.json({ detail: "Credenciais inválidas" }, { status: 401 })
  }),

  http.post(`${API_BASE}/auth/refresh`, async ({ request }) => {
    const body = await request.json() as RefreshRequest
    if (body.refresh === authTokens.refresh) {
      return HttpResponse.json<LoginResponse>({
        access: authTokens.access,
        refresh: authTokens.refresh,
        user: currentUser,
      })
    }
    return HttpResponse.json({ detail: "Token inválido" }, { status: 401 })
  }),

  http.post(`${API_BASE}/auth/logout`, () => {
    return HttpResponse.json({ detail: "Logout realizado com sucesso" })
  }),

  http.post(`${API_BASE}/auth/password-reset`, async ({ request }) => {
    const body = await request.json() as { email: string }
    return HttpResponse.json({ detail: `Instruções de redefinição enviadas para ${body.email}` })
  }),

  http.post(`${API_BASE}/auth/email-verification`, async ({ request }) => {
    const body = await request.json() as { token: string }
    if (body.token === "valid-token") {
      return HttpResponse.json({ detail: "E-mail verificado com sucesso" })
    }
    return HttpResponse.json({ detail: "Token inválido" }, { status: 400 })
  }),

  // ─── CRM - Leads ───────────────────────────────────────
  http.get(`${API_BASE}/leads`, ({ request }) => {
    const url = new URL(request.url)
    const status = url.searchParams.get("status")
    const source = url.searchParams.get("source")
    const search = url.searchParams.get("search")
    const page = parseInt(url.searchParams.get("page") || "1")

    let filtered = [...leads]
    if (status) filtered = filtered.filter((l) => l.status === status)
    if (source) filtered = filtered.filter((l) => l.source === source)
    if (search) {
      const s = search.toLowerCase()
      filtered = filtered.filter((l) => l.name.toLowerCase().includes(s) || l.email?.toLowerCase().includes(s))
    }

    return HttpResponse.json<PaginatedResponse<Lead>>(paginate(filtered, page, 10))
  }),

  http.post(`${API_BASE}/leads`, async ({ request }) => {
    const body = await request.json() as LeadCreateRequest
    const newLead: Lead = {
      id: generateId("lead"),
      name: body.name,
      email: body.email || null,
      phone: body.phone || null,
      document: null,
      source: body.source,
      status: "NEW",
      source_detail: body.source_detail || null,
      assigned_to: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      notes: [],
    }
    leads.push(newLead)
    return HttpResponse.json<Lead>(newLead, { status: 201 })
  }),

  http.get(`${API_BASE}/leads/:id`, ({ params }) => {
    const lead = leads.find((l) => l.id === params.id)
    if (!lead) return HttpResponse.json({ detail: "Lead não encontrado" }, { status: 404 })
    return HttpResponse.json<Lead>(lead)
  }),

  http.patch(`${API_BASE}/leads/:id`, async ({ params, request }) => {
    const lead = leads.find((l) => l.id === params.id)
    if (!lead) return HttpResponse.json({ detail: "Lead não encontrado" }, { status: 404 })
    const body = await request.json() as Partial<Lead>
    Object.assign(lead, body, { updated_at: new Date().toISOString() })
    return HttpResponse.json<Lead>(lead)
  }),

  http.patch(`${API_BASE}/leads/:id/status`, async ({ params, request }) => {
    const lead = leads.find((l) => l.id === params.id)
    if (!lead) return HttpResponse.json({ detail: "Lead não encontrado" }, { status: 404 })
    const body = await request.json() as LeadStatusUpdate
    lead.status = body.status
    lead.updated_at = new Date().toISOString()
    return HttpResponse.json<Lead>(lead)
  }),

  http.post(`${API_BASE}/leads/:id/convert`, ({ params }) => {
    const lead = leads.find((l) => l.id === params.id)
    if (!lead) return HttpResponse.json({ detail: "Lead não encontrado" }, { status: 404 })
    lead.status = "CONVERTED"
    lead.updated_at = new Date().toISOString()

    const newCustomer: Customer = {
      id: generateId("cust"),
      lead_id: lead.id,
      name: lead.name,
      email: lead.email,
      phone: lead.phone,
      document: null,
      birth_date: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    customers.push(newCustomer)
    return HttpResponse.json<Customer>(newCustomer)
  }),

  // ─── CRM - Customers ───────────────────────────────────
  http.get(`${API_BASE}/customers`, ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get("page") || "1")
    return HttpResponse.json<PaginatedResponse<Customer>>(paginate(customers, page, 10))
  }),

  http.get(`${API_BASE}/customers/:id`, ({ params }) => {
    const customer = customers.find((c) => c.id === params.id)
    if (!customer) return HttpResponse.json({ detail: "Cliente não encontrado" }, { status: 404 })
    return HttpResponse.json<Customer>(customer)
  }),

  http.post(`${API_BASE}/customers/:id/contacts`, async ({ params, request }) => {
    const body = await request.json() as Record<string, unknown>
    return HttpResponse.json({
      id: generateId("contact"),
      customer: params.id,
      ...body,
      created_at: new Date().toISOString(),
    })
  }),

  http.post(`${API_BASE}/customers/:id/addresses`, async ({ params, request }) => {
    const body = await request.json() as Record<string, unknown>
    return HttpResponse.json({
      id: generateId("addr"),
      customer: params.id,
      ...body,
      created_at: new Date().toISOString(),
    })
  }),

  http.post(`${API_BASE}/customers/:id/notes`, async ({ params, request }) => {
    const body = await request.json() as Record<string, unknown>
    return HttpResponse.json({
      id: generateId("note"),
      customer: params.id,
      ...body,
      created_at: new Date().toISOString(),
    })
  }),

  http.get(`${API_BASE}/customers/:id/timeline`, ({ params }) => {
    const customer = customers.find((c) => c.id === params.id)
    if (!customer) return HttpResponse.json({ detail: "Cliente não encontrado" }, { status: 404 })

    const timeline = appointments
      .filter((a) => a.customer === params.id)
      .map((a) => ({
        id: a.id,
        type: "visit" as const,
        description: `Consulta: ${services.find((s) => s.id === a.service)?.name || a.service}`,
        timestamp: a.start_time,
        author: a.professional,
      }))

    return HttpResponse.json(timeline)
  }),

  // ─── Scheduling - Professionals ────────────────────────
  http.get(`${API_BASE}/professionals`, () => {
    return HttpResponse.json<Professional[]>(professionals)
  }),

  http.get(`${API_BASE}/professionals/:id`, ({ params }) => {
    const prof = professionals.find((p) => p.id === params.id)
    if (!prof) return HttpResponse.json({ detail: "Profissional não encontrado" }, { status: 404 })
    return HttpResponse.json<Professional>(prof)
  }),

  // ─── Scheduling - Services ─────────────────────────────
  http.get(`${API_BASE}/services`, () => {
    return HttpResponse.json<Service[]>(services)
  }),

  http.get(`${API_BASE}/services/:id`, ({ params }) => {
    const svc = services.find((s) => s.id === params.id)
    if (!svc) return HttpResponse.json({ detail: "Serviço não encontrado" }, { status: 404 })
    return HttpResponse.json<Service>(svc)
  }),

  // ─── Scheduling - Appointments ─────────────────────────
  http.get(`${API_BASE}/appointments`, ({ request }) => {
    const url = new URL(request.url)
    const date = url.searchParams.get("date")
    const professional = url.searchParams.get("professional")
    const status = url.searchParams.get("status")
    const page = parseInt(url.searchParams.get("page") || "1")

    let filtered = [...appointments]
    if (date) filtered = filtered.filter((a) => a.start_time.startsWith(date))
    if (professional) filtered = filtered.filter((a) => a.professional === professional)
    if (status) filtered = filtered.filter((a) => a.status === status)

    return HttpResponse.json<PaginatedResponse<Appointment>>(paginate(filtered, page, 10))
  }),

  http.post(`${API_BASE}/appointments`, async ({ request }) => {
    const body = await request.json() as AppointmentCreateRequest
    const service = services.find((s) => s.id === body.service)
    const newApt: Appointment = {
      id: generateId("apt"),
      customer: body.customer,
      professional: body.professional,
      service: body.service,
      start_time: body.start_time,
      end_time: new Date(new Date(body.start_time).getTime() + (service?.duration_minutes || 60) * 60000).toISOString(),
      status: "scheduled",
      notes: body.notes || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    appointments.push(newApt)
    return HttpResponse.json<Appointment>(newApt, { status: 201 })
  }),

  http.get(`${API_BASE}/appointments/:id`, ({ params }) => {
    const apt = appointments.find((a) => a.id === params.id)
    if (!apt) return HttpResponse.json({ detail: "Agendamento não encontrado" }, { status: 404 })
    return HttpResponse.json<Appointment>(apt)
  }),

  http.patch(`${API_BASE}/appointments/:id`, async ({ params, request }) => {
    const apt = appointments.find((a) => a.id === params.id)
    if (!apt) return HttpResponse.json({ detail: "Agendamento não encontrado" }, { status: 404 })
    const body = await request.json() as AppointmentUpdateRequest
    Object.assign(apt, body, { updated_at: new Date().toISOString() })
    return HttpResponse.json<Appointment>(apt)
  }),

  http.post(`${API_BASE}/appointments/:id/cancel`, ({ params }) => {
    const apt = appointments.find((a) => a.id === params.id)
    if (!apt) return HttpResponse.json({ detail: "Agendamento não encontrado" }, { status: 404 })
    apt.status = "cancelled"
    apt.updated_at = new Date().toISOString()
    return HttpResponse.json<Appointment>(apt)
  }),

  http.post(`${API_BASE}/appointments/:id/reschedule`, async ({ params, request }) => {
    const apt = appointments.find((a) => a.id === params.id)
    if (!apt) return HttpResponse.json({ detail: "Agendamento não encontrado" }, { status: 404 })
    const body = await request.json() as AppointmentUpdateRequest
    if (body.start_time) apt.start_time = body.start_time
    if (body.end_time) apt.end_time = body.end_time
    if (body.professional) apt.professional = body.professional
    if (body.service) apt.service = body.service
    if (body.notes !== undefined) apt.notes = body.notes
    apt.updated_at = new Date().toISOString()
    return HttpResponse.json<Appointment>(apt)
  }),

  // ─── Quotes ────────────────────────────────────────────
  http.get(`${API_BASE}/quotes`, ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get("page") || "1")
    return HttpResponse.json<PaginatedResponse<Quote>>(paginate(quotes, page, 10))
  }),

  http.post(`${API_BASE}/quotes`, async ({ request }) => {
    const body = await request.json() as { customer: string; items: unknown[] }
    const newQuote: Quote = {
      id: generateId("quote"),
      customer: body.customer,
      status: "draft",
      total: 0,
      currency: "BRL",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    quotes.push(newQuote)
    return HttpResponse.json<Quote>(newQuote, { status: 201 })
  }),

  http.get(`${API_BASE}/quotes/:id`, ({ params }) => {
    const quote = quotes.find((q) => q.id === params.id)
    if (!quote) return HttpResponse.json({ detail: "Orçamento não encontrado" }, { status: 404 })
    return HttpResponse.json<Quote>(quote)
  }),

  http.post(`${API_BASE}/quotes/:id/items`, async ({ params, request }) => {
    const body = await request.json() as { quantity?: number; unit_price?: number; description?: string }
    return HttpResponse.json({
      id: generateId("item"),
      quote: params.id,
      description: body.description || "",
      quantity: body.quantity || 1,
      unit_price: body.unit_price || 0,
      total: (body.quantity || 1) * (body.unit_price || 0),
    })
  }),

  http.post(`${API_BASE}/quotes/:id/send`, ({ params }) => {
    const quote = quotes.find((q) => q.id === params.id)
    if (!quote) return HttpResponse.json({ detail: "Orçamento não encontrado" }, { status: 404 })
    quote.status = "sent"
    quote.updated_at = new Date().toISOString()
    return HttpResponse.json<Quote>(quote)
  }),

  http.post(`${API_BASE}/quotes/:id/approve`, ({ params }) => {
    const quote = quotes.find((q) => q.id === params.id)
    if (!quote) return HttpResponse.json({ detail: "Orçamento não encontrado" }, { status: 404 })
    quote.status = "approved"
    quote.updated_at = new Date().toISOString()
    return HttpResponse.json<Quote>(quote)
  }),

  http.post(`${API_BASE}/quotes/:id/reject`, ({ params }) => {
    const quote = quotes.find((q) => q.id === params.id)
    if (!quote) return HttpResponse.json({ detail: "Orçamento não encontrado" }, { status: 404 })
    quote.status = "rejected"
    quote.updated_at = new Date().toISOString()
    return HttpResponse.json<Quote>(quote)
  }),

  // ─── Finance - Payments ─────────────────────────────────
  http.get(`${API_BASE}/payments`, ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get("page") || "1")
    return HttpResponse.json<PaginatedResponse<Payment>>(paginate(payments, page, 10))
  }),

  http.post(`${API_BASE}/payments`, async ({ request }) => {
    const body = await request.json() as Omit<Payment, "id" | "created_at">
    const newPayment: Payment = {
      id: generateId("pay"),
      ...body,
      created_at: new Date().toISOString(),
    }
    payments.push(newPayment)
    return HttpResponse.json<Payment>(newPayment, { status: 201 })
  }),

  // ─── Finance - Cash Transactions ───────────────────────
  http.get(`${API_BASE}/cash-transactions`, ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get("page") || "1")
    return HttpResponse.json<PaginatedResponse<CashTransaction>>(paginate(cashTransactions, page, 10))
  }),

  http.post(`${API_BASE}/cash-transactions`, async ({ request }) => {
    const body = await request.json() as Omit<CashTransaction, "id" | "created_at">
    const newTx: CashTransaction = {
      id: generateId("cash"),
      ...body,
      created_at: new Date().toISOString(),
    }
    cashTransactions.push(newTx)
    return HttpResponse.json<CashTransaction>(newTx, { status: 201 })
  }),

  // ─── Finance - Reports ─────────────────────────────────
  http.get(`${API_BASE}/financial/reports`, ({ request }) => {
    const url = new URL(request.url)
    const start = url.searchParams.get("start") || "2025-09-01"
    const end = url.searchParams.get("end") || "2025-09-30"

    const income = cashTransactions.filter((t) => t.type === "income").reduce((sum, t) => sum + t.amount, 0)
    const expenses = cashTransactions.filter((t) => t.type === "expense").reduce((sum, t) => sum + t.amount, 0)

    return HttpResponse.json<FinancialReport>({
      period_start: start,
      period_end: end,
      total_income: income,
      total_expenses: expenses,
      net_balance: income - expenses,
    })
  }),

  http.get(`${API_BASE}/financial/reconciliation-reports`, () => {
    return HttpResponse.json({
      period_start: "2025-09-01",
      period_end: "2025-09-30",
      reconciliations: [],
    })
  }),

  http.post(`${API_BASE}/reconciliations`, async ({ request }) => {
    const body = await request.json() as Record<string, unknown>
    return HttpResponse.json({ id: generateId("recon"), ...body }, { status: 201 })
  }),

  // ─── Omnichannel (Etapa 3) ───────────────────────────────
  http.get(`${API_BASE}/conversations`, ({ request }) => {
    const url = new URL(request.url)
    const channel = url.searchParams.get("channel")
    const status = url.searchParams.get("status")
    const assigned_to = url.searchParams.get("assigned_to")
    const search = url.searchParams.get("search")
    const page = parseInt(url.searchParams.get("page") || "1")

    let filtered = [...conversations]
    if (channel) filtered = filtered.filter((c) => c.channel === channel)
    if (status) filtered = filtered.filter((c) => c.status === status)
    if (assigned_to) filtered = filtered.filter((c) => c.assigned_to === assigned_to)
    if (search) {
      const s = search.toLowerCase()
      filtered = filtered.filter(
        (c) =>
          c.external_chat_id.toLowerCase().includes(s) ||
          (c.metadata.display_name || "").toLowerCase().includes(s),
      )
    }

    return HttpResponse.json<PaginatedResponse<Conversation>>(
      paginate(filtered, page, 20),
    )
  }),

  http.get(`${API_BASE}/conversations/:id`, ({ params }) => {
    const conv = conversations.find((c) => c.id === params.id)
    if (!conv) return HttpResponse.json({ detail: "Conversa não encontrada" }, { status: 404 })
    return HttpResponse.json<Conversation>(conv)
  }),

  http.get(`${API_BASE}/conversations/:id/messages`, ({ request, params }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get("page") || "1")
    const msgs = conversationMessages
      .filter((m) => m.conversation === params.id)
      .sort((a, b) => (a.created_at > b.created_at ? 1 : -1))

    return HttpResponse.json<PaginatedResponse<ConversationMessage>>(
      paginate(msgs, page, 50),
    )
  }),

  http.post(`${API_BASE}/conversations/:id/assign`, async ({ params, request }) => {
    const conv = conversations.find((c) => c.id === params.id)
    if (!conv) return HttpResponse.json({ detail: "Conversa não encontrada" }, { status: 404 })
    const body = await request.json() as AssignConversationRequest
    conv.assigned_to = body.assigned_to
    conv.status = "assigned"
    conv.updated_at = new Date().toISOString()
    return HttpResponse.json<Conversation>(conv)
  }),

  http.post(`${API_BASE}/conversations/:id/reply`, async ({ params, request }) => {
    const conv = conversations.find((c) => c.id === params.id)
    if (!conv) return HttpResponse.json({ detail: "Conversa não encontrada" }, { status: 404 })
    const body = await request.json() as OutboundMessageRequest
    const newMsg: ConversationMessage = {
      id: generateId("msg"),
      conversation: params.id as string,
      direction: "outbound",
      sender_kind: "agent",
      body: body.body,
      normalized_body: body.body,
      telegram_message_id: null,
      payload: {},
      created_at: new Date().toISOString(),
    }
    conversationMessages.push(newMsg)
    conv.updated_at = new Date().toISOString()
    return HttpResponse.json<ConversationMessage>(newMsg, { status: 201 })
  }),
]
