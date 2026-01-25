import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


load_dotenv()

class ServicoNotificacao:
    def __init__(self):
        self.email_remetente = os.getenv("EMAIL_REMETENTE")
        self.senha_app = os.getenv("EMAIL_SENHA")
        self.servidor_smtp = "smtp.gmail.com"
        self.porta = 587

    def notificar_usuario(self, usuario, editais_encontrados):
        if not editais_encontrados:
            return

        print(f"Preparando envio de e-mail para {usuario.email}...")

        
        msg = MIMEMultipart()
        msg['From'] = self.email_remetente
        msg['To'] = usuario.email
        msg['Subject'] = f"UFPA: {len(editais_encontrados)} Novos Editais Encontrados!"

        
        corpo_html = f"""
        <html>
          <body>
            <h2>Olá, {usuario.nome}!</h2>
            <p>Encontramos novos editais que combinam com seus interesses:</p>
            <ul>
        """

        for edital in editais_encontrados:
            if edital.link:
                corpo_html += f"<li><a href='{edital.link}'><strong>{edital.titulo}</strong></a></li>"
            else:
                corpo_html += f"<li>{edital.titulo}</li>"

        corpo_html += """
            </ul>
            <p><em>Este é um e-mail automático do seu Monitor de Editais.</em></p>
          </body>
        </html>
        """

        msg.attach(MIMEText(corpo_html, 'html'))

        # faz o Envio via SMTP
        try:
            server = smtplib.SMTP(self.servidor_smtp, self.porta)
            server.starttls() # Criptografa a conexão
            server.login(self.email_remetente, self.senha_app)
            texto_email = msg.as_string()
            server.sendmail(self.email_remetente, usuario.email, texto_email)
            
            print(f"E-mail enviado com sucesso para {usuario.email}")
            server.quit()
            
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            print("Verifique se a 'Senha de App' foi gerada corretamente.")