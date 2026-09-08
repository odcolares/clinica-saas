# API.md — Contratos de API v1.0

## Padrões
- API versionada.
- JSON para contratos de aplicação, salvo integrações específicas.
- Erros padronizados.
- Identidade e tenant derivados do contexto autenticado.
- Paginação e filtros em endpoints de consulta.
- Idempotência para operações externas/transacionais quando aplicável.

## Auth
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- POST /auth/password-reset
- POST /auth/email-verification

## CRM
- POST /leads
- GET /leads
- PATCH /leads/{id}/status
- POST /leads/{id}/convert
- GET /customers
- GET /customers/{id}
- POST /customers/{id}/contacts
- POST /customers/{id}/addresses
- POST /customers/{id}/notes
- GET /customers/{id}/timeline

## Quotes
- POST /quotes
- POST /quotes/{id}/items
- POST /quotes/{id}/send
- POST /quotes/{id}/approve
- POST /quotes/{id}/reject
- GET /quotes

## Scheduling
- POST /appointments
- PATCH /appointments/{id}
- POST /appointments/{id}/cancel
- POST /appointments/{id}/reschedule
- GET /appointments

## Finance
- POST /payments
- POST /cash-transactions
- GET /financial/reports
- POST /reconciliations
- GET /financial/reconciliation-reports

## Regra
Endpoints devem validar tenant, permissão, estado do recurso e regras de domínio antes de persistir alterações.
