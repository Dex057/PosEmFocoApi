# 🔌 Introdução à API REST

Conceitos fundamentais da API do PósEmFoco.

## 📋 O que é uma API REST?

**API** = Application Programming Interface (Interface de Programação)

**REST** = Representational State Transfer

Em termos simples:
- Forma padronizada de sistemas se comunicarem
- Cliente → Servidor → Resposta
- Usa HTTP (mesma do navegador)

---

## 🔄 Requisição & Resposta

### Estrutura de uma Requisição

```
┌──────────────────────────────────┐
│  HTTP METHOD  /endpoint          │ ← Rota
├──────────────────────────────────┤
│ Content-Type: application/json   │ ← Headers
├──────────────────────────────────┤
│ {                                │
│   "email": "joao@example.com",   │ ← Body (dados)
│   "senha": "senha123"            │
│ }                                │
└──────────────────────────────────┘
```

### HTTP Methods (Verbos)

| Método | Significado | Exemplo |
|--------|-------------|----------|
| **GET** | Obter dados | `GET /editais` |
| **POST** | Criar/Enviar dados | `POST /cadastro` |
| **PUT** | Atualizar completo | `PUT /usuario/1` |
| **PATCH** | Atualizar parcial | `PATCH /usuario/1` |
| **DELETE** | Deletar | `DELETE /usuario/1` |

### Estrutura de uma Resposta

```
┌──────────────────────────────────┐
│ HTTP/1.1 200 OK                  │ ← Status
├──────────────────────────────────┤
│ Content-Type: application/json   │ ← Headers
│ Content-Length: 42               │
├──────────────────────────────────┤
│ {                                │
│   "mensagem": "Login sucesso",   │ ← Body (resposta)
│   "usuario": { ... }             │
│ }                                │
└──────────────────────────────────┘
```

---

## 📊 Status HTTP

### Classes

| Faixa | Significado | Exemplo |
|-------|-------------|----------|
| **2xx** | Sucesso | 200 OK, 201 Created |
| **3xx** | Redireção | 301 Moved, 304 Not Modified |
| **4xx** | Erro do cliente | 400 Bad Request, 401 Unauthorized |
| **5xx** | Erro do servidor | 500 Internal Server Error |

### Códigos Comuns

| Código | Significado |
|--------|-------------|n| `200` | Sucesso - Tudo OK |
| `201` | Criado - Recurso novo criado |
| `400` | Requisição inválida |
| `401` | Não autenticado (sem permissão) |
| `404` | Não encontrado |
| `422` | Validação falhou |
| `500` | Erro no servidor |

---

## 📤 Exemplo Prático

### 1. Fazer Login

**Requisição:**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@example.com", "senha": "senha123"}'
```

**Explicação:**
- `-X POST` - Método HTTP POST
- `http://localhost:8000/login` - URL do endpoint
- `-H "Content-Type: application/json"` - Tipo de dados
- `-d '{ ... }'` - Dados JSON

**Resposta (200 OK):**
```json
{
  "mensagem": "Login realizado com sucesso",
  "usuario": {
    "id": 1,
    "nome": "João",
    "email": "joao@example.com"
  }
}
```

### 2. Se Falhar (401 Unauthorized)

**Requisição (senha errada):**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@example.com", "senha": "errada"}'
```

**Resposta (401):**
```json
{
  "detail": "Email ou senha incorretos"
}
```

---

## 🛠️ Ferramentas para Testar

### 1. cURL (Terminal)

```bash
# GET
curl http://localhost:8000/editais

# POST
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "...", "senha": "..."}'
```

### 2. Postman (GUI)

Baixa em: https://www.postman.com/downloads/

1. Nova requisição
2. Selecione método (POST)
3. URL: `http://localhost:8000/login`
4. Tab "Body" → JSON
5. Coloque: `{"email": "...", "senha": "..."}`
6. Click "Send"

### 3. Swagger/OpenAPI (Web)

Acesse: http://localhost:8000/docs

Documentação interativa, pode testar direto!

---

## 📚 Conceitos

### Request Body

Dados enviados ao servidor:
```json
{
  "nome": "João",
  "email": "joao@example.com",
  "senha": "senha123"
}
```

### Response Body

Dados retornados pelo servidor:
```json
{
  "id": 1,
  "mensagem": "Sucesso!"
}
```

### Headers

Metadados da requisição:
```
Content-Type: application/json
Authorization: Bearer token123
User-Agent: PostMan
```

### Status Code

Tipo de resposta:
- `200` - OK
- `400` - Erro do cliente
- `500` - Erro do servidor

---

## 🔐 Autenticação

### Sem Autenticação (Público)
```bash
curl http://localhost:8000/  # Funciona
```

### Com Autenticação (token do /login)
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/me/editais
```

Detalhes em [autenticacao.md](autenticacao.md).

---

## 📚 Próximos Passos

- [Endpoints Completos](endpoints.md) - Documentação de cada endpoint
- [Autenticação](autenticacao.md) - Detalhes de segurança

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
"
