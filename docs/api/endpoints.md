# 📡 Endpoints da API

Documentação técnica completa de todos os endpoints REST do PósEmFoco.

> ⚠️ **Desatualizado em parte.** A seção "API Endpoints" do [README](../../README.md) é a fonte da verdade.
> Mudanças recentes: `GET /` virou redirect para o front (status agora é `GET /health`), o login devolve um
> `token` de sessão em vez de disparar o scraper, `GET /usuarios/{id}/editais` virou `GET /me/editais`, e
> existem `GET|PUT /me/interesses` e `POST /scraper/rodar` — todos com `Authorization: Bearer <token>`.

## 🎯 Visão Geral

API segue padrão REST com:
- ✅ JSON como formato de dados
- ✅ HTTP status codes apropriados
- ✅ Validação com Pydantic
- ✅ CORS habilitado
- ✅ Documentação automática (Swagger)

**Base URL:** `http://localhost:8000`

**Documentação Interativa:** `http://localhost:8000/docs`

---

## 📋 Status & Health

### GET /

Status da API.

**Request:**
```bash
curl http://localhost:8000
```

**Response (200 OK):**
```json
{
  "mensagem": "API PósEmFoco rodando com PostgreSQL"
}
```

---

## 👤 Autenticação

### POST /cadastro

Registra novo usuário e seus interesses.

**Request:**
```bash
curl -X POST http://localhost:8000/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@example.com",
    "senha": "Aluno@2026Pos",
    "nivel_graduacao": "Mestrado",
    "interesses": ["Computação", "Inteligência Artificial", "Python"]
  }'
```

**Parâmetros:**

| Campo | Tipo | Obrigatório | Restrições |
|-------|------|-------------|-----------|
| `nome` | string | Sim | 3-100 caracteres |
| `email` | email | Sim | Formato válido, único |
| `senha` | string | Sim | Min 6 caracteres |
| `nivel_graduacao` | string | Sim | Mestrado, Doutorado, etc |
| `interesses` | array[string] | Não | 0-10 interesses |

**Response (200 OK) - Sucesso:**
```json
{
  "mensagem": "Usuário cadastrado com sucesso!",
  "id": 1
}
```

**Response (400 Bad Request) - Email duplicado:**
```json
{
  "detail": "E-mail já cadastrado."
}
```

**Response (422 Unprocessable Entity) - Validação falhou:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

**Python Example:**
```python
import requests

dados = {
    "nome": "João Silva",
    "email": "joao@example.com",
    "senha": "Aluno@2026Pos",
    "nivel_graduacao": "Mestrado",
    "interesses": ["Computação", "IA"]
}

response = requests.post(
    "http://localhost:8000/cadastro",
    json=dados
)

if response.status_code == 200:
    print(f"Cadastro bem-sucedido! ID: {response.json()['id']}")
else:
    print(f"Erro: {response.json()['detail']}")
```

---

### POST /login

Autentica usuário e inicia scraper em background.

**Request:**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "senha": "Aluno@2026Pos"
  }'
```

**Parâmetros:**

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| `email` | email | Sim |
| `senha` | string | Sim |

**Response (200 OK) - Sucesso:**
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

**Response (401 Unauthorized) - Credenciais inválidas:**
```json
{
  "detail": "Email ou senha incorretos"
}
```

**JavaScript Example:**
```javascript
async function fazer_login() {
    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: 'joao@example.com',
            senha: 'Aluno@2026Pos'
        })
    });
    
    if (response.ok) {
        const data = await response.json();
        console.log(`Bem-vindo, ${data.usuario.nome}!`);
        // Redirecionar para dashboard
    } else {
        const erro = await response.json();
        console.error(`Erro: ${erro.detail}`);
    }
}
```

---

## 📚 Editais

### GET /editais

Lista todos os editais no banco de dados.

**Request:**
```bash
curl http://localhost:8000/editais
```

**Query Parameters (Futuros):**
```
?page=1          # Paginação
?limit=10        # Itens por página
?sort=data       # Campo para ordenar
&order=desc      # desc ou asc
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "titulo": "Edital de Mestrado em Computação",
    "link": "https://ufpa.edu.br/edital-1",
    "resumo": "Seleção de candidatos para...",
    "data_publicacao": "2026-01-25T10:00:00",
    "data_criacao": "2026-01-25T14:30:00"
  },
  {
    "id": 2,
    "titulo": "Edital de Doutorado em Engenharia",
    "link": "https://ufpa.edu.br/edital-2",
    "resumo": "Processo de seleção...",
    "data_publicacao": "2026-01-24T09:00:00",
    "data_criacao": "2026-01-25T14:35:00"
  }
]
```

**Response (200 OK) - Lista vazia:**
```json
[]
```

**Python Example:**
```python
import requests

