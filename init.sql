CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(200) NOT NULL,
    nivel_graduacao VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS interesse (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuario(id),
    palavra_chave VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS edital (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200),
    link TEXT,
    resumo TEXT,
    data_publicacao VARCHAR(50)
);