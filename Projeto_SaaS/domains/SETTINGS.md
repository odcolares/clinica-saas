# SETTINGS.md — Domínio de Configurações (Etapa 5)

## 1. Visão Geral
Domínio responsável pelas configurações do tenant: horários de funcionamento, branding (logo, cores, nome da marca), integrações externas (Google Calendar adapter), webhooks configuráveis e API keys de acesso.

Todos os objetos vivem no schema do tenant (`TENANT_APPS`). O isolamento é garantido pelo django-tenants, e a visibilidade por objeto pelo django-guardian. Segredos (API keys, webhook secrets, configs de integração) nunca são logados.

## 2. Entidades Principais

### TenantSettings
- `id`, `business_start` (TimeField), `business_end` (TimeField), `timezone` (CharField), `logo_url` (URLField), `primary_color` (CharField, hex), `brand_name` (CharField)
- Singleton por schema — `TenantSettings.current()` cria o default se ausente
- Validação: `business_end` deve ser posterior a `business_start`

### IntegrationConfig
- `id`, `provider` (noop | google_calendar), `active` (Boolean), `professional_email` (EmailField), `config` (JSONField)
- Segredo armazenado em `config` é write-only na API
- Relacionamento: pertence a um tenant (scope de schema)

### WebhookEndpoint
- `id`, `name` (CharField), `url` (URLField), `events` (JSONField, lista), `secret` (CharField), `active` (Boolean)
- Validação: `events` deve ser uma lista
- Dispara eventos ao mudar estado do sistema (ex: appointment confirmado)

### ApiKey
- `id`, `name` (CharField), `prefix` (CharField, unique), `key_hash` (CharField, SHA256), `active` (Boolean), `last_used_at` (DateTimeField)
- Só o hash é persistido; o plain_key é retornado uma única vez na criação
- `ApiKey.issue(name)` — método factory que gera o par (obj, plain_key)

## 3. API Endpoints

### Tenant Settings
- `GET /api/v1/settings/tenant` — retorna as configurações atuais (cria default se ausente)
- `PATCH /api/v1/settings/tenant` — atualiza parcialmente as configurações

### Integration Config
- `GET /api/v1/settings/integrations` — lista (filtra por provider, active)
- `POST /api/v1/settings/integrations` — cria nova integração
- `GET /api/v1/settings/integrations/{id}` — detalhe
- `PATCH /api/v1/settings/integrations/{id}` — atualiza
- `DELETE /api/v1/settings/integrations/{id}` — remove

### Webhook Endpoints
- `GET /api/v1/settings/webhooks` — lista
- `POST /api/v1/settings/webhooks` — cria (aceita `secret` write-only)
- `GET /api/v1/settings/webhooks/{id}` — detalhe
- `PATCH /api/v1/settings/webhooks/{id}` — atualiza
- `DELETE /api/v1/settings/webhooks/{id}` — remove

### API Keys
- `GET /api/v1/settings/api-keys` — lista (sem plain_key)
- `POST /api/v1/settings/api-keys` — cria (retorna `plain_key` uma vez)
- `GET /api/v1/settings/api-keys/{id}` — detalhe
- `DELETE /api/v1/settings/api-keys/{id}` — remove (soft delete via `active=False`)

### Notification Settings
- `GET /api/v1/settings/notifications` — retorna configurações de notificação
- `PATCH /api/v1/settings/notifications` — atualiza parcialmente

## 4. Permissões (RBAC)

Todos os resources da Settings requerem autenticação. As permissões por objeto são gerenciadas pelo guardian (ver `apps.crm.permissions`).

## 5. Rate Limiting

Os endpoints utilizam `PlanRateThrottle` e `ScopedRateThrottle` para limitar chamadas baseado no plano do tenant.

## 6. Webhook Configurável

Webhooks são disparados quando eventos de negócio ocorrem (ex: `appointment.confirmed`, `appointment.cancelled`). O webhook recebe o payload JSON com o evento e tenta a entrega com retry exponencial. O segredo é comparado via header `X-Webhook-Signature`.

## 7. Validações de Negócio

- Tenant settings: `business_end` deve ser posterior a `business_start`
- Webhook: `events` deve ser uma lista válida
- API Key: nome é obrigatório e único por tenant
- Integration: `config` é write-only (não retornado em leitura)

## 8. Auditoria

- `simple_history` registra todas as mudanças em TenantSettings, IntegrationConfig, WebhookEndpoint e ApiKey
- ApiKey criação é logada via structlog (`api_key_issued`) com `key_id` e `prefix` (nunca o plain_key)
