# QA.md — Qualidade e Testes v1.0

## Pirâmide
- Unitários.
- Integração.
- Contratos de API.
- E2E.
- Segurança.
- Regressão.

## Cenários críticos
- Isolamento entre tenants.
- Login e autorização.
- Lead → Customer.
- Quote → aprovação.
- Quote aprovado → Appointment.
- Payment → atualização de fluxo.
- Webhooks WhatsApp/Telegram.
- Idempotência e duplicidade.
- Cancelamento/reagendamento.
- Auditoria.

## Critérios de aceite
Toda funcionalidade deve possuir critérios objetivos, testes automatizados para regras críticas e validação em ambiente de homologação antes da produção.
