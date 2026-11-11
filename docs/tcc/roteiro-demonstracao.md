# Roteiro da demonstração do produto (5 a 7 minutos)

Objetivo: mostrar que o PósEmFoco resolve o problema da pesquisa, ligando cada passo a uma
pergunta de pesquisa. Ensaie uma vez inteira antes da apresentação.

## Antes de começar (checklist, 10 min antes)

- [ ] `docker compose up -d` e conferir `GET /health` respondendo.
- [ ] Um e-mail seu aberto na caixa de entrada (o de teste: `python testar_email.py`).
- [ ] Rodar `python -m app.services.scraping.fontes` uma vez: confirma que as fontes estão de pé
      e aquece o que for preciso. Se alguma vier com 0 itens, avisar na fala (ver "Se der errado").
- [ ] Ter pronto um interesse que **existe hoje** nos portais (confira na lista: "mestrado",
      "educação", "enfermagem" retornaram resultados na medição). Não apostar em "ia".
- [ ] Plano B: `docs/tcc/resultados.md` aberto e prints/gravação de uma execução que deu certo.
- [ ] Internet testada; celular com hotspot de reserva.

## Sequência

| Min | O que mostrar | O que dizer | Pergunta de pesquisa |
|---|---|---|---|
| 0:00 | Slide do problema + 3 abas de portais diferentes (SIGAA, SGPS, página institucional) | "Para acompanhar editais, o candidato visita vários sites com layouts diferentes." | Problema / P1 |
| 1:00 | `fontes.py` aberto, mostrando `FonteEdital` e `_sigaa("UFPA", ...)` | "Cada instituição é uma linha de configuração. Quatro motores: SIGAA, HTML estático, WordPress e Plone (APIs nativas dos portais). WordPress e Plone entraram sem mexer no núcleo, e o Selenium saiu quando se viu que nenhuma fonte precisava de navegador." | P2 |
| 2:00 | Cadastro e login na interface (`/frontend/cadastro.html`) | "O usuário só informa palavras-chave. Senha com bcrypt, sessão por token." | — |
| 2:45 | Painel: adicionar interesse e salvar; botão "Buscar agora" | "A coleta normal roda sozinha no worker; aqui forço uma rodada para a demonstração." | P4 |
| 3:45 | Aba "Meus editais" com os resultados + e-mail chegando na caixa de entrada | "Só chega o que casa com o meu interesse, e uma única vez por edital." | P3 / P4 |
| 4:45 | Segunda rodada ("Buscar agora" de novo) sem novos e-mails | "O banco tem `UNIQUE(link)`: sem duplicidade, mesmo com várias rodadas." | P4 |
| 5:15 | `docs/tcc/resultados.md`: tabela de falsos positivos | "Por substring, 'ia' casaria em 513 títulos (Amazônia, ciências). Por palavra inteira, 0. No total, 62,7% das correspondências por substring seriam falsas." | P3 |
| 6:00 | Tabela de cobertura | "16 instituições, 22 fontes, nenhuma falha, 1054 títulos em cerca de 42 s. E um achado: um 'vazio' da rodada anterior era falha de certificado mascarada." | P4 |
| 6:30 | Limitações e próximos passos | Ver abaixo | — |

## Falas de limitação (importante assumir, a banca valoriza)

- 6 públicas do Norte ficaram de fora (anti-bot, SIGAA atrás de login, portais sem API); cada uma está
  documentada em `fontes.py`.
- Compara só o **título** do edital, não o conteúdo do PDF.
- "IA" como sigla isolada não aparece nos títulos, então hoje exige o termo por extenso.
- Sem rotular manualmente os editais, não há precisão/revocação absolutas; a medida compara
  dois critérios entre si.
- Nas fontes WordPress de UNIFAP e UFRR o recorte é "notícias que citam edital": vem notícia de graduação junto, e o filtro por interesse é quem separa.

## Se der errado

| Problema | O que fazer |
|---|---|
| Portal fora do ar ou lento | Mostrar que a rodada continua nas outras fontes (log) e que o erro é registrado |
| 0 itens em uma fonte | No SIGAA pode ser "nenhum processo aberto"; se fosse falha de rede, a tabela mostraria FALHOU (o motor não mascara mais) |
| E-mail não chega | Conferir spam; mostrar o log `[MATCH NOVO]` e o envio como evidência; ter print de e-mail anterior |
| Sem internet | Mostrar gravação/prints e `resultados.md`; rodar `python -m app.services.test_match` (offline) |

## Perguntas prováveis da banca

1. **"Por que não usar uma API?"** As universidades não oferecem uma para os editais; daí o scraping.
2. **"É legal raspar esses sites?"** Só lê páginas públicas, sem login; a LAI exige a publicidade
   desses dados. O sistema usa intervalo entre rodadas e identifica o robô no User-Agent.
3. **"E se o portal mudar de layout?"** O seletor quebra e a fonte devolve 0 itens; o verificador
   `python -m app.services.scraping.fontes` mostra isso, e o ajuste é só na configuração.
4. **"Como escalaria?"** A API já roda com mais de uma instância; o worker é um processo à parte.
5. **"Qual a contribuição científica?"** Avaliação empírica de coleta + filtragem num caso real,
   com métricas (ver `resultados.md`), e uma arquitetura extensível documentada.
6. **"E páginas que só carregam com JavaScript?"** O Selenium foi removido porque nenhuma fonte
   precisava: a UFPA, que parecia exigir navegador, só barrava requisição sem User-Agent. Esse tipo
   de página costuma buscar os dados numa chamada interna (XHR/JSON), que dá para usar direto, sem
   navegador. Onde nem isso basta (anti-bot do IFAM), a fonte fica de fora e o motivo fica documentado.
