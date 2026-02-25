from requests.exceptions import RequestException, Timeout
from supabase import create_client, Client
from postgrest.exceptions import APIError
from django.conf import settings
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class UserNotFoundError(Exception):
    pass


class InvalidUserRoleError(Exception):
    pass


def get_user_email(user_uuid: str) -> str:
    """
    Obtém o email de um utilizador a partir do Supabase Auth.

    Utiliza a Service Role Key para aceder à Admin API.
    Se falhar em produção, lança uma exceção.
    Em DEBUG, retorna um email de fallback.

    Args:
        user_uuid: UUID do utilizador no Supabase Auth.

    Returns:
        Email do utilizador.

    Raises:
        ValueError: Se o email não for encontrado e DEBUG=False.
    """
    try:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise ValueError(
                "SUPABASE_URL e SUPABASE_SERVICE_KEY não estão configurados"
            )

        admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        response = admin_client.auth.admin.get_user_by_id(user_uuid)

        if response and response.user and response.user.email:
            return response.user.email

    except Exception as e:
        # Fallback para desenvolvimento/teste
        if settings.DEBUG:
            fallback_email = os.getenv(
                "DEBUG_FALLBACK_EMAIL",
                f"estudante+{user_uuid[:8]}@teste.local",
            )
            import logging

            logging.getLogger(__name__).warning(
                "[Supabase Auth] Fallback DEBUG — email=%s (uuid=%s, erro=%s)",
                fallback_email,
                user_uuid[:8],
                e,
            )
            return fallback_email

        # Em produção, falhar explicitamente
        raise ValueError(
            f"Email não encontrado para o utilizador {user_uuid}. Erro: {str(e)}"
        )


def get_user_role(user_id):
    """
    Valida o X-User-ID e retorna a role do user.

    Roles esperadas: 0, 1, 2
    Lança:
        - UserNotFoundError: se o usuário não existir
        - InvalidUserRoleError: se a role não estiver entre 0,1,2
    """
    try:
        response = (
            supabase.table("utilizador")
            .select("tipo")
            .eq("auth_user_supabase__id", user_id)
            .maybe_single()
            .execute()
        )

        if not response:
            raise UserNotFoundError(f"Usuário {user_id} não existe")

        user_data = response.data

        role = user_data.get("tipo")
        if role not in [0, 1, 2]:
            raise InvalidUserRoleError(f"Role inválida: {role}")

        return role

    except APIError as e:
        # APIError do Postgrest quando não encontra resultados ou há erro na query
        raise UserNotFoundError(f"Usuário {user_id} não existe")
    except (RequestException, Timeout) as e:
        # Tratamento de rede/timeout
        raise ConnectionError(f"Falha ao conectar com Supabase: {str(e)}")
    """
    Valida o X-User-ID e retorna a role do user.

    Roles esperadas: 0, 1, 2
    Lança:
        - UserNotFoundError: se o usuário não existir
        - InvalidUserRoleError: se a role não estiver entre 0,1,2
    """
    try:
        response = (
            supabase.table("utilizador")
            .select("tipo")
            .eq("auth_user_supabase__id", user_id)
            .maybe_single()
            .execute()
        )

        if not response:
            raise UserNotFoundError(f"Usuário {user_id} não existe")

        user_data = response.data

        role = user_data.get("tipo")
        if role not in [0, 1, 2]:
            raise InvalidUserRoleError(f"Role inválida: {role}")

        return role

    except APIError as e:
        # APIError do Postgrest quando não encontra resultados ou há erro na query
        raise UserNotFoundError(f"Usuário {user_id} não existe")
    except (RequestException, Timeout) as e:
        # Tratamento de rede/timeout
        raise ConnectionError(f"Falha ao conectar com Supabase: {str(e)}")
