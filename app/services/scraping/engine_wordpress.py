"""Motor para portais WordPress: lê a API REST nativa (/wp-json/wp/v2/...) em vez do HTML.

JSON não quebra quando o tema do site muda, ao contrário de um seletor CSS. A `url` da
fonte é o endpoint com os filtros, por exemplo:
    https://www.unifap.br/wp-json/wp/v2/posts?search=edital
    https://www.ufopa.edu.br/wp-json/wp/v2/posts?categories=5,9
"""
import requests
from bs4 import BeautifulSoup

from app.services.scraping.engine_estatico import HEADERS, verificacao_ssl
from app.services.scraping.fontes import FonteEdital

POR_PAGINA = 50


def extrair_itens(posts: list[dict]) -> list[tuple[str, str]]:
    itens = []
    for post in posts:
        # O título vem como HTML ("&#8211;", às vezes <em>); get_text resolve os dois.
        titulo = BeautifulSoup(post.get("title", {}).get("rendered", ""), "html.parser").get_text(" ", strip=True)
        link = post.get("link")
        if titulo and link:
            itens.append((titulo, link))
    return itens


def coletar(fonte: FonteEdital) -> list[tuple[str, str]]:
    itens: list[tuple[str, str]] = []
    for pagina in range(1, fonte.max_paginas + 1):
        resp = requests.get(
            fonte.url,
            params={"per_page": POR_PAGINA, "page": pagina, "_fields": "title,link"},
            headers=HEADERS,
            timeout=20,
            verify=verificacao_ssl(fonte),
        )
        # Pedir página além da última devolve 400 (rest_post_invalid_page_number): acabou.
        if resp.status_code == 400 and pagina > 1:
            break
        resp.raise_for_status()
        posts = resp.json()
        itens.extend(extrair_itens(posts))
        if len(posts) < POR_PAGINA:
            break
    return itens
