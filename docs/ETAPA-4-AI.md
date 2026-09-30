# AI Assistant (Etapa 4) — Entrega Marcos

## Decisões de arquitetura

### Módulos em `apps/ai/services/`
Os 5 módulos do brief (intent, extraction, rag, summarizer, auto_reply) vivem como pacotes Python dentro de `apps/ai/services/`. Cada módulo é um pacote com `__init__.py` que expõe a função principal — evita conflito com `apps/ai/services.py` (existente na branch, contém `record_interaction`/`render_prompt`).

### Por que services/ como pacote e não services.py
- `apps/ai/services.py` já existe nesta branch com `record_interaction` e `render_prompt`.
- O brief exige 5 serviços independentes; um único arquivo ficaria >500 linhas e acoplado.
- Cada módulo é importável como `apps.ai.services.intent` — mesmo import path que o brief especifica.
- Serviços chamam `apps.ai.client`, `apps.ai.breaker`, `apps.ai.cache` — nunca OpenAI direto.
- Cada chamada a um serviço grava `LLMInteraction` via `record_interaction`.

### Separação de responsabilidades
- `services/intent.py` — classifica intenção via Structured Outputs.
- `services/extraction.py` — extrai dados via function calling strict.
- `services/rag.py` — FAQ ILIKE + embedding stub; documenta migração pgvector.
- `services/summarizer.py` — resumo PT-BR, temperature 0.
- `services/auto_reply.py` — monta contexto RAG + resposta.
- `apps/ai/views_ai.py` — DRF endpoints tenant-scoped.
- `apps/omnichannel/urls.py` — append das rotas AI.

### Tenant isolation
Todo endpoint filtra por schema/tenant. Tenant vem do JWT claim ou header `x-tenant-id` (middleware existente). Views derivam do tenant ativo — sem dado cross-tenant.

### Mock local quando infra não existir
Caso `PromptTemplate`/`AsyncOpenAI client`/`breaker`/`cache`/`LLMInteraction` não existissem, seria criado mock local com mesmo import path. Como a infra existe nesta branch, o código usa os objetos reais.

### Testes
- `apps/ai/tests/test_features.py` — 8+ testes, mock do client OpenAI, sem chave real.
- Cobrem: classify_intent, extract_client_data, rag retrieval, summarize, auto_reply, endpoints, tenant isolation, breaker/cache.
