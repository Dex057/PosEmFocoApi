# 🗄️ Modelo de Banco de Dados

Documentação completa do schema PostgreSQL do PósEmFoco.

## 📊 Diagrama ER (Entity-Relationship)

```
┌────────────────┐           ┌──────────────────┐
│    usuario     │ 1 ──────→ │    interesse     │
├────────────────┤ (1:N)     ├──────────────────┤
│ id (PK)        │           │ id (PK)          │
│ nome           │           │ usuario_id (FK)  │
│ email          │           │ palavra_chave    │
│ senha_hash     │           │ data_criacao     │
│ nivel_grad     │           └──────────────────┘
│ data_cadastro  │
└────────────────┘

Tabela: edital (sem relacionamento direto)
├─ id (PK)
├─ titulo
├─ link (UNIQUE)
├─ resumo
├─ data_publicacao
└─ data_criacao
```

---

## 📝 Tabelas Detalhadas

### 1. Tabela: `usuario`

Armazena informações dos usuários cadastrados.

**Schema SQL:**
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

**Colunas:**

| Campo | Tipo | Restrição | Descrição |
|-------|------|-----------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único, auto-incremento |
| `nome` | VARCHAR(100) | NOT NULL | Nome completo do usuário |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | Email único (chave para login) |
| `senha_hash` | VARCHAR(255) | NOT NULL | Hash bcrypt da senha (nunca plain text!) |
| `nivel_graduacao` | VARCHAR(50) | | Mestrado, Doutorado, Pós-doutorado, etc |
| `data_cadastro` | TIMESTAMP | DEFAULT now() | Quando o usuário se cadastrou |

**Índices Recomendados:**
```sql
CREATE INDEX idx_usuario_email ON usuario(email);
CREATE UNIQUE INDEX idx_usuario_email_unique ON usuario(email);
```

**Queries Comuns:**
```sql
-- Buscar por email
SELECT * FROM usuario WHERE email = 'joao@example.com';

-- Contar usuários
SELECT COUNT(*) FROM usuario;

-- Usuários por nível
SELECT nivel_graduacao, COUNT(*) 
FROM usuario 
GROUP BY nivel_graduacao;

-- Usuários cadastrados recentemente (últimos 7 dias)
SELECT * FROM usuario 
WHERE data_cadastro >= NOW() - INTERVAL '7 days'
ORDER BY data_cadastro DESC;
```

---

### 2. Tabela: `interesse`

Armazena as palavras-chave de interesse de cada usuário.

**Schema SQL:**
```sql
CREATE TABLE interesse (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    palavra_chave VARCHAR(100) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);
```

**Colunas:**

| Campo | Tipo | Restrição | Descrição |
|-------|------|-----------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `usuario_id` | INTEGER | FOREIGN KEY | Ref ao usuário dono |
| `palavra_chave` | VARCHAR(100) | NOT NULL | Ex: "Computação", "IA" |
| `data_criacao` | TIMESTAMP | DEFAULT now() | Quando foi criado |

**Índices Recomendados:**
```sql
CREATE INDEX idx_interesse_usuario ON interesse(usuario_id);
CREATE INDEX idx_interesse_palavra ON interesse(palavra_chave);
```

**Constraints Especiais:**
```sql
-- Evitar duplicatas (mesmo usuário não adiciona 2x mesma palavra)
CREATE UNIQUE INDEX idx_interesse_unico 
ON interesse(usuario_id, LOWER(palavra_chave));
```

**Queries Comuns:**
```sql
-- Interesses de um usuário
SELECT palavra_chave FROM interesse 
WHERE usuario_id = 1;

-- Usuários interessados em uma palavra
SELECT u.nome, u.email FROM usuario u
JOIN interesse i ON u.id = i.usuario_id
WHERE LOWER(i.palavra_chave) = 'computação';

-- Palavras mais comuns
SELECT palavra_chave, COUNT(*) as qtd
FROM interesse
GROUP BY palavra_chave
ORDER BY qtd DESC
LIMIT 10;

-- Deletar interesse
DELETE FROM interesse 
WHERE usuario_id = 1 AND palavra_chave = 'Python';

-- Atualizar interesses de um usuário
DELETE FROM interesse WHERE usuario_id = 1;
INSERT INTO interesse (usuario_id, palavra_chave) VALUES
(1, 'Computação'),
(1, 'IA'),
(1, 'Python');
```

