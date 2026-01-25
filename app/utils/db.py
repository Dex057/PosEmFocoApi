import psycopg2
import os
import time  # <--- Biblioteca necessária para esperar
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    
    limit_attempts = 10
    
    for attempt in range(limit_attempts):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'), 
                port=os.getenv('DB_PORT'),
                cursor_factory=RealDictCursor
            )
            
            if attempt > 0:
                print("Conexão estabelecida com sucesso!")
            return conn

        except Exception as e:
            
            print(f"Tentativa {attempt + 1}/{limit_attempts} falhou. O banco ainda está indisponível.")
            print(f"   Erro: {e}")
            print("Aguardando...")
            time.sleep(2) 

    
    print("Erro Fatal: Não foi possível conectar ao PostgreSQL após várias tentativas.")
    return None