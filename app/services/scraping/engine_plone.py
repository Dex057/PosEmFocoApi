"""Motor para portais Plone (padrão de vários portais gov.br): lê a API REST `@search`.

A `url` da fonte é a busca com os filtros, por exemplo:
    https://www.ufac.br/@search?SearchableText=edital&sort_on=effective&sort_order=reverse
A resposta é JSON (`items` com `title` e `@id`); `batching.next` indica se há mais páginas.
"""
import requests

from app.services.scraping.engine_estatico import HEADERS, verificacao_ssl
from app.services.scraping.fontes import FonteEdital

POR_PAGINA = 50


def extrair_itens(dados: dict) -> list[tuple[str, str]]:
    itens = []
    for item in dados.get("items", []):
        titulo = (item.get("title") or "").strip()
        link = item.get("@id")
        if titulo and link:
            itens.append((titulo, link))
    return itens


def coletar(fonte: FonteEdital) -> list[tuple[str, str]]:
    itens: list[tuple[str, str]] = []
    for pagina in range(fonte.max_paginas):
        resp = requests.get(
            fonte.url,
            params={"b_size": POR_PAGINA, "b_start": pagina * POR_PAGINA},
            headers={**HEADERS, "Accept": "application/json"},
            timeout=20,
            verify=verificacao_ssl(fonte),
        )
        resp.raise_for_status()
        dados = resp.json()
        itens.extend(extrair_itens(dados))
        # Só usa `next` como sinal de que há mais páginas, não como URL: atrás de proxy o
        # Plone monta o endereço com o caminho interno (UFAC: /site/@search, que dá 404).
        if not (dados.get("batching") or {}).get("next"):
            break
    return itens
