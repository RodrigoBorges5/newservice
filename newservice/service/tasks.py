"""
Task assíncrona para notificações de email sobre status de CV.

Envia notificações por email aos estudantes quando o estado do seu currículo
é alterado (aprovado ou rejeitado) pela equipa CR.

Utiliza o sistema de tasks do Django (django.tasks) para execução assíncrona
e o Supabase Auth para obter o email do estudante.

Tipos de estado do Currículo:
    0 = Pendente (submissão inicial)
    1 = Aprovado
    2 = Rejeitado
"""

import logging
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.tasks import task

from .models import Curriculo, Notification

logger = logging.getLogger(__name__)

# Mapeamento de status para labels legíveis
STATUS_LABELS = {
    1: "Aprovado",
    2: "Rejeitado",
}


def _get_student_email(user_uuid: str) -> str:
    """
    Obtém o email do estudante via Supabase Auth.
    Função wrapper que usa a função centralizada do supabase_client.

    Args:
        user_uuid: UUID do utilizador no Supabase Auth.

    Returns:
        O endereço de email do estudante.

    Raises:
        ValueError: Se o email não for encontrado e DEBUG=False.
    """
    from service.supabase_client import get_user_email
    return get_user_email(user_uuid)


def _render_email(status: int, context: dict) -> tuple[str, str]:
    """
    Renderiza o template de email apropriado com base no status.

    Args:
        status: Novo status do currículo (1=Aprovado, 2=Rejeitado).
        context: Variáveis de contexto para o template.

    Returns:
        Tupla (html_content, plain_text_content).
    """
    template_map = {
        1: "email/cv_aprovado.html",
        2: "email/cv_rejeitado.html",
    }

    template_name = template_map[status]
    html_content = render_to_string(template_name, context)
    plain_text = strip_tags(html_content)

    return html_content, plain_text


def send_cv_status_notification(
    curriculo_id: int,
    status: int,
    feedback: str = "",
) -> dict:
    """
    Task assíncrona que envia notificação por email ao estudante
    quando o status do seu currículo é alterado.

    Args:
        curriculo_id: ID do currículo validado.
        status: Novo status (1=Aprovado, 2=Rejeitado).
        feedback: Comentário do CR (opcional para aprovação,
                  obrigatório para rejeição).

    Returns:
        Dicionário com resultado do envio:
            - success (bool)
            - curriculo_id (int)
            - status (str)
            - email (str)
            - message (str)

    Raises:
        ValueError: Se os parâmetros forem inválidos.
    """
    log_prefix = f"[CV Notification] curriculo_id={curriculo_id}"

    # ── Validação de parâmetros ──────────────────────────────────────
    if status not in (1, 2):
        msg = f"Status inválido: {status}. Deve ser 1 (Aprovado) ou 2 (Rejeitado)."
        logger.error("%s %s", log_prefix, msg)
        raise ValueError(msg)

    if status == 2 and not feedback:
        msg = "Feedback é obrigatório para rejeição."
        logger.error("%s %s", log_prefix, msg)
        raise ValueError(msg)

    # ── Procurar currículo e dados do estudante ────────────────────────
    try:
        curriculo = Curriculo.objects.select_related(
            "estudante_utilizador_auth_user_supabase_field"
            "__utilizador_auth_user_supabase_field"
        ).get(id=curriculo_id)
    except Curriculo.DoesNotExist:
        msg = f"Currículo com ID {curriculo_id} não encontrado."
        logger.error("%s %s", log_prefix, msg)
        raise ValueError(msg)

    estudante = curriculo.estudante_utilizador_auth_user_supabase_field
    utilizador = estudante.utilizador_auth_user_supabase_field
    user_uuid = str(utilizador.auth_user_supabase_id)
    nome_estudante = utilizador.nome or "Estudante"

    logger.info(
        "%s A iniciar envio – status=%s, estudante=%s",
        log_prefix,
        STATUS_LABELS.get(status, status),
        nome_estudante,
    )

    # ── Obter email via Supabase Auth ────────────────────────────────
    try:
        email = _get_student_email(user_uuid)
    except Exception as e:
        logger.error("%s Falha ao obter email: %s", log_prefix, e)
        # Registar notificação falhada (sem email)
        Notification.objects.create(
            recipient_user_id=user_uuid,
            recipient_email="",
            type="cv_status_change",
            subject=f"CV {STATUS_LABELS.get(status, str(status))}",
            status="failed",
            error_message=f"Falha ao obter email: {e}",
            curriculo_id=curriculo_id,
        )
        return {
            "success": False,
            "curriculo_id": curriculo_id,
            "status": STATUS_LABELS.get(status, str(status)),
            "email": None,
            "message": f"Falha ao obter email: {e}",
        }

    # ── Preparar contexto e renderizar template ──────────────────────
    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")

    subject_map = {
        1: "🎉 O teu currículo foi aprovado!",
        2: "Resultado da validação do teu currículo",
    }

    context = {
        "nome_estudante": nome_estudante,
        "feedback": feedback,
        "site_url": site_url,
        "ano_atual": datetime.now().year,
    }

    try:
        html_content, plain_text = _render_email(status, context)
    except Exception as e:
        logger.error("%s Falha ao renderizar template: %s", log_prefix, e)
        Notification.objects.create(
            recipient_user_id=user_uuid,
            recipient_email=email,
            type="cv_status_change",
            subject=subject_map.get(status, "Notificação de CV"),
            status="failed",
            error_message=f"Falha ao renderizar template: {e}",
            curriculo_id=curriculo_id,
        )
        return {
            "success": False,
            "curriculo_id": curriculo_id,
            "status": STATUS_LABELS.get(status, str(status)),
            "email": email,
            "message": f"Falha ao renderizar template: {e}",
        }

    # ── Enviar email ─────────────────────────────────────────────────
    try:
        send_mail(
            subject=subject_map[status],
            message=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False,
        )

        logger.info(
            "%s Email enviado com sucesso para %s (status=%s)",
            log_prefix,
            email,
            STATUS_LABELS[status],
        )

        # Registar notificação enviada com sucesso
        Notification.objects.create(
            recipient_user_id=user_uuid,
            recipient_email=email,
            type="cv_status_change",
            subject=subject_map[status],
            status="sent",
            curriculo_id=curriculo_id,
        )

        return {
            "success": True,
            "curriculo_id": curriculo_id,
            "status": STATUS_LABELS[status],
            "email": email,
            "message": "Email enviado com sucesso.",
        }

    except Exception as e:
        logger.error(
            "%s Falha ao enviar email para %s: %s",
            log_prefix,
            email,
            e,
        )

        # Registar notificação falhada
        Notification.objects.create(
            recipient_user_id=user_uuid,
            recipient_email=email,
            type="cv_status_change",
            subject=subject_map[status],
            status="failed",
            error_message=str(e),
            curriculo_id=curriculo_id,
        )

        return {
            "success": False,
            "curriculo_id": curriculo_id,
            "status": STATUS_LABELS.get(status, str(status)),
            "email": email,
            "message": f"Falha ao enviar email: {e}",
        }
