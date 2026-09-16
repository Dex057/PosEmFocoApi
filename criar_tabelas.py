# -*- coding: utf-8 -*-
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

SQL_PATH = Path(__file__).parent / "init.sql"


def criar_tabelas():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
    )
    try:
        print("Conectando ao PostgreSQL...")
        with conn.cursor() as cur:
            cur.execute(SQL_PATH.read_text(encoding="utf-8"))
        conn.commit()
        print("Tabelas criadas/verificadas com sucesso!")
    finally:
        conn.close()


if __name__ == '__main__':
    criar_tabelas()
