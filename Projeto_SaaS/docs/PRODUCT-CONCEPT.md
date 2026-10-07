# PRODUCT-CONCEPT.md — Conceito Completo do Produto

## 1. Objetivo
Definir o que o produto é, para quem existe, quais problemas resolve, como funciona e quais princípios orientam sua evolução. Este documento é a referência de produto; detalhes de implementação pertencem à documentação de arquitetura e domínios.

## 2. Definição
O produto é um SaaS de gestão empresarial orientado a negócios de serviços. Ele centraliza relacionamento com clientes, captação e qualificação de leads, serviços, profissionais, orçamentos, aprovação, agenda, pagamentos, comunicação omnichannel, automações e assistência por IA.

## 3. Visão
Tornar a operação de empresas de serviços mais organizada, mensurável e automatizada, conectando comercial, atendimento, agenda e financeiro em um único fluxo.

## 4. Missão
Reduzir tarefas manuais, perda de oportunidades, falhas de comunicação e fragmentação operacional sem retirar do negócio o controle humano sobre decisões importantes.

## 5. Problema de negócio
Empresas de serviços frequentemente utilizam ferramentas desconectadas para contatos, mensagens, agenda, orçamento e pagamentos. Isso cria retrabalho, informação duplicada, falta de histórico e dificuldade para acompanhar o cliente desde o primeiro contato até a fidelização.

## 6. Público-alvo inicial
- Salões de beleza.
- Clínicas e negócios de estética.
- Empresas de serviços profissionais.
- Empresas de construção e prestação de serviços.
- Outros negócios cujo processo central seja captar cliente, vender serviço, agendar/executar e receber.

## 7. Personas
### Administrador do cliente
Gerencia empresa, usuários, permissões, configurações e visão geral.

### Gestor
Acompanha vendas, agenda, equipe, clientes e indicadores.

### Atendente/comercial
Atende leads, cadastra clientes, cria orçamentos e agenda serviços.

### Profissional
Visualiza agenda e executa serviços conforme sua permissão.

### Financeiro
Registra e acompanha pagamentos, entradas, saídas e situação financeira.

### Administrador SaaS
Opera a plataforma, tenants, planos, assinaturas, suporte e configurações globais sem acessar indevidamente dados do cliente.

## 8. Modelo SaaS
- Acesso por navegador.
- Sem instalação local obrigatória para o cliente.
- Login por usuário e senha, com possibilidade de evolução para MFA e outros mecanismos.
- Cobrança recorrente mensal.
- Planos e recursos controlados por entitlements.
- Plataforma, suporte, segurança, backup e controles de privacidade fazem parte da proposta de valor.

## 9. Multi-tenancy
Cada empresa cliente representa um tenant lógico. Os dados operacionais devem permanecer isolados. O tenant é determinado e validado pelo contexto autenticado, e não por uma informação livremente fornecida pelo navegador.

## 10. Proposta de valor
Uma única operação conectada: captar → qualificar → vender → aprovar → agendar → receber → executar → acompanhar → fidelizar.

## 11. Módulos funcionais
### CRM
Cadastro de leads e clientes, contatos, tags, histórico e timeline.

### Serviços e profissionais
Catálogo de serviços, duração, preço base, profissionais e disponibilidade.

### Orçamentos
Criação, itens, descontos, validade, estados, aprovação e histórico.

### Agenda
Agendamentos, profissionais, horários, conflitos e integração com calendário externo.

### Financeiro
Pagamentos e movimentações de caixa com meios de pagamento abstraídos por uma camada de integração.

### Omnichannel
WhatsApp, Instagram, Telegram e futuramente outros canais por meio de adapters.

### Automação
Regras acionadas por eventos ou condições, com limites, permissões e rastreabilidade.

### IA
Classificação, resumo, extração de dados, sugestões e automações controladas.

### SaaS Admin
Operação global da plataforma, tenants, planos, assinaturas, entitlements e suporte.

### Configurações
Horários de funcionamento, branding (logo, cores, nome da marca), integrações externas (Google Calendar), webhooks configuráveis e API keys.

## 12. Orçamento e pagamento
A aprovação de um orçamento registra intenção comercial aceita. O pagamento é uma responsabilidade financeira independente. Um orçamento aprovado pode gerar um agendamento sem significar que o serviço foi pago.

## 13. Agenda e Google Calendar
O produto pode sincronizar compromissos com calendários externos. A integração deve ser tratada como capacidade externa, com credenciais protegidas, tratamento de erros, reconciliação e idempotência.

## 14. Omnichannel
O cliente pode iniciar uma conversa por diferentes canais. A plataforma deve normalizar mensagens para um modelo interno comum, identificar ou sugerir vínculo com lead/cliente, manter histórico e encaminhar para humano, automação ou IA conforme regras configuradas.

## 15. Bot e atendimento
O bot deve coletar informações básicas como identidade, interesse, serviço pretendido e necessidade de agendamento/visita. Quando necessário, encaminha para atendimento humano. O objetivo é acelerar o atendimento, não substituir indiscriminadamente a equipe.

## 16. IA
A IA pode:
- resumir conversas;
- classificar intenção;
- extrair dados estruturados;
- sugerir respostas;
- priorizar leads;
- sugerir próximos passos;
- apoiar automações autorizadas.

A IA não deve assumir autoridade implícita sobre ações críticas, financeiras, exclusões ou mudanças de estado irreversíveis.

## 17. Timeline do cliente
A timeline é a visão consolidada das interações e eventos relevantes: mensagens, alterações comerciais, orçamentos, aprovações, agendamentos, pagamentos e observações permitidas.

## 18. Assinaturas e entitlements
Planos determinam capacidades, limites e condições comerciais. A autorização de uma funcionalidade depende tanto da permissão do usuário quanto da disponibilidade daquele recurso para o tenant.

## 19. Segurança e privacidade
Segurança, privacidade e LGPD devem ser consideradas desde o desenho. O produto deve aplicar minimização de dados, controle de acesso, rastreabilidade, proteção de credenciais, retenção coerente e processos para incidentes e solicitações de titulares conforme aplicável.

## 20. UX
A interface deve reduzir cliques e duplicidade de cadastro. A informação deve acompanhar o fluxo de trabalho real. Estados, erros, permissões e confirmações devem ser claros.

## 21. Métricas de sucesso
Exemplos de indicadores:
- leads captados;
- taxa de qualificação;
- conversão lead → cliente;
- orçamentos emitidos/aprovados;
- tempo até primeiro atendimento;
- taxa de comparecimento;
- receita por serviço;
- recorrência/fidelização;
- utilização por usuário;
- retenção de tenants;
- disponibilidade da plataforma.

## 22. O que o produto não é
- Não é apenas um CRM.
- Não é apenas uma agenda.
- Não é apenas um sistema financeiro.
- Não é um chatbot independente do negócio.
- Não é um agente de IA com autonomia irrestrita.
- Não deve ficar preso a um único provedor externo quando uma abstração razoável for possível.

## 23. Evolução
O MVP deve priorizar o fluxo comercial e operacional principal. Recursos avançados de IA, automações complexas e novos canais devem evoluir sem quebrar o núcleo de CRM, orçamento, agenda e financeiro.

## 24. Regra de ouro
Toda nova funcionalidade deve responder: qual problema de negócio resolve, em qual domínio pertence, quais dados altera, quem pode executá-la, quais eventos gera, como falha e como será auditada.
