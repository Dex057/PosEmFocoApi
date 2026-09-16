"""Checagem rápida do parser estático (sem rede). Rodar: python -m app.services.scraping.test_engine_estatico"""
from bs4 import BeautifulSoup

from app.services.scraping.engine_estatico import extrair_itens

HTML_EXEMPLO = """
<div class="lista">
    <a class="edital" href="/edital-1">Mestrado em Computação</a>
    <a class="edital" href="https://outro-dominio.br/edital-2">Doutorado em Educação</a>
    <a class="edital" href="">Sem link</a>
    <a class="edital"></a>
</div>
"""


def demo():
    soup = BeautifulSoup(HTML_EXEMPLO, "html.parser")
    itens = extrair_itens(soup, "https://universidade.br/editais", "a.edital")

    assert len(itens) == 2, f"esperava 2 itens válidos, veio {len(itens)}"
    assert itens[0] == ("Mestrado em Computação", "https://universidade.br/edital-1")
    assert itens[1] == ("Doutorado em Educação", "https://outro-dominio.br/edital-2")
    print("OK: extrair_itens resolve links relativos e ignora itens sem título/href.")


if __name__ == "__main__":
    demo()
