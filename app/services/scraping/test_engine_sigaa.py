"""Checagem rápida do parser do SIGAA (sem rede). Rodar: python -m app.services.scraping.test_engine_sigaa"""
from bs4 import BeautifulSoup

from app.services.scraping.engine_sigaa import extrair_itens

# Recorte real da listagem: um agrupador (processo seletivo) e os cursos dentro dele.
HTML_EXEMPLO = """
<table class="listagem">
  <thead><tr><th>Curso</th><th class="colVagas">Vagas</th></tr></thead>
  <tbody>
    <tr>
      <td class="agrupador" colspan="4"><b><span>PPGSA - PROCESSO SELETIVO TURMA 2027</span></b></td>
      <td class="agrupador"><a href="/sigaa/public/programa/portal.jsf?id=1864"><img/></a></td>
    </tr>
    <tr class="linhaPar">
      <td>DOUTORADO EM SOCIOLOGIA</td>
      <td class="colVagas">19</td>
      <td class="colData">15/09/2026 \n\t a 15/10/2026</td>
      <td><a href="#" onclick="jsfcljs(document.getElementById('form'),{'id':'79209'},'');">ver</a></td>
    </tr>
    <tr class="linhaImpar">
      <td>MESTRADO EM SOCIOLOGIA</td>
      <td class="colVagas">19</td>
      <td class="colData">15/09/2026 a 15/10/2026</td>
      <td><a href="#" onclick="jsfcljs(document.getElementById('form'),{'id':'79210'},'');">ver</a></td>
    </tr>
    <tr><td colspan="5">Nenhum outro processo</td></tr>
  </tbody>
</table>
"""


def demo():
    soup = BeautifulSoup(HTML_EXEMPLO, "html.parser")
    itens = extrair_itens(soup, "https://sigaa.ufpa.br/sigaa/public/processo_seletivo/lista.jsf")

    assert len(itens) == 2, f"esperava 2 cursos, veio {len(itens)}: {itens}"

    titulo, link = itens[0]
    assert titulo.startswith("DOUTORADO EM SOCIOLOGIA - PPGSA"), titulo
    assert "inscrições: 15/09/2026 a 15/10/2026" in titulo, titulo
    assert link == "https://sigaa.ufpa.br/sigaa/public/programa/portal.jsf?id=1864#ps79209", link

    # Mestrado e doutorado dividem o portal do programa: o id do processo é o que
    # mantém os links distintos (edital.link é UNIQUE no banco).
    assert itens[0][1] != itens[1][1], "links iguais fariam o segundo curso ser descartado"

    # Todos os níveis fora do ar precisa virar erro, não "0 processos abertos".
    from unittest import mock
    from app.services.scraping import engine_sigaa
    from app.services.scraping.fontes import FonteEdital
    fonte = FonteEdital(nome="t", universidade="U", url="https://sigaa.u.br/lista.jsf", engine="sigaa")
    with mock.patch.object(engine_sigaa.requests, "get", side_effect=ConnectionError("fora do ar")):
        try:
            engine_sigaa.coletar(fonte)
            raise AssertionError("falha em todos os níveis deveria propagar")
        except ConnectionError:
            pass

    print("OK: agrupa processo + curso, guarda o prazo, gera link único e não mascara portal fora do ar.")


if __name__ == "__main__":
    demo()
