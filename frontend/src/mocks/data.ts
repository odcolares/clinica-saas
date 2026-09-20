import type {
  Lead,
  LeadCreateRequest,
  Customer,
  Professional,
  Service,
  Appointment,
  AppointmentCreateRequest,
  Quote,
  Payment,
  CashTransaction,
  LeadStatus,
  AppointmentStatus,
} from "@/types/api"

// ─── Leads ───────────────────────────────────────────────

export const leads: Lead[] = [
  {
    id: "lead-001",
    name: "Ana Silva",
    email: "ana.silva@email.com",
    phone: "(11) 98765-4321",
    document: null,
    source: "google",
    status: "NEW",
    assigned_to: "prof-001",
    created_at: "2025-09-15T10:30:00Z",
    updated_at: "2025-09-15T10:30:00Z",
    notes: [],
  },
  {
    id: "lead-002",
    name: "Carlos Mendes",
    email: "carlos.mendes@email.com",
    phone: "(11) 91234-5678",
    document: null,
    source: "facebook",
    status: "CONTACTED",
assigned_to: "prof-001",
    created_at: "2025-09-14T15:00:00Z",
    updated_at: "2025-09-14T15:00:00Z",
    notes: [],
  },
  {
    id: "lead-003",
    name: "Beatriz Costa",
    email: "beatriz.costa@email.com",
    phone: "(11) 99999-8888",
    document: null,
    source: "indicacao",
    status: "QUALIFIED",
assigned_to: "prof-002",
    created_at: "2025-09-13T11:30:00Z",
    updated_at: "2025-09-13T11:30:00Z",
    notes: [],
  },
  {
    id: "lead-004",
    name: "Daniela Souza",
    email: null,
    phone: "(11) 95555-4444",
    document: null,
    source: "site",
    status: "CONVERTED",
assigned_to: "prof-002",
    created_at: "2025-09-12T16:00:00Z",
    updated_at: "2025-09-12T16:00:00Z",
    notes: [],
  },
  {
    id: "lead-005",
    name: "Eduardo Lima",
    email: "eduardo.lima@email.com",
    phone: "(11) 93333-2222",
    document: null,
    source: "other",
    status: "LOST",
assigned_to: null,
    created_at: "2025-09-05T12:00:00Z",
    updated_at: "2025-09-05T12:00:00Z",
    notes: [],
  },
]

export const leadCreateRequests: LeadCreateRequest[] = []

// ─── Customers ───────────────────────────────────────────

export const customers: Customer[] = [
  {
    id: "cust-001",
    lead_id: "lead-004",
    name: "Daniela Souza",
    email: null,
    phone: "(11) 95555-4444",
    document: "123.456.789-00",
    birth_date: "1985-04-15",
    created_at: "2025-09-12T16:00:00Z",
    updated_at: "2025-09-12T16:00:00Z",
  },
  {
    id: "cust-002",
    lead_id: null,
    name: "Fernanda Rocha",
    email: "fernanda.rocha@email.com",
    phone: "(11) 97777-6666",
    document: "987.654.321-00",
    birth_date: "1990-11-20",
    created_at: "2025-09-08T10:00:00Z",
    updated_at: "2025-09-08T10:00:00Z",
  },
  {
    id: "cust-003",
    lead_id: null,
    name: "Gustavo Pereira",
    email: "gustavo.pereira@email.com",
    phone: "(11) 94444-3333",
    document: "456.789.123-00",
    birth_date: "1978-03-10",
    created_at: "2025-09-05T14:00:00Z",
    updated_at: "2025-09-05T14:00:00Z",
  },
]

// ─── Professionals ───────────────────────────────────────

export const professionals: Professional[] = [
  {
    id: "prof-001",
    name: "Dra. Mariana Costa",
    email: "mariana@clinica.com",
    specialty: "Odontologia",
    phone: "(11) 91111-2222",
    active: true,
    created_at: "2025-01-01T00:00:00Z",
  },
  {
    id: "prof-002",
    name: "Dr. Roberto Alves",
    email: "roberto@clinica.com",
    specialty: "Ortodontia",
    phone: "(11) 93333-4444",
    active: true,
    created_at: "2025-01-01T00:00:00Z",
  },
  {
    id: "prof-003",
    name: "Dra. Camila Ferreira",
    email: "camila@clinica.com",
    specialty: "Estética Dental",
    phone: "(11) 95555-6666",
    active: true,
    created_at: "2025-01-01T00:00:00Z",
  },
]

