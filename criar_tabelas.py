# -*- coding: utf-8 -*-
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv(encoding="utf-8")

def resetar_tabelas():
    
    db_config = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }

    commands = (
        
        "DROP TABLE IF EXISTS interesse CASCADE;",
        "DROP TABLE IF EXISTS edital CASCADE;",
        "DROP TABLE IF EXISTS usuario CASCADE;",
        
    
        """
        CREATE TABLE usuario (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            senha_hash VARCHAR(255) NOT NULL,
            nivel_graduacao VARCHAR(50),
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE interesse (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            palavra_chave VARCHAR(50) NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE edital (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255) NOT NULL,
            link TEXT NOT NULL,
            resumo TEXT,
            data_publicacao TIMESTAMP,
            data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn = None
    try:
        print("Conectando ao PostgreSQL...")
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        print("Reiniciando tabelas (DROP & CREATE)...")
        for command in commands:
            cur.execute(command)
        
        cur.close()
        conn.commit()
        print("Tabelas criadas/verificadas com sucesso!")
    except Exception:
        print("Erro ao criar tabelas:")
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    resetar_tabelas()