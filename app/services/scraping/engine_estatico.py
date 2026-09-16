import logging
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.services.scraping.fontes import FonteEdital

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PosEmFocoBot/1.0)"}


def extrair_itens(
    soup: BeautifulSoup, url_base: str, seletor_item: str, link_da_pagina: bool = False
) -> list[tuple[str, str]]:
    itens = []
    for link in soup.select(seletor_item):
        titulo = link.get_text(" ", strip=True)
        if not titulo:
            continue

        if link_da_pagina:
            # Listagens que abrem o item por JavaScript (sem URL própria): guarda a página
            # da listagem, com um fragmento derivado do título só para o link ficar único.
            fragmento = re.sub(r"\W+", "-", titulo.lower()).strip("-")[:60]
            itens.append((titulo, f"{url_base}#{fragmento}"))
            continue

        href = link.get("href")
        if href and not href.lower().startswith("javascript:"):
            itens.append((titulo, urljoin(url_base, href)))
    return itens


def coletar(fonte: FonteEdital) -> list[tuple[str, str]]:
    itens: list[tuple[str, str]] = []
    url_atual = fonte.url
    pagina = 1

    while url_atual and pagina <= fonte.max_paginas:
        resp = requests.get(url_atual, headers=HEADERS, timeout=20, verify=fonte.verificar_ssl)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        itens.extend(extrair_itens(soup, url_atual, fonte.seletor_item, fonte.link_da_pagina))

        proximo = soup.select_one(fonte.seletor_next) if fonte.seletor_next else None
        href_proximo = proximo.get("href") if proximo else None
        url_atual = urljoin(url_atual, href_proximo) if href_proximo else None
        pagina += 1

    return itens
