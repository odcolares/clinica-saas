# ETAPA 0 — Checklist de Revisão/Aceite da Fundação (Code Reviewer)

> Escopo: tarefas do **Marcos** na Etapa 0 (ver `ETAPAS.md` §Etapa 0 e `ETAPA-0-BRIEFING.md`).
> NÃO inclui Etapa 1 (CRM) nem frontend do Odair.
> Fontes normativas: `PROJECT-CONTEXT.md` §4, `ARCHITECTURE.md` (Isolamento), `TECH-STACK.md`
> (Requisitos técnicos), `SECURITY.md`, `AUTH.md`, `DATABASE.md`, `DEVOPS.md`,
> `INFRASTRUCTURE.md`, `DEVELOPMENT-CONTEXT.md` §3–4, §14–18, regras obrigatórias `ETAPAS.md` §Regras.
>
> Cada item tem: **verificar** → **evidência aceita** → **reprovação automática** (gate).
> Status do item na revisão: ✅ aceita / ❌ reprova / ⚠️ risco / ℹ️ observação.

---

## 0. Estrutura e repo (itens 1–2 do briefing)

- [ ] **F-00.1** Repositório existente validado, NÃO recriado; `master` íntegro.
  - Evidência: `git log` contínuo desde `6a17241`; nenhum `git init`/history rewrite.
  - Gate: histórico reescrito ou repo recriado sem ordem do CTO → ❌ CRÍTICO.
- [ ] **F-00.2** Pastas `backend/`, `frontend/`, `docs/` criadas **preservando** `Projeto_SaaS/` intacto.
  - Gate: qualquer arquivo de `Projeto_SaaS/` movido/apagado sem decisão registrada → ❌ ALTO.
- [ ] **F-00.3** `.gitignore` cobre `backend/.env*`, `*.sqlite3` acidental, `staticfiles/`, `media/`.
  - Risco conhecido: `.gitignore` raiz ignora `package-lock.json`/`yarn.lock`/`pnpm-lock.yaml` — antipadrão de reprodutibilidade para o frontend Next.js (decidir antes da Etapa 0 fechar; recomendar versionar lockfile).

## 1. Django 5 + DRF (item 3)

- [ ] **F-01.1** Versões pinadas (Django 5.x, DRF) em `requirements.txt`/lock com hashes ou versões exatas.
- [ ] **F-01.2** Config por ambiente via env vars; `DEBUG` nunca vem de default `True` em código de produção; `ALLOWED_HOSTS` controlado por env.
  - Gate: `DEBUG=True` hardcoded ou secret default no `settings.py` → ❌ ALTO.
- [ ] **F-01.3** `REST_FRAMEWORK` com `DEFAULT_AUTHENTICATION_CLASSES` (JWT) e `DEFAULT_PERMISSION_CLASSES = IsAuthenticated` (deny by default — `SECURITY.md` Princípio).
  - Gate: endpoint público além de signup/login/refresh/reset sem justificativa documentada → ❌ CRÍTICO.

## 2. django-tenants / isolamento por schema (item 4) — **gate central**

- [ ] **F-02.1** `TENANT_APPS`/`SHARED_APPS` declarados corretamente; apps operacionais em `TENANT_APPS`; auth/django-tenants em `SHARED_APPS`.
- [ ] **F-02.2** Custom User no schema **public** com FK `tenant` (padrão django-tenants); `AUTH_USER_MODEL` definido desde o primeiro migration (nunca trocar depois).
  - Gate: `AUTH_USER_MODEL` ausente ou migration já commitado sem ele → ❌ CRÍTICO (migration destrutiva futura).
- [ ] **F-02.3** Requisição sem tenant resolvido **não** serve dados: 401/403, nunca schema `public` como fallback silencioso.
  - Evidência: teste automatizado chamando endpoint autenticado sem header/subdomain → 401/403.
