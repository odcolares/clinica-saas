/**
 * TypeScript API types for Clínica SaaS
 * Generated from Projeto_SaaS/architecture/API.md
 */

// ─── Enums ───────────────────────────────────────────────

export type LeadStatus = "NEW" | "CONTACTED" | "QUALIFIED" | "CONVERTED" | "LOST"
export type AppointmentStatus = "schduled" | "confirmed" | "cancelled" | "completed" | "no_show"
export type InteractionType = "call" | "email" | "visit" | "note"
export type AppointmentStatus = "scheduled" | "confirmed" | "cancelled" | "completed" | "no_show"
export type IntegrationProvider = "noop" | "google_calendar"

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
  phone: string | null
  specialties: string  // comma-separated list, as stored in backend
  specialty_list: string[]  // computed from specialties.split(",")
  active: boolean
  commission_type: CommissionType
  commission_percent: number  // decimal, 0-100
  commission_fixed: number    // decimal value
  user?: string | null  // FK to user
  created_at: string
  updated_at: string
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

// ─── Settings (Etapa 5) ────────────────────────────────

export interface TenantSettings {
  id: string
  business_start: string  // time string "08:00"
  business_end: string    // time string "18:00"
  timezone: string        // e.g. "America/Sao_Paulo"
  logo_url: string
  primary_color: string   // hex color, e.g. "#0F766E"
  brand_name: string
  created_at: string
  updated_at: string
}

export interface TenantSettingsUpdateRequest {
  business_start?: string
  business_end?: string
  timezone?: string
  logo_url?: string
  primary_color?: string
  brand_name?: string
}

export interface IntegrationConfig {
  id: string
  provider: IntegrationProvider
  active: boolean
  professional_email: string
  config: Record<string, unknown>  // write-only on backend, won't be returned
  created_at: string
  updated_at: string
}

export interface IntegrationConfigCreateRequest {
  provider: IntegrationProvider
  professional_email?: string
  config: Record<string, unknown>
}

export interface WebhookEndpoint {
  id: string
  name: string
  url: string
  events: string[]
  active: boolean
  created_at: string
  updated_at: string
}

export interface WebhookEndpointCreateRequest {
  name: string
  url: string
  events?: string[]
  secret?: string
  active?: boolean
}

export interface ApiKey {
  id: string
  name: string
  prefix: string
  active: boolean
  last_used_at: string | null
  created_at: string
  updated_at: string
}

export interface ApiKeyCreateResponse extends ApiKey {
  plain_key: string  // returned only once on creation
}

// ─── Scheduling (Etapa 5 - Professional Dashboard) ───────

export interface ProfessionalDashboardStats {
  professional_id: string
  professional_name: string
  total_appointments: number
  completed_appointments: number
  scheduled_appointments: number
  cancelled_appointments: number
  today_appointments: number
  upcoming_appointments: Appointment[]
  recent_commissions?: CommissionEntry[]
}

export interface CommissionEntry {
  appointment_id: string
  service_name: string
  commission_amount: number
  status: AppointmentStatus
  date: string
}

// ─── Notification Settings (Etapa 5) ─────────────────────

export interface NotificationSettings {
  appointment_confirmation: boolean
  appointment_reminder: boolean
  appointment_reminder_time: number  // minutes before appointment
  appointment_cancellation: boolean
  new_lead_alert: boolean
  payment_received: boolean
  email_notifications: boolean
  sms_notifications: boolean
  push_notifications: boolean
}