response = requests.get("http://localhost:8000/editais")
editais = response.json()

for edital in editais:
    print(f"📄 {edital['titulo']}")
    print(f"   Link: {edital['link']}")
    print(f"   Data: {edital['data_publicacao']}")
    print()
```

---

### POST /editais

Salva novo edital no banco (normalmente chamado pelo scraper).

**Request:**
```bash
curl -X POST http://localhost:8000/editais \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Edital de Mestrado em Computação",
    "link": "https://ufpa.edu.br/edital-novo",
    "resumo": "Seleção de candidatos para mestrado em computação",
    "data_publicacao": "2026-01-25"
  }'
```

**Parâmetros:**

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| `titulo` | string | Sim | Não pode ser duplicado com link |
| `link` | string | Sim | URL válida |
| `resumo` | string | Não | |
| `data_publicacao` | string | Não | Formato: YYYY-MM-DD |

**Response (200 OK) - Sucesso:**
```json
{
  "mensagem": "Edital salvo com sucesso"
}
```

**Response (200 OK) - Duplicado (não salva):**
```json
{
  "mensagem": "Edital não salvo (provavelmente duplicado)"
}
```

---

## 🔄 Fluxos Comuns

### Fluxo Completo: Cadastro → Login → Ver Editais

```bash
# 1. Cadastro
USUARIO_ID=$(curl -X POST http://localhost:8000/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria",
    "email": "maria@example.com",
    "senha": "senha123",
    "nivel_graduacao": "Mestrado",
    "interesses": ["Computação"]
  }' | jq '.id')

echo "Usuário criado com ID: $USUARIO_ID"

# 2. Login (inicia scraper)
LOGIN=$(curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "senha": "senha123"
  }')

echo "Login realizado para: $(echo $LOGIN | jq '.usuario.nome')"

# 3. Aguardar scraper executar (2-3 minutos)
sleep 120

# 4. Ver editais
curl http://localhost:8000/editais | jq '.[0]'
```

---

## ⚠️ Códigos de Status HTTP

| Código | Significado | Exemplo |
|--------|-------------|---------|
| **200** | OK | Requisição bem-sucedida |
| **201** | Created | Recurso criado (futuro) |
| **400** | Bad Request | Email duplicado, validação falhou |
| **401** | Unauthorized | Credenciais inválidas |
| **404** | Not Found | Recurso não existe (futuro) |
| **422** | Unprocessable Entity | Erro de validação Pydantic |
| **500** | Internal Server Error | Erro no servidor |

---

## 🔐 Segurança

### Validação de Input

Todos os inputs são validados com **Pydantic**:

```python
from pydantic import BaseModel, EmailStr

class LoginInput(BaseModel):
    email: EmailStr  # Valida formato de email automaticamente
    senha: str       # Tipo é verificado

# Se você enviar:
# {"email": "invalid", "senha": 123}
# Resposta:
# {"detail": [{"msg": "invalid email format"}]}
```

### Rate Limiting (Futuro)

Para proteger contra brute force:

```python
from slowapi import Limiter

@app.post("/login")
@limiter.limit("5/minute")  # Máx 5 tentativas por minuto
def login(...):
    pass
```

### HTTPS (Produção)

Em produção, sempre usar HTTPS:

```bash
# Será configurado com reverse proxy (nginx/apache)
https://posemfoco.exemplo.com/login
```

---

## 📚 Próximos Passos

- [Introdução à API](introducao.md) - Conceitos REST
- [Autenticação](autenticacao.md) - Mais sobre auth
- [Deployment](../deployment.md) - Colocar em produção

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
