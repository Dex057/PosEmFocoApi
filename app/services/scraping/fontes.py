from dataclasses import dataclass
from typing import Literal, Optional

Engine = Literal["estatico", "sigaa", "wordpress", "plone"]


@dataclass(frozen=True)
class FonteEdital:
    nome: str
    universidade: str
    url: str
    engine: Engine
    seletor_item: str = ""  # seletor CSS do <a> com título (texto) e link (href); "sigaa" não usa
    seletor_next: Optional[str] = None  # seletor do link/botão "próxima página"
    max_paginas: int = 3
    # Cadeia incompleta da RNP já é resolvida por intermediarios.pem (engine_estatico).
    # ponytail: desligar a verificação é a última saída, para um portal com outro defeito de
    # certificado; antes, prefira acrescentar o intermediário que falta em intermediarios.pem.
    verificar_ssl: bool = True
    # Listagens cujo item abre por JavaScript: guarda o link da própria listagem.
    link_da_pagina: bool = False


# Instituições públicas da Região Norte. Os seletores foram conferidos rodando
# `python -m app.services.scraping.fontes` (mostra quantos itens cada fonte devolve).
#
# Para adicionar uma nova instituição:
# 1. Abra a página de editais dela e identifique o seletor CSS do link de cada item
#    (e o do botão de "próxima página", se houver paginação).
# 2. Se o portal for WordPress, teste antes `https://<site>/wp-json/wp/v2/posts?search=edital`:
#    respondendo JSON, use engine="wordpress" com esse endpoint (não depende de seletor).
#    Portal Plone (padrão gov.br)? Teste `curl -H "Accept: application/json"
#    "https://<site>/@search?SearchableText=edital"`: respondendo JSON, use engine="plone".
# 3. Use engine="estatico" se a página for HTML puro (sem JavaScript renderizando a lista) —
#    é bem mais rápido e não depende de navegador.
# 4. Página que só monta a lista por JavaScript: abra o DevTools (aba Rede) e procure a
#    chamada que traz os dados (JSON/XHR); quase sempre dá para usá-la direto com "estatico"
#    ou "wordpress". Antes, confira com `curl -A "Mozilla/5.0"`: a UFPA parecia exigir
#    navegador e só barrava requisição sem User-Agent. Não há motor com navegador.
# 5. Rode o verificador acima: se vier 0 item, o seletor está errado ou a página mudou.
def _sigaa(universidade: str, host: str, **extra) -> "FonteEdital":
    """Lista pública de processos seletivos do SIGAA — mesma estrutura em toda IFES."""
    return FonteEdital(
        nome=f"{universidade} - Processos seletivos (SIGAA)",
        universidade=universidade,
        url=f"https://{host}/sigaa/public/processo_seletivo/lista.jsf?aba=p-processo",
        engine="sigaa",
        **extra,
    )


