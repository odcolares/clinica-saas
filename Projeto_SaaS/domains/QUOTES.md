# QUOTES.md — Orçamentos v1.0

## Objetos
Quote, QuoteItem, QuoteStatus e QuoteApproval.

## Estados
`DRAFT → SENT → APPROVED`
ou `REJECTED` / `EXPIRED`.

## Criação
Quote pertence a um Customer e contém um ou mais QuoteItems. Cada item referencia um Service e calcula quantidade, preço, desconto e subtotal.

## Descontos
Descontos devem ser explícitos, auditáveis e sujeitos às permissões/regras configuradas. Não existe aprovação dupla implícita; caso uma política futura exija limite por percentual ou valor, ela deve ser configurada como regra formal.

## Aprovação
A aprovação registra identidade, data, decisão e condições.

## Regra financeira
Quote aprovado não significa pagamento realizado.

## Integração
Quote aprovado pode iniciar o fluxo de Scheduling. Finance continua proprietário de Payment.
