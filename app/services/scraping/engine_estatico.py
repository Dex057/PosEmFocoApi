import logging
import re
import tempfile
from pathlib import Path
from urllib.parse import urljoin

import certifi
import requests
import urllib3.util.connection
from bs4 import BeautifulSoup

from app.services.scraping.fontes import FonteEdital

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PosEmFocoBot/1.0)"}

# ponytail: IPv4 apenas. O urllib3 tenta o IPv6 primeiro e não cai para o IPv4 antes do
# timeout (~21 s por requisição na UFRR, cujo IPv6 não responde). Todo portal tem IPv4.
# Vale para todo uso do requests no processo; desfaça se algum dia surgir fonte só IPv6.
urllib3.util.connection.HAS_IPV6 = False

# Vários portais .edu.br (UFRR, UFRA...) não enviam o certificado intermediário da RNP, e o
# requests recusa a conexão. Em vez de desligar a verificação, somamos esse intermediário
# (intermediarios.pem, conferido contra a raiz GlobalSign do certifi) às CAs padrão.
# Um arquivo por processo, para dois processos não escreverem o mesmo ao mesmo tempo.
with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False, encoding="utf-8") as _f:
    _f.write(Path(certifi.where()).read_text(encoding="utf-8"))
    _f.write(Path(__file__).with_name("intermediarios.pem").read_text(encoding="utf-8"))
CA_BUNDLE = _f.name


def verificacao_ssl(fonte: FonteEdital):
    return CA_BUNDLE if fonte.verificar_ssl else False


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
        resp = requests.get(url_atual, headers=HEADERS, timeout=20, verify=verificacao_ssl(fonte))
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        itens.extend(extrair_itens(soup, url_atual, fonte.seletor_item, fonte.link_da_pagina))

        proximo = soup.select_one(fonte.seletor_next) if fonte.seletor_next else None
        href_proximo = proximo.get("href") if proximo else None
        url_atual = urljoin(url_atual, href_proximo) if href_proximo else None
        pagina += 1

    return itens
