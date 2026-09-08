# INFRASTRUCTURE.md — Infraestrutura v1.0

## Ambientes
Separação lógica e, quando necessário, física entre desenvolvimento, homologação e produção.

## Componentes
- Aplicação/API.
- Banco de dados.
- Cache/fila quando necessário.
- Armazenamento.
- Reverse proxy/load balancer quando aplicável.
- Monitoramento e logs.

## Rede
Princípio de menor privilégio, portas mínimas, segmentação e acesso administrativo restrito.

## Provisionamento
Infraestrutura deve ser documentada e, quando possível, reproduzível por IaC.

## Operação
Monitorar disponibilidade, CPU, memória, armazenamento, banco, filas, erros de API e integrações externas.
