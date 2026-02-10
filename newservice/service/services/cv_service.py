"""
Service layer para operações de Currículo (CV).
Separa lógica de negócio das views.
"""
from rest_framework.response import Response
from rest_framework import status

from service.models import CVAccessLog, CV_STATUS_LABELS
from service.serializers import CVSignedUrlSerializer
from service.services.storage_service import SupabaseStorageService
from service.services.exceptions import StorageSignedUrlException


class CVService:
    """Service para operações relacionadas com CVs."""
    
    def __init__(self):
        self.storage_service = SupabaseStorageService()
        self.bucket_name = "cvs"
    
    def get_signed_url_for_curriculo(self, curriculo, user_id, user_role):
        """
        Gera URL assinada para um CV e registra auditoria.
        
        Args:
            curriculo: Instância de Curriculo
            user_id: UUID do utilizador
            user_role: Role do utilizador (0=CR, 1=Empresa, 2=Estudante)
        
        Returns:
            str: URL assinada ou None em caso de erro
        """
        if not curriculo.file:
            return None
        
        try:
            signed_url = self.storage_service.get_signed_url(
                bucket_name=self.bucket_name,
                file_path=curriculo.file,
                expiration_seconds=900
            )
            
            # Registar acesso na auditoria
            self._log_cv_access(curriculo, user_id, user_role)
            
            return signed_url
        except (StorageSignedUrlException, Exception):
            return None
    
    def generate_signed_url_response(self, curriculo, user_id, user_role):
        """
        Gera Response completa com URL assinada e metadata do CV.
        
        Args:
            curriculo: Instância de Curriculo
            user_id: UUID do utilizador
            user_role: Role do utilizador (0=CR, 1=Empresa, 2=Estudante)
        
        Returns:
            Response: Response DRF com signed_url + metadata ou erro
        """
        # Validar que o ficheiro existe no storage
        if not curriculo.file:
            return Response(
                {"detail": "Caminho do ficheiro não configurado (inconsistência de dados)."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Gerar signed URL (já registra auditoria)
        signed_url = self.get_signed_url_for_curriculo(curriculo, user_id, user_role)
        
        if not signed_url:
            return Response(
                {"detail": "Erro ao gerar URL assinada para visualização."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Preparar resposta
        response_data = {
            "id": curriculo.id,
            "signed_url": signed_url,
            "status": curriculo.status,
            "status_label": CV_STATUS_LABELS.get(curriculo.status, 'desconhecido'),
            "validated_date": curriculo.validated_date,
            "expires_in_seconds": 900
        }
        
        serializer = CVSignedUrlSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def _log_cv_access(self, curriculo, user_id, user_role):
        """
        Registra acesso ao CV na tabela de auditoria.
        
        Args:
            curriculo: Instância de Curriculo
            user_id: UUID do utilizador
            user_role: Role do utilizador
        """
        try:
            CVAccessLog.objects.create(
                curriculo=curriculo,
                accessed_by_user_id=user_id,
                accessed_by_role=user_role
            )
        except Exception:
            # Log falhou, mas não impede visualização
            # Em produção, considere alertar/logar
            pass
