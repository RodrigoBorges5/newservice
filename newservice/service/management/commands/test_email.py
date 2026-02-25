"""
coamndo de teste para testar envio de email SMTP.

envia um email de teste para verificar que a configuração SMTP
está funcional antes de testar o fluxo completo de review.

Uso:
    python manage.py test_email diogorodrigues@student.dei.uc.pt
"""

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Envia um email de teste para verificar a configuração SMTP."

    def add_arguments(self, parser):
        parser.add_argument(
            "to_email",
            help="Endereço de email de destino para o teste.",
        )

    def handle(self, *args, **options):
        to_email = options["to_email"]

        self.stdout.write(f"\nBackend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Host:    {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        self.stdout.write(f"From:    {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"TLS:     {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"To:      {to_email}\n")

        try:
            send_mail(
                subject="[Teste] Configuração SMTP — New Service",
                message="Se estás a ler este email, a configuração SMTP está funcional!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=(
                    "<h2>Teste SMTP</h2>"
                    "<p>Se estás a ler este email, a configuração SMTP está "
                    "<strong>funcional</strong>! 🎉</p>"
                ),
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("Email enviado com sucesso!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Falha ao enviar email: {e}"))
