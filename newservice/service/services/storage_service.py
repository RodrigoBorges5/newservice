from django.conf import settings

from service.services.exceptions import StorageUploadException, StorageDeleteException, StorageSignedUrlException


from supabase import create_client


class SupabaseStorageService:
    """
    Service layer responsible for interacting with Supabase Storage.
    Encapsulates upload, delete and signed URL generation.
    """

    def __init__(self):
        self.client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )

    def upload_file(self, file, bucket_name: str, file_path: str) -> str:
        """
        Uploads dos ficheiros.

        Args:
            file: Ficheiro a fazer upload.
            bucket_name (str): Nome do bucket.
            file_path (str): Caminho onde o ficheiro será armazenado.

        Devolve:
            str: caminho do ficheiro.

        Erros:
            StorageUploadException: Se o upload falhar ou o ficheiro for inválido.
        """
        if not file:
            raise StorageUploadException("Ficheiro nulo")

        try:
            file_bytes = file.read()

            response = self.client.storage.from_(bucket_name).upload(
                path=file_path,
                file=file_bytes,
                file_options={
                    "content-type": file.content_type,
                    "upsert": "true",
                },
            )

        except Exception as exc:
            raise StorageUploadException(str(exc)) from exc

    def delete_file(self, bucket_name: str, file_path: str) -> None:
        """
        Apaga um ficheiro do Supabase Storage.

        Args:
            bucket_name (str): Nome do bucket.
            file_path (str): Caminho do ficheiro a apagar.

        Erros:
            StorageDeleteException: Se não houver ficheiro para apagar.
        """
        try:
            response = self.client.storage.from_(bucket_name).remove([file_path])

            # Supabase may return a list (success) or dict with error
            if isinstance(response, dict) and response.get("error"):
                raise StorageDeleteException(response["error"]["message"])

        except Exception as exc:
            raise StorageDeleteException(str(exc)) from exc

    def get_signed_url(
        self,
        bucket_name: str,
        file_path: str,
        expiration_seconds: int = 900,
    ) -> str:
        """
        Gera um signed URL para um ficheiro armazenado no Supabase Storage.

        Args:
            bucket_name (str): Nome do bucket.
            file_path (str): Caminho do ficheiro.
            expiration_seconds (int): Tempo de expiração do URL em segundos. Padrão é 900 segundos (15 minutos).
            
        Devolve:
            str: Signed URL.

        Erros:
            StorageSignedUrlException: Se o ficheiro não existir ou a geração do URL falhar.
        """
        try:
            response = self.client.storage.from_(bucket_name).create_signed_url(
                path=file_path,
                expires_in=expiration_seconds,
            )

            if response.get("error"):
                raise StorageSignedUrlException(response["error"]["message"])

            return response["signedURL"]

        except Exception as exc:
            raise StorageSignedUrlException(str(exc)) from exc
