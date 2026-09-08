# SECURITY.md — Segurança v1.0

## Controles
- Isolamento por tenant.
- RBAC.
- Validação server-side.
- Rate limiting.
- Proteção contra replay em webhooks.
- Criptografia em trânsito e em repouso quando aplicável.
- Secrets management.
- Auditoria.
- Gestão segura de sessão.

## Logs
Nunca registrar senha, token, segredo, credencial ou conteúdo sensível desnecessário.

## Webhooks
Validar assinatura/autenticidade, timestamp/nonce quando suportado, idempotência e origem.

## Princípio
Deny by default: ausência de permissão significa ausência de acesso.
