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

## Decisões parametrizáveis (PROJECT-CONTEXT §11)
- `JWT_ACCESS_MINUTES=15`, `JWT_REFRESH_DAYS=7` (env).
- Throttles: login `10/min`, signup `5/min`, password-reset `5/min` (env).
- Algoritmo JWT `HS256` fixo.
