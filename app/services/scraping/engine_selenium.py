import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.services.scraping.fontes import FonteEdital

logger = logging.getLogger(__name__)


def _criar_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def coletar(fonte: FonteEdital) -> list[tuple[str, str]]:
    itens: list[tuple[str, str]] = []
    driver = None

    try:
        driver = _criar_driver()
        driver.set_page_load_timeout(60)
        driver.get(fonte.url)

        pagina_atual = 1
        while pagina_atual <= fonte.max_paginas:
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, fonte.seletor_item))
                )
            except Exception:
                logger.warning(f"[{fonte.nome}] Timeout esperando itens na página {pagina_atual}.")
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            for elemento in driver.find_elements(By.CSS_SELECTOR, fonte.seletor_item):
                titulo = elemento.text.strip()
                link = elemento.get_attribute("href")
                if titulo and link:
                    itens.append((titulo, link))

            if not fonte.seletor_next:
                break

            botoes_proximo = driver.find_elements(By.CSS_SELECTOR, fonte.seletor_next)
            if not botoes_proximo:
                logger.info(f"[{fonte.nome}] Fim da paginação.")
                break

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botoes_proximo[0])
            time.sleep(1)
            driver.execute_script("arguments[0].click();", botoes_proximo[0])
            time.sleep(5)
            pagina_atual += 1

    except Exception as error:
        logger.critical(f"[{fonte.nome}] Erro crítico no Selenium: {error}")
    finally:
        if driver:
            driver.quit()

    return itens
