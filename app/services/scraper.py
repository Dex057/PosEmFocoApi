import logging
import re

from app.dao.edital_dao import EditalDAO
from app.utils.db import get_connection
from app.services.email_service import enviar_notificacao
from app.services.scraping.fontes import FONTES
from app.services.scraping import engine_selenium, engine_estatico, engine_sigaa

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Scraper] - %(message)s')
logger = logging.getLogger(__name__)

ENGINES = {
    "selenium": engine_selenium.coletar,
    "estatico": engine_estatico.coletar,
    "sigaa": engine_sigaa.coletar,
}


def _buscar_interesses() -> dict:
    interesses_map: dict = {}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.palavra_chave, u.email
            FROM interesse i
            JOIN usuario u ON i.usuario_id = u.id
        """)
        for row in cursor.fetchall():
            if isinstance(row, dict):
                chave, email = row['palavra_chave'].lower(), row['email']
            else:
                chave, email = row[0].lower(), row[1]
            interesses_map.setdefault(chave, []).append(email)
        cursor.close()
    except Exception as e:
        logger.error(f"Erro ao buscar interesses no banco: {e}")
        return {}
    finally:
        if conn:
            conn.close()
    return interesses_map


def casa_palavra(palavra: str, titulo_lower: str) -> bool:
    """Casa a palavra-chave inteira, não pedaço de outra.

    Substring solta gera falso positivo em série: "ia" aparece dentro de "ciências",
    "ufpa" dentro de "propesp-ufpa", e o usuário recebe e-mail de tudo.

    Usa lookaround em vez de \\b porque \\b depende do tipo de caractere na ponta:
    "c++" termina em símbolo e nunca casaria.
    """
    return re.search(rf"(?<!\w){re.escape(palavra)}(?!\w)", titulo_lower) is not None


def _processar_itens(itens, palavras_chave, interesses_map, edital_dao, universidade) -> int:
    novos = 0
    for titulo, link in itens:
        titulo_lower = titulo.lower()
        for palavra in palavras_chave:
            if casa_palavra(palavra, titulo_lower):
                dados_edital = {
                    "titulo": titulo,
                    "link": link,
                    "resumo": f"[{universidade}] Contém: {palavra}",
                    "data_publicacao": None,
                }
                if edital_dao.salvar(dados_edital):
                    logger.info(f"[MATCH NOVO] ({universidade}) {titulo}")
                    novos += 1
                    for email in interesses_map.get(palavra, []):
                        enviar_notificacao(email, titulo, link, palavra, universidade)
                else:
                    logger.info(f"   -> Já estava no banco: {titulo}")
                break
    return novos


def executar_scraper():
    logger.info("Iniciando a rotina do robô...")

    interesses_map = _buscar_interesses()
    palavras_chave = list(interesses_map.keys())
    if not palavras_chave:
        logger.info("Nenhum interesse cadastrado. Abortando execução.")
        return

    logger.info(f"Palavras-chave monitoradas: {palavras_chave}")
    logger.info(f"Fontes configuradas: {[f.nome for f in FONTES]}")

    edital_dao = EditalDAO()
    total_novos = 0

    for fonte in FONTES:
        coletar = ENGINES.get(fonte.engine)
        if not coletar:
            logger.error(f"Engine '{fonte.engine}' desconhecida para a fonte '{fonte.nome}'.")
            continue

        logger.info(f"--- Coletando: {fonte.nome} ({fonte.engine}) ---")
        try:
            itens = coletar(fonte)
        except Exception as e:
            logger.error(f"Erro ao coletar '{fonte.nome}': {e}")
            continue

        logger.info(f"Itens coletados em '{fonte.nome}': {len(itens)}")
        total_novos += _processar_itens(itens, palavras_chave, interesses_map, edital_dao, fonte.universidade)

    logger.info(f"--- Scraper Finalizado. Total de novos editais: {total_novos} ---")


if __name__ == "__main__":
    executar_scraper()
