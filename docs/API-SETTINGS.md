# API — Configurações (Etapa 5)

Base: `/api/v1/`. Auth JWT (header `Authorization: Bearer <access>`, tenant no claim).

## Tenant Settings (Singleton)

| Método | Path | Body | Respostas |
|---|---|---|---|
| GET | `/settings/tenant/` | — | 200 (cria default se ausente) |
| PATCH | `/settings/tenant/` | `{business_start?, business_end?, timezone?, logo_url?, primary_color?, brand_name?}` | 200 / 400 |

**Validações:**
- `business_end` deve ser posterior a `business_start`
- `timezone`: formato IANA (ex: `America/Sao_Paulo`)
- `primary_color`: formato hexadecimal (7 chars, ex: `#0F766E`)

## Integration Config

| Método | Path | Body | Respostas |
|---|---|---|---|
| GET | `/settings/integrations/` | filtros `?provider=&active=` | 200 paginado |
| POST | `/settings/integrations/` | `{provider, professional_email?, config}` | 201 / 400 |
| GET | `/settings/integrations/{id}/` | — | 200 / 404 |
| PATCH | `/settings/integrations/{id}/` | campos parciais | 200 / 400 / 404 |
| DELETE | `/settings/integrations/{id}/` | — | 204 / 404 |

**Providers suportados:**
- `noop` — desativado
- `google_calendar` — sincronização bidirecional via adapter

**Nota:** O campo `config` é write-only; não é retornado em respostas GET/PATCH.

## Webhook Endpoints

| Método | Path | Body | Respostas |
|---|---|---|---|
| GET | `/settings/webhooks/` | filtros `?active=` | 200 paginado |
| POST | `/settings/webhooks/` | `{name, url, events?, secret?, active?}` | 201 / 400 |
| GET | `/settings/webhooks/{id}/` | — | 200 / 404 |
| PATCH | `/settings/webhooks/{id}/` | campos parciais | 200 / 400 / 404 |
| DELETE | `/settings/webhooks/{id}/` | — | 204 / 404 |

**Validações:**
- `url`: URL válida (máx 500 chars)
- `events`: deve ser uma lista de strings

## API Keys

| Método | Path | Body | Respostas |
|---|---|---|---|
| GET | `/settings/api-keys/` | — | 200 paginado |
| POST | `/settings/api-keys/` | `{name}` | 201 (retorna `plain_key` uma vez) |
| GET | `/settings/api-keys/{id}/` | — | 200 / 404 |
| DELETE | `/settings/api-keys/{id}/` | — | 204 / 404 |

**Segurança:**
- Só o hash SHA256 do plain_key é armazenado
- O `plain_key` é retornado apenas na resposta de criação
- Formato: `sk_<prefix>_<random>` (ex: `sk_a1b2c3d4_<token>`)

## Notification Settings

| Método | Path | Body | Respostas |
|---|---|---|---|
| GET | `/settings/notifications/` | — | 200 |
| PATCH | `/settings/notifications/` | campos parciais | 200 |

**Campos:**
- `appointment_confirmation`: boolean
- `appointment_reminder`: boolean
- `appointment_reminder_time`: number (minutos, default: 24)
- `appointment_cancellation`: boolean
- `new_lead_alert`: boolean
- `payment_received`: boolean
- `email_notifications`: boolean
- `sms_notifications`: boolean
- `push_notifications`: boolean

## Rate Limiting

Endpoints de Settings utilizam `PlanRateThrottle` e `ScopedRateThrottle`. Limites definidos pelo plano do tenant.
