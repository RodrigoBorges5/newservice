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

### Request:

**Content-Type:** multipart/form-data
**Body:**  
| Campo | Tipo |
|-------|-----------|
| cv | File (PDF)|

Regras de validação do ficheiro

- O ficheiro é obrigatório
- Apenas ficheiros PDF
- Tamanho máximo permitido: 5MB
- O ficheiro é guardado com o nome fixo `cv.pdf`
- Uploads subsequentes sobrescrevem o ficheiro existente

### Respostas:

**Upload do currículo efetuado com sucesso:**
201 Created  
{
"id": 12,
"file": "estudante_45/cv.pdf",
"status": 0
}

**Erro de validação do pedido:**
400 Bad Request

Sem ficheiro

```json
{
  "detail": "Ficheiro de currículo é obrigatório."
}
```

Ficheiro não PDF

```json
{
  "detail": "Apenas ficheiros PDF são permitidos."
}
```

Ficheiro superior a 5MB

```json
{
  "detail": "O ficheiro excede o tamanho máximo de 5MB."
}
```

**Utilizador não autenticado:**
401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Utilizador autenticado sem perfil de estudante:**
404 Not Found

```json
{
  "detail": "Estudante não encontrado."
}
```

**Erro ao efetuar upload do ficheiro para o Supabase Storage:**
503 Service Unavailable

```json
{
  "detail": "Erro ao guardar o currículo."
}
```

Garantia: nenhum registo de currículo é criado na base de dados.

**Erro ao criar ou atualizar o registo Curriculo:**
500 Internal Server Error

```json
{
  "detail": "Erro ao registar CV"
}
```

Garantia: o ficheiro é removido do Storage (rollback).

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

---

## Endpoints de Notificações

### GET /curriculo/notifications/

**Descrição:** Lista as notificações do utilizador autenticado (e.g., alterações de estado do CV, feedback).

**Permissões:**
| Role | Acesso |
|------|--------|
| Estudante (2) | Apenas as suas notificações |
| CR (0) | Todas as notificações; pode filtrar por estudante |
| Empresa (1) | 403 Forbidden |

**Filtros (query params):**

| Parâmetro   | Tipo   | Descrição                                              |
| ----------- | ------ | ------------------------------------------------------ |
| `type`      | string | Tipo de notificação: `cv_status_change`, `cv_feedback` |
| `status`    | string | Estado de envio: `sent`, `failed`                      |
| `date_from` | date   | Data inicial (YYYY-MM-DD)                              |
| `date_to`   | date   | Data final (YYYY-MM-DD)                                |
| `student`   | UUID   | UUID do estudante (apenas CR)                          |

**Ordenação:**

- Campos: `created_at`, `updated_at`, `type`, `status`
- Utilizar `?ordering=campo` ou `?ordering=-campo` (descendente)
- Padrão: `-created_at` (mais recentes primeiro)

**Paginação:**

- `page` - Número da página (padrão: 1)
- `page_size` - Registos por página (padrão: 20, máximo: 100)

**Exemplo de pedido:**

```
GET /service/curriculo/notifications/?type=cv_status_change&status=sent&ordering=-created_at
X-User-ID: <uuid-do-estudante>
```