- [ ] **F-02.4** Teste de isolamento com **2 tenants reais**: dado criado via API no tenant A é invisível/inacessível (404/403) no tenant B, inclusive por enumeração de ID.
  - Gate: ausência desse teste → ❌ CRÍTICO (é o requisito estrutural do produto).
- [ ] **F-02.5** Deploy/migrations usam `migrate_schemas` (não `migrate` puro); documentado no README/CI.
  - Gate: CI roda `migrate` comum → schemas de tenant ficam sem migration → ❌ ALTO.
- [ ] **F-02.6** Django Admin não expõe travessia entre tenants (se admin habilitado em dev, justificar).

## 3. Signup de tenant (item 5)

- [ ] **F-03.1** `POST` de signup cria: schema do tenant + migrate do schema + usuário admin, **atomicamente** (ou com compensação documentada; schema órfão em falha é aceito apenas se logado/auditado).
- [ ] **F-03.2** Validação server-side: slug/domínio único, e-mail válido, senha com política mínima; erros no formato previsível (`API.md` Padrões).
- [ ] **F-03.3** Signup é rate-limited (ver F-08) e auditado (F-06).
- [ ] **F-03.4** Resposta do signup **não** retorna segredos/credenciais geradas fora do contrato documentado.

## 4. Login + JWT (item 6) — política em `AUTH.md`

- [ ] **F-04.1** Access + refresh (SimpleJWT ou equivalente); algoritmo fixo (HS256/RS256 explícito), `none` impossível.
- [ ] **F-04.2** Payload do token carrega **claim de tenant** (id/slug) + identidade; expirações definidas e **documentadas** (AUTH.md exige ciclo de vida definido; se os docs não deram número, a decisão deve ser registrada, não inventada silenciosamente — `PROJECT-CONTEXT.md` §11).
- [ ] **F-04.3** `POST /auth/logout` **invalida de fato**: refresh blacklist (`BLACKLIST_AFTER_ROTATION`) + rotação; logout com token antigo rejeitado.
  - Gate: logout que é no-op com JWT stateless → ❌ ALTO (viola AUTH.md "Logout invalida a sessão/token aplicável").
- [ ] **F-04.4** Login responde com status genérico para usuário inexistente vs senha errada (sem enumeração de conta); usuários com `status` inativo bloqueados (AUTH.md "estado do usuário").
- [ ] **F-04.5** Password reset / email verification: tokens temporários, uso único, armazenados com hash, expiração testada (AUTH.md).
- [ ] **F-04.6** Credenciais só via HTTPS em produção; `SESSION_COOKIE_*`/`CSRF` coerentes com escolha JWT (se token em localStorage/Authorization, documentar trade-off).

## 5. Middleware de tenant context `x-tenant-id` (item 7) — **tensão normativa conhecida**

`ETAPAS.md` pede middleware com `x-tenant-id`; `ARCHITECTURE.md`/`PROJECT-CONTEXT.md` §4 proíbem aceitar tenant apenas de campo do cliente. Aceite exige reconciliação:

- [ ] **F-05.1** `x-tenant-id` é no máximo **hint**: o tenant efetivo é derivado da **identidade autenticada** (claim do JWT). Header presente e divergente do token → **403**, nunca silently-win do header.
  - Evidência: teste: token do tenant A + header tenant B → 403/401 e nenhum dado de B acessível.
  - Gate: middleware que resolve schema **a partir do header antes** da autenticação/validação → ❌ CRÍTICO (cross-tenant read por header forjado).
- [ ] **F-05.2** Ordem de middleware correta no `MIDDLEWARE` (tenant context após autenticação ou com validação cruzada explícita); documentada em comentário/config.
- [ ] **F-05.3** Requisições anônimas permitidas apenas em endpoints públicos nomeados (signup/login/health).

## 6. Auditoria (regra 4; `AUTH.md` objetos; `DATABASE.md` AuditLog)

