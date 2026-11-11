# ❓ Perguntas Frequentes (FAQ)

## 🎓 Dúvidas Gerais

### O que é PósEmFoco?

PósEmFoco é um sistema que monitora automaticamente os portais de dez universidades públicas da Região Norte em busca de novos editais de pós-graduação. Você se cadastra, define seus interesses (ex: "Computação", "IA") e recebe notificações por email quando um edital correspondente é publicado.

---

### Para quem é PósEmFoco?

- Candidatos à pós-graduação nas universidades públicas do Norte (UFPA, UFAM, UFT, UNIFAP, entre outras)
- Pessoas que querem economizar tempo checando site manualmente
- Developers que querem aprender arquitetura de software
- Contribuidores que querem melhorar o projeto

---

### Quanto custa?

**Gratuito!** PósEmFoco é open source e não tem custo.

---

## 🚀 Instalação & Setup

### Qual Python versão preciso?

**Mínimo:** Python 3.10

Verifique:
```bash
python --version  # Deve ser 3.10 ou maior
```

Se tiver Python 3.8 ou 3.9, atualize:
- **Windows:** https://www.python.org/downloads/
- **Mac:** `brew install python@3.10`
- **Linux:** `sudo apt install python3.10`

---

### Preciso de Docker?

**Não é obrigatório.** Docker é útil para:
- Produção
- Isolar dependências
- Facilitar deploy

Mas para desenvolvimento local, não precisa.

---

### Posso instalar no Windows?

**Sim!** Duas opções:

1. **WSL2 (Recomendado):**
   - Instale WSL2
   - Siga guia Linux

2. **Windows Nativo:**
   - Python 3.10+
   - PostgreSQL
   - Siga guia Windows

Veja [Instalação](guias/instalacao.md) para detalhes.

---

## 🗄️ Banco de Dados

### Posso usar SQLite em vez de PostgreSQL?

**Tecnicamente sim, mas não recomendo.**

PostgreSQL é melhor para produção porque:
- Suporta múltiplos usuários
- Melhor performance
- ACID garantido
- Fácil backup/restore

SQLite é melhor para projetos pequenos/prototipagem.

---

### Como fazer backup do banco?

```bash
# Backup simples
pg_dump -U posemfoco_user posemfoco > backup.sql

# Backup comprimido (menor)
pg_dump -U posemfoco_user posemfoco | gzip > backup.sql.gz

# Restaurar
psql -U posemfoco_user posemfoco < backup.sql
```

