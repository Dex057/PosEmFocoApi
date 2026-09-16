import smtplib
import ssl
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_REMETENTE = os.getenv("EMAIL_ADDRESS")
SENHA_APP = os.getenv("EMAIL_PASSWORD")


def enviar_notificacao(email_destinatario, titulo_edital, link_edital, palavra_chave, universidade="instituição"):

    msg = EmailMessage()
    msg['Subject'] = f"PosEmFoco: Novo edital encontrado ({palavra_chave})"
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = email_destinatario


    conteudo_texto = f"""
    Ola!
    
    Encontramos um novo edital compativel com seu interesse: "{palavra_chave}".

    Instituicao: {universidade}
    Titulo: {titulo_edital}
    Link: {link_edital}
    
    Acesse o link acima para mais detalhes.
    """
    msg.set_content(conteudo_texto)

    
    conteudo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }}
            .header {{ background-color: #004b8d; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .card {{ background: white; padding: 15px; border-left: 5px solid #004b8d; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .btn {{ display: inline-block; background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
            .footer {{ text-align: center; font-size: 12px; color: #777; padding: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Novo Edital Encontrado!</h2>
            </div>
            <div class="content">
                <p>Olá,</p>
                <p>O robô do <strong>PósEmFoco</strong> acabou de encontrar uma oportunidade baseada no seu interesse em: <strong style="color: #d9534f;">{palavra_chave}</strong>.</p>
                
                <div class="card">
                    <h3>{titulo_edital}</h3>
                    <p style="color: #666; font-size: 14px;">Publicado por: <strong>{universidade}</strong></p>
                    <p><a href="{link_edital}" class="btn" style="color: white;">Acessar Edital</a></p>
                </div>

                <p>Clique no botão acima para ver todos os detalhes no site da {universidade}.</p>
            </div>
            <div class="footer">
                <p>Este é um e-mail automático do sistema PósEmFoco.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    
    msg.add_alternative(conteudo_html, subtype='html')

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_REMETENTE, SENHA_APP)
            smtp.send_message(msg)
            print(f"   -> E-mail enviado para {email_destinatario}")
    except Exception as e:
        print(f"   -> Erro ao enviar e-mail: {e}")