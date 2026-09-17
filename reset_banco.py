from app.utils.db import get_connection
from criar_tabelas import criar_tabelas  # mesma função usada em criar_tabelas.py, evita schema duplicado

def resetar_banco():
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        print(" Apagando tabelas existentes...")
      
        cursor.execute("DROP TABLE IF EXISTS sessao CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS interesse CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS usuario CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS edital CASCADE;")
        
        conn.commit()
        cursor.close()
        print("Tabelas apagadas com sucesso.")
        
        print("Recriando tabelas...")
        criar_tabelas() 
        
        print("zerado.")

    except Exception as e:
        print(f"Erro ao resetar banco: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    confirmacao = input("Isso vai APAGAR TODOS os dados. Tem certeza? (s/n): ")
    if confirmacao.lower() == 's':
        resetar_banco()
    else:
        print("Operação cancelada.")