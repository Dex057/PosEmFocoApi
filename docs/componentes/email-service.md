# 📧 Email Service

Documentação técnica do sistema de envio de notificações por email.

## 📋 Visão Geral

O Email Service é responsável por:
1. Conectar ao servidor SMTP do Gmail
2. Montar email em formato HTML
3. Enviar notificação ao usuário
4. Log de erros/sucesso

**Arquivo:** `app/services/email_service.py`

---

## 🔧 Código

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def enviar_notificacao(email_destinatario, titulo_edital, link, palavra_chave):
    """
    Envia notificação de novo edital por email.
    
    Args:
        email_destinatario: Email do usuário
        titulo_edital: Título do edital encontrado
        link: URL do edital
        palavra_chave: Palavra-chave que gerou match
    
    Returns:
        bool: True se enviou com sucesso, False caso contrário
    """
    
    email_sender = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD')
    
    try:
        # Conectar ao servidor SMTP
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(email_sender, password)
        
        # Montar email HTML
        mensagem = MIMEMultipart('alternative')
        mensagem['Subject'] = f"🎓 Novo Edital: {titulo_edital}"
        mensagem['From'] = email_sender
        mensagem['To'] = email_destinatario
        
        # Corpo em HTML
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; }}
                    .content {{ padding: 20px; }}
                    .link {{ background-color: #28a745; color: white; }}
                    a {{ color: #007bff; text-decoration: none; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎓 PósEmFoco</h1>
                        <p>Nova oportunidade de pós-graduação</p>
                    </div>
                    <div class="content">
                        <p>Olá!</p>
                        <p>Encontramos um novo edital que corresponde aos seus interesses:</p>
                        <h2>{titulo_edital}</h2>
                        <p><strong>Palavra-chave:</strong> {palavra_chave}</p>
                        <p>
                            <a href="{link}" class="link" style="padding: 10px 20px; display: inline-block; background-color: #28a745; color: white; border-radius: 5px;">
                                Ver Edital
                            </a>
                        </p>
                        <hr>
                        <p>Acompanhe o PósEmFoco para receber mais notificações!</p>
                        <p style="color: #666; font-size: 12px;">
                            Este é um email automático. Não responda este email.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Adicionar corpo
        parte_html = MIMEText(html, 'html')
        mensagem.attach(parte_html)
        
        # Enviar
        servidor.sendmail(email_sender, email_destinatario, mensagem.as_string())
        servidor.quit()
        
        print(f"[EMAIL] ✅ Email enviado para {email_destinatario}")
        return True
        
    except Exception as e:
        print(f"[EMAIL] ❌ Erro ao enviar email: {e}")
        return False
```

---

## 📊 Template de Email

O email enviado tem este formato:

```
╔═══════════════════════════════════════╗
║  🎓 PósEmFoco                        ║
║  Nova oportunidade de pós-graduação   ║
╚═══════════════════════════════════════╝

Olá!

Encontramos um novo edital que corresponde 
aos seus interesses:

┌─────────────────────────────────────┐
│ Mestrado em Computação              │
│ (Edital 2026/01)                    │
└─────────────────────────────────────┘

Palavra-chave: Computação

┌─────────────────────────────────────┐
│         [Ver Edital]                │
└─────────────────────────────────────┘

Acompanhe o PósEmFoco para receber mais!
```

---

## 🔐 Configuração

### Variáveis de Ambiente

**Arquivo: `.env`**

```env
EMAIL_ADDRESS=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_aplicativo
```

### Gerar Senha de Aplicativo

1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione:
   - App: **Mail**
   - Device: **Windows Computer** (ou seu SO)
3. Google gerará senha de 16 caracteres
4. Copie para `.env` em `EMAIL_PASSWORD`

**Importante:** NÃO é a senha da sua conta Gmail!

---

## 🧪 Testar Email

### Teste Manual

```python
from app.services.email_service import enviar_notificacao

resultado = enviar_notificacao(
    email_destinatario='seu_email@gmail.com',
    titulo_edital='Mestrado em Computação',
    link='https://www.ufpa.edu.br/edital-1',
    palavra_chave='Computação'
)

if resultado:
    print("✅ Email enviado com sucesso!")
else:
    print("❌ Erro ao enviar email")
```

### Via Linha de Comando

```bash
python -c "
from app.services.email_service import enviar_notificacao
enviar_notificacao(
    'seu_email@gmail.com',
    'Teste PósEmFoco',
    'https://example.com',
    'Teste'
)
"
```

---

## ⚠️ Troubleshooting

### SMTPAuthenticationError

**Erro:**
```
smtplib.SMTPAuthenticationError: (535, 'Email ou senha incorretos')
```

**Solução:**
1. Verifique EMAIL_PASSWORD é a senha de APP (não conta)
2. Gere nova senha em https://myaccount.google.com/apppasswords
3. Habilite 2FA no Gmail
4. Tente novamente

---

### Connection Timeout

**Erro:**
```
socket.timeout: _ssl.c:1102: The handshake operation timed out
```

**Solução:**
1. Verifique conexão internet
2. Tente outra rede (Wi-Fi ou dados)
3. Verificar firewall (porta 587 bloqueada?)
4. Usar VPN se Gmail bloqueado

---

### Email não chega

**Soluções em ordem:**
1. Verificar spam/lixeira
2. Verificar email está correto em BD
3. Testador manualmente (código acima)
4. Verificar logs: `journalctl -u posemfoco`
5. Verificar credenciais Gmail

---

## 🚀 Futuras Melhorias

- [ ] Templates de email dinâmicos
- [ ] Suporte WhatsApp
- [ ] Suporte Telegram
- [ ] Queue de emails (Redis)
- [ ] Histórico de notificações
- [ ] Preferências de frequência

---

**Versão:** 1.0.0 | **Última atualização:** 25/01/2026
"
