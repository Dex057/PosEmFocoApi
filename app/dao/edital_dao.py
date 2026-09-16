from app.utils.db import get_connection

class EditalDAO:
    def salvar(self, edital):
        conn = get_connection()
        try:
            cursor = conn.cursor()

            # UNIQUE(link) no banco garante atomicidade (sem race condition entre check e insert)
            sql = """
                INSERT INTO edital (titulo, link, resumo, data_publicacao)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """
            cursor.execute(sql, (
                edital['titulo'],
                edital['link'],
                edital.get('resumo'),
                edital.get('data_publicacao')
            ))

            era_novo = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            return era_novo
        except Exception as e:
            print(f"Erro ao salvar edital: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def listar_por_palavras(self, palavras):
        if not palavras:
            return []
        conn = get_connection()
        try:
            cursor = conn.cursor()
            condicoes = " OR ".join(["titulo ILIKE %s"] * len(palavras))
            sql = f"SELECT * FROM edital WHERE {condicoes} ORDER BY id DESC"
            cursor.execute(sql, [f"%{palavra}%" for palavra in palavras])
            editais = cursor.fetchall()
            cursor.close()
            return editais
        except Exception as e:
            print(f"Erro ao listar editais por palavras: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def listar_todos(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # data_publicacao costuma vir vazia do scraper; data_coleta sempre existe
            sql = "SELECT * FROM edital ORDER BY data_coleta DESC"
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