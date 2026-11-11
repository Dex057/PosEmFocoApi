# 🔐 Autenticação

O PósEmFoco usa **sessão por token opaco** guardado no Postgres. Não há JWT.

## Fluxo

```
1. POST /cadastro  {nome, email, senha, nivel_graduacao, interesses[]}
   └─ senha < 6 caracteres → 400; e-mail repetido → 400
   └─ senha vira hash bcrypt (passlib) antes de ir para a tabela usuario

2. POST /login  {email, senha}
   └─ confere o hash com bcrypt
   └─ gera token = secrets.token_urlsafe(32)
   └─ grava (token, usuario_id) na tabela sessao
   └─ responde {token, usuario: {id, nome, email, nivel_graduacao}}

3. Rotas privadas: header  Authorization: Bearer <token>
   └─ a dependência usuario_logado() busca o token em sessao
   └─ token ausente ou desconhecido → 401 "Sessão expirada. Faça login novamente."

4. POST /logout  (mesmo header)
   └─ apaga o token da tabela sessao
```

Por a sessão ficar no banco, e não na memória do processo, ela sobrevive a restart e vale
para qualquer instância da API atrás do mesmo Postgres.

## Rotas

| Rota | Autenticação |
|---|---|
| `GET /`, `GET /health` | pública |
| `POST /cadastro`, `POST /login`, `POST /logout` | pública |
| `GET /editais`, `POST /editais` | pública |
| `GET /me/editais` | token |
| `GET /me/interesses`, `PUT /me/interesses` | token |
| `POST /scraper/rodar` | token |

## Exemplo

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"aluno@exemplo.com","senha":"segredo123"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/me/editais
```

No front (`frontend/app.js`), a resposta do login fica em `localStorage['sessao']` e todo
`fetch` manda o header `Authorization`. Ao receber 401, o front limpa a sessão e volta ao login.

## Limitações conhecidas

- O token **não expira**: vale até o logout. A coluna `sessao.criado_em` já existe para um
  vencimento futuro (ex.: `DELETE FROM sessao WHERE criado_em < now() - interval '30 days'`).
- `POST /editais` é público. É usado para testes; em produção convém protegê-lo.
- Sem limite de tentativas no `/login`.
