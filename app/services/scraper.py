import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.dao.edital_dao import EditalDAO
from app.utils.db import get_connection
from app.services.email_service import enviar_notificacao

# Configuração básica de logs para facilitar a leitura no Docker
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Scraper] - %(message)s')
logger = logging.getLogger(__name__)


def executar_scraper():
    logger.info("Iniciando a rotina do robô...")

    interesses_map = {}
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Busca interesses de todos os usuários
        query = """
                SELECT i.palavra_chave, u.email
                FROM interesse i
                         JOIN usuario u ON i.usuario_id = u.id \
                """
        cursor.execute(query)
        resultados = cursor.fetchall()
        for row in resultados:
            # Garante compatibilidade se o retorno for dict ou tupla
            if isinstance(row, dict):
                chave = row['palavra_chave'].lower()
                email = row['email']
            else:
                chave = row[0].lower()
                email = row[1]

            if chave not in interesses_map:
                interesses_map[chave] = []
            interesses_map[chave].append(email)
        cursor.close()
    except Exception as e:
        logger.error(f"Erro ao buscar interesses no banco: {e}")
        return
    finally:
        if conn: conn.close()

    palavras_chave = list(interesses_map.keys())
    if not palavras_chave:
        logger.info("Nenhum interesse cadastrado. Abortando execução.")
        return

    logger.info(f"Palavras-chave monitoradas: {palavras_chave}")

    # --- CONFIGURAÇÕES PARA DOCKER E HEADLESS ---
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = None
    edital_dao = EditalDAO()
    novos_encontrados = 0
    url_fonte = "https://ufpa.br/?post_type=editais"

    try:
        logger.info("Abrindo navegador (Modo Fantasma)...")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(60)

        logger.info(f"Acessando: {url_fonte}")
        driver.get(url_fonte)

        pagina_atual = 1
        max_paginas = 3

        while pagina_atual <= max_paginas:
            logger.info(f"--- Processando página {pagina_atual} ---")

            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "elementor-heading-title"))
                )
            except:
                logger.warning("Timeout: A página demorou muito ou está vazia.")
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")  # Volta pro topo por garantia
            time.sleep(1)

            elementos = driver.find_elements(By.CSS_SELECTOR, "h2.elementor-heading-title a")
            logger.info(f"Itens detectados na página: {len(elementos)}")

            for elemento in elementos:
                try:
                    titulo = elemento.text.strip()
                    link = elemento.get_attribute("href")

                    if not titulo: continue

                    for palavra in palavras_chave:
                        if palavra in titulo.lower():
                            logger.info(f"[MATCH ENCONTRADO] {titulo}")

                            dados_edital = {
                                "titulo": titulo,
                                "link": link,
                                "resumo": f"Contém: {palavra}",
                                "data_publicacao": None
                            }

                            salvou = edital_dao.salvar(dados_edital)

                            if salvou:
                                logger.info("   -> É novo! Salvando e enviando e-mails...")
                                novos_encontrados += 1
                                emails = interesses_map.get(palavra, [])
                                for email in emails:
                                    enviar_notificacao(email, titulo, link, palavra)
                            else:
                                logger.info("   -> Já estava no banco.")

                            break
                except Exception as e:
                    logger.error(f"Erro ao processar elemento individual: {e}")
                    continue

            try:
                botoes_proximo = driver.find_elements(By.CSS_SELECTOR, "a.next, a.page-numbers.next")
                if not botoes_proximo:
                    logger.info("Botão 'Próximo' não encontrado. Fim da paginação.")
                    break

                botao_proximo = botoes_proximo[0]

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_proximo)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", botao_proximo)

                logger.info("Carregando próxima página...")
                time.sleep(5)  # Espera a nova página carregar
                pagina_atual += 1

            except Exception as e:
                logger.error(f"Erro ao tentar mudar de página: {e}")
                break

    except Exception as error:
        logger.critical(f"Erro Crítico no Scraper: {error}")
    finally:
        if driver:
            driver.quit()
        logger.info(f"--- Scraper Finalizado. Total de novos editais: {novos_encontrados} ---")


if __name__ == "__main__":
    executar_scraper()