"""Checagem do motor WordPress (sem rede). Rodar: python -m app.services.scraping.test_engine_wordpress"""
from unittest import mock

from app.services.scraping import engine_wordpress
from app.services.scraping.fontes import FonteEdital


def _resp(status, posts=None):
    r = mock.Mock(status_code=status)
    r.json.return_value = posts or []
    r.raise_for_status.side_effect = None if status < 400 else Exception(f"HTTP {status}")
    return r


def demo():
    itens = engine_wordpress.extrair_itens([
        {"title": {"rendered": "Mestrado em Direito &#8211; <em>2027</em>"}, "link": "https://u.br/a"},
        {"title": {"rendered": ""}, "link": "https://u.br/sem-titulo"},
        {"title": {"rendered": "Sem link"}},
    ])
    assert itens == [("Mestrado em Direito – 2027", "https://u.br/a")], itens

    fonte = FonteEdital(nome="t", universidade="U", url="https://u.br/wp-json/wp/v2/posts?search=edital",
                        engine="wordpress", max_paginas=5)
    cheia = [{"title": {"rendered": f"Edital {i}"}, "link": f"https://u.br/{i}"} for i in range(engine_wordpress.POR_PAGINA)]

    # Página cheia, depois 400 do WordPress (passou da última): para sem erro.
    with mock.patch.object(engine_wordpress.requests, "get", side_effect=[_resp(200, cheia), _resp(400)]) as get:
        assert len(engine_wordpress.coletar(fonte)) == engine_wordpress.POR_PAGINA
        assert get.call_count == 2

    # Página incompleta: nem pede a próxima.
    with mock.patch.object(engine_wordpress.requests, "get", side_effect=[_resp(200, cheia[:3])]) as get:
        assert len(engine_wordpress.coletar(fonte)) == 3
        assert get.call_count == 1

    # Erro na primeira página não pode ser engolido.
    with mock.patch.object(engine_wordpress.requests, "get", side_effect=[_resp(500)]):
        try:
            engine_wordpress.coletar(fonte)
            raise AssertionError("HTTP 500 deveria propagar")
        except Exception as e:
            assert "500" in str(e)

    print("OK: motor WordPress limpa HTML do título, pagina e para na última página.")


if __name__ == "__main__":
    demo()
