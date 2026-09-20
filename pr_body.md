## Etapa 0 — Frontend Setup (Odair)

Setup completo do projeto Next.js + TypeScript + Tailwind + shadcn/ui + Vitest.

### W1 — Project Scaffold
- Next.js 15 (App Router) + TypeScript strict
- ESLint + Prettier + Tailwind CSS
- shadcn/ui com components.json configurado
- Vitest + React Testing Library

### W2 — Auth & Core Architecture
- Sistema de autenticação JWT com httpOnly cookies
- Middleware de proteção de rotas
- API client com interceptors (Axios)
- Configuração SWR global

### W3 — Typed Hooks
- useLeads, useCustomers, useAppointments, useAuth, useMobile
- Tipos API centralizados

### W4 — UI Library
- 47 componentes shadcn/ui
- ThemeProvider, ThemeToggle, ToasterProvider (Sonner)
- ErrorBoundary com teste

### W5 — Pages & Routes
- App Router: dashboard, login, leads, customers, appointments, calendario, profissionais

### W6 — Feature Components
- AppointmentList + NewAppointmentForm
- LeadConversion, LeadForm, CustomerDetailContent, CalendarView, DashboardContent
- ProfessionalDirectory, LoginForm
- All 53 tests pass | tsc clean | npm run build passes
