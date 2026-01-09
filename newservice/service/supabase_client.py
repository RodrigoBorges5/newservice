from requests.exceptions import RequestException, Timeout
from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class UserNotFoundError(Exception):
    pass

class InvalidUserRoleError(Exception):
    pass

def get_user_role(user_id):
    """
    Valida o X-User-ID e retorna a role do user.
    
    Roles esperadas: 0, 1, 2
    Lança:
        - UserNotFoundError: se o usuário não existir
        - InvalidUserRoleError: se a role não estiver entre 0,1,2
    """
    try:
        response = supabase.table("utilizador").select("tipo").eq("auth_user_supabase__id", user_id).maybe_single().execute()

        if not response:
            raise UserNotFoundError(f"Usuário {user_id} não existe")
        
        user_data = response.data
        
        role = user_data.get("tipo")
        if role not in [0, 1, 2]:
            raise InvalidUserRoleError(f"Role inválida: {role}")

        return role

    except (RequestException, Timeout) as e:
        # Tratamento de rede/timeout
        raise ConnectionError(f"Falha ao conectar com Supabase: {str(e)}")