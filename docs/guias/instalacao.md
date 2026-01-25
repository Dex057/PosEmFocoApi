# 📋 Instalação Detalhada

Este guia fornece instruções passo a passo para instalar o PósEmFoco em diferentes sistemas operacionais.

## 🎯 Pré-requisitos Globais

Antes de começar, certifique-se de ter:

- **Git** - Para clonar o repositório
- **Python 3.10+** - Linguagem principal
- **PostgreSQL 12+** - Banco de dados
- **Google Chrome** - Para web scraping
- **pip** - Gerenciador de pacotes Python
- **Terminal/CMD** - Acesso à linha de comando

---

## 💻 Instalação por Sistema Operacional

### 🐧 Linux (Ubuntu/Debian)

#### 1. Atualize o sistema
```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. Instale Python 3.10+
```bash
# Instalar Python e ferramentas relacionadas
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verificar versão (deve ser 3.10+)
python3 --version
```

#### 3. Instale PostgreSQL
```bash
# Instalar PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Verificar instalação
psql --version

# Iniciar serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Inicia automaticamente

# Verificar status
sudo systemctl status postgresql
```

#### 4. Configure PostgreSQL

```bash
# Acesse o PostgreSQL
sudo -u postgres psql

# Na prompt psql, execute:
```

```sql
-- Criar banco de dados
CREATE DATABASE posemfoco;

-- Criar usuário
CREATE USER posemfoco_user WITH PASSWORD 'sua_senha_segura';

-- Dar permissões
ALTER ROLE posemfoco_user SET client_encoding TO 'utf8';
ALTER ROLE posemfoco_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE posemfoco_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE posemfoco TO posemfoco_user;

-- Sair
\q
```

#### 5. Instale Google Chrome
```bash
# Instalar Chrome
sudo apt install -y google-chrome-stable

# Verificar instalação
google-chrome --version
```

#### 6. Clone o Repositório
```bash
# Criar diretório para projetos (opcional)
mkdir -p ~/projetos
cd ~/projetos

# Clonar repositório
git clone https://github.com/seu-usuario/PosEmFoco.git
cd PosEmFoco
```

#### 7. Configure Ambiente Virtual Python
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Você verá (venv) no início da linha de comando
```

#### 8. Instale Dependências
```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt

# Verificar instalação
pip list
```

#### 9. Configure Variáveis de Ambiente
```bash
# Criar arquivo .env na raiz do projeto
nano .env
```

Adicione (com seus valores):
```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=posemfoco_user
DB_PASSWORD=sua_senha_segura
DB_NAME=posemfoco

# Gmail SMTP
EMAIL_ADDRESS=seu_email@gmail.com
EMAIL_PASSWORD=senha_de_aplicativo_gmail

# Ambiente
ENVIRONMENT=development
```

Salve com `Ctrl+O`, Enter, `Ctrl+X`

#### 10. Inicialize Banco de Dados
```bash
# Criar tabelas
python criar_tabelas.py

# Verificar se foram criadas
psql -U posemfoco_user -d posemfoco -c "\dt"
```

#### 11. Inicie o Servidor
```bash
# Ativar ambiente virtual (se não estiver ativo)
source venv/bin/activate

# Iniciar servidor
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Acesse: `http://localhost:8000`

---

### 🍎 macOS

#### 1. Instale Homebrew (se não tiver)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Instale Python 3.10+
```bash
# Instalar Python
brew install python@3.10

# Criar link (se necessário)
brew link python@3.10

# Verificar versão
python3 --version
```

#### 3. Instale PostgreSQL
```bash
# Instalar PostgreSQL
brew install postgresql

# Iniciar serviço
brew services start postgresql

# Verificar status
brew services list
```

#### 4. Configure PostgreSQL

```bash
# Acesse PostgreSQL
psql postgres

# Execute os comandos SQL (mesmo do Linux, veja acima)
```

#### 5. Instale Google Chrome
```bash
# Instalar Chrome
brew install google-chrome

# Verificar
google-chrome --version
```

#### 6. Clone e Configure (mesmo do Linux, passos 6-11)

```bash
# Clone
git clone https://github.com/seu-usuario/PosEmFoco.git
cd PosEmFoco

# Ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Dependências
pip install -r requirements.txt

# .env (ver Linux, passo 9)

# Banco
python criar_tabelas.py

# Servidor
uvicorn server:app --reload
```

---

### 🪟 Windows (com WSL2 Recomendado)

#### Opção A: WSL2 (Recomendado)

O WSL2 (Windows Subsystem for Linux) é a melhor opção. Basicamente, é Linux rodando no Windows.

