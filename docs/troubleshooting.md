# 🐛 Troubleshooting Completo

Solução de problemas detalhada para desenvolvimento e produção.

## 📋 Índice
1. [Problemas de Instalação](#problemas-de-instalação)
2. [Problemas de Banco de Dados](#problemas-de-banco-de-dados)
3. [Problemas de API/FastAPI](#problemas-de-apifastapi)
4. [Problemas de Selenium/Scraper](#problemas-de-selenium-scraper)
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

## 🕷️ Problemas de Selenium/Scraper

### ChromeDriver não encontrado

**Erro:**
```
selenium.common.exceptions.WebDriverException: unknown error: Chrome failed to start
```

**Solução:**
```bash
# Instalar Chrome
sudo apt install google-chrome-stable  # Linux
brew install google-chrome  # Mac

# Reinstalar webdriver-manager
pip install --upgrade webdriver-manager

# Ou especificar caminho
from selenium.webdriver.chrome.service import Service
service = Service('/usr/bin/google-chrome')
driver = webdriver.Chrome(service=service)
```

---

### TimeoutException ao extrair elementos

**Erro:**
```
selenium.common.exceptions.TimeoutException: Message: Timeout waiting for element
```

**Solução:**
```python
# Aumentar timeout (padrão 10s)
from selenium.webdriver.support.ui import WebDriverWait

# De:
WebDriverWait(driver, 10).until(EC.presence_of_element_located(...))

# Para:
WebDriverWait(driver, 30).until(EC.presence_of_element_located(...))

# Ou adicionar espera
import time
time.sleep(3)  # Aguardar JS carregar
```

---

### Seletor CSS/XPath errado

**Erro:**
```
selenium.common.exceptions.NoSuchElementException: no such element
```

**Solução:**
```python
# 1. Verificar seletor no navegador (F12)
# 2. Usar inspect element para copiar XPath correto
# 3. Testar seletor antes

driver = ...
elementos = driver.find_elements(By.CLASS_NAME, "edital-item")
print(f"Encontrados: {len(elementos)} elementos")

# Se 0, seletor está errado!
```

---

### Site bloqueia scraper

**Erro:**
```
403 Forbidden ou captcha aparece
```

**Solução:**
```python
# Adicionar delay entre requisições
import time
time.sleep(2)  # 2 segundos entre páginas

# Adicionar headers realistas
options = webdriver.ChromeOptions()
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
)
```

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
7. **Documentação oficial** - FastAPI, Selenium, PostgreSQL
8. **Stack Overflow** - Procurar problema similar
9. **Testes unitários** - `pytest` para isolar problema
10. **Pedir ajuda** - GitHub Issues ou comunidades

---

## 📚 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Selenium Docs](https://selenium.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Uvicorn Docs](https://www.uvicorn.org/)

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
