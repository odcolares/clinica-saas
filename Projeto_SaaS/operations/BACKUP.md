# BACKUP.md — Backup v1.0

## Estratégia
- Backup completo inicial.
- Incrementais subsequentes conforme janela definida.
- Cópias protegidas contra perda do ambiente primário.
- Retenção definida por política operacional.

## Banco
Backups devem ser consistentes e testados quanto à restauração.

## Testes
A existência de backup não é considerada suficiente: restaurações devem ser testadas periodicamente e documentadas.

## Segurança
Backups devem possuir controle de acesso e proteção contra alteração/eliminação indevida.
