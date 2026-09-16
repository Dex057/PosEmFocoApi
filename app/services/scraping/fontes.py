from dataclasses import dataclass
from typing import Literal, Optional

Engine = Literal["selenium", "estatico", "sigaa"]


@dataclass(frozen=True)
class FonteEdital:
    nome: str
    universidade: str
    url: str
    engine: Engine
    seletor_item: str = ""  # seletor CSS do <a> com título (texto) e link (href); "sigaa" não usa
    seletor_next: Optional[str] = None  # seletor do link/botão "próxima página"
    max_paginas: int = 3
    # ponytail: alguns portais .edu.br servem a cadeia de certificados incompleta e o
    # requests recusa. Desligar a verificação é aceitável aqui (página pública, sem login),
    # mas confia no conteúdo da rede: só use quando o site for realmente o culpado.
    verificar_ssl: bool = True
    # Listagens cujo item abre por JavaScript: guarda o link da própria listagem.
    link_da_pagina: bool = False


# Instituições públicas da Região Norte. Os seletores foram conferidos rodando
# `python -m app.services.scraping.fontes` (mostra quantos itens cada fonte devolve).
#
# Para adicionar uma nova instituição:
# 1. Abra a página de editais dela e identifique o seletor CSS do link de cada item
#    (e o do botão de "próxima página", se houver paginação).
# 2. Use engine="estatico" se a página for HTML puro (sem JavaScript renderizando a lista) —
#    é bem mais rápido e não depende de navegador.
# 3. Use engine="selenium" só se o conteúdo depender de JavaScript, como a UFPA abaixo.
# 4. Rode o verificador acima: se vier 0 item, o seletor está errado ou a página mudou.
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
    # --- Portais institucionais (editais que não passam pelo SIGAA) ---
    # --- Pará ---
    FonteEdital(
        nome="UFPA - Editais",
        universidade="UFPA",
        url="https://ufpa.br/?post_type=editais",
        engine="selenium",
        seletor_item="h2.elementor-heading-title a",
        seletor_next="a.next, a.page-numbers.next",
        max_paginas=3,
    ),
    FonteEdital(
        nome="UFRA - Editais, programas e seleções",
        universidade="UFRA",
        url="https://novo.ufra.edu.br/index.php?option=com_content&view=category&id=83&Itemid=549",
        engine="estatico",
        seletor_item="h2.tileHeadline a",
        verificar_ssl=False,  # servidor da UFRA não envia o certificado intermediário
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
        verificar_ssl=False,
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
]

# Instituições do Norte ainda sem fonte, e por quê:
#
# - IFAM (https://www2.ifam.edu.br/editais): a listagem é ótima (60+ itens), mas o portal
#   usa anti-bot Radware e devolve captcha depois de algumas requisições. Precisa de
#   Selenium e, mesmo assim, pode ser bloqueado.
# - UEPA (https://sistemas.uepa.br/sgps/selecao/): o sistema de seleções tem os melhores
#   títulos ("PROGRAMA DE PÓS-GRADUAÇÃO EM ENSINO DE MATEMÁTICA..."), mas os links são
#   `javascript:nm_gp_submit5(...)` — sem URL navegável para guardar no banco.
# - UFAC, UNIR, UFRR, UNIFAP, UFOPA, UEA, UERR, UEAP, UNITINS, IFPA, IFAP, IFAC, IFRO,
#   IFRR: não têm página única de listagem de editais em HTML puro (a lista vem por
#   JavaScript ou está espalhada por pró-reitoria). Cada uma precisa de uma fonte
#   "selenium" ou da URL certa de listagem.


if __name__ == "__main__":
    # Verificação de rede: bate em cada fonte e mostra quantos itens saem.
    from app.services.scraping import engine_estatico, engine_sigaa

    coletores = {"estatico": engine_estatico.coletar, "sigaa": engine_sigaa.coletar}

    for fonte in FONTES:
        coletar = coletores.get(fonte.engine)
        if not coletar:
            print(f"{fonte.universidade:12} {fonte.engine:9} pulado (precisa de navegador)")
            continue
        try:
            itens = coletar(fonte)
            exemplo = itens[0][0][:58] if itens else "—"
            print(f"{fonte.universidade:12} {fonte.engine:9} {len(itens):4} itens | {exemplo}")
        except Exception as e:
            print(f"{fonte.universidade:12} {fonte.engine:9} FALHOU: {type(e).__name__}: {str(e)[:60]}")
