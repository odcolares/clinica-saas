# Frontend — Clínica SaaS

> **Responsável:** Odair (Frontend Developer)
> **Status:** Placeholder — ETAPA 0 backend foundation em andamento.
> Este diretório está sendo preparado para o setup do Next.js por Odair.

## O que precisa ser implementado (ETAPA 0 — Odair)

Conforme `ETAPAS.md`, Etapa 0:

- [ ] Setup Next.js + TypeScript strict
- [ ] ESLint + Prettier configurados
- [ ] Tailwind CSS + shadcn/ui instalados
- [ ] Auth page (login, recuperação senha)
- [ ] Configurar API client (axios/fetch com interceptors)
- [ ] Layout base (sidebar, header, footer)

## API Client

Base URL: `http://localhost:8000/api/v1/`

### Auth endpoints (backend — Marcos)
- `POST /tenants/signup` — Criar tenant + admin
- `POST /auth/login` — Login (header `x-tenant-id: <schema_name>`)
- `POST /auth/refresh` — Refresh JWT
- `POST /auth/logout` — Logout (blacklista refresh)

### JWT Response shape
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "tenant": {
    "schema_name": "clinica_exemplo",
    "name": "Clínica Exemplo"
  }
}
```

## Como iniciar

```bash
cd frontend
npm create next-app@latest . --typescript
npm install
npm run dev
```

> Aguarde o backend estar rodando (`docker compose up` em `backend/`).
