from django.http import JsonResponse
from .supabase_client import get_user_role, UserNotFoundError, InvalidUserRoleError
from rest_framework.permissions import BasePermission

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
        role = request.headers.get("X-User-Role", "user")

        if not user_id:
            return JsonResponse(
                {"detail": "Header X-User-ID em falta"},
                status=401
            )
        try:
            # Valida usuário no Supabase
            role = get_user_role(user_id)
        except (UserNotFoundError, InvalidUserRoleError):
            return JsonResponse({"detail": f"Usuário {user_id} não autorizado"}, status=403)
        except ConnectionError as e:
            return JsonResponse({"detail": f"Erro ao conectar com Supabase: {str(e)}"}, status=500)

        
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
