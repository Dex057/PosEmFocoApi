# PósEmFoco - Monitorador de Editais UFPA 🎓

O **PósEmFoco** é um sistema automatizado desenvolvido em Python para monitorar, capturar e notificar usuários sobre novos editais de pós-graduação publicados no site da Universidade Federal do Pará (UFPA).

O sistema permite que o usuário cadastre palavras-chave (ex: "Enfermagem", "Computação") e receba notificações por e-mail instantaneamente assim que um novo edital correspondente for publicado.

## 📋 Sumário

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#️-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Como Usar](#-como-usar)
- [API Endpoints](#-api-endpoints)
- [Arquitetura](#-arquitetura)
- [Troubleshooting](#-troubleshooting)

## 🎯 Visão Geral

PósEmFoco é uma solução inteligente que automatiza o monitoramento de editais acadêmicos. Em vez de os usuários verificarem manualmente o site da UFPA diariamente, o sistema faz isso por eles usando web scraping com Selenium, verifica novos editais contra interesses registrados e envia notificações por e-mail em tempo real.

### Fluxo Principal

1. Usuário se cadastra e define palavras-chave de interesse
2. Sistema executa scraper periodicamente no site da UFPA
3. Novos editais são detectados e armazenados no banco de dados
4. Sistema verifica correspondência entre editais e interesses dos usuários
5. Notificações por e-mail são enviadas automaticamente

## 🚀 Funcionalidades

- **Cadastro e Autenticação:** Sistema de registro e login com senhas criptografadas usando bcrypt
- **Gerenciamento de Interesses:** Usuários podem adicionar múltiplas palavras-chave para monitoramento
- **Web Scraping Inteligente:** Utiliza Selenium para navegar, paginar e extrair dados do site da UFPA
- **Anti-Duplicidade:** Verifica no banco de dados se o edital já foi processado para evitar notificações duplicadas
- **Notificação por E-mail:** Envia e-mails formatados em HTML com informações completas do edital
- **Robustez:** Sistema configurado para rodar em ambiente Linux com modo headless e tratamento de erros de conexão
- **Dados Persistentes:** Todos os editais, usuários e interesses são armazenados em PostgreSQL

## 🛠️ Tecnologias

| Categoria | Tecnologia |
|-----------|-----------|
| **Linguagem** | Python 3.10+ |
| **Framework Web** | FastAPI |
| **Servidor** | Uvicorn |
| **Automação/Scraping** | Selenium & Webdriver Manager |
| **Banco de Dados** | PostgreSQL |
| **Autenticação** | bcrypt (passlib) |
| **Comunicação** | SMTP (Gmail) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Gerenciador de Dependências** | pip |

## 📁 Estrutura do Projeto

```
PosEmFoco/
├── app/
│   ├── dao/                    # Data Access Objects
│   │   ├── usuario_dao.py      # Operações com usuários
│   │   ├── interesse_dao.py    # Operações com interesses
│   │   └── edital_dao.py       # Operações com editais
│   ├── models/                 # Modelos de dados
│   │   ├── usuario.py          # Classe Usuario
│   │   └── edital.py           # Classe Edital
│   ├── services/               # Lógica de negócio
│   │   ├── scraper.py          # Web scraper dos editais
│   │   ├── email_service.py    # Envio de notificações
│   │   └── notificador.py      # Lógica de notificações
│   └── utils/
│       └── db.py               # Configuração do banco de dados
├── frontend/
│   ├── login.html              # Página de login
│   ├── cadastro.html           # Página de cadastro
│   └── style.css               # Estilos CSS
├── criar_tabelas.py            # Script para criar tabelas no BD
├── reset_banco.py              # Script para limpar BD
├── server.py                   # Servidor FastAPI principal
├── requirements.txt            # Dependências do projeto
├── .env                        # Variáveis de ambiente (não versionado)
└── README.md                   # Este arquivo
```

## ⚙️ Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.10 ou superior** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download](https://www.postgresql.org/download/)
- **Google Chrome** - Instalado no sistema operacional (necessário para Selenium)
- **pip** - Gerenciador de pacotes Python (geralmente vem com Python)
- **Git** - [Download](https://git-scm.com/downloads)

### Verificar Instalações

```bash
# Verificar Python
python3 --version

# Verificar PostgreSQL
psql --version

# Verificar pip
pip --version
```

## 📦 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/PosEmFoco.git
cd PosEmFoco
```

### 2. Crie um Ambiente Virtual (Recomendado)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

As dependências principais incluem:
- **fastapi** - Framework web
- **uvicorn** - Servidor ASGI
- **selenium** - Web scraping
- **psycopg2-binary** - Driver PostgreSQL
- **python-dotenv** - Variáveis de ambiente
- **passlib[bcrypt]** - Criptografia de senhas
- **webdriver-manager** - Gerenciamento do ChromeDriver

## 🔧 Configuração

### 1. Configure o Banco de Dados

```bash
# Acesse o PostgreSQL
psql -U postgres

# Crie um novo banco de dados
CREATE DATABASE posemfoco;

# Crie um usuário (opcional, mas recomendado)
CREATE USER posemfoco_user WITH PASSWORD 'sua_senha_segura';
ALTER ROLE posemfoco_user SET client_encoding TO 'utf8';
ALTER ROLE posemfoco_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE posemfoco_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE posemfoco TO posemfoco_user;

# Saia do PostgreSQL
\q
```

### 2. Crie o Arquivo .env

Na raiz do projeto, crie um arquivo `.env` com as seguintes variáveis:

```env
# Banco de Dados PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=posemfoco_user
DB_PASSWORD=sua_senha_segura
DB_NAME=posemfoco

# Configuração de E-mail (Gmail)
EMAIL_ADDRESS=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_aplicativo

# Configuração do Scraper
CHROME_OPTIONS=--headless --disable-gpu

# Ambiente
ENVIRONMENT=development
```

**⚠️ Importante:** 
- Para Gmail, use [Senhas de Aplicativo](https://myaccount.google.com/apppasswords) em vez da senha da conta
- Nunca comite o arquivo `.env` no Git (adicione à `.gitignore`)

### 3. Crie as Tabelas do Banco

```bash
python criar_tabelas.py
```

Este script criará automaticamente as tabelas necessárias:
- `usuario` - Armazena informações dos usuários
- `interesse` - Palavras-chave monitoradas por cada usuário
- `edital` - Editais encontrados pelo scraper

## 🚀 Como Usar

### 1. Inicie o Servidor FastAPI

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

O servidor iniciará em `http://localhost:8000`

### 2. Acesse a Interface Web

Abra seu navegador e acesse:
- **Página de Login:** `http://localhost:8000/frontend/login.html`
- **Página de Cadastro:** `http://localhost:8000/frontend/cadastro.html`
- **Documentação API:** `http://localhost:8000/docs`

### 3. Fluxo de Uso

1. **Cadastro:** Preencha o formulário com seus dados e interesses
2. **Login:** Faça login com suas credenciais
3. **Monitoramento Automático:** O sistema iniciará a busca por editais correspondentes
4. **Notificações:** Receba e-mails quando novos editais forem encontrados

## 📡 API Endpoints

### Autenticação e Usuários

#### `POST /cadastro`
Registra um novo usuário

**Request:**
```json
{
  "nome": "João Silva",
  "email": "joao@example.com",
  "senha": "senha_segura_123",
  "nivel_graduacao": "Mestrado",
  "interesses": ["Computação", "Engenharia"]
}
```

**Response:**
```json
{
  "mensagem": "Usuário cadastrado com sucesso!",
  "id": 1
}
```

#### `POST /login`
Realiza o login e inicia o monitoramento

**Request:**
```json
{
  "email": "joao@example.com",
  "senha": "senha_segura_123"
}
```

**Response:**
```json
{
  "mensagem": "Login realizado com sucesso",
  "usuario": {
    "id": 1,
    "nome": "João Silva",
    "email": "joao@example.com"
  }
}
```

### Editais

#### `GET /`
Verifica se a API está rodando

**Response:**
```json
{
  "mensagem": "API PósEmFoco rodando com PostgreSQL"
}
```

## 🏗️ Arquitetura

### Camadas da Aplicação

```
┌─────────────────────────────────────┐
│        Frontend (HTML/CSS/JS)       │
├─────────────────────────────────────┤
│        FastAPI Server               │
│  (server.py - Endpoints REST)       │
├─────────────────────────────────────┤
│        Services Layer               │
│  - Scraper (Selenium)               │
│  - Email Service (SMTP)             │
│  - Notificador                      │
├─────────────────────────────────────┤
│        DAO Layer (Data Access)      │
│  - UsuarioDAO                       │
│  - InteresseDAO                     │
│  - EditalDAO                        │
├─────────────────────────────────────┤
│        PostgreSQL Database          │
└─────────────────────────────────────┘
```

### Fluxo de Execução do Scraper

1. **Inicialização:** Usuário faz login
2. **Busca de Interesses:** Consulta banco de dados por palavras-chave e e-mails dos usuários
3. **Web Scraping:** Acessa site da UFPA com Selenium
4. **Extração de Dados:** Coleta título, link, data e resumo dos editais
5. **Verificação de Duplicatas:** Checa se edital já existe no banco
6. **Armazenamento:** Salva novo edital no BD
7. **Notificação:** Envia e-mail aos usuários interessados

## 🛠️ Comandos Úteis

### Gerenciar Banco de Dados

```bash
# Criar tabelas
python criar_tabelas.py

# Limpar banco de dados (CUIDADO!)
python reset_banco.py

# Backup do banco
pg_dump -U posemfoco_user posemfoco > backup.sql

# Restaurar backup
psql -U posemfoco_user posemfoco < backup.sql
```

### Ativar Modo Debug

Edite `server.py` para adicionar logs:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testar Envio de E-mail

```bash
python -c "from app.services.email_service import enviar_notificacao; enviar_notificacao('seu_email@gmail.com', 'Teste', 'https://example.com', 'Python')"
```

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'app'"

**Solução:** Certifique-se de estar na pasta raiz do projeto ao executar:
```bash
cd /caminho/para/PosEmFoco
python criar_tabelas.py
```

### Erro: "psycopg2.OperationalError: could not connect to server"

**Solução:** Verifique se PostgreSQL está rodando:
```bash
# Linux
sudo systemctl start postgresql

# Mac (via Homebrew)
brew services start postgresql
```

### Erro: "ConnectionRefusedError" ao enviar e-mail

**Solução:** Verifique credenciais do Gmail no `.env`:
- Use [Senhas de Aplicativo](https://myaccount.google.com/apppasswords)
- Ative "Acesso de apps menos seguros" (alternativa)

### Selenium não encontra Chrome

**Solução:** 
```bash
# Linux - Instale Chrome
sudo apt-get install google-chrome-stable

# Ou use ChromeDriver manualmente
# O webdriver-manager deveria fazer isso automaticamente
```

### Erro: "CORS policy: No 'Access-Control-Allow-Origin'"

**Solução:** CORS já está configurado em `server.py`, mas se persistir:
```python
# Em server.py, verifique se o middleware está ativo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Modelagem de Dados

### Tabela: usuario
```sql
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    nivel_graduacao VARCHAR(50),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: interesse
```sql
CREATE TABLE interesse (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    palavra_chave VARCHAR(100) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);
```

### Tabela: edital
```sql
CREATE TABLE edital (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    link TEXT NOT NULL,
    resumo TEXT,
    data_publicacao TIMESTAMP,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(titulo, link)
);
```

## 🔐 Segurança

- ✅ Senhas armazenadas com bcrypt (hashing)
- ✅ SQL Injection prevenida com prepared statements
- ✅ CORS configurado para requisições cross-origin
- ✅ Variáveis sensíveis armazenadas em `.env`
- ✅ Validação de entrada com Pydantic

### Recomendações Adicionais

1. Use HTTPS em produção
2. Configure rate limiting para APIs
3. Implemente autenticação com JWT (tokens)
4. Adicione logs de auditoria
5. Configure firewall adequadamente

## 📈 Próximas Melhorias

- [ ] Autenticação com JWT tokens
- [ ] Dashboard de visualização de editais
- [ ] Histórico de notificações
- [ ] Filtros avançados de busca
- [ ] Suporte a múltiplas universidades
- [ ] Aplicativo mobile (React Native)
- [ ] Integração com WhatsApp
- [ ] Sistema de recomendações com ML

## 📞 Suporte e Contribuição

### Reportar Bugs

1. Abra uma [Issue](https://github.com/seu-usuario/PosEmFoco/issues)
2. Descreva o problema em detalhes
3. Inclua logs e screenshots se possível

### Contribuir

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ para facilitar a vida dos alunos de pós-graduação da UFPA.

---

**Última atualização:** Janeiro de 2026

**Versão:** 1.0.0

Para mais informações, visite: [GitHub Repository](https://github.com/seu-usuario/PosEmFoco)
