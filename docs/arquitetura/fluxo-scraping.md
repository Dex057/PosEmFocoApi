# 🕷️ Fluxo de Scraping

Documentação técnica detalhada do sistema de web scraping com Selenium.

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Fluxo Completo](#fluxo-completo)
3. [Código Detalhado](#código-detalhado)
4. [Tratamento de Erros](#tratamento-de-erros)
5. [Performance & Otimizações](#performance--otimizações)

---

## 🎯 Visão Geral

O scraper é um módulo que:

1. **Roda em background** após login de qualquer usuário
2. **Acessa site da UFPA** usando Selenium (simula navegador real)
3. **Extrai informações** de editais
4. **Verifica duplicatas** no banco de dados
5. **Salva editais novos**
6. **Notifica usuários** cujos interesses coincidem

**Tecnologias:**
- **Selenium** - Automação de navegador
- **WebDriver Manager** - Gerencia ChromeDriver
- **BeautifulSoup** (opcional) - Parse HTML
- **PostgreSQL** - Armazena dados
- **SMTP/Gmail** - Envia emails

---

## 🔄 Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│ Login do Usuário (POST /login)                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ├─ Verifica credenciais
                     ├─ ✅ Login bem-sucedido
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│ BackgroundTask: executar_scraper()                              │
│ Rodando em paralelo, não bloqueia resposta do login             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ 1. INICIALIZAR SELENIUM    │
        └────────────┬───────────────┘
                     │
     ├─ Baixar ChromeDriver (automático)
     ├─ Inicializar Chrome headless
     └─ Acessar URL: https://www.ufpa.edu.br
                     │
                     ▼
        ┌────────────────────────────┐
        │ 2. EXTRAIR EDITAIS         │
        └────────────┬───────────────┘
                     │
     ├─ Buscar elementos HTML dos editais
     ├─ Extrair: título, link, resumo, data
     ├─ Paginar (página 2, 3, 4...)
     └─ Coletar lista completa
                     │
                     ▼
        ┌────────────────────────────┐
        │ 3. PROCESSAR CADA EDITAL   │
        └────────────┬───────────────┘
                     │
    Para cada edital:
     │
     ├─ 3.1: Verificar duplicata no BD
     │       SELECT * FROM edital 
     │       WHERE titulo = ? AND link = ?
     │
     ├─ 3.2: SE JÁ EXISTE
     │       └─ Pular (não salvar)
     │
     └─ 3.3: SE NÃO EXISTE
            ├─ Salvar no BD
            │  INSERT INTO edital (titulo, link, resumo, data)
            │
            └─ Encontrar usuários interessados
               │
               ▼
        ┌────────────────────────────┐
        │ 4. NOTIFICAR USUÁRIOS      │
        └────────────┬───────────────┘
               │
      SELECT DISTINCT u.id, u.email
      FROM usuario u
      JOIN interesse i ON u.id = i.usuario_id
      WHERE LOWER(i.palavra_chave) LIKE ?
              │
              ▼
         Para cada usuário:
              │
              ├─ Montar email HTML
              ├─ Enviar via SMTP/Gmail
              └─ Log de envio
                     │
                     ▼
        ┌────────────────────────────┐
        │ 5. FINALIZAR              │
        └────────────┬───────────────┘
                     │
              ├─ Fechar Selenium
              ├─ Log de sucesso
              ├─ Calcular tempo
              └─ Salvar último horário
```

---

## 💻 Código Detalhado

### 1. Arquivo: `app/services/scraper.py`

```python
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from app.dao.edital_dao import EditalDAO
from app.dao.interesse_dao import InteresseDAO
from app.dao.usuario_dao import UsuarioDAO
from app.services.email_service import enviar_notificacao

edital_dao = EditalDAO()
interesse_dao = InteresseDAO()
usuario_dao = UsuarioDAO()

def executar_scraper():
    """
    Executa o web scraper para buscar editais na UFPA.
    
    Processo:
    1. Inicializa Selenium
    2. Acessa site da UFPA
    3. Extrai editais
    4. Verifica duplicatas
    5. Notifica usuários
    """
    
    driver = None
    try:
        print("[SCRAPER] Iniciando scraper...")
        inicio = time.time()
        
        # 1. INICIALIZAR SELENIUM
        driver = inicializar_selenium()
        print("[SCRAPER] Selenium inicializado")
        
        # 2. ACESSAR SITE UFPA
        url = "https://www.ufpa.edu.br"  # Substitua pela URL real
        driver.get(url)
        print(f"[SCRAPER] Acessando {url}")
        
        # Esperar página carregar
        time.sleep(2)
        
        # 3. EXTRAIR EDITAIS
        editais = extrair_editais(driver)
        print(f"[SCRAPER] {len(editais)} editais encontrados")
        
        # 4. PROCESSAR CADA EDITAL
        novos = 0
        duplicados = 0
        
        for edital in editais:
            # Verificar se já existe
            existe = edital_dao.buscar_por_titulo_e_link(
                edital['titulo'],
                edital['link']
            )
            
            if existe:
                print(f"[SCRAPER] DUPLICADO: {edital['titulo']}")
                duplicados += 1
                continue
            
            # Salvar novo edital
            edital_dao.salvar(edital)
            print(f"[SCRAPER] NOVO: {edital['titulo']}")
            novos += 1
            
            # 5. NOTIFICAR USUÁRIOS
            notificar_usuarios(edital)
        
        duracao = time.time() - inicio
        print(f"[SCRAPER] Scraper finalizado em {duracao:.2f}s")
        print(f"[SCRAPER] Novos: {novos}, Duplicados: {duplicados}")
        
    except Exception as e:
        print(f"[SCRAPER] ERRO: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Fechar Selenium
        if driver:
            driver.quit()
            print("[SCRAPER] Selenium fechado")


def inicializar_selenium():
    """
    Inicializa o ChromeDriver com configurações.
    
    Returns:
        WebDriver: Driver do Chrome inicializado
    """
    
    # Opções do Chrome
    options = webdriver.ChromeOptions()
    
    # Headless (sem interface gráfica)
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # User agent (simular navegador real)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Desabilitar notificações
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver


def extrair_editais(driver):
    """
    Extrai lista de editais da página.
    
    Args:
        driver: WebDriver inicializado
        
    Returns:
        list: Lista de dicts com { titulo, link, resumo, data_publicacao }
    """
    
    editais = []
    
    try:
        # Esperar elementos carregar (máximo 10 segundos)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "edital-item")  # Ajuste seletor conforme site
            )
        )
        
        # Extrair editais (ajuste seletores conforme HTML real)
        elementos = driver.find_elements(By.CLASS_NAME, "edital-item")
        print(f"[SCRAPER] {len(elementos)} elementos encontrados no HTML")
        
        for elem in elementos:
            try:
                # Extrair título
                titulo_elem = elem.find_element(By.CLASS_NAME, "titulo")
                titulo = titulo_elem.text.strip()
                
                # Extrair link
                link_elem = elem.find_element(By.TAG_NAME, "a")
                link = link_elem.get_attribute("href")
                
                # Se link relativo, fazer absoluto
                if not link.startswith("http"):
                    link = "https://www.ufpa.edu.br" + link
                
                # Extrair resumo
                try:
                    resumo_elem = elem.find_element(By.CLASS_NAME, "resumo")
                    resumo = resumo_elem.text.strip()
                except:
                    resumo = ""
                
                # Extrair data
                try:
                    data_elem = elem.find_element(By.CLASS_NAME, "data")
                    data = data_elem.text.strip()
                except:
                    data = None
                
                edital = {
                    "titulo": titulo,
                    "link": link,
                    "resumo": resumo,
                    "data_publicacao": data
                }
                
                editais.append(edital)
                print(f"[SCRAPER] Extraído: {titulo[:50]}...")
                
            except Exception as e:
                print(f"[SCRAPER] Erro ao extrair elemento: {e}")
                continue
        
        # PAGINAÇÃO (se houver)
        editais.extend(extrair_proxima_pagina(driver))
        
        return editais
    
    except Exception as e:
        print(f"[SCRAPER] Erro ao extrair editais: {e}")
        return editais


def extrair_proxima_pagina(driver, max_paginas=5):
    """
    Extrai editais das próximas páginas.
    
    Args:
        driver: WebDriver
        max_paginas: Máximo de páginas a processar
        
    Returns:
        list: Editais das próximas páginas
    """
    
    editais = []
    
    for pagina in range(2, max_paginas + 1):
        try:
            # Encontrar botão "próxima página"
            # Ajuste seletor conforme site real
            botao_proximo = driver.find_element(
                By.XPATH,
                f"//a[@href='?page={pagina}']"
            )
            
            # Clicar
            botao_proximo.click()
            time.sleep(2)
            
            # Extrair editais desta página
            elementos = driver.find_elements(By.CLASS_NAME, "edital-item")
            for elem in elementos:
                # Mesmo código de antes...
                pass
            
        except:
            print(f"[SCRAPER] Página {pagina} não existe ou erro ao acessar")
            break
    
    return editais


def notificar_usuarios(edital):
    """
    Encontra usuários interessados e envia notificações.
    
    Args:
        edital: Dict com { titulo, link, resumo }
    """
    
    try:
        # 1. Buscar palavras-chave do edital
        palavras_chave = extrair_palavras_chave(edital['titulo'])
        print(f"[NOTIFICADOR] Palavras-chave extraídas: {palavras_chave}")
        
        # 2. Para cada palavra-chave, buscar usuários interessados
        usuarios_notificados = set()
        
        for palavra in palavras_chave:
            # Buscar usuários interessados nesta palavra
            usuarios = interesse_dao.buscar_usuarios_por_palavra(palavra)
            
            for usuario in usuarios:
                if usuario['id'] in usuarios_notificados:
                    continue  # Já notificado
                
                # 3. Enviar email
                try:
                    enviar_notificacao(
                        usuario['email'],
                        edital['titulo'],
                        edital['link'],
                        palavra
                    )
                    usuarios_notificados.add(usuario['id'])
                    print(f"[NOTIFICADOR] Email enviado para {usuario['email']}")
                except Exception as e:
                    print(f"[NOTIFICADOR] Erro ao enviar email: {e}")
    
    except Exception as e:
        print(f"[NOTIFICADOR] Erro ao notificar usuários: {e}")


def extrair_palavras_chave(titulo):
    """
    Extrai possíveis palavras-chave do título do edital.
    
    Args:
        titulo: String com título do edital
        
    Returns:
        list: Lista de palavras-chave
    """
    
    # Palavras ignoráveis
    stopwords = {
        'de', 'do', 'da', 'em', 'para', 'por', 'com', 'sem',
        'e', 'ou', 'edital', 'mestrado', 'doutorado', 'seleção'
    }
    
    # Dividir título
    palavras = titulo.lower().split()
    
    # Filtrar
    palavras_chave = [
        p for p in palavras
        if p not in stopwords and len(p) > 3
    ]
    
    return palavras_chave[:3]  # Top 3 palavras
```

### 2. Arquivo: `app/dao/edital_dao.py`

```python
class EditalDAO:
    def salvar(self, edital):
        """Salva um edital no banco de dados"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO edital (titulo, link, resumo, data_publicacao)
                VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(sql, (
                edital['titulo'],
                edital['link'],
                edital.get('resumo', ''),
                edital.get('data_publicacao')
            ))
            
            conn.commit()
            cursor.close()
            return True
        
        except Exception as e:
            print(f"Erro ao salvar edital: {e}")
            if conn:
                conn.rollback()
            return False
        
        finally:
            if conn:
                conn.close()
    
    def buscar_por_titulo_e_link(self, titulo, link):
        """Verifica se edital já existe"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            sql = "SELECT id FROM edital WHERE titulo = %s AND link = %s"
            cursor.execute(sql, (titulo, link))
            
            resultado = cursor.fetchone()
            cursor.close()
            return resultado is not None
        
        except Exception as e:
            print(f"Erro ao buscar edital: {e}")
            return False
        
        finally:
            if conn:
                conn.close()
```

---

## 🚨 Tratamento de Erros

### Erros Comuns e Soluções

```python
# 1. ChromeDriver não encontrado
# ✅ Solução: WebDriver Manager baixa automaticamente
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
service = Service(ChromeDriverManager().install())

# 2. Site não carrega em tempo
# ✅ Solução: WebDriverWait com timeout
from selenium.webdriver.support.ui import WebDriverWait
WebDriverWait(driver, 10).until(EC.presence_of_element_located(...))

# 3. Seletor CSS/XPath errado
# ✅ Solução: Usar browser DevTools para achar seletor certo
# F12 no Chrome, inspecionar elemento, copiar XPath

# 4. Email não envia
# ✅ Solução: Verificar credenciais do Gmail
# Usar "Senha de Aplicativo" (veja docs/guias/configuracao.md)

# 5. Memória cresce (memory leak)
# ✅ Solução: Fechar driver no finally
finally:
    if driver:
        driver.quit()
```

---

## ⚡ Performance & Otimizações

### Tempo de Execução

```
Tempos típicos:
- Inicializar Selenium:     2-3s
- Acessar site:             3-5s
- Extrair editais (1 pág):  1-2s
- Extrair paginação (3 pág): 5-8s
- Processar e notificar:    2-3s
──────────────────────────
Total:                      15-20s
```

### Otimizações Possíveis

```python
# 1. Cache de editais (1 hora)
CACHE_EDITAIS = None
CACHE_TIME = None

def get_editais_cached():
    global CACHE_EDITAIS, CACHE_TIME
    if CACHE_EDITAIS and time.time() - CACHE_TIME < 3600:
        return CACHE_EDITAIS
    
    CACHE_EDITAIS = extrair_editais(driver)
    CACHE_TIME = time.time()
    return CACHE_EDITAIS

# 2. Requisições paralelas
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(enviar_email, user) for user in usuarios]

# 3. Banco de dados indexado
CREATE INDEX idx_edital_link ON edital(link);
CREATE UNIQUE INDEX idx_edital_unico ON edital(titulo, link);

# 4. Reduzir logs (apenas em debug)
if DEBUG:
    print(f"[SCRAPER] Debug: {info}")
```

### Rate Limiting

```python
# Não sobrecarregar site UFPA
import time

DELAY_ENTRE_PAGINAS = 2  # segundos
DELAY_ENTRE_REQUESTS = 1  # segundos

time.sleep(DELAY_ENTRE_PAGINAS)  # Esperar antes de clicar próximo
```

---

## 🧪 Teste Manual

```bash
# 1. Ativar ambiente virtual
source venv/bin/activate

# 2. Iniciar servidor
uvicorn server:app --reload &

# 3. Fazer login (inicia scraper)
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "senha": "senha123"
  }'

# 4. Ver logs do scraper (em outro terminal)
tail -f /var/log/posemfoco.log  # ou onde configurar

# 5. Verificar se editais foram salvos
psql -U posemfoco_user -d posemfoco -c "SELECT * FROM edital ORDER BY data_criacao DESC LIMIT 5;"
```

---

## 📚 Próximos Passos

- [Email Service](../componentes/email-service.md) - Notificações
- [API Endpoints](../api/endpoints.md) - Usar scraper
- [Deployment](../deployment.md) - Rodar em produção

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
