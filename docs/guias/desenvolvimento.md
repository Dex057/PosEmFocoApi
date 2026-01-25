# 👨‍💻 Guia de Desenvolvimento

Guia completo para desenvolvedores que querem contribuir ou trabalhar no projeto.

## 📋 Índice
1. [Setup para Desenvolvimento](#setup-para-desenvolvimento)
2. [Estrutura de Pastas](#estrutura-de-pastas)
3. [Padrões de Código](#padrões-de-código)
4. [Como Contribuir](#como-contribuir)
5. [Debugging](#debugging)
6. [Testes](#testes)

---

## 🚀 Setup para Desenvolvimento

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/PosEmFoco.git
cd PosEmFoco
```

### 2. Ambiente Virtual

```bash
# Criar
python3 -m venv venv

# Ativar
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências + dev
pip install -r requirements.txt
pip install -r requirements-dev.txt  # pytest, black, flake8, etc
```

### 4. Configure .env

```bash
cp .env.example .env
nano .env
# Edite com suas credenciais
```

### 5. Banco de Dados

```bash
# Criar tabelas
python criar_tabelas.py

# Verificar
psql -U posemfoco_user -d posemfoco -c "\dt"
```

### 6. Execute e Teste

```bash
# Iniciar servidor
uvicorn server:app --reload

# Em outro terminal, testar
curl http://localhost:8000
```

---

## 📁 Estrutura de Pastas

```
PosEmFoco/
│
├── app/                              # Código principal
│   ├── __init__.py
│   ├── dao/                          # Data Access Objects
│   │   ├── __init__.py
│   │   ├── usuario_dao.py            # CRUD usuários
│   │   ├── interesse_dao.py          # CRUD interesses
│   │   ├── edital_dao.py             # CRUD editais
│   │   └── base_dao.py               # DAO base (futuro)
│   │
│   ├── models/                       # Estrutura de dados
│   │   ├── __init__.py
│   │   ├── usuario.py                # Classe Usuario
│   │   ├── edital.py                 # Classe Edital
│   │   └── interesse.py              # Classe Interesse
│   │
│   ├── services/                     # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── scraper.py                # Web scraper
│   │   ├── email_service.py          # SMTP/Email
│   │   ├── notificador.py            # Lógica de matching
│   │   └── base_service.py           # Service base (futuro)
│   │
│   └── utils/                        # Utilitários
│       ├── __init__.py
│       ├── db.py                     # Conexão PostgreSQL
│       ├── logger.py                 # Logging (futuro)
│       └── helpers.py                # Funções auxiliares
│
├── frontend/                         # Interface Web
│   ├── login.html
│   ├── cadastro.html
│   ├── dashboard.html                # (futuro)
│   └── style.css
│
├── tests/                            # Testes automatizados
│   ├── __init__.py
│   ├── test_auth.py                  # Testes de autenticação
│   ├── test_scraper.py               # Testes de scraper
│   ├── test_dao.py                   # Testes de DAO
│   └── conftest.py                   # Fixtures pytest
│
├── docs/                             # Documentação (você está aqui!)
│   ├── README.md
│   ├── guias/
│   ├── arquitetura/
│   ├── api/
│   └── componentes/
│
├── server.py                         # FastAPI principal
├── criar_tabelas.py                  # Script inicializar BD
├── reset_banco.py                    # Script limpar BD
├── requirements.txt                  # Dependências produção
├── requirements-dev.txt              # Dependências desenvolvimento
├── .env.example                      # Template .env
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🎨 Padrões de Código

### Naming Conventions

**Python (PEP 8):**
```python
# Classes - PascalCase
class UsuarioDAO:
    pass

# Funções e variáveis - snake_case
def extrair_editais():
    usuario_id = 1
    return usuario_id

# Constantes - UPPER_SNAKE_CASE
MAX_RETRIES = 3
DATABASE_URL = "postgresql://..."

# Private (início com _)
def _helper_interno():
    pass

# Magic (duplo _)
def __init__(self):
    pass
```

**Arquivo (lowercase + underscore):**
```
usuario_dao.py
email_service.py
criar_tabelas.py
```

### Docstrings

**Google Style (recomendado):**
```python
def salvar_usuario(usuario: Usuario) -> int:
    """
    Salva um novo usuário no banco de dados.
    
    Esta função valida o usuário, criptografa a senha e persiste no BD.
    
    Args:
        usuario (Usuario): Objeto usuário com dados válidos
        
    Returns:
        int: ID do usuário recém criado
        
    Raises:
        ValueError: Se usuário inválido
        DatabaseError: Se erro no BD
        
    Example:
        >>> usuario = Usuario("João", "joao@example.com", "senha123")
        >>> id = salvar_usuario(usuario)
        >>> print(id)  # 1
    """
    pass
```

### Type Hints

```python
from typing import List, Optional, Dict, Tuple

# Variáveis
usuario_id: int = 1
nome: str = "João"
emails: List[str] = ["joao@example.com"]
dados: Dict[str, str] = {"nome": "João"}

# Funções
def buscar_usuario(usuario_id: int) -> Optional[Dict]:
    """Busca usuário por ID, retorna dict ou None"""
    pass

def buscar_multiplos(ids: List[int]) -> List[Dict]:
    """Busca múltiplos usuários"""
    pass

def dividir_nome(nome: str) -> Tuple[str, str]:
    """Retorna (nome, sobrenome)"""
    pass
```

### Imports

**Ordem recomendada:**
```python
# 1. Stdlib
import os
import sys
import json
from datetime import datetime
from typing import List, Optional

# 2. Third-party
from fastapi import FastAPI
from selenium import webdriver
import psycopg2

# 3. Local
from app.dao.usuario_dao import UsuarioDAO
from app.services.email_service import enviar_email
from app.utils.db import get_connection
```

**Remover imports não usados:**
```python
# ❌ Ruim
import os
import sys
import json

usuario = "João"
# sys e json não usados!

# ✅ Bom
import os

usuario = "João"
```

### Formatação

Use **Black** para formatação automática:

```bash
pip install black

# Formatar arquivo
black app/dao/usuario_dao.py

# Formatar tudo
black .

# Ver diferenças sem aplicar
black --check .
```

### Linting

Use **Flake8** para detectar erros:

```bash
pip install flake8

# Verificar arquivo
flake8 app/dao/usuario_dao.py

# Verificar tudo
flake8 .

# Ignorar algumas regras
flake8 . --ignore=E501,W503
```

### Exemplo: Código Bem Estruturado

```python
"""
app/dao/usuario_dao.py

Data Access Object para operações de usuário.
"""

from typing import Optional, Dict
from app.utils.db import get_connection


class UsuarioDAO:
    """Acesso aos dados de usuários no banco PostgreSQL."""
    
    def salvar(self, usuario) -> int:
        """
        Insere novo usuário no banco.
        
        Args:
            usuario: Objeto com nome, email, senha_hash, nivel_graduacao
            
        Returns:
            int: ID do usuário inserido
            
        Raises:
            Exception: Se erro na inserção
        """
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
            raise
            
        finally:
            if conn:
                conn.close()
    
    def buscar_por_email(self, email: str) -> Optional[Dict]:
        """
        Busca usuário por email.
        
        Args:
            email: Email do usuário
            
        Returns:
            Dict com dados do usuário ou None
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            sql = """
                SELECT id, nome, email, senha_hash, nivel_graduacao
                FROM usuario
                WHERE email = %s
            """
            
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

---

## 🤝 Como Contribuir

### 1. Fork e Branch

```bash
# 1. Fork no GitHub (clique em Fork)

# 2. Clone seu fork
git clone https://github.com/seu-usuario/PosEmFoco.git
cd PosEmFoco

# 3. Crie branch para sua feature
git checkout -b feature/nome-da-feature

# Exemplo:
git checkout -b feature/adicionar-dashboard
```

### 2. Desenvolvimento

```bash
# Faça suas alterações
# Teste localmente
pytest

# Verifique formatação
black . --check
flake8 .
```

### 3. Commit e Push

```bash
# Stage alterações
git add .

# Commit com mensagem descritiva
git commit -m "Adiciona dashboard com filtros

- Filtra editais por data
- Exibe gráfico de interesses
- Exporta para PDF"

# Push para seu fork
git push origin feature/adicionar-dashboard
```

### 4. Pull Request

- Vá ao GitHub
- Clique em "New Pull Request"
- Descreva as mudanças
- Aguarde review

### 5. Code Review

- Responda aos comentários
- Faça ajustes se necessário
- Após aprovação, será merged

---

## 🐛 Debugging

### Logs

```python
# Usar prints (desenvolvimento rápida)
print(f"[SCRAPER] Iniciando... usuario_id={usuario_id}")

# Ou melhor: usar logging (futuro)
import logging
logger = logging.getLogger(__name__)
logger.info(f"Iniciando scraper para usuário {usuario_id}")
```

### Breakpoints (VSCode)

```python
# Colocar breakpoint (F9 ou clique na linha)
def minha_funcao():
    usuario = buscar_usuario(1)
    # Pausa aqui ↓
    print(usuario)
    return usuario
```

Abra debug: Debug → Start Debugging (F5)

### Print Debug

```python
# Técnica simples mas eficaz
def extrair_editais(driver):
    elementos = driver.find_elements(...)
    print(f"DEBUG: {len(elementos)} elementos encontrados")
    
    for i, elem in enumerate(elementos):
        titulo = elem.text
        print(f"DEBUG [{i}]: {titulo}")
```

### PostMan (Testar API)

```
1. Baixe PostMan (https://www.postman.com/)
2. Crie requisição:
   - POST http://localhost:8000/cadastro
   - Headers: Content-Type: application/json
   - Body: {
       "nome": "Teste",
       "email": "teste@example.com",
       "senha": "senha123",
       "nivel_graduacao": "Mestrado",
       "interesses": ["IA"]
     }
3. Clique Send
4. Veja resposta
```

### VS Code Extensions Recomendadas

```
- Python
- Pylance
- Jupyter
- SQLTools (PostgreSQL)
- Thunder Client (alternativa PostMan)
- GitLens
```

---

## 🧪 Testes

### Estructura

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartilhadas
├── test_auth.py             # Testes de autenticação
├── test_dao.py              # Testes de DAO
└── test_scraper.py          # Testes de scraper
```

### Exemplo com pytest

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

@pytest.fixture
def usuario_teste():
    """Fixture que cria um usuário para testes"""
    return {
        "nome": "Teste User",
        "email": "teste@example.com",
        "senha": "senha123",
        "nivel_graduacao": "Mestrado",
        "interesses": ["Python"]
    }

def test_cadastro_sucesso(usuario_teste):
    """Testa cadastro bem-sucedido"""
    response = client.post("/cadastro", json=usuario_teste)
    assert response.status_code == 200
    assert "mensagem" in response.json()
    assert "id" in response.json()

def test_email_duplicado(usuario_teste):
    """Testa rejeição de email duplicado"""
    # Primeiro cadastro
    client.post("/cadastro", json=usuario_teste)
    
    # Segundo cadastro com mesmo email
    response = client.post("/cadastro", json=usuario_teste)
    assert response.status_code == 400
    assert "já cadastrado" in response.json()["detail"]

def test_login_sucesso(usuario_teste):
    """Testa login bem-sucedido"""
    # Cadastrar
    client.post("/cadastro", json=usuario_teste)
    
    # Login
    response = client.post("/login", json={
        "email": usuario_teste["email"],
        "senha": usuario_teste["senha"]
    })
    assert response.status_code == 200
    assert "usuario" in response.json()
```

### Executar Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_auth.py

# Com cobertura
pip install pytest-cov
pytest --cov=app

# Verbose
pytest -v

# Parar no primeiro erro
pytest -x
```

---

## 📊 Checklist para Pull Request

Antes de submeter PR:

- [ ] Código segue `black` (formatação)
- [ ] Código passa `flake8` (linting)
- [ ] Testes passam (`pytest`)
- [ ] Docstrings adicionadas
- [ ] Type hints presentes
- [ ] Sem imports não usados
- [ ] Sem print() (usar logging)
- [ ] Testado localmente
- [ ] Commit messages claros
- [ ] Documentação atualizada (se necessário)

---

## 🚀 Próximos Passos

- [Troubleshooting](../troubleshooting.md) - Resolver problemas
- [Deployment](../deployment.md) - Deploy em produção
- [Arquitetura](../arquitetura/visao-geral.md) - Entender design

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
