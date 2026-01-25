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
- [Contribuição](#-contribuição)

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
│   ├── __init__.py
│   ├── dao/                    # Data Access Objects - Acesso aos dados
│   │   ├── usuario_dao.py      # CRUD de usuários
│   │   ├── interesse_dao.py    # Gerenciamento de palavras-chave
│   │   ├── edital_dao.py       # Gerenciamento de editais
│   │   └── __init__.py
│   ├── models/                 # Modelos de dados
│   │   ├── usuario.py          # Classe Usuario
│   │   ├── edital.py           # Classe Edital
│   │   └── __init__.py
│   ├── services/               # Lógica de negócio
│   │   ├── scraper.py          # Web scraper dos editais (Selenium)
│   │   ├── email_service.py    # Envio de notificações por e-mail
│   │   ├── notificador.py      # Lógica de correspondência edital-interesse
│   │   └── __init__.py
│   └── utils/
│       ├── db.py               # Conexão com PostgreSQL
│       └── __init__.py
├── frontend/
│   ├── login.html              # Interface de login
│   ├── cadastro.html           # Interface de cadastro
│   └── style.css               # Estilos compartilhados
├── criar_tabelas.py            # Script para inicializar o banco
├── reset_banco.py              # Script para limpar dados (apenas dev)
├── server.py                   # Servidor FastAPI principal
├── requirements.txt            # Dependências do projeto
├── .env                        # Variáveis de ambiente (NÃO versionado)
├── .gitignore                  # Configurações do Git
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

### Status
#### `GET /`
Verifica se a API está rodando

**Response:**
```json
{
  "mensagem": "API PósEmFoco rodando com PostgreSQL"
}
```

### Autenticação e Cadastro

#### `POST /cadastro`
Registra um novo usuário e suas palavras-chave de interesse

**Request:**
```json
{
  "nome": "João Silva",
  "email": "joao@example.com",
  "senha": "senha_segura_123",
  "nivel_graduacao": "Mestrado",
  "interesses": ["Computação", "Inteligência Artificial", "Python"]
}
```

**Response (Sucesso):**
```json
{
  "mensagem": "Usuário cadastrado com sucesso!",
  "id": 1
}
```

**Response (Erro - Email duplicado):**
```json
{
  "detail": "E-mail já cadastrado."
}
```

#### `POST /login`
Realiza login e inicia automaticamente a busca por novos editais

**Request:**
```json
{
  "email": "joao@example.com",
  "senha": "senha_segura_123"
}
```

**Response (Sucesso):**
```json
{
  "mensagem": "Login realizado com sucesso. Buscando novos editais...",
  "usuario": {
    "id": 1,
    "nome": "João Silva",
    "email": "joao@example.com",
    "nivel_graduacao": "Mestrado"
  }
}
```

**Response (Erro - Credenciais inválidas):**
```json
{
  "detail": "Email ou senha incorretos"
}
```

### Editais

#### `GET /editais`
Lista todos os editais já encontrados

**Response:**
```json
[
  {
    "id": 1,
    "titulo": "Edital de Mestrado em Computação",
    "link": "https://ufpa.edu.br/edital-1",
    "resumo": "Descrição do edital...",
    "data_publicacao": "2026-01-25",
    "data_criacao": "2026-01-25T10:30:00"
  }
]
```

#### `POST /editais`
Registra um novo edital no banco (normalmente usado pelo scraper)

**Request:**
```json
{
  "titulo": "Edital de Doutorado em Engenharia",
  "link": "https://ufpa.edu.br/edital-novo",
  "resumo": "Descrição do novo edital",
  "data_publicacao": "2026-01-25"
}
```

**Response (Sucesso):**
```json
{
  "mensagem": "Edital salvo com sucesso"
}
```

**Response (Edital duplicado):**
```json
{
  "mensagem": "Edital não salvo (provavelmente duplicado)"
}
```

## 🏗️ Arquitetura

A aplicação segue o padrão de **camadas** (Layered Architecture) para maior organização e manutenibilidade:

```
┌─────────────────────────────────────────────────────┐
│         Frontend (HTML5 + CSS3 + JS)                │
│    ├─ login.html (autenticação de usuários)        │
│    └─ cadastro.html (registro e interesses)        │
└────────────────────┬────────────────────────────────┘
                     │ HTTP Requests
┌────────────────────▼────────────────────────────────┐
│       FastAPI Server (server.py)                    │
│    - Gerencia endpoints REST                        │
│    - Validação com Pydantic                         │
│    - Hashing de senhas com bcrypt                   │
│    - CORS habilitado para requisições externas      │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│      Services Layer (app/services/)                 │
│    ├─ scraper.py (extrai dados via Selenium)       │
│    ├─ email_service.py (envia notificações SMTP)   │
│    └─ notificador.py (lógica de matching)          │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│       DAO Layer (app/dao/)                          │
│    ├─ usuario_dao.py (CRUD usuários)               │
│    ├─ interesse_dao.py (gerencia interesses)       │
│    └─ edital_dao.py (gerencia editais)             │
└────────────────────┬────────────────────────────────┘
                     │ SQL Queries
┌────────────────────▼────────────────────────────────┐
│       PostgreSQL Database                           │
│    ├─ usuario (armazena usuários registrados)      │
│    ├─ interesse (palavras-chave por usuário)       │
│    └─ edital (editais encontrados)                 │
└─────────────────────────────────────────────────────┘
```

### Fluxo de Execução

1. **Cadastro:**
   - Usuário preenche formulário → POST /cadastro
   - Servidor valida dados e criptografa senha
   - Interesses são salvos na tabela `interesse`

2. **Login:**
   - Usuário autentica → POST /login
   - Credenciais são validadas contra o banco
   - Uma tarefa de background é iniciada (executar_scraper)

3. **Scraping (Automático após login):**
   - Selenium acessa site da UFPA
   - Extrai informações dos editais
   - Verifica duplicatas no banco
   - Salva novos editais

4. **Notificação:**
   - Sistema busca interesses de cada usuário
   - Compara com editais encontrados
   - Envia e-mails para usuários correspondentes
   - Registra histórico no banco

## 🛠️ Comandos Úteis

### Gerenciar Banco de Dados

```bash
# Criar as tabelas automaticamente
python criar_tabelas.py

# Limpar todos os dados (CUIDADO - apenas desenvolvimento)
python reset_banco.py

# Backup do banco
pg_dump -U posemfoco_user posemfoco > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -U posemfoco_user posemfoco < backup_20260125.sql
```

### Executar a Aplicação

```bash
# Iniciar o servidor FastAPI (modo desenvolvimento com reload)
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Iniciar em modo produção (sem reload)
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testar Funcionalidades

```bash
# Verificar documentação da API (Swagger UI)
# Acesse: http://localhost:8000/docs

# Testar endpoint de status
curl http://localhost:8000/

# Testar cadastro
curl -X POST http://localhost:8000/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste",
    "email": "teste@example.com",
    "senha": "senha123",
    "nivel_graduacao": "Mestrado",
    "interesses": ["Python", "IA"]
  }'

