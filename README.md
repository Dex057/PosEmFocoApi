# PósEmFoco - Monitorador de Editais de Pós-Graduação (Região Norte) 🎓

O **PósEmFoco** é um sistema automatizado desenvolvido em Python (trabalho de conclusão de curso) para monitorar, capturar e notificar usuários sobre novos editais de pós-graduação publicados pelas universidades públicas da Região Norte do Brasil.

O sistema permite que o usuário cadastre palavras-chave (ex: "Enfermagem", "Computação") e receba notificações por e-mail assim que um novo edital correspondente a algum interesse cadastrado for publicado por qualquer uma das universidades monitoradas.

> **Status atual:** dez instituições monitoradas — todas as públicas do Pará (UFPA, UFRA, UFOPA, UNIFESSPA, IFPA, UEPA), mais UNIFAP (AP), UFAM (AM), UFT e IFTO (TO). As demais públicas do Norte ainda não têm fonte configurada, e o motivo de cada uma está anotado no fim de [`fontes.py`](app/services/scraping/fontes.py). Adicionar uma é cadastrar uma `FonteEdital`, não reescrever código — veja [Adicionando uma nova universidade](#adicionando-uma-nova-universidade).

## 📋 Sumário

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#️-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Como Usar](#-como-usar)
- [Fontes de Editais](#-fontes-de-editais)
- [API Endpoints](#-api-endpoints)
- [Arquitetura](#-arquitetura)
- [Troubleshooting](#-troubleshooting)
- [Contribuição](#-contribuição)

## 🎯 Visão Geral

PósEmFoco é uma solução inteligente que automatiza o monitoramento de editais acadêmicos. Em vez de os usuários verificarem manualmente o site da UFPA diariamente, o sistema faz isso por eles usando web scraping com Selenium, verifica novos editais contra interesses registrados e envia notificações por e-mail em tempo real.

### Fluxo Principal

1. Usuário se cadastra e define palavras-chave de interesse
2. Um processo `worker` separado da API roda o scraper sozinho em loop, a cada `INTERVALO_SCRAPER_MINUTOS` (padrão 60min) — não depende de ninguém logar nem de a API estar recebendo requisições
3. Novos editais são detectados e armazenados no banco de dados
4. Sistema verifica correspondência entre editais e interesses dos usuários
5. Notificações por e-mail são enviadas automaticamente

> No painel o usuário pode forçar uma rodada extra do scraper (`POST /scraper/rodar`), que roda em background dentro do processo da API. Quem garante o monitoramento contínuo é o `worker`.

### Por que API e worker são processos separados

O scraper (principalmente o motor Selenium) é pesado e roda por vários segundos/minutos. Se ele rodasse dentro do mesmo processo da API:
- um travamento ou consumo alto de memória no scraping afetaria as respostas HTTP;
- reiniciar a API (deploy, crash) interromperia um scraping em andamento.

Por isso o `worker.py` roda como um container/processo próprio (`docker-compose.yml` tem os serviços `app` e `worker`, ambos usando a mesma imagem, cada um com seu comando), compartilhando apenas o banco Postgres com a API.

## 🚀 Funcionalidades

- **Cadastro e Autenticação:** Sistema de registro e login com senhas criptografadas usando bcrypt
- **Gerenciamento de Interesses:** Usuários podem adicionar múltiplas palavras-chave para monitoramento
- **Coleta Multi-Universidade:** Cada universidade é uma "fonte" configurável (URL + seletores), sem precisar duplicar código para adicionar uma nova
- **Dois motores de coleta:** HTML estático (`requests` + `BeautifulSoup`, rápido, sem navegador) e Selenium (para páginas que dependem de JavaScript) — a fonte escolhe qual usar
- **Anti-Duplicidade:** Verifica no banco de dados se o edital já foi processado para evitar notificações duplicadas
- **Notificação por E-mail:** Envia e-mails formatados em HTML com informações completas do edital
- **Dados Persistentes:** Todos os editais, usuários e interesses são armazenados em PostgreSQL

## 🛠️ Tecnologias

| Categoria | Tecnologia |
|-----------|-----------|
| **Linguagem** | Python 3.10+ |
| **Framework Web** | FastAPI |
| **Servidor** | Uvicorn |
| **Scraping (HTML estático)** | requests & BeautifulSoup |
| **Scraping (JS renderizado)** | Selenium & Webdriver Manager |
| **Banco de Dados** | PostgreSQL |
| **Autenticação** | bcrypt (passlib) |
| **Comunicação** | SMTP (Gmail) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Gerenciador de Dependências** | pip |

## 🌐 Fontes de Editais

| Instituição | UF | Páginas monitoradas | Motor |
|---|---|---|---|
| UFPA | PA | SIGAA + `ufpa.br/?post_type=editais` | sigaa + selenium |
| UFRA | PA | SIGAA + `novo.ufra.edu.br` (categoria Editais) | sigaa + estático |
| UFOPA | PA | SIGAA | sigaa |
| UNIFESSPA | PA | SIGAA + `editais.unifesspa.edu.br` (pós-graduação) | sigaa + estático |
| IFPA | PA | SIGAA (instável — o servidor deles responde 502 com frequência) | sigaa |
| UEPA | PA | SGPS (sistema de seleções) + `uepa.br` | estático |
| UNIFAP | AP | SIGAA | sigaa |
| UFAM | AM | `ufam.edu.br/editais` | estático |
| UFT | TO | `uft.edu.br/editais` | estático |
| IFTO | TO | `ifto.edu.br/editais` | estático |

O motor **sigaa** é o que rende mais: quase toda IFES expõe
`/sigaa/public/processo_seletivo/lista.jsf` sem login, com o mesmo layout, e de lá saem o
curso, o número de vagas e o **período de inscrição** — em vez de notícia solta do portal.
Para incluir uma nova IFES basta uma linha: `_sigaa("SIGLA", "sigaa.dominio.br")`.

Para conferir se as fontes continuam de pé (portais mudam de layout sem aviso):

```bash
python -m app.services.scraping.fontes
# UFPA         sigaa       81 itens | DOUTORADO EM SOCIOLOGIA E ANTROPOLOGIA - PPGSA...
# UEPA         estatico    73 itens | PROCESSO SELETIVO PARA O CURSO DE PÓS-GRADUAÇÃO...
```

Se alguma linha vier com `0 itens`, o seletor daquela fonte quebrou.

As públicas do Norte ainda de fora (IFAM, UFAC, UNIR, UFRR, UEA, UERR, UEAP, UNITINS, IFAP,
IFAC, IFRO, IFRR) estão listadas no fim do `fontes.py`, cada uma com o motivo: anti-bot,
lista renderizada por JavaScript ou links sem URL navegável.

Cada instituição monitorada é uma `FonteEdital` em [`app/services/scraping/fontes.py`](app/services/scraping/fontes.py):

```python
FonteEdital(
    nome="UFPA - Editais",
    universidade="UFPA",
    url="https://ufpa.br/?post_type=editais",
    engine="selenium",                              # "estatico" ou "selenium"
    seletor_item="h2.elementor-heading-title a",     # CSS do <a> com título + link
    seletor_next="a.next, a.page-numbers.next",      # CSS do link "próxima página" (opcional)
    max_paginas=3,
)
```

O orquestrador (`app/services/scraper.py`) itera sobre `FONTES`, despacha para o motor certo (`engine_estatico.py` ou `engine_selenium.py`) e aplica a mesma lógica de deduplicação/notificação para todas as universidades — não há nada específico da UFPA fora do arquivo de configuração.

### Adicionando uma nova universidade

1. Abra a página de editais da universidade e veja se a lista aparece no HTML puro (view-source) ou só depois de JavaScript rodar.
2. Identifique o seletor CSS do link de cada item (e da paginação, se houver).
3. Adicione uma nova `FonteEdital` em `fontes.py`:
   - `engine="estatico"` se o HTML puro já contém a lista (mais rápido, sem navegador);
   - `engine="selenium"` se o conteúdo só aparece após JavaScript.
4. Rode `python -m app.services.scraping.fontes` para validar a coleta (mostra quantos itens cada fonte devolveu).

Nenhuma outra parte do sistema precisa mudar — o scraper, o banco e o e-mail já são genéricos.

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
│   │   ├── scraper.py          # Orquestrador: busca interesses, roda as fontes, casa e notifica
│   │   ├── scraping/           # Coleta multi-universidade
│   │   │   ├── fontes.py           # Config de cada universidade (URL, seletores, motor)
│   │   │   ├── engine_estatico.py  # Motor requests + BeautifulSoup (HTML estático)
│   │   │   └── engine_selenium.py  # Motor Selenium (páginas com JS)
│   │   ├── email_service.py    # Envio de notificações por e-mail
│   │   └── __init__.py
│   └── utils/
│       ├── db.py               # Conexão com PostgreSQL
│       └── __init__.py
├── frontend/
│   ├── login.html              # Interface de login
│   ├── cadastro.html           # Interface de cadastro
│   ├── painel.html             # Editais do usuário logado (pós-login)
│   └── style.css               # Estilos compartilhados
├── criar_tabelas.py            # Script para inicializar o banco
├── reset_banco.py              # Script para limpar dados (apenas dev)
├── server.py                   # Servidor FastAPI (API HTTP)
├── worker.py                   # Processo separado: roda o scraper em loop
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
- **requests + beautifulsoup4** - Scraping de páginas HTML estáticas (motor padrão para novas fontes)
- **selenium + webdriver-manager** - Scraping de páginas que dependem de JavaScript
- **psycopg2-binary** - Driver PostgreSQL
- **python-dotenv** - Variáveis de ambiente
- **passlib[bcrypt]** - Criptografia de senhas

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

Copie o template e preencha com valores reais:

```bash
cp .env.example .env
```

Variáveis:

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

# A cada quantos minutos o worker roda o scraper (padrão: 60)
INTERVALO_SCRAPER_MINUTOS=60
```

Depois de configurar o e-mail, valide as credenciais antes de subir tudo:
```bash
python testar_email.py seu_email_pessoal@exemplo.com
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

Rodando via `docker compose up`, os serviços `app` (API) e `worker` (scraper) já sobem juntos. Rodando manualmente (fora do Docker), são dois processos separados:

### 1. Inicie o Servidor FastAPI

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

O servidor iniciará em `http://localhost:8000`

### 1.1 Inicie o Worker (scraper em loop)

Em outro terminal:
```bash
python worker.py
```

Ele roda `executar_scraper()` a cada `INTERVALO_SCRAPER_MINUTOS` (padrão 60) e não depende da API estar de pé — só precisa do banco.

### 2. Acesse a Interface Web

Abra seu navegador e acesse:
- **Página de Login:** `http://localhost:8000/frontend/login.html`
- **Página de Cadastro:** `http://localhost:8000/frontend/cadastro.html`
- **Painel (pós-login):** `http://localhost:8000/frontend/painel.html`
- **Documentação API:** `http://localhost:8000/docs`

### 3. Fluxo de Uso

1. **Cadastro:** Preencha o formulário com seus dados e interesses
2. **Login:** Faça login com suas credenciais — você é redirecionado para o painel
3. **Painel:** Lista os editais que combinam com seus interesses (`GET /me/editais`), permite editar as
   palavras-chave (`PUT /me/interesses`) e forçar uma busca na hora (`POST /scraper/rodar`)
4. **Monitoramento Automático:** O `worker` verifica as fontes configuradas periodicamente, sem precisar de login
5. **Notificações:** Receba e-mails quando novos editais forem encontrados

## 📡 API Endpoints

Os endpoints `/me/*` e `/scraper/rodar` exigem o header `Authorization: Bearer <token>`, devolvido pelo
`POST /login`. As sessões ficam em memória no processo da API — reiniciar o servidor derruba todo mundo.

### Status
#### `GET /`
Redireciona para a interface web (`/frontend/login.html`)

#### `GET /health`
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
Realiza login e devolve o token de sessão usado nos endpoints `/me/*`

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
  "mensagem": "Login realizado com sucesso.",
  "token": "0kZt...",
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
    "resumo": "[UFPA] Contém: computação",
    "data_publicacao": null,
    "data_coleta": "2026-01-25T10:30:00"
  }
]
```

#### `GET /me/editais` 🔒
Lista os editais que combinam com os interesses do usuário logado (usado pelo painel)

**Response:** mesmo formato de `GET /editais`, filtrado pelas palavras-chave do usuário.

### Interesses

#### `GET /me/interesses` 🔒
Lista as palavras-chave do usuário logado: `["computação", "direito"]`

#### `PUT /me/interesses` 🔒
Substitui a lista inteira de palavras-chave (lista vazia remove todas)

**Request:** `{ "interesses": ["computação", "direito"] }`
**Response:** a lista já normalizada (sem espaços sobrando nem itens vazios)

### Scraper

#### `POST /scraper/rodar` 🔒
Dispara uma rodada do scraper em segundo plano. Se já houver uma rodando no mesmo processo, o disparo é ignorado.

**Response:**
```json
{
  "mensagem": "Busca iniciada. Os novos editais aparecem aqui em alguns minutos."
}
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
│    ├─ cadastro.html (registro e interesses)        │
│    └─ painel.html (editais do usuário logado)      │
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
│    ├─ scraper.py (orquestra fontes + matching)     │
│    ├─ scraping/ (fontes.py + engine_estatico.py    │
│    │            + engine_selenium.py, por           │
│    │            universidade)                       │
│    └─ email_service.py (envia notificações SMTP)   │
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
   - A API devolve um token de sessão, guardado no `localStorage` pelo front

3. **Scraping (worker em loop ou disparo manual pelo painel):**
   - O orquestrador percorre todas as `FONTES` configuradas
   - Cada fonte é coletada pelo motor indicado (estático ou Selenium)
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
curl http://localhost:8000/health

# Checagem rápida da API sem banco (DAOs falsos)
python test_api.py

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

`init.sql` é a única fonte de verdade do schema (é o que o Postgres roda automaticamente ao subir o container, e também o que `criar_tabelas.py`/`reset_banco.py` executam fora do Docker).

### Tabela: usuario
```sql
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(200) NOT NULL,
    nivel_graduacao VARCHAR(50),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela: interesse
```sql
CREATE TABLE interesse (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuario(id) ON DELETE CASCADE,
    palavra_chave VARCHAR(100) NOT NULL
);
```

### Tabela: edital
```sql
CREATE TABLE edital (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    link TEXT UNIQUE NOT NULL,
    resumo TEXT,
    data_publicacao VARCHAR(50),
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

`link` é `UNIQUE` no banco — a deduplicação do scraper usa `INSERT ... ON CONFLICT (link) DO NOTHING`, então não há race condition entre checar e inserir.

> ⚠️ Se você já tinha subido o container do Postgres antes dessa mudança, o `init.sql` só roda em um volume vazio. Rode `docker compose down -v` (apaga os dados) e suba de novo, ou aplique o `init.sql` manualmente.

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
- [ ] Cadastrar as demais universidades públicas do Norte em `fontes.py` (UFAM, UFRR, UFAC, UFRO, UNIFAP, UFT, UNIFESSPA, UFOPA, UEPA, UEA...)
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

**Última atualização:** 16 de setembro de 2026

**Versão:** 2.0.0 (arquitetura de scraping multi-universidade)

**Status:** Em desenvolvimento — projeto de TCC 🎓

Para mais informações, visite: [GitHub Repository](https://github.com/seu-usuario/PosEmFoco)
