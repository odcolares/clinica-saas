# DEVELOPMENT-CONTEXT.md — Contexto de Desenvolvimento

## Princípios
- Multi-tenant por padrão.
- Segurança e autorização no backend.
- Separação clara de responsabilidades entre módulos.
- Auditoria de operações relevantes.
- APIs versionadas e contratos explícitos.
- IA como camada assistiva/controlada, sem autoridade implícita sobre ações críticas.

## Regras operacionais
- A aprovação do orçamento não representa pagamento. O financeiro permanece responsável pelas transações financeiras.
- Tenant deriva do contexto autenticado; não confiar em tenant_id enviado pelo cliente.
- Segredos nunca aparecem em logs.
- Integrações externas devem ser idempotentes quando necessário.

## Status da implementação
Documentação v1.0 consolidada. Stack tecnológica definitiva e parâmetros operacionais (RPO/RTO, provedores, regras de desconto) ainda pendentes de definição.
