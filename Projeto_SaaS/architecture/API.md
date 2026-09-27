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

## Omnichannel
- GET /conversations — lista conversas (filtros: channel, status, assigned_to, customer, lead)
- GET /conversations/{id}
- GET /conversations/{id}/messages — mensagens da conversa
- POST /conversations/{id}/assign — atribui a um atendente (RBAC guardian)
- POST /conversations/{id}/reply — envia resposta pelo adapter do canal
- GET /messages — lista mensagens das conversas visíveis
- POST /omnichannel/telegram/webhook — webhook público do Telegram

Regras do webhook do Telegram:
- Autenticidade: segredo POR TENANT (`TELEGRAM_WEBHOOK_SECRET_<SCHEMA>`) comparado ao header `X-Telegram-Bot-Api-Secret-Token` (tempo constante); o segredo global só autoriza como fallback explícito (`TELEGRAM_ALLOW_GLOBAL_WEBHOOK_SECRET=True`). Sem segredo do tenant → 403.
- Tenant: resolvido pelo header `x-tenant-id` (hint de roteamento, sem JWT). Sem tenant → 400.
- Idempotência: por `telegram_message_id`; reentregas não duplicam mensagens.
- Resposta: 200 rápido `{ok, conversation, message, duplicate}`.
- Rate limiting: escopo `telegram` (por IP), configurável via `THROTTLE_TELEGRAM`.

## Finance
- POST /payments
- POST /cash-transactions
- GET /financial/reports
- POST /reconciliations
- GET /financial/reconciliation-reports

## Regra
Endpoints devem validar tenant, permissão, estado do recurso e regras de domínio antes de persistir alterações.
