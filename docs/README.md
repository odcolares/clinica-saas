# Clínica SaaS — API Documentation

> **Responsável:** Marcos (Backend)
> **Stack:** Django 5 + Django REST Framework + django-tenants

## Structure

This directory contains auto-generated and manually maintained API documentation for the Clínica SaaS backend.

## Contents

- `API-FUNDACAO.md` — Endpoints da fundação (ETAPA 0): health, signup, auth JWT
- `API-CRM.md` — Endpoints do CRM (ETAPA 1): leads, customers, contatos, endereços, notas, timeline, tags
- `Projeto_SaaS/architecture/API.md` — Contrato canônico de alto nível

## Quick Start

```bash
cd backend
cp .env.example .env
docker compose up -d
```

API base: `http://localhost:8000/api/v1/`

See `Projeto_SaaS/architecture/API.md` for endpoint contracts (canonical source).
