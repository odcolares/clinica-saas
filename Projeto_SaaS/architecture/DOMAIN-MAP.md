# DOMAIN-MAP.md — Mapa do Ecossistema de Domínios

## 1. Objetivo
Mapear os domínios do produto, suas responsabilidades, entidades proprietárias, dependências e fronteiras. Este documento orienta onde uma nova regra deve ser implementada.

## 2. Visão geral
```text
                         ┌──────────────────┐
                         │    SaaS Admin    │
                         └────────┬─────────┘
                                  │
┌──────────────┐          ┌───────▼────────┐          ┌──────────────┐
│ Omnichannel  │─────────▶│      CRM       │◀─────────│     AI       │
└──────┬───────┘          └───────┬────────┘          └──────────────┘
       │                           │
       │                    ┌──────▼───────┐
       │                    │    Quotes    │
       │                    └──────┬───────┘
       │                           │
       │                    ┌──────▼───────┐
       └───────────────────▶│  Scheduling  │
                            └──────┬───────┘
                                   │
                            ┌──────▼───────┐
                            │   Finance    │
                            └──────────────┘

Auth/RBAC, Security, Audit, Observability, Subscriptions e Integrations atravessam os domínios.
```

## 3. Auth/RBAC
Responsável por identidade, autenticação, sessão, roles e permissões. Não deve incorporar regras de negócio específicas de CRM ou financeiro.

## 4. CRM
Proprietário de Lead e Customer. Responsável por ciclo de relacionamento, cadastro, contatos, tags, notas, interações e timeline comercial.

## 5. Quotes
Proprietário de Quote, QuoteItem e QuoteApproval. Responsável por composição comercial, validade, estados e registro da decisão do cliente.

## 6. Scheduling
Proprietário de Appointment, disponibilidade, profissionais e regras de conflito. Pode consumir dados de Customer, Service e Professional por contratos apropriados.

## 7. Finance
Proprietário de Payment e CashTransaction. Responsável por registro financeiro e integração com provedores de pagamento.

## 8. Omnichannel
Proprietário de Conversation e ConversationMessage. Responsável pela entrada/saída de mensagens, normalização, status de entrega e vínculo com entidades internas.

## 9. AI
Camada transversal de inteligência. Consome contexto permitido dos domínios e devolve resultados estruturados. Não deve tornar-se proprietário duplicado das entidades de negócio.

## 10. SaaS Admin
Responsável pela operação global: tenants, planos, assinaturas, entitlements, suporte e configurações de plataforma.

## 11. Subscriptions
Define estado de assinatura, plano, recursos e limites aplicáveis ao tenant. Pode ser módulo do SaaS Admin ou domínio separado conforme evolução.

## 12. Integrations
Responsável pelos adapters e contratos com serviços externos: canais, Google Calendar, provedores de pagamento, e-mail e outros.

## 13. Camadas transversais
- Security
- Audit
- Observability
- QA
- DevOps
- Backup
- Disaster Recovery

## 14. Regras de dependência
1. Um domínio não deve acessar diretamente tabelas internas de outro domínio apenas por conveniência.
2. Compartilhamento deve ocorrer por serviço, contrato, evento ou leitura explicitamente autorizada.
3. A propriedade da entidade permanece em um único domínio.
4. Integrações externas nunca devem definir diretamente o modelo interno sem normalização.
5. Falhas de integrações externas devem ser isoladas e observáveis.

## 15. Fluxos principais
### Comercial
Omnichannel/Atendimento → CRM → Quotes → Approval → Scheduling → Finance.

### Atendimento
Canal → Webhook → Omnichannel → CRM → Humano/Automação/IA.

### Agenda
Customer + Service + Professional → Scheduling → Calendar Adapter.

### Financeiro
Quote/Appointment → intenção financeira → Payment Provider → Finance → histórico.

## 16. Regra para novas entidades
Antes de criar uma entidade, identificar o domínio proprietário. Evitar duplicação semântica como `Customer` em múltiplos módulos.

## 17. Regra para novos eventos
Eventos devem representar fatos de negócio relevantes, possuir versão e payload estável, ser idempotentes quando necessário e não expor dados sensíveis desnecessários.
