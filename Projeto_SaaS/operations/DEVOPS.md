# DEVOPS.md — CI/CD v1.0

## Ambientes
Development, Staging/Homologação e Production.

## Pipeline
1. lint/format;
2. testes unitários;
3. testes de integração;
4. análise de segurança/dependências;
5. build;
6. migrations controladas;
7. deploy;
8. smoke tests;
9. monitoramento.

## Rollback
Toda versão implantável deve possuir estratégia de rollback compatível com migrations e mudanças de dados.

## Secrets
Segredos somente em secret manager/variáveis protegidas; nunca no repositório.
