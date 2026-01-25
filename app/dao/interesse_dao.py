from app.utils.db import get_connection

class InteresseDAO:
    def salvar_lista(self, usuario_id, lista_interesses):
        if not lista_interesses:
            return True

        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            sql = "INSERT INTO interesse (usuario_id, palavra_chave) VALUES (%s, %s)"
            
            dados = [(usuario_id, interesse.strip()) for interesse in lista_interesses]
            
            cursor.executemany(sql, dados)
            
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao salvar interesses: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()