# Listar editais
curl http://localhost:8000/editais
```

### Debugging

```bash
# Ver logs detalhados do servidor
uvicorn server:app --reload --log-level debug

# Ativar modo debug em Python scripts
python -c "import logging; logging.basicConfig(level=logging.DEBUG); exec(open('criar_tabelas.py').read())"
```

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'app'"

**Problema:** Python não encontra o módulo da aplicação.

**Solução:** Certifique-se de estar na pasta raiz do projeto:
```bash
cd /caminho/para/PosEmFoco
python criar_tabelas.py
```

### Erro: "psycopg2.OperationalError: could not connect to server"

**Problema:** Não consegue conectar ao PostgreSQL.

**Solução:** Verifique se PostgreSQL está rodando e se as credenciais estão corretas:
```bash
# Linux
sudo systemctl start postgresql

# Mac (Homebrew)
brew services start postgresql

# Verificar se está rodando
sudo systemctl status postgresql
```

Verifique as variáveis no `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=posemfoco_user
DB_PASSWORD=sua_senha_segura
DB_NAME=posemfoco
```

### Erro: "SMTPAuthenticationError" ao enviar e-mail

**Problema:** Falha na autenticação com Gmail.

**Solução:**
1. Use [Senhas de Aplicativo](https://myaccount.google.com/apppasswords) (recomendado)
2. Não use a senha da conta Google
3. Verifique se habilitou acesso a apps menos seguros (menos seguro, não recomendado)

Exemplo `.env` correto:
```env
EMAIL_ADDRESS=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_aplicativo  # Não é a senha da conta!
```

### Erro: "ConnectionRefusedError" ao iniciar servidor

**Problema:** Porta 8000 já está em uso ou servidor não inicia.

**Solução:** Use outra porta:
```bash
uvicorn server:app --reload --port 8001
```

Ou libere a porta:
```bash
# Linux - Ver processo na porta
lsof -i :8000

