# API do CRM — ETAPA 1 (Marcos)

Base: `/api/v1/`. Erros no envelope `{ "detail": ... }`. Todas as rotas exigem
JWT `Authorization: Bearer <access>` com claim `tenant` — o tenant efetivo vem
da identidade, nunca do cliente. Listagens são paginadas (`count`/`next`/
`previous`/`results`, 20 por página) e aceitam filtros, `search` e `ordering`.

Contrato canônico de alto nível: `Projeto_SaaS/architecture/API.md` §CRM.

## Leads

### `POST /leads/`
Cria um Lead com status inicial `NEW`.
Body: `{ name, email?, phone?, document?, source?, assigned_to?, notes? }`
→ `201` Lead

### `GET /leads/`
Filtros: `status__code`, `source`, `assigned_to` · `search=name|email|phone|document` ·
`ordering=created_at|updated_at|name` → `200` lista paginada

### `GET /leads/{id}/` · `PATCH /leads/{id}/` · `DELETE /leads/{id}/`
`PATCH` aceita os mesmos campos do create. `DELETE` restrito a papéis
administrativos (`admin`/`manager`). Objeto fora do escopo do usuário → `404`.

### `PATCH /leads/{id}/status/`
Body: `{ status, reason? }`. Transições controladas:
`NEW → CONTACTED|LOST`, `CONTACTED → QUALIFIED|LOST`,
`QUALIFIED → CONVERTED|LOST`, `LOST → CONTACTED` (reativação).
`reason` é obrigatório para `LOST`. Toda transição é auditada com autor, data e
motivo. Transição inválida → `400`; status inexistente → `400`.

### `POST /leads/{id}/convert/`
Converte um Lead `QUALIFIED` em Customer, preservando o Lead original.
Procura Customer existente por `email` → `document` → `phone`; se achar,
vincula; senão, cria. → `201 { customer, created: true, lead_id }` quando cria ·
`200 { customer, created: false, lead_id }` quando vincula · `400` se não estiver
`QUALIFIED` · `409` se já convertido.

## Customers

### `POST /customers/` · `GET /customers/`
Create aceita `{ name, email?, phone?, document?, status?, source?, assigned_to?, tags? }`
(`tags` por nome). Listagem filtra por `status`, `source`, `assigned_to`, `tags`;
`search=name|email|phone|document`; `ordering=created_at|updated_at|name`.

### `GET /customers/{id}/` · `PATCH /customers/{id}/` · `DELETE /customers/{id}/`
`GET` inclui `contacts`, `addresses` e `notes` aninhados. `DELETE` restrito a
papéis administrativos.

### `POST /customers/{id}/contacts/`
Body: `{ kind(email|phone|whatsapp|other), value, label?, is_primary? }` → `201`

### `POST /customers/{id}/addresses/`
Body: `{ street, city, number?, complement?, district?, state?, zipcode?, country?, label?, is_primary? }` → `201`

### `POST /customers/{id}/notes/`
Body: `{ body }` → `201` (autor = usuário autenticado)

### `GET /customers/{id}/timeline/`
→ `200 { customer, events: [...] }`. Consolida notas, interações e o marco de
conversão, mais recentes primeiro. Não duplica dados de Quotes/Agenda/Finance.

## Lookups e tags

- `GET|POST /tags/` · `GET|DELETE /tags/{id}/` — CustomerTag por nome.
- `GET|POST /lead-sources/` · `GET /lead-sources/{id}/` — LeadSource.
- `GET /lead-statuses/` · `GET /lead-statuses/{id}/` — LeadStatus (somente leitura;
  estados semeados por migration).

## Decisões (PROJECT-CONTEXT §11)

- **Transições de Lead**: mapa fixo conforme `CRM.md`; `LOST` exige motivo.
- **Critérios de conversão**: correspondência em cascata `email` → `document` →
  `phone`; sem correspondência, cria Customer. Lead original nunca é apagado.
- **RBAC por objeto (django-guardian)**: papéis `admin`/`manager` enxergam todo o
  tenant; demais usuários enxergam apenas objetos em que são criadores ou
  responsáveis atribuídos (`view`/`change`). Exclusão é exclusiva de papéis
  administrativos. O isolamento entre tenants é o schema (django-tenants).
- **Auditoria**: `django-simple-history` em Customer, Lead e agregados; transições
  e conversão registram autor/data/motivo.
- **Rate limiting**: não aplicado a esta etapa (definido na fundação para auth).