**ON DELETE CASCADE:**
```
Quando um usuário é deletado, seus interesses são automaticamente deletados.
Isso mantém a integridade referencial.
```

---

### 3. Tabela: `edital`

Armazena os editais encontrados pelo scraper.

**Schema SQL:**
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

**Colunas:**

| Campo | Tipo | Restrição | Descrição |
|-------|------|-----------|-----------|
| `id` | SERIAL | PRIMARY KEY | Identificador único |
| `titulo` | VARCHAR(255) | NOT NULL | Título do edital |
| `link` | TEXT | NOT NULL | URL completa do edital |
| `resumo` | TEXT | | Descrição/resumo do edital |
| `data_publicacao` | TIMESTAMP | | Data do edital (nem sempre disponível) |
| `data_criacao` | TIMESTAMP | DEFAULT now() | Quando foi salvo no BD |

**Constraint UNIQUE:**
```
UNIQUE(titulo, link) garante que não salvamos editais duplicados.
Combinação título + link é praticamente única.
```

**Índices Recomendados:**
```sql
CREATE INDEX idx_edital_data ON edital(data_publicacao DESC);
CREATE INDEX idx_edital_link ON edital(link);
CREATE UNIQUE INDEX idx_edital_unico ON edital(titulo, link);
```

**Queries Comuns:**
```sql
-- Todos os editais
SELECT * FROM edital ORDER BY data_criacao DESC;

-- Editais recentes (últimos 7 dias)
SELECT * FROM edital 
WHERE data_criacao >= NOW() - INTERVAL '7 days'
ORDER BY data_criacao DESC;

-- Buscar edital específico
SELECT * FROM edital WHERE titulo ILIKE '%Computação%';

-- Contar editais por data
SELECT DATE(data_criacao) as data, COUNT(*) as qtd
FROM edital
GROUP BY DATE(data_criacao)
ORDER BY data DESC;

-- Verificar se edital existe (antes de inserir)
SELECT id FROM edital 
WHERE titulo = 'Edital de Mestrado' AND link = 'https://...';

-- Deletar editais antigos (mais de 1 ano)
DELETE FROM edital 
WHERE data_criacao < NOW() - INTERVAL '1 year';
```

---

## 🔗 Relacionamentos

### Usuario ↔ Interesse (1:N)

Um usuário pode ter múltiplos interesses.

```sql
-- Exemplo: Usuário 1 com seus interesses
SELECT u.nome, i.palavra_chave
FROM usuario u
JOIN interesse i ON u.id = i.usuario_id
WHERE u.id = 1;

-- Resultado:
-- | nome | palavra_chave |
-- |------|---------------|
-- | João | Computação    |
-- | João | IA            |
-- | João | Python        |
```

### Sem Relacionamento Direto: Usuario ↔ Edital

Os editais não têm referência direta aos usuários. O matching é feito em memória:

```python
# No código Python:
# 1. Buscar edital (título contém "Computação")
edital = {"titulo": "Mestrado em Computação", ...}

# 2. Buscar usuários interessados em "Computação"
usuarios = db.query("""
    SELECT DISTINCT u.id, u.email FROM usuario u
    JOIN interesse i ON u.id = i.usuario_id
    WHERE LOWER(i.palavra_chave) = 'computação'
""")

# 3. Enviar email para cada usuário
for usuario in usuarios:
    enviar_email(usuario.email, edital)
```

---

## 📈 Performance & Otimizações

### Índices Completos