Veja [Deployment](deployment.md#backup-e-recovery) para mais.

---

### Quanto espaço o banco usa?

Muito pouco:
- 1000 editais ≈ 100 KB
- 100 usuários ≈ 10 KB
- Total ≈ 1 MB

Bancos podem ter GB sem problema.

---

## 🔐 Segurança & Senha

### Minha senha é armazenada em plain text?

**Não!** Senhas são criptografadas com **bcrypt**.

Processo:
1. Você digita: `"Aluno@2026"`
2. Sistema aplica bcrypt: `"$2b$12$..."`
3. Armazena hash (irreversível)
4. No login, compara hash do bcrypt

Mesmo administrador do BD não consegue recuperar sua senha!

---

### Como meu email não vaza?

Email é armazenado em plain text no BD (necessário para enviar notificações).

Mas:
- ✅ Banco é protegido por senha
- ✅ BD só é acessível localmente (produção)
- ✅ HTTPS protege em trânsito
- ✅ Nunca compartilhamos dados

---

### O sistema envia meu email para terceiros?

**Não.** Email é usado apenas para:
1. Login (verificação)
2. Notificações de editais

Nunca vendemos, compartilhamos ou usamos para spam.

---

## 📧 Email & Notificações

### Por que não recebo email?

**Verificar em ordem:**

1. **Spam?** Verifique pasta de spam/lixeira
2. **Email correto?** Verifique cadastro
3. **Gmail ativado?** Teste em [Configuração](guias/configuracao.md#testando-envio-de-email)
4. **Senha de app?** Não é a senha da conta!
5. **Internet?** Teste conexão

---

### Qual frequência de notificações?

Você recebe email quando:
- Um edital **novo** é publicado
- E contém uma de suas **palavras-chave**

Depende da publicação de novos editais. O `worker` verifica as fontes a cada `INTERVALO_SCRAPER_MINUTOS` (padrão 60).

---

### Posso desativar notificações?

**Futuramente sim.** Por enquanto, deletar conta desativa notificações.

---

## 🕷️ Scraper & Web Scraping

### Quais sites o scraper acessa?

As fontes de `app/services/scraping/fontes.py` (páginas públicas, sem login):
- 100% automaticamente
- Sem overload (delays entre requisições)
- Valida duplicatas
- Respeita robots.txt (não blocado)

---

### Por que demora para atualizar?

Uma rodada completa das 17 fontes leva cerca de 40 s (medido em `docs/tcc/resultados.md`):
de 1 a 5 s por fonte, quase tudo esperando a resposta do portal.

Roda no `worker`, em loop, sem depender de login (e sob demanda em `POST /scraper/rodar`).

---

### O scraper sobrecarrega os portais?

**Não.** Sistema:
- Aguarda 2s entre páginas
- Não usa força bruta
- Simula navegador real
- Não faz 1000+ requisições

É bem-educado com o site.

---

## 🚀 Desenvolvimento

### Como contribuir?

1. Fork no GitHub
2. Clone seu fork
3. Crie branch para sua feature
4. Commit + Push
5. Abra Pull Request

Veja [Guia de Desenvolvimento](guias/desenvolvimento.md#como-contribuir) para detalhes.

---

### Quais tecnologias usa?

```
Frontend:    HTML5, CSS3, JavaScript
Backend:     Python 3.10+, FastAPI
BD:          PostgreSQL 12+
Scraping:    requests + BeautifulSoup (SIGAA, HTML, API do WordPress)
Email:       SMTP (Gmail)
Auth:        bcrypt (passlib)
```

Veja [Stack Tecnológico](README.md#tecnologias) no README.

---

### Onde começo a estudar código?

1. Leia [Arquitetura](arquitetura/visao-geral.md) - entender design
2. Leia [Fluxo de Autenticação](arquitetura/fluxo-autenticacao.md) - login
3. Leia [Fluxo de Scraping](arquitetura/fluxo-scraping.md) - scraper
4. Explore código em `app/`
5. Execute testes: `pytest`

---

### Como rodar testes?

```bash
# Instalar dependências teste
pip install pytest

# Rodar todos
pytest

# Rodar específico
pytest tests/test_auth.py

# Com cobertura
pip install pytest-cov
pytest --cov=app
```

---

## 🐛 Troubleshooting

### Meu problema não está aqui

1. Verifique [Troubleshooting Completo](troubleshooting.md)
2. Pesquise em Google
3. Abra [Issue no GitHub](https://github.com/seu-usuario/PosEmFoco/issues)
4. Pergunte em comunidades (Reddit, Discord, etc)

---

### Como relatar um bug?

Abra Issue no GitHub com:
- **Título:** Descrição clara do problema
- **Descrição:** O que aconteceu e o que esperava
- **Passos:** Como reproduzir
- **Logs:** Cole mensagem de erro completa
- **Ambiente:** SO, Python version, etc

Exemplo:
```
Título: Login falha com email em minúsculas

Descrição:
Ao fazer login com email em minúsculas, recebo erro 401

Passos para reproduzir:
1. Cadastro com "Maria@example.com"
2. Logout
3. Login com "maria@example.com" (minúscula)
4. Recebo "Email ou senha incorretos"

Logs:
[Endpoint POST /login]
[Erro 401: Email ou senha incorretos]

Ambiente:
- Ubuntu 20.04
- Python 3.10.5
```

---

## 📊 Performance & Escalabilidade

### Quantos usuários suporta?

**Teoricamente:**
- SQLite: ~100
- PostgreSQL: 1000+
- PostgreSQL + Nginx: 10000+
- Kubernetes: ilimitado

Para começar, PostgreSQL local suporta tranquilamente.

---

### Preciso de CDN?

**Não para começar.** CDN (Cloudflare) é bom para:
- Produção com muitos usuários
- Cachear recursos estáticos
- DDoS protection

Mas inicial não é necessário.

---

### Como escalar para produção?

1. **Código:** Implemente CI/CD (GitHub Actions)
2. **BD:** PostgreSQL em servidor dedicado
3. **Cache:** Redis para cache de editais
4. **Load Balancer:** Nginx load balancing
5. **CDN:** Cloudflare cache
6. **Monitoramento:** Prometheus + Grafana

Veja [Deployment](deployment.md) para detalhes.

---

## 🌐 Deploy & Produção

### Posso fazer deploy no Heroku?

**Sim!** Heroku é fácil para começar.

Mas precisa:
- Cartão de crédito
- PostgreSQL add-on (pago)
- Custom domain (opcional)

Veja deployment guides em [Deployment](deployment.md).

---

### Como usar meu próprio domínio?

1. Compre domínio (GoDaddy, Namecheap, etc)
2. Configure DNS para seu servidor
3. Instale SSL/HTTPS (Let's Encrypt)
4. Configure Nginx

Veja [Nginx](deployment.md#nginx-reverse-proxy) + [SSL](deployment.md#sslhttps).

---

### Dados são perdidos ao resetar?

**Sim.** Se deletar banco:
```bash
python reset_banco.py
```

Sempre faça backup antes!

---

## 💡 Ideias & Roadmap

### Posso adicionar nova feature?

**Sim!** Siga [Guia de Desenvolvimento](guias/desenvolvimento.md#como-contribuir):
1. Fork
2. Crie branch
3. Desenvolva
4. Pull Request

Idéias populares:
- Dashboard visualizar editais
- Filtros avançados
- Integração WhatsApp
- Suporte múltiplas universidades
- Mobile app

---

### Como priorizam features?

**Baseado em:**
1. Comunidade (issues/upvotes)
2. Viabilidade técnica
3. Mantibilidade
4. Tempo disponível

---

## 📞 Contato & Suporte

### Onde pedir ajuda?

1. **Documentação:** Leia [docs/](README.md)
2. **FAQ:** Aqui mesmo
3. **Troubleshooting:** [troubleshooting.md](troubleshooting.md)
4. **Issues:** [GitHub Issues](https://github.com/seu-usuario/PosEmFoco/issues)
5. **Discussions:** [GitHub Discussions](https://github.com/seu-usuario/PosEmFoco/discussions)

---

### Como reportar vulnerabilidade?

⚠️ **Não abra issue pública!**

Envie email privado para:
`seu-email@example.com`

Inclua:
- Descrição da vulnerabilidade
- Como reproduzir
- Impacto potencial
- Sua sugestão de fix

Agradecemos a responsabilidade! 🙏

---

## 🎉 Agradecimentos

Obrigado por usar PósEmFoco!

Se este projeto ajudou você:
- ⭐ Dê uma estrela no GitHub
- 👥 Convide amigos
- 💬 Dê feedback
- 🤝 Contribua código

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
"
