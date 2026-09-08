# PROJECT-CONTEXT.md — Contexto Mestre do Projeto

## 1. Propósito
Este é o primeiro arquivo a ser lido por qualquer pessoa ou agente de desenvolvimento que trabalhe no Projeto SaaS. Ele define o norte do produto, a ordem de leitura da documentação e as regras que não devem ser quebradas sem decisão explícita.

## 2. Produto em uma frase
Plataforma SaaS multi-tenant para gestão de clientes, leads, serviços, profissionais, orçamentos, agenda, pagamentos, atendimento omnichannel, automações e recursos de IA.

## 3. Ordem oficial de leitura
1. `PROJECT-CONTEXT.md`
2. `docs/PRODUCT-CONCEPT.md`
3. `architecture/DOMAIN-MAP.md`
4. `architecture/ARCHITECTURE.md`
5. `architecture/TECH-STACK.md`
6. `architecture/API.md`
7. `design/DESIGN.md`
8. Documentos de domínio em `domains/`
9. `security/SECURITY.md`
10. `operations/QA.md`
11. `operations/DEVOPS.md`
12. `operations/INFRASTRUCTURE.md`
13. `operations/BACKUP.md`
14. `operations/DISASTER-RECOVERY.md`
15. `docs/DEVELOPMENT-CONTEXT.md`
16. `docs/CONSOLIDATION.md`

## 4. Regras arquiteturais obrigatórias
- Multi-tenancy existe desde o início; isolamento de dados é requisito estrutural.
- O backend é a autoridade para tenant, autenticação, autorização e regras de negócio.
- Nunca confiar somente em `tenant_id` enviado pelo frontend.
- RBAC e permissões granulares devem ser aplicados no backend.
- Cada domínio possui propriedade clara sobre seus dados.
- Integrações externas devem usar adapters/contracts.
- Webhooks devem validar autenticidade, ser idempotentes quando aplicável e impedir processamento duplicado.
- Operações críticas devem possuir auditoria.
- Segredos, tokens e credenciais nunca devem aparecer em logs.
- Aprovação de orçamento não é pagamento.
- IA é uma camada controlada de assistência; não recebe autoridade implícita para ações críticas.
- Assinaturas e entitlements controlam acesso a recursos e limites.

## 5. Fluxo de negócio canônico
Lead → Qualificação → Customer → Quote → Aprovação → Appointment → Payment → Execução → Histórico/Fidelização.

## 6. Fluxo omnichannel canônico
Canal → Adapter → Webhook → Validação → Normalização → Conversation → Lead/Customer → Timeline → Atendimento/Automação/IA.

## 7. Fluxo de segurança canônico
Request → Authentication → Tenant Context → Authorization → Domain Validation → Persistence → Audit.

## 8. Propriedade dos dados
- CRM: Lead, Customer, contatos, endereços, tags e timeline comercial.
- Quotes: Quote, QuoteItem e QuoteApproval.
- Scheduling: Appointment e disponibilidade.
- Finance: Payment e CashTransaction.
- Omnichannel: Conversation e ConversationMessage.
- SaaS Admin: Tenants, planos, assinaturas, entitlements e administração da plataforma.

## 9. Como uma nova funcionalidade deve ser desenvolvida
Antes de codificar:
1. identificar o domínio proprietário;
2. verificar o modelo de dados;
3. verificar regras de autorização e tenant;
4. definir contrato/API/eventos;
5. definir auditoria e idempotência;
6. definir testes;
7. avaliar impacto em integrações, assinatura e observabilidade;
8. atualizar documentação afetada.

## 10. Definition of Done
Uma funcionalidade só é considerada concluída quando código, persistência, autorização, testes, observabilidade, documentação e tratamento de falhas necessários estiverem coerentes com este contexto.

## 11. Regra para decisões não definidas
Não inventar decisões de negócio, preços, limites, RPO/RTO, fornecedores ou políticas legais como se fossem definitivos. Quando ainda não aprovados, tratar como parametrizáveis e registrar a decisão necessária.

## 12. Norte
> Entender o produto antes de codificar, respeitar o domínio antes de alterar dados, validar segurança antes de expor comportamento e documentar a decisão antes de consolidá-la.
