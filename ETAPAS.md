# ETAPAS.md — Plano de Desenvolvimento Técnico

## Objetivo

Definir as etapas de desenvolvimento do Clinica SaaS focadas exclusivamente em infraestrutura técnica, backend, banco de dados e frontend. Cada fase entrega um incremento funcional do sistema.

---

## Divisão de Responsabilidades

| Pessoa           | Responsabilidade                                                                   |
| ---------------- | ---------------------------------------------------------------------------------- |
| **Marcos** | Backend (Django + DRF), banco de dados, infraestrutura, CI/CD, auth, multi-tenancy |
| **Odair**  | Frontend (React + Next.js), UI components, Tailwind, shadcn/ui, UX                 |

**Regra de comunicação:**

- Backend expõe API → Frontend consome
- Marcos define os endpoints (contrato) antes de Odair implementar
- Ambos revisam o trabalho do outro
- Ninguém faz deploy sozinho — merge request com aprovação

---

## Etapa 0: Fundação (Semanas 1-2)

**Responsáveis:** Marcos (80%) / Odair (20%)

**Objetivo:** Projeto estruturado, autenticação multi-tenant funcionando, infraestrutura básica.

### Marcos — Backend + Infra

- [X] Criar repositório Git
- [X] Estruturar pastas (backend/, frontend/, docs/)
- [X] Setup Django + Django REST Framework
- [X] django-tenants configurado (schema-level isolation)
- [X] Signup de tenant (cria schema + usuário admin)
- [X] Login + JWT (autenticação backend)
- [X] Middleware de tenant context (`x-tenant-id`)
- [X] Setup Docker local (PostgreSQL + Redis)
- [X] CI/CD pipeline (GitHub Actions → Railway + Vercel)
- [X] Variáveis de ambiente (.env)
- [X] Sentry + structlog configurado
- [X] Rate limiting no backend
- [X] Documentar endpoints iniciais

### Odair — Frontend Setup

- [X] Setup Next.js + TypeScript strict
- [X] ESLint + Prettier configurados
- [X] Tailwind CSS + shadcn/ui instalados
- [X] Auth page (login, recuperação senha)
- [X] Configurar API client (axios/fetch com interceptors)
- [X] Layout base (sidebar, header, footer)

---

## Etapa 1: CRM Core (Semanas 3-4)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Cadastro de clientes e leads funcionando com multi-tenancy.

### Marcos — Backend API

- [X] CRUD de Leads (`POST/GET/PATCH /leads`)
- [X] CRUD de Customers (`GET/POST /customers`)
- [X] Conversão Lead → Customer (endpoint)
- [X] Tags, contatos, notas, timeline
- [X] Permissões por tenant (django-guardian)
- [X] Filtros por schema em todos os endpoints
- [X] Audit log (django-simple-history)
- [X] Testes unitários (modelos + views)
- [X] Documentar todos os endpoints na API.md

### Odair — Frontend

- [X] Listagem de leads com filtros
- [X] Formulário de lead + validação
- [X] Detalhe de customer + timeline
- [X] Conversão lead → customer (UI)
- [X] Dashboard simples (cards + gráfico)
- [X] Autenticação integrada (guardar JWT, redirect)
- [X] Tratamento de erros (toast notifications)

---

## Etapa 2: Agenda (Semanas 5-6)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Agendamento de serviços com controle de disponibilidade.

### Marcos — Backend API

- [X] Model Professional (perfil + especialidades)
- [X] Model Service (duração, preço)
- [X] CRUD de Appointments
- [X] Regras de conflito (horário indisponível)
- [X] Disponibilidade por profissional
- [X] Integração Google Calendar (adapter pattern)
- [X] Webhook de confirmação
- [X] Testes de conflito (edge cases)

### Odair — Frontend

- [X] Calendário mensal (FullCalendar ou equivalente)
- [X] Formulário de agendamento
- [X] Lista de profissionais com disponibilidade
- [X] Seleção de serviço + profissional
- [X] Confirmação/cancelamento pelo cliente
- [X] Visualização de agenda do tenant
- [X] Responsividade mobile

---

## Etapa 3: Omnichannel (Semanas 7-8)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Atendimento via Telegram integrado ao CRM.

### Marcos — Backend API

- [X] Telegram Bot webhook
- [X] Model Conversation + ConversationMessage
- [X] Normalização de mensagens
- [X] Atribuição para atendente
- [X] Integração com CRM (lead criado a partir de mensagem)
- [X] Redis para cache de sessões
- [X] Rate limiting por canal
- [X] Testes de webhook (simulação)
- [X] Adapter pattern para canais futuros (WhatsApp)

### Odair — Frontend

- [X] Interface de atendimento ao vivo
- [X] Lista de conversas
- [X] Mensagens em tempo real (polling)
- [X] Mensagens automáticas (templates)
- [X] Badge de status do agente
- [X] Painel de gestão de canais

---

## Etapa 4: AI Assistant (Semanas 9+)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Automação com IA para triagem de leads e respostas.

### Marcos — Backend API

