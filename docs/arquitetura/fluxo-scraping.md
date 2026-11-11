# 🕷️ Fluxo de Scraping

Como o PósEmFoco coleta editais, casa com os interesses dos usuários e notifica. Reflete o código
atual (`worker.py`, `app/services/scraper.py`, `app/services/scraping/`).

## Visão geral

```
worker.py (loop a cada INTERVALO_SCRAPER_MINUTOS)
   └─ executar_scraper()                         app/services/scraper.py
        1. _buscar_interesses()   palavra-chave -> [e-mails]   (se vazio, encerra)
        2. para cada FonteEdital em FONTES:
             coletar = ENGINES[fonte.engine]     sigaa | estatico | wordpress | plone
             itens   = coletar(fonte)            lista de (título, link)
             _processar_itens(...)
        3. _processar_itens:
             para cada (título, link) e cada palavra-chave:
               casa_palavra(palavra, título)?    palavra inteira, sem acento quebrado
                 sim -> EditalDAO.salvar()       INSERT ... ON CONFLICT (link) DO NOTHING
                        era novo? -> enviar_notificacao() p/ cada e-mail daquela palavra
```

A API não depende do worker: o usuário também pode forçar uma rodada com `POST /scraper/rodar`
(background task dentro do processo da API).

## Fontes e motores

Cada instituição é uma `FonteEdital` em `app/services/scraping/fontes.py` (URL, motor, seletores).
O orquestrador não tem nada específico de instituição.

| Motor | Quando usar | Como coleta |
|---|---|---|
| `sigaa` | Instituições com SIGAA (`/sigaa/public/processo_seletivo/lista.jsf`) | `requests` + BeautifulSoup; lê curso, vagas e período de inscrição; um link único por curso |
| `estatico` | Portais cuja lista já vem no HTML | `requests` + BeautifulSoup com seletor CSS e paginação |
| `wordpress` | Portais WordPress que expõem `/wp-json/wp/v2/posts` (UFOPA, UNIFAP, UFRR, UEA, UERR) | `requests` na API REST nativa; JSON, sem seletor CSS; pagina até a última página |
| `plone` | Portais Plone com a API `@search` (UFAC, IFAC) | `requests` com `Accept: application/json`; pagina por `b_start` (o link `next` do Plone pode vir com caminho interno quebrado) |

Verificar se as fontes continuam de pé: `python -m app.services.scraping.fontes`
(0 itens = seletor quebrou ou portal mudou; no SIGAA, 0 itens também pode ser "nenhum processo aberto" — se todos os níveis falharem, o motor levanta erro em vez de devolver vazio).

Rede: as conexões usam um bundle de CAs com o intermediário da RNP (`intermediarios.pem`), que
vários portais .edu.br não enviam, e só IPv4 (o IPv6 de alguns portais não responde e custava
~20 s por requisição).

## Casamento de palavra-chave

`casa_palavra()` exige a palavra inteira (lookaround em vez de `\b`, para aceitar termos como `c++`).
Motivo: por substring, "ia" casaria dentro de "Amazônia" e "ciências". Medição em
[`docs/tcc/resultados.md`](../tcc/resultados.md). Teste: `python -m app.services.test_match`.

## Anti-duplicidade

`edital.link` é `UNIQUE`. O INSERT usa `ON CONFLICT (link) DO NOTHING` e o `rowcount` diz se o
edital era novo. Só edital novo dispara e-mail, sem condição de corrida entre checar e inserir.

## Tratamento de falhas

- Falha em uma fonte é registrada em log e a rodada continua nas demais.
- Motor desconhecido numa fonte é registrado e a fonte é pulada.
- Erro no envio de e-mail é tratado em `email_service.py`, sem derrubar a rodada.
- Erro não tratado na rodada inteira é capturado em `worker.py`, que tenta de novo no próximo intervalo.

## Limites conhecidos

- O título do portal é o único texto comparado; o conteúdo do PDF do edital não é lido.
- `data_publicacao` ainda é gravada como `NULL`.
- Algumas públicas do Norte seguem sem fonte (anti-bot, JavaScript, links sem URL navegável);
  o motivo de cada uma está no fim de `fontes.py`.
