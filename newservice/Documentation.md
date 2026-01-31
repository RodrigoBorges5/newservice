# API Documentation

Guia para endpoints com exemplos e respostas:

**Base URL:** `http://localhost:8000/service/`

**T.1.1 - Base Authentication - Qualquer URL menos os incluidos no EXCLUDED_PATH em middleware.py**

Resposta sem Header:
{
    "detail": "Header X-User-ID em falta"
}

Resposta com Header X-User_ID:
X-User-ID = [ID]
{
    "status": "ok",
    "user_id": [ID]
    "user_role": [tipo de utilizador]
}

**T.1.4 - Role Authentication - Qualquer URL com limitação de role**
**Exemplo: necessita de role estudante (permission_classes = [IsStudent])**

Resposta sem role estudante:
{
    "detail": "Não possui permição para efetuar esta ação."
}

Resposta com Header X-User_ID:
X-User-ID = [ID]
{
    "status": "ok",
    "user_id": [ID],
    "user_role": 2
}

---

## Endpoints de Currículo

### GET /curriculo/me/

**Descrição:** Retorna o currículo do estudante autenticado
**Permissão:** IsStudent (role=2)
**Headers:** X-User-ID = [ID do estudante]

**Resposta com sucesso (200 OK):**

```json
{
    "id": 1,
    "file": "path/to/curriculo.pdf",
    "status": 0,
    "descricao": "Currículo atualizado 2026",
    "validated_date": null,
    "estudante_utilizador_auth_user_supabase_field": "uuid-estudante"
}
```

**Resposta sem currículo (404 NOT FOUND):**

```json
{
    "detail": "Currículo não encontrado. Por favor, submeta o seu CV."
}
```

**Resposta sem perfil de estudante (404 NOT FOUND):**

```json
{
    "detail": "Perfil de estudante não encontrado."
}
```

---

### POST /curriculo/me/

**Descrição:** Cria novo currículo para o estudante autenticado (US-2.2)
**Permissão:** IsStudent (role=2)
**Headers:** X-User-ID = [ID do estudante]

**Body (exemplo):**

```json
{
    "file": "path/to/meu_curriculo.pdf",
    "descricao": "Currículo com experiência em Python e Django"
}
```

**Resposta com sucesso (201 CREATED):**

```json
{
    "message": "Currículo submetido com sucesso! Aguarde validação da equipa CR.",
    "data": {
        "id": 1,
        "file": "path/to/meu_curriculo.pdf",
        "status": 0,
        "descricao": "Currículo com experiência em Python e Django",
        "validated_date": null,
        "estudante_utilizador_auth_user_supabase_field": "uuid-estudante"
    }
}
```

**Resposta com CV duplicado (400 BAD REQUEST):**

```json
{
    "detail": "Já existe um currículo associado a este estudante."
}
```

**Resposta sem aceitar termos (400 BAD REQUEST):**

```json
{
    "detail": "Erro ao submeter currículo: deves aceitar."
}
```

ou

```json
{
    "estudante_utilizador_auth_user_supabase_field": [
        "Deves aceitar a partilhar os dados a submeter o curriculo. Por favor, aceite os termos de dados."
    ]
}
```

**Resposta com ficheiro não-PDF (400 BAD REQUEST):**

```json
{
    "file": [
        "O ficheiro do curriculo deve estar em formato PDF."
    ]
}
```

**Resposta com caminho muito longo (400 BAD REQUEST):**

```json
{
    "file": [
        "O caminho do ficheiro é demasiado longo."
    ]
}
```

---

### DELETE /curriculo/me/

**Descrição:** Remove o currículo do estudante autenticado
**Permissão:** IsStudent (role=2)
**Headers:** X-User-ID = [ID do estudante]

**Resposta com sucesso (204 NO CONTENT):**

```json
{
    "message": "Currículo eliminado com sucesso. Crie novo CV se desejar."
}
```

**Resposta sem currículo (404 NOT FOUND):**

```json
{
    "detail": "Currículo não encontrado. Por favor, submeta o seu CV."
}
```

### GET /curriculo/

**Filtros Suportados:**

- `status` e `status_in` (múltiplos status)
- `validated_date_after`, `validated_date_before` (ranges de data)
- `estudante_grau`, `estudante_grau_in` (grau académico)
- `estudante_ano_min`, `estudante_ano_max` (range de anos)
- `estudante_area` (ID da área)
- `estudante_area_nome` (nome da área, case-insensitive)

---

### GET /curriculo/ /view/

**Restrições por Role:**

- **Empresa**: Vê apenas CVs aprovados (status=1)
- **CR**: Vê todos os CVs
- **Estudante**: Bloqueado, use `/curriculo/me/`

---

### GET /curriculo/access-history/

**Descrição:** Histórico de acessos a um CV (CR only)
**Paginação:** 50 registos/página
**Ordenação:** Por accessed_at DESC (mais recentes primeiro)
**Retenção:** 12 meses (limpeza automática via Celery)
