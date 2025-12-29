# API Documentation

Guia para endpoints com exemplos e respostas:

**Base URL:** `http://localhost:8000/service/`

**T.1.1 - Base Authentication - Qualquer URL menos os incluidos no EXCLUDED_PATH em middleware.py**

Resposta sem Header:
{
    "detail": "Header X-User-ID em falta"
}
Resposta com Header X-User_ID:
X-User-ID = ID
{
    "status": "ok",
    "user_id": "ID"
    "user_role": "tipo de utilizador"
}