# API da Fundação — ETAPA 0 (Marcos)

Base: `/api/v1/`. Erros no envelope `{ "detail": ... }`. JWT Bearer com claim `tenant`.

## `GET /health/` (público)
→ `{ "status": "ok", "etapa": 0 }`

## `POST /tenants/signup/` (público, throttle `signup`)
Cria schema do tenant + usuário admin. Body:
`{ tenant_name, tenant_slug, admin_username, admin_email, admin_password(min 8) }`
→ `201 { tenant, user, access, refresh }` · `409` se slug existe.

## `POST /auth/login/` (público, throttle `login`)
Requer header `x-tenant-id: <schema>` (roteamento p/ schema do tenant).
Body `{ username, password }` → `200 { tenant, user, access, refresh }`.
Falha genérica `400 { detail: "Credenciais inválidas." }` (sem enumeração).

## `POST /auth/refresh/` (público, throttle `login`)
Body `{ refresh }` → `200 { access, refresh? }` (rotação + blacklist).

## `POST /auth/logout/` (autenticado, throttle `login`)
Body `{ refresh }` → `200`. Refresh blacklistado; reuso → `401`.

## `GET /auth/me/` (autenticado)
→ `200 { tenant, user }`. Header `x-tenant-id` divergente do claim JWT → `403`.

## `POST /auth/password-reset/` (público, throttle `password_reset`)
Body `{ email }` → `200 { detail }`. Sempre retorna 200 genérico (não revela se o e-mail existe). Em `DEBUG=True`, inclui `uid` e `token` no response (entrega em produção é uma etapa posterior — Etapa 1).

## `POST /auth/password-reset/confirm/` (público, throttle `password_reset`)
Body `{ uid, token, new_password(min 8) }` → `200 { detail }`. Valida token via `PasswordResetTokenGenerator`; `set_password` invalida o token automaticamente (uso único). Sempre 200, mesmo token inválido (sem enumeração).

## Decisões parametrizáveis (PROJECT-CONTEXT §11)
- `JWT_ACCESS_MINUTES=15`, `JWT_REFRESH_DAYS=7` (env).
- Throttles: login `10/min`, signup `5/min`, password-reset `5/min` (env).
- Algoritmo JWT `HS256` fixo.
- `PASSWORD_RESET_TIMEOUT` padrão Django: 3 dias (259200s). Token expira após esse período.