// ─── Services ────────────────────────────────────────────

export const services: Service[] = [
  {
    id: "svc-001",
    name: "Consulta Inicial",
    duration_minutes: 60,
    price: 350.0,
    description: "Avaliação completa e diagnóstico inicial",
  },
  {
    id: "svc-002",
    name: "Limpeza Dental",
    duration_minutes: 90,
    price: 280.0,
    description: "Higienização profissional completa",
  },
  {
    id: "svc-003",
    name: "Clareamento a Laser",
    duration_minutes: 120,
    price: 1200.0,
    description: "Tratamento de clareamento com tecnologia a laser",
  },
  {
    id: "svc-004",
    name: "Restauração",
    duration_minutes: 90,
    price: 450.0,
    description: "Recuperação de dentes com restaurações",
  },
  {
    id: "svc-005",
    name: "Ortodontia (Ajuste)",
    duration_minutes: 30,
    price: 200.0,
    description: "Ajuste de aparelho ortodôntico",
  },
]

// ─── Appointments ────────────────────────────────────────

export const appointments: Appointment[] = [
  {
    id: "apt-001",
    customer: "cust-001",
    professional: "prof-001",
    service: "svc-001",
    start_time: "2025-09-20T09:00:00Z",
    end_time: "2025-09-20T10:00:00Z",
    status: "scheduled",
    notes: "Primeira consulta - avaliar necessidade de tratamento",
    created_at: "2025-09-15T10:00:00Z",
    updated_at: "2025-09-15T10:00:00Z",
  },
  {
    id: "apt-002",
    customer: "cust-002",
    professional: "prof-002",
    service: "svc-002",
    start_time: "2025-09-20T11:00:00Z",
    end_time: "2025-09-20T12:30:00Z",
    status: "confirmed",
    notes: "",
    created_at: "2025-09-10T08:00:00Z",
    updated_at: "2025-09-18T09:00:00Z",
  },
  {
    id: "apt-003",
    customer: "cust-003",
    professional: "prof-003",
    service: "svc-003",
    start_time: "2025-09-21T14:00:00Z",
    end_time: "2025-09-21T16:00:00Z",
    status: "scheduled",
    notes: "Paciente interessado em clareamento",
    created_at: "2025-09-12T14:00:00Z",
    updated_at: "2025-09-12T14:00:00Z",
  },
  {
    id: "apt-004",
    customer: "cust-001",
    professional: "prof-001",
    service: "svc-004",
    start_time: "2025-09-18T10:00:00Z",
    end_time: "2025-09-18T11:30:00Z",
    status: "completed",
    notes: "Restauração na primeira molar",
    created_at: "2025-09-05T09:00:00Z",
    updated_at: "2025-09-18T11:30:00Z",
  },
  {
    id: "apt-005",
    customer: "cust-002",
    professional: "prof-002",
    service: "svc-005",
    start_time: "2025-09-22T15:00:00Z",
    end_time: "2025-09-22T15:30:00Z",
    status: "cancelled",
    notes: "Paciente cancelou por urgência",
    created_at: "2025-09-10T10:00:00Z",
    updated_at: "2025-09-20T08:00:00Z",
  },
  {
    id: "apt-006",
    customer: "cust-003",
    professional: "prof-001",
    service: "svc-001",
    start_time: "2025-09-23T09:30:00Z",
    end_time: "2025-09-23T10:30:00Z",
    status: "scheduled",
    notes: "",
    created_at: "2025-09-15T11:00:00Z",
    updated_at: "2025-09-15T11:00:00Z",
  },
  {
    id: "apt-007",
    customer: "cust-001",
    professional: "prof-003",
    service: "svc-002",
    start_time: "2025-09-24T10:00:00Z",
    end_time: "2025-09-24T11:30:00Z",
    status: "scheduled",
    notes: "Retorno para limpeza",
    created_at: "2025-09-16T09:00:00Z",
    updated_at: "2025-09-16T09:00:00Z",
  },
  {
    id: "apt-008",
    customer: "cust-002",
    professional: "prof-001",
    service: "svc-003",
    start_time: "2025-09-25T13:00:00Z",
    end_time: "2025-09-25T15:00:00Z",
    status: "confirmed",
    notes: "",
    created_at: "2025-09-12T10:00:00Z",
    updated_at: "2025-09-19T14:00:00Z",
  },
  {
    id: "apt-009",
    customer: "cust-003",
    professional: "prof-002",
    service: "svc-004",
    start_time: "2025-09-26T11:00:00Z",
    end_time: "2025-09-26T12:30:00Z",
    status: "scheduled",
    notes: "Restauração molar superior",
    created_at: "2025-09-18T15:00:00Z",
    updated_at: "2025-09-18T15:00:00Z",
  },
  {
    id: "apt-010",
    customer: "cust-001",
    professional: "prof-003",
    service: "svc-005",
    start_time: "2025-09-27T16:00:00Z",
    end_time: "2025-09-27T16:30:00Z",
    status: "scheduled",
    notes: "Ajuste de aparelho",
    created_at: "2025-09-19T09:00:00Z",
    updated_at: "2025-09-19T09:00:00Z",
  },
]

