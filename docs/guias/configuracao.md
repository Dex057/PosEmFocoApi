# ⚙️ Configuração Completa

Guia detalhado para configurar todas as variáveis e dependências do PósEmFoco.

## 📋 Índice
1. [Arquivo .env](#arquivo-env)
2. [Banco de Dados](#banco-de-dados)
3. [Gmail/SMTP](#gmailsmtp)
4. [Variáveis Avançadas](#variáveis-avançadas)
5. [Verificação](#verificação)

---

## 📄 Arquivo .env

O arquivo `.env` armazena todas as variáveis sensíveis. **Nunca commit no Git!**

### Localização
```
PosEmFoco/
├── .env                    # Criar aqui
├── .gitignore              # Deve conter: .env
└── ...
```

### Criar Arquivo .env

**Linux/Mac:**
```bash
touch .env
nano .env
```

**Windows:**
- Crie um arquivo `novo arquivo de texto.txt`
- Renomeie para `.env` (com ponto no início)
- Edite com Notepad ou VSCode

### Template Completo

```env
# ============================================
# BANCO DE DADOS - PostgreSQL
# ============================================
DB_HOST=localhost           # Endereço do servidor
DB_PORT=5432                # Porta padrão PostgreSQL
DB_USER=posemfoco_user      # Usuário criado
DB_PASSWORD=sua_senha       # Senha (change me!)
DB_NAME=posemfoco           # Nome do banco

# ============================================
# EMAIL - SMTP (Gmail)
# ============================================
EMAIL_ADDRESS=seu_email@gmail.com           # Seu email
EMAIL_PASSWORD=xyzabc123def456ghi           # Senha de app (NÃO a senha da conta!)

# ============================================
# SCRAPER - Selenium
# ============================================
CHROME_OPTIONS=--headless --disable-gpu     # Opções do Chrome headless
SCRAPER_TIMEOUT=30                          # Timeout em segundos
SCRAPER_RETRY_COUNT=3                       # Tentativas de retry

# ============================================
# APLICAÇÃO
# ============================================
ENVIRONMENT=development                     # development, staging, production
DEBUG=true                                  # Ativar modo debug
LOG_LEVEL=INFO                              # DEBUG, INFO, WARNING, ERROR

# ============================================
# SEGURANÇA
# ============================================
SECRET_KEY=sua_chave_secreta_aqui           # Para JWT futura
ALLOWED_HOSTS=localhost,127.0.0.1           # CORS allowed origins

# ============================================
# OPCIONAL - Configuração Avançada
# ============================================
MAX_WORKERS=4                               # Workers para tarefas paralelas
CACHE_TTL=3600                              # Cache em segundos
MAIL_FROM_NAME=PósEmFoco                    # Nome que aparece no email
```

### Explicação Detalhada

#### PostgreSQL
```env
DB_HOST=localhost
# - localhost: banco na mesma máquina
# - 192.168.1.100: banco em outra máquina
# - db.exemplo.com: banco em servidor remoto

DB_PORT=5432
# Porta padrão do PostgreSQL. Mude se configurou diferente.

DB_USER=posemfoco_user
# Deve corresponder ao usuário criado no PostgreSQL

DB_PASSWORD=sua_senha
# ⚠️ ALTERE PARA UMA SENHA FORTE!
# Exemplo: Aluno@2026Ufpa#Pos123

DB_NAME=posemfoco
# Nome do banco criado
```

#### Email (Gmail)
```env
EMAIL_ADDRESS=seu_email@gmail.com
# Seu endereço Gmail. Deve estar ativo.

EMAIL_PASSWORD=xyzabc123def456ghi
# ⚠️ NÃO é a senha da sua conta Gmail!
# É a "Senha de App" (veja próxima seção)
```

#### Scraper
```env
CHROME_OPTIONS=--headless --disable-gpu
# --headless: executa sem abrir janela do navegador
# --disable-gpu: desativa aceleração de GPU
# --no-sandbox: necessário em alguns ambientes Linux
# Para modo debug (ver navegador): retire --headless

SCRAPER_TIMEOUT=30
# Tempo máximo em segundos para cada página carregar
# Aumente se site for lento

SCRAPER_RETRY_COUNT=3
# Número de tentativas se falhar
```

---

## 🔐 PostgreSQL - Configuração Detalhada

### Criar Usuário

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Na prompt do psql:
```

```sql
-- Criar usuário com senha
CREATE USER posemfoco_user WITH PASSWORD 'sua_senha_forte';

-- Dar permissões de conexão
ALTER USER posemfoco_user CREATEDB;

-- Sair
\q
```

### Criar Database

```bash
# Como usuário postgres
sudo -u postgres psql

# Na prompt:
```

```sql
-- Criar banco
CREATE DATABASE posemfoco OWNER posemfoco_user;

-- Configurar encoding (importante!)
ALTER DATABASE posemfoco SET client_encoding = 'utf8';

-- Conectar ao banco
\c posemfoco

-- Dar todas as permissões
GRANT ALL PRIVILEGES ON DATABASE posemfoco TO posemfoco_user;

-- Ver se criou
\l

-- Sair
\q
```

### Testar Conexão

```bash
# Conectar como posemfoco_user
psql -h localhost -U posemfoco_user -d posemfoco

# Deve solicitar a senha. Se conectar, tudo OK!
# Saia com: \q
```

### Resetar Banco (Cuidado!)

Se precisar limpar tudo (só em desenvolvimento):

```bash
# Deletar banco
sudo -u postgres psql -c "DROP DATABASE IF EXISTS posemfoco;"

# Recriar banco
sudo -u postgres psql -c "CREATE DATABASE posemfoco OWNER posemfoco_user;"

# Recriar tabelas
python criar_tabelas.py
```

---

## 📧 Gmail/SMTP - Configuração Detalhada

### Passo 1: Habilitar 2FA no Gmail

1. Acesse: https://myaccount.google.com
2. Vá em **Segurança** (painel esquerdo)
3. Role até **Verificação em duas etapas**
4. Clique em **Ativar** e siga os passos

### Passo 2: Criar Senha de App

1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione:
   - **App:** Mail
   - **Dispositivo:** Windows Computer (ou seu SO)
3. Clique em **Gerar**
4. Google vai gerar uma senha (ex: `xyzabc123def456ghi`)
5. Copie essa senha para o `.env`:

```env
EMAIL_ADDRESS=seu_email@gmail.com
EMAIL_PASSWORD=xyzabc123def456ghi
```

### Testar Envio de Email

```bash
# Com ambiente virtual ativo
python -c "
from app.services.email_service import enviar_notificacao
enviar_notificacao(
    'seu_email@gmail.com',
    'Teste PósEmFoco',
    'https://www.ufpa.edu.br',
    'Python'
)
print('Email enviado com sucesso!')
"
```

Se receber o email, está funcionando!

### Solucionar Problemas de Email

```python
# Se receber erro, teste a conexão:
import smtplib

email = "seu_email@gmail.com"
senha = "sua_senha_de_app"

try:
    servidor = smtplib.SMTP('smtp.gmail.com', 587)
    servidor.starttls()
    servidor.login(email, senha)
    print("Conectado com sucesso!")
    servidor.quit()
except Exception as e:
    print(f"Erro: {e}")
```

---

## 🔧 Variáveis Avançadas

### DEBUG Mode

Em desenvolvimento, ative debug para ver mais logs:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

No código FastAPI:
```python
if os.getenv("DEBUG") == "true":
    print("Modo debug ativado")
```

### CORS (Cross-Origin)

Para permitir requisições de outros domínios:

```env
ALLOWED_HOSTS=localhost,127.0.0.1,app.exemplo.com
```

Em `server.py`:
```python
origins = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
```

### Database Pool

Para conexões simultâneas:

```env
DB_POOL_SIZE=5              # Conexões simultâneas
DB_MAX_OVERFLOW=10          # Conexões adicionais
```

---

## ✅ Verificação de Configuração

### Checklist

```bash
# 1. Arquivo .env existe?
ls -la .env

# 2. Python e pip?
python --version
pip --version

# 3. Dependências?
pip list | grep fastapi

# 4. PostgreSQL?
psql -U posemfoco_user -d posemfoco -c "SELECT 1;"

# 5. Email funciona?
python -c "from app.services.email_service import enviar_notificacao; print('OK')"

# 6. Banco tem tabelas?
psql -U posemfoco_user -d posemfoco -c "\dt"

# 7. Servidor inicia?
uvicorn server:app --reload
# Deve exibir: INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Script de Verificação Automática

Crie `verificar_config.py`:

```python
#!/usr/bin/env python
import os
import sys

def verificar():
    print("🔍 Verificando configuração...\n")
    
    checks = {
        "Python 3.10+": sys.version_info >= (3, 10),
        ".env existe": os.path.exists(".env"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_USER": os.getenv("DB_USER"),
        "EMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS"),
    }
    
    for check, resultado in checks.items():
        status = "✅" if resultado else "❌"
        print(f"{status} {check}: {resultado}")
    
    if all(checks.values()):
        print("\n✅ Todas as verificações passaram!")
        return 0
    else:
        print("\n❌ Algumas verificações falharam. Verifique .env")
        return 1

if __name__ == "__main__":
    sys.exit(verificar())
```

Execute:
```bash
python verificar_config.py
```

---

## 🚀 Ambientes Diferentes

### Desenvolvimento
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DB_HOST=localhost
CHROME_OPTIONS=--headless --disable-gpu --no-sandbox
```

### Staging (teste em servidor)
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
DB_HOST=db.staging.exemplo.com
CHROME_OPTIONS=--headless --disable-gpu --no-sandbox
```

### Produção
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
DB_HOST=db.prod.exemplo.com
CHROME_OPTIONS=--headless --disable-gpu --no-sandbox --disable-dev-shm-usage
```

---

## 📞 Suporte

Veja: [Troubleshooting](../troubleshooting.md) | [FAQ](../faq.md)

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
