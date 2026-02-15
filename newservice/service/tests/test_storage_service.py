import uuid
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework.test import APIRequestFactory

# Import all models that have managed = False
from service.models import Estudante, Curriculo, Utilizador, Area, AreaEstudante, Cr, Empresa, Vaga
from service.views import CurriculoViewSet
from service.services.storage_service import SupabaseStorageService
from service.services.exceptions import StorageUploadException, StorageSignedUrlException

# --- THE FIX ---
# This loop forces Django to create tables for unmanaged models in the test DB
UNMANAGED_MODELS = [Area, AreaEstudante, Cr, Curriculo, Empresa, Estudante, Utilizador, Vaga]
for model in UNMANAGED_MODELS:
    model._meta.managed = True
# ---------------

class UploadCVTest(TestCase):
    def setUp(self):
        # IMPORTANT: Run without --keepdb at least once after adding the fix above
        # so Django creates the tables.
        self.factory = APIRequestFactory()
        
        self.supabase_id = str(uuid.uuid4())
        self.utilizador = Utilizador.objects.create(
            auth_user_supabase_id=self.supabase_id,
            nome="Test User",
            tipo=2
        )

        self.estudante = Estudante.objects.create(
            utilizador_auth_user_supabase_field=self.utilizador,
            share_aceites=True
        )

    @patch("service.views.IsStudent.has_permission", return_value=True)
    @patch("service.services.storage_service.SupabaseStorageService.upload_file")
    def test_upload_cv_success(self, mock_upload_file, mock_perm):
        mock_upload_file.return_value = f"user/{self.supabase_id}/cv.pdf"

        fake_file = SimpleUploadedFile(
            name="cv.pdf",
            content=b"%PDF-1.4 content",
            content_type="application/pdf",
        )
        
        request = self.factory.post("/curriculo/me/", {"cv": fake_file}, format="multipart")
        request.user_id = self.supabase_id
        request.role = 2 

        view = CurriculoViewSet.as_view({"post": "get_my_cv"})
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Curriculo.objects.filter(estudante_utilizador_auth_user_supabase_field=self.estudante).exists())

# (Keep the SupabaseStorageServiceTest class as it was)
# ======================================================
# Supabase Storage Service — UNIT TESTS
# ======================================================
class SupabaseStorageServiceTest(TestCase):

    def setUp(self):
        patcher = patch("service.services.storage_service.create_client")
        self.addCleanup(patcher.stop)
        self.mock_create_client = patcher.start()

        self.mock_client = MagicMock()
        self.mock_create_client.return_value = self.mock_client
        self.service = SupabaseStorageService()

    def test_upload_file_success(self):
        storage_chain = self.mock_client.storage.from_.return_value
        storage_chain.upload.return_value = {"path": "user/123/cv.pdf"}

        result = self.service.upload_file(
            file=b"fake content",
            bucket_name="cvs",
            file_path="user/123/cv.pdf",
        )

        self.assertEqual(result, "user/123/cv.pdf")

    def test_upload_file_without_file_raises(self):
        with self.assertRaises(StorageUploadException):
            self.service.upload_file(
                file=None, bucket_name="cvs", file_path="cv.pdf"
            )

    def test_delete_file_success(self):
        storage_chain = self.mock_client.storage.from_.return_value
        storage_chain.remove.return_value = {}
        self.service.delete_file("cvs", "cv.pdf")
        storage_chain.remove.assert_called_once_with(["cv.pdf"])

    def test_get_signed_url_failure(self):
        storage_chain = self.mock_client.storage.from_.return_value
        storage_chain.create_signed_url.return_value = {"error": {"message": "Not found"}}

        with self.assertRaises(StorageSignedUrlException):
            self.service.get_signed_url("cvs", "cv.pdf")