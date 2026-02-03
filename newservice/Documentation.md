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

---

### POST /curriculo/me/

**Descrição:** Cria novo currículo para o estudante autenticado (US-2.2)
**Permissão:** IsStudent (role=2)
**Headers:** X-User-ID = [ID do estudante]

### DELETE /curriculo/me/

**Descrição:** Remove o currículo do estudante autenticado
**Permissão:** IsStudent (role=2)
**Headers:** X-User-ID = [ID do estudante]

### GET /curriculo/

**Descrição:** Lista múltiplos currículos com filtros aplicados
**Permissão:** IsAll (role=0, 1, 2)
**Headers:** X-User-ID = [ID do utilizador]

**Restrições por Role:**

- **CR (role=0)**: Vê todos os CVs (status 0, 1, 2) - pode usar todos os filtros
- **Empresa (role=1)**: Vê apenas CVs aprovados (status=1) - pode usar todos os filtros
- **Estudante (role=2)**: Deve usar `/curriculo/me/` para seu próprio CV

**Filtros Suportados (Query Params):**

- `status` - Status exato do CV (0=pendente, 1=aprovado, 2=rejeitado)
- `status_in` - Múltiplos status (e.g., `?status_in=0&status_in=1`)
- `validated_date_after` - CVs validados após data (YYYY-MM-DD)
- `validated_date_before` - CVs validados antes de data (YYYY-MM-DD)
- `estudante_grau` - Grau do estudante (case-insensitive)
- `estudante_grau_in` - Múltiplos graus
- `estudante_ano_min` - Ano de faculdade mínimo (>=)
- `estudante_ano_max` - Ano de faculdade máximo (<=)
- `estudante_area` - ID da área do estudante
- `estudante_area_nome` - Nome da área do estudante (case-insensitive, contém)

---

### GET /curriculo/view/

**Descrição:** Visualiza um CV específico com signed URL
**Permissão:** IsAll (role=0, 1, 2)
**Headers:** X-User-ID = [ID do utilizador]

**Restrições por Role:**

- **CR (role=0)**: Pode ver qualquer CV (todos os status)
- **Empresa (role=1)**: Vê apenas CVs aprovados (status=1)
- **Estudante (role=2)**: Bloqueado, use `/curriculo/me/`

---

### GET /curriculo/access-history/

**Descrição:** Histórico de acessos a um CV (CR only)
**Paginação:** 50 registos/página
**Ordenação:** Por accessed_at DESC (mais recentes primeiro)
**Retenção:** 12 meses (limpeza automática via Celery)

**Query:**

- `page` - Número da página (padrão: 1)
- `page_size` - Registos por página (padrão: 50, máximo: 100)
