"""Coleta a lista pública de processos seletivos do SIGAA.

Quase toda IFES usa SIGAA e expõe /sigaa/public/processo_seletivo/lista.jsf sem login.
É melhor fonte que raspar notícia do portal: sai o nome do curso, o número de vagas e o
período de inscrição, em HTML puro e com o mesmo layout em todas as instituições.

A página é uma tabela onde `td.agrupador` é o processo seletivo (com link para o portal
do programa) e as linhas seguintes são os cursos daquele processo.
"""
import logging
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.services.scraping.fontes import FonteEdital

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PosEmFocoBot/1.0)"}

# Níveis do filtro da própria página: stricto sensu, especialização e lato sensu.
NIVEIS = ("S", "E", "L")

# O link de "visualizar processo" é um submit JSF; o id do processo vem no onclick e é o
# que garante um link único por curso (mestrado e doutorado do mesmo programa dividem o
# mesmo portal, e `edital.link` é UNIQUE no banco).
ID_PROCESSO = re.compile(r"'id':'(\d+)'")


def extrair_itens(soup: BeautifulSoup, url_base: str) -> list[tuple[str, str]]:
    itens: list[tuple[str, str]] = []
    processo = ""
    link_programa = url_base

    for linha in soup.select("table.listagem tr"):
        agrupador = linha.select_one("td.agrupador")
        if agrupador:
            rotulo = linha.select_one("td.agrupador span") or agrupador
            processo = rotulo.get_text(" ", strip=True)
            ancora = linha.select_one("td.agrupador a[href]")
            href = ancora["href"] if ancora else None
            link_programa = urljoin(url_base, href) if href and href != "#" else url_base
            continue

        celula_curso = linha.find("td")
        if not celula_curso or not linha.select_one("td.colVagas"):
            continue  # cabeçalho, rodapé ou linha de paginação

        curso = celula_curso.get_text(" ", strip=True)
        if not curso:
            continue

        celula_periodo = linha.select_one("td.colData")
        periodo = " ".join(celula_periodo.get_text(" ", strip=True).split()) if celula_periodo else ""

        titulo = f"{curso} - {processo}" if processo else curso
        if periodo:
            titulo = f"{titulo} (inscrições: {periodo})"

        achado = ID_PROCESSO.search(str(linha))
        sufixo = achado.group(1) if achado else curso.lower().replace(" ", "-")[:40]
        itens.append((titulo, f"{link_programa}#ps{sufixo}"))

    return itens


def coletar(fonte: FonteEdital) -> list[tuple[str, str]]:
    itens: list[tuple[str, str]] = []

    for nivel in NIVEIS:
        separador = "&" if "?" in fonte.url else "?"
        url = f"{fonte.url}{separador}nivel={nivel}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30, verify=fonte.verificar_ssl)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"SIGAA {fonte.universidade} nível {nivel} falhou: {e}")
            continue

        itens.extend(extrair_itens(BeautifulSoup(resp.text, "html.parser"), url))

    return itens
