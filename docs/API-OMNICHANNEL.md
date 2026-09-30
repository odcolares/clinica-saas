# API — Omnichannel (Etapa 3, Marcos/Backend + Odair/Frontend)

Base: `/api/v1/`. Auth JWT (header `Authorization: Bearer <access>`, tenant no claim).

## Conversas

| Método | Path | Body | Respostas |
|---|---|---|---|
| GET | `/conversations` | filtros `?channel=&status=&assigned_to=&customer=&lead=&search=&page=` | 200 paginado |
| GET | `/conversations/{id}` | — | 200 / 404 |
| PATCH | `/conversations/{id}/assign` | `{assigned_to: string}` (RBAC guardian: só receptor/manager atribui) | 200 / 404 |
| POST | `/conversations/{id}/reply` | `{body: string}` | 201 (mensagem outbound) / 404 |
| GET | `/conversations/{id}/messages` | `page=` | 200 paginado (ordenado por `created_at`) |

## Webhook público (Telegram)

`POST /omnichannel/telegram/webhook` com header `X-Telegram-Bot-Api-Secret-Token`:
- Autenticidade: segredo por tenant comparado ao token (tempo constante).
- Idempotência: por `telegram_message_id`.
- Resposta: `200` `{ok, conversation, message, duplicate}`.
- Rate limiting por IP (escopo `telegram`).

## Frontend

- Hooks SWR em `frontend/src/hooks/use-conversations.ts`.
- Mensagens reais via polling 8s (`refreshInterval: 8000`) — sem WebSocket no backend.
- Templates armazenados offline via `localStorage` — sem endpoint backend (backend não expõe).
- Status do agente inferido do token auth — sem Device API.

## Mocks (MSW)

Handlers em `frontend/src/mocks/handlers.ts`, dados em `frontend/src/mocks/data.ts`.

## Testes

- `frontend/src/components/omnichannel/*.test.tsx` (vitest + @testing-library)
- 10 testes cobrindo: agent-status-badge (online/offline), conversation-list (render/filtros/seleção), conversation-chat (mensagens/envio/atribuição).
