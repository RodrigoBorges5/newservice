"""
Supabase Client Helper
Fornece uma instância configurada do Supabase client para uso em todo o projeto.
"""
from supabase import create_client, Client
from django.conf import settings


def get_supabase_client() -> Client:
    """
    Retorna uma instância autenticada do Supabase client.
    
    Returns:
        Client: Instância do Supabase client configurada.
    
    Raises:
        ValueError: Se as variáveis SUPABASE_URL ou SUPABASE_KEY não estiverem configuradas.
    """
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    
    if not url or not key:
        raise ValueError(
            "SUPABASE_URL e SUPABASE_KEY devem estar configurados no arquivo .env"
        )
    
    return create_client(url, key)


# Instância global reutilizável (opcional - use com cuidado em ambientes assíncronos)
supabase: Client = None

def get_or_create_supabase_client() -> Client:
    """
    Retorna a instância global do Supabase client ou cria uma nova se não existir.
    
    Returns:
        Client: Instância do Supabase client.
    """
    global supabase
    if supabase is None:
        supabase = get_supabase_client()
    return supabase
