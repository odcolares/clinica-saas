# ARCHITECTURE.md — Arquitetura v1.0

## Arquitetura lógica
A solução é organizada por domínios, com contratos entre módulos e baixo acoplamento.

### Domínios
- Auth/RBAC
- CRM
- Quotes
- Scheduling
- Finance
- Omnichannel
- AI
- SaaS Administration
- Subscriptions

### Camadas transversais
Security, Audit, Observability, QA, DevOps, Backup e Disaster Recovery.

## Isolamento
Toda operação de dados deve carregar e validar o contexto de Tenant. O tenant nunca é aceito apenas de um campo enviado pelo cliente; o backend deriva/valida o contexto a partir da identidade autenticada.

## Integrações
Canais externos usam adapters e webhooks. Módulos internos comunicam-se por serviços/contratos definidos, evitando acesso direto indevido às tabelas de outros domínios.

## Propriedade dos dados
CRM é proprietário de Lead/Customer. Quotes é proprietário de Quote/QuoteItem. Scheduling é proprietário de Appointment. Finance é proprietário de Payment/CashTransaction. Omnichannel é proprietário de Conversation/ConversationMessage.
