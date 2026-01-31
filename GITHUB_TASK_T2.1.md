# T2.1: Criar Service Layer SupabaseStorageService

## 📋 Informações da Task

**Sprint**: 2  
**Dev Responsável**: Dev 1 (Backend Core)  
**Dependências**: T0.2 (Variáveis de ambiente Supabase configuradas)  
**User Story Relacionada**: US-2 (Submissão de CV)  
**Requisito Funcional**: FR-2 (Estudantes - Submissão de CV)

---

## 📝 Descrição

Criar uma service layer reutilizável `SupabaseStorageService` que encapsule todas as operações com Supabase Storage (bucket de CVs). Esta service deve implementar métodos para upload, delete e geração de URLs assinadas (signed URLs).

### Objetivo

Centralizar a lógica de interação com Supabase Storage num único lugar, facilitando testes, manutenção e reutilização em múltiplos endpoints.

---

## ✅ Critérios de Aceitação

- **C1**: Classe `SupabaseStorageService` criada em `service/services/storage_service.py`
- **C2**: Método `upload_file(file, bucket_name, file_path)` implementado
  - Valida se o ficheiro não é nulo
  - Retorna o caminho armazenado (storage_path) em caso de sucesso
  - Retorna exceção customizada em caso de falha
- **C3**: Método `delete_file(bucket_name, file_path)` implementado
  - Remove ficheiro do Supabase Storage
  - Trata caso onde ficheiro não existe (sem erro)
- **C4**: Método `get_signed_url(bucket_name, file_path, expiration_seconds=900)` implementado
  - Gera URL assinada com expiração configurável (default 15 min)
  - Retorna URL pública válida
  - Trata erro se ficheiro não existe
- **C5**: Exceções customizadas criadas
  - `StorageUploadException`
  - `StorageDeleteException`
  - `StorageSignedUrlException`
- **C6**: Supabase client reutiliza a instância do settings (SUPABASE_URL, SUPABASE_KEY)
- **C7**: Código documentado com docstrings no formato Google
- **C8**: Testes unitários criados com mocks do Supabase client

---

## 🎯 Tasks Relacionadas

| Task   | Descrição                                              | Status   |
| ------ | ------------------------------------------------------ | -------- |
| T0.2   | Configurar variáveis de ambiente Supabase             | ✅ DONE  |
| T2.2   | Implementar endpoint `POST /api/curriculo/upload/`    | Blocked  |
| T2.5   | Integrar lógica de upload com Storage                 | Blocked  |
| T2.6   | Testes de upload (mock Supabase Storage)              | Blocked  |

---

## 📂 Estrutura de Ficheiros

```
newservice/
└── service/
    └── services/
        ├── __init__.py
        ├── storage_service.py          ← 🆕 CRIAR
        ├── exceptions.py               ← 🆕 CRIAR (se não existir)
        └── tests/
            ├── __init__.py
            └── test_storage_service.py ← 🆕 CRIAR
```

---

## 🔧 Implementação - Pseudo-código

```python
# service/services/storage_service.py

from supabase import Client
from django.conf import settings
from .exceptions import (
    StorageUploadException,
    StorageDeleteException,
    StorageSignedUrlException
)

class SupabaseStorageService:
    """Service layer para Supabase Storage."""
    
    def __init__(self):
        """Inicializa client do Supabase."""
        from service.supabase_client import get_supabase_client
        self.client: Client = get_supabase_client()
    
    def upload_file(self, file, bucket_name: str, file_path: str) -> str:
        """
        Upload de ficheiro para Supabase Storage.
        
        Args:
            file: Ficheiro (bytes ou arquivo)
            bucket_name: Nome do bucket (ex: 'curriculos')
            file_path: Caminho no bucket (ex: 'estudante_123/cv.pdf')
        
        Returns:
            str: Caminho armazenado do ficheiro
        
        Raises:
            StorageUploadException: Se upload falhar
        """
        try:
            # Implementar lógica
            pass
        except Exception as e:
            raise StorageUploadException(f"Upload falhou: {str(e)}")
    
    def delete_file(self, bucket_name: str, file_path: str) -> bool:
        """
        Apaga ficheiro do Supabase Storage.
        
        Args:
            bucket_name: Nome do bucket
            file_path: Caminho no bucket
        
        Returns:
            bool: True se apagado, False se ficheiro não existe
        
        Raises:
            StorageDeleteException: Se falha inesperada
        """
        try:
            # Implementar lógica
            pass
        except Exception as e:
            raise StorageDeleteException(f"Delete falhou: {str(e)}")
    
    def get_signed_url(
        self,
        bucket_name: str,
        file_path: str,
        expiration_seconds: int = 900
    ) -> str:
        """
        Gera URL assinada para acesso a ficheiro.
        
        Args:
            bucket_name: Nome do bucket
            file_path: Caminho no bucket
            expiration_seconds: Tempo de expiração em segundos (default 15 min)
        
        Returns:
            str: URL assinada pública
        
        Raises:
            StorageSignedUrlException: Se geração de URL falhar
        """
        try:
            # Implementar lógica
            pass
        except Exception as e:
            raise StorageSignedUrlException(f"Signed URL falhou: {str(e)}")
```