- [ ] **F-06.1** `django-simple-history` instalado e aplicado aos modelos que existem na Etapa 0 (Tenant, User); `AuditLog`/histórico **imutável** (sem rota de delete; soft-delete não se aplica a auditoria — DATABASE.md Integridade).
- [ ] **F-06.2** Eventos da Etapa 0 auditados com ator + timestamp + tenant: signup de tenant, login ok/falha, logout, refresh, password-reset solicitado/consumido.
- [ ] **F-06.3** Middleware de auditoria não grava payload com senha/token (ver F-09).

## 7. Segredos fora do código (item 10; regra 10; DEVOPS.md Secrets)

- [ ] **F-07.1** `SECRET_KEY`, `DATABASE_URL`, senha Redis/Postgres, Sentry DSN, chaves externas: **somente** via env; `settings.py` usa `env(...)` sem default real.
  - Gate: qualquer segredo literal commitado → ❌ CRÍTICO (e exige rotação + limpeza de histórico documentada).
- [ ] **F-07.2** `.env.example` completo (todas as vars, valores dummy) e versionado; `.env` ignorado.
- [ ] **F-07.3** Nenhuma credencial hardcoded nos arquivos de ambiente local; senhas dev dummy aceitas **apenas** para serviços locais e identificadas como tal.
- [ ] **F-07.4** CI usa GitHub Secrets; nenhum segredo impresso em log de pipeline.
- [ ] **F-07.5** Verificação pós-entrega: `git log -p`/grep por `SECRET_KEY=`, `postgres://`, DSN Sentry no histórico dos commits novos.

## 8. Rate limiting (item 12; `AUTH.md` Segurança; `SECURITY.md`)

- [ ] **F-08.1** Limites em `login`, `signup`, `password-reset`, `refresh` (throttling DRF ou middleware), backend Redis configurado via env.
- [ ] **F-08.2** Resposta 429 com header de retry documentado; teste automatizado dispara o limite.
- [ ] **F-08.3** Limite por IP **e** por conta/tenant onde aplicável (evitar lockout global por IP compartilhado — registrar decisão).

## 9. Sentry + structlog (item 11; TECH-STACK; SECURITY.md Logs)

- [ ] **F-09.1** structlog JSON configurado; request/correlation id (`DEVELOPMENT-CONTEXT.md` §16).
- [ ] **F-09.2** **Nenhum** `Authorization`/`Cookie`/`password`/`token` em logs: processors de scrub no structlog **e** `before_send`/`deny_urls`/`before_breadcrumb` no Sentry.
  - Evidência: teste/log de requisição de login falha mostrando payload sanitizado.
  - Gate: log de request com headers/body crus → ❌ ALTO.
- [ ] **F-09.3** Sentry inicializado só com DSN presente (dev sem DSN não quebra boot); `environment`/`release` tags definidas.

## 10. Ambiente local (item 8)

- [ ] **F-10.1** PostgreSQL **16** + Redis locais, sem containers: Postgres local com role/database documentados, Redis via WSL na porta padrão.
- [ ] **F-10.2** Usuário Postgres com privilégio de criação de schema (exigência django-tenants) — documentado; sem `superuser` hardcoded como default de produção.
- [ ] **F-10.3** Bootstrap reprodutível: `subir-aplicacao.bat` + `migrate_schemas` + `createsuperuser`; subir do zero funciona (evidência: saída real).
- [ ] **F-10.4** Portas padrão não conflitam com serviços existentes; Postgres/Redis **não** expostos publicamente em produção (INFRASTRUCTURE.md Rede) — em dev local, bind em `127.0.0.1` é preferível.

## 11. Migrations (DATABASE.md; DEVELOPMENT-CONTEXT §4)

- [ ] **F-11.1** Todas as migrations versionadas e commitadas; nenhuma alteração manual em migration existente.
- [ ] **F-11.2** CI falha se `makemigrations --check --dry-run` detectar drift.
- [ ] **F-11.3** Reversibilidade avaliada (DATABASE.md: reversíveis quando tecnicamente seguro); operações destrutivas (drop column/table) proibidas na Etapa 0 sem ADR.
- [ ] **F-11.4** Índices em `tenant`/FKs conforme DATABASE.md Integridade; constraints protegendo unicidade (slug/domínio de tenant, email de user).

