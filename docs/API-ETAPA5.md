# API Etapa 5 — Configurações & Profissionais (Fundação)

Contrato definido por Marcos antes do frontend (regra 8 ETAPAS.md).

## App novo: `apps.settings` (TENANT_APPS)

Base: `CrmBaseViewSet` + `visible_queryset` + `grant_member_perms` + `TimeStampedModel` + `HistoricalRecords`. Tenant isolado por schema.

### 1. TenantSettings — singleton por schema

`GET /api/v1/settings/tenant/` → objeto único (cria default se ausente)
`PATCH /api/v1/settings/tenant/` → atualiza

Campos:
- `business_start: "08:00"`, `business_end: "18:00"`, `timezone: "America/Sao_Paulo"`
- `logo_url: ""`, `primary_color: "#0F766E"`, `brand_name: ""`
- Futuro: `services.get_daily_slots` e `validate_business_hours` passam a ler daqui (hoje fixo 08-18 em `scheduling/services.py:25`).

### 2. Professional — comissões (extensão, não novo CRUD)

CRUD base já existe na Etapa 2: `professionals/` em `scheduling/urls.py:15`.
Etapa 5 adiciona campos + migration `scheduling/0002`:

- `commission_type: "percent" | "fixed" | "none"` (default `none`)
- `commission_percent: decimal 0-100` (default 0)
- `commission_fixed: decimal >=0` (default 0)

`PATCH /api/v1/professionals/{id}/` passa a aceitar os 3 campos. Validação: se type=percent, percent 0-100; se fixed, fixed >=0.

### 3. IntegrationConfig — Google Calendar por tenant

`GET/POST /api/v1/settings/integrations/` + `GET/PATCH/DELETE /api/v1/settings/integrations/{id}/`

Campos: `provider` (`google_calendar|noop`), `active bool`, `config JSON` (credenciais nunca logadas), `professional_email` opcional.

Adapter (`scheduling/calendar.py`): `get_calendar_adapter()` passa a ler `IntegrationConfig(active, provider=google_calendar)` do schema atual; fallback `NoopCalendarAdapter`. Stub vira funcional por tenant sem quebrar `sync_to_calendar`.

### 4. WebhookEndpoint — webhooks configuráveis

`CRUD /api/v1/settings/webhooks/`

Campos: `name`, `url`, `events[]` (ex. `appointment.created|confirmed|cancelled`), `secret`, `active`.
Escopo futuro: disparo via signals. Fundação: só CRUD + validação URL + secret.

### 5. ApiKey — chaves por tenant

`GET/POST /api/v1/settings/api-keys/` + `DELETE` (sem leitura do segredo após criação)

Campos: `name`, `prefix` (8 chars visíveis), `key_hash` (sha256, nunca plain), `active`.
Criação retorna `plain_key` uma única vez (`sk_<prefix>_<rand>`). Autenticação por key entra em etapa posterior; fundação só gerencia.

### 6. Rate limiting por plano

`Tenant.plan` (`tenants/models.py:12`, default `starter`) passa a dirigir throttle:

- `apps.settings.throttling.PlanRateThrottle` lê `connection.tenant.plan`:
  - `starter: 60/min`, `pro: 300/min`, `enterprise: 1000/min` (env override `THROTTLE_PLAN_<PLAN>`)
- Aplicado como `throttle_classes` extra nos ViewSets de settings + scheduling na fundação. Scopes legados (`login, signup, telegram`) mantidos em `settings_middleware.py:72`.

## Verificação

- `python backend/manage.py check`
- `python backend/manage.py makemigrations --check` (após `migrate` local)
- `pytest backend/tests/test_settings.py -q` (novo)
- Critérios ETAPAS.md: endpoints testados, tenant isolado, RBAC por objeto, audit via history, doc viva.
