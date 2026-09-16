"""Checagem do casamento de palavra-chave. Rodar: python -m app.services.test_match"""
from app.services.scraper import casa_palavra


def demo():
    titulo = "mestrado em ciências sociais - processo seletivo turma 2027".lower()

    # O caso que motivou a função: "ia" está dentro de "ciências".
    assert not casa_palavra("ia", titulo), "'ia' não pode casar por estar dentro de 'ciências'"
    assert not casa_palavra("social", titulo), "'social' não pode casar dentro de 'sociais'"

    assert casa_palavra("mestrado", titulo)
    assert casa_palavra("ciências", titulo), "acento precisa funcionar"
    assert casa_palavra("processo seletivo", titulo), "interesse com mais de uma palavra"

    # Palavra-chave com caractere especial não pode virar regex.
    assert not casa_palavra("c++", titulo)
    assert casa_palavra("c++", "vaga para docente de c++ no campus")

    print("OK: casa palavra inteira, respeita acento e não quebra com regex na palavra-chave.")


if __name__ == "__main__":
    demo()
