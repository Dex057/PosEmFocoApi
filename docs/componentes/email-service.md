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
        mensagem['Subject'] = f\"🎓 Novo Edital: {titulo_edital}\"\n        mensagem['From'] = email_sender\n        mensagem['To'] = email_destinatario\n        \n        # Corpo em HTML\n        html = f\"\"\"\n        <html>\n            <head>\n                <style>\n                    body {{ font-family: Arial, sans-serif; }}\n                    .container {{ max-width: 600px; margin: 0 auto; }}\n                    .header {{ background-color: #007bff; color: white; padding: 20px; }}\n                    .content {{ padding: 20px; }}\n                    .link {{ background-color: #28a745; color: white; }}\n                    a {{ color: #007bff; text-decoration: none; }}\n                </style>\n            </head>\n            <body>\n                <div class=\"container\">\n                    <div class=\"header\">\n                        <h1>🎓 PósEmFoco</h1>\n                        <p>Nova oportunidade de pós-graduação</p>\n                    </div>\n                    <div class=\"content\">\n                        <p>Olá!</p>\n                        <p>Encontramos um novo edital que corresponde aos seus interesses:</p>\n                        <h2>{titulo_edital}</h2>\n                        <p><strong>Palavra-chave:</strong> {palavra_chave}</p>\n                        <p>\n                            <a href=\"{link}\" class=\"link\" style=\"padding: 10px 20px; display: inline-block; background-color: #28a745; color: white; border-radius: 5px;\">\n                                Ver Edital\n                            </a>\n                        </p>\n                        <hr>\n                        <p>Acompanhe o PósEmFoco para receber mais notificações!</p>\n                        <p style=\"color: #666; font-size: 12px;\">\n                            Este é um email automático. Não responda este email.\n                        </p>\n                    </div>\n                </div>\n            </body>\n        </html>\n        \"\"\"\n        \n        # Adicionar corpo\n        parte_html = MIMEText(html, 'html')\n        mensagem.attach(parte_html)\n        \n        # Enviar\n        servidor.sendmail(email_sender, email_destinatario, mensagem.as_string())\n        servidor.quit()\n        \n        print(f\"[EMAIL] ✅ Email enviado para {email_destinatario}\")\n        return True\n        \n    except Exception as e:\n        print(f\"[EMAIL] ❌ Erro ao enviar email: {e}\")\n        return False
```

---

## 📊 Template de Email

O email enviado tem este formato:

```
╔═══════════════════════════════════════╗
║  🎓 PósEmFoco                        ║\n║  Nova oportunidade de pós-graduação   ║\n╚═══════════════════════════════════════╝\n\nOlá!\n\nEncontramos um novo edital que corresponde \naos seus interesses:\n\n┌─────────────────────────────────────┐\n│ Mestrado em Computação              │\n│ (Edital 2026/01)                    │\n└─────────────────────────────────────┘\n\nPalavra-chave: Computação\n\n┌─────────────────────────────────────┐\n│         [Ver Edital]                │\n└─────────────────────────────────────┘\n\nAcompanhe o PósEmFoco para receber mais!\n```

---\n\n## 🔐 Configuração\n\n### Variáveis de Ambiente\n\n**Arquivo: `.env`**\n\n```env\nEMAIL_ADDRESS=seu_email@gmail.com\nEMAIL_PASSWORD=sua_senha_de_aplicativo\n```\n\n### Gerar Senha de Aplicativo\n\n1. Acesse: https://myaccount.google.com/apppasswords\n2. Selecione:\n   - App: **Mail**\n   - Device: **Windows Computer** (ou seu SO)\n3. Google gerará senha de 16 caracteres\n4. Copie para `.env` em `EMAIL_PASSWORD`\n\n**Importante:** NÃO é a senha da sua conta Gmail!\n\n---\n\n## 🧪 Testar Email\n\n### Teste Manual\n\n```python\nfrom app.services.email_service import enviar_notificacao\n\nresultado = enviar_notificacao(\n    email_destinatario='seu_email@gmail.com',\n    titulo_edital='Mestrado em Computação',\n    link='https://www.ufpa.edu.br/edital-1',\n    palavra_chave='Computação'\n)\n\nif resultado:\n    print(\"✅ Email enviado com sucesso!\")\nelse:\n    print(\"❌ Erro ao enviar email\")\n```

### Via Linha de Comando\n\n```bash\npython -c \"\nfrom app.services.email_service import enviar_notificacao\nenviar_notificacao(\n    'seu_email@gmail.com',\n    'Teste PósEmFoco',\n    'https://example.com',\n    'Teste'\n)\n\"\n```\n\n---\n\n## ⚠️ Troubleshooting\n\n### SMTPAuthenticationError\n\n**Erro:**\n```\nsmtplib.SMTPAuthenticationError: (535, 'Email ou senha incorretos')\n```\n\n**Solução:**\n1. Verifique EMAIL_PASSWORD é a senha de APP (não conta)\n2. Gere nova senha em https://myaccount.google.com/apppasswords\n3. Habilite 2FA no Gmail\n4. Tente novamente\n\n---\n\n### Connection Timeout\n\n**Erro:**\n```\nsocket.timeout: _ssl.c:1102: The handshake operation timed out\n```\n\n**Solução:**\n1. Verifique conexão internet\n2. Tente outra rede (Wi-Fi ou dados)\n3. Verificar firewall (porta 587 bloqueada?)\n4. Usar VPN se Gmail bloqueado\n\n---\n\n### Email não chega\n\n**Soluções em ordem:**\n1. Verificar spam/lixeira\n2. Verificar email está correto em BD\n3. Testador manualmente (código acima)\n4. Verificar logs: `journalctl -u posemfoco`\n5. Verificar credenciais Gmail\n\n---\n\n## 🚀 Futuras Melhorias\n\n- [ ] Templates de email dinâmicos\n- [ ] Suporte WhatsApp\n- [ ] Suporte Telegram\n- [ ] Queue de emails (Redis)\n- [ ] Histórico de notificações\n- [ ] Preferências de frequência\n\n---\n\n**Versão:** 1.0.0 | **Última atualização:** 25/01/2026\n"