FONTES: list[FonteEdital] = [
    # --- SIGAA: processos seletivos de pós com curso, vagas e prazo de inscrição ---
    _sigaa("UFPA", "sigaa.ufpa.br"),
    _sigaa("UFRA", "sigaa.ufra.edu.br"),
    _sigaa("UFOPA", "sigaa.ufopa.edu.br"),
    _sigaa("UNIFESSPA", "sigaa.unifesspa.edu.br"),
    _sigaa("IFPA", "sigaa.ifpa.edu.br"),
    _sigaa("UNIFAP", "sigaa.unifap.br"),
    _sigaa("UEAP", "sigaa.ueap.edu.br"),  # hoje sem stricto aberto: lista vazia é legítima
    # --- Portais institucionais (editais que não passam pelo SIGAA) ---
    # --- Pará ---
    FonteEdital(
        nome="UFPA - Editais",
        universidade="UFPA",
        url="https://ufpa.br/?post_type=editais",
        engine="estatico",  # a lista vem no HTML; só exige User-Agent (sem ele, 403)
        seletor_item='h2.elementor-heading-title a[href*="/editais/"]',
        seletor_next="a.next, a.page-numbers.next",
        max_paginas=3,
    ),
    FonteEdital(
        nome="UFRA - Editais, programas e seleções",
        universidade="UFRA",
        url="https://novo.ufra.edu.br/index.php?option=com_content&view=category&id=83&Itemid=549",
        engine="estatico",
        seletor_item="h2.tileHeadline a",
    ),
    FonteEdital(
        nome="UNIFESSPA - Editais de pós-graduação",
        universidade="UNIFESSPA",
        url="https://editais.unifesspa.edu.br/taxonomy/term/25",
        engine="estatico",
        seletor_item="article.node-edital h2.title a",
        seletor_next="li.pager-next a, li.next a",
    ),
    FonteEdital(
        # A UEPA é estadual e não tem SIGAA. O sistema de seleções (SGPS) traz o nome
        # completo do processo, mas cada item abre por JavaScript, sem URL própria — daí
        # link_da_pagina: o usuário cai na listagem e acha o processo por lá.
        nome="UEPA - Sistema de seleções (SGPS)",
        universidade="UEPA",
        url="https://sistemas.uepa.br/sgps/selecao/",
        engine="estatico",
        seletor_item="a.css_nome_grid_line",
        link_da_pagina=True,
    ),
    FonteEdital(
        # A home ainda vale: traz editais divulgados como notícia, que não entram no SGPS.
        nome="UEPA - Destaques e editais",
        universidade="UEPA",
        url="https://www.uepa.br/",
        engine="estatico",
        seletor_item="div.card-body h5 a",
    ),
    # --- Amazonas ---
    FonteEdital(
        nome="UFAM - Editais",
        universidade="UFAM",
        url="https://ufam.edu.br/editais",
        engine="estatico",
        seletor_item="div.tileItem h3 a",
    ),
    # --- Tocantins ---
    FonteEdital(
        nome="UFT - Editais",
        universidade="UFT",
        url="https://www.uft.edu.br/editais",
        engine="estatico",
        seletor_item="a.listing-item-main-link",
    ),
    FonteEdital(
        nome="IFTO - Editais",
        universidade="IFTO",
        url="https://www.ifto.edu.br/editais",
        engine="estatico",
        seletor_item="div.collection-item h3 a",
    ),
    # --- WordPress (API REST nativa) ---
    FonteEdital(
        nome="UFOPA - Editais e processos seletivos",
        universidade="UFOPA",
        url="https://www.ufopa.edu.br/wp-json/wp/v2/posts?categories=5,9",  # Processo Seletivo, Editais e Concursos
        engine="wordpress",
        max_paginas=2,
    ),
    FonteEdital(
        nome="UNIFAP - Notícias de editais",
        universidade="UNIFAP",
        url="https://www.unifap.br/wp-json/wp/v2/posts?search=edital",  # só há categoria "notícias"
        engine="wordpress",
        max_paginas=2,
    ),
    FonteEdital(
        nome="UFRR - Notícias de editais",
        universidade="UFRR",
        url="https://ufrr.br/wp-json/wp/v2/posts?search=edital",  # só há categoria "notícias"
        engine="wordpress",
        max_paginas=2,
    ),
    FonteEdital(
        nome="UEA - Notícias de editais",
        universidade="UEA",
        url="https://uea.edu.br/wp-json/wp/v2/posts?search=edital",
        engine="wordpress",
        max_paginas=2,
    ),
    FonteEdital(
        nome="UERR - Notícias de editais",
        universidade="UERR",
        url="https://www.uerr.edu.br/wp-json/wp/v2/posts?search=edital",
        engine="wordpress",
        max_paginas=2,
    ),
    # --- Plone (API REST @search) ---
    FonteEdital(
        nome="UFAC - Editais e notícias",
        universidade="UFAC",
        url="https://www.ufac.br/@search?SearchableText=edital&sort_on=effective&sort_order=reverse",
        engine="plone",
        max_paginas=2,
    ),
    FonteEdital(
        nome="IFAC - Editais e notícias",
        universidade="IFAC",
        url="https://www.ifac.edu.br/@search?SearchableText=edital&sort_on=effective&sort_order=reverse",
        engine="plone",
        max_paginas=2,
    ),
]

# Instituições do Norte ainda sem fonte, e por quê:
#
# - IFAM (https://www2.ifam.edu.br/editais): a listagem é ótima (60+ itens), mas o portal
#   usa anti-bot Radware e devolve captcha depois de algumas requisições. Precisa de
#   navegador real e, mesmo assim, pode ser bloqueado.
# - UEPA (https://sistemas.uepa.br/sgps/selecao/): o sistema de seleções tem os melhores
#   títulos ("PROGRAMA DE PÓS-GRADUAÇÃO EM ENSINO DE MATEMÁTICA..."), mas os links são
#   `javascript:nm_gp_submit5(...)` — sem URL navegável para guardar no banco.
# - UNIR: tem SIGAA, mas a lista pública de processos seletivos redireciona para login.
# - IFAP, IFRO: portais Joomla, sem API nem feed funcionando; precisam de fonte "estatico"
#   com a página de editais e o seletor de cada um.
# - IFRR, UNITINS: sem API do WordPress/Plone nem busca acessível (404 / página de erro);
#   mesmo caso, fonte "estatico" com a URL certa de listagem.
# - IFPA: entra só pelo SIGAA (processos seletivos).


if __name__ == "__main__":
    # Verificação de rede: bate em cada fonte e mostra quantos itens saem.
    from app.services.scraper import ENGINES as coletores

    for fonte in FONTES:
        coletar = coletores.get(fonte.engine)
        if not coletar:
            print(f"{fonte.universidade:12} {fonte.engine:9} motor desconhecido")
            continue
        try:
            itens = coletar(fonte)
            exemplo = itens[0][0][:58] if itens else "—"
            print(f"{fonte.universidade:12} {fonte.engine:9} {len(itens):4} itens | {exemplo}")
        except Exception as e:
            print(f"{fonte.universidade:12} {fonte.engine:9} FALHOU: {type(e).__name__}: {str(e)[:60]}")
