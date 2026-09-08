# DEVELOPMENT-CONTEXT.md — Guia de Desenvolvimento por Domínio

## 1. Objetivo
Traduzir o conceito e o mapa de domínios em regras práticas para implementação. O desenvolvedor deve usar este documento junto com o documento específico do domínio.

## 2. Processo padrão de desenvolvimento
1. Ler `PROJECT-CONTEXT.md`.
2. Ler `PRODUCT-CONCEPT.md`.
3. Localizar o domínio em `DOMAIN-MAP.md`.
4. Ler o documento específico do domínio.
5. Fazer análise de impacto.
6. Definir alterações de dados, API, eventos, permissões e auditoria.
7. Implementar em pequenas mudanças verificáveis.
8. Testar caminho feliz e falhas.
9. Atualizar documentação.

## 3. Auth/RBAC
Implementar autenticação e autorização como preocupações centrais. Toda operação protegida deve verificar identidade, tenant e permissão. Nunca usar somente ocultação de botão como controle de acesso.

## 4. Database
Migrations devem ser versionadas. Índices devem acompanhar padrões de consulta. Constraints devem proteger invariantes importantes. Dados financeiros e de auditoria não devem ser apagados por conveniência.

## 5. CRM
Lead e Customer pertencem ao CRM. Conversão de lead não deve destruir histórico. A timeline deve preservar contexto. Pesquisas e filtros devem considerar tenant e performance.

## 6. Quotes
Estados devem possuir transições válidas. Totais devem ser calculados de forma consistente. Aprovação deve ser registrada com timestamp, ator e contexto. Aprovação não cria automaticamente um pagamento.

## 7. Scheduling
Validar conflitos, disponibilidade e permissões no backend. Integrações de calendário devem ser tratadas como externas e eventualmente inconsistentes; usar reconciliação e idempotência.

## 8. Finance
Valores monetários devem usar representação adequada. Pagamentos devem ter identificador externo quando houver provedor. Webhooks financeiros devem ser autenticados, idempotentes e auditáveis.

## 9. Omnichannel
Criar um modelo interno normalizado. Adapters traduzem formatos externos para o modelo interno. Webhooks devem validar assinatura/origem quando suportado, evitar replay, persistir eventos e tratar duplicidade.

## 10. AI
Prompts, modelos e políticas devem ser versionáveis. Entradas devem ser minimizadas. Saídas estruturadas devem ser validadas. Ações críticas exigem regra explícita e, quando aplicável, confirmação humana.

## 11. SaaS Admin
Separar claramente administração global de administração do tenant. Acesso administrativo deve ser altamente auditado. Não permitir que uma operação global seja confundida com permissão de usuário do cliente.

## 12. Subscriptions
Features e limites devem ser verificados por entitlements. Evitar espalhar regras de plano por dezenas de endpoints; centralizar política de acesso a capacidades.

## 13. API
Contratos devem ser explícitos, versionáveis e consistentes. Erros devem possuir formato previsível. Validação de entrada é obrigatória. Paginação, filtros e ordenação devem ter comportamento documentado.

## 14. Segurança
Aplicar menor privilégio, validação server-side, proteção de segredos, logs sem dados sensíveis, rate limiting onde necessário e auditoria das ações relevantes.

## 15. Testes
Cada alteração deve avaliar unitários, integração e, quando necessário, testes de contrato/E2E. Testar principalmente isolamento de tenant, autorização, idempotência e transições de estado.

## 16. Observabilidade
Operações importantes devem gerar logs estruturados e métricas úteis. Correlation/request IDs devem permitir rastrear uma operação entre componentes sem registrar segredos.

## 17. Backup e continuidade
Backups devem ser verificáveis. Restauração deve ser testada. O sistema deve possuir procedimento operacional para incidentes, recuperação e validação pós-restore.

## 18. Checklist de PR
- [ ] Domínio correto.
- [ ] Tenant isolation validado.
- [ ] Autorização validada.
- [ ] Regras de negócio cobertas.
- [ ] Migration segura.
- [ ] API/eventos atualizados.
- [ ] Idempotência avaliada.
- [ ] Auditoria avaliada.
- [ ] Logs sem segredos.
- [ ] Testes adicionados/atualizados.
- [ ] Documentação atualizada.

## 19. Regra de mudança arquitetural
Se a implementação exigir quebrar uma fronteira de domínio, duplicar propriedade de entidade ou alterar uma decisão estrutural, interromper a implementação dessa parte e registrar a decisão arquitetural antes de consolidar a mudança.
