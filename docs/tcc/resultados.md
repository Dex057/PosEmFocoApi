# Resultados medidos (base para as perguntas 3 e 4 da pesquisa)

Gerado por `python avaliar.py` em 11/11/2026, rede real, sem tocar no banco nem enviar e-mail.
Para repetir: `python avaliar.py`.

## Cobertura e confiabilidade por fonte (pergunta 4)

| Fonte | Motor | Itens | Tempo (s) | Resultado |
|---|---|---|---|---|
| UFPA - Processos seletivos (SIGAA) | sigaa | 111 | 2,0 | ok |
| UFRA - Processos seletivos (SIGAA) | sigaa | 4 | 2,2 | ok |
| UFOPA - Processos seletivos (SIGAA) | sigaa | 30 | 2,9 | ok |
| UNIFESSPA - Processos seletivos (SIGAA) | sigaa | 19 | 2,2 | ok |
| IFPA - Processos seletivos (SIGAA) | sigaa | 2 | 1,3 | ok |
| UNIFAP - Processos seletivos (SIGAA) | sigaa | 25 | 2,8 | ok |
| UEAP - Processos seletivos (SIGAA) | sigaa | 0 | 2,6 | vazia legítima* |
| UFPA - Editais | estático | 30 | 4,5 | ok |
| UFRA - Editais, programas e seleções | estático | 10 | 0,8 | ok |
| UNIFESSPA - Editais de pós-graduação | estático | 30 | 1,8 | ok |
| UEPA - Sistema de seleções (SGPS) | estático | 76 | 0,7 | ok |
| UEPA - Destaques e editais | estático | 6 | 1,0 | ok |
| UFAM - Editais | estático | 24 | 1,1 | ok |
| UFT - Editais | estático | 5 | 0,9 | ok |
| IFTO - Editais | estático | 14 | 0,5 | ok |
| UFOPA - Editais e processos seletivos | wordpress | 100 | 1,1 | ok |
| UNIFAP - Notícias de editais | wordpress | 100 | 1,7 | ok |
| UFRR - Notícias de editais | wordpress | 100 | 3,0 | ok |
| UEA - Notícias de editais | wordpress | 100 | 2,1 | ok |
| UERR - Notícias de editais | wordpress | 100 | 4,0 | ok |
| UFAC - Editais e notícias | plone | 100 | 1,6 | ok |
| IFAC - Editais e notícias | plone | 100 | 1,1 | ok |

\* O SIGAA da UEAP respondeu normalmente com a página de processos stricto sensu, sem nenhum
aberto no momento. Como o motor agora levanta erro quando a conexão falha, "vazia" aqui é
resposta real do portal, não falha escondida (ver item 1 abaixo).

- 22 fontes de 16 instituições: 21 com itens, 1 vazia legítima, nenhuma falha.
- 1054 títulos únicos (deduplicados por link) em uma rodada, em cerca de 42 s no total.
- As fontes WordPress e Plone devolvem até 100 itens cada porque o limite é de 2 páginas de 50;
  o filtro por interesse vem depois.
- Instituições públicas do Norte ainda de fora: IFAM (anti-bot), UNIR (lista do SIGAA exige
  login), IFAP e IFRO (Joomla sem API) e IFRR e UNITINS (sem API nem busca acessível).

### O que mudou em relação à rodada de 04/11/2026 (13 fontes, 10 instituições, 313 títulos)

Vale registrar no TCC, porque cada item é um achado sobre coleta automatizada:

1. **Falha mascarada como "vazio".** A rodada anterior registrou o SIGAA da UFRA como
   "vazio legítimo". Na verdade a conexão falhava por certificado: o servidor não envia o
   certificado intermediário da RNP (*RNP ICPEdu GR46 OV TLS CA 2025*), e o motor SIGAA
   tratava a falha de todos os níveis como lista vazia. Corrigido: falha total agora vira erro, e
   a UFRA devolveu 4 processos. Lição para a pergunta 4: "0 itens" e "falhou" precisam ser
   distinguidos, senão a taxa de sucesso fica inflada.
2. **Certificados incompletos resolvidos sem desligar a verificação.** UFRR, UFRA e UEPA têm
   o mesmo defeito de cadeia. Em vez de `verify=False`, o projeto passou a incluir o
   intermediário (`app/services/scraping/intermediarios.pem`, conferido contra a raiz
   GlobalSign) junto às CAs padrão.
