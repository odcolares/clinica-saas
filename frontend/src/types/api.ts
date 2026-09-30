/**
 * TypeScript API types for Clínica SaaS
 * Generated from Projeto_SaaS/architecture/API.md
 */

// ─── Enums ───────────────────────────────────────────────

export type LeadStatus = "NEW" | "CONTACTED" | "QUALIFIED" | "CONVERTED" | "LOST"
export type AppointmentStatus = "scheduled" | "confirmed" | "cancelled" | "completed"
export type InteractionType = "call" | "email" | "visit" | "note"

// ─── Auth ────────────────────────────────────────────────

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface User {
  id: string
  email: string
  name: string
  role: "admin" | "professional" | "receptionist"
  tenant: string
}

export interface RefreshRequest {
  refresh: string
}

export interface PasswordResetRequest {
  email: string
}

export interface EmailVerificationRequest {
  token: string
}

// ─── CRM ─────────────────────────────────────────────────

export interface Lead {
  id: string
  name: string
  email: string | null
  phone: string | null
  document?: string | null
  source: string
  status: LeadStatus
  source_detail?: string | null
  assigned_to?: string | null
  created_at: string
  updated_at: string
  notes?: LeadNote[]
}

export interface LeadNote {
  id: string
  lead: string
  body: string
  author: string
  created_at: string
}

export interface LeadCreateRequest {
  name: string
  email?: string | null
  phone?: string | null
  document?: string | null
  source: string
  source_detail?: string | null
}

export interface LeadStatusUpdate {
  status: LeadStatus
  reason?: string
}

export interface LeadConversionResponse {
  customer: Customer
  created: boolean
  lead_id: number
}

export interface Customer {
  id: string
  lead_id?: string | null
  name: string
  email: string | null
  phone: string | null
  document?: string | null
  birth_date?: string | null
  created_at: string
  updated_at: string
}

export interface CustomerContact {
  id: string
  customer: string
  kind: "phone" | "email" | "whatsapp"
  value: string
  label?: string
  is_primary: boolean
  created_at: string
}

export interface CustomerAddress {
  id: string
  customer: string
  label?: string
  street: string
  number: string
  complement?: string | null
  district: string
  zipcode: string
  country?: string
  is_primary: boolean
  created_at: string
}

export interface CustomerNote {
  id: string
  customer: string
  body: string
  author: string
  created_at: string
}

export interface TimelineEntry {
  id: string
  kind: InteractionType
  description: string
  timestamp: string
  author?: string
}

// ─── Quotes ──────────────────────────────────────────────

export interface Quote {
  id: string
  customer: string
  status: "draft" | "sent" | "approved" | "rejected"
  total: number
  currency: string
  created_at: string
  updated_at: string
  items?: QuoteItem[]
}

export interface QuoteItem {
  id: string
  quote: string
  description: string
  quantity: number
  unit_price: number
  total: number
}

// ─── Scheduling ─────────────────────────────────────────

export interface Professional {
  id: string
  name: string
  email: string | null
  specialty: string
  phone?: string | null
  active: boolean
  created_at: string
}

export interface Service {
  id: string
  name: string
  duration_minutes: number
  price: number
  description?: string | null
}

export interface Appointment {
  id: string
  customer: string
  professional: string
  service: string
  start_time: string
  end_time: string
  status: AppointmentStatus
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface AppointmentCreateRequest {
  customer: string
  professional: string
  service: string
  start_time: string
  notes?: string | null
}

export interface AppointmentUpdateRequest {
  start_time?: string
  end_time?: string
  professional?: string
  service?: string
  notes?: string
}

// ─── Finance ───────────────────────────────────────────

export interface Payment {
  id: string
  customer: string
  appointment?: string | null
  amount: number
  currency: string
  method: "card" | "cash" | "pix" | "transfer"
  status: "pending" | "paid" | "failed"
  created_at: string
}

export interface CashTransaction {
  id: string
  type: "income" | "expense"
  amount: number
  description: string
  category: string
  created_at: string
}

export interface FinancialReport {
  period_start: string
  period_end: string
  total_income: number
  total_expenses: number
  net_balance: number
}

// ─── Pagination ────────────────────────────────────────

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface LeadFilters {
  status?: LeadStatus
  source?: string
  date_start?: string
  date_end?: string
  search?: string
  assigned_to?: string
}

export interface AppointmentFilters {
  date?: string
  professional?: string
  status?: AppointmentStatus
}

export interface AvailabilitySlot {
  start: string
  end: string
  available: boolean
}

export interface ProfessionalAvailability {
  professional: string
  professional_name: string
  date: string
  slots: AvailabilitySlot[]
}

export interface AvailabilityFilters {
  professional?: string
  date: string
  service?: string
}

// ─── Omnichannel (Etapa 3) ────────────────────────────────

export type ConversationChannel = "telegram" | "whatsapp"
export type ConversationStatus = "open" | "assigned" | "closed"
export type MessageDirection = "inbound" | "outbound"
export type MessageSender = "customer" | "agent" | "system"

export interface Conversation {
  id: string
  channel: ConversationChannel
  external_chat_id: string
  status: ConversationStatus
  assigned_to: string | null
  customer: string | null
  lead: string | null
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface ConversationMessage {
  id: string
  conversation: string
  direction: MessageDirection
  sender_kind: MessageSender
  body: string
  normalized_body: string
  telegram_message_id: string | null
  payload: Record<string, unknown>
  created_at: string
}

export interface ConversationFilters {
  channel?: ConversationChannel
  status?: ConversationStatus
  assigned_to?: string
  customer?: string
  lead?: string
  search?: string
}

export interface OutboundMessageRequest {
  body: string
}

export interface AssignConversationRequest {
  assigned_to: string
}

export interface Template {
  id: string
  name: string
  channel: string
  body: string
  active: boolean
  created_at: string
}
