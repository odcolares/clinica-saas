# ETAPAS.md — Plano de Desenvolvimento Técnico

## Objetivo

Definir as etapas de desenvolvimento do Clinica SaaS focadas exclusivamente em infraestrutura técnica, backend, banco de dados e frontend. Cada fase entrega um incremento funcional do sistema.

---

## Divisão de Responsabilidades

| Pessoa | Responsabilidade |
|--------|-----------------|
| **Marcos** | Backend (Django + DRF), banco de dados, infraestrutura, CI/CD, auth, multi-tenancy |
| **Odair** | Frontend (React + Next.js), UI components, Tailwind, shadcn/ui, UX |

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
- [ ] Criar repositório Git
- [ ] Estruturar pastas (backend/, frontend/, docs/)
- [ ] Setup Django + Django REST Framework
- [ ] django-tenants configurado (schema-level isolation)
- [ ] Signup de tenant (cria schema + usuário admin)
- [ ] Login + JWT (autenticação backend)
- [ ] Middleware de tenant context (`x-tenant-id`)
- [ ] Setup Docker local (PostgreSQL + Redis)
- [ ] CI/CD pipeline (GitHub Actions → Railway + Vercel)
- [ ] Variáveis de ambiente (.env)
- [ ] Sentry + structlog configurado
- [ ] Rate limiting no backend
- [ ] Documentar endpoints iniciais

### Odair — Frontend Setup
- [ ] Setup Next.js + TypeScript strict
- [ ] ESLint + Prettier configurados
- [ ] Tailwind CSS + shadcn/ui instalados
- [ ] Auth page (login, recuperação senha)
- [ ] Configurar API client (axios/fetch com interceptors)
- [ ] Layout base (sidebar, header, footer)

---

## Etapa 1: CRM Core (Semanas 3-4)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Cadastro de clientes e leads funcionando com multi-tenancy.

### Marcos — Backend API
- [ ] CRUD de Leads (`POST/GET/PATCH /leads`)
- [ ] CRUD de Customers (`GET/POST /customers`)
- [ ] Conversão Lead → Customer (endpoint)
- [ ] Tags, contatos, notas, timeline
- [ ] Permissões por tenant (django-guardian)
- [ ] Filtros por schema em todos os endpoints
- [ ] Audit log (django-simple-history)
- [ ] Testes unitários (modelos + views)
- [ ] Documentar todos os endpoints na API.md

### Odair — Frontend
- [ ] Listagem de leads com filtros
- [ ] Formulário de lead + validação
- [ ] Detalhe de customer + timeline
- [ ] Conversão lead → customer (UI)
- [ ] Dashboard simples (cards + gráfico)
- [ ] Autenticação integrada (guardar JWT, redirect)
- [ ] Tratamento de erros (toast notifications)

---

## Etapa 2: Agenda (Semanas 5-6)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Agendamento de serviços com controle de disponibilidade.

### Marcos — Backend API
- [ ] Model Professional (perfil + especialidades)
- [ ] Model Service (duração, preço)
- [ ] CRUD de Appointments
- [ ] Regras de conflito (horário indisponível)
- [ ] Disponibilidade por profissional
- [ ] Integração Google Calendar (adapter pattern)
- [ ] Webhook de confirmação
- [ ] Testes de conflito (edge cases)

### Odair — Frontend
- [ ] Calendário mensal (FullCalendar ou equivalente)
- [ ] Formulário de agendamento
- [ ] Lista de profissionais com disponibilidade
- [ ] Seleção de serviço + profissional
- [ ] Confirmação/cancelamento pelo cliente
- [ ] Visualização de agenda do tenant
- [ ] Responsividade mobile

---

## Etapa 3: Omnichannel (Semanas 7-8)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Atendimento via Telegram integrado ao CRM.

### Marcos — Backend API
- [ ] Telegram Bot webhook
- [ ] Model Conversation + ConversationMessage
- [ ] Normalização de mensagens
- [ ] Atribuição para atendente
- [ ] Integração com CRM (lead criado a partir de mensagem)
- [ ] Redis para cache de sessões
- [ ] Rate limiting por canal
- [ ] Testes de webhook (simulação)
- [ ] Adapter pattern para canais futuros (WhatsApp)

### Odair — Frontend
- [ ] Interface de atendimento ao vivo
- [ ] Lista de conversas
- [ ] Mensagens em tempo real (polling)
- [ ] Mensagens automáticas (templates)
- [ ] Badge de status do agente
- [ ] Painel de gestão de canais

---

## Etapa 4: AI Assistant (Semanas 9+)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Automação com IA para triagem de leads e respostas.

### Marcos — Backend API
- [ ] Integração OpenAI API (classificação de intenção)
- [ ] Respostas automáticas (RAG - FAQs)
- [ ] Resumo de conversa (LLM)
- [ ] Extração de dados do cliente (nome, telefone, serviço)
- [ ] Circuit breaker para OpenAI
- [ ] Cache de respostas (Redis)
- [ ] Logs de interação com IA (audit)
- [ ] Prompt management (templates parametrizáveis)

### Odair — Frontend
- [ ] Badge "IA respondeu" nas mensagens
- [ ] Botão "Melhore esta resposta"
- [ ] Painel de configuração de IA
- [ ] Histórico de interações da IA
- [ ] Ajustes de prompt (UI amigável)

---

## Etapa 5: Configurações & Profissionais (Semanas 11+)

**Responsáveis:** Marcos (backend) + Odair (frontend)

**Objetivo:** Gestão de profissionais e configurações do tenant.

### Marcos — Backend API
- [ ] CRUD de Profissionais
- [ ] Comissões e percentuais
- [ ] Configurações do tenant (horários, branding)
- [ ] Integrações externas (Google Calendar adapter)
- [ ] Webhooks configuráveis
- [ ] API keys management
- [ ] Rate limiting por plano

### Odair — Frontend
- [ ] Gestão de profissionais (CRUD + agenda)
- [ ] Configurações do tenant (logo, cores, horários)
- [ ] Painel de integrações
- [ ] Dashboard de profissionais
- [ ] Configurações de notificação

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
> **Atualização:** Conforme etapas concluídas