**Resposta (200 OK):**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "type": "cv_status_change",
      "subject": "🎉 O teu currículo foi aprovado!",
      "status": "sent",
      "recipient_email": "aluno@exemplo.pt",
      "created_at": "2026-02-15T15:30:00Z",
      "updated_at": "2026-02-15T15:30:00Z",
      "read": false,
      "curriculo": 42,
      "error_message": ""
    }
  ]
}
```

---

### PATCH /curriculo/notifications/{id}/

**Descrição:** Marca uma notificação como lida (ou não lida).

**Permissões:**

- Estudante: apenas as suas próprias notificações
- CR: qualquer notificação
- Empresa: 403 Forbidden

**Body (JSON):**

```json
{
  "read": true
}
```

**Resposta (200 OK):**

```json
{
  "id": 1,
  "read": true
}
```

**Erros:**
| Código | Descrição |
|--------|-----------|
| 401 | Header `X-User-ID` em falta |
| 403 | Sem permissão (Empresa, ou estudante a alterar notificação de outrem) |
| 404 | Notificação não encontrada |
| 405 | Método não permitido (POST, PUT, DELETE) |

---

### Modelo Notification

| Campo               | Tipo     | Descrição                           |
| ------------------- | -------- | ----------------------------------- |
| `id`                | int      | Chave primária (auto-incremento)    |
| `recipient_user_id` | UUID     | UUID do utilizador destinatário     |
| `recipient_email`   | string   | Email no momento do envio           |
| `type`              | string   | `cv_status_change` ou `cv_feedback` |
| `subject`           | string   | Assunto do email enviado            |
| `status`            | string   | `sent` ou `failed`                  |
| `error_message`     | string   | Mensagem de erro (vazio se sucesso) |
| `read`              | bool     | Se foi lida pelo utilizador         |
| `curriculo`         | int/null | FK para o currículo associado       |
| `created_at`        | datetime | Data de criação                     |
| `updated_at`        | datetime | Data da última atualização          |

As notificações são criadas automaticamente pela task `send_cv_status_notification` sempre que o estado de um CV é alterado (aprovado ou rejeitado).

# API Documentation – CR Review de Currículos

## Endpoints de Review de Currículo (CR)

### POST /curriculo/{id}/review/

**Descrição:**
Endpoint utilizado por utilizadores com role **CR (0)** para validar um currículo pendente, aprovando ou rejeitando o CV e opcionalmente adicionando feedback.

**Permissão:** IsCR (role=0)

**Headers obrigatórios:**

```
X-User-ID: <uuid-do-cr>
```

---

## Request

**Content-Type:** application/json

### Body

```json
{
  "curriculo_id": 42,
  "status": 1,
  "feedback": "Perfil técnico sólido"
}
```

### Campos

| Campo        | Tipo    | Obrigatório | Descrição                                   |
| ------------ | ------- | ----------- | ------------------------------------------- |
| curriculo_id | integer | Sim         | ID do currículo a validar                   |
| status       | integer | Sim         | Novo estado do CV (1=aprovado, 2=rejeitado) |
| feedback     | string  | Condicional | Obrigatório se status=2 (rejeitado)         |

---

## Regras de Validação

* Apenas currículos com estado **PENDING (0)** podem ser validados
* Não é permitido voltar um currículo ao estado PENDING
* `status` só aceita os valores:

  * `1` – aprovado
  * `2` – rejeitado
* Se `status = 2`, o campo `feedback` é obrigatório
* O currículo deve existir
* Apenas utilizadores CR podem executar esta ação

---

## Comportamento Interno

Consoante o valor de `status`, o sistema executa:

* `curriculo.approve(cr_user)` se status = 1
* `curriculo.reject(cr_user, feedback)` se status = 2

Durante o processo:

* O currículo muda de estado
* A data de validação é automaticamente registada
* É criado um registo de review (`CrCurriculo`)
* São disparadas notificações automáticas para o estudante

---

## Response

### Sucesso – 200 OK

```json
{
  "curriculo_id": 42,
  "status": "Aprovado",
  "feedback": "Perfil técnico sólido",
  "review_date": "2026-02-16",
  "validated_by": "João Silva"
}
```

### Campos de Resposta

| Campo        | Tipo        | Descrição                             |
| ------------ | ----------- | ------------------------------------- |
| curriculo_id | integer     | ID do currículo validado              |
| status       | string      | Estado legível (Aprovado / Rejeitado) |
| feedback     | string/null | Feedback do CR                        |
| review_date  | date        | Data da validação                     |
| validated_by | string      | Nome do CR que validou                |

---

## Erros Comuns

### Currículo não encontrado – 404 Not Found

```json
{
  "detail": "Currículo não encontrado."
}
```

### Currículo já validado – 400 Bad Request

```json
{
  "detail": "Este currículo já foi validado."
}
```

### Feedback obrigatório em rejeição – 400 Bad Request

```json
{
  "feedback": [
    "Feedback é obrigatório quando o currículo é rejeitado."
  ]
}
```

### Status inválido – 400 Bad Request

```json
{
  "status": [
    "Status inválido."
  ]
}
```

### Sem permissões (não CR) – 403 Forbidden

```json
{
  "detail": "Não possui permissão para efetuar esta ação."
}
```

### Header de autenticação em falta – 401 Unauthorized

```json
{
  "detail": "Header X-User-ID em falta"
}
```

---

## Observações

* Um currículo só pode ser validado **uma única vez**
* Cada currículo possui no máximo **uma review**
* A validação é uma operação irreversível
* Notificações são enviadas automaticamente após aprovação ou rejeição
