from app.utils.db import get_connection

class EditalDAO:
    def salvar(self, edital):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Verifica duplicidade pelo link
            sql_check = "SELECT id FROM edital WHERE link = %s"
            cursor.execute(sql_check, (edital['link'],))
            if cursor.fetchone():
                return False # Já existe

            sql = """
                INSERT INTO edital (titulo, link, resumo, data_publicacao) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                edital['titulo'],
                edital['link'],
                edital.get('resumo'),
                edital.get('data_publicacao')
            ))
            
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao salvar edital: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def listar_todos(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM edital ORDER BY data_publicacao DESC"
            cursor.execute(sql)
            editais = cursor.fetchall()
            cursor.close()
            return editais
        except Exception as e:
            print(f"Erro ao listar editais: {e}")
            return []
        finally:
            if conn:
                conn.close()