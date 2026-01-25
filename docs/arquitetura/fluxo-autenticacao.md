# 🔐 Fluxo de Autenticação

Documentação técnica detalhada do sistema de cadastro e login.

## 📋 Índice
1. [Conceitos](#conceitos)
2. [Fluxo de Cadastro](#fluxo-de-cadastro)
3. [Fluxo de Login](#fluxo-de-login)
4. [Segurança](#segurança)
5. [Testes](#testes)

---

## 🎯 Conceitos

### Senhas vs Hashes

```
Senha: "Aluno@2026"
                    ↓ bcrypt (irreversível)
Hash: "$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcg7b3XeKeUxWdeS86AGR0Iy/1m"
```

**Importante:**
- ✅ Armazenar: HASH
- ❌ Nunca armazenar: SENHA
- Verificação: `hash == bcrypt(senha_digitada, salt)`

### Bcrypt

Função de hash cripto-segura:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # 12 rounds = mais seguro
)

# Gerar hash
hash_senha = pwd_context.hash("Aluno@2026")
# Resultado: $2b$12$...

# Verificar
pwd_context.verify("Aluno@2026", hash_senha)  # True
pwd_context.verify("senha_errada", hash_senha)  # False
```

---

## 📝 Fluxo de Cadastro

### Diagrama Sequencial

```
Frontend                  FastAPI              DAO              PostgreSQL
   │                        │                   │                   │
   │─ POST /cadastro ──────→│                   │                   │
   │  { nome, email,        │                   │                   │
   │    senha, interesse }  │                   │                   │
   │                        │                   │                   │
   │                        ├─ Validar Pydantic│                   │
   │                        │  (email válido?)  │                   │
   │                        │                   │                   │
   │                        ├─ Hash senha ──────┤                   │
   │                        │  bcrypt           │                   │
   │                        │                   │                   │
   │                        ├─ Buscar email ───→│─ SELECT email ───→│
   │                        │  (já existe?)     │                   │
   │                        │←─────────────────←│←───────────────────│
   │                        │  (não existe)     │                   │
   │                        │                   │                   │
   │                        ├─ Salvar usuário ─→│─ INSERT usuario ──→│
   │                        │  (com hash)       │                   │
   │                        │                   │                   │
   │                        │←─────────────────←│←─ id retornado ────│
   │                        │ id = 1            │                   │
   │                        │                   │                   │
   │                        ├─ Salvar interesses→│─ INSERT interesse→│
   │                        │                   │   (usuario_id, ... │
   │                        │                   │                   │
   │←─ Resposta OK ────────│                   │                   │
   │  { mensagem, id }     │                   │                   │
   │                        │                   │                   │
```

### Código Passo a Passo

#### 1. Frontend (login.html)

```html
<form id="formCadastro">
    <input type="text" id="nome" placeholder="Nome completo" required>
    <input type="email" id="email" placeholder="Email" required>
    <input type="password" id="senha" placeholder="Senha" required>
    <select id="nivel">
        <option>Mestrado</option>
        <option>Doutorado</option>
    </select>
    <input type="text" id="interesses" placeholder="Python, IA, ...">
    <button type="submit">Cadastrar</button>
</form>

<script>
document.getElementById('formCadastro').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const dados = {
        nome: document.getElementById('nome').value,
        email: document.getElementById('email').value,
        senha: document.getElementById('senha').value,
        nivel_graduacao: document.getElementById('nivel').value,
        interesses: document.getElementById('interesses').value.split(',')
                                                          .map(i => i.trim())
    };
    
    const res = await fetch('/cadastro', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dados)
    });
    
    const resposta = await res.json();
    if (res.ok) {
        alert('Cadastro com sucesso! ID: ' + resposta.id);
    } else {
        alert('Erro: ' + resposta.detail);
    }
});
</script>
```

#### 2. FastAPI Endpoint (server.py)

```python
from pydantic import BaseModel, EmailStr
from typing import List

class UsuarioInput(BaseModel):
    nome: str
    email: str              # Pydantic valida formato
    senha: str
    nivel_graduacao: str
    interesses: List[str] = []

@app.post("/cadastro")
def cadastrar(dados: UsuarioInput):
    # 1. Verificar se email já existe
    usuario_existente = usuario_dao.buscar_por_email(dados.email)
    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="E-mail já cadastrado."
        )
    
    # 2. Hash da senha
    class UsuarioParaSalvar:
        def __init__(self, d):
            self.nome = d.nome
            self.email = d.email
            self.senha_hash = gerar_hash(d.senha)  # ✅ NUNCA armazena senha plana
            self.nivel_graduacao = d.nivel_graduacao
    
    novo_usuario = UsuarioParaSalvar(dados)
    
    # 3. Salvar usuário no banco
    usuario_id = usuario_dao.salvar(novo_usuario)
    
    if not usuario_id:
        raise HTTPException(
            status_code=500,
            detail="Erro ao cadastrar usuário"
        )
    
    # 4. Salvar interesses
    if dados.interesses:
        interesse_dao.salvar_lista(usuario_id, dados.interesses)
    
    # 5. Responder ao cliente
    return {
        "mensagem": "Usuário cadastrado com sucesso!",
        "id": usuario_id
    }