- [X] Integração OpenAI API (classificação de intenção)
- [X] Respostas automáticas (RAG - FAQs)
- [X] Resumo de conversa (LLM)
- [X] Extração de dados do cliente (nome, telefone, serviço)
- [X] Circuit breaker para OpenAI
- [X] Cache de respostas (Redis)
- [X] Logs de interação com IA (audit)
- [X] Prompt management (templates parametrizáveis)

### Odair — Frontend

- [X] Badge "IA respondeu" nas mensagens
- [X] Botão "Melhore esta resposta"
- [X] Painel de configuração de IA
- [X] Histórico de interações da IA
- [X] Ajustes de prompt (UI amigável)

---

## Etapa 5: Configurações & Profissionais (Semanas 11+)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Gestão de profissionais e configurações do tenant.

### Marcos — Backend API

- [X] CRUD de Profissionais
- [X] Comissões e percentuais
- [X] Configurações do tenant (horários, branding)
- [X] Integrações externas (Google Calendar adapter)
- [X] Webhooks configuráveis
- [X] API keys management
- [X] Rate limiting por plano

### Odair — Frontend

- [x] Gestão de profissionais (CRUD + agenda)
- [x] Configurações do tenant (logo, cores, horários)
- [x] Painel de integrações
- [x] Dashboard de profissionais
- [x] Configurações de notificação

---

## Fluxo de trabalho

```
┌─────────────────────────────────────────────────────────────┐
│  MARCOS (Backend)                                            │
│  ├─ Define modelos Django + migrations                      │
│  ├─ Cria endpoints API (DRF)                               │
│  ├─ Configura multi-tenancy + auth                         │
│  ├─ Escreve testes unitários + integration                  │
│  └─ Faz deploy no Railway                                   │
│                                                             │
│  ODGAR (Frontend)                                            │
│  ├─ Consome API (contrato definido por Marcos)            │
│  ├─ Cria components com shadcn/ui + Tailwind               │
│  ├─ Gerencia estado (React hooks + Zustand)               │
│  └─ Faz deploy no Vercel                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Railway  │      │  Vercel  │      │ GitHub   │
    │ (Backend)│◄────►│ (Frontend)│◄────►│ (CI/CD)  │
    └──────────┘      └──────────┘      └──────────┘
```

---

## Regras obrigatórias

1. **Backend é a autoridade** — nunca confiar no frontend
2. **Tenant isolation** — cada query filtrada por schema
3. **RBAC rigoroso** — permissões por objeto (django-guardian)
4. **Audit trail** — registrar tudo (django-simple-history)
5. **Adapters** — integrações externas sempre por adapter
6. **Testes automatizados** — no pipeline de CI/CD
7. **Documentação viva** — atualizar conforme implementa
8. **Contrato antes de código** — Marcos define endpoint, Odair implementa
9. **Nenhum deploy sem review** — merge request com aprovação
10. **Segredos nunca no código** — sempre .env ou secrets manager

---

## Critérios de fechamento por etapa

- [ ] Todos os endpoints testados (unit + integration)
- [ ] Frontend responsivo (mobile + desktop)
- [ ] Deploy no ambiente de staging
- [ ] Documentação atualizada (API.md)
- [ ] Testes passando no CI/CD
- [ ] Usuários do tenant conseguem usar sem erro
- [ ] Multi-tenancy funcionando (schema isolado)

---

## Dependências entre etapas

```
Etapa 0 (Fundação) ──► Etapa 1 (CRM) ──► Etapa 2 (Agenda)
                                                          │
                                                          ▼
Etapa 3 (Omnichannel) ◄─────────────────────────────────┘
                                                          │
                                                          ▼
Etapa 4 (AI) ◄────────────────────────────────────────────┘
                                                          │
                                                          ▼
Etapa 5 (Configurações) ◄─────────────────────────────────┘
```

---

## Links relacionados

- [[00 - Visão Geral do Projeto]]
- [[01 - Stack Tecnológica]]
- [[02 - Arquitetura Multi-Tenant]]
- [[03 - Módulos Funcionais]]
- [[06 - Segurança e Regras]]
- [TECH-STACK.md](architecture/TECH-STACK.md)
- [DOMAIN-MAP.md](architecture/DOMAIN-MAP.md)
- [API.md](architecture/API.md)

---

> **Criado:** 2026-01-15
> **Responsáveis:** Marcos (Backend/DB) + Odair (Frontend/UI)
> **Atualização:** 2026-09-20 — Etapa 2 Frontend (Agenda) concluída: calendário FullCalendar, formulário agendamento, disponibilidade profissionais, confirmação/cancelamento, responsividade mobile
> **Atualização:** 2026-09-30 — Etapa 3 Frontend (Omnichannel) concluída: interface de atendimento ao vivo (conversation-chat), lista de conversas (conversation-list), polling 8s, templates offline via localStorage, badge de status do agente, painel de gestão de canais. 10 testes vitest passando.
> **Atualização:** 2026-10-07 — Etapa 5 Frontend concluída: Gestão de profissionais (CRUD completo com comissões), Configurações do tenant (horários de funcionamento, branding), Painel de integrações (Google Calendar, webhooks, API keys), Dashboard de profissionais (comissões e agendamentos), Configurações de notificação. 71 testes vitest passando.
