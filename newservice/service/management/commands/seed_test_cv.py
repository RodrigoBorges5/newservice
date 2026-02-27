"""
comando de teste para criar dados de teste para o fluxo de email de CV.

cria um user no Supabase Auth - Utilizador - Estudante - Currículo (pendente)
para que se possa testar POST /curriculo/{id}/review/ com envio de email.

Uso:
    python manage.py seed_test_cv
    python manage.py seed_test_cv --email outro@email.com --nome "Outro Nome"
"""

import uuid
import os

from django.core.management.base import BaseCommand
from django.utils import timezone
from supabase import create_client

from service.models import Utilizador, Estudante, Curriculo


class Command(BaseCommand):
    help = "Cria user no Supabase Auth + utilizador + estudante + CV pendente para teste de email."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            default="diogorodrigues@student.dei.uc.pt",
            help="Email do estudante de teste (default: diogorodrigues@student.dei.uc.pt)",
        )
        parser.add_argument(
            "--nome",
            default="Diogo Rodrigues",
            help="Nome do estudante de teste",
        )
        parser.add_argument(
            "--uuid",
            default=None,
            help="UUID específico para o utilizador (opcional — usa UUID do Supabase Auth)",
        )

    def _get_or_create_supabase_user(self, email, nome):
        """
        Cria (ou encontra) um utilizador no Supabase Auth.
        Retorna o UUID do utilizador.
        """
        url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not url or not service_key:
            raise RuntimeError(
                "SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar definidos no .env"
            )

        admin_client = create_client(url, service_key)

        # Tentar encontrar o utilizador existente pelo email
        try:
            # Listar users e procurar pelo email
            users_response = admin_client.auth.admin.list_users()
            for user in users_response:
                if hasattr(user, "email") and user.email == email:
                    self.stdout.write(
                        f"  [Supabase]   User já existe no Auth: {email} (UUID={user.id})"
                    )
                    return uuid.UUID(str(user.id))
        except Exception:
            pass  # Se falhar a listagem, tenta criar

        # Criar novo utilizador
        response = admin_client.auth.admin.create_user(
            {
                "email": email,
                "password": "test-password-123!",
                "email_confirm": True,
                "user_metadata": {"nome": nome},
            }
        )
        user_id = uuid.UUID(str(response.user.id))
        self.stdout.write(
            f"  [Supabase]   User criado no Auth: {email} (UUID={user_id})"
        )
        return user_id

    def handle(self, *args, **options):
        email = options["email"]
        nome = options["nome"]

        self.stdout.write(self.style.NOTICE(f"\n{'=' * 60}"))
        self.stdout.write(self.style.NOTICE("  Seed: Dados de teste para email de CV"))
        self.stdout.write(self.style.NOTICE(f"{'=' * 60}\n"))

        # 0) Criar/encontrar user no Supabase Auth
        if options["uuid"]:
            user_uuid = uuid.UUID(options["uuid"])
            self.stdout.write(f"  [Supabase]   UUID fornecido manualmente: {user_uuid}")
        else:
            user_uuid = self._get_or_create_supabase_user(email, nome)

        # 1) Utilizador
        utilizador, u_created = Utilizador.objects.get_or_create(
            auth_user_supabase_id=user_uuid,
            defaults={
                "nome": nome,
                "descricao": "Estudante de teste para validação de email",
                "tipo": 2,  # Estudante
            },
        )
        action = "Criado" if u_created else "Já existia"
        self.stdout.write(
            f"  [Utilizador] {action}: {utilizador.nome} (UUID={user_uuid})"
        )

        # 2) Estudante
        estudante, e_created = Estudante.objects.get_or_create(
            utilizador_auth_user_supabase_field=utilizador,
            defaults={
                "tipo": 2,
                "idade": 22,
                "grau": "Licenciatura",
                "ano": 3,
                "disponibilidade": "full-time",
                "share_aceites": True,
            },
        )
        action = "Criado" if e_created else "Já existia"
        self.stdout.write(
            f"  [Estudante]  {action}: grau={estudante.grau}, ano={estudante.ano}"
        )

        # 3) Currículo pendente
        curriculo = Curriculo.objects.create(
            estudante_utilizador_auth_user_supabase_field=estudante,
            file=f"estudante_{user_uuid}/cv_teste.pdf",
            status=Curriculo.CV_STATUS_PENDING,
            creation_date=timezone.now().date(),
        )
        self.stdout.write(f"  [Currículo]  Criado: id={curriculo.id}, status=pendente")

        self.stdout.write(self.style.SUCCESS(f"\n{'=' * 60}"))
        self.stdout.write(self.style.SUCCESS("  Dados criados com sucesso!"))
        self.stdout.write(self.style.SUCCESS(f"{'=' * 60}"))
        self.stdout.write(f"""
  Para testar o review (aprovação):
    POST /curriculo/{curriculo.id}/review/
    Header: X-User-Id: <uuid-de-um-CR>
    Body:   {{"status": 1}}

  Para testar o review (rejeição):
    POST /curriculo/{curriculo.id}/review/
    Header: X-User-Id: <uuid-de-um-CR>
    Body:   {{"status": 2, "feedback": "O CV precisa de foto profissional."}}

  UUID do estudante: {user_uuid}
  Email esperado:    {email}

  NOTA: Como o utilizador NÃO existe no Supabase Auth,
  a procura de email vai falhar. A task vai usar o email
  passado via recipient_email (para rejeição) ou o
  fallback de DEBUG (estudante+<uuid>@teste.local).

  Para garantir envio ao email correto, vamos criar um
  override — ver instruções abaixo.
""")
