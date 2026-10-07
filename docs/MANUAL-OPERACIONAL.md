# Manual Operacional — Clinica-SaaS

## 1. Arquitetura do Sistema

### Multi-Tenant (django-tenants)
O sistema usa isolamento por schema. Cada tenant (clínica) tem seu próprio schema no PostgreSQL. Não há compartilhamento de dados entre tenants.

### Autenticação
- **JWT Bearer** com claims `tenant` (schema), `user_id` e `role`
- Header obrigatório: `Authorization: Bearer <access_token>`
- Header opcional para roteamento: `x-tenant-id: <schema>`
- Tokens expiram em 15 minutos (access) / 7 dias (refresh)

### Rate Limiting por Plano
| Plano | Limite |
|-------|--------|
| Starter | 60 req/min |
| Pro | 300 req/min |
| Enterprise | 1000 req/min |

---

## 2. Administração

### Criar novo tenant

```
POST /api/v1/tenants/signup/
Content-Type: application/json

{
  "tenant_name": "Clínica Exemplo",
  "tenant_slug": "clinica-exemplo",
  "admin_username": "admin",
  "admin_email": "admin@clinicaexemplo.com",
  "admin_password": "senha_segura_123"
}
```

**Resposta:** `201 Created`
```json
{
  "tenant": {...},
  "user": {...},
  "access": "...",
  "refresh": "..."
}
```

### Alterar plano do tenant

1. Acesse o **Admin do Django**: `/admin/`
2. Faça login com superusuário
3. Vá para **Tenants** → **Tenant**
4. Localize o tenant e clique em **Editar**
5. Altere o campo **Plan** para: `starter` | `pro` | `enterprise`
6. Clique em **Salvar**

---

## 3. Gestão de Usuários

### Papéis e Permissões (RBAC)

| Papel | Permissões |
|-------|-----------|
| `superuser` | Acesso total a todos os tenants |
| `admin` | Acesso total ao seu tenant |
| `manager` | Gerencia agendamentos, profissionais, clientes |
| `user` | Apenas visualiza |
| `professional` | Agenda própria, atende conversas |

### Criar/editar usuário

1. Acesse o **Admin do Django**: `/admin/`
2. **Auth** → **User**
3. Clique em **Add User** ou edite um existente
4. Preencha username, e-mail, senha
5. Em **User permissions**, atribua permissões específicas

### Atribuir papel por tenant

1. **Tenants** → **TenantUser**
2. Crie um novo registro com: tenant, user, role

---

## 4. Fluxos Detalhados

### Fluxo completo: Lead → Cliente

```
1. CRM → Leads → POST /leads/
   {name, email, source, assigned_to}
2. Leads → PATCH /leads/{id}/status/
   {status: "CONTACTED"}
3. Leads → PATCH /leads/{id}/status/
   {status: "QUALIFIED"}
4. Leads → POST /leads/{id}/convert/
   → Cria Customer automaticamente
5. CRM → Customers → GET /customers/{id}/
   → Timeline mostra histórico de conversão
```

### Fluxo de agendamento

```
1. Scheduler → Services → POST /services/
   {name, duration_minutes, price}
2. Scheduler → Professionals → POST /professionals/
   {name, specialties, commission_type}
3. Scheduler → Availability → GET /availability/?professional=1&date=2026-10-08
   → Retorna slots livres
4. Scheduler → Appointments → POST /appointments/
   {professional, service, customer, start}
   → 409 se conflito (overlap)
```

### Regra de conflito
Overlap = mesmo profissional + status em (`SCHEDULED`, `CONFIRMED`) + `start < novo_end AND end > novo_start`.
Adjacente (`end == start`) é **permitido**.
Cancelado/Completo/No-show **não bloqueiam**.

### Fluxo de atendimento (Omnichannel)

```
1. Omnichannel → Conversations → GET /conversations/
   → Lista de conversas por canal
2. Conversations → PATCH /conversations/{id}/assign
   {assigned_to: "user_id"}
3. Conversations → POST /conversations/{id}/reply
   {body: "mensagem"}
→ 201 mensagem outbound
4. Conversations → GET /conversations/{id}/messages
   → Lista mensagens (polling a cada 8s no frontend)
```

---

## 5. Relatórios

### Dashboard

**Endpoint:** `GET /api/v1/dashboard/stats/`

**Resposta:**
```json
{
  "appointments_today": 8,
  "leads_this_week": 3,
  "revenue": {
    "currency": "BRL",
    "amount": 1250.00
  }
}
```

### Dashboard do Profissional

**Endpoint:** `GET /api/v1/professional-dashboard/stats/`

**Resposta:**
```json
{
  "appointments_today": 5,
  "commission_earned": {
    "currency": "BRL",
    "amount": 450.00
  },
  "appointments_by_status": {...}
}
```

---

## 6. Integrações

### Google Calendar

1. **Settings** → **Integrations** → `POST /settings/integrations/`
   ```json
   {
     "provider": "google_calendar",
     "professional_email": "profissional@clinica.com",
     "config": {
       "client_id": "...",
       "client_secret": "...",
       "refresh_token": "..."
     }
   }
   ```
2. O sistema usa `GoogleCalendarAdapter` para sincronizar eventos
3. Sincronização idempotente via `external_event_id`

