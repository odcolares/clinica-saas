# Manual do Cliente — Clinica-SaaS

## 1. Visão Geral do Sistema

O **Clinica-SaaS** é uma plataforma online para gestão completa de clínicas. Com ele você pode:

- **Gerenciar leads** (prospects que ainda não são clientes)
- ** Administrar clientes** (pacientes)
- **Organizar a agenda** (profissionais, serviços e agendamentos)
- **Atender clientes** via WhatsApp e Telegram
- **Visualizar relatórios** em tempo real
- **Configurar sua clínica** (horários, integrações, notificações)

> **URL de acesso:** https://clinica-saas-frontend.vercel.app/login  
> Use as credenciais fornecidas pelo administrador do sistema.

---

## 2. Primeiro Acesso

1. Acesse a URL acima
2. Digite seu e-mail e senha
3. Clique em **Entrar**

Na primeira visita, você será direcionado para a **Dashboard** principal.

---

## 3. Gestão de Leads

**Leads** são pessoas interessadas em seus serviços que ainda não agendaram.

### Criar um novo lead

1. No menu lateral, clique em **Leads**
2. Clique no botão **Novo Lead**
3. Preencha:
   - **Nome** (obrigatório)
   - **E-mail** (opcional)
   - **Telefone** (opcional)
   - **Documento** (opcional)
   - **Fonte** (como o lead chegou: Google, WhatsApp, etc.)
   - **Observações** (opcional)
4. Clique em **Salvar**

### Mudar status de um lead

1. Na lista de leads, clique no lead desejado
2. No campo **Status**, selecione:
   - `Novo` - Lead recém-chegado
   - `Contatado` - Já entrou em contato
   - `Qualificado` - Interessado e pronto para converter
   - `Convertido` - Virou cliente
   - `Perdido` - Não converteu (motivo obrigatório)
3. Clique em **Atualizar**

### Converter lead em cliente

1. Abra o lead com status `Qualificado`
2. Clique em **Converter para Cliente**
3. Confirme os dados
4. O lead será automaticamente vinculado ao cliente criado

---

## 4. Gestão de Clientes

**Clientes** são pessoas que já realizaram algum agendamento ou compra.

### Visualizar cliente

1. No menu, clique em **Clientes**
2. Clique no nome do cliente
3. Veja todas as informações:
   - Dados pessoais (nome, documento, etc.)
   - Contatos (e-mails, telefones, WhatsApp)
   - Endereços
   - Histórico de interações
   - Agendamentos passados e futuros

### Adicionar contato

1. Abra o cliente desejado
2. Na aba **Contatos**, clique em **Adicionar Contato**
3. Selecione o tipo (e-mail, telefone, WhatsApp)
4. Digite o valor
5. Clique em **Salvar**

### Adicionar endereço

1. Abra o cliente
2. Na aba **Endereços**, clique em **Adicionar Endereço**
3. Preencha: rua, número, complemento, bairro, cidade, estado, CEP
4. Clique em **Salvar**

---

## 5. Agenda e Profissionais

### Profissionais

Profissionais são os profissionais que trabalham na sua clínica (médicos, terapeutas, etc.).

#### Cadastrar profissional

1. No menu, clique em **Profissionais**
2. Clique em **Novo Profissional**
3. Preencha:
   - **Nome** (obrigatório)
   - **E-mail** (opcional)
   - **Telefone** (opcional)
   - **Especialidades** (múltiplas)
   - **Comissão** (percentual ou valor fixo)
4. Clique em **Salvar**

### Serviços

Serviços são os atendimentos oferecidos (consulta, exame, terapia, etc.).

#### Cadastrar serviço

1. No menu, clique em **Serviços**
2. Clique em **Novo Serviço**
3. Preencha:
   - **Nome** (obrigatório)
   - **Descrição** (opcional)
   - **Duração** (em minutos)
   - **Preço** (opcional)
4. Clique em **Salvar**

### Agendamentos

#### Criar agendamento

1. No menu, clique em **Agenda**
2. Clique na data e horário desejado
3. Selecione:
   - **Profissional**
   - **Serviço**
   - **Cliente** (ou crie um novo)
   - **Data e hora de início**