```

**Função gerar_hash:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def gerar_hash(senha: str):
    return pwd_context.hash(senha)
```

#### 3. DAO (usuario_dao.py)

```python
class UsuarioDAO:
    def salvar(self, usuario):
        """Insere novo usuário no banco"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO usuario (nome, email, senha_hash, nivel_graduacao)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """
            
            cursor.execute(sql, (
                usuario.nome,
                usuario.email,
                usuario.senha_hash,
                usuario.nivel_graduacao
            ))
            
            usuario_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            return usuario_id
            
        except Exception as e:
            print(f"Erro ao salvar usuário: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    def buscar_por_email(self, email):
        """Busca usuário por email"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            sql = "SELECT id, nome, email, senha_hash, nivel_graduacao FROM usuario WHERE email = %s"
            cursor.execute(sql, (email,))
            
            resultado = cursor.fetchone()
            cursor.close()
            
            if resultado:
                return {
                    'id': resultado[0],
                    'nome': resultado[1],
                    'email': resultado[2],
                    'senha_hash': resultado[3],
                    'nivel_graduacao': resultado[4]
                }
            return None
            
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
        finally:
            if conn:
                conn.close()
```

#### 4. Banco de Dados

O INSERT acontece:
```sql
INSERT INTO usuario (nome, email, senha_hash, nivel_graduacao)
VALUES ('João Silva', 'joao@example.com', '$2b$12$...', 'Mestrado')
RETURNING id;
-- Retorna: 1
```

---

## 🔑 Fluxo de Login

### Diagrama Sequencial

```
Frontend                  FastAPI              DAO              PostgreSQL
   │                        │                   │                   │
   │─ POST /login ────────→ │                   │                   │
   │  { email, senha }      │                   │                   │
   │                        │                   │                   │
   │                        ├─ Buscar usuário ─→│─ SELECT * WHERE──→│
   │                        │                   │  email = ...      │
   │                        │←─────────────────←│←─ hash_senha ─────│
   │                        │                   │                   │
   │                        ├─ Verificar senha  │                   │
   │                        │ (bcrypt.verify)   │                   │
   │                        │                   │                   │
   │                        ├─ Se inválido:     │                   │
   │                        │  erro 401         │                   │
   │                        │                   │                   │
   │←─ Erro 401 ───────────│                   │                   │
   │  "Email ou senha      │                   │                   │
   │   incorretos"         │                   │                   │
   │                        │                   │                   │
   │  (ou SE credenciais OK)                   │                   │
   │                        │                   │                   │
   │                        ├─ Inicia scraper   │                   │
   │                        │ (background task) │                   │
   │                        │                   │                   │
   │←─ Resposta OK ────────│                   │                   │
   │  { mensagem,          │                   │                   │
   │    usuario }          │                   │                   │
```

### Código Passo a Passo

#### 1. Frontend (login.html)

```html
<form id="formLogin">
    <input type="email" id="email" placeholder="Email" required>
    <input type="password" id="senha" placeholder="Senha" required>
    <button type="submit">Login</button>
</form>

<script>
document.getElementById('formLogin').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const dados = {
        email: document.getElementById('email').value,
        senha: document.getElementById('senha').value
    };
    
    const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dados)
    });
    
    if (res.ok) {
        const resposta = await res.json();
        alert('Login bem-sucedido! Buscando editais...');
        // Redirecionar ou atualizar página
        window.location.href = '/frontend/dashboard.html';
    } else {
        const erro = await res.json();
        alert('Erro: ' + erro.detail);
    }
});
</script>
```

#### 2. FastAPI Endpoint (server.py)

```python
from fastapi import BackgroundTasks

class LoginInput(BaseModel):
    email: str
    senha: str

@app.post("/login")
def login(dados: LoginInput, background_tasks: BackgroundTasks):
    # 1. Buscar usuário por email
    usuario_encontrado = usuario_dao.buscar_por_email(dados.email)
    
    if not usuario_encontrado:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )
    
    # 2. Verificar senha (bcrypt)
    senha_valida = verificar_senha(
        dados.senha,
        usuario_encontrado['senha_hash']
    )
    
    if not senha_valida:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )
    
    # 3. Log
    print(f"Login efetuado por {usuario_encontrado['nome']}")
    
    # 4. Inicia scraper em background
    background_tasks.add_task(executar_scraper)
    print("Scraper iniciado em background")
    
    # 5. Responder
    return {
        "mensagem": "Login realizado com sucesso. Buscando novos editais...",
        "usuario": {
            "id": usuario_encontrado['id'],
            "nome": usuario_encontrado['nome'],
            "email": usuario_encontrado['email'],
            "nivel_graduacao": usuario_encontrado['nivel_graduacao']
        }
    }

def verificar_senha(senha_pura: str, senha_hash: str):
    return pwd_context.verify(senha_pura, senha_hash)
```

