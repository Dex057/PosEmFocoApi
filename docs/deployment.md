# 🚀 Deployment em Produção

Guia completo para colocar PósEmFoco em produção.

## 📋 Índice
1. [Checklist Pré-Deploy](#checklist-pré-deploy)
2. [Configuração de Servidor](#configuração-de-servidor)
3. [PostgreSQL em Produção](#postgresql-em-produção)
4. [FastAPI com Uvicorn](#fastapi-com-uvicorn)
5. [Nginx (Reverse Proxy)](#nginx-reverse-proxy)
6. [SSL/HTTPS](#sslhttps)
7. [Monitoramento](#monitoramento)
8. [Backup e Recovery](#backup-e-recovery)

---

## ✅ Checklist Pré-Deploy

- [ ] Todos os testes passam (`pytest`)
- [ ] Sem console.log() ou print() desnecessários
- [ ] DEBUG=false no .env
- [ ] SECRET_KEY alterada (não usar padrão)
- [ ] Senhas do BD e email configuradas
- [ ] CORS restringido (não use `*` em produção)
- [ ] Documentação atualizada
- [ ] Plano de rollback
- [ ] Backup do BD feito
- [ ] Monitoramento configurado

---

## 🖥️ Configuração de Servidor

### Requisitos

```
- Ubuntu 20.04+ ou Debian 10+
- Mínimo 2GB RAM
- 10GB storage
- Python 3.10+
- PostgreSQL 12+
```

### Criar Usuário de Serviço

```bash
# Como root
sudo useradd -m -s /bin/bash posemfoco
sudo usermod -aG docker posemfoco  # Se usar Docker
sudo usermod -aG postgres posemfoco  # Para BD

# Dar permissões de diretório
sudo chown -R posemfoco:posemfoco /opt/posemfoco
```

### Fazer Deploy

```bash
# SSH no servidor
ssh usuario@seu-servidor.com

# Mudar para usuário posemfoco
sudo -u posemfoco -i

# Clonar repositório
cd /opt/posemfoco
git clone https://github.com/seu-usuario/PosEmFoco.git .

# Ou para atualizações
git pull origin main
```

---

## 🗄️ PostgreSQL em Produção

### Otimizações

**Arquivo: `/etc/postgresql/12/main/postgresql.conf`**

```ini
# Conexões
max_connections = 200
shared_buffers = 256MB          # 25% da RAM

# Performance
effective_cache_size = 1GB      # 50% da RAM
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB

# Logs
log_min_duration_statement = 1000  # Log queries > 1s
log_statement = 'all'
```

Reiniciar:
```bash
sudo systemctl restart postgresql
```

### Backup Automático

**Cron job diário:**

```bash
# Arquivo: /etc/cron.d/posemfoco-backup
0 2 * * * posemfoco /usr/local/bin/backup_db.sh

# Script: /usr/local/bin/backup_db.sh
#!/bin/bash
BACKUP_DIR="/backups/posemfoco"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR
pg_dump -U posemfoco_user posemfoco > $BACKUP_DIR/posemfoco_$DATE.sql
gzip $BACKUP_DIR/posemfoco_$DATE.sql

# Manter apenas últimos 30 dias
find $BACKUP_DIR -type f -mtime +30 -delete
```

Teste:
```bash
chmod +x /usr/local/bin/backup_db.sh
/usr/local/bin/backup_db.sh
ls -lh /backups/posemfoco/
```

### Replicação (Failover)

Para alta disponibilidade:

```bash
# Server primário
pg_basebackup -h primario.com -D /var/lib/postgresql/backup -U replicator

# Server replica
# Configurar replication slot...
# (Avançado, fora do escopo deste doc)
```

---

## 🚀 FastAPI com Uvicorn

### Arquivo: `/opt/posemfoco/venv/bin/start.sh`

```bash
#!/bin/bash
cd /opt/posemfoco

# Ativar venv
source venv/bin/activate

# Start Uvicorn
uvicorn server:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --log-level info \
    --access-log
```

Permissões:
```bash
chmod +x /opt/posemfoco/venv/bin/start.sh
```

### Systemd Service

**Arquivo: `/etc/systemd/system/posemfoco.service`**

```ini
[Unit]
Description=PósEmFoco API
After=network.target postgresql.service

[Service]
Type=notify
User=posemfoco
WorkingDirectory=/opt/posemfoco
ExecStart=/opt/posemfoco/venv/bin/start.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment="PATH=/opt/posemfoco/venv/bin"

[Install]
WantedBy=multi-user.target
```

Usar:
```bash
# Registrar
sudo systemctl daemon-reload
sudo systemctl enable posemfoco

# Iniciar
sudo systemctl start posemfoco

# Ver status
sudo systemctl status posemfoco

# Ver logs
sudo journalctl -u posemfoco -f
```

---

## 🔄 Nginx (Reverse Proxy)

### Instalação

```bash
sudo apt install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Configuração

**Arquivo: `/etc/nginx/sites-available/posemfoco`**

```nginx
upstream posemfoco_backend {
    # Load balancing entre múltiplos workers
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name posemfoco.exemplo.com www.posemfoco.exemplo.com;
    
    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name posemfoco.exemplo.com www.posemfoco.exemplo.com;
    
    # SSL (veja próxima seção)
    ssl_certificate /etc/letsencrypt/live/posemfoco.exemplo.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/posemfoco.exemplo.com/privkey.pem;
    
    # Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Segurança
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Limite de upload
    client_max_body_size 10M;
    
    # Proxy reverso
    location / {
        proxy_pass http://posemfoco_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Cache de arquivos estáticos
    location /static/ {
        alias /opt/posemfoco/frontend/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Ativar:
```bash
sudo ln -s /etc/nginx/sites-available/posemfoco \
           /etc/nginx/sites-enabled/posemfoco

sudo nginx -t  # Validar sintaxe
sudo systemctl reload nginx
```

---

## 🔒 SSL/HTTPS

### Let's Encrypt (Grátis)

```bash
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot certonly --nginx -d posemfoco.exemplo.com -d www.posemfoco.exemplo.com

# Auto-renew (cron automático)
sudo certbot renew --dry-run
```

### Verificar

```bash
curl https://posemfoco.exemplo.com
```

---

## 📊 Monitoramento

### Logs

**Nginx:**
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

**FastAPI (Systemd):**
```bash
sudo journalctl -u posemfoco -f
```

**PostgreSQL:**
```bash
tail -f /var/log/postgresql/postgresql-12-main.log
```

### Prometheus + Grafana (Futuro)

Integração avançada de métricas:

```python
# Adicionar em server.py
from prometheus_client import Counter, Histogram, generate_latest

login_counter = Counter('login_total', 'Total logins')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.post("/login")
def login(...):
    login_counter.inc()
    # ...

@app.get("/metrics")
def metrics():
    return generate_latest()
```

### Health Check

```python
@app.get("/health")
def health():
    try:
        # Testar BD
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503
```

---

## 💾 Backup e Recovery

### Backup Manual

```bash
# Dump completo
pg_dump -U posemfoco_user posemfoco > backup.sql

# Dump comprimido
pg_dump -U posemfoco_user posemfoco | gzip > backup.sql.gz

# Apenas dados (sem schema)
pg_dump -U posemfoco_user --data-only posemfoco > backup_data.sql
```

### Restaurar

```bash
# Do arquivo SQL
psql -U posemfoco_user posemfoco < backup.sql

# De arquivo comprimido
gunzip -c backup.sql.gz | psql -U posemfoco_user posemfoco
```

### Disaster Recovery

Se servidor cair:

```bash
# 1. Provisionar novo servidor
# 2. Instalar PostgreSQL
# 3. Restaurar BD
psql -U posemfoco_user posemfoco < backup.sql

# 4. Deploy código
git clone ... /opt/posemfoco

# 5. Iniciar serviço
sudo systemctl start posemfoco

# 6. Verificar
curl https://posemfoco.exemplo.com/health
```

---

## 🚨 Troubleshooting Produção

### API lenta

```bash
# 1. Ver logs
sudo journalctl -u posemfoco -f

# 2. Verificar CPU/Memória
top -p $(pgrep -f uvicorn | tr '\n' ',')

# 3. Aumentar workers
# Em start.sh: --workers 8

# 4. Reloadar
sudo systemctl restart posemfoco
```

### PostgreSQL lento

```bash
# Ver queries longas
psql -U posemfoco_user -d posemfoco -c "
  SELECT query, mean_exec_time 
  FROM pg_stat_statements 
  ORDER BY mean_exec_time DESC 
  LIMIT 10;
"

# Recriar índices
REINDEX TABLE usuario;
```

### Espaço em disco cheio

```bash
# Ver espaço
df -h

# Limpar logs antigos
sudo journalctl --vacuum-time=30d

# Limpar backups antigos
find /backups/posemfoco -type f -mtime +30 -delete
```

---

## 📈 Próximos Passos

- [Troubleshooting](../troubleshooting.md)
- [Monitoramento Avançado](#monitoramento) (Prometheus, Grafana)
- [Auto-scaling](#) (Kubernetes - futuro)

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