3. **IPv6 quebrado custava 20 s por requisição.** A UFRR (e a UEPA/SGPS, antes 20,7 s, agora
   0,8 s) anuncia IPv6 que não responde, e o cliente HTTP espera o timeout antes de usar o IPv4.
   A coleta passou a usar só IPv4.
4. **A UFPA - Editais não precisava de navegador.** A página já entrega a lista em HTML; só
   recusava (HTTP 403) requisições sem User-Agent. Passou do Selenium para o motor estático.
   Com isso, nenhuma fonte usava mais o Selenium, e o motor foi removido (com o Chromium da
   imagem Docker). Página que monta a lista por JavaScript costuma buscar os dados numa chamada
   interna (XHR/JSON), que dá para usar direto.
5. **Novo motor WordPress.** Lê a API REST nativa (`/wp-json/wp/v2/posts`) em vez do HTML, sem
   seletor CSS que quebra quando o tema muda. Incluiu a UFRR (antes sem fonte) e os portais
   da UNIFAP e da UFOPA, e depois UEA e UERR. Isso reforça a pergunta 2: o motor entrou sem
   alterar o núcleo do sistema.
6. **Novo motor Plone.** Vários portais gov.br usam Plone, que expõe a API REST `@search` em JSON.
   Incluiu UFAC e IFAC, antes sem fonte. Achado: o link de "próxima página" que o Plone da UFAC
   devolve vem com o caminho interno do servidor (`/site/@search`) e dá 404. Por isso o motor pagina
   pela URL configurada (`b_start`) e usa o `next` só como sinal de que há mais páginas.
7. **SIGAA da UEAP.** Entrou com uma linha (`_sigaa("UEAP", ...)`), mesmo layout das IFES.

## Palavra inteira x substring (pergunta 3)

Sobre os 1054 títulos coletados, com 14 palavras-chave de amostra (escolhidas por mim como interesses
plausíveis de candidatos; não é amostra de usuários reais):

| Palavra | Substring | Palavra inteira | Falsos positivos evitados |
|---|---|---|---|
| ia | 513 | 0 | 513 |
| ti | 402 | 0 | 402 |
| social | 4 | 4 | 0 |
| saúde | 23 | 23 | 0 |
| computação | 9 | 9 | 0 |
| engenharia | 20 | 20 | 0 |
| educação | 55 | 55 | 0 |
| enfermagem | 16 | 16 | 0 |
| direito | 17 | 13 | 4 |
| biologia | 7 | 7 | 0 |
| física | 10 | 9 | 1 |
| história | 11 | 11 | 0 |
| doutorado | 101 | 101 | 0 |
| mestrado | 279 | 279 | 0 |
| **Total** | 1467 | 547 | 920 |

Leitura honesta dos números:

- A busca por substring geraria 1467 correspondências; a por palavra inteira, 547. Ou seja, 920
  (62,7%) das correspondências por substring seriam falsos positivos.
- Quase todo o ganho vem das palavras curtas: "ia" casaria dentro de "Amazônia" (56 vezes),
  "ciências" (50) e "especialização" (29); "ti" casaria dentro de "seletivo" (168), "vestibular" (47) e
  "matemática" (17). Nas palavras longas a diferença foi zero ou pequena ("direito": 4;
  "física": 1).
- Consequência: a palavra inteira é essencial para siglas e termos curtos, mas tem um custo.
  "IA" como palavra isolada não apareceu em nenhum título (e "inteligência artificial" aparece 1
  vez), então hoje um usuário com o interesse "ia" não receberia nada. Isso vira ponto de
  melhoria: sinônimos/expansão de siglas.
- A palavra inteira não resolve variação de flexão: "social" não casa com "sociais" (2 títulos).
  Dá para tratar com radical (stemming), mas aumentaria o risco de falso positivo. É decisão de projeto.
- Esta medida compara os dois critérios entre si. Sem rotular manualmente quais editais são
  realmente relevantes, não dá para calcular precisão/revocação absolutas.
- O mesmo critério de palavra inteira vale para o e-mail e para o painel (`GET /me/editais`).
