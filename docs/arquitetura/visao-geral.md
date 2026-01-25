# 🏗️ Visão Geral da Arquitetura

Documento que descreve as decisões de design e padrões arquiteturais do PósEmFoco.

## 📐 Visão Geral

PósEmFoco segue uma **arquitetura em camadas** (Layered Architecture), que separa as responsabilidades em níveis bem definidos. Isso torna o código mais organizado, testável e manutenível.

```
┌─────────────────────────────────────────────────┐
│     Frontend Layer (HTML/CSS/JavaScript)        │
│  - login.html, cadastro.html                    │
│  - Validação básica no cliente                  │
└────────────────┬────────────────────────────────┘
                 │ HTTP Requests
┌────────────────▼────────────────────────────────┐
│  Presentation Layer (FastAPI - server.py)       │
│  - Endpoints REST (/cadastro, /login, etc)      │
│  - Validação com Pydantic                       │
│  - CORS habilitado                              │
│  - Background tasks (scraper)                   │
└────────────────┬────────────────────────────────┘
                 │ Chama services
┌────────────────▼────────────────────────────────┐
│  Business Logic Layer (app/services/)           │
│  - scraper.py: extrai dados                     │
│  - email_service.py: envia notificações         │
│  - notificador.py: lógica de matching           │
└────────────────┬────────────────────────────────┘
                 │ Chama DAOs
┌────────────────▼────────────────────────────────┐
│  Data Access Layer (app/dao/)                   │
│  - usuario_dao.py: CRUD de usuários             │
│  - interesse_dao.py: CRUD de interesses        │
│  - edital_dao.py: CRUD de editais               │
└────────────────┬────────────────────────────────┘
                 │ SQL Queries
┌────────────────▼────────────────────────────────┐
│  Data Layer (PostgreSQL)                        │
│  - usuario, interesse, edital                   │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Padrões de Design

### 1. **DAO (Data Access Object)**

**Objetivo:** Centralizar acesso ao banco de dados.

**Implementação:**
```python
# app/dao/usuario_dao.py
class UsuarioDAO:
    def salvar(self, usuario):
        # Lógica de inserção no BD
        pass
    
    def buscar_por_email(self, email):
        # Lógica de busca no BD
        pass
```

**Benefícios:**
- Isolamento da lógica SQL
- Fácil de testar
- Mudança de BD sem afetar o resto do código

---

### 2. **Service Layer**

**Objetivo:** Encapsular lógica de negócio complexa.

**Implementação:**
```python
# app/services/scraper.py
def executar_scraper():
    # 1. Buscar interesses dos usuários
    # 2. Fazer web scraping
    # 3. Salvar editais
    # 4. Notificar usuários
    pass
```

**Benefícios:**
- Lógica separada de endpoints
- Reutilizável em múltiplos contextos
- Fácil de testar isoladamente

---

### 3. **MVC-like Pattern**

**Models** - Estrutura de dados:
```python
class Usuario:
    id: int
    nome: str
    email: str
```

**Views** - FastAPI endpoints:
```python
@app.post("/cadastro")
def cadastrar(dados: UsuarioInput):
    # Chama service
    pass
```

**Controllers** (Services) - Lógica:
```python
def cadastrar_usuario(dados):
    # Valida, criptografa, salva
    pass
```

---

## 🔄 Fluxo de Requisição

### Exemplo: POST /cadastro

```
1. Cliente (Frontend)
   └─ POST /cadastro com { nome, email, senha, interesses }

2. FastAPI Server (server.py)
   └─ Recebe, valida com Pydantic
   └─ Chama UsuarioDAO.salvar()

3. DAO Layer (usuario_dao.py)
   └─ Conecta ao banco
   └─ Executa INSERT
   └─ Retorna ID

4. Business Logic (se houver interesses)
   └─ Chama InteresseDAO.salvar_lista()

5. Response
   └─ Retorna { "mensagem": "...", "id": 1 }

6. Background Task
   └─ FastAPI inicia executar_scraper() em paralelo
```

---

## 🗄️ Padrão de Dados

### Estrutura de Pastas

```
app/
├── models/                  # Definições de dados
│   ├── usuario.py          # Classe Usuario
│   ├── edital.py           # Classe Edital
│   └── __init__.py
│
├── dao/                     # Data Access Objects
│   ├── usuario_dao.py       # SQL de usuários
│   ├── interesse_dao.py     # SQL de interesses
│   ├── edital_dao.py        # SQL de editais
│   └── __init__.py
│
├── services/                # Lógica de Negócio
│   ├── scraper.py           # Web scraping
│   ├── email_service.py     # Envio de email
│   ├── notificador.py       # Matching edital-interesse
│   └── __init__.py
│
├── utils/                   # Utilitários
│   ├── db.py                # Conexão com BD
│   └── __init__.py
│
└── __init__.py
```

### Fluxo de Dados

```
Entrada (Frontend/API)
    │
    ▼
FastAPI (server.py)
    ├─ Valida dados (Pydantic)
    ├─ Chama Service
    │
    ▼
Services (scraper, email_service, etc)
    ├─ Lógica de negócio
    ├─ Chama DAO
    │
    ▼
DAO (usuario_dao, interesse_dao, etc)
    ├─ Monta SQL
    ├─ Executa query
    ├─ Retorna dados
    │
    ▼
