# AUTH.md — Autenticação e Autorização v1.0

## Objetos
Tenant, User, Role, Permission, RolePermission, Session/RefreshToken, PasswordResetToken, EmailVerificationToken e AuditLog.

## Autenticação
- Login valida identidade e estado do usuário.
- Refresh renova sessão conforme política.
- Logout invalida a sessão/token aplicável.
- Recuperação de senha usa tokens temporários e de uso único.
- Verificação de e-mail possui expiração e invalidação após uso.

## Autorização
RBAC com permissões granulares. Toda operação sensível deve validar:
1. identidade;
2. tenant;
3. permissão;
4. regras de negócio.

## Segurança
- Senhas armazenadas apenas como hashes apropriados.
- Tokens não aparecem em logs.
- Rate limiting para autenticação e endpoints sensíveis.
- Sessões e tokens possuem ciclo de vida definido.
- Auditoria para alterações administrativas e eventos relevantes.
