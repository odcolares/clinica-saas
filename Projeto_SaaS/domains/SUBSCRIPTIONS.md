# SUBSCRIPTIONS.md — Assinaturas v1.0

## Objetos
Plan, PlanFeature/Limit, Subscription, SubscriptionPeriod e BillingEvent.

## Plano
Define recursos e limites disponíveis.

## Subscription
Relaciona Tenant ao plano e controla estado e período contratado.

## Ciclo
- Ativa.
- Renovação.
- Upgrade.
- Downgrade.
- Suspensão/cancelamento conforme política.

## Controle de acesso
A aplicação deve consultar o entitlement do tenant antes de liberar recursos limitados pelo plano.

## Billing
Cobrança e eventos financeiros devem possuir rastreabilidade e integração desacoplada. A assinatura não deve alterar diretamente lançamentos financeiros sem passar pelo contrato do Finance.
