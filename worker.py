import logging
import os
import time

from app.services.scraper import executar_scraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Worker] - %(message)s')
logger = logging.getLogger(__name__)

INTERVALO_SCRAPER_MINUTOS = int(os.getenv("INTERVALO_SCRAPER_MINUTOS", "60"))


def main():
    logger.info(f"Worker iniciado. Rodando o scraper a cada {INTERVALO_SCRAPER_MINUTOS} minuto(s).")
    while True:
        try:
            executar_scraper()
        except Exception as e:
            logger.error(f"Erro na rotina do scraper: {e}")
        time.sleep(INTERVALO_SCRAPER_MINUTOS * 60)


if __name__ == "__main__":
    main()