### Webhooks

**Endpoints webhook públicos:**
- Telegram: `POST /api/v1/omnichannel/telegram/webhook` (header `X-Telegram-Bot-Api-Secret-Token`)
- Confirmação de agendamento: `POST /api/v1/appointments/confirm-webhook/` (body `{token, action}`, header `x-tenant-id`)

**Webhooks de saída (tenant configurável):**
```
POST /settings/webhooks/
{name, url, events: ["appointment.confirmed", "lead.converted"], secret, active}
```

Eventos disparados via signals. Entrega com retry exponencial. Validação via `X-Webhook-Signature` header.

### Chaves de API

```
POST /settings/api-keys/
{name: "Integration mobile"}

Resposta:
{"id": 1, "prefix": "a1b2c3d4", "plain_key": "sk_a1b2c3d4_xxx..."}
```

**Autenticação futura:** header `Authorization: Bearer sk_...`  
**Hash:** SHA256 do plain_key armazenado no campo `key_hash`

---

## 7. Solução de Problemas

### Problemas comuns

#### Deploy falha no build

**Sintomas:** Build falha com `Command failed` no GitHub Actions.

**Causas possíveis:**
- Variável `RENDER_API_KEY` ou `RENDER_SERVICE_ID` não configurada
- `DJANGO_SETTINGS_MODULE` com valor incorreto (`config.settings.production` em vez de `config.settings`)
- `DJANGO_SECRET_KEY` não configurada quando DEBUG=False

**Solução:**
1. Verifique os GitHub Secrets:
   ```bash
   gh secret list
   ```
2. Confirme as variáveis no painel Render.com → Service → Settings → Environment
3. Garanta que `DJANGO_SETTINGS_MODULE=config.settings`

#### Migrações não aplicam

**Sintomas:** `No migrations to apply` ou tabelas não criadas.

**Comando para rodar manualmente:**
```bash
cd backend
python manage.py migrate_schemas
```

#### Rate limit (429)

**Sintomas:** Requisições retornam `429 Too Many Requests`.

**Diagnóstico:**
```bash
# Verificar logs
curl -H "Authorization: Bearer $ACCESS" https://api.clinica.com.br/api/v1/health/
```

**Solução:**
- Aguarde o limite do plano renovar
- Considere upgrade de plano (`starter` → `pro` → `enterprise`)

#### Webhook não recebe eventos

**Diagnóstico:**
1. Verifique se o webhook está ativo (`GET /settings/webhooks/`)
2. Verifique se o evento está na lista (`events` field)
3. Teste conectividade: `curl -X POST <url_do_webhook> -d '{"test": true}'`
4. Verifique logs: `docker logs clinica-web`

#### Problemas de timezone

**Sintomas:** Agendamentos aparecem com horário errado.

**Verificação:**
```sql
SELECT tenant_slug, timezone FROM tenants_tenant WHERE slug = '<slug>';
```

**Correção:**
```
PATCH /settings/tenant/
{"timezone": "America/Sao_Paulo"}
```

---

## 8. Manutenção

### Restart do serviço

**Render.com:**
```bash
render restart --service srv-xxxxxxxxxx
```

**Docker local:**
```bash
docker-compose down
docker-compose up -d --build
```

### Banco de dados

**Backup PostgreSQL (local):**
```bash
pg_dump -U clinica -h localhost clinica > backup-$(date +%Y%m%d).sql
```

**Restore:**
```bash
psql -U clinica -h localhost clinica < backup.sql
```

**Verificar migrações:**
```bash
cd backend
python manage.py showmigrations
```

### Testes

**Backend:**
```bash
cd backend
python manage.py test
pytest tests/
```

**Frontend:**
```bash
cd frontend
npm test
```

### Logs em tempo real

**Render.com:**
```bash
render logs --service srv-xxxxxxxxxx --tail
```

**Docker:**
```bash
docker-compose logs -f web
```

---

## 9. Segurança

### Rotação de credenciais

| Credencial | Frequência | Local |
|-----------|------------|-------|
| DJANGO_SECRET_KEY | 30 dias | Render.com → Environment |
| POSTGRES_PASSWORD | 60 dias | Render.com → Database |
| RENDER_API_KEY | 90 dias | Render.com → Account → API Keys |

### Segredos nunca no código

- API keys do OpenAI: via env `OPENAI_API_KEY`
- Credenciais Google Calendar: via `IntegrationConfig.config` (write-only)
- Webhook secrets: via `WebhookEndpoint.secret`

### Auditoria

- `django-simple-history` em: TenantSettings, IntegrationConfig, WebhookEndpoint, ApiKey, Lead, Customer
- Structlog registra eventos: `api_key_issued`, `lead_converted`, `appointment_confirmed`

---

## 10. URLs Úteis

| Recurso | URL |
|---------|-----|
| Dashboard | https://clinica-saas-frontend.vercel.app |
| API Docs (Swagger) | https://api.clinica.com.br/api/schema/swagger/ |
| Admin Django | https://api.clinica.com.br/admin/ |
| Render.com | https://dashboard.render.com |
| Repositório GitHub | https://github.com/odcolares/clinica-saas |

---

*Manual operacional atualizado em: 07/10/2026*