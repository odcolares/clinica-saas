# DISASTER-RECOVERY.md — Disaster Recovery v1.0

## Objetivo
Restaurar serviços e dados após falha grave.

## RPO/RTO
Os valores definitivos devem ser aprovados conforme criticidade do negócio e capacidade de infraestrutura antes da produção.

## Processo
1. detectar incidente;
2. classificar severidade;
3. preservar evidências;
4. acionar plano;
5. restaurar infraestrutura/dados;
6. validar integridade;
7. executar smoke tests;
8. liberar operação;
9. realizar pós-incidente.

## Testes
DR deve ser exercitado periodicamente, com evidências e ações corretivas.
