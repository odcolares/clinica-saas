# PROJECT.md — Especificação do Projeto v1.0

## Objetivo
Plataforma SaaS multi-tenant para gestão de relacionamento, atendimento omnichannel, orçamentos, agenda, pagamentos, automações e recursos de IA.

## Princípios
- Multi-tenant por padrão.
- Segurança e autorização no backend.
- Separação clara de responsabilidades entre módulos.
- Auditoria de operações relevantes.
- APIs versionadas e contratos explícitos.
- IA como camada assistiva/controlada, sem autoridade implícita sobre ações críticas.

## Fluxo de negócio de referência
Lead → Qualificação → Customer → Quote → Aprovação → Appointment → Payment → Execução → Histórico/Fidelização.

## Regra
A aprovação do orçamento não representa pagamento. O financeiro permanece responsável pelas transações financeiras.
