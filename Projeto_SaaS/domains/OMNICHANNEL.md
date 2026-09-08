# OMNICHANNEL.md — Omnichannel v1.0

## Objetos
Conversation, ConversationMessage, ChannelConnection e ChannelAdapter.

## Arquitetura
`Canal externo → Adapter → Webhook/Receiver → Normalização → Conversation → CRM`

## Canais
- WhatsApp
- Telegram
- Instagram
- E-mail

## Webhooks
Receivers devem:
1. validar autenticidade/assinatura;
2. prevenir replay conforme o provedor;
3. identificar o ChannelConnection/Tenant;
4. normalizar a mensagem;
5. localizar ou criar vínculo com Lead/Customer;
6. persistir Conversation/Message;
7. registrar evento.

## Segurança
Credenciais e tokens são armazenados de forma segura e nunca entram em logs.

## CRM
Omnichannel registra a comunicação; CRM apresenta a relação com Lead/Customer. Nenhum canal deve criar regras comerciais paralelas.
