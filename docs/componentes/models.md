# 📦 Models (estrutura de dados)

O projeto tem dois tipos de "model": as classes de domínio em `app/models/` e os schemas
Pydantic de entrada declarados em `server.py`.

## Classes de domínio (`app/models/`)

```python
# app/models/edital.py
@dataclass
class Edital:
    titulo: str
    link: str
    data_publicacao: Optional[datetime] = None
    resumo: Optional[str] = None

# app/models/usuario.py
class Usuario:
    def __init__(self, id=None, nome=None, email=None, senha_hash=None, nivel_graduacao=None): ...
```

São estruturas simples, sem validação. Os DAOs devolvem as linhas do banco como `dict`, e não
como instâncias dessas classes.

## Schemas de entrada da API (`server.py`)

O FastAPI usa estes schemas para validar o corpo das requisições (campo faltando ou de tipo
errado → 422):

| Schema | Campos | Usado em |
|---|---|---|
| `UsuarioInput` | `nome`, `email`, `senha`, `nivel_graduacao`, `interesses: List[str] = []` | `POST /cadastro` |
| `LoginInput` | `email`, `senha` | `POST /login` |
| `InteressesInput` | `interesses: List[str]` | `PUT /me/interesses` |
| `EditalInput` | `titulo`, `link`, `resumo?`, `data_publicacao?` | `POST /editais` |

Regras que ficam fora do schema, na própria rota:
- senha com pelo menos 6 caracteres e e-mail único (`/cadastro`);
- interesses com espaços nas pontas são aparados e os vazios descartados (`/me/interesses`).

Não há schemas de resposta: as rotas devolvem `dict`/listas diretamente.

## Tabelas (`init.sql`)

| Tabela | Colunas | Observação |
|---|---|---|
| `usuario` | `id`, `nome`, `email` (UNIQUE), `senha_hash`, `nivel_graduacao`, `data_cadastro` | |
| `interesse` | `id`, `usuario_id` → usuario, `palavra_chave` | `ON DELETE CASCADE` |
| `edital` | `id`, `titulo`, `link` (UNIQUE), `resumo`, `data_publicacao`, `data_coleta` | `link` único evita duplicatas |
| `sessao` | `token` (PK), `usuario_id` → usuario, `criado_em` | `ON DELETE CASCADE` |

`data_publicacao` é `VARCHAR`, porque cada portal escreve a data de um jeito. Para ordenar,
use `data_coleta`, que sempre está preenchida.
