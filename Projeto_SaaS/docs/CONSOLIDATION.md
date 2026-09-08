# CONSOLIDATION.md — Consolidação Final da Documentação v1.0

## Status
CONSOLIDADA PARA IMPLEMENTAÇÃO

## Decisões globais
1. Multi-tenant obrigatório.
2. Tenant deriva do contexto autenticado; não confiar em tenant_id enviado pelo cliente.
3. RBAC + permissões granulares.
4. Auditoria de operações relevantes.
5. CRM não é proprietário de orçamento, agenda ou financeiro.
6. Quote aprovado não significa pagamento.
7. Scheduling é proprietário de Appointment.
8. Finance é proprietário de Payment e CashTransaction.
9. Omnichannel usa adapters por canal.
10. IA não possui autoridade implícita sobre ações críticas.
11. Secrets nunca aparecem em logs.
12. Integrações externas devem ser idempotentes quando necessário.
13. Migrations são versionadas.
14. Backup deve ser restaurável e DR deve ser testado.
15. SaaS Admin é separado do Admin do Tenant.
16. Subscription controla entitlements e limites.

## Fluxos canônicos

### Comercial
Lead → Qualified → Customer → Quote → Approved → Appointment → Payment → Service.

### Comunicação
Channel → Adapter → Webhook → Normalization → Conversation → Lead/Customer → Timeline.

### Segurança
Request → Authentication → Tenant Context → Authorization → Domain Validation → Persistence → Audit.

## Pontos que permanecem parametrizáveis
- Valores de RPO/RTO.
- Planos, preços e limites.
- Política exata de descontos.
- Prazos de retenção.
- Provedor/tecnologia definitiva de cada componente da stack, caso ainda não tenha sido formalmente aprovada.

## Critério de encerramento
A documentação v1.0 está pronta para entrar na fase de implementação desde que os itens parametrizáveis sejam definidos no momento em que forem necessários e qualquer decisão que altere arquitetura seja refletida nos respectivos .md.
