# DATABASE.md — Modelo de Dados v1.0

## Regra global
Entidades operacionais multi-tenant possuem `tenant_id` ou vínculo inequívoco com Tenant. Foreign keys, índices e políticas de acesso devem preservar isolamento.

## Objetos principais

### Tenant
Representa uma empresa cliente do SaaS.
- Identificação, status e plano.
- Proprietário lógico dos dados operacionais.

### User
Identidade de acesso.
- Pertence a um Tenant.
- Status de acesso.
- Relacionamento com roles/permissões.

### Role
Perfil lógico de autorização, como administrador, gestor ou atendente.

### Permission
Permissão granular para uma operação/recurso.

### RolePermission
Relaciona roles e permissões.

### Customer
Cliente efetivo da empresa.
- Dados cadastrais.
- Relacionamentos com contatos, endereços, interações e módulos comerciais.

### Lead
Potencial cliente.
- Origem, status, responsável e histórico.
- Nunca é apagado simplesmente por conversão.

### CustomerContact
Meios de contato do Customer.

### CustomerAddress
Endereços associados ao Customer.

### CustomerNote
Observação interna, com autoria e timestamp.

### CustomerTag
Classificação para busca e segmentação.

### Interaction
Interação relevante com Lead/Customer.

### Quote
Orçamento comercial.
- Customer, validade, status, totais e responsável.

### QuoteItem
Itens do orçamento, quantidade, preço unitário, desconto aplicável e subtotal.

### QuoteApproval
Registro da decisão de aprovação/rejeição.

### Appointment
Agendamento, proprietário do domínio Scheduling.

### Professional
Profissional responsável pela execução de serviços.

### Service
Serviço comercializável, duração e preço base.

### Payment
Transação de pagamento, proprietária do Finance.

### CashTransaction
Entrada/saída de caixa.

### Conversation
Conversa omnichannel.

### ConversationMessage
Mensagem individual de uma Conversation.

### AuditLog
Registro imutável de eventos relevantes.

## Integridade
- Foreign keys onde aplicável.
- Índices em tenant_id, chaves de relacionamento, status e campos de busca.
- Valores monetários e estados devem usar tipos apropriados.
- Soft delete somente quando houver justificativa; registros financeiros e de auditoria não devem ser apagados por conveniência.

## Migrations e Seeds
Migrations são versionadas e reversíveis quando tecnicamente seguro. Seeds são idempotentes e limitadas a dados iniciais necessários.
