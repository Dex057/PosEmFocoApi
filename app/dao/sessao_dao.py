from app.utils.db import get_connection

class SessaoDAO:
    def criar(self, token, usuario_id):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessao (token, usuario_id) VALUES (%s, %s)", (token, usuario_id)
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao criar sessão: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def usuario_id_por_token(self, token):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT usuario_id FROM sessao WHERE token = %s", (token,))
            linha = cursor.fetchone()
            cursor.close()
            if not linha:
                return None
            return linha['usuario_id'] if isinstance(linha, dict) else linha[0]
        except Exception as e:
            print(f"Erro ao buscar sessão: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def remover(self, token):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessao WHERE token = %s", (token,))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao remover sessão: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
