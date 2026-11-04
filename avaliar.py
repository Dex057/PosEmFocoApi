"""Gera as métricas do TCC: cobertura/tempo/falha por fonte e falsos positivos (substring x palavra inteira).

Rodar: python avaliar.py [--selenium]   (sem a flag, pula fontes que precisam de navegador)
Não toca no banco nem envia e-mail.
"""
import sys
import time

from app.services.scraper import ENGINES, casa_palavra
from app.services.scraping.fontes import FONTES

# Amostra de interesses plausíveis; as curtas ("ia", "ti") são o pior caso para substring.
PALAVRAS = ["ia", "ti", "social", "saúde", "computação", "engenharia", "educação",
            "enfermagem", "direito", "biologia", "física", "história", "doutorado", "mestrado"]


def main():
    com_selenium = "--selenium" in sys.argv
    titulos = {}  # link -> titulo (dedup entre fontes)
    print("| Fonte | Motor | Itens | Tempo (s) | Resultado |\n|---|---|---|---|---|")
    ok = falha = 0
    for f in FONTES:
        if f.engine == "selenium" and not com_selenium:
            print(f"| {f.nome} | {f.engine} | - | - | pulada (navegador) |")
            continue
        t0 = time.time()
        try:
            itens = ENGINES[f.engine](f)
            res = "ok" if itens else "0 itens (seletor/página)"
            ok += bool(itens); falha += not itens
            for t, l in itens:
                titulos[l] = t
        except Exception as e:
            itens, res = [], f"FALHOU: {type(e).__name__}"
            falha += 1
        print(f"| {f.nome} | {f.engine} | {len(itens)} | {time.time() - t0:.1f} | {res} |")

    print(f"\nFontes com sucesso: {ok}; com falha/vazias: {falha}; títulos únicos (por link): {len(titulos)}\n")

    baixos = [t.lower() for t in titulos.values()]
    print("| Palavra | Substring | Palavra inteira | Falsos positivos evitados |\n|---|---|---|---|")
    tot_sub = tot_int = 0
    for p in PALAVRAS:
        sub = sum(p in t for t in baixos)
        inteira = sum(casa_palavra(p, t) for t in baixos)
        tot_sub += sub; tot_int += inteira
        print(f"| {p} | {sub} | {inteira} | {sub - inteira} |")
    print(f"| **Total** | {tot_sub} | {tot_int} | {tot_sub - tot_int} |")


if __name__ == "__main__":
    main()
