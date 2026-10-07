# API — Agenda (Etapa 2, Marcos/Backend)

Base: `/api/v1/`. Auth JWT (header `Authorization: Bearer <access>`, tenant no claim).
Exceção: webhook de confirmação (token na URL lógica, `x-tenant-id` como hint).

## Profissionais

| Método | Path | Body | Respostas |
|---|---|---|---|
| POST | `/professionals/` | `{name, email?, phone?, specialties?, commission_type?, commission_percent?, commission_fixed?, active?, user?}` | 201 / 400 |
| GET | `/professionals/` | filtros `?active=&search=&ordering=` | 200 paginado |
| GET/PATCH/DELETE | `/professionals/{id}/` | — | 200 / 404 |

**Comissões:**
- `commission_type`: `none` | `percent` | `fixed` (default: `none`)
- `commission_percent`: decimal 0-100 (quando `percent`)
- `commission_fixed`: decimal >= 0 (quando `fixed`)
- Validação: percentual entre 0-100, valor fixo não negativo

## Serviços

| Método | Path | Body | Respostas |
|---|---|---|---|
| POST | `/services/` | `{name, description?, duration_minutes?, price?, active?}` | 201 / 400 |
| GET | `/services/` | filtros `?active=&search=&ordering=` | 200 paginado |
| GET/PATCH/DELETE | `/services/{id}/` | — | 200 / 404 |

## Agendamentos

| Método | Path | Body | Respostas |
|---|---|---|---|
| POST | `/appointments/` | `{professional, service, customer, start, end?, notes?}` (`end` calculado de `service.duration_minutes` se omitido) | 201 / 400 / 409 (conflito) |
| GET | `/appointments/` | filtros `?status=&professional=&service=&customer=` | 200 (lista **sem** `confirmation_token`) |
| GET | `/appointments/{id}/` | — | 200 (detail com `confirmation_token` e `external_event_id`) / 404 |
| PATCH | `/appointments/{id}/` | `{start?, end?, service?, notes?}` (revalida conflito) | 200 / 400 / 409 / 404 |
| POST | `/appointments/{id}/cancel/` | — | 200 idempotente (já `CANCELLED` → 200) |
| POST | `/appointments/{id}/reschedule/` | `{start, end?}` | 200 / 400 / 409 / 404 |
| POST | `/appointments/{id}/confirm/` | — | 200 idempotente |
| DELETE | `/appointments/{id}/` | — | 204 (guardian: só manager tem `delete`) |

## Disponibilidade

`GET /availability/?professional=<id>&date=YYYY-MM-DD&service=<id opcional>` →
`{"professional": 1, "date": "2026-09-26", "slots": [{"start": iso, "end": iso}]}`.
Expediente fixo 08:00–18:00 (America/Sao_Paulo), passo = `service.duration_minutes`
(default 30). Erros: 400 (parâmetro ausente/formato), 404 (profissional/serviço).

## Webhook de confirmação (público, link do cliente)

`POST /appointments/confirm-webhook/` com `x-tenant-id: <schema>`:
`{"token": "<confirmation_token>", "action": "confirm"|"cancel"}` →
200 com o agendamento / 404 (token inválido). Sem JWT; o segredo é o token UUID.

## Regra de conflito

Sobreposição = mesmo profissional + status em (`SCHEDULED`, `CONFIRMED`) +
`start < novo_end AND end > novo_start`. Adjacente (`end == start`) é permitido;
`CANCELLED`/`COMPLETED`/`NO_SHOW` não bloqueiam. Falha retorna 409 com mensagem
do horário ocupado. Ponto único de verdade: `validate_no_conflict()` em
`apps/scheduling/services.py`.

## Calendário externo (adapter)

`apps/scheduling/calendar.py`: `CalendarAdapter` (interface) +
`NoopCalendarAdapter` (padrão, só loga) + `GoogleCalendarAdapter` (stub;
credenciais via env `GOOGLE_CALENDAR_CREDENTIALS`, nunca no código).
Idempotência via `external_event_id`; `sync_to_calendar()` atualiza após
create/update/reschedule. Falha de credencial → 400, nunca 500 cru.