## 12. CI/CD GitHub Actions (item 9; DEVOPS.md Pipeline)

- [ ] **F-12.1** Pipeline na ordem DEVOPS: lint/format → testes unit → integração → análise de dependências/segurança (`pip-audit`/`bandit` ou dependabot alert) → build → checagem de migrations. Deploy Railway separado e **somente** em branch protegida.
- [ ] **F-12.2** Testes rodam com Postgres real no CI (não sqlite — django-tenants não funciona em sqlite).
  - Gate: CI verde sem Postgres de serviço → testes de tenant fake/skip → ❌ ALTO.
- [ ] **F-12.3** Proteção de branch: merge só com review (regra 9 ETAPAS: nenhum deploy sem review); `master` não aceita push direto.
- [ ] **F-12.4** Vercel: fora do escopo de código do Marcos na Etapa 0; se aparecer workflow de deploy frontend, marcar ℹ️ (pertence ao Odair, revisar contrato de env vars).
- [ ] **F-12.5** CI não publica segredos em logs; artifacts limitados ao necessário.

## 13. Documentação de endpoints (item 13; API.md)

- [ ] **F-13.1** Endpoints da fundação documentados (signup, login, refresh, logout, password-reset, health): método, payload, respostas de erro, rate limit, requisito de tenant. Via OpenAPI (`drf-spectacular`) ou atualização de `API.md` — registrar onde.
- [ ] **F-13.2** Formato de erro padronizado e consistente com `API.md` Padrões (versionamento `/api/v1/` ou decisão registrada).
- [ ] **F-13.3** `DEVELOPMENT-CONTEXT.md` §18 checklist de PR respondido na descrição do MR.

## 14. Testes da fundação (DoD do briefing)

Mínimo aceitável (unit + integração no CI):
- [ ] **F-14.1** Signup cria schema + admin; login do admin emite JWT com claim de tenant correto.
- [ ] **F-14.2** Isolamento 2 tenants (F-02.4).
- [ ] **F-14.3** Header `x-tenant-id` divergente do token → rejeitado (F-05.1).
- [ ] **F-14.4** Logout invalida refresh; refresh reutilizado rejeitado.
- [ ] **F-14.5** Throttle dispara em login (429).
- [ ] **F-14.6** Smoke: resposta/ log não contém token/senha (F-09.2).

---

## Gatilhos de reprovação automática (resumo)

1. Tenant resolvido por header/client sem validação contra identidade → **CRÍTICO**.
2. Ausência de teste de isolamento entre 2 tenants → **CRÍTICO**.
3. Segredo no código/histórico/CI log → **CRÍTICO** + rotação obrigatória.
4. `AUTH_USER_MODEL` não definido antes das migrations → **CRÍTICO**.
5. Endpoint sensível `AllowAny` sem decisão registrada → **ALTO**.
6. CI sem Postgres real / com skip de testes de tenant → **ALTO**.
7. Logs com headers/payload cru → **ALTO**.
8. `migrate` em vez de `migrate_schemas` no fluxo de deploy → **ALTO**.

## Procedimento de revisão (quando o código do OpenCode chegar)

1. `git fetch` + diff `6a17241..HEAD` (commits novos do backend).
2. Ler `settings/` (ordenar por: MIDDLEWARE, apps, REST_FRAMEWORK, SIMPLE_JWT, TENANT_APPS/SHARED_APPS, env).
3. Rodar testes + `ruff`/`bandit` + `makemigrations --check` localmente (não alterar código).
4. Executar probes manuais: signup → login → header forjado → isolamento 2 tenants → throttle.
5. Emitir relatório: por item F-xx, status + severidade + local/problema/impacto/evidência/recomendação.

> Revisor não altera código. Decisões não documentadas (expiração JWT, limites de throttle,
> política de senha) devem ser **registradas como decisão pendente**, não inventadas
> (`PROJECT-CONTEXT.md` §11).
