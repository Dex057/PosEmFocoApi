from app.utils.db import get_connection

class UsuarioDAO:
    def salvar(self, usuario):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            sql = "INSERT INTO usuario (nome, email, senha_hash, nivel_graduacao) VALUES (%s, %s, %s, %s) RETURNING id"
            
            cursor.execute(sql, (usuario.nome, usuario.email, usuario.senha_hash, usuario.nivel_graduacao))
            
            resultado = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            return resultado['id']
            
        except Exception as e:
            print(f"Erro ao salvar usuário: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def buscar_por_email(self, email):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            sql = "SELECT * FROM usuario WHERE email = %s"
            cursor.execute(sql, (email,))
            usuario = cursor.fetchone()
            cursor.close()
            return usuario
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
        finally:
            if conn:
                conn.close()