from django.http import JsonResponse
from .supabase_client import (
    get_user_role,
    UserNotFoundError,
    InvalidUserRoleError,
)
from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)

EXCLUDED_PATHS = [
    "/service/",
]

class UserHeaderMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in EXCLUDED_PATHS:
            return self.get_response(request)

        user_id = request.headers.get("X-User-ID")

        if not user_id:
            return JsonResponse(
                {"detail": "Header X-User-ID em falta"},
                status=401
            )

        try:
            # valida usuário e retorna role a partir do Supabase
            role = get_user_role(user_id)

        except UserNotFoundError:
            return JsonResponse(
                {"detail": f"Usuário {user_id} não encontrado"},
                status=401
            )

        except InvalidUserRoleError:
            return JsonResponse(
                {"detail": f"Usuário {user_id} não possui permissão válida"},
                status=403
            )

        except Exception:
            logger.exception("Erro ao conectar com Supabase")
            return JsonResponse(
                {"detail": "Erro interno ao validar usuário"},
                status=500
            )

        request.user_id = user_id
        request.role = role

        return self.get_response(request)

class IsStudent(BasePermission):
    message = "Não possui permição para efetuar esta ação."

    def has_permission(self, request, view):
        return getattr(request, "role", None) == 2


class IsCompany(BasePermission):
    message = "Não possui permição para efetuar esta ação."

    def has_permission(self, request, view):
        return getattr(request, "role", None) == 1


class IsCR(BasePermission):
    message = "Não possui permição para efetuar esta ação."

    def has_permission(self, request, view):
        return getattr(request, "role", None) == 0


class VagaPermission(BasePermission):
    """
    Permissões para o endpoint /vagas/:
    
    - CR (role=0): CRUD completo (admin)
    - Empresas (role=1): CRUD apenas para as suas próprias vagas
    - Estudantes (role=2): Apenas leitura
    """
    message = "Não possui permissão para efetuar esta ação."

    def has_permission(self, request, view):
        role = getattr(request, "role", None)
        
        # CR (role=0) e Company (role=1): podem aceder a endpoints de escrita
        if role in [0, 1]:
            return True
        
        # Estudantes (role=2): apenas leitura
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return role == 2
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica permissões ao nível do objeto (vaga específica).
        Chamado em operações PUT, PATCH, DELETE em /vagas/{id}/
        """
        role = getattr(request, "role", None)
        
        # leitura permitida para todos os roles autorizados
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # CR (role=0): pode modificar/remover QUALQUER vaga (admin)
        if role == 0:
            return True
        
        # Company (role=1): só pode modificar/remover as SUAS vagas
        if role == 1:
            user_id = getattr(request, "user_id", None)
            # verifica se a vaga pertence à empresa do utilizador
            return str(obj.empresa_utilizador_auth_user_supabase_field) == str(user_id)
        
        return False
class IsAll(BasePermission):
    """
    Permite acesso a todos os tipos de usuários autenticados.
    """
    message = "Não possui permissão para efetuar esta ação."

    def has_permission(self, request, view):
        return getattr(request, "role", None) in [0, 1, 2]
    
class IsCROrIsCompany(BasePermission):
    """
    Permite acesso a usuários com role CR (0) ou Company (1).
    """
    message = "Não possui permissão para efetuar esta ação. Apenas CR ou Empresas podem acessar."

    def has_permission(self, request, view):
        return getattr(request, "role", None) in [0, 1]


class IsStudentOrCR(BasePermission):
    """
    Permite acesso a Estudantes (role=2) e CR (role=0).

    Estudantes veem apenas as suas próprias notificações (filtragem
    feita na view). CR pode ver todas ou filtrar por estudante.
    Empresas (role=1) não têm acesso.
    """
    message = "Não possui permissão para efetuar esta ação. Apenas Estudantes ou CR podem aceder."

    def has_permission(self, request, view):
        return getattr(request, "role", None) in [0, 2]