// ─── Quotes ─────────────────────────────────────────────

export const quotes: Quote[] = [
  {
    id: "quote-001",
    customer: "cust-001",
    status: "approved",
    total: 1750.0,
    currency: "BRL",
    created_at: "2025-09-12T16:00:00Z",
    updated_at: "2025-09-12T16:00:00Z",
  },
  {
    id: "quote-002",
    customer: "cust-002",
    status: "sent",
    total: 1200.0,
    currency: "BRL",
    created_at: "2025-09-10T08:00:00Z",
    updated_at: "2025-09-10T08:00:00Z",
  },
]

// ─── Payments ────────────────────────────────────────────

export const payments: Payment[] = [
  {
    id: "pay-001",
    customer: "cust-001",
    appointment: "apt-004",
    amount: 450.0,
    currency: "BRL",
    method: "pix",
    status: "paid",
    created_at: "2025-09-18T11:30:00Z",
  },
  {
    id: "pay-002",
    customer: "cust-002",
    appointment: "apt-002",
    amount: 280.0,
    currency: "BRL",
    method: "card",
    status: "paid",
    created_at: "2025-09-20T12:30:00Z",
  },
]

// ─── Cash Transactions ───────────────────────────────────

export const cashTransactions: CashTransaction[] = [
  {
    id: "cash-001",
    type: "income",
    amount: 450.0,
    description: "Pagamento consulta - Daniela Souza",
    category: "consultas",
    created_at: "2025-09-18T11:30:00Z",
  },
  {
    id: "cash-002",
    type: "income",
    amount: 280.0,
    description: "Pagamento limpeza - Fernanda Rocha",
    category: "consultas",
    created_at: "2025-09-20T12:30:00Z",
  },
  {
    id: "cash-003",
    type: "expense",
    amount: 1500.0,
    description: "Pagamento fornecedor de material odontológico",
    category: "materiais",
    created_at: "2025-09-15T09:00:00Z",
  },
]

// ─── Auth ────────────────────────────────────────────────

export const authTokens = {
  access: "mock-access-token-abc123",
  refresh: "mock-refresh-token-def456",
}

export const currentUser = {
  id: "user-001",
  email: "admin@clinica.com",
  name: "Administrador",
  role: "admin" as const,
  tenant: "clinica-saas",
}

// ─── Helpers ─────────────────────────────────────────────

export function generateId(prefix: string): string {
  return `${prefix}-${Date.now().toString(36)}`
}

export function paginate<T>(items: T[], page: number, pageSize: number) {
  const start = (page - 1) * pageSize
  const end = start + pageSize
  return {
    count: items.length,
    next: end < items.length ? `?page=${page + 1}` : null,
    previous: page > 1 ? `?page=${page - 1}` : null,
    results: items.slice(start, end),
  }
}
