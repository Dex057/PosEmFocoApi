CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(200) NOT NULL,
    nivel_graduacao VARCHAR(50),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS interesse (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuario(id) ON DELETE CASCADE,
    palavra_chave VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS edital (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    link TEXT UNIQUE NOT NULL,
    resumo TEXT,
    data_publicacao VARCHAR(50),
    data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessões de login. Substitui o dicionário em memória: sobrevive a restart/deploy
-- e funciona com mais de um processo/worker da API por trás do mesmo Postgres.
CREATE TABLE IF NOT EXISTS sessao (
    token VARCHAR(64) PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