4. Clique em **Confirmar**

> O horário final é calculado automaticamente com base na duração do serviço.

#### Confirmar agendamento

1. Ao criar, o status já é `Agendado`
2. Para confirmar, clique no agendamento e selecione **Confirmar**
3. O cliente receberá uma notificação

#### Cancelar agendamento

1. Abra o agendamento
2. Clique em **Cancelar**
3. Confirme a ação

---

## 6. Atendimento Omnichannel

Atenda seus clientes pelo WhatsApp e Telegram em uma única interface.

### Visualizar conversas

1. No menu, clique em **Atendimento**
2. Veja a lista de conversas
3. Conversas não atendidas aparecem com destaque

### Enviar mensagem

1. Abra a conversa desejada
2. Digite sua mensagem na caixa inferior
3. Clique em **Enviar**

### Atribuir conversa

1. Na lista de conversas, clique nos três pontinhos
2. Selecione **Atribuir para mim**
3. A conversa agora aparece como atendida por você

---

## 7. Dashboard

O dashboard mostra um resumo do seu dia:

- **Agendamentos de hoje** (com status e horários)
- **Leads recentes**
- **Clientes com agendamentos próximos**
- **Atividade da semana**

### Navegar no calendário

- Use as setas **<** e **>** para mudar o mês
- Clique em um dia para ver os agendamentos daquele dia
- Clique em um agendamento para ver os detalhes

---

## 8. Configurações

### Dados da clínica (Tenant)

1. No menu, clique em **Configurações** → **Clínica**
2. Atualize:
   - **Nome da clínica**
   - **Horário de funcionamento** (início e fim)
   - **Fuso horário**
   - **Logo** (URL da imagem)
   - **Cor principal** (hexadecimal)
3. Clique em **Salvar**

### Notificações

1. Em **Configurações** → **Notificações**
2. Ative/desative:
   - `Confirmação de agendamento`
   - `Lembrete de agendamento` (configura o tempo, em minutos)
   - `Cancelamento de agendamento`
   - `Novo lead`
   - `Pagamento recebido` (quando implementado)
3. Escolha os canais:
   - **E-mail**
   - **SMS**
   - **Notificação push**
4. Clique em **Salvar**

### Integrações

1. Em **Configurações** → **Integrações**
2. Conecte ao Google Calendar clicando em **Conectar**
3. Autorize o acesso
4. Configure quais eventos sincronizar

### Webhooks

1. Em **Configurações** → **Webhooks**
2. Clique em **Adicionar Webhook**
3. Preencha:
   - **Nome** (identifique o webhook)
   - **URL** (onde receberá os eventos)
   - **Eventos** (quais eventos enviar)
   - **Segredo** (para validar a origem)
4. Clique em **Ativar**

### Chaves de API

1. Em **Configurações** → **Chaves de API**
2. Clique em **Gerar Nova Chave**
3. Dê um nome à chave
4. **Copie a chave agora** - ela não será mostrada novamente
5. Use a chave no header: `Authorization: Bearer sua_chave_aqui`

> ⚠️ Mantenha a chave em segurança. Nunca compartilhe com terceiros.

---

## Problemas Comuns

### Esqueci minha senha
1. Na tela de login, clique em **Esqueci minha senha**
2. Digite seu e-mail
3. Siga as instruções enviadas

### Não recebo notificações
- Verifique se as notificações estão ativadas em **Configurações** → **Notificações**
- Confirme se seu e-mail/celular está atualizado

### Agendamento mostra horário ocupado
- Verifique se não há outro agendamento no mesmo horário
- Horários adjacentes são permitidos (ex: 08:00-09:00 e 09:00-10:00)

### Estou com dificuldades no atendimento
- Certifique-se de que seu status esteja como **Disponível**
- Clique no ícone de status na barra lateral

---

## Suporte

Precisa de ajuda?
- **E-mail:** suporte@clinicasaas.com.br
- **WhatsApp:** (11) 99999-9999
- **Horário:** Segunda a Sexta, 8h às 18h

---

*Manual atualizado em: 07/10/2026*