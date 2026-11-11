# 🗄️ Camada DAO

Cada tabela tem um DAO em `app/dao/` com SQL puro via `psycopg2`. A conexão vem de
`app.utils.db.get_connection()`.

## Padrão de todos os métodos

```python
conn = get_connection()
try:
    cursor = conn.cursor()
    cursor.execute(sql, params)      # sempre parametrizado (%s), nunca f-string com dado do usuário
    conn.commit()                    # só nas escritas
    ...
except Exception as e:
    print(f"Erro ao ...: {e}")
    conn.rollback()                  # nas escritas
    return False / None / []         # o erro vira valor "vazio", não exceção
finally:
    conn.close()
```

Quem chama decide o que fazer com o retorno vazio. Em geral a rota responde 500.

## Métodos

### `UsuarioDAO` (`usuario_dao.py`)
| Método | Retorno |
|---|---|
| `salvar(usuario)` | `id` do novo usuário, ou `None`. Lê `nome`, `email`, `senha_hash` e `nivel_graduacao` do objeto |
| `buscar_por_email(email)` | linha (`dict`) ou `None` |

### `InteresseDAO` (`interesse_dao.py`)
| Método | Retorno |
|---|---|
| `listar_por_usuario(usuario_id)` | `list[str]` de palavras-chave |
| `substituir(usuario_id, lista)` | `True`/`False`. Apaga todos e insere a lista nova na mesma transação; lista vazia limpa tudo |

### `EditalDAO` (`edital_dao.py`)
| Método | Retorno |
|---|---|
| `salvar(edital: dict)` | `True` se era novo. Usa `ON CONFLICT (link) DO NOTHING`, então a deduplicação é atômica no banco |
| `listar_por_palavras(palavras)` | editais cujo **título** contém alguma palavra (`ILIKE '%p%'` com `OR`), mais novos primeiro |
| `listar_todos()` | todos, ordenados por `data_coleta DESC` |

### `SessaoDAO` (`sessao_dao.py`)
| Método | Retorno |
|---|---|
| `criar(token, usuario_id)` | `True`/`False` |
| `usuario_id_por_token(token)` | `id` ou `None` |
| `remover(token)` | `True`/`False` |

## Observações

- `listar_por_palavras` monta só os marcadores `%s` dinamicamente. Os valores continuam
  parametrizados, então não há SQL injection.
- O retorno de `salvar()` do `EditalDAO` é o que o scraper usa para saber se o edital é
  **novo** e só então notificar por e-mail.
- Há uma conexão por chamada, sem pool. Atende ao volume atual; um `psycopg2.pool` resolveria
  se virar gargalo.
