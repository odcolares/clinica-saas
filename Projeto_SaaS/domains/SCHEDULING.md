# SCHEDULING.md — Domínio de Agendamento

## 1. Visão Geral
Domínio responsável pelo agendamento de serviços, controle de disponibilidade de profissionais, gestão de calendário e integrações externas (Google Calendar).

## 2. Entidades Principais

### Professional
- `id`, `name`, `email`, `phone`, `specialties` (comma-separated), `active`, `created_at`, `updated_at`
- Comissões: `commission_type` (none | percent | fixed), `commission_percent` (0-100), `commission_fixed` (decimal)
- `user` — FK opcional para Auth User
- Relacionamento: 1:N com Appointment

### Service
- `id`, `name`, `duration_minutes`, `price`, `description`
- Relacionamento: 1:N com Appointment

### Appointment
- `id`, `customer`, `professional`, `service`, `start`, `end`, `status`, `notes`, `confirmation_token`, `external_event_id`, `created_at`, `updated_at`
- Status: `SCHEDULED` | `CONFIRMED` | `CANCELLED` | `COMPLETED` | `NO_SHOW`
- Relacionamento: N:1 com Customer, Professional, Service

### ProfessionalAvailability
- `professional`, `professional_name`, `date`, `slots[]`
- Slot: `start`, `end`, `available`

## 3. Fluxos Principais

### Agendamento
1. Cliente seleciona profissional + serviço + data/hora
2. Backend valida disponibilidade (slot livre)
3. Cria Appointment com status `scheduled`
4. Notifica profissional/cliente

### Confirmação
1. Profissional/recepcionista confirma agendamento
2. Status: `scheduled` → `confirmed`
3. Envia confirmação ao cliente

### Cancelamento
1. Cliente ou profissional cancela
2. Status: `scheduled`/`confirmed` → `cancelled`
3. Libera slot na disponibilidade
4. Notifica partes envolvidas

### Conclusão
1. Após atendimento, marca como concluído
2. Status: `confirmed` → `completed`
3. Gera pagamento/financeiro se aplicável

## 4. Disponibilidade

### Regras
- Slots de 30 min (configurável por serviço)
- Horário comercial: 07:00-20:00 (configurável)
- Conflito: mesmo profissional + mesmo horário = bloqueado
- Buffer entre agendamentos (configurável)

### Endpoints de Disponibilidade
- `GET /api/v1/availability?date=YYYY-MM-DD&professional=ID` — lista disponibilidade do dia
- `GET /api/v1/availability/{professionalId}?date=YYYY-MM-DD` — disponibilidade específica

## 5. Integrações Externas

### Google Calendar (Adapter Pattern)
- Sincronização bidirecional de agendamentos
- Webhook para confirmação/cancelamento externo
- Reconciliação periódica (idempotência)

## 6. Permissões (RBAC)

| Ação | Roles Permitidos |
|------|------------------|
| Criar agendamento | admin, receptionist, professional |
| Confirmar agendamento | admin, receptionist, professional |
| Cancelar agendamento | admin, receptionist, professional, customer (próprio) |
| Ver disponibilidade | admin, receptionist, professional |
| Ver calendário do tenant | admin, receptionist |

## 7. Validações de Negócio

- Não agendar em slot ocupado
- Não agendar fora do horário comercial
- Serviço deve existir e estar ativo
- Profissional deve estar ativo
- Cliente deve existir (ou ser criado no fluxo)

## 8. Auditoria

- Log de criação/confirmação/cancelamento/conclusão
- Registrar: ator, timestamp, status anterior → novo
- Rastrear conflitos detectados e resolvidos

## 9. Testes Obrigatórios

- Conflito de horário (mesmo profissional, mesmo horário)
- Agendamento fora do horário comercial
- Cancelamento libera slot
- Confirmação muda status corretamente
- Integração Google Calendar (webhook + reconciliação)
- Permissões por role
- Isolamento de tenant (multi-tenancy)