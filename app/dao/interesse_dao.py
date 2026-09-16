from app.utils.db import get_connection

class InteresseDAO:
    def listar_por_usuario(self, usuario_id):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT palavra_chave FROM interesse WHERE usuario_id = %s", (usuario_id,))
            linhas = cursor.fetchall()
            cursor.close()
            if not linhas:
                return []
            if isinstance(linhas[0], dict):
                return [linha['palavra_chave'] for linha in linhas]
            return [linha[0] for linha in linhas]
        except Exception as e:
            print(f"Erro ao listar interesses: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def substituir(self, usuario_id, lista_interesses):
        """Troca todos os interesses do usuário pela lista informada (lista vazia limpa tudo)."""
        conn = get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM interesse WHERE usuario_id = %s", (usuario_id,))

            dados = [(usuario_id, interesse.strip()) for interesse in lista_interesses if interesse.strip()]
            if dados:
                cursor.executemany(
                    "INSERT INTO interesse (usuario_id, palavra_chave) VALUES (%s, %s)", dados
                )

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