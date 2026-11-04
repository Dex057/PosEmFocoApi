# 🎓 Primeiro Uso

Tutorial prático passo a passo para novos usuários do PósEmFoco.

## 🎯 Objetivo

Neste tutorial você vai:
1. ✅ Acessar a aplicação
2. ✅ Criar uma conta
3. ✅ Definir interesses
4. ✅ Fazer login
5. ✅ Receber notificações

**Tempo estimado:** 5 minutos

---

## 📋 Pré-requisitos

- ✅ Servidor rodando (`uvicorn server:app --reload`)
- ✅ Acesso à http://localhost:8000
- ✅ Email Gmail funcional

Se não tiver, veja [Instalação](instalacao.md).

---

## 🚀 Passo 1: Acessar a Aplicação

1. Abra seu navegador (Chrome, Firefox, Safari, Edge)
2. Digite: **http://localhost:8000**
3. Você verá uma mensagem JSON:
   ```json
   {"mensagem": "API PósEmFoco rodando com PostgreSQL"}
   ```

Perfeito! Sistema está rodando.

---

## 📝 Passo 2: Ir para Página de Cadastro

1. Digite na barra de endereço:
   ```
   http://localhost:8000/frontend/cadastro.html
   ```

2. Você verá um formulário como este:
   
   ```
   ┌──────────────────────────────┐
   │   PósEmFoco - Cadastro       │
   ├──────────────────────────────┤
   │ Nome Completo:               │
   │ [_____________________]      │
   │                              │
   │ Email:                       │
   │ [_____________________]      │
   │                              │
   │ Senha:                       │
   │ [_____________________]      │
   │                              │
   │ Nível:  [Mestrado ▼]        │
   │                              │
   │ Interesses:                  │
   │ [_____________________]      │
   │ (ex: Python, IA, ...)        │
   │                              │
   │       [Cadastrar]            │
   └──────────────────────────────┘
   ```

---

## ✏️ Passo 3: Preencher Formulário

### Nome Completo
- Digite seu nome completo
- Exemplo: `João Silva Alves`

### Email
- **Importante:** Use um email **real e funcional**
- Você receberá notificações aqui
- Exemplo: `joao@gmail.com`

### Senha
- Crie uma senha **forte**
- Mínimo 6 caracteres
- Recomendação: `Aluno@2026Ufpa`

### Nível de Educação
- Selecione o dropdown
- Opções:
  - Mestrado
  - Doutorado
  - Pós-doutorado
  - Especialização
- Exemplo: `Mestrado`

### Interesses
- Digite palavras-chave separadas por **vírgula**
- Exemplos:
  ```
  Computação, Inteligência Artificial
  Python, Machine Learning, IA
  Engenharia, Sistemas Computacionais
  ```

**Dica:** Quanto mais específicas as palavras, melhor os resultados!

---

## 📤 Passo 4: Enviar Cadastro

1. Clique em **[Cadastrar]**
2. Aguarde 2-3 segundos
3. Você verá uma mensagem:
   ```
   ✅ Cadastro com sucesso! ID: 1
   ```

**Parabéns!** Você foi registrado no sistema.

---

## 🔐 Passo 5: Fazer Login

1. Agora acesse:
   ```
   http://localhost:8000/frontend/login.html
   ```

2. Você verá:
   ```
   ┌──────────────────────────────┐
   │   PósEmFoco - Login          │
   ├──────────────────────────────┤
   │ Email:                       │
   │ [_____________________]      │
   │                              │
   │ Senha:                       │
   │ [_____________________]      │
   │                              │
   │       [Entrar]               │
   └──────────────────────────────┘
   ```

3. Preencha:
   - **Email:** `joao@gmail.com` (mesmo do cadastro)
   - **Senha:** `Aluno@2026Ufpa` (mesma do cadastro)

4. Clique em **[Entrar]**

5. Você verá:
   ```
   ✅ Login bem-sucedido!
   ```

---

## 🕷️ Passo 6: Aguardar Scraper

⏳ **O que está acontecendo:**

- O `worker` roda o scraper em loop (padrão: a cada 60 min); para antecipar, use o botão do painel (`POST /scraper/rodar`)
- Ele consulta os portais das universidades configuradas
- Extraindo editais
- Verificando se correspondem seus interesses
- Levará **2-3 minutos** para completar

**Não feche a página! Pode abrir outra abinha.**

---

## 📧 Passo 7: Verificar Email

1. Aguarde 3-5 minutos
2. Abra seu **inbox do Gmail**
3. Procure por emails de `seu-email@gmail.com` (ou do servidor)
4. Você pode ver:
   - 📧 Notificações de editais
   - ✅ Email de teste (se configurado)

**Se não receber:**
- Verifique **pasta de Spam**
- Verifique se Gmail recebeu email
- Veja [Troubleshooting](../troubleshooting.md#email)

---

## 🎉 Sucesso!

Você completou o tutorial! 🎓

**Você conseguiu:**
- ✅ Cadastro na plataforma
- ✅ Login com credenciais
- ✅ Ativar monitoramento de editais
- ✅ Receber notificações por email

---

## 📚 Próximos Passos

1. **Explorar a API:** [API Endpoints](../api/endpoints.md)
2. **Entender arquitetura:** [Visão Geral](../arquitetura/visao-geral.md)
3. **Começar a desenvolver:** [Guia de Desenvolvimento](desenvolvimento.md)
4. **Fazer deploy:** [Guia de Deployment](../deployment.md)

---

## ❓ Dúvidas?

Consulte:
- [FAQ](../faq.md) - Perguntas frequentes
- [Troubleshooting](../troubleshooting.md) - Problemas comuns
- [Documentação Completa](../README.md) - Índice geral

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
"
