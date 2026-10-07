# TECH-STACK.md — Diretrizes de Stack v1.0

## Stack Definida

| Camada | Tecnologia | Custo | Observação |
|--------|-----------|-------|------------|
| **Backend/API** | Django 5 + Django REST Framework | $0 | Auth, admin, ORM, migrations built-in |
| **Frontend** | React + Next.js | $0 | SSR/SSG, rotas, hooks, SSR streaming |
| **UI Components** | shadcn/ui | $0 | Componentes modernos, acessíveis, customizáveis |
| **Estilo** | Tailwind CSS | $0 | Utilitários CSS, design system responsivo |
| **Banco de Dados** | PostgreSQL 16 | $0 | Schema-level multi-tenancy via django-tenants |
| **Multi-tenancy** | django-tenants | $0 | Isolation por schema (1 schema = 1 tenant) |
| **Fila/Async** | Redis + Celery | $0 | Webhooks, tarefas assíncronas, rate limiting |
| **RBAC** | django-guardian | $0 | Permissões granulares por objeto |
| **Audit Log** | django-simple-history | $0 | Rastreabilidade de alterações |
| **Omnichannel** | Telegram Bot API + WhatsApp Business API (Twilio) | $0 / pago | Telegram grátis; WhatsApp cobra por mensagem (~$0.005/msg) |
| **IA** | Ollama (local) / OpenAI API (produção) | $0 / pago | Ollama para dev; OpenAI para produção |
| **Pagamentos (assinatura SaaS)** | Mercado Pago | $0 mensal | ~3.99% por transação, recorrência nativa |
| **E-mail** | SendGrid (free tier) / Gmail SMTP | $0 | Até 100 e-mails/dia grátis |
| **Storage** | Cloudflare R2 | $0 | 10GB grátis, sem egress fee |
| **Deploy** | Render.com (free tier, 500 hrs/mo) | $0 | 500 horas/mês inclui PostgreSQL 256MB + Redis 25MB |
| **CI/CD** | GitHub Actions | $0 | 2000 min/mês para repos privados |
| **Secrets** | Variáveis de ambiente (.env) | $0 | Migrar para AWS Secrets Manager em produção |
| **Observabilidade** | structlog + Sentry (free tier) | $0 | Logs JSON + captura de erros |

## Diretrizes

A stack definitiva deve ser registrada aqui antes da implementação concreta, mantendo separação entre:
- aplicação frontend;
- API/backend;
- banco de dados;
- filas/eventos;
- integrações externas;
- observabilidade;
- CI/CD.

## Requisitos técnicos
- Banco relacional com migrations versionadas.
- API com autenticação e autorização centralizadas.
- Secrets fora do código-fonte.
- Logs estruturados sem credenciais ou tokens.
- Testes automatizados no pipeline.
- Ambientes separados para desenvolvimento, homologação e produção.

## Omnichannel — Detalhes

### Telegram (grátis)
- Bot API oficial: $0
- Sem custo por mensagem
- Integração simples via webhooks
- Suporta: texto, imagem, áudio, vídeo, documentos, localização
- **Disponível desde o dia 1**

### WhatsApp (pago)
- Provedor: Twilio WhatsApp API
- Custo: ~$0.005 por mensagem enviada/recebida
- Requer: conta Twilio + número de telefone verificado + aprovação da Meta
- **Recomendação:** Adicionar após validação do MVP (não bloqueante)
- Alternativa futura: Evolution API (self-hosted, open source)

## Custos estimados (MVP)

```
Hospedagem Backend (Render.com):        $0
Hospedagem Frontend (Vercel):          $0
PostgreSQL (Render):                  $0
Redis (Railway):                    $0
Telegram Bot:                       $0
WhatsApp (Twilio - 100 msg):       ~$0.50
OpenAI API (uso leve):              ~$5-10
Mercado Pago:                       $0 mensal (só ~3.99% por transação)
E-mail (SendGrid free):             $0
                                    ───────
Total estimado:                     ~$5-10/mês
```

## Regra de consolidação
Nenhuma tecnologia adicional deve ser introduzida durante a implementação sem atualizar este documento e avaliar impacto arquitetural.
