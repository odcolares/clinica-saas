# CRM.md — CRM v1.0

## Objetos
Customer, Lead, CustomerContact, CustomerAddress, CustomerNote, LeadSource, LeadStatus, LeadAssignment, CustomerTag e Interaction.

## Lead
Estados:
`NEW → CONTACTED → QUALIFIED → CONVERTED`
com caminhos controlados para `LOST` e reativação.

Toda transição registra autor, data e motivo quando aplicável.

## Conversão
Ao converter:
1. procurar Customer existente por critérios configurados;
2. se existir, vincular;
3. se não existir, criar;
4. preservar o Lead original;
5. registrar auditoria.

## Atribuição
Pode considerar origem, serviço, região, disponibilidade e fila. Deve existir fallback para fila geral.

## Timeline
A timeline consolida interações relevantes sem duplicar dados proprietários de Quotes, Agenda ou Finance.

## Limites
CRM não é proprietário de orçamento, agendamento ou pagamento.
