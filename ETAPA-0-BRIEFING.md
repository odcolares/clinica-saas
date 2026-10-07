# ETAPA 0 — Briefing do CTO (Marcos) — SOMENTE ETAPA 0, NÃO ir para ETAPA 1

> Arquivo de apoio aos agentes conectados no canvas Maestri.
> Espelha a nota do canvas `ETAPA-0-Briefing-Marcos`.

## 1. Fato observado (repo em C:\Users\Marcos\Downloads\PROJETOS\clinica-saas)
- Branch `master`; origin `https://github.com/odcolares/clinica-saas.git`; último commit `6a17241`.
- Na raiz NÃO existem `backend/`, `frontend/`, `docs/`. Existe `Projeto_SaaS/` (PROJECT-CONTEXT.md,
  architecture/, domains/, design/, operations/, security/, docs/) + `ETAPAS.md` + `.gitignore`.
- Ou seja: ETAPA 0 ainda NÃO foi iniciada em código. Só existe documentação/produto.

## 2. Escopo — tarefas do MARCOS na ETAPA 0 (ver ETAPAS.md, sem ETAPA 1)
1. Criar repositório Git (validar o existente; NÃO recriar sem ordem do CTO).
2. Estruturar pastas (`backend/`, `frontend/`, `docs/`) preservando `Projeto_SaaS/` existente.
3. Setup Django 5 + DRF.
4. django-tenants configurado (schema-level isolation).
5. Signup de tenant (cria schema + usuário admin).
6. Login + JWT.
7. Middleware de tenant context (`x-tenant-id`).
8. Setup local (PostgreSQL 16 + Redis).
9. CI/CD pipeline (GitHub Actions → Railway + Vercel).
10. Variáveis de ambiente (`.env`; nunca commitar segredos).
11. Sentry + structlog configurado.
12. Rate limiting no backend.
13. Documentar endpoints iniciais.

## 3. Documentos normativos (ler antes de agir)
- `Projeto_SaaS/PROJECT-CONTEXT.md`
- `Projeto_SaaS/docs/DEVELOPMENT-CONTEXT.md`
- `Projeto_SaaS/architecture/TECH-STACK.md`
- `Projeto_SaaS/architecture/API.md`
- `Projeto_SaaS/architecture/DOMAIN-MAP.md`
- `Projeto_SaaS/domains/DATABASE.md`
- `Projeto_SaaS/domains/AUTH.md`
- `Projeto_SaaS/operations/DEVOPS.md`
- `Projeto_SaaS/operations/INFRASTRUCTURE.md`
- `Projeto_SaaS/security/SECURITY.md`

## 4. Divisão entre os terminais já conectados (NÃO criar novos terminais)
- **OpenCode (Dev Senior)** → validar estado + criar `backend/`, PostgreSQL 16 + Redis locais,
  `.env.example`, setup Django 5 + DRF + django-tenants, base de signup/login JWT/middleware.
  Menor mudança necessária. Sem ETAPA 1 (sem CRM) e sem frontend do Odair.
- **Oh My PI (Code Reviewer)** → checklist de aceite da fundação + revisão sem alterar código
  (severidade CRÍTICO/ALTO/MÉDIO/BAIXO com local/problema/impacto/evidência/recomendação).
- **Freebuff (Hercules - QA)** → plano + validação da fundação (isolamento por schema, auth,
  rate limiting, Sentry/structlog, CI, .env), como usuário comum/técnico/malicioso.
  Documentar achados, sem corrigir.

## 5. Ordem
1. OpenCode implementa → 2. Oh My PI revisa → 3. Freebuff valida → 4. CTO consolida.

## 6. Definition of Done (Marcos, ETAPA 0)
Código + migrations + tenant isolation + JWT + middleware + ambiente local + CI + logs sem segredos
+ testes + docs de endpoints, tudo validado por review + QA.
