# 🐛 Troubleshooting Completo

Solução de problemas detalhada para desenvolvimento e produção.

## 📋 Índice
1. [Problemas de Instalação](#problemas-de-instalação)
2. [Problemas de Banco de Dados](#problemas-de-banco-de-dados)
3. [Problemas de API/FastAPI](#problemas-de-apifastapi)
4. [Problemas do Scraper](#problemas-do-scraper)
5. [Problemas de Email](#problemas-de-email)
6. [Problemas de Produção](#problemas-de-produção)

---

## 🔧 Problemas de Instalação

### Python não reconhecido

**Erro:**
```
command not found: python
```

**Solução:**
```bash
# Verificar instalação
which python3
python3 --version

# Criar alias (opcional)
alias python=python3

# Ou instalar
sudo apt install python3  # Linux
brew install python@3.10  # Mac
```

---

### Pip não funciona

**Erro:**
```
command not found: pip
```

**Solução:**
```bash
# Usar python -m pip
python -m pip --version
python -m pip install -r requirements.txt

# Ou instalar pip
sudo apt install python3-pip
pip --version
```

---

### Permissão negada em venv

**Erro:**
```
Permission denied: './venv/bin/activate'
```

**Solução:**
```bash
# Dar permissão
chmod +x venv/bin/activate

# Ou recriar venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

---

## 🗄️ Problemas de Banco de Dados

### PostgreSQL não inicializa

**Erro:**
```
psql: could not connect to server: Connection refused
```

**Solução:**
```bash
# Linux: iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl status postgresql

# Mac: iniciar PostgreSQL
brew services start postgresql

# Windows: verificar Services
# Pesquisar "Services" → PostgreSQL → Start

# Testar conexão
psql -U postgres
```

---

### Senha do PostgreSQL errada

**Erro:**
```
psql: FATAL: Ident authentication failed for user "posemfoco_user"
```

**Solução:**
```bash
# Reset de senha
sudo -u postgres psql

# Na prompt psql:
ALTER USER posemfoco_user WITH PASSWORD 'nova_senha_forte';

# Atualizar .env
nano .env
# DB_PASSWORD=nova_senha_forte
```

---

### Banco de dados não existe

**Erro:**
```
psycopg2.OperationalError: database "posemfoco" does not exist
```

**Solução:**
```bash
# Criar banco
sudo -u postgres createdb posemfoco

# Ou via psql
sudo -u postgres psql
CREATE DATABASE posemfoco OWNER posemfoco_user;

# Criar tabelas
python criar_tabelas.py
```

---

### "relation does not exist"

**Erro:**
```
psycopg2.ProgrammingError: relation "usuario" does not exist
```

**Solução:**
```bash
# Tabelas não foram criadas
python criar_tabelas.py

# Ou verificar
psql -U posemfoco_user -d posemfoco -c "\dt"

# Se vazio, criar manualmente:
psql -U posemfoco_user -d posemfoco < criar_tabelas.sql
```

---

### Permissão negada no banco

**Erro:**
```
psycopg2.OperationalError: permission denied for schema public
```

**Solução:**
```bash
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE posemfoco TO posemfoco_user;
```

---

## 🚀 Problemas de API/FastAPI

### ModuleNotFoundError: No module named 'app'

**Erro:**
```
ModuleNotFoundError: No module named 'app'
```

**Solução:**
```bash
# 1. Certifique-se de estar no diretório raiz
pwd  # Deve terminar em /PosEmFoco
ls -la | grep app  # Deve exibir pasta app

# 2. PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/caminho/completo/PosEmFoco"

# 3. Ou usar módulo Python para executar
python -m uvicorn server:app --reload
```

---

### Porta 8000 em uso

**Erro:**
```
[Errno 48] Address already in use
```

**Solução:**
```bash
# Usar outra porta
uvicorn server:app --reload --port 8001

# Ou liberar porta
# Linux: ver processo
lsof -i :8000
kill -9 <PID>

# Mac:
lsof -i :8000
kill -9 <PID>

# Windows (PowerShell):
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

### Erro 422 na requisição

**Erro:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

**Solução:**
```
Validação Pydantic falhou. Verifique:
- Email deve ser válido (nome@dominio.com)
- Campos obrigatórios não podem estar vazios
- Tipos devem corresponder (string, int, etc)
```

**Exemplo correto:**
```bash
curl -X POST http://localhost:8000/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João",
    "email": "joao@example.com",
    "senha": "senha123",
    "nivel_graduacao": "Mestrado",
    "interesses": ["Python"]
  }'
```

---

### CORS error no navegador

**Erro:**
```
Access to XMLHttpRequest from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solução:**
```python
# Em server.py, o CORS já está configurado:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Desenvolvimento: aceita tudo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Se persistir, verifique:
# 1. Server está rodando (http://localhost:8000)
# 2. Middleware está acima de rotas
# 3. Recarregue navegador (Ctrl+Shift+R)
```

---

### Pydantic validation error

**Erro:**
```
validation error for UsuarioInput
interesses ensure this value is a list (type=type_error.list)
```

**Solução:**
```bash
# Erro: interesses não é array
curl -X POST http://localhost:8000/cadastro \
  -d '{"interesses": "Computação"}'  # ❌ String

# Correto: array
curl -X POST http://localhost:8000/cadastro \
  -d '{"interesses": ["Computação"]}'  # ✅ Array
```

---

## 🕷️ Problemas do Scraper

Primeiro passo sempre: `python -m app.services.scraping.fontes` (mostra itens por fonte) ou
`python avaliar.py` (tabela com tempo e FALHOU/ok).

### Fonte devolve 0 itens

**Causa:** o portal mudou o layout e o `seletor_item` não casa mais.

**Solução:**
```bash
# Baixe a página como o motor baixa (com User-Agent) e procure o link de um edital
curl -s -A "Mozilla/5.0 (compatible; PosEmFocoBot/1.0)" "<url da fonte>" -o pagina.html
```
Ajuste o seletor em `fontes.py` e rode o verificador de novo. No SIGAA, 0 itens pode ser só
"nenhum processo aberto"; se todos os níveis falharem, o motor levanta erro (não devolve vazio).

---

### HTTP 403 Forbidden

**Causa:** alguns portais (ex.: UFPA) recusam requisição sem User-Agent.

**Solução:** os motores já mandam `HEADERS` de `engine_estatico.py`. Se uma fonte nova
der 403 mesmo assim, compare com `curl -A "Mozilla/5.0" <url>`; captcha ou anti-bot (IFAM)
não tem solução simples e a fonte fica de fora, anotada no fim de `fontes.py`.

---

### `SSLError: certificate verify failed: unable to get local issuer certificate`

**Causa:** o servidor não envia o certificado intermediário (comum em .edu.br com a CA da RNP).

**Solução:** os intermediários conhecidos ficam em `app/services/scraping/intermediarios.pem`.
Para outra CA:
```bash
# URL do intermediário que falta
openssl s_client -connect host:443 -servername host </dev/null | openssl x509 -noout -ext authorityInfoAccess
# Baixe, converta para PEM, confira contra as raízes do certifi e acrescente ao arquivo
openssl x509 -inform DER -in inter.crt -out inter.pem
openssl verify -CAfile "$(python -c 'import certifi;print(certifi.where())')" inter.pem
```
`verificar_ssl=False` na fonte é a última saída.

---

### Uma fonte leva ~20 s por página

**Causa:** o portal anuncia IPv6 que não responde, e o cliente espera o timeout antes do IPv4.

**Solução:** a coleta já força IPv4 (`urllib3.util.connection.HAS_IPV6 = False` em
`engine_estatico.py`). Se voltar a acontecer, confira com:
```bash
python -c "import socket;print(socket.getaddrinfo('host',443))"
```

---

### Lista só aparece depois do JavaScript

**Causa:** a página monta a lista no navegador. O projeto não usa navegador headless.

**Solução:** abra o DevTools (F12) → aba Rede → recarregue e procure a chamada XHR/JSON que
traz os itens. Se o portal for WordPress, teste `https://<site>/wp-json/wp/v2/posts?search=edital`
e use `engine="wordpress"`. Se for Plone, teste
`curl -H "Accept: application/json" "https://<site>/@search?SearchableText=edital"` e use `engine="plone"`.

---

## 📧 Problemas de Email

### SMTPAuthenticationError ao enviar email

**Erro:**
```
smtplib.SMTPAuthenticationError: (535, b'5.7.8 Username and password not accepted')
```

**Solução:**
```bash
# 1. Verificar credenciais
# EMAIL_ADDRESS deve ser seu Gmail (exemplo@gmail.com)
# EMAIL_PASSWORD deve ser SENHA DE APP (não a senha da conta!)

# 2. Gerar nova senha de app
# Acesse: https://myaccount.google.com/apppasswords
# Selecione: Mail + Windows Computer
# Copie a senha gerada e atualize .env

# 3. Se usar 2FA, habilitá-lo primeiro
# https://myaccount.google.com/security

# 4. Testar
python -c "
import smtplib
email = 'seu@gmail.com'
senha = 'sua_senha_de_app'
try:
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(email, senha)
    print('✅ Conectado!')
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

---

### ConnectionRefusedError ao conectar SMTP

**Erro:**
```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solução:**
```python
# Verificar servidor SMTP
import smtplib

# Gmail
servidor = "smtp.gmail.com"
porta = 587
s = smtplib.SMTP(servidor, porta)

# Testar
s.starttls()
s.quit()
print("✅ Conectado ao SMTP")
```

---

### Email não chegando na caixa

**Solução:**
```
1. Verificar spam
2. Verificar logs de envio
3. Verificar credenciais do Gmail
4. Tentar com outro email (testar funcionalidade)
```

---

## ⚡ Problemas de Produção

### Serviço não inicia

**Erro:**
```
systemctl status posemfoco → inactive (dead)
```

**Solução:**
```bash
# Ver erro detalhado
sudo journalctl -u posemfoco -n 20

# Verificar arquivo .service
sudo systemctl status posemfoco --full

# Recriar serviço
sudo nano /etc/systemd/system/posemfoco.service
# Editar...

# Recarregar systemd
sudo systemctl daemon-reload
sudo systemctl start posemfoco
```

---

### Nginx não roteia para FastAPI

**Erro:**
```
502 Bad Gateway
```

**Solução:**
```bash
# 1. Verificar se FastAPI está rodando
sudo systemctl status posemfoco

# 2. Verificar porta
ss -tlnp | grep 8000

# 3. Verificar configuração nginx
sudo nginx -t

# 4. Ver logs nginx
sudo tail -f /var/log/nginx/error.log

# 5. Reiniciar nginx
sudo systemctl restart nginx
```

---

### SSL certificate expirou

**Erro:**
```
SSL_ERROR_RX_RECORD_TOO_LONG ou aviso no navegador
```

**Solução:**
```bash
# Renovar certificado
sudo certbot renew

# Forçar renovação
sudo certbot renew --force-renewal

# Verificar próxima renovação
sudo certbot show-renew-date
```

---

### Memória cheia

**Erro:**
```
killed by SIGKILL
```

**Solução:**
```bash
# Ver memória
free -h
top

# Liberar cache
sudo sync && echo 3 > /proc/sys/vm/drop_caches

# Aumentar SWAP
# Configurar limites em systemd
```

---

### Disco cheio

**Erro:**
```
No space left on device
```

**Solução:**
```bash
# Ver espaço
df -h

# Deletar backups antigos
find /backups -type f -mtime +30 -delete

# Limpar logs
sudo journalctl --vacuum-time=30d

# Limpar cache pip
pip cache purge
```

---

## 🔍 Checklist de Debugging

1. **Ler mensagem de erro completa** - Não ignore contexto
2. **Verificar logs** - `journalctl`, `tail -f`, `/var/log/`
3. **Testar isoladamente** - BD, Email, Scraper separadamente
4. **Verificar permissões** - Arquivos, diretórios, BD
5. **Revisar configuração** - `.env`, systemd, nginx
6. **Procurar em Google** - Copiar mensagem de erro exato
7. **Documentação oficial** - FastAPI, requests, PostgreSQL
8. **Stack Overflow** - Procurar problema similar
9. **Testes unitários** - `pytest` para isolar problema
10. **Pedir ajuda** - GitHub Issues ou comunidades

---

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [WordPress REST API](https://developer.wordpress.org/rest-api/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Uvicorn Docs](https://www.uvicorn.org/)

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