# Matar processo
kill -9 <PID>
```

### Erro: Selenium não encontra Chrome

**Problema:** ChromeDriver não está disponível.

**Solução:**
```bash
# Linux - Instalar Chrome
sudo apt-get update
sudo apt-get install google-chrome-stable

# Verificar instalação
google-chrome --version

# Reinstalar dependências Python
pip install --upgrade webdriver-manager selenium
```

### Erro: "CORS policy: No 'Access-Control-Allow-Origin'"

**Problema:** Requisições do frontend são bloqueadas.

**Solução:** CORS já está configurado em `server.py`, mas se persistir, verifique:
```python
# Em server.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, use URLs específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Erro: "Permission denied" ao executar scripts

**Problema:** Scripts Python não têm permissão de execução.

**Solução:**
```bash
chmod +x criar_tabelas.py reset_banco.py
python criar_tabelas.py  # Em vez de ./criar_tabelas.py
```

### Banco de dados vazio após inicializar

**Problema:** Tabelas não foram criadas.

**Solução:** Execute manualmente:
```bash
python criar_tabelas.py
```

E verifique se as tabelas foram criadas:
```bash
psql -U posemfoco_user -d posemfoco -c "\dt"
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

- [ ] Autenticação com JWT tokens (mais seguro que sessões simples)
- [ ] Dashboard de visualização de editais com filtros avançados
- [ ] Histórico de notificações enviadas
- [ ] API para buscar editais com filtros (data, área, etc)
- [ ] Suporte a múltiplas universidades (UFRJ, USP, etc)
- [ ] Aplicativo mobile (React Native ou Flutter)
- [ ] Integração com WhatsApp/Telegram
- [ ] Sistema de recomendações com Machine Learning
- [ ] Testes automatizados (pytest, unittest)
- [ ] Deploy com Docker e CI/CD
- [ ] Monitoramento e logs centralizados
- [ ] Rate limiting e throttling nas APIs

## 📄 Padrões de Código

### Convenções

- **Python:** PEP 8 (seguir estilos do projeto existente)
- **Banco de Dados:** Nomes em snake_case, plurais para tabelas
- **API:** RESTful, nomes de endpoints em minúsculas
- **Git:** Commits descritivos em português ou inglês
- **Docstrings:** Descrever função, parâmetros e retorno

### Exemplo de Função Bem Documentada

```python
def salvar_usuario(usuario: Usuario) -> int:
    """
    Salva um novo usuário no banco de dados.
    
    Args:
        usuario: Objeto Usuario com nome, email e senha_hash
        
    Returns:
        int: ID do usuário recém criado, ou None se falhar
        
    Raises:
        Exception: Se email já existe ou erro de banco
    """
    # implementação...
    pass
```

## 📞 Contribuição

### Reportar Bugs

1. Abra uma [Issue](https://github.com/seu-usuario/PosEmFoco/issues)
2. Descreva o problema com detalhes
3. Inclua logs e/ou screenshots se possível
4. Mencione sua versão de Python e OS

### Contribuir com Código

1. Faça um Fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças com mensagens descritivas
   ```bash
   git commit -m "Adiciona nova funcionalidade de filtro"
   ```
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request descrevendo suas mudanças

### Diretrizes de Contribuição

- Seguir o padrão de código do projeto
- Testar mudanças localmente antes de fazer push
- Adicionar comentários em código complexo
- Atualizar documentação se necessário
- Manter coerência com a estrutura existente

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ para facilitar a vida dos alunos de pós-graduação da UFPA.

---

**Última atualização:** 25 de janeiro de 2026

**Versão:** 1.0.0

**Status:** Em desenvolvimento 🚀

Para mais informações, visite: [GitHub Repository](https://github.com/seu-usuario/PosEmFoco)
