# TECH-STACK.md — Diretrizes de Stack v1.0

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

## Regra de consolidação
Nenhuma tecnologia adicional deve ser introduzida durante a implementação sem atualizar este documento e avaliar impacto arquitetural.