Database (PostgreSQL)
    └─ Armazena/recupera dados
    │
    ▼
DAO
    ├─ Processa resultado
    │
    ▼
Service
    ├─ Processa resultado
    │
    ▼
FastAPI
    ├─ Formata response JSON
    │
    ▼
Saída (Frontend/API Response)
```

---

## 🔐 Segurança

### Autenticação

**Senhas:**
- Armazenadas com bcrypt (hash)
- Nunca armazenar senha plana
- Sempre verificar com `pwd_context.verify()`

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Criptografar
hash_senha = pwd_context.hash("senha_usuario")

# Verificar
pwd_context.verify("senha_usuario", hash_senha)  # True/False
```

### Validação de Input

**Pydantic Models:**
```python
class UsuarioInput(BaseModel):
    nome: str                # Obrigatório
    email: str               # Obrigatório, validado
    senha: str               # Obrigatório
    nivel_graduacao: str     # Obrigatório
    interesses: List[str] = []  # Opcional, padrão vazio
```

Pydantic valida:
- Tipo de dados
- Campos obrigatórios
- Formato (email, URL, etc)

### SQL Injection Prevention

**Parameterized Queries:**
```python
# ✅ SEGURO - Usa placeholders %s
sql = "INSERT INTO usuario (nome, email) VALUES (%s, %s)"
cursor.execute(sql, (nome, email))

# ❌ INSEGURO - Concatenação de strings
sql = f"INSERT INTO usuario (nome, email) VALUES ('{nome}', '{email}')"
cursor.execute(sql)
```

### CORS

**Cross-Origin Resource Sharing:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Produção: especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Decisões Arquiteturais

### Por que Layered Architecture?

| Aspecto | Benefício |
|---------|-----------|
| **Separação de Concerns** | Cada camada tem uma responsabilidade |
| **Testabilidade** | Fácil mockar dependências |
| **Manutenibilidade** | Mudanças isoladas por camada |
| **Escalabilidade** | Fácil adicionar novas features |
| **Reutilização** | Services usados por múltiplos endpoints |

### Por que FastAPI?

- ✅ Rápido (baseado em Starlette + Uvicorn)
- ✅ Validação automática (Pydantic)
- ✅ Documentação automática (Swagger)
- ✅ Suporte a async (background tasks)
- ✅ Ótimo para MVPs

### Por que PostgreSQL?

- ✅ ACID garantido
- ✅ Suporte a JSON/arrays
- ✅ Escalável
- ✅ Open source
- ✅ Excelente para produção

### Por que Selenium?

- ✅ Simula navegador real
- ✅ JavaScript é executado
- ✅ Handles dinâmico
- ✅ Suporta paginação

---

## 🚀 Fluxo Geral de Execução

### Startup
```
1. Ler .env
2. Inicializar FastAPI
3. Configurar CORS
4. Conectar ao banco (lazy - só quando precisa)
5. Servidor ativo em porta 8000
```

### User Signup
```
1. POST /cadastro → validate with Pydantic
2. usuarioDAO.salvar(usuario) → INSERT usuario
3. interesseDAO.salvar_lista(id, interesses) → INSERT interesses
4. Retorna { mensagem, id }
```

### User Login
```
1. POST /login → validate email/senha
2. usuarioDAO.buscar_por_email(email) → SELECT usuario
3. Verificar senha com bcrypt
4. Inicia background task: executar_scraper()
5. Retorna { mensagem, usuario }
```

### Scraper (Background)
```
1. Buscar todos os usuários e seus interesses
2. Inicializar Selenium
3. Acessar site UFPA
4. Extrair editais
5. Para cada edital:
   a. Verificar se já existe (SELECT)
   b. Se novo, INSERT no banco
6. Para cada edital novo:
   a. Buscar usuários interessados
   b. Enviar email (SMTP)
7. Finalizar
```

---

## 🔌 Extensibilidade

### Adicionar Novo Endpoint

```python
# 1. Criar DAO se precisar
class NovoDAO:
    def buscar_tudo(self):
        pass

# 2. Criar Service se houver lógica
def processar_novo():
    pass

# 3. Adicionar endpoint em server.py
@app.get("/novo")
def novo_endpoint():
    dao = NovoDAO()
    dados = dao.buscar_tudo()
    return {"dados": dados}
```

### Adicionar Nova Feature

1. Criar `novo_service.py` em `app/services/`
2. Criar `novo_dao.py` em `app/dao/`
3. Criar migrations do BD (se tabelas novas)
4. Adicionar endpoint em `server.py`
5. Testar

---

## 📚 Convenções

### Nomes

```
✅ Bom
usuario_dao.py (arquivo)
UsuarioDAO (classe)
buscar_por_email (método)
usuario_id (variável)

❌ Ruim
UsuarioDAOClass.py
getUserByEmail
userId
```

### Estrutura de Arquivos

Manter consistência:
```
app/
├── models/
│   └── xxx.py          # Sempre ter __init__.py
├── dao/
│   └── xxx_dao.py
├── services/
│   └── xxx_service.py  (ou xxx.py)
└── utils/
    └── helper.py
```

---

## 📞 Próximos Passos

- [Banco de Dados](banco-dados.md) - Schema completo
- [Fluxo de Autenticação](fluxo-autenticacao.md) - Login detalhado
- [Fluxo de Scraping](fluxo-scraping.md) - Web scraper detalhado

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
