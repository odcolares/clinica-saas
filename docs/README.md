# Clínica SaaS — API Documentation

> **Responsável:** Marcos (Backend)
> **Stack:** Django 5 + Django REST Framework + django-tenants

## Structure

This directory contains auto-generated and manually maintained API documentation for the Clínica SaaS backend.

## Contents

- `API-FUNDACAO.md` — Endpoints da fundação (ETAPA 0): health, signup, auth JWT
- `API-CRM.md` — Endpoints do CRM (ETAPA 1): leads, customers, contatos, endereços, notas, timeline, tags
- `API-SCHEDULING.md` — Endpoints da Agenda (ETAPA 2): profissionais, serviços, agendamentos, disponibilidade
- `API-OMNICHANNEL.md` — Endpoints do Omnichannel (ETAPA 3): conversas, mensagens, atribuição, resposta, webhook Telegram
- `Projeto_SaaS/architecture/API.md` — Contrato canônico de alto nível

## Quick Start

Modo tradicional local (sem containers): PostgreSQL local + Redis via WSL.

```bat
REM a partir da raiz do repo
copy backend\.env.example backend\.env
.\subir-aplicacao.bat
```

O script garante role/database `clinica` no Postgres local, sobe o Redis
no WSL, aplica `migrate_schemas` e abre backend (`:8000`) + frontend (`:3000`).

API base: `http://localhost:8000/api/v1/`

See `Projeto_SaaS/architecture/API.md` for endpoint contracts (canonical source).