---

## 🔒 Segurança

### Proteções Implementadas

| Proteção | Implementação |
|----------|---------------|
| Hash de Senhas | bcrypt com 12 rounds |
| Validação de Email | Pydantic EmailStr |
| SQL Injection | Parameterized queries (%s) |
| Senhas Idênticas | Cada senha tem seu próprio salt |
| Timing Attack | bcrypt resiste naturalmente |

### Proteções Faltando (Para Futuro)

```python
# JWT Token (Session Management)
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from datetime import datetime, timedelta
import jwt

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def criar_token(usuario_id: int):
    """Gera JWT token válido por 24h"""
    payload = {
        'usuario_id': usuario_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/login")
def login(dados: LoginInput):
    # ... verificação ...
    
    token = criar_token(usuario_encontrado['id'])
    
    return {
        "mensagem": "Login sucesso",
        "token": token
    }

# Rate Limiting (Impedir brute force)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")  # Máx 5 tentativas por minuto
def login(request: Request, dados: LoginInput):
    pass
```

---

## 🧪 Testes

### Teste Manual com curl

```bash
# 1. Cadastro
curl -X POST http://localhost:8000/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Silva",
    "email": "maria@example.com",
    "senha": "senha123!",
    "nivel_graduacao": "Doutorado",
    "interesses": ["IA", "Python"]
  }'

# Resposta esperada:
# {"mensagem": "Usuário cadastrado com sucesso!", "id": 1}

# 2. Login com senha correta
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "senha": "senha123!"
  }'

# Resposta esperada:
# {"mensagem": "Login realizado...", "usuario": {...}}

# 3. Login com senha errada (deve falhar)
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "senha": "senha_errada"
  }'

# Resposta esperada (erro):
# {"detail": "Email ou senha incorretos"}

# 4. Email duplicado (deve falhar)
curl -X POST http://localhost:8000/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Outro Usuario",
    "email": "maria@example.com",
    "senha": "outra_senha",
    "nivel_graduacao": "Mestrado",
    "interesses": []
  }'

# Resposta esperada (erro):
# {"detail": "E-mail já cadastrado."}
```

### Teste Automatizado (pytest)

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_cadastro_sucesso():
    response = client.post("/cadastro", json={
        "nome": "Teste User",
        "email": "teste@example.com",
        "senha": "senha123!",
        "nivel_graduacao": "Mestrado",
        "interesses": ["Python"]
    })
    assert response.status_code == 200
    assert response.json()["mensagem"] == "Usuário cadastrado com sucesso!"

def test_email_duplicado():
    # Primeiro cadastro
    client.post("/cadastro", json={
        "nome": "User 1",
        "email": "user1@example.com",
        "senha": "senha123!",
        "nivel_graduacao": "Mestrado",
        "interesses": []
    })
    
    # Segundo cadastro com mesmo email
    response = client.post("/cadastro", json={
        "nome": "User 2",
        "email": "user1@example.com",
        "senha": "outra_senha!",
        "nivel_graduacao": "Doutorado",
        "interesses": []
    })
    assert response.status_code == 400
    assert "já cadastrado" in response.json()["detail"]

def test_login_sucesso():
    # Cadastrar
    client.post("/cadastro", json={
        "nome": "Login User",
        "email": "login@example.com",
        "senha": "senha123!",
        "nivel_graduacao": "Mestrado",
        "interesses": []
    })
    
    # Fazer login
    response = client.post("/login", json={
        "email": "login@example.com",
        "senha": "senha123!"
    })
    assert response.status_code == 200
    assert "usuario" in response.json()

def test_login_senha_errada():
    response = client.post("/login", json={
        "email": "inexistente@example.com",
        "senha": "qualquer_senha"
    })
    assert response.status_code == 401
    assert "incorretos" in response.json()["detail"]
```

Execute testes:
```bash
pytest tests/test_auth.py -v
```

---

## 📚 Próximos Passos

- [Fluxo de Scraping](fluxo-scraping.md) - Como o web scraper funciona
- [API Endpoints](../api/endpoints.md) - Documentação de endpoints
- [Guia de Desenvolvimento](../guias/desenvolvimento.md) - Contribuir

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
