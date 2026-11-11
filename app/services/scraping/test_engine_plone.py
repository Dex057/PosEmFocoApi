"""Checagem do motor Plone (sem rede). Rodar: python -m app.services.scraping.test_engine_plone"""
from unittest import mock

from app.services.scraping import engine_plone
from app.services.scraping.fontes import FonteEdital


def _resp(dados, status=200):
    r = mock.Mock(status_code=status)
    r.json.return_value = dados
    r.raise_for_status.side_effect = None if status < 400 else Exception(f"HTTP {status}")
    return r


def demo():
    itens = engine_plone.extrair_itens({"items": [
        {"title": " Mestrado em Educação ", "@id": "https://u.br/a"},
        {"title": "", "@id": "https://u.br/sem-titulo"},
        {"title": "Sem link"},
    ]})
    assert itens == [("Mestrado em Educação", "https://u.br/a")], itens

    fonte = FonteEdital(nome="t", universidade="U", url="https://u.br/@search?SearchableText=edital",
                        engine="plone", max_paginas=5)
    p1 = {"items": [{"title": "A", "@id": "https://u.br/1"}], "batching": {"next": "https://u.br/site/@search?b_start=50"}}
    p2 = {"items": [{"title": "B", "@id": "https://u.br/2"}], "batching": {"next": None}}

    # Pagina pela URL da fonte com b_start (o `next` do Plone pode vir com caminho interno
    # quebrado, como /site/ na UFAC) e para quando não há próxima página.
    with mock.patch.object(engine_plone.requests, "get", side_effect=[_resp(p1), _resp(p2)]) as get:
        assert engine_plone.coletar(fonte) == [("A", "https://u.br/1"), ("B", "https://u.br/2")]
        assert get.call_args_list[1].args[0] == fonte.url, "não pode seguir a URL do next"
        assert get.call_args_list[1].kwargs["params"]["b_start"] == engine_plone.POR_PAGINA
        assert get.call_args_list[0].kwargs["headers"]["Accept"] == "application/json"

    # Respeita max_paginas mesmo com next.
    fonte1 = FonteEdital(nome="t", universidade="U", url=fonte.url, engine="plone", max_paginas=1)
    with mock.patch.object(engine_plone.requests, "get", side_effect=[_resp(p1)]) as get:
        assert len(engine_plone.coletar(fonte1)) == 1 and get.call_count == 1

    # Erro HTTP não pode ser engolido.
    with mock.patch.object(engine_plone.requests, "get", side_effect=[_resp({}, 500)]):
        try:
            engine_plone.coletar(fonte)
            raise AssertionError("HTTP 500 deveria propagar")
        except Exception as e:
            assert "500" in str(e)

    print("OK: motor Plone pede JSON, pagina por b_start, respeita max_paginas e propaga erro.")


if __name__ == "__main__":
    demo()
