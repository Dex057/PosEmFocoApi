"""Envia um e-mail de teste usando as credenciais do .env (EMAIL_ADDRESS/EMAIL_PASSWORD).
Uso: python testar_email.py destinatario@exemplo.com
"""
import sys

from app.services.email_service import enviar_notificacao

if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else input("E-mail de destino para o teste: ")
    enviar_notificacao(
        destino,
        "Edital de Teste - PósEmFoco",
        "https://exemplo.com/edital-teste",
        "teste",
    )