```powershell
# No PowerShell como Administrador:
wsl --install

# Reinicie o computador
# Após reiniciar, o Ubuntu será instalado automaticamente

# Verifique a versão
wsl --list --verbose
```

Depois, siga as instruções do **Linux (Ubuntu/Debian)** acima. Você estará usando Linux!

#### Opção B: Windows Nativo (Mais Complicado)

Se preferir não usar WSL2:

##### 1. Instale Python 3.10+
- Baixe: https://www.python.org/downloads/
- Marque "Add Python to PATH" durante instalação
- Verifique:
  ```cmd
  python --version
  pip --version
  ```

##### 2. Instale PostgreSQL
- Baixe: https://www.postgresql.org/download/windows/
- Execute instalador (use padrões)
- Anote a senha do usuário `postgres`
- Verifique (abra pgAdmin ou Command Line)

##### 3. Configure PostgreSQL

Abra `pgAdmin` (ícone na área de trabalho) e crie:
- Database: `posemfoco`
- User: `posemfoco_user` (com senha)

##### 4. Instale Google Chrome
- Baixe: https://www.google.com/chrome/
- Execute instalador
- Verifique no "Programas e Recursos"

##### 5. Clone Repositório

```cmd
# Abra Command Prompt
git clone https://github.com/seu-usuario/PosEmFoco.git
cd PosEmFoco
```

##### 6. Ambiente Virtual
```cmd
python -m venv venv
venv\Scripts\activate

# Você verá (venv) no prompt
```

##### 7. Dependências
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

##### 8. Configure .env

Crie arquivo `.env` na raiz do projeto (use Notepad):
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=posemfoco_user
DB_PASSWORD=sua_senha
DB_NAME=posemfoco

EMAIL_ADDRESS=seu_email@gmail.com
EMAIL_PASSWORD=senha_de_app

ENVIRONMENT=development
```

##### 9. Inicialize BD
```cmd
python criar_tabelas.py
```

##### 10. Inicie Servidor
```cmd
uvicorn server:app --reload
```

---

## ✅ Verificação de Instalação

Após completar os passos, verifique se tudo funciona:

### 1. Teste Python
```bash
python --version              # Deve ser 3.10+
python -c "import fastapi"    # Deve não gerar erro
```

### 2. Teste PostgreSQL
```bash
# Linux/Mac
psql -U posemfoco_user -d posemfoco -c "SELECT 1;"

# Windows (use pgAdmin ou Command Line)
```

### 3. Teste Chrome
```bash
# Linux/Mac
google-chrome --version

# Windows
# Procure por "Google Chrome" no menu Iniciar
```

### 4. Teste Servidor
```bash
# Com ambiente virtual ativo
uvicorn server:app --reload

# Você verá:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

Acesse: http://localhost:8000 (deve exibir JSON com mensagem)

### 5. Teste Banco de Dados
```bash
# Deve listar as 3 tabelas criadas
psql -U posemfoco_user -d posemfoco -c "\dt"

# Output esperado:
#             List of relations
#  Schema |    Name    | Type  |     Owner
# --------+------------+-------+------------------
#  public | edital     | table | posemfoco_user
#  public | interesse  | table | posemfoco_user
#  public | usuario    | table | posemfoco_user
```

---

## 🚀 Próximos Passos

Após instalação bem-sucedida:

1. Leia: [Configuração](configuracao.md) - Setup detalhado
2. Leia: [Primeiro Uso](primeiro-uso.md) - Tutorial prático
3. Explore: Documentação em `docs/`

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError: No module named 'app'"
```bash
# Certifique-se de estar na pasta raiz do projeto
cd /caminho/para/PosEmFoco
source venv/bin/activate  # ou venv\Scripts\activate no Windows
python criar_tabelas.py
```

### "psycopg2.OperationalError: could not connect to server"
```bash
# Verifique se PostgreSQL está rodando
sudo systemctl status postgresql    # Linux
brew services list                  # Mac
# Windows: pgAdmin ou Services

# Verifique credenciais em .env
```

### "ConnectionRefusedError" na inicialização
```bash
# Porta 8000 em uso, use outra
uvicorn server:app --reload --port 8001
```

Veja [Troubleshooting Completo](../troubleshooting.md) para mais problemas.

---

## 📞 Precisa de Ajuda?

- [FAQ](../faq.md) - Perguntas frequentes
- [Troubleshooting](../troubleshooting.md) - 30+ soluções
- [Issues no GitHub](https://github.com/seu-usuario/PosEmFoco/issues)

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
