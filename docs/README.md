# Clínica SaaS — API Documentation

> **Responsável:** Marcos (Backend)
> **Stack:** Django 5 + Django REST Framework + django-tenants

## Structure

This directory contains auto-generated and manually maintained API documentation for the Clínica SaaS backend.

## Contents

- `API-CONTRACT.md` — Full API contract with endpoint specs, request/response schemas, and error codes
- `openapi.yaml` — OpenAPI 3.0 schema (auto-generated via drf-spectacular)
- `ARCHITECTURE.md` — Backend architecture decisions and patterns

## Quick Start

```bash
cd backend
cp .env.example .env
docker compose up -d
```

API base: `http://localhost:8000/api/v1/`

See `Projeto_SaaS/architecture/API.md` for endpoint contracts (canonical source).
