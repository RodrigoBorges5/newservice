"""
Testes para o endpoint de notificações.

Cobre:
    - Listagem (GET) com permissões por role
    - Filtros: type, status, date_from, date_to, student
    - Ordenação e paginação
    - Marcação como lida (PATCH)
    - Proteção de acesso entre utilizadores
"""

import uuid
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from service.models import Notification


# UUIDs de teste
STUDENT_UUID = str(uuid.uuid4())
STUDENT_UUID_2 = str(uuid.uuid4())
CR_UUID = str(uuid.uuid4())
COMPANY_UUID = str(uuid.uuid4())

# Mapeamento role por UUID (usado pelo mock do middleware)
ROLE_MAP = {
    STUDENT_UUID: 2,    # Estudante
    STUDENT_UUID_2: 2,  # Segundo estudante
    CR_UUID: 0,         # CR
    COMPANY_UUID: 1,    # Empresa
}


def _mock_get_user_role(user_id):
    """Mock para get_user_role – devolve role conforme ROLE_MAP."""
    role = ROLE_MAP.get(user_id)
    if role is None:
        from service.supabase_client import UserNotFoundError
        raise UserNotFoundError(f"Utilizador {user_id} não encontrado")
    return role


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
)
@patch("service.middleware.get_user_role", side_effect=_mock_get_user_role)
class NotificationEndpointTests(TestCase):
    """Testes para GET /curriculo/notifications/ e PATCH /curriculo/notifications/{id}/."""

    def setUp(self):
        self.client = APIClient()
        self.base_url = "/service/curriculo/notifications/"

        now = timezone.now()

        # ── Notificações do estudante 1 ──────────────────────────────
        self.notif_1 = Notification.objects.create(
            recipient_user_id=STUDENT_UUID,
            recipient_email="aluno1@teste.local",
            type="cv_status_change",
            subject="CV Aprovado",
            status="sent",
            read=False,
        )
        self.notif_2 = Notification.objects.create(
            recipient_user_id=STUDENT_UUID,
            recipient_email="aluno1@teste.local",
            type="cv_feedback",
            subject="Feedback do CV",
            status="failed",
            error_message="SMTP timeout",
            read=True,
        )
        # Forçar data diferente para testes de filtro por data
        Notification.objects.filter(pk=self.notif_2.pk).update(
            created_at=now - timedelta(days=5)
        )
        self.notif_2.refresh_from_db()

        # ── Notificação do estudante 2 ───────────────────────────────
        self.notif_3 = Notification.objects.create(
            recipient_user_id=STUDENT_UUID_2,
            recipient_email="aluno2@teste.local",
            type="cv_status_change",
            subject="CV Rejeitado",
            status="sent",
            read=False,
        )

    # ================================================================
    # 1. Estudante vê apenas as suas notificações
    # ================================================================
    def test_student_list_own_notifications(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        resp = self.client.get(self.base_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [n["id"] for n in resp.data["results"]]
        self.assertIn(self.notif_1.id, ids)
        self.assertIn(self.notif_2.id, ids)
        self.assertNotIn(self.notif_3.id, ids)

    # ================================================================
    # 2. CR vê todas as notificações
    # ================================================================
    def test_cr_list_all_notifications(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = CR_UUID
        resp = self.client.get(self.base_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [n["id"] for n in resp.data["results"]]
        self.assertEqual(len(ids), 3)

    # ================================================================
    # 3. Empresa recebe 403
    # ================================================================
    def test_company_forbidden(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = COMPANY_UUID
        resp = self.client.get(self.base_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ================================================================
    # 4. Filtro por type
    # ================================================================
    def test_filter_by_type(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        resp = self.client.get(self.base_url, {"type": "cv_feedback"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [n["id"] for n in resp.data["results"]]
        self.assertEqual(ids, [self.notif_2.id])

    # ================================================================
    # 5. Filtro por status
    # ================================================================
    def test_filter_by_status(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        resp = self.client.get(self.base_url, {"status": "failed"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [n["id"] for n in resp.data["results"]]
        self.assertEqual(ids, [self.notif_2.id])

    # ================================================================
    # 6. Filtro por date_from
    # ================================================================
    def test_filter_by_date_from(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        date_str = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        resp = self.client.get(self.base_url, {"date_from": date_str})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [n["id"] for n in resp.data["results"]]
        # notif_2 was created 5 days ago – should be excluded
        self.assertIn(self.notif_1.id, ids)
        self.assertNotIn(self.notif_2.id, ids)

    # ================================================================
    # 7. Filtro por date_to
    # ================================================================
    def test_filter_by_date_to(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        date_str = (timezone.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        resp = self.client.get(self.base_url, {"date_to": date_str})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [n["id"] for n in resp.data["results"]]
        # notif_2 was created 5 days ago – should be included
        self.assertIn(self.notif_2.id, ids)
        self.assertNotIn(self.notif_1.id, ids)

    # ================================================================
    # 8. CR filtra por student UUID
    # ================================================================
    def test_cr_filter_by_student(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = CR_UUID
        resp = self.client.get(self.base_url, {"student": STUDENT_UUID_2})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [n["id"] for n in resp.data["results"]]
        self.assertEqual(ids, [self.notif_3.id])

    # ================================================================
    # 9. Ordenação por created_at ascendente
    # ================================================================
    def test_ordering_created_at_asc(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        resp = self.client.get(self.base_url, {"ordering": "created_at"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [n["id"] for n in resp.data["results"]]
        # notif_2 is older → should come first
        self.assertEqual(ids[0], self.notif_2.id)

    # ================================================================
    # 10. Paginação
    # ================================================================
    def test_pagination(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = CR_UUID
        resp = self.client.get(self.base_url, {"page_size": 2})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 2)
        self.assertIn("next", resp.data)
        self.assertIsNotNone(resp.data["next"])

    # ================================================================
    # 11. PATCH – estudante marca a sua notificação como lida
    # ================================================================
    def test_student_mark_as_read(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        url = f"{self.base_url}{self.notif_1.id}/"
        resp = self.client.patch(url, {"read": True}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.notif_1.refresh_from_db()
        self.assertTrue(self.notif_1.read)

    # ================================================================
    # 12. PATCH – estudante NÃO pode alterar notificação de outro
    # ================================================================
    def test_student_cannot_mark_others_notification(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        url = f"{self.base_url}{self.notif_3.id}/"
        resp = self.client.patch(url, {"read": True}, format="json")
        # notif_3 pertence a STUDENT_UUID_2 → 404 (queryset filtrado)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # ================================================================
    # 13. PATCH – CR pode marcar qualquer notificação
    # ================================================================
    def test_cr_mark_any_notification_as_read(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = CR_UUID
        url = f"{self.base_url}{self.notif_3.id}/"
        resp = self.client.patch(url, {"read": True}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.notif_3.refresh_from_db()
        self.assertTrue(self.notif_3.read)

    # ================================================================
    # 14. Sem X-User-ID recebe 401
    # ================================================================
    def test_unauthenticated_returns_401(self, mock_role):
        resp = self.client.get(self.base_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # ================================================================
    # 15. POST não é permitido (read-only + PATCH)
    # ================================================================
    def test_post_not_allowed(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        resp = self.client.post(self.base_url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ================================================================
    # 16. DELETE não é permitido
    # ================================================================
    def test_delete_not_allowed(self, mock_role):
        self.client.defaults["HTTP_X_USER_ID"] = STUDENT_UUID
        url = f"{self.base_url}{self.notif_1.id}/"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
