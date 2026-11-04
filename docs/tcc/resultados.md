# Resultados medidos (base para as perguntas 3 e 4 da pesquisa)

Gerado por `python avaliar.py` em 04/11/2026, rede real, sem tocar no banco nem enviar e-mail.
Para repetir: `python avaliar.py` (adicione `--selenium` para incluir a fonte que exige navegador).

## Cobertura e confiabilidade por fonte (pergunta 4)

| Fonte | Motor | Itens | Tempo (s) | Resultado |
|---|---|---|---|---|
| UFPA - Processos seletivos (SIGAA) | sigaa | 106 | 1,9 | ok |
| UFRA - Processos seletivos (SIGAA) | sigaa | 0 | 1,2 | vazio legítimo* |
| UFOPA - Processos seletivos (SIGAA) | sigaa | 30 | 2,0 | ok |
| UNIFESSPA - Processos seletivos (SIGAA) | sigaa | 21 | 2,6 | ok |
| IFPA - Processos seletivos (SIGAA) | sigaa | 2 | 1,3 | ok |
| UNIFAP - Processos seletivos (SIGAA) | sigaa | 21 | 2,5 | ok |
| UFPA - Editais | selenium | - | - | não medida (exige navegador) |
| UFRA - Editais, programas e seleções | estático | 10 | 0,8 | ok |
| UNIFESSPA - Editais de pós-graduação | estático | 30 | 3,5 | ok |
| UEPA - Sistema de seleções (SGPS) | estático | 76 | 20,7 | ok |
| UEPA - Destaques e editais | estático | 6 | 1,0 | ok |
| UFAM - Editais | estático | 24 | 1,1 | ok |
| UFT - Editais | estático | 5 | 3,2 | ok |
| IFTO - Editais | estático | 14 | 0,7 | ok |

\* O SIGAA da UFRA respondeu normalmente com a mensagem "Nenhum processo seletivo encontra-se aberto
para inscrições neste nível de ensino". Zero itens aqui é a realidade do portal, não falha do coletor.

- 13 das 14 fontes foram medidas: nenhuma falhou; 12 devolveram itens e 1 estava legitimamente vazia.
- 313 títulos únicos (deduplicados por link) coletados em uma rodada.
- Tempo total das 13 fontes: cerca de 43 s, dominado pela UEPA/SGPS (20,7 s).
- A fonte por Selenium (UFPA - Editais) ficou fora desta rodada, então a cobertura do motor
  Selenium não está medida aqui.

## Palavra inteira x substring (pergunta 3)

Sobre os 313 títulos coletados, com 14 palavras-chave de amostra (escolhidas por mim como interesses
plausíveis de candidatos; não é amostra de usuários reais):

| Palavra | Substring | Palavra inteira | Falsos positivos evitados |
|---|---|---|---|
| ia | 195 | 0 | 195 |
| ti | 141 | 0 | 141 |
| social | 3 | 3 | 0 |
| saúde | 9 | 9 | 0 |
| computação | 8 | 8 | 0 |
| engenharia | 6 | 6 | 0 |
| educação | 26 | 26 | 0 |
| enfermagem | 7 | 7 | 0 |
| direito | 3 | 3 | 0 |
| biologia | 6 | 6 | 0 |
| física | 4 | 4 | 0 |
| história | 5 | 5 | 0 |
| doutorado | 60 | 60 | 0 |
| mestrado | 164 | 164 | 0 |
| **Total** | 637 | 301 | 336 |

Leitura honesta dos números:

- A busca por substring geraria 637 correspondências; a por palavra inteira, 301. Ou seja, 336
  (52,7%) das correspondências por substring seriam falsos positivos.
- Todo o ganho vem das palavras curtas: "ia" casaria dentro de "Amazônia" (42 vezes), "ciências" (28)
  e "geografia" (21); "ti" casaria dentro de "seletivo" (115 vezes), "matemática" e "institucional".
  Nas palavras longas a diferença foi zero nesta amostra.
- Consequência: a palavra inteira é essencial para siglas e termos curtos, mas tem um custo.
  "IA" como palavra isolada não apareceu em nenhum título, então hoje um usuário com o interesse "ia"
  não receberia nada (os editais dizem "Inteligência Artificial" por extenso). Isso vira ponto de
  melhoria: sinônimos/expansão de siglas.
- A palavra inteira não resolve variação de flexão: "social" não casa com "sociais".
  Dá para tratar com radical (stemming), mas aumentaria o risco de falso positivo. É decisão de projeto.
- Esta medida compara os dois critérios entre si. Sem rotular manualmente quais editais são
  realmente relevantes, não dá para calcular precisão/revocação absolutas.