---

## 🧪 Testes Esperados

```python
# service/services/tests/test_storage_service.py

import pytest
from unittest.mock import Mock, patch
from service.services.storage_service import SupabaseStorageService
from service.services.exceptions import (
    StorageUploadException,
    StorageDeleteException,
    StorageSignedUrlException
)

class TestSupabaseStorageService:
    """Testes da SupabaseStorageService."""
    
    @pytest.fixture
    def service(self):
        """Fixture que retorna instância da service."""
        return SupabaseStorageService()
    
    def test_upload_file_success(self, service):
        """Testa upload bem-sucedido."""
        # Arrange
        file = b"PDF content here"
        bucket = "curriculos"
        path = "estudante_1/cv.pdf"
        
        # Act
        result = service.upload_file(file, bucket, path)
        
        # Assert
        assert result == path
    
    def test_upload_file_fails(self, service):
        """Testa upload com falha."""
        # Arrange
        file = b"PDF content"
        
        # Act & Assert
        with pytest.raises(StorageUploadException):
            service.upload_file(file, "invalid_bucket", "path")
    
    def test_delete_file_success(self, service):
        """Testa delete bem-sucedido."""
        # Implementar teste
        pass
    
    def test_get_signed_url_success(self, service):
        """Testa geração de signed URL."""
        # Implementar teste
        pass
```

---

## 📋 Checklist de Implementação

- [ ] Ficheiro `service/services/storage_service.py` criado
- [ ] Ficheiro `service/services/exceptions.py` criado com 3 exceções
- [ ] Ficheiro `service/services/tests/test_storage_service.py` criado
- [ ] Ficheiro `service/services/__init__.py` criado (para imports)
- [ ] Classe `SupabaseStorageService` com 3 métodos implementados
- [ ] Integração com `get_supabase_client()` funcionando
- [ ] Docstrings no formato Google em todos os métodos
- [ ] Testes unitários passando (mínimo 80% de cobertura)
- [ ] Testes mockam o cliente Supabase (sem chamadas reais)
- [ ] Code review realizado
- [ ] CI/CD pipeline verde (sem erros de linting)

---

## 🔗 Referências

- [Supabase Storage Python Docs](https://supabase.com/docs/reference/python/storage-createbucket)
- [Supabase Signed URLs](https://supabase.com/docs/guides/storage/security/signed-urls)
- [Python Exception Handling](https://docs.python.org/3/tutorial/errors.html)

---

## 📌 Notas Importantes

1. **Reutilização do Client**: Usar a mesma instância do Supabase client do projeto (via settings ou singleton)
2. **Segurança**: URLs assinadas têm expiração obrigatória (não usar infinita)
3. **Bucket Naming**: Convenção de nomes (ex: `curriculos`, `vagas`, `documentos`)
4. **Path Structure**: Organizar ficheiros por tipo de utilizador (ex: `estudante_123/cv.pdf`)
5. **Error Handling**: Todas as exceções devem ser específicas e com mensagens descritivas

---

**Criado em**: 19 Janeiro 2026  
**Versão**: 1.0  
**Status**: 📋 Ready for Development