```sql
-- Índices para melhor performance
CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_interesse_usuario ON interesse(usuario_id);
CREATE INDEX idx_interesse_palavra ON interesse(palavra_chave);
CREATE INDEX idx_edital_data ON edital(data_publicacao DESC);
CREATE INDEX idx_edital_link ON edital(link);

-- Índices únicos (validam unicidade)
CREATE UNIQUE INDEX idx_usuario_email_unique ON usuario(email);
CREATE UNIQUE INDEX idx_edital_unico ON edital(titulo, link);
```

### Query Optimization

**❌ Ruim:**
```sql
SELECT * FROM edital;  -- Retorna TUDO
```

**✅ Bom:**
```sql
SELECT id, titulo, link, data_criacao FROM edital
WHERE data_criacao >= NOW() - INTERVAL '7 days'
ORDER BY data_criacao DESC
LIMIT 50;
```

**Melhorias:**
- Selecionar apenas colunas necessárias
- Filtrar com WHERE
- Ordenar com índice
- Limitar resultados

### Connection Pooling

Em produção, usar pool de conexões:

```python
# Ao invés de criar conexão nova para cada query
conn = psycopg2.connect(...)  # Caro!

# Usar pool (implementar depois)
pool = ConnectionPool(min_size=5, max_size=20)
conn = pool.getConnection()
```

---

## 🔄 Transações & ACID

PostgreSQL garante ACID (Atomicity, Consistency, Isolation, Durability):

```python
# Exemplo de transação
try:
    cursor.execute("INSERT INTO usuario ...")
    cursor.execute("INSERT INTO interesse ...")
    conn.commit()  # Confirma tudo ou nada
except Exception as e:
    conn.rollback()  # Desfaz tudo se erro
    raise e
```

---

## 🔐 Segurança de Dados

### Backup Regular

```bash
# Backup completo
pg_dump -U posemfoco_user posemfoco > backup_$(date +%Y%m%d).sql

# Restaurar
psql -U posemfoco_user posemfoco < backup_20260125.sql

# Backup apenas estrutura
pg_dump -U posemfoco_user --schema-only posemfoco > schema.sql

# Backup com dados sensíveis excluídos
pg_dump -U posemfoco_user --exclude-table-data=usuario posemfoco > backup_sem_usuarios.sql
```

### Permissões

```sql
-- Usuário comum não pode deletar/alterar tudo
REVOKE ALL ON usuario FROM public;
GRANT SELECT ON usuario TO posemfoco_user;
GRANT INSERT ON usuario TO posemfoco_user;

-- Apenas para admin
GRANT ALL ON usuario TO admin_user;
```

### Criptografia

- ✅ Senhas: bcrypt
- ❓ Email: não criptografado (necessário buscar)
- ❓ Tokens: seria bom adicionar JWT

---

## 📊 Estatísticas e Monitoramento

```sql
-- Tamanho do banco
SELECT pg_size_pretty(pg_database_size('posemfoco'));

-- Tamanho de cada tabela
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Usuários ativos (login no último mês)
SELECT COUNT(*) FROM usuario
WHERE data_cadastro >= NOW() - INTERVAL '30 days';

-- Editais por mês
SELECT 
    DATE_TRUNC('month', data_criacao)::DATE as mes,
    COUNT(*) as qtd
FROM edital
GROUP BY DATE_TRUNC('month', data_criacao)
ORDER BY mes DESC;
```

---

## 🛠️ Manutenção

### Vacuum (Cleanup)

Libera espaço e otimiza:
```sql
VACUUM ANALYZE;  -- Recomendado executar 1x por semana
```

### Reset Banco (Apenas DEV!)

```bash
# Deletar banco
dropdb -U postgres posemfoco

# Recrear
createdb -U postgres posemfoco -O posemfoco_user

# Recriar tabelas
python criar_tabelas.py
```

---

## 📚 Próximos Passos

- [Fluxo de Autenticação](fluxo-autenticacao.md)
- [Fluxo de Scraping](fluxo-scraping.md)
- [API Endpoints](../api/endpoints.md)

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
